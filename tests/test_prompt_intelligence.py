"""
Tests for Elite Prompt Intelligence System (Phase 0).

Covers: analyzer, templates, chain, enhancer, cache, history, and brand DNA presence.
"""

from __future__ import annotations

import pytest

from skyyrose.elite_studio.prompts.analyzer import PromptAnalysis, PromptAnalyzer
from skyyrose.elite_studio.prompts.cache import PromptCache, _jaccard_similarity, _tokenize
from skyyrose.elite_studio.prompts.chain import PromptChain
from skyyrose.elite_studio.prompts.enhancer import EnhancedPrompt, PromptEnhancer
from skyyrose.elite_studio.prompts.history import PromptHistory
from skyyrose.elite_studio.prompts.templates import (
    BRAND_COLORS,
    BRAND_NAME,
    BRAND_TAGLINE,
    COLLECTION_DNA,
    PromptTemplateRegistry,
)

# ===================================================================
# Analyzer Tests
# ===================================================================


class TestPromptAnalyzer:
    def setup_method(self):
        self.analyzer = PromptAnalyzer()

    def test_low_quality_vague_prompt(self):
        result = self.analyzer.analyze("make me something cool")
        assert result.score <= 2.0
        assert len(result.missing) >= 5
        assert result.enhancement_potential > 0.7

    def test_medium_quality_partial_prompt(self):
        result = self.analyzer.analyze("render the black rose hoodie in dark gothic style")
        assert result.score >= 2.0
        assert result.intent in ("product-render", "design-ideation")

    def test_high_quality_detailed_prompt(self):
        result = self.analyzer.analyze(
            "Generate a product render of br-005 BLACK Rose Hoodie Signature "
            "Edition from the Black Rose collection. French terry fabric in "
            "black, $65, edgy gothic aesthetic for FW26. 4K resolution."
        )
        assert result.score >= 6.0
        assert len(result.missing) <= 3

    def test_detects_sku(self):
        result = self.analyzer.analyze("render br-001")
        assert "product SKU" not in " ".join(result.missing)

    def test_detects_collection(self):
        result = self.analyzer.analyze("something for love hurts")
        assert "collection name" not in " ".join(result.missing)

    def test_detects_garment_type(self):
        result = self.analyzer.analyze("design a hoodie")
        assert "garment type" not in " ".join(result.missing)

    def test_detects_color(self):
        result = self.analyzer.analyze("black and rose gold hoodie")
        assert "color" not in " ".join(result.missing)

    def test_detects_fabric(self):
        result = self.analyzer.analyze("sherpa jacket")
        assert "fabric" not in " ".join(result.missing)

    def test_detects_season(self):
        result = self.analyzer.analyze("for FW26 season")
        assert "season" not in " ".join(result.missing)

    def test_detects_price(self):
        result = self.analyzer.analyze("$65 hoodie")
        assert "target price" not in " ".join(result.missing)

    def test_detects_mood(self):
        result = self.analyzer.analyze("edgy dark gothic aesthetic")
        assert "mood" not in " ".join(result.missing)

    def test_intent_detection_render(self):
        result = self.analyzer.analyze("render this product image")
        assert result.intent == "product-render"

    def test_intent_detection_3d(self):
        result = self.analyzer.analyze("create a 3d model glb file")
        assert result.intent == "3d-model"

    def test_intent_detection_social(self):
        result = self.analyzer.analyze("social media post for instagram")
        assert result.intent == "social-pack"

    def test_intent_detection_copy(self):
        result = self.analyzer.analyze("write product description seo copy")
        assert result.intent == "product-copy"

    def test_intent_detection_design(self):
        result = self.analyzer.analyze("design a new piece concept")
        assert result.intent == "design-ideation"

    def test_intent_detection_character(self):
        result = self.analyzer.analyze("create a mascot character sprite")
        assert result.intent == "character-sheet"

    def test_intent_unknown_vague(self):
        result = self.analyzer.analyze("yo do the thing")
        assert result.intent == "unknown"

    def test_analysis_is_frozen(self):
        result = self.analyzer.analyze("test")
        with pytest.raises(AttributeError):
            result.score = 99.0  # type: ignore[misc]

    def test_score_clamped_to_ten(self):
        # Even an incredibly detailed prompt won't exceed 10
        result = self.analyzer.analyze(
            "render br-001 Black Rose crewneck in black sherpa fabric "
            "$35 edgy gothic for FW26 on instagram like reference.jpg 2048x2048"
        )
        assert result.score <= 10.0


