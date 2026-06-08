---
title: Settings Helper Regression Tests
type: test
status: completed
date: 2026-06-08
---

# Settings Helper Regression Tests

## Summary

Add executable regression coverage for the legacy Django sample's environment
helper behavior without requiring the full Django 1.6 runtime.

## Problem Frame

The existing settings security baseline used source-level checks because this
host does not provide the original Django 1.6 dependency stack. Those checks
guard important strings, but the highest-risk behavior is whether production
settings fail closed without `DJANGO_SECRET_KEY` and whether debug, allowed
hosts, and Twitter credentials are actually read from the environment.

## Requirements

- R1. Tests must run with Python 3 and no installed Django package.
- R2. Production settings must raise `ImproperlyConfigured` when
  `DJANGO_SECRET_KEY` is absent.
- R3. Debug mode may use the explicit local-development fallback key.
- R4. `DJANGO_ALLOWED_HOSTS` must parse comma-separated host lists.
- R5. Twitter credentials must come from environment variables.
- R6. The baseline guard must run these tests.

## Implementation Units

### U1. Django Exception Stub

- **Goal:** Import `app/settings.py` in isolation by stubbing only
  `django.core.exceptions.ImproperlyConfigured`.
- **Files:** `scripts/test-settings-helpers.py`
- **Verification:** `python3 scripts/test-settings-helpers.py`

### U2. Helper Behavior Tests

- **Goal:** Exercise secret-key failure, debug fallback, environment host lists,
  boolean parsing, and Twitter credential reads.
- **Files:** `scripts/test-settings-helpers.py`
- **Verification:** `scripts/check-baseline.sh`

### U3. Guard And Docs

- **Goal:** Make the executable settings contract part of normal verification.
- **Files:** `scripts/check-baseline.sh`, `README.md`, `CHANGES.md`, this plan
- **Verification:** `scripts/check-baseline.sh`, `git diff --check`

## Risks & Dependencies

- These tests intentionally do not boot Django, load URL routing, or connect to
  Twitter.
- Full app execution still requires the legacy Django and python-social-auth
  dependency stack documented in `requirements.txt`.
