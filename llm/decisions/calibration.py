"""Measure whether a decision backend's probabilities mean anything.

Run labelled cases through the backend, then report accuracy, expected calibration
error (ECE), and the lowest confidence threshold that reaches a target precision.
A threshold is only recommended when enough cases clear it; otherwise the report
says ``None`` and every answer should stay SPLIT.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .backend import DistributionBackend
from .engine import serialize_state
from .types import Question

ECE_BINS = 10
GATE_FLOOR = 0.5  # GatePolicy thresholds must exceed this


class LabelledCase(BaseModel):
    """One question about one state, with the option key a person judged correct."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    state: str | dict[str, Any] | list[Any]
    question: Question
    expected: str

    @model_validator(mode="after")
    def _expected_is_an_option(self) -> LabelledCase:
        if self.expected not in {key for key, _ in self.question.options()}:
            raise ValueError(f"expected {self.expected!r} is not one of the question's options")
        return self

    @property
    def shape(self) -> str:
        """Calibration group: confidences are only comparable within one shape."""
        return f"{self.question.type}/{len(self.question.options())}"


class CaseRecord(BaseModel):
    """What the backend predicted for one case."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    predicted: str | None
    confidence: float = Field(..., ge=0.0, le=1.0)
    correct: bool
    error: str | None = None


class CalibrationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    cases: int
    failures: int
    accuracy: float
    ece: float
    target_precision: float
    min_support: int
    recommended_threshold: float | None
    sharp_rate_at_threshold: float


async def _record(backend: DistributionBackend, case: LabelledCase) -> CaseRecord:
    try:
        distribution = await backend.distribution(
            serialize_state(case.state), case.question.instructions, case.question.options()
        )
        predicted = max(distribution, key=lambda key: (distribution[key], key))
        return CaseRecord(
            predicted=predicted,
            confidence=distribution[predicted],
            correct=predicted == case.expected,
        )
    except Exception as exc:  # a failed case counts against the backend, never for it
        return CaseRecord(predicted=None, confidence=0.0, correct=False, error=str(exc))


async def run_cases(
    backend: DistributionBackend, cases: Sequence[LabelledCase], concurrency: int = 4
) -> list[CaseRecord]:
    """Evaluate cases with bounded concurrency. Each case is a paid backend call."""
    if concurrency < 1:
        raise ValueError("concurrency must be >= 1")
    limit = asyncio.Semaphore(concurrency)

    async def bounded(case: LabelledCase) -> CaseRecord:
        async with limit:
            return await _record(backend, case)

    return list(await asyncio.gather(*(bounded(case) for case in cases)))


def expected_calibration_error(records: Sequence[CaseRecord], bins: int = ECE_BINS) -> float:
    """Weighted mean gap between confidence and accuracy across confidence bins.

    Only answered cases count; failures are reported separately, so a backend that
    mostly errors cannot look well calibrated.
    """
    records = [r for r in records if r.predicted is not None]
    if not records:
        return 0.0
    total = 0.0
    for index in range(bins):
        low, high = index / bins, (index + 1) / bins
        members = [
            r for r in records if low < r.confidence <= high or (index == 0 and r.confidence == 0)
        ]
        if members:
            accuracy = sum(r.correct for r in members) / len(members)
            confidence = sum(r.confidence for r in members) / len(members)
            total += len(members) / len(records) * abs(accuracy - confidence)
    return total


def recommend_threshold(
    records: Sequence[CaseRecord], target_precision: float, min_support: int
) -> float | None:
    """Lowest confidence whose cleared cases reach ``target_precision``, else None.

    Only thresholds above 0.5 are candidates: ``GatePolicy`` accepts nothing lower.
    """
    answered = {r.confidence for r in records if r.predicted is not None}
    for threshold in sorted(c for c in answered if c > GATE_FLOOR):
        cleared = [r for r in records if r.predicted is not None and r.confidence >= threshold]
        if len(cleared) < min_support:
            return None
        if sum(r.correct for r in cleared) / len(cleared) >= target_precision:
            return threshold
    return None


def calibration_report(
    records: Sequence[CaseRecord], target_precision: float = 0.95, min_support: int = 30
) -> CalibrationReport:
    if not records:
        raise ValueError("no records to report on")
    if not 0.5 < target_precision <= 1.0 or min_support < 1:
        raise ValueError("target_precision must be in (0.5, 1] and min_support >= 1")
    threshold = recommend_threshold(records, target_precision, min_support)
    cleared = 0 if threshold is None else sum(r.confidence >= threshold for r in records)
    return CalibrationReport(
        cases=len(records),
        failures=sum(r.error is not None for r in records),
        accuracy=sum(r.correct for r in records) / len(records),
        ece=expected_calibration_error(records),
        target_precision=target_precision,
        min_support=min_support,
        recommended_threshold=threshold,
        sharp_rate_at_threshold=cleared / len(records),
    )
