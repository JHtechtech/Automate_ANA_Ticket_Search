"""Watchlist configuration loading."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Settings, WatchRoute, Watchlist


def load_watchlist(path: str | Path) -> Watchlist:
    """Load and validate a JSON watchlist file."""

    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    watchlist = Watchlist(
        settings=Settings.from_dict(data.get("settings", {})),
        routes=[WatchRoute.from_dict(route) for route in data.get("routes", [])],
    )
    watchlist.validate()
    return watchlist
