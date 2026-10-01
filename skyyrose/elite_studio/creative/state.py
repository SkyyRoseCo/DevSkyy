"""
CreativeOperationState — shared state for the Creative Operations Hub graph.

Handles all 14 creative intents with unified state structure.
Each node populates its result field and sets status/error accordingly.

"""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import TypedDict


class CreativeIntent(StrEnum):
    """All supported creative operation intents."""

    PRODUCT_RENDER = "product-render"
    THREE_D_MODEL = "3d-model"
    SOCIAL_PACK = "social-pack"
    PRODUCT_COPY = "product-copy"
    CHARACTER_SHEET = "character-sheet"
    SCENE_COMPOSITE = "scene-composite"
    VIRTUAL_TRYON = "virtual-tryon"
    FULL_PRODUCT_LAUNCH = "full-product-launch"
    DESIGN_IDEATION = "design-ideation"
    MOCKUP = "mockup"
    COLLECTION_PLAN = "collection-plan"
    TECH_PACK = "tech-pack"
    MOODBOARD = "moodboard"
    COLORWAY_EXPLORE = "colorway-explore"
    TRIPO_GENERATE = "tripo-generate"


class CreativeOperationState(TypedDict, total=False):
    """Shared state flowing through the Creative Operations Hub graph.

    Required fields are set at invocation. Optional result fields
    are populated by individual nodes as the operation progresses.
    """

    # --- Inputs (set at invocation) ---
    operation_id: str
    intent: str
    tenant_id: str
    sku: str
    params: dict

    # --- Assembled context (set by entry_node) ---
    fashion_context: dict | None

    # --- Stage results (set by specialized nodes) ---
    render_result: dict | None
    model_3d_result: dict | None
    social_result: dict | None
    copy_result: dict | None
    character_result: dict | None
    composite_result: dict | None
    tryon_result: dict | None
    design_result: dict | None
    tech_pack_result: dict | None
    collection_plan_result: dict | None
    tripo_result: dict | None

    # --- Control flow ---
    status: str  # "running", "success", "error"
    error: str

    # --- Metrics ---
    stage_timings: dict[str, float]
    token_usage: dict[str, int]
    cost_usd: float


def create_initial_state(
    intent: str,
    params: dict,
    sku: str = "",
    tenant_id: str = "",
) -> CreativeOperationState:
    """Create the initial state for a creative operation."""
    return CreativeOperationState(
        operation_id=str(uuid.uuid4()),
        intent=intent,
        tenant_id=tenant_id,
        sku=sku,
        params=params,
        fashion_context=None,
        render_result=None,
        model_3d_result=None,
        social_result=None,
        copy_result=None,
        character_result=None,
        composite_result=None,
        tryon_result=None,
        design_result=None,
        tech_pack_result=None,
        collection_plan_result=None,
        tripo_result=None,
        status="running",
        error="",
        stage_timings={},
        token_usage={},
        cost_usd=0.0,
    )
