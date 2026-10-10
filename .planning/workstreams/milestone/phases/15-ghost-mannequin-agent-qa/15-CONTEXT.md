# Phase 15: Ghost Mannequin Agent + QA - Context

**Gathered:** 2026-05-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a LangGraph agent in Elite Studio that turns a single in-scope garment SKU into a validated, white-background ghost-mannequin front shot — without crashing, overspending, or silently shipping a broken image.

Scope is **single-SKU** (`--sku <id>` entry point). Batch dispatch + WooCommerce upload belong to Phase 18. CSV write-back belongs to Phase 17.

The agent must enforce the SkyyRose **96+ replica bar**: per-metric vetoes against the SKU's product flatlay (silhouette, color ΔE, pattern, CLIP semantic) and against the techflat (logo placement) — not blended into one vibe-pass score.

</domain>

<decisions>
## Implementation Decisions

### Ground Truth & QA Inputs

- **D-01:** **Product flatlay (`source-photo` from `data/product-bundles/<dir>/manifest.json`) is the QA ground truth.** Score every generated image against the flatlay for silhouette, color, pattern, fabric drape, and CLIP semantic similarity. The flatlay represents the actual physical garment — replicate it, don't invent.
- **D-02:** **Techflat (`techflat-front` from manifest) is the logo placement reference, not the QA ground truth.** Score the logo region (per `branding_spec` from CSV col 16) against the techflat for position/scale/rotation. Logo-region scoring is a separate gate from flatlay scoring — they cannot blend.
- **D-03:** **Per-metric vetoes, not blended scores.** Any single metric below its floor forces `recommendation = regenerate`, regardless of overall vibe-pass. Floors:
  - Silhouette IoU ≥ 0.96
  - Color ΔE (LAB, garment region) ≤ 2.0
  - CLIP semantic similarity ≥ 0.85 (against flatlay)
  - Pattern preservation: qualitative pass via Claude Sonnet QA
  - Logo position/scale: ≤ 5% drift from techflat reference
  - Corner-pixel purity (QA-04): all four corners within 5 RGB units of (255, 255, 255)

### Generation Pipeline (2D-to-3D for every SKU)

- **D-04:** **Every SKU goes through the 2D-to-3D pipeline.** No direct 2D path. Stages:
  1. Read flatlay from manifest
  2. Image-to-3D digitization → `.glb` mesh (cached per SKU, reused on retries)
  3. Headless Blender render of the `.glb` → scaffold image
  4. Gemini RAS synthesis (Nano Banana 2 / `gemini-2.5-flash-image`) using scaffold + flatlay + techflat as references
  5. Per-metric QA scoring
- **D-05:** **`.glb` artifacts are durable, cached per SKU.** Digitize once, version-pin, reuse for all attempts/retries/future regens. Re-digitization on retry burns budget with zero quality benefit. `.glb` cache lives at `renders/3d/cache/{sku}.glb`.

### 3D Digitization Vendor

- **D-06:** **Tripo (image-to-3D) is the default vendor.** Reasons:
  - User has paid Tripo credits → marginal cost ≈ $0
  - Image-to-3D client already wrapped at `ai_3d/providers/tripo.py:226` (`type: "image_to_model"`, `BASE_URL = "https://api.tripo3d.ai/v2/openapi"`)
  - `get_balance` probe is free — bake into dry-run mode
- **D-07:** **Meshy is the wired fallback.** Phase 16's `MeshyClient` (imported in `skyyrose/elite_studio/agents/three_d_agent.py:24`) stays available. Auto-swap to Meshy if Tripo `.glb` is unusable for Blender headless render (too high-poly, malformed UVs, missing textures). Manual swap if Tripo credits exhaust.
- **D-08:** **Tripo region check required before Phase 15 first paid run.** Per project memory, `.ai` and `.com` are separate regions with separate keys. Verify `TRIPO3D_API_KEY` in `.env.hf` matches the `.ai` endpoint baked into the provider client.

### Generation Strategy: Hybrid + Jersey Rule

