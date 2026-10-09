# Handoff — Elite Studio Pipeline Hardening (2026-05-11)

**Base:** `main` @ `19a8952d7` (P1/P2/P4/P5/P6 hardening committed)
**Scope:** Render pipeline merge + provider tournament wire-in + studio-rooted hardening
**Verification:** 83/83 tests green (28 render_pipeline + 36 round-table + 8 trellis + 11 hardening)
**Status:** P3 (manifest revision) pending, P7 (ADK as generator engine) pending, FILESYSTEM RESTRUCTURE open (user asked, awaiting clarification)
**Critical constraint locked into memory:** Elite Studio is the canonical imagery hub — NOT being retired. Future SaaS product. Every imagery pipeline routes through `skyyrose/elite_studio/`. ADK render_pipeline, round-table 3D, Meshy/TRELLIS/Tripo/FASHN are engines IT composes. See `/Users/theceo/.claude/projects/-Users-theceo-DevSkyy/memory/project_elite_studio_canonical.md`.

---

## What shipped this session

### Phase A — Render pipeline merge (commit `535fe4865`)
Merged `execute/render-pipeline-validation` into main. 17 files, 558+/100-. ADK pipeline at `agents/render_pipeline/` — 9-step SequentialAgent + LoopAgent with 28 unit tests. `dossier_loader` gained `logo_reference` + `extra_logos` fields (additive, defaulted).

### Phase C — MeshyAgent wired into round-table (commit `e84d1d007`)
`ThreeDProvider.MESHY` added to `orchestration/threed_round_table.py`: enum + quality (geo=82, tex=82) + 300s timeout + lazy loader + dispatch + conditional injection in `compete_image_to_3d`.

### Phase D — TRELLIS.2 subprocess wrapper (commits `d52104e26`, `719bc9c8d`)
New `agents/trellis_agent.py` — subprocess wrapper around the `trellis2` conda env (mirrors Blender pattern at `skyyrose/elite_studio/agents/three_d_agent.py:252`). `is_available()` probes for conda + repo; gracefully disables on machines without the env. `ThreeDProvider.TRELLIS_2` wired into round-table with quality (geo=98, tex=95 — SOTA local) + 600s timeout + `enable_trellis=False` opt-in flag. 8 unit tests.

### Blocker 1 — ADK output path aligned (commit bundled in `e525affd1`)
`agents/render_pipeline/tools/generate_image.py` no longer writes to `agents/render_pipeline/output/`. Default is now `renders/gated/<sku>/<sku>-<view>-render.webp` per `docs/PIPELINE-ARCHITECTURE.md` Pipeline 1 spec. Override via `RENDER_PIPELINE_OUTPUT_DIR` env. Per-SKU subdir. 28 tests still green.

### Hardening batch (commit `19a8952d7`)
Single commit, 8 files, 609+/28-:

| ID | What | Files |
|---|---|---|
| **P1** | `RunBudget` thread-safe cost ceiling. `ELITE_STUDIO_BUDGET_USD=25.0` default. Stages call `ensure_within_budget` → `spend`. `BudgetExceededError` halts run cleanly. | `skyyrose/elite_studio/budget.py` (new) |
| **P2** | `telemetry.write_run_summary()` persists per-SKU JSON to `logs/runs/<workflow_id>.json` on every run completion (success or failure). `finalize_node` rewired to capture engine, qa, fidelity, budget snapshot, timings. | `skyyrose/elite_studio/telemetry.py`, `graph/nodes.py` |
| **P4** | `_sku_tokens_consistent(task_id, image_path)` rejects round-table dispatch on cross-SKU leakage. Variant-aware (br-003 ≠ br-003-oakland; permits `br-003-baseball-classic-oakland.jpeg` for `br-003-oakland` task). Zero-cost guard — fires before any provider call. | `orchestration/threed_round_table.py` |
| **P5** | `TrellisTimeoutError(TrellisAgentError)` — distinct exception so round-table circuit breaker can treat cold-start timeouts differently from hard failures. | `agents/trellis_agent.py` |
| **P6** | `ThreeDAgent.generate_replica` gained `ELITE_STUDIO_USE_ROUND_TABLE=1` opt-in. When set, Stage 1 routes through `ThreeDRoundTable.compete_image_to_3d` (Meshy + Tripo + TRELLIS + AniGen tournament) instead of direct `MeshyClient`. Default behavior unchanged — no breakage. | `skyyrose/elite_studio/agents/three_d_agent.py` |

`EliteStudioState` schema extended with `budget: RunBudget | None` and `run_summary_path: str`. `create_initial_state` instantiates default budget.

