# Twitter Timeline Status ID Limit

## Status: Completed

## Context

Timeline items currently accept any positive Python integer as a status ID.
An untrusted provider object can therefore supply an integer with thousands of
decimal digits. On supported Python releases, converting such a value for the
timeline permalink raises `ValueError` because it exceeds the interpreter's
integer-string conversion limit, turning malformed provider data into a
template-time server error.

## Priority

Medium response-boundary reliability. Reject unrenderable provider identifiers
before they reach templates.

## Requirements

- Bound accepted timeline status IDs to an unsigned 64-bit integer.
- Preserve positive IDs through `2**64 - 1` and reject zero, negatives,
  booleans, `2**64`, and arbitrarily large integers.
- Reject the complete timeline if any item has an invalid status ID.
- Preserve provider request limits, text and screen-name validation, posting
  behavior, stable errors, templates, credentials, and routes.
- Add focused tests, portable contracts, synchronized guidance, and truthful
  completion evidence.

## Scope Boundaries

- Do not change dependencies, settings, database models, templates, OAuth,
  provider request shape, result limits, text limits, or screen-name rules.
- Do not contact Django, a database, Twitter, OAuth, or a browser in tests.
- Do not merge or close stacked pull requests without explicit authorization.

## Implementation Units

1. Add one explicit maximum status-ID constant and enforce it in
   `timeline_status_is_renderable`.
2. Extend the dependency-free helper suite with exact-boundary and complete
   timeline-rejection cases.
3. Register source, regression, guidance, and completed-plan contracts in the
   portable baseline checker.

## Verification

- focused status-ID helper tests
- full repository and external-directory `make check` on available supported
  Python runtimes
- hostile constant, predicate, off-by-one, focused-test, full-timeline,
  guidance, and plan-status mutations
- shell syntax, Python compilation, exact diff, generated-artifact,
  dependency/workflow-drift, conflict-marker, whitespace, and secret audits

## Work Completed

- Added `MAX_TWITTER_STATUS_ID` at the unsigned 64-bit maximum and enforced it
  alongside the existing positive non-boolean integer predicate.
- Added exact-maximum, first-invalid, and 5,001-digit ID regressions plus
  complete-timeline rejection coverage.
- Registered implementation, tests, guidance, and completed-plan evidence in
  the portable baseline checker.

## Verification Completed

- The two focused status-ID tests passed after failing before implementation.
- Python 3.12 and Python 3.14 repository-root and external-directory `make check` passed.
- Seven hostile mutations covering the constant, predicate, off-by-one limit,
  focused test, complete-timeline test, guidance, and plan status were rejected.
- Shell syntax, Python compilation, exact diff, generated-artifact,
  dependency/workflow-drift, conflict-marker, whitespace, and secret audits
  passed before commit.
- No live Django, database, OAuth, browser, or Twitter execution was performed.
