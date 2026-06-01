# Telegram Setup Guide

Use this guide when you are ready to connect the local EVA award-alert prototype to your own Telegram account. Start with dry-run mode first, then send one real stub alert, and only later connect a live award-search provider.

References used for this setup:

- Telegram BotFather guide: <https://core.telegram.org/bots/features#botfather>
- Telegram Bot API `sendMessage`: <https://core.telegram.org/bots/api#sendmessage>
- Telegram Bot API `getUpdates`: <https://core.telegram.org/bots/api#getupdates>

## 1. Create a Bot with BotFather

1. Open Telegram.
2. Search for the verified `@BotFather` account.
3. Send `/newbot`.
4. Choose a display name, for example `EVA Award Alert Trial`.
5. Choose a username that ends with `bot`, for example `eva_award_alert_trial_bot`.
6. Copy the bot token that BotFather returns.

Important: the token can control your bot. Do not commit it to Git, paste it into screenshots, or store it in `config/*.json`.

## 2. Optional Bot Profile Settings

These settings are not required for alerts, but they make the bot easier to recognize.

In `@BotFather`, use `/mybots`, select your bot, then set:

- **Description**: `Sends private EVA Air business award availability alerts.`
- **About**: `EVA award alert bot.`
- **Botpic**: optional.
- **Commands**: optional; this prototype sends outbound alerts and does not need command handling yet.

If you add commands, keep them simple:

```text
start - Start the bot chat so alerts can be delivered
help - Show bot purpose and owner notes
```

## 3. Start a Private Chat with Your Bot

Telegram bots cannot message a private user until that user starts the conversation.

1. Open your new bot in Telegram.
2. Tap **Start** or send `/start`.
3. Send any short message such as `test`.

This creates an update that you can use to discover your `chat_id`.

## 4. Export the Bot Token Locally

In your terminal:

```bash
export TELEGRAM_BOT_TOKEN='replace-with-your-bot-token'
```

Verify the token works:

```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

Expected result: JSON with `"ok":true` and your bot username.

## 5. Find Your Private Chat ID

After you send `/start` or `test` to the bot, run:

```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates"
```

Look for a response shape like this:

```json
{
  "message": {
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "text": "test"
  }
}
```

Export that `id` value:

```bash
export TELEGRAM_CHAT_ID='123456789'
```

If `getUpdates` returns an empty result:

1. Send another message to the bot in Telegram.
2. Run `getUpdates` again.
3. If you previously configured a webhook, remove it first:

```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook?drop_pending_updates=false"
```

## 6. Send One Manual Telegram API Message

Before using the project CLI, confirm Telegram itself can deliver a message:

```bash
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=EVA award alert bot Telegram test"
```

Expected result: Telegram receives the message and the API returns `"ok":true`.

## 7. Enable One Real Stub Alert from This Project

Keep the committed configs dry-run by default. For a real Telegram smoke test, copy the trial config to `/tmp` and change only the temporary copy:

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
```

Run the project with the stub provider:

```bash
eva-award-alert --once --config /tmp/watchlist.telegram-test.json --provider stub
```

Expected result:

- Telegram receives one fake EVA business award alert.
- The CLI summary includes `alerts_sent=1`.
- Running the same command again with the same `/tmp/eva_award_alert_telegram_test.db` should not send a duplicate alert.

## 8. Group Chat or Channel Alerts

Private chat is the simplest setup. If you prefer a group or channel:

### Group Chat

1. Add the bot to the group.
2. Send a message in the group, such as `/start@your_bot_username`.
3. Run `getUpdates` and look for the group `chat.id`.
4. Export that group ID as `TELEGRAM_CHAT_ID`.

Group IDs are often negative numbers.

### Channel

For a public channel, you can usually use the channel username format as the chat ID:

```bash
export TELEGRAM_CHAT_ID='@your_channel_username'
```

Add the bot to the channel with permission to post messages. For private channels, use Telegram's returned numeric chat ID after the bot has access.

## 9. Recommended Trial-to-Production Settings

| Stage | Provider | Config | `dry_run` | Destination |
| --- | --- | --- | --- | --- |
| Local unit tests | `stub` | test fixtures | `true` | Console only |
| One-route trial | `stub` | `config/watchlist.trial.json` | `true` | Console only |
| Telegram smoke test | `stub` | `/tmp/watchlist.telegram-test.json` | `false` | Private chat |
| Full-route dry run | `stub` | `config/watchlist.example.json` | `true` | Console only |
| Future live trial | live provider | copied config | start with `true` | Console first |
| Future production | live provider | production config | `false` | Private chat/group/channel |

## 10. Troubleshooting

### `getUpdates` is empty

- Make sure you sent `/start` or a new message to the bot.
- Make sure you are using the correct bot token.
- Delete any webhook with `deleteWebhook` before using `getUpdates`.

### Telegram says `chat not found`

- For private chat alerts, you probably did not start the bot from your Telegram account yet.
- For group alerts, make sure the bot is in the group and use the numeric group chat ID.
- For channel alerts, make sure the bot can post to the channel.

### Telegram says `Unauthorized`

- The token is wrong, revoked, or copied with extra spaces.
- Regenerate a token in `@BotFather` if you think it leaked.

### No duplicate alert is sent on the second test run

That is expected. The SQLite state already saw the stub availability result. Delete the temporary database to repeat first-run behavior:

```bash
rm -f /tmp/eva_award_alert_telegram_test.db
```

## Security Checklist

- Keep `TELEGRAM_BOT_TOKEN` in environment variables or a local secret manager.
- Never commit real tokens or chat IDs if the repository is public.
- Use a separate test bot for trial runs.
- Rotate the token with BotFather if it is exposed.
- Keep committed configs in `dry_run` mode unless there is a strong reason to do otherwise.
