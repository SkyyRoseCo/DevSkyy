#!/usr/bin/env python3
"""Calibrate the in-house decision layer against a labelled JSONL set.

Each line of ``--cases`` is a ``llm.decisions.LabelledCase``::

    {"state": "...", "question": {"type": "choice", "instructions": "...",
     "criteria": {"a": "...", "b": "..."}}, "expected": "a"}

Reports are grouped by question shape (``choice/3``, ``noul/2``, ...) because
confidences are not comparable across shapes. Any failed case exits 1.

Every case is one paid OpenAI request (two with order debiasing, the default), so
the run refuses without ``--yes`` and prints the manifest instead (CLAUDE.md §1).

    python scripts/decision_calibrate.py --cases data.jsonl            # manifest only
    python scripts/decision_calibrate.py --cases data.jsonl --yes      # paid run
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from llm.decisions import (  # noqa: E402
    LabelledCase,
    LogprobBackend,
    calibration_report,
    run_cases,
)
from llm.decisions.backend import SYSTEM_PROMPT, render_prompt  # noqa: E402
from llm.decisions.engine import serialize_state  # noqa: E402
from llm.model_ids import OPENAI_MINI_MODEL, OPENAI_VISION_MODEL  # noqa: E402

CHARS_PER_TOKEN = 4  # rough planning figure for the manifest, not a billing number
# Chat models registered in llm/model_ids.py whose settings support logprobs.
LOGPROB_MODELS = (OPENAI_MINI_MODEL, OPENAI_VISION_MODEL)


def load_cases(path: Path) -> list[LabelledCase]:
    cases = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                cases.append(LabelledCase.model_validate_json(line))
            except ValueError as exc:
                raise SystemExit(f"{path}:{number}: invalid case: {exc}") from exc
    if not cases:
        raise SystemExit(f"{path}: no cases")
    return cases


def prompt_chars(case: LabelledCase) -> int:
    """Characters of one request exactly as the backend renders it."""
    question = case.question
    user = render_prompt(serialize_state(case.state), question.instructions, question.options())
    return len(SYSTEM_PROMPT) + len(user)


def manifest(cases: list[LabelledCase], model: str, debias: bool) -> dict[str, object]:
    calls = len(cases) * (2 if debias else 1)
    chars = sum(prompt_chars(case) for case in cases)
    return {
        "action": "decision calibration (paid OpenAI chat completions)",
        "model": model,
        "cases": len(cases),
        "requests": calls,
        "approx_input_tokens": chars * (2 if debias else 1) // CHARS_PER_TOKEN,
        "output_tokens_per_request": 1,
    }


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cases", type=Path, required=True, help="labelled JSONL file")
    parser.add_argument("--model", choices=LOGPROB_MODELS, default=OPENAI_MINI_MODEL)
    parser.add_argument("--target-precision", type=float, default=0.95)
    parser.add_argument("--min-support", type=int, default=30)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--no-debias", action="store_true", help="one request per case")
    parser.add_argument("--yes", action="store_true", help="confirm the paid run")
    args = parser.parse_args(argv)
    # Reject bad settings here, before any paid request, not after the run.
    if not 0.5 < args.target_precision <= 1.0:
        parser.error("--target-precision must be in (0.5, 1]")
    if args.min_support < 1:
        parser.error("--min-support must be >= 1")
    if args.concurrency < 1:
        parser.error("--concurrency must be >= 1")
    return args


async def _run(args: argparse.Namespace, cases: list[LabelledCase]) -> dict[str, dict]:
    """One report per question shape; confidences are not comparable across shapes."""
    from llm.providers.openai import OpenAIClient

    backend = LogprobBackend(OpenAIClient(), args.model, debias_order=not args.no_debias)
    records = await run_cases(backend, cases, concurrency=args.concurrency)
    groups: dict[str, list] = {}
    for case, record in zip(cases, records, strict=True):
        groups.setdefault(case.shape, []).append(record)
    return {
        shape: calibration_report(group, args.target_precision, args.min_support).model_dump()
        for shape, group in sorted(groups.items())
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cases = load_cases(args.cases)
    plan = manifest(cases, args.model, not args.no_debias)
    if not args.yes:
        print("STOP — paid run not confirmed. Re-run with --yes to proceed.", file=sys.stderr)
        print(json.dumps(plan, indent=2))
        return 2
    reports = asyncio.run(_run(args, cases))
    print(json.dumps(reports, indent=2))
    failures = sum(report["failures"] for report in reports.values())
    if failures:
        print(f"{failures} case(s) failed; thresholds are not trustworthy.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
