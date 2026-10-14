"""In-house decision layer. Every test mocks the HTTP/client boundary; no paid calls."""

from __future__ import annotations

import asyncio
import json
import math
from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import TypeAdapter, ValidationError

from llm.base import CompletionResponse
from llm.decisions import (
    Choice,
    ChoiceAnswer,
    DecisionBackendError,
    DecisionEngine,
    DecisionFailure,
    GatePolicy,
    LabelledCase,
    LogprobBackend,
    Noul,
    NoulAnswer,
    Route,
    Score,
    ScoreAnswer,
    calibration_report,
    run_cases,
)
from llm.decisions.backend import letter_mass, normalize, render_prompt
from llm.decisions.calibration import CaseRecord, expected_calibration_error
from llm.decisions.engine import MAX_STATE_CHARS, serialize_state
from llm.decisions.gate import build_answer
from llm.decisions.types import Question
from llm.model_ids import OPENAI_MINI_MODEL
from llm.providers.openai import OpenAIClient

TIER = Choice(
    instructions="How hard is the request?",
    criteria={"simple": "lookup or rewrite", "hard": "multi-step reasoning"},
)
URGENT = Noul(instructions="Is it urgent?", true_when="needs action today", false_when="can wait")
RISK = Score(instructions="Rate the risk.", criteria=["none", "some", "severe"])


def raw_logprobs(top: dict[str, float]) -> dict:
    """Chat Completions body whose first output token has these top logprobs."""
    entries = [{"token": token, "logprob": math.log(p), "bytes": None} for token, p in top.items()]
    return {
        "choices": [
            {
                "message": {"role": "assistant", "content": next(iter(top))},
                "logprobs": {"content": [{"token": "x", "logprob": 0.0, "top_logprobs": entries}]},
                "finish_reason": "length",
            }
        ],
        "usage": {"prompt_tokens": 50, "completion_tokens": 1, "total_tokens": 51},
    }


def completion(top: dict[str, float]) -> CompletionResponse:
    return CompletionResponse(
        content="A", model=OPENAI_MINI_MODEL, provider="openai", raw=raw_logprobs(top)
    )


class StubBackend:
    """Returns fixed distributions per instruction text, or raises."""

    model = "stub"

    def __init__(self, table: dict[str, dict[str, float] | Exception]) -> None:
        self.table = table

    async def distribution(self, state, instructions, options):
        outcome = self.table[instructions]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


# --------------------------------------------------------------------------- types


def test_questions_expose_closed_option_sets():
    assert TIER.options() == [("simple", "lookup or rewrite"), ("hard", "multi-step reasoning")]
    assert URGENT.options() == [("true", "needs action today"), ("false", "can wait")]
    assert [key for key, _ in RISK.options()] == ["0", "1", "2"]


def test_question_union_parses_by_type():
    parsed = TypeAdapter(Question).validate_python(
        {"type": "noul", "instructions": "x?", "true_when": "y", "false_when": "n"}
    )
    assert isinstance(parsed, Noul)


@pytest.mark.parametrize(
    "build",
    [
        lambda: Choice(instructions="q", criteria={"only": "one"}),
        lambda: Choice(instructions="  ", criteria={"a": "1", "b": "2"}),
        lambda: Choice(instructions="q", criteria={"a": " ", "b": "2"}),
        lambda: Score(instructions="q", criteria=["single"]),
        lambda: Noul(instructions="q", true_when="", false_when="n"),
        lambda: Choice(instructions="q", criteria={str(i): "x" for i in range(27)}),
    ],
)
def test_invalid_questions_rejected(build):
    with pytest.raises(ValidationError):
        build()


def test_failure_can_never_route_sharp():
    assert DecisionFailure(error="boom").route is Route.SPLIT
    with pytest.raises(ValidationError):
        DecisionFailure(error="boom", route=Route.SHARP)


# ---------------------------------------------------------------------------- gate


def test_choice_routes_on_min_confidence():
    policy = GatePolicy(min_confidence=0.8)
    sharp = build_answer(TIER, {"simple": 0.85, "hard": 0.15}, policy)
    split = build_answer(TIER, {"simple": 0.75, "hard": 0.25}, policy)
    assert isinstance(sharp, ChoiceAnswer)
    assert (sharp.choice, sharp.route) == ("simple", Route.SHARP)
    assert (split.choice, split.route) == ("simple", Route.SPLIT)


def test_tie_never_routes_sharp():
    answer = build_answer(TIER, {"simple": 0.5, "hard": 0.5}, GatePolicy())
    assert answer.route is Route.SPLIT


