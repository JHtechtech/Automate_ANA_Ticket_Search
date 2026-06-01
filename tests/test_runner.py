import sqlite3

from eva_award_alert.config import load_watchlist
from eva_award_alert.notifier import TelegramNotifier
from eva_award_alert.providers import StubAwardSearchProvider
from eva_award_alert.runner import AwardSearchRunner
from eva_award_alert.state import StateStore


def test_new_stub_results_alert_once_per_dedupe_key(tmp_path):
    watchlist = load_watchlist("config/watchlist.example.json")
    # Keep this unit test focused on deduplication for one route.
    watchlist.routes[:] = watchlist.routes[:1]
    store = StateStore(str(tmp_path / "state.db"))
    store.initialize()
    notifier = TelegramNotifier(dry_run=True)
    runner = AwardSearchRunner(watchlist, StubAwardSearchProvider(), store, notifier)

    first = runner.run_once()
    second = runner.run_once()

    assert first.routes_checked == 1
    assert first.results_seen == 1
    assert first.new_results == 1
    assert first.alerts_sent == 1
    assert second.routes_checked == 1
    assert second.results_seen == 1
    assert second.new_results == 0
    assert second.alerts_sent == 0

    connection = sqlite3.connect(tmp_path / "state.db")
    alert_count = connection.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    result_count = connection.execute("SELECT COUNT(*) FROM availability_results").fetchone()[0]
    connection.close()

    assert alert_count == 1
    assert result_count == 1
    store.close()
