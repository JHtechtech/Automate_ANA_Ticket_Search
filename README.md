# Automate ANA Ticket Search

A planning-first repository for building an automated monitor that searches selected All Nippon Airways (ANA) routes for business class award or cash-ticket availability and sends timely Telegram alerts when matching seats appear.

> **Status:** Planning and product definition. No production scraper, bot, or scheduler has been implemented yet.

## Problem Statement

Premium-cabin ANA availability can appear and disappear quickly. Manually checking the same routes, dates, cabin, and passenger counts is repetitive and easy to miss. This project aims to define and later build a lightweight alerting platform that:

- Watches user-defined ANA routes and date ranges.
- Filters for business class availability.
- Sends Telegram notifications as soon as a matching result is detected.
- Keeps a simple history of checks and alerts so duplicate alerts can be controlled.

## Initial Product Goal

Create a reliable personal monitoring tool before expanding into a broader platform. The first usable version should be small, auditable, and easy to run on a schedule.

### MVP Scope

The minimum viable product should support:

1. **Route watchlist**
   - Origin airport, destination airport, one-way or round-trip preference.
   - Target departure date or flexible date window.
   - Passenger count.
   - Cabin preference: business class first.

2. **Scheduled search runner**
   - Executes searches at a configurable interval.
   - Records each check attempt and outcome.
   - Applies rate limits and backoff to avoid aggressive querying.

3. **Availability detection**
   - Normalizes search results into a consistent internal format.
   - Compares new results against previously seen availability.
   - Flags newly available options for alerting.

4. **Telegram alerts**
   - Sends concise messages containing route, date, cabin, price or award details when available, and a booking/search link if supported.
   - Prevents repeated alerts for the same unchanged result.

5. **Configuration-first operation**
   - Stores watched routes and alert preferences in a simple local config file for the first version.
   - Keeps secrets, such as the Telegram bot token, in environment variables.

## Non-Goals for the First Version

The first version should intentionally avoid:

- Automated booking or payment.
- Circumventing website protections, authentication controls, or terms of service.
- Multi-user SaaS account management.
- Complex dashboards before the basic alerting workflow is proven.
- Storing payment details, passport information, or other sensitive travel documents.

## Key Design Principles

- **Compliance-aware:** Prefer official APIs, authorized integrations, or user-permitted data sources where available. If browser automation is later considered, keep it conservative and respectful of applicable terms.
- **Small and observable:** Start with logs, local storage, and clear alert history before adding more infrastructure.
- **Configurable but simple:** A text-based watchlist should be enough for the MVP.
- **Duplicate-safe alerts:** Alert only when a result is new or materially changed.
- **Failure-tolerant:** Temporary search failures should not crash the service or spam Telegram.

## Proposed Architecture

```text
+-------------------+       +-------------------+       +-------------------+
| Watchlist Config  | ----> | Scheduled Runner  | ----> | Search Provider   |
+-------------------+       +-------------------+       +-------------------+
                              |                         |
                              v                         v
                       +-------------------+       +-------------------+
                       | Result Normalizer | <---- | Raw Search Result |
                       +-------------------+       +-------------------+
                              |
                              v
                       +-------------------+
                       | State / History   |
                       +-------------------+
                              |
                              v
                       +-------------------+
                       | Telegram Notifier |
                       +-------------------+
```

### Component Responsibilities

| Component | Responsibility |
| --- | --- |
| Watchlist config | Defines routes, dates, passenger counts, cabin, polling interval, and alert preferences. |
| Scheduled runner | Triggers searches, handles retries, applies backoff, and coordinates the workflow. |
| Search provider | Encapsulates the data source used to look up ANA availability. |
| Result normalizer | Converts source-specific output into a stable internal schema. |
| State/history store | Tracks checks, previously seen availability, alert status, and errors. |
| Telegram notifier | Formats and sends alerts through a Telegram bot. |

## Candidate Technology Stack

The final stack can change, but a pragmatic starting point would be:

- **Language:** Python, because it is quick for automation, scheduling, and bot integrations.
- **Configuration:** YAML or TOML for route watchlists.
- **Storage:** SQLite for local state and alert history.
- **Scheduling:** Cron, systemd timer, GitHub Actions, or a lightweight Python scheduler depending on deployment target.
- **Notifications:** Telegram Bot API.
- **Deployment:** Local machine, small VPS, Docker container, or serverless job once the runtime behavior is known.

## Example Watchlist Shape

```yaml
routes:
  - name: "Tokyo to New York business class"
    origin: "HND"
    destination: "JFK"
    trip_type: "one_way"
    cabin: "business"
    passengers: 1
    date_window:
      start: "2026-10-01"
      end: "2026-10-14"
    alert:
      telegram_chat_id_env: "TELEGRAM_CHAT_ID"
      notify_on: "new_availability"

settings:
  poll_interval_minutes: 30
  max_retries: 2
  duplicate_suppression_hours: 24
```

## Example Telegram Alert

```text
ANA business class availability found
Route: HND -> JFK
Date: 2026-10-08
Passengers: 1
Cabin: Business
Source: ANA search provider
Action: Review and book manually
```

## Data Model Draft

The MVP can begin with a few SQLite tables:

| Table | Purpose |
| --- | --- |
| `watch_routes` | Stores configured route monitoring rules if config is imported into the database. |
| `search_runs` | Stores each scheduled check, status, timestamps, and error details. |
| `availability_results` | Stores normalized availability options returned by a search. |
| `alerts` | Stores notification attempts, destination chat, sent time, and deduplication key. |

## Milestones

### Milestone 1: Planning and README

- Define the product goal, scope, and non-goals.
- Document an MVP architecture.
- Decide the first implementation stack.

### Milestone 2: Local Prototype

- Add a configuration file format for watched routes.
- Add a command-line entry point that loads the watchlist.
- Stub the search provider so the alerting flow can be tested without live ANA access.
- Add SQLite state tracking.

### Milestone 3: Telegram Alert Flow

- Create Telegram bot setup instructions.
- Add environment-variable based bot credentials.
- Send test alerts from the CLI.
- Implement duplicate suppression.

### Milestone 4: Search Provider Integration

- Research compliant options for ANA availability data.
- Implement the selected provider behind a clean interface.
- Add conservative retry, timeout, and rate-limit behavior.
- Normalize and persist returned availability.

### Milestone 5: Deployment

- Add Docker support or deployment scripts.
- Add scheduler documentation.
- Add health checks and logs.
- Document operational procedures for updating watchlists.

## Open Questions

Before implementation, the following decisions need to be made:

1. Should the first version monitor ANA cash fares, award availability, or both?
2. Which source is acceptable and reliable for availability data?
3. What routes, date ranges, passenger counts, and cabins should be included in the first watchlist?
4. How frequently should searches run without becoming noisy or impolite?
5. Where should the bot run: local machine, VPS, Docker container, or scheduled cloud job?
6. Should alerts include only newly seen availability, or also price/availability changes?

## Compliance and Safety Notes

This project should not automate purchases or bypass website protections. Any future search implementation should be reviewed against the terms and technical constraints of the selected data source. The bot should only store the minimum information needed to detect availability and send alerts.

## Getting Started for Contributors

For now, review this README and refine the planning assumptions. Once the MVP scope is confirmed, the next code changes should add:

1. A sample watchlist config.
2. A Python project skeleton.
3. A stub search provider.
4. A Telegram notifier module with test-mode support.
