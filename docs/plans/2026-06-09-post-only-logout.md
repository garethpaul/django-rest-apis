---
title: POST Only Logout
type: security
status: completed
date: 2026-06-09
---

# POST Only Logout

## Summary

Keep logout behind a CSRF-protected POST form instead of exposing it as a GET
link.

## Requirements

- R1. The logout view must use Django's `require_POST` decorator.
- R2. The shared base template must not render `/logout` as a link.
- R3. The logout UI must submit a POST form with `{% csrf_token %}`.
- R4. No-Django-runtime helper stubs must continue importing `home.views`.
- R5. README and the source baseline must document the guard.

## Verification

- `make check`
- `scripts/check-baseline.sh`
- `python3 scripts/test-view-helpers.py`
- `git diff --check`
