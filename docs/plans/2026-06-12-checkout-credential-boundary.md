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

- Preserve the canonical bytes of every file under `.github/workflows` and the
  reviewed raw bytes of `Makefile`.
- Keep an exact recursive path/type inventory and SHA-256 manifest for every
  workflow file.
- Keep an exact recursive path/type inventory under `.github/actions` and a
  SHA-256 manifest for every repository-local `action.yml` or `action.yaml`;
  the current approved inventory is empty and the directory itself is absent.
- Traverse both Actions trees with no-follow `lstat` checks and reject every
  symlink or non-regular file, including nested symlink directories.
- Run verifier processes with `PYTHONPATH` and `PYTHONHOME` unset,
  `PYTHONNOUSERSITE=1`, and `python3 -I -S`; use the built-in `_hashlib`
  OpenSSL SHA-256 primitive rather than an import-hookable `hashlib` wrapper.
- Before repository-controlled tests, require a clean Git tree, snapshot every
  tracked file with its permission mode, index-stage metadata, and committed
  tree identity, then create exact separate test and verifier copies.
- Preserve each tracked mode in both copies and validate byte/mode equality
  before containers. Reject a source or prepared
  `scripts/check-baseline.sh` without its tracked executable bit.
- Run candidate tests and Make as non-root users in separate no-network,
  read-only, capability-free containers. The test container receives only the
  test copy; it must not mount the source, verifier, snapshot, or host tools.
  Verifier containers receive only read-only source/snapshot/verifier mounts.
- Before candidate code, resolve and verify absolute root-owned host Python,
  Git, Docker, environment, shell, and filesystem tools. Restrict host `PATH`
  to `/usr/bin:/bin` and never invoke repository-controlled shell/tool paths.
- Invoke Make with absolute `-C` and `-f Makefile` arguments, scrub
  `MAKEFILES`, `MAKEFLAGS`, `MFLAGS`, and `GNUMAKEFLAGS`, and reject every root or nested
  `GNUmakefile` or lowercase `makefile` shadow.
- Preserve the Python 3.10, 3.12, and 3.14 matrix, pinned actions, read-only
  permissions, bounded execution, and `make check` entry point through the
  canonical workflow hash. Run the checker and independent mutation tests
  before `make check`, and prevent caller `PYTHON` overrides in Make.
- Reject inventory, byte-content, line-ending, symlink, local-action, and
  verification-wiring regressions in the local baseline.

## Verification

- The local `make check` passed with all seven settings, thirteen view tests,
  and twenty-nine canonical Actions/Makefile-contract tests.
- The same gate passed from an external working directory.
- Workflow and local-action hostile mutations were rejected by the baseline
  guard, including every adversarial YAML spelling from independent review,
  a repository-local composite checkout action, added and duplicate workflow
  files, content and line-ending changes, nested directory and file symlinks,
  FIFOs and other non-regular types, Makefile no-op and interpreter mutations,
  coordinated unsafe workflow/Make changes, checker hash self-updates,
  `PYTHONPATH`/`sitecustomize`/module-shadow attacks, test-time Make replacement,
  tracked blob/index/tree mutation, verifier timing mutation, fake writable
  `PATH` tools, `GNUmakefile`/lowercase `makefile` shadows, includes, and every
  Make environment injection including `GNUMAKEFLAGS=-n`, plus prepared-copy
  mode loss and a non-executable tracked baseline.
- `git diff --check` and shell syntax validation passed.

## Maintenance Contract

Any legitimate workflow edit, workflow addition or removal, repository-local
action change, or Makefile edit requires a reviewed canonical contract update.
The review must inspect the complete changed bytes and types, update the exact
path/type inventory and SHA-256 manifests in
`scripts/check-workflow-checkout.py`, independently update the expected hashes
and mutations in `scripts/test-workflow-checkout.py`, update guidance where
needed, and rerun repository, external-directory, and hosted verification
before merging. A checker-only hash refresh is insufficient.
The hosted sequence must continue to prepare a clean tracked snapshot, run the
exact copied test inventory with isolated startup, verify the source snapshot,
run explicit `make -f Makefile`, and verify the snapshot again.

## Residual Risks

- The legacy dependency set remains unchanged and retains known vulnerability
  exposure; dependency modernization requires a separate compatibility change.
- The Python matrix verifies dependency-free source contracts; it does not establish Django runtime compatibility for the Django 1.6 application.
- A hosted runner credential-state diagnostic was not performed. The local
  checker instead freezes the complete reviewed workflow and Makefile bytes and
  rejects any unreviewed Actions path or filesystem type.