def test_score_reports_expected_level_and_mode():
    answer = build_answer(RISK, {"0": 0.1, "1": 0.2, "2": 0.7}, GatePolicy(min_confidence=0.6))
    assert isinstance(answer, ScoreAnswer)
    assert answer.score == pytest.approx(1.6)
    assert (answer.level, answer.route) == (2, Route.SHARP)


@pytest.mark.parametrize(
    ("p_yes", "route"),
    [(0.95, Route.SHARP), (0.05, Route.SHARP), (0.5, Route.SPLIT), (0.89, Route.SPLIT)],
)
def test_noul_deadband_abstains(p_yes, route):
    answer = build_answer(URGENT, {"true": p_yes, "false": 1 - p_yes}, GatePolicy())
    assert isinstance(answer, NoulAnswer)
    assert answer.route is route


def test_distribution_must_match_options():
    with pytest.raises(ValueError):
        build_answer(TIER, {"simple": 1.0}, GatePolicy())


@pytest.mark.parametrize(
    "kwargs",
    [
        {"min_confidence": 0.5},
        {"noul_yes": 0.5},
        {"noul_no": 0.5},
        {"min_confidence": 1.1},
    ],
)
def test_gate_policy_rejects_permissive_settings(kwargs):
    with pytest.raises(ValidationError):
        GatePolicy(**kwargs)


# ------------------------------------------------------------------------- backend


def test_letter_mass_merges_spacing_variants_and_ignores_other_tokens():
    mass = letter_mass(raw_logprobs({"A": 0.5, " A": 0.2, "B": 0.1, "Sure": 0.15}), "AB")
    assert mass["A"] == pytest.approx(0.7)
    assert mass["B"] == pytest.approx(0.1)


@pytest.mark.parametrize("raw", [{}, {"choices": []}, {"choices": [{"logprobs": None}]}])
def test_missing_logprobs_raise(raw):
    with pytest.raises(DecisionBackendError):
        letter_mass(raw, "AB")


def test_low_valid_mass_is_refused_not_guessed():
    with pytest.raises(DecisionBackendError):
        normalize({"A": 0.2, "B": 0.1}, min_coverage=0.5)
    assert normalize({"A": 0.6, "B": 0.2}, 0.5) == pytest.approx({"A": 0.75, "B": 0.25})


def test_prompt_letters_follow_option_order():
    prompt = render_prompt("s", "q", [("x", "first"), ("y", "second")])
    assert "A. first\nB. second" in prompt


async def test_logprob_backend_averages_both_orders():
    client = Mock()
    # forward order: A=simple 0.9; reversed order: A=hard 0.3, B=simple 0.7
    client.complete = AsyncMock(
        side_effect=[completion({"A": 0.9, "B": 0.1}), completion({"A": 0.3, "B": 0.7})]
    )
    backend = LogprobBackend(client)
    distribution = await backend.distribution("s", TIER.instructions, TIER.options())
    assert distribution == pytest.approx({"simple": 0.8, "hard": 0.2})
    kwargs = client.complete.await_args.kwargs
    assert (kwargs["max_tokens"], kwargs["temperature"]) == (1, 0.0)
    assert (kwargs["logprobs"], kwargs["top_logprobs"]) == (True, 20)
    assert "A. multi-step reasoning" in kwargs["messages"][1].content


async def test_logprob_backend_single_order_makes_one_call():
    client = Mock()
    client.complete = AsyncMock(return_value=completion({"A": 0.9, "B": 0.1}))
    backend = LogprobBackend(client, debias_order=False)
    assert await backend.distribution("s", "q", TIER.options()) == pytest.approx(
        {"simple": 0.9, "hard": 0.1}
    )
    assert client.complete.await_count == 1


async def test_logprob_backend_option_bounds():
    backend = LogprobBackend(Mock())
    with pytest.raises(DecisionBackendError):
        await backend.distribution("s", "q", [("a", "only")])
    with pytest.raises(ValueError):
        LogprobBackend(Mock(), min_coverage=0.0)


async def test_openai_wire_request_carries_logprob_settings(monkeypatch):
    client = OpenAIClient(api_key="test")
    transport = AsyncMock(return_value=Mock(json=lambda: raw_logprobs({"A": 0.95, "B": 0.05})))
    monkeypatch.setattr(client, "_make_request", transport)
    backend = LogprobBackend(client, debias_order=False)
    distribution = await backend.distribution("s", "q", TIER.options())
    body = transport.await_args.kwargs["json"]
    assert body["model"] == OPENAI_MINI_MODEL
    assert (body["max_tokens"], body["temperature"]) == (1, 0.0)
    assert (body["logprobs"], body["top_logprobs"]) == (True, 20)
    assert distribution["simple"] == pytest.approx(0.95)


