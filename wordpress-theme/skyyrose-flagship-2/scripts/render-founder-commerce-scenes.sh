#!/usr/bin/env bash
# Render the nine founder commerce scenes at three review viewports.
set -euo pipefail

theme_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_dir="$(cd "$theme_dir/../.." && pwd)"
runner="$theme_dir/scripts/render-founder-commerce-scenes.cjs"
port="${SR2_COMMERCE_RENDER_PORT:-18109}"
base_url="http://127.0.0.1:${port}/tools/v2-theme-preview.php"
server_log="$(mktemp -t sr2-commerce-render.XXXXXX)"
server_pid=""

cleanup() {
	if [[ -n "$server_pid" ]]; then
		kill "$server_pid" 2>/dev/null || true
		wait "$server_pid" 2>/dev/null || true
	fi
	rm -f "$server_log"
}
trap cleanup EXIT

# Some desktop hosts export both FORCE_COLOR and NO_COLOR. Node warns when
# both are present, so prefer the explicit no-color setting for this QA task.
unset FORCE_COLOR

runtime_node_modules="${SR2_NODE_MODULES:-}"
if [[ -z "$runtime_node_modules" && -d "$theme_dir/node_modules/playwright" && -d "$theme_dir/node_modules/sharp" ]]; then
	runtime_node_modules="$theme_dir/node_modules"
fi
if [[ -z "$runtime_node_modules" ]]; then
	user_name="$(id -un)"
	bundled_node_modules="/Users/${user_name}/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"
	if [[ -d "$bundled_node_modules/playwright" && -d "$bundled_node_modules/sharp" ]]; then
		runtime_node_modules="$bundled_node_modules"
	fi
fi
if [[ -z "$runtime_node_modules" ]]; then
	echo 'Commerce scene rendering requires Playwright and Sharp. Set SR2_NODE_MODULES to a node_modules directory containing both packages.' >&2
	exit 1
fi

NODE_PATH="$runtime_node_modules" node -e "require('playwright'); require('sharp')"
php -l "$repo_dir/tools/v2-theme-preview.php" >/dev/null

php -S "127.0.0.1:${port}" -t "$repo_dir" >"$server_log" 2>&1 &
server_pid="$!"
for attempt in {1..30}; do
	if curl --silent --fail --max-time 1 "$base_url?route=black-rose" >/dev/null 2>&1; then
		break
	fi
	if [[ "$attempt" -eq 30 ]]; then
		cat "$server_log" >&2
		exit 1
	fi
	sleep 0.1
done

NODE_PATH="$runtime_node_modules" \
	SR2_COMMERCE_PREVIEW_URL="$base_url" \
	node "$runner"
