"""Tests for the LogoRegistry path resolver."""

from __future__ import annotations

import pytest

from skyyrose.elite_studio.logo_registry import (
    LogoNotFoundError,
    LogoRegistry,
    SkuFolderUnknownError,
)


@pytest.fixture(scope="module")
def registry() -> LogoRegistry:
    return LogoRegistry.load()


# ─── Schema basics ────────────────────────────────────────────────────


def test_version_is_current(registry: LogoRegistry) -> None:
    assert registry.version >= 4


def test_brand_primary_is_sr_monogram(registry: LogoRegistry) -> None:
    assert registry.brand_primary == "sr-monogram-rose-gold"


# ─── Centralized logo path resolution ─────────────────────────────────


def test_brand_primary_resolves_to_logos_dir(registry: LogoRegistry) -> None:
    path = registry.image_path(sku="br-005", logo_id="sr-monogram-rose-gold")
    assert path.parent.name == "logos"
    assert path.name == "sr-monogram-rose-gold.jpeg"
    assert path.exists(), f"missing brand-primary asset: {path}"


def test_black_roses_stays_centralized(registry: LogoRegistry) -> None:
    """High-fanout collection logo stays in logos/, not co-located."""
    entry = registry.get_logo("black-roses-cloud-cluster")
    assert entry.co_located_per_sku is False
    assert entry.collection == "black_rose"


def test_red_rose_is_dual_collection(registry: LogoRegistry) -> None:
    """red-roses-cloud-cluster is DUAL-collection (founder re-confirmed 2026-05-27):
    used on BOTH Signature (sg-009) AND Love Hurts (lh-003, lh-004 inside-hood).
    The 2026-05-25 'Signature only' reclassification was reverted in the registry.
    """
    entry = registry.get_logo("red-roses-cloud-cluster")
    assert entry.collection == "shared_signature_love_hurts"


def test_heart_rose_is_love_hurts(registry: LogoRegistry) -> None:
    entry = registry.get_logo("heart-rose-composite")
    assert entry.collection == "love_hurts"


# ─── Per-SKU sport patch resolution ───────────────────────────────────


@pytest.mark.parametrize(
    "sku,logo_id,expected_folder",
    [
        ("br-008", "nfl-authentic-collection-card", "black-is-beautiful-football-jersey-red"),
        ("br-009", "nfl-authentic-collection-card", "black-is-beautiful-football-jersey-white"),
        ("br-010", "nba-authentic-collection-card", "black-is-beautiful-basketball-jersey"),
        ("br-011", "hockey-championship-card", "black-is-beautiful-hockey-jersey"),
        ("br-003", "mlb-authentic-collection-card", "black-is-beautiful-jersey"),
        ("br-012", "mlb-authentic-collection-card", "jersey-last-oakland-baseball"),
        ("br-014", "mlb-authentic-collection-card", "black-is-beautiful-jersey-giants"),
        ("br-015", "mlb-authentic-collection-card", "black-is-beautiful-jersey-white"),
    ],
)
def test_sport_patch_resolves_to_per_sku_folder(
    registry: LogoRegistry, sku: str, logo_id: str, expected_folder: str
) -> None:
    path = registry.image_path(sku=sku, logo_id=logo_id)
    assert path.parent.name == expected_folder
    assert path.name.endswith(".jpeg")
    assert path.exists(), f"missing per-SKU patch asset: {path}"


def test_sport_patch_without_sku_folder_raises(registry: LogoRegistry) -> None:
    with pytest.raises(SkuFolderUnknownError):
        registry.image_path(sku="zz-999", logo_id="nfl-authentic-collection-card")


def test_unknown_logo_raises(registry: LogoRegistry) -> None:
    with pytest.raises(LogoNotFoundError):
        registry.image_path(sku="br-005", logo_id="nonexistent-logo")


# ─── Placement lookups ────────────────────────────────────────────────


def test_new_baseball_skus_have_mlb_patch(registry: LogoRegistry) -> None:
    """br-014/015 added in registry v4 — must carry mlb patch (br-013 retired)."""
    for sku in ("br-014", "br-015"):
        assert registry.has_sku(sku), f"{sku} missing from sku_logos"
        placements = registry.placements_for(sku)
        logo_ids = {p["logo_id"] for p in placements}
        assert "mlb-authentic-collection-card" in logo_ids
        assert "black-roses-cloud-cluster" in logo_ids


def test_br013_retired(registry: LogoRegistry) -> None:
    """br-013 was confirmed duplicate of br-003 and retired 2026-05-25."""
    assert not registry.has_sku("br-013")
    assert registry.sku_folder("br-013") is None


