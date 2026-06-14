# Django Runtime Verification Matrix

Status: In Progress

## Problem

Portable tests cover secret-key settings, social-auth metadata shapes, Twitter
status/result/item/text validation, hostile accessor containment, and source
compilation. The repository does not define repeatable exact-head evidence for
legacy Django startup, database initialization, rendered templates, social
authentication, or live provider responses.

## Requirements

1. Add an exact-commit matrix for environment setup, startup, migrations,
   anonymous/authenticated routes, templates, social-auth success and failure,
   timeline rendering, malformed provider data, logout, and relaunch.
2. Require synthetic account and provider data plus sanitized runtime, database,
   result, and evidence fields with explicit pass, fail, blocked, or not-run.
3. Keep settings/helper, local Django, database, browser, OAuth, and live Twitter
   evidence separate so portable checks cannot imply integration execution.
4. Add mutation-sensitive contracts for the matrix, repository guidance, and
   completed plan evidence.

## Scope Boundaries

- Do not change Python, Django behavior, templates, dependencies, migrations,
  routes, provider integration, settings, or runtime configuration.
- Do not add Django secrets, OAuth credentials, account identifiers, access
  tokens, cookies, database files, timeline content, screenshots, or logs.
- Do not claim Django server, database, browser, OAuth, or live Twitter
  execution from settings, helper, compile, or static checks.
- Do not merge or close stacked pull requests without explicit authorization.

## Verification

- Pending implementation and bounded repository validation.
