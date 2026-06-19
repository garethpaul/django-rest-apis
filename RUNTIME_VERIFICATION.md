# Django Runtime Verification Matrix

Use this matrix for exact-head runtime evidence that cannot be inferred from
the portable `make check` baseline. Use an isolated synthetic account and
synthetic provider payloads for each scenario. Record only sanitized results; never
retain credentials, account identifiers, access tokens,
cookies, database contents, timeline content, screenshots, or logs.

Commit: pending implementation commit
Pull request: pending
Evidence status: not run

Dependency security status: direct pinned audit selected Django 1.6.11 and
reported 18 known vulnerabilities. The repository is unsuitable for live
deployment and no audit-clean claim is made.

| # | Scenario | Boundary | Required sanitized evidence | Status |
|---|---|---|---|---|
| 1 | Environment isolation | Local runtime | Python and dependency versions; isolated environment identifier | not run |
| 2 | Required configuration validation | Django settings | Missing-variable class and expected startup refusal | not run |
| 3 | Django startup and system check | Local Django | Command class, exit status, and warning count | not run |
| 4 | Database migration | Local database | Database engine class, migration command status, and unapplied count | not run |
| 5 | Anonymous home route | Django request | Route, response status, and redirect target class | not run |
| 6 | Authenticated home route | Django request | Route, response status, and template name | not run |
| 7 | Template escaping and rendering | Browser or Django client | Synthetic marker class and escaped/rendered result | not run |
| 8 | Social authentication success | Private OAuth sandbox | Synthetic provider class, callback status, and session outcome | not run |
| 9 | Social authentication denial | Private OAuth sandbox | Denial class, callback status, and stable user-facing outcome | not run |
| 10 | Valid timeline collection | Synthetic provider | Payload shape, response status, and rendered item count | not run |
| 11 | Malformed provider accessor | Synthetic provider | Failure class, response status, and contained-error outcome | not run |
| 12 | Successful status submission | Synthetic provider | POST result, redirect target, and provider call count | not run |
| 13 | Provider write failure | Synthetic provider | Failure class, response status, and preserved timeline count | not run |
| 14 | Logout and relaunch | Browser or Django client | POST result, session state, and anonymous relaunch status | not run |

## Evidence Rules

- Replace the pending commit and pull-request fields with the exact tested head
  before recording any scenario as `pass`, `fail`, or `blocked`.
- Use only `pass`, `fail`, `blocked`, or `not run`; explain blockers without
  embedding machine paths, credentials, provider data, or private identifiers.
- Keep portable settings/helper/source results separate from local Django,
  database, browser, OAuth, social-auth provider, and live Twitter evidence.
- A static check, source compile, or synthetic helper test cannot mark an
  integration scenario as passed.

No Django server, database migration, browser, OAuth, social-auth provider, or
live Twitter scenario was executed for this review. Twitter's legacy API and
the historical social-auth integration were not exercised with credentials.