### Phase F report (uncommitted, advisory)
`tasks/phase-f-report.md` — 7 legacy scripts banner-marked with `# DEPRECATED:` comments, ~33 standalone scripts flagged for archive. No functional changes. **Re-read this report through the lens of the elite_studio-canonical correction** — the "migrate" buckets need re-classification: scripts that already call `skyyrose.elite_studio` are correctly wired; only scripts that bypass elite_studio need attention.

### Phase G report (uncommitted, advisory)
`tasks/phase-g-report.md` — 8 docs + 2 wolf files touched. Codemaps refreshed. `docs/3D_GENERATION_PIPELINE.md` gained provider tournament section. `.wolf/cerebrum.md` + `.wolf/anatomy.md` updated. Subagent claimed `docs/PIPELINE-ARCHITECTURE.md` was wrong abstraction and skipped — **subagent was wrong, doc exists and is the correct banner target**.

---

## Still to do

### P3 — Manifest revision (HIGHEST PRIORITY, doc work, no money)
`tasks/phase-e-manifest.md` currently quotes `$5-20` cost range. Real ceiling is `~$30` per 33-SKU run with 3-judge QA + refine loop + 3D providers. Revise with:
- Per-stage breakdown (Gemini gen, QA tournament 3-judge, refine loop, 3D round-table)
- Budget-aware (now that P1 enforces `ELITE_STUDIO_BUDGET_USD=25.0`, the run will fail-clean before breach — manifest should explain this safety)
- Elite-studio-rooted phrasing (NOT "ADK pipeline dispatch" — "Elite Studio render run, ADK engine")

### P7 — ADK render_pipeline reachable from generator_node
Currently `generator_node` calls `GeneratorAgent.generate()` directly. Add `engine="adk-render"` option that dispatches into `agents.render_pipeline.agent.root_agent`. Studio then has Layer 1 = legacy compositor / Layer 2 = ADK render. Both selectable per-run.

### FILESYSTEM RESTRUCTURE (OPEN — user request, awaiting clarification)
User said: *"within the Elite studio should be a structurally sound file system thats easily read upon and follows some of the elite production practices. products should have a home file directory inside the elite studio with sub directories making it clean, clear so when need to render its no confusion."*

**Current chaos** (8+ scattered output roots — grep confirmed):
- `renders/gated/<sku>/` (just-aligned ADK output)
- `renders/3d/` (ThreeDAgent default `output_dir_3d`)
- `renders/2d/` (ThreeDAgent default `output_dir_2d`)
- `renders/output/{tripo,compositor,b2-smoke}/`
- `output/` (flat, mixed `.glb`s — legacy)
- `generated_assets/{3d,product_images,lora_test}/`
- `assets/3d-models-generated/meshy/`
- `skyyrose/elite_studio/logs/runs/<wf_id>.json` (just-added P2)

**Proposed canonical tree** (per-SKU home inside elite_studio):
```
skyyrose/elite_studio/products/<sku>/
  source/          # canonical inputs — techflat, real photos, hero refs
  renders/
    2d/<view>/v1.webp    # front/back/detail/hero, versioned
    3d/glb/v1.glb        # winning provider GLB
    3d/scaffolds/<view>.png
  variants/<variant_id>/
  qa/                    # scores.json, flagged/
  runs/<workflow_id>.json
```

**4 questions I asked, user requested clarification, NOT answered yet:**
1. **Tree root** — inside the package (`skyyrose/elite_studio/products/`) vs sibling workspace (`studio_workspace/products/`) vs env-configurable
2. **Brand layer** — flat `<sku>/` for now vs `<brand>/<sku>/` from day 1 (SaaS scoping)
3. **Migration** — hard cutover vs symlink shim vs coexist (new writers only)
4. **Versioning** — keep all attempts (`v1/v2/...`) vs rotate last N vs overwrite

**Next agent: ASK these again, or interpret based on user clarification when they reply.**

---

## Test baseline (anchor for verifying you didn't break anything)

```bash
python -m pytest \
  agents/render_pipeline/tests/test_tools.py \
  tests/test_round_table.py \
  tests/orchestration/test_threed_round_table_alignment.py \
  tests/test_trellis_agent.py \
  tests/test_elite_studio_hardening.py \
  -q --timeout=30
# Expected: 83 passed
```

---

## Critical context (DO NOT FORGET)

### Elite Studio is the hub (memory: `project_elite_studio_canonical.md`)
- NOT being retired
- Every imagery pipeline routes through `skyyrose/elite_studio/`
- Future SaaS product (scope later)
- ADK render_pipeline, round-table, Meshy/TRELLIS/Tripo/FASHN are ENGINES it composes
- Phase F "migrate" classifications need re-reading through this lens

