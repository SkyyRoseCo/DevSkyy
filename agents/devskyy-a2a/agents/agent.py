# ruff: noqa
"""DevSkyy A2A Coordinator
========================

Thin ADK + A2A dispatch layer that routes external A2A requests to the
canonical DevSkyy SuperAgent layer (``agents/<domain>_agent.py``).

Responsibilities (per ``tasks/adk-a2a-DESIGN_SPEC.md``):

* Validate inbound requests (SKU shape, retired-SKU rejection, budget cap).
* Dispatch to the SuperAgent that owns the domain — never call paid provider
  APIs (FASHN, Tripo, Meshy) directly. The SuperAgents own preflight, retry,
  and cost gating.
* Return structured success/error envelopes; never leak Python tracebacks.
* Expose an ``AgentCard`` so external A2A callers can discover skills.

Design notes:

* SuperAgent imports are **deferred to inside each skill function** so the
  agent module loads even when the parent DevSkyy venv is unreachable.
* No ``google.auth.default()`` at import time — Vertex AI auth is only
  required when actually deployed to Cloud Run / Agent Engine, not in
  prototype mode or local ``make playground``.
* Cost-gate is a static lookup (skill → estimated USD). The SuperAgents
  enforce the real provider-level cost ceiling.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import LongRunningFunctionTool
from google.genai import types

# Make the parent DevSkyy repo importable so skills can dispatch to
# SuperAgents at agents/<domain>_agent.py without re-installing the world.
# This is the prototype path; production should `pip install -e ..` instead.
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# =============================================================================
# Cost gate + validation — enforced before any SuperAgent import
# =============================================================================

# Conservative per-skill cost estimates in USD. Real cost is enforced
# downstream by the SuperAgent (FASHN preflight, Tripo retry budget, etc.).
_COST_ESTIMATES_USD: dict[str, float] = {
    "generate_3d_model": 0.40,  # Tripo or Meshy via the round-table tournament
    "product_description": 0.05,  # Anthropic via creative_agent
    "qa_render": 0.08,  # Claude + Gemini judge dual-pass
    "brand_check": 0.04,  # Anthropic
    "list_products": 0.0,  # Local CSV read
    "semantic_search": 0.0,  # Local SentenceTransformers embeddings
}

# SKUs intentionally retired (per CLAUDE.md / memory). Calls naming these
# return a structured error rather than reach the SuperAgent layer.
_RETIRED_SKUS: frozenset[str] = frozenset(
    {
        "lh-001",
        "sg-004",
        "sg-008",
        "sg-010",
        "sg-d01",
        "sg-d02",
        "sg-d03",
        "sg-d04",
        "br-d01",
        "br-d02",
        "br-d03",
        "br-d04",
    }
)

# The retired tagline that must never be emitted by any creative skill.
_RETIRED_TAGLINE: str = "Where Love Meets Luxury"


def _check_budget(skill: str, max_cost_usd: float | None) -> dict[str, Any] | None:
    """Return an error dict if the estimated cost exceeds the cap, else None.

    Args:
        skill: One of the keys in ``_COST_ESTIMATES_USD``.
        max_cost_usd: Caller-supplied cap. ``None`` means no cap (only valid
            for free skills; paid skills require an explicit cap).

    Returns:
        Structured error envelope, or ``None`` if the call may proceed.
    """
    estimate = _COST_ESTIMATES_USD.get(skill, 0.0)
    if estimate > 0.0 and max_cost_usd is None:
        return {
            "ok": False,
            "error": "missing_budget",
            "skill": skill,
            "estimate_usd": estimate,
            "message": (
                f"Skill '{skill}' costs ~${estimate:.2f} per call; " "caller must pass max_cost_usd"
            ),
        }
    if max_cost_usd is not None and estimate > max_cost_usd:
        return {
            "ok": False,
            "error": "budget_exceeded",
            "skill": skill,
            "estimate_usd": estimate,
            "max_cost_usd": max_cost_usd,
            "message": (f"Estimated cost ${estimate:.2f} exceeds cap ${max_cost_usd:.2f}"),
        }
    return None


def _validate_sku(sku: str) -> dict[str, Any] | None:
    """Reject empty or retired SKUs. Return error envelope or None."""
    if not sku or not isinstance(sku, str):
        return {
            "ok": False,
            "error": "invalid_sku",
            "sku": sku,
            "message": "SKU must be a non-empty string",
        }
    normalized = sku.strip().lower()
    if normalized in _RETIRED_SKUS:
        return {
            "ok": False,
            "error": "retired_sku",
            "sku": sku,
            "message": (
                f"SKU '{sku}' is retired and not valid for new operations. "
                "See MEMORY.md for the retired-SKU list."
            ),
        }
    return None


def _skill_unavailable(skill: str, reason: str) -> dict[str, Any]:
    """Standard envelope when a SuperAgent dispatch can't be performed."""
    return {
        "ok": False,
        "error": "skill_unavailable",
        "skill": skill,
        "reason": reason,
        "message": (
            f"Skill '{skill}' could not be dispatched. "
            "Likely the SuperAgent venv is not reachable from the A2A "
            "coordinator's runtime."
        ),
    }


