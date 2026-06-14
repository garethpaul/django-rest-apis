# Contain Twitter Timeline Attribute Failures

Status: In Progress

## Context

Timeline shape validation checks the provider status ID, text, user, and screen
name before the template renders them. Those reads currently use unguarded
`getattr` calls. A malformed provider object with a raising property or custom
attribute hook can therefore escape validation and turn a bad timeline item
into a server error instead of the existing provider-neutral timeline failure.

## Requirements

- R1. Treat exceptions raised while reading timeline status or nested user
  attributes as a non-renderable item.
- R2. Preserve valid status acceptance, integer/string constraints, tuple/list
  support, and the existing provider-detail-free timeline error.
- R3. Preserve failed-post error precedence when timeline validation also
  rejects an item.
- R4. Add dependency-free regressions for raising status and nested-user
  accessors without requiring the legacy Django runtime.
- R5. Add static and mutation-sensitive contracts for exception containment and
  completed verification evidence.

## Implementation Units

### 1. Attribute containment

Files:

- `home/views.py`

Keep attribute reads inside the renderability helper and return `False` when a
provider-controlled accessor raises.

### 2. Regression and source contracts

Files:

- `scripts/test-view-helpers.py`
- `scripts/check-baseline.sh`

Exercise failures at the status and nested-user levels and prove the complete
timeline is rejected through the existing stable error path.

### 3. Guidance and evidence

Files:

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `AGENTS.md`

Document the provider-object exception boundary and completed validation.

## Verification

Verification: Pending

- Run Python 3.12 and 3.14 helper suites, source contracts, bytecode compilation,
  external-working-directory validation, and full `make check`.
- Run focused hostile mutations against exception containment, nested access,
  regression coverage, documentation, and plan completion status.
- Inspect the exact diff, artifacts, whitespace, and credential-shaped additions
  before committing.

## Scope Boundaries

- Do not change timeline field requirements, Twitter API calls, template output,
  post/redirect behavior, or user-visible error text.
- Do not broaden exception handling around network calls beyond the existing
  `TwitterError` boundary.
- Do not claim live Django, database, social-auth, template, or Twitter provider
  execution.
