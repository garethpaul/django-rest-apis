#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SETTINGS="$ROOT_DIR/app/settings.py"
VIEWS="$ROOT_DIR/home/views.py"
HOME_TEMPLATE="$ROOT_DIR/templates/home.html"
BASE_TEMPLATE="$ROOT_DIR/templates/base.html"
REQUIREMENTS="$ROOT_DIR/requirements.txt"
README="$ROOT_DIR/README.md"
PLAN="$ROOT_DIR/docs/plans/2026-06-08-django-settings-security-baseline.md"
STATUS_PLAN="$ROOT_DIR/docs/plans/2026-06-08-twitter-status-normalization.md"
CHECK_PLAN="$ROOT_DIR/docs/plans/2026-06-08-django-check-wrapper.md"
TOKEN_PLAN="$ROOT_DIR/docs/plans/2026-06-08-twitter-token-fallback.md"
SOCIAL_AUTH_ROW_PLAN="$ROOT_DIR/docs/plans/2026-06-09-twitter-social-auth-row-fallback.md"
BLANK_TOKEN_PLAN="$ROOT_DIR/docs/plans/2026-06-09-twitter-blank-token-fallback.md"
ACCESS_TOKEN_ERROR_PLAN="$ROOT_DIR/docs/plans/2026-06-09-twitter-access-token-error.md"
ENV_BOOL_PLAN="$ROOT_DIR/docs/plans/2026-06-09-django-env-bool-normalization.md"
MALFORMED_TOKEN_PLAN="$ROOT_DIR/docs/plans/2026-06-09-twitter-malformed-token-fallback.md"
CI_PLAN="$ROOT_DIR/docs/plans/2026-06-10-ci-baseline.md"
SECURE_COOKIE_PLAN="$ROOT_DIR/docs/plans/2026-06-10-production-secure-cookies.md"
TWITTER_API_ERROR_PLAN="$ROOT_DIR/docs/plans/2026-06-12-twitter-api-error-boundary.md"
POST_REDIRECT_PLAN="$ROOT_DIR/docs/plans/2026-06-12-twitter-post-redirect-get.md"
CI_WORKFLOW="$ROOT_DIR/.github/workflows/check.yml"
MAKEFILE="$ROOT_DIR/Makefile"
VIEW_TESTS="$ROOT_DIR/scripts/test-view-helpers.py"

require_file() {
  path=$1
  if [ ! -f "$ROOT_DIR/$path" ]; then
    printf '%s\n' "Required file is missing: $path" >&2
    exit 1
  fi
}

for path in \
  ".gitignore" \
  ".github/workflows/check.yml" \
  "CHANGES.md" \
  "README.md" \
  "SECURITY.md" \
  "VISION.md" \
  "Makefile" \
  "requirements.txt" \
  "app/settings.py" \
  "home/views.py" \
  "templates/base.html" \
  "templates/home.html" \
  "scripts/test-settings-helpers.py" \
  "scripts/test-view-helpers.py" \
  "docs/plans/2026-06-08-django-check-wrapper.md" \
  "docs/plans/2026-06-08-django-settings-security-baseline.md" \
  "docs/plans/2026-06-08-settings-helper-regression-tests.md" \
  "docs/plans/2026-06-08-twitter-status-normalization.md" \
  "docs/plans/2026-06-08-twitter-token-fallback.md" \
  "docs/plans/2026-06-09-post-only-logout.md" \
  "docs/plans/2026-06-09-twitter-access-token-error.md" \
  "docs/plans/2026-06-09-django-env-bool-normalization.md" \
  "docs/plans/2026-06-10-ci-baseline.md" \
  "docs/plans/2026-06-10-production-secure-cookies.md" \
  "docs/plans/2026-06-12-twitter-api-error-boundary.md" \
  "docs/plans/2026-06-12-twitter-post-redirect-get.md" \
  "docs/plans/2026-06-09-twitter-malformed-token-fallback.md" \
  "docs/plans/2026-06-09-twitter-social-auth-row-fallback.md" \
  "docs/plans/2026-06-09-twitter-blank-token-fallback.md" \
  "scripts/check-baseline.sh"; do
  require_file "$path"
