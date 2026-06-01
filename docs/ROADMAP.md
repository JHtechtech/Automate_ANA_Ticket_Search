# Roadmap

This roadmap is intentionally split into small issues so the project looks and behaves like an active open-source project while keeping safety and compliance boundaries clear.

## Now: Local Prototype Hardening

- Keep the stub workflow reliable.
- Improve docs and setup ergonomics.
- Add CI so tests run automatically on pull requests.
- Keep trial configs dry-run by default.

## Next: Provider Discovery Spike

- Manually validate ANA Mileage Club partner-award search behavior for EVA-operated flights.
- Document result shapes, error states, rate limits, session behavior, and compliance constraints.
- Decide whether a live provider can be implemented safely.

## Later: Production-Ready Monitoring

- Add a compliance-reviewed live provider behind `AwardSearchProvider`.
- Add structured logging and metrics.
- Add production scheduler/deployment docs.
- Add route enable/disable controls and better operational runbooks.

## Not Planned

- Automated booking.
- Automated payment.
- Credential harvesting or committed session storage.
- Circumventing website protections.
