"""Offline regression cases for grounding and QA; no model requests permitted."""

import copy
import json
from unittest.mock import AsyncMock, Mock

import pytest

from skyyrose.elite_studio.agents import quality_agent as qa
from skyyrose.elite_studio.agents.qa_contract import JudgeResponse, parse_response
from skyyrose.elite_studio.prompts.chain import PromptChain
from skyyrose.elite_studio.prompts.enhancer import PromptEnhancer


@pytest.fixture
def product(monkeypatch, tmp_path):
    reference = tmp_path / "front.png"
    reference.write_bytes(b"offline-reference")
    record = {
        "sku": "br-001",
        "name": "Fixture garment",
        "collection": "black-rose",
        "garment": {
            "color": "black",
            "fit": {"specification": None},
            "materials": {"specification": "Maker-specified woven fabric"},
            "features": {"specification": "Maker-specified closure"},
        },
        "dossier": {"full_text": "**FOUNDER_CONFIRMED:** exact 3–4 inches; “preserve this”."},
        "logos": {},
        "corrections": [],
        "authority": "FOUNDER_CONFIRMED",
        "render_sources": {"front": "front.png"},
        "images": {},
        "gaps": [],
    }
    monkeypatch.setattr(
        "skyyrose.elite_studio.prompts.chain.get_product", lambda sku: copy.deepcopy(record)
    )
    monkeypatch.setattr(qa, "get_product", lambda sku: copy.deepcopy(record))
    monkeypatch.setattr(qa, "REPO_ROOT", tmp_path)
    return record


def response(mode="flat_lay", score=100):
    finding = {"status": "match", "evidence": "Visible feature agrees in A and B"}
    metric = {"score": score, "evidence": "Visible integrated light and drape"}
    return {
        "identity": {
            k: dict(finding)
            for k in ("silhouette", "construction", "artwork", "lettering", "color", "placement")
        },
        "scene": (
            {
                **{k: dict(metric) for k in ("lighting", "edges", "shadows")},
                **{k: dict(finding) for k in ("scale", "perspective", "occlusion")},
            }
            if mode == "scene_composite"
            else None
        ),
        "ghost_fidelity": metric if mode == "flat_lay" else None,
        "notes": "Offline synthetic judge fixture, not a model evaluation",
    }


def test_existing_sku_no_generic_defaults(product):
    result = PromptChain().enhance("render br-001 hoodie", required_views=("front",))
    assert result["product_constraints"]["br-001"]["dossier"] == product["dossier"]
    assert result["product_constraints"]["br-001"]["garment"] == product["garment"]
    assert "french terry" not in result["enhanced"].lower()
    assert "kangaroo" not in result["enhanced"].lower()
    assert "br-001.garment.fit" in result["gaps"]
    assert result["brief_status"] == "incomplete"
    assert "imagery-prompting.md" in result["imagery_standard"]


def test_missing_view_not_substituted(product):
    result = PromptChain().enhance("render br-001 back", required_views=("back",))
    assert "br-001.render_sources.back" in result["gaps"]


def test_defaults_require_explicit_new_design():
    assert "french terry" not in PromptChain().enhance("render a hoodie")["enhanced"].lower()
    idea = PromptChain().enhance("design a new hoodie", intent="design-ideation", new_design=True)
    assert "french terry" in idea["enhanced"].lower()
    with pytest.raises(ValueError):
        PromptChain().enhance("render hoodie", intent="product-render", new_design=True)


def test_unknown_sku_fails_closed():
    with pytest.raises(KeyError):
        PromptChain().enhance("render br-999")


def test_product_cache_never_serves_stale_facts(product):
    cache = Mock()
    enhancer = PromptEnhancer(cache=cache)
    first = enhancer.enhance("render br-001")
    product["garment"]["color"] = "founder correction"
    second = enhancer.enhance("render br-001")
    assert first.enhanced != second.enhanced
    cache.check.assert_not_called()
    cache.store.assert_not_called()
    assert second.gaps


@pytest.mark.parametrize("bad", ["", "{}", '{"identity":', "OVERALL: 100\nIDENTITY_MISMATCH: NO"])
def test_malformed_responses_are_not_approval(bad):
    with pytest.raises(ValueError):
        parse_response(bad, "flat_lay")


