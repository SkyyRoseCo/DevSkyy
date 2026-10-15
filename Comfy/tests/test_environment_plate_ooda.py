from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from Comfy.scripts.environment_plate_ooda import (
    FORBIDDEN_ENVIRONMENT_SUBJECTS,
    EnvironmentContractError,
    build_founder_approval_packet,
    build_prompt_only_workflow,
    load_contract,
    validate_contract,
    validate_workflow_is_product_free,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPO_ROOT / "Comfy/scene-contracts"

CONTRACTS = (
    "lh-commerce-2-runway-environment-a1.json",
    "br-commerce-2-runway-environment-a1.json",
    "sig-commerce-1-runway-environment-a1.json",
    "sig-commerce-2-runway-environment-a1.json",
)


def _live_object_info(price: float = 0.11) -> dict:
    runway = {
        "input": {
            "required": {
                "prompt": ["STRING", {"multiline": True}],
                "ratio": ["COMBO", {"options": ["1920:1080"]}],
            },
            "optional": {"reference_image": ["IMAGE", {}]},
        },
        "output": ["IMAGE"],
        "name": "RunwayTextToImageNode",
        "display_name": "Runway Text to Image",
        "description": "Generate an image from a text prompt using Runway Gen 4.",
        "python_module": "comfy_api_nodes.nodes_runway",
        "category": "partner/image/Runway",
        "api_node": True,
        "price_badge": {"expr": json.dumps({"type": "usd", "usd": price})},
    }
    return {
        "RunwayTextToImageNode": runway,
        "ResizeImageMaskNode": {"input": {"required": {"input": ["IMAGE", {}]}}},
        "SaveImage": {"input": {"required": {"images": ["IMAGE", {}]}}},
    }


def _portable_contract(name: str, tmp_path: Path) -> tuple[dict, Path]:
    source = tmp_path / "local-inspiration.png"
    source.write_bytes(b"local-only-composition-inspiration")
    path = CONTRACT_ROOT / name
    contract = load_contract(path)
    contract["local_composition_inspiration"] = [
        {
            "path": str(source),
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "authority_role": "COMPOSITION_ATMOSPHERE_ONLY",
            "sent_to_runway": False,
        }
    ]
    return contract, path


@pytest.mark.parametrize("name", CONTRACTS)
def test_all_scene_environment_contracts_are_prompt_only_and_fail_closed(
    name: str, tmp_path: Path
) -> None:
    contract, path = _portable_contract(name, tmp_path)

    assert validate_contract(contract, contract_path=path) == []
    assert contract["provider_inputs"] == {
        "mode": "prompt_only",
        "reference_image": None,
        "protected_assets_sent": [],
        "reason": contract["provider_inputs"]["reason"],
    }
    assert set(contract["forbidden_plate_content"]) == set(FORBIDDEN_ENVIRONMENT_SUBJECTS)
    assert contract["credit_control"]["max_paid_generations"] == 1
    assert contract["credit_control"]["automatic_paid_retries"] is False
    assert contract["credit_control"]["approval_receipt"] is None
    assert contract["output"]["promotion_allowed"] is False
    assert contract["output"]["wiring_allowed"] is False
    assert contract["output"]["deployment_allowed"] is False


def test_lh_workflow_matches_builder_and_contains_no_source_upload() -> None:
    contract = load_contract(CONTRACT_ROOT / CONTRACTS[0])
    tracked = json.loads(
        (REPO_ROOT / "Comfy/workflows/lh-commerce-2-runway-environment-a1.api.json").read_text(
            encoding="utf-8"
        )
    )

    assert build_prompt_only_workflow(contract) == tracked
    assert validate_workflow_is_product_free(tracked) == []
    assert {node["class_type"] for node in tracked.values()} == {
        "RunwayTextToImageNode",
        "ResizeImageMaskNode",
        "SaveImage",
    }
    runway = tracked["1"]
    assert "reference_image" not in runway["inputs"]
    assert all(node["class_type"] != "LoadImage" for node in tracked.values())


def test_workflow_rejects_reference_or_protected_node() -> None:
    contract = load_contract(CONTRACT_ROOT / CONTRACTS[0])
    workflow = build_prompt_only_workflow(contract)
    workflow["1"]["inputs"]["reference_image"] = ["9", 0]
    workflow["9"] = {"class_type": "LoadImage", "inputs": {"image": "protected.png"}}
    workflow["10"] = {
        "class_type": "ImageCompositeMasked",
        "inputs": {"destination": ["1", 0], "source": ["9", 0]},
    }

    failures = validate_workflow_is_product_free(workflow)

    assert "Runway environment node must not receive reference_image" in failures
    assert "Runway environment workflow must not contain LoadImage" in failures
    assert any("ImageCompositeMasked" in failure for failure in failures)


def test_prompt_must_forbid_every_governed_subject(tmp_path: Path) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)
    contract["request"]["prompt"] = contract["request"]["prompt"].replace(
        "no sculptures", "sculptures are welcome"
    )

    failures = validate_contract(contract, contract_path=path)

    assert "prompt must explicitly forbid sculptures" in failures


