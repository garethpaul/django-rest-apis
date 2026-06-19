---
title: Twitter Status Type Guard
type: reliability
status: completed
date: 2026-06-13
---

# Twitter Status Type Guard

## Summary

Treat non-string Twitter status values as invalid input before normalization or
provider calls, matching the existing defensive token boundary.

## Requirements

- Return `None` for non-string status values without calling `.strip()`.
- Preserve trimming, empty-status rejection, and the 280-character limit.
- Prove malformed values do not reach `PostUpdates` through the home helper.
- Keep the legacy Django runtime, provider wiring, templates, and POST/Redirect/GET
  behavior unchanged.
- Update source contracts and maintenance documentation.

## Verification

Completed on 2026-06-13:

- `make check` passed on Python 3.12.8 and Python 3.14.0 with 7 settings tests,
  15 view tests, source contracts, and bytecode compilation.
- `make -f /absolute/path/to/Makefile check` passed from `/tmp`.
- Eight hostile mutations were rejected across the type guard, helper and home
  regressions, provider-write assertion, documentation, and completed-plan
  evidence.
- `sh -n scripts/check-baseline.sh`, `git diff --check`, focused diff review,
  and a changed-line secret-pattern scan passed.
- The historical Django/social-auth stack was not installed or launched.

## Non-Goals

- Installing or launching the historical Django/social-auth dependency stack.
- Changing valid status text semantics or Twitter API behavior.
- Adding new endpoints, forms, or templates.
