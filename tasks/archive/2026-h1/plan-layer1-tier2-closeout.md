# Plan: Layer 1/Tier 2 Closeout — Open Items

**Branch:** `feat/v2-phase-0-5`
**Created:** 2026-05-05
**Source:** ship-readiness summary covering 7 commits (`9aa775004`..`8d5e640f8`)
**Scope:** Address the 3 non-blocking open items flagged by code-quality review before the PR ships. Each phase is self-contained and resumable in a fresh chat context.

---

## Phase 0 — Documentation Discovery (DONE in plan-creation chat)

The orchestrator has already grounded the plan in the actual code shapes. Subsequent phases cite exact files and line numbers below. **Re-run the relevant reads at the start of each phase** to avoid stale assumptions.

### Authoritative sources

| Topic | File | Anchor |
|-------|------|--------|
| Production pipeline 5-step flow | `scripts/nano_banana/pipeline.py` | `class ProductionPipeline` (l.64), `run_single` (l.133), `run_batch` (l.444) |
| Dossier injection into vision_desc | `scripts/nano_banana/pipeline.py` | l.169-187 (Tier 2 fix landed in `e6f908c14`) |
| Refinement prompt 3-tier construction | `scripts/nano_banana/pipeline.py` | `_build_refinement_prompt` (l.564) |
| Layer 1 single-SKU validator | `scripts/nano_banana/_validate_layer1.py` | hardcoded br-001 at l.110, l.124 |
| Spec builder | `scripts/nano_banana/spec_builder.py` | `build_dna_from_sku` (l.81), `augment_prompt_with_dossier_negatives` (l.109) |
| Tournament entry + result shapes | `scripts/nano_banana/tournament.py` | `run_tournament` (l.758), `TournamentResult` (l.188), `_dna_to_spec` (l.285), `JudgmentScore` (l.134) |
| FAL Kontext refinement | `scripts/nano_banana/engine_fal.py` | `refine_with_kontext` (l.163), `_closest_kontext_aspect_ratio` (l.41), `_is_png_bytes` (l.62) |
| Dossier loader (canonical truth) | `skyyrose/core/dossier_loader.py` | `Dossier` (l.41), `get_product_with_dossier` (l.146), `DossierMissingError` (l.32) |
| Existing test patterns | `tests/scripts/nano_banana/` | `test_spec_builder.py`, `test_kontext_helpers.py`, `test_refinement_prompt.py`, `conftest.py` |
| Catalog truth | `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` | 33 SKUs; `dossier_slug` column maps SKU → `data/dossiers/{slug}.md` |

### Allowed APIs (verified by reading source on 2026-05-05)

- `nano_banana.spec_builder.build_dna_from_sku(sku)` → `dict` with `spec`, `_dossier`, plus catalog row fields. **Raises** `KeyError` (SKU not in CSV) or `DossierMissingError` (no dossier file).
- `nano_banana.spec_builder.augment_prompt_with_dossier_negatives(prompt, dna)` → `str`. Idempotent if `dna["_dossier"]` is missing/empty.
- `nano_banana.pipeline.ProductionPipeline.from_env()` → reads `.env.secrets`, builds clients.
- `nano_banana.pipeline.ProductionPipeline.run_batch(products, views=None, output_dir=None)` → `list[PipelineResult]`. Iterates `run_single` per SKU × view; rate-limited via `cfg.retry_delay_seconds`.
- `nano_banana.pipeline.PipelineResult.to_dict()` → dict for JSON serialization (drops `vision_desc` field — see pipeline.py:48-61).
- `nano_banana.tournament.run_tournament(clients, source_path, candidate_path, dna, passing_threshold=98)` → `TournamentResult`. `clients` is a dict with optional keys `openai`, `anthropic`, `gemini`.
- `nano_banana.engine_fal.refine_with_kontext(image_path, prompt)` → `bytes | None` (PNG output, dim-preserving since `6df3b7fb0`). Internally calls `fal_client.subscribe("fal-ai/flux-pro/kontext", arguments={...})`.

### Anti-patterns to avoid

