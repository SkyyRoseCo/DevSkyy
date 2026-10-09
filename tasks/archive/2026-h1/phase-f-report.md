# Phase F Audit Report — Render Pipeline Migration
**Date:** 2026-05-11  
**Scope:** Read-only audit + banner comments only. No functional changes. Uncommitted.

---

## Section 1: Scripts Audited — Count by Classification

Total image/3D/render scripts found in `scripts/`: **~55** (Python + shell).

| Bucket | Count | Scripts |
|--------|-------|---------|
| **MIGRATE** | 7 | `batch_flux_collections.py`, `pipeline_product_renders.py`, `smoke_b2_compositor.py`, `smoke_flux_br001.py`, `smoke_sg006.py`, `smoke_test_flux_br001.py`, `score_existing_renders.py` |
| **KEEP LEGACY** | 15 | `nano-banana-run.py` + all `scripts/nano_banana/*`, `tripo_dispatch.py`, `tripo_publish.py`, `tripo_spike_asset_extraction.py`, `rerun_stage3.py`, `audit_golden_coverage.py`, `audit_prompts.py`, `build_brand_centroid.py`, `capture_goldens.py`, `curate_centroid_test_set.py`, `generate_stage3_prompts.py`, `measure_brand_centroid_gate.py`, `regenerate_centroid_sidecars.py`, `seed_goldens_from_source.py`, `sync_brand_to_php.py` |
| **DELETE / CONSOLIDATE** | ~33 | All standalone 3D/image generation scripts below |

**DELETE / CONSOLIDATE detail** (standalone scripts, no `elite_studio` or `render_pipeline` import, ad-hoc or superseded):

- `batch_3d_generation.py`, `batch_enhance_clothing.py`, `composite_products.py`, `enhance_product_images.py`, `enhance_colors_for_3d.py`, `enhance_with_ai_pipeline.py`, `ecommerce_image_pro.py`, `gen3d_simple.py`, `generate_2d_25d_assets.py`, `generate_2d_25d_visualizations.py`, `generate_3d_color_accurate.py`, `generate_3d_direct.py`, `generate_3d_http.py`, `generate_3d_models_from_assets.py`, `generate_3d_models_official_sdk.py`, `generate_3d_models.py`, `generate_3d_trellis.py` (standalone Gradio client — superseded by `agents/trellis_agent.py`), `generate_ai_models_with_products.py`, `generate_clothing_3d_huggingface.py`, `generate_clothing_3d.py`, `generate_exact_3d_replicas.py`, `generate_premier_3d_models.py`, `generate_skyyrose_3d.py`, `generate_skyyrose_assets.py`, `gemini_lookbook.py`, `gemini_scene_gen.py`, `gradio_3d_app.py`, `meshy_3d_generator.py` (superseded by `agents/meshy_agent.py`), `meshy_webhook_server.py`, `process_all_products.py`, `process_priority_products.py`, `retexture_3d_models.py`, `texture_skyyrose_glb.py`, `run_compositor_pipeline.py` (standalone fal_client, no elite_studio), `run_scene_round_table.py` (uses `llm.round_table`, no `orchestration/threed_round_table.py`).

**Note:** The CI workflow `asset-generation.yml` calls `scripts/run_asset_pipeline.py` → `orchestration.asset_pipeline.ProductAssetPipeline`. That script uses neither `elite_studio` nor `render_pipeline` — it is a separate orchestration layer. Not classified above; needs its own review.

---

## Section 2: Files Modified

Banner comment added (one line each, no functional changes):

| File | Banner added |
|------|-------------|
| `scripts/batch_flux_collections.py` | line 1 |
| `scripts/pipeline_product_renders.py` | line 2 (after shebang) |
| `scripts/smoke_b2_compositor.py` | line 2 (after shebang) |
| `scripts/smoke_flux_br001.py` | line 1 |
| `scripts/smoke_sg006.py` | line 1 |
| `scripts/smoke_test_flux_br001.py` | line 1 |
| `scripts/score_existing_renders.py` | line 2 (after shebang) |

Banner text used:
```
# DEPRECATED: this script uses the legacy compositor. Prefer agents/render_pipeline (see docs/PIPELINE-ARCHITECTURE.md). Migration tracked in tasks/todo.md Phase F.
```

---

## Section 3: Migration Recommendations (Priority Order)

1. **`pipeline_product_renders.py`** — Production-grade PIPELINE 1 (product card + gallery renders). Calls `skyyrose.elite_studio` directly. This is the highest-value migration target: it generates the canonical product images that land in WooCommerce. Output dir today: `renders/gated/`. ADK pipeline writes to `agents/render_pipeline/output/<sku>-<view>-render.webp`. After migration, align output path or add a copy step to `renders/output/<sku>/`.

