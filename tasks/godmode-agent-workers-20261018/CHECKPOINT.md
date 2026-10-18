# GOD MODE worker integration checkpoint — 2026-10-18

Owner selected Claude Opus 5.5 main worker and Codex GPT-6.1 Sol independent
machine reviewer. GOD MODE retains approval, durable memory and release authority.

Implemented: authenticated dashboard execution and project memory; three fixed
local verifier workflows; two additional immutable-source-packet analysis
workflows; isolated Claude Agent SDK and Codex exec CLI adapters; no-tools policy;
exact model/source/schema/auth bindings; complete canonical preorder coverage;
transactional two-run daily qualification reservation; independent watchdog;
separate machine and human review; no automatic retry or memory promotion.

Checkpoint qualification: offline behavior and source verification only.
Live provider and integrated browser qualification are pending at this checkpoint.
Production, media generation, publishing and deployment remain disabled.

Existing backend25 tests pass; adapter20 and workflow8 tests cover restrictions,
parent SIGKILL cleanup, coverage, approval/model drift, review binding and retained
reservation exhaustion. UI11 tests/type/lint pass; final production build receipt
will be recorded separately. Existing dependency audit release limitations remain.

Runtime uses explicit workstation profile and durable SQLite, not a cloud queue.
Canonical Fashion/GODMODE plugin sources remain external package dependencies.
Install requirements-godmode.txt into the repository environment. Local launcher:
`.venv/bin/python scripts/run_god_mode.py`. Existing backend sign-in is required
for the dashboard. Never commit local environment files, auth documents or DBs.
