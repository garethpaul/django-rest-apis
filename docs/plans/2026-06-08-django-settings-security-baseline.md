---
title: Django Settings Security Baseline
type: fix
status: completed
date: 2026-06-08
---

# Django Settings Security Baseline

## Summary

Move the legacy Django sample's signing key, debug flag, and Twitter credentials
out of tracked source and add a repeatable source guard for the settings
security contract.

## Problem Frame

The repository had review findings for a hardcoded `SECRET_KEY` and `DEBUG =
True` in `app/settings.py`. The same settings file also contained tracked
Twitter credential placeholders. Even placeholders create a weak sample pattern
because new users often replace them directly in source.

## Requirements

- R1. `SECRET_KEY` must come from `DJANGO_SECRET_KEY`, with only an explicit
  debug-mode local fallback.
- R2. `DEBUG` must default to false and be enabled through `DJANGO_DEBUG`.
- R3. `TEMPLATE_DEBUG` must track `DEBUG`.
- R4. Twitter API keys and access tokens must come from environment variables.
- R5. `ALLOWED_HOSTS` must be environment-driven and non-empty by default.
- R6. Tweet submission must read from POST only.
- R7. Twitter status links must use HTTPS and safe external-link attributes.
- R8. Legacy dependencies must be pinned to the Django 1.6-era stack.
- R9. README and a guard script must document and verify the configuration
  boundary.

## Implementation Units

### U1. Environment-Driven Settings

- **Goal:** Remove hardcoded Django and Twitter secrets from tracked settings.
- **Files:** `app/settings.py`
- **Verification:** `scripts/check-baseline.sh`

### U2. Static Guard

- **Goal:** Verify the legacy settings contract without requiring a full Django
  1.4 runtime on this host.
- **Files:** `scripts/check-baseline.sh`, `requirements.txt`,
  `home/views.py`, `templates/home.html`
- **Verification:** `scripts/check-baseline.sh`, `git diff --check`

### U3. Documentation

- **Goal:** Make local setup and future maintenance expectations explicit.
- **Files:** `README.md`, `CHANGES.md`, this plan
- **Verification:** `scripts/check-baseline.sh`

## Risks & Dependencies

- This pass does not modernize Django, python-social-auth, python-twitter, or
  Fabric dependencies.
- Running the full app still requires the legacy dependency stack.
- Deployed environments that used the committed key must rotate to a new
  `DJANGO_SECRET_KEY`.
