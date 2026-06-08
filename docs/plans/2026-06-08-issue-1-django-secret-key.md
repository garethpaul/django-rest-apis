---
title: Issue 1 Django Secret Key Configuration
type: fix
status: active
date: 2026-06-08
origin: public repository security audit
execution: code
---

# Issue 1 Django Secret Key Configuration

## Summary

Remove the public Django signing key from the sample app and require deployments to provide `DJANGO_SECRET_KEY`.

## Problem Frame

The public repository committed a concrete Django `SECRET_KEY` while the app enables sessions, CSRF middleware, Django auth, and Twitter OAuth login. Any deployment using the repository default exposes a known signer for Django security-sensitive values.

## Requirements

- R1. `app/settings.py` must not contain the public committed `SECRET_KEY`.
- R2. The app must read `SECRET_KEY` from deploy-time configuration and fail closed when it is missing.
- R3. `DEBUG` must default to off instead of on.
- R4. `ALLOWED_HOSTS` must be configurable through deploy-time configuration.
- R5. README must document local setup for the required secret, debug mode, and allowed hosts.
- R6. The GitHub issue and PR must be marked `URGENT`.

## Implementation Unit

### U1. Settings Hardening

- **Goal:** Add small environment helpers, require `DJANGO_SECRET_KEY`, default `DJANGO_DEBUG` to false, and read `DJANGO_ALLOWED_HOSTS` from the environment.
- **Files:** `app/settings.py`, `README.md`, `scripts/check-django-secret-config.sh`
- **Verification:** `scripts/check-django-secret-config.sh`, `python3 -m py_compile app/settings.py`, and `git diff --check`.

## Risks

- Local users must set `DJANGO_SECRET_KEY` before running management commands or starting the sample app.
- Changing `SECRET_KEY` invalidates existing signed sessions and tokens for any existing deployment.