### STOP-AND-SHOW gate is binding
- Phase E (33-SKU i2i re-render) is HALTED. `tasks/phase-e-manifest.md` written.
- Per `CLAUDE.md`: no paid API call without explicit user `[y/yes/dispatch]`
- 4 dispatch options were offered in the manifest; user said "we're not starting any rendering until this pipeline is hardened" — DO NOT DISPATCH

### Background agent outputs (advisory, uncommitted)
- `tasks/phase-f-report.md` — script migration audit (needs elite_studio-canonical re-read)
- `tasks/phase-g-report.md` — docs/codemap refresh (skipped `docs/PIPELINE-ARCHITECTURE.md` in error)

### Provider tournament shape
`orchestration/threed_round_table.py` ThreeDProvider enum (post-Phase D):
```
HUNYUAN3D_2, TRIPOSR, INSTANTMESH, LGM, SHAP_E, POINT_E,
TRIPO3D, ANIGEN, MESHY,
TRELLIS_2,   # local GPU, opt-in via enable_trellis=False
CUSTOM
```
TRELLIS quality leads at geo=98/tex=95. Default enable: `enable_meshy=True`, `enable_tripo3d=True`, `enable_anigen=True`, `enable_trellis=False`.

### Output path env vars (P-batch additions)
| Var | Default | Owner |
|---|---|---|
| `RENDER_PIPELINE_OUTPUT_DIR` | `REPO_ROOT/renders/gated` | ADK pipeline |
| `TRELLIS_OUTPUT_DIR` | `renders/3d` | TRELLIS wrapper |
| `TRELLIS_CONDA_ENV` | `trellis2` | TRELLIS wrapper |
| `TRELLIS_PYTHON` | (auto-resolve via conda) | TRELLIS wrapper override |
| `TRELLIS_TIMEOUT_SECONDS` | `600` | TRELLIS wrapper |
| `ELITE_STUDIO_BUDGET_USD` | `25.0` | Studio run budget (P1) |
| `ELITE_STUDIO_RUN_SUMMARY_DIR` | `skyyrose/elite_studio/logs/runs/` | Studio run summaries (P2) |
| `ELITE_STUDIO_USE_ROUND_TABLE` | `0` | ThreeDAgent dispatch toggle (P6) |

---

## Where to resume

1. **First action:** read this entire file + `tasks/phase-e-manifest.md` + the user's last 3 messages in the conversation history.
2. **Address the filesystem question** — user asked, I proposed structure + 4 questions, user wants clarification. Ask again (or interpret their clarification when they reply).
3. **Then P3** (manifest revision) and **P7** (ADK as generator engine option). Both pure code/docs, no money.
4. **Phase E dispatch** remains BLOCKED on user's explicit `[y]` after filesystem + P3 + P7 are done.

---

## Recent commits on main (most recent first)

```
19a8952d7  feat(elite-studio): hardening P1/P2/P4/P5/P6 — budget, summaries, SKU guards
e525affd1  feat(dashboard): wire assets to real data — priority 6  [contains the ADK output-path realign as side effect]
719bc9c8d  chore(tests): drop unused os import in test_trellis_agent
d52104e26  feat(3d-round-table): wire local TRELLIS.2 as image-to-3D provider
6ebc1622f  test(theme): add PHPUnit suite + PHPCS-clean hardening batch — 93.6% coverage
e84d1d007  feat(3d-round-table): wire MeshyAgent into round-table tournament
535fe4865  merge: execute/render-pipeline-validation -> main (ADK render pipeline)
```

---

## Pipeline integrity statement

As of `19a8952d7`, the Elite Studio canonical pipeline has:
- A hard cost ceiling (P1)
- A run summary written on every completion (P2)
- A cross-SKU image-leak guard at the round-table boundary (P4)
- A distinct timeout exception for cold-start TRELLIS runs (P5)
- An opt-in path that routes 3D generation through the provider tournament instead of single-provider Meshy (P6)
- All 4 ThreeDProvider expansions (MESHY, TRELLIS_2 + the pre-existing ANIGEN, TRIPO3D) at quality + timeout + dispatch + injection parity
- 83/83 tests green

It is **not yet dispatch-ready** because (a) the manifest cost estimate is stale (P3), (b) the on-disk product home structure is undecided (open filesystem question), (c) the 3 dossier `logo_reference` gaps + 11 `extra_logos` gaps remain (Corey-authoring decision per `feedback_dossier_authoring.md`), and (d) the user explicitly said "no rendering until elite-level."