done

if ! grep -Fq "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" "$CI_WORKFLOW" ||
  ! grep -Fq "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405" "$CI_WORKFLOW" ||
  ! grep -Fq 'python-version: ["3.10", "3.12", "3.14"]' "$CI_WORKFLOW" ||
  ! grep -Fq "run: make check" "$CI_WORKFLOW"; then
  printf '%s\n' "GitHub Actions workflow must pin actions and run make check across supported Python releases." >&2
  exit 1
fi

if ! grep -Fq "permissions:" "$CI_WORKFLOW" || ! grep -Fq "contents: read" "$CI_WORKFLOW"; then
  printf '%s\n' "GitHub Actions workflow must keep repository access read-only." >&2
  exit 1
fi

if ! grep -Fq "workflow_dispatch:" "$CI_WORKFLOW" || ! grep -Fq "timeout-minutes: 5" "$CI_WORKFLOW"; then
  printf '%s\n' "GitHub Actions workflow must support bounded manual verification." >&2
  exit 1
fi

if ! grep -Fq "runs-on: ubuntu-24.04" "$CI_WORKFLOW"; then
  printf '%s\n' "GitHub Actions must use the stable Ubuntu 24.04 runner." >&2
  exit 1
fi

if ! grep -Fq 'ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))' "$MAKEFILE" ||
  [ "$(grep -o '\$(ROOT)' "$MAKEFILE" | wc -l | tr -d ' ')" -ne 7 ]; then
  printf '%s\n' "Make verification must resolve helper scripts from the repository root." >&2
  exit 1
fi

if grep -Fq ')e-_u9#$xfu5(uw!izbq!yu+dtf1*ce5@7w42p^ro*i-+)$yy%' "$SETTINGS"; then
  printf '%s\n' "app/settings.py must not contain the old hardcoded SECRET_KEY." >&2
  exit 1
fi

if ! grep -Fq "DJANGO_SECRET_KEY" "$SETTINGS" || ! grep -Fq "DJANGO_DEBUG" "$SETTINGS"; then
  printf '%s\n' "Django SECRET_KEY and DEBUG must be controlled by environment variables." >&2
  exit 1
fi

if ! grep -Fq "value.strip().lower()" "$SETTINGS"; then
  printf '%s\n' "Django boolean environment flags must strip whitespace before parsing." >&2
  exit 1
fi

if grep -Eq '^DEBUG[[:space:]]*=[[:space:]]*True' "$SETTINGS"; then
  printf '%s\n' "DEBUG must not default to True." >&2
  exit 1
fi

if ! grep -Fq "TEMPLATE_DEBUG = DEBUG" "$SETTINGS"; then
  printf '%s\n' "TEMPLATE_DEBUG must follow DEBUG." >&2
  exit 1
fi

if ! grep -Fq "DJANGO_ALLOWED_HOSTS" "$SETTINGS" || grep -Eq '^ALLOWED_HOSTS[[:space:]]*=[[:space:]]*\[\]' "$SETTINGS"; then
  printf '%s\n' "ALLOWED_HOSTS must be environment-driven and non-empty by default." >&2
  exit 1
fi

if ! grep -Fq "SECURE_COOKIES = not DEBUG or env_bool('DJANGO_SECURE_COOKIES', False)" "$SETTINGS" ||
  ! grep -Fq "SESSION_COOKIE_SECURE = SECURE_COOKIES" "$SETTINGS" ||
  ! grep -Fq "CSRF_COOKIE_SECURE = SECURE_COOKIES" "$SETTINGS"; then
  printf '%s\n' "Production session and CSRF cookies must always use the secure flag." >&2
  exit 1
fi

