---
title: Twitter Social Extra Data Type Guard
type: fix
date: 2026-06-13
status: completed
---

# Twitter Social Extra Data Type Guard

## Summary

Treat malformed non-mapping social-auth metadata as unavailable and retain the
existing environment-token fallback instead of raising while reading the
legacy database row.

## Problem Frame

`get_twitter` normalizes malformed values inside the nested `access_token`
mapping, but it calls `.get` on `UserSocialAuth.extra_data` before verifying
that the outer value is a mapping. A corrupted or historically incompatible
row containing a string, list, or scalar therefore raises an attribute error
and bypasses otherwise valid environment credentials.

## Requirements

- R1. Only dictionary-shaped `extra_data` may be queried for an
  `access_token` value.
- R2. Non-dictionary `extra_data` must use the existing normalized environment
  access-token key and secret.
- R3. Dictionary metadata and nested token precedence must remain unchanged.
- R4. Missing or invalid credentials must continue raising the existing stable
  `ImproperlyConfigured` error.
- R5. Offline helper tests must cover at least string and list outer metadata
  without constructing a live Twitter client.
- R6. The static baseline, project guidance, and completed plan evidence must
  enforce the guard through `make check`.

## Implementation Units

### U1. Guard Social Metadata Shape

- **Files:** `home/views.py`
- **Goal:** Read nested social OAuth data only when the outer container is a
  dictionary; otherwise preserve environment fallback credentials.
- **Covers:** R1, R2, R3, R4

### U2. Add Malformed-Row Regressions

- **Files:** `scripts/test-view-helpers.py`
- **Goal:** Prove non-mapping social metadata cannot crash token construction
  or override valid environment credentials.
- **Covers:** R2, R4, R5

### U3. Enforce Maintenance Evidence

- **Files:** `scripts/check-baseline.sh`, `README.md`, `CHANGES.md`, `VISION.md`
- **Goal:** Require the source guard, regression names, documentation, and
  truthful completed verification evidence.
- **Covers:** R6

## Verification

- Python 3.12.8 and Python 3.14.0 each passed seven settings tests, 17 view
  helper tests, and Python compilation.
- `make check` passed on Python 3.12.8 and Python 3.14.0, and the rooted wrapper
  passed from `/tmp` with Python 3.12.8.
- Shell syntax, `git diff --check`, explicit secret-pattern inspection, and
  generated-artifact inspection passed.
- Seven hostile mutations were rejected for a removed guard, wrong accepted
  container type, each removed malformed-row regression, weakened fallback
  assertion, documentation drift, and incomplete plan status.
- The historical Django stack was not installed or launched. Verification used
  no credentials, constructed no real Twitter client, and made no live Twitter
  request.

## Risks

- Dictionary subclasses remain accepted, matching the existing nested token
  contract and legacy Python compatibility.
- Other malformed social-auth model attributes remain outside this focused
  fallback boundary.
