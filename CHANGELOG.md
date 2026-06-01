# Changelog

All notable changes to this project will be documented in this file.

The format follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses semantic versioning once release artifacts are published.

## [0.1.0] - 2026-06-01

### Added

- Initial Python package scaffold for the EVA Air award alert bot.
- `eva-award-alert` CLI with one-shot and watch modes.
- JSON watchlist loading and validation for EVA Air (`BR`) business award routes to Taipei (`TPE`).
- Recommended full route config and safer one-route trial config.
- Deterministic stub provider for local workflow validation without live ANA/EVA access.
- SQLite state store for search runs, availability results, and alert history.
- Duplicate suppression for unchanged award availability results.
- Telegram notifier with dry-run mode and real `sendMessage` support when configured.
- Trial, Telegram setup, ANA award usage, and hand-by-hand user guides.
- Unit tests for config loading and deduplication/alert behavior.
- MIT license and open-source project metadata drafts.

### Not Included Yet

- Live ANA Mileage Club or EVA Air award-search provider.
- Production deployment automation.
- Background service packaging.
- Automated booking, ticketing, payment, or credential storage.