def test_four_mlb_jerseys_exactly(registry: LogoRegistry) -> None:
    """The MLB authentic collection patch is now placed on exactly 4 SKUs."""
    mlb_users = [
        sku
        for sku in registry._sku_logos  # noqa: SLF001 — test-only introspection
        if any(
            p["logo_id"] == "mlb-authentic-collection-card" for p in registry.placements_for(sku)
        )
    ]
    assert sorted(mlb_users) == ["br-003", "br-012", "br-014", "br-015"]


def test_lh003_uses_red_rose_not_heart_rose(registry: LogoRegistry) -> None:
    """Founder re-confirmed 2026-05-27: lh-003 uses red-roses-cloud-cluster
    (all_over + mesh_panels), NOT heart-rose-composite. The 2026-05-25 switch to
    heart-rose was itself wrong and was reverted in the registry."""
    placements = registry.placements_for("lh-003")
    logo_ids = [p["logo_id"] for p in placements]
    assert "heart-rose-composite" not in logo_ids
    assert logo_ids.count("red-roses-cloud-cluster") >= 2  # all_over + mesh_panels


def test_lh004_uses_both_red_rose_and_heart_rose(registry: LogoRegistry) -> None:
    """Founder re-confirmed 2026-05-27: lh-004 carries BOTH —
    red-roses-cloud-cluster (inside_hood) AND heart-rose-composite (back_center)."""
    placements = registry.placements_for("lh-004")
    logo_ids = [p["logo_id"] for p in placements]
    assert "red-roses-cloud-cluster" in logo_ids  # inside_hood
    assert "heart-rose-composite" in logo_ids  # back_center


def test_sg009_uses_red_rose(registry: LogoRegistry) -> None:
    """Signature Sherpa is the canonical home of red-roses-cloud-cluster."""
    placements = registry.placements_for("sg-009")
    logo_ids = [p["logo_id"] for p in placements]
    assert "red-roses-cloud-cluster" in logo_ids


# ─── Sport patch enumeration ──────────────────────────────────────────


def test_four_sport_patches_registered(registry: LogoRegistry) -> None:
    patches = registry.sport_patches()
    assert set(patches.keys()) == {
        "nfl-authentic-collection-card",
        "nba-authentic-collection-card",
        "mlb-authentic-collection-card",
        "hockey-championship-card",
    }
    for entry in patches.values():
        assert entry.co_located_per_sku is True
        assert entry.category == "sport_patch"


def test_jersey_contract_carries_founder_patch_and_relative_lettering(registry):
    import json

    from scripts.oai_render.prompt import build_prompt
    from scripts.scaffold_sku_asset_folders import _build_placement_md

    raw = json.loads(registry._source.read_text())
    prompt = build_prompt(
        name="Last Oakland Baseball",
        sku="br-012",
        collection="black-rose",
        reference_labels=[],
        dossier_text="Old patch sizing: 2in x 2.5in",
        is_patch=True,
        style="ghost",
    )
    brief = _build_placement_md("br-012", {"name": "Last Oakland"}, raw)
    for output in (prompt, brief):
        assert '"width": 3' in output
        assert '"height": 4' in output
        assert '"ratio": 0.72' in output
        assert "FOUNDER_CONFIRMED" in output
        assert "sole authority" in output
    assert prompt.index("Old patch sizing") < prompt.index("CANONICAL LOGO")


def test_contract_reloads_founder_changes_without_prompt_copy(monkeypatch, tmp_path, registry):
    import json

    from scripts.oai_render.prompt import build_prompt
    from skyyrose.elite_studio import logo_registry

    raw = json.loads(registry._source.read_text())
    patch = next(
        i for i in raw["sku_logos"]["br-012"]["decoration_sizing"]["items"] if i["kind"] == "patch"
    )
    patch["dimension_inches"]["width"] = 3.125  # isolated test amendment, not a product edit
    target = tmp_path / "registry.json"
    target.write_text(json.dumps(raw))
    monkeypatch.setattr(logo_registry, "REGISTRY_JSON", target)
    output = build_prompt(
        name="Jersey",
        sku="br-012",
        collection="black-rose",
        reference_labels=[],
        dossier_text=None,
        is_patch=True,
        style="ghost",
    )
    assert '"width": 3.125' in output
    returned = LogoRegistry.load().decoration_sizing_for("br-012")
    returned["items"].clear()
    assert LogoRegistry.load().decoration_sizing_for("br-012")["items"]


