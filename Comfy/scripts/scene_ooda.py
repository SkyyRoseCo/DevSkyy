#!/usr/bin/env python3
"""Fail-closed Higgsfield -> Comfy OODA runner for SkyyRose scene candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMFY_ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_json_file(path: Path) -> str:
    """Hash parsed JSON canonically so formatting changes do not invalidate execution."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def execution_fingerprint(manifest: dict[str, Any]) -> str:
    """Hash the executable contract without the receipt path that authorizes it."""
    normalized = json.loads(json.dumps(manifest))
    normalized.setdefault("credit_control", {})["approval_receipt"] = None
    return sha256_text(json.dumps(normalized, sort_keys=True, separators=(",", ":")))


def resolve_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "skyyrose.scene-ooda/1":
        raise ValueError("unsupported or missing scene OODA schema")
    for key in ("scene_id", "source_bindings", "provider_capability", "execute_blockers"):
        if key not in data:
            raise ValueError(f"manifest missing required key: {key}")
    return data


def verify_file(path: Path, expected_sha256: str | None) -> dict[str, Any]:
    result: dict[str, Any] = {"path": str(path), "exists": path.is_file()}
    if not result["exists"]:
        result["status"] = "MISSING"
        return result
    actual = sha256_file(path)
    result["actual_sha256"] = actual
    if expected_sha256:
        result["expected_sha256"] = expected_sha256
        result["status"] = "PASS" if actual == expected_sha256 else "HASH_MISMATCH"
    else:
        result["status"] = "PRESENT_UNHASHED"
    return result


