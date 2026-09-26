"""Owner hardening contract A–F plus intent, projection and lifecycle regressions."""

import json

import pytest
from pydantic import ValidationError

from skyyrose.core.context_resolver import ResolutionRequest, resolve_context
from skyyrose.core.paths import REPO_ROOT
from skyyrose.core.product import get_product
from skyyrose.core.product_truth import project_product


def payload(stage="M2", exact=False):
    data = json.loads((REPO_ROOT / "docs/examples/context-resolver-abstract.json").read_text())
    data["lifecycle_stage"] = stage
    data["content_intent"]["lifecycle_stage"] = stage
    if exact:
        data["collection_context"] = "black-rose"
        data["absence_reasons"].pop("collection_context")
        data["representation_mode"] = "EXACT_PRODUCT"
        data["content_intent"]["representation_mode"] = "EXACT_PRODUCT"
        data["production_method"] = "SOURCE_COMPOSITE"
        data["products"] = [
            {
                "sku": "br-001",
                "required_views": ["front"],
                "required_details": ["front_treatment", "preorder"],
            }
        ]
    return data


def test_A_presence_absence_contradiction():
    data = payload()
    data["collection_context"] = "black-rose"
    with pytest.raises(ValidationError, match="present field"):
        ResolutionRequest.model_validate(data)


def test_B_C_authority_over_stale_copy_real_product(monkeypatch):
    from skyyrose.core import context_resolver

    original = get_product

    # The registry nulls stale copy once it is corrected, so the stale
    # pre-order claim is injected rather than assumed to still be live data.
    def with_stale_copy(sku):
        record = original(sku)
        record["content"]["seo_meta"] = {"value": "Gothic luxury. Pre-order now."}
        return record

    monkeypatch.setattr(context_resolver, "get_product", with_stale_copy)
    context = resolve_context(ResolutionRequest.model_validate(payload(exact=True)))
    assert context.status == "PLANNING_READY"
    truth = context.execution_products[0]
    assert truth["facts"]["front_treatment"]["value"] == "embossed"
    assert truth["facts"]["preorder"]["value"] is False
    assert any(
        c["field"] == "front_treatment" and c["status"] == "SUPERSEDED"
        for c in context.product_conflicts
    )
    assert any(
        c["field"] == "preorder" and c["status"] == "STALE" for c in context.product_conflicts
    )
    # Stale claims stay in raw audit; legitimate back embroidery is not globally rewritten.
    assert "embroider" in json.dumps(context.products).lower()
    assert "embroider" not in json.dumps(truth).lower()
    assert "pre-order" not in json.dumps(truth).lower()
    assert any(c["field"] == "decoration_dimensions" for c in context.product_conflicts)


def test_D_missing_back_blocks(monkeypatch):
    from skyyrose.core import context_resolver

    original = get_product

    def missing(sku):
        record = original(sku)
        record["images"]["back"] = None
        return record

    monkeypatch.setattr(context_resolver, "get_product", missing)
    data = payload(exact=True)
    data["products"][0]["required_views"] = ["back"]
    result = resolve_context(ResolutionRequest.model_validate(data))
    assert result.status == "BLOCKED"
    assert any(g.blocking and g.field.endswith("images.back") for g in result.gaps)


def test_E_M2_internal_without_campaign_brief_is_planning_ready():
    result = resolve_context(ResolutionRequest.model_validate(payload()))
    assert result.status == "PLANNING_READY"
    assert result.request_snapshot["absence_reasons"]["campaign_brief"]
    assert not result.release_ready and not result.action_authorized


@pytest.mark.parametrize("stage", ["M5", "M6"])
def test_F_campaign_authority_missing_blocks(stage):
    data = payload(stage)
    data["campaign_authority_required"] = True
    result = resolve_context(ResolutionRequest.model_validate(data))
    assert result.status == "BLOCKED"
    assert any(g.field == "campaign_brief" and g.blocking for g in result.gaps)


