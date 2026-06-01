"""Award-search providers.

The production ANA Mileage Club/EVA partner-award integration is intentionally not
implemented yet. The stub provider lets the runner, state, and alerting flow be
built and tested safely before live search automation is evaluated.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import AvailabilityResult, WatchRoute


class AwardSearchProvider(ABC):
    """Interface for any award availability search provider."""

    name: str

    @abstractmethod
    def search(self, route: WatchRoute) -> list[AvailabilityResult]:
        """Return normalized availability results for a configured route."""


class StubAwardSearchProvider(AwardSearchProvider):
    """Deterministic fake provider used for local development and tests."""

    name = "stub"

    def __init__(self, emit_results: bool = True) -> None:
        self.emit_results = emit_results

    def search(self, route: WatchRoute) -> list[AvailabilityResult]:
        if not self.emit_results:
            return []

        return [
            AvailabilityResult(
                route_name=route.name,
                airline=route.airline,
                flight_number=f"{route.airline}1",
                origin=route.origin,
                destination=route.destination,
                departure_date=route.date_window.start,
                cabin=route.cabin,
                passengers=route.passengers,
                award_program=route.award_program,
                seats_available=1,
                source=self.name,
                booking_reference="dry-run stub result; verify manually before booking",
            )
        ]


def build_provider(name: str) -> AwardSearchProvider:
    """Factory for supported providers."""

    if name == "stub":
        return StubAwardSearchProvider()
    if name == "stub-empty":
        return StubAwardSearchProvider(emit_results=False)
    if name in {"ana", "ana-mileage-club"}:
        raise NotImplementedError(
            "ANA Mileage Club provider is a planned compliance-reviewed integration. "
            "Use --provider stub for local workflow development."
        )
    raise ValueError(f"unsupported provider: {name}")
