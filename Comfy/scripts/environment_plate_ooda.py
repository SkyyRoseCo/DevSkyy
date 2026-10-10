#!/usr/bin/env python3
"""Fail-closed Runway Gen-4 environment-plate preflight for SkyyRose scenes.

This module deliberately has no paid execution command. It validates the scene
contract and the live Comfy partner-node schema, builds a prompt-only workflow,
and prints the exact founder-approval packet that must exist before another
tool may submit the workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from collections.abc import Mapping
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COMFY_BASE_URL = "http://127.0.0.1:8189"
CONTRACT_SCHEMA = "skyyrose.runway-environment-plate/1"
RUNWAY_NODE = "RunwayTextToImageNode"
RUNWAY_MODEL = "gen-4"
RUNWAY_RATIO = "1920:1080"
MASTER_WIDTH = 2048
MASTER_HEIGHT = 1152
BIREFNET_MODEL_SHA256 = "9ab37426bf4de0567af6b5d21b16151357149139362e6e8992021b8ce356a154"

FORBIDDEN_ENVIRONMENT_SUBJECTS = (
    "people",
    "garments",
    "products",
    "text",
    "wordmarks",
    "signage",
    "hearts",
    "roses",
    "sculptures",
    "monuments",
    "robed figures",
    "Beast characters",
    "ballrooms",
    "flower walls",
)


class EnvironmentContractError(ValueError):
    """Raised when a plate could violate source, content, or spend policy."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_json(value: Any) -> str:
    return _sha256_bytes(_canonical_json(value).encode("utf-8"))


def _contract_sha256(contract: Mapping[str, Any]) -> str:
    """Hash execution inputs and gate state, excluding the approval binding."""
    normalized = json.loads(json.dumps(contract))
    normalized.setdefault("credit_control", {})["approval_receipt"] = None
    # A gate transition requires a refreshed approval for the new authority state.
    return _sha256_json(normalized)


