"""Behavioral tests for the shared Creative Operations Hub local route."""

import json
from dataclasses import replace

import pytest
from PIL import Image

from skyyrose.elite_studio.creative.editorial import (
    Direction,
    ResolvedEditorial,
    identity,
    run_editorial,
    verify_context_link,
)
from skyyrose.elite_studio.creative.local_composite import AssetRef, LocalCompositeGrant, Placement


class SyntheticBrand:
    def __init__(self, root):
        import hashlib

        self.root = root
        self.brand = "Synthetic Apricot Laboratory"
        self.instruction = "Preserve the synthetic checkerboard and orange border."
        self.status = "PLANNING_READY"
        self.medium = "image"
        for name, color, size in [("source", "orange", (12, 12)), ("background", "navy", (48, 48))]:
            im = Image.new("RGB", size, color)
            if name == "source":
                for y in range(3, 9):
                    for x in range(3, 9):
                        im.putpixel((x, y), (255, 255, 255) if (x + y) % 2 else (0, 0, 0))
            im.save(root / f"{name}.png")
        Image.new("L", (12, 12), 255).save(root / "mask.png")
        self.refs = {
            n: AssetRef(f"{n}.png", hashlib.sha256((root / f"{n}.png").read_bytes()).hexdigest())
            for n in ("source", "background", "mask")
        }

    def resolve(self):
        execution = {
            "job": {"id": "synthetic-job", "status": self.status},
            "brand": {
                "name": self.brand,
                "rules": [{"id": "SYN-1", "instruction": self.instruction}],
            },
            "intent": {"medium": self.medium, "production_type": "editorial_still"},
            "production_method": {"technique": "SOURCE_COMPOSITE"},
            "products": [
                {
                    "name": "Synthetic checker tile",
                    "selected_source": {
                        "path": self.refs["source"].path,
                        "sha256": self.refs["source"].sha256,
                    },
                }
            ],
        }
        return ResolvedEditorial(
            execution,
            {"execution_digest": identity(execution), "evidence": "Synthetic test authority only"},
            self.refs["source"],
        )

    def direction(self, key="A"):
        return Direction(
            key,
            f"Check contrast {key}",
            "Synthetic authorship",
            "navy surface",
            "centered tile",
            "test source",
            "clarity",
            "synthetic novelty",
            "pixel corruption",
            self.refs["background"],
            self.refs["mask"],
            Placement(8, 8, 2),
        )

    def grant(self):
        return LocalCompositeGrant(
            "synthetic-job",
            self.refs["source"].sha256,
            "output",
            "Synthetic test invocation; no external permissions",
        )


def test_second_brand_produces_real_output_without_identity_leakage(tmp_path):
    brand = SyntheticBrand(tmp_path)
    result = run_editorial(
        brand,
        [brand.direction()],
        root=tmp_path,
        output_dir=tmp_path / "output/run",
        grant=brand.grant(),
    )
    with Image.open(tmp_path / "output/run/A.png") as im:
        assert im.size == (48, 48)
    assert verify_context_link(tmp_path / "output/run")
    assert result["market_results"] is None
    assert result["experiment_class"] == "creative_direction"
    assert result["authority"]["spend"] is False
    assert result["pilot"] == "incomplete_pending_visual_review"
    for forbidden in ["skyyrose", "black-rose", "oakland", "bay area", "br-001"]:
        assert forbidden not in json.dumps(result).lower()
    assert json.loads((tmp_path / "output/run/A-verification.json").read_text())["status"] == "PASS"


def test_brief_cannot_self_grant(tmp_path):
    brand = SyntheticBrand(tmp_path)
    with pytest.raises(PermissionError):
        run_editorial(
            brand,
            [brand.direction()],
            root=tmp_path,
            output_dir=tmp_path / "output/run",
            grant=None,
        )
    assert not (tmp_path / "output/run/A.png").exists()


@pytest.mark.parametrize("change", ["rule", "source", "artifact", "audit"])
def test_changed_evidence_invalidates_run(tmp_path, change):
    brand = SyntheticBrand(tmp_path)
    kwargs = dict(root=tmp_path, output_dir=tmp_path / "output/run", grant=brand.grant())
    run_editorial(brand, [brand.direction()], **kwargs)
    if change == "rule":
        brand.instruction = "Different binding meaning"
    if change == "source":
        Image.new("RGB", (12, 12), "red").save(tmp_path / "source.png")
    if change == "artifact":
        Image.new("RGB", (48, 48), "red").save(tmp_path / "output/run/A.png")
    if change == "audit":
        (tmp_path / "output/run/audit.json").write_text("{}")
    with pytest.raises((ValueError, PermissionError)):
        run_editorial(brand, [brand.direction()], **kwargs)


