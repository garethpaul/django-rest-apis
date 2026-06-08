# [P2] Disable debug mode for deployed web applications

## Severity

P2 - security/reliability

## Evidence

- `app/settings.py:23`: `DEBUG = True`
- `app/settings.py:25`: `TEMPLATE_DEBUG = True`

## Problem

Debug mode is enabled in application startup code. In deployed web apps, debug mode can expose detailed stack traces, configuration details, or development-only behavior to users when an error occurs.

## Suggested fix

Default debug mode to false, enable it only through an explicit local development setting, and keep deployed WSGI or Flask entry points in production mode.

## Review metadata

- Repository: `garethpaul/django-rest-apis`
- Reviewed commit: `cbeac7344b30b4a6a1a5784fb1b4a41e8c4cdf40`
- Labels: `bug`, `codex-review`, `severity:P2`
- Codex review fingerprint: `7e13c2bcf3c2314f`
