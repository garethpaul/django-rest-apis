# Twitter Timeline Screen-Name Guard

Status: Planned

## Problem

Timeline item validation currently accepts any nonblank string as a provider
screen name. The template inserts that value into a Twitter status URL path, so
malformed provider data containing separators, punctuation, or an overlong name
can produce an unintended link even though the item passed the pre-render
boundary.

## Requirements

1. Accept only canonical ASCII Twitter screen names containing 1-15 letters,
   digits, or underscores.
2. Reject non-string, blank, prefixed, punctuated, path-like, whitespace-bearing,
   non-ASCII, and overlong values before template rendering.
3. Preserve valid timeline objects verbatim and retain the existing complete-
   timeline rejection and stable generic error behavior.
4. Cover direct helper acceptance/rejection and malformed full-timeline results.
5. Add mutation-sensitive source, test, documentation, and completed-plan
   contracts.

## Scope Boundaries

- Do not normalize or rewrite provider screen names.
- Do not change templates, provider calls, result limits, posting behavior,
  credentials, dependencies, or user-visible errors.
- Do not claim live Django, OAuth, browser, or Twitter provider execution.
- Do not merge or close stacked pull requests without explicit authorization.

## Implementation

1. Add a Python 2-compatible compiled expression and a small screen-name
   predicate in `home/views.py`.
2. Use the predicate from the existing guarded timeline-item validator.
3. Add dependency-free helper and complete-timeline regression tests.
4. Extend the static baseline and contributor documentation contracts.
5. Run focused tests, hostile mutations, repository and external-directory
   `make check`, compile checks, and final artifact/secret/diff audits.

## Verification

Pending implementation and bounded validation.