for name in SOCIAL_AUTH_TWITTER_KEY SOCIAL_AUTH_TWITTER_SECRET TWITTER_ACCESS_TOKEN TWITTER_ACCESS_TOKEN_SECRET; do
  if ! grep -Fq "$name" "$SETTINGS"; then
    printf '%s\n' "app/settings.py must read $name from the environment." >&2
    exit 1
  fi
done

if grep -Fq "YOUR_TWITTER" "$SETTINGS"; then
  printf '%s\n' "Twitter placeholder credentials must not remain in app/settings.py." >&2
  exit 1
fi

if grep -Fq "request.REQUEST" "$VIEWS" || ! grep -Fq "request.POST.get(\"status\"" "$VIEWS"; then
  printf '%s\n' "home view must read tweet status from POST only." >&2
  exit 1
fi

if ! grep -Fq "def normalize_status" "$VIEWS" || ! grep -Fq "MAX_STATUS_LENGTH = 280" "$VIEWS"; then
  printf '%s\n' "home view must normalize and bound submitted Twitter status text." >&2
  exit 1
fi

if ! grep -Fq "ImproperlyConfigured" "$VIEWS"; then
  printf '%s\n' "Twitter API setup must fail clearly when credentials are missing." >&2
  exit 1
fi

if ! grep -Fq "from django.views.decorators.http import require_POST" "$VIEWS" || ! grep -Fq "@require_POST" "$VIEWS"; then
  printf '%s\n' "Logout view must require POST instead of GET." >&2
  exit 1
fi

if grep -Fq 'href="/logout"' "$BASE_TEMPLATE"; then
  printf '%s\n' "Logout must not be exposed as a GET link." >&2
  exit 1
fi

if ! grep -Fq '<form action="/logout" method="post">' "$BASE_TEMPLATE" || ! grep -Fq "{% csrf_token %}" "$BASE_TEMPLATE"; then
  printf '%s\n' "Logout template must use a CSRF-protected POST form." >&2
  exit 1
fi

if ! grep -Fq "https://twitter.com" "$HOME_TEMPLATE" || ! grep -Fq 'rel="noopener noreferrer"' "$HOME_TEMPLATE"; then
  printf '%s\n' "Twitter status links must use HTTPS and safe external-link rel attributes." >&2
  exit 1
fi

for requirement in "Django>=1.6,<1.7" "python-social-auth>=0.1.26,<0.3" "python-twitter>=2,<4" "South>=0.8,<1" "Fabric>=1,<2"; do
  if ! grep -Fq "$requirement" "$REQUIREMENTS"; then
    printf '%s\n' "requirements.txt must pin legacy dependency era: $requirement" >&2
    exit 1
  fi
done

if ! grep -Fq ".env" "$ROOT_DIR/.gitignore"; then
  printf '%s\n' ".gitignore must ignore local environment files." >&2
  exit 1
fi

if ! grep -Fq "scripts/check-baseline.sh" "$README" || ! grep -Fq "DJANGO_SECRET_KEY" "$README"; then
  printf '%s\n' "README must document the baseline guard and required environment variables." >&2
  exit 1
fi

if ! grep -Fq "make check" "$README"; then
  printf '%s\n' "README must document the root make check gate." >&2
  exit 1
fi

if ! grep -Fq "Do not install these historical requirements into a modern environment" "$README"; then
  printf '%s\n' "README must warn against installing the legacy dependency stack on modern hosts." >&2
  exit 1
fi

if ! grep -Fq "status normalization" "$README"; then
  printf '%s\n' "README must document the Twitter status normalization checks." >&2
  exit 1
fi

if ! grep -Fq "missing social OAuth token fallback" "$README"; then
  printf '%s\n' "README must document missing social OAuth token fallback." >&2
  exit 1
fi

if ! grep -Fq "social-auth row fallback" "$README" ||
  ! grep -Fq "docs/plans/2026-06-09-twitter-social-auth-row-fallback.md" "$README"; then
  printf '%s\n' "README must document missing social-auth row fallback." >&2
  exit 1
