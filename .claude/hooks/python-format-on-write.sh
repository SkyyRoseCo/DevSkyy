#!/usr/bin/env bash
# PostToolUse hook — formats a single Python file immediately after
# Edit/Write/MultiEdit with the project's canonical chain (isort -> ruff
# check --fix -> black, matching `make format`), then surfaces any remaining
# unfixable lint. Non-blocking: it formats in place and never undoes the write.
#
# The Python sibling of phpcs-on-write.sh — PHP already auto-formats on write;
# this closes the asymmetry so .py debt does not compound between commits.
#
# Skip rules:
#   - Path must end in .py and exist
#   - Path must be inside a checkout of THIS repo — the main checkout or any
#     worktree of it (.claude/worktrees/*, ~/.codex/worktrees/*): the edited
#     file's `git rev-parse --git-common-dir` must equal the hook's own
#   - Path must NOT be under .venv*/, node_modules/, build/, dist/, .next/
#
# Tools run with cwd = the edited file's checkout so that tree's pyproject.toml
# governs. (2026-09-18: worktree edits were skipped outright, so PR branches
# landed unformatted and CI lint went red.)
#
# Bypass: export PY_FORMAT_ON_WRITE_DISABLE=1

set -euo pipefail

if [[ "${PY_FORMAT_ON_WRITE_DISABLE:-0}" == "1" ]]; then
    exit 0
fi

# Fail-open on missing jq — this is a formatter, not a safety gate.
if ! command -v jq >/dev/null 2>&1; then
    echo "[py-format-on-write] jq missing from PATH — skipping (warning, not blocking)." >&2
    exit 0
fi

file_path=$(cat | jq -r '.tool_input.file_path // ""')

[[ -z "$file_path" ]] && exit 0
[[ "$file_path" == *.py ]] || exit 0
[[ -f "$file_path" ]] || exit 0

case "$file_path" in
    */.venv*/* | */node_modules/* | */build/* | */dist/* | */.next/*) exit 0 ;;
esac

# The hook's own repo (the checkout it is wired from) and the edited file's.
# Same git common dir = same repo, whichever worktree the file lives in.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || exit 0
HOOK_COMMON="$(git -C "$SCRIPT_DIR" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || exit 0
FILE_DIR="$(dirname "$file_path")"
FILE_ROOT="$(git -C "$FILE_DIR" rev-parse --show-toplevel 2>/dev/null)" || exit 0
FILE_COMMON="$(git -C "$FILE_DIR" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || exit 0
[[ "$FILE_COMMON" == "$HOOK_COMMON" ]] || exit 0

# Resolve each tool from the file's checkout venv, then the hook's checkout
# venv (worktrees have no venv of their own), then PATH; no-op if absent.
run_tool() {
    local bin="$1"
    shift
    if [[ -x "$FILE_ROOT/.venv/bin/$bin" ]]; then
        "$FILE_ROOT/.venv/bin/$bin" "$@"
    elif [[ -x "$HOOK_ROOT/.venv/bin/$bin" ]]; then
        "$HOOK_ROOT/.venv/bin/$bin" "$@"
    elif command -v "$bin" >/dev/null 2>&1; then
        "$bin" "$@"
    fi
}

cd "$FILE_ROOT"

# Canonical format chain (mirrors `make format`), scoped to one file, best-effort.
run_tool isort "$file_path" >/dev/null 2>&1 || true
run_tool ruff check --fix --quiet "$file_path" >/dev/null 2>&1 || true
run_tool black --quiet "$file_path" >/dev/null 2>&1 || true

# Surface remaining (unfixable) lint as a non-blocking warning (exit 2 = visible).
lint=$(run_tool ruff check --quiet "$file_path" 2>&1) || true
if [[ -n "$lint" ]]; then
    echo "[py-format-on-write] formatted $(basename "$file_path"); remaining lint:" >&2
    echo "" >&2
    echo "$lint" | head -30 >&2 || true
    exit 2
fi

exit 0
