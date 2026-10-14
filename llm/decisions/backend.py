"""Probability distributions from first-token log probabilities.

The model is shown the options as letters (A, B, ...) and asked for one letter. The
distribution is read from the top log probabilities of that single output token, not
from a confidence number the model writes about itself. Probability mass on tokens
that are not a valid letter is dropped; if too little valid mass remains the call
fails rather than guessing.

Language models favour options by position. ``debias_order`` asks twice, the second
time with the options reversed, and averages the two distributions.

Each ``distribution`` call is one or two paid API requests.
"""

from __future__ import annotations

import math
import string
from collections.abc import Sequence
from typing import Any, Protocol

from llm.base import BaseLLMClient, Message
from llm.model_ids import OPENAI_MINI_MODEL

LETTERS = string.ascii_uppercase
TOP_LOGPROBS = 20  # API maximum

SYSTEM_PROMPT = (
    "You make exactly one decision about the STATE. Read the QUESTION and the lettered "
    "OPTIONS, then reply with the single letter of the best option and nothing else."
)


class DecisionBackendError(Exception):
    """A distribution could not be produced. Callers must escalate, never guess."""


class DistributionBackend(Protocol):
    """Anything that turns a question into a probability per option key."""

    model: str

    async def distribution(
        self, state: str, instructions: str, options: Sequence[tuple[str, str]]
    ) -> dict[str, float]: ...


def render_prompt(state: str, instructions: str, options: Sequence[tuple[str, str]]) -> str:
    """User message listing the options as letters in the given order."""
    lines = [f"{LETTERS[i]}. {meaning}" for i, (_, meaning) in enumerate(options)]
    return f"STATE:\n{state}\n\nQUESTION:\n{instructions}\n\nOPTIONS:\n" + "\n".join(lines)


def letter_mass(raw: dict[str, Any], letters: str) -> dict[str, float]:
    """Sum probability per valid letter from the first output token's top logprobs."""
    try:
        top = raw["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
    except (KeyError, IndexError, TypeError) as exc:
        raise DecisionBackendError("response carries no first-token logprobs") from exc
    mass = dict.fromkeys(letters, 0.0)
    for entry in top:
        token = str(entry.get("token", "")).strip().upper()
        if token in mass:
            mass[token] += math.exp(_checked_logprob(entry.get("logprob")))
    return mass


def _checked_logprob(value: Any) -> float:
    """A log probability is a finite real number <= 0; anything else is a bad response."""
    if type(value) not in (int, float) or not math.isfinite(value) or value > 0:
        raise DecisionBackendError(f"malformed logprob {value!r}")
    return float(value)


def normalize(mass: dict[str, float], min_coverage: float) -> dict[str, float]:
    """Normalize to 1.0, refusing when valid letters hold too little mass."""
    coverage = sum(mass.values())
    if coverage < min_coverage:
        raise DecisionBackendError(
            f"valid options hold {coverage:.2f} of probability mass (< {min_coverage})"
        )
    return {key: value / coverage for key, value in mass.items()}


class LogprobBackend:
    """OpenAI-compatible chat backend reading first-token logprobs."""

    def __init__(
        self,
        client: BaseLLMClient,
        model: str = OPENAI_MINI_MODEL,
        *,
        min_coverage: float = 0.5,
        debias_order: bool = True,
    ) -> None:
        if not 0.0 < min_coverage <= 1.0:
            raise ValueError("min_coverage must be in (0, 1]")
        self.client = client
        self.model = model
        self.min_coverage = min_coverage
        self.debias_order = debias_order

    async def _ask(
        self, state: str, instructions: str, options: Sequence[tuple[str, str]]
    ) -> dict[str, float]:
        letters = LETTERS[: len(options)]
        response = await self.client.complete(
            messages=[
                Message.system(SYSTEM_PROMPT),
                Message.user(render_prompt(state, instructions, options)),
            ],
            model=self.model,
            temperature=0.0,
            max_tokens=1,
            logprobs=True,
            top_logprobs=TOP_LOGPROBS,
        )
        mass = normalize(letter_mass(response.raw, letters), self.min_coverage)
        return {key: mass[letters[i]] for i, (key, _) in enumerate(options)}

    async def distribution(
        self, state: str, instructions: str, options: Sequence[tuple[str, str]]
    ) -> dict[str, float]:
        if not 2 <= len(options) <= len(LETTERS):
            raise DecisionBackendError(f"need 2..{len(LETTERS)} options, got {len(options)}")
        forward = await self._ask(state, instructions, options)
        if not self.debias_order:
            return forward
        backward = await self._ask(state, instructions, list(reversed(options)))
        return {key: (forward[key] + backward[key]) / 2 for key in forward}