fi

if ! grep -Fq "blank social OAuth token fallback" "$README" ||
  ! grep -Fq "docs/plans/2026-06-09-twitter-blank-token-fallback.md" "$README"; then
  printf '%s\n' "README must document blank social OAuth token fallback." >&2
  exit 1
fi

if ! grep -Fq "malformed social OAuth token fallback" "$README" ||
  ! grep -Fq "docs/plans/2026-06-09-twitter-malformed-token-fallback.md" "$README"; then
  printf '%s\n' "README must document malformed social OAuth token fallback." >&2
  exit 1
fi

if ! grep -Fq "missing Twitter access tokens fail clearly" "$README" ||
  ! grep -Fq "docs/plans/2026-06-09-twitter-access-token-error.md" "$README"; then
  printf '%s\n' "README must document missing Twitter access token configuration errors." >&2
  exit 1
fi

if ! grep -Fq "parsing trims whitespace" "$README" ||
  ! grep -Fq "docs/plans/2026-06-09-django-env-bool-normalization.md" "$README"; then
  printf '%s\n' "README must document boolean environment flag normalization." >&2
  exit 1
fi

if ! grep -Fq "POST-only logout" "$README"; then
  printf '%s\n' "README must document the POST-only logout guard." >&2
  exit 1
fi

if ! grep -Fq "GitHub Actions" "$README" ||
  ! grep -Fq "docs/plans/2026-06-10-ci-baseline.md" "$README" ||
  ! grep -Fq "GitHub Actions" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "GitHub Actions" "$ROOT_DIR/SECURITY.md" ||
  ! grep -Fq "GitHub Actions" "$ROOT_DIR/CHANGES.md"; then
  printf '%s\n' "Project docs must record the GitHub Actions CI baseline." >&2
  exit 1
fi

if ! grep -Fq "Fall back to environment Twitter tokens" "$ROOT_DIR/VISION.md"; then
  printf '%s\n' "VISION.md must keep social-auth fallback direction visible." >&2
  exit 1
fi

if ! grep -Fq "Ignore blank saved social-auth tokens" "$ROOT_DIR/VISION.md"; then
  printf '%s\n' "VISION.md must keep blank social-auth token handling visible." >&2
  exit 1
fi

if ! grep -Fq "Ignore malformed saved social-auth tokens" "$ROOT_DIR/VISION.md"; then
  printf '%s\n' "VISION.md must keep malformed social-auth token handling visible." >&2
  exit 1
fi

if ! grep -Fq "Fail clearly when Twitter access tokens are absent" "$ROOT_DIR/VISION.md"; then
  printf '%s\n' "VISION.md must keep missing access-token error handling visible." >&2
  exit 1
fi

if ! grep -Fq "Contain expected Twitter API failures" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "docs/plans/2026-06-12-twitter-api-error-boundary.md" "$README" ||
  ! grep -Fq "Expected Twitter API errors" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "Project docs must preserve the Twitter API failure boundary." >&2
  exit 1
fi

if ! grep -Fq "Normalize boolean environment flags" "$ROOT_DIR/VISION.md"; then
  printf '%s\n' "VISION.md must keep boolean environment flag normalization visible." >&2
  exit 1
fi

if ! grep -Fq "check: verify" "$ROOT_DIR/Makefile"; then
  printf '%s\n' "Makefile must expose make check as the repository verification wrapper." >&2
  exit 1
fi