# -------------------------------------------------------------------------- engine


async def test_engine_answers_each_question_and_isolates_failures():
    backend = StubBackend(
        {
            TIER.instructions: {"simple": 0.95, "hard": 0.05},
            URGENT.instructions: DecisionBackendError("no logprobs"),
            RISK.instructions: {"0": 0.2, "1": 0.5, "2": 0.3},
        }
    )
    result = await DecisionEngine(backend).decide(
        {"request": "rename a file"}, {"tier": TIER, "urgent": URGENT, "risk": RISK}
    )
    assert result.answers["tier"].route is Route.SHARP
    assert isinstance(result.answers["urgent"], DecisionFailure)
    assert "no logprobs" in result.answers["urgent"].error
    assert result.answers["risk"].route is Route.SPLIT
    assert not result.all_sharp
    assert result.model == "stub"


async def test_engine_cancellation_is_not_swallowed():
    class Cancelling:
        model = "stub"

        async def distribution(self, *_):
            raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await DecisionEngine(Cancelling()).decide("s", {"tier": TIER})


async def test_engine_rejects_bad_requests():
    engine = DecisionEngine(StubBackend({}))
    with pytest.raises(ValueError):
        await engine.decide("s", {})
    with pytest.raises(ValueError):
        await engine.decide("   ", {"tier": TIER})


def test_state_serialization_is_stable_and_bounded():
    assert serialize_state({"b": 1, "a": "é"}) == '{"a": "é", "b": 1}'
    with pytest.raises(ValueError):
        serialize_state("x" * (MAX_STATE_CHARS + 1))


# --------------------------------------------------------------------- calibration


def test_labelled_case_expected_must_be_an_option():
    with pytest.raises(ValidationError):
        LabelledCase(state="s", question=TIER, expected="medium")


async def test_run_cases_counts_failures_as_wrong():
    backend = StubBackend(
        {TIER.instructions: {"simple": 0.9, "hard": 0.1}, URGENT.instructions: RuntimeError("x")}
    )
    cases = [
        LabelledCase(state="s", question=TIER, expected="simple"),
        LabelledCase(state="s", question=TIER, expected="hard"),
        LabelledCase(state="s", question=URGENT, expected="true"),
    ]
    records = await run_cases(backend, cases, concurrency=2)
    assert [r.correct for r in records] == [True, False, False]
    assert records[2].predicted is None
    assert records[2].error == "x"
    with pytest.raises(ValueError):
        await run_cases(backend, cases, concurrency=0)


def _records(spec: list[tuple[float, bool]]) -> list[CaseRecord]:
    return [CaseRecord(predicted="a", confidence=c, correct=ok) for c, ok in spec]


def test_ece_zero_when_confidence_matches_accuracy():
    records = _records([(1.0, True)] * 4 + [(0.5, True), (0.5, False)])
    assert expected_calibration_error(records) == pytest.approx(0.0)
    assert expected_calibration_error(_records([(0.9, False)] * 2)) == pytest.approx(0.9)


def test_report_recommends_lowest_threshold_meeting_precision():
    records = _records([(0.95, True)] * 30 + [(0.7, False)] * 10)
    report = calibration_report(records, target_precision=0.95, min_support=30)
    assert report.recommended_threshold == pytest.approx(0.95)
    assert report.sharp_rate_at_threshold == pytest.approx(0.75)
    assert report.accuracy == pytest.approx(0.75)


def test_report_withholds_threshold_without_support():
    report = calibration_report(_records([(0.99, True)] * 5), min_support=30)
    assert report.recommended_threshold is None
    assert report.sharp_rate_at_threshold == 0.0
    with pytest.raises(ValueError):
        calibration_report([])
    with pytest.raises(ValueError):
        calibration_report(_records([(0.9, True)]), target_precision=0.5)


def test_report_withholds_threshold_when_precision_never_reached():
    report = calibration_report(_records([(0.9, False)] * 40), min_support=10)
    assert report.recommended_threshold is None
    assert expected_calibration_error([]) == 0.0


# --------------------------------------------------------------------------- script


@pytest.fixture
def cases_file(tmp_path):
    path = tmp_path / "cases.jsonl"
    case = LabelledCase(state="rename a file", question=TIER, expected="simple")
    path.write_text(case.model_dump_json() + "\n\n", encoding="utf-8")
    return path


