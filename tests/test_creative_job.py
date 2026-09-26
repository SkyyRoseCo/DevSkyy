"""Synthetic evidence checks; no claim of real creative approval."""

import hashlib

import pytest
from pydantic import ValidationError

from skyyrose.core.context_resolver import ResolutionRequest, SourceReference
from skyyrose.core.creative_job import (
    GATES,
    JobPlan,
    VerificationRecord,
    assess_artifact,
    build_job,
    render_brief,
)
from skyyrose.core.paths import REPO_ROOT
from skyyrose.elite_studio.prompts.enhancer import PromptEnhancer


def request():
    return ResolutionRequest.model_validate_json(
        (REPO_ROOT / "docs/examples/context-resolver-abstract.json").read_text()
    )


def plan(**changes):
    data = dict(
        deliverables=["Editorial concept frame"],
        experience_outcome="Place and belonging",
        authored_meaning="Truthful Oakland origin",
        production_method={
            "technique": "ABSTRACT",
            "rationale": "No real SKU depicted",
            "inputs": [],
            "feasibility_evidence": [],
        },
        success_evidence=["Authored rationale and reviewed frame"],
        channel_requirements=["Static editorial frame"],
        approval_requirements=["Owner release"],
        novelty_dimensions=["Daylight local setting"],
        major_initiative=True,
        accessibility_applicable=False,
        accessibility_reason="Internal noninteractive prototype",
        commerce_applicable=False,
        commerce_reason="No offer or shopping action",
    )
    data.update(changes)
    return JobPlan.model_validate(data)


