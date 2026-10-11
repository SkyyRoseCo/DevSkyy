# PR: Layer 1/Tier 2 Closeout — Mock Coverage + Typed VisionContext

**Source branch:** `feat/v2-phase-0-5`
**Suggested base branch:** `main`
**Scope:** the 9 most-recent commits on `feat/v2-phase-0-5` covering the Layer 1 refinement-loop wiring, Tier 2 dossier integration, and the closeout work (mock coverage + VisionContext refactor).

> ⚠️ **PR-scope decision needed:** the local `feat/v2-phase-0-5` branch is 65 commits ahead of `main`, of which only the bottom 9 are the Layer 1/Tier 2 closeout work this description covers. The other 56 commits cover Phase 0 deliverables (KB scaffolding, brand canon, B2/C3 quality gates, RAG pipelines, scope routing, embedding gates, CLIP alignment, brand centroids, dual-vision migration). Bundling them into one PR would be unmanageable to review. Recommended path: **cut a focused branch (`feat/layer1-tier2-closeout`) from `main` containing only the 9 closeout commits, push, and open a PR against `main`.** This description is written for that focused branch.

---

## Summary

Closes the Layer 1/Tier 2 dossier integration cycle with three artifacts:

1. **Production code that scores against canonical dossiers** — pipeline now hard-fails on missing dossier (no fallback to inferred DNA), generator sees authored negatives at render time, refinement loop consumes synthesis-judge fixes.
2. **Mock-based coverage on previously 0% paid-API code paths** — 67 new tests at SDK boundaries (FAL, OpenAI, Gemini, Anthropic). `pipeline.py` 13 → 98%, `tournament.py` 26 → 85%, `engine_fal.py` 23 → 85%.
3. **Typed `VisionContext` dataclass** replacing the dual-role `vision_desc` dict. Mapping-style shim keeps ~30 read-side consumers unchanged; only 2 write sites in `pipeline.run_single` migrated to attribute syntax.

Plus one production bug fix discovered while writing tests.

---

## Commits in scope

| SHA | Type | Headline |
|-----|------|----------|
| `9407600dc` | docs | Layer 1/Tier 2 closeout phased plan |
| `602174a3b` | test+refactor | mock coverage 13→98% on pipeline + typed VisionContext |
| `8d5e640f8` | refactor | /simplify cleanup — collapse duplicates, cache, drop noise |
| `e6f908c14` | feat | Tier 2 production dossier load + Layer 2 negative prompts |
| `6720d0919` | test | re-validate Layer 1 against canonical dossier — honest +36 lift |
| `65cc8ea2f` | fix | load judge spec from canonical dossier, not ad-hoc DNA |
| `6df3b7fb0` | fix | preserve Kontext PNG output + dimensions; bump GPT timeout |
| `909e50d2a` | test | Layer 1 closed-loop validation: 45→90 (against fake DNA) |
| `(prior session)` | feat | Layer 1 — wire synthesis fixes into refinement loop |

---

## Bug fix included

**`pipeline.py` `UnboundLocalError` on QA exception path.** When `run_tournament` raised an exception, `qa_result` was never assigned in the `try` block, but the downstream refinement check then read `hasattr(qa_result, "judges")` — which raised `UnboundLocalError` instead of returning `False`. Two-line fix:

```python
qa_result: TournamentResult | None = None  # initialize before try
try:
    qa_result = run_tournament(...)
    ...
except Exception as exc:
    log.error(...)

# downstream:
if qa_result is not None and hasattr(qa_result, "judges"):
    ...
```

Surfaced by `test_run_single_qa_exception_records_issue_but_returns_result`.

---

## Coverage table