2. **`batch_flux_collections.py`** — Batch FLUX synthesis for Love Hurts + Signature collections. Imports `skyyrose.elite_studio.synthesis.flux_pipeline.render` directly. Currently the main multi-SKU batch runner. Should become a thin CLI wrapper calling `agents.render_pipeline.cli` (which already has `--sku` and `--collection` args).

3. **`score_existing_renders.py`** — QA scoring tool; reads `renders/` and calls `elite_studio` quality utilities. After `pipeline_product_renders.py` migrates its output path, this scorer needs to read from the new ADK output dir. Low effort — just update the `--renders-dir` default and import path.

4. **`smoke_b2_compositor.py`** — Real-API smoke test for the B2 6-stage compositor. Once the ADK pipeline has its own integration test (see `agents/render_pipeline/eval/`), this can be replaced by `make adk-eval-live`. Lowest urgency.

5. **`smoke_flux_br001.py`, `smoke_sg006.py`, `smoke_test_flux_br001.py`** — Three overlapping br-001/sg-006 smoke tests. All three call the same legacy `flux_pipeline.render`. Consolidate into one ADK eval fixture rather than migrating individually. `agents/render_pipeline/eval/` is the right home.

**Note on `rerun_stage3.py`:** Classified KEEP LEGACY. It targets three specific quarantined SKUs from a past prompt-construction bug. It is not an ongoing production path. Do not migrate; delete after confirming those SKUs have been re-rendered through the ADK pipeline.

---

## Section 4: WordPress Build Script Status

- **`wordpress-theme/skyyrose-flagship/scripts/build-css.js`** — Pure CSS minification. No image or 3D path references. Not affected by pipeline change.
- **`scripts/deploy-theme.sh`** — Transfers `wordpress-theme/skyyrose-flagship/` to skyyrose.co over SFTP. No reference to `renders/output/` or `agents/render_pipeline/output/`. Not affected.
- **`scripts/theme-build.sh`** — Orchestrates CSS + JS build + PHP lint. No render pipeline dependency. Not affected.

**Path alignment status:** The ADK pipeline writes to `agents/render_pipeline/output/<sku>-<view>-render.webp`. The legacy scripts write to `renders/output/<sku>/` and `renders/gated/`. WordPress product images are uploaded separately via `tripo_publish.py` (reads `renders/output/tripo/<sku>/`) and `run_asset_pipeline.py` → `orchestration.asset_pipeline`. Neither of those reads from the ADK output directory yet. **No WordPress build scripts are broken, but the ADK output path is not yet wired into any WooCommerce upload path.** That gap needs a copy/move step or an updated `tripo_publish.py`-equivalent for ADK outputs before Phase F is fully live.

---

## Section 5: Open Questions for the User

1. **ADK output path:** `agents/render_pipeline/output/` is currently a local scratch dir inside the agents package. Should it be moved to `renders/output/<sku>/` to match the legacy layout, or should downstream scripts (tripo_publish, score_existing_renders) be updated to read from the new path? Keeping two separate output roots will cause confusion during the transition.

2. **`run_asset_pipeline.py` + CI workflow:** `asset-generation.yml` calls this script, which uses `orchestration.asset_pipeline.ProductAssetPipeline` — not `agents.render_pipeline`. Is `ProductAssetPipeline` a wrapper around the ADK pipeline, or a separate legacy orchestration layer? If the latter, the CI workflow is also on the legacy path and needs tracking.

3. **`run_scene_round_table.py`:** This script uses `llm.round_table` (the LLM scene competition), not `orchestration/threed_round_table.py` (the new 3D provider abstraction). Should it be updated to call the new `ThreeDProvider.MESHY` / `ThreeDProvider.TRELLIS_2` paths, or is it intentionally a separate creative-generation tool?

4. **DELETE/CONSOLIDATE scripts:** ~33 standalone scripts are superseded by `agents/meshy_agent.py`, `agents/trellis_agent.py`, and `orchestration/threed_round_table.py`. Are any of these still used as reference implementations or one-off utilities the team wants to keep? If not, a single cleanup commit to move them to `scripts/archive/` would reduce noise significantly.

5. **`docs/PIPELINE-ARCHITECTURE.md`:** The banner comments reference this file. It does not currently exist. Should it be created as part of Phase F, or is there an existing doc (e.g., `agents/render_pipeline/DESIGN.md`) that should be linked instead?
