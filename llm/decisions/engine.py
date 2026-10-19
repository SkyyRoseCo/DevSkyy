"""Evaluate named questions against one state, concurrently, failing closed.

Each question is answered independently. A question whose backend call fails comes
back as a ``DecisionFailure`` routed SPLIT; the other answers are kept. Nothing in
this module can turn a failure into a SHARP route.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Mapping
from typing import Any

from .backend import DistributionBackend
from .gate import GatePolicy, build_answer
from .types import Answer, DecisionFailure, DecisionResult, Question

logger = logging.getLogger(__name__)

MAX_STATE_CHARS = 48_000
MAX_QUESTIONS = 32


def serialize_state(state: str | Mapping[str, Any] | list[Any]) -> str:
    """Strings pass through; structured state is rendered as stable JSON."""
    if isinstance(state, str):
        text = state
    else:
        text = json.dumps(state, sort_keys=True, ensure_ascii=False, default=str)
    if not text.strip():
        raise ValueError("state must not be empty")
    if len(text) > MAX_STATE_CHARS:
        raise ValueError(f"state is {len(text)} chars; trim it to {MAX_STATE_CHARS} or fewer")
    return text


class DecisionEngine:
    """Ask typed questions about a state; route each answer SHARP or SPLIT."""

    def __init__(self, backend: DistributionBackend, policy: GatePolicy | None = None) -> None:
        self.backend = backend
        self.policy = policy or GatePolicy()

    async def _answer(self, state: str, question: Question) -> Answer:
        distribution = await self.backend.distribution(
            state, question.instructions, question.options()
        )
        return build_answer(question, distribution, self.policy)

    async def decide(
        self,
        state: str | Mapping[str, Any] | list[Any],
        questions: Mapping[str, Question],
    ) -> DecisionResult:
        if not 1 <= len(questions) <= MAX_QUESTIONS:
            raise ValueError(f"ask 1..{MAX_QUESTIONS} questions, got {len(questions)}")
        text = serialize_state(state)
        names = list(questions)
        outcomes = await asyncio.gather(
            *(self._answer(text, questions[name]) for name in names),
            return_exceptions=True,
        )
        answers: dict[str, Answer] = {}
        for name, outcome in zip(names, outcomes, strict=True):
            if isinstance(outcome, BaseException) and not isinstance(outcome, Exception):
                raise outcome  # cancellation and interpreter exits are not decisions
            if isinstance(outcome, Exception):
                logger.warning("decision %r failed, escalating: %s", name, outcome)
                answers[name] = DecisionFailure(error=f"{type(outcome).__name__}: {outcome}")
            else:
                answers[name] = outcome
        return DecisionResult(answers=answers, model=self.backend.model)
