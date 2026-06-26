# Historical Python and Django Support Documentation Plan

status: completed

## Goal

Replace the vague “Python matching the era” prerequisite with an exact,
source-backed compatibility boundary for the archived Django dependency range.

## Evidence

- `requirements.txt` preserves `Django>=1.6,<1.7`, which resolves to Django
  1.6.11 in the reviewed direct dependency audit.
- The official Django 1.6 release notes state that the series requires
  Python 2.6.5 or newer and supports the Python 2.6, 2.7, 3.2, and 3.3 series, while
  explicitly excluding Python 3.4.
- The repository's Python 3.10, 3.12, and 3.14 CI matrix intentionally runs
  dependency-free source and helper checks without installing Django 1.6.
- No maintained, secure, end-to-end Django runtime is currently declared.

## Work Completed

- Added an exact historical compatibility section and official documentation
  link to `README.md`.
- Clarified the runtime matrix, security policy, vision, and changelog so
  portable modern checks cannot be mistaken for framework support.
- Added a fail-closed baseline contract for the compatibility wording and this
  completed plan.

## Verification Completed

- Repository and external-directory `make check` passed the complete portable
  baseline.
- Three README, runtime-matrix, and completed-plan mutations were rejected;
  current-tree and 97-commit secret scans found no leaks.
- No Django server, database, browser, OAuth, provider, or live Twitter runtime
  was executed or claimed.
