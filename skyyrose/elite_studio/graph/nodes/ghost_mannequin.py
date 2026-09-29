"""
Ghost mannequin graph nodes — Phase B2 pipeline stages.

three_d_node, preflight_node, ghost_mannequin_composite_node,
plus the collar-detection helper _is_collar_garment and its keyword set.
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..state import EliteStudioState
from ._shared import _THREE_D_EST_COST_USD, run_sync

logger = logging.getLogger(__name__)


def _shim():
    """Return the public ``graph.nodes`` shim module for dynamic attribute lookup.

    Tests patch ``skyyrose.elite_studio.graph.nodes._is_collar_garment``;
    calling it through ``_shim()._is_collar_garment`` ensures the patch
    resolves at call time. See layer1._shim docstring for the rationale
    and circular-import-avoidance pattern. ``ThreeDAgent`` is instantiated
    directly here (not via _shim) because no test patches it.
    """
    from .. import nodes as _nodes_shim

    return _nodes_shim


# ---------------------------------------------------------------------------
# Collar detection
# ---------------------------------------------------------------------------

_COLLAR_KEYWORDS = {"hoodie", "jacket", "crewneck", "bomber", "windbreaker", "sherpa"}


def _is_collar_garment(sku: str) -> bool:
    """Return True for garments that need neck-in composite."""
    try:
        from ...catalog import Catalog

        cat = Catalog.load()
        name = cat.require(sku).name.lower()
        return any(kw in name for kw in _COLLAR_KEYWORDS)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Node functions
# ---------------------------------------------------------------------------


def three_d_node(state: EliteStudioState) -> dict:
    """Legendary 3D generation node.

    Generates a 3D .glb replica and renders front/back/ghost shots.
    Updates the state with the 3D-rendered paths.

    Sync wrapper around an async agent — matches the convention used by every
    other node in this file. The shared `run_sync` helper handles both
    no-running-loop (sync `graph.invoke()`) and running-loop (`graph.ainvoke()`)
    cases via `nest_asyncio`. Async safety inside the agent itself is enforced
    by `asyncio.to_thread` wrappers around `subprocess.run` (Blender) and
    `shutil.move` (cross-device renders) — see three_d_agent.py.
    """
    from ...agents.three_d_agent import ThreeDAgent
    from ...agents.vision_agent import _reference_path
    from ...budget import BudgetExceededError

    sku = state["sku"]

    # Reference image: techflat from state or vision-agent lookup
    try:
        ref_path = _reference_path(sku, "front")
        supplied = state.get("reference_path")
        if supplied and Path(supplied).resolve() != Path(ref_path):
            raise ValueError("State reference does not match the registry front binding")
    except (KeyError, ValueError, OSError) as exc:
        return {"status": "error", "error": str(exc), "failed_step": "3d_generation"}

    # Budget guard — round-table tournament (Meshy + Tripo + TRELLIS local +
    # AniGen) can dispatch up to 4 providers in parallel; estimate the
    # ceiling at $0.50 to cover the worst case before any provider fires.
    budget = state.get("budget")
    if budget is not None and hasattr(budget, "ensure_within_budget"):
        try:
            budget.ensure_within_budget(_THREE_D_EST_COST_USD, stage="three_d")
        except BudgetExceededError as exc:
            return {
                "status": "error",
                "error": f"budget exceeded before 3D generation: {exc}",
                "failed_step": "3d_generation",
            }

    # The dossier loaded inside generate_replica is now the source of truth for
    # branding spec; enrichment_prompt and vision_result are no longer fed
    # into the RAS prompt (they were thin and could drift from the dossier).
    agent = ThreeDAgent()
    replica_result = run_sync(agent.generate_replica(sku, ref_path))

    if budget is not None and hasattr(budget, "spend") and replica_result.get("success"):
        budget.spend(_THREE_D_EST_COST_USD, stage="three_d")

    if not replica_result["success"]:
        return {
            "status": "error",
            "error": replica_result.get("error", "3D Generation failed"),
            "failed_step": "3d_generation",
        }

    # Map the renders to the state paths
    renders = replica_result["renders"]

    # Convert to standard GenerationResult for compatibility
    gen_result = agent.generate_result_bridge(replica_result, state["view"])

    return {
        "generation_result": gen_result,
        "ghost_mannequin_front_path": renders.get("front", ""),
        "ghost_mannequin_back_path": renders.get("back", ""),
        "three_d_model_path": replica_result["glb_path"],
        "three_d_fidelity_score": replica_result["fidelity_score"],
    }


def preflight_node(state: EliteStudioState) -> dict:
    """Dual-vision pre-flight: verify reference image matches registry spec.

    Only runs for ghost_mannequin style — flat_lay skips (returns empty dict).
    """
    if state.get("style", "flat_lay") != "ghost_mannequin":
        return {}

    sku = state["sku"]

    try:
        from skyyrose.core.product import get_product, render_reference

        product = get_product(sku)
        expected_garment = f"{product['name']} — {product['dossier']['garment_type_lock']}"
        view = state.get("view", "front")
        ref_path = render_reference(product, view)["path"]
        supplied = state.get("reference_path")
        if supplied and Path(supplied).resolve() != Path(ref_path):
            raise ValueError("State reference does not match the registry SKU/view binding")

    except Exception as exc:
        return {
            "status": "error",
            "error": f"Preflight catalog load failed: {exc}",
            "failed_step": "preflight",
        }

    from ...agents.vision_agent import DualVisionGate

    gate = DualVisionGate()
    result = run_sync(
        gate.verify_reference(
            image_path=ref_path,
            sku=sku,
            expected_garment=expected_garment,
            view=view,
        )
    )

    if not result.passed:
        logger.warning("[Preflight] BLOCKED %s: %s", sku, result.blocking_reason)
        return {
            "preflight_result": result,
            "status": "error",
            "error": f"Preflight blocked: {result.blocking_reason}",
            "failed_step": "preflight",
        }

    return {"preflight_result": result}


def ghost_mannequin_composite_node(state: EliteStudioState) -> dict:
    """Neck-in composite for collar garments (hoodies, jackets, crewnecks).

    For collar garments: crops the top 20% of the back render and pastes
    it behind the front render's neckline area to create the hollow-man effect.
    For non-collar garments: saves the front render as-is (no neck-in).
    """
    import time as _time

    from PIL import Image

    from ...models import GhostMannequinCompositeResult

    start = _time.monotonic()
    sku = state["sku"]
    front_path = state.get("ghost_mannequin_front_path", "")
    back_path = state.get("ghost_mannequin_back_path", "")

    if not front_path:
        gen = state.get("generation_result")
        front_path = gen.output_path if gen and gen.success else ""

    if not front_path:
        return {
            "ghost_mannequin_composite_result": GhostMannequinCompositeResult(
                success=False, error="No front render available for composite"
            )
        }

    collar = _shim()._is_collar_garment(sku)
    out_dir = __import__("pathlib").Path(front_path).parent
    out_path = str(out_dir / f"{sku}-front-ghost-composite.webp")

    if not collar or not back_path or not __import__("pathlib").Path(back_path).exists():
        # Non-collar or no back render: pass front through unchanged
        __import__("shutil").copy2(front_path, out_path)
        timings = dict(state.get("stage_timings", {}))
        timings["ghost_composite"] = round(_time.monotonic() - start, 2)
        return {
            "ghost_mannequin_composite_result": GhostMannequinCompositeResult(
                success=True,
                output_path=out_path,
                front_path=front_path,
                back_path=back_path,
                neck_in_applied=False,
            ),
            "stage_timings": timings,
        }

    # Neck-in composite: paste top 20% of back render behind front render neckline
    try:
        front_img = Image.open(front_path).convert("RGBA")
        back_img = Image.open(back_path).convert("RGBA").resize(front_img.size)

        w, h = front_img.size
        neck_fraction = 0.20
        neck_strip = back_img.crop((0, 0, w, int(h * neck_fraction)))

        composite = Image.new("RGBA", front_img.size, (255, 255, 255, 255))
        composite.paste(neck_strip, (0, 0))
        composite = Image.alpha_composite(composite, front_img)
        composite.convert("RGB").save(out_path, "WEBP", quality=92)
    except Exception as exc:
        return {
            "ghost_mannequin_composite_result": GhostMannequinCompositeResult(
                success=False, error=f"Composite failed: {exc}"
            )
        }

    timings = dict(state.get("stage_timings", {}))
    timings["ghost_composite"] = round(_time.monotonic() - start, 2)
    return {
        "ghost_mannequin_composite_result": GhostMannequinCompositeResult(
            success=True,
            output_path=out_path,
            front_path=front_path,
            back_path=back_path,
            neck_in_applied=True,
        ),
        "stage_timings": timings,
    }
