---
title: Django REST APIs Check Wrapper
type: chore
status: completed
date: 2026-06-08
---

# Django REST APIs Check Wrapper

## Summary

Add a repository-standard `make check` entry point that runs the existing
legacy Django settings and view-helper verification gates from the repository
root.

## Requirements

- R1. `make check` must run the source baseline plus the no-Django-runtime
  settings and view helper tests.
- R2. The Makefile must expose `lint`, `test`, `verify`, and `check` targets
  without requiring installation of the legacy Django dependency stack.
- R3. README, CHANGES, and baseline checks must document and preserve the root
  check wrapper.

## Verification

- `make check`
- `scripts/check-baseline.sh`
- `git diff --check`
