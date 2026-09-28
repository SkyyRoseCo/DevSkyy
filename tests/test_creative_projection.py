"""Compact contracts preserve owner meaning; tests do not certify visual output."""

import hashlib
import json

import pytest

from skyyrose.core.context_resolver import (
    ResolutionRequest,
    SourceIntegrityError,
    execution_context,
    operative_rules,
)
from skyyrose.core.creative_job import JobPlan, audit_bundle, build_job, execution_bundle
from skyyrose.core.paths import REPO_ROOT, THEME_ROOT
from skyyrose.core.product import get_product
from skyyrose.core.product_truth import project_product


@pytest.fixture
def exact_job():
    data = json.loads((REPO_ROOT / "docs/examples/context-resolver-abstract.json").read_text())
    data.update(
        collection_context="black-rose",
        representation_mode="EXACT_PRODUCT",
        products=[{"sku": "br-001", "required_views": ["front"], "required_details": []}],
    )
    data["absence_reasons"].pop("collection_context")
    data["content_intent"]["representation_mode"] = "EXACT_PRODUCT"
    source = THEME_ROOT / get_product("br-001")["images"]["front"]["path"]
    reference = {
        "path": str(source.relative_to(REPO_ROOT)),
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }
    plan = JobPlan(
        deliverables=["Internal front-source composite"],
        experience_outcome="Clear product recognition",
        authored_meaning="Internal exploration preserving authored identity",
        production_method={
            "technique": "SOURCE_COMPOSITE",
            "rationale": "Contract fixture using the existing front reference",
            "inputs": [reference],
            "feasibility_evidence": [reference],
        },
        success_evidence=["Final output requires separate visual verification"],
        channel_requirements=["Internal review frame"],
        approval_requirements=["No publication authority"],
        novelty_dimensions=[],
        major_initiative=False,
        accessibility_applicable=False,
        accessibility_reason="Noninteractive internal fixture",
        commerce_applicable=False,
        commerce_reason="No transaction",
    )
    return build_job(ResolutionRequest.model_validate(data), plan)


def test_compact_rules_carry_exact_instructions_limits_and_bound_sources(exact_job):
    compact = execution_bundle(exact_job)
    audit = audit_bundle(exact_job)
    raw_rules = {rule["id"]: rule for rule in audit["job"]["context"]["applicable_rules"]}
    projected = {rule["id"]: rule for rule in compact["brand"]["rules"]}
    assert set(projected) == set(compact["brand"]["required_rules"])
    for rule_id, rule in projected.items():
        assert rule["instruction"] == raw_rules[rule_id]["rule"]
        assert rule["scope"] == raw_rules[rule_id]["scope"]
        assert rule["exceptions"] == raw_rules[rule_id].get("exceptions", [])
        assert rule["applicability"]["applies"] is True
        assert rule["applicability"]["reason"]
        source_bytes = (REPO_ROOT / rule["source"]["path"]).read_bytes()
        assert hashlib.sha256(source_bytes).hexdigest() == rule["source"]["sha256"]
        source_rules = {item["id"]: item for item in json.loads(source_bytes)["rules"]}
        assert source_rules[rule_id]["rule"] == rule["instruction"]
    assert projected["A"]["interpretation_limit"] == raw_rules["A"]["interpretation_limit"]
    assert "F1" in projected and projected["F1"]["instruction"]
    assert "P2-001" in projected and projected["P2-001"]["instruction"]
    assert "No invented views" in compact["products"][0]["negative_constraints"][1]
    assert compact["products"] == audit["job"]["context"]["execution_products"]
    assert "raw_product_snapshots" not in compact
    assert compact["release"]["publication_authorized"] is False


def test_cli_and_job_compact_rule_meaning_agree(exact_job):
    assert (
        execution_context(exact_job.context)["rules"]
        == execution_bundle(exact_job)["brand"]["rules"]
    )


@pytest.mark.parametrize("missing", ["rule", "applicability", "source"])
def test_missing_rule_meaning_or_source_cannot_emit_compact_success(exact_job, missing):
    context = exact_job.context.model_copy(deep=True)
    selected = context.execution_rule_ids[0]
    if missing == "rule":
        context.applicable_rules[:] = [r for r in context.applicable_rules if r["id"] != selected]
    elif missing == "applicability":
        context.rule_explanations[:] = [r for r in context.rule_explanations if r["id"] != selected]
    else:
        context.source_manifest[:] = []
    with pytest.raises(SourceIntegrityError):
        operative_rules(context)


@pytest.mark.parametrize("sku", ["br-006", "sg-009"])
def test_founder_keep_decisions_survive_execution_projection(sku):
    product = get_product(sku)
    projected = project_product(product, ["front"], [])["execution"]
    assert product["render_policy"]["keepers"]
    assert projected["render_policy"] == product["render_policy"]
    assert projected["render_policy_source"]["sources"] == product["provenance"]["sources"]
    assert projected["render_policy_source"]["absence_grants_permission"] is False
    projected["render_policy"]["keepers"].clear()
    assert product["render_policy"]["keepers"]


def test_new_policy_restrictions_are_preserved_without_inferred_permission():
    record = {"sku": "synthetic", "render_policy": {"forbidden_operations": ["recolor"]}}
    projected = project_product(record, [], [])["execution"]
    assert projected["render_policy"] == record["render_policy"]
    assert projected["permissions"]["product_mutation"] is False
    assert projected["render_policy_source"]["absence_grants_permission"] is False
