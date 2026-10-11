# TEST.md — cli-anything-skyyrose-flagship-2

## Part 1 — Test plan

### Inventory

| File               | Kind                                                                                              | Planned                                                                                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_core.py`     | Unit: synthetic git repos in `tmp_path`, no network, no real theme                                | 27 planned → 64 written (incl. parametrized; 9 added from the independent review, 8 in-process CLI command tests added for coverage, 11 in `TestP3Followups`) |
| `test_full_e2e.py` | E2E: the real flagship-2 theme scripts + God Mode X's real checker + installed CLI via subprocess | 10 planned → 10 written (incl. parametrized)                                                                                                                  |

### Unit plan (`test_core.py`)

- `core/gates.py` (7): every package.json script lands in exactly one class;
  unknown scripts are `unclassified` and refused; `render:*`, `certify:*`,
  `workflow:*`, `author:*` and the image-judge scripts are `blocked`; asking to
  run a build gate as a check is refused; a missing script is refused.
- `core/version.py` (6): reads the triple; detects disagreement; refuses a
  non-X.Y.Z version and a no-op bump; `plan_bump` writes nothing;
  `write_version` updates all three and reads back; a failed write restores
  already-written files.
- `core/candidate.py` (5): a clean tree's revision is HEAD; an edit makes the
  tree dirty and changes the candidate id; a second edit to an already-dirty
  file changes the id again; a commit changes the id; `pin_status` reports drift
  when the registry bytes change.
- `core/session.py` (4): new → save → load round trip; schema mismatch is
  rejected; `open_or_create` resumes only for the same repo; logs are written
  per run.
- `core/evidence.py` (5): a review by the gate owner is rejected (builder cannot
  self-review); runs on another candidate are excluded and counted; a dirty
  candidate gives `claim: partial` and FTT `BLOCKED`; a failed gate gives
  `claim: blocked` and FTT `FAIL`; a log edited after the run is refused.

### E2E plan (`test_full_e2e.py`)

Runs against the real checkout that contains this harness. Requires the pinned
toolchain (`SKYYROSE2_NODE_BIN_DIR` → Node 22.23.2, Python 3.12.12, php),
`node_modules` in the theme, and a God Mode X clone (`GOD_MODE_X_ROOT`).
**Opt-in:** set `SKYYROSE2_E2E=1`. Workflow 3 edits a tracked file, so use a
dedicated worktree. Once opted in, tests **fail, not skip**, when any
requirement is missing.

Workflows:

1. **Gate run → evidence → God Mode X** — run `check:registry`, `check:i18n`,
   `check:tokens`, `check:source-integrity` through the installed CLI; export;
   verify God Mode X's `check_completion.py` returns `PASS`, the record's
   artifact hashes match the copied logs, and the tracked tree is unchanged.
2. **Fashion Theme Team review** — owner review is refused; an independent
   review flips FTT from `BLOCKED` to `PASS` for the same candidate.
3. **Stale-candidate binding** — after a tracked edit, export refuses (no runs
   for the new candidate); rerunning a gate on the dirty tree exports
   `claim: partial`, which God Mode X rejects. The edit is reverted in
   `finally`.
4. **Refusals** — a blocked script and an unclassified name exit non-zero
   without running anything.
5. **Introspection** — `--help`, `doctor --json`, `info --json`,
   `version check --json`, `pin status --json`, `scripts list --json` (every
   package.json script classified).

## P3 follow-ups (2026-10-11)

The independent review left three open P3 findings. Each is now fixed, with
tests in `TestP3Followups`:

- **P3a — the gate owner is self-asserted.** Every run entry and log header
  records `owner_source` (`env` or `git`), and the record lists them in
  `fashion_theme_team.owner_sources`. When an included run's owner came from
  env, the record gets an OPEN P3 finding, "gate owner supplied via
  SKYYROSE2_GATE_OWNER is unverified". It does not block. If someone edits the
  source in `session.json`, it no longer matches the log, and the export
  refuses.
- **P3b — `session new` dropped an earlier FAIL review.** The FTT verdict now
  reads reviews from every session in the CLI home that match the same candidate
  and `harness_sha256` (`session.other_sessions`). Each reviewer's latest review
  stands. Any independent FAIL makes the verdict FAIL. PASS needs at least one
  independent PASS. A gate runner in another session also counts as an owner. A
  corrupt session file raises an error instead of being skipped.
- **P3c — `node_modules` was not part of the identity.** The environment label
  now ends with `;deps=<12 hex>`, the sha256 of
  `node_modules/.package-lock.json`, or `;deps=none` if that file is missing. A
  run made under different deps does not count as PASS: its criterion FAILs, and
  so does the FTT verdict. `doctor` reports the digest and flags a missing
  lockfile.

Result on branch `fix/cli-flagship2-p3s-20261011`, with the same command plus
`-q`:

```
74 passed in 20.51s
```

That is 64 unit tests and 10 E2E tests with `SKYYROSE2_E2E=1`. Without the
opt-in, the result is 64 passed and 10 skipped. Lint is clean: `ruff format`
left 15 files unchanged, `ruff check` passed, and `mypy` found no issues in 8
source files.

## Part 2 — Results

Run 2026-10-10 in worktree `DevSkyy-cli-flagship2-20261010` (origin/main
b5c14f738), macOS arm64. Toolchain: Node 22.23.2 (nodejs.org tarball,
sha256-verified), npm 10.9.8, Python 3.12.12, PHP 8.5.6.

Command:

```bash
SKYYROSE2_E2E=1 SKYYROSE2_NODE_BIN_DIR= VIRTUAL_ENV= CLI_ANYTHING_FORCE_INSTALLED=1 < node-v22.23.2 > /bin < repo > /.venv \
  python -m pytest cli_anything/skyyrose_flagship_2/tests -v --tb=no -s