- Do **not** reintroduce `branding_spec` fallback paths. Tier 2 fix (`e6f908c14`) made dossier loading hard-fail on missing dossier; keep that contract.
- Do **not** re-add the `assets/data/prompts/overrides/{sku}.json` parallel store. Retired 2026-04-25; CI rejects references to it.
- Do **not** mutate `vision_desc` directly in new code. Future-proof: treat it as read-only after the dossier merge at pipeline.py:173-174.
- Do **not** invent FAL client method names — the only call surface is `fal_client.subscribe(model_id, arguments=...)`. Mock at that layer.
- Do **not** create new validators in `scripts/nano_banana/` without the leading-underscore convention for paid-call manuals. `_validate_layer1.py` set the precedent.

---

## Phase 1 — Multi-SKU Production Pipeline Validation Driver

**Open Item #2:** "Still no end-to-end pytest run on the production pipeline. Tier 2 fix is in code but only validated against `_validate_layer1.py` (which uses a single br-001 candidate). A full batch run with the corrected dossier-loading code would surface any regressions on other SKUs."

**Goal:** Surface any regressions in the Tier 2 dossier-loading code by running the full 5-step `ProductionPipeline` against a curated cross-collection SKU sample, with explicit cost cap and pass/fail summary.

### Tasks

- [ ] **1.1** Read `scripts/nano_banana/_validate_layer1.py` and `scripts/nano_banana/pipeline.py:run_batch` end-to-end before writing. Confirm `from_env()` env loading order matches the validator (`.env.judge-*` + `.env.hf` + `.env.secrets`).
- [ ] **1.2** Pick the SKU sample. Constraints:
    - One per collection (Black Rose, Love Hurts, Signature, Kids Capsule) → 4 SKUs minimum
    - Each must have a dossier file (verify `data/dossiers/{slug}.md` exists for each picked SKU)
    - Each must have a real source image at `wordpress-theme/skyyrose-flagship/assets/images/products/`
    - Suggested seed: `br-001`, `lh-002`, `sg-007`, `kids-001` — but verify dossier presence before locking. Read the catalog CSV directly to confirm `dossier_slug` is populated for each pick.
- [ ] **1.3** Create `scripts/nano_banana/_validate_pipeline_multi_sku.py` (leading underscore signals "manual paid-call validator, not a library script"). Pattern to copy: `_validate_layer1.py:41-105` for env loading + key-presence guard.
- [ ] **1.4** Build the products list as a `list[dict]` matching the shape `run_batch` expects: `{"sku": ..., "name": ..., "collection": ..., "source_image": <abs path>}`. Pull names/collections from the catalog CSV via `nano_banana.catalog.load_catalog()` — do not hardcode.
- [ ] **1.5** Cost cap: hard-stop after the first SKU produces a result if total estimated cost exceeds `$10` (configurable via `MAX_USD` env var, default 10). Read `result.cost_usd` after each SKU and abort the loop on exceed.
- [ ] **1.6** Output: print a summary table (sku, collection, qa_score, qa_passed, refinement_applied, cost_usd) and write the full `[r.to_dict() for r in results]` list to `tasks/multi-sku-validation-{ts}.json`.
- [ ] **1.7** Document a "STOP — Confirm before proceeding" gate at the top of `main()` per the project's STOP AND SHOW protocol. Print: action, SKUs, estimated max cost, source image paths. Require `y` on stdin to proceed.

### Documentation references

