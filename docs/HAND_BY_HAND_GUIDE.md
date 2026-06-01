# Hand-by-Hand Guide: Using the EVA / ANA Award Alert Bot

This guide is written for someone who wants to use the tool from scratch, one step at a time. You do not need to understand the code internals to follow it.

The tool is currently a **safe local prototype**. It can run with fake/stub award data, store results locally, prevent duplicate alerts, and send Telegram messages. It does **not** search live ANA/EVA award inventory yet.

## What You Will Accomplish

By the end of this guide, you will have:

1. Installed the project locally.
2. Run the automated checks.
3. Run a one-route trial alert in dry-run mode.
4. Confirmed duplicate suppression works.
5. Created a Telegram bot.
6. Sent one real Telegram test alert using fake/stub data.
7. Learned how to edit the watchlist routes.
8. Learned how to reset local state and troubleshoot common issues.

## Important Safety Notes

- Keep committed configs in `dry_run` mode.
- Do not commit Telegram bot tokens or chat IDs.
- Do not use stub alerts for booking decisions; stub availability is fake.
- The live ANA/EVA provider is not implemented yet.
- This tool should alert you to manually review and book; it should not book automatically.

## Step 0: Confirm Your Computer Has Python

Open a terminal and run:

```bash
python --version
```

If that fails, try:

```bash
python3 --version
```

You need Python 3.11 or newer. If `python3` works but `python` does not, use `python3` anywhere this guide says `python`.

## Step 1: Go to the Project Folder

From your terminal, move into the repository folder:

```bash
cd /path/to/Automate_ANA_Ticket_Search
```

Confirm the files are there:

```bash
pwd
python -c "from pathlib import Path; print(Path('pyproject.toml').exists(), Path('config/watchlist.trial.json').exists())"
```

Expected output should include `True True`.

## Step 2: Create a Virtual Environment

Create an isolated Python environment:

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

After activation, your terminal prompt may show `(.venv)`.

## Step 3: Install the Tool

Upgrade packaging tools:

```bash
python -m pip install --upgrade pip
```

Install this project in editable mode with test dependencies:

```bash
python -m pip install -e '.[dev]'
```

Confirm the command-line tool is available:

```bash
eva-award-alert --help
```

If `eva-award-alert` is not found, use this fallback form:

```bash
PYTHONPATH=src python -m eva_award_alert.cli --help
```

## Step 4: Run the Automated Checks

Run tests:

```bash
pytest -q
```

Expected result:

```text
3 passed
```

Run Python compilation check:

```bash
python -m compileall -q src
```

Expected result: no output and exit success.

If either command fails, stop and fix the local environment before continuing.

## Step 5: Understand the Two Watchlist Files

There are two main config files:

| File | Use Case |
| --- | --- |
| `config/watchlist.trial.json` | One-route safe trial. Start here. |
| `config/watchlist.example.json` | Full recommended North America-to-Taipei route list. Use later. |

Start with the trial file because it has only one route and is easier to verify.

## Step 6: Open the Trial Watchlist

View the trial config:

```bash
cat config/watchlist.trial.json
```

Important fields:

- `origin`: starting airport, such as `SFO`.
- `destination`: Taipei, `TPE`.
- `airline`: EVA Air code, `BR`.
- `award_program`: `ANA Mileage Club`.
- `cabin`: `business`.
- `passengers`: usually `1`.
- `date_window.start` and `date_window.end`: dates to monitor.
- `notifier.dry_run`: should be `true` for the first tests.

## Step 7: Run the First Dry-Run Alert

Run the tool once with the stub provider:

```bash
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

If you need the fallback command:

```bash
PYTHONPATH=src python -m eva_award_alert.cli --once --config config/watchlist.trial.json --provider stub
```

Expected output includes a fake alert like:

```text
EVA business award seat found
Route: SFO -> TPE
Award program: ANA Mileage Club
Source: stub
```

Expected summary:

```text
Run complete: routes_checked=1, results_seen=1, new_results=1, alerts_sent=1
```

This means the local workflow works: config -> provider -> state -> notifier.

## Step 8: Run It Again to Confirm Duplicate Suppression

Run the same command again:

```bash
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

Expected summary:

```text
Run complete: routes_checked=1, results_seen=1, new_results=0, alerts_sent=0
```

This is good. The bot already saw that fake award seat and did not alert you again.

## Step 9: Inspect the Local Database

The trial config writes state to:

```text
data/eva_award_alert_trial.db
```

List the database tables:

```bash
sqlite3 data/eva_award_alert_trial.db '.tables'
```

Inspect search runs:

```bash
sqlite3 data/eva_award_alert_trial.db 'SELECT id, route_name, provider, status FROM search_runs;'
```

Inspect stored availability:

```bash
sqlite3 data/eva_award_alert_trial.db 'SELECT origin, destination, departure_date, cabin, seats_available, award_program FROM availability_results;'
```

Inspect alerts:

```bash
sqlite3 data/eva_award_alert_trial.db 'SELECT route_name, destination, dry_run, sent_at FROM alerts;'
```

If `sqlite3` is not installed, you can skip this step. The tests and CLI summaries are enough for the first trial.

## Step 10: Reset the Trial if You Want to See the First Alert Again

Delete the trial database:

```bash
rm -f data/eva_award_alert_trial.db
```

Run the trial again:

