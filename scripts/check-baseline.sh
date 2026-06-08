#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SETTINGS="$ROOT_DIR/app/settings.py"
README="$ROOT_DIR/README.md"
PLAN="$ROOT_DIR/docs/plans/2026-06-08-django-settings-security-baseline.md"

require_file() {
  path=$1
  if [ ! -f "$ROOT_DIR/$path" ]; then
    printf '%s\n' "Required file is missing: $path" >&2
    exit 1
  fi
}

for path in \
  ".gitignore" \
  "CHANGES.md" \
  "README.md" \
  "SECURITY.md" \
  "VISION.md" \
  "app/settings.py" \
  "docs/plans/2026-06-08-django-settings-security-baseline.md" \
  "scripts/check-baseline.sh"; do
  require_file "$path"
done

if grep -Fq ')e-_u9#$xfu5(uw!izbq!yu+dtf1*ce5@7w42p^ro*i-+)$yy%' "$SETTINGS"; then
  printf '%s\n' "app/settings.py must not contain the old hardcoded SECRET_KEY." >&2
  exit 1
fi

if ! grep -Fq "DJANGO_SECRET_KEY" "$SETTINGS" || ! grep -Fq "DJANGO_DEBUG" "$SETTINGS"; then
  printf '%s\n' "Django SECRET_KEY and DEBUG must be controlled by environment variables." >&2
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

if ! grep -Fq ".env" "$ROOT_DIR/.gitignore"; then
  printf '%s\n' ".gitignore must ignore local environment files." >&2
  exit 1
fi

if ! grep -Fq "scripts/check-baseline.sh" "$README" || ! grep -Fq "DJANGO_SECRET_KEY" "$README"; then
  printf '%s\n' "README must document the baseline guard and required environment variables." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$PLAN"; then
  printf '%s\n' "Plan must be marked completed." >&2
  exit 1
fi

python3 -m py_compile "$SETTINGS"

printf '%s\n' "Django settings security baseline checks passed."
