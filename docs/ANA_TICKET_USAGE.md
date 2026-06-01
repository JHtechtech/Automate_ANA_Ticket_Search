# Using the Alert Bot for ANA Mileage Club Award Tickets

This guide explains how to use this project for **ANA Mileage Club award-ticket monitoring**, especially the original target use case: finding **EVA Air (`BR`) business-class partner-award seats between North America and Taipei (`TPE`)** that can potentially be booked through ANA Mileage Club.

> Note: If you said "Anna tickets," this guide assumes you mean **ANA Mileage Club award tickets**. The current code does not perform live ANA searches yet; it gives you a safe trial workflow and the structure needed to add a compliance-reviewed ANA provider later.

Official references to review before any live provider work:

- ANA Mileage Club flight awards overview: <https://www.ana.co.jp/en/jp/guide/amc/award/>
- ANA International Flight Awards: <https://www.ana.co.jp/en/us/amc/international-flight-awards/>
- ANA partner airlines page listing EVA Air: <https://www.ana.co.jp/en/us/amc/partner-airlines/>
- ANA partner flight award terms / usage conditions: <https://www.ana.co.jp/en/jp/guide/amc/award/tk/usage/>
- ANA itineraries and airlines that cannot be requested online: <https://www.ana.co.jp/en/jp/guide/amc/award/international/unavailable-application/>

## What This Bot Can Do Today

Today, the bot can safely test the local workflow:

1. Load a watchlist of ANA/EVA partner-award routes.
2. Simulate award availability with the `stub` provider.
3. Store search runs, availability results, and alerts in SQLite.
4. Format Telegram alerts.
5. Suppress duplicate alerts for the same unchanged award seat.

This is enough to validate your local setup, Telegram setup, route configuration, state database, and alert behavior before live ANA provider work begins.

## What This Bot Cannot Do Yet

The bot does **not** currently:

- Log in to ANA Mileage Club.
- Search live ANA award inventory.
- Search live EVA inventory.
- Hold, book, ticket, or pay for an award.
- Bypass ANA or EVA website protections.
- Store ANA Mileage Club passwords or sensitive traveler details.

Any live ANA integration should be added only after reviewing ANA's terms, authentication behavior, rate limits, and technical constraints.

## Recommended Workflow

Use this order:

1. Confirm your ANA Mileage Club booking goal.
2. Configure one route in `config/watchlist.trial.json`.
3. Run the stub provider locally.
4. Verify duplicate suppression.
5. Configure Telegram and send one stub alert.
6. Confirm the exact ANA/EVA award-search path manually in the ANA website.
7. Add a live provider spike behind the existing provider interface.
8. Run the live provider in dry-run mode first.
9. Only then consider scheduled production monitoring.

## 1. Confirm the ANA Award Goal

Write down the exact award you want before changing the config:

| Field | Example |
| --- | --- |
| Award program | `ANA Mileage Club` |
| Operating airline | `EVA Air` / `BR` |
| Origin | `SFO` |
| Destination | `TPE` |
| Cabin | `business` |
| Passengers | `1` |
| Trip type | `one_way` for monitoring, even if final ANA booking rules require round-trip or multi-segment handling |
| Date window | `2026-10-01` to `2026-10-14` |

The key idea is that the alert bot should detect the seat quickly; you still review and book manually in ANA.

## 2. Configure a Safe Trial Route

Start with `config/watchlist.trial.json`, not the full route list.

Example route block:

```json
{
  "name": "Trial SFO to Taipei EVA business award",
  "airline": "BR",
  "airline_name": "EVA Air",
  "origin": "SFO",
  "destination": "TPE",
  "trip_type": "one_way",
  "search_type": "award",
  "award_program": "ANA Mileage Club",
  "cabin": "business",
  "passengers": 1,
  "date_window": {"start": "2026-10-01", "end": "2026-10-03"},
  "alert": {
    "notify_on": "new_award_availability",
    "urgency": "high"
  }
}
```

Change only these fields first:

- `origin`
- `destination`
- `date_window.start`
- `date_window.end`
- `passengers`

Keep these fields unchanged for the first ANA/EVA trial:

- `airline`: `BR`
- `search_type`: `award`
- `award_program`: `ANA Mileage Club`
- `cabin`: `business`
- `notifier.dry_run`: `true`

## 3. Install and Test Locally

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
pytest -q
python -m compileall -q src
```

If these checks fail, fix them before testing Telegram or adding a live provider.

## 4. Run the ANA/EVA Stub Trial

Run the trial once:

```bash
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

Expected behavior:

