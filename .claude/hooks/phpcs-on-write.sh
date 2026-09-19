#!/usr/bin/env bash
# PostToolUse hook — runs PHPCS on a single PHP file immediately after
# Edit/Write/MultiEdit with THAT THEME's own standard. Non-blocking warning
# (exit 2 surfaces findings to Claude but does not undo the write).
#
# Catches violations at write time so debt does not compound between deploys.
# Memory log shows: 156 errors → 0 across 3 sessions, phpcbf run 6+ times.
# Per-file scan at write time prevents that cycle.
#
# Two themes live in wordpress-theme/: skyyrose-flagship ("SkyyRose", text
# domain `skyyrose`) and skyyrose-flagship-2 ("SkyyRose Flagship 2", text
# domain `skyyrose-flagship-2`). Each carries its own ruleset (flagship:
# `.phpcs.xml`, flagship-2: `phpcs.xml`); applying one theme's ruleset to the
# other flags every i18n call as a TextDomainMismatch. A theme with no ruleset
# gets a one-line notice, never a borrowed standard.
#
# Skip rules:
#   - Path must end in .php and exist
#   - Path must be under wordpress-theme/<theme>/ inside a checkout of THIS
#     repo — the main checkout or any worktree of it, resolved from the file
#   - Path must NOT be under vendor/, tests/, node_modules/, or assets/js/lib/
#   - Theme ruleset = first of .phpcs.xml, phpcs.xml, .phpcs.xml.dist,
#     phpcs.xml.dist in wordpress-theme/<theme>/ (PHPCS lookup order)
#
# Bypass: export PHPCS_ON_WRITE_DISABLE=1

set -euo pipefail

if [[ "${PHPCS_ON_WRITE_DISABLE:-0}" == "1" ]]; then
    exit 0
fi

# Fail-open on missing jq — this is a style linter, not a safety gate.
# Blocking writes because a lint helper can't parse the payload would punish
# users for a missing dev tool. paid-api-stopgate.sh fails closed because
# money is at stake; PHPCS findings are not money.
if ! command -v jq >/dev/null 2>&1; then
    echo "[phpcs-on-write] jq missing from PATH — skipping (warning, not blocking)." >&2
    exit 0
fi

payload=$(cat)
file_path=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // ""')

# Skip if no file path in payload
[[ -z "$file_path" ]] && exit 0

# Skip if not PHP
[[ "$file_path" == *.php ]] || exit 0

# File must exist on disk (Write may have just created it, Edit modified it)
[[ -f "$file_path" ]] || exit 0

# Theme = the wordpress-theme/<name>/ segment of the edited path.
[[ "$file_path" =~ ^(.*/wordpress-theme)/([^/]+)/ ]] || exit 0
THEMES_DIR="${BASH_REMATCH[1]}"
THEME_NAME="${BASH_REMATCH[2]}"
THEME_DIR="$THEMES_DIR/$THEME_NAME"

# Only checkouts of THIS repo: the file's git common dir must equal the hook's
# (main checkout and every worktree of it share one common dir).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_COMMON="$(git -C "$SCRIPT_DIR" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || exit 0
FILE_COMMON="$(git -C "$THEME_DIR" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || exit 0
[[ "$FILE_COMMON" == "$HOOK_COMMON" ]] || exit 0

# Skip excluded subdirectories (mirrors .phpcs.xml exclude-pattern exactly).
# tests/* must be skipped wholesale — phpcs honors exclude-pattern only
# when sniffing directories, not when given an explicit file path.
case "$file_path" in
    "$THEME_DIR"/vendor/*)        exit 0 ;;
    "$THEME_DIR"/node_modules/*)  exit 0 ;;
    "$THEME_DIR"/tests/*)         exit 0 ;;
    "$THEME_DIR"/assets/js/lib/*) exit 0 ;;
esac

# The standard is always the edited theme's own ruleset, found in PHPCS's own
# lookup order: .phpcs.xml → phpcs.xml → .phpcs.xml.dist → phpcs.xml.dist
# (skyyrose-flagship ships .phpcs.xml; skyyrose-flagship-2 ships phpcs.xml).
STANDARD=""
for candidate in .phpcs.xml phpcs.xml .phpcs.xml.dist phpcs.xml.dist; do
    if [[ -f "$THEME_DIR/$candidate" ]]; then
        STANDARD="$THEME_DIR/$candidate"
        break
    fi
done
if [[ -z "$STANDARD" ]]; then
    echo "[phpcs-on-write] $THEME_NAME has no ruleset (.phpcs.xml / phpcs.xml / .phpcs.xml.dist / phpcs.xml.dist) — not applying another theme's standard; skipped $(basename "$file_path")." >&2
    exit 0
fi

# PHPCS binary: the theme's own vendor/, else a sibling theme's. The binary is
# shared tooling (WPCS installed); the RULESET above is never borrowed.
PHPCS_BIN="$THEME_DIR/vendor/bin/phpcs"
if [[ ! -x "$PHPCS_BIN" ]]; then
    for candidate in "$THEMES_DIR"/*/vendor/bin/phpcs; do
        if [[ -x "$candidate" ]]; then
            PHPCS_BIN="$candidate"
            break
        fi
    done
fi
if [[ ! -x "$PHPCS_BIN" ]]; then
    echo "[phpcs-on-write] no vendor/bin/phpcs under $THEMES_DIR — run: cd $THEME_DIR && composer install" >&2
    exit 0
fi
PHPCBF_BIN="${PHPCS_BIN%phpcs}phpcbf"

# Run phpcs with the theme root as cwd so the ruleset's relative paths resolve.
cd "$THEME_DIR"
result=$("$PHPCS_BIN" --standard="$STANDARD" -s --report=full "$file_path" 2>&1) || rc=$?
rc=${rc:-0}

# PHPCS exit codes: 0=clean, 1=errors found, 2=warnings only, 3=errors+warnings.
# Any non-zero means findings worth surfacing.
if [[ "$rc" -eq 0 ]]; then
    exit 0
fi

# Surface findings to Claude via stderr (exit 2 = warning visible, non-blocking).
# `|| true` on head prevents SIGPIPE from killing the hook under set -o pipefail
# when phpcs output is shorter than the head limit.
echo "[phpcs-on-write] PHPCS findings in $(basename "$file_path") ($THEME_NAME standard: $STANDARD):" >&2
echo "" >&2
echo "$result" | head -50 >&2 || true
echo "" >&2
echo "[phpcs-on-write] Fix with: cd $THEME_DIR && $PHPCBF_BIN --standard=$STANDARD '$file_path'" >&2
exit 2
