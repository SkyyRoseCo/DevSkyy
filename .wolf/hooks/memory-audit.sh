#!/usr/bin/env bash
# .wolf/hooks/memory-audit.sh
#
# Thin wrapper around memory-audit.py. Callable directly (manual run) or wired
# into Claude Code SessionStart hooks via ~/.claude/settings.json:
#
#   {
#     "type": "command",
#     "command": "bash \"$CLAUDE_PROJECT_DIR/.wolf/hooks/memory-audit.sh\"",
#     "timeout": 5
#   }
#
# Exits 0 on success (including when decay is detected — decay is informational,
# not a failure). Exits non-zero if the audit script is missing or crashes.
#
# Repo root: SKYYROSE_REPO_ROOT, else CLAUDE_PROJECT_DIR, else this script's
# own checkout (two levels up), so it works on any machine and in worktrees.

set -euo pipefail

REPO_ROOT="${SKYYROSE_REPO_ROOT:-${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}}"
AUDIT_PY="${REPO_ROOT}/.wolf/hooks/memory-audit.py"

if [[ ! -f "$AUDIT_PY" ]]; then
  # Surface it as a (non-blocking) hook error rather than a silent no-op.
  echo "[memory-audit] $AUDIT_PY not found" >&2
  exit 1
fi

exec python3 "$AUDIT_PY" "$@"
