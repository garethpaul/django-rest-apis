# Guard Malformed Twitter Timeline Items

status: in progress

## Context

`load_twitter_home` rejects malformed outer timeline result types, but a list
or tuple can still contain values that do not provide the fields dereferenced
by `templates/home.html`. A successful provider result containing a missing or
malformed status ID, text value, user object, or screen name can therefore
reach rendering as a broken timeline instead of the existing contained
provider failure.

## Requirements

- R1. Valid list and tuple timelines containing renderable status objects must
  remain unchanged.
- R2. Each status must provide a positive integer ID, string text, and a
  nonblank string `user.screen_name` before the timeline reaches the template.
- R3. A malformed item must reject the complete timeline with the existing
  provider-detail-free load error rather than silently publishing partial
  provider data.
- R4. A failed status post must retain its existing post error if the following
  timeline contains a malformed item.
- R5. Dependency-free tests and static contracts must reject removal or
  weakening of the item boundary.

## Scope Boundaries

- Do not change Twitter endpoints, request parameters, credentials, social
  authentication lookup behavior, or template markup.
- Do not broaden exception handling beyond attribute access needed to inspect
  successful provider values.
- Do not modernize the historical Django or python-twitter dependency set.

## Implementation

- Add a small renderability predicate for the template's exact status fields.
- Apply the predicate only after the existing list-or-tuple result boundary.
- Add focused helper cases for accepted items, malformed top-level fields,
  malformed nested users, whole-timeline rejection, and failed-post precedence.
- Extend the baseline scanner and project documentation with mutation-sensitive
  source, test, and completed-plan contracts.

## Verification

- Run `make check` with every locally available supported Python runtime.
- Run the canonical check from an external working directory.
- Run shell syntax, bytecode compilation, and `git diff --check` checks.
- Verify isolated mutations for the predicate, required fields, whole-timeline
  rejection, error precedence, regression tests, documentation, and completed
  plan evidence.
- Audit intended paths for generated artifacts and credential-like additions.

## Risks

- The legacy provider may expose an undocumented status shape; the guard is
  deliberately limited to fields the current template already requires.
- Live Twitter responses and Django template rendering remain unavailable on
  this host, so dependency-free tests prove the boundary rather than provider
  compatibility.
