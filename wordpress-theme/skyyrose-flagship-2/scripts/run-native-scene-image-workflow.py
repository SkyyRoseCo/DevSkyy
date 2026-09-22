#!/usr/bin/env python3
"""Run the fail-closed LH-COMMERCE-1 image workflow as a state machine.

This workflow never calls an image model itself. The ``preflight`` phase emits
the exact receipt that Codex must hold before calling the built-in image tool;
``record`` binds the returned candidate bytes; and ``verify`` enforces the GPT
vision review before a candidate can advance to the separate founder gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
THEME_DIR = Path(__file__).resolve().parent.parent
BASE = THEME_DIR / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1"
PREFLIGHT_DIR = BASE / "preflight-v1"
POSTFLIGHT_DIR = BASE / "postflight-v1/native-scene-v1"
CONTRACT = (
    PREFLIGHT_DIR / "vision-authored-prompts/lh-commerce-1-native-scene-regeneration-plan-v1.json"
)
PLANNING_RECEIPT = PREFLIGHT_DIR / "lh-commerce-1-native-scene-planning-validation-v1.json"
JUDGE_RECEIPT = PREFLIGHT_DIR / "judge-availability-receipt-v1.json"
OPUS_REVIEW = PREFLIGHT_DIR / "adversarial-planning/lh-native-scene-opus-review-v1.json"
FOUNDER_AUTHORIZATION = PREFLIGHT_DIR / "lh-native-scene-founder-authorization-v1.json"
SAFE_ZONES = PREFLIGHT_DIR / "lh-commerce-1-responsive-safe-zones-v1.json"
RELEASE_RECEIPT = PREFLIGHT_DIR / "lh-commerce-1-pass-ready-to-generate-v1.json"
BATCH_MANIFEST = POSTFLIGHT_DIR / "generation-batch-manifest-v1.json"
REVIEWS_DIR = POSTFLIGHT_DIR / "adversarial-reviews"
ADVERSARIAL_RECEIPT = POSTFLIGHT_DIR / "pass-adversarial-verification-receipt-v1.json"
JUDGE_PROBE = THEME_DIR / "scripts/verify-image-judge-availability.py"
PLANNING_VALIDATOR = THEME_DIR / "scripts/validate-native-scene-regeneration-preflight.py"
SAFE_ZONE_MEASURER = THEME_DIR / "scripts/measure-native-scene-safe-zones.mjs"
ADVERSARIAL_VALIDATOR = THEME_DIR / "scripts/validate-image-generation-adversarial.py"
JUDGE_MAX_AGE = timedelta(minutes=15)
SAFE_ZONE_MAX_AGE = timedelta(minutes=15)
RELEASE_MAX_AGE = timedelta(minutes=15)
FOUNDER_AUTH_MAX_AGE = timedelta(hours=24)
EXPECTED_JUDGES = ["gpt-5.5-pro"]
SYSTEM_GENERATED_IMAGE_ROOT = (Path.home() / ".codex/generated_images").resolve()
SYSTEM_TOOL_CALL_PATTERN = re.compile(
    r"^exec-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
SYSTEM_BATCH_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
# Runtime-owned verifier binaries must be pinned here by absolute path and SHA-256.
# This environment exposes no authenticated verifier, so the allowlist is
# intentionally empty and image generation remains fail-closed.
TRUSTED_PROVIDER_VERIFIER_ALLOWLIST: dict[str, str] = {}
EXPECTED_RENDER_BINDINGS = [
    "tools/v2-theme-preview.php",
    "wordpress-theme/skyyrose-flagship-2/template-collection.php",
    "wordpress-theme/skyyrose-flagship-2/functions.php",
    "wordpress-theme/skyyrose-flagship-2/data/scene-narrative-blueprints.json",
    "wordpress-theme/skyyrose-flagship-2/data/founder-selected-theme-placeholders-v1.json",
    "wordpress-theme/skyyrose-flagship-2/data/product-presentation-registry.json",
    "wordpress-theme/skyyrose-flagship-2/assets/css/design-tokens.css",
    "wordpress-theme/skyyrose-flagship-2/assets/css/theme.css",
    "wordpress-theme/skyyrose-flagship-2/assets/js/theme.js",
    "wordpress-theme/skyyrose-flagship-2/assets/js/house-of-roses-motion.js",
    "wordpress-theme/skyyrose-flagship-2/assets/js/kids-capsule-reveal.js",
    "wordpress-theme/skyyrose-flagship-2/assets/sot/fonts/archivo-latin.woff2",
    "wordpress-theme/skyyrose-flagship-2/assets/sot/fonts/hanken-grotesk-latin.woff2",
    "wordpress-theme/skyyrose-flagship-2/assets/sot/fonts/anton-latin.woff2",
    "wordpress-theme/skyyrose-flagship-2/assets/sot/fonts/cinzel-latin.woff2",
    "wordpress-theme/skyyrose-flagship-2/assets/sot/fonts/inter-latin.woff2",
]


class WorkflowBlocked(ValueError):
    """Raised when a release prerequisite is absent, stale, or unsafe."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WorkflowBlocked(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing workflow artifact: {path.relative_to(ROOT)}")
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    require(isinstance(value, dict), f"JSON root must be an object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def root_path(value: str) -> Path:
    require(bool(value) and not Path(value).is_absolute(), "bound path must be repository-relative")
    path = (ROOT / value).resolve()
    require(path == ROOT or ROOT in path.parents, f"bound path escapes repository: {value}")
    return path


def is_git_tracked(path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", str(path.relative_to(ROOT))],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def parse_time(value: Any, label: str) -> datetime:
    require(isinstance(value, str), f"{label} timestamp is missing")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise WorkflowBlocked(f"{label} timestamp is invalid") from error
    require(parsed.tzinfo is not None, f"{label} timestamp must be timezone-aware")
    return parsed.astimezone(UTC)


def validate_fresh_time(
    value: Any,
    label: str,
    max_age: timedelta,
    now: datetime,
) -> datetime:
    parsed = parse_time(value, label)
    require(parsed <= now + timedelta(minutes=1), f"{label} is future-dated")
    require(now - parsed <= max_age, f"{label} is stale")
    return parsed


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        json.dump(payload, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def invalidate_adversarial_receipt(reason: str) -> None:
    write_json_atomic(
        ADVERSARIAL_RECEIPT,
        {
            "schema": "skyyrose.adversarial-image-verification-receipt.v1",
            "status": "BLOCKED_STALE_ADVERSARIAL_VERIFICATION",
            "generated_at": datetime.now(UTC).isoformat(),
            "reason": reason,
        },
    )


def provider_verifier_path() -> str | None:
    """Resolve only a root-owned, signed, hash-pinned runtime verifier."""

    for raw_path, expected_hash in TRUSTED_PROVIDER_VERIFIER_ALLOWLIST.items():
        path = Path(raw_path)
        if not path.is_absolute() or not path.is_file() or path.is_symlink():
            continue
        resolved = path.resolve()
        if resolved == ROOT or ROOT in resolved.parents or Path.home() in resolved.parents:
            continue
        metadata = resolved.stat()
        if metadata.st_uid != 0 or metadata.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            continue
        if not re.fullmatch(r"[0-9a-f]{64}", expected_hash) or sha256(resolved) != expected_hash:
            continue
        signature = subprocess.run(
            ["/usr/bin/codesign", "--verify", "--deep", "--strict", str(resolved)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if signature.returncode == 0:
            return str(resolved)
    return None


def run_refresh() -> list[str]:
    blockers: list[str] = []
    if provider_verifier_path() is None:
        blockers.append("TRUSTED_PROVIDER_TOOL_RESULT_VERIFIER_UNAVAILABLE")
    judge = subprocess.run([sys.executable, str(JUDGE_PROBE)], cwd=ROOT, check=False)
    if judge.returncode:
        blockers.append("REQUIRED_JUDGE_LIVE_PROBE_FAILED")
    planning = subprocess.run(
        [sys.executable, str(PLANNING_VALIDATOR), "--write-receipt"],
        cwd=ROOT,
        check=False,
    )
    if planning.returncode:
        blockers.append("NATIVE_SCENE_PLANNING_VALIDATION_FAILED")
    safe_zones = subprocess.run(["node", str(SAFE_ZONE_MEASURER)], cwd=ROOT, check=False)
    if safe_zones.returncode:
        blockers.append("RESPONSIVE_SAFE_ZONE_MEASUREMENT_FAILED")
    return blockers


def validate_safe_zones(receipt: dict[str, Any], contract_hash: str, now: datetime) -> None:
    require(
        receipt.get("schema") == "skyyrose.native-scene-responsive-safe-zones.v1",
        "safe-zone receipt schema is stale",
    )
    require(receipt.get("status") == "PASS_MEASURED_SAFE_ZONES", "safe zones are not measured")
    require(receipt.get("contract_sha256") == contract_hash, "safe zones bind a stale contract")
    require(
        receipt.get("coordinate_space") == "normalized_generation_frame",
        "safe zones use the wrong coordinate space",
    )
    validate_fresh_time(receipt.get("measured_at"), "safe-zone measurement", SAFE_ZONE_MAX_AGE, now)
    preview_url = urlparse(receipt.get("preview_url", ""))
    require(
        preview_url.scheme == "http"
        and preview_url.hostname == "127.0.0.1"
        and preview_url.path == "/tools/v2-theme-preview.php"
        and parse_qs(preview_url.query) == {"route": ["love-hurts"]},
        "safe zones were not measured from the canonical loopback V2 route",
    )
    preview_identity = receipt.get("preview_identity", {})
    require(
        preview_identity.get("route") == "love-hurts"
        and preview_identity.get("template") == "template-collection.php"
        and preview_identity.get("theme", "").startswith("SkyyRose Flagship 2 "),
        "safe-zone preview identity is invalid",
    )
    current_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    require(
        preview_identity.get("commit") == current_commit,
        "safe zones were measured from a different commit",
    )
    bindings = receipt.get("render_source_bindings", [])
    require(
        [item.get("path") for item in bindings] == EXPECTED_RENDER_BINDINGS,
        "safe-zone rendered-code binding set drifted",
    )
    for binding in bindings:
        bound_path = root_path(binding.get("path", ""))
        require(bound_path.is_file(), f"safe-zone render source is missing: {binding.get('path')}")
        require(
            is_git_tracked(bound_path),
            f"safe-zone render source is untracked: {binding.get('path')}",
        )
        require(
            binding.get("sha256") == sha256(bound_path),
            f"safe-zone render source changed: {binding.get('path')}",
        )
    source_asset = receipt.get("source_asset", {})
    source_path = root_path(source_asset.get("path", ""))
    require(source_path.is_file(), "safe-zone scene source is missing")
    require(is_git_tracked(source_path), "safe-zone scene source is untracked")
    require(source_asset.get("sha256") == sha256(source_path), "safe-zone scene source changed")
    require(source_asset.get("dimensions") == [1672, 941], "safe-zone scene dimensions drifted")
    breakpoints = receipt.get("breakpoints", [])
    require(
        [item.get("id") for item in breakpoints] == ["desktop", "tablet", "mobile"],
        "safe-zone breakpoint order or coverage drifted",
    )
    for breakpoint in breakpoints:
        require(
            breakpoint.get("measurement_source") == "rendered_v2_dom", "safe zones are inferred"
        )
        require(breakpoint.get("keep_clear"), f"empty safe zones for {breakpoint.get('id')}")
        require(
            breakpoint.get("source_image_sha256") == source_asset.get("sha256"),
            f"rendered source hash drifted for {breakpoint.get('id')}",
        )
        require(
            breakpoint.get("source_dimensions") == source_asset.get("dimensions"),
            f"rendered source dimensions drifted for {breakpoint.get('id')}",
        )
        crop = breakpoint.get("crop_transform", {})
        require(
            crop.get("object_fit") == "cover" and crop.get("object_position") == "50% 50%",
            f"unsupported object-fit transform for {breakpoint.get('id')}",
        )
        screenshot = root_path(breakpoint.get("screenshot", ""))
        require(screenshot.is_file(), f"safe-zone screenshot missing for {breakpoint.get('id')}")
        require(
            breakpoint.get("screenshot_sha256") == sha256(screenshot),
            f"safe-zone screenshot changed for {breakpoint.get('id')}",
        )
        for zone in breakpoint["keep_clear"]:
            rect = zone.get("rect", [])
            require(len(rect) == 4, f"malformed safe-zone rect: {zone.get('id')}")
            require(
                all(type(value) in (int, float) and 0 <= value <= 1 for value in rect),
                f"safe-zone rect outside normalized frame: {zone.get('id')}",
            )
            require(
                rect[0] < rect[2] and rect[1] < rect[3], f"empty safe-zone rect: {zone.get('id')}"
            )


def candidate_job_ids(contract: dict[str, Any]) -> list[str]:
    count = contract.get("batch_and_review_contract", {}).get("candidate_count")
    require(type(count) is int and count > 0, "candidate count is invalid")
    return [f"lh-commerce-1-native-r{index:02d}" for index in range(1, count + 1)]


def validate_judge_receipt(receipt: dict[str, Any], now: datetime) -> None:
    require(
        receipt.get("schema") == "skyyrose.image-judge-availability.v1",
        "judge receipt schema is stale",
    )
    require(receipt.get("status") == "PASS_ALL_JUDGES_AVAILABLE", "required judge unavailable")
    require(receipt.get("all_judges_available") is True, "required judge set is incomplete")
    require(receipt.get("secrets_in_receipt") is False, "judge receipt secret state is unsafe")
    validate_fresh_time(receipt.get("checked_at"), "judge availability", JUDGE_MAX_AGE, now)
    judges = receipt.get("judges", [])
    require(
        [item.get("model") for item in judges] == EXPECTED_JUDGES,
        "required judge roster drifted",
    )
    for judge in judges:
        require(
            judge.get("available") is True
            and judge.get("reason") == "live_model_probe_passed"
            and type(judge.get("configured_credentials_tried")) is int
            and judge["configured_credentials_tried"] > 0,
            f"required judge did not pass live probe: {judge.get('model')}",
        )


def validate_source_audit(planning: dict[str, Any]) -> None:
    audit = planning.get("source_audit")
    require(isinstance(audit, list) and audit, "planning source audit is missing")
    seen: set[str] = set()
    for item in audit:
        item_path = item.get("path", "")
        require(item_path not in seen, f"duplicate planning source audit path: {item_path}")
        seen.add(item_path)
        current = root_path(item_path)
        require(current.is_file(), f"audited source is missing: {item_path}")
        require(item.get("sha256") == sha256(current), f"audited source changed: {item_path}")
        require(is_git_tracked(current), f"untracked bound input: {item_path}")


def expected_reviewed_files(context: dict[str, Any]) -> list[dict[str, Any]]:
    reviewed = [dict(item) for item in context["planning"]["source_audit"]]
    reviewed.extend(
        {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "git_tracked": True,
            "role": role,
        }
        for path, role in (
            (OPUS_REVIEW, "opus_planning_review"),
            (FOUNDER_AUTHORIZATION, "founder_generation_authorization"),
            (SAFE_ZONES, "measured_responsive_safe_zones"),
        )
    )
    return reviewed


def validate_tournament_policy_link(release: dict[str, Any], context: dict[str, Any]) -> None:
    canonical_policy = next(
        item
        for item in context["contract"]["bindings"]["validation_only_evidence"]
        if item["role"] == "mandatory_tournament_policy"
    )
    policy = root_path(canonical_policy["path"])
    require(
        release.get("tournament_policy", {}).get("path") == canonical_policy["path"],
        "release tournament policy path drifted",
    )
    require(
        release["tournament_policy"].get("sha256") == sha256(policy),
        "release tournament policy changed",
    )


def collect_release_blockers() -> tuple[list[str], dict[str, Any] | None]:
    blockers: list[str] = []
    try:
        contract = load_json(CONTRACT)
        contract_hash = sha256(CONTRACT)
        planning = load_json(PLANNING_RECEIPT)
        require(
            planning.get("status") == "PASS_PROMPT_PACKAGE_READY_FOR_OPUS_REVIEW",
            "planning validator did not pass",
        )
        require(
            planning.get("contract", {}).get("sha256") == contract_hash, "planning receipt is stale"
        )
        validate_source_audit(planning)

        product_sot_binding = contract.get("bindings", {}).get("current_product_sot", {})
        product_sot = root_path(product_sot_binding.get("path", ""))
        require(product_sot.is_file(), "bound product SOT is missing")
        require(
            product_sot_binding.get("sha256") == sha256(product_sot),
            "product SOT differs from the prompt contract",
        )

        judges = load_json(JUDGE_RECEIPT)
        now = datetime.now(UTC)
        validate_judge_receipt(judges, now)

        opus = load_json(OPUS_REVIEW)
        require(
            opus.get("schema") == "skyyrose.adversarial-planning-review.v1",
            "Opus review schema is stale",
        )
        require(opus.get("reviewer_id") == "claude-opus-5", "Opus review uses the wrong model")
        require(
            opus.get("available") is True and opus.get("ship") is True,
            "Opus review did not approve planning",
        )
        require(opus.get("blocking_findings") == [], "Opus review still has blockers")
        require(opus.get("contract_sha256") == contract_hash, "Opus review binds a stale contract")

        authorization = load_json(FOUNDER_AUTHORIZATION)
        require(
            authorization.get("schema")
            == "skyyrose.native-scene-founder-generation-authorization.v1",
            "founder authorization schema is stale",
        )
        require(
            authorization.get("generation_authorized") is True,
            "founder did not authorize generation",
        )
        require(
            authorization.get("contract_sha256") == contract_hash,
            "founder authorization binds a stale contract",
        )
        require(
            authorization.get("deployment_authorized") is False,
            "generation authorization incorrectly permits deployment",
        )
        require(
            authorization.get("final_visual_approval_granted") is False,
            "generation authorization invents final approval",
        )
        auth_time = parse_time(authorization.get("authorized_at"), "founder authorization")
        require(
            auth_time <= now + timedelta(minutes=1),
            "founder authorization is future-dated",
        )
        require(
            now - auth_time <= FOUNDER_AUTH_MAX_AGE, "founder generation authorization is stale"
        )

        safe_zones = load_json(SAFE_ZONES)
        validate_safe_zones(safe_zones, contract_hash, now)
        require(is_git_tracked(CONTRACT), "native-scene prompt contract is untracked")
        require(is_git_tracked(OPUS_REVIEW), "Opus planning review is untracked")
        require(is_git_tracked(FOUNDER_AUTHORIZATION), "founder authorization is untracked")
        require(is_git_tracked(SAFE_ZONES), "safe-zone receipt is untracked")

        jobs = candidate_job_ids(contract)
        require(
            provider_verifier_path() is not None,
            "trusted provider tool-result verifier is unavailable",
        )
        require(
            authorization.get("candidate_count") == len(jobs),
            "founder authorization candidate count differs from the prompt contract",
        )
        return blockers, {
            "contract": contract,
            "contract_hash": contract_hash,
            "planning": planning,
            "judges": judges,
            "opus": opus,
            "authorization": authorization,
            "safe_zones": safe_zones,
            "jobs": jobs,
        }
    except (
        KeyError,
        TypeError,
        WorkflowBlocked,
        json.JSONDecodeError,
        OSError,
        subprocess.CalledProcessError,
    ) as error:
        blockers.append(str(error))
        return blockers, None


def preflight(refresh: bool) -> int:
    invalidate_adversarial_receipt("a new release preflight was started")
    refresh_blockers = run_refresh()
    blockers, context = collect_release_blockers()
    blockers = [*refresh_blockers, *blockers]
    now = datetime.now(UTC).isoformat()
    if blockers or context is None:
        receipt = {
            "schema": "skyyrose.image-generation-preflight-receipt.v1",
            "status": "BLOCKED_NATIVE_SCENE_RELEASE",
            "generated_at": now,
            "scene_id": "LH-COMMERCE-1",
            "generation_permitted": False,
            "blockers": list(dict.fromkeys(blockers)),
        }
        write_json_atomic(RELEASE_RECEIPT, receipt)
        print("BLOCKED_NATIVE_SCENE_RELEASE " + " | ".join(receipt["blockers"]))
        return 1

    contract = context["contract"]
    product_sot_binding = contract["bindings"]["current_product_sot"]
    product_sot = root_path(product_sot_binding["path"])
    policy_binding = next(
        item
        for item in contract["bindings"]["validation_only_evidence"]
        if item["role"] == "mandatory_tournament_policy"
    )
    reviewed_files = expected_reviewed_files(context)
    receipt = {
        "schema": "skyyrose.image-generation-preflight-receipt.v1",
        "status": "PASS_READY_TO_GENERATE",
        "generated_at": now,
        "scene_id": "LH-COMMERCE-1",
        "workflow_profile": "native_scene_regeneration_v1",
        "prompt_contract": {
            "path": str(CONTRACT.relative_to(ROOT)),
            "sha256": context["contract_hash"],
        },
        "product_sot": {
            "path": str(product_sot.relative_to(ROOT)),
            "sha256": sha256(product_sot),
        },
        "tournament_policy": {
            "path": policy_binding["path"],
            "sha256": sha256(root_path(policy_binding["path"])),
        },
        "judge_availability": {
            "path": str(JUDGE_RECEIPT.relative_to(ROOT)),
            "sha256": sha256(JUDGE_RECEIPT),
        },
        "opus_review": {"path": str(OPUS_REVIEW.relative_to(ROOT)), "sha256": sha256(OPUS_REVIEW)},
        "founder_authorization": {
            "path": str(FOUNDER_AUTHORIZATION.relative_to(ROOT)),
            "sha256": sha256(FOUNDER_AUTHORIZATION),
        },
        "responsive_safe_zones": {
            "path": str(SAFE_ZONES.relative_to(ROOT)),
            "sha256": sha256(SAFE_ZONES),
        },
        "active_generation_jobs": context["jobs"],
        "bound_skus": sorted(contract["product_bindings"]),
        "reviewed_file_count": len(reviewed_files),
        "reviewed_files": reviewed_files,
        "generation_permitted": True,
        "downstream_state": "GENERATION_ALLOWED_COMPOSITOR_BLOCKED_PENDING_GPT_AND_FOUNDER_REVIEW",
    }
    write_json_atomic(RELEASE_RECEIPT, receipt)
    print(
        "PASS_READY_TO_GENERATE "
        f"jobs={len(context['jobs'])} contract_sha256={context['contract_hash']}"
    )
    return 0


def parse_outputs(values: list[str]) -> dict[str, Path]:
    parsed: dict[str, Path] = {}
    for value in values:
        require("=" in value, f"output must use JOB_ID=PATH: {value}")
        job_id, raw_path = value.split("=", 1)
        require(
            job_id and raw_path and job_id not in parsed, f"invalid or duplicate output: {value}"
        )
        parsed[job_id] = Path(raw_path).resolve()
    return parsed


def validate_release_receipt(release: dict[str, Any]) -> dict[str, Any]:
    require(
        release.get("schema") == "skyyrose.image-generation-preflight-receipt.v1",
        "release receipt schema is invalid",
    )
    require(release.get("status") == "PASS_READY_TO_GENERATE", "release preflight is not passing")
    require(release.get("scene_id") == "LH-COMMERCE-1", "release scene is invalid")
    require(
        release.get("workflow_profile") == "native_scene_regeneration_v1",
        "release workflow profile is invalid",
    )
    require(release.get("generation_permitted") is True, "release receipt forbids generation")
    now = datetime.now(UTC)
    validate_fresh_time(release.get("generated_at"), "release receipt", RELEASE_MAX_AGE, now)
    blockers, context = collect_release_blockers()
    require(not blockers and context is not None, "current release prerequisites no longer pass")
    expected_links = {
        "prompt_contract": CONTRACT,
        "product_sot": root_path(context["contract"]["bindings"]["current_product_sot"]["path"]),
        "judge_availability": JUDGE_RECEIPT,
        "opus_review": OPUS_REVIEW,
        "founder_authorization": FOUNDER_AUTHORIZATION,
        "responsive_safe_zones": SAFE_ZONES,
    }
    for key, current in expected_links.items():
        link = release.get(key, {})
        require(link.get("path") == str(current.relative_to(ROOT)), f"release {key} path drifted")
        require(link.get("sha256") == sha256(current), f"release {key} hash drifted")
    validate_tournament_policy_link(release, context)
    require(release.get("active_generation_jobs") == context["jobs"], "released job set drifted")
    require(
        release.get("bound_skus") == sorted(context["contract"]["product_bindings"]),
        "released SKU set drifted",
    )
    expected_reviewed = expected_reviewed_files(context)
    require(release.get("reviewed_files") == expected_reviewed, "released source audit drifted")
    require(
        release.get("reviewed_file_count") == len(expected_reviewed),
        "released source audit count drifted",
    )
    return context


def parse_sidecars(values: list[str]) -> dict[str, Path]:
    return parse_outputs(values)


def validate_exact_artifact_mapping(
    artifacts: dict[str, Path], expected_jobs: list[str], label: str
) -> None:
    require(
        set(artifacts) == set(expected_jobs),
        f"{label} do not cover the exact released job set",
    )
    require(
        len(set(artifacts.values())) == len(expected_jobs),
        f"{label} paths are not unique",
    )


def add_unique_provider_job_id(provider_job_id: str, seen: set[str]) -> str:
    normalized = provider_job_id.strip()
    require(bool(normalized), "generation provider job ID is missing")
    require(normalized not in seen, f"duplicate provider job identity: {normalized}")
    seen.add(normalized)
    return normalized


def validate_generation_sidecar(
    sidecar_path: Path,
    job_id: str,
    output: Path,
    release: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    candidate_directory = root_path(contract["output_contract"]["candidate_directory"])
    require(
        sidecar_path.is_file() and candidate_directory in sidecar_path.parents,
        f"generation sidecar is missing or outside candidate directory: {sidecar_path}",
    )
    sidecar = load_json(sidecar_path)
    require(
        sidecar.get("schema") == "skyyrose.image-generation-job-evidence.v1",
        f"generation sidecar schema is invalid: {job_id}",
    )
    require(sidecar.get("job_id") == job_id, f"generation sidecar job mismatch: {job_id}")
    require(sidecar.get("scene_id") == "LH-COMMERCE-1", f"generation scene mismatch: {job_id}")
    require(sidecar.get("model_id") == "gpt-image-2", f"generation model mismatch: {job_id}")
    require(
        sidecar.get("operation") == "multi_reference_native_scene_regeneration",
        f"generation operation mismatch: {job_id}",
    )
    release_hash = sha256(RELEASE_RECEIPT)
    require(
        sidecar.get("release_receipt_sha256") == release_hash,
        f"generation sidecar binds a stale release: {job_id}",
    )
    require(
        sidecar.get("prompt_contract_sha256") == release["prompt_contract"]["sha256"],
        f"generation sidecar binds a stale prompt: {job_id}",
    )
    prompt_hash = canonical_json_sha256(contract["prompt_payload"])
    require(
        sidecar.get("prompt_payload_sha256") == prompt_hash,
        f"generation prompt payload hash mismatch: {job_id}",
    )
    ordered_hashes = [
        item["sha256"] for item in contract["bindings"]["generator_conditioning_references"]
    ]
    require(
        sidecar.get("ordered_input_hashes") == ordered_hashes,
        f"generation input order or hashes drifted: {job_id}",
    )
    require(
        isinstance(sidecar.get("provider_job_id"), str)
        and sidecar["provider_job_id"] == sidecar["provider_job_id"].strip()
        and bool(sidecar["provider_job_id"]),
        f"generation provider job ID is missing: {job_id}",
    )
    provider_link = sidecar.get("provider_result_receipt", {})
    provider_path = root_path(provider_link.get("path", ""))
    require(
        provider_path.is_file() and candidate_directory in provider_path.parents,
        f"provider result receipt is missing or outside candidate directory: {job_id}",
    )
    require(
        provider_link.get("sha256") == sha256(provider_path),
        f"provider result receipt hash mismatch: {job_id}",
    )
    provider = load_json(provider_path)
    require(
        provider.get("schema") == "skyyrose.image-tool-result.v1"
        and provider.get("provider") == "openai"
        and provider.get("tool_name") == "image_gen.imagegen",
        f"provider result receipt schema or tool is invalid: {job_id}",
    )
    require(
        provider.get("tool_call_id") == sidecar["provider_job_id"],
        f"provider result identity mismatch: {job_id}",
    )
    raw_result = provider.get("raw_result")
    require(
        isinstance(raw_result, dict)
        and set(raw_result) == {"tool_call_id", "generated_image_path", "output_hint"},
        f"provider raw result is missing or structurally incomplete: {job_id}",
    )
    require(
        provider.get("raw_result_sha256") == canonical_json_sha256(raw_result),
        f"provider raw result hash mismatch: {job_id}",
    )
    require(
        raw_result.get("tool_call_id") == sidecar["provider_job_id"]
        and isinstance(raw_result.get("output_hint"), str),
        f"provider raw result identity mismatch: {job_id}",
    )
    source = Path(raw_result.get("generated_image_path", "")).resolve()
    require(
        SYSTEM_GENERATED_IMAGE_ROOT in source.parents
        and source.parent.parent == SYSTEM_GENERATED_IMAGE_ROOT
        and bool(SYSTEM_BATCH_PATTERN.fullmatch(source.parent.name))
        and bool(SYSTEM_TOOL_CALL_PATTERN.fullmatch(source.stem))
        and source.stem == sidecar["provider_job_id"]
        and source.suffix.lower() == ".png"
        and source.is_file(),
        f"provider result is not a system-managed Codex image artifact: {job_id}",
    )
    system_source = provider.get("system_managed_source", {})
    require(
        system_source.get("path") == str(source)
        and system_source.get("sha256") == sha256(source)
        and system_source.get("bytes") == source.stat().st_size,
        f"system-managed provider artifact binding mismatch: {job_id}",
    )
    require(
        provider.get("output", {}).get("path") == str(output.relative_to(ROOT))
        and provider.get("output", {}).get("sha256") == sha256(output)
        and sha256(source) == sha256(output),
        f"provider result output mismatch: {job_id}",
    )
    verifier = provider_verifier_path()
    require(verifier is not None, f"trusted provider verifier unavailable: {job_id}")
    verification = subprocess.run(
        [
            verifier,
            "--receipt",
            str(provider_path),
            "--artifact",
            str(source),
            "--tool-call-id",
            sidecar["provider_job_id"],
            "--sha256",
            sha256(source),
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    require(
        verification.returncode == 0,
        f"signed provider execution evidence did not verify: {job_id}",
    )
    generated_at = validate_fresh_time(
        sidecar.get("generated_at"), f"generation job {job_id}", RELEASE_MAX_AGE, datetime.now(UTC)
    )
    release_time = parse_time(release["generated_at"], "release receipt")
    require(generated_at >= release_time, f"generation predates release: {job_id}")
    require(
        datetime.fromtimestamp(source.stat().st_mtime, UTC) + timedelta(seconds=1) >= release_time,
        f"system-managed provider artifact predates release: {job_id}",
    )
    require(
        sidecar.get("output", {}).get("path") == str(output.relative_to(ROOT)),
        f"generation sidecar output path mismatch: {job_id}",
    )
    require(
        sidecar.get("output", {}).get("sha256") == sha256(output),
        f"generation sidecar output hash mismatch: {job_id}",
    )
    require(
        datetime.fromtimestamp(output.stat().st_mtime, UTC) + timedelta(seconds=1) >= release_time,
        f"generated output predates release: {job_id}",
    )
    return sidecar


def inspect_png(output: Path, expected_dimensions: list[int]) -> tuple[list[int], str]:
    try:
        with Image.open(output) as image:
            require(image.format == "PNG", f"generated output content is not PNG: {output}")
            image.verify()
        with Image.open(output) as image:
            image.load()
            dimensions = list(image.size)
            mode = image.mode
    except (OSError, SyntaxError, ValueError) as error:
        raise WorkflowBlocked(f"generated PNG failed full decode: {output}") from error
    require(dimensions == expected_dimensions, f"generated output dimensions drifted: {output}")
    require(mode in {"RGB", "RGBA"}, f"generated output color mode is invalid: {output}")
    return dimensions, mode


def record(outputs_raw: list[str], sidecars_raw: list[str]) -> int:
    invalidate_adversarial_receipt("a new generation batch recording was started")
    release = load_json(RELEASE_RECEIPT)
    context = validate_release_receipt(release)
    outputs = parse_outputs(outputs_raw)
    sidecars = parse_sidecars(sidecars_raw)
    expected_jobs = release["active_generation_jobs"]
    validate_exact_artifact_mapping(outputs, expected_jobs, "outputs")
    validate_exact_artifact_mapping(sidecars, expected_jobs, "sidecars")
    contract = context["contract"]
    candidate_directory = root_path(contract["output_contract"]["candidate_directory"])
    expected_dimensions = contract["output_contract"]["dimensions"]
    jobs: dict[str, Any] = {}
    output_hashes: set[str] = set()
    provider_job_ids: set[str] = set()
    for job_id in expected_jobs:
        output = outputs[job_id]
        require(output.is_file(), f"generated output missing: {output}")
        require(output.suffix.lower() == ".png", f"generated output must be PNG: {output}")
        require(
            candidate_directory in output.parents,
            f"output escapes released candidate directory: {output}",
        )
        dimensions, mode = inspect_png(output, expected_dimensions)
        output_hash = sha256(output)
        require(output_hash not in output_hashes, f"duplicate generated output bytes: {output}")
        output_hashes.add(output_hash)
        sidecar = validate_generation_sidecar(sidecars[job_id], job_id, output, release, contract)
        provider_job_id = add_unique_provider_job_id(sidecar["provider_job_id"], provider_job_ids)
        jobs[job_id] = {
            "scene_id": "LH-COMMERCE-1",
            "model": "gpt-image-2",
            "operation": "multi_reference_native_scene_regeneration",
            "prompt_payload_sha256": sidecar["prompt_payload_sha256"],
            "ordered_input_hashes": sidecar["ordered_input_hashes"],
            "provider_job_id": provider_job_id,
            "provider_result_receipt": sidecar["provider_result_receipt"],
            "generated_at": sidecar["generated_at"],
            "generation_sidecar": {
                "path": str(sidecars[job_id].relative_to(ROOT)),
                "sha256": sha256(sidecars[job_id]),
            },
            "output": {
                "path": str(output.relative_to(ROOT)),
                "sha256": output_hash,
                "dimensions": dimensions,
                "color_mode": mode,
            },
            "product_bindings": contract["product_bindings"],
            "approval_state": "FOUNDER_REVIEW_REQUIRED",
        }
    manifest = {
        "schema": "skyyrose.image-generation-batch.v1",
        "approval_state": "FOUNDER_REVIEW_REQUIRED",
        "founder_approval_required": True,
        "preflight_receipt": str(RELEASE_RECEIPT.relative_to(ROOT)),
        "preflight_receipt_sha256": sha256(RELEASE_RECEIPT),
        "prompt_contract": str(CONTRACT.relative_to(ROOT)),
        "prompt_contract_sha256": sha256(CONTRACT),
        "product_sot_sha256": release["product_sot"]["sha256"],
        "tournament_policy": release["tournament_policy"],
        "jobs": jobs,
        "downstream_state": "BLOCKED_PENDING_GPT_AND_FOUNDER_REVIEW",
    }
    write_json_atomic(BATCH_MANIFEST, manifest)
    print(f"RECORDED_NATIVE_SCENE_BATCH jobs={len(jobs)} manifest_sha256={sha256(BATCH_MANIFEST)}")
    return 0


def verify(founder_override: Path | None = None) -> int:
    command = [
        sys.executable,
        str(ADVERSARIAL_VALIDATOR),
        "--preflight",
        str(RELEASE_RECEIPT),
        "--batch",
        str(BATCH_MANIFEST),
        "--reviews",
        str(REVIEWS_DIR),
        "--receipt",
        str(ADVERSARIAL_RECEIPT),
        "--write-receipt",
    ]
    if founder_override is not None:
        command.extend(["--founder-override", str(founder_override)])
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def status() -> int:
    adversarial_passed = False
    founder_approval_required = True
    founder_approval_recorded = False
    compositor_permitted_outputs: dict[str, str] = {}
    if ADVERSARIAL_RECEIPT.is_file() and BATCH_MANIFEST.is_file() and RELEASE_RECEIPT.is_file():
        adversarial = load_json(ADVERSARIAL_RECEIPT)
        adversarial_passed = (
            adversarial.get("status") == "PASS_GPT_VISION_REVIEW"
            and adversarial.get("preflight_receipt", {}).get("sha256") == sha256(RELEASE_RECEIPT)
            and adversarial.get("generation_batch_manifest", {}).get("sha256")
            == sha256(BATCH_MANIFEST)
        )
        founder_approval_required = adversarial.get("founder_approval_required") is True
        founder_approval_recorded = adversarial.get("founder_approval_recorded") is True
        if founder_approval_recorded:
            compositor_permitted_outputs = adversarial.get("approved_output_hashes", {})
    result = {
        "scene_id": "LH-COMMERCE-1",
        "release_receipt": load_json(RELEASE_RECEIPT) if RELEASE_RECEIPT.is_file() else None,
        "batch_recorded": BATCH_MANIFEST.is_file(),
        "gpt_review_passed": adversarial_passed,
        "founder_approval_required": founder_approval_required,
        "founder_approval_recorded": founder_approval_recorded,
        "promotion_permitted": adversarial_passed and founder_approval_recorded,
        "compositor_permitted_outputs": compositor_permitted_outputs,
    }
    print(json.dumps(result, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="phase", required=True)
    subparsers.add_parser("preflight")
    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("--output", action="append", default=[], metavar="JOB_ID=PATH")
    record_parser.add_argument("--sidecar", action="append", default=[], metavar="JOB_ID=PATH")
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--founder-override", type=Path)
    subparsers.add_parser("status")
    args = parser.parse_args()
    try:
        if args.phase == "preflight":
            return preflight(refresh=True)
        if args.phase == "record":
            return record(args.output, args.sidecar)
        if args.phase == "verify":
            return verify(args.founder_override)
        return status()
    except (KeyError, TypeError, WorkflowBlocked, json.JSONDecodeError, OSError) as error:
        print(f"BLOCKED_NATIVE_SCENE_WORKFLOW {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