# ===================================================================
# Template Registry Tests
# ===================================================================


class TestPromptTemplateRegistry:
    def setup_method(self):
        self.registry = PromptTemplateRegistry()

    def test_all_twelve_intents_have_templates(self):
        expected_intents = {
            "product-render",
            "3d-model",
            "social-pack",
            "product-copy",
            "design-ideation",
            "mockup",
            "character-sheet",
            "scene-composite",
            "collection-plan",
            "tech-pack",
            "moodboard",
            "colorway-explore",
        }
        for intent in expected_intents:
            template = self.registry.get_template(intent)
            assert template is not None, f"Missing template for {intent}"
            assert template.intent == intent

    def test_templates_have_required_fields(self):
        for template in self.registry.list_templates():
            assert len(template.required_fields) > 0
            assert template.name
            assert template.template
            assert template.example_output

    def test_templates_have_skyyrose_brand_references(self):
        """Every example_output should reference SkyyRose products or brand elements."""
        brand_indicators = {
            "skyyrose",
            "rose",
            "oakland",
            "black rose",
            "love hurts",
            "signature",
            "b76e79",
            "0a0a0a",
            "d4af37",
            "dc143c",
            "c0c0c0",
        }
        for template in self.registry.list_templates():
            lower = template.example_output.lower()
            found = any(ind in lower for ind in brand_indicators)
            assert (
                found
            ), f"Template '{template.intent}' example_output missing SkyyRose brand reference"

    def test_list_intents(self):
        intents = self.registry.list_intents()
        assert len(intents) == 12

    def test_has_intent(self):
        assert self.registry.has_intent("product-render")
        assert not self.registry.has_intent("nonexistent")

    def test_unknown_intent_returns_none(self):
        assert self.registry.get_template("nonexistent") is None


# ===================================================================
# Chain Tests
# ===================================================================


class TestPromptChain:
    def setup_method(self):
        self.chain = PromptChain()

    def test_basic_enhancement(self):
        result = self.chain.enhance("make me a hoodie")
        assert "enhanced" in result
        assert len(result["enhanced"]) > len("make me a hoodie")
        assert len(result["context_added"]) > 0

    def test_intent_preserved(self):
        result = self.chain.enhance("make me a hoodie", intent="design-ideation")
        assert result["intent"] == "design-ideation"

    def test_auto_intent_detection(self):
        result = self.chain.enhance("render a product image of br-001")
        assert result["intent"] == "product-render"

    def test_season_injection(self):
        result = self.chain.enhance("make a hoodie", intent="design-ideation", new_design=True)
        # Should have added a season
        assert any("season" in c.lower() for c in result["context_added"])

    def test_collection_detection_from_sku(self):
        result = self.chain.enhance("render br-005")
        enhanced = result["enhanced"].lower()
        assert "black rose" in enhanced or "rose" in enhanced

    def test_collection_detection_from_name(self):
        result = self.chain.enhance(
            "design something for love hurts", intent="design-ideation", new_design=True
        )
        assert any("love hurts" in c.lower() for c in result["context_added"])

    def test_brand_injection(self):
        result = self.chain.enhance("design a hoodie", intent="design-ideation", new_design=True)
        enhanced = result["enhanced"].lower()
        assert "skyyrose" in enhanced or "luxury grows" in enhanced or "b76e79" in enhanced

    def test_no_fabric_default_for_existing_render(self):
        result = self.chain.enhance("render a hoodie")
        assert "french terry" not in result["enhanced"].lower()

    def test_render_does_not_invent_resolution(self):
        result = self.chain.enhance("render br-001", intent="product-render")
        assert "4K (2048x2730)" not in result["enhanced"]
        assert result["brief_status"] == "incomplete"

    def test_fashion_context_override(self):
        custom_context = {"collection_dna": "custom brand override context"}
        result = self.chain.enhance("design something", fashion_context=custom_context)
        assert "custom brand override context" in result["enhanced"]

    def test_template_name_returned(self):
        result = self.chain.enhance("render br-001", intent="product-render")
        assert result["template_used"]


# ===================================================================
# Enhancer Tests
# ===================================================================


