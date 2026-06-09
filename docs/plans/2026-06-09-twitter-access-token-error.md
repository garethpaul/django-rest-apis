# Twitter Access Token Error

Status: Completed
Date: 2026-06-09

## Goal

Make missing Twitter access-token configuration fail with a clear Django
configuration error after social-auth and environment fallbacks are exhausted.

## Changes

- Replaced the generic missing-token exception in `get_twitter` with
  `ImproperlyConfigured`.
- Added a no-Django-runtime view helper test for missing environment access
  tokens and missing social-auth rows.
- Extended the source baseline to require the explicit error path and test.
- Documented the access-token configuration error guard in the README,
  changelog, and vision.

## Verification

- `sh -n scripts/check-baseline.sh`
- `scripts/check-baseline.sh`
- `python3 -m py_compile app/settings.py home/views.py scripts/test-settings-helpers.py scripts/test-view-helpers.py`
- `python3 scripts/test-settings-helpers.py`
- `python3 scripts/test-view-helpers.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
