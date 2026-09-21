# OpenWolf Operating Protocol

You are working in an OpenWolf-managed project. These rules apply every turn.

## File Navigation

1. Check `.wolf/anatomy.md` BEFORE reading any file. It has a 2-3 line
   description and token estimate for every file in the project.
2. If the description in anatomy.md is sufficient for your task, do NOT read the
   full file.
3. If a file is not in anatomy.md, search with Grep/Glob, then update anatomy.md
   with the new entry.

## Code Generation

1. Before generating code, read `.wolf/cerebrum.md` and respect every entry.
2. Check the `## Do-Not-Repeat` section — these are past mistakes that must not
   recur.
3. Follow all conventions in `## Key Learnings` and `## User Preferences`.

## After Actions

1. After every significant action, append a one-line entry to `.wolf/memory.md`:
   `| HH:MM | description | file(s) | outcome | ~tokens |`
2. After creating, deleting, or renaming files: update `.wolf/anatomy.md`.
3. When the action relates to a claim captured by claude-mem (see the digest
   below), append `[cmem #NNN]` to the memory.md row so the two systems
   cross-reference.

## claude-mem Cross-Reference

A SessionStart hook (`.wolf/hooks/claude-mem-sync.sh`) syncs the last 25
claude-mem observations for this project into `.wolf/claude-mem-digest.md`. Read
that file when you need cross-session context that isn't already in
`cerebrum.md`/`anatomy.md`/`memory.md`.

**Wiring** (per-clone, since `.claude/` is gitignored to protect
keys/preferences): add this entry under `hooks.SessionStart[0].hooks` in
`.claude/settings.json`. The script is non-blocking — it no-ops cleanly when the
DB or sqlite3 are missing.

```json
{
  "type": "command",
  "command": "bash /Users/theceo/DevSkyy/.wolf/hooks/claude-mem-sync.sh",
  "timeout": 5
}
```

Verify wiring with:
`bash .wolf/hooks/claude-mem-sync.sh && ls -la .wolf/claude-mem-digest.md`.

**Use the digest to:**

1. **Cite observation IDs** — when logging to `.wolf/memory.md` or adding
   entries to `.wolf/cerebrum.md`, append `[cmem #NNN]` so the OpenWolf record
   links to claude-mem's richer narrative.
2. **Avoid duplicate discovery** — if an answer already exists in the digest (or
   in full via `get_observations([NNN])` / the `mem-search` skill), do not
   re-explore the codebase.
3. **Refresh mid-session** — when you've just landed a significant observation
   and need the digest updated before the next hop, run
   `bash .wolf/hooks/claude-mem-sync.sh`.

**Direction of sync:**

- **claude-mem → OpenWolf**: via this hook at SessionStart (and manual refresh).
- **OpenWolf → claude-mem**: **automatic** — claude-mem ingests session
  transcripts, so any `.wolf/*` edit you make is already observed. No action
  required in this direction.

**Data location:** observations live in `~/.claude-mem/claude-mem.db` (SQLite,
project-scoped on the `project` column; this project = `DevSkyy`).

## Cerebrum Learning (MANDATORY — every session)

OpenWolf's value comes from learning across sessions. You MUST update
`.wolf/cerebrum.md` whenever you learn something useful. This is not optional.

**Update `## User Preferences` when the user:**

- Corrects your approach ("no, do it this way instead")
- Expresses a style preference (naming, structure, formatting)
- Shows a preferred workflow or tool choice
- Rejects a suggestion — record what they preferred instead
- Asks for more/less detail, verbosity, explanation

**Update `## Key Learnings` when you discover:**

- A project convention not obvious from the code (e.g., "tests go in
  `__tests__/` not `test/`")
- A framework-specific pattern this project uses
- An API behavior that surprised you
- A dependency quirk or version constraint
- How modules connect or data flows through the system

**Update `## Do-Not-Repeat` (with date) when:**

- The user corrects a mistake you made
- You try something that fails and find the right approach
- You discover a gotcha that would trip up a fresh session

**Update `## Decision Log` when:**

- A significant architectural or technical choice is made
- The user explains why they chose approach A over B
- A trade-off is explicitly discussed

**The bar is LOW.** If in doubt, add it. A cerebrum entry that's slightly
redundant costs nothing. A missing entry means the next session repeats the same
discovery process.

## Bug Logging (MANDATORY)

**Log a bug to `.wolf/buglog.json` whenever ANY of these happen:**

- The user reports an error, bug, or problem
- A test fails or a command produces an error
- You fix something that was broken
- You edit a file more than twice to get it right
- An import, module, or dependency is missing or wrong
- A runtime error, type error, or syntax error occurs
- A build or lint command fails
- A feature doesn't work as expected
- You change error handling, try/catch blocks, or validation logic
- The user says something "doesn't work", "is broken", or "shows wrong X"

**Before fixing:** call the `wolf-memory` MCP tool `bug_search` (or read
`.wolf/buglog.json` if that server isn't available in this harness) — the fix
may already be known.

**Preferred path — the `wolf-memory` MCP server:** call `bug_log` directly. It
allocates the next `bug-NNN` id and appends the entry atomically across
concurrent sessions on this checkout, and bumps an existing near-duplicate
instead of creating a new entry, per the rule below.
`python scripts/wolf_bug_id.py` remains the CLI fallback where there is no MCP
client; hand-editing `buglog.json` is what caused past cross-session id
collisions — use it only when neither is reachable.

**Ids are provisional on a branch that is behind `main`.** The counter is seeded
from the local `buglog.json`, so it de-races sessions sharing one checkout, not
branches: a branch that predates entries on `main` will hand out ids `main` has
already used. Merge `main`'s buglog before treating an id as final (bug-348/349
were first issued as 339/340 this way).

**After fixing (manual-edit fallback only):** if you can't use `bug_log`, append
to `.wolf/buglog.json` with this structure:

```json
{
  "id": "bug-NNN",
  "timestamp": "ISO date",
  "error_message": "exact error or user complaint",
  "file": "file that was fixed",
  "root_cause": "why it broke",
  "fix": "what you changed to fix it",
  "tags": ["relevant", "keywords"],
  "related_bugs": [],
  "occurrences": 1,
  "last_seen": "ISO date"
}
```

**The threshold is LOW.** When in doubt, log it. A false positive in the bug log
costs nothing. A missed bug means repeating the same mistake later.

**Recurring bugs sync to CLAUDE.md.** If you log a bug that already exists (bump
its `occurrences` + `last_seen` instead of duplicating), or any entry reaches
`occurrences >= 2`, run `python scripts/wolf_recurring_sync.py` — it regenerates
the 1-line recurring-issues digest between the `wolf:recurring` markers in
CLAUDE.md so every future session loads it automatically. (A Stop hook in
`.claude/settings.json` also runs this sync at every turn end as a backstop —
per-clone wiring, like the claude-mem sync hook.)

## Token Discipline

- Never re-read a file already read this session unless it was modified since.
- Prefer anatomy.md descriptions over full file reads when possible.
- Prefer targeted Grep over full file reads when searching for specific code.
- If appending to a file, do not read the entire file first.

## Design QC / Reframe

Moved to skills — `.claude/skills/design-qc/SKILL.md` and
`.claude/skills/reframe/SKILL.md` (auto-trigger on matching requests; no need to
hold their workflows resident here).

## Session End

Before ending or when asked to wrap up:

1. Write a session summary to `.wolf/memory.md`.
2. Review the session: did you learn anything? Did the user correct you? Did you
   fix a bug? If yes, update `.wolf/cerebrum.md` and/or `.wolf/buglog.json`.
