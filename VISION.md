## Django REST APIs Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Django REST APIs is a sample Django app for Twitter OAuth and simple REST API
calls.

The repository is useful as a historical Django 1.4-era example of social auth,
Twitter API usage, Fabric startup, and local database initialization. Project
setup notes live in [`README.md`](README.md).

The goal is to preserve the sample while making credentials, legacy dependency
constraints, and upgrade paths explicit.

The current focus is:

Priority:

- Keep the Twitter OAuth flow and REST API examples understandable
- Avoid committing Twitter keys, access tokens, or local settings secrets
- Preserve the documented legacy setup for Django, south, Fabric, and python-twitter
- Keep account-changing actions behind POST and CSRF protection
- Redirect after successful status posts so browser refreshes cannot resubmit
  account-changing requests
- Fall back to environment Twitter tokens when saved social-auth tokens are absent
- Ignore blank saved social-auth tokens so environment fallbacks remain usable
- Ignore malformed saved social-auth tokens so environment fallbacks remain usable
- Fail clearly when Twitter access tokens are absent
- Contain expected Twitter API failures without exposing provider details
- Normalize boolean environment flags before evaluating debug-mode settings
- Keep production session and CSRF cookies transport-secure
- Keep GitHub Actions aligned with the local Python `make check` baseline
- Keep time-drift troubleshooting visible for OAuth failures

Next priorities:

- Keep credentials out of tracked settings and covered by the baseline guard
- Add README notes for supported Python and Django versions
- Modernize Django and dependency usage in a dedicated pass
- Keep tests around OAuth configuration boundaries and API wrappers

Contribution rules:

- One PR = one focused Django, Twitter, config, or documentation change.
- Do not mix framework upgrades with behavior changes unless required.
- Verify `python manage.py` commands in the declared environment.
- Update setup docs whenever configuration or credentials handling changes.
- Keep `.github/workflows/check.yml` in sync with the local settings and view
  helper guard.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Twitter API keys, access tokens, and token secrets must not be committed.
Configuration should fail clearly when credentials are absent.

OAuth callback and REST behavior should avoid logging tokens or user data.

## What We Will Not Merge (For Now)

- Hardcoded real Twitter credentials
- Broad Django upgrades bundled with unrelated feature work
- API calls that log or expose user tokens
- Setup changes that leave the sample impossible to run from docs

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