def _resolve_bound_path(_contract_path: Path, raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (PROJECT_ROOT / path).resolve()


def load_contract(path: Path) -> dict[str, Any]:
    contract_path = path.expanduser().resolve()
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EnvironmentContractError(f"invalid environment contract: {exc}") from exc
    if not isinstance(contract, dict) or contract.get("schema") != CONTRACT_SCHEMA:
        raise EnvironmentContractError("unsupported environment contract schema")
    return contract


def validate_contract(
    contract: Mapping[str, Any],
    *,
    contract_path: Path,
    execution_ready: bool = False,
    approval_packet: bool = False,
) -> list[str]:
    """Return every blocking policy failure without weakening later checks."""
    failures: list[str] = []
    provider = contract.get("provider")
    if not isinstance(provider, Mapping):
        failures.append("provider contract is missing")
    elif (
        provider.get("name") != "runway"
        or provider.get("model") != RUNWAY_MODEL
        or provider.get("node") != RUNWAY_NODE
        or provider.get("route") != "comfy_partner_node"
        or provider.get("comfy_base_url") != DEFAULT_COMFY_BASE_URL
    ):
        failures.append("provider must be Runway Gen-4 through local Comfy at 127.0.0.1:8189")

    provider_inputs = contract.get("provider_inputs")
    if not isinstance(provider_inputs, Mapping):
        failures.append("provider_inputs contract is missing")
    else:
        if provider_inputs.get("mode") != "prompt_only":
            failures.append("current environment plate route must be prompt-only")
        if provider_inputs.get("reference_image") is not None:
            failures.append("no image reference may be sent to Runway in the current route")
        if provider_inputs.get("protected_assets_sent") != []:
            failures.append("protected assets sent to Runway must be an explicit empty list")

    request = contract.get("request")
    if not isinstance(request, Mapping):
        failures.append("request contract is missing")
        prompt = ""
    else:
        prompt = request.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            failures.append("environment prompt is missing")
            prompt = ""
        if request.get("ratio") != RUNWAY_RATIO:
            failures.append(f"Runway ratio must be {RUNWAY_RATIO}")
        if request.get("num_outputs") != 1:
            failures.append("environment request must contain exactly one output")
    prompt_casefold = prompt.casefold()
    if "environment only" not in prompt_casefold:
        failures.append("prompt must explicitly say environment only")
    for subject in FORBIDDEN_ENVIRONMENT_SUBJECTS:
        if f"no {subject.casefold()}" not in prompt_casefold:
            failures.append(f"prompt must explicitly forbid {subject}")
    positive_scan = prompt_casefold
    for allowed_zone in (
        "customer zone",
        "monument zone",
        "protected-object zone",
        "protected object zone",
    ):
        positive_scan = positive_scan.replace(allowed_zone, "")
    for subject in FORBIDDEN_ENVIRONMENT_SUBJECTS:
        positive_scan = positive_scan.replace(f"no {subject.casefold()}", "")
    positive_subject_terms = (
        "person",
        "people",
        "model",
        "customer",
        "garment",
        "product",
        "pants",
        "shorts",
        "logo",
        "wordmark",
        "text",
        "signage",
        "heart",
        "rose",
        "sculpture",
        "monument",
        "robed",
        "beast",
        "ballroom",
        "flower wall",
    )
    leaked_terms = sorted({term for term in positive_subject_terms if term in positive_scan})
    if leaked_terms:
        failures.append("prompt positively requests forbidden content: " + ", ".join(leaked_terms))

    declared_forbidden = contract.get("forbidden_plate_content")
    if not isinstance(declared_forbidden, list) or set(declared_forbidden) != set(
        FORBIDDEN_ENVIRONMENT_SUBJECTS
    ):
        failures.append("forbidden_plate_content must exactly match the governed policy")

    postprocess = contract.get("comfy_local_postprocess")
    if not isinstance(postprocess, Mapping):
        failures.append("comfy_local_postprocess is missing")
    else:
        birefnet = postprocess.get("birefnet_evidence")
        if not isinstance(birefnet, Mapping) or (
            birefnet.get("schema") != "skyyrose.birefnet-edge-confidence/1"
            or birefnet.get("model_sha256") != BIREFNET_MODEL_SHA256
            or birefnet.get("role") != "ALPHA_AND_EDGE_CONFIDENCE_ONLY"
            or birefnet.get("generative_use_allowed") is not False
            or birefnet.get("independent_visual_review_required") is not True
        ):
            failures.append("BiRefNet evidence contract is missing or not hash-bound")

    inspirations = contract.get("local_composition_inspiration")
    if not isinstance(inspirations, list) or not inspirations:
        failures.append("at least one local composition inspiration record is required")
    else:
        for index, item in enumerate(inspirations):
            if not isinstance(item, Mapping):
                failures.append(f"composition inspiration {index} is malformed")
                continue
            if item.get("sent_to_runway") is not False:
                failures.append(f"composition inspiration {index} must never be sent to Runway")
            raw_path = item.get("path")
            expected_hash = item.get("sha256")
            if not isinstance(raw_path, str) or not isinstance(expected_hash, str):
                failures.append(f"composition inspiration {index} has no path/hash binding")
                continue
            source = _resolve_bound_path(contract_path, raw_path)
            if not source.is_file():
                failures.append(f"composition inspiration {index} is missing: {source}")
                continue
            if _sha256_bytes(source.read_bytes()) != expected_hash:
                failures.append(f"composition inspiration {index} hash mismatch")
            if item.get("authority_role") != "COMPOSITION_ATMOSPHERE_ONLY":
                failures.append(f"composition inspiration {index} has an invalid authority role")

    credit = contract.get("credit_control")
    if not isinstance(credit, Mapping):
        failures.append("credit_control is missing")
    else:
        if credit.get("max_paid_generations") != 1:
            failures.append("max_paid_generations must equal one")
        if credit.get("paid_generations_recorded") != 0:
            failures.append("paid_generations_recorded must be zero before the candidate")
        if credit.get("automatic_paid_retries") is not False:
            failures.append("automatic paid retries must be disabled")
        approval = credit.get("approval_receipt")
        if execution_ready:
            if not isinstance(approval, Mapping):
                failures.append("execution-ready contract requires a bound approval receipt")
        elif approval is not None:
            failures.append("approval receipt must remain null until explicit founder approval")
        ceiling = credit.get("max_live_price_usd")
        if isinstance(ceiling, bool) or not isinstance(ceiling, (int, float)) or ceiling <= 0:
            failures.append("max_live_price_usd must be a positive number")

    output = contract.get("output")
    if not isinstance(output, Mapping):
        failures.append("output contract is missing")
    else:
        for field in ("candidate_path", "approval_path", "attempt_marker"):
            if not isinstance(output.get(field), str) or not output[field].strip():
                failures.append(f"output.{field} is required")
        for field in ("promotion_allowed", "wiring_allowed", "deployment_allowed"):
            if output.get(field) is not False:
                failures.append(f"output.{field} must be false")

    restart = contract.get("post_merge_execution_gate")
    # Read-only packets may request a fresh approval after the merge gate changes.
    # Submission still requires execution_ready and a bound receipt independently.
    post_merge_packet = (
        approval_packet and isinstance(restart, Mapping) and restart.get("required") is False
    )
    expected_restart = (
        {"required": False, "action": "SATISFIED"}
        if execution_ready or post_merge_packet
        else {"required": True, "action": "REBASE_OR_RESTART_FROM_MERGED_MAIN"}
    )
    if not isinstance(restart, Mapping) or any(
        restart.get(key) != value for key, value in expected_restart.items()
    ):
        failures.append("paid execution merge/restart state is invalid")
    execution_blockers = contract.get("execution_blockers")
    if not isinstance(execution_blockers, list) or not all(
        isinstance(blocker, str) and blocker.strip() for blocker in execution_blockers
    ):
        failures.append("execution_blockers must be a list of non-empty strings")
    elif (execution_ready or post_merge_packet) and execution_blockers:
        failures.append("execution-ready contract must have no declared blockers")
    return failures


def build_prompt_only_workflow(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Build a Runway workflow with no upload or image-reference path."""
    request = contract["request"]
    prefix = contract["output"]["filename_prefix"]
    return {
        "1": {
            "class_type": RUNWAY_NODE,
            "inputs": {"prompt": request["prompt"], "ratio": request["ratio"]},
            "_meta": {"title": f"{contract['scene_id']} product-free environment only"},
        },
        "2": {
            "class_type": "ResizeImageMaskNode",
            "inputs": {
                "input": ["1", 0],
                "resize_type": {
                    "resize_type": "scale dimensions",
                    "width": MASTER_WIDTH,
                    "height": MASTER_HEIGHT,
                    "crop": "disabled",
                },
                "scale_method": "lanczos",
            },
        },
        "3": {
            "class_type": "SaveImage",
            "inputs": {"images": ["2", 0], "filename_prefix": prefix},
        },
    }


def validate_workflow_is_product_free(workflow: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    runway_count = 0
    for node_id, node in workflow.items():
        if not isinstance(node, Mapping):
            failures.append(f"workflow node {node_id} is malformed")
            continue
        class_type = node.get("class_type")
        inputs = node.get("inputs")
        if class_type == "LoadImage":
            failures.append("Runway environment workflow must not contain LoadImage")
        if class_type == RUNWAY_NODE:
            runway_count += 1
            if isinstance(inputs, Mapping) and "reference_image" in inputs:
                failures.append("Runway environment node must not receive reference_image")
        if class_type in {
            "JoinImageWithAlpha",
            "RemoveBackground",
            "ImageCompositeMasked",
            "BriaRemoveImageBackground",
        }:
            failures.append(
                f"protected/composite node {class_type} is forbidden in plate generation"
            )
    if runway_count != 1:
        failures.append("environment workflow must contain exactly one Runway node")
    return failures


def _live_object_info(*, base_url: str = DEFAULT_COMFY_BASE_URL) -> dict[str, Any]:
    if base_url != DEFAULT_COMFY_BASE_URL:
        raise EnvironmentContractError("Comfy base URL must be exactly http://127.0.0.1:8189")
    try:
        with urllib.request.urlopen(f"{base_url}/object_info", timeout=10) as response:
            body = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise EnvironmentContractError(f"Comfy node inventory unavailable: {exc}") from exc
    node = body.get(RUNWAY_NODE) if isinstance(body, dict) else None
    if not isinstance(node, dict):
        raise EnvironmentContractError(f"{RUNWAY_NODE} is not installed")
    return body


def _live_price(node_schema: Mapping[str, Any]) -> float:
    badge = node_schema.get("price_badge")
    expression = badge.get("expr") if isinstance(badge, Mapping) else None
    try:
        price = json.loads(expression)["usd"] if isinstance(expression, str) else None
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise EnvironmentContractError("Runway partner node price is not parseable") from exc
    if isinstance(price, bool) or not isinstance(price, (int, float)) or price <= 0:
        raise EnvironmentContractError("Runway partner node has no positive USD price")
    return float(price)


def _validate_live_runway_schema(node_schema: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    inputs = node_schema.get("input")
    required = inputs.get("required") if isinstance(inputs, Mapping) else None
    if not isinstance(required, Mapping) or not {"prompt", "ratio"}.issubset(required):
        failures.append("live Runway node must require prompt and ratio inputs")
    description = " ".join(
        str(node_schema.get(field, ""))
        for field in ("name", "display_name", "description", "python_module")
    ).casefold()
    if "runway" not in description or ("gen 4" not in description and "gen-4" not in description):
        failures.append("live partner-node schema does not identify Runway Gen-4")
    if node_schema.get("api_node") is not True:
        failures.append("live Runway node is not declared as a partner API node")
    return failures


def build_founder_approval_packet(
    *,
    contract: Mapping[str, Any],
    contract_path: Path,
    live_object_info: Mapping[str, Any],
) -> dict[str, Any]:
    """Create the exact read-only packet shown before any paid submission."""
    failures = validate_contract(contract, contract_path=contract_path, approval_packet=True)
    declared_blockers = (
        list(contract.get("execution_blockers", []))
        if isinstance(contract.get("execution_blockers"), list)
        else []
    )
    try:
        workflow = build_prompt_only_workflow(contract)
    except (KeyError, TypeError) as exc:
        workflow = {}
        failures.append(f"prompt-only workflow cannot be built: {exc}")
    failures.extend(validate_workflow_is_product_free(workflow))
    live_node_schema = live_object_info.get(RUNWAY_NODE)
    if not isinstance(live_node_schema, Mapping):
        raise EnvironmentContractError(f"{RUNWAY_NODE} is not installed")
    failures.extend(_validate_live_runway_schema(live_node_schema))
    live_price = _live_price(live_node_schema)
    credit = contract.get("credit_control")
    ceiling = credit.get("max_live_price_usd") if isinstance(credit, Mapping) else None
    if isinstance(ceiling, (int, float)) and not isinstance(ceiling, bool) and live_price > ceiling:
        failures.append(
            f"live Runway price ${live_price:.2f} exceeds ${float(ceiling):.2f} ceiling"
        )
    workflow_hash = _sha256_json(workflow)
    contract_hash = _contract_sha256(contract)
    used_classes = {
        str(node.get("class_type"))
        for node in workflow.values()
        if isinstance(node, Mapping) and isinstance(node.get("class_type"), str)
    }
    missing_classes = sorted(used_classes - set(live_object_info))
    if missing_classes:
        failures.append(f"live Comfy node inventory is incomplete: {missing_classes}")
    used_schemas = {
        name: live_object_info[name] for name in sorted(used_classes) if name in live_object_info
    }
    live_schema_hash = _sha256_json(used_schemas)
    output = contract.get("output")
    output = output if isinstance(output, Mapping) else {}
    request = contract.get("request")
    request = request if isinstance(request, Mapping) else {}
    prompt = request.get("prompt") if isinstance(request.get("prompt"), str) else ""
    fingerprint_material = {
        "schema": "skyyrose.runway-environment-execution-fingerprint/1",
        "scene_id": contract.get("scene_id"),
        "candidate_id": contract.get("candidate_id"),
        "contract_sha256": contract_hash,
        "workflow_sha256": workflow_hash,
        "prompt_sha256": _sha256_bytes(prompt.encode("utf-8")),
        "live_node_schema_sha256": live_schema_hash,
        "live_price_usd": live_price,
        "approval_path": output.get("approval_path"),
        "attempt_marker": output.get("attempt_marker"),
        "max_paid_generations": 1,
    }
    return {
        "schema": "skyyrose.runway-environment-founder-packet/1",
        "status": (
            "BLOCKED"
            if failures or declared_blockers
            else "BLOCKED_PENDING_EXPLICIT_FOUNDER_APPROVAL"
        ),
        "scene_id": contract.get("scene_id"),
        "candidate_id": contract.get("candidate_id"),
        "execution_fingerprint": _sha256_json(fingerprint_material),
        "fingerprint_material": fingerprint_material,
        "prompt": prompt,
        "live_partner_node": {
            "class_type": RUNWAY_NODE,
            "model": RUNWAY_MODEL,
            "price_usd": live_price,
            "schema_sha256": live_schema_hash,
        },
        "one_candidate_ceiling": {
            "max_paid_generations": 1,
            "max_price_usd": ceiling,
            "automatic_paid_retries": False,
        },
        "candidate_bound_approval_path": output.get("approval_path"),
        "attempt_marker": output.get("attempt_marker"),
        "workflow": workflow,
        "workflow_sha256": workflow_hash,
        "contract_sha256": contract_hash,
        "protected_assets_sent_to_runway": [],
        "paid_submission_performed": False,
        "failures": failures,
        "declared_execution_blockers": declared_blockers,
        "next_action": (
            "REMEDIATE_BLOCKERS_WITHOUT_SUBMISSION"
            if failures or declared_blockers
            else "STOP_FOR_EXPLICIT_FOUNDER_APPROVAL"
        ),
        "post_merge_execution_gate": contract.get("post_merge_execution_gate"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("preflight", nargs="?")
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--base-url", default=DEFAULT_COMFY_BASE_URL)
    args = parser.parse_args()
    if args.preflight not in {None, "preflight"}:
        parser.error("only the read-only preflight action is supported")
    try:
        contract = load_contract(args.contract)
        packet = build_founder_approval_packet(
            contract=contract,
            contract_path=args.contract,
            live_object_info=_live_object_info(base_url=args.base_url),
        )
    except EnvironmentContractError as exc:
        packet = {
            "schema": "skyyrose.runway-environment-founder-packet/1",
            "status": "BLOCKED",
            "paid_submission_performed": False,
            "failures": [str(exc)],
            "next_action": "REMEDIATE_BLOCKERS_WITHOUT_SUBMISSION",
        }
    print(json.dumps(packet, indent=2))
    return 0 if packet.get("status") == "BLOCKED_PENDING_EXPLICIT_FOUNDER_APPROVAL" else 2


if __name__ == "__main__":
    sys.exit(main())
