"""Command-line entry point for the EVA award alert bot."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from .config import load_watchlist
from .notifier import build_notifier
from .providers import build_provider
from .runner import AwardSearchRunner
from .state import StateStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run EVA Air award availability checks.")
    parser.add_argument(
        "--config",
        default="config/watchlist.example.json",
        help="Path to watchlist JSON configuration.",
    )
    parser.add_argument(
        "--provider",
        default="stub",
        help="Award search provider to use. Currently supported: stub, stub-empty.",
    )
    parser.add_argument(
        "--database",
        help="Override SQLite database path from config.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--once",
        action="store_true",
        help="Run one check cycle and exit. This is the default mode.",
    )
    mode.add_argument(
        "--watch",
        action="store_true",
        help="Continuously run checks using poll_interval_minutes from the config.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    watchlist = load_watchlist(Path(args.config))
    database_path = args.database or watchlist.settings.database_path
    provider = build_provider(args.provider)
    notifier = build_notifier(watchlist.settings.notifier)

    store = StateStore(database_path)
    try:
        store.initialize()
        runner = AwardSearchRunner(watchlist, provider, store, notifier)
        while True:
            summary = runner.run_once()
            print(
                "Run complete: "
                f"routes_checked={summary.routes_checked}, "
                f"results_seen={summary.results_seen}, "
                f"new_results={summary.new_results}, "
                f"alerts_sent={summary.alerts_sent}"
            )
            if not args.watch:
                break
            sleep_seconds = watchlist.settings.poll_interval_minutes * 60
            print(f"Sleeping for {sleep_seconds} seconds before the next check cycle")
            time.sleep(sleep_seconds)
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
