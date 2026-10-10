"""Dual-judge policy with registry-bound offline reference fixtures."""

from unittest.mock import AsyncMock

import pytest

from skyyrose.elite_studio.agents import quality_agent
from skyyrose.elite_studio.agents.qa_contract import JudgeResponse


def _decision(fidelity=100, mismatch=False):
    finding = {"status": "match", "evidence": "Visible reference agrees with candidate"}
    identity = {
        k: dict(finding)
        for k in ("silhouette", "construction", "artwork", "lettering", "color", "placement")
    }
    if mismatch:
        identity["silhouette"]["status"] = "mismatch"
    return JudgeResponse.model_validate(
        {
            "identity": identity,
            "scene": None,
            "ghost_fidelity": {"score": fidelity, "evidence": "Visible volume/drape"},
            "notes": "Synthetic fixture",
        }
    ).decision("flat_lay")


@pytest.fixture
def agent(monkeypatch, tmp_path):
    image = tmp_path / "reference.png"
    image.write_bytes(b"offline-image")
    monkeypatch.setattr(quality_agent, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        quality_agent,
        "get_product",
        lambda sku: {
            "sku": sku,
            "render_sources": {"front": "reference.png"},
            "dossier": {"full_text": "Founder fixture specification"},
        },
    )
    return object.__new__(quality_agent.QualityAgent), str(image)


async def test_both_pass_at_80_threshold(agent, monkeypatch):
    qa, image = agent
    monkeypatch.setattr(qa, "_score_openai", AsyncMock(return_value=_decision(50)))
    monkeypatch.setattr(qa, "_score_gemini", AsyncMock(return_value=_decision(55)))
    result = await qa.verify(image, "br-004", view="front")
    assert result.success and result.overall_status == "pass"
    assert result.details["min_score"] == 80


async def test_min_score_below_80_fails(agent, monkeypatch):
    qa, image = agent
    monkeypatch.setattr(qa, "_score_openai", AsyncMock(return_value=_decision()))
    monkeypatch.setattr(qa, "_score_gemini", AsyncMock(return_value=_decision(49)))
    result = await qa.verify(image, "br-004", view="front")
    assert result.overall_status == "fail"
    assert result.recommendation == "regenerate"


async def test_identity_mismatch_auto_rejects(agent, monkeypatch):
    qa, image = agent
    monkeypatch.setattr(qa, "_score_openai", AsyncMock(return_value=_decision(mismatch=True)))
    monkeypatch.setattr(qa, "_score_gemini", AsyncMock(return_value=_decision()))
    result = await qa.verify(image, "br-011", view="front")
    assert result.overall_status == "fail"
    assert "identity" in result.details["reject_reason"]
