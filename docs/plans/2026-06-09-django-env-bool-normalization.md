# Django Env Bool Normalization

Status: Completed
Date: 2026-06-09

## Goal

Keep boolean environment flags predictable when local shells or deploy systems
include surrounding whitespace.

## Changes

- Trimmed boolean environment values before lowercasing and truthy checks.
- Added no-Django-runtime regression coverage for whitespace-padded truthy and
  falsey values.
- Extended the source baseline, README, changelog, and vision with the
  normalized boolean flag contract.

## Verification

- `scripts/check-baseline.sh`
- `python3 scripts/test-settings-helpers.py`
- `make check`
- `git diff --check`