# =============================================================================
# Skills — each dispatches to the canonical SuperAgent layer
# =============================================================================


def list_products(collection: str = "", in_stock_only: bool = True) -> dict[str, Any]:
    """List products from the canonical SkyyRose catalog (read-only, no cost).

    Args:
        collection: Filter to one of ``black-rose``, ``love-hurts``,
            ``signature``, ``kids-capsule``. Empty string returns all.
        in_stock_only: Only return rows where ``published == "1"``.

    Returns:
        ``{"ok": True, "products": [...], "count": int, "collection": str}``
        or a structured error envelope.
    """
    skill = "list_products"
    budget_err = _check_budget(skill, max_cost_usd=0.0)
    if budget_err:
        return budget_err
    try:
        from skyyrose.core.catalog_loader import read_catalog_rows  # type: ignore[import-not-found]
    except ImportError as exc:
        return _skill_unavailable(skill, str(exc))

    try:
        rows = list(read_catalog_rows())
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error": "catalog_read_failed",
            "skill": skill,
            "message": str(exc),
        }

    if collection:
        rows = [r for r in rows if r.get("collection") == collection]
    if in_stock_only:
        rows = [r for r in rows if str(r.get("published", "0")) == "1"]
    return {
        "ok": True,
        "skill": skill,
        "products": rows,
        "count": len(rows),
        "collection": collection or "all",
    }


def semantic_search(query: str, top_k: int = 5) -> dict[str, Any]:
    """Semantic search over the catalog + dossiers (local embeddings, no cost).

    Args:
        query: Free-text query, e.g. "dark gothic crewneck".
        top_k: How many matches to return (1–20).

    Returns:
        ``{"ok": True, "matches": [...], "query": str}`` or an error envelope.
    """
    skill = "semantic_search"
    if not query:
        return {"ok": False, "error": "missing_query", "skill": skill}
    top_k = max(1, min(int(top_k), 20))
    budget_err = _check_budget(skill, max_cost_usd=0.0)
    if budget_err:
        return budget_err
    try:
        from orchestration.catalog_retriever import (
            CatalogRetriever,  # type: ignore[import-not-found]
        )
    except ImportError as exc:
        return _skill_unavailable(skill, str(exc))

    try:
        retriever = CatalogRetriever()
        matches = retriever.search(query=query, top_k=top_k)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error": "retrieval_failed",
            "skill": skill,
            "message": str(exc),
        }
    return {
        "ok": True,
        "skill": skill,
        "query": query,
        "matches": matches,
        "top_k": top_k,
    }


def product_description(
    sku: str,
    audience: str = "luxury",
    max_words: int = 60,
    max_cost_usd: float = 0.10,
) -> dict[str, Any]:
    """Generate a dossier-grounded product description via CommerceAgent.

    Args:
        sku: Active SKU from the canonical catalog.
        audience: Audience tag — ``luxury``, ``streetwear``, ``kids``.
        max_words: Length cap.
        max_cost_usd: Required budget cap. Skill rejects if estimate > cap.

    Returns:
        ``{"ok": True, "sku": str, "description": str, "tokens_used": int}``
        or a structured error envelope.
    """
    skill = "product_description"
    sku_err = _validate_sku(sku)
    if sku_err:
        return sku_err
    budget_err = _check_budget(skill, max_cost_usd)
    if budget_err:
        return budget_err
    try:
        from agents.commerce_agent import CommerceAgent  # type: ignore[import-not-found]
    except ImportError as exc:
        return _skill_unavailable(skill, str(exc))

    try:
        agent = CommerceAgent()
        result = agent.describe_product(sku=sku, audience=audience, max_words=int(max_words))
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error": "commerce_agent_failed",
            "skill": skill,
            "sku": sku,
            "message": str(exc),
        }

    description = result.get("description", "") if isinstance(result, dict) else str(result)
    if _RETIRED_TAGLINE.lower() in description.lower():
        return {
            "ok": False,
            "error": "retired_tagline_emitted",
            "skill": skill,
            "sku": sku,
            "message": (
                f"CommerceAgent returned a description containing the retired "
                f"tagline '{_RETIRED_TAGLINE}'. Rejected per brand policy."
            ),
        }
    return {
        "ok": True,
        "skill": skill,
        "sku": sku,
        "audience": audience,
        "description": description,
        "tokens_used": result.get("tokens_used", 0) if isinstance(result, dict) else 0,
    }


