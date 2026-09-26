"""Behavioral checks for the read-only context boundary; no provider execution."""

import json
import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError

from skyyrose.core import context_resolver as resolver


def request(**changes):
    data = dict(
        job_id="fixture",
        brand="skyyrose",
        objective="Explore a collection world",
        collection_context=None,
        campaign_brief=None,
        lifecycle_stage="M2",
        channel=None,
        intended_use="INTERNAL",
        audience="collection customers",
        representation_mode="BRAND_ABSTRACT",
        products=[],
        decisions=[],
        constraints=[],
        absence_reasons={"collection_context": "Master brand", "campaign_brief": "Exploration"},
    )
    data.update(changes)
    data["absence_reasons"] = {
        k: v for k, v in data["absence_reasons"].items() if data.get(k) is None
    }
    data["content_intent"] = {
        "medium": "image",
        "production_type": "editorial_still",
        "content_role": "editorial",
        "shot_role": "EDITORIAL",
        "distribution_channels": [],
        **{
            k: data[k]
            for k in ("intended_use", "audience", "representation_mode", "lifecycle_stage")
        },
    }
    data["production_method"] = (
        "SOURCE_COMPOSITE" if data["representation_mode"] == "EXACT_PRODUCT" else "ABSTRACT"
    )
    return resolver.ResolutionRequest.model_validate(data)


@pytest.fixture
def package(tmp_path):
    path = tmp_path / "constitution"
    shutil.copytree(resolver.PACKAGE, path)
    return path


def test_abstract_and_scoped_palette_do_not_grant_release():
    result = resolver.resolve_context(
        request(
            palette_intents=[
                {"domain": "NATURAL_LOCATION", "purpose": "Truthful blue sky"},
                {"domain": "INTERFACE", "purpose": "Accessible blue focus indicator"},
            ]
        )
    )
    assert result.status == "PLANNING_READY"
    assert "P5-001" in result.palette_policies[0]["rule_ids"]
    assert not result.release_ready and not result.action_authorized
    assert "K1-001" not in result.selected_rule_ids


def test_kids_context_and_fresh_content_identity():
    req = request(collection_context="kids-capsule")
    first = resolver.resolve_context(req)
    second = resolver.resolve_context(req)
    assert "K5-001" in first.selected_rule_ids
    assert first.resolution_id == second.resolution_id


def test_invalid_contract_fails_closed():
    with pytest.raises(ValidationError):
        request(absence_reasons={})
    with pytest.raises(ValidationError):
        request(lifecycle_stage="PREVIEW")
    with pytest.raises(ValidationError):
        request(unknown_override=True)


def test_exact_mode_requires_real_sku():
    assert (
        resolver.resolve_context(request(representation_mode="EXACT_PRODUCT")).status == "BLOCKED"
    )


def test_unknown_sku_blocks():
    result = resolver.resolve_context(
        request(
            representation_mode="EXACT_PRODUCT",
            products=[
                {"sku": "never-a-real-sku", "required_views": ["front"], "required_details": []},
            ],
        )
    )
    assert result.status == "BLOCKED"


def test_real_product_required_view_and_mode_mismatch():
    product = {"sku": "br-001", "required_views": ["front"], "required_details": ["name"]}
    result = resolver.resolve_context(
        request(representation_mode="EXACT_PRODUCT", products=[product])
    )
    assert result.status == "PLANNING_READY"
    assert result.products[0]["sku"] == "br-001"
    assert result.source_manifest
    assert resolver.resolve_context(request(products=[product])).status == "BLOCKED"


def test_missing_required_view_blocks_but_unrequested_does_not():
    result = resolver.resolve_context(
        request(
            representation_mode="EXACT_PRODUCT",
            products=[
                {"sku": "br-001", "required_views": ["back_packshot"], "required_details": []},
            ],
        )
    )
    assert result.status == "BLOCKED"
    assert any(g.blocking and "back_packshot" in g.field for g in result.gaps)


def test_product_recolor_and_collection_mismatch_block():
    result = resolver.resolve_context(
        request(
            representation_mode="EXACT_PRODUCT",
            collection_context="kids-capsule",
            products=[{"sku": "br-001", "required_views": ["front"], "required_details": []}],
            palette_intents=[
                {"domain": "LIGHTING", "purpose": "Blue light", "alters_product": True}
            ],
        )
    )
    assert result.status == "BLOCKED"
    assert {g.source for g in result.conflicts} == {"br-001", "P2-001"}


def test_tampered_constitution_blocks(package):
    f = package / "constitution.json"
    f.write_text(f.read_text() + "\n")
    with pytest.raises(resolver.SourceIntegrityError, match="digest mismatch"):
        resolver.resolve_context(request(), package=package)