class TestPromptEnhancer:
    def setup_method(self):
        # Use no-Redis cache for unit testing
        self.enhancer = PromptEnhancer(cache=PromptCache(redis_url="redis://fake:9999"))

    def test_end_to_end_enhancement(self):
        result = self.enhancer.enhance("make me a cool hoodie for winter")
        assert isinstance(result, EnhancedPrompt)
        assert result.score_after >= result.score_before
        assert len(result.enhanced) > len(result.original)
        assert len(result.context_added) > 0

    def test_enhanced_prompt_is_frozen(self):
        result = self.enhancer.enhance("test prompt")
        with pytest.raises(AttributeError):
            result.enhanced = "modified"  # type: ignore[misc]

    def test_intent_auto_detection(self):
        result = self.enhancer.enhance("create a 3d model of the sherpa jacket")
        assert result.intent == "3d-model"

    def test_explicit_intent_override(self):
        result = self.enhancer.enhance("do something", intent="social-pack")
        assert result.intent == "social-pack"

    def test_cache_key_deterministic(self):
        r1 = self.enhancer.enhance("test prompt", intent="product-render")
        r2 = self.enhancer.enhance("test prompt", intent="product-render")
        assert r1.cache_key == r2.cache_key

    def test_analyze_only(self):
        result = self.enhancer.analyze_only("render br-001 black rose hoodie")
        assert isinstance(result, PromptAnalysis)
        assert result.score > 0

    def test_brand_dna_in_output(self):
        result = self.enhancer.enhance("make me a hoodie")
        lower = result.enhanced.lower()
        brand_present = (
            "skyyrose" in lower
            or "b76e79" in lower
            or "luxury grows" in lower
            or "rose gold" in lower
            or "oakland" in lower
        )
        assert brand_present, "Enhanced prompt missing SkyyRose brand DNA"


# ===================================================================
# Cache Tests (with fakeredis)
# ===================================================================


class TestPromptCache:
    @pytest.fixture(autouse=True)
    def setup_fakeredis(self):
        """Set up fakeredis for cache testing."""
        try:
            import fakeredis

            self.redis = fakeredis.FakeRedis(decode_responses=True)
            self.cache = PromptCache.__new__(PromptCache)
            self.cache._redis = self.redis
            self.cache._hits = 0
            self.cache._misses = 0
        except ImportError:
            pytest.skip("fakeredis not installed")

    def _make_enhanced(self, original: str = "test", intent: str = "product-render"):
        return EnhancedPrompt(
            original=original,
            enhanced=f"Enhanced: {original}",
            intent=intent,
            score_before=2.0,
            score_after=8.0,
            context_added=("added season", "added brand"),
            cache_key="test_key",
            template_used="Product Imagery Render",
        )

    def test_store_and_exact_check(self):
        enhanced = self._make_enhanced("render br-001 hoodie")
        self.cache.store("render br-001 hoodie", enhanced)
        result = self.cache.check("render br-001 hoodie", "product-render")
        assert result is not None
        assert result.enhanced == enhanced.enhanced

    def test_cache_miss(self):
        result = self.cache.check("never stored this", "product-render")
        assert result is None

    def test_similarity_match(self):
        enhanced = self._make_enhanced("render the black rose hoodie in gothic style")
        self.cache.store("render the black rose hoodie in gothic style", enhanced)
        # Similar but not identical prompt
        result = self.cache.check(
            "render black rose hoodie gothic", "product-render", threshold=0.4
        )
        assert result is not None

    def test_invalidate_by_intent(self):
        enhanced = self._make_enhanced(intent="product-render")
        self.cache.store("test prompt", enhanced)
        removed = self.cache.invalidate_by_intent("product-render")
        assert removed >= 1

    def test_get_stats(self):
        self.cache.check("miss", "product-render")
        stats = self.cache.get_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert stats["redis"] is True


class TestTokenSimilarity:
    def test_tokenize_removes_stop_words(self):
        tokens = _tokenize("make me a cool hoodie for winter")
        assert "me" not in tokens
        assert "a" not in tokens
        assert "hoodie" in tokens
        assert "winter" in tokens
        assert "cool" in tokens

    def test_jaccard_identical(self):
        a = frozenset({"hoodie", "black", "rose"})
        assert _jaccard_similarity(a, a) == 1.0

    def test_jaccard_disjoint(self):
        a = frozenset({"hoodie", "black"})
        b = frozenset({"shirt", "white"})
        assert _jaccard_similarity(a, b) == 0.0

    def test_jaccard_partial_overlap(self):
        a = frozenset({"hoodie", "black", "rose"})
        b = frozenset({"hoodie", "black", "gothic"})
        sim = _jaccard_similarity(a, b)
        assert 0.3 < sim < 0.8

    def test_jaccard_empty_sets(self):
        assert _jaccard_similarity(frozenset(), frozenset()) == 0.0