def brand_check(asset_text: str, collection: str = "") -> dict[str, Any]:
    """Check copy against SkyyRose brand rules via creative_agent.

    Args:
        asset_text: The text to validate (product copy, ad headline, etc.).
        collection: Optional collection scope for tone-specific rules.

    Returns:
        ``{"ok": True, "compliant": bool, "violations": [...], ...}``.
    """
    skill = "brand_check"
    if not asset_text:
        return {"ok": False, "error": "missing_text", "skill": skill}
    budget_err = _check_budget(skill, max_cost_usd=0.10)
    if budget_err:
        return budget_err

    # Cheap pre-check that doesn't require importing creative_agent: the
    # retired tagline is a hard structural ban.
    violations: list[str] = []
    if _RETIRED_TAGLINE.lower() in asset_text.lower():
        violations.append(
            f"Retired tagline detected: '{_RETIRED_TAGLINE}'. "
            "No tagline is authorised."
        )

    try:
        from agents.creative_agent import CreativeAgent  # type: ignore[import-not-found]
    except ImportError as exc:
        # Even without CreativeAgent, return the structural verdict.
        return {
            "ok": True,
            "skill": skill,
            "compliant": len(violations) == 0,
            "violations": violations,
            "deep_check_unavailable": str(exc),
        }

    try:
        agent = CreativeAgent()
        deep = agent.check_brand_compliance(text=asset_text, collection=collection)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": True,
            "skill": skill,
            "compliant": len(violations) == 0,
            "violations": violations,
            "deep_check_failed": str(exc),
        }

    if isinstance(deep, dict):
        violations.extend(deep.get("violations", []))
    return {
        "ok": True,
        "skill": skill,
        "compliant": len(violations) == 0,
        "violations": violations,
        "collection": collection,
    }


def generate_3d_model(
    sku: str,
    quality: str = "standard",
    max_cost_usd: float = 1.00,
) -> dict[str, Any]:
    """Generate a 3D model for a SKU via the threed_round_table tournament.

    Args:
        sku: Active SKU. The round-table internally picks Tripo/Meshy/HF.
        quality: ``standard`` or ``production``.
        max_cost_usd: Required budget cap.

    Returns:
        ``{"ok": True, "asset_url": str, "provider": str, "cost_usd": float}``.
    """
    skill = "generate_3d_model"
    sku_err = _validate_sku(sku)
    if sku_err:
        return sku_err
    budget_err = _check_budget(skill, max_cost_usd)
    if budget_err:
        return budget_err
    try:
        from orchestration.threed_round_table import (
            ThreedRoundTable,  # type: ignore[import-not-found]
        )
    except ImportError as exc:
        return _skill_unavailable(skill, str(exc))

    try:
        table = ThreedRoundTable()
        result = table.run(sku=sku, quality=quality, max_cost_usd=max_cost_usd)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error": "round_table_failed",
            "skill": skill,
            "sku": sku,
            "message": str(exc),
        }

    return {
        "ok": True,
        "skill": skill,
        "sku": sku,
        **(result if isinstance(result, dict) else {"result": result}),
    }


def qa_render(image_path: str, sku: str, max_cost_usd: float = 0.20) -> dict[str, Any]:
    """Run QA on a generated render: SSIM vs. golden + dual-judge LLM verdict.

    This is a long-running tool — judge calls take 5–15 s.

    Args:
        image_path: Local path to the rendered image (webp/jpg/png).
        sku: SKU the render is for; used to find ``assets/golden/{sku}/reference.jpg``.
        max_cost_usd: Required budget cap.

    Returns:
        ``{"ok": True, "verdict": "pass"|"fail", "ssim": float,
        "judge_scores": {...}}``.
    """
    skill = "qa_render"
    sku_err = _validate_sku(sku)
    if sku_err:
        return sku_err
    budget_err = _check_budget(skill, max_cost_usd)
    if budget_err:
        return budget_err

    image_path_obj = Path(image_path)
    if not image_path_obj.is_file():
        return {
            "ok": False,
            "error": "image_not_found",
            "skill": skill,
            "image_path": str(image_path_obj),
        }

    try:
        from skyyrose.elite_studio.agents.quality_agent import (
            QualityAgent,  # type: ignore[import-not-found]
        )
    except ImportError as exc:
        return _skill_unavailable(skill, str(exc))

    try:
        agent = QualityAgent()
        verdict = agent.score_render(image_path=str(image_path_obj), sku=sku)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error": "quality_agent_failed",
            "skill": skill,
            "sku": sku,
            "message": str(exc),
        }
    return {
        "ok": True,
        "skill": skill,
        "sku": sku,
        **(verdict if isinstance(verdict, dict) else {"verdict": str(verdict)}),
    }


# =============================================================================
# Agent + App + AgentCard
# =============================================================================


