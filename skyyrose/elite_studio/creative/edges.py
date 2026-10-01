"""
Creative Operations Hub routing edges.

Routing logic for the unified creative operations LangGraph.

"""

from __future__ import annotations

from .state import CreativeIntent

# Node name constants
ENTRY = "entry"
PRODUCT_RENDER = "product_render"
THREE_D_MODEL = "three_d_model"
SOCIAL_PACK = "social_pack"
PRODUCT_COPY = "product_copy"
CHARACTER = "character"
SCENE_COMPOSITE = "scene_composite"
DESIGN_IDEATION = "design_ideation"
COLLECTION_PLAN = "collection_plan"
TRIPO_GENERATE = "tripo_generate"
FINALIZE = "finalize"

# Intent → node name routing map
_INTENT_TO_NODE: dict[str, str] = {
    CreativeIntent.PRODUCT_RENDER: PRODUCT_RENDER,
    CreativeIntent.THREE_D_MODEL: THREE_D_MODEL,
    CreativeIntent.SOCIAL_PACK: SOCIAL_PACK,
    CreativeIntent.PRODUCT_COPY: PRODUCT_COPY,
    CreativeIntent.CHARACTER_SHEET: CHARACTER,
    CreativeIntent.SCENE_COMPOSITE: SCENE_COMPOSITE,
    CreativeIntent.VIRTUAL_TRYON: PRODUCT_RENDER,  # tryon uses render pipeline
    CreativeIntent.FULL_PRODUCT_LAUNCH: PRODUCT_RENDER,  # starts with render
    CreativeIntent.DESIGN_IDEATION: DESIGN_IDEATION,
    CreativeIntent.MOCKUP: DESIGN_IDEATION,  # mockup is a design sub-intent
    CreativeIntent.COLLECTION_PLAN: COLLECTION_PLAN,
    CreativeIntent.TECH_PACK: DESIGN_IDEATION,  # tech pack via design agent
    CreativeIntent.MOODBOARD: DESIGN_IDEATION,  # moodboard via design agent
    CreativeIntent.COLORWAY_EXPLORE: DESIGN_IDEATION,  # colorway via design agent
    CreativeIntent.TRIPO_GENERATE: TRIPO_GENERATE,
}


def route_intent(state: dict) -> str:
    """Route to the correct node based on the operation intent.

    Called after entry_node. Returns a node name constant.
    If state has error, route directly to finalize.
    """
    if state.get("status") == "error":
        return FINALIZE

    intent = state.get("intent", "")
    return _INTENT_TO_NODE.get(intent, FINALIZE)


def after_render(state: dict) -> str:
    """Route after the product render node.

    Full product launch chains to social pack.
    All other intents go to finalize.
    """
    if state.get("status") == "error":
        return FINALIZE

    intent = state.get("intent", "")
    if intent == CreativeIntent.FULL_PRODUCT_LAUNCH:
        return SOCIAL_PACK

    return FINALIZE


def after_any(state: dict) -> str:
    """Generic post-node router — always goes to finalize."""
    return FINALIZE
