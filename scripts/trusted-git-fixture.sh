#!/bin/sh
set -eu

printf '%s\n' "$1" "$2" "$3" "$4" >> "$GIT_ARGUMENT_LOG"
exec /usr/bin/git "$@"
