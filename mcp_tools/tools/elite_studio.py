"""Elite Studio MCP tools — thin surface over skyyrose/elite_studio/cli.py.

Exposes the LangGraph + Coordinator imagery pipeline as 5 MCP tools without
reimplementing any logic. Per CLAUDE.md / memory canon, Elite Studio is the
canonical hub for imagery: every paid engine (Nano-Banana, Tripo, Meshy,
FASHN, FLUX) is composed through it.

Tools:
    es_render             — single SKU produce via Coordinator
    es_batch              — batch produce via Coordinator.produce_batch
    es_validate_dossier   — hard-fail check for dossier existence
    es_cost_estimate      — pre-run cost projection for paid engines
    es_status             — generated/missing count + reader drift audit

Reuses (no rewrites):
    skyyrose.elite_studio.coordinator.Coordinator
    skyyrose.elite_studio.cli.build_team
    skyyrose.core.dossier_loader.{DossierMissingError, get_product_with_dossier}
    skyyrose.core.catalog_loader.read_catalog_rows
    skyyrose.elite_studio.budget.RunBudget
    skyyrose.elite_studio.config.validate_dossier_readers

FASHN gating: `with_tryon=True` raises NotImplementedError until D7 ships the
real FASHN integration. Plan rule (CLAUDE.md): never silently return input
image as a "successful" tryon. Existing tryon_agent.py:53 stub IS that lie —
we refuse to amplify it via MCP.
"""

from __future__ import annotations

import asyncio
from typing import Any, Literal

from pydantic import Field

from mcp_tools.api_client import _format_response
from mcp_tools.security import secure_tool
from mcp_tools.server import logger, mcp
from mcp_tools.types import BaseAgentInput

# Cost estimates per engine. Single source of truth, mirrors paid-api-stopgate
# rules. When you add a new paid engine here, also add it to
# .claude/hooks/paid-api-stopgate.sh RULES.
_COST_PER_SAMPLE_USD = {
    "fashn-tryon": 0.075,
    "fashn-bgremove": 0.025,
    "gemini-imagen": 0.04,
    "openai-dalle": 0.04,
    "flux-pro-kontext": 0.05,
    "tripo-multiview": 0.50,
    "meshy-text-to-3d": 0.10,
    "nano-banana": 0.02,
}

_DEFAULT_SAMPLES_PER_SKU = {
    "fashn-tryon": 16,
    "fashn-bgremove": 16,
    "nano-banana": 4,
    "flux-pro-kontext": 4,
    "gemini-imagen": 4,
    "tripo-multiview": 1,
    "meshy-text-to-3d": 1,
    "openai-dalle": 4,
}

# Valid render views — matches the conventions used by Coordinator.produce
# (which accepts arbitrary `view: str` but only these produce semantically
# correct output filenames). Centralized so RenderInput, BatchInput, and
# StatusInput share one source of truth.
_ValidView = Literal["front", "back", "side", "detail"]


def _is_sku_complete(sku: str, view: str = "front") -> bool:
    """Predicate matching the Coordinator's output-file naming convention.

    Mirrors coordinator.py:249 — `f"{sku}-model-{view}-gemini.jpg"`. Threading
    `view` through eliminates the previous bug where non-front views always
    counted as "missing", causing batch jobs to re-render and burn paid credit.
    """
    from skyyrose.elite_studio.config import OUTPUT_DIR

    return (OUTPUT_DIR / sku / f"{sku}-model-{view}-gemini.jpg").exists()


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class RenderInput(BaseAgentInput):
    sku: str = Field(..., min_length=1, max_length=64, description="Product SKU (e.g., 'br-001')")
    view: _ValidView = Field(default="front", description="View slug")
    style: Literal["flat_lay", "ghost_mannequin"] = Field(
        default="flat_lay", description="Render style"
    )
    with_compositor: bool = Field(
        default=False, description="Run scene compositor after generation."
    )
    with_tryon: bool = Field(
        default=False,
        description="Run FASHN virtual tryon — ships in D7. Raises until then.",
    )
    confirm: bool = Field(
        default=False,
        description="Must be True to dispatch paid generation. False = dry-run cost preview.",
    )


class BatchInput(BaseAgentInput):
    skus: list[str] | None = Field(
        default=None,
        description="Explicit SKU list. Omit to use all_skus / remaining_only.",
        max_length=200,
    )
    all_skus: bool = Field(default=False, description="Process every SKU in catalog.")
    remaining_only: bool = Field(
        default=False, description="Only SKUs missing a generated image for the given view."
    )
    view: _ValidView = Field(default="front")
    confirm: bool = Field(default=False)


