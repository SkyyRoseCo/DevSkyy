"""CopyAdapter unit tests — the copy/content domain adapter for the evaluation core.

Mirrors tests/quality/test_imagery_adapter.py style: inline helpers, constructor-injected
fake judge, tmp_path for file I/O, no conftest. The adapter scores SkyyRose copy against
brand canon (voice, collection-canon attribution, no urgency theatre, name-not-SKU, etc.).
"""

from __future__ import annotations

import json

import pytest

from evaluation.adapter import DomainAdapter
from evaluation.domains.copy import _DIMENSIONS, COPY_TOOL, CopyAdapter, CopyBrief


def _brief(
    collection: str | None = None,
    content_type: str = "product_description",
    product_name: str | None = "Black Rose Crewneck",
) -> CopyBrief:
    return CopyBrief(
        collection=collection,
        content_type=content_type,
        product_name=product_name,
        brand_voice_context="Declarative fragments. Refusal as posture. No hedging.",
        additional_direction="",
    )


def _good_output(**overrides) -> dict:
    out = {
        "brand_analysis": "The copy opens with a declarative fragment, no hedging.",
        "brand_voice_fidelity": 5,
        "correct_collection_canon": 5,
        "garment_as_protagonist": 5,
        "no_urgency_theatre": 5,
        "no_related_products_push": 5,
        "name_not_sku_referencing": 5,
        "canonical_tagline_only": 5,
        "oakland_anchoring": 5,
        "failure_tags": [],
        "reason": "clean",
    }
    out.update(overrides)
    return out


# --- tool schema ---------------------------------------------------------------


def test_copy_tool_schema_has_brand_analysis_first_and_eight_dimensions():
    props = COPY_TOOL["input_schema"]["properties"]
    assert list(props.keys())[0] == "brand_analysis"
    for dim in _DIMENSIONS:
        assert dim in props
    assert len(_DIMENSIONS) == 8


def test_copy_tool_required_and_additional_properties_closed():
    schema = COPY_TOOL["input_schema"]
    assert COPY_TOOL["name"] == "copy_qc_verdict"
    assert schema["additionalProperties"] is False
    required = set(schema["required"])
    assert {"brand_analysis", "failure_tags", "reason"} <= required
    assert set(_DIMENSIONS) <= required


# --- deterministic checks (free, no LLM) ---------------------------------------


def test_deterministic_check_retired_tagline():
    tags = CopyAdapter().deterministic_checks("Where Love Meets Luxury is our promise.", _brief())
    assert "retired_tagline_present" in tags


def test_deterministic_check_urgency_markers():
    tags = CopyAdapter().deterministic_checks("Only 3 left! Buy before selling fast.", _brief())
    assert "urgency_timer_present" in tags


def test_deterministic_check_sku_first_naming():
    tags = CopyAdapter().deterministic_checks("br-001 is now available to shop.", _brief())
    assert "sku_first_naming" in tags


def test_deterministic_check_sku_parenthetical_is_allowed():
    """A SKU as a parenthetical backend key right after the name is permitted."""
    clean = "The Black Rose Crewneck (br-001) is armor."
    assert CopyAdapter().deterministic_checks(clean, _brief()) == []


def test_deterministic_check_related_products_push():
    tags = CopyAdapter().deterministic_checks("You may also like the Black Rose Bomber.", _brief())
    assert "related_products_push" in tags


def test_deterministic_checks_clean_copy_returns_empty_list():
    clean = "The Black Rose Crewneck is armor."
    assert CopyAdapter().deterministic_checks(clean, _brief()) == []


def test_deterministic_check_unrelated_products_not_flagged():
    """'unrelated products' must NOT trip the related-products substring match."""
    text = "Browse unrelated products from our sister lineup."
    assert "related_products_push" not in CopyAdapter().deterministic_checks(text, _brief())


def test_deterministic_check_sku_parenthetical_with_spaces_allowed():
    """A SKU in a spaced parenthetical, e.g. '( br-001 )', is still a backend key."""
    clean = "The Black Rose Crewneck ( br-001 ) is armor."
    assert CopyAdapter().deterministic_checks(clean, _brief()) == []


# --- parse_verdict -------------------------------------------------------------


def test_parse_verdict_all_perfect_scores_passes():
    v = CopyAdapter().parse_verdict(_good_output(), [])
    assert v.passed is True
    assert v.score == 1.0
    assert v.domain == "copy"
    assert dict(v.gate_results) == dict.fromkeys(_DIMENSIONS, 5)


def test_parse_verdict_oakland_zero_still_passes():
    """Dropping only the 0.05-weight dimension to 0 → composite 0.95, still passes."""
    v = CopyAdapter().parse_verdict(_good_output(oakland_anchoring=0), [])
    assert v.passed is True
    assert round(v.score, 2) == 0.95


