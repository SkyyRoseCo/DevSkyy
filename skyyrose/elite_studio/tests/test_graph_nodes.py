"""Tests for graph node functions — agents mocked at call site."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from skyyrose.elite_studio.graph.nodes import (
    compositor_node,
    finalize_node,
    generator_node,
    quality_node,
    vision_node,
)
from skyyrose.elite_studio.graph.state import create_initial_state
from skyyrose.elite_studio.tests.conftest import (
    make_generation_result,
    make_quality_verification,
    make_synthesized_vision,
)


def _state(**overrides):
    s = dict(create_initial_state("br-001"))
    s.update(overrides)
    return s


class TestVisionNode:
    def test_success_returns_vision_result(self):
        vision = make_synthesized_vision(success=True)
        mock_agent = MagicMock()
        mock_agent.analyze = AsyncMock(return_value=vision)

        with patch("skyyrose.elite_studio.graph.nodes.VisionAgent", return_value=mock_agent):
            result = vision_node(_state())

        assert result["vision_result"] is vision
        assert "vision" in result["stage_timings"]
        assert "status" not in result  # no error key on success

    def test_failure_sets_error_status(self):
        vision = make_synthesized_vision(success=False, error="API timeout")
        mock_agent = MagicMock()
        mock_agent.analyze = AsyncMock(return_value=vision)

        with patch("skyyrose.elite_studio.graph.nodes.VisionAgent", return_value=mock_agent):
            result = vision_node(_state())

        assert result["status"] == "error"
        assert result["failed_step"] == "vision"
        assert "API timeout" in result["error"]

    def test_timing_recorded(self):
        vision = make_synthesized_vision(success=True)
        mock_agent = MagicMock()
        mock_agent.analyze = AsyncMock(return_value=vision)

        with patch("skyyrose.elite_studio.graph.nodes.VisionAgent", return_value=mock_agent):
            result = vision_node(_state())

        assert isinstance(result["stage_timings"]["vision"], float)
        assert result["stage_timings"]["vision"] >= 0


class TestGeneratorNode:
    def _state_with_vision(self, **overrides):
        return _state(vision_result=make_synthesized_vision(success=True), **overrides)

    def test_success_returns_generation_result(self):
        gen = make_generation_result(success=True)
        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(return_value=gen)

        with patch("skyyrose.elite_studio.graph.nodes.GeneratorAgent", return_value=mock_agent):
            result = generator_node(self._state_with_vision())

        assert result["generation_result"] is gen
        assert "generation" in result["stage_timings"]

    def test_no_vision_result_returns_error(self):
        result = generator_node(_state(vision_result=None))
        assert result["status"] == "error"
        assert result["failed_step"] == "generation"

    def test_failed_vision_returns_error(self):
        result = generator_node(_state(vision_result=make_synthesized_vision(success=False)))
        assert result["status"] == "error"

    def test_generation_failure_sets_error(self):
        gen = make_generation_result(success=False, error="Blocked by safety filter")
        mock_agent = MagicMock()
        mock_agent.generate = AsyncMock(return_value=gen)

        with patch("skyyrose.elite_studio.graph.nodes.GeneratorAgent", return_value=mock_agent):
            result = generator_node(self._state_with_vision())

        assert result["status"] == "error"
        assert result["failed_step"] == "generation"


class TestQualityNode:
    def _state_with_gen(self, **overrides):
        return _state(
            vision_result=make_synthesized_vision(success=True),
            generation_result=make_generation_result(success=True),
            **overrides,
        )

    def test_success_returns_quality_result(self):
        qc = make_quality_verification(success=True, recommendation="approve")
        mock_agent = MagicMock()
        mock_agent.verify = AsyncMock(return_value=qc)

        with patch("skyyrose.elite_studio.graph.nodes.QualityAgent", return_value=mock_agent):
            result = quality_node(self._state_with_gen())

        assert result["quality_result"] is qc
        assert "quality" in result["stage_timings"]

    def test_no_generation_returns_error(self):
        result = quality_node(
            _state(generation_result=None, vision_result=make_synthesized_vision())
        )
        assert result["status"] == "error"
        assert result["failed_step"] == "quality"

    def test_failed_generation_returns_error(self):
        result = quality_node(
            _state(
                generation_result=make_generation_result(success=False),
                vision_result=make_synthesized_vision(success=True),
            )
        )
        assert result["status"] == "error"


class TestCompositorNode:
    def test_no_generation_returns_none_compositor(self):
        result = compositor_node(_state(generation_result=None))
        assert result["compositor_result"] is None

    def test_failed_generation_returns_none_compositor(self):
        result = compositor_node(_state(generation_result=make_generation_result(success=False)))
        assert result["compositor_result"] is None

    def test_timing_always_recorded(self):
        result = compositor_node(_state(generation_result=None))
        assert "compositing" in result["stage_timings"]


class TestFinalizeNode:
    def test_requires_qa_approval_even_without_other_error(self):
        result = finalize_node(_state(status="running"))
        assert result["status"] == "error"

    def test_preserves_error_status(self):
        result = finalize_node(_state(status="error"))
        assert result["status"] == "error"
