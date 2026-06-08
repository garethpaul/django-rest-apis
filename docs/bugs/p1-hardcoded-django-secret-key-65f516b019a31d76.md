# [P1] Move Django SECRET_KEY out of source control

## Severity

P1 - security/session-integrity

## Evidence

- `app/settings.py:44`: `SECRET_KEY = 'django-rest-apis-local-development-key'`

## Problem

The Django `SECRET_KEY` is committed as a literal value. Anyone with the repository can reuse the signing key, which can invalidate assumptions around signed cookies, password reset tokens, and other cryptographic signatures if this key is used in a deployed environment.

## Suggested fix

Read `SECRET_KEY` from an environment variable or deployment secret store, provide a safe development default only outside production, and rotate the deployed key after removing the committed value.

## Review metadata

- Repository: `garethpaul/django-rest-apis`
- Reviewed commit: `e480ebdad5a1d852f3fea67c2b187678fde4bf2c`
- Labels: `bug`, `codex-review`, `severity:P1`
- Codex review fingerprint: `65f516b019a31d76`
