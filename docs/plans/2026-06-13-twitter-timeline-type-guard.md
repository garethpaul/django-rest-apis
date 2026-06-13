# Guard Malformed Twitter Timeline Results

status: planned

## Context

`load_twitter_home` handles `twitter.TwitterError`, but otherwise passes the
provider result directly to the template. A malformed successful response such
as `None`, a mapping, or a string can therefore reach timeline rendering even
though the view expects an ordered collection of status objects.

## Requirements

- R1. Valid list and tuple timeline results must remain renderable.
- R2. Any other timeline result type must become an empty timeline with the
  existing provider-detail-free load error.
- R3. Successful status posts must still redirect without loading a timeline.
- R4. Failed status posts must preserve their existing post error while a
  malformed timeline result is contained.
- R5. Dependency-free tests and static contracts must reject removal or
  weakening of the timeline type boundary.

## Scope Boundaries

- Do not change Twitter endpoints, request parameters, credentials, or social
  authentication lookup behavior.
- Do not broaden exception handling beyond `twitter.TwitterError`.
- Do not modernize the historical Django or python-twitter dependency set.

## Implementation

- Normalize successful timeline results at the provider boundary in
  `home/views.py`.
- Add focused helper cases in `scripts/test-view-helpers.py` for valid tuples,
  malformed results, and failed-post precedence.
- Extend `scripts/check-baseline.sh` and project documentation with a static,
  mutation-sensitive timeline result contract.

## Verification

- Run `make check` with each locally available supported Python runtime.
- Run the canonical check from an external working directory.
- Run shell syntax, bytecode compilation, and `git diff --check` checks.
- Verify isolated mutations for accepted types, malformed fallback, error
  precedence, regression tests, documentation, and completed plan evidence.
- Audit intended paths for generated artifacts and credential-like additions.
