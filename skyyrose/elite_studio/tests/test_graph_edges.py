"""Tests for conditional edge routing functions."""

from __future__ import annotations

from skyyrose.elite_studio.graph.edges import (
    COMPOSITOR,
    FINALIZE,
    GENERATOR,
    QUALITY,
    after_compositor,
    after_generation,
    after_quality,
    after_vision,
)
from skyyrose.elite_studio.graph.state import EliteStudioState, create_initial_state
from skyyrose.elite_studio.tests.conftest import (
    make_generation_result,
    make_quality_verification,
    make_synthesized_vision,
)

END = "__end__"


def _base_state(**overrides) -> EliteStudioState:
    """Create a base state with sensible defaults."""
    s = dict(create_initial_state("br-001"))
    s.update(overrides)
    return EliteStudioState(**s)  # type: ignore[misc]


class TestAfterVision:
    def test_routes_to_generator_on_success(self):
        state = _base_state(vision_result=make_synthesized_vision(success=True))
        assert after_vision(state) == GENERATOR

    def test_routes_to_end_on_failure(self):
        state = _base_state(vision_result=make_synthesized_vision(success=False))
        assert after_vision(state) == END

    def test_routes_to_end_when_vision_is_none(self):
        state = _base_state(vision_result=None)
        assert after_vision(state) == END


class TestAfterGeneration:
    def test_routes_to_quality_on_success(self):
        state = _base_state(generation_result=make_generation_result(success=True))
        assert after_generation(state) == QUALITY

    def test_routes_to_end_on_failure(self):
        state = _base_state(generation_result=make_generation_result(success=False))
        assert after_generation(state) == END

    def test_routes_to_end_when_none(self):
        state = _base_state(generation_result=None)
        assert after_generation(state) == END


class TestAfterQuality:
    def test_routes_to_finalize_when_approved_no_compositor(self):
        qc = make_quality_verification(recommendation="approve")
        state = _base_state(quality_result=qc, enable_compositor=False)
        assert after_quality(state) == FINALIZE

    def test_routes_to_compositor_when_enabled(self):
        qc = make_quality_verification(recommendation="approve")
        state = _base_state(quality_result=qc, enable_compositor=True)
        assert after_quality(state) == COMPOSITOR

    def test_retries_when_regenerate_recommended(self):
        qc = make_quality_verification(recommendation="regenerate")
        state = _base_state(quality_result=qc, retry_count=0, max_retries=2)
        assert after_quality(state) == GENERATOR

    def test_no_retry_when_limit_reached(self):
        qc = make_quality_verification(recommendation="regenerate")
        state = _base_state(quality_result=qc, retry_count=2, max_retries=2)
        # retry_count == max_retries → cannot retry; compositor disabled → FINALIZE
        assert after_quality(state) == FINALIZE

    def test_no_retry_when_limit_reached_compositor_enabled(self):
        qc = make_quality_verification(recommendation="regenerate")
        state = _base_state(
            quality_result=qc,
            retry_count=2,
            max_retries=2,
            enable_compositor=True,
        )
        assert after_quality(state) == FINALIZE

    def test_routes_to_finalize_when_no_qc_result(self):
        state = _base_state(quality_result=None, enable_compositor=False)
        assert after_quality(state) == FINALIZE

    def test_manual_review_routes_to_finalize_not_generator(self):
        qc = make_quality_verification(recommendation="manual_review")
        state = _base_state(quality_result=qc, retry_count=0)
        # manual_review is not "regenerate" — should not retry
        assert after_quality(state) in (FINALIZE, COMPOSITOR)


class TestAfterCompositor:
    def test_always_routes_to_finalize(self):
        state = create_initial_state("br-001")
        assert after_compositor(state) == FINALIZE
