"""Scheduled runner orchestration for award checks."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Watchlist
from .notifier import Notifier
from .providers import AwardSearchProvider
from .state import StateStore


@dataclass(frozen=True)
class RunnerSummary:
    routes_checked: int = 0
    results_seen: int = 0
    new_results: int = 0
    alerts_sent: int = 0


class AwardSearchRunner:
    """Coordinates provider searches, state updates, and notifications."""

    def __init__(
        self,
        watchlist: Watchlist,
        provider: AwardSearchProvider,
        store: StateStore,
        notifier: Notifier,
    ) -> None:
        self.watchlist = watchlist
        self.provider = provider
        self.store = store
        self.notifier = notifier

    def run_once(self) -> RunnerSummary:
        routes_checked = 0
        results_seen = 0
        new_results = 0
        alerts_sent = 0

        for route in self.watchlist.routes:
            routes_checked += 1
            run_id = self.store.start_search_run(route, self.provider.name)
            try:
                results = self.provider.search(route)
                results_seen += len(results)
                for result in results:
                    is_new = self.store.upsert_result(result)
                    if not is_new:
                        continue
                    new_results += 1
                    if self.store.alert_recently_sent(
                        result.dedupe_key,
                        self.watchlist.settings.duplicate_suppression_hours,
                    ):
                        continue
                    message = self.notifier.send(result)
                    self.store.record_alert(
                        result=result,
                        destination=getattr(self.notifier, "destination", "unknown"),
                        message=message,
                        dry_run=getattr(self.notifier, "dry_run", False),
                    )
                    alerts_sent += 1
                self.store.finish_search_run(run_id, "success")
            except Exception as exc:
                self.store.finish_search_run(run_id, "failed", str(exc))
                raise

        return RunnerSummary(
            routes_checked=routes_checked,
            results_seen=results_seen,
            new_results=new_results,
            alerts_sent=alerts_sent,
        )
