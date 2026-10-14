"""Typed decision questions and answers.

Three question shapes, all reduced to one probability distribution over a closed,
caller-defined option set:

- ``Choice``: pick one of the caller's keys.
- ``Score``: rate on an ordered scale; the answer is the expected level index.
- ``Noul``: a yes/no probability (``noul`` = probability the answer is yes).

An answer can never name an option the caller did not define. It can still be the
wrong valid option with high confidence, which is why ``gate.py`` routes on
calibrated thresholds and treats every failure as an escalation.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_OPTIONS = 26  # one letter per option, A..Z


def _require_text(value: str) -> str:
    if not value.strip():
        raise ValueError("must not be blank")
    return value


class _Question(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    instructions: str = Field(..., min_length=1)

    @field_validator("instructions")
    @classmethod
    def _instructions_not_blank(cls, value: str) -> str:
        return _require_text(value)


class Choice(_Question):
    """Pick one option. ``criteria`` maps each option key to what it means."""

    type: Literal["choice"] = "choice"
    criteria: dict[str, str] = Field(..., min_length=2, max_length=MAX_OPTIONS)

    @field_validator("criteria")
    @classmethod
    def _criteria_not_blank(cls, value: dict[str, str]) -> dict[str, str]:
        for key, meaning in value.items():
            _require_text(key)
            _require_text(meaning)
        return value

    def options(self) -> list[tuple[str, str]]:
        return list(self.criteria.items())


class Score(_Question):
    """Rate on an ordered scale. ``criteria[i]`` describes level ``i`` (lowest first)."""

    type: Literal["score"] = "score"
    criteria: list[str] = Field(..., min_length=2, max_length=MAX_OPTIONS)

    @field_validator("criteria")
    @classmethod
    def _levels_not_blank(cls, value: list[str]) -> list[str]:
        return [_require_text(level) for level in value]

    def options(self) -> list[tuple[str, str]]:
        return [(str(index), level) for index, level in enumerate(self.criteria)]


class Noul(_Question):
    """Yes/no as a probability. ``true_when`` / ``false_when`` define each side."""

    type: Literal["noul"] = "noul"
    true_when: str = Field(..., min_length=1)
    false_when: str = Field(..., min_length=1)

    @field_validator("true_when", "false_when")
    @classmethod
    def _sides_not_blank(cls, value: str) -> str:
        return _require_text(value)

    def options(self) -> list[tuple[str, str]]:
        return [("true", self.true_when), ("false", self.false_when)]


Question = Annotated[Choice | Score | Noul, Field(discriminator="type")]


class Route(StrEnum):
    """Where a decision goes next.

    ``SHARP``: confident enough for code to take the cheap, deterministic path.
    ``SPLIT``: escalate to the strong model or a person. Every failure is ``SPLIT``.

    ``SHARP`` never authorizes a paid, production, or irreversible action; those
    stay behind the STOP-AND-SHOW gate whatever the confidence.
    """

    SHARP = "sharp"
    SPLIT = "split"


class _Answer(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    route: Route


class ChoiceAnswer(_Answer):
    type: Literal["choice"] = "choice"
    choice: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    probabilities: dict[str, float]


class ScoreAnswer(_Answer):
    type: Literal["score"] = "score"
    score: float = Field(..., ge=0.0, description="Expected level index")
    level: int = Field(..., ge=0, description="Most probable level index")
    confidence: float = Field(..., ge=0.0, le=1.0)
    probabilities: dict[str, float]


class NoulAnswer(_Answer):
    type: Literal["noul"] = "noul"
    noul: float = Field(..., ge=0.0, le=1.0, description="Probability the answer is yes")


class DecisionFailure(_Answer):
    """The question could not be answered. Always routed ``SPLIT``."""

    type: Literal["failure"] = "failure"
    route: Route = Route.SPLIT
    error: str

    @field_validator("route")
    @classmethod
    def _always_split(cls, value: Route) -> Route:
        if value is not Route.SPLIT:
            raise ValueError("a failed decision must route SPLIT")
        return value


Answer = ChoiceAnswer | ScoreAnswer | NoulAnswer | DecisionFailure


class DecisionResult(BaseModel):
    """Answers keyed by the caller's question names."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    answers: dict[str, Answer]
    model: str

    @property
    def all_sharp(self) -> bool:
        return all(answer.route is Route.SHARP for answer in self.answers.values())
