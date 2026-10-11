"""Synthetic contract fixtures; no real imagery approval or canonical SOT writes."""

import copy
import hashlib
import json
from unittest.mock import patch

import pytest
from PIL import Image

from skyyrose.core import product_registry as registry


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def setup(tmp_path):
    theme = tmp_path / "wordpress-theme/skyyrose-flagship-2"
    (theme / "assets/v2-original/products").mkdir(parents=True)
    (theme / "data/v2-media-reviews").mkdir(parents=True)
    products = {}
    assets = {}
    from skyyrose.core.native_review import REVIEW_CHECKS

    for index, sku in enumerate(("br-001", "br-004")):
        relative = f"assets/v2-original/products/{sku}.png"
        image = theme / relative
        Image.new("RGB", (1024, 1536), (index * 30, 20, 30)).save(image)
        receipt_path = f"data/v2-media-reviews/{sku}.json"
        evidence = {
            "asset_sha256": digest(image),
            "reviewer": "fixture-reviewer",
            "producer": "fixture-maker",
            "production_id": f"fixture-{sku}",
            "verdict": "PASS",
            "v2_originality_pass": True,
            "product_fidelity_pass": True,
            "roles": ["card_front", "pdp_on_model_front"],
            "skus": [sku],
            "collections": ["black-rose"],
        }
        reference = {"path": image.relative_to(tmp_path).as_posix(), "sha256": digest(image)}
        # Typed contract fixture only; this test never asserts a real visual approval.
        native = {
            "operation_id": evidence["production_id"],
            "job_digest": "1" * 64,
            "sources_digest": "2" * 64,
            "candidate": reference,
            "full_size_pixels": reference,
            "desktop_card": reference,
            "mobile_card": reference,
            "reviewer": evidence["reviewer"],
            "status": "PASS",
            "method": "ACTUAL_PIXEL_INSPECTION",
            "checks": dict.fromkeys(REVIEW_CHECKS, "PASS"),
        }
        native_path = tmp_path / f"native-{sku}.json"
        native_path.write_text(json.dumps(native))
        evidence["native_review"] = {"path": native_path.name, "sha256": digest(native_path)}
        evidence["contexts"] = dict.fromkeys(
            ("card_desktop", "card_mobile", "pdp_desktop", "pdp_mobile"), reference
        )
        (theme / receipt_path).write_text(json.dumps(evidence))
        assets[relative] = {
            "sha256": digest(image),
            "kind": "photograph",
            "status": "INDEPENDENT_VISUAL_PASS",
            "origin": "V2_ORIGINAL_20261002",
            **{
                k: evidence[k]
                for k in ("producer", "production_id", "roles", "skus", "collections")
            },
            "review": {
                "path": receipt_path,
                "sha256": digest(theme / receipt_path),
                "reviewer": "fixture-reviewer",
                "verdict": "PASS",
            },
        }
        products[sku] = {
            "catalog": {
                "sku": sku,
                "name": f"Canonical {sku}",
                "collection": "black-rose",
                "dossier_slug": sku,
            },
            "garment": {
                "features": {"specification": "founder text", "source": "derived_from_dossier"}
            },
            "dossier": {"slug": sku, "content": "founder prose"},
            "images": {
                "image": {"path": "assets/original-source.jpg"},
                "card_front": {"old": "retained"},
            },
        }
    inventory = {
        "schema": "skyyrose.v2.media-eligibility.v1",
        "assets": assets,
        "disallowed_legacy_sha256": [],
    }
    (theme / "data/v2-media-eligibility.json").write_text(json.dumps(inventory))
    target = tmp_path / "registry.json"
    target.write_text(
        json.dumps(
            {"products": products, "catalog_columns": ["sku", "name", "collection", "dossier_slug"]}
        )
    )
    return theme, target, inventory


def apply(setup, assignments=None):
    theme, target, _ = setup
    return registry.update_reviewed_card_fronts(
        assignments
        or {sku: f"assets/v2-original/products/{sku}.png" for sku in ("br-001", "br-004")},
        path=target,
        theme_root=theme,
        evidence_root=target.parent,
    )