```bash
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

Because the database was deleted, the bot treats the stub seat as new again.

## Step 11: Create a Telegram Bot

Open Telegram and talk to `@BotFather`.

1. Send `/newbot`.
2. Pick a display name, such as `EVA Award Alert Trial`.
3. Pick a username ending in `bot`, such as `eva_award_alert_trial_bot`.
4. Copy the bot token.

Do not paste the token into Git or a committed config file.

## Step 12: Start a Chat with Your Bot

1. Open your new bot in Telegram.
2. Tap **Start** or send `/start`.
3. Send a message such as `test`.

Bots cannot send private messages to you until you start the conversation.

## Step 13: Export Telegram Environment Variables

In your terminal:

```bash
export TELEGRAM_BOT_TOKEN='replace-with-your-bot-token'
```

Check that the token works:

```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

Expected: JSON with `"ok":true`.

Find your chat ID:

```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates"
```

Look for:

```json
"chat": {"id": 123456789}
```

Export it:

```bash
export TELEGRAM_CHAT_ID='123456789'
```

If `getUpdates` is empty, send another message to your bot and run the command again.

## Step 14: Send a Manual Telegram Test Message

Before connecting the project, test Telegram directly:

```bash
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=EVA award alert bot manual Telegram test"
```

Expected: you receive a Telegram message.

## Step 15: Send One Real Telegram Alert from the Project

Do not edit the committed trial config directly. Copy it to `/tmp`:

```bash
cp config/watchlist.trial.json /tmp/watchlist.telegram-test.json
```

Change the temporary copy so `dry_run` is false and the database is temporary:

```bash
python - <<'PY'
import json
from pathlib import Path
path = Path('/tmp/watchlist.telegram-test.json')
data = json.loads(path.read_text())
data['settings']['notifier']['dry_run'] = False
data['settings']['database_path'] = '/tmp/eva_award_alert_telegram_test.db'
path.write_text(json.dumps(data, indent=2) + '\n')
PY
```

Run the project:

```bash
eva-award-alert --once --config /tmp/watchlist.telegram-test.json --provider stub
```

Expected:

- You receive one Telegram alert.
- The alert is fake/stub data.
- The CLI summary includes `alerts_sent=1`.

Run it again:

```bash
eva-award-alert --once --config /tmp/watchlist.telegram-test.json --provider stub
```

Expected:

- No duplicate Telegram message.
- The CLI summary includes `alerts_sent=0`.

## Step 16: Edit the Trial Route for Your Real Target

Open `config/watchlist.trial.json` in your editor.

For the first real planning trial, change only:

```json
"origin": "SFO",
"destination": "TPE",
"passengers": 1,
"date_window": {"start": "2026-10-01", "end": "2026-10-03"}
```

Examples:

### LAX to Taipei

```json
"origin": "LAX",
"destination": "TPE"
```

### JFK to Taipei

```json
"origin": "JFK",
"destination": "TPE"
```

### Wider date window

```json
"date_window": {"start": "2026-11-01", "end": "2026-11-14"}
```

Keep these unchanged for now:

```json
"airline": "BR",
"search_type": "award",
"award_program": "ANA Mileage Club",
"cabin": "business"
```

## Step 17: Run the Full Recommended Route List Later

After the one-route trial works, you can run the full example watchlist:

```bash
eva-award-alert --once --config config/watchlist.example.json --provider stub
```

This will produce one fake stub result per configured route on the first run.

The full route list includes:

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

## Step 18: Try Watch Mode

Watch mode runs repeatedly using `poll_interval_minutes` from the config.

```bash
eva-award-alert --watch --config config/watchlist.trial.json --provider stub
```

Stop it with `Ctrl+C`.

For a quick smoke test, copy the config to `/tmp` and set the interval to `1` minute instead of waiting 15 minutes.

## Step 19: Understand What Happens When an Alert Arrives

When a future live provider exists and Telegram sends an alert, do this:

1. Open ANA Mileage Club manually.
2. Search the same route and date.
3. Confirm the operating airline is EVA Air / `BR`.
4. Confirm the cabin is business.
5. Confirm the seat is actually bookable, not waitlisted or mixed cabin.
6. Book manually if you want it.

The bot should notify you quickly. It should not make the booking decision for you.

## Step 20: Current Limitation — No Live ANA Search Yet

Right now, these commands use `--provider stub`, which means fake data.

A future live provider should be added behind this interface:

```bash
eva-award-alert --watch --config /path/to/your/config.json --provider ana-mileage-club
```

Until that provider is implemented, use this tool to validate:

- Config format.
- Telegram delivery.
- Duplicate suppression.
- SQLite state.
- Operational workflow.

## Common Problems and Fixes

### `eva-award-alert: command not found`

Run:

```bash
python -m pip install -e '.[dev]'
```

Or use:

```bash
PYTHONPATH=src python -m eva_award_alert.cli --once --config config/watchlist.trial.json --provider stub
```

### The second run does not send an alert

That is expected. Duplicate suppression is working. Delete the database if you want to reset:

```bash
rm -f data/eva_award_alert_trial.db /tmp/eva_award_alert_telegram_test.db
```

### Telegram says `chat not found`

Start a chat with your bot first, then export the correct `TELEGRAM_CHAT_ID`.

### Telegram says `Unauthorized`

Your token is wrong or expired. Regenerate it in `@BotFather`.

### I changed config but behavior did not change

Check which config file you are passing to `--config`. If you copied a config to `/tmp`, edits to `config/watchlist.trial.json` will not affect the `/tmp` copy.

## The Short Version

If you already installed everything, the everyday trial commands are:

```bash
pytest -q
eva-award-alert --once --config config/watchlist.trial.json --provider stub
eva-award-alert --once --config config/watchlist.trial.json --provider stub
```

First run should alert. Second run should not duplicate.