def ref(path):
    return SourceReference(path=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


@pytest.fixture
def evidence(tmp_path):
    artifact = tmp_path / "frame.txt"
    artifact.write_text("SYNTHETIC artifact")
    review = tmp_path / "review.txt"
    review.write_text("SYNTHETIC review, not a real approval")
    return ref(artifact), ref(review)


def records(job, artifact, evidence):
    result = []
    for gate in GATES:
        applicable = gate not in ("PRODUCT_FIDELITY", "ACCESSIBILITY", "COMMERCE_INTEGRITY")
        result.append(
            VerificationRecord(
                gate=gate,
                contract_id=job.contract_id,
                artifact=artifact,
                applicable=applicable,
                applicability_reason="Synthetic test applicability",
                result="PASS" if applicable else None,
                reviewer="test reviewer",
                method="fixture",
                recorded_at="2026-09-24T00:00:00Z",
                observations="Synthetic test only",
                evidence=[evidence],
            )
        )
    return result


def assess(job, artifact, rs, evidence, root):
    return assess_artifact(
        job,
        artifact,
        rs,
        novelty_evidence=[evidence],
        experiment_evidence=[],
        experiment_applicability_reason="Fixture test, not market experiment",
        root=root,
    )


def test_contract_binds_plan_and_context():
    first = build_job(request(), plan())
    second = build_job(request(), plan())
    assert first.contract_id == second.contract_id
    assert first.production_path_ready and not first.action_authorized
    assert (
        first.contract_id
        != build_job(request(), plan(deliverables=["Different deliverable"])).contract_id
    )
    assert first.context.resolution_id in render_brief(first)


def test_blocked_context_cannot_be_planning_ready():
    req = request().model_copy(
        update={
            "representation_mode": "EXACT_PRODUCT",
            "content_intent": request().content_intent.model_copy(
                update={"representation_mode": "EXACT_PRODUCT"}
            ),
        }
    )
    job = build_job(req, plan())
    assert not job.production_path_ready and job.blockers


def test_unresolved_production_and_missing_novelty_block():
    job = build_job(
        request(),
        plan(
            production_method={
                "technique": "UNRESOLVED",
                "rationale": "TBD",
                "inputs": [],
                "feasibility_evidence": [],
            },
            novelty_dimensions=[],
        ),
    )
    assert "No credible fidelity-preserving production method" in job.blockers
    assert "Major initiative requires meaningful novelty dimensions" in job.blockers


def test_complete_synthetic_records_never_authorize_action(tmp_path, evidence):
    job = build_job(request(), plan())
    artifact, proof = evidence
    result = assess(job, artifact, records(job, artifact, proof), proof, tmp_path)
    assert not result.release_ready and not result.action_authorized
    assert "Lifecycle has not reached release-candidate review" in result.blockers


def test_missing_failed_duplicate_and_wrong_applicability_block(tmp_path, evidence):
    job = build_job(request(), plan())
    artifact, proof = evidence
    rs = records(job, artifact, proof)
    assert not assess(job, artifact, rs[:-1], proof, tmp_path).release_ready
    assert not assess(job, artifact, rs + [rs[0]], proof, tmp_path).release_ready
    assert not assess(
        job, artifact, [rs[0].model_copy(update={"result": "FAIL"})] + rs[1:], proof, tmp_path
    ).release_ready
    wrong = rs[0].model_copy(update={"applicable": False, "result": None})
    assert not assess(job, artifact, [wrong] + rs[1:], proof, tmp_path).release_ready


def test_changed_artifact_or_evidence_invalidates_pass(tmp_path, evidence):
    job = build_job(request(), plan())
    artifact, proof = evidence
    rs = records(job, artifact, proof)
    (tmp_path / artifact.path).write_text("changed output")
    assert not assess(job, artifact, rs, proof, tmp_path).release_ready


def test_contract_edit_invalidates_old_records(tmp_path, evidence):
    job = build_job(request(), plan())
    artifact, proof = evidence
    rs = records(job, artifact, proof)
    edited = job.model_copy(update={"plan": plan(deliverables=["Changed output"])})
    assert not assess(edited, artifact, rs, proof, tmp_path).release_ready


def test_pass_requires_evidence_and_null_requires_nonapplicable(evidence):
    job = build_job(request(), plan())
    artifact, proof = evidence
    data = records(job, artifact, proof)[0].model_dump()
    data["evidence"] = []
    with pytest.raises(ValidationError):
        VerificationRecord.model_validate(data)
    data["evidence"] = [proof]
    data["result"] = None
    with pytest.raises(ValidationError):
        VerificationRecord.model_validate(data)


def test_resolved_shadow_rollback_consumer():
    class Chain:
        calls = 0

        def enhance(self, **kwargs):
            self.calls += 1
            return {"enhanced": "legacy default brief", "context_added": ["legacy"]}

    class Cache:
        pass

    chain = Chain()
    enhancer = PromptEnhancer(chain=chain, cache=Cache())
    resolved = enhancer.build_creative_brief(request(), plan())
    assert chain.calls == 0 and resolved["contract"]
    assert "legacy default brief" not in resolved["brief"]
    shadow = enhancer.build_creative_brief(request(), plan(), mode="shadow")
    assert shadow["comparison"]["changed"] and chain.calls == 1
    legacy = enhancer.build_creative_brief(request(), plan(), mode="legacy")
    assert legacy["contract"] is None and not legacy["resolver_guarantees"]


def test_any_failed_criterion_blocks_even_with_gate_pass(tmp_path, evidence):
    job = build_job(request(), plan())
    artifact, proof = evidence
    rs = records(job, artifact, proof)
    altered = rs[0].model_dump()
    altered["criteria"] = {
        "origin": {"applicable": True, "result": "FAIL", "reason": "Wrong origin"}
    }
    rs[0] = VerificationRecord.model_validate(altered)
    assert not assess(job, artifact, rs, proof, tmp_path).release_ready


def test_missing_or_changed_review_evidence_blocks(tmp_path, evidence):
    job = build_job(request(), plan())
    artifact, proof = evidence
    rs = records(job, artifact, proof)
    (tmp_path / proof.path).unlink()
    assert not assess(job, artifact, rs, proof, tmp_path).release_ready


def test_rule_checklist_matches_ratified_contract():
    from skyyrose.core.creative_job import FIDELITY
    import json

    spec = json.loads(
        (REPO_ROOT / "docs/brand/constitution-v1/implementation-contracts.json").read_text()
    )
    assert set(FIDELITY) == set(spec["fidelity_criteria"])


def test_exact_photography_requires_actual_requested_view():
    import hashlib
    from skyyrose.core.context_resolver import ProductRequirement

    wrong = REPO_ROOT / "docs/brand/constitution-v1/constitution.json"
    reference = {"path": str(wrong), "sha256": hashlib.sha256(wrong.read_bytes()).hexdigest()}
    req = request().model_copy(
        update={
            "representation_mode": "EXACT_PRODUCT",
            "content_intent": request().content_intent.model_copy(
                update={"representation_mode": "EXACT_PRODUCT"}
            ),
            "products": [
                ProductRequirement(
                    sku="br-001", required_views=["front"], required_details=["name"]
                )
            ],
        }
    )
    job = build_job(
        req,
        plan(
            production_method={
                "technique": "SOURCE_COMPOSITE",
                "rationale": "Invalid source fixture",
                "inputs": [reference],
                "feasibility_evidence": [reference],
            }
        ),
    )
    assert not job.production_path_ready
    assert any("every requested canonical view" in b for b in job.blockers)


def test_brief_keeps_full_request_and_scoped_policies():
    job = build_job(request(), plan())
    brief = render_brief(job)
    for text in ("BRAND_ABSTRACT", "NATURAL_LOCATION", "image", "SkyyRose customers", "P5-001"):
        assert text in brief


def test_M6_complete_intent_records_can_advance_without_action_authority(
    tmp_path, evidence, monkeypatch
):
    from skyyrose.core import context_resolver
    from skyyrose.core.creative_job import Criterion

    monkeypatch.setattr(context_resolver, "REPO_ROOT", tmp_path)
    brief = tmp_path / "campaign.txt"
    brief.write_text("Synthetic campaign authority fixture")
    req = request().model_copy(
        update={
            "lifecycle_stage": "M6",
            "campaign_brief": ref(brief),
            "absence_reasons": {"collection_context": "Master brand"},
            "content_intent": request().content_intent.model_copy(update={"lifecycle_stage": "M6"}),
        }
    )
    job = build_job(req, plan(major_initiative=False))
    assert job.status == "PRODUCTION_READY"
    artifact, proof = evidence
    rs = records(job, artifact, proof)
    enriched = []
    for record in rs:
        criteria = {
            name: Criterion(applicable=True, result="PASS", reason="Synthetic requirement evidence")
            for name in job.context.verification_requirements.get(record.gate, [])
        }
        enriched.append(record.model_copy(update={"criteria": criteria}))
    result = assess(job, artifact, enriched, proof, tmp_path)
    assert result.status == "RELEASE_CANDIDATE" and result.release_ready
    assert not result.action_authorized
    # Same PASS without the editorial-specific criteria must not pass.
    assert not assess(job, artifact, rs, proof, tmp_path).release_ready


def test_high_cost_source_requires_derivative_coverage():
    job = build_job(request(), plan(high_cost_source=True))
    assert job.status == "BLOCKED"
    assert "High-cost production requires derivative coverage planning" in job.blockers


def test_compact_projection_default_separate_from_audit():
    from skyyrose.core.creative_job import audit_bundle, execution_bundle

    job = build_job(request(), plan())
    execution = execution_bundle(job)
    audit = audit_bundle(job)
    assert "raw_product_snapshots" not in execution
    assert "raw_product_snapshots" in audit
    assert "constitution_sha256" in execution["brand"]
    assert "applicable_rules" not in render_brief(job)
    assert "raw_product_snapshots" in render_brief(job, debug=True)


def test_interactive_intent_cannot_disable_accessibility_or_commerce():
    req = request()
    data = req.model_dump()
    data["content_intent"].update(
        medium="interactive",
        production_type="experimental_shopping_experience",
        content_role="experimental_shopping_experience",
    )
    req = ResolutionRequest.model_validate(data)
    job = build_job(req, plan(accessibility_applicable=False, commerce_applicable=False))
    assert job.status == "BLOCKED"
    assert "Content intent requires accessibility verification" in job.blockers
    assert "Content intent requires commerce-integrity verification" in job.blockers
