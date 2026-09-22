#!/usr/bin/env python3
"""Validate collection hero sources, runtime safeguards, and approval boundaries."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

THEME = Path(__file__).resolve().parents[1]
MANIFEST = THEME / "data/collection-hero-motion.json"
FUNCTIONS = THEME / "functions.php"
TEMPLATE = THEME / "template-collection.php"
CONTROLLER = THEME / "assets/js/theme.js"
EXPECTED_SOURCES = {
    "signature": "assets/sot/images/hero/signature-golden-gate-monuments-v2.webp",
    "black-rose": "assets/sot/images/hero/black-rose-bay-bridge-monuments-v4.webp",
    "love-hurts": "assets/sot/images/hero/love-hurts-rose-aisle-monuments-v3.webp",
    "kids-capsule": "assets/sot/images/hero/kids-capsule-heir-throne-v3.webp",
}
REQUIRED_SAFEGUARDS = {
    "load_only_in_view",
    "pause_offscreen",
    "pause_when_hidden",
    "save_data_uses_still",
    "reduced_motion_uses_still",
    "user_pause_control",
    "video_failure_uses_still",
    "play_rejection_uses_still",
    "requires_mp4_and_webm",
}
AI_STATUSES = {
    "founder_review_required",
    "founder_approved",
    "provider_failed",
    "blocked_daily_generation_limit",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_asset(record: object, label: str) -> Path:
    if not isinstance(record, dict):
        raise ValueError(f"{label} is not an asset record")
    raw = record.get("file")
    expected_sha = record.get("sha256")
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
        raise ValueError(f"{label} has an unsafe path")
    path = (THEME / raw).resolve()
    try:
        path.relative_to(THEME.resolve())
    except ValueError as error:
        raise ValueError(f"{label} escapes the theme") from error
    if not path.is_file() or not isinstance(expected_sha, str) or sha256(path) != expected_sha:
        raise ValueError(f"{label} hash drift")
    return path


def validate_ai_assets(slug: str, ai_motion: dict, status: str, max_bytes: int) -> None:
    job_id = ai_motion.get("job_id")
    if status == "provider_failed":
        if (
            not isinstance(job_id, str)
            or not job_id
            or any(key in ai_motion for key in ("master", "web"))
        ):
            raise ValueError(f"{slug} provider failure record is incomplete")
        return
    if status == "blocked_daily_generation_limit":
        if any(key in ai_motion for key in ("master", "web")):
            raise ValueError(f"{slug} limit-blocked motion must not expose assets")
        return
    if not isinstance(job_id, str) or not job_id:
        raise ValueError(f"{slug} reviewable motion lacks a provider job ID")

    master = validate_asset(ai_motion.get("master"), f"{slug} AI master")
    web = ai_motion.get("web", [])
    if not isinstance(web, list) or len(web) != 2:
        raise ValueError(f"{slug} AI motion lacks MP4 and WebM derivatives")
    expected_root = f"assets/video/collection-heroes/{'approved' if status == 'founder_approved' else 'candidates'}/{slug}/"
    master_relative = master.relative_to(THEME).as_posix()
    if not master_relative.startswith(expected_root):
        raise ValueError(f"{slug} AI master is outside its {status} boundary")

    extensions: set[str] = set()
    for index, record in enumerate(web, start=1):
        path = validate_asset(record, f"{slug} AI web asset {index}")
        relative = path.relative_to(THEME).as_posix()
        if not relative.startswith(expected_root) or path.suffix.lower() not in {".mp4", ".webm"}:
            raise ValueError(f"{slug} AI web asset violates its approval boundary")
        if path.stat().st_size > max_bytes:
            raise ValueError(f"{slug} AI web asset exceeds the runtime byte budget")
        extensions.add(path.suffix.lower())
    if extensions != {".mp4", ".webm"}:
        raise ValueError(f"{slug} AI motion requires one MP4 and one WebM")
    if (
        status == "founder_review_required"
        and ai_motion.get("internal_visual_qa") != "pass_pending_founder_review"
    ):
        raise ValueError(f"{slug} candidate lacks internal visual QA")
    if status == "founder_approved" and not ai_motion.get("founder_approved_at"):
        raise ValueError(f"{slug} approved motion lacks founder approval evidence")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema") != "skyyrose.v2.collection-hero-motion.v1":
        raise ValueError("collection hero motion schema is unsupported")
    runtime = manifest.get("runtime", {})
    if runtime.get("exact_pixel_motion") != "active":
        raise ValueError("exact-pixel collection hero motion is not active")
    performance = runtime.get("performance", {})
    if not isinstance(performance, dict) or not REQUIRED_SAFEGUARDS.issubset(performance):
        raise ValueError("collection hero performance safeguards are incomplete")
    if any(performance[key] is not True for key in REQUIRED_SAFEGUARDS):
        raise ValueError("collection hero performance safeguards must be explicitly true")
    max_bytes = performance.get("max_web_asset_bytes")
    if not isinstance(max_bytes, int) or not 250000 <= max_bytes <= 2500000:
        raise ValueError("collection hero web motion byte budget is unsafe")
    creative_gate = runtime.get("creative_gate", {})
    if creative_gate.get("strongest_short_form_hook_by_seconds") != 1:
        raise ValueError("collection hero hook is not front-loaded")
    if creative_gate.get("authentic_product_established_by_seconds") != 1.5:
        raise ValueError("collection hero product proof timing drift")
    if creative_gate.get("predictor_is_not_product_approval") is not True:
        raise ValueError("virality prediction must not override product approval")

    collections = manifest.get("collections", {})
    if not isinstance(collections, dict) or set(collections) != set(EXPECTED_SOURCES):
        raise ValueError("collection hero motion manifest must cover all four collections")

    approved = 0
    for slug, collection in collections.items():
        if not isinstance(collection, dict):
            raise ValueError(f"{slug} collection motion record is malformed")
        source_record = collection.get("source")
        if (
            not isinstance(source_record, dict)
            or source_record.get("file") != EXPECTED_SOURCES[slug]
        ):
            raise ValueError(f"{slug} is not bound to its approved hero master")
        validate_asset(source_record, f"{slug} source")
        treatment = collection.get("exact_pixel_treatment")
        if not isinstance(treatment, str) or len(treatment.strip()) < 12:
            raise ValueError(f"{slug} has no exact-pixel motion treatment")
        ai_motion = collection.get("ai_motion", {})
        status = ai_motion.get("status") if isinstance(ai_motion, dict) else None
        if status not in AI_STATUSES:
            raise ValueError(f"{slug} has unsupported AI motion status: {status}")
        validate_ai_assets(slug, ai_motion, status, max_bytes)
        if status == "founder_approved":
            approved += 1

    functions_source = FUNCTIONS.read_text(encoding="utf-8")
    template_source = TEMPLATE.read_text(encoding="utf-8")
    controller_source = CONTROLLER.read_text(encoding="utf-8")
    for source in EXPECTED_SOURCES.values():
        responsive_name = Path(source).stem + "-1440w.webp"
        if responsive_name not in functions_source:
            raise ValueError(f"approved responsive hero is not wired: {responsive_name}")
    if (
        "skyyrose2_collection_hero_motion" not in template_source
        or "hero_motion_mp4" in template_source
    ):
        raise ValueError("collection template can bypass the approved hero-motion resolver")
    for runtime_guard in (
        "markMotionFailed",
        "prefers-reduced-motion",
        "navigator.connection",
        "IntersectionObserver",
    ):
        if runtime_guard not in controller_source:
            raise ValueError(f"collection hero runtime guard is missing: {runtime_guard}")

    print(
        f"Collection hero motion valid: {len(collections)} exact-pixel treatments, "
        f"{approved} founder-approved AI motion plates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
