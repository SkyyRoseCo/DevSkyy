"""Turn a probability distribution into a typed, routed answer.

Pure functions, no I/O. Thresholds are policy: the defaults are deliberately strict
placeholders until ``calibration.py`` measures real ones on a labelled set. Published
results for this design (REFLEX, arXiv 2609.26532) found wrong answers with a mean
confidence of 0.778, so a gate near 0.7 still lets confident mistakes through.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .types import (
    ChoiceAnswer,
    Noul,
    NoulAnswer,
    Question,
    Route,
    Score,
    ScoreAnswer,
)


class GatePolicy(BaseModel):
    """Confidence needed before code may act on an answer without escalating.

    ``min_confidence`` applies to Choice and Score (probability of the top option).
    A Noul is SHARP only outside the deadband: ``noul >= noul_yes`` or
    ``noul <= noul_no``. Everything between abstains to SPLIT. The bounds keep the
    deadband non-empty (``noul_no < 0.5 < noul_yes``).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    min_confidence: float = Field(default=0.9, gt=0.5, le=1.0)
    noul_yes: float = Field(default=0.9, gt=0.5, le=1.0)
    noul_no: float = Field(default=0.1, ge=0.0, lt=0.5)


def _top(distribution: dict[str, float]) -> tuple[str, float]:
    key = max(distribution, key=lambda option: (distribution[option], option))
    return key, distribution[key]


def _route(confident: bool) -> Route:
    return Route.SHARP if confident else Route.SPLIT


def build_answer(
    question: Question,
    distribution: dict[str, float],
    policy: GatePolicy,
) -> ChoiceAnswer | ScoreAnswer | NoulAnswer:
    """Shape a normalized distribution over ``question.options()`` keys into an answer."""
    expected = {key for key, _ in question.options()}
    if set(distribution) != expected:
        raise ValueError("distribution keys do not match the question's options")
    if isinstance(question, Noul):
        noul = distribution["true"]
        confident = noul >= policy.noul_yes or noul <= policy.noul_no
        return NoulAnswer(noul=noul, route=_route(confident))
    key, confidence = _top(distribution)
    confident = confidence >= policy.min_confidence
    if isinstance(question, Score):
        score = sum(int(level) * p for level, p in distribution.items())
        return ScoreAnswer(
            score=score,
            level=int(key),
            confidence=confidence,
            probabilities=distribution,
            route=_route(confident),
        )
    return ChoiceAnswer(
        choice=key,
        confidence=confidence,
        probabilities=distribution,
        route=_route(confident),
    )
