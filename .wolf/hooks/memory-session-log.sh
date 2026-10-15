#!/usr/bin/env bash
# .wolf/hooks/memory-session-log.sh
#
# Appends one row to .wolf/memory.md when a Claude Code session opens
# (SessionStart: startup / resume / clear) and when it closes (SessionEnd).
# .wolf/memory.md is the git-tracked cross-LLM coordination log (founder,
# 2026-09-08): every session must leave a trace there so parallel agents
# (Claude / Codex / Ralph) can see each other's work and avoid overlapping it.
#
# Wired in .claude/settings.json under hooks.SessionStart and hooks.SessionEnd:
#   { "type": "command",
#     "command": "bash /Users/theceo/DevSkyy/.wolf/hooks/memory-session-log.sh",
#     "timeout": 5 }
#
# Reads the hook JSON from stdin. Never blocks the session: every failure path
# exits 0 after a line on stderr. Override paths for tests with
# SKYYROSE_REPO_ROOT and WOLF_MEMORY_FILE.

set -uo pipefail

REPO_ROOT="${SKYYROSE_REPO_ROOT:-/Users/theceo/DevSkyy}"
MEMORY_FILE="${WOLF_MEMORY_FILE:-${REPO_ROOT}/.wolf/memory.md}"

if ! command -v jq > /dev/null 2>&1; then
  echo "[wolf-memory] jq not found; skipping session log" >&2
  exit 0
fi

INPUT="$(cat 2> /dev/null || true)"
EVENT="$(printf '%s' "$INPUT" | jq -r '.hook_event_name // empty' 2> /dev/null)"
SID="$(printf '%s' "$INPUT" | jq -r '.session_id // empty' 2> /dev/null)"
SOURCE="$(printf '%s' "$INPUT" | jq -r '.source // empty' 2> /dev/null)"
REASON="$(printf '%s' "$INPUT" | jq -r '.reason // empty' 2> /dev/null)"
SID_SHORT="${SID:0:8}"
[[ -z "$SID_SHORT" ]] && SID_SHORT="unknown"

case "$EVENT" in
  SessionStart)
    # compact is not a new session; startup / resume / clear / fork are.
    [[ "$SOURCE" == "compact" ]] && exit 0
    PHASE="session start (${SOURCE:-startup})"
    OUTCOME="open"
    ;;
  SessionEnd)
    PHASE="session end (${REASON:-exit})"
    OUTCOME="closed"
    ;;
  *)
    echo "[wolf-memory] unsupported hook event '${EVENT}'; skipping" >&2
    exit 0
    ;;
esac

if [[ ! -f "$MEMORY_FILE" ]]; then
  echo "[wolf-memory] $MEMORY_FILE not found; skipping" >&2
  exit 0
fi

# Keep the live log small: archive older rows once it passes the threshold
# (scripts/wolf_memory_rotate.py; no-op under 128KB, never loses a byte).
if [[ "$EVENT" == "SessionStart" && -z "${WOLF_MEMORY_FILE:-}" ]]; then
  python3 "${REPO_ROOT}/scripts/wolf_memory_rotate.py" --quiet --file "$MEMORY_FILE" >&2 \
    || echo "[wolf-memory] rotation failed; log left as-is" >&2
fi

BRANCH="$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2> /dev/null || echo '?')"
SHA="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2> /dev/null || echo '?')"
DIRTY_LIST="$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no 2> /dev/null | awk '{print $NF}')"
DIRTY_COUNT=0
[[ -n "$DIRTY_LIST" ]] && DIRTY_COUNT="$(printf '%s\n' "$DIRTY_LIST" | wc -l | tr -d ' ')"
DIRTY_HEAD="$(printf '%s\n' "$DIRTY_LIST" | head -5 | paste -sd ' ' -)"
[[ "$DIRTY_COUNT" -gt 5 ]] && DIRTY_HEAD="${DIRTY_HEAD} (+$((DIRTY_COUNT - 5)) more)"
[[ -z "$DIRTY_HEAD" ]] && DIRTY_HEAD="—"

STAMP="$(date +%H:%M)"
DESC="${PHASE} — ${SID_SHORT} on ${BRANCH} @${SHA} · uncommitted: ${DIRTY_COUNT}"
# Table cells must not contain pipes.
DESC="${DESC//|/¦}"
DIRTY_HEAD="${DIRTY_HEAD//|/¦}"

printf '| %s | %s | %s | %s | — |\n' "$STAMP" "$DESC" "$DIRTY_HEAD" "$OUTCOME" >> "$MEMORY_FILE" \
  || {
    echo "[wolf-memory] append to $MEMORY_FILE failed" >&2
    exit 0
  }

if [[ "$EVENT" == "SessionStart" ]]; then
  echo "[wolf-memory] session ${SID_SHORT} logged to .wolf/memory.md — append a row after every significant action and include the file in your commit."
fi
exit 0