def test_tampered_owner_source_blocks(package):
    f = package / "OWNER-RATIFICATION-KPS-20260923.md"
    f.write_text(f.read_text() + "changed")
    with pytest.raises(resolver.SourceIntegrityError):
        resolver.resolve_context(request(), package=package)


def test_no_cached_success_after_manifest_change(package):
    resolver.resolve_context(request(), package=package)
    f = package / "context-manifest.json"
    m = json.loads(f.read_text())
    m["records"].pop()
    f.write_text(json.dumps(m))
    with pytest.raises(resolver.SourceIntegrityError, match="manifest mismatch"):
        resolver.resolve_context(request(), package=package)


def test_reference_escape_rejected():
    with pytest.raises(resolver.SourceIntegrityError, match="escapes"):
        resolver.resolve_context(request(campaign_brief={"path": "../outside", "sha256": "0" * 64}))


def test_required_detail_absent_blocks():
    result = resolver.resolve_context(
        request(
            representation_mode="EXACT_PRODUCT",
            products=[
                {
                    "sku": "br-001",
                    "required_views": ["front"],
                    "required_details": ["garment.invented"],
                },
            ],
        )
    )
    assert result.status == "BLOCKED"
    assert any(g.blocking and g.field.endswith("garment.invented") for g in result.gaps)


def test_governance_never_becomes_creative_permission():
    result = resolver.resolve_context(request())
    assert "F2" not in {r["id"] for r in result.creative_freedoms}
    assert {"F2", "F3", "M-002", "P3-001"} <= {r["id"] for r in result.protected_constraints}
    assert result.typography
    assert result.request_snapshot["constraints"] == []


def test_pending_or_unrelated_approval_cannot_ratify_rule(package):
    import hashlib

    f = package / "constitution.json"
    c = json.loads(f.read_text())
    c["rules"][0]["decision_event"] = "B-001"
    f.write_text(json.dumps(c))
    manifest = package / "context-manifest.json"
    m = json.loads(manifest.read_text())
    m["constitution"]["sha256"] = hashlib.sha256(f.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(m))
    with pytest.raises(resolver.SourceIntegrityError, match="ratification lineage"):
        resolver.resolve_context(request(), package=package)
    c["rules"][0]["decision_event"] = "D-001"
    f.write_text(json.dumps(c))
    m["constitution"]["sha256"] = hashlib.sha256(f.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(m))
    with pytest.raises(resolver.SourceIntegrityError, match="decision wording"):
        resolver.resolve_context(request(), package=package)


def test_product_source_change_during_read_fails_closed(tmp_path, monkeypatch):
    import hashlib

    source = tmp_path / "product.json"
    source.write_text("old")
    monkeypatch.setattr(resolver, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        resolver, "provenance", lambda: {"sources": {"registry": {"path": "product.json"}}}
    )

    def racing_reader(sku):
        source.write_text("new")
        return {
            "sku": sku,
            "images": {},
            "gaps": [],
            "provenance": {
                "sources": {
                    "registry": {
                        "path": "product.json",
                        "sha256": hashlib.sha256(b"new").hexdigest(),
                    }
                }
            },
        }

    monkeypatch.setattr(resolver, "get_product", racing_reader)
    with pytest.raises(resolver.SourceIntegrityError):
        resolver.resolve_context(
            request(
                representation_mode="EXACT_PRODUCT",
                products=[
                    {"sku": "synthetic", "required_views": ["front"], "required_details": []}
                ],
            )
        )


def test_snapshot_binds_code_typography_and_output_rules():
    result = resolver.resolve_context(request())
    paths = {s["path"] for s in result.source_manifest}
    assert str(Path(resolver.__file__).resolve()) in paths
    assert str(resolver.THEME_ROOT / "data/brand/typography.json") in paths
    assert {r["id"] for r in result.applicable_rules} == set(result.selected_rule_ids)


def test_truncated_approval_cannot_reverse_prohibition(package):
    import hashlib

    f = package / "constitution.json"
    c = json.loads(f.read_text())
    c["rules"][0]["rule"] = "replace that origin"
    f.write_text(json.dumps(c))
    mf = package / "context-manifest.json"
    m = json.loads(mf.read_text())
    m["constitution"]["sha256"] = hashlib.sha256(f.read_bytes()).hexdigest()
    mf.write_text(json.dumps(m))
    with pytest.raises(resolver.SourceIntegrityError, match="decision wording"):
        resolver.resolve_context(request(), package=package)