def verify_native_workflow_dependencies(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Verify every executable native-scene dependency by immutable content hash."""
    native = manifest.get("native_scene_workflow")
    if not isinstance(native, dict):
        return []

    dependency_fields = (
        ("segmentation", "workflow", "workflow_sha256"),
        ("segmentation", "coverage_authority", "sha256"),
        ("background", "workflow", "workflow_sha256"),
        ("background", "approval_contract", "approval_contract_sha256"),
        ("composite", "workflow_builder", "workflow_builder_sha256"),
    )
    results: list[dict[str, Any]] = []
    for section_name, path_key, hash_key in dependency_fields:
        section = native.get(section_name)
        binding = section.get(path_key) if isinstance(section, dict) else None
        if isinstance(binding, dict):
            path_value = binding.get("path")
            expected_sha256 = binding.get(hash_key)
        else:
            path_value = binding
            expected_sha256 = section.get(hash_key) if isinstance(section, dict) else None
        if not isinstance(path_value, str) or not path_value.strip():
            results.append(
                {
                    "section": section_name,
                    "field": path_key,
                    "status": "MISSING_DEPENDENCY_PATH",
                }
            )
            continue
        if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
            results.append(
                {
                    "section": section_name,
                    "field": hash_key,
                    "path": str(resolve_path(path_value)),
                    "status": "MISSING_DEPENDENCY_HASH",
                }
            )
            continue
        dependency_path = resolve_path(path_value)
        if path_key == "workflow" and dependency_path.is_file():
            actual_sha256 = sha256_json_file(dependency_path)
            result = {
                "path": str(dependency_path),
                "exists": True,
                "actual_sha256": actual_sha256,
                "expected_sha256": expected_sha256,
                "hash_mode": "canonical_json",
                "status": "PASS" if actual_sha256 == expected_sha256 else "HASH_MISMATCH",
            }
        else:
            result = verify_file(dependency_path, expected_sha256)
        result["section"] = section_name
        result["field"] = path_key
        results.append(result)
    segmentation = native.get("segmentation")
    rgb_verification_ok = (
        isinstance(segmentation, dict)
        and segmentation.get("verification_schema") == "skyyrose.protected-rgb-verification/1"
        and segmentation.get("verification_required_before_composite") is True
    )
    results.append(
        {
            "section": "segmentation",
            "field": "protected_rgb_verification",
            "status": "PASS" if rgb_verification_ok else "MISSING_PROTECTED_RGB_VERIFICATION",
        }
    )
    return results


def verify_team_contract(manifest: dict[str, Any]) -> dict[str, Any]:
    team = manifest.get("fashion_theme_team", {})
    contract_path = resolve_path(team.get("team_contract", ""))
    result: dict[str, Any] = {
        "path": str(contract_path),
        "plugin": team.get("plugin"),
        "phase_id": team.get("phase_id"),
        "current_owner": team.get("current_owner"),
    }
    if not contract_path.is_file():
        result["status"] = "MISSING_TEAM_CONTRACT"
        return result
    index = json.loads(contract_path.read_text(encoding="utf-8"))
    indexed_scenes = {scene.get("scene_id") for scene in index.get("scenes", [])}
    required_roles = {
        "catalog-sot-integrator",
        "brand-experience-architect",
        "visual-commerce-qa",
        "theme-release-engineer",
    }
    serialized_ownership = json.dumps(index.get("phase_ownership", {}))
    missing_roles = sorted(role for role in required_roles if role not in serialized_ownership)
    failures = []
    if index.get("schema") != "skyyrose.scene-ooda-team-index/1":
        failures.append("invalid team-index schema")
    if team.get("plugin") != "fashion-theme-team@personal":
        failures.append("wrong or missing Fashion Theme Team plugin")
    if manifest["scene_id"] not in indexed_scenes:
        failures.append("scene missing from team index")
    if not team.get("phase_id") or not team.get("accountable") or not team.get("next_authority"):
        failures.append("incomplete durable phase assignment")
    if missing_roles:
        failures.append(f"team index missing required roles: {', '.join(missing_roles)}")
    result["failures"] = failures
    result["status"] = "PASS" if not failures else "INVALID_TEAM_CONTRACT"
    return result


def verify_creative_direction(manifest: dict[str, Any]) -> dict[str, Any]:
    direction = manifest.get("creative_direction")
    failures: list[str] = []
    if not isinstance(direction, dict):
        return {"status": "MISSING_CREATIVE_DIRECTION", "failures": ["missing creative_direction"]}
    if direction.get("style") != "cinematic_urban_grit":
        failures.append("style must be cinematic_urban_grit")
    for key in ("story_role", "logo_off_recognition"):
        if not isinstance(direction.get(key), str) or not direction[key].strip():
            failures.append(f"{key} must be a non-empty string")
    for key, minimum in (("focal_hierarchy", 3), ("material_language", 3), ("anti_generic", 3)):
        value = direction.get(key)
        if not isinstance(value, list) or len(value) < minimum:
            failures.append(f"{key} must contain at least {minimum} entries")
    return {
        "status": "PASS" if not failures else "INVALID_CREATIVE_DIRECTION",
        "failures": failures,
    }


def verify_optical_contract(manifest: dict[str, Any]) -> dict[str, Any]:
    optical = manifest.get("optical_contract")
    failures: list[str] = []
    if not isinstance(optical, dict):
        return {"status": "MISSING_OPTICAL_CONTRACT", "failures": ["missing optical_contract"]}

    output = optical.get("output", {})
    width = output.get("width") if isinstance(output, dict) else None
    height = output.get("height") if isinstance(output, dict) else None
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        failures.append("output width and height must be positive integers")
        width = height = 0

    horizon_y = optical.get("horizon_y")
    if not isinstance(horizon_y, int) or horizon_y < 0 or (height and horizon_y > height):
        failures.append("horizon_y must be inside the output geometry")

    subject_boxes = optical.get("subject_boxes")
    if not isinstance(subject_boxes, list) or not subject_boxes:
        failures.append("subject_boxes must contain at least one measured box")
    else:
        for index, box in enumerate(subject_boxes):
            if not isinstance(box, dict):
                failures.append(f"subject_boxes[{index}] must be an object")
                continue
            x, y, box_width, box_height = (box.get(key) for key in ("x", "y", "width", "height"))
            if not all(isinstance(value, int) for value in (x, y, box_width, box_height)):
                failures.append(f"subject_boxes[{index}] geometry must use integers")
                continue
            if x < 0 or y < 0 or box_width <= 0 or box_height <= 0:
                failures.append(f"subject_boxes[{index}] has invalid geometry")
            if width and height and (x + box_width > width or y + box_height > height):
                failures.append(f"subject_boxes[{index}] exceeds output geometry")

    contact_points = optical.get("contact_points")
    if not isinstance(contact_points, list) or not contact_points:
        failures.append("contact_points must contain at least one measured point")
    else:
        for index, point in enumerate(contact_points):
            if not isinstance(point, dict):
                failures.append(f"contact_points[{index}] must be an object")
                continue
            x, y = point.get("x"), point.get("y")
            if not isinstance(x, int) or not isinstance(y, int):
                failures.append(f"contact_points[{index}] coordinates must be integers")
            elif x < 0 or y < 0 or (width and x > width) or (height and y > height):
                failures.append(f"contact_points[{index}] exceeds output geometry")

    if optical.get("lens_class") not in {"wide", "normal", "telephoto"}:
        failures.append("lens_class must be wide, normal, or telephoto")
    if optical.get("camera_height") not in {"low", "eye_level", "high"}:
        failures.append("camera_height must be low, eye_level, or high")
    if optical.get("floor_response") not in {"dry_matte", "damp_satin", "wet_reflective"}:
        failures.append("floor_response must be dry_matte, damp_satin, or wet_reflective")
    if optical.get("reflection_mode") not in {"none", "subtle", "controlled"}:
        failures.append("reflection_mode must be none, subtle, or controlled")
    for key in ("key_light", "shadow_behavior"):
        if not isinstance(optical.get(key), dict) or not optical[key]:
            failures.append(f"{key} must be a non-empty object")
    requirements = optical.get("requirements")
    required_flags = ("contact", "occlusion", "depth", "grain_match", "edge_spill_match")
    if not isinstance(requirements, dict) or any(
        requirements.get(flag) is not True for flag in required_flags
    ):
        failures.append("all native-integration requirements must be true")

    return {
        "status": "PASS" if not failures else "INVALID_OPTICAL_CONTRACT",
        "failures": failures,
    }


def verify_prompt_adherence(manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate a fail-closed preflight and post-capture adherence contract."""
    if "prompt_adherence" not in manifest:
        return {"status": "PASS", "configured": False, "failures": []}
    adherence = manifest["prompt_adherence"]

    failures: list[str] = []
    if not isinstance(adherence, dict):
        return {
            "status": "INVALID_PROMPT_ADHERENCE",
            "configured": True,
            "failures": ["prompt_adherence must be an object"],
        }
    if adherence.get("mode") != "FAIL_CLOSED":
        failures.append("prompt_adherence mode must be FAIL_CLOSED")
    if (
        not isinstance(adherence.get("independent_reviewer_role"), str)
        or not adherence["independent_reviewer_role"].strip()
    ):
        failures.append("independent_reviewer_role must be a non-empty string")

    preflight = adherence.get("preflight")
    if not isinstance(preflight, dict):
        failures.append("preflight must be an object")
    else:
        required_roles = preflight.get("required_source_roles")
        if (
            not isinstance(required_roles, list)
            or not required_roles
            or not all(isinstance(role, str) and role.strip() for role in required_roles)
        ):
            failures.append("required_source_roles must contain non-empty strings")
        else:
            allowed_provider_uses = {
                "SOURCE_AUTHORITY_ONLY",
                "FASHN_PRIMARY_PRODUCT_INPUT",
                "FASHN_PRIMARY_PRODUCT_INPUT_AFTER_SEPARATE_APPROVAL",
                "RUNWAY_ENVIRONMENT_REFERENCE_ONLY",
                "COMFY_PROTECTED_COMPOSITE_ONLY",
                "LOCAL_CORRECTION_COMPOSITION_AUTHORITY_ONLY",
                "LOCAL_CORRECTION_ENVIRONMENT_AUTHORITY_ONLY",
                "COMFY_PROTECTED_CORRECTION_INPUT",
            }
            valid_provider_roles: list[str] = []
            for binding in manifest.get("source_bindings", []):
                if not isinstance(binding, dict) or "provider_use" not in binding:
                    continue
                role = binding.get("role")
                provider_use = binding.get("provider_use")
                if not isinstance(role, str) or not role.strip():
                    failures.append("provider-routed source binding requires a non-empty role")
                    continue
                if not isinstance(provider_use, str) or provider_use not in allowed_provider_uses:
                    failures.append(f"invalid provider_use for source role: {role}")
                    continue
                role_tokens = set(filter(None, re.split(r"[^a-z0-9]+", role.casefold())))
                if provider_use == "RUNWAY_ENVIRONMENT_REFERENCE_ONLY":
                    forbidden_runway_tokens = {
                        "customer",
                        "product",
                        "garment",
                        "identity",
                        "sculpture",
                        "monument",
                        "cast",
                        "look",
                    }
                    if not role_tokens.intersection(
                        {"world", "environment"}
                    ) or role_tokens.intersection(forbidden_runway_tokens):
                        failures.append(
                            f"Runway may receive only a world/environment source: {role}"
                        )
                        continue
                if provider_use.startswith("FASHN_") and "product" not in role_tokens:
                    failures.append(f"FASHN may receive only an explicit product source: {role}")
                    continue
                valid_provider_roles.append(role)
            routed_roles = [
                binding.get("role")
                for binding in manifest.get("source_bindings", [])
                if isinstance(binding, dict) and binding.get("send_to_higgsfield") is True
            ]
            routed_roles.extend(valid_provider_roles)
            missing_roles = sorted(set(required_roles) - set(routed_roles))
            if missing_roles:
                failures.append(f"missing routed source roles: {', '.join(missing_roles)}")
            duplicate_roles = sorted(
                role for role in set(required_roles) if routed_roles.count(role) != 1
            )
            if duplicate_roles:
                failures.append(
                    "required source roles must be routed exactly once: "
                    + ", ".join(duplicate_roles)
                )

        required_claims = preflight.get("required_prompt_claims")
        if (
            not isinstance(required_claims, list)
            or not required_claims
            or not all(isinstance(claim, str) and claim.strip() for claim in required_claims)
        ):
            failures.append("required_prompt_claims must contain non-empty strings")
        else:
            if isinstance(manifest.get("native_scene_workflow"), dict):
                native = manifest["native_scene_workflow"]
                background = native.get("background", {})
                prompt_packet = " ".join(
                    str(value)
                    for value in (
                        background.get("prompt", "") if isinstance(background, dict) else "",
                        native.get("foreground", ""),
                    )
                ).casefold()
            else:
                prompt_packet = " ".join(
                    str(manifest.get("higgsfield", {}).get(key, ""))
                    for key in ("prompt", "brand_context", "product_context")
                ).casefold()
            missing_claims = [
                claim for claim in required_claims if claim.casefold() not in prompt_packet
            ]
            if missing_claims:
                failures.append(f"missing required prompt claims: {', '.join(missing_claims)}")

    post_capture = adherence.get("post_capture")
    if not isinstance(post_capture, dict):
        failures.append("post_capture must be an object")
    else:
        minimum_score = post_capture.get("minimum_total_score")
        if (
            not isinstance(minimum_score, int)
            or isinstance(minimum_score, bool)
            or not 90 <= minimum_score <= 100
        ):
            failures.append("minimum_total_score must be an integer from 90 to 100")
        dimensions = post_capture.get("dimensions")
        if not isinstance(dimensions, list) or not dimensions:
            failures.append("post_capture dimensions must be a non-empty list")
        else:
            total_weight = 0
            dimension_ids: list[str] = []
            for index, dimension in enumerate(dimensions):
                if not isinstance(dimension, dict):
                    failures.append(f"dimensions[{index}] must be an object")
                    continue
                dimension_id = dimension.get("id")
                weight = dimension.get("weight")
                if not isinstance(dimension_id, str) or not dimension_id.strip():
                    failures.append(f"dimensions[{index}].id must be a non-empty string")
                else:
                    dimension_ids.append(dimension_id)
                if not isinstance(weight, (int, float)) or isinstance(weight, bool) or weight <= 0:
                    failures.append(f"dimensions[{index}].weight must be positive")
                else:
                    total_weight += weight
            if len(dimension_ids) != len(set(dimension_ids)):
                failures.append("post_capture dimension ids must be unique")
            if total_weight != 100:
                failures.append("post_capture dimension weights must total 100")

    hard_fail_invariants = adherence.get("hard_fail_invariants")
    if (
        not isinstance(hard_fail_invariants, list)
        or not hard_fail_invariants
        or not all(
            isinstance(invariant, str) and invariant.strip() for invariant in hard_fail_invariants
        )
    ):
        failures.append("hard_fail_invariants must contain non-empty strings")
    if adherence.get("disposition_on_failure") != "QUARANTINE_NO_AUTOMATIC_RETRY":
        failures.append("disposition_on_failure must be QUARANTINE_NO_AUTOMATIC_RETRY")

    return {
        "status": "PASS" if not failures else "INVALID_PROMPT_ADHERENCE",
        "configured": True,
        "failures": failures,
    }


def verify_prompt_adherence_review(
    manifest: dict[str, Any], candidate: Path, review_path: Path | None
) -> dict[str, Any]:
    """Verify an independent, candidate-bound post-capture adherence scorecard."""
    contract_check = verify_prompt_adherence(manifest)
    candidate_check = verify_file(candidate, None)
    result: dict[str, Any] = {
        "status": "INVALID_PROMPT_ADHERENCE_REVIEW",
        "contract_check": contract_check,
        "candidate_check": candidate_check,
        "failures": [],
    }
    if contract_check["status"] != "PASS":
        result["failures"].append("prompt adherence contract is invalid")
        return result
    if not contract_check["configured"]:
        return {
            **result,
            "status": "PASS",
            "configured": False,
            "failures": [],
        }
    result["configured"] = True
    if candidate_check["status"] != "PRESENT_UNHASHED":
        result["failures"].append("candidate is missing")
        return result
    quarantine_path = prompt_adherence_quarantine_path(
        manifest["scene_id"], candidate_check["actual_sha256"]
    )
    if quarantine_path.is_file():
        result["status"] = "CANDIDATE_HASH_QUARANTINED"
        result["quarantine_marker"] = str(quarantine_path)
        try:
            result["quarantine_record"] = json.loads(quarantine_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            result["failures"].append(f"quarantine marker cannot be parsed: {exc}")
        return result
    if review_path is None:
        result["failures"].append("candidate-bound prompt adherence review is required")
        return result

    review_path = review_path.expanduser().resolve()
    result["review_path"] = str(review_path)
    review_check = verify_file(review_path, None)
    result["review_receipt_check"] = review_check
    if review_check["status"] != "PRESENT_UNHASHED":
        result["failures"].append("review receipt is missing")
        return result
    try:
        review = json.loads(review_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result["failures"].append(f"review receipt cannot be parsed: {exc}")
        return result
    if not isinstance(review, dict):
        result["failures"].append("review receipt must be an object")
        return result

    adherence = manifest["prompt_adherence"]
    failures: list[str] = result["failures"]
    if review.get("schema") != "skyyrose.prompt-adherence-review/1":
        failures.append("invalid prompt adherence review schema")
    if review.get("scene_id") != manifest.get("scene_id"):
        failures.append("review scene does not match manifest")
    if review.get("candidate_sha256") != candidate_check.get("actual_sha256"):
        failures.append("review is not bound to the current candidate hash")
    if review.get("manifest_fingerprint") != execution_fingerprint(manifest):
        failures.append("review is stale for the current executable manifest")

    reviewer = review.get("reviewer")
    if not isinstance(reviewer, dict):
        failures.append("reviewer must be an object")
    else:
        if reviewer.get("role") != adherence["independent_reviewer_role"]:
            failures.append("reviewer role does not match the independent review contract")
        if reviewer.get("independent") is not True:
            failures.append("reviewer must attest independent=true")
        if not isinstance(reviewer.get("id"), str) or not reviewer["id"].strip():
            failures.append("reviewer id must be a non-empty string")
        else:
            reviewer_id = reviewer["id"].strip().casefold()
            accountable = (
                str(manifest.get("fashion_theme_team", {}).get("accountable", ""))
                .strip()
                .casefold()
            )
            if reviewer_id == accountable:
                failures.append("reviewer must be independent from the accountable manager")

    dimensions = adherence["post_capture"]["dimensions"]
    expected_scores = {dimension["id"]: dimension["weight"] for dimension in dimensions}
    scores = review.get("scores")
    weighted_total = 0.0
    if not isinstance(scores, dict):
        failures.append("scores must be an object")
    else:
        missing_scores = sorted(set(expected_scores) - set(scores))
        extra_scores = sorted(set(scores) - set(expected_scores))
        if missing_scores:
            failures.append(f"missing dimension scores: {', '.join(missing_scores)}")
        if extra_scores:
            failures.append(f"unexpected dimension scores: {', '.join(extra_scores)}")
        for dimension_id, weight in expected_scores.items():
            score = scores.get(dimension_id)
            if (
                not isinstance(score, (int, float))
                or isinstance(score, bool)
                or not 0 <= score <= 100
            ):
                failures.append(f"score for {dimension_id} must be between 0 and 100")
            else:
                weighted_total += score * weight / 100

    expected_invariants = adherence["hard_fail_invariants"]
    hard_fail_results = review.get("hard_fail_results")
    hard_failures: list[str] = []
    if not isinstance(hard_fail_results, list):
        failures.append("hard_fail_results must be a list")
    else:
        observed: dict[str, dict[str, Any]] = {}
        for index, item in enumerate(hard_fail_results):
            if not isinstance(item, dict) or not isinstance(item.get("invariant"), str):
                failures.append(f"hard_fail_results[{index}] must name an invariant")
                continue
            invariant = item["invariant"]
            if invariant in observed:
                failures.append(f"duplicate hard-fail result: {invariant}")
                continue
            observed[invariant] = item
        missing_invariants = [item for item in expected_invariants if item not in observed]
        extra_invariants = [item for item in observed if item not in expected_invariants]
        if missing_invariants:
            failures.append(f"missing hard-fail results: {', '.join(missing_invariants)}")
        if extra_invariants:
            failures.append(f"unexpected hard-fail results: {', '.join(extra_invariants)}")
        for invariant in expected_invariants:
            item = observed.get(invariant)
            if item is None:
                continue
            if not isinstance(item.get("failed"), bool):
                failures.append(f"hard-fail result must use a boolean: {invariant}")
            elif item["failed"]:
                hard_failures.append(invariant)
            if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
                failures.append(f"hard-fail result requires evidence: {invariant}")

    result["weighted_total"] = round(weighted_total, 2)
    result["minimum_total_score"] = adherence["post_capture"]["minimum_total_score"]
    result["hard_failures"] = hard_failures
    if failures:
        return result
    if hard_failures:
        result["status"] = "HARD_FAIL_QUARANTINED"
    elif weighted_total < adherence["post_capture"]["minimum_total_score"]:
        result["status"] = "BELOW_THRESHOLD_QUARANTINED"
    else:
        result["status"] = "PASS"
    return result


def prompt_adherence_quarantine_path(scene_id: str, candidate_sha256: str) -> Path:
    """Return the immutable quarantine marker path for a candidate hash."""
    safe_scene_id = "".join(
        character if character.isalnum() or character in {"-", "_"} else "-"
        for character in scene_id.casefold()
    )
    return (
        COMFY_ROOT / "quarantine" / "prompt-adherence" / safe_scene_id / f"{candidate_sha256}.json"
    )


def persist_prompt_adherence_quarantine(manifest: dict[str, Any], review: dict[str, Any]) -> Path:
    """Persist the first hard-fail/below-threshold disposition without overwrite."""
    candidate_sha256 = review.get("candidate_check", {}).get("actual_sha256")
    if not isinstance(candidate_sha256, str) or not candidate_sha256:
        raise ValueError("cannot quarantine a candidate without a SHA-256")
    marker = prompt_adherence_quarantine_path(manifest["scene_id"], candidate_sha256)
    marker.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "schema": "skyyrose.prompt-adherence-quarantine/1",
        "scene_id": manifest["scene_id"],
        "candidate_sha256": candidate_sha256,
        "manifest_fingerprint": execution_fingerprint(manifest),
        "recorded_at": datetime.now(UTC).isoformat(),
        "disposition": review["status"],
        "weighted_total": review.get("weighted_total"),
        "minimum_total_score": review.get("minimum_total_score"),
        "hard_failures": review.get("hard_failures", []),
        "review_path": review.get("review_path"),
        "review_sha256": review.get("review_receipt_check", {}).get("actual_sha256"),
        "immutable": True,
        "automatic_retry": False,
    }
    try:
        with marker.open("x", encoding="utf-8") as handle:
            json.dump(document, handle, indent=2)
            handle.write("\n")
    except FileExistsError:
        pass
    return marker


def verify_comfy_contract(manifest: dict[str, Any]) -> dict[str, Any]:
    comfy = manifest.get("comfy")
    failures: list[str] = []
    if not isinstance(comfy, dict):
        return {"status": "MISSING_COMFY_CONTRACT", "failures": ["comfy contract must not be null"]}
    if comfy.get("routing") != "local" or comfy.get("server") != "http://127.0.0.1:8189":
        failures.append("Comfy must route only to the observed local Desktop API at 8189")
    if comfy.get("role") not in {
        "POST_CAPTURE_PROTECTED_CORRECTION_ONLY",
        "PROTECTED_SEGMENTATION_AND_NATIVE_COMPOSITION",
    }:
        failures.append("Comfy role must remain protected-correction or native-composition only")
    for key in ("allowed_operations", "forbidden_operations"):
        if not isinstance(comfy.get(key), list) or not comfy[key]:
            failures.append(f"{key} must be a non-empty list")
    for key in (
        "requires_candidate_hash",
        "requires_mask_for_product_pixels",
        "requires_independent_review",
    ):
        if comfy.get(key) is not True:
            failures.append(f"{key} must be true")
    return {
        "status": "PASS" if not failures else "INVALID_COMFY_CONTRACT",
        "failures": failures,
    }


def verify_provider_capability(manifest: dict[str, Any]) -> dict[str, Any]:
    capability = manifest.get("provider_capability")
    failures: list[str] = []
    if not isinstance(capability, dict):
        return {
            "status": "MISSING_PROVIDER_CAPABILITY",
            "failures": ["missing provider_capability"],
        }
    route_contract = manifest.get("route_contract")
    native_workflow = manifest.get("native_scene_workflow")
    if isinstance(route_contract, dict) and capability.get("higgsfield_role") != (
        "REFERENCE_GENERATION_CANDIDATE_ONLY"
    ):
        route_mode = route_contract.get("mode")
        if not isinstance(route_mode, str) or not route_mode.strip() or not capability.get("rule"):
            return {
                "status": "INVALID_PROVIDER_CAPABILITY",
                "failures": ["routed provider capability requires a mode and fail-closed rule"],
            }
        return {
            "status": "PASS",
            "failures": [],
            "model": None,
            "operation": route_mode,
            "provider_route": "EVIDENCE_SELECTED",
        }
    if isinstance(native_workflow, dict):
        required_roles = ("fashn_role", "runway_role", "comfy_role")
        missing_roles = [role for role in required_roles if not capability.get(role)]
        if missing_roles or native_workflow.get("mode") != "environment_rebuild_around_source":
            return {
                "status": "INVALID_PROVIDER_CAPABILITY",
                "failures": ["native provider route is incomplete: " + ", ".join(missing_roles)],
            }
        return {
            "status": "PASS",
            "failures": [],
            "model": None,
            "operation": native_workflow["mode"],
            "provider_route": "FASHN_RUNWAY_COMFY_PROTECTED",
        }
    required = (
        "registry_path",
        "registry_sha256",
        "runtime_receipt",
        "runtime_receipt_sha256",
        "model_id",
        "operation",
    )
    missing = [key for key in required if not capability.get(key)]
    if missing:
        return {
            "status": "MISSING_RUNTIME_CAPABILITY",
            "failures": [f"missing provider capability fields: {', '.join(missing)}"],
        }

    registry_check = verify_file(
        resolve_path(capability["registry_path"]), capability["registry_sha256"]
    )
    receipt_check = verify_file(
        resolve_path(capability["runtime_receipt"]),
        capability["runtime_receipt_sha256"],
    )
    if registry_check["status"] != "PASS":
        failures.append("provider registry file or hash is invalid")
    if receipt_check["status"] != "PASS":
        failures.append("runtime capability receipt file or hash is invalid")

    model: dict[str, Any] | None = None
    if not failures:
        try:
            registry = json.loads(
                resolve_path(capability["registry_path"]).read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"provider registry cannot be parsed: {exc}")
        else:
            if registry.get("schema") != "product-fidelity-model-registry.v2":
                failures.append("unsupported provider registry schema")
            for candidate in registry.get("models", []):
                identifiers = [candidate.get("id"), *candidate.get("aliases", [])]
                if capability["model_id"].casefold() in {
                    identifier.casefold()
                    for identifier in identifiers
                    if isinstance(identifier, str)
                }:
                    model = candidate
                    break
            if model is None:
                failures.append("provider model is absent from the bound registry")
            elif capability["operation"] not in model.get("allowed_operations", []):
                failures.append("provider operation is not allowed for the bound model")
            elif model.get("fidelity_tier") != "candidate_only":
                failures.append("Higgsfield scene generation must remain candidate_only")
    return {
        "status": "PASS" if not failures else "INVALID_PROVIDER_CAPABILITY",
        "failures": failures,
        "registry_check": registry_check,
        "runtime_receipt_check": receipt_check,
        "model": model.get("id") if model else None,
        "operation": capability.get("operation"),
    }


def verify_authorization_receipt(
    manifest: dict[str, Any], raw_path: str | None, expected_action: str
) -> dict[str, Any]:
    if not raw_path:
        return {"status": "MISSING_RECEIPT", "expected_action": expected_action}
    path = resolve_path(raw_path)
    if not path.is_file():
        return {
            "status": "MISSING_RECEIPT_FILE",
            "path": str(path),
            "expected_action": expected_action,
        }
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "INVALID_RECEIPT", "path": str(path), "error": str(exc)}
    failures: list[str] = []
    if receipt.get("schema") != "skyyrose.scene-ooda-receipt/1":
        failures.append("invalid receipt schema")
    if receipt.get("scene_id") != manifest.get("scene_id"):
        failures.append("receipt scene does not match manifest")
    if receipt.get("action") != expected_action:
        failures.append("receipt action does not match required action")
    payload = receipt.get("payload", {})
    if expected_action in {
        "higgsfield-enhance-review",
        "runway-background-prompt-review",
    }:
        if payload.get("inspection", {}).get("status") != "PASS":
            failures.append("enhanced prompt review did not pass")
        if payload.get("generation_submitted") is not False:
            failures.append("prompt-review receipt must record generation_submitted=false")
        expected_prompt_sha256 = manifest.get("credit_control", {}).get("prompt_sha256")
        if expected_prompt_sha256 and payload.get("prompt_sha256") != expected_prompt_sha256:
            failures.append("prompt-review receipt is stale for the current prompt")
    if expected_action in {
        "paid-generation-approval",
        "runway-background-paid-approval",
    }:
        if payload.get("allow_paid_attempts") != 1:
            failures.append("approval must authorize exactly one paid attempt")
        if payload.get("candidate_bound") is not True:
            failures.append("approval must be candidate-bound")
        if (
            not isinstance(payload.get("planned_candidate_id"), str)
            or not payload["planned_candidate_id"].strip()
        ):
            failures.append("approval must name a planned candidate id")
        elif payload["planned_candidate_id"] != manifest.get("credit_control", {}).get(
            "planned_candidate_id"
        ):
            failures.append("approval planned candidate does not match the manifest")
        control = manifest.get("credit_control", {})
        if control.get("mode") == "ONE_SEPARATELY_APPROVED_RUNWAY_BACKGROUND_CANDIDATE":
            if payload.get("maximum_price_usd") != control.get("max_live_price_usd"):
                failures.append("approval price ceiling does not match the manifest")
        elif payload.get("maximum_estimated_credits") != control.get("max_estimated_credits"):
            failures.append("approval credit ceiling does not match the manifest")
        if payload.get("manifest_sha256") != execution_fingerprint(manifest):
            failures.append("approval is not bound to the current executable manifest")
    return {
        "status": "PASS" if not failures else "INVALID_RECEIPT",
        "path": str(path),
        "failures": failures,
    }


def verify_credit_control(manifest: dict[str, Any]) -> dict[str, Any]:
    control = manifest.get("credit_control")
    failures: list[str] = []
    if not isinstance(control, dict):
        return {
            "status": "MISSING_CREDIT_CONTROL",
            "failures": ["missing credit_control"],
            "prompt_review": {"status": "MISSING_RECEIPT"},
            "paid_approval": {"status": "MISSING_RECEIPT"},
            "attempt_available": False,
        }
    mode = control.get("mode")
    if mode not in {
        "ONE_CANDIDATE_ONE_PAID_ATTEMPT",
        "ONE_SEPARATELY_APPROVED_RUNWAY_BACKGROUND_CANDIDATE",
    }:
        failures.append("mode must be a supported one-candidate paid-attempt mode")
    if control.get("max_paid_generations") != 1:
        failures.append("max_paid_generations must equal 1")
    recorded = control.get("paid_generations_recorded")
    if not isinstance(recorded, int) or recorded < 0:
        failures.append("paid_generations_recorded must be a non-negative integer")
    if control.get("automatic_paid_retries") is not False:
        failures.append("automatic_paid_retries must be false")
    if (
        not isinstance(control.get("planned_candidate_id"), str)
        or not control["planned_candidate_id"].strip()
    ):
        failures.append("planned_candidate_id must be a non-empty string")
    ceiling_key = (
        "max_live_price_usd"
        if mode == "ONE_SEPARATELY_APPROVED_RUNWAY_BACKGROUND_CANDIDATE"
        else "max_estimated_credits"
    )
    maximum_estimated_credits = control.get(ceiling_key)
    if (
        not isinstance(maximum_estimated_credits, (int, float))
        or isinstance(maximum_estimated_credits, bool)
        or maximum_estimated_credits <= 0
    ):
        failures.append(f"{ceiling_key} must be a positive number")
    provider_estimate = manifest.get("provider_capability", {}).get("estimated_credits")
    if (
        isinstance(maximum_estimated_credits, (int, float))
        and isinstance(provider_estimate, (int, float))
        and provider_estimate > maximum_estimated_credits
    ):
        failures.append("provider estimate exceeds the approved credit ceiling")
    for key in (
        "require_current_observe_pass",
        "require_prompt_review_pass",
        "require_candidate_bound_approval",
    ):
        if control.get(key) is not True:
            failures.append(f"{key} must be true")
    if control.get("rejected_candidate_may_be_next_input") is not False:
        failures.append("rejected_candidate_may_be_next_input must be false")
    if control.get("on_failure") != "OPEN_ISSUE_AND_STOP":
        failures.append("on_failure must be OPEN_ISSUE_AND_STOP")
    if mode == "ONE_SEPARATELY_APPROVED_RUNWAY_BACKGROUND_CANDIDATE":
        background = manifest.get("native_scene_workflow", {}).get("background", {})
        if background.get("count") != 1:
            failures.append("Runway background count must equal 1")
        current_prompt = background.get("prompt", "")
        prompt_review_action = "runway-background-prompt-review"
        paid_approval_action = "runway-background-paid-approval"
    else:
        if manifest.get("higgsfield", {}).get("count") != 1:
            failures.append("Higgsfield count must equal 1")
        current_prompt = manifest.get("higgsfield", {}).get("prompt", "")
        prompt_review_action = "higgsfield-enhance-review"
        paid_approval_action = "paid-generation-approval"
    current_prompt_sha256 = sha256_text(current_prompt)
    if control.get("prompt_sha256") != current_prompt_sha256:
        failures.append("prompt_sha256 does not match the current prompt")

    prompt_review = verify_authorization_receipt(
        manifest, control.get("prompt_review_receipt"), prompt_review_action
    )
    paid_approval = verify_authorization_receipt(
        manifest, control.get("approval_receipt"), paid_approval_action
    )
    return {
        "status": "PASS" if not failures else "INVALID_CREDIT_CONTROL",
        "failures": failures,
        "prompt_review": prompt_review,
        "paid_approval": paid_approval,
        "attempt_available": isinstance(recorded, int)
        and recorded < control.get("max_paid_generations", 0),
    }


def observe(manifest: dict[str, Any]) -> dict[str, Any]:
    catalog = manifest["catalog_snapshot"]
    catalog_checks = [
        verify_file(resolve_path(catalog["catalog_path"]), catalog["catalog_sha256"]),
        verify_file(
            resolve_path(catalog["image_manifest_path"]),
            catalog["image_manifest_sha256"],
        ),
    ]
    source_checks = [
        verify_file(resolve_path(binding["path"]), binding["sha256"])
        for binding in manifest["source_bindings"]
    ]
    dependency_checks = [
        verify_file(resolve_path(dependency["path"]), dependency.get("expected_sha256"))
        for dependency in manifest.get("authority_dependencies", [])
    ]
    native_workflow_dependency_checks = verify_native_workflow_dependencies(manifest)
    forbidden_input_checks = [
        verify_file(resolve_path(binding["path"]), binding.get("sha256"))
        for binding in manifest.get("forbidden_inputs", [])
    ]
    forbidden_paths = {
        str(resolve_path(binding["path"])) for binding in manifest.get("forbidden_inputs", [])
    }
    routed_paths = {
        str(resolve_path(binding["path"]))
        for binding in manifest["source_bindings"]
        if binding.get("send_to_higgsfield") or isinstance(binding.get("provider_use"), str)
    }
    forbidden_routing_clean = not forbidden_paths.intersection(routed_paths)
    team_contract_check = verify_team_contract(manifest)
    creative_direction_check = verify_creative_direction(manifest)
    optical_contract_check = verify_optical_contract(manifest)
    prompt_adherence_check = verify_prompt_adherence(manifest)
    comfy_contract_check = verify_comfy_contract(manifest)
    provider_capability_check = verify_provider_capability(manifest)
    credit_control_check = verify_credit_control(manifest)
    source_ready = all(check["status"] == "PASS" for check in catalog_checks + source_checks)
    dependencies_ready = all(
        check["status"] == "PASS" for check in dependency_checks + native_workflow_dependency_checks
    )
    configuration_ready = (
        source_ready
        and dependencies_ready
        and forbidden_routing_clean
        and team_contract_check["status"] == "PASS"
        and creative_direction_check["status"] == "PASS"
        and optical_contract_check["status"] == "PASS"
        and prompt_adherence_check["status"] == "PASS"
        and comfy_contract_check["status"] == "PASS"
        and provider_capability_check["status"] == "PASS"
        and credit_control_check["status"] == "PASS"
    )
    paid_authorized = (
        credit_control_check["prompt_review"]["status"] == "PASS"
        and credit_control_check["paid_approval"]["status"] == "PASS"
        and credit_control_check["attempt_available"]
    )
    paid_route_permitted = (
        manifest.get("execution_strategy", {}).get("full_frame_paid_generation", True) is not False
    )
    return {
        "scene_id": manifest["scene_id"],
        "catalog_checks": catalog_checks,
        "source_checks": source_checks,
        "dependency_checks": dependency_checks,
        "native_workflow_dependency_checks": native_workflow_dependency_checks,
        "forbidden_input_checks": forbidden_input_checks,
        "forbidden_routing_clean": forbidden_routing_clean,
        "team_contract_check": team_contract_check,
        "creative_direction_check": creative_direction_check,
        "optical_contract_check": optical_contract_check,
        "prompt_adherence_check": prompt_adherence_check,
        "comfy_contract_check": comfy_contract_check,
        "provider_capability_check": provider_capability_check,
        "credit_control_check": credit_control_check,
        "source_ready": source_ready,
        "dependencies_ready": dependencies_ready,
        "configuration_ready": configuration_ready,
        "paid_authorized": paid_authorized,
        "paid_route_permitted": paid_route_permitted,
        "execute_blockers": manifest["execute_blockers"],
        "paid_execution_ready": configuration_ready
        and dependencies_ready
        and not manifest["execute_blockers"]
        and paid_authorized
        and provider_capability_check["status"] == "PASS"
        and paid_route_permitted,
    }


def higgsfield_command(manifest: dict[str, Any], enhance_only: bool) -> list[str]:
    if manifest.get("provider_capability", {}).get("higgsfield_role") != (
        "REFERENCE_GENERATION_CANDIDATE_ONLY"
    ):
        raise RuntimeError("this scene does not authorize a new Higgsfield generation route")
    config = manifest["higgsfield"]
    command = [
        "higgsfield",
        "--json",
        "product-photoshoot",
        "create",
        "--mode",
        config["mode"],
        "--prompt",
        config["prompt"],
        "--aspect_ratio",
        config["aspect_ratio"],
        "--count",
        str(config["count"]),
        "--brand_context",
        config["brand_context"],
        "--product_context",
        config["product_context"],
    ]
    for binding in manifest["source_bindings"]:
        if binding.get("send_to_higgsfield"):
            command.extend(["--image", str(resolve_path(binding["path"]))])
    if enhance_only:
        command.append("--enhance-only")
    return command


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    parsed: Any = None
    if completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError:
            parsed = completed.stdout.strip()
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": parsed,
        "stderr": completed.stderr.strip(),
    }


