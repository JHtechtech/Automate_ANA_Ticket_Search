# Issue: Add CI for tests and compile checks

## Labels

`ci`, `testing`, `good first issue`

## Problem

The project has local tests, but pull requests should automatically run the same checks so contributors can see failures before merging.

## Proposed Work

- Add a GitHub Actions workflow for Python 3.11+.
- Install the package with dev dependencies.
- Run `pytest -q`.
- Run `python -m compileall -q src`.
- Optionally run `git diff --check` for whitespace checks.

## Acceptance Criteria

- CI runs on pull requests and pushes to the main branch.
- CI passes for the current prototype.
- README or contributing docs mention the CI checks.
