---
title: Twitter Blank Token Fallback
type: reliability
status: completed
date: 2026-06-09
---

# Twitter Blank Token Fallback

## Summary

Treat blank saved social-auth OAuth token values as missing so the sample can
fall back to valid Twitter tokens from the environment.

## Requirements

- R1. Strip credential-like values before deciding whether they are present.
- R2. Do not let empty or whitespace saved OAuth token values overwrite valid
  environment fallback tokens.
- R3. Keep no-Django-runtime view helper coverage for blank saved token values.
- R4. README, VISION, CHANGES, and the baseline guard must document the blank
  token fallback.
- R5. The repository verification wrapper must expose a Python compile build
  target.

## Verification

- `python3 scripts/test-view-helpers.py`
- `scripts/check-baseline.sh`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
