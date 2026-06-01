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
