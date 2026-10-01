"""Offline FAQ failures exercise current authority, parsing, and retired copy."""

import importlib
from pathlib import Path

import pytest


@pytest.fixture
def faq(monkeypatch: pytest.MonkeyPatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "tasks/prelaunch-faq-rewrite-2026-09-26"))
    return importlib.import_module("build_faq")


def test_missing_policy_quote_blocks_candidate(faq, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        faq,
        "SECTIONS",
        [
            (
                "Orders",
                [
                    (
                        "When?",
                        "Read the policy.",
                        [{"kind": "policy_page", "ref": "9712 policy", "quote": "ship tomorrow"}],
                    )
                ],
            )
        ],
    )
    assert faq.verify_sources({"9712": "No estimated date supplied."}, {}) == [
        "[When?] quote not on page 9712 policy: 'ship tomorrow'"
    ]


def test_retired_tagline_and_reply_promise_are_rejected(faq) -> None:
    assert "retired tagline" in faq.banned_hits("Luxury Grows from Concrete.")
    assert "response-time wording" in faq.banned_hits("We respond within 24 hours.")
    assert faq.banned_hits("Cancel up to 48 hours before its estimated ship date.") == []


def test_no_tagline_faq_and_all_answers_parse(faq) -> None:
    markup = faq.block_markup()
    branch, entries = faq.parse_like_theme(markup)
    assert branch == "details"
    assert len(entries) == 22
    assert all("Luxury Grows from Concrete" not in entry["answer"] for entry in entries)
    assert faq.registry_invariants() == []
