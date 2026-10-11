"""Isolated geometry/source/review bindings; no canonical registry writes."""

from __future__ import annotations

import copy
import hashlib
import json

import pytest
from PIL import Image

from skyyrose.core.card_annotations import geometry_digest, geometry_paths, validate_annotation
from skyyrose.core.product_registry import update_garment_highlights


@pytest.fixture
def setup(tmp_path):
    theme = tmp_path / "theme"
    (theme / "assets/cards").mkdir(parents=True)
    (theme / "data").mkdir()
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "products": {
                    sku: {"catalog": {"sku": sku}, "garment": {"materials": "founder words"}}
                    for sku in ("a", "b")
                }
            }
        )
    )
    approved = {}
    annotations = {}
    rows = []
    for index, sku in enumerate(("a", "b")):
        asset = theme / f"assets/cards/{sku}.webp"
        Image.new("RGB", (1024, 1536), (index * 30, 20, 30)).save(asset)
        source = {
            "path": f"assets/cards/{sku}.webp",
            "sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
            "width": 1024,
            "height": 1536,
        }
        approved[sku] = {
            "src": source["path"],
            "sha256": source["sha256"],
            "width": 1024,
            "height": 1536,
            "scene_status": "FOUNDER_APPROVED_V2_CARD",
            "current_fidelity_status": "EXISTING_SCOPED_APPROVAL_RETAINED",
        }
        polygons = [
            {
                "outer": [[100, 100], [900, 100], [900, 1400], [100, 1400]],
                "holes": [[[200, 200], [300, 200], [300, 300], [200, 300]]],
            }
        ]
        annotations[sku] = {
            "sku": sku,
            "status": "INDEPENDENT_VISUAL_PASS",
            "source": source,
            "polygons": polygons,
            "review": {"geometry_sha256": geometry_digest(polygons)},
        }
        rows.append(
            {
                "sku": sku,
                "status": "PASS",
                "annotator": "maker-agent",
                "reviewer": "independent-agent",
                "source": source,
                "geometry_sha256": geometry_digest(polygons),
            }
        )
    (theme / "data/approved-card-fronts.json").write_text(json.dumps({"products": approved}))
    receipt = tmp_path / "review.json"
    receipt.write_text(json.dumps({"schema_version": 1, "reviews": rows}))
    for annotation in annotations.values():
        annotation["review"]["evidence_sha256"] = hashlib.sha256(receipt.read_bytes()).hexdigest()
    return theme, registry, receipt, annotations


def test_native_geometry_and_atomic_product_fact_preservation(setup):
    theme, registry, receipt, annotations = setup
    before = json.loads(registry.read_text())
    assert geometry_paths(annotations["a"]["polygons"]) == [
        "M100 100 L900 100 L900 1400 L100 1400 Z M200 200 L300 200 L300 300 L200 300 Z"
    ]
    assert update_garment_highlights(
        annotations, evidence_path=receipt, path=registry, theme_root=theme
    ) == ["a", "b"]
    after = json.loads(registry.read_text())
    for sku in annotations:
        assert after["products"][sku]["garment"] == before["products"][sku]["garment"]
        stored = after["products"][sku]["presentation"]["garment_highlight"]
        assert validate_annotation(sku, stored, theme_root=theme) == stored
    assert (
        update_garment_highlights(
            annotations, evidence_path=receipt, path=registry, theme_root=theme
        )
        == []
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_sku",
        "float",
        "bool",
        "bounds",
        "zero_area",
        "self_intersection",
        "hole_outside",
        "hole_cross",
        "fake_hash",
        "draft",
        "cross_sku",
        "path_traversal",
    ],
)
def test_invalid_geometry_or_binding_rejected_without_partial_write(setup, mutation):
    theme, registry, receipt, annotations = setup
    original = registry.read_bytes()
    record = annotations["b"]
    if mutation == "wrong_sku":
        record["sku"] = "a"
    elif mutation in {"float", "bool", "bounds"}:
        record["polygons"][0]["outer"][0][0] = {"float": 100.1, "bool": True, "bounds": 1025}[
            mutation
        ]
    elif mutation == "zero_area":
        record["polygons"][0]["outer"] = [[1, 1], [2, 2], [3, 3]]
    elif mutation == "self_intersection":
        record["polygons"][0]["outer"] = [[100, 100], [900, 1200], [900, 100], [100, 1400]]
    elif mutation == "hole_outside":
        record["polygons"][0]["holes"][0] = [[0, 0], [20, 0], [20, 20]]
    elif mutation == "hole_cross":
        record["polygons"][0]["holes"].append([[250, 250], [400, 250], [400, 400], [250, 400]])
    elif mutation == "fake_hash":
        record["review"]["evidence_sha256"] = "0" * 64
    elif mutation == "draft":
        record["status"] = "DRAFT"
    elif mutation == "cross_sku":
        record["source"] = annotations["a"]["source"]
    elif mutation == "path_traversal":
        record["source"]["path"] = "assets/../cards/b.webp"
    with pytest.raises(ValueError):
        update_garment_highlights(
            annotations, evidence_path=receipt, path=registry, theme_root=theme
        )
    assert registry.read_bytes() == original


