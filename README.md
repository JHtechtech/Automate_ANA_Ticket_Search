# EVA Air Award Ticket Alert Bot

A planning-first repository for building an automated Telegram bot that monitors **EVA Air business class award-ticket availability** from North American cities to Taipei and alerts as soon as a matching award seat appears. The repository name still mentions ANA because one likely implementation path is monitoring EVA partner-award space through ANA Mileage Club, not because this project is looking for ANA-operated flights or cash tickets.

> **Status:** Planning and product definition. No production search provider, bot, or scheduler has been implemented yet.

## Problem Statement

EVA Air business class award space from North America to Taipei can be scarce and may disappear quickly after release. A common target use case is that EVA releases only a very small number of business class award seats on a flight, often just one seat, so manual checking can easily miss the opportunity.

This project aims to define and later build a lightweight alerting bot that:

- Watches selected North America-to-Taipei EVA Air routes and date ranges.
- Searches for **award-ticket availability only**; cash fares are out of scope.
- Prioritizes business class, especially one-passenger availability.
- Sends Telegram notifications as soon as a newly released matching award seat is detected.
- Keeps a simple history of checks and alerts so duplicate notifications can be controlled.

## Initial Product Goal

Create a reliable personal monitoring tool that can catch newly released EVA Air business class award seats quickly. The first usable version should be small, auditable, and easy to run on a frequent schedule without becoming noisy or aggressive.

### Primary Route Focus

The initial watchlist should focus on EVA Air flights from North American gateways to Taipei. As of the planning review on **2026-05-31**, EVA's own 2026 route announcement says its North American network includes Los Angeles, San Francisco, Seattle, New York, Houston, Dallas-Fort Worth, Chicago, Vancouver, and Toronto, with Washington, D.C. scheduled to start on 2026-06-26.

Recommended initial routes:

- `LAX -> TPE`
- `SFO -> TPE`
- `SEA -> TPE`
- `JFK -> TPE`
- `IAH -> TPE`
- `DFW -> TPE`
- `ORD -> TPE`
- `YVR -> TPE`
- `YYZ -> TPE`
- `IAD -> TPE` once service begins

Additional North American gateways can be added later through configuration if EVA changes its network.

### MVP Scope

The minimum viable product should support:

1. **Route watchlist**
   - North American origin airport and Taipei destination airport, usually `TPE`.
   - One-way monitoring first, with round-trip support deferred unless clearly needed.
   - Target departure date or flexible date window.
   - Passenger count, with `1` as the primary use case.
   - Cabin preference: business class.
   - Airline filter: EVA Air (`BR`).
   - Award-ticket mode only.
   - Optional booking/search program filter, such as ANA Mileage Club partner awards.

2. **Scheduled search runner**
   - Executes award searches at a configurable interval.
   - Records each check attempt and outcome.
   - Applies rate limits and backoff to avoid aggressive querying.
   - Supports tighter polling for high-priority routes while remaining compliant with the selected data source.

3. **Award availability detection**
   - Normalizes search results into a consistent internal format.
   - Compares new results against previously seen award availability.
   - Flags newly released or newly observed EVA business class award seats for alerting.
   - Treats one available business class seat as a valid alert-worthy result.

4. **Telegram alerts**
   - Sends concise messages containing route, date, cabin, passenger count, award details when available, and a booking/search reference if supported.
   - Emphasizes urgency because the target seat may be the only released business class award seat on that flight.
   - Prevents repeated alerts for the same unchanged result.

5. **Configuration-first operation**
   - Stores watched routes and alert preferences in a simple local config file for the first version.
   - Keeps secrets, such as the Telegram bot token, in environment variables.

## Non-Goals for the First Version

The first version should intentionally avoid:

- Monitoring cash fares.
- Automated booking, ticketing, or payment.
- Circumventing website protections, authentication controls, or terms of service.
- Multi-user SaaS account management.
- Complex dashboards before the basic alerting workflow is proven.
- Storing payment details, passport information, loyalty-program passwords, or other sensitive travel documents.

## When to Start Coding

Planning should not continue indefinitely. This project is ready to move from planning into implementation when the team can answer enough questions to build a safe local prototype, even if the live award-search provider is not finalized yet.

### Start Coding When These Are True

1. **Target use case is fixed**
   - The bot monitors EVA Air business class award seats from North America to Taipei.
   - The first passenger count is `1`.
   - Cash fares, automated booking, and payment are excluded.

2. **Initial watchlist is concrete**
   - At least one origin airport, destination, date window, cabin, passenger count, and award program/source are written down in config form.
   - The first route can be a single high-priority route such as `SFO -> TPE`; the project does not need every route configured before coding begins.

