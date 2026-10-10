import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from skyyrose.elite_studio.agents.three_d_agent import ThreeDAgent


@pytest.fixture
def mock_three_d_agent():
    with (
        patch("skyyrose.elite_studio.agents.three_d_agent.ThreeDGenerationPipeline"),
        patch("skyyrose.elite_studio.agents.three_d_agent.VirtualPhotoshootGenerator"),
        patch("skyyrose.elite_studio.agents.three_d_agent.Path.mkdir"),
    ):
        agent = ThreeDAgent(output_dir_3d="/tmp/renders/3d", output_dir_2d="/tmp/renders/2d")
        return agent


def _make_meshy_mock(model_path: str = "/tmp/renders/3d/techflat_meshy.glb"):
    """Return a configured MeshyClient async context-manager mock."""
    mock_instance = AsyncMock()
    mock_instance.generate_from_image.return_value = {
        "model_path": model_path,
        "thumbnail_url": "http://example.com/thumb.png",
        "task_id": "task-abc",
        "model_urls": {"glb": "http://example.com/model.glb"},
    }
    mock_cls = MagicMock()
    mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
    return mock_cls, mock_instance


def _make_flux_result(
    output_path: str | None = "/tmp/renders/2d/br-001/final.jpg",
    error: str = "",
    ok: bool = True,
):
    """Build a RenderResult-shaped mock for the FLUX synthesis pipeline.

    The legacy GeneratorAgent (Gemini RAS) was replaced by ``flux_render``;
    tests must mock the new entry point, not the removed class.
    """
    audit = MagicMock()
    audit.to_dict = MagicMock(return_value={"matches_dossier": ok, "violations": []})
    result = MagicMock()
    result.ok = ok
    result.output_path = Path(output_path) if output_path else None
    result.quarantine_path = None
    result.audit_result = audit
    result.manifest = {}
    result.attempts = 1
    result.duration_ms = 0
    result.error = error
    return result


def _fake_product_with_dossier(sku: str = "br-001") -> dict:
    """Return a deterministic fake product+dossier payload for unit tests.

    Mirrors the shape returned by skyyrose.core.product.get_product
    without touching the canonical CSV or filesystem.
    """
    return {
        "sku": sku,
        "name": "Test Product",
        "collection": "black-rose",
        "dossier_slug": "test-product",
        "corrections": [{"text": "exact founder correction", "authority": "FOUNDER_CONFIRMED"}],
        "provenance": {"fixture": True},
        "dossier": {
            "sku": sku,
            "name": "Test Product",
            "collection": "black-rose",
            "slug": "test-product",
            "garment_type_lock": "Test garment. NOT a jersey.",
            "branding_block": "### Front\n- **front-chest** (10in): test. **Technique:** embossed. **Color:** black.",
            "negative_block": "- No printed graphics.",
            "scene_pose": "test pose",
            "scene_setting": "test setting",
        },
    }


def _patch_dossier_loader():
    """Patch the lazy-imported dossier loader inside generate_replica."""
    return patch(
        "skyyrose.core.product.get_product",
        return_value=_fake_product_with_dossier(),
    )


def _make_audit_mock(matches_dossier: bool = True):
    """Mock VisionAuditAgent to return a deterministic audit result."""
    audit_instance = MagicMock()
    audit_result = MagicMock()
    audit_result.ok = matches_dossier
    audit_result.matches_dossier = matches_dossier
    audit_result.violations = []
    audit_result.to_dict = MagicMock(
        return_value={
            "matches_dossier": matches_dossier,
            "violations": [],
            "raw_text": "",
            "model": "gemini-3-flash-preview",
            "error": "",
        }
    )
    audit_instance.audit = MagicMock(return_value=audit_result)
    cls_mock = MagicMock(return_value=audit_instance)
    return cls_mock


@pytest.mark.asyncio
async def test_three_d_agent_initialization(mock_three_d_agent):
    assert mock_three_d_agent.output_dir_3d == Path("/tmp/renders/3d")
    assert mock_three_d_agent.output_dir_2d == Path("/tmp/renders/2d")


