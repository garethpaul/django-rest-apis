# Current Django SECRET_KEY Guard

## Context

Repo-local finding: `docs/bugs/p1-hardcoded-django-secret-key-65f516b019a31d76.md`

The current default branch removed the original generated Django secret, but still contains a committed debug-mode fallback key:

```python
SECRET_KEY = 'django-rest-apis-local-development-key'
```

## Plan

1. Require `DJANGO_SECRET_KEY` in every mode instead of using a committed fallback.
2. Update the source-level settings helper tests to prove debug mode also requires a configured secret.
3. Extend the baseline guard to reject any committed development `SECRET_KEY` fallback.
4. Remove stale repo-local bug files once the scanner evidence is addressed or already resolved on the default branch.

## Verification

- Run `scripts/check-baseline.sh`.
- Run `git diff --check`.