- **D-09:** **Tier-1 ensemble of 3 candidates for ALL SKUs.** Three Gemini RAS synthesis runs in parallel (mutated seeds/prompt-temp), all scored, highest-scoring candidate selected. Math: with per-metric pass rate `p = 0.7` per single shot, ensemble-of-3 lifts overall pass rate from 70% → 97.3%.
- **D-10:** **Per-veto-fail behavior splits by garment type:**
  - **Jersey SKUs** (br-003, br-003-giants, br-003-oakland, br-003-white, br-008, br-009, br-010, br-011, br-012 = 9 SKUs): on veto fail, cascade to GPT-Image-1 (single shot) → Ideogram v3 (single shot) → flag to `failures.json`. Cascade earns its keep on jerseys because Tier 2/3 have measurably better text fidelity for stitched numbers/letters.
  - **Non-jersey SKUs** (19 SKUs): on veto fail, single mutated retry at Tier 1 → flag to `failures.json`. No cascade — Tier 2/3 are not measurably better than Tier 1 for non-text failure modes; cascade collapses to "more expensive retry."
- **D-11:** **Cascade is bounded.** Jersey path = max 1 GPT-Image-1 attempt + 1 Ideogram attempt after Tier-1 ensemble exhausts. Non-jersey path = max 1 mutated retry. No infinite loops.

### Failure Handling

- **D-12:** **Accessories silently skipped at runtime.** sg-007 (Signature Beanie), lh-005 (The Fannie), and any SKU not resolved by `garment_type_lock` (empty value) skip with reason logged to `failures.json`. No exception raised. No abort. (Implements GM-06.)
- **D-13:** **`failures.json` schema: append + structured.** Each run appends entries with `{sku, attempt_number, timestamp, stage, failure_class (safety/retryable/non-retryable/skipped), error_message, score_breakdown}`. History preserved across runs for audit. Same SKU re-run dedupes by overwriting the latest attempt entry, not appending duplicates.
- **D-14:** **Retry class separation.** Retryable (HTTP 429, transient 5xx, network blip): exponential backoff inside the agent. Non-retryable (Gemini safety block, content filter, wrong modality, file-write failure): immediately flag to `failures.json` without retry. (Implements QA-02.)

### Spend Cap

- **D-15:** **Hard spend cap mechanism: `--max-spend` CLI flag + `GHOST_MAX_SPEND_USD` env var fallback + config default.**
  - Default: $25 hard cap per Phase 15 single-SKU testing run (covers ~40 retries on one SKU under worst-case Meshy fallback at $0.50/digitization).
  - Cap check: estimate cost of next API call before dispatching. If projected total > cap, halt before the cap-crossing call and exit with clear message: amount spent, amount remaining, last successful SKU.
  - Phase 18 batch run gets a separate $30 cap defined when that phase plans.

### Dry-Run Mode (STOP-AND-SHOW)

- **D-16:** **`--dry-run` produces a full cost manifest with zero API calls.**
  - Lists target SKU(s), resolved bundle directory, garment type, projected per-image API + per-tier fallback cost, total projected cost.
  - Calls `Tripo.get_balance()` (free) — verifies credits ≥ projected cost, exits non-zero if insufficient.
  - Confirms `.glb` cache hit/miss per SKU (avoids surprise digitization charge on retries).
  - This is the STOP-AND-SHOW gate per project canon. No paid run proceeds without operator review of the dry-run output.

### Telemetry & Audit Trail

- **D-17:** **Per-attempt JSONL audit log.** Every generation attempt (success or veto-fail) writes one line to `renders/ghost-mannequin/audit/{run_timestamp}.jsonl` containing `{sku, attempt_number, vendor, model, prompt_template_id, score_breakdown_per_metric, vetoes_failed, cost, latency_ms}`. Phase 18 batch run consumes this to replace estimated pass rates with measured data — closes the theory-vs-measurement gap.

### Output Path & Format

- **D-18:** **Output: `renders/ghost-mannequin/{sku}-ghost-front.webp`, 1200×1200 px WebP.** (Implements GM-05 verbatim.) `front_model_image` CSV column update is Phase 17 territory — Phase 15 only writes the file.

### What's NOT in Phase 15