3. **The first data-source experiment is selected**
   - A provider spike has a clear hypothesis, such as evaluating ANA Mileage Club partner-award search for EVA-operated award availability.
   - The spike has explicit compliance boundaries: no purchase automation, no bypassing technical controls, and no secret storage in source control.

4. **The alert workflow can be tested without live award data**
   - A stub provider can emit fake EVA business award availability.
   - The runner can compare stub results against local history.
   - Telegram messages can be tested in dry-run mode before sending real alerts.

5. **The first implementation slice is small enough to finish**
   - The first code milestone should load config, run a stub search, persist state, and print or dry-run an alert.
   - Live provider integration should come after that workflow is proven locally.

### Do Not Wait For These Before Coding

The project does **not** need all of the following before coding starts:

- A perfect final provider decision.
- A dashboard design.
- Multi-user support.
- Every North American route and date window.
- Production deployment automation.

Those can be decided after the local prototype proves that the watchlist, state, deduplication, and alert flow are shaped correctly.

### First Coding Slice

The first real code change should be intentionally boring and testable:

1. Add a sample watchlist config for one EVA North America-to-Taipei award route.
2. Add a Python package and CLI entry point.
3. Add a stub award-search provider that returns deterministic fake availability.
4. Add SQLite state tables for search runs, availability results, and alerts.
5. Add a Telegram notifier interface with `dry_run` output first.
6. Add tests proving that a newly seen award seat creates one alert and the same unchanged seat does not create duplicate alerts.

A good rule of thumb: **start coding the local prototype now; postpone live search automation until the stubbed workflow and compliance boundaries are clear.**

## Key Design Principles

- **Award-only:** The bot is optimized for award-seat detection, not fare shopping.
- **EVA-focused:** The initial implementation should treat EVA Air business class to Taipei as the core use case rather than a generic airline search product.
- **Fast but respectful:** Poll often enough to catch scarce releases, while using conservative timeouts, rate limits, and backoff.
- **Compliance-aware:** Prefer official APIs, authorized integrations, or user-permitted data sources where available. If browser automation is later considered, keep it conservative and respectful of applicable terms.
- **Small and observable:** Start with logs, local storage, and clear alert history before adding more infrastructure.
- **Configurable but simple:** A text-based watchlist should be enough for the MVP.
- **Duplicate-safe alerts:** Alert only when an award result is new or materially changed.
- **Failure-tolerant:** Temporary search failures should not crash the service or spam Telegram.

## Proposed Architecture

```text
+-------------------+       +-------------------+       +-----------------------+
| Watchlist Config  | ----> | Scheduled Runner  | ----> | Award Search Provider |
+-------------------+       +-------------------+       +-----------------------+
                              |                         |
                              v                         v
                       +-------------------+       +-------------------+
                       | Result Normalizer | <---- | Raw Award Result  |
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
| Watchlist config | Defines EVA routes, date windows, passenger count, cabin, award program/source, polling interval, and alert preferences. |
| Scheduled runner | Triggers award searches, handles retries, applies backoff, and coordinates the workflow. |
| Award search provider | Encapsulates the selected compliant data source used to look up award availability. |
| Result normalizer | Converts source-specific award-search output into a stable internal schema. |
| State/history store | Tracks checks, previously seen award seats, alert status, and errors. |
| Telegram notifier | Formats and sends urgent award-seat alerts through a Telegram bot. |

## Research-Backed Assumptions

This README was revised with current web research instead of relying only on memory. The following assumptions should guide the first implementation:

- **ANA is a partner-award search path, not the target airline.** ANA lists EVA Air as a Star Alliance partner, and ANA partner flight awards include business class as an eligible class while excluding EVA Premium Economy awards.
- **The data source must be chosen deliberately.** The first provider spike should evaluate ANA Mileage Club partner-award search because the user intent is to catch EVA partner-award seats, but implementation must respect ANA/EVA terms, authentication requirements, rate limits, and technical controls.
- **Routes are not static.** The North America-to-Taipei route list should be config-driven because EVA's network can change; the README route list is a starting watchlist, not hard-coded product logic.
- **Cash fares remain out of scope.** Price tracking, fare alerts, and revenue inventory should not be included unless this project is explicitly re-scoped later.

Reference URLs used for this planning pass:

- EVA Air 2026 Washington, D.C. launch and North America gateway list: <https://www.evaair.com/en-hk/about-eva-air/news/news-releases/2026-02-11-evaair-new-route-taipei-to-washington-dc.html>
- ANA partner airlines page listing EVA Air as a Star Alliance member: <https://www.ana.co.jp/en/us/amc/partner-airlines/>
- ANA partner flight award terms and eligible classes: <https://www.ana.co.jp/en/jp/guide/amc/award/tk/usage/>

## Candidate Technology Stack

The final stack can change, but a pragmatic starting point would be:

- **Language:** Python, because it is quick for automation, scheduling, and bot integrations.
- **Configuration:** YAML or TOML for route watchlists.
- **Storage:** SQLite for local state and alert history.
- **Scheduling:** Cron, systemd timer, Docker cron, or a lightweight Python scheduler depending on deployment target.
- **Notifications:** Telegram Bot API.
- **Deployment:** Local machine, small VPS, Docker container, or scheduled cloud job once the runtime behavior is known.

## Example Watchlist Shape

```yaml
routes:
  - name: "SFO to Taipei EVA business award"
    airline: "BR"
    airline_name: "EVA Air"
    origin: "SFO"
    destination: "TPE"
    trip_type: "one_way"
    search_type: "award"
    award_program: "ANA Mileage Club"
    cabin: "business"
    passengers: 1
    date_window:
      start: "2026-10-01"
      end: "2026-10-14"
    alert:
      telegram_chat_id_env: "TELEGRAM_CHAT_ID"
      notify_on: "new_award_availability"
      urgency: "high"