def inspect_enhanced_prompt(manifest: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    stdout = result.get("stdout")
    prompts = stdout.get("prompts", []) if isinstance(stdout, dict) else []
    prompt_text = "\n".join(item.get("prompt", "") for item in prompts if isinstance(item, dict))
    assertions = manifest["higgsfield"].get("prompt_assertions", {})
    lowered = prompt_text.casefold()
    missing_required = [
        phrase
        for phrase in assertions.get("required_phrases", [])
        if phrase.casefold() not in lowered
    ]
    present_forbidden = [
        phrase for phrase in assertions.get("forbidden_phrases", []) if phrase.casefold() in lowered
    ]
    passed = bool(prompt_text) and not missing_required and not present_forbidden
    return {
        "status": "PASS" if passed else "REJECTED_ENHANCER_PRODUCT_DRIFT",
        "prompt_present": bool(prompt_text),
        "missing_required_phrases": missing_required,
        "present_forbidden_phrases": present_forbidden,
    }


def write_receipt(scene_id: str, action: str, payload: dict[str, Any]) -> Path:
    receipt_dir = COMFY_ROOT / "receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    recorded_at = datetime.now(UTC)
    stamp = recorded_at.strftime("%Y%m%dT%H%M%S%fZ")
    receipt_path = receipt_dir / f"{scene_id.lower()}-{action}-{stamp}.json"
    document = {
        "schema": "skyyrose.scene-ooda-receipt/1",
        "scene_id": scene_id,
        "action": action,
        "recorded_at": recorded_at.isoformat(),
        "payload": payload,
    }
    receipt_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return receipt_path


def require_cli(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"required CLI not found on PATH: {name}")


def action_validate(manifest: dict[str, Any]) -> int:
    report = observe(manifest)
    if manifest.get("provider_capability", {}).get("higgsfield_role") == (
        "REFERENCE_GENERATION_CANDIDATE_ONLY"
    ):
        report["higgsfield_command_preview"] = higgsfield_command(manifest, True)
    else:
        report["higgsfield_command_preview"] = None
        report["selected_route"] = manifest.get("route_contract") or manifest.get(
            "native_scene_workflow"
        )
    print(json.dumps(report, indent=2))
    return 0 if report["configuration_ready"] else 2


def action_enhance(manifest: dict[str, Any]) -> int:
    if manifest.get("provider_capability", {}).get("higgsfield_role") != (
        "REFERENCE_GENERATION_CANDIDATE_ONLY"
    ):
        raise RuntimeError("this scene does not authorize Higgsfield prompt enhancement")
    require_cli("higgsfield")
    report = observe(manifest)
    if not report["configuration_ready"]:
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 2
    result = run_command(higgsfield_command(manifest, True))
    inspection = inspect_enhanced_prompt(manifest, result)
    receipt = write_receipt(
        manifest["scene_id"],
        "higgsfield-enhance",
        {"observe": report, "result": result, "inspection": inspection},
    )
    print(
        json.dumps(
            {"receipt": str(receipt), "inspection": inspection, "result": result},
            indent=2,
        )
    )
    if result["exit_code"] != 0:
        return result["exit_code"]
    return 0 if inspection["status"] == "PASS" else 4


def action_execute(manifest: dict[str, Any], allow_spend: bool) -> int:
    if not allow_spend:
        raise RuntimeError("paid generation requires the explicit --allow-spend flag")
    if manifest.get("provider_capability", {}).get("higgsfield_role") != (
        "REFERENCE_GENERATION_CANDIDATE_ONLY"
    ):
        raise RuntimeError("this scene does not authorize a new Higgsfield paid execution")
    require_cli("higgsfield")
    report = observe(manifest)
    if not report["paid_execution_ready"]:
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 3
    result = run_command(higgsfield_command(manifest, False))
    adherence_required = verify_prompt_adherence(manifest).get("configured") is True
    candidate_status = (
        "CANDIDATE_ONLY_PROMPT_ADHERENCE_REVIEW_REQUIRED"
        if adherence_required
        else "CANDIDATE_ONLY_PENDING_INDEPENDENT_REVIEW"
    )
    receipt = write_receipt(
        manifest["scene_id"],
        "higgsfield-generate",
        {
            "observe": report,
            "result": result,
            "candidate_status": candidate_status,
        },
    )
    print(
        json.dumps(
            {
                "receipt": str(receipt),
                "result": result,
                "candidate_status": candidate_status,
                "next_action": "review-candidate" if adherence_required else None,
            },
            indent=2,
        )
    )
    if result["exit_code"] != 0:
        return result["exit_code"]
    return 5 if adherence_required else 0


def action_review_enhance(manifest: dict[str, Any], receipt_path: Path | None) -> int:
    if receipt_path is None:
        raise RuntimeError("enhancement review requires --receipt /absolute/path/to/receipt.json")
    receipt_path = receipt_path.expanduser().resolve()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    result = receipt.get("payload", {}).get("result")
    if not isinstance(result, dict):
        raise ValueError("receipt does not contain a Higgsfield result payload")
    inspection = inspect_enhanced_prompt(manifest, result)
    review_receipt = write_receipt(
        manifest["scene_id"],
        "higgsfield-enhance-review",
        {
            "reviewed_receipt": str(receipt_path),
            "inspection": inspection,
            "generation_submitted": False,
            "prompt_sha256": sha256_text(manifest["higgsfield"]["prompt"]),
        },
    )
    print(json.dumps({"receipt": str(review_receipt), "inspection": inspection}, indent=2))
    return 0 if inspection["status"] == "PASS" else 4


def action_review_candidate(
    manifest: dict[str, Any], candidate: Path | None, receipt_path: Path | None
) -> int:
    if candidate is None:
        raise RuntimeError("candidate review requires --candidate /absolute/path/to/image")
    review = verify_prompt_adherence_review(
        manifest, candidate.expanduser().resolve(), receipt_path
    )
    if review["status"] in {
        "HARD_FAIL_QUARANTINED",
        "BELOW_THRESHOLD_QUARANTINED",
    }:
        marker = persist_prompt_adherence_quarantine(manifest, review)
        review["quarantine_marker"] = str(marker)
    print(json.dumps(review, indent=2))
    return 0 if review["status"] == "PASS" else 4


def action_stage(
    manifest: dict[str, Any], candidate: Path | None, receipt_path: Path | None
) -> int:
    if candidate is None:
        raise RuntimeError("staging requires --candidate /absolute/path/to/image")
    candidate = candidate.expanduser().resolve()
    check = verify_file(candidate, None)
    if not check["exists"]:
        print(json.dumps(check, indent=2), file=sys.stderr)
        return 2
    adherence_review = verify_prompt_adherence_review(manifest, candidate, receipt_path)
    if adherence_review["status"] != "PASS":
        if adherence_review["status"] in {
            "HARD_FAIL_QUARANTINED",
            "BELOW_THRESHOLD_QUARANTINED",
        }:
            marker = persist_prompt_adherence_quarantine(manifest, adherence_review)
            adherence_review["quarantine_marker"] = str(marker)
        print(json.dumps(adherence_review, indent=2), file=sys.stderr)
        return 4
    require_cli("comfy")
    result = run_command(["comfy", "--where", "local", "upload", str(candidate)])
    receipt = write_receipt(
        manifest["scene_id"],
        "comfy-stage-candidate",
        {
            "candidate": check,
            "candidate_status": "CANDIDATE_ONLY_PROMPT_ADHERENCE_PASS",
            "prompt_adherence_review": adherence_review,
            "result": result,
        },
    )
    print(json.dumps({"receipt": str(receipt), "result": result}, indent=2))
    return 0 if result["exit_code"] == 0 else result["exit_code"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=(
            "validate",
            "enhance",
            "review-enhance",
            "execute",
            "review-candidate",
            "stage",
        ),
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--allow-spend", action="store_true")
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--receipt", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = load_manifest(args.manifest.resolve())
        if args.action == "validate":
            return action_validate(manifest)
        if args.action == "enhance":
            return action_enhance(manifest)
        if args.action == "review-enhance":
            return action_review_enhance(manifest, args.receipt)
        if args.action == "execute":
            return action_execute(manifest, args.allow_spend)
        if args.action == "review-candidate":
            return action_review_candidate(manifest, args.candidate, args.receipt)
        return action_stage(manifest, args.candidate, args.receipt)
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
