"""
Tests for Fashion Intelligence Core — Phase 1.

Covers: knowledge base, trends, photography, color, sizing, editorial,
materials, QA rules, context builder, and design tools.
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Knowledge base tests
# ---------------------------------------------------------------------------


class TestFashionKnowledgeBase:
    def setup_method(self):
        from skyyrose.elite_studio.fashion.knowledge import FashionKnowledgeBase

        self.kb = FashionKnowledgeBase()

    def test_get_garment_hoodie(self):
        garment = self.kb.get_garment("hoodie")
        assert garment is not None
        assert garment.name == "hoodie"
        assert garment.category == "tops"

    def test_get_garment_case_insensitive(self):
        assert self.kb.get_garment("HOODIE") is not None
        assert self.kb.get_garment("Jersey") is not None

    def test_get_garment_unknown_returns_none(self):
        assert self.kb.get_garment("space_suit") is None

    def test_get_fabric_sherpa(self):
        fabric = self.kb.get_fabric("sherpa")
        assert fabric is not None
        assert (
            "pile" in fabric.rendering_notes.lower() or "texture" in fabric.rendering_notes.lower()
        )

    def test_get_fabric_french_terry(self):
        fabric = self.kb.get_fabric("french terry")
        assert fabric is not None
        assert "french terry" in fabric.name

    def test_get_default_fabric_for_hoodie(self):
        assert self.kb.get_default_fabric_for_garment("hoodie") == "french terry"

    def test_get_default_fabric_for_jersey(self):
        assert self.kb.get_default_fabric_for_garment("jersey") == "mesh"

    def test_get_default_fabric_for_unknown_returns_cotton(self):
        assert self.kb.get_default_fabric_for_garment("unknown_garment") == "cotton"

    def test_list_garments_not_empty(self):
        garments = self.kb.list_garments()
        assert len(garments) >= 8

    def test_list_fabrics_not_empty(self):
        fabrics = self.kb.list_fabrics()
        assert len(fabrics) >= 7

    def test_garment_is_frozen(self):
        garment = self.kb.get_garment("hoodie")
        with pytest.raises((AttributeError, TypeError)):
            garment.name = "modified"  # type: ignore[misc]

    def test_brand_tagline_present(self):
        from skyyrose.elite_studio.fashion.knowledge import BRAND_TAGLINE

        assert BRAND_TAGLINE == ""


# ---------------------------------------------------------------------------
# Trend advisor tests
# ---------------------------------------------------------------------------


class TestTrendAdvisor:
    def setup_method(self):
        from skyyrose.elite_studio.fashion.trends import TrendAdvisor

        self.advisor = TrendAdvisor()

    def test_get_current_trends_all(self):
        trends = self.advisor.get_current_trends()
        assert len(trends) >= 8

    def test_get_current_trends_fw26(self):
        trends = self.advisor.get_current_trends("FW26")
        assert len(trends) > 0
        for t in trends:
            assert "FW26" in t.season

    def test_get_trends_for_category_silhouette(self):
        trends = self.advisor.get_trends_for_category("silhouette")
        assert len(trends) >= 1
        for t in trends:
            assert t.category == "silhouette"

    def test_get_relevance_score_hoodie(self):
        score = self.advisor.get_relevance_score("hoodie", "FW26")
        assert 0.0 <= score <= 1.0
        assert score > 0.0

    def test_get_relevance_score_unknown_garment_baseline(self):
        score = self.advisor.get_relevance_score("unknown_garment")
        assert score == 0.3

    def test_trend_signal_is_frozen(self):
        trends = self.advisor.get_current_trends()
        t = trends[0]
        with pytest.raises((AttributeError, TypeError)):
            t.name = "modified"  # type: ignore[misc]

    def test_oversized_silhouettes_trend_present(self):
        all_trends = self.advisor.get_current_trends()
        names = [t.name for t in all_trends]
        assert "Oversized Silhouettes" in names

    def test_sherpa_trend_present(self):
        trends = self.advisor.get_trends_for_category("fabric")
        names = [t.name for t in trends]
        assert "Sherpa & Fleece Comeback" in names

    def test_relevance_score_jersey(self):
        score = self.advisor.get_relevance_score("jersey")
        assert score > 0.5  # jersey has strong trend alignment

    def test_trend_notes_for_garment(self):
        notes = self.advisor.get_trend_notes_for_garment("hoodie")
        assert len(notes) > 0
        # Notes should mention SkyyRose
        assert any("SkyyRose" in n or "hoodie" in n.lower() or "Black Rose" in n for n in notes)


# ---------------------------------------------------------------------------
# Photography director tests
# ---------------------------------------------------------------------------


class TestPhotographyDirector:
    def setup_method(self):
        from skyyrose.elite_studio.fashion.photography import PhotographyDirector

        self.director = PhotographyDirector()

    def test_get_standard_ecommerce(self):
        std = self.director.get_standard("ecommerce")
        assert std is not None
        assert std.style == "ecommerce"

    def test_get_standard_editorial(self):
        std = self.director.get_standard("editorial")
        assert std is not None
        assert std.style == "editorial"

    def test_get_standard_unknown_returns_none(self):
        assert self.director.get_standard("unknown_style") is None

    def test_recommend_style_beanie_returns_flatlay(self):
        style = self.director.recommend_style("beanie")
        assert style == "flat-lay"

    def test_recommend_style_jersey_black_rose(self):
        style = self.director.recommend_style("jersey", "black-rose")
        assert style == "editorial"

    def test_recommend_style_hoodie_signature_lookbook(self):
        style = self.director.recommend_style("hoodie", "signature")
        assert style == "lookbook"

    def test_get_fabric_lighting_notes_sherpa(self):
        notes = self.director.get_fabric_lighting_notes("sherpa")
        assert "sherpa" in notes.lower() or "pile" in notes.lower()

    def test_photography_standard_is_frozen(self):
        std = self.director.get_standard("ecommerce")
        with pytest.raises((AttributeError, TypeError)):
            std.style = "modified"  # type: ignore[misc]

    def test_list_styles_includes_all(self):
        styles = self.director.list_styles()
        assert "ecommerce" in styles
        assert "editorial" in styles
        assert "flat-lay" in styles
        assert "lookbook" in styles


# ---------------------------------------------------------------------------
# Color advisor tests
# ---------------------------------------------------------------------------


class TestColorAdvisor:
    def setup_method(self):
        from skyyrose.elite_studio.fashion.colorway import ColorAdvisor

        self.advisor = ColorAdvisor()

    def test_get_collection_palette_black_rose(self):
        palette = self.advisor.get_collection_palette("black-rose")
        assert palette.collection == "black-rose"
        assert palette.primary == "#0A0A0A"

    def test_get_collection_palette_love_hurts_crimson(self):
        palette = self.advisor.get_collection_palette("love-hurts")
        assert "#DC143C" in (palette.primary, palette.secondary, palette.accent)

    def test_get_collection_palette_signature_gold(self):
        palette = self.advisor.get_collection_palette("signature")
        assert "#D4AF37" in (palette.primary, palette.secondary, palette.accent)

    def test_get_collection_palette_kids_capsule_rose_gold(self):
        palette = self.advisor.get_collection_palette("kids-capsule")
        assert "#B76E79" in (palette.primary, palette.secondary, palette.accent)

    def test_get_collection_palette_unknown_returns_global(self):
        palette = self.advisor.get_collection_palette("unknown-collection")
        assert palette.collection == "global"

    def test_validate_color_fidelity_exact_match(self):
        assert self.advisor.validate_color_fidelity("#B76E79", "#B76E79") is True

    def test_validate_color_fidelity_close_colors(self):
        # Colors within 1-2 hex steps per channel should pass
        assert self.advisor.validate_color_fidelity("#B76E79", "#B76E7A") is True

    def test_validate_color_fidelity_very_different_colors(self):
        assert self.advisor.validate_color_fidelity("#0A0A0A", "#FFFFFF") is False

    def test_suggest_colorways_returns_list(self):
        colorways = self.advisor.suggest_colorways("hoodie", "black-rose", n=3)
        assert len(colorways) >= 1
        assert all(isinstance(c.name, str) for c in colorways)

    def test_color_palette_is_frozen(self):
        palette = self.advisor.get_collection_palette("black-rose")
        with pytest.raises((AttributeError, TypeError)):
            palette.primary = "#FFFFFF"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Sizing advisor tests
# ---------------------------------------------------------------------------


class TestSizingAdvisor:
    def setup_method(self):
        from skyyrose.elite_studio.fashion.sizing import SizingAdvisor

        self.advisor = SizingAdvisor()

    def test_get_guideline_hoodie(self):
        guide = self.advisor.get_guideline("hoodie")
        assert "S" in guide.size_range or "3XL" in guide.size_range

    def test_get_guideline_set_kids(self):
        guide = self.advisor.get_guideline("set", "kids-capsule")
        assert "2T" in guide.size_range

    def test_get_guideline_unknown_returns_default(self):
        guide = self.advisor.get_guideline("unknown_garment")
        assert guide.size_range != ""

    def test_get_size_chart_hoodie_has_all_sizes(self):
        chart = self.advisor.get_size_chart("hoodie")
        assert "S" in chart
        assert "3XL" in chart
        assert "chest" in chart["M"]

    def test_get_size_chart_shorts_has_inseam(self):
        chart = self.advisor.get_size_chart("shorts")
        assert "inseam" in chart["M"]

    def test_get_size_chart_unknown_returns_empty(self):
        chart = self.advisor.get_size_chart("space_suit")
        assert chart == {}

    def test_sizing_guideline_is_frozen(self):
        guide = self.advisor.get_guideline("hoodie")
        with pytest.raises((AttributeError, TypeError)):
            guide.size_range = "modified"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Materials expert tests
# ---------------------------------------------------------------------------


class TestMaterialsExpert:
    def setup_method(self):
        from skyyrose.elite_studio.fashion.materials import MaterialsExpert

        self.expert = MaterialsExpert()

    def test_get_rendering_spec_sherpa(self):
        spec = self.expert.get_rendering_spec("sherpa")
        assert spec is not None
        assert spec.fabric == "sherpa"

    def test_get_rendering_spec_alias_terry(self):
        spec = self.expert.get_rendering_spec("terry")
        assert spec is not None
        assert spec.fabric == "french terry"

    def test_get_rendering_spec_unknown_returns_none(self):
        assert self.expert.get_rendering_spec("unobtainium") is None

    def test_validate_texture_sherpa_pass(self):
        assert (
            self.expert.validate_texture(
                "sherpa", "dense pile texture with deep micro-shadows between fibers"
            )
            is True
        )

    def test_validate_texture_sherpa_fail_on_flat(self):
        assert self.expert.validate_texture("sherpa", "flat smooth cotton surface") is False

    def test_validate_texture_mesh_pass(self):
        assert (
            self.expert.validate_texture(
                "mesh", "open-weave grid pattern semi-transparent athletic mesh"
            )
            is True
        )

    def test_validate_texture_mesh_fail_on_solid(self):
        assert self.expert.validate_texture("mesh", "solid opaque fabric surface") is False

    def test_get_prompt_keywords_satin(self):
        kws = self.expert.get_prompt_keywords("satin")
        assert len(kws) > 0
        assert any("gloss" in kw.lower() or "specular" in kw.lower() for kw in kws)

    def test_rendering_spec_is_frozen(self):
        spec = self.expert.get_rendering_spec("sherpa")
        with pytest.raises((AttributeError, TypeError)):
            spec.fabric = "modified"  # type: ignore[misc]

    def test_build_texture_prompt_segment(self):
        segment = self.expert.build_texture_prompt_segment("sherpa")
        assert len(segment) > 0
        assert "pile" in segment.lower() or "texture" in segment.lower()


# ---------------------------------------------------------------------------
# QA rules tests
# ---------------------------------------------------------------------------


class TestFashionQA:
    def setup_method(self):
        from skyyrose.elite_studio.fashion.qa_rules import FashionQA

        self.qa = FashionQA()

    def test_get_rules_all(self):
        rules = self.qa.get_rules()
        assert len(rules) >= 15

    def test_get_rules_by_category_fabric(self):
        rules = self.qa.get_rules("fabric")
        assert len(rules) >= 4
        for r in rules:
            assert r.category == "fabric"

    def test_get_rules_for_jersey(self):
        rules = self.qa.get_rules_for_garment("jersey")
        names = [r.name for r in rules]
        assert "Jersey Number Placement" in names

    def test_get_rules_for_collection_black_rose(self):
        rules = self.qa.get_rules_for_collection("black-rose")
        names = [r.name for r in rules]
        assert "Black Rose Dark Tone" in names

    def test_get_rules_for_collection_love_hurts(self):
        rules = self.qa.get_rules_for_collection("love-hurts")
        names = [r.name for r in rules]
        assert "Love Hurts Crimson Accuracy" in names

    def test_qa_rule_is_frozen(self):
        rules = self.qa.get_rules()
        rule = rules[0]
        with pytest.raises((AttributeError, TypeError)):
            rule.name = "modified"  # type: ignore[misc]

    def test_rules_have_fail_examples(self):
        rules = self.qa.get_rules("fabric")
        for rule in rules:
            assert len(rule.fail_examples) > 0


# ---------------------------------------------------------------------------
# Fashion context builder tests
# ---------------------------------------------------------------------------


class TestFashionContextBuilder:
    def setup_method(self):
        from skyyrose.elite_studio.fashion.context import FashionContextBuilder

        self.builder = FashionContextBuilder()

    def test_build_basic(self):
        ctx = self.builder.build(
            garment_type="hoodie",
            collection="black-rose",
            season="FW26",
        )
        assert ctx.garment_type == "hoodie"
        assert ctx.fabric == "french terry"
        assert len(ctx.color_palette) == 3
        assert ctx.color_palette[0] == "#0A0A0A"

    def test_build_collection_dna_present(self):
        ctx = self.builder.build(garment_type="joggers", collection="love-hurts")
        assert "Love Hurts" in ctx.collection_dna or "love" in ctx.collection_dna.lower()

    def test_build_from_catalog_br001(self):
        ctx = self.builder.build_from_product_catalog("br-001")
        assert ctx.garment_type in ("crewneck", "garment")
        assert ctx.fabric != ""
        assert len(ctx.color_palette) == 3

    def test_build_from_catalog_lh004(self):
        ctx = self.builder.build_from_product_catalog("lh-004")
        assert ctx.garment_type in ("varsity jacket", "jacket", "garment")

    def test_build_from_catalog_unknown_sku(self):
        ctx = self.builder.build_from_product_catalog("xx-999")
        assert ctx.garment_type == "garment"

    def test_build_context_is_frozen(self):
        ctx = self.builder.build(garment_type="hoodie", collection="signature")
        with pytest.raises((AttributeError, TypeError)):
            ctx.garment_type = "modified"  # type: ignore[misc]

    def test_build_includes_rendering_spec(self):
        ctx = self.builder.build(garment_type="jacket", collection="black-rose")
        assert ctx.rendering_spec != ""
        assert ctx.fabric in ("sherpa", "french terry", "fleece")

    def test_brand_tagline_in_collection_dna(self):
        ctx = self.builder.build(garment_type="hoodie", collection="signature")
        # collection DNA should include collection-level content
        assert len(ctx.collection_dna) > 20


# ---------------------------------------------------------------------------
# Design ideation tests
# ---------------------------------------------------------------------------


class TestDesignIdeation:
    def setup_method(self):
        from skyyrose.elite_studio.fashion.design.ideation import DesignBrief, DesignIdeationAgent

        self.agent = DesignIdeationAgent()
        self.DesignBrief = DesignBrief

    def test_generate_concept_black_rose(self):
        brief = self.DesignBrief(
            collection="black-rose",
            garment_type="hoodie",
            season="FW26",
            target_price_usd=65.0,
            design_intent="Gothic luxury hoodie with embroidered silver rose",
        )
        concept = self.agent.generate_concept(brief)
        assert concept.concept_id != ""
        assert "BLACK Rose" in concept.concept_name or "Black Rose" in concept.concept_name
        assert len(concept.generation_prompt) > 50

    def test_concept_includes_brand_dna(self):
        brief = self.DesignBrief(
            collection="signature",
            garment_type="shirt",
            season="SS27",
            target_price_usd=65.0,
            design_intent="Bay Area pride tee",
        )
        concept = self.agent.generate_concept(brief)
        assert (
            "Signature" in concept.concept_name or "signature" in concept.generation_prompt.lower()
        )

    def test_generate_alternatives_returns_multiple(self):
        brief = self.DesignBrief(
            collection="love-hurts",
            garment_type="joggers",
            season="FW26",
            target_price_usd=95.0,
            design_intent="Crimson-accented luxury joggers",
        )
        alts = self.agent.generate_alternatives(brief, n=2)
        assert len(alts) >= 1

    def test_concept_is_frozen(self):
        brief = self.DesignBrief(
            collection="kids-capsule",
            garment_type="set",
            season="FW26",
            target_price_usd=40.0,
            design_intent="Bold colorblock kids set",
        )
        concept = self.agent.generate_concept(brief)
        with pytest.raises((AttributeError, TypeError)):
            concept.concept_id = "modified"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Collection planner tests
# ---------------------------------------------------------------------------


class TestCollectionPlanner:
    def setup_method(self):
        from skyyrose.elite_studio.fashion.design.collection_planner import CollectionPlanner

        self.planner = CollectionPlanner()

    def test_plan_black_rose_collection(self):
        plan = self.planner.plan_collection("black-rose", "FW26", "Gothic luxury meets Oakland")
        assert plan.collection == "black-rose"
        assert plan.season == "FW26"
        assert len(plan.product_categories) > 0
        assert len(plan.hero_pieces) > 0

    def test_plan_has_launch_sequence(self):
        plan = self.planner.plan_collection("love-hurts", "FW26", "Crimson emotion")
        assert len(plan.launch_sequence) > 0

    def test_plan_has_trend_hooks(self):
        plan = self.planner.plan_collection("signature", "SS27", "West Coast elevation")
        assert len(plan.trend_hooks) > 0

    def test_plan_all_collections(self):
        plans = self.planner.plan_all_collections("FW26")
        assert len(plans) == 4
        collections = [p.collection for p in plans]
        assert "black-rose" in collections
        assert "love-hurts" in collections
        assert "signature" in collections
        assert "kids-capsule" in collections

    def test_plan_is_frozen(self):
        plan = self.planner.plan_collection("black-rose", "FW26", "Test theme")
        with pytest.raises((AttributeError, TypeError)):
            plan.collection = "modified"  # type: ignore[misc]
