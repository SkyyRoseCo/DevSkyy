#!/usr/bin/env bash
# Run after root npm ci. Provision the tools used by PHP hooks and browser QA.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v composer > /dev/null
command -v php > /dev/null
test -x node_modules/.bin/playwright
composer install --working-dir=wordpress-theme/skyyrose-flagship --no-interaction --prefer-dist --no-progress
test -x wordpress-theme/skyyrose-flagship/vendor/bin/phpcbf
wordpress-theme/skyyrose-flagship/vendor/bin/phpcbf --version
wordpress-theme/skyyrose-flagship/vendor/bin/phpcs -i
if [[ "$(uname -s)" == Linux ]]; then
  node_modules/.bin/playwright install --with-deps chromium
else
  node_modules/.bin/playwright install chromium
fi
CAPTURE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/devskyy-browser-smoke.XXXXXX")"
node_modules/.bin/playwright screenshot --browser chromium about:blank "$CAPTURE_DIR/browser.png"
test -s "$CAPTURE_DIR/browser.png"
printf 'Browser launch verified: %s/browser.png\n' "$CAPTURE_DIR"
printf '%s\n' 'Tool provisioning passed. This blank-page smoke test is not theme or staging visual acceptance.'