- **D-19:** **HF datasets + SDXL LoRA training are out of scope.** Gemini Nano Banana 2 doesn't accept LoRAs; the LoRA infrastructure described in the user-shared conversation feeds a separate non-product imagery path (lookbook, editorial, collection-page atmosphere). Phase 15 stays focused on ghost mannequin product photography. LoRA work is pre-v1.3 backlog.
- **D-20:** **No CSV write-back, no WooCommerce upload, no batch dispatch.** Those belong to Phase 17 (REV-01..04) and Phase 18 (UPLOAD-01).

### Claude's Discretion

- **Prompt template architecture per garment type** (jersey, hoodie, crewneck, tee, shorts, joggers, jacket, set): planner picks file layout — `skyyrose/elite_studio/prompts/ghost_mannequin/<garment_type>.py` registry vs single dispatch table. Decision low-impact; either pattern works.
- **`.glb` cache eviction policy**: planner decides whether to keep cache forever (small disk cost — ~1-5 MB per `.glb` × 28 SKUs = under 150 MB) or implement TTL-based eviction. Default to "keep forever" unless storage constraint surfaces.
- **Blender render parameter tuning**: lighting, camera position, FOV. Use ThreeDAgent's existing render config from Phase 16 as starting point. Planner tunes only if Blender output unusable as Gemini RAS scaffold.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Specification (locked requirements)
- `.planning/ROADMAP.md` §"Phase 15: Ghost Mannequin Agent + QA" — 5 success criteria + dependency on Phase 14
- `.planning/REQUIREMENTS.md` §GM-01..06, §QA-01, QA-02, QA-04 — all in scope (QA-03 dropped 2026-04-25)
- `.planning/PROJECT.md` — milestone v1.2 framing, palette canon

### Upstream Phases (dependencies)
- `.planning/phases/14-catalog-foundation/14-01-SUMMARY.md` — `garment_type_lock` column added to `skyyrose-catalog.csv` (column 22), 22-column schema, accessory-row handling
- `.planning/phases/14-catalog-foundation/14-02-SUMMARY.md` — catalog adapter wiring across pipelines
- `.planning/phases/14-catalog-foundation/14-03-SUMMARY.md` — preflight audit script (INFRA-07)
- `.planning/phases/16-3d-replica-architect-purge/16-SUMMARY.md` — ThreeDAgent + Meshy wiring + Gemini RAS synthesis pattern; this is the architectural precedent Phase 15 builds on

### Source Code (existing infrastructure to extend)
- `skyyrose/elite_studio/agents/three_d_agent.py` (355 lines) — Phase 16 ADK SuperAgent. Phase 15 ghost mannequin agent reuses its Tripo/Meshy + Blender + Gemini RAS pipeline as a foundation; does NOT reimplement
- `skyyrose/elite_studio/graph/builder.py` + `nodes.py` + `state.py` + `edges.py` + `runner.py` — LangGraph wiring layer. Phase 15 adds a `ghost_mannequin_node` to this graph
- `skyyrose/elite_studio/agents/quality_agent.py` — existing QA agent (Claude Sonnet). Phase 15 extends with per-metric structured-veto verdict logic, NOT replaces
- `skyyrose/elite_studio/coordinator.py` — legacy orchestrator (still active alongside LangGraph)
- `skyyrose/elite_studio/models.py` — frozen dataclasses (`ProductData`, `QualityVerification`, `PreflightResult`, `DualAgentResult`, `CompositorResult`, `TryOnResult`). Phase 15 adds `GhostMannequinResult` to this module
- `imagery/visual_comparison.py` — SSIM (30%) + color histogram (25%) + perceptual hash (20%) + CLIP cosine (25%, openai/clip-vit-base-patch32) scoring engine. Already has tiered thresholds 0.22/0.28 as log-only messages — Phase 15 promotes them to hard vetoes
- `ai_3d/providers/tripo.py` (line 226 — `_create_image_to_3d_task`) — Tripo image-to-3D client; default 3D vendor for Phase 15
- `ai_3d/providers/meshy.py` — Meshy image-to-3D client; fallback vendor wired from Phase 16