def test_script_refuses_paid_run_without_yes(cases_file, monkeypatch, capsys):
    import decision_calibrate

    monkeypatch.setattr(
        decision_calibrate, "LogprobBackend", Mock(side_effect=AssertionError("paid call"))
    )
    assert decision_calibrate.main(["--cases", str(cases_file)]) == 2
    plan = json.loads(capsys.readouterr().out)
    assert (plan["cases"], plan["requests"], plan["model"]) == (1, 2, OPENAI_MINI_MODEL)


def test_script_runs_with_yes(cases_file, monkeypatch, capsys):
    import decision_calibrate

    backend = StubBackend({TIER.instructions: {"simple": 0.97, "hard": 0.03}})
    monkeypatch.setattr(decision_calibrate, "LogprobBackend", Mock(return_value=backend))
    monkeypatch.setattr("llm.providers.openai.OpenAIClient", Mock())
    assert decision_calibrate.main(["--cases", str(cases_file), "--yes", "--min-support", "1"]) == 0
    report = json.loads(capsys.readouterr().out)["choice/2"]
    assert (report["cases"], report["accuracy"]) == (1, 1.0)
    assert report["recommended_threshold"] == pytest.approx(0.97)


def test_script_rejects_invalid_case_lines(tmp_path):
    import decision_calibrate

    bad = tmp_path / "bad.jsonl"
    bad.write_text('{"state": "s"}\n', encoding="utf-8")
    with pytest.raises(SystemExit, match="bad.jsonl:1"):
        decision_calibrate.main(["--cases", str(bad)])


# ------------------------------------------------------------ review hardening


@pytest.mark.parametrize("logprob", [float("nan"), float("inf"), True, 0.5, 1000.0, "-0.1"])
def test_malformed_logprobs_are_refused(logprob):
    raw = raw_logprobs({"A": 0.9, "B": 0.1})
    raw["choices"][0]["logprobs"]["content"][0]["top_logprobs"][0]["logprob"] = logprob
    with pytest.raises(DecisionBackendError):
        letter_mass(raw, "AB")


def test_ece_ignores_failed_cases():
    failed = [CaseRecord(predicted=None, confidence=0.0, correct=False, error="x")] * 9
    records = failed + _records([(0.99, False)])
    assert expected_calibration_error(records) == pytest.approx(0.99)
    assert calibration_report(records, min_support=1).failures == 9


def test_threshold_never_below_gate_floor():
    records = _records([(0.4, True)] * 40)
    assert calibration_report(records, min_support=10).recommended_threshold is None


async def test_run_cases_survives_invalid_distribution():
    backend = StubBackend({TIER.instructions: {"simple": float("nan"), "hard": 0.1}})
    [record] = await run_cases(backend, [LabelledCase(state="s", question=TIER, expected="hard")])
    assert record.predicted is None
    assert record.error


def test_script_reports_per_question_shape(tmp_path, monkeypatch, capsys):
    import decision_calibrate

    path = tmp_path / "mixed.jsonl"
    lines = [
        LabelledCase(state="a", question=TIER, expected="simple").model_dump_json(),
        LabelledCase(state="b", question=URGENT, expected="true").model_dump_json(),
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    backend = StubBackend(
        {
            TIER.instructions: {"simple": 0.97, "hard": 0.03},
            URGENT.instructions: {"true": 0.96, "false": 0.04},
        }
    )
    monkeypatch.setattr(decision_calibrate, "LogprobBackend", Mock(return_value=backend))
    monkeypatch.setattr("llm.providers.openai.OpenAIClient", Mock())
    assert decision_calibrate.main(["--cases", str(path), "--yes", "--min-support", "1"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert set(report) == {"choice/2", "noul/2"}
    assert report["noul/2"]["recommended_threshold"] == pytest.approx(0.96)


def test_script_exits_nonzero_when_cases_fail(cases_file, monkeypatch, capsys):
    import decision_calibrate

    backend = StubBackend({TIER.instructions: DecisionBackendError("401")})
    monkeypatch.setattr(decision_calibrate, "LogprobBackend", Mock(return_value=backend))
    monkeypatch.setattr("llm.providers.openai.OpenAIClient", Mock())
    assert decision_calibrate.main(["--cases", str(cases_file), "--yes"]) == 1
    assert json.loads(capsys.readouterr().out)["choice/2"]["failures"] == 1


def test_script_rejects_unregistered_model(cases_file):
    import decision_calibrate

    with pytest.raises(SystemExit):
        decision_calibrate.main(["--cases", str(cases_file), "--model", "made-up-model"])