```

```
collecting ... [_resolve_cli] Using installed command: /Users/theceo/DevSkyy/.venv/bin/cli-anything-skyyrose-flagship-2
tests/test_core.py::TestGates::test_every_script_gets_exactly_one_class PASSED
tests/test_core.py::TestGates::test_unclassified_is_refused PASSED
tests/test_core.py::TestGates::test_blocked_is_refused[render:commerce-scenes] PASSED
tests/test_core.py::TestGates::test_blocked_is_refused[certify:x] PASSED
tests/test_core.py::TestGates::test_build_cannot_run_as_check PASSED
tests/test_core.py::TestGates::test_missing_script_is_refused PASSED
tests/test_core.py::TestGates::test_image_judge_scripts_are_blocked_even_with_check_prefix PASSED
tests/test_core.py::TestVersion::test_reads_triple PASSED
tests/test_core.py::TestVersion::test_detects_disagreement PASSED
tests/test_core.py::TestVersion::test_rejects_bad_or_noop_version[2.5] PASSED
tests/test_core.py::TestVersion::test_rejects_bad_or_noop_version[v2.6.0] PASSED
tests/test_core.py::TestVersion::test_rejects_bad_or_noop_version[2.5.1] PASSED
tests/test_core.py::TestVersion::test_plan_writes_nothing PASSED
tests/test_core.py::TestVersion::test_write_updates_all_three PASSED
tests/test_core.py::TestVersion::test_failed_write_rolls_back PASSED
tests/test_core.py::TestCandidate::test_clean_revision_is_head PASSED
tests/test_core.py::TestCandidate::test_edit_dirties_and_changes_id PASSED
tests/test_core.py::TestCandidate::test_second_edit_to_dirty_file_changes_id PASSED
tests/test_core.py::TestCandidate::test_untracked_gate_input_dirties_and_changes_id PASSED
tests/test_core.py::TestCandidate::test_untracked_outside_gate_inputs_is_ignored PASSED
tests/test_core.py::TestCandidate::test_commit_changes_id PASSED
tests/test_core.py::TestCandidate::test_pin_status_detects_drift PASSED
tests/test_core.py::TestSession::test_round_trip PASSED
tests/test_core.py::TestSession::test_schema_mismatch_rejected PASSED
tests/test_core.py::TestSession::test_resume_only_same_repo PASSED
tests/test_core.py::TestSession::test_logs_written_per_run PASSED
tests/test_core.py::TestEvidence::test_owner_cannot_review_own_candidate PASSED
tests/test_core.py::TestEvidence::test_check_that_mutates_fails PASSED
tests/test_core.py::TestEvidence::test_stale_runs_excluded PASSED
tests/test_core.py::TestEvidence::test_dirty_is_partial_and_failed_is_blocked PASSED
tests/test_core.py::TestEvidence::test_independent_review_passes_clean_candidate PASSED
tests/test_core.py::TestEvidence::test_tampered_log_refused PASSED
tests/test_core.py::test_repo_discovery_fails_closed PASSED
tests/test_core.py::test_verify_refuses_without_wp_fixture PASSED
tests/test_core.py::test_fixture_dir_is_keyed_by_pin_manifest PASSED
tests/test_core.py::test_missing_fixture_manifest_is_a_clear_error PASSED
tests/test_core.py::TestReviewFindings::test_env_owner_swap_cannot_launder_self_review PASSED
tests/test_core.py::TestReviewFindings::test_review_without_runs_is_refused PASSED
tests/test_core.py::TestReviewFindings::test_flipped_ledger_status_is_caught PASSED
tests/test_core.py::TestReviewFindings::test_runs_from_other_harness_code_are_stale PASSED
tests/test_core.py::TestReviewFindings::test_record_carries_harness_hash PASSED
tests/test_core.py::TestReviewFindings::test_earlier_failure_is_reported PASSED
tests/test_core.py::TestReviewFindings::test_missing_pin_is_a_mismatch PASSED
tests/test_core.py::TestReviewFindings::test_unknown_owner_is_refused PASSED
tests/test_core.py::test_review_of_other_harness_code_does_not_count PASSED
tests/test_full_e2e.py::test_doctor_is_healthy PASSED
tests/test_full_e2e.py::test_help_and_introspection PASSED
tests/test_full_e2e.py::test_every_package_script_is_classified PASSED
  record: /private/var/folders/bz/k0nc044d1fz2rs3kz_gyv99m0000gn/T/pytest-of-theceo/pytest-157/test_gates_to_god_mode_x_pass0/evidence/task-evidence.json