def test_missing_jersey_sizing_or_unknown_sku_fails_closed(registry):
    import json

    from skyyrose.elite_studio.logo_registry import RegistryContractError

    raw = json.loads(registry._source.read_text())
    del raw["sku_logos"]["br-012"]["decoration_sizing"]
    with pytest.raises(RegistryContractError, match="requires registered decoration sizing"):
        LogoRegistry(raw).prompt_instructions("br-012")
    with pytest.raises(RegistryContractError, match="absent"):
        LogoRegistry(raw).prompt_instructions("missing-sku")


def test_render_reference_uses_registry_patch_and_blank_exterior(registry):
    assert registry.primary_reference_for("br-012") == registry.image_path(
        sku="br-012", logo_id="mlb-authentic-collection-card"
    )
    assert registry.primary_reference_for("sg-011") is None
    assert registry.primary_reference_for("sg-012") is None


def test_unbound_bridge_reference_does_not_fall_back_to_generic_cluster(registry):
    from skyyrose.elite_studio.logo_registry import RegistryContractError

    from copy import deepcopy

    raw = deepcopy(registry._raw)
    raw["sku_logos"]["sg-002"]["render_reference"] = {
        "status": "UNBOUND",
        "reason": "SKU-specific photographic artwork is unbound",
    }
    with pytest.raises(RegistryContractError, match="SKU-specific photographic artwork"):
        LogoRegistry(raw).primary_reference_for("sg-002")


def test_actual_render_plan_observes_registry_material_change(monkeypatch, tmp_path):
    import json

    from scripts.oai_render import pipeline, references
    from skyyrose.core import product_registry

    raw = product_registry.load_registry()
    raw["products"]["sg-006"]["garment"]["materials"]["specification"] = (
        "Isolated test material: founder-specified brushed cotton."
    )
    target = tmp_path / "registry.json"
    target.write_text(json.dumps(raw))
    monkeypatch.setattr(product_registry, "PRODUCT_REGISTRY", target)
    monkeypatch.setattr(references, "build_references", lambda *args, **kwargs: [])
    monkeypatch.setattr(pipeline, "build_scene", lambda **kwargs: None)
    plan = pipeline.plan_sku("sg-006", references.load_catalog(), references.build_dossier_index())
    assert not plan.error
    assert "Isolated test material: founder-specified brushed cotton." in plan.prompt
    assert "Isolated test material: founder-specified brushed cotton." in plan.dossier_spec


def test_source_map_reads_registry_changes_without_cache(monkeypatch, tmp_path):
    import json

    from scripts.oai_render import references
    from skyyrose.core import product_registry

    raw = product_registry.load_registry()
    target = tmp_path / "registry.json"
    target.write_text(json.dumps(raw))
    monkeypatch.setattr(product_registry, "PRODUCT_REGISTRY", target)
    before = references.get_source_map()["sg-006"]["front"]
    raw["products"]["sg-006"]["render_sources"]["front"] = "test-fixture/amended-front.png"
    target.write_text(json.dumps(raw))
    assert references.get_source_map()["sg-006"]["front"] != before
    assert (
        references.get_source_map()["sg-006"]["front"]
        .as_posix()
        .endswith("test-fixture/amended-front.png")
    )


@pytest.mark.parametrize(
    "sku", ["br-003", "br-008", "br-009", "br-010", "br-011", "br-012", "br-014", "br-015"]
)
def test_real_jersey_plan_uses_registered_card_as_patch(sku):
    from scripts.oai_render import pipeline, references

    plan = pipeline.plan_sku(sku, references.load_catalog(), references.build_dossier_index())
    assert plan.error is None
    assert plan.is_patch
    patch_refs = [ref for ref in plan.references if ref.kind == "patch"]
    assert len(patch_refs) == 1
    assert patch_refs[0].path == LogoRegistry.load().primary_reference_for(sku)
    assert '"width": 3' in plan.prompt and '"height": 4' in plan.prompt


@pytest.mark.parametrize("parent", ["kids-001", "kids-002"])
def test_real_kids_pair_plan_resolves_registered_joggers_component(parent):
    from scripts.oai_render import pipeline, references

    pair = next(pair for pair in references.PAIRS if pair.skus[0] == parent)
    plan = pipeline.plan_pair(pair, references.load_catalog(), references.build_dossier_index())
    assert plan.error is None
    assert "COMPONENT SCOPE: render only the joggers" in plan.prompt
    registry = LogoRegistry.load()
    placements = registry.placements_for(parent + "-joggers")
    assert [placement["position"] for placement in placements] == ["left_thigh"]
    assert placements[0] in registry.placements_for(parent)


