---
title: Production Secure Cookies
type: security
status: completed
date: 2026-06-10
---

# Production Secure Cookies

## Summary

Ensure authenticated session and CSRF cookies cannot be sent over cleartext
transport when the archival Django sample runs with production settings.

## Work Completed

- Added a shared secure-cookie setting for session and CSRF cookies.
- Made the secure flag unconditional whenever `DJANGO_DEBUG` is disabled, so a
  falsey environment override cannot weaken production behavior.
- Kept debug-mode defaults compatible with local HTTP development.
- Added `DJANGO_SECURE_COOKIES=1` as an opt-in for debug environments served
  over HTTPS.
- Added isolated settings tests for production enforcement, debug defaults, and
  debug HTTPS opt-in without installing Django 1.6.
- Rooted Make verification to the repository, pinned CI to Ubuntu 24.04, and
  extended the source baseline and documentation.

## Verification

- `python3 scripts/test-settings-helpers.py`
- `make check`
- `make -f /absolute/path/to/Makefile check`
- Mutation checks for production cookie weakening, removed settings tests,
  floating runner, unrooted Make targets, and incomplete plan status
- `sh -n scripts/check-baseline.sh`
- `git diff --check`

The unsupported Django 1.6 dependency set was not installed or started during
this maintenance pass.
