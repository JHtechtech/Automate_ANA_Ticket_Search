# EVA Air Award Ticket Alert Bot

A Python prototype for monitoring **EVA Air (`BR`) business-class award availability** from North America to Taipei (`TPE`) and sending Telegram-style alerts when new award seats are detected.

The repository name may still mention ANA because the likely live data-source spike is ANA Mileage Club partner-award search for EVA-operated award space. This project is **not** for ANA-operated flights, cash fares, automated booking, or payment.

## Current Status

This is a local trial prototype. It already includes:

- Watchlist configuration files for recommended EVA North America-to-Taipei routes.
- A safe one-route trial config.
- A CLI runner that can run once or continuously on a polling interval.
- A deterministic stub award-search provider.
- SQLite state for search runs, normalized availability results, and alerts.
- Telegram alert formatting with dry-run mode enabled by default.
- Tests for config loading and duplicate suppression.

The live ANA Mileage Club / EVA award-search provider is intentionally **not implemented yet**. Build and test the local workflow first, then add a live provider only after compliance, rate-limit, authentication, and technical constraints are reviewed.

## Product Scope

### In Scope

- EVA Air business-class award tickets only.
- North America `->` Taipei (`TPE`) routes.
- One passenger as the first target use case.
- New-seat detection and duplicate alert suppression.
- Telegram notification workflow.
- Local SQLite state.
- Dry-run trial mode before production.

### Out of Scope

- Cash fare monitoring.
- Automated booking, ticketing, or payment.
- Bypassing website protections or access controls.
- Storing loyalty-program passwords, passport data, payment details, or other sensitive travel documents.
- Multi-user SaaS features.

## Recommended Initial Routes

The full example watchlist in `config/watchlist.example.json` includes these recommended EVA North America-to-Taipei routes:

- `LAX -> TPE`
- `SFO -> TPE`
- `SEA -> TPE`
- `JFK -> TPE`
- `IAH -> TPE`
- `DFW -> TPE`
- `ORD -> TPE`
- `YVR -> TPE`
- `YYZ -> TPE`
- `IAD -> TPE`

For safer testing, start with the one-route trial config at `config/watchlist.trial.json` before using the full route list.

## Repository Layout

```text
config/
  watchlist.example.json   # Full recommended route watchlist
  watchlist.trial.json     # One-route dry-run trial watchlist
docs/
  ANA_TICKET_USAGE.md      # How to use the bot for ANA Mileage Club award tickets
  TELEGRAM_SETUP.md        # Telegram bot setup and smoke-test guide
  TRIAL_RUN.md             # Step-by-step trial guide
src/eva_award_alert/
  cli.py                   # CLI entry point
  config.py                # Watchlist loader
  models.py                # Domain models and validation
  notifier.py              # Telegram/dry-run alert formatting
  providers.py             # Provider interface and stub provider
  runner.py                # Search/state/alert orchestration
  state.py                 # SQLite persistence
tests/
  test_config.py           # Watchlist config tests
  test_runner.py           # Deduplication and alert-flow tests
```

## Setup

Use Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

If you do not install the package, prefix commands with `PYTHONPATH=src` and run `python -m eva_award_alert.cli ...` instead of `eva-award-alert ...`.

## Test the Prototype

Run the automated checks:

```bash
pytest -q
python -m compileall -q src
```

Run the one-route dry-run trial:

```bash
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

Expected first-run summary:

```text
routes_checked=1, results_seen=1, new_results=1, alerts_sent=1
```

Run the same command again against the same trial database:

```bash
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

Expected second-run summary:

```text
routes_checked=1, results_seen=1, new_results=0, alerts_sent=0
```

That second run proves duplicate suppression is working.

For detailed test-trial instructions, including SQLite inspection, watch-mode smoke testing, and optional real Telegram test messages, see `docs/TRIAL_RUN.md`. For BotFather, chat ID, token, and Telegram smoke-test setup, see `docs/TELEGRAM_SETUP.md`. For a step-by-step ANA Mileage Club award-ticket usage guide, see `docs/ANA_TICKET_USAGE.md`.

## CLI Usage

Run once with the trial config:

```bash
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

Run the full recommended-route stub workflow:

```bash
eva-award-alert --once --config config/watchlist.example.json --provider stub
```

Run continuously using `poll_interval_minutes` from the config:

```bash
eva-award-alert --watch --config config/watchlist.trial.json --provider stub
```

Supported providers today:

- `stub`: emits deterministic fake award availability for local testing.
- `stub-empty`: emits no availability.

Planned provider:

- `ana` / `ana-mileage-club`: reserved for a future compliance-reviewed ANA Mileage Club partner-award integration.

## Configuration

Each route defines the airline, airports, trip type, award program, cabin, passengers, date window, and alert behavior. Example:

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
  "alert": {"notify_on": "new_award_availability", "urgency": "high"}
}
```

Secrets are referenced by environment-variable name, not stored directly in config:

```json
{
  "telegram_bot_token_env": "TELEGRAM_BOT_TOKEN",
  "telegram_chat_id_env": "TELEGRAM_CHAT_ID"
}
```

Keep `dry_run` set to `true` until trial output is verified. When you are ready to send a real Telegram test alert, follow `docs/TELEGRAM_SETUP.md` and use environment variables for `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

## Data Model

SQLite tables are created automatically when the runner starts:

| Table | Purpose |
| --- | --- |
| `search_runs` | Tracks each route/provider check, status, timestamps, and errors. |
| `availability_results` | Stores normalized award results and their dedupe keys. |
| `alerts` | Stores alert attempts, destination, dry-run flag, sent time, and message text. |

## How the Local Flow Works

1. `config.py` loads and validates the watchlist.
2. `cli.py` builds the provider, notifier, SQLite store, and runner.
3. `runner.py` asks the provider for each route's availability.
4. `state.py` inserts new results or updates already-seen results.
5. New dedupe keys trigger `notifier.py` to print or send an alert.
6. Alerts are recorded so unchanged results do not notify repeatedly.

## Trial-to-Production Path

For ANA Mileage Club award-ticket usage specifically, follow `docs/ANA_TICKET_USAGE.md`. At a high level, use this order:

1. Run `pytest -q` and `python -m compileall -q src`.
2. Run the one-route dry-run trial in `docs/TRIAL_RUN.md`.
3. Confirm duplicate suppression by running the same trial twice.
4. Configure Telegram using `docs/TELEGRAM_SETUP.md`.
5. Optionally send one real Telegram message with the stub provider.
6. Confirm the first real route/date window.
7. Research and document the live provider approach.
8. Implement the live provider behind the existing `AwardSearchProvider` interface.
9. Add conservative rate limits, retries, timeouts, and observability.
10. Only then consider production scheduling/deployment.

## Compliance and Safety

This project must not automate bookings, purchases, login bypasses, or technical-control circumvention. Any live award-search provider must be reviewed against the selected data source's terms, authentication requirements, rate limits, and technical constraints.

## Development Notes

Common commands:

```bash
pytest -q
python -m compileall -q src
git diff --check
```

Reset local trial state:

```bash
rm -f data/eva_award_alert_trial.db data/eva_award_alert.db
```
