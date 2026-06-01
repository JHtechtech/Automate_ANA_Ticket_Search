#!/usr/bin/env bash
set -euo pipefail

# Helper script for maintainers with GitHub CLI access.
# This repository environment may not have `gh` installed or authenticated, so
# this script is intentionally opt-in and safe to run only when you control the
# target GitHub repository.

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed. Install it before running this script." >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run: gh auth login" >&2
  exit 1
fi

DESCRIPTION="Safe local prototype for EVA Air business-class award alerting via ANA Mileage Club-style partner award monitoring and Telegram dry-run alerts."
TOPICS=(award-travel ana-mileage-club eva-air telegram-bot flight-alerts travel-tools python sqlite open-source)

gh repo edit --description "$DESCRIPTION"
for topic in "${TOPICS[@]}"; do
  gh repo edit --add-topic "$topic"
done

gh release create v0.1.0 \
  --title "v0.1.0 - Initial Local Prototype" \
  --notes-file docs/releases/v0.1.0.md

for issue_file in docs/issues/*.md; do
  title=$(sed -n '1s/^# Issue: //p' "$issue_file")
  gh issue create --title "$title" --body-file "$issue_file"
done
