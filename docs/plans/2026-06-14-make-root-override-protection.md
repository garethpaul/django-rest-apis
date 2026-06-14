---
title: Make Repository Root Override Protection
type: reliability
status: active
date: 2026-06-14
---

# Make Repository Root Override Protection

## Status: Active

## Problem Frame

The Makefile derives an absolute repository path in `ROOT`, but command-line
assignments take precedence over its current assignment. `make ROOT=/tmp lint`
therefore attempts to execute an untracked helper outside the checkout instead
of the repository's deterministic baseline gate.

## Scope Boundaries

- Preserve the existing `lint`, `test`, `build`, `verify`, and `check` targets.
- Preserve all seven repository-root command references.
- Preserve `PYTHON` as an intentional caller-selected interpreter override.
- Do not change Django, Twitter, template, dependency, or runtime behavior.

## Requirements

- R1. Derive the repository root from the loaded Makefile itself.
- R2. Command-line and environment assignments must not redirect that root.
- R3. The deterministic checker must require the protected assignment form.
- R4. Full verification must pass from repository and external directories.
- R5. Isolated mutations that restore caller control must fail verification.

## Implementation

1. Protect the Makefile repository-root assignment from caller overrides.
2. Update the existing root contract and register this plan in the checker.
3. Run focused, full, external-directory, hostile-override, and mutation gates.

## Verification

- `sh -n scripts/check-baseline.sh`
- `make lint`
- `make check`
- External-working-directory `make -C <repository> check`
- Hostile command-line and environment `ROOT` assignments
- Python 3.12 and Python 3.14 where available
- `git diff --check`
- Isolated hostile assignment mutations
