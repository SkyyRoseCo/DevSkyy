"""Tests for PromptEnrichmentAgent — rule-based prompt enrichment."""

from __future__ import annotations

import pytest

from skyyrose.elite_studio.agents.prompt_enrichment_agent import PromptEnrichmentAgent
from skyyrose.elite_studio.models import EnrichedPrompt


class TestEnrichedPromptModel:
    def test_frozen(self):
        ep = EnrichedPrompt(success=True, original_spec="a", enriched_spec="b")
        with pytest.raises((AttributeError, TypeError)):
            ep.success = False  # type: ignore[misc]

    def test_defaults(self):
        ep = EnrichedPrompt(success=False)
        assert ep.original_spec == ""
        assert ep.enriched_spec == ""
        assert ep.additions == ()
        assert ep.error == ""


class TestPromptEnrichmentAgent:
    def setup_method(self):
        self.agent = PromptEnrichmentAgent()

    # --- Happy path ---

    def test_black_rose_sku_gets_collection_dna(self):
        result = self.agent.enrich("br-001", "A black crewneck with rose logo.")
        assert result.success is True
        assert "black-rose" in result.enriched_spec
        assert "Oakland" in result.enriched_spec

    def test_love_hurts_sku_gets_collection_dna(self):
        result = self.agent.enrich("lh-002", "Red varsity joggers.")
        assert result.success is True
        assert "love-hurts" in result.enriched_spec or "cathedral" in result.enriched_spec.lower()

    def test_signature_sku_gets_collection_dna(self):
        result = self.agent.enrich("sg-005", "Bay Bridge shirt.")
        assert result.success is True
        assert "signature" in result.enriched_spec or "Golden Gate" in result.enriched_spec

    def test_kids_sku_gets_collection_dna(self):
        result = self.agent.enrich("kids-001", "Kids red set.")
        assert result.success is True
        assert "kids-capsule" in result.enriched_spec or "playful" in result.enriched_spec.lower()

    def test_style_modifiers_always_appended(self):
        result = self.agent.enrich("br-001", "Some spec.")
        assert "editorial lighting" in result.enriched_spec
        assert "luxury brand aesthetic" in result.enriched_spec
        assert "SkyyRose brand DNA" in result.enriched_spec

    def test_original_spec_preserved(self):
        spec = "Unique spec text XYZ123."
        result = self.agent.enrich("br-001", spec)
        assert spec in result.enriched_spec

    def test_original_spec_stored(self):
        spec = "Original spec content."
        result = self.agent.enrich("sg-007", spec)
        assert result.original_spec == spec

    def test_additions_populated(self):
        result = self.agent.enrich("br-001", "spec text")
        assert len(result.additions) > 0
        # Should contain collection and style modifier entries
        addition_types = {a.split(":")[0] for a in result.additions}
        assert "collection_dna" in addition_types
        assert "style_modifier" in addition_types

    def test_sku_header_in_enriched_spec(self):
        result = self.agent.enrich("br-003", "spec")
        assert "br-003" in result.enriched_spec

    # --- Unknown SKU ---

    def test_unknown_sku_still_succeeds(self):
        result = self.agent.enrich("xx-999", "Mystery product spec.")
        assert result.success is True
        # No collection DNA, but style modifiers still applied
        assert "editorial lighting" in result.enriched_spec

    def test_unknown_sku_no_collection_dna(self):
        result = self.agent.enrich("xx-999", "spec")
        # Should not contain any collection-specific text
        assert "Oakland" not in result.enriched_spec
        assert "Golden Gate" not in result.enriched_spec
        assert "cathedral" not in result.enriched_spec.lower()

    # --- Empty spec ---

    def test_empty_spec_still_enriches(self):
        result = self.agent.enrich("br-001", "")
        assert result.success is True
        assert len(result.enriched_spec) > 0

    # --- Immutability ---

    def test_result_is_frozen(self):
        result = self.agent.enrich("br-001", "spec")
        with pytest.raises((AttributeError, TypeError)):
            result.success = False  # type: ignore[misc]

    # --- Error handling ---

    def test_exception_returns_failure(self, monkeypatch):
        """If internal logic raises, agent returns success=False with error."""

        def _boom(*args, **kwargs):
            raise RuntimeError("Simulated internal error")

        monkeypatch.setattr(
            "skyyrose.elite_studio.agents.prompt_enrichment_agent.PromptEnrichmentAgent._enrich",
            _boom,
        )
        result = self.agent.enrich("br-001", "spec")
        assert result.success is False
        assert "Simulated internal error" in result.error
