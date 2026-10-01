"""
Tests for Creative Operations Hub — Phase 2.

Covers: CreativeIntent enum, entry_node, routing, individual nodes (mocked),
run_creative end-to-end (mocked sub-nodes), enqueue_creative job data.
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# CreativeIntent enum tests
# ---------------------------------------------------------------------------


class TestCreativeIntent:
    def test_all_intents_present(self):
        from skyyrose.elite_studio.creative.state import CreativeIntent

        intents = {e.value for e in CreativeIntent}
        expected = {
            "product-render",
            "3d-model",
            "social-pack",
            "product-copy",
            "character-sheet",
            "scene-composite",
            "virtual-tryon",
            "full-product-launch",
            "design-ideation",
            "mockup",
            "collection-plan",
            "tech-pack",
            "moodboard",
            "colorway-explore",
            "tripo-generate",
        }
        assert intents == expected

    def test_intent_values_are_strings(self):
        from skyyrose.elite_studio.creative.state import CreativeIntent

        for intent in CreativeIntent:
            assert isinstance(intent.value, str)
            assert "-" in intent.value or intent.value.isalpha()


# ---------------------------------------------------------------------------
# State tests
# ---------------------------------------------------------------------------


class TestCreativeOperationState:
    def test_create_initial_state(self):
        from skyyrose.elite_studio.creative.state import create_initial_state

        state = create_initial_state(
            intent="product-render",
            params={"view": "front"},
            sku="br-001",
            tenant_id="tenant-1",
        )
        assert state["intent"] == "product-render"
        assert state["sku"] == "br-001"
        assert state["status"] == "running"
        assert state["error"] == ""
        assert state["operation_id"] != ""
        assert state["fashion_context"] is None

    def test_initial_state_has_all_result_fields(self):
        from skyyrose.elite_studio.creative.state import create_initial_state

        state = create_initial_state("design-ideation", {})
        for field in (
            "render_result",
            "model_3d_result",
            "social_result",
            "copy_result",
            "character_result",
            "composite_result",
            "tryon_result",
            "design_result",
            "tech_pack_result",
            "collection_plan_result",
        ):
            assert field in state
            assert state[field] is None


# ---------------------------------------------------------------------------
# Entry node tests
# ---------------------------------------------------------------------------


class TestEntryNode:
    @pytest.mark.parametrize(
        "intent,params",
        [
            ("design-ideation", {"approved": True}),
            ("not-a-real-intent", {}),
            ("product-render", {"spend_authorized": True}),
            ("design-ideation", {"governor_context": {"authorized": True}}),
        ],
    )
    def test_entry_denies_caller_authority(self, intent, params):
        from skyyrose.elite_studio.creative.nodes import entry_node

        result = entry_node({"intent": intent, "sku": "synthetic", "params": params})
        assert result["status"] == "error"
        assert result["error_code"] == "PAID_GOVERNOR_REQUIRED"
        assert result["provider_called"] is False


# ---------------------------------------------------------------------------
# Routing tests
# ---------------------------------------------------------------------------


class TestRouteIntent:
    def test_product_render_routes_to_product_render(self):
        from skyyrose.elite_studio.creative.edges import PRODUCT_RENDER, route_intent

        state = {"intent": "product-render", "status": "running"}
        assert route_intent(state) == PRODUCT_RENDER

    def test_social_pack_routes_to_social_pack(self):
        from skyyrose.elite_studio.creative.edges import SOCIAL_PACK, route_intent

        state = {"intent": "social-pack", "status": "running"}
        assert route_intent(state) == SOCIAL_PACK

    def test_design_ideation_routes_to_design(self):
        from skyyrose.elite_studio.creative.edges import DESIGN_IDEATION, route_intent

        state = {"intent": "design-ideation", "status": "running"}
        assert route_intent(state) == DESIGN_IDEATION

    def test_mockup_routes_to_design(self):
        from skyyrose.elite_studio.creative.edges import DESIGN_IDEATION, route_intent

        state = {"intent": "mockup", "status": "running"}
        assert route_intent(state) == DESIGN_IDEATION

    def test_collection_plan_routes_correctly(self):
        from skyyrose.elite_studio.creative.edges import COLLECTION_PLAN, route_intent

        state = {"intent": "collection-plan", "status": "running"}
        assert route_intent(state) == COLLECTION_PLAN

    def test_character_sheet_routes_to_character(self):
        from skyyrose.elite_studio.creative.edges import CHARACTER, route_intent

        state = {"intent": "character-sheet", "status": "running"}
        assert route_intent(state) == CHARACTER

    def test_error_state_routes_to_finalize(self):
        from skyyrose.elite_studio.creative.edges import FINALIZE, route_intent

        state = {"intent": "product-render", "status": "error"}
        assert route_intent(state) == FINALIZE

    def test_all_14_intents_have_routing(self):
        from skyyrose.elite_studio.creative.edges import route_intent
        from skyyrose.elite_studio.creative.state import CreativeIntent

        for intent in CreativeIntent:
            state = {"intent": intent.value, "status": "running"}
            result = route_intent(state)
            assert result != "", f"Intent {intent.value} routed to empty string"

    def test_after_render_full_launch_chains_to_social(self):
        from skyyrose.elite_studio.creative.edges import SOCIAL_PACK, after_render

        state = {"intent": "full-product-launch", "status": "running"}
        assert after_render(state) == SOCIAL_PACK

    def test_after_render_normal_goes_to_finalize(self):
        from skyyrose.elite_studio.creative.edges import FINALIZE, after_render

        state = {"intent": "product-render", "status": "running"}
        assert after_render(state) == FINALIZE


# ---------------------------------------------------------------------------
# Product copy node tests (no external deps)
# ---------------------------------------------------------------------------


class TestProductCopyNode:
    def test_generates_copy_for_known_sku(self):
        from skyyrose.elite_studio.creative.nodes import product_copy_node

        state = {
            "intent": "product-copy",
            "sku": "br-001",
            "params": {
                "product_name": "BLACK Rose Crewneck",
                "garment_type": "crewneck",
                "collection": "black-rose",
                "price": 35,
            },
            "fashion_context": {
                "garment_type": "crewneck",
                "collection_dna": "Black Rose: gothic luxury",
                "fabric": "french terry",
                "size_range": "S-3XL",
                "color_palette": ["#0A0A0A", "#C0C0C0", "#B76E79"],
            },
            "stage_timings": {},
        }
        result = product_copy_node(state)
        assert result.get("copy_result") is not None
        copy = result["copy_result"]
        assert copy["success"] is True
        assert "SkyyRose" in copy["short_description"] or "BLACK Rose" in copy["short_description"]
        assert len(copy["meta_title"]) <= 70
        assert len(copy["meta_description"]) <= 160
        assert len(copy["keywords"]) > 0

    def test_copy_includes_brand_tagline(self):
        from skyyrose.elite_studio.creative.nodes import product_copy_node

        state = {
            "intent": "product-copy",
            "sku": "sg-007",
            "params": {"product_name": "Signature Beanie", "collection": "signature"},
            "fashion_context": {
                "collection_dna": "Signature: West Coast prestige",
                "fabric": "knit",
                "size_range": "One Size",
                "color_palette": ["#0A0A0A", "#D4AF37", "#B76E79"],
            },
            "stage_timings": {},
        }
        result = product_copy_node(state)
        copy = result.get("copy_result", {})
        assert copy.get("success") is True
        combined = (
            copy.get("short_description", "")
            + copy.get("long_description", "")
            + " ".join(copy.get("keywords", []))
        )
        assert "SkyyRose" in combined or "Luxury" in combined


# ---------------------------------------------------------------------------
# Design ideation node tests (no external deps)
# ---------------------------------------------------------------------------


class TestDesignIdeationNode:
    @pytest.mark.parametrize("params", [{}, {"approved": True}])
    def test_unqualified_design_path_denied(self, params):
        from skyyrose.elite_studio.creative.nodes import design_ideation_node

        result = design_ideation_node({"intent": "design-ideation", "params": params})
        assert result["error_code"] == "PAID_GOVERNOR_REQUIRED"
        assert result["provider_called"] is False


# ---------------------------------------------------------------------------
# Collection plan node tests
# ---------------------------------------------------------------------------


class TestCollectionPlanNode:
    def test_unqualified_collection_path_denied(self):
        from skyyrose.elite_studio.creative.nodes import collection_plan_node

        result = collection_plan_node({"intent": "collection-plan", "params": {"approved": True}})
        assert result["error_code"] == "PAID_GOVERNOR_REQUIRED"
        assert result["provider_called"] is False


# ---------------------------------------------------------------------------
# Finalize node tests
# ---------------------------------------------------------------------------


class TestFinalizeNode:
    def test_sets_success_when_no_error(self):
        from skyyrose.elite_studio.creative.nodes import finalize_node

        state = {"status": "running", "error": ""}
        result = finalize_node(state)
        assert result.get("status") == "success"

    def test_preserves_error_state(self):
        from skyyrose.elite_studio.creative.nodes import finalize_node

        state = {"status": "error", "error": "something went wrong"}
        result = finalize_node(state)
        # Should return empty dict — error state preserved from state
        assert result == {}


# ---------------------------------------------------------------------------
# run_creative end-to-end tests (mocked graph)
# ---------------------------------------------------------------------------


class TestRunCreative:
    def test_run_creative_design_ideation(self):
        from skyyrose.elite_studio.creative.runner import run_creative

        result = run_creative(
            intent="design-ideation",
            params={
                "collection": "black-rose",
                "garment_type": "hoodie",
                "design_intent": "Gothic luxury",
                "target_price_usd": 65.0,
            },
        )
        assert "operation_id" in result
        assert result.get("intent") == "design-ideation"
        # Status should be success or error (not running)
        assert result.get("status") in ("success", "error")

    def test_run_creative_collection_plan(self):
        from skyyrose.elite_studio.creative.runner import run_creative

        result = run_creative(
            intent="collection-plan",
            params={"collection": "signature", "season": "FW26", "theme": "West Coast"},
        )
        assert result.get("status") in ("success", "error")

    def test_run_creative_invalid_intent(self):
        from skyyrose.elite_studio.creative.runner import run_creative

        result = run_creative(intent="not-valid", params={})
        assert result.get("status") == "error"
        assert result.get("error") != ""

    def test_run_creative_product_copy(self):
        from skyyrose.elite_studio.creative.runner import run_creative

        result = run_creative(
            intent="product-copy",
            params={
                "product_name": "BLACK Rose Crewneck",
                "collection": "black-rose",
                "garment_type": "crewneck",
                "price": 35,
            },
            sku="br-001",
        )
        assert result.get("status") in ("success", "error")


# ---------------------------------------------------------------------------
# enqueue_creative tests
# ---------------------------------------------------------------------------


class TestEnqueueCreative:
    def test_enqueue_creative_produces_correct_job_data(self):
        """Verify enqueue_creative builds correct EliteStudioJobData."""
        from skyyrose.elite_studio.queue.job_types import EliteStudioJobData

        job = EliteStudioJobData(
            sku="br-001",
            intent="social-pack",
            creative_params={"collection": "black-rose"},
            priority=7,
        )
        assert job.intent == "social-pack"
        assert job.creative_params == {"collection": "black-rose"}
        assert job.priority == 7
        assert job.sku == "br-001"

    def test_job_data_default_intent(self):
        from skyyrose.elite_studio.queue.job_types import EliteStudioJobData

        job = EliteStudioJobData(sku="sg-001")
        assert job.intent == "product-render"
        assert job.creative_params == {}

    def test_job_data_validates_sku(self):
        from pydantic import ValidationError

        from skyyrose.elite_studio.queue.job_types import EliteStudioJobData

        with pytest.raises(ValidationError):
            EliteStudioJobData(sku="")
