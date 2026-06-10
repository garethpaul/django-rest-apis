# CI Baseline

status: completed

## Context

The repository had a local Python `make check` baseline for legacy Django
settings and Twitter helper contracts, but no hosted workflow ran it for pushes
and pull requests.

## Objectives

- Run isolated settings and view-helper tests across modern Python releases.
- Avoid installing the unsupported Django 1.6-era dependency set in CI.
- Pin third-party action code and keep repository access read-only.

## Changes

- Added a GitHub Actions workflow that runs `make check` on Python 3.10, 3.12,
  and 3.14 for pushes, pull requests, and manual dispatches.
- Pinned checkout and Python setup actions to reviewed commits, limited
  repository access to read-only, and bounded execution with timeout and
  concurrency cancellation.
- Kept the historical dependency file out of CI installation and documented
  the dedicated migration boundary required for a runnable modern Django app.
- Extended the baseline guard and docs so the hosted CI path stays visible.

## Verification

- `make check`
- Python 3.10, 3.12, and 3.14 hosted jobs
- `git diff --check`
