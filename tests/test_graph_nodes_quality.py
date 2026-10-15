"""
Tests for the Layer 4 dual-QC quality_node and human_review_node.

All external dependencies (CLIP model, Claude API, approval queue) are
mocked so these tests run without any real AI services or network calls.
"""

from __future__ import annotations

from unittest.mock import patch

from skyyrose.elite_studio.models import GenerationResult, QualityVerification, SynthesizedVision
from skyyrose.elite_studio.quality.human_review import ReviewDecision
from skyyrose.elite_studio.quality.ml_classifier import ClassifierResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_state(
    sku: str = "br-001",
    gen_success: bool = True,
    output_path: str = "/tmp/gen.jpg",
    enable_human_review: bool = False,
    human_review_result=None,
    workflow_id: str = "test-workflow",
) -> dict:
    """Build a minimal graph state dict for quality/human_review nodes."""
    vision = SynthesizedVision(
        success=True,
        unified_spec="Black Rose hoodie, gothic aesthetic, luxury streetwear",
        providers_used=("gemini",),
    )
    gen = GenerationResult(
        success=gen_success,
        provider="gemini",
        model="gemini-3-pro",
        output_path=output_path,
    )
    return {
        "sku": sku,
        "view": "front",
        "vision_result": vision,
        "generation_result": gen if gen_success else None,
        "quality_result": None,
        "classifier_result": None,
        "human_review_result": human_review_result,
        "retry_count": 0,
        "max_retries": 2,
        "status": "running",
        "error": "",
        "failed_step": "",
        "workflow_id": workflow_id,
        "stage_timings": {},
        "enable_compositor": False,
        "enable_human_review": enable_human_review,
        "review_confidence_threshold": 0.6,
    }


def _high_confidence_classifier() -> ClassifierResult:
    return ClassifierResult(
        success=True, score=0.9, confidence=0.92, label="high quality fashion photo"
    )


def _low_confidence_classifier() -> ClassifierResult:
    return ClassifierResult(success=True, score=0.5, confidence=0.35, label="uncertain")


def _passing_qc() -> QualityVerification:
    return QualityVerification(
        success=True,
        provider="anthropic",
        model="claude-sonnet",
        overall_status="pass",
        recommendation="approve",
    )


def _failing_qc() -> QualityVerification:
    return QualityVerification(
        success=True,
        provider="anthropic",
        model="claude-sonnet",
        overall_status="fail",
        recommendation="regenerate",
    )


# ---------------------------------------------------------------------------
# quality_node — missing inputs
# ---------------------------------------------------------------------------


class TestQualityNodeMissingInputs:
    def test_returns_error_when_no_generation_result(self):
        from skyyrose.elite_studio.graph.nodes import quality_node

        state = _make_state(gen_success=False)
        state["generation_result"] = None

        result = quality_node(state)

        assert result["status"] == "error"
        assert result["failed_step"] == "quality"

    def test_returns_error_when_generation_failed(self):
        from skyyrose.elite_studio.graph.nodes import quality_node

        state = _make_state()
        state["generation_result"] = GenerationResult(
            success=False, provider="gemini", model="gemini-3-pro", error="API error"
        )

        result = quality_node(state)

        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# quality_node — high-confidence classifier path (no LLM call)
# ---------------------------------------------------------------------------


