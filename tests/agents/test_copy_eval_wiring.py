"""Wiring tests for the opt-in copy-quality gate in SkyyRoseContentAgent.

The gate is soft-signal and OFF by default (COPY_EVAL_ENABLED). These tests cover the
seam without any live LLM: brief construction maps brand fields, the gate is a no-op when
disabled, and when enabled it records the verdict into content.metadata and never blocks.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agents.skyyrose_content_agent import (
    BrandDNA,
    ContentRequest,
    ContentType,
    GeneratedContent,
    SkyyRoseContentAgent,
)
from evaluation.contracts import Verdict
from orchestration.brand_context import Collection


@pytest.fixture
def agent() -> SkyyRoseContentAgent:
    with patch("agents.skyyrose_content_agent.BrandContextInjector") as mock_injector:
        mock_injector.return_value = MagicMock()
        a = SkyyRoseContentAgent()
    a._brand_dna = BrandDNA()
    return a


@pytest.fixture
def request_obj() -> ContentRequest:
    return ContentRequest(
        content_type=ContentType.COLLECTION_PAGE,
        collection=Collection.BLACK_ROSE,
        title="Black Rose Crewneck",
        additional_direction="armor, not lifestyle",
    )


def _content() -> GeneratedContent:
    return GeneratedContent(
        content_type=ContentType.COLLECTION_PAGE,
        collection=Collection.BLACK_ROSE,
        title="Black Rose Crewneck",
        body_html="<p>The Black Rose Crewneck is armor.</p>",
    )


def test_build_copy_brief_maps_brand_fields(agent, request_obj):
    brief = agent._build_copy_brief(_content(), request_obj)
    assert brief.collection == Collection.BLACK_ROSE.value
    assert brief.content_type == request_obj.content_type.value
    assert brief.product_name == request_obj.title
    assert brief.additional_direction == "armor, not lifestyle"
    assert "SKYYROSE" in brief.brand_voice_context  # pulled from BrandDNA.to_prompt_context()


@pytest.mark.asyncio
async def test_maybe_eval_copy_disabled_is_noop(agent, request_obj, monkeypatch):
    monkeypatch.delenv("COPY_EVAL_ENABLED", raising=False)

    class _Boom:
        async def evaluate(self, **_):
            raise AssertionError("evaluator must not run when COPY_EVAL_ENABLED is unset")

    content = _content()
    out = await agent._maybe_eval_copy(content, request_obj, evaluator=_Boom())

    assert out is content
    assert "copy_eval" not in content.metadata


@pytest.mark.asyncio
async def test_maybe_eval_copy_enabled_records_verdict_and_never_blocks(
    agent, request_obj, monkeypatch
):
    monkeypatch.setenv("COPY_EVAL_ENABLED", "1")

    class _Fake:
        async def evaluate(self, *, subject, ref):
            assert "armor" in subject  # the body_html is what gets judged
            return Verdict(
                domain="copy",
                passed=False,
                score=0.42,
                gate_results={},
                failure_tags=("voice_drift",),
                reason="too hedged",
                cost_usd=0.004,
            )

    content = _content()
    out = await agent._maybe_eval_copy(content, request_obj, evaluator=_Fake())

    assert out is content  # soft-signal: failing copy is still returned, never blocked
    record = content.metadata["copy_eval"]
    assert record["passed"] is False
    assert record["score"] == 0.42
    assert record["failure_tags"] == ["voice_drift"]
    assert record["cost_usd"] == 0.004


@pytest.mark.asyncio
async def test_maybe_eval_copy_judge_exception_does_not_block(agent, request_obj, monkeypatch):
    """A crashing judge must NOT abort generation — soft-signal records the error and returns."""
    monkeypatch.setenv("COPY_EVAL_ENABLED", "1")

    class _Boom:
        async def evaluate(self, *, subject, ref):
            raise RuntimeError("judge unreachable")

    content = _content()
    out = await agent._maybe_eval_copy(content, request_obj, evaluator=_Boom())

    assert out is content  # never blocks, even when the evaluator crashes
    assert "error" in content.metadata["copy_eval"]