### Asset Sources
- `data/product-bundles/<dir>/manifest.json` — per-SKU asset registry. Schema: `{sku, name, dirname, collection, files: {techflat-front, techflat-back, source-photo, logo-ref, spec}}`. Phase 15 reads `source-photo` (flatlay = ground truth) and `techflat-front` (logo placement reference)
- `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` (33 SKUs, 28 garments + 2 accessories + 3 jersey color variants — TBD reconciliation): `sku`, `garment_type_lock` (col 22), `branding_spec` (col 16), `render_source_override` (col 18), `front_model_image` (col 8 = output target)

### Project Conventions
- `CLAUDE.md` (root) — STOP-AND-SHOW protocol for paid API calls (mandatory before any Tripo/Meshy/Gemini paid run); Context7-first for any external library; production-grade code quality (no TODOs, no placeholders, no half-baked code)
- `.wolf/cerebrum.md` — Do-Not-Repeat list, project conventions
- `~/.claude/projects/-Users-theceo-DevSkyy/memory/feedback_no_silent_fallback.md` — 3D pipeline must hard-fail; CSV `branding_spec` is not a silent fallback
- `~/.claude/projects/-Users-theceo-DevSkyy/memory/feedback_tripo_multi_account.md` — `.ai` and `.com` are separate Tripo regions with separate keys; verify before dispatch