class TestQualityNodeHighConfidence:
    def test_classifier_pass_requires_dual_vision(self, tmp_path):
        from skyyrose.elite_studio.graph.nodes import quality_node

        img = tmp_path / "gen.jpg"
        img.write_bytes(b"FAKE")
        state = _make_state(output_path=str(img))

        high_conf = _high_confidence_classifier()

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier.predict",
                return_value=high_conf,
            ),
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityAgent.verify",
                return_value=_passing_qc(),
            ) as mock_llm,
        ):
            result = quality_node(state)

        # Classifier confidence cannot replace fidelity evidence.
        mock_llm.assert_called_once()

        assert result["classifier_result"] is high_conf
        assert result["quality_result"] is not None
        qc: QualityVerification = result["quality_result"]
        assert qc == _passing_qc()
        assert qc.overall_status == "pass"
        assert qc.recommendation == "approve"

    def test_classifier_fail_score_produces_regenerate(self, tmp_path):
        from skyyrose.elite_studio.graph.nodes import quality_node

        img = tmp_path / "gen.jpg"
        img.write_bytes(b"FAKE")
        state = _make_state(output_path=str(img))

        # High confidence but low score (label maps to fail)
        low_score = ClassifierResult(
            success=True, score=0.1, confidence=0.95, label="low quality blurry photo"
        )

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier.predict",
                return_value=low_score,
            ),
            patch("skyyrose.elite_studio.graph.nodes.QualityAgent.verify") as mock_llm,
        ):
            result = quality_node(state)

        mock_llm.assert_not_called()
        qc = result["quality_result"]
        assert qc.recommendation == "regenerate"
        assert qc.overall_status == "fail"

    def test_stage_timings_set(self, tmp_path):
        from skyyrose.elite_studio.graph.nodes import quality_node

        img = tmp_path / "gen.jpg"
        img.write_bytes(b"FAKE")
        state = _make_state(output_path=str(img))

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityAgent.verify", return_value=_passing_qc()
            ),
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier.predict",
                return_value=_high_confidence_classifier(),
            ),
        ):
            result = quality_node(state)

        assert "quality" in result["stage_timings"]
        assert result["stage_timings"]["quality"] >= 0.0


# ---------------------------------------------------------------------------
# quality_node — low-confidence classifier path (LLM runs)
# ---------------------------------------------------------------------------


class TestQualityNodeLowConfidence:
    def test_llm_runs_when_classifier_uncertain(self, tmp_path):
        from skyyrose.elite_studio.graph.nodes import quality_node

        img = tmp_path / "gen.jpg"
        img.write_bytes(b"FAKE")
        state = _make_state(output_path=str(img))

        low_conf = _low_confidence_classifier()
        llm_result = _passing_qc()

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier.predict",
                return_value=low_conf,
            ),
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityAgent.verify",
                return_value=llm_result,
            ) as mock_llm,
        ):
            result = quality_node(state)

        mock_llm.assert_called_once()
        assert result["quality_result"] is llm_result
        assert result["classifier_result"] is low_conf

    def test_llm_regenerate_propagated(self, tmp_path):
        from skyyrose.elite_studio.graph.nodes import quality_node

        img = tmp_path / "gen.jpg"
        img.write_bytes(b"FAKE")
        state = _make_state(output_path=str(img))

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier.predict",
                return_value=_low_confidence_classifier(),
            ),
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityAgent.verify",
                return_value=_failing_qc(),
            ),
        ):
            result = quality_node(state)

        assert result["quality_result"].recommendation == "regenerate"


# ---------------------------------------------------------------------------
# human_review_node
# ---------------------------------------------------------------------------


class TestHumanReviewNode:
    def test_returns_error_when_no_generation(self):
        from skyyrose.elite_studio.graph.nodes import human_review_node

        state = _make_state(gen_success=False)
        state["generation_result"] = None

        result = human_review_node(state)

        assert result["status"] == "error"
        assert result["failed_step"] == "human_review"

    def test_approve_decision_stored_in_state(self, tmp_path):
        from skyyrose.elite_studio.graph.nodes import human_review_node

        img = tmp_path / "gen.jpg"
        img.write_bytes(b"FAKE")
        state = _make_state(output_path=str(img))
        state["quality_result"] = _passing_qc()

        approve_decision = ReviewDecision(review_id="rev-1", decision="approve", reviewer="alice")

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.HumanReviewGate.submit_for_review",
                return_value="rev-1",
            ),
            patch(
                "skyyrose.elite_studio.graph.nodes.HumanReviewGate.get_decision",
                return_value=approve_decision,
            ),
        ):
            result = human_review_node(state)

        assert result["human_review_result"] is approve_decision
        # approve: quality_result should NOT be overridden to regenerate
        assert (
            "quality_result" not in result
            or result.get("quality_result") is None
            or result.get("quality_result", _passing_qc()).recommendation != "regenerate"
        )

    def test_reject_decision_overrides_qc_to_regenerate(self, tmp_path):
        from skyyrose.elite_studio.graph.nodes import human_review_node

        img = tmp_path / "gen.jpg"
        img.write_bytes(b"FAKE")
        state = _make_state(output_path=str(img))
        state["quality_result"] = _passing_qc()

        reject_decision = ReviewDecision(
            review_id="rev-2", decision="reject", reviewer="bob", notes="wrong colour"
        )

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.HumanReviewGate.submit_for_review",
                return_value="rev-2",
            ),
            patch(
                "skyyrose.elite_studio.graph.nodes.HumanReviewGate.get_decision",
                return_value=reject_decision,
            ),
        ):
            result = human_review_node(state)

        assert result["human_review_result"] is reject_decision
        assert result["quality_result"].recommendation == "regenerate"
        assert result["quality_result"].overall_status == "fail"
        assert result["quality_result"].details.get("human_rejected") is True

    def test_stage_timings_set(self, tmp_path):
        from skyyrose.elite_studio.graph.nodes import human_review_node

        img = tmp_path / "gen.jpg"
        img.write_bytes(b"FAKE")
        state = _make_state(output_path=str(img))

        approve_decision = ReviewDecision(review_id="rev-3", decision="approve", reviewer="carol")

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.HumanReviewGate.submit_for_review",
                return_value="auto-approve:test",
            ),
            patch(
                "skyyrose.elite_studio.graph.nodes.HumanReviewGate.get_decision",
                return_value=approve_decision,
            ),
        ):
            result = human_review_node(state)

        assert "human_review" in result["stage_timings"]
        assert result["stage_timings"]["human_review"] >= 0.0


