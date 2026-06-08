#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SETTINGS="$ROOT_DIR/app/settings.py"
README="$ROOT_DIR/README.md"

if grep -Fq ')e-_u9#$xfu5(uw!izbq!yu+dtf1*ce5@7w42p^ro*i-+)$yy%' "$SETTINGS"; then
  printf '%s\n' "settings.py must not ship the old public Django SECRET_KEY." >&2
  exit 1
fi

if ! grep -Fq "SECRET_KEY = required_env('DJANGO_SECRET_KEY')" "$SETTINGS"; then
  printf '%s\n' "settings.py must require DJANGO_SECRET_KEY." >&2
  exit 1
fi

if ! grep -Fq "DEBUG = env_bool('DJANGO_DEBUG', False)" "$SETTINGS"; then
  printf '%s\n' "settings.py must default DEBUG off." >&2
  exit 1
fi

if ! grep -Fq "ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS')" "$SETTINGS"; then
  printf '%s\n' "settings.py must configure ALLOWED_HOSTS from the environment." >&2
  exit 1
fi

if ! grep -Fq 'DJANGO_SECRET_KEY' "$README"; then
  printf '%s\n' "README must document DJANGO_SECRET_KEY setup." >&2
  exit 1
fi

printf '%s\n' "Django secret configuration checks passed."