@pytest.mark.parametrize("status", ["mismatch", "not_visible"])
def test_wrong_artwork_or_hidden_lettering_blocks(status):
    data = response()
    data["identity"]["artwork"]["status"] = status
    decision = parse_response(json.dumps(data), "flat_lay")
    assert not decision["accepted"]
    assert decision["identity_mismatch"] == (status == "mismatch")
    assert decision["missing_evidence"] == (status == "not_visible")


def test_weighted_scene_total_and_pasted_light_separate_identity():
    data = response("scene_composite")
    data["scene"]["lighting"]["score"] = 0
    decision = parse_response(json.dumps(data), "scene_composite")
    assert decision["score"] == 65
    assert not decision["identity_mismatch"]
    assert not decision["accepted"]
    data["scene"]["lighting"]["score"] = 80
    data["scene"]["edges"]["score"] = 90
    data["scene"]["shadows"]["score"] = 70
    assert parse_response(json.dumps(data), "scene_composite")["score"] == 79.5


@pytest.mark.parametrize("score", [-1, 101, "99", True, float("nan")])
def test_invalid_scores_rejected(score):
    data = response()
    data["ghost_fidelity"]["score"] = score
    with pytest.raises(ValueError):
        parse_response(json.dumps(data), "flat_lay")


def test_provider_total_and_wrong_mode_rejected():
    data = response()
    data["overall"] = 100
    with pytest.raises(ValueError):
        parse_response(json.dumps(data), "flat_lay")
    with pytest.raises(ValueError):
        parse_response(json.dumps(response()), "scene_composite")


@pytest.fixture
def agent(product, monkeypatch):
    # Bypass ADK initialization; none of these tests may dispatch it.
    agent = object.__new__(qa.QualityAgent)
    monkeypatch.setattr(agent, "execute", AsyncMock(side_effect=AssertionError("No ADK calls")))
    return agent


@pytest.mark.asyncio
@pytest.mark.parametrize("second", ["pass", "low", "hidden", "error"])
async def test_dual_judge_policy(agent, tmp_path, monkeypatch, second):
    candidate = tmp_path / "candidate.png"
    candidate.write_bytes(b"offline-candidate")
    first = parse_response(json.dumps(response()), "flat_lay")
    other = response(score=40 if second == "low" else 100)
    if second == "hidden":
        other["identity"]["lettering"]["status"] = "not_visible"
    a = AsyncMock(return_value=first)
    b = (
        AsyncMock(side_effect=RuntimeError("secret-must-not-escape"))
        if second == "error"
        else AsyncMock(return_value=parse_response(json.dumps(other), "flat_lay"))
    )
    monkeypatch.setattr(agent, "_score_openai", a)
    monkeypatch.setattr(agent, "_score_gemini", b)
    result = await agent.verify(str(candidate), "render br-001", sku="br-001", view="front")
    assert (result.overall_status == "pass") == (second == "pass")
    assert result.success == (second != "error")
    assert "secret-must-not-escape" not in str(result)
    assert a.call_args.args[0][1] != a.call_args.args[1][1]
    agent.execute.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kwargs",
    [{}, {"view": "back"}, {"view": "side"}, {"view": "front", "reference_path": "wrong.png"}],
)
async def test_missing_or_wrong_binding_never_calls_judges(agent, monkeypatch, kwargs):
    judge = AsyncMock(side_effect=AssertionError("Must block before dispatch"))
    monkeypatch.setattr(agent, "_score_openai", judge)
    result = await agent.verify("candidate.png", "br-001", **kwargs)
    assert not result.success
    assert result.recommendation == "manual_review"
    judge.assert_not_called()


@pytest.mark.asyncio
async def test_openai_sends_both_images_schema_and_no_retries(agent, monkeypatch):
    from types import SimpleNamespace

    create = Mock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    finish_reason="stop",
                    message=SimpleNamespace(content=json.dumps(response()), refusal=None),
                )
            ]
        )
    )
    client = Mock()
    client.with_options.return_value.chat.completions.create = create
    monkeypatch.setattr("skyyrose.elite_studio.config.get_openai_client", lambda: client)
    result = await agent._score_openai(
        ("image/png", "REF", "a"), ("image/jpeg", "CAND", "b"), "compare", "flat_lay"
    )
    body = create.call_args.kwargs
    images = [
        p["image_url"]["url"] for p in body["messages"][0]["content"] if p["type"] == "image_url"
    ]
    assert images == ["data:image/png;base64,REF", "data:image/jpeg;base64,CAND"]
    assert body["response_format"]["json_schema"]["strict"] is True
    client.with_options.assert_called_once_with(max_retries=0)
    assert result["accepted"]


