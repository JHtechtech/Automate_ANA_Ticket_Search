# Trial Run Guide

Use this guide to test the EVA award alert bot safely before any production deployment or live award-search integration.

The trial goal is to prove the local workflow end to end:

1. Load a watchlist configuration.
2. Run the scheduled runner once or in watch mode.
3. Use the stub provider to simulate one EVA business award seat.
4. Store search runs, availability results, and alerts in SQLite.
5. Verify duplicate suppression.
6. Optionally send a real Telegram test message after dry-run output looks correct.

## Trial Safety Rules

- Keep `dry_run` set to `true` for the first trial.
- Use the `stub` provider until the live provider has a separate compliance review.
- Do not put Telegram tokens, chat IDs, airline credentials, or loyalty-program passwords in source control.
- Use a temporary SQLite database under `data/` or `/tmp/` so trial state can be deleted easily.
- Treat all stub availability as fake; never use it for booking decisions.

## 1. Create a Local Python Environment

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

If you do not want a virtual environment, you can run the prototype with `PYTHONPATH=src`, but the editable install is closer to how a real deployment will execute the CLI.

## 2. Run the Automated Checks

```bash
pytest -q
python -m compileall -q src
```

Both commands should pass before you run a trial.

## 3. Run a One-Route Dry-Run Trial

The repository includes `config/watchlist.trial.json`, which monitors only one trial route and keeps Telegram in dry-run mode.

```bash
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

Expected behavior on the first run:

- The CLI prints one fake EVA business award alert.
- The summary ends with `routes_checked=1`, `results_seen=1`, `new_results=1`, and `alerts_sent=1`.
- SQLite state is written to `data/eva_award_alert_trial.db`.

Run the exact same command again:

```bash
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

Expected behavior on the second run:

- No alert message is printed.
- The summary ends with `routes_checked=1`, `results_seen=1`, `new_results=0`, and `alerts_sent=0`.
- This proves duplicate suppression is working for unchanged availability.

## 4. Inspect the Trial Database

```bash
sqlite3 data/eva_award_alert_trial.db '.tables'
sqlite3 data/eva_award_alert_trial.db 'SELECT route_name, status, started_at, completed_at FROM search_runs;'
sqlite3 data/eva_award_alert_trial.db 'SELECT route_name, origin, destination, departure_date, cabin, seats_available FROM availability_results;'
sqlite3 data/eva_award_alert_trial.db 'SELECT route_name, destination, dry_run, sent_at FROM alerts;'
```

You should see one stored availability result and one stored alert after running the same stub trial twice.

## 5. Test Watch Mode Without Waiting 15 Minutes

For a short watch-mode smoke test, copy the trial config and temporarily set `poll_interval_minutes` to `1`.

```bash
cp config/watchlist.trial.json /tmp/watchlist.trial.fast.json
python - <<'PY'
import json
from pathlib import Path
path = Path('/tmp/watchlist.trial.fast.json')
data = json.loads(path.read_text())
data['settings']['poll_interval_minutes'] = 1
data['settings']['database_path'] = '/tmp/eva_award_alert_watch_trial.db'
path.write_text(json.dumps(data, indent=2) + '\n')
PY
eva-award-alert --watch --config /tmp/watchlist.trial.fast.json --provider stub
```

Stop the process with `Ctrl+C` after two cycles. The first cycle should alert; later cycles should not duplicate the same alert.

## 6. Optional: Send a Real Telegram Test Alert

Only do this after dry-run output looks correct.

1. Create a Telegram bot with BotFather and save the bot token locally.
2. Find the target chat ID.
3. Export secrets in your shell, not in a committed file:

```bash
export TELEGRAM_BOT_TOKEN='replace-with-your-token'
export TELEGRAM_CHAT_ID='replace-with-your-chat-id'
```

4. Copy the trial config outside the repository or to `/tmp`, then set `dry_run` to `false` and use a fresh database path:

```bash
cp config/watchlist.trial.json /tmp/watchlist.telegram-test.json
python - <<'PY'
import json
from pathlib import Path
path = Path('/tmp/watchlist.telegram-test.json')
data = json.loads(path.read_text())
data['settings']['notifier']['dry_run'] = False
data['settings']['database_path'] = '/tmp/eva_award_alert_telegram_test.db'
path.write_text(json.dumps(data, indent=2) + '\n')
PY
eva-award-alert --once --config /tmp/watchlist.telegram-test.json --provider stub
```

Expected behavior: Telegram receives one fake/stub alert. If you run the command again against the same database, it should not send a duplicate.

## 7. Trial Exit Criteria

The prototype is ready for the next implementation phase when all of these are true:

- Unit tests pass.
- A dry-run trial produces one alert on the first run.
- A second dry-run trial against the same database produces no duplicate alert.
- The SQLite tables contain the expected search run, availability result, and alert records.
- Optional Telegram test sends exactly one message using stub data.
- The first real route/date window has been confirmed.
- The live award-search provider approach has been reviewed for compliance and technical feasibility.

## 8. Reset Trial State

Delete the trial database when you want to repeat the first-run behavior:

```bash
rm -f data/eva_award_alert_trial.db /tmp/eva_award_alert_watch_trial.db /tmp/eva_award_alert_telegram_test.db
```

## What Comes After Trial

After the trial succeeds, the next code milestone should not jump straight to production. The next step is a provider spike that implements a live award-search provider behind the existing `AwardSearchProvider` interface, with clear rate limits, error handling, and compliance boundaries.