# ---------------------------------------------------------------------------
# after_quality_v2 edge function
# ---------------------------------------------------------------------------


class TestAfterQualityV2:
    def test_routes_to_human_review_when_low_confidence_and_enabled(self):
        from skyyrose.elite_studio.graph.edges import after_quality_v2

        state = _make_state(enable_human_review=True)
        state["classifier_result"] = ClassifierResult(
            success=True, score=0.5, confidence=0.4, label="uncertain"
        )
        state["quality_result"] = _passing_qc()
        state["human_review_result"] = None

        assert after_quality_v2(state) == "human_review"

    def test_skips_human_review_when_disabled(self):
        from skyyrose.elite_studio.graph.edges import after_quality_v2

        state = _make_state(enable_human_review=False)
        state["classifier_result"] = ClassifierResult(
            success=True, score=0.5, confidence=0.4, label="uncertain"
        )
        state["quality_result"] = _passing_qc()

        result = after_quality_v2(state)
        assert result != "human_review"

    def test_routes_to_generator_when_regenerate_and_retries_left(self):
        from skyyrose.elite_studio.graph.edges import after_quality_v2

        state = _make_state()
        state["classifier_result"] = _high_confidence_classifier()
        state["quality_result"] = _failing_qc()  # recommendation = regenerate
        state["retry_count"] = 0
        state["max_retries"] = 2
        state["human_review_result"] = None

        assert after_quality_v2(state) == "generator"

    def test_routes_to_finalize_when_no_retries_left(self):
        from skyyrose.elite_studio.graph.edges import after_quality_v2

        state = _make_state()
        state["classifier_result"] = _high_confidence_classifier()
        state["quality_result"] = _failing_qc()
        state["retry_count"] = 2
        state["max_retries"] = 2
        state["human_review_result"] = None
        state["enable_compositor"] = False

        assert after_quality_v2(state) == "finalize"

    def test_routes_to_compositor_when_enabled(self):
        from skyyrose.elite_studio.graph.edges import after_quality_v2

        state = _make_state()
        state["enable_compositor"] = True
        state["classifier_result"] = _high_confidence_classifier()
        state["quality_result"] = _passing_qc()
        state["retry_count"] = 0
        state["max_retries"] = 2
        state["human_review_result"] = None

        assert after_quality_v2(state) == "compositor"

    def test_skips_human_review_when_already_reviewed(self):
        from skyyrose.elite_studio.graph.edges import after_quality_v2

        state = _make_state(enable_human_review=True)
        state["classifier_result"] = ClassifierResult(
            success=True, score=0.5, confidence=0.4, label="uncertain"
        )
        state["quality_result"] = _passing_qc()
        # Already reviewed — should not loop back
        state["human_review_result"] = ReviewDecision(
            review_id="rev-done", decision="approve", reviewer="dave"
        )

        result = after_quality_v2(state)
        assert result != "human_review"