class ValidateDossierInput(BaseAgentInput):
    sku: str = Field(..., min_length=1, max_length=64)


class CostEstimateInput(BaseAgentInput):
    skus: list[str] = Field(..., min_length=1, max_length=500, description="SKUs to estimate.")
    engine: Literal[
        "fashn-tryon",
        "fashn-bgremove",
        "gemini-imagen",
        "openai-dalle",
        "flux-pro-kontext",
        "tripo-multiview",
        "meshy-text-to-3d",
        "nano-banana",
    ] = Field(..., description="Engine to estimate against.")
    samples_per_sku: int | None = Field(
        default=None,
        ge=1,
        le=64,
        description="Override default samples-per-SKU for this engine.",
    )


class StatusInput(BaseAgentInput):
    audit_readers: bool = Field(
        default=True,
        description="Run validate_dossier_readers() cross-check across catalog readers.",
    )
    view: _ValidView = Field(
        default="front",
        description="Which view to check completeness against (front | back | side | detail).",
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_skus(input: BatchInput) -> list[str]:
    """Resolve the SKU list for batch processing without dispatching.

    Resolution order: explicit `skus` > `all_skus` > `remaining_only` > error.
    Threads `input.view` through `_is_sku_complete` so non-front views don't
    silently re-render already-completed assets (CR finding 2026-05-22).
    """
    from skyyrose.elite_studio.utils import discover_all_skus  # local: heavy import chain

    if input.skus:
        return input.skus
    if input.all_skus:
        return discover_all_skus()
    if input.remaining_only:
        all_skus = discover_all_skus()
        return [s for s in all_skus if not _is_sku_complete(s, input.view)]
    raise ValueError("Must specify skus, all_skus=True, or remaining_only=True")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(
    name="es_render",
    annotations={
        "title": "Elite Studio render — single SKU produce",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
@secure_tool("es_render")
async def es_render(params: RenderInput) -> str:
    """Render a single SKU via Coordinator.produce — Elite Studio canonical path.

    Composes vision → generator → quality → compositor agents. Pre-dispatch
    cost gate via RunBudget. Dossier hard-fail via DossierMissingError (never
    silently falls back to CSV branding_spec).

    FASHN tryon: passing `with_tryon=True` raises NotImplementedError until
    D7 ships the real integration. The current tryon_agent.py stub returns
    input unchanged — exposing it as a "successful tryon" would be the silent
    fallback CLAUDE.md prohibits.

    Args:
        params.sku: product SKU
        params.view: front | back | side | detail (default "front")
        params.style: flat_lay | ghost_mannequin
        params.with_compositor: scene compositing post-generation
        params.with_tryon: FASHN tryon — raises until D7
        params.confirm: must be True to dispatch (False = dry-run cost preview)
    """
    if params.with_tryon:
        # D7 shipped the FASHN client + tryon_agent rewrite (no more silent
        # stub). End-to-end wiring through es_render still requires an image
        # upload pipeline (local render → public URL → FASHN). Call
        # TryOnAgent.execute_tryon directly with pre-hosted URLs until then.
        raise NotImplementedError(
            "FASHN client + tryon_agent shipped in D7 — call "
            "TryOnAgent.execute_tryon directly with public HTTPS image URLs. "
            "MCP-level integration pending the image-upload pipeline."
        )

    # Validate dossier first (hard-fail before any paid generation).
    # Two failure modes: SKU not in catalog (KeyError) vs catalog has SKU
    # but no dossier file (DossierMissingError). Both must hard-fail.
    from skyyrose.core.dossier_loader import (
        DossierMissingError,
        get_product_with_dossier,
    )

    try:
        get_product_with_dossier(params.sku)
    except KeyError as exc:
        raise RuntimeError(
            f"SKU {params.sku!r} not in catalog: {exc}. Add the SKU to "
            "wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv first."
        ) from exc
    except DossierMissingError as exc:
        raise RuntimeError(
            f"dossier missing for {params.sku}: {exc}. Authored dossiers are "
            "required — CSV branding_spec is not a fallback."
        ) from exc

    if not params.confirm:
        report = {
            "dry_run": True,
            "sku": params.sku,
            "view": params.view,
            "style": params.style,
            "dossier_ok": True,
            "estimated_engine": "nano-banana",
            "estimated_cost_usd": _COST_PER_SAMPLE_USD["nano-banana"]
            * _DEFAULT_SAMPLES_PER_SKU["nano-banana"],
            "note": "set confirm=True to dispatch real generation",
        }
        return _format_response(report, params.response_format, "Render plan (dry-run)")

    # Real dispatch via Coordinator (runs in worker thread — heavy compute)
    from skyyrose.elite_studio.cli import build_team

    def _run() -> Any:
        team = build_team(with_compositor=params.with_compositor)
        return team.produce(params.sku, params.view)

    result = await asyncio.to_thread(_run)
    logger.info("es_render dispatched", extra={"sku": params.sku, "view": params.view})

    report = {
        "ok": getattr(result, "status", "unknown") == "success",
        "sku": params.sku,
        "view": params.view,
        "status": getattr(result, "status", "unknown"),
        "output_path": str(getattr(result, "output_path", "") or ""),
        "error": getattr(result, "error", None),
        "qc_score": (
            getattr(result.quality, "score", None) if getattr(result, "quality", None) else None
        ),
    }
    return _format_response(report, params.response_format, "Render result")


@mcp.tool(
    name="es_batch",
    annotations={
        "title": "Elite Studio batch — Coordinator.produce_batch wrapper",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
@secure_tool("es_batch")
async def es_batch(params: BatchInput) -> str:
    """Run Coordinator.produce_batch across multiple SKUs.

    Resolves SKU list (explicit > all_skus > remaining_only), validates each
    SKU has a dossier, then dispatches. Bails on first dossier miss — does
    not silently skip.

    Args:
        params.skus: explicit list, OR
        params.all_skus: True, OR
        params.remaining_only: True (missing-image only)
        params.view: render view
        params.confirm: must be True to dispatch
    """
    skus = _resolve_skus(params)
    if not skus:
        # Empty filter is always a dry-run condition (nothing to dispatch).
        report = {
            "dry_run": True,
            "resolved_skus": [],
            "note": "no SKUs matched filter",
        }
        return _format_response(report, params.response_format, "Batch — empty filter")

    # Validate every dossier upfront
    from skyyrose.core.dossier_loader import DossierMissingError, get_product_with_dossier

    missing_dossiers: list[str] = []
    for sku in skus:
        try:
            get_product_with_dossier(sku)
        except DossierMissingError:
            missing_dossiers.append(sku)
        except KeyError:
            missing_dossiers.append(f"{sku} (not in catalog)")

    if missing_dossiers:
        report = {
            "ok": False,
            "blocked_at": "dossier_validation",
            "missing_dossiers": missing_dossiers,
            "resolved_skus": skus,
        }
        return _format_response(report, params.response_format, "Batch BLOCKED — missing dossiers")

    if not params.confirm:
        est_cost = (
            _COST_PER_SAMPLE_USD["nano-banana"]
            * _DEFAULT_SAMPLES_PER_SKU["nano-banana"]
            * len(skus)
        )
        report = {
            "dry_run": True,
            "resolved_skus": skus,
            "sku_count": len(skus),
            "estimated_cost_usd": round(est_cost, 2),
            "note": "set confirm=True to dispatch real generation",
        }
        return _format_response(report, params.response_format, "Batch plan (dry-run)")

    from skyyrose.elite_studio.cli import build_team

    def _run() -> Any:
        team = build_team()
        return team.produce_batch(skus=skus, view=params.view, skip_existing=params.remaining_only)

    results = await asyncio.to_thread(_run)
    # Destructure list[ProductionResult] into per-SKU success/failure so the
    # caller can retry ONLY failed SKUs without double-spending on successes
    # (CR finding 2026-05-22 — was truncating to str(results)[:1500]).
    successes: list[str] = []
    failures: list[dict[str, str]] = []
    for r in results or []:
        sku = getattr(r, "sku", "?")
        status = getattr(r, "status", "unknown")
        if status == "success":
            successes.append(sku)
        else:
            failures.append({"sku": sku, "status": status, "error": getattr(r, "error", "") or ""})

    report = {
        "ok": not failures,
        "sku_count": len(skus),
        "view": params.view,
        "success_count": len(successes),
        "failure_count": len(failures),
        "successes": successes,
        "failures": failures,
    }
    return _format_response(
        report, params.response_format, "Batch complete" if not failures else "Batch partial"
    )


@mcp.tool(
    name="es_validate_dossier",
    annotations={
        "title": "Validate dossier presence for a SKU (hard-fail check)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
@secure_tool("es_validate_dossier")
async def es_validate_dossier(params: ValidateDossierInput) -> str:
    """Check dossier presence for a SKU. Raises DossierMissingError if missing.

    Per CLAUDE.md feedback: CSV branding_spec is NOT a fallback for a missing
    dossier. This tool surfaces the hard-fail explicitly so an orchestrator
    agent can refuse paid generation before dispatch.
    """
    from skyyrose.core.dossier_loader import DossierMissingError, get_product_with_dossier

    try:
        product = get_product_with_dossier(params.sku)
    except KeyError as exc:
        report = {"ok": False, "sku": params.sku, "error": f"SKU not in catalog: {exc}"}
        return _format_response(report, params.response_format, "Dossier check FAILED")
    except DossierMissingError as exc:
        report = {
            "ok": False,
            "sku": params.sku,
            "error": str(exc),
            "remediation": "Author a dossier .md file under data/dossiers/ for this SKU.",
        }
        return _format_response(report, params.response_format, "Dossier check FAILED")
    except Exception:
        # Catch-all to avoid leaking internal paths or stack traces to MCP
        # clients (YAML parse errors, PermissionError, etc.). Full detail in
        # the server log under correlation ID.
        logger.exception("es_validate_dossier_unexpected_error", extra={"sku": params.sku})
        report = {
            "ok": False,
            "sku": params.sku,
            "error": "dossier validation error — check server logs (see correlation ID)",
        }
        return _format_response(report, params.response_format, "Dossier check FAILED")

    report = {
        "ok": True,
        "sku": params.sku,
        "dossier_slug": product.get("dossier_slug", ""),
        "title": product.get("title", ""),
        "collection": product.get("collection", ""),
    }
    return _format_response(report, params.response_format, "Dossier OK")


@mcp.tool(
    name="es_cost_estimate",
    annotations={
        "title": "Pre-run cost projection for paid Elite Studio engines",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
@secure_tool("es_cost_estimate")
async def es_cost_estimate(params: CostEstimateInput) -> str:
    """Project the USD cost of running a batch through a specific engine.

    Estimates use the single source of truth (_COST_PER_SAMPLE_USD), which
    mirrors the paid-api-stopgate hook rules. When a new paid engine is added
    in either place, update both.

    Args:
        params.skus: list of SKUs
        params.engine: which engine to project against
        params.samples_per_sku: override default samples (e.g., custom batch size)

    Returns:
        Per-SKU cost + total + budget recommendation.
    """
    if params.engine not in _COST_PER_SAMPLE_USD:
        raise ValueError(f"unknown engine: {params.engine}")

    samples = params.samples_per_sku or _DEFAULT_SAMPLES_PER_SKU[params.engine]
    per_sample = _COST_PER_SAMPLE_USD[params.engine]
    per_sku = per_sample * samples
    total = per_sku * len(params.skus)

    report = {
        "engine": params.engine,
        "sku_count": len(params.skus),
        "samples_per_sku": samples,
        "per_sample_usd": per_sample,
        "per_sku_usd": round(per_sku, 4),
        "total_usd": round(total, 2),
        "recommended_budget_ceiling_usd": round(total * 1.2, 2),  # 20% buffer
        "skus": params.skus[:20] + (["..."] if len(params.skus) > 20 else []),
    }
    return _format_response(report, params.response_format, f"Estimate: ${round(total, 2)}")


@mcp.tool(
    name="es_status",
    annotations={
        "title": "Elite Studio status — generated/missing + reader drift audit",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
@secure_tool("es_status")
async def es_status(params: StatusInput) -> str:
    """Report image-generation progress + optional dossier-reader drift audit.

    The reader audit cross-checks `skyyrose.core.catalog_loader` against
    `skyyrose.elite_studio.catalog` (via validate_dossier_readers). Drift
    means the two paths return different dossier data — silent correctness
    bug.
    """
    from skyyrose.elite_studio.utils import discover_all_skus

    all_skus = discover_all_skus()
    generated: list[str] = []
    missing: list[str] = []
    for sku in all_skus:
        # Use the shared _is_sku_complete helper so the view is respected
        # (CR finding 2026-05-22 — was hardcoding "front").
        (generated if _is_sku_complete(sku, params.view) else missing).append(sku)

    report: dict[str, Any] = {
        "view_checked": params.view,
        "total_skus": len(all_skus),
        "generated_count": len(generated),
        "remaining_count": len(missing),
        "generated_pct": (round(100.0 * len(generated) / len(all_skus), 1) if all_skus else 0.0),
        "remaining_skus": missing[:50],
    }

    if params.audit_readers:
        try:
            from skyyrose.elite_studio.config import validate_dossier_readers

            await asyncio.to_thread(validate_dossier_readers)
            report["reader_audit"] = {"ok": True, "readers_checked": 2}
        except Exception as exc:
            report["reader_audit"] = {
                "ok": False,
                "error": str(exc),
                "alert": "DOSSIER READER DRIFT — investigate before next paid run",
            }

    return _format_response(report, params.response_format, "Elite Studio status")
