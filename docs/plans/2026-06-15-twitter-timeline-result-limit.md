---
title: Twitter Timeline Result Limit
type: reliability
status: in_progress
date: 2026-06-15
execution: code
---

# Twitter Timeline Result Limit

## Problem Frame

The home view requests ten Twitter statuses but accepts an arbitrarily long
list or tuple if the provider ignores that request limit. The response boundary
must reject oversized collections before rendering or traversing their items.

## Scope

- Define the requested timeline count once.
- Reject provider lists or tuples longer than that count.
- Preserve valid shorter results, malformed-result handling, item validation,
  post-error precedence, and the existing request screen-name guard.
- Do not change authentication, posting, templates, or provider credentials.

## Requirements

- R1. The provider request and response-length check use the same limit.
- R2. More than ten returned statuses produce the generic timeline error and
  no rendered statuses.
- R3. Ten or fewer valid statuses remain accepted.
- R4. Focused and static contracts reject removal of the limit or its tests.

## Verification

- Focused helper tests for exact-limit and oversized responses.
- Repository and external-directory `make check`.
- Hostile mutations for constant, response guard, and regression-test removal.
- Diff, generated-artifact, conflict-marker, and credential audits.

## Risks

- A provider that returns extra usable statuses is treated as malformed rather
  than silently truncated, keeping the response contract explicit.

## Status: In Progress
