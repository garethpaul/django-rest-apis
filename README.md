# django-rest-apis

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/django-rest-apis` is a Python web API or service project. Sample Django App for Twitter showcasing OAuth and simple REST API calls.

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python (11).

## Repository Contents

- `README.md` - project overview and local usage notes
- `requirements.txt` - Python dependency or packaging metadata
- `CHANGES.md` - maintenance history
- `app` - source or example code
- `home` - source or example code
- `manage.py`
- `SECURITY.md` - security reporting and disclosure guidance
- `Makefile` - repository-level verification wrapper
- `scripts/check-baseline.sh` - source-level settings security guard
- `templates` - source or example code
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: app, home, scripts, templates
- Dependency and build manifests: requirements.txt
- Entry points or build surfaces: manage.py, `Makefile`, `scripts/check-baseline.sh`
- Test-looking files: home/tests.py

## Getting Started

### Prerequisites

- Git
- Python matching the era of the project

### Setup

```bash
git clone https://github.com/garethpaul/django-rest-apis.git
cd django-rest-apis
python -m pip install -r requirements.txt
export DJANGO_DEBUG=1
export DJANGO_SECRET_KEY=local-development-secret
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
export SOCIAL_AUTH_TWITTER_KEY=
export SOCIAL_AUTH_TWITTER_SECRET=
export TWITTER_ACCESS_TOKEN=
export TWITTER_ACCESS_TOKEN_SECRET=
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Run Django management commands through `python manage.py ...`.
- The app is a legacy Django sample. Keep real Twitter OAuth credentials in
  environment variables or untracked local shell configuration.

## Testing and Verification

Run the source-level settings security guard before committing:

```bash
make check
scripts/check-baseline.sh
```

`make check` runs the source baseline and no-Django-runtime helper tests from
the repository root. The guard verifies that `DJANGO_SECRET_KEY`,
`DJANGO_DEBUG`, and Twitter credential settings are environment-driven and that
the old hardcoded `SECRET_KEY` is gone. It also runs no-Django-runtime settings
helper tests, checks POST-only status submission, Twitter status normalization,
safe Twitter status links, missing social OAuth token fallback, missing
social-auth row fallback, and pinned legacy dependency ranges. Logout is kept
behind a CSRF-protected POST-only form instead of a GET link.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- Detected references to Twitter. Keep API keys, OAuth credentials, tokens, and account-specific values in local configuration only.
- Required environment variables for local app startup are:
  `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`,
  `SOCIAL_AUTH_TWITTER_KEY`, `SOCIAL_AUTH_TWITTER_SECRET`,
  `TWITTER_ACCESS_TOKEN`, and `TWITTER_ACCESS_TOKEN_SECRET`.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include app/settings.py, app/urls.py, home/views.py, requirements.txt, and 1 more.
- Review changes touching external API calls or credential-adjacent configuration; examples from the scan include app/settings.py, home/views.py, requirements.txt, templates/home.html, and 1 more.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include app/settings.py, app/urls.py, app/wsgi.py, fabfile.py, and 6 more.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `CHANGES.md` for maintenance history.
- See `docs/plans/2026-06-08-settings-helper-regression-tests.md` for the
  executable settings helper test plan.
- See `docs/plans/2026-06-08-twitter-token-fallback.md` for optional
  social-auth token fallback coverage.
- See `docs/plans/2026-06-09-twitter-social-auth-row-fallback.md` for missing
  social-auth row fallback coverage.
- See `docs/plans/2026-06-09-post-only-logout.md` for the POST-only logout
  guard.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
