# Changelog

## 2026-06-09

- Fell back to environment Twitter access tokens when the saved social-auth row
  is missing.
- Changed logout from a GET link to a CSRF-protected POST-only form and added a
  source baseline guard.

## 2026-06-08

- Added a root `make check` wrapper for the source baseline and helper tests.
- Allowed Twitter API setup to fall back to environment access tokens when a
  social-auth record has no stored OAuth token data.
- Added the token fallback plan to the baseline verifier.
- Moved Django `SECRET_KEY` and debug mode to environment-driven settings.
- Moved Twitter API credentials and access tokens to environment variables.
- Made `ALLOWED_HOSTS` environment-driven with local defaults for development.
- Restricted tweet submission handling to POST data and hardened Twitter status
  links with HTTPS plus safe external-link attributes.
- Pinned the legacy dependency ranges to the Django 1.6-era stack.
- Added a static baseline guard for the legacy Django settings security contract.
- Added no-Django-runtime regression tests for settings helper behavior.
- Added Twitter status normalization and no-Django-runtime view helper tests.
