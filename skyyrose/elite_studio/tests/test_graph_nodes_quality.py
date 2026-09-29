"""
Tests for the dual-QC quality_node and human_review_node.

Tests cover:
- quality_node: high-confidence classifier → skip LLM (pass path)
- quality_node: low-confidence classifier → LLM QC called (uncertain path)
- quality_node: missing generation result → error state
- quality_node: classifier result stored in state
- human_review_node: approve decision propagates
- human_review_node: reject decision overrides quality_result recommendation
- human_review_node: missing generation result → error state
- after_quality_v2 edge routing: human_review, regenerate, compositor, finalize
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from skyyrose.elite_studio.graph.edges import after_quality_v2
from skyyrose.elite_studio.graph.nodes import human_review_node, quality_node
from skyyrose.elite_studio.graph.state import create_initial_state
from skyyrose.elite_studio.models import GenerationResult, QualityVerification, SynthesizedVision
from skyyrose.elite_studio.quality.human_review import ReviewDecision
from skyyrose.elite_studio.quality.ml_classifier import ClassifierResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_state(
    sku: str = "br-001",
    has_generation: bool = True,
    has_vision: bool = True,
    gen_success: bool = True,
    gen_path: str = "/tmp/br-001-front.jpg",
    classifier_result: ClassifierResult | None = None,
    quality_result: QualityVerification | None = None,
    human_review_result: ReviewDecision | None = None,
    retry_count: int = 0,
    max_retries: int = 2,
    enable_compositor: bool = False,
    enable_human_review: bool = False,
    review_confidence_threshold: float = 0.6,
) -> dict:
    """Create a minimal test state dict."""
    state = create_initial_state(sku=sku)
    state = dict(state)

    if has_generation:
        state["generation_result"] = GenerationResult(
            success=gen_success,
            provider="google",
            model="gemini-3-pro-image-preview",
            output_path=gen_path if gen_success else "",
        )
    if has_vision:
        state["vision_result"] = SynthesizedVision(
            success=True,
            unified_spec="A fashion product image showing br-001 crewneck",
            providers_used=("gemini",),
        )

    if classifier_result is not None:
        state["classifier_result"] = classifier_result
    if quality_result is not None:
        state["quality_result"] = quality_result
    if human_review_result is not None:
        state["human_review_result"] = human_review_result

    state["retry_count"] = retry_count
    state["max_retries"] = max_retries
    state["enable_compositor"] = enable_compositor
    state["enable_human_review"] = enable_human_review
    state["review_confidence_threshold"] = review_confidence_threshold
    return state


def _high_confidence_result(passed: bool = True) -> ClassifierResult:
    return ClassifierResult(
        success=True,
        score=0.9 if passed else 0.1,
        confidence=0.95,
        label="high quality fashion photo" if passed else "low quality blurry photo",
    )


def _low_confidence_result() -> ClassifierResult:
    return ClassifierResult(
        success=True,
        score=0.5,
        confidence=0.3,
        label="uncertain",
    )


# ---------------------------------------------------------------------------
# quality_node: missing prerequisite
# ---------------------------------------------------------------------------


class TestQualityNodePrerequisites:
    def test_no_generation_result_returns_error(self):
        state = _make_state(has_generation=False)
        result = quality_node(state)
        assert result["status"] == "error"
        assert result["failed_step"] == "quality"

    def test_generation_failed_returns_error(self):
        state = _make_state(gen_success=False)
        result = quality_node(state)
        assert result["status"] == "error"
        assert result["failed_step"] == "quality"

    def test_no_vision_result_returns_error(self):
        state = _make_state(has_vision=False, has_generation=True)
        result = quality_node(state)
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# quality_node: high-confidence classifier → skip LLM
# ---------------------------------------------------------------------------


class TestQualityNodeHighConfidence:
    def test_high_confidence_requires_dual_vision(self):
        """A classifier cannot supply exact product fidelity evidence."""
        state = _make_state()

        mock_classifier = MagicMock()
        mock_classifier.predict.return_value = _high_confidence_result(passed=True)

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier", return_value=mock_classifier
            ),
            patch("skyyrose.elite_studio.graph.nodes.QualityAgent") as mock_llm_cls,
        ):
            mock_llm_cls.return_value.verify = AsyncMock(
                return_value=QualityVerification(
                    success=True,
                    provider="dual_vision",
                    overall_status="pass",
                    recommendation="approve",
                )
            )
            result = quality_node(state)
            mock_llm_cls.return_value.verify.assert_called_once()

        assert "classifier_result" in result
        assert result["classifier_result"].confidence >= 0.8

    def test_high_confidence_pass_sets_approve(self):
        state = _make_state()
        mock_classifier = MagicMock()
        mock_classifier.predict.return_value = _high_confidence_result(passed=True)

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier", return_value=mock_classifier
            ),
            patch("skyyrose.elite_studio.graph.nodes.QualityAgent") as mock_llm_cls,
        ):
            mock_llm_cls.return_value.verify = AsyncMock(
                return_value=QualityVerification(
                    success=True,
                    provider="dual_vision",
                    overall_status="pass",
                    recommendation="approve",
                )
            )
            result = quality_node(state)

        qc = result.get("quality_result")
        assert qc is not None
        assert qc.recommendation == "approve"
        assert qc.overall_status == "pass"

    def test_high_confidence_fail_sets_regenerate(self):
        state = _make_state()
        mock_classifier = MagicMock()
        mock_classifier.predict.return_value = _high_confidence_result(passed=False)

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier", return_value=mock_classifier
            ),
            patch("skyyrose.elite_studio.graph.nodes.QualityAgent") as mock_llm_cls,
        ):
            mock_llm_cls.return_value.verify = AsyncMock(
                return_value=QualityVerification(
                    success=True,
                    provider="dual_vision",
                    overall_status="pass",
                    recommendation="approve",
                )
            )
            result = quality_node(state)

        qc = result.get("quality_result")
        assert qc is not None
        assert qc.recommendation == "regenerate"
        assert qc.overall_status == "fail"

    def test_classifier_result_stored_in_state(self):
        state = _make_state()
        expected_classifier = _high_confidence_result()
        mock_classifier = MagicMock()
        mock_classifier.predict.return_value = expected_classifier

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier", return_value=mock_classifier
            ),
            patch("skyyrose.elite_studio.graph.nodes.QualityAgent") as mock_llm_cls,
        ):
            mock_llm_cls.return_value.verify = AsyncMock(
                return_value=QualityVerification(
                    success=True,
                    provider="dual_vision",
                    overall_status="pass",
                    recommendation="approve",
                )
            )
            result = quality_node(state)

        assert result["classifier_result"] == expected_classifier


# ---------------------------------------------------------------------------
# quality_node: low-confidence classifier → LLM called
# ---------------------------------------------------------------------------


class TestQualityNodeLowConfidence:
    def test_low_confidence_triggers_llm(self):
        """When classifier.confidence < 0.8, QualityAgent should be invoked."""
        state = _make_state()

        mock_classifier = MagicMock()
        mock_classifier.predict.return_value = _low_confidence_result()

        mock_qc = QualityVerification(
            success=True,
            provider="anthropic",
            model="claude-sonnet-4",
            overall_status="pass",
            recommendation="approve",
        )
        mock_llm = MagicMock()
        mock_llm.verify = AsyncMock(return_value=mock_qc)

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier", return_value=mock_classifier
            ),
            patch("skyyrose.elite_studio.graph.nodes.QualityAgent", return_value=mock_llm),
        ):
            result = quality_node(state)
            mock_llm.verify.assert_called_once()

        assert result["quality_result"].provider == "anthropic"

    def test_low_confidence_still_stores_classifier_result(self):
        state = _make_state()
        low_conf = _low_confidence_result()
        mock_classifier = MagicMock()
        mock_classifier.predict.return_value = low_conf

        mock_llm = MagicMock()
        mock_llm.verify = AsyncMock(
            return_value=QualityVerification(
                success=True,
                provider="anthropic",
                model="claude-sonnet-4",
                overall_status="pass",
                recommendation="approve",
            )
        )

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier", return_value=mock_classifier
            ),
            patch("skyyrose.elite_studio.graph.nodes.QualityAgent", return_value=mock_llm),
        ):
            result = quality_node(state)

        assert result["classifier_result"] == low_conf

    def test_stage_timings_updated(self):
        state = _make_state()
        mock_classifier = MagicMock()
        mock_classifier.predict.return_value = _high_confidence_result()

        with (
            patch(
                "skyyrose.elite_studio.graph.nodes.QualityClassifier", return_value=mock_classifier
            ),
            patch("skyyrose.elite_studio.graph.nodes.QualityAgent") as mock_qa,
        ):
            mock_qa.return_value.verify = AsyncMock(
                return_value=QualityVerification(
                    success=False, overall_status="fail", recommendation="manual_review"
                )
            )
            result = quality_node(state)

        assert "quality" in result.get("stage_timings", {})


# ---------------------------------------------------------------------------
# human_review_node
# ---------------------------------------------------------------------------


class TestHumanReviewNode:
    def test_no_generation_returns_error(self):
        state = _make_state(has_generation=False)
        result = human_review_node(state)
        assert result["status"] == "error"
        assert result["failed_step"] == "human_review"

    def test_approve_decision_stored(self):
        state = _make_state()
        state["workflow_id"] = "job-test-1"

        mock_gate = MagicMock()
        mock_gate.submit_for_review.return_value = "review-001"
        mock_gate.get_decision.return_value = ReviewDecision(
            review_id="review-001", decision="approve", reviewer="alice"
        )

        with patch("skyyrose.elite_studio.graph.nodes.HumanReviewGate", return_value=mock_gate):
            result = human_review_node(state)

        decision = result.get("human_review_result")
        assert decision is not None
        assert decision.decision == "approve"
        assert decision.reviewer == "alice"

    def test_reject_overrides_quality_recommendation(self):
        """Reviewer reject should update quality_result.recommendation to 'regenerate'."""
        existing_qc = QualityVerification(
            success=True,
            provider="anthropic",
            model="claude-sonnet-4",
            overall_status="pass",
            recommendation="approve",
        )
        state = _make_state(quality_result=existing_qc)

        mock_gate = MagicMock()
        mock_gate.submit_for_review.return_value = "review-002"
        mock_gate.get_decision.return_value = ReviewDecision(
            review_id="review-002", decision="reject", reviewer="bob", notes="wrong colors"
        )

        with patch("skyyrose.elite_studio.graph.nodes.HumanReviewGate", return_value=mock_gate):
            result = human_review_node(state)

        updated_qc = result.get("quality_result")
        assert updated_qc is not None
        assert updated_qc.recommendation == "regenerate"
        assert updated_qc.overall_status == "fail"
        assert result["human_review_result"].decision == "reject"

    def test_reject_notes_propagated(self):
        existing_qc = QualityVerification(
            success=True,
            provider="anthropic",
            model="claude-sonnet-4",
            overall_status="pass",
            recommendation="approve",
        )
        state = _make_state(quality_result=existing_qc)

        mock_gate = MagicMock()
        mock_gate.submit_for_review.return_value = "review-003"
        mock_gate.get_decision.return_value = ReviewDecision(
            review_id="review-003", decision="reject", reviewer="carol", notes="bad lighting"
        )

        with patch("skyyrose.elite_studio.graph.nodes.HumanReviewGate", return_value=mock_gate):
            result = human_review_node(state)

        updated_qc = result.get("quality_result")
        assert "bad lighting" in updated_qc.details.get("notes", "")

    def test_stage_timings_include_human_review(self):
        state = _make_state()

        mock_gate = MagicMock()
        mock_gate.submit_for_review.return_value = "review-004"
        mock_gate.get_decision.return_value = ReviewDecision(
            review_id="review-004", decision="approve", reviewer="system"
        )

        with patch("skyyrose.elite_studio.graph.nodes.HumanReviewGate", return_value=mock_gate):
            result = human_review_node(state)

        assert "human_review" in result.get("stage_timings", {})


# ---------------------------------------------------------------------------
# after_quality_v2 edge routing
# ---------------------------------------------------------------------------


class TestAfterQualityV2:
    def test_low_confidence_with_human_review_enabled_routes_to_human_review(self):
        state = _make_state(
            enable_human_review=True,
            review_confidence_threshold=0.6,
            classifier_result=ClassifierResult(
                success=True, score=0.5, confidence=0.3, label="uncertain"
            ),
        )
        # No human review yet, no QC recommendation to regenerate
        state["quality_result"] = QualityVerification(
            success=True,
            provider="clip",
            model="clip",
            overall_status="unknown",
            recommendation="approve",
        )
        result = after_quality_v2(state)
        assert result == "human_review"

    def test_already_reviewed_skips_human_review(self):
        state = _make_state(
            enable_human_review=True,
            classifier_result=ClassifierResult(
                success=True, score=0.5, confidence=0.2, label="uncertain"
            ),
            human_review_result=ReviewDecision(
                review_id="r1", decision="approve", reviewer="alice"
            ),
        )
        state["quality_result"] = QualityVerification(
            success=True,
            provider="clip",
            model="clip",
            overall_status="pass",
            recommendation="approve",
        )
        result = after_quality_v2(state)
        # Should not go to human_review again
        assert result != "human_review"

    def test_regenerate_routes_to_generator(self):
        state = _make_state(retry_count=0, max_retries=2)
        state["quality_result"] = QualityVerification(
            success=True,
            provider="anthropic",
            model="claude-sonnet-4",
            overall_status="fail",
            recommendation="regenerate",
        )
        result = after_quality_v2(state)
        assert result == "generator"

    def test_regenerate_exhausted_retries_routes_to_finalize(self):
        state = _make_state(retry_count=2, max_retries=2)
        state["quality_result"] = QualityVerification(
            success=True,
            provider="anthropic",
            model="claude-sonnet-4",
            overall_status="fail",
            recommendation="regenerate",
        )
        result = after_quality_v2(state)
        assert result == "finalize"

    def test_approve_with_compositor_routes_to_compositor(self):
        state = _make_state(enable_compositor=True)
        state["quality_result"] = QualityVerification(
            success=True,
            provider="anthropic",
            model="claude-sonnet-4",
            overall_status="pass",
            recommendation="approve",
        )
        result = after_quality_v2(state)
        assert result == "compositor"

    def test_approve_without_compositor_routes_to_finalize(self):
        state = _make_state(enable_compositor=False)
        state["quality_result"] = QualityVerification(
            success=True,
            provider="anthropic",
            model="claude-sonnet-4",
            overall_status="pass",
            recommendation="approve",
        )
        result = after_quality_v2(state)
        assert result == "finalize"

    def test_high_confidence_no_human_review_enabled_routes_to_finalize(self):
        state = _make_state(
            enable_human_review=False,
            classifier_result=ClassifierResult(
                success=True, score=0.9, confidence=0.95, label="high quality fashion photo"
            ),
        )
        state["quality_result"] = QualityVerification(
            success=True,
            provider="clip",
            model="clip",
            overall_status="pass",
            recommendation="approve",
        )
        result = after_quality_v2(state)
        assert result == "finalize"

    def test_no_classifier_result_no_human_review_routes_normally(self):
        state = _make_state()
        state["quality_result"] = QualityVerification(
            success=True,
            provider="anthropic",
            model="claude-sonnet-4",
            overall_status="pass",
            recommendation="approve",
        )
        result = after_quality_v2(state)
        assert result == "finalize"