def test_parse_verdict_weighted_score_below_threshold_fails():
    """Two 0.20-weight dimensions at 0 → composite 0.60, below the 0.80 floor."""
    v = CopyAdapter().parse_verdict(
        _good_output(brand_voice_fidelity=0, correct_collection_canon=0), []
    )
    assert v.passed is False
    assert round(v.score, 2) == 0.60


def test_parse_verdict_hard_fail_tag_overrides_high_score():
    """A hard-fail tag fails the verdict even when every dimension scores 5."""
    out = _good_output(failure_tags=["retired_tagline_present"])
    v = CopyAdapter().parse_verdict(out, [])
    assert v.passed is False
    assert "retired_tagline_present" in v.failure_tags


def test_parse_verdict_missing_dimension_is_zero():
    out = _good_output(correct_collection_canon=0)
    del out["brand_voice_fidelity"]
    v = CopyAdapter().parse_verdict(out, [])
    assert v.gate_results["brand_voice_fidelity"] == 0
    assert v.passed is False  # 0+0 on the two 0.20 dims drags composite to 0.60


def test_parse_verdict_detail_contains_brand_analysis():
    out = _good_output(brand_analysis="The copy opens with a declarative fragment.")
    v = CopyAdapter().parse_verdict(out, [])
    assert v.detail["brand_analysis"].startswith("The copy opens")


def test_parse_verdict_does_not_set_cost_or_attempts():
    """Core stamps cost_usd/attempts via replace(); the adapter leaves them at defaults."""
    v = CopyAdapter().parse_verdict(_good_output(), [])
    assert v.cost_usd == 0.0
    assert v.attempts == 0


def test_parse_verdict_carries_deterministic_failures():
    v = CopyAdapter().parse_verdict(_good_output(), ["sku_first_naming"])
    assert "sku_first_naming" in v.failure_tags
    assert v.passed is False


# --- build_judge_request -------------------------------------------------------


def test_build_judge_request_structure():
    req = CopyAdapter().build_judge_request("Black Rose Crewneck.", _brief(collection="black_rose"))
    assert req["tool"]["name"] == "copy_qc_verdict"
    msg = req["messages"][0]
    assert msg["role"] == "user"
    assert msg["content"][0]["type"] == "text"


def test_build_judge_request_embeds_subject_and_collection():
    subject = "The Black Rose Crewneck is armor."
    req = CopyAdapter().build_judge_request(subject, _brief(collection="black_rose"))
    text = req["messages"][0]["content"][0]["text"]
    assert subject in text
    assert "black_rose" in text


# --- revise (regenerate_fn injection seam) -------------------------------------


@pytest.mark.asyncio
async def test_revise_calls_regenerate_fn_with_ref_and_critique():
    captured = {}

    async def regenerate_fn(ref, critique):
        captured["ref"] = ref
        captured["critique"] = critique
        return "revised copy"

    adapter = CopyAdapter(regenerate_fn=regenerate_fn)
    critique = {"failure_tags": ("voice_drift",), "reason": "hedging", "detail": {}}
    result = await adapter.revise(_brief(), critique)

    assert result == "revised copy"
    assert captured["critique"] == critique


@pytest.mark.asyncio
async def test_revise_without_regenerate_fn_raises():
    with pytest.raises(NotImplementedError):
        await CopyAdapter().revise(_brief(), {"failure_tags": (), "reason": "", "detail": {}})


# --- load_ground_truth ---------------------------------------------------------


def test_load_ground_truth_from_json_file(tmp_path):
    state = {
        "hero-copy-v1": {"approved": True, "flagged": False, "comment": "clean"},
        "pdp-v2": {"approved": True, "flagged": True, "comment": "urgency theatre"},
    }
    f = tmp_path / "copy-review-state.json"
    f.write_text(json.dumps(state), encoding="utf-8")

    gt = {row["subject_id"]: row for row in CopyAdapter(review_state_path=f).load_ground_truth()}

    assert gt["hero-copy-v1"]["label_pass"] is True
    assert gt["pdp-v2"]["label_pass"] is False  # flagged overrides approved


def test_load_ground_truth_empty_when_file_missing(tmp_path):
    missing = tmp_path / "nope.json"
    assert CopyAdapter(review_state_path=missing).load_ground_truth() == []


# --- protocol conformance ------------------------------------------------------


def test_copy_adapter_satisfies_domain_adapter_protocol():
    assert isinstance(CopyAdapter(), DomainAdapter)
    assert CopyAdapter().domain == "copy"
