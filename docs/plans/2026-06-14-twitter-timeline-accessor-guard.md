# Contain Twitter Timeline Attribute Failures

Status: Completed

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

Document the provider-object exception boundary and completed validation.

## Verification

Verification: Completed

- Python 3.12.8 and Python 3.14.0 each pass seven settings tests, 24 view-helper
  tests, source contracts, and bytecode compilation through full `make check`.
- The external-working-directory Python 3.12.8 `make check` passes from `/tmp`.
- Eight focused hostile mutations alter exception scope, rejection behavior,
  status/user accessor fixtures, malformed-item coverage, failed-post
  precedence, documentation, or plan status; every mutation is rejected.
- Shell and Python syntax, whitespace, exact-diff, artifact, untracked-file, and
  credential-shaped addition audits pass.
- Plan-aware correctness, testing, maintainability, security, reliability, and
  project-standards review found no actionable issues.
- `agent-browser` is unavailable and the legacy project was not started; no
  browser, Django server, database, template, social-auth, or live Twitter
  execution is claimed.

## Work Completed

- Wrapped timeline status, text, nested user, screen-name, and final validation
  operations in one provider-object exception boundary.
- Returned `False` for raised provider attributes so the existing complete-list
  rejection and generic timeline error handle the failure.
- Added direct status and nested-user accessor regressions plus integration
  coverage for failed-post error precedence.

## Scope Boundaries

- Do not change timeline field requirements, Twitter API calls, template output,
  post/redirect behavior, or user-visible error text.
- Do not broaden exception handling around network calls beyond the existing
  `TwitterError` boundary.
- Do not claim live Django, database, social-auth, template, or Twitter provider
  execution.

This change claims no live Django or Twitter provider execution.
