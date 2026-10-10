"""
Tests for QualityClassifier — CLIP-based fast quality predictor.

All CLIP model calls are mocked so tests run without transformers installed.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from math import exp, log
from unittest.mock import MagicMock, patch

import pytest

from skyyrose.elite_studio.quality.ml_classifier import (
    _CANDIDATE_LABELS,
    _LABEL_SCORES,
    ClassifierResult,
    QualityClassifier,
)

# ---------------------------------------------------------------------------
# ClassifierResult dataclass
# ---------------------------------------------------------------------------


class TestClassifierResult:
    def test_frozen(self):
        result = ClassifierResult(success=True, score=0.9, confidence=0.95, label="high quality")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            result.score = 0.1  # type: ignore[misc]

    def test_default_error_empty(self):
        result = ClassifierResult(success=True, score=0.5, confidence=0.5, label="test")
        assert result.error == ""

    def test_all_fields_accessible(self):
        result = ClassifierResult(
            success=False, score=0.0, confidence=0.0, label="error", error="boom"
        )
        assert result.success is False
        assert result.score == 0.0
        assert result.error == "boom"


# ---------------------------------------------------------------------------
# Fallback behaviour (transformers not installed)
# ---------------------------------------------------------------------------


class TestClassifierFallback:
    def test_returns_neutral_result_when_transformers_missing(self, tmp_path):
        """When transformers is not importable the classifier returns a safe fallback."""
        # Create a dummy image file so predict() doesn't fail on file-not-found
        img = tmp_path / "test.jpg"
        img.write_bytes(b"FAKEJPEG")

        classifier = QualityClassifier()

        with patch(
            "skyyrose.elite_studio.quality.ml_classifier._load_clip_model",
            side_effect=ImportError("No module named 'transformers'"),
        ):
            result = classifier.predict(str(img))

        assert result.success is True
        assert result.score == 0.5
        assert result.confidence == 0.3
        assert result.label == "uncertain"
        assert result.error == ""

    def test_returns_error_result_on_generic_exception(self, tmp_path):
        img = tmp_path / "test.jpg"
        img.write_bytes(b"FAKEJPEG")

        classifier = QualityClassifier()

        with patch(
            "skyyrose.elite_studio.quality.ml_classifier.QualityClassifier._run_clip",
            side_effect=RuntimeError("GPU exploded"),
        ):
            result = classifier.predict(str(img))

        assert result.success is False
        assert "GPU exploded" in result.error
        assert result.score == 0.0


# ---------------------------------------------------------------------------
# CLIP inference (mocked)
# ---------------------------------------------------------------------------


class TestClassifierWithMockCLIP:
    def _mock_clip_call(self, logits: list[float], image_path: str) -> ClassifierResult:
        """Exercise classifier scoring without loading optional ML libraries."""
        mock_model = MagicMock()
        mock_processor = MagicMock()

        # processor returns a mock that model can accept
        mock_inputs = MagicMock()
        mock_processor.return_value = mock_inputs

        # Only the external tensor operations are mocked. The real classifier
        # still selects the label, calculates confidence, and weights the score.
        weights = [exp(value - max(logits)) for value in logits]
        probabilities = [value / sum(weights) for value in weights]
        prob_tensor = MagicMock()
        prob_tensor.tolist.return_value = probabilities
        prob_tensor.argmax.return_value.item.return_value = probabilities.index(max(probabilities))
        mock_output = MagicMock()
        mock_output.logits_per_image.softmax.return_value.squeeze.return_value = prob_tensor
        mock_model.return_value = mock_output

        classifier = QualityClassifier()

        with (
            patch.dict("sys.modules", {"torch": MagicMock()}),
            patch(
                "skyyrose.elite_studio.quality.ml_classifier._load_clip_model",
                return_value=(mock_model, mock_processor),
            ),
            patch(
                "PIL.Image.open",
                return_value=MagicMock(convert=MagicMock(return_value=MagicMock())),
            ),
        ):
            return classifier.predict(image_path)

    def test_high_quality_label_gives_high_score(self, tmp_path):
        img = tmp_path / "good.jpg"
        img.write_bytes(b"FAKE")

        # Use large logit gap so softmax strongly favours index 0.
        # softmax([100, 0, 0]) ≈ [1.0, 0.0, 0.0]
        logits = [100.0, 0.0, 0.0]
        result = self._mock_clip_call(logits, str(img))

        assert result.success is True
        assert result.score > 0.7
        assert result.confidence > 0.99
        assert result.label == _CANDIDATE_LABELS[0]

    def test_low_quality_label_gives_low_score(self, tmp_path):
        img = tmp_path / "bad.jpg"
        img.write_bytes(b"FAKE")

        # softmax([0, 100, 0]) ≈ [0.0, 1.0, 0.0]
        logits = [0.0, 100.0, 0.0]
        result = self._mock_clip_call(logits, str(img))

        assert result.success is True
        assert result.score < 0.4
        assert result.label == _CANDIDATE_LABELS[1]

    def test_inappropriate_label_gives_zero_score(self, tmp_path):
        img = tmp_path / "bad2.jpg"
        img.write_bytes(b"FAKE")

        # softmax([0, 0, 100]) ≈ [0.0, 0.0, 1.0]
        logits = [0.0, 0.0, 100.0]
        result = self._mock_clip_call(logits, str(img))

        assert result.success is True
        assert result.score < 0.05  # _LABEL_SCORES["inappropriate content"] == 0.0
        assert result.label == _CANDIDATE_LABELS[2]

    def test_score_clamped_between_0_and_1(self, tmp_path):
        img = tmp_path / "clamp.jpg"
        img.write_bytes(b"FAKE")

        # All weight on high quality
        logits = [100.0, 0.0, 0.0]
        result = self._mock_clip_call(logits, str(img))

        assert 0.0 <= result.score <= 1.0

    def test_weighted_score_matches_formula(self, tmp_path):
        """Verify the weighted score formula using _run_clip directly with known post-softmax probs."""
        img = tmp_path / "weight.jpg"
        img.write_bytes(b"FAKE")

        known_probs = [0.6, 0.3, 0.1]  # desired post-softmax values
        expected = (
            0.6 * _LABEL_SCORES["high quality fashion photo"]
            + 0.3 * _LABEL_SCORES["low quality blurry photo"]
            + 0.1 * _LABEL_SCORES["inappropriate content"]
        )
        # Log-probabilities recover the known distribution through softmax.
        # Keep _run_clip real so this fails if its weighted formula regresses.
        result = self._mock_clip_call([log(prob) for prob in known_probs], str(img))

        assert result.success is True
        assert result.score == pytest.approx(expected, abs=0.001)
