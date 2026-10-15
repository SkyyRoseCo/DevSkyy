from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scene_ooda.py"
SPEC = importlib.util.spec_from_file_location("scene_ooda", SCRIPT)
assert SPEC and SPEC.loader
scene_ooda = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scene_ooda)


def test_higgsfield_command_is_enhance_only_and_source_bound(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    source.write_bytes(b"source")
    manifest = {
        "provider_capability": {"higgsfield_role": "REFERENCE_GENERATION_CANDIDATE_ONLY"},
        "higgsfield": {
            "mode": "hero_banner",
            "prompt": "campaign",
            "aspect_ratio": "16:9",
            "count": 1,
            "brand_context": "brand",
            "product_context": "product",
        },
        "source_bindings": [
            {
                "path": str(source),
                "send_to_higgsfield": True,
            }
        ],
    }

    command = scene_ooda.higgsfield_command(manifest, enhance_only=True)

    assert command[:4] == [
        "higgsfield",
        "--json",
        "product-photoshoot",
        "create",
    ]
    assert command[-1] == "--enhance-only"
    assert command[command.index("--image") + 1] == str(source)


def test_higgsfield_command_rejects_disabled_scene_route() -> None:
    manifest = {"provider_capability": {"higgsfield_role": "DISABLED_FOR_NEW_FULL_SCENE_ATTEMPTS"}}

    with pytest.raises(RuntimeError, match="does not authorize"):
        scene_ooda.higgsfield_command(manifest, enhance_only=False)


def test_observe_fails_closed_on_missing_dependency(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    source.write_bytes(b"source")
    digest = scene_ooda.sha256_file(source)
    manifest = {
        "scene_id": "TEST-SCENE",
        "catalog_snapshot": {
            "catalog_path": str(source),
            "catalog_sha256": digest,
            "image_manifest_path": str(source),
            "image_manifest_sha256": digest,
        },
        "source_bindings": [{"path": str(source), "sha256": digest}],
        "authority_dependencies": [{"path": str(tmp_path / "missing.png")}],
        "execute_blockers": [],
    }

    report = scene_ooda.observe(manifest)

    assert report["source_ready"] is True
    assert report["dependencies_ready"] is False
    assert report["configuration_ready"] is False
    assert report["paid_execution_ready"] is False


def test_enhanced_prompt_inspection_rejects_product_drift() -> None:
    manifest = {
        "higgsfield": {
            "prompt_assertions": {
                "required_phrases": ["right chest", "side-body"],
                "forbidden_phrases": ["left sleeve", "sleeve graphic"],
            }
        }
    }
    result = {
        "stdout": {
            "prompts": [{"prompt": "A left sleeve graphic replaces the right chest artwork."}]
        }
    }

    inspection = scene_ooda.inspect_enhanced_prompt(manifest, result)

    assert inspection["status"] == "REJECTED_ENHANCER_PRODUCT_DRIFT"
    assert inspection["missing_required_phrases"] == ["side-body"]
    assert inspection["present_forbidden_phrases"] == ["left sleeve", "sleeve graphic"]


def test_enhanced_prompt_inspection_accepts_bound_product_facts() -> None:
    manifest = {
        "higgsfield": {
            "prompt_assertions": {
                "required_phrases": ["right chest", "side-body", "OAKLAND"],
                "forbidden_phrases": ["left sleeve"],
            }
        }
    }
    result = {
        "stdout": {
            "prompts": [
                {
                    "prompt": "Small rose on the right chest, floral side-body artwork, and OAKLAND shorts."
                }
            ]
        }
    }

    inspection = scene_ooda.inspect_enhanced_prompt(manifest, result)

    assert inspection["status"] == "PASS"
    assert inspection["missing_required_phrases"] == []
    assert inspection["present_forbidden_phrases"] == []


def test_all_remaining_scene_manifests_follow_team_ooda() -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    index = json.loads((contract_root / "scene-ooda-index.json").read_text(encoding="utf-8"))

    assert index["plugin"] == "fashion-theme-team@personal"
    assert index["phase_ownership"]["decide"]["independent"] is True
    assert index["candidate_rules"]["rejected_assets_are_evidence_only"] is True
    assert (
        index["candidate_rules"][
            "environment_provider_must_not_receive_protected_customer_product_or_sculpture"
        ]
        is True
    )
    assert index["phase_ownership"]["promotion"]["required_state"] == "FOUNDER_APPROVED_VISUAL"

    expected_scenes = {
        "BR-COMMERCE-2",
        "LH-COMMERCE-2",
        "SIG-COMMERCE-1",
        "SIG-COMMERCE-2",
        "SIG-COMMERCE-3",
    }
    actual_scenes = set()
    for entry in index["scenes"]:
        manifest_path = scene_ooda.resolve_path(entry["contract"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        actual_scenes.add(manifest["scene_id"])
        assert manifest.get("route_contract", {}).get("mode") in {
            "environment_rebuild_around_source",
            "selective_vto_then_environment_rebuild_around_source",
            "mask_bound_local_correction_only",
        } or manifest.get("native_scene_workflow", {}).get("mode") == (
            "environment_rebuild_around_source"
        )
        assert manifest["creative_direction"]["style"] == "cinematic_urban_grit"
        assert scene_ooda.verify_creative_direction(manifest)["status"] == "PASS"
        assert scene_ooda.verify_optical_contract(manifest)["status"] == "PASS"
        assert scene_ooda.verify_comfy_contract(manifest)["status"] == "PASS"
        assert scene_ooda.verify_credit_control(manifest)["status"] == "PASS"
        assert manifest["comfy"]["server"] == "http://127.0.0.1:8189"
        assert manifest["credit_control"]["max_paid_generations"] == 1
        assert manifest["credit_control"]["automatic_paid_retries"] is False
        assert manifest["credit_control"]["rejected_candidate_may_be_next_input"] is False
        if manifest["scene_id"] != "BR-COMMERCE-2":
            assert manifest["execute_blockers"]
        assert manifest["promotion_gate"] == "FOUNDER_APPROVED_VISUAL"
        assert scene_ooda.verify_team_contract(manifest)["status"] == "PASS"
        if manifest["provider_capability"].get("higgsfield_role") != (
            "REFERENCE_GENERATION_CANDIDATE_ONLY"
        ):
            assert all(
                binding.get("send_to_higgsfield") is not True
                for binding in manifest["source_bindings"]
            )
            assert all(
                isinstance(binding.get("provider_use"), str) and binding["provider_use"].strip()
                for binding in manifest["source_bindings"]
            )

    assert actual_scenes == expected_scenes


def test_lh_native_workflow_dependencies_are_hash_bound_and_fail_closed() -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    manifest = json.loads(
        (contract_root / "lh-commerce-2-higgsfield-comfy-ooda.json").read_text(encoding="utf-8")
    )

    checks = scene_ooda.verify_native_workflow_dependencies(manifest)

    assert len(checks) == 6
    assert all(check["status"] == "PASS" for check in checks)

    manifest["native_scene_workflow"]["background"][
        "workflow"
    ] = "Comfy/workflows/does-not-exist.api.json"
    missing_checks = scene_ooda.verify_native_workflow_dependencies(manifest)
    assert any(check["status"] == "MISSING" for check in missing_checks)
    assert scene_ooda.observe(manifest)["configuration_ready"] is False

    manifest = json.loads(
        (contract_root / "lh-commerce-2-higgsfield-comfy-ooda.json").read_text(encoding="utf-8")
    )
    manifest["native_scene_workflow"]["segmentation"][
        "verification_required_before_composite"
    ] = False
    rgb_checks = scene_ooda.verify_native_workflow_dependencies(manifest)
    assert any(check["status"] == "MISSING_PROTECTED_RGB_VERIFICATION" for check in rgb_checks)


def test_paid_execution_needs_portable_authorities_and_receipts() -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    manifest = json.loads(
        (contract_root / "br-commerce-2-higgsfield-comfy-ooda.json").read_text(encoding="utf-8")
    )
    manifest["execute_blockers"] = []
    manifest["credit_control"]["prompt_review_receipt"] = None
    manifest["credit_control"]["approval_receipt"] = None

    report = scene_ooda.observe(manifest)

    assert report["configuration_ready"] is False
    assert any(check["status"] == "MISSING" for check in report["source_checks"])
    assert report["credit_control_check"]["prompt_review"]["status"] == "MISSING_RECEIPT"
    assert report["credit_control_check"]["paid_approval"]["status"] == "MISSING_RECEIPT"
    assert report["paid_authorized"] is False
    assert report["paid_execution_ready"] is False


def test_optical_contract_rejects_geometry_outside_frame() -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    manifest = json.loads(
        (contract_root / "sig-commerce-1-higgsfield-comfy-ooda.json").read_text(encoding="utf-8")
    )
    manifest["optical_contract"]["subject_boxes"][0]["x"] = 2048

    result = scene_ooda.verify_optical_contract(manifest)

    assert result["status"] == "INVALID_OPTICAL_CONTRACT"
    assert "subject_boxes[0] exceeds output geometry" in result["failures"]


def test_collection_world_prompt_adherence_is_hash_bound_and_fail_closed() -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    expected = {
        "BR-COMMERCE-2": {
            "role": "black_rose_collection_world_reference",
            "suffix": "black-rose-bay-bridge-monuments-v4.webp",
            "forbidden": "copied star monument",
        },
        "LH-COMMERCE-2": {
            "role": "love_hurts_collection_world_reference",
            "suffix": "love-hurts-rose-aisle-monuments-v3.webp",
            "forbidden": "copied star/heart monument",
        },
    }

    for filename in (
        "br-commerce-2-higgsfield-comfy-ooda.json",
        "lh-commerce-2-higgsfield-comfy-ooda.json",
    ):
        manifest = json.loads((contract_root / filename).read_text(encoding="utf-8"))
        rule = expected[manifest["scene_id"]]
        binding = next(item for item in manifest["source_bindings"] if item["role"] == rule["role"])
        serialized = json.dumps(manifest).casefold()

        assert binding["path"].endswith(rule["suffix"])
        assert (
            scene_ooda.verify_file(scene_ooda.resolve_path(binding["path"]), binding["sha256"])[
                "status"
            ]
            == "PASS"
        )
        assert rule["forbidden"] in serialized
        adherence = scene_ooda.verify_prompt_adherence(manifest)
        assert adherence == {"status": "PASS", "configured": True, "failures": []}
        assert manifest["prompt_adherence"]["post_capture"]["minimum_total_score"] == 90
        assert manifest["prompt_adherence"]["disposition_on_failure"] == (
            "QUARANTINE_NO_AUTOMATIC_RETRY"
        )


def test_prompt_adherence_rejects_missing_source_role_and_prompt_claim() -> None:
    manifest = {
        "source_bindings": [{"role": "product"}],
        "higgsfield": {
            "prompt": "customer-first scene",
            "brand_context": "brand",
            "product_context": "product",
        },
        "prompt_adherence": {
            "mode": "FAIL_CLOSED",
            "independent_reviewer_role": "visual-commerce-qa",
            "preflight": {
                "required_source_roles": ["product", "world"],
                "required_prompt_claims": ["customer-first", "four zippered pockets"],
            },
            "post_capture": {
                "minimum_total_score": 90,
                "dimensions": [{"id": "fidelity", "weight": 100}],
            },
            "hard_fail_invariants": ["wrong product"],
            "disposition_on_failure": "QUARANTINE_NO_AUTOMATIC_RETRY",
        },
    }

    result = scene_ooda.verify_prompt_adherence(manifest)

    assert result["status"] == "INVALID_PROMPT_ADHERENCE"
    assert "missing routed source roles: product, world" in result["failures"]
    assert "missing required prompt claims: four zippered pockets" in result["failures"]


def test_prompt_adherence_rejects_unrouted_duplicate_null_and_weak_threshold() -> None:
    base = {
        "source_bindings": [
            {"role": "product", "send_to_higgsfield": True},
            {"role": "world", "send_to_higgsfield": False},
        ],
        "higgsfield": {
            "prompt": "customer-first exact product world",
            "brand_context": "brand",
            "product_context": "product",
        },
        "prompt_adherence": {
            "mode": "FAIL_CLOSED",
            "independent_reviewer_role": "visual-commerce-qa",
            "preflight": {
                "required_source_roles": ["product", "world"],
                "required_prompt_claims": ["customer-first", "exact product"],
            },
            "post_capture": {
                "minimum_total_score": 0,
                "dimensions": [{"id": "fidelity", "weight": 100}],
            },
            "hard_fail_invariants": ["wrong product"],
            "disposition_on_failure": "QUARANTINE_NO_AUTOMATIC_RETRY",
        },
    }

    result = scene_ooda.verify_prompt_adherence(base)
    assert "missing routed source roles: world" in result["failures"]
    assert "minimum_total_score must be an integer from 90 to 100" in result["failures"]

    base["source_bindings"] = [
        {"role": "product", "send_to_higgsfield": True},
        {"role": "product", "send_to_higgsfield": True},
        {"role": "world", "send_to_higgsfield": True},
    ]
    base["prompt_adherence"]["post_capture"]["minimum_total_score"] = 90
    result = scene_ooda.verify_prompt_adherence(base)
    assert "required source roles must be routed exactly once: product" in result["failures"]

    base["prompt_adherence"] = None
    result = scene_ooda.verify_prompt_adherence(base)
    assert result["status"] == "INVALID_PROMPT_ADHERENCE"


def test_prompt_adherence_accepts_explicit_provider_use_routing() -> None:
    manifest = {
        "source_bindings": [
            {"role": "product", "provider_use": "SOURCE_AUTHORITY_ONLY"},
            {"role": "world", "provider_use": "RUNWAY_ENVIRONMENT_REFERENCE_ONLY"},
        ],
        "native_scene_workflow": {
            "foreground": "protected product",
            "background": {"prompt": "environment only with no people and no products"},
        },
        "prompt_adherence": {
            "mode": "FAIL_CLOSED",
            "independent_reviewer_role": "visual-commerce-qa",
            "preflight": {
                "required_source_roles": ["product", "world"],
                "required_prompt_claims": ["environment only", "no people", "no products"],
            },
            "post_capture": {
                "minimum_total_score": 90,
                "dimensions": [{"id": "fidelity", "weight": 100}],
            },
            "hard_fail_invariants": ["wrong product"],
            "disposition_on_failure": "QUARANTINE_NO_AUTOMATIC_RETRY",
        },
    }

    assert scene_ooda.verify_prompt_adherence(manifest) == {
        "status": "PASS",
        "configured": True,
        "failures": [],
    }


@pytest.mark.parametrize(
    ("provider_use", "role", "expected_failure"),
    [
        ("", "product", "invalid provider_use"),
        ("UNKNOWN_PROVIDER_ROUTE", "product", "invalid provider_use"),
        (
            "RUNWAY_ENVIRONMENT_REFERENCE_ONLY",
            "protected_customer_product_and_sculpture",
            "Runway may receive only a world/environment source",
        ),
        (
            "FASHN_PRIMARY_PRODUCT_INPUT",
            "approved_customer_identity",
            "FASHN may receive only an explicit product source",
        ),
        (
            "RUNWAY_ENVIRONMENT_REFERENCE_ONLY",
            "protected_customer_product_environment",
            "Runway may receive only a world/environment source",
        ),
        (
            "FASHN_PRIMARY_PRODUCT_INPUT",
            "nonproduct_customer_identity",
            "FASHN may receive only an explicit product source",
        ),
    ],
)
def test_prompt_adherence_rejects_invalid_or_misrouted_provider_use(
    provider_use: str, role: str, expected_failure: str
) -> None:
    manifest = {
        "source_bindings": [{"role": role, "provider_use": provider_use}],
        "native_scene_workflow": {
            "foreground": "protected source",
            "background": {"prompt": "environment only"},
        },
        "prompt_adherence": {
            "mode": "FAIL_CLOSED",
            "independent_reviewer_role": "visual-commerce-qa",
            "preflight": {
                "required_source_roles": [role],
                "required_prompt_claims": ["environment only"],
            },
            "post_capture": {
                "minimum_total_score": 90,
                "dimensions": [{"id": "fidelity", "weight": 100}],
            },
            "hard_fail_invariants": ["wrong product"],
            "disposition_on_failure": "QUARANTINE_NO_AUTOMATIC_RETRY",
        },
    }

    result = scene_ooda.verify_prompt_adherence(manifest)

    assert result["status"] == "INVALID_PROMPT_ADHERENCE"
    assert expected_failure in " ".join(result["failures"])


def _prompt_adherence_review(
    manifest: dict, candidate_sha256: str, score: float, hard_failure: bool = False
) -> dict:
    dimensions = manifest["prompt_adherence"]["post_capture"]["dimensions"]
    invariants = manifest["prompt_adherence"]["hard_fail_invariants"]
    return {
        "schema": "skyyrose.prompt-adherence-review/1",
        "scene_id": manifest["scene_id"],
        "candidate_sha256": candidate_sha256,
        "manifest_fingerprint": scene_ooda.execution_fingerprint(manifest),
        "reviewer": {
            "id": "independent-reviewer-test",
            "role": manifest["prompt_adherence"]["independent_reviewer_role"],
            "independent": True,
        },
        "scores": {dimension["id"]: score for dimension in dimensions},
        "hard_fail_results": [
            {
                "invariant": invariant,
                "failed": hard_failure and index == 0,
                "evidence": f"reviewed invariant {index}",
            }
            for index, invariant in enumerate(invariants)
        ],
    }


def test_candidate_bound_prompt_adherence_enforces_threshold_and_hard_fail(
    tmp_path: Path,
) -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    manifest = json.loads(
        (contract_root / "lh-commerce-2-higgsfield-comfy-ooda.json").read_text(encoding="utf-8")
    )
    candidate = tmp_path / "candidate.png"
    candidate.write_bytes(b"candidate pixels")
    candidate_sha256 = scene_ooda.sha256_file(candidate)
    review_path = tmp_path / "review.json"

    review_path.write_text(
        json.dumps(_prompt_adherence_review(manifest, candidate_sha256, 90)),
        encoding="utf-8",
    )
    passed = scene_ooda.verify_prompt_adherence_review(manifest, candidate, review_path)
    assert passed["status"] == "PASS"
    assert passed["weighted_total"] == 90

    review_path.write_text(
        json.dumps(_prompt_adherence_review(manifest, candidate_sha256, 89)),
        encoding="utf-8",
    )
    below = scene_ooda.verify_prompt_adherence_review(manifest, candidate, review_path)
    assert below["status"] == "BELOW_THRESHOLD_QUARANTINED"
    assert below["weighted_total"] == 89

    review_path.write_text(
        json.dumps(_prompt_adherence_review(manifest, candidate_sha256, 100, True)),
        encoding="utf-8",
    )
    hard_failed = scene_ooda.verify_prompt_adherence_review(manifest, candidate, review_path)
    assert hard_failed["status"] == "HARD_FAIL_QUARANTINED"
    assert hard_failed["weighted_total"] == 100
    assert hard_failed["hard_failures"] == [manifest["prompt_adherence"]["hard_fail_invariants"][0]]

    stale = _prompt_adherence_review(manifest, "0" * 64, 100)
    review_path.write_text(json.dumps(stale), encoding="utf-8")
    invalid = scene_ooda.verify_prompt_adherence_review(manifest, candidate, review_path)
    assert invalid["status"] == "INVALID_PROMPT_ADHERENCE_REVIEW"
    assert "review is not bound to the current candidate hash" in invalid["failures"]

    review_path.write_text("[]", encoding="utf-8")
    malformed = scene_ooda.verify_prompt_adherence_review(manifest, candidate, review_path)
    assert malformed["status"] == "INVALID_PROMPT_ADHERENCE_REVIEW"
    assert "review receipt must be an object" in malformed["failures"]

    manager_review = _prompt_adherence_review(manifest, candidate_sha256, 100)
    manager_review["reviewer"]["id"] = " FASHION-THEME-LEAD "
    review_path.write_text(json.dumps(manager_review), encoding="utf-8")
    manager = scene_ooda.verify_prompt_adherence_review(manifest, candidate, review_path)
    assert manager["status"] == "INVALID_PROMPT_ADHERENCE_REVIEW"
    assert "reviewer must be independent from the accountable manager" in manager["failures"]


def test_comfy_stage_blocks_without_passing_prompt_adherence_review(
    tmp_path: Path,
) -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    manifest = json.loads(
        (contract_root / "lh-commerce-2-higgsfield-comfy-ooda.json").read_text(encoding="utf-8")
    )
    candidate = tmp_path / "candidate.png"
    candidate.write_bytes(b"candidate pixels")

    assert scene_ooda.action_stage(manifest, candidate, None) == 4


def test_hard_fail_quarantine_is_durable_for_candidate_hash(tmp_path: Path, monkeypatch) -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    manifest = json.loads(
        (contract_root / "lh-commerce-2-higgsfield-comfy-ooda.json").read_text(encoding="utf-8")
    )
    candidate = tmp_path / "candidate.png"
    candidate.write_bytes(b"candidate pixels")
    candidate_sha256 = scene_ooda.sha256_file(candidate)
    review_path = tmp_path / "review.json"
    monkeypatch.setattr(scene_ooda, "COMFY_ROOT", tmp_path / "Comfy")

    review_path.write_text(
        json.dumps(_prompt_adherence_review(manifest, candidate_sha256, 100, True)),
        encoding="utf-8",
    )
    assert scene_ooda.action_review_candidate(manifest, candidate, review_path) == 4
    marker = scene_ooda.prompt_adherence_quarantine_path(manifest["scene_id"], candidate_sha256)
    assert marker.is_file()
    first_record = json.loads(marker.read_text(encoding="utf-8"))
    assert first_record["disposition"] == "HARD_FAIL_QUARANTINED"
    assert first_record["automatic_retry"] is False

    review_path.write_text(
        json.dumps(_prompt_adherence_review(manifest, candidate_sha256, 100)),
        encoding="utf-8",
    )
    replacement = scene_ooda.verify_prompt_adherence_review(manifest, candidate, review_path)
    assert replacement["status"] == "CANDIDATE_HASH_QUARANTINED"

    upload_called = False

    def fake_run_command(_command):
        nonlocal upload_called
        upload_called = True
        return {"exit_code": 0, "stdout": {}, "stderr": ""}

    monkeypatch.setattr(scene_ooda, "require_cli", lambda _name: None)
    monkeypatch.setattr(scene_ooda, "run_command", fake_run_command)
    assert scene_ooda.action_stage(manifest, candidate, review_path) == 4
    assert upload_called is False


def test_direct_stage_hard_fail_persists_quarantine_before_return(
    tmp_path: Path, monkeypatch
) -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    manifest = json.loads(
        (contract_root / "lh-commerce-2-higgsfield-comfy-ooda.json").read_text(encoding="utf-8")
    )
    candidate = tmp_path / "candidate.png"
    candidate.write_bytes(b"direct-stage candidate pixels")
    candidate_sha256 = scene_ooda.sha256_file(candidate)
    review_path = tmp_path / "review.json"
    monkeypatch.setattr(scene_ooda, "COMFY_ROOT", tmp_path / "Comfy")

    upload_called = False

    def fake_run_command(_command):
        nonlocal upload_called
        upload_called = True
        return {"exit_code": 0, "stdout": {}, "stderr": ""}

    monkeypatch.setattr(scene_ooda, "require_cli", lambda _name: None)
    monkeypatch.setattr(scene_ooda, "run_command", fake_run_command)
    review_path.write_text(
        json.dumps(_prompt_adherence_review(manifest, candidate_sha256, 100, True)),
        encoding="utf-8",
    )
    assert scene_ooda.action_stage(manifest, candidate, review_path) == 4
    marker = scene_ooda.prompt_adherence_quarantine_path(manifest["scene_id"], candidate_sha256)
    assert marker.is_file()

    review_path.write_text(
        json.dumps(_prompt_adherence_review(manifest, candidate_sha256, 100)),
        encoding="utf-8",
    )
    assert scene_ooda.action_stage(manifest, candidate, review_path) == 4
    assert upload_called is False


def test_credit_control_rejects_paid_retry_configuration() -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    manifest = json.loads(
        (contract_root / "br-commerce-2-higgsfield-comfy-ooda.json").read_text(encoding="utf-8")
    )
    manifest["credit_control"]["max_paid_generations"] = 2
    manifest["credit_control"]["automatic_paid_retries"] = True

    result = scene_ooda.verify_credit_control(manifest)

    assert result["status"] == "INVALID_CREDIT_CONTROL"
    assert "max_paid_generations must equal 1" in result["failures"]
    assert "automatic_paid_retries must be false" in result["failures"]


def test_signature_ensemble_is_preserve_and_correct_only() -> None:
    contract_root = Path(__file__).resolve().parents[1] / "scene-contracts"
    manifest = json.loads(
        (contract_root / "sig-commerce-3-higgsfield-comfy-ooda.json").read_text(encoding="utf-8")
    )

    assert manifest["execution_strategy"]["full_frame_paid_generation"] is False
    assert manifest["execution_strategy"]["mode"] == (
        "PRESERVE_EXISTING_SCENE_MASK_BOUND_CORRECTION_ONLY"
    )
    assert "full-frame paid regeneration" in manifest["comfy"]["forbidden_operations"]
    report = scene_ooda.observe(manifest)
    assert report["paid_route_permitted"] is False
    assert report["paid_execution_ready"] is False


def test_rejected_source_cannot_be_routed_to_any_provider_or_local_operation(
    tmp_path: Path,
) -> None:
    allowed = tmp_path / "allowed.png"
    rejected = tmp_path / "rejected.png"
    allowed.write_bytes(b"allowed")
    rejected.write_bytes(b"rejected")
    manifest = {
        "scene_id": "TEST-SCENE",
        "catalog_snapshot": {
            "catalog_path": str(allowed),
            "catalog_sha256": scene_ooda.sha256_file(allowed),
            "image_manifest_path": str(allowed),
            "image_manifest_sha256": scene_ooda.sha256_file(allowed),
        },
        "source_bindings": [
            {
                "path": str(rejected),
                "sha256": scene_ooda.sha256_file(rejected),
                "send_to_higgsfield": True,
            }
        ],
        "forbidden_inputs": [{"path": str(rejected), "sha256": scene_ooda.sha256_file(rejected)}],
        "authority_dependencies": [],
        "execute_blockers": [],
        "fashion_theme_team": {
            "plugin": "fashion-theme-team@personal",
            "team_contract": "Comfy/scene-contracts/scene-ooda-index.json",
            "phase_id": "TEST-1",
            "accountable": "fashion-theme-lead",
            "next_authority": "visual-commerce-qa",
        },
    }

    report = scene_ooda.observe(manifest)

    assert report["forbidden_routing_clean"] is False
    assert report["paid_execution_ready"] is False

    manifest["source_bindings"][0]["send_to_higgsfield"] = False
    manifest["source_bindings"][0]["provider_use"] = "COMFY_PROTECTED_CORRECTION_INPUT"
    report = scene_ooda.observe(manifest)
    assert report["forbidden_routing_clean"] is False
    assert report["configuration_ready"] is False