PASSED
tests/test_full_e2e.py::test_ftt_review_requires_independent_reviewer PASSED
tests/test_full_e2e.py::test_edit_makes_old_runs_stale_and_dirty_is_partial PASSED
tests/test_full_e2e.py::test_refusals_run_nothing[render:commerce-scenes] PASSED
tests/test_full_e2e.py::test_refusals_run_nothing[certify:image-generation-preflight] PASSED
tests/test_full_e2e.py::test_refusals_run_nothing[nope:script] PASSED
tests/test_full_e2e.py::test_build_plan_does_not_run PASSED
============================= 55 passed in 15.44s ==============================
```

**Summary:** 63 passed, 0 failed (53 unit, 10 E2E) with `SKYYROSE2_E2E=1`.
Without the opt-in: 53 passed, 10 skipped. (The per-test listing above is the
55-test run, before the coverage tests were added.) The installed command was
used, as the `[_resolve_cli]` line shows.

### Full gate chain through the installed CLI

`check all` on clean candidate `c39251f11e7e4d19` (HEAD b5c14f738), first run
(before the review fixes):

```
✓ check:source-integrity       PASS exit 0 in 0.42s
✓ check:registry               PASS exit 0 in 0.43s
✓ check:assets                 PASS exit 0 in 0.67s
✓ check:i18n                   PASS exit 0 in 0.14s
✓ check:tokens                 PASS exit 0 in 0.1s
✓ check:card-renditions        PASS exit 0 in 7.12s
✓ check:scene-posters          PASS exit 0 in 0.3s
✓ check:font-delivery          PASS exit 0 in 0.44s
✓ check:frame-delivery         PASS exit 0 in 17.13s
✓ check:archive-theme          PASS exit 0 in 0.15s
✓ lint:php                     PASS exit 0 in 3.52s
✓ verify                       PASS exit 0 in 44.19s
claim verified · God Mode X PASS · Fashion Theme Team BLOCKED (awaiting independent review)
```

Final run after the review fixes, with the CLI code frozen at harness
`30aef6fbce86`, session `20261010T232731Z-c537ed`: all 12 gates PASS (`verify`
took 68.68s). Claim `verified`, God Mode X PASS, Fashion Theme Team BLOCKED
until a new independent review.

### Independent review (Fashion Theme Team `theme-release-engineer`)

The first review returned **FAIL**. It re-validated the record with God Mode X
(PASS), re-hashed all 12 logs, and found these issues. Each fix has a regression
test in `TestReviewFindings`:

- **P1 — self-review laundering.** Independence was checked against
  `SKYYROSE2_GATE_OWNER` at review time. It is now checked against the owners
  recorded on the candidate's runs.
- **P1 — no provenance.** Evidence was not bound to the tool code. Runs, reviews
  and records now carry `harness_sha256`, and so does the target environment
  label.
- **P2 — editable status.** A status flipped in `session.json` survived export.
  Each log now starts with a JSON header, and the export re-derives every status
  from that hashed log.
- **P3 — fail-open defaults.** A pin missing from `build-inputs.json` went
  unchecked, and the owner fell back to `unknown-owner`. Both now fail closed.
- **P3 — dropped failures.** An earlier FAIL superseded by a rerun was dropped
  silently. It is now reported as a P3 finding plus `cli.earlier_failures`.
- **P4 — untracked files.** Untracked files did not count toward the candidate.
  Fixed with `GATE_INPUT_DIRS`.

The first full run had no WordPress fixture, and `verify` failed with exit 255
(`UNVERIFIED: set V2_WP_FIXTURE`). That run is why `fixture prepare`, the
`doctor` fixture check, and the up-front refusal by `verify`/`package:theme`
were added. Two defects were found while testing and fixed with regression
tests:

- `--json` failures printed two JSON documents;
- a missing fixture manifest raised a raw `FileNotFoundError`.

### Coverage gaps

- **Build gates:** a real `build run` is not covered by an automated E2E,
  because it rewrites tracked files in the checkout under test. It was run by
  hand once: `build run build:registry` and `build run build:assets` both
  returned PASS on the clean tree and left 0 tracked changes, so the outputs
  reproduced byte-identical.
- **REPL:** `test_repl_runs_piped_commands_and_exits` drives it with piped
  stdin. Writing that test exposed a real bug: prompt_toolkit swallowed piped
  input, so an agent running
  `printf 'info\n' | cli-anything-skyyrose-flagship-2` got no output. The REPL
  now uses `input()` when stdin is not a TTY. The interactive prompt_toolkit
  path is not covered by automated tests.
- **Preview:** not implemented (see README).

### Coverage

The E2E tests drive the installed CLI through a subprocess, which plain
`pytest --cov` does not count. With that tool, the CLI module looked like 51%
and `backend.py` like 73%. The real figures come from coverage.py 7.16 run with
`[run] patch = subprocess` and `parallel = true`, then `coverage combine`:

| Module                                                              | Coverage |
| ------------------------------------------------------------------- | -------- |
| core/candidate.py                                                   | 100%     |
| core/gates.py                                                       | 100%     |
| core/evidence.py                                                    | 93%      |
| core/version.py                                                     | 92%      |
| skyyrose_flagship_2_cli.py                                          | 93%      |
| utils/backend.py                                                    | 87%      |
| core/session.py                                                     | 85%      |
| **Total** (excluding the vendored `repl_skin.py` and `__main__.py`) | **91%**  |