def test_unsupported_route_and_blocked_context_do_not_render(tmp_path):
    brand = SyntheticBrand(tmp_path)
    brand.medium = "video"
    with pytest.raises(NotImplementedError):
        run_editorial(
            brand,
            [brand.direction()],
            root=tmp_path,
            output_dir=tmp_path / "output/run",
            grant=brand.grant(),
        )
    brand.medium = "image"
    brand.status = "BLOCKED"
    with pytest.raises(ValueError, match="Blocked"):
        run_editorial(
            brand,
            [brand.direction()],
            root=tmp_path,
            output_dir=tmp_path / "output/run",
            grant=brand.grant(),
        )
    assert not (tmp_path / "output/run").exists()


def test_cross_run_direction_budget_is_enforced(tmp_path):
    brand = SyntheticBrand(tmp_path)
    for i in range(3):
        run_editorial(
            brand,
            [brand.direction()],
            root=tmp_path,
            output_dir=tmp_path / f"output/run{i}",
            grant=brand.grant(),
        )
    with pytest.raises(PermissionError, match="budget"):
        run_editorial(
            brand,
            [brand.direction()],
            root=tmp_path,
            output_dir=tmp_path / "output/run4",
            grant=brand.grant(),
        )
    assert not (tmp_path / "output/run4/A.png").exists()


def test_mismatched_compact_audit_rejected(tmp_path):
    brand = SyntheticBrand(tmp_path)
    original = brand.resolve
    brand.resolve = lambda: replace(original(), audit={"execution_digest": "bad"})
    with pytest.raises(ValueError, match="mismatch"):
        run_editorial(
            brand,
            [brand.direction()],
            root=tmp_path,
            output_dir=tmp_path / "output/run",
            grant=brand.grant(),
        )


def test_reuse_does_not_consume_another_render(tmp_path):
    brand = SyntheticBrand(tmp_path)
    args = dict(root=tmp_path, output_dir=tmp_path / "output/run", grant=brand.grant())
    a = run_editorial(brand, [brand.direction()], **args)
    b = run_editorial(brand, [brand.direction()], **args)
    assert a == b
    assert (
        len(
            json.loads(
                next((tmp_path / ".artifacts/creative-os-authority").glob("*.json")).read_text()
            )["attempts"]
        )
        == 1
    )


def test_market_planning_is_complete_and_never_execution():
    from pydantic import ValidationError

    from skyyrose.elite_studio.creative.editorial import ExperimentPlan

    with pytest.raises(ValidationError, match="assignment_exposure"):
        ExperimentPlan(experiment_class="market", hypothesis="Test preference")
    for kind in ("creative_direction", "experience", "execution"):
        assert (
            ExperimentPlan(experiment_class=kind, hypothesis="Bounded hypothesis").experiment_class
            == kind
        )
    plan = ExperimentPlan(
        experiment_class="market",
        hypothesis="Test preference",
        assignment_exposure="Random assignment, not executed",
        primary_metric="Declared conversion",
        guardrails="No traffic without grant",
        measurement_validity="Instrumentation review required",
        sample_horizon="Prospective plan",
        stopping_rule="Predeclared horizon",
        budget="Zero authorized",
        approval_reference="NOT AUTHORIZED: planning only",
    )
    assert plan.budget == "Zero authorized"


def test_destination_change_does_not_reset_same_authority_budget(tmp_path):
    brand = SyntheticBrand(tmp_path)
    for i in range(3):
        destination = f"destination{i}"
        grant = replace(brand.grant(), output_root=destination)
        run_editorial(
            brand,
            [brand.direction()],
            root=tmp_path,
            output_dir=tmp_path / destination,
            grant=grant,
        )
    with pytest.raises(PermissionError, match="budget"):
        run_editorial(
            brand,
            [brand.direction()],
            root=tmp_path,
            output_dir=tmp_path / "destination4",
            grant=replace(brand.grant(), output_root="destination4"),
        )


