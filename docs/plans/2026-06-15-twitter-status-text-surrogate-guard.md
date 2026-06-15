# Twitter Status Text Surrogate Guard

## Status: Planned

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