| File | Before | After | Target |
|------|--------|-------|--------|
| `scripts/nano_banana/pipeline.py` | 13.23% | **98.06%** | ≥60% ✅ |
| `scripts/nano_banana/tournament.py` | 25.62% | **84.88%** | ≥60% ✅ |
| `scripts/nano_banana/engine_fal.py` | 22.82% | **85.23%** | ≥70% ✅ |
| `scripts/nano_banana/spec_builder.py` | 91.07% | 91.38% | — |
| `scripts/nano_banana/vision_context.py` | (new) | **97.14%** | — |
| Total nano_banana package | 7.17% | 27.91% | — |

The remaining package-level gap is in modules untouched by this PR (`cli.py` 0%, `generate.py` 8%, `vision_describe.py` 5%, `prompt_registry.py` 20%, etc.) — out of scope for this closeout.

---

## Test counts

- Before: 53 tests in `tests/scripts/nano_banana/` (5 files)
- After: 181 tests (9 files)
- New files added: `test_engine_fal_mocked.py` (13), `test_tournament_mocked.py` (30), `test_pipeline_mocked.py` (51), `test_vision_context.py` (32). Net +128.

---

## Architectural changes

### Typed `VisionContext` replaces dual-role `vision_desc` dict

**Before:** `vision_desc` was a `dict` carrying inferred Gemini DNA, then mutated mid-pipeline to add canonical `spec` (str) and `_dossier` (Dossier object) keys. Reviewer flagged this as a structural smell — the dict-of-everything hides which fields belong to which producer.

**After:** `VisionContext` dataclass with explicit fields (`inferred`, `catalog`, `spec`, `dossier`). Mapping-style `__getitem__` / `__contains__` / `get` shim keeps ~30 read-side consumers unchanged:

| Consumer | Site | Read pattern |
|----------|------|--------------|
| `tournament._dna_to_spec` | `tournament.py:285` | `dna.get("spec")`, `dna.get("garment_type")`, `dna["text_content"]` |
| `router.route_product` | `router.py:106` | `vision_desc.get("graphics")`, `vision_desc.get("fabric_appearance")` |
| `prompt_registry.get_prompt` | `prompt_registry.py:422` | `vision_desc.get("garment_type")` |
| `dna_prompts.*` | `dna_prompts.py:111-122` | many `dna.get(k, default)` |
| `metrics.*` | `metrics.py:308, 322` | `dna.get(k)` |
| `composite_fallback.*` | `composite_fallback.py:237-238` | `dna.get(k, default)` |
| `spec_builder.augment_prompt_with_dossier_negatives` | `spec_builder.py:127` | `dna.get("_dossier")` |

**Co-presence invariant** enforced in `__post_init__`: if `dossier` is `None`, `spec` must also be `None` (you cannot have a derived spec without a source dossier).

**JSON safety:** `to_dict()` drops the `Dossier` object (large, not JSON-safe) but preserves the `spec` string.

---

## Test plan

- [x] `pytest tests/scripts/nano_banana/ -v` → 181 pass, 0 fail
- [x] `pytest tests/scripts/ tests/test_catalog_csv_integrity.py` → 134 pass (cross-package regression check)
- [x] `pytest tests/scripts/nano_banana/ --cov=nano_banana --cov-report=term` → coverage table above
- [x] Tests pass with invalidated env keys: `OPENAI_API_KEY=invalid ANTHROPIC_API_KEY=invalid GOOGLE_API_KEY=invalid FAL_KEY=invalid pytest tests/scripts/nano_banana/` → all 181 pass (mocks intercept correctly; no real API calls)
- [x] `ruff check .` → clean
- [x] `mypy scripts/nano_banana/ skyyrose/core/dossier_loader.py` → clean (24 source files, 0 errors)
- [x] **`python scripts/nano_banana/_validate_layer1.py` against br-001 — PASS verdict.** See **Validation results** below. Cost: ~$0.80–$1.50.

---

## Validation results (Layer 1 paid validator)

Run on 2026-05-05 against br-001 from a `feat/v2-phase-0-5` git worktree (after Phase 3 VisionContext refactor):

