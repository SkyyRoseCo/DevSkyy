"""In-house typed decision layer (Choice / Score / Noul), no external decision vendor.

Usage::

    from llm.decisions import Choice, DecisionEngine, LogprobBackend, Route
    from llm.providers.openai import OpenAIClient

    engine = DecisionEngine(LogprobBackend(OpenAIClient()))
    result = await engine.decide(
        {"request": text},
        {"tier": Choice(instructions="How hard is this request?",
                        criteria={"simple": "lookup or rewrite", "hard": "multi-step reasoning"})},
    )
    answer = result.answers["tier"]
    if answer.route is Route.SHARP:
        ...  # deterministic cheap path
    else:
        ...  # escalate to the strong model

Calibrate thresholds with ``scripts/decision_calibrate.py`` before relying on SHARP.
"""

from .backend import DecisionBackendError, DistributionBackend, LogprobBackend
from .calibration import CalibrationReport, LabelledCase, calibration_report, run_cases
from .engine import DecisionEngine
from .gate import GatePolicy
from .types import (
    Choice,
    ChoiceAnswer,
    DecisionFailure,
    DecisionResult,
    Noul,
    NoulAnswer,
    Route,
    Score,
    ScoreAnswer,
)

__all__ = [
    "CalibrationReport",
    "Choice",
    "ChoiceAnswer",
    "DecisionBackendError",
    "DecisionEngine",
    "DecisionFailure",
    "DecisionResult",
    "DistributionBackend",
    "GatePolicy",
    "LabelledCase",
    "LogprobBackend",
    "Noul",
    "NoulAnswer",
    "Route",
    "Score",
    "ScoreAnswer",
    "calibration_report",
    "run_cases",
]
