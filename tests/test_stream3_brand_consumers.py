"""Offline output contracts for the bounded stream 3 consumer correction."""

import json

import pytest

from skyyrose.core.product import get_product
from skyyrose.multi_agent.agents import BRAND_WRITER, PRODUCT_ANALYST
from skyyrose.multi_agent.orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
from skyyrose.multi_agent.tools import generate_product_copy, get_brand_guidelines


@pytest.mark.asyncio
async def test_brand_guidelines_has_no_active_tagline():
    result = await get_brand_guidelines.handler({})
    guidelines = json.loads(result["content"][0]["text"])
    assert guidelines["tagline"] == ""
    assert guidelines["retired_taglines"] == [
        "Luxury Grows from Concrete.",
        "Where Love Meets Luxury",
    ]
    for prompt in (BRAND_WRITER.prompt, ORCHESTRATOR_SYSTEM_PROMPT):
        assert "No active brand tagline" in prompt
        assert "Luxury Grows from Concrete" not in prompt
        assert "Where Love Meets Luxury" not in prompt


@pytest.mark.asyncio
async def test_copy_support_returns_complete_registry_record():
    result = await generate_product_copy.handler({"sku": "br-001"})
    payload = json.loads(result["content"][0]["text"])
    expected = get_product("br-001")
    actual = payload["product_data"]
    for field in ("sku", "catalog", "garment", "dossier", "content", "authority", "gaps"):
        assert actual[field] == expected[field]
    assert "FOUNDER_CONFIRMED" in payload["instruction"]
    assert "get_product" in PRODUCT_ANALYST.prompt
    assert "cite the registry provenance" in PRODUCT_ANALYST.prompt


@pytest.mark.asyncio
async def test_copy_support_unknown_sku_reports_failure_without_empty_specs():
    result = await generate_product_copy.handler({"sku": "unknown-sku"})
    payload = json.loads(result["content"][0]["text"])
    assert payload["success"] is False
    assert "product_data" not in payload


def test_canonical_copy_reader_is_allowed_for_nested_agents():
    for agent in (BRAND_WRITER, PRODUCT_ANALYST):
        assert "mcp__skyyrose-tools__generate_product_copy" in agent.tools
        assert "mcp__skyyrose-tools__elite_studio_produce" not in agent.tools
    assert "mcp__skyyrose-tools__get_brand_guidelines" in BRAND_WRITER.tools
