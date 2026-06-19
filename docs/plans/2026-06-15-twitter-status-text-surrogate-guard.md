# Twitter Status Text Surrogate Guard

## Status: Completed

## Context

User-authored status text is trimmed, type-checked, and limited to 280
characters before it reaches `PostUpdates`. A string containing an unpaired
UTF-16 surrogate passes those checks but cannot be encoded as UTF-8, so the
provider client can raise an uncaught encoding failure instead of treating the
input as invalid.

## Priority

Medium request-boundary reliability. Reject status text that cannot be encoded
for the provider request before invoking the provider client.

## Requirements

- Reject normalized status text containing lone high or low surrogate code
  units.
- Preserve ordinary Unicode and valid supplementary-plane characters.
- Prove invalid text never reaches `PostUpdates` and preserves the existing
  timeline-rendering fallback.
- Reuse the existing UTF-8 encodability predicate shared with timeline
  validation.
- Preserve status length, posting, redirect, stable error, credential,
  template, and route behavior.
- Add focused tests, portable contracts, synchronized guidance, and truthful
  completion evidence.

## Scope Boundaries

- Do not change dependencies, settings, database models, templates, OAuth,
  provider request shape, result limits, timeline validation, or screen-name
  rules.
- Do not contact Django, a database, Twitter, OAuth, or a browser in tests.
- Do not merge or close stacked pull requests without explicit authorization.

## Implementation Units

1. Apply `twitter_text_is_utf8_encodable` at the normalized outbound status
   boundary in `home/views.py`.
2. Extend the dependency-free helper suite with lone-surrogate rejection,
   valid supplementary-character preservation, and full home-flow coverage.
3. Register implementation, regression, guidance, and completed-plan
   contracts in the portable baseline checker.

## Verification

- focused status normalization and provider-bypass tests
- full repository and external-directory `make check` on available supported
  Python runtimes
- hostile predicate, high-surrogate, low-surrogate, provider-bypass,
  valid-Unicode, guidance, plan-status, and verification-evidence mutations
- shell syntax, Python compilation, exact diff, generated-artifact,
  dependency/workflow/template-drift, conflict-marker, whitespace, and secret
  audits

## Work Completed

- Reused the timeline UTF-8 encodability predicate in outbound status
  normalization after trimming and length validation.
- Added high- and low-surrogate rejection, valid supplementary-character
  preservation, and full home-flow provider-bypass regressions.
- Registered implementation, tests, guidance, and completed-plan evidence in
  the portable baseline checker.

## Verification Completed

- The focused status and complete helper suites passed after reproducing the
  prior unencodable value accepted by `normalize_status`.
- Python 3.12 and Python 3.14 repository-root and external-directory `make check` passed.
- Eight isolated hostile mutations covering the predicate, high and low
  surrogate fixtures, provider bypass, valid Unicode preservation, guidance,
  plan status, and verification evidence were rejected.
- Shell syntax, Python compilation, exact diff, generated-artifact,
  dependency/workflow/template-drift, conflict-marker, whitespace, and secret
  audits passed before commit.
- The implementation was committed as
  `f1c6886b97c59fcb8d54ac966691adec00d3b95d`.
- Canonical hosted verification passed on that exact implementation head:
  push run `27567084975` and pull-request run `27567095220` each completed
  successfully across Python 3.10, 3.12, and 3.14. PR #19 remained open,
  clean, and mergeable, and the branch had no open code-scanning alerts.
- No live Django, database, OAuth, browser, or Twitter execution was performed.
