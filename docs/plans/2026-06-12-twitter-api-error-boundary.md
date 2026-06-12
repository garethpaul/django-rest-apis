# Twitter API Error Boundary

status: completed

## Context

The authenticated home view calls `PostUpdates` and `GetUserTimeline` without
handling the `TwitterError` raised by the pinned python-twitter versions. A
provider rejection, rate limit, or temporary API failure therefore escapes as
an internal Django error.

## Priority

Expected upstream failures should not take down the page or expose provider
details. A failed post should still allow an existing timeline to render, while
a failed timeline should produce an empty state and a stable message.

## Prioritized Backlog

1. Contain documented python-twitter API failures in the home view now.
2. Preserve explicit Django configuration errors from `get_twitter`.
3. Modernize the unsupported Django and Twitter dependency stack separately.

## Implementation

- Add a helper that posts an optional status and loads the timeline.
- Catch only `twitter.TwitterError` around provider operations.
- Preserve timeline results when posting fails and return an empty timeline
  when loading fails.
- Render generic user-facing messages without provider exception text.
- Add no-Django-runtime regression tests and baseline contracts.

## Verification

- `sh -n scripts/check-baseline.sh`
- `python3 -m py_compile home/views.py scripts/test-view-helpers.py`
- `python3 scripts/test-view-helpers.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
- Mutations removing either `TwitterError` boundary or exposing provider detail
  must fail.