def test_batch_adopts_exact_sources_without_founder_approval_or_fact_changes(setup):
    theme, target, _ = setup
    before = registry.load_registry(target)
    assert apply(setup) == ["br-001", "br-004"]
    after = registry.load_registry(target)
    for sku in before["products"]:
        binding = after["products"][sku]["images"]["card_front"]
        assert binding["scene_status"] == "INDEPENDENT_REVIEWED_V2_CARD"
        assert binding["current_fidelity_status"] == "INDEPENDENT_VISUAL_PASS"
        assert binding["source_sha256"] == binding["sha256"] == digest(theme / binding["src"])
        assert binding["alt"] == f"Canonical {sku}"
        restored = copy.deepcopy(after["products"][sku])
        restored["images"]["card_front"] = before["products"][sku]["images"]["card_front"]
        assert restored == before["products"][sku]
    assert apply(setup) == []


@pytest.mark.parametrize(
    "mutation", ["unknown", "mixed", "drift", "failed_review", "collection", "alias", "legacy"]
)
def test_invalid_batch_preserves_authority_and_projections(setup, mutation):
    theme, target, inventory = setup
    assignments = {sku: f"assets/v2-original/products/{sku}.png" for sku in ("br-001", "br-004")}
    if mutation == "unknown":
        assignments["br-999"] = "assets/v2-original/products/br-999.png"
    elif mutation == "mixed":
        assignments["br-004"] = assignments["br-001"]
    elif mutation == "drift":
        (theme / assignments["br-004"]).write_bytes(b"changed")
    elif mutation == "alias":
        assignments["br-004"] = "assets/v2-original/products//br-004.png"
    elif mutation == "legacy":
        inventory["disallowed_legacy_sha256"] = [
            inventory["assets"][assignments["br-004"]]["sha256"]
        ]
    elif mutation == "collection":
        row = inventory["assets"][assignments["br-004"]]
        row["collections"] = ["signature"]
        receipt = theme / row["review"]["path"]
        data = json.loads(receipt.read_text())
        data["collections"] = ["signature"]
        receipt.write_text(json.dumps(data))
        row["review"]["sha256"] = digest(receipt)
    else:
        row = inventory["assets"][assignments["br-004"]]
        receipt = theme / row["review"]["path"]
        data = json.loads(receipt.read_text())
        data["verdict"] = "FAIL"
        receipt.write_text(json.dumps(data))
        row["review"]["sha256"] = digest(receipt)
    (theme / "data/v2-media-eligibility.json").write_text(json.dumps(inventory))
    before = target.read_bytes()
    with pytest.raises((ValueError, KeyError)):
        apply(setup, assignments)
    assert target.read_bytes() == before
    assert not (target.parent / "skyyrose-catalog.csv").exists()


def test_failed_registry_commit_rolls_back_every_projection(setup, monkeypatch):
    _, target, _ = setup
    csv = target.parent / "skyyrose-catalog.csv"
    csv.write_text("original CSV")
    before = target.read_bytes()
    original = registry._atomic_write

    def fail(path, content):
        if path == target:
            raise OSError("synthetic registry commit failure")
        return original(path, content)

    monkeypatch.setattr(registry, "_atomic_write", fail)
    with pytest.raises(OSError, match="synthetic registry"):
        apply(setup)
    assert target.read_bytes() == before
    assert csv.read_text() == "original CSV"
    assert not (target.parent / "dossiers/br-001.md").exists()


def test_current_product_reader_exposes_new_master_without_changing_original_views(
    setup, monkeypatch
):
    from skyyrose.core import product

    theme, target, _ = setup
    apply(setup)
    monkeypatch.setattr(registry, "PRODUCT_REGISTRY", target)
    monkeypatch.setattr(product, "REPO_ROOT", target.parent)
    # The actual get_product reader, including its dossier and registry consumers.
    record = product.get_product("br-001")
    assert record["images"]["card_front"]["path"] == "assets/v2-original/products/br-001.png"
    assert record["images"]["card_front"]["scene_status"] == "INDEPENDENT_REVIEWED_V2_CARD"
    binding = registry.load_registry(target)["products"]["br-001"]["images"]["card_front"]
    assert record["images"]["card_front"]["review"] == binding["review"]
    assert record["images"]["card_front"]["candidate_id"] == binding["candidate_id"]
    record["images"]["card_front"]["review"]["reviewer"] = "changed consumer"
    assert product.get_product("br-001")["images"]["card_front"]["review"] == binding["review"]
    assert registry.load_registry(target)["products"]["br-001"]["images"]["image"] == {
        "path": "assets/original-source.jpg"
    }


