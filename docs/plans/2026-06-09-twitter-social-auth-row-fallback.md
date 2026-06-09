---
title: Twitter Social Auth Row Fallback
type: reliability
status: completed
date: 2026-06-09
---

# Twitter Social Auth Row Fallback

## Summary

Extend the Twitter API setup fallback so users without a saved
`UserSocialAuth` row can still use configured environment access tokens.

## Requirements

- R1. Preserve the existing environment fallback for social-auth rows that lack
  stored OAuth token data.
- R2. Catch `UserSocialAuth.DoesNotExist` and continue with environment access
  tokens.
- R3. Do not catch broad database or API errors.
- R4. Add no-Django-runtime regression coverage for the missing-row branch.
- R5. Update README, VISION, CHANGES, and the source baseline guard.

## Verification

- `python3 scripts/test-view-helpers.py`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`
