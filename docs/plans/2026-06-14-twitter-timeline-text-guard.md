# Twitter Timeline Text Guard

Status: Completed

## Problem

Timeline item validation requires string-like text but accepts an empty or
whitespace-only value. A malformed provider response can therefore pass the
pre-render boundary even though the status body has no renderable content.

## Requirements

1. Require timeline status text to contain non-whitespace content.
2. Preserve valid text verbatim and keep existing ID, user, accessor-failure,
   collection, post-error, and generic timeline-error behavior.
3. Cover the helper and complete-timeline rejection paths.
4. Add mutation-sensitive source, test, documentation, and completed-plan
   contracts.
5. Run the full Python 3.12 and 3.14 repository gates, including an unrelated
   working-directory invocation.

## Scope Boundaries

- Do not normalize provider text before rendering or change templates.
- Do not change provider calls, item limits, status posting, credentials,
  dependencies, or user-visible errors.
- Do not claim live Django or Twitter provider execution.
- Do not merge or close stacked pull requests without explicit authorization.

## Verification

- The dependency-free view helper suite passed all 24 cases, including direct
  helper and full timeline rejection for whitespace-only provider text.
- Six hostile mutations were rejected for removed or weakened source guards,
  missing helper/loader cases, documentation drift, and reopened plan status.
- `make check` passed under Python 3.12.8 and Python 3.14.0, including seven
  settings tests, 24 view tests, source contracts, and bytecode compilation;
  the Python 3.12 gate also passed from an unrelated working directory.
- This change claims no live Django or Twitter provider execution.
