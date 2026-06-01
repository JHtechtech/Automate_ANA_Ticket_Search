"""SQLite persistence for search runs, results, and alerts."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .models import AvailabilityResult, WatchRoute


class StateStore:
    """Small SQLite-backed state store."""

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row

    def close(self) -> None:
        self.connection.close()

    def initialize(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS search_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_name TEXT NOT NULL,
                provider TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT NOT NULL,
                error TEXT
            );

            CREATE TABLE IF NOT EXISTS availability_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dedupe_key TEXT NOT NULL UNIQUE,
                route_name TEXT NOT NULL,
                airline TEXT NOT NULL,
                flight_number TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                departure_date TEXT NOT NULL,
                cabin TEXT NOT NULL,
                passengers INTEGER NOT NULL,
                award_program TEXT NOT NULL,
                seats_available INTEGER NOT NULL,
                source TEXT NOT NULL,
                booking_reference TEXT,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dedupe_key TEXT NOT NULL,
                route_name TEXT NOT NULL,
                destination TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                dry_run INTEGER NOT NULL,
                message TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def start_search_run(self, route: WatchRoute, provider: str) -> int:
        now = utcnow_iso()
        cursor = self.connection.execute(
            """
            INSERT INTO search_runs (route_name, provider, started_at, status)
            VALUES (?, ?, ?, ?)
            """,
            (route.name, provider, now, "running"),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def finish_search_run(self, run_id: int, status: str, error: str | None = None) -> None:
        self.connection.execute(
            """
            UPDATE search_runs
            SET completed_at = ?, status = ?, error = ?
            WHERE id = ?
            """,
            (utcnow_iso(), status, error, run_id),
        )
        self.connection.commit()

    def upsert_result(self, result: AvailabilityResult) -> bool:
        """Persist a result and return True only when first seen."""

        now = utcnow_iso()
        try:
            self.connection.execute(
                """
                INSERT INTO availability_results (
                    dedupe_key, route_name, airline, flight_number, origin, destination,
                    departure_date, cabin, passengers, award_program, seats_available,
                    source, booking_reference, first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.dedupe_key,
                    result.route_name,
                    result.airline,
                    result.flight_number,
                    result.origin,
                    result.destination,
                    result.departure_date.isoformat(),
                    result.cabin,
                    result.passengers,
                    result.award_program,
                    result.seats_available,
                    result.source,
                    result.booking_reference,
                    now,
                    now,
                ),
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            self.connection.execute(
                """
                UPDATE availability_results
                SET seats_available = ?, source = ?, booking_reference = ?, last_seen_at = ?
                WHERE dedupe_key = ?
                """,
                (
                    result.seats_available,
                    result.source,
                    result.booking_reference,
                    now,
                    result.dedupe_key,
                ),
            )
            self.connection.commit()
            return False

    def alert_recently_sent(self, dedupe_key: str, suppression_hours: int) -> bool:
        threshold = datetime.now(UTC) - timedelta(hours=suppression_hours)
        row = self.connection.execute(
            """
            SELECT 1 FROM alerts
            WHERE dedupe_key = ? AND sent_at >= ?
            LIMIT 1
            """,
            (dedupe_key, threshold.isoformat()),
        ).fetchone()
        return row is not None

    def record_alert(self, result: AvailabilityResult, destination: str, message: str, dry_run: bool) -> None:
        self.connection.execute(
            """
            INSERT INTO alerts (dedupe_key, route_name, destination, sent_at, dry_run, message)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (result.dedupe_key, result.route_name, destination, utcnow_iso(), int(dry_run), message),
        )
        self.connection.commit()


def utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()
