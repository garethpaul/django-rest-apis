---
title: Twitter Post Redirect Get
type: fix
status: completed
date: 2026-06-12
---

# Twitter Post Redirect Get

## Summary

Redirect the authenticated home view after a successful Twitter status post so
browser refreshes cannot resubmit the same mutation. Preserve the existing
inline error and timeline behavior when Twitter rejects the post.

## Problem Frame

The home view currently handles a status POST, posts to Twitter, loads the
timeline, and renders the response directly. Refreshing that response can cause
the browser to resubmit the POST and publish a duplicate status. The view also
makes an unnecessary timeline request before the browser performs its next GET.

## Requirements

- R1. A successful non-empty status post must redirect to `/home`.
- R2. The successful POST path must not request the Twitter timeline.
- R3. A failed Twitter post must keep rendering the timeline with the stable,
  provider-detail-free error message.
- R4. GET requests and empty or invalid statuses must continue rendering the
  timeline without redirecting.
- R5. Helper and home-view tests must exercise successful redirect and failed
  post rendering without live Twitter or Django services.
- R6. The static baseline, README, VISION, and CHANGES must preserve the
  POST/Redirect/GET contract.

## Non-Goals

- Changing Twitter credentials, status length, or token fallback behavior.
- Adding success flash messages.
- Modernizing Django or the social-auth dependency stack.
- Performing live Twitter API requests.

## Work Completed

- Added an explicit successful-post outcome to the Twitter home helper.
- Redirected successful status submissions to `/home` before timeline loading.
- Preserved timeline rendering and stable errors when posting fails.
- Added isolated helper and home-view tests plus baseline and documentation
  enforcement for the POST/Redirect/GET contract.

## Verification

- `python3 scripts/test-view-helpers.py`
- `make check`
- Python 3.10, 3.12, and 3.14 matrix where locally available.
- Mutation check: removing the success redirect must fail tests.
- Mutation check: loading the timeline after a successful post must fail tests.
- `sh -n scripts/check-baseline.sh`
- `git diff --check`
