"""Notification formatting and delivery."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from .models import AvailabilityResult


class Notifier(Protocol):
    dry_run: bool

    def send(self, result: AvailabilityResult) -> str:
        """Send an alert and return the message text."""


@dataclass
class TelegramNotifier:
    """Telegram notifier with dry-run support.

    In dry-run mode the notifier prints the message and does not call Telegram.
    """

    bot_token_env: str = "TELEGRAM_BOT_TOKEN"
    chat_id_env: str = "TELEGRAM_CHAT_ID"
    dry_run: bool = True

    @property
    def destination(self) -> str:
        if self.dry_run:
            return "dry-run"
        return os.environ[self.chat_id_env]

    def send(self, result: AvailabilityResult) -> str:
        message = format_alert(result)
        if self.dry_run:
            print(message)
            return message

        bot_token = os.environ[self.bot_token_env]
        chat_id = os.environ[self.chat_id_env]
        payload = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            json.loads(response.read().decode("utf-8"))
        return message


def build_notifier(config: dict[str, object]) -> TelegramNotifier:
    return TelegramNotifier(
        bot_token_env=str(config.get("telegram_bot_token_env", "TELEGRAM_BOT_TOKEN")),
        chat_id_env=str(config.get("telegram_chat_id_env", "TELEGRAM_CHAT_ID")),
        dry_run=bool(config.get("dry_run", True)),
    )


def format_alert(result: AvailabilityResult) -> str:
    lines = [
        "EVA business award seat found",
        f"Route: {result.origin} -> {result.destination}",
        f"Date: {result.departure_date.isoformat()}",
        f"Passengers: {result.passengers}",
        f"Cabin: {result.cabin.title()}",
        f"Seats available: {result.seats_available}",
        f"Award program: {result.award_program}",
        f"Airline: EVA Air ({result.airline})",
        f"Flight: {result.flight_number}",
        f"Source: {result.source}",
        "Action: Review and book manually as soon as possible",
    ]
    if result.booking_reference:
        lines.append(f"Reference: {result.booking_reference}")
    return "\n".join(lines)
