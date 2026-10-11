#!/usr/bin/env bash
# Verify that the V2 reconnect records describe the active workspace. Normal
# reconnects report candidate drift without blocking edits; --strict preserves
# the immutable-candidate requirements used before release or handoff.
set -euo pipefail

strict=0
if [[ "${1:-}" == "--strict" ]]; then
	strict=1
elif [[ -n "${1:-}" ]]; then
	echo "Usage: $0 [--strict]" >&2
	exit 2
fi

warning_count=0
report_candidate_drift() {
	local message="$1"
	if [[ "$strict" -eq 1 ]]; then
		echo "FAIL V2 reconnect guard: $message" >&2
		exit 1
	fi
	echo "WARN V2 reconnect guard: $message" >&2
	warning_count=$((warning_count + 1))
}

THEME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$THEME_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if ! expected_branch="$(jq -er '.candidate.branch | strings | select(length > 0)' .fashion-theme/codex-desktop-handoff.json)" || \
	! git check-ref-format --branch "$expected_branch" >/dev/null; then
	echo 'FAIL V2 reconnect guard: handoff candidate branch is missing or invalid.' >&2
	exit 1
fi
branch="$(git branch --show-current)"
if [[ "$branch" != "$expected_branch" ]]; then
	report_candidate_drift "expected candidate branch $expected_branch, found ${branch:-detached}"
fi

for document in \
	.fashion-theme/v2-remodel-ledger.json \
	.fashion-theme/workspace-ledger.json \
	.fashion-theme/codex-desktop-handoff.json; do
	jq empty "$document"
done

while IFS=$'\t' read -r manifest_path expected_hash; do
	if [[ ! -f "$manifest_path" ]]; then
		echo "FAIL V2 reconnect guard: handoff manifest missing: $manifest_path" >&2
		exit 1
	fi
	actual_hash="$(shasum -a 256 "$manifest_path" | awk '{print $1}')"
	if [[ "$actual_hash" != "$expected_hash" ]]; then
		report_candidate_drift "handoff manifest hash drift: $manifest_path"
	fi
done < <(jq -r '.manifests | to_entries[] | [.value.path, .value.sha256] | @tsv' .fashion-theme/codex-desktop-handoff.json)

integration="$(jq -r '.current_integration.current_integration_commit' .fashion-theme/v2-remodel-ledger.json)"
workspace_integration="$(jq -r '.worktrees[] | select(.worktree == "/Users/theceo/DevSkyy") | .current_integration_commit' .fashion-theme/workspace-ledger.json)"
handoff_integration="$(jq -r '.candidate.current_integration_commit' .fashion-theme/codex-desktop-handoff.json)"

if [[ -z "$integration" || "$integration" == "null" || "$integration" != "$workspace_integration" || "$integration" != "$handoff_integration" ]]; then
	echo 'FAIL V2 reconnect guard: ledger and handoff integration commits disagree.' >&2
	exit 1
fi

git cat-file -e "${integration}^{commit}"
if ! git merge-base --is-ancestor "$integration" HEAD; then
	echo "FAIL V2 reconnect guard: integration commit $integration is not in this checkout." >&2
	exit 1
fi

# A source checkpoint is followed only by its single metadata checkpoint. Any
# farther distance means the reconnect records were not refreshed after work.
distance="$(git rev-list --count "${integration}..HEAD")"
if [[ "$distance" -gt 1 ]]; then
	report_candidate_drift "handoff is $distance commits behind HEAD; refresh the ledgers before strict verification."
fi

if [[ "$distance" -eq 1 ]]; then
	if git diff --name-only "$integration..HEAD" | grep -Ev '^\.fashion-theme/(v2-remodel-ledger|workspace-ledger|codex-desktop-handoff)\.json$' | grep -q .; then
		report_candidate_drift 'post-source checkpoint includes non-metadata changes.'
	fi
fi

# All built assets are release inputs, never ignored worktree leftovers.
for asset in \
	wordpress-theme/skyyrose-flagship-2/assets/css/design-tokens.min.css \
	wordpress-theme/skyyrose-flagship-2/assets/css/immersive.min.css \
	wordpress-theme/skyyrose-flagship-2/assets/css/mascot.min.css \
	wordpress-theme/skyyrose-flagship-2/assets/css/theme.min.css \
	wordpress-theme/skyyrose-flagship-2/assets/js/house-of-roses-motion.min.js \
	wordpress-theme/skyyrose-flagship-2/assets/js/immersive.min.js \
	wordpress-theme/skyyrose-flagship-2/assets/js/kids-capsule-reveal.min.js \
	wordpress-theme/skyyrose-flagship-2/assets/js/mascot-loader.min.js \
	wordpress-theme/skyyrose-flagship-2/assets/js/mascot.min.js \
	wordpress-theme/skyyrose-flagship-2/assets/js/skyy-3d.min.js \
	wordpress-theme/skyyrose-flagship-2/assets/js/theme.min.js; do
	git ls-files --error-unmatch "$asset" >/dev/null
done

if git status --porcelain -- .fashion-theme wordpress-theme/skyyrose-flagship-2 | grep -q .; then
	report_candidate_drift 'owned V2 paths contain uncommitted changes.'
fi

if [[ "$warning_count" -gt 0 ]]; then
	echo "V2 workspace reconnect passed for active editing with $warning_count warning(s) at $(git rev-parse --short HEAD) (source $integration)."
else
	echo "V2 reconnect guard passed at $(git rev-parse --short HEAD) (source $integration)."
fi