def test_shot_sku_and_back_binding_cannot_bypass_reference_requirements():
    data = payload(exact=True)
    data["content_intent"]["shots"] = [
        {
            "shot_id": "back",
            "shot_role": "BACK",
            "purpose": "Back detail",
            "exact_product": True,
            "product_skus": ["br-001", "unknown"],
        }
    ]
    result = resolve_context(ResolutionRequest.model_validate(data))
    assert result.status == "BLOCKED"
    assert any("unknown" in g.field for g in result.gaps)
    assert any(g.field.endswith(".BACK") for g in result.gaps)


def test_medium_channel_and_duplicate_mode_cannot_conflict():
    data = payload()
    data["channel"] = "film"
    with pytest.raises(ValidationError, match="Legacy channel"):
        ResolutionRequest.model_validate(data)
    data = payload()
    data["content_intent"]["representation_mode"] = "EXACT_PRODUCT"
    with pytest.raises(ValidationError, match="contradicts"):
        ResolutionRequest.model_validate(data)


def test_dimension_number_conflict_and_required_axis_block():
    raw = get_product("br-001")
    raw["catalog"]["branding_spec"] = "10 inches wide"
    raw["dossier"]["branding_block"] = "12 inches wide"
    result = project_product(raw, ["front"], ["decoration_dimensions"])
    assert any(c["status"] == "CONFLICTED" for c in result["conflicts"])
    assert result["execution"]["unresolved_required_gaps"]
    assert all("size_inches" not in p for p in result["execution"]["protected_placements"])


def test_rule_selection_reasons_exclusions_and_intent_gate_profiles():
    data = payload()
    data["major_initiative"] = True
    result = resolve_context(ResolutionRequest.model_validate(data))
    assert len(result.execution_rule_ids) < len(result.applicable_rules)
    assert "N6.discovery" in result.execution_rule_ids
    assert any(not r["included"] and r["reason"] for r in result.rule_explanations)
    assert "composition" in result.verification_requirements["CREATIVE_QA"]
    data["content_intent"]["content_role"] = "product_card"
    card = resolve_context(ResolutionRequest.model_validate(data))
    assert "crop_resilience" in card.verification_requirements["CREATIVE_QA"]
    assert card.verification_requirements != result.verification_requirements


@pytest.mark.parametrize(
    "role", ["editorial_still", "editorial_shoot", "lookbook", "short_film", "awareness"]
)
def test_campaign_role_aliases_cannot_bypass_authority(role):
    data = payload("M5")
    data["content_intent"]["content_role"] = role
    result = resolve_context(ResolutionRequest.model_validate(data))
    assert result.status == "BLOCKED"
    assert any(g.field == "campaign_brief" for g in result.gaps)


def test_preorder_detail_retains_registry_authority():
    result = resolve_context(ResolutionRequest.model_validate(payload(exact=True)))
    field = result.execution_products[0]["required_details"]["preorder"]
    assert field["authority"] == "REGISTRY_DESIRED_STATE_NOT_LIVE_COMMERCE"
    assert field["source"] == "catalog.is_preorder"


def test_compact_cli_defaults_to_execution_and_audit_is_explicit():
    import subprocess
    import sys

    path = str(REPO_ROOT / "docs/examples/context-resolver-abstract.json")
    compact = subprocess.run(
        [sys.executable, "-m", "skyyrose.core.context_resolver", path],
        capture_output=True,
        text=True,
        check=True,
    )
    audit = subprocess.run(
        [sys.executable, "-m", "skyyrose.core.context_resolver", path, "--audit"],
        capture_output=True,
        text=True,
        check=True,
    )
    compact_data = json.loads(compact.stdout)
    audit_data = json.loads(audit.stdout)
    assert compact_data["bundle_type"] == "EXECUTION_CONTEXT"
    assert "applicable_rules" not in compact_data and "applicable_rules" in audit_data
    assert compact_data["status"] == "PLANNING_READY"
    assert len(compact.stdout) < len(audit.stdout)
