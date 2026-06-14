---
title: Make Repository Root Override Protection
type: reliability
status: completed
date: 2026-06-14
---

# Make Repository Root Override Protection

## Status: Completed

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

## Work Completed

- Protected the derived repository-root assignment with GNU Make's `override`
  directive while preserving all seven root references and the `PYTHON`
  override.
- Updated the existing exact root contract and registered this plan in the
  deterministic checker.
- Preserved every verification target and all Django and Twitter behavior.

## Verification Completed

- `sh -n scripts/check-baseline.sh` passed.
- `make lint` and `make check` passed on Python 3.12.8 and Python 3.14.0.
- External-working-directory `make -C <repository> lint` and `make -C
  <repository> check` passed.
- Full checks passed with command-line and environment `ROOT=/tmp`
  assignments, while commands continued to resolve inside the repository.
- Three isolated hostile assignment mutations were rejected: a regular
  assignment, a conditional assignment, and a caller-directory assignment.
