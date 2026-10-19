#!/usr/bin/env bash
# .wolf/hooks/handoff-gate.sh — enforces the session handoff log rule
# (CLAUDE.md / AGENTS.md "Session handoff log").
#
# Every agent that changes the repo must leave a row in the MAIN checkout's
# .wolf/memory.md so parallel agents (Claude Code, Codex, Ralph loops) can see
# where each other left off. One script serves both harnesses — Claude Code and
# Codex share the hook protocol (JSON on stdin, same output fields):
#
#   PostToolUse       file edit / mutating shell command → record a per-session
#                     "unlogged" marker (latest-row fingerprint, memory path,
#                     worktree). Logging-only writes are exempt.
#   Stop              unlogged → FIRST time this session: block once with a
#                     pre-filled row ({"decision":"block"}). Every later time:
#                     non-blocking reminder to the user ({"systemMessage"}).
#   UserPromptSubmit  still unlogged → remind the MODEL via additionalContext.
#
# "Logged" means the session's newest `sid:<id8>` row differs from the one seen
# when the marker was written — a fingerprint, not a count, so rotating old rows
# into .wolf/memory-archive/ (scripts/wolf_memory_rotate.py) can't confuse it.
# The automatic start/end rows from memory-session-log.sh carry no `sid:` tag,
# so they never satisfy the gate.
#
# The repo is resolved from the EDITED PATH (or `cd`/`-C` targets of a shell
# command), so a session whose shell wandered out of the repo is still gated;
# Stop reads everything from the marker and ignores its own cwd.
#
# Fails open only on missing infrastructure (no jq / session id / memory file)
# and never blocks twice in a session, so it cannot trap an agent.
# Test overrides: WOLF_MEMORY_FILE, WOLF_HANDOFF_STATE_DIR, WOLF_HANDOFF_NOW.

set -uo pipefail

AGENT="agent"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      AGENT="${2:-agent}"
      shift 2
      ;;
    *) shift ;;
  esac
done

command -v jq > /dev/null 2>&1 || exit 0

