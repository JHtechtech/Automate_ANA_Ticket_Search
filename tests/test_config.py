from eva_award_alert.config import load_watchlist


def test_load_recommended_watchlist_routes():
    watchlist = load_watchlist("config/watchlist.example.json")

    origins = [route.origin for route in watchlist.routes]

    assert origins == ["LAX", "SFO", "SEA", "JFK", "IAH", "DFW", "ORD", "YVR", "YYZ", "IAD"]
    assert {route.destination for route in watchlist.routes} == {"TPE"}
    assert {route.airline for route in watchlist.routes} == {"BR"}
    assert {route.search_type for route in watchlist.routes} == {"award"}
    assert {route.cabin for route in watchlist.routes} == {"business"}
    assert {route.passengers for route in watchlist.routes} == {1}


def test_load_trial_watchlist_is_single_safe_route():
    watchlist = load_watchlist("config/watchlist.trial.json")

    assert len(watchlist.routes) == 1
    route = watchlist.routes[0]
    assert route.origin == "SFO"
    assert route.destination == "TPE"
    assert route.airline == "BR"
    assert route.search_type == "award"
    assert route.cabin == "business"
    assert route.passengers == 1
    assert watchlist.settings.notifier["dry_run"] is True
    assert watchlist.settings.database_path == "data/eva_award_alert_trial.db"
