#!/usr/bin/env bash
set -euo pipefail

# Absolute file arguments come from lint-staged. Never run an unscoped --fix.
if [ "$#" -eq 0 ]; then
  echo 'Frontend lint requires at least one staged filename.' >&2
  exit 1
fi
cd "$(dirname "$0")/../frontend"
npx --no-install eslint --fix -- "$@"