def test_unregistered_filename_cannot_replace_registry_source(monkeypatch, tmp_path):
    from scripts.oai_render import references

    registered = references.find_flatlay_photo("sg-011")
    rogue = tmp_path / "sg-011-unregistered-real-front.jpg"
    rogue.write_bytes(b"illustrative test fixture; not an approved image")
    monkeypatch.setattr(references.config, "PRODUCT_REFERENCES_DIR", tmp_path)
    refs = references.build_references("sg-011", "signature")
    assert references.find_flatlay_photo("sg-011") == registered
    assert all(ref.path != rogue for ref in refs)
    assert refs[0].path == registered


def test_supplemental_logo_binding_cannot_replace_required_sport_patch(registry):
    from copy import deepcopy

    raw = deepcopy(registry._raw)
    raw["sku_logos"]["br-012"]["render_reference"] = {
        "path": "illustrative-fixture/wrong-nonsport-logo.png"
    }
    amended = LogoRegistry(raw)
    assert amended.primary_reference_for("br-012") == amended.image_path(
        sku="br-012", logo_id="mlb-authentic-collection-card"
    )


@pytest.fixture
def garment_artwork_registry(tmp_path, monkeypatch, registry):
    from copy import deepcopy
    from hashlib import sha256

    from skyyrose.elite_studio import logo_registry

    raw = deepcopy(registry._raw)
    source = tmp_path / "sg-002-front.png"
    source.write_bytes(b"isolated physical-source binding fixture")
    raw["products"]["sg-002"]["render_sources"]["front"] = source.name
    raw["sku_logos"]["sg-002"]["render_reference"] = {
        "status": "BOUND",
        "kind": "garment_artwork",
        "path": source.name,
        "sha256": sha256(source.read_bytes()).hexdigest(),
        "view": "front",
    }
    monkeypatch.setattr(logo_registry, "PROJECT_ROOT", tmp_path)
    return raw, source


def test_bound_garment_artwork_hash_and_product_path(garment_artwork_registry):
    raw, source = garment_artwork_registry
    registry = LogoRegistry(raw)
    assert registry.primary_reference_for("sg-002") == source
    assert registry.reference_kind_for("sg-002") == "garment"


@pytest.mark.parametrize("failure", ["missing", "tampered", "missing_hash", "wrong_sku", "escape"])
def test_bound_garment_artwork_fails_closed(garment_artwork_registry, failure):
    from skyyrose.elite_studio.logo_registry import RegistryContractError

    raw, source = garment_artwork_registry
    binding = raw["sku_logos"]["sg-002"]["render_reference"]
    if failure == "missing":
        source.unlink()
        expected = "file is missing"
    elif failure == "tampered":
        source.write_bytes(b"different product pixels")
        expected = "hash mismatch"
    elif failure == "missing_hash":
        binding.pop("sha256")
        expected = "registered SHA-256"
    elif failure == "wrong_sku":
        raw["products"]["sg-002"]["render_sources"]["front"] = "sg-005-front.png"
        expected = "does not match this product"
    else:
        binding["path"] = "../outside.png"
        expected = "within the repository"
    with pytest.raises(RegistryContractError, match=expected):
        LogoRegistry(raw).primary_reference_for("sg-002")


@pytest.mark.parametrize("sku", ["sg-001", "sg-002", "sg-003", "sg-005"])
def test_bridge_real_front_plan_uses_one_bound_garment_source(sku):
    from scripts.oai_render import pipeline, references

    registry = LogoRegistry.load()
    expected = registry.primary_reference_for(sku)
    plan = pipeline.plan_sku(sku, references.load_catalog(), references.build_dossier_index())
    assert plan.error is None
    assert len(plan.references) == 1
    assert plan.references[0].path.resolve() == expected.resolve()
    assert plan.references[0].kind == "garment"
    assert "REGISTERED GARMENT SOURCE (FRONT VIEW)" in plan.references[0].label
    assert "LOGO/BRANDING CLOSE-UP" not in plan.prompt
    assert "GARMENT TECH FLAT (FRONT VIEW)" not in plan.prompt
    assert '"kind": "garment_artwork"' in plan.prompt


@pytest.mark.parametrize("sku", ["sg-001", "sg-002", "sg-003", "sg-005"])
def test_bridge_front_binding_cannot_supply_a_back_render(sku):
    from scripts.oai_render import pipeline, references

    plan = pipeline.plan_sku(
        sku, references.load_catalog(), references.build_dossier_index(), view="back"
    )
    assert plan.error and "front only; no registered back source" in plan.error
    assert not plan.prompt
