# Issue: Add production deployment guide

## Labels

`documentation`, `deployment`, `operations`, `roadmap`

## Problem

The current docs explain local trials, but production monitoring needs a repeatable runbook.

## Proposed Work

- Document a small VPS or local-machine deployment path.
- Explain environment variables for Telegram secrets.
- Explain persistent SQLite storage location and backups.
- Add systemd, cron, or Docker examples.
- Add operational guidance for logs, restarts, route changes, and disabling alerts.

## Acceptance Criteria

- A production deployment guide exists under `docs/`.
- The guide starts with dry-run mode.
- The guide includes rollback/disable instructions.
- The guide does not require committing secrets.
