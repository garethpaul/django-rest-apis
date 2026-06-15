# Twitter Timeline Text Surrogate Guard

## Status: Planned

## Context

Timeline items currently accept any nonblank provider string within the
280-character limit. A string containing an unpaired UTF-16 surrogate passes
those checks but cannot be encoded as UTF-8, so malformed provider data can
fail later while Django prepares the response body.

## Priority

Medium response-boundary reliability. Reject provider text that cannot be
encoded for an HTTP response before it reaches the template.

## Requirements

- Reject timeline text containing lone high or low surrogate code units.
- Preserve ordinary Unicode and valid supplementary-plane characters.
- Reject the complete timeline if any item contains unencodable text.
- Preserve status-ID, result-count, text-length, screen-name, posting, stable
  error, credential, template, and route behavior.
- Add focused tests, portable contracts, synchronized guidance, and truthful
  completion evidence.

## Scope Boundaries

- Do not change dependencies, settings, database models, templates, OAuth,
  provider request shape, result limits, text limits, or screen-name rules.
- Do not contact Django, a database, Twitter, OAuth, or a browser in tests.
- Do not merge or close stacked pull requests without explicit authorization.

## Implementation Units

1. Add a small helper that recognizes strings encodable as UTF-8 and use it in
   `timeline_status_is_renderable`.
2. Extend the dependency-free helper suite with lone-surrogate rejection,
   valid supplementary-character preservation, and complete-timeline cases.
3. Register implementation, regression, guidance, and completed-plan
   contracts in the portable baseline checker.

## Verification

- focused timeline text encoding helper tests
- full repository and external-directory `make check` on available supported
  Python runtimes
- hostile helper, predicate, focused-test, complete-timeline, valid-Unicode,
  guidance, and plan-status mutations
- shell syntax, Python compilation, exact diff, generated-artifact,
  dependency/workflow-drift, conflict-marker, whitespace, and secret audits
