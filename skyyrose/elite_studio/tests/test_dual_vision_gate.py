from unittest.mock import AsyncMock, patch

import pytest

from skyyrose.elite_studio.agents.vision_agent import DualVisionGate, VisionAgent


def _make_gate() -> DualVisionGate:
    """Build a DualVisionGate with the OpenAI client and the inherited ADK
    `execute` method stubbed. `verify_reference` calls `await self.execute(...)`
    for ADK observability before any model call — without this stub, tests would
    hit the real CreativeAgent.execute and emit un-awaited-coroutine warnings.
    """
    with patch("openai.OpenAI"):
        gate = DualVisionGate()
    gate.execute = AsyncMock(return_value={})
    return gate


def test_alias_works():
    """VisionAgent must remain importable for nodes.py compatibility."""
    assert VisionAgent is DualVisionGate


@pytest.mark.asyncio
async def test_consensus_both_yes(tmp_path):
    """Both models YES → passed=True, verdict=consensus."""
    img = tmp_path / "test.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100)  # minimal JPEG header

    gate = _make_gate()
    with (
        patch.object(gate, "_call_openai", return_value="YES: confirms hoodie"),
        patch.object(gate, "_call_gemini", return_value="YES: hoodie confirmed"),
    ):
        result = await gate.verify_reference(str(img), sku="br-004", expected_garment="hoodie")

    assert result.passed


@pytest.mark.asyncio
async def test_consensus_a_no_blocks(tmp_path):
    """Agent A NO → passed=False even if B says YES."""
    img = tmp_path / "test.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100)

    gate = _make_gate()
    with (
        patch.object(gate, "_call_openai", return_value="NO: this is a baseball jersey"),
        patch.object(gate, "_call_gemini", return_value="YES: looks like a hoodie"),
    ):
        result = await gate.verify_reference(
            str(img), sku="br-011", expected_garment="hockey jersey"
        )

    assert not result.passed
    assert "baseball jersey" in result.blocking_reason


@pytest.mark.asyncio
async def test_consensus_b_no_blocks(tmp_path):
    """Agent B NO → passed=False even if A says YES."""
    img = tmp_path / "test.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100)

    gate = _make_gate()
    with (
        patch.object(gate, "_call_openai", return_value="YES: hoodie confirmed"),
        patch.object(gate, "_call_gemini", return_value="NO: this is a crewneck, not a hoodie"),
    ):
        result = await gate.verify_reference(str(img), sku="br-004", expected_garment="hoodie")

    assert not result.passed


@pytest.mark.asyncio
async def test_analyze_wraps_verify_reference(tmp_path):
    """analyze() is the nodes.py interface — must return SynthesizedVision."""
    img = tmp_path / "ref.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100)

    gate = _make_gate()
    with (
        patch.object(gate, "_call_openai", return_value="YES: sg-013 mint crewneck confirmed"),
        patch.object(gate, "_call_gemini", return_value="YES: confirmed crewneck"),
    ):
        from skyyrose.elite_studio.models import SynthesizedVision

        result = await gate.analyze("sg-013", "front")
    assert isinstance(result, SynthesizedVision)
    assert result.success


@pytest.fixture(autouse=True)
def bound_reference(monkeypatch, tmp_path):
    from skyyrose.core import product

    monkeypatch.setattr(product, "REPO_ROOT", tmp_path)

    def record(sku):
        path = "ref.jpg" if sku == "sg-013" else "test.jpg"
        return {
            "sku": sku,
            "name": "Fixture garment",
            "dossier": {"branding_block": "Fixture"},
            "render_sources": {"front": path},
            "provenance": {"fixture": True},
        }

    monkeypatch.setattr("skyyrose.elite_studio.agents.vision_agent.get_product", record)