def test_founder_packet_exposes_exact_price_fingerprint_and_stop(tmp_path: Path) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)
    contract["execution_blockers"] = []

    packet = build_founder_approval_packet(
        contract=contract,
        contract_path=path,
        live_object_info=_live_object_info(),
    )

    assert packet["status"] == "BLOCKED_PENDING_EXPLICIT_FOUNDER_APPROVAL"
    assert len(packet["execution_fingerprint"]) == 64
    assert packet["prompt"] == contract["request"]["prompt"]
    assert packet["live_partner_node"]["price_usd"] == 0.11
    assert packet["one_candidate_ceiling"] == {
        "max_paid_generations": 1,
        "max_price_usd": 0.11,
        "automatic_paid_retries": False,
    }
    assert packet["candidate_bound_approval_path"] == contract["output"]["approval_path"]
    assert packet["attempt_marker"] == contract["output"]["attempt_marker"]
    assert packet["protected_assets_sent_to_runway"] == []
    assert packet["paid_submission_performed"] is False
    assert packet["declared_execution_blockers"] == []
    assert packet["next_action"] == "STOP_FOR_EXPLICIT_FOUNDER_APPROVAL"


def test_declared_scene_blockers_remain_fail_closed(tmp_path: Path) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)

    packet = build_founder_approval_packet(
        contract=contract,
        contract_path=path,
        live_object_info=_live_object_info(),
    )

    assert packet["status"] == "BLOCKED"
    assert packet["failures"] == []
    assert packet["declared_execution_blockers"] == contract["execution_blockers"]
    assert packet["next_action"] == "REMEDIATE_BLOCKERS_WITHOUT_SUBMISSION"


def test_live_price_drift_blocks_before_submission(tmp_path: Path) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)

    packet = build_founder_approval_packet(
        contract=contract,
        contract_path=path,
        live_object_info=_live_object_info(price=0.12),
    )

    assert packet["status"] == "BLOCKED"
    assert any("exceeds" in failure for failure in packet["failures"])
    assert packet["paid_submission_performed"] is False
    assert packet["next_action"] == "REMEDIATE_BLOCKERS_WITHOUT_SUBMISSION"


def test_live_schema_must_identify_expected_partner_node(tmp_path: Path) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)
    contract["execution_blockers"] = []
    schema = _live_object_info()
    schema["RunwayTextToImageNode"]["description"] = "Unknown image generator"
    schema["RunwayTextToImageNode"]["name"] = "Unknown"
    schema["RunwayTextToImageNode"]["display_name"] = "Unknown"
    schema["RunwayTextToImageNode"]["python_module"] = "unknown"

    packet = build_founder_approval_packet(
        contract=contract,
        contract_path=path,
        live_object_info=schema,
    )

    assert packet["status"] == "BLOCKED"
    assert "live partner-node schema does not identify Runway Gen-4" in packet["failures"]
    assert packet["paid_submission_performed"] is False