@pytest.mark.asyncio
async def test_generate_replica_success(mock_three_d_agent, sample_sku):
    mock_meshy_cls, _ = _make_meshy_mock()
    flux_result = _make_flux_result()

    with (
        _patch_dossier_loader(),
        patch("skyyrose.elite_studio.agents.three_d_agent.MeshyClient", mock_meshy_cls),
        patch("skyyrose.elite_studio.agents.three_d_agent.subprocess.run"),
        patch(
            "skyyrose.elite_studio.synthesis.render",
            new_callable=AsyncMock,
            return_value=flux_result,
        ) as render_mock,
        patch(
            "skyyrose.elite_studio.agents.three_d_agent.CreativeAgent.execute",
            new_callable=AsyncMock,
            return_value={},
        ),
        patch(
            "skyyrose.elite_studio.agents.vision_audit_agent.VisionAuditAgent",
            _make_audit_mock(matches_dossier=True),
        ),
        patch(
            "skyyrose.elite_studio.forensics.write_manifest",
            return_value=Path("/tmp/manifest.json"),
        ),
        patch(
            "skyyrose.elite_studio.forensics.quarantine_path",
            return_value=Path("/tmp/quarantine"),
        ),
    ):
        result = await mock_three_d_agent.generate_replica(sample_sku, "path/to/techflat.png")

    from skyyrose.elite_studio.synthesis.prompts.base_prompts import build_base_prompt

    delivered = render_mock.call_args.kwargs["dossier"]
    assert delivered["product_corrections"] == _fake_product_with_dossier()["corrections"]
    assert "exact founder correction" in build_base_prompt(delivered)
    assert "FOUNDER_CONFIRMED" in build_base_prompt(delivered)
    assert result["reference_evidence"]["view"] == "front"
    assert result["success"] is True
    assert "glb_path" in result
    assert "renders" in result
    # Fidelity must be a real computed value, not the old hardcoded constant
    assert 0.0 <= result["fidelity_score"] <= 100.0
    assert result["fidelity_score"] != 99.0
    assert result["provider"] == "flux"


@pytest.mark.asyncio
async def test_meshy_failure_returns_error(mock_three_d_agent):
    """When MeshyClient returns None, generate_replica must report failure."""
    mock_instance = AsyncMock()
    mock_instance.generate_from_image.return_value = None
    mock_cls = MagicMock()
    mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

    with (
        _patch_dossier_loader(),
        patch("skyyrose.elite_studio.agents.three_d_agent.MeshyClient", mock_cls),
        patch(
            "skyyrose.elite_studio.agents.three_d_agent.CreativeAgent.execute",
            new_callable=AsyncMock,
            return_value={},
        ),
    ):
        result = await mock_three_d_agent.generate_replica("br-001", "path/to/techflat.png")

    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_blender_failure_falls_back_gracefully(mock_three_d_agent):
    """Blender failure should not crash the pipeline — fallback to techflat scaffold."""
    mock_meshy_cls, _ = _make_meshy_mock()
    flux_result = _make_flux_result()

    with (
        _patch_dossier_loader(),
        patch("skyyrose.elite_studio.agents.three_d_agent.MeshyClient", mock_meshy_cls),
        patch(
            "skyyrose.elite_studio.agents.three_d_agent.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "blender"),
        ),
        patch(
            "skyyrose.elite_studio.synthesis.render",
            new_callable=AsyncMock,
            return_value=flux_result,
        ),
        patch(
            "skyyrose.elite_studio.agents.three_d_agent.CreativeAgent.execute",
            new_callable=AsyncMock,
            return_value={},
        ),
        patch(
            "skyyrose.elite_studio.agents.vision_audit_agent.VisionAuditAgent",
            _make_audit_mock(matches_dossier=True),
        ),
        patch(
            "skyyrose.elite_studio.forensics.write_manifest",
            return_value=Path("/tmp/manifest.json"),
        ),
        patch(
            "skyyrose.elite_studio.forensics.quarantine_path",
            return_value=Path("/tmp/quarantine"),
        ),
        # Thumbnail fetch succeeds
        patch("skyyrose.elite_studio.agents.three_d_agent.httpx.AsyncClient") as mock_http,
    ):
        mock_resp = MagicMock()
        mock_resp.content = b"fake-image-bytes"
        mock_resp.raise_for_status = MagicMock()
        mock_http.return_value.__aenter__ = AsyncMock(
            return_value=MagicMock(get=AsyncMock(return_value=mock_resp))
        )
        mock_http.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await mock_three_d_agent.generate_replica("br-001", "path/to/techflat.png")

    assert result["success"] is True
    # Blender fallback lowers fidelity score below 100
    assert result["fidelity_score"] < 100.0


@pytest.mark.asyncio
async def test_none_synth_result_returns_error(mock_three_d_agent):
    """A FLUX synthesis failure (no output, no quarantine) returns a failure dict."""
    mock_meshy_cls, _ = _make_meshy_mock()
    flux_result = _make_flux_result(
        output_path=None,
        error="Synthesis failed: no output produced",
        ok=False,
    )

    with (
        _patch_dossier_loader(),
        patch("skyyrose.elite_studio.agents.three_d_agent.MeshyClient", mock_meshy_cls),
        patch("skyyrose.elite_studio.agents.three_d_agent.subprocess.run"),
        patch(
            "skyyrose.elite_studio.synthesis.render",
            new_callable=AsyncMock,
            return_value=flux_result,
        ),
        patch(
            "skyyrose.elite_studio.agents.three_d_agent.CreativeAgent.execute",
            new_callable=AsyncMock,
            return_value={},
        ),
    ):
        result = await mock_three_d_agent.generate_replica("br-001", "path/to/techflat.png")

    assert result["success"] is False
    assert "Synthesis" in result["error"]


@pytest.fixture(autouse=True)
def reference_fixture(monkeypatch):
    monkeypatch.setattr(
        "skyyrose.core.product.render_reference",
        lambda record, view: {
            "path": str(Path("path/to/techflat.png").resolve()),
            "view": view,
            "sku": record["sku"],
        },
    )
