# Portable Parent Execute Check Plan

Status: Completed

## Goal

Keep checkout-copy mode validation meaningful when the source checkout lives
under owner-only directories such as the canonical `.explore` workspace.

## Evidence

- On an unchanged `master` checkout whose repository directories are mode
  `0700`, `make lint` fails in
  `test_prepare_preserves_and_validates_tracked_file_modes`.
- PR #21 deliberately changed the tracked script assertion from exact `0755`
  to requiring owner execute permission, but its parent-directory assertion
  still requires all three execute bits with `(mode & 0o111) == 0o111`.
- Git does not track directory modes. The security property needed by the
  prepared copy is that the executing owner can traverse its directories.

## Decision

Require owner execute permission for copied parent directories, matching the
portable executable-file assertion and preserving failure for non-traversable
owner directories.

## Verification

1. Preserve the failing `make lint` output as the red regression.
2. Change only the parent-directory assertion.
3. Run the focused test, mutation checks, and `make check`.
4. Require hosted exact-head checks before merge.

## Verification Evidence

- RED: unchanged `master` failed because mode `0700` produced only the owner
  execute bit instead of all three execute bits.
- GREEN: the focused 32-test checkout-contract suite passed after requiring
  owner traversal and explicitly setting the synthetic repository and scripts
  directory to `0700`; the owner-only directory regression passed.
- The hostile all-execute-bit mutation was rejected by the focused regression.
- Repository and external-directory `make check` passed.