### User-Shared Research (this session)
- claude.ai share `f3e6d1b2-ffb4-42ae-af8e-56b22f7cc43b` — 96+ fidelity pipeline architecture; pasted into discussion. Key arguments captured in decisions D-01 through D-11. Referenced files in that conversation (`docs/GFA_96_PIPELINE_SPEC_v2.md`, `imagery/hf_dataset_publisher.py`, `imagery/lora_trainer_hf.py`) **were never saved to repo** — do not look for them. The reasoning is canonical; the artifacts are not

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`ThreeDAgent`** (`skyyrose/elite_studio/agents/three_d_agent.py`) — Phase 16 SuperAgent already implements 2D-to-3D + Blender + Gemini RAS pipeline. Phase 15 ghost mannequin agent wraps it with ensemble + per-metric vetoes + jersey cascade logic. Saves ~200+ lines of net-new code
- **`MeshyClient`** (`ai_3d/providers/meshy.py`) — wired Meshy image-to-3D client; available as Tripo fallback
- **`TripoClient.image_to_3d`** (`ai_3d/providers/tripo.py:226`, `_create_image_to_3d_task`) — wraps `https://api.tripo3d.ai/v2/openapi` with `type: "image_to_model"`. Already validated input model (`ImageGenerationRequest` with file-exists + ≤10 MB checks). Phase 15 uses this directly via a thin agent wrapper
- **`imagery/visual_comparison.py`** — multi-metric scoring engine (SSIM, color histogram, perceptual hash, CLIP cosine). Already has tiered thresholds at 0.22 and 0.28 as log-only messages. Phase 15 promotes selected thresholds to hard vetoes
- **`PreflightResult`** (in `models.py`) — dual-vision verification (agent A and agent B both verify the reference image matches the SKU before any generation). Phase 15 reuses for pre-generation gate
- **`logo_fingerprint`** field on `ProductData` — per-SKU branding fingerprint already populated. Phase 15 uses for logo-placement scoring
- **`GarmentFidelityAgent`** (referenced in `renders/__main__.py` per shared convo) — confirmed missing from `renders/pipeline.py` (CRAWL_NOT_FOUND in shared convo's Exa probe). Treat as legacy/dead reference; do not import

### Established Patterns

- **LangGraph orchestration via `graph/` directory split** (builder/nodes/state/edges/runner) — not a single `graph.py`. New ghost mannequin node attaches via `builder.py`, state shape extends in `state.py`, conditional edges in `edges.py`
- **ADK SuperAgent promotion** (Phase 16 pattern) — `ThreeDAgent` inherits from `CreativeAgent` for telemetry + Back Data capture. Phase 15 ghost mannequin agent should follow the same pattern for observability
- **Cost-ceiling constants in `graph/nodes.py`** (`_GENERATOR_EST_COST_USD = 0.04`, `_THREE_D_EST_COST_USD = 0.50`, `_ADK_RENDER_EST_COST_USD = 0.20`) — extend with `_GHOST_MANNEQUIN_EST_COST_USD` for Phase 15 cap math
- **Garment-type prompt routing** (per GM-03) — established by Phase 14's `garment_type_lock` column. Phase 15 templates dispatch on this value
- **STOP-AND-SHOW gate at dispatch layer** (per `tripo_agent.py:13-14` notes) — agents dispatch unconditionally; callers obtain confirmation. Phase 15 dry-run mode + cost manifest is the STOP-AND-SHOW

### Integration Points

- **LangGraph builder** at `skyyrose/elite_studio/graph/builder.py` — register `ghost_mannequin_node`
- **State extension** at `skyyrose/elite_studio/graph/state.py` — add ghost-mannequin fields to graph state
- **Models module** at `skyyrose/elite_studio/models.py` — add `GhostMannequinResult` frozen dataclass
- **CLI entry point** at `skyyrose/elite_studio/agents/ghost_mannequin_agent.py` — `python -m skyyrose.elite_studio.agents.ghost_mannequin_agent --sku <id> [--dry-run] [--max-spend N]`
- **Output directory** at `renders/ghost-mannequin/` — create on first run; `audit/` subdir for JSONL telemetry; `failures.json` at root
- **`.glb` cache directory** at `renders/3d/cache/{sku}.glb` — shared with Phase 16 ThreeDAgent's existing 3D output convention

</code_context>

<specifics>
## Specific Ideas

- **96+ replica bar from user-shared convo:** the framing shift from "looks correct" to "matches source photo" is the operative change. 96 against the source flatlay is a reachable target; 96 against an abstract concept of "right ghost mannequin" is not solvable by any pipeline. Score against source.
- **"FLATLAY-MESHY"** (user emphasis): when the user said "EVERYTHING SHOULD BE 2D TO 3D," the input to the digitization step is the flatlay, NOT the techflat. Techflat is for logo placement only. Misreading this would feed Tripo a vector logo layout and produce a wrong `.glb`.
- **Tripo > Meshy on credit economics, not on technical merit for our pipeline.** User has paid Tripo credits → marginal cost of Tripo ≈ $0; Meshy requires per-call payment. For our single-flatlay → scaffold-only workflow (Gemini RAS overwrites textures), Tripo's surface-detail edge is technically wasted, but at $0 marginal it's free unused fidelity.

</specifics>

<deferred>
## Deferred Ideas

- **HF dataset publisher + SDXL LoRA training pipeline** (from user-shared convo) — for non-product imagery (lookbook, editorial, collection-page atmosphere). Pre-v1.3 backlog. Not Phase 15 scope.
- **Per-garment-type 3D vendor routing** (Tripo for jerseys, Meshy for everything else) — only relevant if Tripo `.glb` consistently fails Blender scaffold quality on jerseys. Phase 15 ships with Tripo-default + Meshy-fallback; per-type routing is a Phase 18 backlog item if measured failures justify it.
- **TRELLIS local 3D digitization** — zero per-image cost but requires dedicated GPU. If a render box (RTX 4090+) is provisioned later, swapping in TRELLIS would drop per-SKU cost from ~$0.50 (Meshy) to ~$0 (just Gemini RAS). Bookmark for v1.3.
- **Per-attempt prompt mutation strategies** — Phase 15 uses seed-mutation + temperature-mutation for ensemble. Beyond that (semantic prompt rewriting, style-transfer prompt augmentation) belongs to a future "prompt optimization" phase.
- **Frontend review UI** — CLI approval (Phase 17) is sufficient for 30-product catalog. UI deferred per REQUIREMENTS.md "Out of Scope."
- **Multi-angle generation (back, side, 3/4)** — only front techflats confirmed in current bundles. Back generation deferred to v1.3 per `REQUIREMENTS.md` "Future Requirements" GM-BACK-01/02.
- **Human-gated cascade approval** (require operator OK before Tier 2 GPT-Image-1 spend) — considered but rejected. Cap-based gate ($25) is sufficient given small per-attempt cost ($0.042-$0.050) and the cascade only triggers on jersey vetoes.

</deferred>

---

*Phase: 15-Ghost-Mannequin-Agent-QA*
*Context gathered: 2026-05-13*
