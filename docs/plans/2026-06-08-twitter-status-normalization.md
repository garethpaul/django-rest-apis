---
title: Twitter Status Normalization
type: fix
status: completed
date: 2026-06-08
---

# Twitter Status Normalization

## Summary

Normalize submitted Twitter status text before the legacy view calls the Twitter
API, and add no-Django-runtime regression tests for the helper.

## Requirements

- R1. Whitespace-only status submissions must not call the Twitter API.
- R2. Submitted status text must be stripped before posting.
- R3. Status text over 280 characters must be ignored before posting.
- R4. Helper behavior must be covered without requiring a Django runtime.
- R5. README, CHANGES, and the source baseline guard must document and preserve
  the view-helper test path.

## Verification

- `python3 scripts/test-view-helpers.py`
- `scripts/check-baseline.sh`
- `git diff --check`