@pytest.mark.parametrize(
    "mutation",
    [
        "source",
        "blocked",
        "symlink",
        "reviewer",
        "review_source",
        "review_geometry",
        "review_status",
        "duplicate_review",
        "stale_evidence",
    ],
)
def test_changed_source_and_false_independence_fail_closed(setup, mutation):
    theme, registry, receipt, annotations = setup
    original = registry.read_bytes()
    if mutation == "source":
        (theme / annotations["a"]["source"]["path"]).write_bytes(b"changed pixels")
    elif mutation == "blocked":
        path = theme / "data/approved-card-fronts.json"
        manifest = json.loads(path.read_text())
        manifest["products"]["a"]["current_fidelity_status"] = "BLOCKED_PRODUCT_MISMATCH"
        path.write_text(json.dumps(manifest))
    elif mutation == "symlink":
        path = theme / annotations["a"]["source"]["path"]
        other = theme / "assets/cards/replacement.webp"
        path.rename(other)
        path.symlink_to(other)
    else:
        value = json.loads(receipt.read_text())
        row = value["reviews"][0]
        if mutation == "reviewer":
            row["reviewer"] = row["annotator"]
        elif mutation == "review_source":
            row["source"] = annotations["b"]["source"]
        elif mutation == "review_geometry":
            row["geometry_sha256"] = "0" * 64
        elif mutation == "review_status":
            row["status"] = "UNREVIEWED"
        elif mutation == "duplicate_review":
            value["reviews"].append(copy.deepcopy(row))
        elif mutation == "stale_evidence":
            value["additional"] = "changed since approval"
        receipt.write_text(json.dumps(value))
        if mutation != "stale_evidence":
            for annotation in annotations.values():
                annotation["review"]["evidence_sha256"] = hashlib.sha256(
                    receipt.read_bytes()
                ).hexdigest()
    with pytest.raises(ValueError):
        update_garment_highlights(
            annotations, evidence_path=receipt, path=registry, theme_root=theme
        )
    assert registry.read_bytes() == original


def test_write_failure_preserves_registry(setup, monkeypatch):
    theme, registry, receipt, annotations = setup
    original = registry.read_bytes()

    def fail(*args):
        raise OSError("injected atomic replace failure")

    monkeypatch.setattr("skyyrose.core.product_registry.os.replace", fail)
    with pytest.raises(OSError):
        update_garment_highlights(
            annotations, evidence_path=receipt, path=registry, theme_root=theme
        )
    assert registry.read_bytes() == original


def _bind_geometry(receipt, annotation):
    value = json.loads(receipt.read_text())
    row = next(r for r in value["reviews"] if r["sku"] == annotation["sku"])
    digest = geometry_digest(annotation["polygons"])
    annotation["review"]["geometry_sha256"] = digest
    row["geometry_sha256"] = digest
    receipt.write_text(json.dumps(value))
    annotation["review"]["evidence_sha256"] = hashlib.sha256(receipt.read_bytes()).hexdigest()


def _perimeter_256():
    return (
        [[100 + i * 10, 100] for i in range(64)]
        + [[740, 100 + i * 10] for i in range(64)]
        + [[740 - i * 10, 740] for i in range(64)]
        + [[100, 740 - i * 10] for i in range(64)]
    )


def _holes(count):
    return [
        [[200 + 30 * i, 200], [210 + 30 * i, 200], [210 + 30 * i, 210], [200 + 30 * i, 210]]
        for i in range(count)
    ]


