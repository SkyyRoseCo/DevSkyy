#!/usr/bin/env bash
# Stop test-gate (WORKTREE-AWARE) — runs the fast pytest suite for the STOPPING
# session's OWN worktree, not a hardcoded path.
#
# Why worktree-aware: one git worktree = one HEAD, but multiple Claude sessions can
# run concurrently in DIFFERENT worktrees of the same repo (e.g. a Ralph loop churning
# `main` while another session works in .claude/worktrees/<x>). A path-hardcoded gate
# blocks EVERY session on main's state, so one session's broken WIP false-blocks another
# session's clean Stop. This gate reads the stopping session's cwd (Claude Code passes
# it as JSON on stdin: {"cwd": "...", ...}) and gates only the tree that session is in.
#
# Flake handling: on a red run, settle 5s then re-run `pytest --last-failed`; block
# (exit 2) ONLY if the failure reproduces — absorbs load-timeout flakes and mid-edit
# races without ever masking a real, reproducible failure.
set -uo pipefail

# bug-263: on macOS, Apple's _scproxy SIGSEGVs on the child side of subprocess
# fork() (nw_settings_child_has_forked) unless proxy resolution is short-circuited.
# conftest.py setdefault's no_proxy too late — networking can arm before conftest
# imports — so export it HERE, before Python starts, which is the reliable fix.
# Harmless off darwin (just an unused env var). Without this the gate false-blocks
# on ~100 subprocess-spawning tests that crash with exit -11.
export NO_PROXY='*' no_proxy='*'

# The stopping session's cwd arrives as JSON on stdin. Fall back to $PWD if absent
# (jq missing / non-JSON invocation) so the gate still works.
input=$(cat 2>/dev/null || true)
cwd=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null || true)
[ -n "$cwd" ] && [ -d "$cwd" ] || cwd="$PWD"

# Resolve THAT worktree's git root; if it isn't a repo, don't block the Stop.
REPO=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO" || exit 0

# Gate only when Python actually changed in THIS worktree. No Python change means
# there is nothing to verify, so this is the one legitimately silent exit 0.
git status --porcelain -- '*.py' | grep -q . || exit 0

# Worktrees have no venv of their own — they share the primary checkout's .venv
# (first entry of `git worktree list`). No interpreter = tests NOT verified:
# fail CLOSED (bug-230), never a silent pass.
PY="$REPO/.venv/bin/python"
if [ ! -x "$PY" ]; then
  MAIN_WT=$(git -C "$REPO" worktree list --porcelain 2>/dev/null | sed -n '1s/^worktree //p')
  PY="${MAIN_WT:-/nonexistent}/.venv/bin/python"
fi
if [ ! -x "$PY" ]; then
  echo "Stop-gate: no python interpreter — tests NOT verified (looked for $REPO/.venv/bin/python and the primary worktree's .venv/bin/python). Blocking Stop (worktree: $REPO)." >&2
  exit 2
fi

# Half-written NEW test files (untracked) are not a gate — ignore them.
ig=$(git ls-files --others --exclude-standard "tests/*.py" "tests/**/*.py" 2>/dev/null \
     | sed "s/^/--ignore=/" | tr "\n" " ")

run_full()       { $PY -m pytest tests/ -x -q $ig 2>&1; }
run_lastfailed() { $PY -m pytest --last-failed -q $ig 2>&1; }

out=$(run_full); rc=$?
[ "$rc" -eq 0 ] && exit 0   # green on the first try

# First run failed. Settle (load drains / the other session's edit completes), then
# re-run only what failed. --last-failed uses the cache from the run above; empty cache
# falls back to the full suite (still safe).
sleep 5
out2=$(run_lastfailed); rc2=$?
if [ "$rc2" -eq 0 ]; then
  echo "Stop-gate: failure cleared on clean re-run (transient flake / mid-edit race) — not blocking."
  exit 0
fi

echo "$out2" | tail -25 >&2
echo "Stop-gate: failure reproduced on re-run — blocking Stop (worktree: $REPO)." >&2
exit 2