def test_pilot_input_preparation_is_immutable(tmp_path):
    from scripts.run_creative_os_pilot import immutable_bytes

    path = tmp_path / "evidence"
    immutable_bytes(path, b"original")
    immutable_bytes(path, b"original")
    with pytest.raises(ValueError, match="preserve"):
        immutable_bytes(path, b"changed")
    assert path.read_bytes() == b"original"


def test_missing_visual_review_and_false_owner_approval_do_not_pass(tmp_path):
    from skyyrose.elite_studio.creative.editorial import assess_editorial_review

    brand = SyntheticBrand(tmp_path)
    directory = tmp_path / "output/run"
    run_editorial(
        brand, [brand.direction()], root=tmp_path, output_dir=directory, grant=brand.grant()
    )
    result = assess_editorial_review(directory, {}, root=tmp_path, adapter=brand)
    assert result["pilot"] == "incomplete"
    assert result["results"][0]["visible_fidelity"] == "BLOCKED"
    with pytest.raises(ValueError, match="owner approval"):
        assess_editorial_review(
            directory,
            {"A": {"creative_assessment": "OWNER_APPROVED"}},
            root=tmp_path,
            adapter=brand,
        )


def test_duplicate_candidate_cannot_count_as_three(tmp_path):
    from skyyrose.elite_studio.creative.editorial import assess_editorial_review

    brand = SyntheticBrand(tmp_path)
    directory = tmp_path / "output/run"
    run_editorial(
        brand, [brand.direction()], root=tmp_path, output_dir=directory, grant=brand.grant()
    )
    path = directory / "production.json"
    production = json.loads(path.read_text())
    production["candidates"] *= 3
    path.write_text(json.dumps(production))
    with pytest.raises(ValueError, match="Duplicate"):
        assess_editorial_review(directory, {}, root=tmp_path, adapter=brand)


def test_extra_applicable_visual_failure_cannot_be_ignored(tmp_path):
    from skyyrose.elite_studio.creative.editorial import assess_editorial_review

    brand = SyntheticBrand(tmp_path)
    directory = tmp_path / "output/run"
    produced = run_editorial(
        brand, [brand.direction()], root=tmp_path, output_dir=directory, grant=brand.grant()
    )
    keys = [
        "source_view",
        "silhouette",
        "trim",
        "artwork_placement",
        "proportions_construction",
        "color_material",
        "occlusion",
        "canvas_clipping",
        "boundary",
    ]
    review = {
        "artifact_sha256": produced["candidates"][0]["receipt"]["output_sha256"],
        "reviewer": "test",
        "method": "synthetic fixture inspection",
        "criteria": {k: {"result": "PASS", "evidence": "synthetic test evidence"} for k in keys},
        "creative_assessment": "REVISE",
    }
    review["criteria"]["additional_material_trait"] = {
        "applicable": True,
        "result": "FAIL",
        "evidence": "Failure must control",
    }
    result = assess_editorial_review(directory, {"A": review}, root=tmp_path, adapter=brand)
    assert result["results"][0]["visible_fidelity"] == "BLOCKED"


def test_production_job_must_match_context(tmp_path):
    from skyyrose.elite_studio.creative.editorial import assess_editorial_review

    brand = SyntheticBrand(tmp_path)
    directory = tmp_path / "output/run"
    run_editorial(
        brand, [brand.direction()], root=tmp_path, output_dir=directory, grant=brand.grant()
    )
    path = directory / "production.json"
    p = json.loads(path.read_text())
    p["job_id"] = "different"
    path.write_text(json.dumps(p))
    with pytest.raises(ValueError, match="linkage"):
        assess_editorial_review(directory, {}, root=tmp_path, adapter=brand)


def test_assessment_re_resolves_authority_instead_of_trusting_saved_context(tmp_path):
    from skyyrose.elite_studio.creative.editorial import assess_editorial_review

    brand = SyntheticBrand(tmp_path)
    directory = tmp_path / "output/run"
    run_editorial(
        brand, [brand.direction()], root=tmp_path, output_dir=directory, grant=brand.grant()
    )
    brand.instruction = "Changed binding rule after rendering"
    with pytest.raises(ValueError, match="stale"):
        assess_editorial_review(directory, {}, root=tmp_path, adapter=brand)
