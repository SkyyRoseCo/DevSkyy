"""Offline product/view binding and founder-prose propagation contracts."""

import copy
import json
from unittest.mock import AsyncMock, Mock

import pytest

from skyyrose.core import product as core
from skyyrose.core import product_registry
from skyyrose.elite_studio.agents import vision_agent


@pytest.fixture
def product_fixture(monkeypatch, tmp_path):
    registry = copy.deepcopy(product_registry.load_registry())
    record = registry["products"]["br-001"]
    record["corrections"] = [
        {
            "text": "Front view and back view: preserve the exact 3–4 inch artwork, also available in black.",
            "authority": "FOUNDER_CONFIRMED",
        }
    ]
    record["dossier"][
        "content"
    ] += "\n**FOUNDER_CONFIRMED:** Styled with the matching piece; front view and back view retain 3–4 inches.\n"
    record["render_sources"] = {"front": "front.png", "back": "back.png"}
    (tmp_path / "front.png").write_bytes(b"front-fixture")
    (tmp_path / "back.png").write_bytes(b"back-fixture")
    # Similarly named files must never be guessed.
    (tmp_path / "br-001.jpg").write_bytes(b"wrong-unbound-garment")
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(registry))
    monkeypatch.setattr(product_registry, "PRODUCT_REGISTRY", path)
    monkeypatch.setattr(core, "REPO_ROOT", tmp_path)
    return record, registry, path


def test_reference_exact_view_provenance_and_no_guessing(product_fixture):
    _, registry, path = product_fixture
    front = core.render_reference(core.get_product("br-001"), "front")
    back = core.render_reference(core.get_product("br-001"), "back")
    assert front["path"] != back["path"]
    assert front["sha256"] != back["sha256"]
    assert back["binding"] == "products.br-001.render_sources.back"
    assert back["provenance"]["sources"]["registry"]["sha256"]
    registry["products"]["br-001"]["render_sources"]["back"] = None
    path.write_text(json.dumps(registry))
    with pytest.raises(ValueError, match="missing render_sources.back"):
        vision_agent._reference_path("br-001", "back")


@pytest.mark.parametrize("binding", ["../outside.png", "missing.png", ""])
def test_reference_fails_closed(product_fixture, binding):
    record = core.get_product("br-001")
    record["render_sources"]["front"] = binding
    with pytest.raises((ValueError, OSError)):
        core.render_reference(record, "front")


@pytest.mark.asyncio
async def test_vision_absent_view_stops_every_dispatch(product_fixture, monkeypatch):
    _, registry, path = product_fixture
    registry["products"]["br-001"]["render_sources"]["back"] = None
    path.write_text(json.dumps(registry))
    gate = object.__new__(vision_agent.DualVisionGate)
    gate.execute = AsyncMock()
    gate._call_openai = AsyncMock()
    gate._call_gemini = AsyncMock()
    result = await gate.analyze("br-001", "back")
    assert not result.success
    result = await gate.verify_reference(
        str(path.parent / "front.png"), "br-001", "Fixture", "back"
    )
    assert not result.passed
    gate.execute.assert_not_called()
    gate._call_openai.assert_not_called()
    gate._call_gemini.assert_not_called()


@pytest.mark.asyncio
async def test_vision_rejects_substitution_and_carries_evidence(product_fixture):
    _, _, path = product_fixture
    gate = object.__new__(vision_agent.DualVisionGate)
    gate.execute = AsyncMock()
    gate._call_openai = AsyncMock(return_value="YES")
    gate._call_gemini = AsyncMock(return_value="YES")
    result = await gate.verify_reference(
        str(path.parent / "front.png"), "br-001", "Fixture", "back"
    )
    assert not result.passed
    gate.execute.assert_not_called()
    result = await gate.analyze("br-001", "back")
    assert result.success
    assert result.reference_evidence["view"] == "back"
    assert gate._call_openai.call_args.args[0] == str(path.parent / "back.png")