- Pattern to copy verbatim: `_validate_layer1.py:41-105` (env loading + missing-key guard).
- Pattern to copy: `pipeline.py:444-521` (`run_batch` summary construction — your driver wraps this, doesn't reimplement it).
- Confirmation protocol: `CLAUDE.md` "STOP AND SHOW" section.

### Verification checklist

- [ ] Script aborts cleanly when any required env var is missing (test by running with `OPENAI_API_KEY=""`).
- [ ] Script aborts cleanly when a picked SKU has no dossier (test by passing a known-bad SKU).
- [ ] STOP-gate prevents accidental paid call (test by passing `n` on stdin).
- [ ] Real run with all 4 SKUs produces 4 `PipelineResult` entries.
- [ ] Per-SKU `qa_score` is recorded; no Python exception bubbles to top-level.
- [ ] Output JSON at `tasks/multi-sku-validation-{ts}.json` is valid JSON and parseable.

### Anti-pattern guards

- Do **not** call paid APIs in CI. This script is manual-only — leading underscore + module-level comment block must say so explicitly.
- Do **not** reuse `_validate_layer1.py`'s br-001-only logic; this is a new file with batch semantics, not a refactor of the Layer 1 validator.
- Do **not** suppress exceptions inside the SKU loop. If `run_single` raises, log and continue, but record the exception in the JSON so it's not silently lost.

---

## Phase 2 — Mock-Based Coverage on Paid-API Code Paths

**Open Item #1:** "Coverage on paid-API code paths is 0%. Acceptable for integration test territory but worth noting in PR description."

**Goal:** Bring `pipeline.py` 13% → ~60%, `tournament.py` 26% → ~60%, `engine_fal.py` 23% → ~70% by mocking SDK boundaries and exercising orchestration logic. No paid calls; no integration territory.

### Tasks

- [ ] **2.1** Read `tests/scripts/nano_banana/conftest.py` and existing test files (`test_spec_builder.py`, `test_kontext_helpers.py`, `test_refinement_prompt.py`) to identify the established fixture patterns. Reuse `conftest.py` fixtures rather than duplicating.
- [ ] **2.2** Create `tests/scripts/nano_banana/test_pipeline_mocked.py`. Mock surface (mock at the lowest reasonable layer):
    - `nano_banana.client.get_genai_client` / `get_openai_client` → return `MagicMock()` instances
    - `nano_banana.vision_describe.describe_product` → return a fixed dict (covers cache hit/miss paths in `_get_or_cache_vision`, pipeline.py:523)
    - `nano_banana.generate.generate_gemini` / `generate_gpt` → return PNG bytes from a fixture
    - `nano_banana.engine_fal.generate_flux_fal` / `refine_with_kontext` → return PNG bytes
    - `nano_banana.tournament.run_tournament` → return a hand-built `TournamentResult` fixture
    - `nano_banana.utils.quality_gate` → return `True`
    - `nano_banana.utils.save_image` → no-op
    - `nano_banana.prompt_registry.PromptRegistry.load` → return a stub registry
    - `nano_banana.router.route_product` → return a list of one `RouteDecision`
- [ ] **2.3** Tests to add in `test_pipeline_mocked.py`:
    - `test_run_single_happy_path_no_refinement` — Tournament returns score above `qa_auto_approve`, no refinement triggered, cost recorded.
    - `test_run_single_text_threshold_triggers_refinement` — Judge `text_accuracy` below `qa_refine_text_threshold`, refinement called.
    - `test_run_single_logo_threshold_triggers_refinement` — Same for `logo_accuracy`.
    - `test_run_single_hallucination_veto_triggers_refinement` — Synthesis judge `hallucination_veto=True`, refinement called even with high vision-pair score.
    - `test_run_single_dossier_soft_fail_falls_back_to_inferred_dna` — `build_dna_from_sku` raises `DossierMissingError`, pipeline logs warning and proceeds with inferred DNA. Verify `vision_desc` lacks `spec` key.
    - `test_run_single_dossier_negatives_appended_to_prompt` — When dossier exists, `augment_prompt_with_dossier_negatives` mutation appears in the prompt passed to `generate_gemini`. Spy on the prompt argument.
    - `test_run_single_router_returns_no_decisions_returns_empty_result` — Edge case: empty router decisions list.
    - `test_run_single_all_attempts_fail_records_failure` — All `cfg.max_attempts` generation attempts return `None`; result has no `output_path`, has `issues`.
    - `test_run_batch_aggregates_pass_fail_skip_counts` — Mock `run_single`, verify summary counts in batch report match `passed/needs_review/skipped`.
    - `test_run_batch_skips_products_missing_source_image` — One product has missing `source_image`; result has `issues=["No source image available"]`, no `run_single` call for it.
- [ ] **2.4** Create `tests/scripts/nano_banana/test_tournament_mocked.py`. Mock surface:
    - OpenAI: `client.chat.completions.create` → return `MagicMock` with `.choices[0].message.content = '{"overall": 75, ...}'`
    - Gemini: `client.models.generate_content` → return `MagicMock` with `.text = '{"overall": 75, ...}'`
    - Anthropic: `client.messages.create` → return `MagicMock` with `.content[0].text = '{"overall": 75, ...}'`
- [ ] **2.5** Tests to add in `test_tournament_mocked.py`:
    - `test_run_tournament_three_judges_aggregates_correctly` — All three judges return scores; aggregate equals `synthesis_overall` (per `TournamentResult` doc, l.196-201).
    - `test_run_tournament_synthesis_failure_falls_back_to_vision_pair_mean` — Anthropic mock raises; aggregate equals `vision_pair_mean`.
    - `test_run_tournament_only_one_vision_judge_available` — Only OpenAI client passed; verify graceful single-judge path.
    - `test_run_tournament_uses_dossier_spec_when_present` — `dna` has `"spec"` key; verify the spec text is included in the prompt sent to each judge (spy on the call args). Cross-check against `_dna_to_spec` (l.285).
    - `test_run_tournament_synthesizes_spec_from_flat_fields_when_no_spec_key` — `dna` lacks `"spec"`; verify `_dna_to_spec` reconstructs from flat fields.
    - `test_zero_judgment_returned_when_judge_call_raises` — Forced exception path returns a `_zero_judgment` (l.733), not propagated.
    - `test_hallucination_veto_set_when_synthesis_overall_below_50_with_consensus` — Boundary case for the synthesis-judge veto logic.
- [ ] **2.6** Create `tests/scripts/nano_banana/test_engine_fal_mocked.py`. Mock surface:
    - `fal_client.subscribe` → return `{"images": [{"url": "https://...", "content_type": "image/png"}]}`
    - `nano_banana.engine_fal._download_image` → return a fixture PNG bytes
    - `os.environ.get("FAL_KEY")` via monkeypatch
- [ ] **2.7** Tests to add in `test_engine_fal_mocked.py`:
    - `test_refine_with_kontext_returns_png_bytes` — Happy path; verify aspect-ratio-preserving call to `_closest_kontext_aspect_ratio`.
    - `test_refine_with_kontext_no_fal_key_returns_none` — `_fal_available()` False; returns `None`.
    - `test_refine_with_kontext_subscribe_raises_returns_none` — FAL exception caught; returns `None`.
    - `test_refine_with_kontext_non_png_response_returns_none` — `_is_png_bytes` False; returns `None`.
    - `test_generate_flux_fal_passes_correct_arguments` — Verify the `arguments` dict to `subscribe` matches the FLUX model schema (image, prompt, aspect_ratio, output_format).
- [ ] **2.8** Run `pytest tests/scripts/nano_banana/ --cov=scripts.nano_banana --cov-report=term-missing` and confirm:
    - `pipeline.py` ≥ 60%
    - `tournament.py` ≥ 60%
    - `engine_fal.py` ≥ 70%
    - All 53 existing tests still pass.

### Documentation references

- pytest mock pattern (existing): `tests/scripts/nano_banana/test_spec_builder.py` uses `monkeypatch` for `get_product_with_dossier`. Copy that style.
- pytest fixture pattern (existing): `tests/scripts/nano_banana/conftest.py` for shared image fixtures.
- TournamentResult shape: `tournament.py:188-235` — use this exact shape when hand-building fixtures.
- JudgmentScore shape: `tournament.py:134` (read full class body before writing fixture).

### Verification checklist

- [ ] `pytest tests/scripts/nano_banana/ -v` → all pass.
- [ ] `pytest tests/scripts/nano_banana/ --cov=scripts.nano_banana --cov-report=term` shows the targets above.
- [ ] No paid API calls during test run (verify by running with `OPENAI_API_KEY=invalid`, `ANTHROPIC_API_KEY=invalid`, etc. — tests must still pass because mocks intercept).
- [ ] `ruff check tests/scripts/nano_banana/` clean.
- [ ] `black --check tests/scripts/nano_banana/` clean.

### Anti-pattern guards

- Do **not** mock at the wrong layer. Mock at the SDK boundary (`client.chat.completions.create`), not at the wrapper (`judge_with_gpt`) — the latter hides the routing logic we're trying to cover.
- Do **not** add network-dependent tests to this file. Anything that hits a real URL belongs in a separate `_validate_*` script, not pytest.
- Do **not** use `pytest.skip` to mask real coverage gaps. If a path is genuinely untestable without paid calls, document it in the test docstring with rationale.
- Do **not** invent FAL methods — the only call surface is `fal_client.subscribe(model_id, arguments={...})`. Verify in `engine_fal.py:163` before mocking.

---

## Phase 3 — Typed VisionContext Container

**Open Item #3:** "Production pipeline `vision_desc` dict carries dual roles (inferred DNA + canonical dossier). Code-quality reviewer flagged this as a structural smell — could be a typed dataclass instead."

**Goal:** Replace the string-keyed `vision_desc` dict with a typed `VisionContext` dataclass that explicitly separates (a) inferred Gemini DNA fields, (b) catalog metadata, (c) canonical spec, (d) dossier object. Maintain backward-compatible dict-style access during the migration so consumers in `tournament.py` don't break.

**Risk:** Higher than Phases 1-2. This touches `tournament.py:_dna_to_spec` (l.285), `pipeline.py:run_single` (l.187, 316, 405), and `spec_builder.py:augment_prompt_with_dossier_negatives` (l.109). Plan for a single PR with full test coverage before merge.

### Tasks

- [ ] **3.1** Read all consumers of `vision_desc` / `dna` parameter end-to-end:
    - `pipeline.py:164-187` (construction and dossier merge)
    - `pipeline.py:195` (passed to `route_product`)
    - `pipeline.py:212` (passed to `registry.get_prompt`)
    - `pipeline.py:218` (passed to `augment_prompt_with_dossier_negatives`)
    - `pipeline.py:316, 405` (passed as `dna=` to `run_tournament`)
    - `tournament.py:285` (`_dna_to_spec` reads `dna.get("spec")`, `dna.get("garment_type")`, etc.)
    - `tournament.py:758` (`run_tournament` parameter)
    - `spec_builder.py:81` (`build_dna_from_sku` builds the dict)
    - `spec_builder.py:127` (`augment_prompt_with_dossier_negatives` reads `dna.get("_dossier")`)
    - `router.py` — find all `vision_desc` reads via `grep -n vision_desc scripts/nano_banana/router.py`
- [ ] **3.2** Define `VisionContext` in a new file `scripts/nano_banana/vision_context.py`:
    - Fields: `inferred: dict`, `catalog: dict`, `spec: str | None`, `dossier: Dossier | None`
    - `__getitem__`, `__contains__`, `get(key, default)` shim methods that read from the merged view in this priority: `catalog` > `inferred` > `{"spec": self.spec, "_dossier": self.dossier}`. This gives backward-compat dict access for tournament/router consumers without touching their code.
    - `to_dict()` for JSON serialization (drops `dossier` object, keeps `spec` string).
    - `__post_init__` validation: `spec` and `dossier` must be co-present or co-absent (you don't have one without the other from the canonical loader).
- [ ] **3.3** Update `spec_builder.build_dna_from_sku` to return `VisionContext` instead of dict.
- [ ] **3.4** Update `pipeline._get_or_cache_vision` to return `VisionContext` (with `inferred=desc`, `catalog={}`, `spec=None`, `dossier=None`).
- [ ] **3.5** Update `pipeline.run_single`:
    - Replace `vision_desc["spec"] = ...` with `vision_desc.spec = ...`
    - Replace `vision_desc["_dossier"] = ...` with `vision_desc.dossier = ...`
    - Update `result.vision_desc` to store `vision_desc.to_dict()` for JSON serialization
- [ ] **3.6** Update `spec_builder.augment_prompt_with_dossier_negatives` signature to accept `VisionContext` directly, drop the `dna.get("_dossier")` indirection.
- [ ] **3.7** Update tests:
    - All `test_pipeline_mocked.py` cases that construct fake `dna` dicts → use `VisionContext(...)` instead.
    - `test_spec_builder.py` → update fixtures to `VisionContext`.
    - `_validate_layer1.py` → if it reads `dna["spec"]`, switch to `dna.spec`. (Verify by running the script if you have envs set up.)
- [ ] **3.8** Verify `tournament._dna_to_spec` works unchanged because `__getitem__` shim returns spec when `dna["spec"]` is requested.

### Documentation references

- Existing dataclass patterns: `pipeline.py:31` (`PipelineResult`), `tournament.py:134` (`JudgmentScore`), `tournament.py:188` (`TournamentResult`).
- Dossier shape: `skyyrose/core/dossier_loader.py:41` (read `Dossier` class fields before designing `VisionContext`).
- Backward-compat dict access pattern (Python stdlib): `collections.abc.Mapping` — implement at minimum `__getitem__`, `__iter__`, `__len__` if needed by any consumer.

### Verification checklist

- [ ] `pytest tests/scripts/nano_banana/ -v` → all pass.
- [ ] `mypy scripts/nano_banana/` clean (verify type hints on new dataclass).
- [ ] `ruff check scripts/nano_banana/ tests/scripts/nano_banana/` clean.
- [ ] `grep -rn 'vision_desc\["\|dna\["\|dna\.get(' scripts/nano_banana/ tests/scripts/nano_banana/` returns no results outside `vision_context.py` itself (i.e., all consumers use attribute access, not dict access).
- [ ] If Phase 1 ran successfully, re-run `_validate_pipeline_multi_sku.py` against 1 SKU only to confirm no regression.

### Anti-pattern guards

- Do **not** drop the `__getitem__` shim until every consumer is migrated. The shim is the bridge that lets Phase 3 ship without coordinated changes across `tournament.py` / `router.py`.
- Do **not** rename existing fields. `inferred_dna` → `inferred` is fine; `spec` → `judge_spec` would force every test fixture to update.
- Do **not** add JSON serialization fields that leak the `Dossier` object. `.to_dict()` should serialize spec text only, not the full dossier (which is large).

---

## Phase 4 — Verification & PR Description

**Goal:** Run the full quality gate, write the PR description capturing all 7 commits + the new work, and verify nothing regressed.

### Tasks

- [ ] **4.1** Run the full local gate:
    - `make format` (isort + ruff --fix + black)
    - `make lint`
    - `pytest tests/scripts/nano_banana/ -v`
    - `pytest tests/ -k "not slow" --timeout=30` (catch any cross-package breakage)
    - `mypy scripts/nano_banana/ skyyrose/core/dossier_loader.py`
- [ ] **4.2** Run `pytest --cov=scripts.nano_banana --cov-report=term-missing` and capture final coverage numbers per file. Compare to the targets in Phase 2.
- [ ] **4.3** Write `tasks/pr-description-phase-0-5-closeout.md` with:
    - Summary of all 7 prior commits (already in session summary)
    - New phases 1-3 work
    - Final coverage table
    - Multi-SKU validation results (from Phase 1 JSON)
    - Honest open items remaining (e.g., paid-API integration tests still 0% — but now structurally so, not from missing tests on testable code)
    - Test plan checklist
- [ ] **4.4** Run a fresh `_validate_layer1.py` against br-001 to confirm the Phase 3 dataclass refactor didn't break the Layer 1 lift (45 → 90 verdict).
- [ ] **4.5** `gh pr create` with the description from 4.3.

### Verification checklist

- [ ] All gates green.
- [ ] Coverage targets met or rationale documented.
- [ ] PR description includes test plan with executable verification steps.
- [ ] No leaked secrets in any new file (`grep -rE 'sk-ant|sk-proj|AIza' scripts/nano_banana/ tests/scripts/nano_banana/`).
- [ ] `.env.judge-*` files still chmod 600 + gitignored.

### Anti-pattern guards

- Do **not** auto-merge. PR review on this branch is required (cross-cutting refactor in Phase 3).
- Do **not** force-push after PR opens. Add new commits only.

---

## Phase Sequencing Rationale

| Phase | Risk | Cost | Why this order |
|-------|------|------|----------------|
| 1 | Low — additive script, gated by STOP-confirm | $5-15 paid (manual) | Validates Tier 2 dossier code in production scope first. If broken, blocks Phase 2. |
| 2 | Low — pure pytest mocks | $0 | Coverage is a quality metric improvement, no behavior change. |
| 3 | Medium — refactor across 3 files | $0 | Done last because Phase 2 mocks become the safety net. Coverage from Phase 2 catches regressions. |
| 4 | Low — gates + PR | $0 | Standard ship checklist. |

**Total time estimate:** 1.5-3 hours of focused work, primarily Phase 2 (test authoring) and Phase 3 (refactor).
**Total paid API spend:** $5-15 in Phase 1 manual run, $0 elsewhere.