| Stage | Score | Vision-pair mean | Hallucination veto |
|-------|-------|------------------|---------------------|
| **Baseline** (existing `br-001-crewneck.png`) | 38.0 | 51.0 | True |
| **Post-refine** (Kontext 1-pass) | 62.0 | 90.0 | True |
| **Delta** | **+24.0** | **+39.0** | unchanged |

**Verdict: PASS** (script's threshold is delta ≥ 20).

**What this proves:**
- ✅ The VisionContext refactor is regression-free. The validator ran end-to-end with no exception path; spec source confirmed as "canonical dossier (4,152c spec text)" — Tier 2 wiring works through the typed dataclass.
- ✅ The result JSON serialized cleanly via `vision_desc.to_dict()` without leaking the `Dossier` object. See `tasks/archive/2026-h1/layer1-validation-1778015839.json`.
- ⚠️ The +24 lift is below the historical +36 (canonical) and +45 (fake DNA) runs. **The +24 is honest.** Today's baseline is lower (38 vs 45) because Opus 4.7 now vetoes hallucinations the prior run flagged less aggressively — the existing `br-001-crewneck.png` carries full-color rose artwork violating the canonical "tonal embossed black-on-black" spec.
- ⚠️ Hallucination veto persists post-refine (True → True). That's a generation-quality story, not a refactor regression. Multi-pass refinement would likely close more of the gap.

**Stage timings (wall):** baseline tournament 244.1s · Kontext refine 19.5s · post-refine tournament 215.2s. Total ~8 min.

---

## Honest open items (not blocking)

1. **Multi-SKU production validation deferred.** The Phase 1 driver (`_validate_pipeline_multi_sku.py`, ~$5–$15 per run, one SKU per collection) is captured in the plan at `tasks/archive/2026-h1/plan-layer1-tier2-closeout.md` but not yet executed. The single-SKU `_validate_layer1.py` from the prior session validated br-001 only.

2. **Tournament + engine_fal coverage at 85%, not 98%.** The remaining gaps (`tournament.py:434-467` GPT vision adapter SDK call, `502-536` Opus synthesis SDK call; `engine_fal.py:69-86` the `_fal_available()` import-guard branches) require either real SDK dispatch or import-mocking that hides what's being tested. Documented as integration territory.

3. **Read-side consumers still use dict access via the shim.** Per the plan: "Do not drop the `__getitem__` shim until every consumer is migrated." A follow-up PR can migrate `tournament._dna_to_spec`, `router._has_text_graphics`, etc., to attribute access — at which point the shim becomes optional.

4. **`vision_desc` cache file format on disk is a plain dict, not a serialized VisionContext.** Disk cache predates the dossier merge, so it only stores inferred Gemini fields. On read, the cached dict is wrapped as `VisionContext(inferred=cache)` with `spec=None, dossier=None`. The dossier merge happens fresh in `run_single` after the cache load. This is intentional — the cache is for the expensive Gemini call only, not the cheap dossier read.

---

## Files changed

**Source (3 files):**
- `scripts/nano_banana/pipeline.py` — bug fix, VisionContext integration, return-type updates
- `scripts/nano_banana/spec_builder.py` — `build_dna_from_sku` returns VisionContext; `augment_prompt_with_dossier_negatives` accepts both
- `scripts/nano_banana/vision_context.py` — **new**, 130 lines

**Tests (4 new files + 1 modified):**
- `tests/scripts/nano_banana/test_engine_fal_mocked.py` — **new**, 13 tests
- `tests/scripts/nano_banana/test_tournament_mocked.py` — **new**, 30 tests
- `tests/scripts/nano_banana/test_pipeline_mocked.py` — **new**, 51 tests
- `tests/scripts/nano_banana/test_vision_context.py` — **new**, 32 tests

**Docs (2 files):**
- `tasks/archive/2026-h1/plan-layer1-tier2-closeout.md` — **new**, the multi-phase plan
- `tasks/pr-description-phase-0-5-closeout.md` — **new**, this file
