---
title: Checkout Credential Boundary
date: 2026-06-12
status: completed
execution: code
---

# Checkout Credential Boundary

## Summary

Disable checkout credential persistence while preserving the pinned action,
read-only permissions, supported Python matrix, and existing verification path.

## Requirements

- Keep exactly one commit-pinned checkout step.
- Set `persist-credentials: false` on that checkout step.
- Preserve the Python 3.10, 3.12, and 3.14 matrix and `make check` entry point.
- Reject workflow, evidence, and guidance regressions in the local baseline.

## Verification

- The local `make check` passed with all seven settings and thirteen view tests.
- The same gate passed from an external working directory.
- Workflow and plan hostile mutations were rejected by the baseline guard.
- `git diff --check` and shell syntax validation passed.