INPUT="$(cat 2> /dev/null || true)"
# One jq pass for every field the hook reads. Fields are joined with the ASCII
# unit separator: unlike tab it is not IFS whitespace, so empty fields survive.
# PATCH_FILE = first non-log file a Codex apply_patch touches.
IFS=$'\x1f' read -r EVENT SID CWD TOOL FP CMD PATCH_FILE ACTIVE < <(
  printf '%s' "$INPUT" | jq -r '[
      .hook_event_name, .session_id, .cwd, .tool_name,
      (.tool_input.file_path // .tool_input.notebook_path),
      ((.tool_input.command // .tool_input.cmd)
         | if type == "array" then join(" ") else . end),
      (if .tool_name == "apply_patch" and (.tool_input.command | type) == "string" then
         [.tool_input.command | scan("(?m)^\\*\\*\\* (?:Add|Update|Delete) File: (.+)$")[0]]
         | map(select(endswith(".wolf/memory.md") | not)) | .[0]
       else null end),
      .stop_hook_active
    ] | map(. // "" | tostring | gsub("[\n\u001f]"; " ; ")) | join("\u001f")' 2> /dev/null
) || exit 0
[[ -n "${SID:-}" ]] || exit 0
[[ -n "${CWD:-}" && -d "$CWD" ]] || CWD="$PWD"
SID8="${SID:0:8}"

STATE_DIR="${WOLF_HANDOFF_STATE_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/wolf-handoff}"
MARKER="$STATE_DIR/$SID.dirty"
NUDGED="$STATE_DIR/$SID.nudged"

# Fingerprint of this session's newest log row ("none" when it has none).
last_row_fp() {
  local row
  row="$(grep -F "sid:$SID8" "$1" 2> /dev/null | tail -1)"
  [[ -n "$row" ]] && printf '%s' "$row" | cksum | awk '{print $1}' || echo none
}

# Sets WT (worktree root) and MAIN (first `git worktree list` entry — the one
# memory.md every agent can see) for a path, walking up to an existing dir.
resolve_repo() {
  local d="$1"
  while [[ ! -d "$d" && "$d" != "/" ]]; do d="$(dirname "$d")"; done
  WT="$(git -C "$d" rev-parse --show-toplevel 2> /dev/null)" || return 1
  MAIN="$(git -C "$d" worktree list --porcelain 2> /dev/null | awk '/^worktree /{print substr($0, 10); exit}')"
  [[ -n "$MAIN" ]]
}

# Shell commands that change repo state; read-only ones never need a row.
is_mutating_shell() {
  local c
  c="$(printf '%s' "$1" | sed -E 's/[0-9]*>&[0-9]+//g; s#[0-9]*>[[:space:]]*/dev/null##g')"
  printf '%s' "$c" | grep -Eq \
    '(^|[;&|(`"'"'"'[:space:]])(git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?(commit|push|merge|rebase|reset|checkout|switch|cherry-pick|revert|am|apply|rm|mv|tag|stash)|rm|mv|cp|mkdir|ln|touch|tee|truncate|sed[[:space:]]+-i|perl[[:space:]]+-p?i|npm[[:space:]]+(run|install|i|ci|publish)|pnpm|yarn|pip[[:space:]]+install|uv[[:space:]]+(add|pip)|make|gh[[:space:]]+(pr|issue|release|api)|vercel|fly|docker[[:space:]]+(compose[[:space:]]+)?(up|build|push|run))([[:space:]]|$)|>'
}

# Record the first unlogged change (keeps the earliest fingerprint).
mark_dirty() {
  local memory="${WOLF_MEMORY_FILE:-$MAIN/.wolf/memory.md}"
  [[ -f "$memory" && ! -f "$MARKER" ]] || return 0
  mkdir -p "$STATE_DIR" 2> /dev/null || return 0
  printf '%s\n%s\n%s\n' "$(last_row_fp "$memory")" "$memory" "$WT" > "$MARKER"
}

# Loads the marker; returns 0 while the session is still unlogged, else clears it.
still_unlogged() {
  [[ -f "$MARKER" ]] || return 1
  {
    read -r FP0
    read -r MEMORY
    read -r WT
  } < "$MARKER"
  [[ -f "${MEMORY:-}" ]] || {
    rm -f "$MARKER"
    return 1
  }
  # Logged = a sid row exists AND it is newer than the one seen at mark time.
  # ("none" after a rotation archived the old row is NOT a new row.)
  local now
  now="$(last_row_fp "$MEMORY")"
  if [[ "$now" != none && "$now" != "$FP0" ]]; then
    rm -f "$MARKER"
    return 1
  fi
}

suggested_row() {
  local branch
  # symbolic-ref names unborn branches too; detached HEAD falls back to the sha.
  branch="$(git -C "${WT:-$CWD}" symbolic-ref --short -q HEAD 2> /dev/null \
    || { s="$(git -C "${WT:-$CWD}" rev-parse --short HEAD 2> /dev/null)" && echo "detached@$s"; } \
    || echo '?')"
  printf '| %s | %s @ %s sid:%s | <what you did> | <files / PRs> | <done · in-progress · blocked> + <next step> | ~<tokens> |' \
    "${WOLF_HANDOFF_NOW:-$(date '+%Y-%m-%d %H:%M')}" "$AGENT" "$branch" "$SID8"
}

case "$EVENT" in
  PostToolUse)
    case "$TOOL" in
      Edit | Write | MultiEdit | NotebookEdit)
        [[ -n "$FP" && "$FP" != *".wolf/memory.md" ]] || exit 0
        [[ "$FP" == /* ]] || FP="$CWD/$FP"
        resolve_repo "$FP" && mark_dirty
        ;;
      apply_patch)
        # Codex: logging-only patches leave PATCH_FILE empty and are exempt.
        [[ -n "$PATCH_FILE" ]] || exit 0
        [[ "$PATCH_FILE" == /* ]] || PATCH_FILE="$CWD/$PATCH_FILE"
        resolve_repo "$PATCH_FILE" && mark_dirty
        ;;
      Bash)
        [[ -n "$CMD" && "$CMD" != *".wolf/memory.md"* ]] || exit 0
        is_mutating_shell "$CMD" || exit 0
        # Where did it run? cwd first, then any absolute `cd X` / `-C X` target.
        for D in "$CWD" $(printf '%s' "$CMD" | grep -oE '(cd|-C)[[:space:]]+/[^[:space:];&|]+' | awk '{print $2}'); do
          if resolve_repo "$D"; then
            mark_dirty
            break
          fi
        done
        ;;
    esac
    ;;

  Stop)
    still_unlogged || exit 0
    [[ "$ACTIVE" == "true" ]] && exit 0
    ROW="$(suggested_row)"
    if [[ ! -f "$NUDGED" ]]; then
      touch "$NUDGED" 2> /dev/null
      jq -n --arg r "Session handoff log required (CLAUDE.md / AGENTS.md). You changed the repo and have not logged it. Append ONE row to $MEMORY (the main checkout's copy, not a worktree's), keeping the sid tag exactly:
$ROW
Append only — never edit other agents' rows. This is the only block this session; later turns get reminders." \
        '{decision: "block", reason: $r}'
    else
      jq -n --arg m "Handoff log: unlogged repo changes this session — append a sid:$SID8 row to $MEMORY before you leave." \
        '{systemMessage: $m}'
    fi
    # Housekeeping: drop markers from sessions idle for a week.
    find "$STATE_DIR" -type f -mtime +7 -delete 2> /dev/null
    ;;

  UserPromptSubmit)
    still_unlogged || exit 0
    jq -n --arg c "Reminder (handoff-gate): you have unlogged repo changes from an earlier turn. Before ending this turn, append a row to $MEMORY:
$(suggested_row)" \
      '{hookSpecificOutput: {hookEventName: "UserPromptSubmit", additionalContext: $c}}'
    ;;
esac

exit 0
