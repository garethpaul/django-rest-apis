---
title: Twitter Timeline Text Limit
type: security
status: completed
date: 2026-06-15
---

# Twitter Timeline Text Limit

## Problem

Successful Twitter timeline items require nonblank text but currently accept an
arbitrarily large provider-controlled string. That allows malformed responses
to pass validation and expand template rendering beyond the same 280-character
boundary already enforced for posted statuses.

## Priorities

1. P0: Reject timeline item text longer than `MAX_STATUS_LENGTH`.
2. P1: Preserve exact-limit responses, complete-timeline rejection, and posting
   error precedence.
3. P2: Keep provider requests, templates, authentication, and dependencies
   unchanged.

## Requirements

- Reuse `MAX_STATUS_LENGTH` for provider-returned timeline text.
- Accept nonblank text at exactly the configured limit.
- Reject the complete timeline when any item exceeds the limit.
- Preserve existing accessor exception containment and generic error handling.
- Add mutation-sensitive tests, source contracts, guidance, and completed-plan
  evidence.
- Do not claim live Django, database, OAuth, browser, or Twitter execution.

## Implementation Units

### U1: Timeline Item Text Boundary

**File:** `home/views.py`

Extend `timeline_status_is_renderable` with the existing status-length limit
without changing accepted object shape or provider call behavior.

### U2: Boundary Regression Coverage

**File:** `scripts/test-view-helpers.py`

Cover exact-limit acceptance, oversized item rejection, and posting-error
precedence when an oversized timeline item follows a failed post.

### U3: Portable Contract And Guidance

**Files:** `scripts/check-baseline.sh`, `README.md`, `SECURITY.md`, `VISION.md`,
`CHANGES.md`, and this plan.

Protect the implementation, focused tests, maintained guidance, and completed
verification evidence.

## Verification

- Run focused helper tests and Python compilation.
- Run repository-root and external-directory `make check` on available supported
  Python versions.
- Reject isolated limit, predicate, focused-test, guidance, and incomplete-plan
  mutations.
- Audit the exact diff, Python caches, generated artifacts, dependency/workflow
  drift, conflict markers, whitespace, and credential-shaped additions.

## Completion Evidence

- Reused `MAX_STATUS_LENGTH` to reject oversized provider timeline text while
  preserving nonblank text at exactly 280 characters.
- Added focused exact-limit, oversized-result, and posting-error precedence
  regressions; the two oversized scenarios failed before the source guard.
- repository-root and external-directory `make check` passed on Python 3.12 and Python 3.14 with 7 settings tests and 34 view-helper tests per gate.
- Six hostile mutations were rejected for predicate removal, an off-by-one
  boundary, focused-test removal, precedence-test removal, missing guidance,
  and incomplete plan status.
- Exact-path diff, Python-cache cleanup, generated-artifact,
  dependency/workflow-drift, conflict-marker, whitespace, and
  credential-shaped-addition audits passed.
- No live Django, database, OAuth, browser, or Twitter execution was performed.

## Scope Boundaries

- Do not change template markup, escaping, provider request counts, credentials,
  posting behavior, or error copy.
- Do not update dependencies or workflows.
- Keep this pull request stacked on PR #15 and preserve base-first ordering.