def test_independent_png_front_allows_separately_reviewed_geometry_and_rejects_revocation(
    setup, monkeypatch
):
    from skyyrose.core import card_annotations
    from skyyrose.core.card_annotations import geometry_digest, validate_annotation

    theme, target, inventory = setup
    monkeypatch.setattr(card_annotations, "REPO_ROOT", target.parent)
    apply(setup)
    products = registry.load_registry(target)["products"]
    fronts = {sku: product["images"]["card_front"] for sku, product in products.items()}
    (theme / "data/approved-card-fronts.json").write_text(json.dumps({"products": fronts}))
    sku = "br-001"
    front = fronts[sku]
    source = {"path": front["src"], **{key: front[key] for key in ("sha256", "width", "height")}}
    polygons = [{"outer": [[100, 100], [900, 100], [900, 1400], [100, 1400]], "holes": []}]
    geometry_hash = geometry_digest(polygons)
    receipt = target.parent / "region-review.json"
    receipt.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "reviews": [
                    {
                        "sku": sku,
                        "status": "PASS",
                        "source": source,
                        "geometry_sha256": geometry_hash,
                        "annotator": "fixture-segmenter",
                        "reviewer": "fixture-region-reviewer",
                    }
                ],
            }
        )
    )
    annotation = {
        "sku": sku,
        "status": "INDEPENDENT_VISUAL_PASS",
        "source": source,
        "polygons": polygons,
        "review": {
            "geometry_sha256": geometry_hash,
            "evidence_sha256": digest(receipt),
            "evidence_path": str(receipt),
        },
    }
    expected = copy.deepcopy(annotation)
    expected["review"]["evidence_path"] = "region-review.json"
    assert validate_annotation(sku, annotation, evidence_path=receipt, theme_root=theme) == expected
    inventory["assets"][front["src"]]["status"] = "REVISE"
    (theme / "data/v2-media-eligibility.json").write_text(json.dumps(inventory))
    with pytest.raises(ValueError, match="eligibility rejected"):
        validate_annotation(sku, annotation, evidence_path=receipt, theme_root=theme)


def test_actual_native_and_context_dependencies_cannot_be_missing(setup):
    theme, target, inventory = setup
    master = "assets/v2-original/products/br-001.png"
    row = inventory["assets"][master]
    receipt = theme / row["review"]["path"]
    data = json.loads(receipt.read_text())
    data["native_review"] = {"path": "nonexistent-native-review.json", "sha256": "0" * 64}
    receipt.write_text(json.dumps(data))
    row["review"]["sha256"] = digest(receipt)
    (theme / "data/v2-media-eligibility.json").write_text(json.dumps(inventory))
    before = target.read_bytes()
    with pytest.raises(ValueError, match="Review dependency is missing"):
        apply(setup)
    assert target.read_bytes() == before


def test_projection_branch_is_atomic_with_registry_commit_failure(setup, monkeypatch):
    theme, target, _ = setup
    raw = registry.load_registry(target)
    raw["storefront_card_manifest"] = {
        "schema_version": 1,
        "authorization": "synthetic fixture only",
    }
    target.write_text(json.dumps(raw))
    projection = theme / "data/approved-card-fronts.json"
    projection.write_text("original card projection")
    frontend = target.parent / "frontend-catalog.csv"
    frontend.write_text("original frontend")
    before = target.read_bytes()
    original_outputs = registry._compatibility_outputs

    def isolated_canonical_branch(raw, destination):
        with (
            patch.object(registry, "_CANONICAL_REGISTRY", target),
            patch.object(registry, "V2_CARD_FRONT_PROJECTION", projection),
            patch.object(registry, "FRONTEND_CATALOG_REPLICA", frontend),
        ):
            return original_outputs(raw, destination)

    monkeypatch.setattr(registry, "_compatibility_outputs", isolated_canonical_branch)
    original_write = registry._atomic_write

    def fail(destination, content):
        if destination == target:
            raise OSError("synthetic final commit failure")
        return original_write(destination, content)

    monkeypatch.setattr(registry, "_atomic_write", fail)
    with pytest.raises(OSError, match="synthetic final commit"):
        apply(setup)
    assert target.read_bytes() == before
    assert projection.read_text() == "original card projection"
    assert frontend.read_text() == "original frontend"
    monkeypatch.setattr(registry, "_atomic_write", original_write)
    apply(setup)
    assert (
        json.loads(projection.read_text())["products"]["br-001"]
        == registry.load_registry(target)["products"]["br-001"]["images"]["card_front"]
    )


