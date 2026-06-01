"""Domain models for EVA award alert monitoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class DateWindow:
    """Inclusive departure-date window for a route search."""

    start: date
    end: date

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DateWindow":
        return cls(start=date.fromisoformat(data["start"]), end=date.fromisoformat(data["end"]))


@dataclass(frozen=True)
class WatchRoute:
    """A configured route to monitor for award availability."""

    name: str
    airline: str
    airline_name: str
    origin: str
    destination: str
    trip_type: str
    search_type: str
    award_program: str
    cabin: str
    passengers: int
    date_window: DateWindow
    alert: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WatchRoute":
        return cls(
            name=data["name"],
            airline=data["airline"],
            airline_name=data["airline_name"],
            origin=data["origin"],
            destination=data["destination"],
            trip_type=data["trip_type"],
            search_type=data["search_type"],
            award_program=data["award_program"],
            cabin=data["cabin"],
            passengers=int(data["passengers"]),
            date_window=DateWindow.from_dict(data["date_window"]),
            alert=dict(data.get("alert", {})),
        )

    def validate(self) -> None:
        errors: list[str] = []
        if self.airline != "BR":
            errors.append(f"{self.name}: airline must be BR for EVA Air")
        if self.destination != "TPE":
            errors.append(f"{self.name}: destination must be TPE for the initial MVP")
        if self.search_type != "award":
            errors.append(f"{self.name}: search_type must be award")
        if self.cabin != "business":
            errors.append(f"{self.name}: cabin must be business")
        if self.passengers < 1:
            errors.append(f"{self.name}: passengers must be at least 1")
        if self.date_window.end < self.date_window.start:
            errors.append(f"{self.name}: date_window.end must be on or after date_window.start")
        if errors:
            raise ValueError("; ".join(errors))


@dataclass(frozen=True)
class Settings:
    """Runtime settings shared by all routes."""

    poll_interval_minutes: int
    max_retries: int
    duplicate_suppression_hours: int
    database_path: str
    notifier: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        return cls(
            poll_interval_minutes=int(data.get("poll_interval_minutes", 15)),
            max_retries=int(data.get("max_retries", 2)),
            duplicate_suppression_hours=int(data.get("duplicate_suppression_hours", 24)),
            database_path=str(data.get("database_path", "data/eva_award_alert.db")),
            notifier=dict(data.get("notifier", {})),
        )


@dataclass(frozen=True)
class Watchlist:
    """Complete watchlist configuration."""

    settings: Settings
    routes: list[WatchRoute]

    def validate(self) -> None:
        if not self.routes:
            raise ValueError("watchlist must include at least one route")
        for route in self.routes:
            route.validate()


@dataclass(frozen=True)
class AvailabilityResult:
    """Normalized award-seat availability returned by a provider."""

    route_name: str
    airline: str
    flight_number: str
    origin: str
    destination: str
    departure_date: date
    cabin: str
    passengers: int
    award_program: str
    seats_available: int
    source: str
    booking_reference: str | None = None

    @property
    def dedupe_key(self) -> str:
        parts = [
            self.award_program,
            self.airline,
            self.flight_number,
            self.origin,
            self.destination,
            self.departure_date.isoformat(),
            self.cabin,
            str(self.passengers),
        ]
        return "|".join(parts)
