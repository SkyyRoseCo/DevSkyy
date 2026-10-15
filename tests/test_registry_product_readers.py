"""Default product readers use registry records, with isolated legacy fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from skyyrose.core import dossier_loader, sot_images


def _markdown(material: str) -> str:
    return (
        "---\nsku: test-001\nname: Founder product\ncollection: signature\n---\n"
        f"# Product\n\n**Garment type lock:** {material}\n\n"
        "## Branding\nFront embroidery.\n\n## Negative\n- No invented marks.\n"
    )


@pytest.fixture
def registry_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "logo-registry.json"
    path.write_text(
        json.dumps(
            {
                "products": {
                    "test-001": {
                        "catalog": {"sku": "test-001", "collection": "signature"},
                        "dossier": {"slug": "founder-product", "content": _markdown("Satin")},
                        "images": {
                            "front_model_image": {"path": "assets/model.webp"},
                            "image": {"path": "assets/flat.jpeg"},
                            "back_image": {"path": "assets/back.jpeg"},
                        },
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    def read_current_registry() -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    # The registry API has its own schema/loading tests; these tests exercise
    # reader routing and refresh against actual changing file contents.
    monkeypatch.setattr(dossier_loader, "load_registry", read_current_registry)
    monkeypatch.setattr(sot_images, "load_registry", read_current_registry)
    return path


def test_default_dossier_ignores_generated_markdown(
    registry_file: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mirrors = tmp_path / "dossiers"
    mirrors.mkdir()
    (mirrors / "founder-product.md").write_text(_markdown("Wrong fleece"))
    monkeypatch.setattr(dossier_loader, "DOSSIERS_DIR", mirrors)

    dossier = dossier_loader.load_dossier("founder-product")
    assert dossier.garment_type_lock == "Satin"
    assert dossier.slug == "founder-product"
    assert dossier_loader.load_dossier("founder-product", mirrors).raw == dossier.raw


def test_dossier_observes_founder_correction_without_cache_clear(registry_file: Path) -> None:
    assert dossier_loader.load_dossier("founder-product").garment_type_lock == "Satin"
    payload = json.loads(registry_file.read_text())
    payload["products"]["test-001"]["dossier"]["content"] = _markdown("Corrected satin")
    registry_file.write_text(json.dumps(payload))
    assert dossier_loader.load_dossier("founder-product").garment_type_lock == "Corrected satin"


def test_structured_garment_fields_never_rewrite_the_founders_prose(registry_file: Path) -> None:
    """Structured garment fields live beside the dossier, never inside its prose.

    They are extracted from the founder's prose, so letting them replace the
    Garment type lock would put derived text -- and sizes -- into render prompts
    in place of what the founder wrote.
    """
    payload = json.loads(registry_file.read_text())
    garment = {
        "materials": {"specification": "Nylon", "source": "derived_from_dossier"},
        "fit": {"specification": "Relaxed", "source": "derived_from_dossier"},
        "color": "Black",
        "available_sizes": ["S", "M"],
    }
    payload["products"]["test-001"]["garment"] = garment
    registry_file.write_text(json.dumps(payload))

    dossier = dossier_loader.load_dossier("founder-product")

    assert dossier.garment_type_lock == "Satin"
    assert dossier.raw == _markdown("Satin")
    for injected in ("Nylon", "Relaxed", "Available sizes", "take precedence"):
        assert injected not in dossier.garment_type_lock
    assert json.loads(registry_file.read_text())["products"]["test-001"]["garment"] == garment


@pytest.mark.parametrize("content", [None, "", "   "])
def test_missing_registry_dossier_fails_closed(registry_file: Path, content: str | None) -> None:
    payload = json.loads(registry_file.read_text())
    payload["products"]["test-001"]["dossier"]["content"] = content
    registry_file.write_text(json.dumps(payload))
    with pytest.raises(dossier_loader.DossierMissingError, match="product registry"):
        dossier_loader.load_dossier("founder-product")


def test_unknown_dossier_does_not_fall_back_to_mirror(
    registry_file: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "obsolete.md").write_text(_markdown("Obsolete mirror"))
    monkeypatch.setattr(dossier_loader, "DOSSIERS_DIR", tmp_path)
    with pytest.raises(dossier_loader.DossierMissingError):
        dossier_loader.load_dossier("obsolete")


def test_explicit_noncanonical_dossier_fixture_still_works(tmp_path: Path) -> None:
    (tmp_path / "fixture.md").write_text(_markdown("Fixture material"))
    assert dossier_loader.load_dossier("fixture", tmp_path).garment_type_lock == "Fixture material"
    (tmp_path / "fixture.md").write_text(_markdown("Changed fixture"))
    assert dossier_loader.load_dossier("fixture", tmp_path).garment_type_lock == "Changed fixture"


def test_registry_images_keep_front_first_and_back_fallback(registry_file: Path) -> None:
    assert sot_images.resolve_image("test-001") == "assets/model.webp"
    assert sot_images.resolve_image("test-001", "packshot") == "assets/flat.jpeg"
    assert sot_images.resolve_image("test-001", "back") == "assets/back.jpeg"
    assert sot_images.has_render("test-001")
    assert sot_images.all_skus() == ["test-001"]
    assert sot_images.resolve_image("missing") is None


def test_registry_image_edit_is_immediately_visible(registry_file: Path) -> None:
    assert sot_images.resolve_image("test-001") == "assets/model.webp"
    payload = json.loads(registry_file.read_text())
    del payload["products"]["test-001"]["images"]["front_model_image"]
    registry_file.write_text(json.dumps(payload))
    assert sot_images.resolve_image("test-001") == "assets/flat.jpeg"
    assert not sot_images.has_render("test-001")
    assert sot_images.build_manifest()["test-001"]["front"] == "assets/flat.jpeg"
    sot_images.refresh()  # Retained public API; no stale cache is needed.


def test_default_images_ignore_canonical_generated_collection_tree(
    registry_file: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    collection = tmp_path / "signature"
    collection.mkdir()
    (collection / "sot.json").write_text('{"products":[{"sku":"obsolete"}]}')
    monkeypatch.setattr(sot_images, "COLLECTIONS_DIR", tmp_path)
    monkeypatch.setattr(sot_images, "_CANONICAL_COLLECTIONS_DIR", tmp_path)
    assert sot_images.all_skus() == ["test-001"]


def test_noncanonical_collection_fixture_remains_explicit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    collection = tmp_path / "fixture-collection"
    collection.mkdir()
    (collection / "sot.json").write_text(
        json.dumps(
            {"products": [{"sku": "fixture", "images": {"image": {"path": "assets/f.jpg"}}}]}
        )
    )
    monkeypatch.setattr(sot_images, "COLLECTIONS_DIR", tmp_path)
    assert sot_images.resolve_image("fixture") == "assets/f.jpg"
    assert sot_images._index()["fixture"]["collection"] == "fixture-collection"


def test_registry_image_paths_still_reject_traversal(registry_file: Path) -> None:
    payload = json.loads(registry_file.read_text())
    payload["products"]["test-001"]["images"]["front_model_image"]["path"] = "../secret"
    registry_file.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="escapes"):
        sot_images.resolve_image("test-001")
