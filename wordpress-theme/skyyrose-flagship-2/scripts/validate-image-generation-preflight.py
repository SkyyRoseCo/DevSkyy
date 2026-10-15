#!/usr/bin/env python3
"""Fail-closed lineage and fidelity gate for a SkyyRose image-generation batch."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
THEME_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PROMPT = (
    THEME_DIR
    / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/image-model-prompts-v1.json"
)
PRODUCT_SOT = ROOT / "data/product-sot.json"
DEFAULT_RECEIPT = (
    THEME_DIR
    / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/preflight-v1/pass-ready-to-generate-receipt-v1.json"
)
JUDGE_AVAILABILITY = (
    THEME_DIR
    / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/preflight-v1/judge-availability-receipt-v1.json"
)
EXPECTED_JOBS = {"br-commerce-2-v3", "lh-commerce-1-v2", "sig-commerce-3-v3"}
ALLOWED_REFERENCE_APPROVALS = {"canonical_founder_product_proof", "canonical_logo_proof"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL {message}")


def root_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    require(path == ROOT or ROOT in path.parents, f"path escapes repository: {value}")
    return path


def audit_file(
    audit: dict[str, dict[str, Any]],
    path: Path,
    expected_hash: str,
    category: str,
) -> str:
    require(path.is_file(), f"{category} missing: {path.relative_to(ROOT)}")
    actual_hash = sha256(path)
    require(
        actual_hash == expected_hash,
        f"{category} hash mismatch: {path.relative_to(ROOT)}; expected {expected_hash}, got {actual_hash}",
    )
    relative = str(path.relative_to(ROOT))
    existing = audit.get(relative)
    if existing:
        require(existing["sha256"] == actual_hash, f"conflicting hashes for {relative}")
        if category not in existing["categories"]:
            existing["categories"].append(category)
    else:
        audit[relative] = {
            "path": relative,
            "sha256": actual_hash,
            "bytes": path.stat().st_size,
            "categories": [category],
        }
    return actual_hash


def all_reference_hashes(product: dict[str, Any]) -> set[str]:
    hashes = {item["sha256"] for item in product.get("references", [])}
    hashes.update(
        item["sha256"]
        for item in product.get("media", {}).values()
        if isinstance(item, dict) and item.get("sha256")
    )
    return hashes


def joined_text(product: dict[str, Any]) -> str:
    garment = product["garment"]
    parts = [garment.get("type_lock", ""), garment.get("branding_summary", "")]
    parts.extend(region.get("description", "") for region in garment.get("branding_regions", []))
    parts.extend(garment.get("negative_constraints", []))
    return " ".join(" ".join(parts).lower().split())


def validate_product_semantics(products: dict[str, Any]) -> None:
    br005 = joined_text(products["br-005"])
    require("silicone" in br005 and "raised" in br005, "br-005 lacks raised silicone truth")
    require("side body" in br005 or "side-body" in br005, "br-005 lacks side-body artwork truth")
    require(
        "sleeves remain" in br005 and "plain black" in br005, "br-005 does not lock plain sleeves"
    )

    br007 = joined_text(products["br-007"])
    require("narrow white" in br007, "br-007 lacks narrow white side-construction truth")
    require(
        "above the narrow white" in br007, "br-007 does not place Love Hurts above the white insert"
    )
    require(
        "final d" in br007 and "unobscured" in br007,
        "br-007 does not protect the final D in OAKLAND",
    )
    require(
        "zipper" in br007 and "side hand pockets" in br007,
        "br-007 pocket construction is incomplete",
    )

    lh004 = joined_text(products["lh-004"])
    require("satin" in lh004 and "lustrous" in lh004, "lh-004 does not lock lustrous satin")
    require("not a satin" not in lh004, "lh-004 still contains stale non-satin language")

    for sku in ("lh-002", "lh-006"):
        text = joined_text(products[sku])
        require("heart" in text and "rose" in text, f"{sku} lacks heart-and-roses logo truth")
        require(
            "wearer-left" in text or "wearer's-left" in text,
            f"{sku} lacks wearer-left thigh placement",
        )

    sg001 = joined_text(products["sg-001"])
    require(
        "blue" in sg001 and "lower wearer-left" in sg001,
        "sg-001 lacks lower wearer-left blue rose truth",
    )
    require("no sr monogram" in sg001, "sg-001 does not explicitly reject the stale SR monogram")

    sg005 = joined_text(products["sg-005"])
    require(
        "blue/cyan" in sg005 and "front-center-chest" in sg005,
        "sg-005 lacks blue/cyan center-chest truth",
    )


def validate_prompt_semantics(job_id: str, job: dict[str, Any]) -> None:
    positive = job["positive_prompt"].lower()
    negative = job["negative_prompt"].lower()
    invariants = " ".join(job["invariants"]).lower()
    combined = f"{positive} {negative} {invariants}"

    if job_id == "br-commerce-2-v3":
        for phrase in (
            "raised tonal silicone",
            "side-body",
            "sleeves remain plain black",
            "narrow white mesh",
            "above the narrow white",
            "final d in oakland",
        ):
            require(phrase in combined, f"{job_id} prompt omits required phrase: {phrase}")
        require(
            "no broad white" in negative,
            f"{job_id} negative prompt does not reject broad white panels",
        )

        require("no sleeve art" in negative, f"{job_id} negative prompt does not reject sleeve art")
    elif job_id == "lh-commerce-1-v2":
        for phrase in ("lustrous satin", "heart-and-roses composite", "wearer's left upper thigh"):
            require(phrase in combined, f"{job_id} prompt omits required phrase: {phrase}")
        require(
            "no matte cotton" in negative, f"{job_id} negative prompt does not reject matte cotton"
        )
        require(
            "no sr monogram" in negative, f"{job_id} negative prompt does not reject SR monogram"
        )
    elif job_id == "sig-commerce-3-v3":
        for phrase in ("surgical logo correction", "wearer's-left leg", "embroidered blue rose"):
            require(phrase in combined, f"{job_id} prompt omits required phrase: {phrase}")
        require(
            "no sr monogram" in negative, f"{job_id} negative prompt does not reject SR monogram"
        )
        require(
            "only lower wearer-left shorts logo changes" in invariants,
            f"{job_id} lacks measured edit-region invariant",
        )


def validate_localized_edit_controls(
    audit: dict[str, dict[str, Any]], job_id: str, job: dict[str, Any]
) -> None:
    """Reject semantic full-frame rewrites before a paid localized product edit."""
    controls = job.get("localized_edit_controls")
    require(isinstance(controls, dict), f"{job_id} lacks localized_edit_controls")
    require(
        controls.get("provider_operation") == "explicit_mask_edit",
        f"{job_id} is not routed through an explicit-mask provider operation",
    )
    require(
        controls.get("mask_polarity") == "white_is_editable_black_is_locked",
        f"{job_id} mask polarity is missing or unsafe",
    )
    require(
        controls.get("outside_mask_changed_pixels") == 0,
        f"{job_id} does not require zero outside-mask drift",
    )
    require(
        controls.get("semantic_review_required") is True,
        f"{job_id} does not require post-generation logo/construction review",
    )
    mask = controls.get("mask")
    require(isinstance(mask, dict), f"{job_id} mask binding is missing")
    mask_path = root_path(mask.get("path", ""))
    audit_file(audit, mask_path, mask.get("sha256", ""), f"{job_id}_editable_mask")

    targets = [item for item in job["input_images"] if item["role"] == "edit_target"]
    require(len(targets) == 1, f"{job_id} must have exactly one edit target before mask validation")
    target_path = root_path(targets[0]["path"])
    with Image.open(target_path) as opened:
        target = ImageOps.exif_transpose(opened)
    with Image.open(mask_path) as opened:
        mask_image = ImageOps.exif_transpose(opened)
    require(mask_image.size == target.size, f"{job_id} mask dimensions do not match edit target")
    require(mask_image.mode in {"L", "1"}, f"{job_id} mask must be a grayscale canonical mask")
    extrema = mask_image.getextrema()
    require(
        extrema[0] == 0 and extrema[1] == 255,
        f"{job_id} mask must contain locked and editable pixels",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    # A certification attempt invalidates any older pass before reviewing the
    # current lineage. A failed rerun must never leave a stale green receipt.
    if args.write_receipt and args.receipt.exists():
        args.receipt.unlink()

    prompt_path = args.prompt.resolve()
    require(
        prompt_path.suffix.lower() in {".json", ".html"}, "prompt contract must be .json or .html"
    )
    require(
        prompt_path.suffix.lower() == ".json",
        "this validator currently requires the executable JSON contract",
    )
    require(prompt_path.is_file(), f"prompt contract missing: {prompt_path}")

    prompt = load_json(prompt_path)
    product_sot = load_json(PRODUCT_SOT)
    products = product_sot["products"]
    audit: dict[str, dict[str, Any]] = {}
    product_sot_hash = sha256(PRODUCT_SOT)
    audit_file(audit, PRODUCT_SOT, product_sot_hash, "current_product_sot")
    require(
        prompt["schema"] == "skyyrose.image-model-prompt-contract.v2",
        "stale prompt-contract schema",
    )
    require(
        prompt["product_sot_sha256"] == product_sot_hash,
        "prompt contract is stale against current product SOT",
    )

    active_jobs = prompt.get("active_generation_jobs", [])
    require(len(active_jobs) == len(set(active_jobs)), "duplicate active generation job")
    require(
        set(active_jobs) == EXPECTED_JOBS, f"active job set must be exactly {sorted(EXPECTED_JOBS)}"
    )
    require(
        set(prompt.get("generation_jobs", {})) == EXPECTED_JOBS,
        "generation_jobs contains stale or missing jobs",
    )

    tournament_binding = prompt["tournament_policy"]
    tournament_path = root_path(tournament_binding["path"])
    audit_file(
        audit,
        tournament_path,
        tournament_binding["sha256"],
        "mandatory_adversarial_tournament_policy",
    )
    tournament = load_json(tournament_path)
    require(
        tournament["schema"] == "skyyrose.image-generation-tournament-policy.v1",
        "stale tournament policy schema",
    )
    require(
        tournament["required_vision_judges"] == ["gpt-5.5-pro", "gemini-3.1-pro-preview"],
        "wrong required vision judges",
    )
    require(tournament["synthesis_model"] == "claude-opus-5", "wrong synthesis model")
    require(tournament["minimum_each_vision_score"] == 95, "vision threshold must remain 95")
    require(tournament["minimum_final_score"] == 98, "final threshold must remain 98")
    require(
        tournament["required_hallucination_veto_result"] is False,
        "hallucination veto must resolve false",
    )
    require(tournament["all_judges_available"] is True, "all judges must be available")
    require(
        tournament["unverifiable_required_regions"] == 0, "all required regions must be verifiable"
    )
    require(
        tournament["source_hashes_current"] is True, "tournament must require current source hashes"
    )
    require(
        tournament["founder_approval_required"] is True, "founder approval must remain required"
    )
    require(
        JUDGE_AVAILABILITY.is_file(),
        "judge-availability receipt missing; run verify-image-judge-availability.py",
    )
    availability_hash = sha256(JUDGE_AVAILABILITY)
    audit_file(audit, JUDGE_AVAILABILITY, availability_hash, "live_required_judge_availability")
    availability = load_json(JUDGE_AVAILABILITY)
    require(
        availability["schema"] == "skyyrose.image-judge-availability.v1",
        "stale judge-availability schema",
    )
    require(
        availability["status"] == "PASS_ALL_JUDGES_AVAILABLE",
        "one or more required tournament judges are unavailable",
    )
    require(
        availability["all_judges_available"] is tournament["all_judges_available"] is True,
        "judge availability disagrees with policy",
    )
    require(
        [item["model"] for item in availability["judges"]]
        == ["gpt-5.5-pro", "gemini-3.1-pro-preview", "claude-opus-5"],
        "judge-availability receipt covers the wrong models",
    )

    proof_manifest_binding = prompt["proof_binding"]["manifest"]
    proof_manifest_path = root_path(proof_manifest_binding["path"])
    audit_file(audit, proof_manifest_path, proof_manifest_binding["sha256"], "proof_manifest")
    proof = load_json(proof_manifest_path)
    require(
        proof["schema"] == "skyyrose.image-generation-product-proof.v1",
        "stale proof-manifest schema",
    )
    require(
        proof["stage"] == prompt["proof_binding"]["required_stage"] == "BEFORE_PROMPT_AUTHORING",
        "proof board was not built before prompt authoring",
    )
    require(
        proof["approval_state"] == "INPUT_EVIDENCE_ONLY_NOT_GENERATED",
        "proof manifest has unsafe approval state",
    )
    require(
        proof["product_sot"]["sha256"] == product_sot_hash,
        "proof manifest is stale against current product SOT",
    )

    board_binding = prompt["proof_binding"]["board"]
    board_path = root_path(board_binding["path"])
    audit_file(audit, board_path, board_binding["sha256"], "visually_reviewed_product_proof_board")
    proof_board_path = (THEME_DIR / proof["board"]["file"]).resolve()
    require(proof_board_path == board_path, "prompt and proof manifest bind different proof boards")
    require(proof["board"]["sha256"] == board_binding["sha256"], "proof board hash disagreement")

    proof_by_source: dict[str, dict[str, Any]] = {}
    for item in proof["items"]:
        source = item["source"]
        require(source not in proof_by_source, f"duplicate proof source: {source}")
        proof_by_source[source] = item
        audit_file(audit, root_path(source), item["sha256"], "founder_product_or_logo_proof")
        for sku in item["skus"]:
            require(sku in products, f"proof references unknown SKU: {sku}")
            require(
                item["product_hashes"][sku] == products[sku]["product_hash"],
                f"proof has stale product hash for {sku}",
            )
            require(
                item["sha256"] in all_reference_hashes(products[sku]),
                f"proof file is no longer canonical for {sku}: {source}",
            )

    bound_skus = {
        sku for job in prompt["generation_jobs"].values() for sku in job["product_bindings"]
    }
    require(
        bound_skus == {"br-005", "br-007", "lh-004", "lh-002", "lh-006", "sg-001", "sg-005"},
        "unexpected SKU coverage",
    )
    validate_product_semantics(products)

    # Review every dossier and canonical reference that can feed a bound SKU,
    # not only the subset selected by the prompt author.
    for sku in sorted(bound_skus):
        product = products[sku]
        require(
            product["verification"]["record_complete"] is True,
            f"{sku} product record is incomplete",
        )
        require(
            product["verification"]["proof_level"] == "physical_product_photo",
            f"{sku} lacks physical-product proof",
        )
        require(
            product["verification"]["no_visual_invention_allowed"] is True,
            f"{sku} allows visual invention",
        )
        dossier = root_path(product["source"]["dossier"])
        audit_file(audit, dossier, product["source"]["dossier_sha256"], f"{sku}_canonical_dossier")
        roles: set[str] = set()
        for reference in product.get("references", []):
            role = reference["role"]
            require(role not in roles, f"{sku} has duplicate canonical reference role: {role}")
            roles.add(role)
            audit_file(
                audit,
                root_path(reference["path"]),
                reference["sha256"],
                f"{sku}_canonical_reference",
            )

    consumed_proof_sources: set[str] = set()
    for job_id in active_jobs:
        job = prompt["generation_jobs"][job_id]
        require(job["status"] == "READY_FOR_PREFLIGHT", f"{job_id} is not ready for preflight")
        require(job["model"] == "gpt-image-2", f"{job_id} uses an unexpected model")
        require(job["operation"] == "edit", f"{job_id} is not a reference-bound edit")
        require(
            job["output"]
            == {
                "format": "png",
                "background": "transparent",
                "approval_state": "FOUNDER_REVIEW_REQUIRED",
            },
            f"{job_id} has unsafe output settings",
        )
        require(job.get("positive_prompt", "").strip(), f"{job_id} positive prompt is empty")
        require(job.get("negative_prompt", "").strip(), f"{job_id} negative prompt is empty")
        require(job.get("invariants"), f"{job_id} invariants are empty")
        validate_prompt_semantics(job_id, job)

        roles: set[str] = set()
        edit_target_count = 0
        input_hashes: set[str] = set()
        for item in job["input_images"]:
            role = item["role"]
            require(role not in roles, f"{job_id} has duplicate input role: {role}")
            roles.add(role)
            edit_target_count += role == "edit_target"
            require(
                item["sha256"] not in input_hashes,
                f"{job_id} passes the same file under multiple roles",
            )
            input_hashes.add(item["sha256"])
            audit_file(audit, root_path(item["path"]), item["sha256"], f"{job_id}_{role}")
            if role == "edit_target":
                require(
                    "correction_only" in item["approval"],
                    f"{job_id} edit target lacks correction-only scope",
                )
            else:
                require(
                    item["approval"] in ALLOWED_REFERENCE_APPROVALS,
                    f"{job_id} passes an unapproved reference: {item['path']}",
                )
                require(
                    item["path"] in proof_by_source,
                    f"{job_id} reference was not visualized before prompting: {item['path']}",
                )
        require(edit_target_count == 1, f"{job_id} must have exactly one edit target")
        validate_localized_edit_controls(audit, job_id, job)

        for sku, product_hash in job["product_bindings"].items():
            require(
                products[sku]["product_hash"] == product_hash,
                f"{job_id} has stale product hash for {sku}",
            )
        proof_sources = set(job["proof_sources"])
        require(proof_sources, f"{job_id} has no proof sources")
        require(proof_sources <= set(proof_by_source), f"{job_id} names an unknown proof source")
        reference_paths = {
            item["path"] for item in job["input_images"] if item["role"] != "edit_target"
        }
        require(
            proof_sources == reference_paths,
            f"{job_id} proof sources and model reference inputs differ",
        )
        consumed_proof_sources.update(proof_sources)

    require(
        consumed_proof_sources == set(proof_by_source),
        "one or more proof-board files are stale or unused by this batch",
    )

    prompt_hash = sha256(prompt_path)
    audit_file(audit, prompt_path, prompt_hash, "executable_prompt_contract")
    receipt = {
        "schema": "skyyrose.image-generation-preflight-receipt.v1",
        "status": "PASS_READY_TO_GENERATE",
        "generated_at": datetime.now(UTC).isoformat(),
        "prompt_contract": {"path": str(prompt_path.relative_to(ROOT)), "sha256": prompt_hash},
        "product_sot": {"path": str(PRODUCT_SOT.relative_to(ROOT)), "sha256": product_sot_hash},
        "proof_manifest": {
            "path": str(proof_manifest_path.relative_to(ROOT)),
            "sha256": sha256(proof_manifest_path),
        },
        "proof_board": {"path": str(board_path.relative_to(ROOT)), "sha256": sha256(board_path)},
        "tournament_policy": {
            "path": str(tournament_path.relative_to(ROOT)),
            "sha256": sha256(tournament_path),
        },
        "judge_availability": {
            "path": str(JUDGE_AVAILABILITY.relative_to(ROOT)),
            "sha256": availability_hash,
        },
        "active_generation_jobs": active_jobs,
        "bound_skus": sorted(bound_skus),
        "reviewed_file_count": len(audit),
        "reviewed_files": sorted(audit.values(), key=lambda item: item["path"]),
        "downstream_state": "GENERATION_ALLOWED_COMPOSITOR_BLOCKED_PENDING_TWO_VISION_JUDGES_AND_SYNTHESIS",
    }
    if args.write_receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        "PASS_READY_TO_GENERATE "
        f"jobs={len(active_jobs)} skus={len(bound_skus)} reviewed_files={len(audit)} "
        f"prompt_sha256={prompt_hash}"
    )
    if not args.write_receipt:
        print("NOTE receipt not written; rerun with --write-receipt before generation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