@pytest.mark.parametrize(
    "boundary", ["ring_vertices", "polygons", "holes", "rings", "total_vertices", "outer_union"]
)
def test_runtime_contract_positive_boundaries_and_outer_union(setup, boundary):
    theme, _, receipt, annotations = setup
    annotation = annotations["a"]
    outer = annotation["polygons"][0]["outer"]
    if boundary == "ring_vertices":
        polygons = [{"outer": _perimeter_256(), "holes": []}]
    elif boundary == "polygons":
        polygons = [{"outer": copy.deepcopy(outer), "holes": []} for _ in range(16)]
    elif boundary == "holes":
        polygons = [{"outer": outer, "holes": _holes(16)}]
    elif boundary == "rings":
        polygons = [{"outer": copy.deepcopy(outer), "holes": _holes(3)} for _ in range(16)]
    elif boundary == "total_vertices":
        polygons = [{"outer": _perimeter_256(), "holes": []} for _ in range(8)]
    else:
        # Overlapping, edge-touching and nested independent outer regions use
        # union composition, so they must not be rejected as cross-ring errors.
        polygons = [
            {"outer": [[100, 100], [500, 100], [500, 500], [100, 500]], "holes": []},
            {"outer": [[300, 300], [700, 300], [700, 700], [300, 700]], "holes": []},
            {"outer": [[700, 300], [900, 300], [900, 700], [700, 700]], "holes": []},
            {"outer": [[200, 200], [250, 200], [250, 250], [200, 250]], "holes": []},
        ]
    annotation["polygons"] = polygons
    _bind_geometry(receipt, annotation)
    assert (
        validate_annotation("a", annotation, evidence_path=receipt, theme_root=theme)["polygons"]
        == polygons
    )


@pytest.mark.parametrize("limit", ["ring_vertices", "polygons", "holes", "rings", "total_vertices"])
def test_runtime_overlimits_rejected_before_geometry_work(setup, monkeypatch, limit):
    theme, registry, receipt, annotations = setup
    annotation = annotations["a"]
    outer = annotation["polygons"][0]["outer"]
    if limit == "ring_vertices":
        polygons = [{"outer": _perimeter_256() + [[105, 105]], "holes": []}]
    elif limit == "polygons":
        polygons = [{"outer": copy.deepcopy(outer), "holes": []} for _ in range(17)]
    elif limit == "holes":
        polygons = [{"outer": outer, "holes": _holes(17)}]
    elif limit == "rings":
        polygons = [{"outer": copy.deepcopy(outer), "holes": _holes(3)} for _ in range(16)]
        polygons[0]["holes"] = _holes(4)
    else:
        polygons = [{"outer": _perimeter_256(), "holes": []} for _ in range(8)]
        polygons.append({"outer": [[10, 10], [20, 10], [20, 20]], "holes": []})
    annotation["polygons"] = polygons
    _bind_geometry(receipt, annotation)
    before = registry.read_bytes()

    def forbidden(*args):
        pytest.fail("Expensive ring validation ran before budget rejection")

    monkeypatch.setattr("skyyrose.core.card_annotations._ring", forbidden)
    with pytest.raises(ValueError):
        update_garment_highlights(
            {"a": annotation}, evidence_path=receipt, path=registry, theme_root=theme
        )
    assert registry.read_bytes() == before


@pytest.mark.parametrize("filename", ["a space.webp", "aé.webp", "a..webp"])
def test_runtime_incompatible_paths_rejected_even_when_manifest_matches(setup, filename):
    theme, _, receipt, annotations = setup
    annotation = annotations["a"]
    old = theme / annotation["source"]["path"]
    relative = f"assets/cards/{filename}"
    old.rename(theme / relative)
    annotation["source"]["path"] = relative
    manifest_path = theme / "data/approved-card-fronts.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["products"]["a"]["src"] = relative
    manifest_path.write_text(json.dumps(manifest))
    value = json.loads(receipt.read_text())
    value["reviews"][0]["source"]["path"] = relative
    receipt.write_text(json.dumps(value))
    annotation["review"]["evidence_sha256"] = hashlib.sha256(receipt.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="theme-relative"):
        validate_annotation("a", annotation, evidence_path=receipt, theme_root=theme)


def test_current_registry_preserves_canonical_card_source_ownership():
    """The newer canonical card bindings remain visible through get_product."""
    from skyyrose.core.card_annotations import THEME_ROOT
    from skyyrose.core.product import all_skus, get_product
    from skyyrose.core.product_registry import load_registry

    registry = load_registry()
    projected = json.loads((THEME_ROOT / "data/approved-card-fronts.json").read_text())
    assert registry["storefront_card_manifest"]["schema_version"] == projected["schema_version"]
    assert len(registry["products"]) == len(projected["products"]) == 33
    for sku in all_skus():
        assert registry["products"][sku]["images"]["card_front"] == projected["products"][sku]
        assert get_product(sku)["images"]["card_front"] is not None
        assert "images.card_front" not in get_product(sku)["gaps"]