# ===================================================================
# History Tests (with fakeredis)
# ===================================================================


class TestPromptHistory:
    @pytest.fixture(autouse=True)
    def setup_fakeredis(self):
        try:
            import fakeredis

            self.redis = fakeredis.FakeRedis(decode_responses=True)
            self.history = PromptHistory.__new__(PromptHistory)
            self.history._redis = self.redis
        except ImportError:
            pytest.skip("fakeredis not installed")

    def test_record_and_retrieve_best(self):
        self.history.record("great prompt", "product-render", 0.95, "job-001")
        self.history.record("mediocre prompt", "product-render", 0.5, "job-002")
        self.history.record("excellent prompt", "product-render", 0.99, "job-003")

        best = self.history.get_best_patterns("product-render", n=2)
        assert len(best) == 2
        # Best should be first (highest quality)
        assert best[0]["quality"] >= best[1]["quality"]

    def test_failure_patterns(self):
        self.history.record("bad prompt", "product-render", 0.2, "job-bad-1")
        self.history.record("worse prompt", "product-render", 0.1, "job-bad-2")
        self.history.record("good prompt", "product-render", 0.9, "job-good-1")

        failures = self.history.get_failure_patterns("product-render")
        assert len(failures) == 2
        for f in failures:
            assert f["quality"] < 0.4

    def test_average_quality(self):
        self.history.record("p1", "social-pack", 0.8, "j1")
        self.history.record("p2", "social-pack", 0.6, "j2")
        avg = self.history.get_average_quality("social-pack")
        assert 0.6 <= avg <= 0.8

    def test_entry_count(self):
        self.history.record("p1", "3d-model", 0.7, "j1")
        self.history.record("p2", "3d-model", 0.8, "j2")
        assert self.history.get_entry_count("3d-model") == 2

    def test_clear_intent(self):
        self.history.record("p1", "mockup", 0.9, "j1")
        cleared = self.history.clear_intent("mockup")
        assert cleared >= 1
        assert self.history.get_entry_count("mockup") == 0

    def test_empty_history_returns_defaults(self):
        assert self.history.get_best_patterns("nonexistent") == []
        assert self.history.get_average_quality("nonexistent") == 0.0
        assert self.history.get_entry_count("nonexistent") == 0


# ===================================================================
# Brand DNA Integration Tests
# ===================================================================


class TestBrandDNAPresence:
    """Verify SkyyRose brand DNA is woven into the prompt system."""

    def test_collection_dna_has_all_four_collections(self):
        assert "black-rose" in COLLECTION_DNA
        assert "love-hurts" in COLLECTION_DNA
        assert "signature" in COLLECTION_DNA
        assert "kids-capsule" in COLLECTION_DNA

    def test_brand_colors_complete(self):
        assert BRAND_COLORS["rose_gold"] == "#B76E79"
        assert BRAND_COLORS["dark"] == "#0A0A0A"
        assert BRAND_COLORS["gold"] == "#D4AF37"
        assert BRAND_COLORS["crimson"] == "#DC143C"
        assert BRAND_COLORS["silver"] == "#C0C0C0"

    def test_brand_name_and_tagline(self):
        from skyyrose.elite_studio.brand import BrandConfig

        assert BRAND_NAME == "SkyyRose"
        assert BRAND_TAGLINE == BrandConfig.load().tagline_active == ""

    def test_enhancement_injects_brand_for_black_rose(self):
        chain = PromptChain()
        result = chain.enhance(
            "design a hoodie for black rose", intent="design-ideation", new_design=True
        )
        enhanced = result["enhanced"].lower()
        assert "gothic" in enhanced or "noir" in enhanced or "darkness" in enhanced

    def test_enhancement_injects_brand_for_love_hurts(self):
        chain = PromptChain()
        result = chain.enhance("design something for love hurts")
        enhanced = result["enhanced"].lower()
        assert "emotion" in enhanced or "passion" in enhanced or "hurts" in enhanced

    def test_enhancement_injects_brand_for_signature(self):
        chain = PromptChain()
        result = chain.enhance("render sg-002 from signature collection")
        enhanced = result["enhanced"].lower()
        assert "west coast" in enhanced or "gold" in enhanced or "signature" in enhanced
