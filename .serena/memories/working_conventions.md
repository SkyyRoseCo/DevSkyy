# Working conventions (stable subset; canonical text is CLAUDE.md §1–§3)

- Money / production / irreversible actions -> show the exact manifest and wait for `y`.
  One manifest, one `y`, one call. Approval never carries over.
- Tag load-bearing claims `[live] [repo] [repro] [test] [docs] [inferred]`; severity
  needs `[live]`. Never report "done" without check output from the same session.
- Shared checkout `/Users/theceo/DevSkyy` is dirty and holds other agents' work: never
  `--amend` / `reset` / `rebase` / bare `git stash` there; check `git branch --show-current`
  before every commit; use `git worktree add` for real isolation.
- Tests: `rtk proxy pytest ...`; never `-o addopts=""`.
- Commit with the global git identity (repo-local identity once leaked "Offline Fixture").
- `main` requires a PR and 8 status checks; any failing check blocks, and never `--admin`.
- Append one handoff row to the MAIN checkout's `.wolf/memory.md` per session;
  `.husky/pre-push` needs a row with `@ <branch>` dated today or yesterday.
- Use Context7 before non-stdlib code; use Serena symbolic tools before reading whole
  files. `activate_project` rewrites `.serena/project.yml` — do not commit that change.