_INSTRUCTION = """\
You are the DevSkyy A2A coordinator for the SkyyRose luxury fashion platform.

You dispatch external requests to specialized SuperAgents. You DO NOT call
paid provider APIs (FASHN, Tripo, Meshy, OpenAI, Anthropic) directly — the
SuperAgents own preflight, retry, and cost gating.

Brand rules (hard-blocks):
- No tagline is authorised — never emit one.
- "Where Love Meets Luxury" is RETIRED — never emit it; flag if seen.
- Active collections: Black Rose, Love Hurts, Signature, Kids Capsule.
- Retired SKUs (reject silently): lh-001, sg-004, sg-008, sg-010,
  sg-d01..sg-d04, br-d01..br-d04.

For any paid skill, the caller MUST pass max_cost_usd. Your tools enforce
this — never bypass.

When a tool returns an error envelope, return it to the caller verbatim.
Never fabricate a successful response when a tool fails.
"""


root_agent = Agent(
    name="devskyy_a2a_coordinator",
    model=Gemini(
        model="gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "DevSkyy A2A coordinator — dispatches to SkyyRose SuperAgents "
        "(commerce, creative, imagery, 3D) over the A2A protocol."
    ),
    instruction=_INSTRUCTION,
    tools=[
        list_products,
        semantic_search,
        product_description,
        brand_check,
        generate_3d_model,
        LongRunningFunctionTool(func=qa_render),
    ],
)


app = App(
    root_agent=root_agent,
    name="devskyy_a2a",
)


# A2A AgentCard — exposed at /.well-known/agent.json when the agent is
# wrapped with `google.adk.a2a.utils.agent_to_a2a()` for HTTP serving.
def get_agent_card(base_url: str = "http://localhost:8080") -> AgentCard:
    """Build the AgentCard advertising this agent's skills.

    Args:
        base_url: The public URL where the A2A server is reachable. Caller
            should pass the production URL when deployed (e.g. the Cloud Run
            service URL); leave default for local dev.
    """
    return AgentCard(
        name="devskyy-a2a",
        description=(
            "DevSkyy A2A coordinator: catalog read, semantic search, dossier-"
            "grounded product copy, brand-rule checking, 3D asset generation, "
            "and render QA — all dispatched to canonical SkyyRose SuperAgents."
        ),
        url=f"{base_url}/a2a",
        version="0.1.0",
        protocol_version="0.3.0",
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["application/json"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[
            AgentSkill(
                id="list_products",
                name="List products",
                description=(
                    "Read-only listing of SkyyRose products from the canonical "
                    "catalog. Free; no budget required."
                ),
                tags=["catalog", "read-only", "free"],
                examples=["List all signature collection products"],
            ),
            AgentSkill(
                id="semantic_search",
                name="Semantic catalog search",
                description=(
                    "Free-text similarity search over catalog + dossiers using "
                    "local SentenceTransformers embeddings. Free; no budget."
                ),
                tags=["catalog", "rag", "free"],
                examples=["Find dark crewnecks for an Oakland streetwear drop"],
            ),
            AgentSkill(
                id="product_description",
                name="Generate product description",
                description=(
                    "Dossier-grounded product copy via CommerceAgent. Caller "
                    "MUST pass max_cost_usd. Estimated $0.05 per call."
                ),
                tags=["copy", "creative", "paid"],
                examples=[
                    "Write a 60-word luxury description for SKU br-001",
                ],
            ),
            AgentSkill(
                id="brand_check",
                name="Brand-rule compliance check",
                description=(
                    "Validate copy against SkyyRose brand rules (palette, "
                    "tagline, collection iconography). Hard-blocks the retired "
                    "tagline 'Where Love Meets Luxury'."
                ),
                tags=["creative", "brand", "paid"],
                examples=[
                    "Check this product copy: 'The Black Rose Crewneck is armor...'",
                ],
            ),
            AgentSkill(
                id="generate_3d_model",
                name="Generate 3D model",
                description=(
                    "Dispatch to threed_round_table tournament (Tripo + Meshy "
                    "+ HuggingFace 3D) for SKU. Estimated $0.40 per call."
                ),
                tags=["imagery", "3d", "paid"],
                examples=["Generate a production-quality 3D model for br-005"],
            ),
            AgentSkill(
                id="qa_render",
                name="QA a render",
                description=(
                    "SSIM vs. golden reference + dual-judge (Claude + Gemini) "
                    "verdict for a generated image. Long-running."
                ),
                tags=["imagery", "qa", "paid", "long-running"],
                examples=[
                    "QA the render at renders/output/br-001-front.webp for br-001",
                ],
            ),
        ],
    )


__all__ = [
    "app",
    "root_agent",
    "get_agent_card",
    "list_products",
    "semantic_search",
    "product_description",
    "brand_check",
    "generate_3d_model",
    "qa_render",
]
