# Issue: Research ANA Mileage Club partner-award provider feasibility

## Labels

`research`, `provider`, `compliance`, `roadmap`

## Problem

The project needs a live award-search provider eventually, but it should not be implemented until ANA Mileage Club behavior, constraints, and compliance boundaries are documented.

## Proposed Work

- Manually test ANA Mileage Club partner-award search for EVA-operated routes.
- Document required inputs, output states, cabin labels, availability indicators, and errors.
- Document whether searches require login, round-trip input, or service-center handling.
- Record rate-limit, timeout, session, and authentication constraints.
- Recommend whether implementation should proceed and what guardrails are required.

## Acceptance Criteria

- A provider research document exists under `docs/`.
- The document clearly states whether a live provider is feasible.
- Compliance and safety boundaries are explicit.
- No credentials, cookies, or sensitive screenshots are committed.