def test_malformed_contract_builds_blocked_packet_instead_of_crashing(tmp_path: Path) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)
    contract["request"] = None

    packet = build_founder_approval_packet(
        contract=contract,
        contract_path=path,
        live_object_info=_live_object_info(),
    )

    assert packet["status"] == "BLOCKED"
    assert any("request contract is missing" in failure for failure in packet["failures"])
    assert any("workflow cannot be built" in failure for failure in packet["failures"])
    assert packet["paid_submission_performed"] is False


def test_contract_rejects_protected_reference_even_when_named_environment(
    tmp_path: Path,
) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)
    contract["provider_inputs"]["mode"] = "image_reference"
    contract["provider_inputs"]["reference_image"] = "protected-scene.png"
    contract["provider_inputs"]["protected_assets_sent"] = ["customer"]

    failures = validate_contract(contract, contract_path=path)

    assert "current environment plate route must be prompt-only" in failures
    assert "no image reference may be sent to Runway in the current route" in failures
    assert "protected assets sent to Runway must be an explicit empty list" in failures


def test_loader_rejects_wrong_schema(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"schema": "unknown"}), encoding="utf-8")

    with pytest.raises(EnvironmentContractError, match="unsupported"):
        load_contract(path)


def test_fingerprint_changes_with_prompt_or_live_schema(tmp_path: Path) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)
    first = build_founder_approval_packet(
        contract=contract,
        contract_path=path,
        live_object_info=_live_object_info(),
    )
    changed_contract = copy.deepcopy(contract)
    changed_contract["request"]["prompt"] += " Extra empty architecture."
    second = build_founder_approval_packet(
        contract=changed_contract,
        contract_path=path,
        live_object_info=_live_object_info(),
    )
    changed_schema = _live_object_info()
    changed_schema["RunwayTextToImageNode"]["description"] = "Updated live schema"
    third = build_founder_approval_packet(
        contract=contract,
        contract_path=path,
        live_object_info=changed_schema,
    )

    assert first["execution_fingerprint"] != second["execution_fingerprint"]
    assert first["execution_fingerprint"] != third["execution_fingerprint"]


def test_merge_gate_transition_requires_refreshed_founder_fingerprint(tmp_path: Path) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)
    contract["execution_blockers"] = []
    first = build_founder_approval_packet(
        contract=contract,
        contract_path=path,
        live_object_info=_live_object_info(),
    )
    contract["post_merge_execution_gate"] = {"required": False, "action": "SATISFIED"}
    second = build_founder_approval_packet(
        contract=contract,
        contract_path=path,
        live_object_info=_live_object_info(),
    )

    assert first["execution_fingerprint"] != second["execution_fingerprint"]
    assert first["contract_sha256"] != second["contract_sha256"]

    assert first["failures"] == second["failures"] == []
    assert second["next_action"] == "STOP_FOR_EXPLICIT_FOUNDER_APPROVAL"
    assert second["paid_submission_performed"] is False


def test_postmerge_approval_packet_keeps_execution_blockers(tmp_path: Path) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)
    contract["post_merge_execution_gate"] = {"required": False, "action": "SATISFIED"}
    contract["execution_blockers"] = ["independent review pending"]
    packet = build_founder_approval_packet(
        contract=contract, contract_path=path, live_object_info=_live_object_info()
    )
    assert "execution-ready contract must have no declared blockers" in packet["failures"]
    assert packet["next_action"] == "REMEDIATE_BLOCKERS_WITHOUT_SUBMISSION"


def test_postmerge_packet_does_not_relax_submission_receipt(tmp_path: Path) -> None:
    contract, path = _portable_contract(CONTRACTS[0], tmp_path)
    contract["post_merge_execution_gate"] = {"required": False, "action": "SATISFIED"}
    contract["execution_blockers"] = []
    failures = validate_contract(contract, contract_path=path, execution_ready=True)
    assert "execution-ready contract requires a bound approval receipt" in failures
