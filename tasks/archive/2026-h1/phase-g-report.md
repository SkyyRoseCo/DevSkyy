# Phase G — Documentation Update Report

**Date:** 2026-05-11
**Scope:** Docs-only update for three features merged to main: ADK render pipeline, MeshyAgent in ThreeDRoundTable, TRELLIS.2 via TrellisAgent.

---

## Files Updated

### docs/CODEMAPS/backend.md
Added `meshy_agent.py`, `trellis_agent.py`, and `render_pipeline/` subtree to the agents/ directory listing.

### docs/CODEMAPS/INDEX.md
Bumped `Last Updated` from 2026-02-19 to 2026-05-11.

### docs/ARCHITECTURE.md
Updated `Last Updated` from 2026-02-22 to 2026-05-11. Added surgical entries for `meshy_agent.py`, `trellis_agent.py` (with double-gate annotation), and `render_pipeline/` under the agents/ layer section.

### docs/3D_GENERATION_PIPELINE.md
Prepended a "Provider Tournament (Current)" section above the existing 4-stage pipeline describing Tripo3D, Meshy (external API, geo=82/tex=82, 300 s), and TRELLIS.2 (local GPU, opt-in, geo=98/tex=95, 600 s).

### docs/HUGGINGFACE_3D_INTEGRATION.md
Added a callout at the top clarifying that TRELLIS.2 is NOT a HF Space — it runs locally via conda subprocess and cannot be called through HuggingFace3DClient.

### docs/NANO_BANANA.md
Updated `Last updated` date. Added a note explaining that `agents/render_pipeline/` is a higher-level ADK SequentialAgent that orchestrates on top of Nano Banana's generation layer; Nano Banana remains the generation engine.

### .wolf/cerebrum.md
Appended a `[2026-05-11]` Key Learnings entry covering: ThreeDProvider.MESHY and TRELLIS_2 enum values; double-gate behavior for TRELLIS_2 (enable_trellis flag + conda env availability check); graceful-disable semantics; ADK render pipeline 9-step structure and venv.

### .wolf/anatomy.md
Added entries for:
- `agents/meshy_agent.py`
- `agents/trellis_agent.py`
- `agents/render_pipeline/agent.py` (new section `## agents/render_pipeline/`)
- `tests/test_trellis_agent.py`

---

## Files Skipped (with reason)

| File | Reason |
|------|--------|
| `docs/TODOS.md` | grep confirmed zero items matching render-pipeline, meshy, trellis, threed_round — nothing to mark done |
| `docs/SKYYROSE_WORDPRESS_PLAN.md` | grep confirmed no 3D pipeline section; only two incidental "3D" references unrelated to these providers |
| `docs/PIPELINE-ARCHITECTURE.md` | Documents three workflow-level pipelines (product cards / editorial / brand copy) — has no provider list; adding MESHY/TRELLIS_2 here would break the doc's structural logic |

---

## No Code Files Modified

Zero changes to `.py`, `.ts`, `.tsx`, `.php`, or any non-doc file. `tasks/todo.md` and `tasks/phase-e-manifest.md` untouched.