if ! grep -Fq "build:" "$ROOT_DIR/Makefile" || \
  ! grep -Fq "verify: lint test build" "$ROOT_DIR/Makefile"; then
  printf '%s\n' "Makefile must expose build and include it in verification." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$PLAN"; then
  printf '%s\n' "Plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$STATUS_PLAN"; then
  printf '%s\n' "Status normalization plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$CHECK_PLAN"; then
  printf '%s\n' "Check wrapper plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$TOKEN_PLAN" || ! grep -Fq "make check" "$TOKEN_PLAN"; then
  printf '%s\n' "Twitter token fallback plan must be marked completed and record make check verification." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$SOCIAL_AUTH_ROW_PLAN" || ! grep -Fq "make check" "$SOCIAL_AUTH_ROW_PLAN"; then
  printf '%s\n' "Twitter social-auth row fallback plan must be marked completed and record make check verification." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$BLANK_TOKEN_PLAN" || ! grep -Fq "make check" "$BLANK_TOKEN_PLAN"; then
  printf '%s\n' "Twitter blank token fallback plan must be marked completed and record make check verification." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$ROOT_DIR/docs/plans/2026-06-09-post-only-logout.md"; then
  printf '%s\n' "POST-only logout plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "make check" "$ROOT_DIR/docs/plans/2026-06-09-post-only-logout.md"; then
  printf '%s\n' "POST-only logout plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "Status: Completed" "$ACCESS_TOKEN_ERROR_PLAN"; then
  printf '%s\n' "Twitter access token error plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "make check" "$ACCESS_TOKEN_ERROR_PLAN"; then
  printf '%s\n' "Twitter access token error plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "Status: Completed" "$ENV_BOOL_PLAN"; then
  printf '%s\n' "Django env bool normalization plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "make check" "$ENV_BOOL_PLAN"; then
  printf '%s\n' "Django env bool normalization plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "Status: Completed" "$MALFORMED_TOKEN_PLAN"; then
  printf '%s\n' "Twitter malformed token fallback plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "make check" "$MALFORMED_TOKEN_PLAN"; then
  printf '%s\n' "Twitter malformed token fallback plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$CI_PLAN" ||
  ! grep -Fq "make check" "$CI_PLAN"; then
  printf '%s\n' "CI baseline plan must be completed and record make check verification." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$SECURE_COOKIE_PLAN" ||
  ! grep -Fq "make check" "$SECURE_COOKIE_PLAN"; then
  printf '%s\n' "Production secure cookie plan must be completed and record verification." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$TWITTER_API_ERROR_PLAN" ||
  ! grep -Fq "Mutations removing either" "$TWITTER_API_ERROR_PLAN"; then
  printf '%s\n' "Twitter API error-boundary plan must record completed mutation verification." >&2
  exit 1
fi

if ! grep -Fq "ImproperlyConfigured" "$ROOT_DIR/scripts/test-settings-helpers.py"; then
  printf '%s\n' "Settings helper tests must cover the production secret-key failure." >&2
  exit 1
fi

if ! grep -Fq "test_env_bool_strips_and_parses_expected_truthy_values" "$ROOT_DIR/scripts/test-settings-helpers.py"; then
  printf '%s\n' "Settings helper tests must cover whitespace-normalized boolean flags." >&2
  exit 1
fi

if ! grep -Fq "test_production_always_uses_secure_session_and_csrf_cookies" "$ROOT_DIR/scripts/test-settings-helpers.py" ||
  ! grep -Fq "test_debug_https_can_opt_in_to_secure_cookies" "$ROOT_DIR/scripts/test-settings-helpers.py"; then
  printf '%s\n' "Settings helper tests must cover production and debug secure-cookie behavior." >&2
  exit 1
fi

if ! grep -Fq "test_normalize_status_ignores_overlong_text" "$VIEW_TESTS"; then
  printf '%s\n' "View helper tests must cover overlong status submissions." >&2
  exit 1
fi

if ! grep -Fq "def load_twitter_home" "$VIEWS" ||
  [ "$(grep -Fc 'except twitter.TwitterError' "$VIEWS")" -lt 2 ] ||
  ! grep -Fq "test_load_twitter_home_preserves_timeline_when_post_fails" "$VIEW_TESTS" ||
  ! grep -Fq "test_load_twitter_home_returns_stable_error_when_timeline_fails" "$VIEW_TESTS" ||
  ! grep -Fq "twitter_error" "$HOME_TEMPLATE"; then
  printf '%s\n' "Twitter API failures must render stable view errors with helper coverage." >&2
  exit 1