- The bot prints one fake EVA business award alert.
- The alert says the award program is ANA Mileage Club.
- The summary includes `routes_checked=1`, `results_seen=1`, `new_results=1`, and `alerts_sent=1`.

Run the same command again:

```bash
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

Expected behavior:

- No second alert is printed.
- The summary includes `new_results=0` and `alerts_sent=0`.

That confirms the bot will not spam you repeatedly for the same unchanged award result.

## 5. Inspect the Local State

The trial config writes SQLite state to `data/eva_award_alert_trial.db`.

```bash
sqlite3 data/eva_award_alert_trial.db '.tables'
sqlite3 data/eva_award_alert_trial.db 'SELECT route_name, provider, status FROM search_runs;'
sqlite3 data/eva_award_alert_trial.db 'SELECT origin, destination, departure_date, cabin, seats_available, award_program FROM availability_results;'
sqlite3 data/eva_award_alert_trial.db 'SELECT route_name, dry_run, sent_at FROM alerts;'
```

You should see:

- At least two `search_runs` after running the command twice.
- One `availability_results` row for the stubbed award seat.
- One `alerts` row because the second run was suppressed.

## 6. Connect Telegram

Follow `docs/TELEGRAM_SETUP.md` to:

1. Create a bot with `@BotFather`.
2. Export `TELEGRAM_BOT_TOKEN`.
3. Start a private chat with your bot.
4. Find and export `TELEGRAM_CHAT_ID`.
5. Send one manual `sendMessage` test.

Then copy the trial config to `/tmp` and disable dry-run only in the copy:

```bash
cp config/watchlist.trial.json /tmp/watchlist.ana-telegram-test.json
python - <<'PY'
import json
from pathlib import Path
path = Path('/tmp/watchlist.ana-telegram-test.json')
data = json.loads(path.read_text())
data['settings']['notifier']['dry_run'] = False
data['settings']['database_path'] = '/tmp/eva_award_alert_ana_telegram_test.db'
path.write_text(json.dumps(data, indent=2) + '\n')
PY
eva-award-alert --once --config /tmp/watchlist.ana-telegram-test.json --provider stub
```

Expected behavior: Telegram receives one fake ANA Mileage Club / EVA business award alert.

## 7. Manually Validate the ANA Search Path

Before coding a live provider, manually perform the search in ANA Mileage Club so you know exactly what the provider must reproduce.

Record these details:

- Does ANA show the route online?
- Does the search require round-trip input even if you only care about one direction?
- Does EVA Air appear as `BR` or `EVA Air` in the result?
- What cabin labels does ANA use for business class?
- What result means "available" versus waitlisted, unavailable, or mixed cabin?
- What errors appear when no seats are available?
- Are there date-range, calendar, or session limitations?
- Are there restrictions requiring a service-center request for the route or itinerary?

Do not automate login or search behavior until these details and the compliance boundaries are clear.

## 8. Add the Live ANA Provider Later

When ready, implement the live provider behind the existing `AwardSearchProvider` interface in `src/eva_award_alert/providers.py`.

The provider must return normalized `AvailabilityResult` objects with:

- `route_name`
- `airline`
- `flight_number`
- `origin`
- `destination`
- `departure_date`
- `cabin`
- `passengers`
- `award_program`
- `seats_available`
- `source`
- `booking_reference`

Do not change the runner, notifier, or state layers unless the provider proves the current interface is insufficient.

## 9. Live Provider Safety Requirements

A live ANA provider should include:

- Conservative polling intervals.
- Timeouts.
- Retry limits.
- Backoff after errors.
- Clear logging.
- Dry-run mode by default.
- No hard-coded credentials.
- No committed cookies or session tokens.
- No automatic booking or purchase flow.
- A way to disable routes quickly if the provider starts failing.

## 10. How to Use It Day to Day After Live Provider Exists

Once a live provider exists and has passed trial testing:

1. Update your copied production config with real route/date windows.
2. Keep only the routes you truly care about enabled.
3. Start in dry-run mode and review logs.
4. Turn Telegram on after dry-run output looks correct.
5. Run with `--watch` on a small VPS, local machine, or scheduled job.
6. When you receive an alert, immediately verify manually in ANA Mileage Club.
7. Book manually if the award is still available.
8. Leave duplicate suppression enabled so unchanged seats do not spam Telegram.

Example future command:

```bash
eva-award-alert --watch --config /path/to/your/ana-eva-production-watchlist.json --provider ana-mileage-club
```

## Resetting the Trial

Delete trial databases when you want to repeat the first-alert behavior:

```bash
rm -f data/eva_award_alert_trial.db /tmp/eva_award_alert_ana_telegram_test.db
```