settings:
  poll_interval_minutes: 15
  max_retries: 2
  duplicate_suppression_hours: 24
```

## Example Telegram Alert

```text
EVA business award seat found
Route: SFO -> TPE
Date: 2026-10-08
Passengers: 1
Cabin: Business
Search type: Award ticket
Award program: ANA Mileage Club partner award
Airline: EVA Air (BR)
Action: Review and book manually as soon as possible
```

## Data Model Draft

The MVP can begin with a few SQLite tables:

| Table | Purpose |
| --- | --- |
| `watch_routes` | Stores configured EVA award route monitoring rules if config is imported into the database. |
| `search_runs` | Stores each scheduled award check, status, timestamps, and error details. |
| `availability_results` | Stores normalized EVA business award-seat options returned by a search. |
| `alerts` | Stores notification attempts, destination chat, sent time, and deduplication key. |

## Milestones

### Milestone 1: Planning and README

- Define the EVA award-ticket product goal, scope, and non-goals.
- Document an MVP architecture.
- Decide the first implementation stack.
- Capture the criteria for when planning is complete enough to begin coding.

### Milestone 2: Local Prototype

- Add a configuration file format for North America-to-Taipei EVA award routes.
- Add a command-line entry point that loads the watchlist.
- Stub the award search provider so the alerting flow can be tested without live availability access.
- Add SQLite state tracking.

### Milestone 3: Telegram Alert Flow

- Create Telegram bot setup instructions.
- Add environment-variable based bot credentials.
- Send test alerts from the CLI.
- Implement duplicate suppression for the same flight/date/cabin/passenger-count result.

### Milestone 4: Award Search Provider Integration

- Research compliant options for EVA Air award availability data.
- Implement the selected provider behind a clean interface.
- Add conservative retry, timeout, and rate-limit behavior.
- Normalize and persist returned award availability.

### Milestone 5: Deployment

- Add Docker support or deployment scripts.
- Add scheduler documentation.
- Add health checks and logs.
- Document operational procedures for updating watchlists and polling frequency.

## Open Questions

Before implementation, the following decisions need to be made:

1. Which North American EVA gateways should be in the first watchlist?
2. What date ranges should be monitored first?
3. Should ANA Mileage Club partner-award search be the first compliant source spike, or should another authorized source be evaluated first?
4. How frequently should high-priority searches run without becoming noisy or impolite?
5. Where should the bot run: local machine, VPS, Docker container, or scheduled cloud job?
6. Should alerts include only newly seen availability, or also changes in award details such as seat count, cabin, or operating flight number?

## Compliance and Safety Notes

This project should not automate purchases, bookings, logins, or bypass website protections. Any future award-search implementation should be reviewed against the terms and technical constraints of the selected data source. The bot should only store the minimum information needed to detect award availability and send alerts.

## Getting Started for Contributors

For now, review this README and refine the planning assumptions. The project is ready to start coding the local prototype once one initial route/date window and the first provider-spike hypothesis are confirmed. The next code changes should add:

1. A sample EVA award watchlist config.
2. A Python project skeleton and CLI entry point.
3. A stub award search provider with deterministic fake availability.
4. SQLite state tracking for search runs, availability results, and alerts.
5. A Telegram notifier module with dry-run/test-mode support.
6. Tests for new-seat detection and duplicate suppression.