@pytest.mark.parametrize("failure", ["native_status", "context_hash", "nested_missing"])
def test_bound_native_reviews_and_nested_contexts_are_checked(setup, failure):
    theme, target, inventory = setup
    master = "assets/v2-original/products/br-001.png"
    row = inventory["assets"][master]
    receipt = theme / row["review"]["path"]
    binding = {
        "path": (theme / master).relative_to(target.parent).as_posix(),
        "sha256": row["sha256"],
    }
    native = {
        "status": "PASS",
        "reviewer": "fixture-reviewer",
        "operation_id": row["production_id"],
        **dict.fromkeys(("candidate", "full_size_pixels", "desktop_card", "mobile_card"), binding),
    }
    if failure == "native_status":
        native["status"] = "FAIL"
    if failure == "nested_missing":
        native["extra_detail"] = {"path": "missing.png", "sha256": "0" * 64}
    native_path = target.parent / "native-review.json"
    native_path.write_text(json.dumps(native))
    data = json.loads(receipt.read_text())
    data["native_review"] = {"path": "native-review.json", "sha256": digest(native_path)}
    data["contexts"] = {
        "card_desktop": binding if failure != "context_hash" else {**binding, "sha256": "0" * 64}
    }
    receipt.write_text(json.dumps(data))
    row["review"]["sha256"] = digest(receipt)
    (theme / "data/v2-media-eligibility.json").write_text(json.dumps(inventory))
    before = target.read_bytes()
    with pytest.raises(ValueError):
        registry.update_reviewed_card_fronts(
            {"br-001": master}, path=target, theme_root=theme, evidence_root=target.parent
        )
    assert target.read_bytes() == before


@pytest.mark.parametrize(
    "field,value",
    [
        ("scene_status", "FOUNDER_APPROVED_V2_CARD"),
        ("current_fidelity_status", "BLOCKED_PRODUCT_MISMATCH"),
        ("review", None),
        (
            "review",
            {"path": "../review.json", "sha256": "0" * 64, "reviewer": "r", "verdict": "PASS"},
        ),
    ],
)
def test_schema_rejects_mixed_statuses_or_incomplete_new_review(setup, field, value):
    from jsonschema import Draft202012Validator

    _, target, _ = setup
    apply(setup)
    binding = registry.load_registry(target)["products"]["br-001"]["images"]["card_front"]
    binding[field] = value
    schema = json.loads(
        registry._CANONICAL_REGISTRY.with_name("logo-registry.schema.json").read_text()
    )
    assert list(Draft202012Validator(schema["$defs"]["cardFrontBinding"]).iter_errors(binding))


def test_invalid_native_dimensions_rejected_even_when_all_role_hashes_match(setup):
    theme, target, inventory = setup
    relative = "assets/v2-original/products/br-001.png"
    Image.new("RGB", (1023, 1536)).save(theme / relative)
    row = inventory["assets"][relative]
    row["sha256"] = digest(theme / relative)
    receipt = theme / row["review"]["path"]
    data = json.loads(receipt.read_text())
    data["asset_sha256"] = row["sha256"]
    receipt.write_text(json.dumps(data))
    row["review"]["sha256"] = digest(receipt)
    (theme / "data/v2-media-eligibility.json").write_text(json.dumps(inventory))
    with pytest.raises(ValueError, match="full-resolution native pixels"):
        apply(setup)


