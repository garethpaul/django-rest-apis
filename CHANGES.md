# Changelog

## 2026-06-08

- Moved Django `SECRET_KEY` and debug mode to environment-driven settings.
- Moved Twitter API credentials and access tokens to environment variables.
- Made `ALLOWED_HOSTS` environment-driven with local defaults for development.
- Restricted tweet submission handling to POST data and hardened Twitter status
  links with HTTPS plus safe external-link attributes.
- Pinned the legacy dependency ranges to the Django 1.6-era stack.
- Added a static baseline guard for the legacy Django settings security contract.
- Added no-Django-runtime regression tests for settings helper behavior.
- Added Twitter status normalization and no-Django-runtime view helper tests.
