# Twitter Malformed Token Fallback

Status: Completed
Date: 2026-06-09

## Goal

Keep malformed saved social-auth token values from overriding valid Twitter
access tokens configured in the environment.

## Changes

- Updated token normalization to ignore non-string credential values.
- Added a no-Django-runtime regression test for malformed saved social-auth
  OAuth token values falling back to environment tokens.
- Extended the source baseline to require the malformed-token test, helper
  guard, README note, vision note, and completed plan.
- Documented the malformed-token fallback in the README, changelog, and vision.

## Verification

- `scripts/check-baseline.sh`
- `python3 scripts/test-settings-helpers.py`
- `python3 scripts/test-view-helpers.py`
- `make check`
- `git diff --check`