fi

if ! grep -Fq "return [], None, True" "$VIEWS" ||
  ! grep -Fq "if posted:" "$VIEWS" ||
  ! grep -Fq "return HttpResponseRedirect('/home')" "$VIEWS" ||
  ! grep -Fq "test_load_twitter_home_skips_timeline_after_successful_post" "$VIEW_TESTS" ||
  ! grep -Fq "test_home_redirects_after_successful_status_post" "$VIEW_TESTS" ||
  ! grep -Fq "test_home_renders_timeline_when_status_post_fails" "$VIEW_TESTS"; then
  printf '%s\n' "Successful Twitter posts must use the tested POST/Redirect/GET path." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$POST_REDIRECT_PLAN" ||
  ! grep -Fq "make check" "$POST_REDIRECT_PLAN"; then
  printf '%s\n' "Twitter POST/Redirect/GET plan must remain completed and verified." >&2
  exit 1
fi

if grep -Fq "provider detail" "$VIEWS"; then
  printf '%s\n' "Twitter API view errors must not expose provider exception details." >&2
  exit 1
fi

if ! grep -Fq "test_get_twitter_uses_environment_tokens_when_social_token_is_missing" "$VIEW_TESTS"; then
  printf '%s\n' "View helper tests must cover missing social OAuth token fallback." >&2
  exit 1
fi

if ! grep -Fq "test_get_twitter_uses_environment_tokens_when_social_auth_is_missing" "$VIEW_TESTS"; then
  printf '%s\n' "View helper tests must cover missing social-auth row fallback." >&2
  exit 1
fi

if ! grep -Fq "test_get_twitter_uses_environment_tokens_when_social_token_is_blank" "$VIEW_TESTS"; then
  printf '%s\n' "View helper tests must cover blank social OAuth token fallback." >&2
  exit 1
fi

if ! grep -Fq "test_get_twitter_uses_environment_tokens_when_social_token_is_malformed" "$VIEW_TESTS"; then
  printf '%s\n' "View helper tests must cover malformed social OAuth token fallback." >&2
  exit 1
fi

if ! grep -Fq "test_get_twitter_raises_configuration_error_when_access_tokens_are_missing" "$VIEW_TESTS"; then
  printf '%s\n' "View helper tests must cover missing Twitter access token configuration errors." >&2
  exit 1
fi

if ! grep -Fq "extra_data.get('access_token')" "$VIEWS"; then
  printf '%s\n' "get_twitter must read optional social OAuth token data without KeyError." >&2
  exit 1
fi

if ! grep -Fq "def normalize_token" "$VIEWS"; then
  printf '%s\n' "get_twitter must normalize blank credential values before using them." >&2
  exit 1
fi

if ! grep -Fq "STRING_TYPES" "$VIEWS" || ! grep -Fq "not isinstance(value, STRING_TYPES)" "$VIEWS"; then
  printf '%s\n' "get_twitter must ignore malformed non-string credential values." >&2
  exit 1
fi

if ! grep -Fq "except UserSocialAuth.DoesNotExist" "$VIEWS"; then
  printf '%s\n' "get_twitter must fall back when the social-auth row is missing." >&2
  exit 1
fi

if grep -Fq "raise Exception('No user for twitter API call')" "$VIEWS" ||
  ! grep -Fq "Twitter access token and secret must be configured" "$VIEWS"; then
  printf '%s\n' "get_twitter must fail clearly when Twitter access tokens are missing." >&2
  exit 1
fi

python3 -m py_compile "$SETTINGS" "$VIEWS" "$VIEW_TESTS"
python3 "$ROOT_DIR/scripts/test-settings-helpers.py"
python3 "$VIEW_TESTS"

printf '%s\n' "Django settings security baseline checks passed."
