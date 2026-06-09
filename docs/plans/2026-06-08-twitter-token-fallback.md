---
title: Twitter Token Fallback
type: fix
status: completed
date: 2026-06-08
---

# Twitter Token Fallback

## Summary

Avoid a `KeyError` when a social-auth record exists without stored Twitter
OAuth token data, and fall back to the environment-provided access token pair.

## Requirements

- R1. Existing configured Twitter consumer key/secret validation remains.
- R2. Missing `extra_data["access_token"]` does not crash `get_twitter`.
- R3. Environment access token settings remain the fallback when user token data is absent.
- R4. View helper tests cover the missing social-token path.
- R5. README, changelog, and source baseline document the fallback behavior.

## Verification

- `make check`
- `python3 scripts/test-settings-helpers.py`
- `python3 scripts/test-view-helpers.py`
- `scripts/check-baseline.sh`
- `git diff --check`
