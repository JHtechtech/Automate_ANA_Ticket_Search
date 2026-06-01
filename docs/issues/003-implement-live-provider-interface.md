# Issue: Implement a compliance-reviewed live award provider

## Labels

`provider`, `enhancement`, `blocked`, `roadmap`

## Blocked By

- `002-provider-discovery-spike.md`

## Problem

The current `stub` provider validates the workflow but does not search live award inventory.

## Proposed Work

- Implement a live provider behind the existing `AwardSearchProvider` interface only after provider discovery is approved.
- Normalize live results into `AvailabilityResult` objects.
- Add conservative timeouts, retries, and backoff.
- Keep dry-run mode available for all live-provider tests.
- Add tests with recorded, sanitized fixtures or mocked responses.

## Acceptance Criteria

- The runner, state store, and notifier do not require major rewrites.
- Live-provider tests do not require real credentials in CI.
- The provider handles no-availability and error states without alert spam.
- Documentation explains how to enable and disable the provider safely.
