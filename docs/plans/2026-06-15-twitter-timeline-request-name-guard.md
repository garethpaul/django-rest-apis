# Twitter Timeline Request Screen-Name Guard

Status: Completed

## Problem

Timeline response items now require canonical Twitter screen names, but
`load_twitter_home()` still forwards the local Django username directly to
`GetUserTimeline`. A username containing punctuation, whitespace, non-ASCII
text, or more than 15 characters therefore crosses the provider boundary even
though it cannot be a canonical Twitter screen name.

## Requirements

1. Reject a noncanonical timeline request screen name before calling
   `GetUserTimeline`.
2. Preserve successful posting behavior and the existing post-error precedence.
3. Return the existing stable timeline error when no earlier post error exists.
4. Prove malformed request names do not invoke the provider timeline method.
5. Add mutation-sensitive source, test, documentation, and completed-plan
   contracts.

## Scope Boundaries

- Do not normalize, truncate, or rewrite local usernames.
- Do not change provider response validation, posting limits, credentials,
  templates, dependencies, or user-visible error strings.
- Do not claim live Django, database, OAuth, browser, or Twitter execution.
- Do not merge or close stacked pull requests without explicit authorization.

## Implementation

1. Reuse `twitter_screen_name_is_valid()` immediately before the timeline API
   request.
2. Return an empty timeline with the existing error contract when validation
   fails.
3. Add direct loader regressions for valid forwarding, malformed rejection,
   provider non-invocation, and post-error precedence.
4. Extend the static baseline and repository documentation contracts.
5. Run focused tests, hostile mutations, root and external-directory
   `make check`, compilation, and final artifact/secret/diff audits.

## Priority Follow-Ups

1. P0: contain malformed timeline request identifiers before provider I/O.
2. P1: exercise the stacked Django/OAuth flow in a configured runtime.
3. P2: verify behavior against a maintained provider integration before any
   dependency modernization.

## Verification

- The test-first helper run failed only the two new provider non-invocation
  regressions before the source guard was added; all 29 view helper tests then
  passed.
- Six effective hostile mutations were rejected for guard removal, inverted
  validation, either regression removal, README contract removal, and reopened
  plan status.
- Disposable completed-plan `make check` gates passed with Python 3.12 and
  Python 3.14 from both the repository root and an external working directory.
- Final worktree validation passed the same root and external-directory matrix
  after this completed evidence was recorded.
- This change claims no live Django, database, OAuth, browser, or Twitter
  provider execution.
