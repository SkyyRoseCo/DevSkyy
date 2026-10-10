#!/usr/bin/env python3
"""Fail closed when a cinematic scene lacks complete 100-percent evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
THEME = Path(__file__).resolve().parents[1]
PRODUCT_SOT = ROOT / "data/product-sot.json"
CONTRACT = THEME / "data/scene-production-contract.json"
BLUEPRINTS = THEME / "data/scene-narrative-blueprints.json"
MANIFEST = THEME / "assets/scroll-world/generated-candidates/scene-candidate-manifest.json"


def validate_founder_commerce_casts(collection_blueprints: object, products: object) -> None:
    if not isinstance(collection_blueprints, dict) or not isinstance(products, dict):
        raise ValueError("scene commerce cast sources are invalid")

    scene_ids: set[str] = set()
    for collection in ("black-rose", "love-hurts", "signature"):
        collection_blueprint = collection_blueprints.get(collection)
        if not isinstance(collection_blueprint, dict):
            raise ValueError(f"founder commerce collection is missing: {collection}")
        chapters = collection_blueprint.get("commerce_scene_chapters")
        if not isinstance(chapters, list) or len(chapters) != 3:
            raise ValueError(f"founder commerce scene count drift: {collection}")
        for chapter in chapters:
            if not isinstance(chapter, dict):
                raise ValueError(f"founder commerce scene is invalid: {collection}")
            scene_id = chapter.get("scene_id")
            if not isinstance(scene_id, str) or not scene_id or scene_id in scene_ids:
                raise ValueError(f"founder commerce scene ID is invalid or duplicated: {scene_id}")
            scene_ids.add(scene_id)
            skus = chapter.get("product_bindings")
            if not isinstance(skus, list) or not skus or len(skus) != len(set(skus)):
                raise ValueError(f"founder commerce cast is empty or duplicated: {scene_id}")
            if chapter.get("individual_product_links_required") is not True:
                raise ValueError(f"individual commerce links are not required: {scene_id}")
            if chapter.get("aggregate_bundle_product") is not False:
                raise ValueError(f"scene implies an unapproved bundle product: {scene_id}")
            for field in (
                "direction",
                "primary_cta",
                "hero_aspect",
                "story_support",
                "product_focus",
            ):
                if not isinstance(chapter.get(field), str) or not chapter[field].strip():
                    raise ValueError(f"founder commerce scene lacks {field}: {scene_id}")
            generation_gate = chapter.get("generation_gate")
            if not isinstance(generation_gate, str) or not generation_gate.startswith(
                "BLOCKED_UNTIL_"
            ):
                raise ValueError(f"founder fidelity gate is missing: {scene_id}")
            if chapter.get("approval_state") != "FOUNDER_DIRECTION_LOCKED":
                raise ValueError(f"founder direction lock is missing: {scene_id}")
            if chapter.get("generation_state") != "NOT_GENERATED":
                raise ValueError(f"unapproved generation state: {scene_id}")

            for sku in skus:
                product = products.get(sku)
                if not isinstance(product, dict):
                    raise ValueError(f"founder commerce cast uses unknown SKU: {sku}")
                identity = product.get("identity")
                if not isinstance(identity, dict) or identity.get("collection") != collection:
                    raise ValueError(f"founder commerce cast crosses collections: {scene_id} {sku}")
                if chapter.get("preorder_product_links_required") is True:
                    commerce = product.get("commerce")
                    if not isinstance(commerce, dict) or commerce.get("is_preorder") is not True:
                        raise ValueError(
                            f"founder pre-order scene includes a non-pre-order SKU: {scene_id} {sku}"
                        )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_asset(root: Path, raw: object, *, label: str) -> Path:
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
        raise ValueError(f"{label} has an unsafe path")
    resolved_root = root.resolve()
    resolved = (root / raw).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"{label} escapes its approved asset root") from error
    if not resolved.is_file():
        raise ValueError(f"{label} does not resolve")
    return resolved


def product_reference_hashes(product: dict[str, object]) -> dict[Path, str]:
    media = product.get("media", {})
    hashes: dict[Path, str] = {}
    if isinstance(media, dict):
        for record in media.values():
            if not isinstance(record, dict) or not isinstance(record.get("path"), str):
                continue
            if not isinstance(record.get("sha256"), str):
                continue
            hashes[(ROOT / record["path"]).resolve()] = record["sha256"]
    references = product.get("references", [])
    if isinstance(references, list):
        for record in references:
            if not isinstance(record, dict) or not isinstance(record.get("path"), str):
                continue
            if not isinstance(record.get("sha256"), str):
                continue
            hashes[(ROOT / record["path"]).resolve()] = record["sha256"]
    return hashes


def validate_asset_record(record: object, *, label: str) -> Path:
    if not isinstance(record, dict):
        raise ValueError(f"{label} record is invalid")
    asset = resolve_asset(THEME, record.get("file"), label=label)
    if sha256(asset) != record.get("sha256"):
        raise ValueError(f"{label} hash drift")
    return asset


def validate_approved_candidate(candidate: dict[str, object], contract: dict[str, object]) -> None:
    chapter = str(candidate.get("chapter", "unnamed"))
    if candidate.get("provenance_blockers"):
        raise ValueError(f"{chapter}: founder-approved scene retains provenance blockers")
    evaluation = candidate.get("evaluation")
    if not isinstance(evaluation, dict):
        raise ValueError(f"{chapter}: founder-approved scene has no evaluation evidence")

    categories = contract.get("categories", {})
    if not isinstance(categories, dict):
        raise ValueError("scene production contract categories are invalid")
    for category, requirements in categories.items():
        result = evaluation.get(category)
        if not isinstance(result, dict) or result.get("score") != 100:
            raise ValueError(f"{chapter}: {category} is not independently scored 100")
        required_checks = requirements.get("checks", []) if isinstance(requirements, dict) else []
        checks = result.get("checks", {})
        if not isinstance(checks, dict):
            raise ValueError(f"{chapter}: {category} checks are missing")
        missing = [check for check in required_checks if checks.get(check) is not True]
        if missing:
            raise ValueError(f"{chapter}: {category} failed checks: {', '.join(missing)}")

    evidence = evaluation.get("evidence", {})
    if not isinstance(evidence, dict):
        raise ValueError(f"{chapter}: release evidence is missing")
    missing_evidence = [
        item for item in contract.get("required_evidence", []) if not evidence.get(item)
    ]
    if missing_evidence:
        raise ValueError(f"{chapter}: release evidence missing: {', '.join(missing_evidence)}")


def main() -> int:
    product_sot_bytes = PRODUCT_SOT.read_bytes()
    product_sot = json.loads(product_sot_bytes)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    blueprints = json.loads(BLUEPRINTS.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if contract.get("schema") != "skyyrose.v2.cinematic-scene-contract.v1":
        raise ValueError("scene production contract schema is unsupported")
    if blueprints.get("schema") != "skyyrose.v2.scene-narrative-blueprints.v1":
        raise ValueError("scene narrative blueprint schema is unsupported")
    if manifest.get("schema") != "skyyrose.v2.scene-candidates.v1":
        raise ValueError("scene candidate manifest schema is unsupported")
    if contract.get("required_score") != 100:
        raise ValueError("scene production contract must require 100 in every category")
    for category, requirements in contract.get("categories", {}).items():
        if requirements.get("required_score") != 100:
            raise ValueError(f"scene category does not require 100: {category}")
    delivery_policy = contract.get("delivery_policy", {})
    required_motion_formats = delivery_policy.get("required_motion_formats")
    max_motion_bytes = delivery_policy.get("max_served_motion_bytes")
    if required_motion_formats != ["mp4", "webm"]:
        raise ValueError("scene motion must provide MP4 and WebM")
    if not isinstance(max_motion_bytes, int) or not 1000000 <= max_motion_bytes <= 5000000:
        raise ValueError("scene motion byte budget is invalid")
    if delivery_policy.get("source_footage_not_served_directly") is not True:
        raise ValueError("scene source footage must not be served directly")

    expected_sot_sha = hashlib.sha256(product_sot_bytes).hexdigest()
    if manifest.get("product_sot_sha256") != expected_sot_sha:
        raise ValueError("scene candidate manifest is not bound to the current product SOT")
    if manifest.get("production_stage") != "previsualization":
        raise ValueError(
            "candidate manifest must remain previsualization until scenes pass release evidence"
        )

    products = product_sot.get("products", {})
    collection_blueprints = blueprints.get("collections", {})
    if not isinstance(collection_blueprints, dict) or not collection_blueprints:
        raise ValueError("scene narrative blueprints have no collections")
    validate_founder_commerce_casts(collection_blueprints, products)
    candidates = manifest.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("scene candidate manifest has no candidates")

    approved = 0
    blocked_references = 0
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("scene candidate record is invalid")
        sku = candidate.get("sku")
        if sku not in products:
            raise ValueError(f"scene candidate uses unknown SKU: {sku}")
        collection = candidate.get("collection")
        if collection not in collection_blueprints:
            raise ValueError(f"scene candidate has no narrative blueprint: {collection}")
        if products[sku].get("identity", {}).get("collection") != collection:
            raise ValueError(f"scene candidate product crosses collection boundaries: {sku}")
        asset = resolve_asset(
            MANIFEST.parent, candidate.get("file"), label=f"{candidate.get('chapter')}: candidate"
        )
        if sha256(asset) != candidate.get("sha256"):
            raise ValueError(f"scene candidate asset hash drift: {candidate.get('chapter')}")

        responsive_assets = candidate.get("responsive_assets", {})
        if not isinstance(responsive_assets, dict):
            raise ValueError(f"scene responsive assets are invalid: {candidate.get('chapter')}")
        for viewport, responsive in responsive_assets.items():
            if not isinstance(responsive, dict):
                raise ValueError(
                    f"scene responsive asset is invalid: {candidate.get('chapter')} {viewport}"
                )
            responsive_path = resolve_asset(
                MANIFEST.parent,
                responsive.get("file"),
                label=f"{candidate.get('chapter')}: responsive {viewport}",
            )
            if sha256(responsive_path) != responsive.get("sha256"):
                raise ValueError(
                    f"scene responsive asset hash drift: {candidate.get('chapter')} {viewport}"
                )

        chapter = str(candidate.get("chapter", "unnamed"))
        motion_formats: set[str] = set()
        for bundle_name in ("motion_assets", "product_reveal_assets"):
            bundle = candidate.get(bundle_name, [])
            if not isinstance(bundle, list):
                raise ValueError(f"{chapter}: {bundle_name} is invalid")
            for index, record in enumerate(bundle, start=1):
                bundle_path = validate_asset_record(
                    record, label=f"{chapter}: {bundle_name}[{index}]"
                )
                if bundle_name == "motion_assets" and bundle_path.suffix.lower() in {
                    ".mp4",
                    ".webm",
                }:
                    if bundle_path.stat().st_size > max_motion_bytes:
                        raise ValueError(f"{chapter}: served motion exceeds the byte budget")
                    motion_formats.add(bundle_path.suffix.lower().lstrip("."))
                if bundle_name == "motion_assets" and "source-footage" in bundle_path.parts:
                    raise ValueError(
                        f"{chapter}: raw source footage is exposed as a served motion asset"
                    )
        if candidate.get("motion_assets") and motion_formats != set(required_motion_formats):
            raise ValueError(f"{chapter}: motion assets require MP4 and WebM")
        review_preview = candidate.get("review_preview")
        if review_preview is not None:
            preview_path = validate_asset_record(review_preview, label=f"{chapter}: review_preview")
            if preview_path.suffix.lower() == ".html":
                preview_source = preview_path.read_text(encoding="utf-8")
                for safety_attribute in ("muted", "loop", "playsinline", 'preload="metadata"'):
                    if safety_attribute not in preview_source:
                        raise ValueError(f"{chapter}: review preview lacks {safety_attribute}")

        status = candidate.get("status")
        if status not in {"founder_review_required", "revision_required", "founder_approved"}:
            raise ValueError(f"unsupported scene candidate status: {status}")

        authorized_hashes = product_reference_hashes(products[sku])
        references = candidate.get("product_references", [])
        blockers = candidate.get("provenance_blockers", [])
        if not isinstance(references, list) or not references:
            raise ValueError(
                f"scene candidate has no product references: {candidate.get('chapter')}"
            )
        if not isinstance(blockers, list):
            raise ValueError(
                f"scene candidate provenance blockers are invalid: {candidate.get('chapter')}"
            )
        for reference in references:
            path = (THEME / str(reference)).resolve()
            if path in authorized_hashes:
                if not path.is_file() or sha256(path) != authorized_hashes[path]:
                    raise ValueError(f"scene product reference hash drift: {sku} {reference}")
                continue
            if status != "revision_required" or reference not in blockers:
                raise ValueError(
                    f"scene candidate reference is outside product SOT: {sku} {reference}"
                )
            if not path.is_file():
                raise ValueError(f"blocked scene reference does not resolve: {sku} {reference}")
            blocked_references += 1

        if status == "founder_approved":
            approved += 1
            validate_approved_candidate(candidate, contract)

    print(
        f"Scene production contract valid: {len(candidates)} previsualizations, "
        f"{approved} fully approved, {blocked_references} blocked references, "
        "100 required in every category."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