def test_gemini_serializes_pair_and_detects_truncation(monkeypatch):
    from skyyrose.elite_studio import gemini_rest

    post = Mock(
        return_value={
            "success": True,
            "data": {
                "candidates": [
                    {"finishReason": "MAX_TOKENS", "content": {"parts": [{"text": "{}"}]}}
                ]
            },
        }
    )
    monkeypatch.setattr(gemini_rest, "_post_with_retry", post)
    result = gemini_rest.analyze_vision(
        "fixture-model",
        "compare",
        "CAND",
        reference_images=[{"mime_type": "image/png", "data": "REF"}],
        response_schema=JudgeResponse.model_json_schema(),
    )
    payload = post.call_args.args[2]
    images = [
        p["inline_data"]["data"] for p in payload["contents"][0]["parts"] if "inline_data" in p
    ]
    assert images == ["REF", "CAND"]
    assert post.call_args.kwargs == {"attempt_limit": 1}
    assert payload["generationConfig"]["responseMimeType"] == "application/json"
    assert not result["success"]


@pytest.mark.parametrize("mode", ["flat_lay", "scene_composite"])
def test_blank_evidence_rejected(mode):
    data = response(mode)
    data["identity"]["lettering"]["evidence"] = "   "
    with pytest.raises(ValueError):
        parse_response(json.dumps(data), mode)


@pytest.mark.asyncio
async def test_openai_refusal_or_truncation_is_not_parseable_approval(agent, monkeypatch):
    from types import SimpleNamespace

    client = Mock()
    monkeypatch.setattr("skyyrose.elite_studio.config.get_openai_client", lambda: client)
    for finish, refusal in (("length", None), ("stop", "refused")):
        client.with_options.return_value.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    finish_reason=finish,
                    message=SimpleNamespace(content=json.dumps(response()), refusal=refusal),
                )
            ]
        )
        with pytest.raises(ValueError):
            await agent._score_openai(
                ("image/png", "REF", "a"), ("image/png", "CAND", "b"), "compare", "flat_lay"
            )


def test_gemini_structured_qa_never_rotates_keys_on_failure(monkeypatch):
    from skyyrose.elite_studio import gemini_rest

    monkeypatch.setattr(gemini_rest, "_KEYS", ["offline-one", "offline-two"])
    post = Mock(
        return_value=Mock(
            status_code=429, raise_for_status=Mock(side_effect=RuntimeError("rate limit"))
        )
    )
    monkeypatch.setattr(gemini_rest.requests, "post", post)
    result = gemini_rest.analyze_vision(
        "fixture-model",
        "compare",
        "CAND",
        reference_images=[{"mime_type": "image/png", "data": "REF"}],
        response_schema=JudgeResponse.model_json_schema(),
    )
    assert not result["success"]
    assert post.call_count == 1


def test_failed_qa_never_routes_to_compositing_or_success(monkeypatch):
    from skyyrose.elite_studio.graph.edges import (
        FINALIZE,
        after_human_review,
        after_quality,
        after_quality_v2,
    )
    from skyyrose.elite_studio.graph.nodes.layer1 import finalize_node
    from skyyrose.elite_studio.models import QualityVerification

    monkeypatch.setattr("skyyrose.elite_studio.telemetry.write_run_summary", lambda *args: None)
    for qc in (
        None,
        QualityVerification(success=False, overall_status="fail", recommendation="manual_review"),
        QualityVerification(success=True, overall_status="fail", recommendation="regenerate"),
    ):
        state = {
            "sku": "br-001",
            "status": "running",
            "quality_result": qc,
            "retry_count": 2,
            "max_retries": 2,
            "enable_compositor": True,
        }
        assert after_quality(state) == FINALIZE
        assert after_quality_v2(state) == FINALIZE
        assert after_human_review(state) == FINALIZE
        result = finalize_node(state)
        assert result["status"] == "error"
        assert result["failed_step"] == "quality"