@pytest.mark.parametrize(
    "failure",
    [
        "simulated",
        "revise_check",
        "missing_check",
        "no_native",
        "no_contexts",
        "missing_context",
        "producer_alias",
    ],
)
def test_native_actual_review_is_mandatory_and_all_checks_must_pass(setup, failure):
    theme, target, inventory = setup
    row = inventory["assets"]["assets/v2-original/products/br-001.png"]
    receipt = theme / row["review"]["path"]
    evidence = json.loads(receipt.read_text())
    native_path = target.parent / evidence["native_review"]["path"]
    native = json.loads(native_path.read_text())
    if failure == "simulated":
        native["method"] = "SIMULATED_FIXTURE"
    elif failure == "revise_check":
        native["checks"]["product_fidelity"] = "REVISE"
    elif failure == "missing_check":
        native["checks"].pop("product_fidelity")
    elif failure == "no_native":
        evidence.pop("native_review")
    elif failure == "no_contexts":
        evidence.pop("contexts")
    elif failure == "missing_context":
        evidence["contexts"].pop("pdp_mobile")
    else:
        row["producer"] = " FIXTURE-REVIEWER "
        evidence["producer"] = row["producer"]
    native_path.write_text(json.dumps(native))
    if "native_review" in evidence:
        evidence["native_review"]["sha256"] = digest(native_path)
    receipt.write_text(json.dumps(evidence))
    row["review"]["sha256"] = digest(receipt)
    (theme / "data/v2-media-eligibility.json").write_text(json.dumps(inventory))
    before = target.read_bytes()
    with pytest.raises(ValueError):
        apply(setup)
    assert target.read_bytes() == before


@pytest.mark.parametrize("dependency", ["inventory", "master", "native", "context"])
@pytest.mark.parametrize("timing", ["prepare_outputs", "mid_projection", "final_commit"])
def test_dependency_drift_at_every_commit_boundary_rolls_back(
    setup, monkeypatch, dependency, timing
):
    theme, target, inventory = setup
    before = target.read_bytes()
    csv = target.parent / "skyyrose-catalog.csv"
    csv.write_text("original CSV")
    relative = "assets/v2-original/products/br-001.png"
    row = inventory["assets"][relative]
    evidence = json.loads((theme / row["review"]["path"]).read_text())
    context = target.parent / "fixture-context.bin"
    context.write_bytes(b"contract context")
    evidence["contexts"]["pdp_mobile"] = {"path": context.name, "sha256": digest(context)}
    receipt = theme / row["review"]["path"]
    receipt.write_text(json.dumps(evidence))
    row["review"]["sha256"] = digest(receipt)
    inventory_path = theme / "data/v2-media-eligibility.json"
    inventory_path.write_text(json.dumps(inventory))
    mutated = False

    def mutate():
        nonlocal mutated
        if mutated:
            return
        mutated = True
        if dependency == "inventory":
            inventory["assets"][relative]["status"] = "REVISE"
            inventory_path.write_text(json.dumps(inventory))
        elif dependency == "master":
            (theme / relative).write_bytes(b"changed master")
        elif dependency == "native":
            (target.parent / evidence["native_review"]["path"]).write_text("changed native")
        else:
            context.write_bytes(b"changed context")

    outputs = registry._compatibility_outputs
    write = registry._atomic_write

    def build(raw, destination):
        result = outputs(raw, destination)
        if timing == "prepare_outputs":
            mutate()
        return result

    def atomic(destination, content):
        write(destination, content)
        if timing == "mid_projection" and destination == csv:
            mutate()
        if timing == "final_commit" and destination == target:
            mutate()

    monkeypatch.setattr(registry, "_compatibility_outputs", build)
    monkeypatch.setattr(registry, "_atomic_write", atomic)
    with pytest.raises(ValueError, match="dependency drift"):
        apply(setup)
    assert target.read_bytes() == before
    assert csv.read_text() == "original CSV"
    assert not (target.parent / "dossiers/br-001.md").exists()


@pytest.mark.parametrize(
    "relative",
    [
        "tools/v2-source-certification/package.py",
        "skyyrose/core/native_review.py",
        "wordpress-theme/skyyrose-flagship/data/logo-registry.schema.json",
    ],
)
def test_code_and_schema_snapshot_drift_fails_without_editing_real_files(
    setup, monkeypatch, relative
):
    theme, target, _ = setup
    snapshots = None
    original_snapshot = registry._snapshot_dependency
    original_outputs = registry._compatibility_outputs

    def remember(dependencies, path, expected=None):
        nonlocal snapshots
        snapshots = dependencies
        return original_snapshot(dependencies, path, expected)

    def output(raw, destination):
        result = original_outputs(raw, destination)
        # Corrupt the captured expected identity only; production source files stay untouched.
        matching = [p for p in snapshots if str(p).endswith(relative)]
        assert len(matching) == 1
        path = matching[0]
        snapshots[path] = ("0" * 64, path.resolve())
        return result

    monkeypatch.setattr(registry, "_snapshot_dependency", remember)
    monkeypatch.setattr(registry, "_compatibility_outputs", output)
    before = target.read_bytes()
    with pytest.raises(ValueError, match="dependency drift"):
        apply(setup)
    assert target.read_bytes() == before


