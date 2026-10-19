#!/usr/bin/env bash
# PostToolUse hook — precision cleanup of ONE Python file after Edit/Write/MultiEdit.
#
# Replaces python-format-on-write.sh, which ran isort -> ruff --fix -> black over the WHOLE
# file and so rewrote lines the edit never touched. This tidies only what the edit touched
# or orphaned (see scripts/precision_cleanup.py for the contract). Non-blocking: always
# exits 0, never undoes the write.
#
# The repo root comes from this script's own location, so it works from any clone or worktree.
#
# Bypass: export PRECISION_CLEANUP_DISABLE=1

[[ "${PRECISION_CLEANUP_DISABLE:-0}" == "1" ]] && exit 0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 0
TARGET="$SCRIPT_DIR/../../scripts/precision_cleanup.py"
[[ -f "$TARGET" ]] || exit 0

# A formatter is not a gate: with no interpreter there is nothing to do, and that is fine.
PYTHON="$(command -v python3 || true)"
[[ -n "$PYTHON" ]] || exit 0

exec "$PYTHON" "$TARGET"