def test_oai_dossier_and_corrections_preserved(product_fixture):
    from scripts.oai_render import prompt
    from skyyrose.core.dossier_loader import DOSSIERS_DIR

    record, _, _ = product_fixture
    body = prompt.read_dossier(DOSSIERS_DIR / (record["dossier"]["slug"] + ".md"))
    assert body == record["dossier"]["content"]
    result = prompt.build_prompt(
        name="Fixture",
        sku="br-001",
        collection="black-rose",
        reference_labels=[],
        dossier_text=body,
        is_patch=False,
    )
    assert record["corrections"][0]["text"] in result
    assert record["dossier"]["content"] in result
    with pytest.raises(KeyError):
        prompt.corrections_for("br-999")


def test_lookbook_serialized_request_contains_current_truth(product_fixture, monkeypatch, tmp_path):
    from scripts.oai_render import lookbook
    from scripts.oai_render.references import ReferenceImage

    record, registry, path = product_fixture
    scene = tmp_path / "scene.png"
    scene.write_bytes(b"scene-fixture")
    client = Mock()
    client.edit.return_value = b"mocked-result"
    monkeypatch.setattr(lookbook, "OAIImageClient", lambda: client)

    # Isolate supplementary artwork; still resolve the current bound garment.
    def refs(sku, collection):
        from pathlib import Path

        ref = core.render_reference(core.get_product(sku), "front")
        return [ReferenceImage(path=Path(ref["path"]), label="front", kind="garment")]

    monkeypatch.setattr(lookbook, "_garment_refs", refs)
    lookbook._generate_one("br-001", scene, None, tmp_path / "out.png")
    assert record["corrections"][0]["text"] in client.edit.call_args.kwargs["prompt"]
    assert str(client.edit.call_args.kwargs["image_paths"][0]) == str(tmp_path / "front.png")
    registry["products"]["br-001"]["render_sources"]["front"] = "back.png"
    path.write_text(json.dumps(registry))
    lookbook._generate_one("br-001", scene, None, tmp_path / "out.png")
    assert str(client.edit.call_args.kwargs["image_paths"][0]) == str(tmp_path / "back.png")


def test_platform_record_preserves_compatibility_and_full_truth(product_fixture):
    from skyyrose.elite_studio.platform.catalog_source import SkyyRoseCatalogSource

    result = SkyyRoseCatalogSource().get("br-001")
    record = core.get_product("br-001")
    assert result.row == record["catalog_row"]
    assert result.product["corrections"] == record["corrections"]
    assert result.product["render_sources"] == record["render_sources"]
    assert result.product["provenance"]["sources"] == record["provenance"]["sources"]


def test_missing_dossier_has_no_mirror_fallback(product_fixture):
    from scripts.oai_render import lookbook
    from scripts.oai_render.references import MissingReferenceError
    from skyyrose.core.dossier_loader import DossierMissingError
    from skyyrose.elite_studio.platform.catalog_source import SkyyRoseCatalogSource

    _, registry, path = product_fixture
    registry["products"]["br-001"]["dossier"]["content"] = ""
    path.write_text(json.dumps(registry))
    with pytest.raises(DossierMissingError):
        SkyyRoseCatalogSource().get("br-001")
    with pytest.raises(MissingReferenceError):
        lookbook._resolve("br-001", None)


@pytest.mark.asyncio
async def test_three_d_rejects_wrong_reference_before_dispatch(product_fixture, monkeypatch):
    from skyyrose.elite_studio.agents import three_d_agent

    agent = object.__new__(three_d_agent.ThreeDAgent)
    agent.execute = AsyncMock()
    provider = Mock()
    monkeypatch.setattr(three_d_agent, "MeshyClient", provider)
    _, _, path = product_fixture
    with pytest.raises(ValueError, match="registry front binding"):
        await agent.generate_replica("br-001", str(path.parent / "back.png"))
    agent.execute.assert_not_called()
    provider.assert_not_called()