def test_caller_mapping_mutation_cannot_change_frozen_batch(setup, monkeypatch):
    _, target, _ = setup
    assignments = {"br-001": "assets/v2-original/products/br-001.png"}
    original = registry._compatibility_outputs

    def output(raw, destination):
        assignments["br-001"] = "assets/v2-original/products/br-004.png"
        return original(raw, destination)

    monkeypatch.setattr(registry, "_compatibility_outputs", output)
    apply(setup, assignments)
    assert (
        registry.load_registry(target)["products"]["br-001"]["images"]["card_front"]["src"]
        == "assets/v2-original/products/br-001.png"
    )


@pytest.mark.parametrize("extra", ["tablet", "unknown"])
def test_only_supported_optional_tablet_contexts_are_permitted(setup, extra):
    theme, target, inventory = setup
    row = inventory["assets"]["assets/v2-original/products/br-001.png"]
    receipt = theme / row["review"]["path"]
    evidence = json.loads(receipt.read_text())
    if extra == "tablet":
        evidence["contexts"]["card_tablet"] = evidence["contexts"]["card_desktop"]
        evidence["contexts"]["pdp_tablet"] = evidence["contexts"]["pdp_desktop"]
    else:
        evidence["contexts"]["unreviewed_surface"] = evidence["contexts"]["card_desktop"]
    receipt.write_text(json.dumps(evidence))
    row["review"]["sha256"] = digest(receipt)
    (theme / "data/v2-media-eligibility.json").write_text(json.dumps(inventory))
    if extra == "tablet":
        assert apply(setup) == ["br-001", "br-004"]
    else:
        before = target.read_bytes()
        with pytest.raises(ValueError, match="contexts are required"):
            apply(setup)
        assert target.read_bytes() == before


@pytest.mark.parametrize("failure", ["other_master_pixels", "unsafe_context", "role_drift"])
def test_exact_master_and_safe_role_context_bindings_are_required(setup, failure):
    theme, target, inventory = setup
    row = inventory["assets"]["assets/v2-original/products/br-001.png"]
    receipt = theme / row["review"]["path"]
    evidence = json.loads(receipt.read_text())
    native_path = target.parent / evidence["native_review"]["path"]
    native = json.loads(native_path.read_text())
    if failure == "other_master_pixels":
        duplicate = target.parent / "same-pixels.png"
        Image.new("RGB", (1024, 1536), (180, 180, 180)).save(duplicate)
        reference = {"path": duplicate.name, "sha256": digest(duplicate)}
        native["candidate"] = reference
        native["full_size_pixels"] = reference
    elif failure == "unsafe_context":
        evidence["contexts"]["pdp_mobile"]["path"] = "../outside.png"
    else:
        evidence["contexts"]["card_mobile"] = {"path": "missing.png", "sha256": "0" * 64}
    native_path.write_text(json.dumps(native))
    evidence["native_review"]["sha256"] = digest(native_path)
    receipt.write_text(json.dumps(evidence))
    row["review"]["sha256"] = digest(receipt)
    (theme / "data/v2-media-eligibility.json").write_text(json.dumps(inventory))
    before = target.read_bytes()
    with pytest.raises(ValueError):
        apply(setup)
    assert target.read_bytes() == before


def test_dimensions_are_decoded_from_validated_bytes_even_if_path_read_is_swapped(
    setup, monkeypatch
):
    """Reproduce an ABA path read without changing the approved final bytes."""
    import io

    _, target, _ = setup
    original_open = Image.open
    swapped = io.BytesIO()
    Image.new("RGB", (1536, 1024), (1, 2, 3)).save(swapped, format="PNG")
    swapped_bytes = swapped.getvalue()

    def path_swap_open(value, *args, **kwargs):
        # A pathname read can observe different pixels between hash checks;
        # decoding the already-validated snapshot retains its actual dimensions.
        if not isinstance(value, io.BytesIO):
            return original_open(io.BytesIO(swapped_bytes), *args, **kwargs)
        return original_open(value, *args, **kwargs)

    monkeypatch.setattr(Image, "open", path_swap_open)
    apply(setup)
    front = registry.load_registry(target)["products"]["br-001"]["images"]["card_front"]
    assert (front["width"], front["height"]) == (1024, 1536)
