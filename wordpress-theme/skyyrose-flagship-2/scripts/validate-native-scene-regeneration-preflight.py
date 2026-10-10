#!/usr/bin/env python3
"""Validate the LH-COMMERCE-1 native-scene planning package fail closed.

The default mode certifies only that the prompt-planning contract is internally
consistent and bound to current bytes.  ``--generation-gate`` is a deliberately
fail-closed assertion for this planning-only schema: it reports every blocker
and never issues generation authority.  A separate, future generation-release
schema must bind fresh founder authorization, measured safe zones, current
tracked references, and live required judges before any image request is sent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
THEME_DIR = Path(__file__).resolve().parent.parent
SCENE_ROOT = THEME_DIR / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1"
DEFAULT_CONTRACT = (
    SCENE_ROOT / "preflight-v1/vision-authored-prompts/"
    "lh-commerce-1-native-scene-regeneration-plan-v1.json"
)
DEFAULT_RECEIPT = SCENE_ROOT / "preflight-v1/lh-commerce-1-native-scene-planning-validation-v1.json"
RECEIPT_ROOT = SCENE_ROOT / "preflight-v1"
JUDGE_RECEIPT_MAX_AGE = timedelta(minutes=15)

EXPECTED_GENERATOR_ROLE_ORDER = [
    "locked_environment_composition_reference",
    "approved_two_model_identity_pose_and_product_placement_reference",
    "canonical_lh_004_physical_product_reference",
    "canonical_lh_002_physical_product_reference",
    "canonical_lh_006_physical_product_reference",
    "canonical_heart_rose_thigh_mark_reference",
]
EXPECTED_GENERATOR_ROLES = set(EXPECTED_GENERATOR_ROLE_ORDER)
EXPECTED_EVIDENCE_ROLES = {
    "patched_model_lineage_receipt",
    "protected_model_lineage_receipt",
    "product_proof_manifest",
    "product_proof_contact_sheet",
    "mandatory_tournament_policy",
    "live_judge_availability_receipt",
    "lh_004_canonical_dossier",
    "lh_002_canonical_dossier",
    "lh_006_canonical_dossier",
}
EXPECTED_CURRENT_PRODUCT_SOT_BINDING = {
    "role": "current_product_sot",
    "usage": "validation_only",
    "path": "data/product-sot.json",
    "sha256": "4ccfbe18aba2846c8406f1f0d34853158e563601051527a47f8e401a71beea12",
}
EXPECTED_STATIC_EVIDENCE_BINDINGS = [
    {
        "role": "patched_model_lineage_receipt",
        "usage": "validation_only",
        "path": (
            "wordpress-theme/skyyrose-flagship-2/assets/scroll-world/generated-candidates/"
            "founder-commerce-scenes-v1/limited-pro-v1/"
            "lh-commerce-1-pro-session-logo-patched-v2.receipt.json"
        ),
        "sha256": "f94e6b7abb1324d6c633ae92204131e09ec69652afc63814838fef40c68952ee",
    },
    {
        "role": "protected_model_lineage_receipt",
        "usage": "validation_only",
        "path": (
            "wordpress-theme/skyyrose-flagship-2/assets/scroll-world/generated-candidates/"
            "founder-commerce-scenes-v1/limited-pro-v1/"
            "lh-commerce-1-pro-session-generated-protected-v1.receipt.json"
        ),
        "sha256": "9a0872ea0e5f8a0236907715ac7bc07a5cfc8e57a03c26d0e9fae0dff6ba2221",
    },
    {
        "role": "product_proof_manifest",
        "usage": "validation_only",
        "path": (
            "wordpress-theme/skyyrose-flagship-2/assets/scroll-world/generated-candidates/"
            "founder-commerce-scenes-v1/preflight-v1/product-proof-manifest-v1.json"
        ),
        "sha256": "bbc431f8ee5e0826d9ff15d8cce68637784da780e03c6e5b738ecf16d595f8bf",
    },
    {
        "role": "product_proof_contact_sheet",
        "usage": "validation_only",
        "path": (
            "wordpress-theme/skyyrose-flagship-2/assets/scroll-world/generated-candidates/"
            "founder-commerce-scenes-v1/preflight-v1/product-proof-board-v1.png"
        ),
        "sha256": "18134718710facfed7ea247fc8c43cf0cfdc397f4fda76ca1ce42b07d29c6e53",
    },
    {
        "role": "mandatory_tournament_policy",
        "usage": "validation_only",
        "path": "wordpress-theme/skyyrose-flagship-2/data/image-generation-tournament-policy-v1.json",
        "sha256": "e146dc140ac25fabf885dcc86300f60fbc1f2a6bf4d94a26f18c8cb589872da4",
    },
    {
        "role": "lh_004_canonical_dossier",
        "usage": "validation_only",
        "path": "wordpress-theme/skyyrose-flagship/data/dossiers/love-hurts-bomber-jacket.md",
        "sha256": "133a5535541782f89d2fe8f43d560b50deebf1a91cd2367abcf1169c6d5c1e4e",
    },
    {
        "role": "lh_002_canonical_dossier",
        "usage": "validation_only",
        "path": "wordpress-theme/skyyrose-flagship/data/dossiers/love-hurts-joggers.md",
        "sha256": "b531f6634fa54726b2f0740c7bed4530754f1f8469f3270a7d0e78b7756c5eb0",
    },
    {
        "role": "lh_006_canonical_dossier",
        "usage": "validation_only",
        "path": "wordpress-theme/skyyrose-flagship/data/dossiers/love-hurts-joggers-white.md",
        "sha256": "b61eab3f92fabba681ddc0253d74ba74c839a22b4be8fc5a6f2ab70eb020822a",
    },
]
DYNAMIC_JUDGE_EVIDENCE_BINDING = {
    "role": "live_judge_availability_receipt",
    "usage": "validation_only",
    "path": (
        "wordpress-theme/skyyrose-flagship-2/assets/scroll-world/generated-candidates/"
        "founder-commerce-scenes-v1/preflight-v1/judge-availability-receipt-v1.json"
    ),
}
EXPECTED_TOURNAMENT_POLICY = {
    "schema": "skyyrose.image-generation-tournament-policy.v1",
    "required_vision_judges": ["gpt-5.5-pro"],
    "synthesis_model": None,
    "minimum_each_vision_score": 95,
    "minimum_final_score": 95,
    "required_hallucination_veto_result": False,
    "all_judges_available": True,
    "unverifiable_required_regions": 0,
    "source_hashes_current": True,
    "founder_approval_required": True,
    "evaluation_scope": "every generated output in every image-generation batch",
    "review_authorities": ["gpt-5.5-pro", "founder"],
    "downstream_rule": (
        "all outputs must pass GPT vision review and explicit founder approval before compositing"
    ),
}
EXPECTED_PRODUCTS = {
    "lh-004": "c379ded98f2a9203848f4b996ecc0f2f96f637254e0abc206718bd2317523a69",
    "lh-002": "9443f3752197f9c541ee9dca4254d923876edd4c9f4f2000b0101f5cc20cdaed",
    "lh-006": "279787da0b0a41cf8ca41f8825721a8b725af239586461b34e90c1f33e045079",
}
EXPECTED_BREAKPOINTS = {"desktop", "tablet", "mobile"}
EXPECTED_REGION_GATES = {
    "lh004_satin_and_color_blocking",
    "lh004_front_construction_and_branding",
    "lh002_body_side_panels_and_drawstring",
    "lh002_left_thigh_mark",
    "lh006_body_side_panels_and_drawstring",
    "lh006_left_thigh_mark",
    "model_identity_and_anatomy",
}
EXPECTED_REJECTION_RULES = {
    "STALE_SOURCE_OR_HASH",
    "UNTRACKED_GENERATION_REFERENCE",
    "AMBIGUOUS_OR_DUPLICATE_INPUT_ROLE",
    "MISSING_EXACT_PRODUCT_REGION",
    "PRODUCT_CONSTRUCTION_OR_MATERIAL_DRIFT",
    "LOGO_TEXT_PLACEMENT_SCALE_OR_TECHNIQUE_DRIFT",
    "MODEL_IDENTITY_POSE_OR_ANATOMY_DRIFT",
    "PASTED_CUTOUT_OR_EDGE_HALO",
    "FLOATING_FEET_OR_FLOOR_PLANE_FAILURE",
    "IMPOSSIBLE_SHADOW_OR_REFLECTION",
    "INCONSISTENT_LIGHT_OR_MATERIAL_RESPONSE",
    "DEPTH_GRAIN_OR_OPTICS_MISMATCH",
    "HERO_ROSE_BLOCKED_OR_DEEMPHASIZED",
    "UI_SAFE_ZONE_COLLISION",
    "UNVERIFIABLE_REQUIRED_REGION",
    "TOURNAMENT_OR_FOUNDER_APPROVAL_MISSING",
}
RASTER_ONLY_VERDICTS = {
    "VALIDATED_INCOMPATIBLE",
    "NO_OBSERVED_CONTRADICTION",
    "UNRESOLVABLE",
}
EXPECTED_CALIBRATION_RECORDS = {
    "required_asset_roles": [
        "locked_environment_composition_reference",
        "approved_two_model_identity_pose_and_product_placement_reference",
    ],
    "records": [],
    "authority_state": "ABSENT_NO_RELIGHT_AUTHORITY",
    "all_records_must_be_hash_verified": True,
}
EXPECTED_NATIVE_SCENE_REQUIREMENTS = {
    "camera": {
        "single_lens_single_exposure_intent": True,
        "preserve_plate_aspect_ratio": "1672:941",
        "preserve_central_cathedral_vanishing_point": True,
        "preserve_aisle_and_pew_perspective": True,
        "reject_horizon_or_architecture_drift": True,
    },
    "floor": {
        "models_share_one_solved_floor_plane": True,
        "both_shoes_make_visible_contact": True,
        "no_plate_texture_may_continue_through_soles": True,
        "reflection_strength_must_not_exceed_observed_floor_gloss": True,
    },
    "pose_relationship": {
        "two_models_remain_a_single_fashion_pair": True,
        "retain_approved_identity_and_front_product_readability": True,
        "anatomy_may_not_change": True,
        "hands_may_not_hide_required_product_regions": True,
        "garments_may_not_merge_or_swap_between_models": True,
    },
    "occlusion": {
        "required_product_regions_must_be_verifiable": True,
        "enchanted_rose_max_occlusion_fraction": 0.15,
        "models_may_receive_natural_environment_occlusion_only_if_no_product_gate_is_hidden": True,
        "no_ui_safe_zone_intersection": True,
    },
    "lighting": {
        "author_scene_as_one_native_exposure": True,
        "respect_overhead_aisle_beam_warm_practicals_red_environment_bounce_and_atmospheric_falloff": True,
        "do_not_copy_or_infer_a_protected_pixel_relight_field_from_the_current_raster_pair": True,
        "product_material_response_must_remain_truthful": True,
        "white_and_black_bomber_panels_must_read_as_lustrous_satin": True,
        "joggers_must_read_as_cotton_fleece_not_satin": True,
        "faces_may_not_be_relit_as_a_postprocess": True,
    },
    "shadows": {
        "contact_shadow_required_under_every_shoe": True,
        "cast_shadow_direction_penumbra_density_and_lobe_count_must_not_contradict_plate_exemplars": True,
        "generic_centered_drop_shadow_forbidden": True,
        "floating_feet_fatal": True,
    },
    "reflections": {
        "floor_reflections_must_reproject_through_the_same_floor_plane": True,
        "reflection_is_vertically_compressed_distance_blurred_and_floor_tinted": True,
        "mirror_clone_reflection_forbidden": True,
        "reflection_may_not_invent_product_detail": True,
    },
    "depth_and_atmosphere": {
        "models_match_depth_of_field_at_placement_depth": True,
        "haze_may_wrap_around_but_not_hide_product_regions": True,
        "foreground_midground_and_rose_depth_order_must_remain_legible": True,
    },
    "grain_and_optics": {
        "one_shared_full_frame_grain_field": True,
        "grain_scale_matches_plate": True,
        "vignette_chromatic_aberration_highlight_rolloff_and_edge_sharpness_are_shared": True,
        "hard_alpha_halo_and_mismatched_edge_sharpness_are_fatal": True,
    },
    "hero_rose": {
        "role": "co_equal_emotional_focal_point",
        "must_remain_under_glass": True,
        "must_remain_recognizable": True,
        "minimum_saliency_ratio_vs_dominant_model": 0.8,
        "max_occlusion_fraction": 0.15,
    },
}
SEALED_SECTION_SHA256 = {
    "product_bindings": "e5de2378022e71963766b853c97f41487420dae32a2bd1d4f30c3e94fdec0d73",
    "native_scene_requirements": "8e9edbd3b7feb4f5afffab4000b121ea60417e7059f70162197388efbe6009ba",
    "prompt_payload": "6d0e2232ff88684f65a7425e37fcf39612fefbf5a30e79b831d3af3a4d38cd3a",
    "per_region_fidelity_checks": "f62dd67e0726eac90aedf081a4ebb377efd7787b13091e0eeb6b6582b948ad87",
    "batch_and_review_contract": "143672a0b6846f6696d48955c7ea9d450f98f9db7882978691b46bb48d8acd4a",
    "output_contract": "7731ab99563d7faa3ac542016eae69a20fe57adf443a188954ea560a8057d639",
    "pre_generation_gates": "ed655aa7ee964a1bfc05b7ae2278c633b73a837b2aebf5cbd77ac71937df1e0f",
}
SEALED_GENERATOR_REFERENCES_SHA256 = (
    "cf482301e98f71a981e1628207410e69719b1cc862e2fc09a80cb4a32d6eda40"
)


class ValidationError(ValueError):
    """Raised when a planning invariant or source binding fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def strict_equal(actual: Any, expected: Any) -> bool:
    """Compare JSON-like values without Python's bool/int aliasing."""

    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            strict_equal(actual[key], expected[key]) for key in expected
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            strict_equal(actual_item, expected_item)
            for actual_item, expected_item in zip(actual, expected, strict=True)
        )
    return actual == expected


def canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_binding_manifest_contract(bindings: dict[str, Any]) -> None:
    """Pin transitive inputs; review-policy and live-judge hashes rotate explicitly."""

    require(
        strict_equal(bindings.get("current_product_sot"), EXPECTED_CURRENT_PRODUCT_SOT_BINDING),
        "current product SOT binding drifted from its canonical path or hash",
    )
    evidence_items = bindings.get("validation_only_evidence")
    require(isinstance(evidence_items, list), "validation-only evidence list is malformed")
    evidence_paths = [item.get("path") for item in evidence_items if isinstance(item, dict)]
    require(
        len(evidence_paths) == len(evidence_items),
        "validation-only evidence item is malformed",
    )
    require(
        len(evidence_paths) == len(set(evidence_paths)),
        "duplicate validation-only evidence path",
    )

    rotating_roles = {
        DYNAMIC_JUDGE_EVIDENCE_BINDING["role"],
        "mandatory_tournament_policy",
    }
    static_items = [item for item in evidence_items if item.get("role") not in rotating_roles]
    expected_static_items = [
        item
        for item in EXPECTED_STATIC_EVIDENCE_BINDINGS
        if item.get("role") != "mandatory_tournament_policy"
    ]
    require(
        strict_equal(static_items, expected_static_items),
        "static validation-only evidence manifest drifted",
    )
    policy_items = [
        item for item in evidence_items if item.get("role") == "mandatory_tournament_policy"
    ]
    require(len(policy_items) == 1, "tournament policy binding must appear exactly once")
    canonical_policy_binding = next(
        item
        for item in EXPECTED_STATIC_EVIDENCE_BINDINGS
        if item.get("role") == "mandatory_tournament_policy"
    )
    policy_item = policy_items[0]
    require(
        {key: policy_item.get(key) for key in ("role", "usage", "path")}
        == {key: canonical_policy_binding.get(key) for key in ("role", "usage", "path")},
        "tournament policy binding path or usage drifted",
    )
    require(
        isinstance(policy_item.get("sha256"), str) and len(policy_item["sha256"]) == 64,
        "tournament policy binding has invalid sha256",
    )
    dynamic_items = [
        item
        for item in evidence_items
        if item.get("role") == DYNAMIC_JUDGE_EVIDENCE_BINDING["role"]
    ]
    require(len(dynamic_items) == 1, "dynamic judge evidence binding must appear exactly once")
    dynamic = dynamic_items[0]
    require(
        set(dynamic) == {*DYNAMIC_JUDGE_EVIDENCE_BINDING, "sha256"},
        "dynamic judge evidence binding has unexpected fields",
    )
    require(
        strict_equal(
            {key: dynamic.get(key) for key in DYNAMIC_JUDGE_EVIDENCE_BINDING},
            DYNAMIC_JUDGE_EVIDENCE_BINDING,
        ),
        "dynamic judge evidence binding path or usage drifted",
    )
    dynamic_hash = dynamic.get("sha256")
    require(
        isinstance(dynamic_hash, str)
        and len(dynamic_hash) == 64
        and all(character in "0123456789abcdef" for character in dynamic_hash),
        "dynamic judge evidence binding has invalid sha256",
    )


def resolve_receipt_path(value: Path) -> Path:
    """Confine receipts to the scene preflight directory without symlink escape."""

    candidate = value if value.is_absolute() else ROOT / value
    require(candidate.suffix.lower() == ".json", "receipt path must end in .json")
    require(not candidate.is_symlink(), "receipt path may not be a symlink")
    resolved = candidate.resolve(strict=False)
    receipt_root = RECEIPT_ROOT.resolve()
    require(
        resolved.parent == receipt_root or receipt_root in resolved.parent.parents,
        "receipt path must stay inside the native-scene preflight directory",
    )
    return resolved


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    """Atomically replace a receipt only after validation succeeds."""

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


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def root_path(value: str) -> Path:
    require(
        bool(value) and not Path(value).is_absolute(),
        f"bound path must be repository-relative: {value}",
    )
    path = (ROOT / value).resolve()
    require(path == ROOT or ROOT in path.parents, f"bound path escapes repository: {value}")
    return path


def is_git_tracked(path: Path) -> bool:
    relative = str(path.relative_to(ROOT))
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", relative],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def normalize_mode(mode: str) -> str:
    return "RGBA" if "A" in mode else "RGB"


def audit_binding(
    item: dict[str, Any],
    category: str,
    *,
    rotating_hash_allowed: bool = False,
) -> dict[str, Any]:
    require(item.get("usage") == category, f"wrong usage for role {item.get('role')}")
    path = root_path(item["path"])
    require(path.is_file(), f"missing bound input: {item['path']}")
    actual_hash = sha256(path)
    if not rotating_hash_allowed:
        require(actual_hash == item.get("sha256"), f"stale hash for {item['path']}")
    audit: dict[str, Any] = {
        "role": item["role"],
        "usage": category,
        "path": item["path"],
        "sha256": actual_hash,
        "bytes": path.stat().st_size,
        "git_tracked": is_git_tracked(path),
    }
    if category == "generator_conditioning":
        require(
            path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"},
            f"generator input is not an image: {item['path']}",
        )
        with Image.open(path) as image:
            actual_dimensions = [image.width, image.height]
            actual_mode = normalize_mode(image.mode)
        require(actual_dimensions == item.get("dimensions"), f"dimension drift for {item['path']}")
        require(actual_mode == item.get("color_mode"), f"color-mode drift for {item['path']}")
        audit["dimensions"] = actual_dimensions
        audit["color_mode"] = actual_mode
    return audit


def product_reference_pairs(product: dict[str, Any]) -> set[tuple[str, str]]:
    pairs = {
        (item["path"], item["sha256"])
        for item in product.get("references", [])
        if isinstance(item, dict) and item.get("path") and item.get("sha256")
    }
    pairs.update(
        (item["path"], item["sha256"])
        for item in product.get("media", {}).values()
        if isinstance(item, dict) and item.get("path") and item.get("sha256")
    )
    return pairs


def validate_product_bindings(
    contract: dict[str, Any],
    product_sot: dict[str, Any],
    generator_items: list[dict[str, Any]],
) -> None:
    bindings = contract.get("product_bindings", {})
    require(set(bindings) == set(EXPECTED_PRODUCTS), "product binding set drifted")
    products = product_sot.get("products", {})
    by_role = {item["role"]: item for item in generator_items}

    for sku, expected_hash in EXPECTED_PRODUCTS.items():
        require(sku in products, f"current product SOT is missing {sku}")
        require(
            products[sku].get("product_hash") == expected_hash,
            f"current product hash drifted for {sku}",
        )
        require(
            bindings[sku].get("product_hash") == expected_hash,
            f"contract product hash drifted for {sku}",
        )
        require(
            bindings[sku].get("required_regions"), f"required product regions are empty for {sku}"
        )
        require(bindings[sku].get("forbidden_drift"), f"forbidden drift is empty for {sku}")
        require(
            products[sku].get("verification", {}).get("no_visual_invention_allowed") is True,
            f"{sku} permits visual invention",
        )

    role_to_sku = {
        "canonical_lh_004_physical_product_reference": "lh-004",
        "canonical_lh_002_physical_product_reference": "lh-002",
        "canonical_lh_006_physical_product_reference": "lh-006",
    }
    for role, sku in role_to_sku.items():
        item = by_role[role]
        require(
            (item["path"], item["sha256"]) in product_reference_pairs(products[sku]),
            f"{role} is not canonical for {sku} in current product SOT",
        )

    logo_item = by_role["canonical_heart_rose_thigh_mark_reference"]
    for sku in ("lh-002", "lh-006"):
        require(
            (logo_item["path"], logo_item["sha256"]) in product_reference_pairs(products[sku]),
            f"canonical thigh mark is stale or non-canonical for {sku}",
        )


def validate_receipt_lineage(
    evidence_by_role: dict[str, dict[str, Any]],
    generator_by_role: dict[str, dict[str, Any]],
    product_sot_hash: str,
) -> dict[str, Any]:
    patched_receipt = load_json(
        root_path(evidence_by_role["patched_model_lineage_receipt"]["path"])
    )
    model = generator_by_role["approved_two_model_identity_pose_and_product_placement_reference"]
    require(
        patched_receipt.get("output") == model["path"],
        "patched receipt points to a different model layer",
    )
    require(
        patched_receipt.get("output_sha256") == model["sha256"],
        "patched receipt output hash drifted",
    )
    require(
        patched_receipt.get("changed_pixels_outside_allowed_rois") == 0,
        "patched receipt changed pixels outside allowed regions",
    )
    require(
        patched_receipt.get("all_non_logo_pixels_preserved") is True,
        "patched receipt does not preserve non-logo pixels",
    )
    require(
        model.get("bound_machine_receipt_approval_state") == patched_receipt.get("approval_state"),
        "model reference misstates its bound machine approval state",
    )
    require(
        model.get("machine_founder_approval_record_present") is False,
        "planning contract invents a machine founder-approval record",
    )

    protected_receipt = load_json(
        root_path(evidence_by_role["protected_model_lineage_receipt"]["path"])
    )
    require(
        protected_receipt.get("rgb_preserved") is True,
        "protected model receipt does not preserve RGB",
    )
    require(
        protected_receipt.get("output_sha256") == patched_receipt.get("source_sha256"),
        "protected and patch receipt chain is broken",
    )

    proof = load_json(root_path(evidence_by_role["product_proof_manifest"]["path"]))
    require(
        proof.get("schema") == "skyyrose.image-generation-product-proof.v1",
        "wrong proof manifest schema",
    )
    require(
        proof.get("stage") == "BEFORE_PROMPT_AUTHORING",
        "proof board was not built before prompt authoring",
    )
    require(
        proof.get("approval_state") == "INPUT_EVIDENCE_ONLY_NOT_GENERATED",
        "unsafe proof-manifest approval state",
    )
    require(
        proof.get("product_sot", {}).get("sha256") == product_sot_hash,
        "proof manifest is stale against product SOT",
    )
    board = evidence_by_role["product_proof_contact_sheet"]
    require(
        proof.get("board", {}).get("sha256") == board["sha256"],
        "proof board hash disagrees with manifest",
    )

    policy = load_json(root_path(evidence_by_role["mandatory_tournament_policy"]["path"]))
    require(
        strict_equal(policy, EXPECTED_TOURNAMENT_POLICY),
        "mandatory tournament policy drifted from the complete fail-closed policy",
    )
    require(
        policy.get("required_vision_judges") == ["gpt-5.5-pro"],
        "mandatory vision judge set drifted",
    )
    require(policy.get("synthesis_model") is None, "post-generation synthesis must be disabled")
    require(policy.get("minimum_each_vision_score") == 95, "vision threshold drifted")
    require(policy.get("minimum_final_score") == 95, "final threshold drifted")
    require(
        policy.get("required_hallucination_veto_result") is False,
        "hallucination veto policy drifted",
    )
    require(
        policy.get("unverifiable_required_regions") == 0,
        "policy permits unverifiable product regions",
    )
    require(
        policy.get("founder_approval_required") is True,
        "policy no longer requires founder approval",
    )

    availability = load_json(root_path(evidence_by_role["live_judge_availability_receipt"]["path"]))
    require(
        availability.get("schema") == "skyyrose.image-judge-availability.v1",
        "wrong judge availability schema",
    )
    expected_models = ["gpt-5.5-pro"]
    require(
        [item.get("model") for item in availability.get("judges", [])] == expected_models,
        "judge receipt covers wrong models",
    )
    judges_live = (
        availability.get("status") == "PASS_ALL_JUDGES_AVAILABLE"
        and availability.get("all_judges_available") is True
        and all(item.get("available") is True for item in availability.get("judges", []))
    )
    judge_receipt_fresh = False
    if judges_live:
        checked_at_raw = availability.get("checked_at")
        require(isinstance(checked_at_raw, str), "live judge receipt is missing checked_at")
        try:
            checked_at = datetime.fromisoformat(checked_at_raw)
        except ValueError as error:
            raise ValidationError("live judge receipt has invalid checked_at") from error
        require(
            checked_at.tzinfo is not None, "live judge receipt checked_at must be timezone-aware"
        )
        checked_at = checked_at.astimezone(UTC)
        now = datetime.now(UTC)
        require(
            checked_at <= now + timedelta(minutes=1),
            "live judge receipt checked_at is in the future",
        )
        require(now - checked_at <= JUDGE_RECEIPT_MAX_AGE, "live judge receipt is stale")
        judge_receipt_fresh = True
    return {
        "patched_model_lineage_current": True,
        "protected_rgb_lineage_current": True,
        "model_reference_machine_approval_state": patched_receipt.get("approval_state"),
        "model_reference_machine_founder_approval_recorded": (
            patched_receipt.get("approval_state") == "FOUNDER_APPROVED"
        ),
        "product_proof_current": True,
        "tournament_thresholds_locked": True,
        "required_judges_live": judges_live and judge_receipt_fresh,
        "judge_availability_receipt_fresh": judge_receipt_fresh,
        "judge_availability_status": availability.get("status"),
    }


def validate_illumination_invariant(contract: dict[str, Any]) -> dict[str, Any]:
    illumination = contract.get("illumination_identifiability", {})
    allowed = set(illumination.get("raster_only_allowed_outcomes", []))
    require(allowed == RASTER_ONLY_VERDICTS, "raster-only verdict set may not grant compatibility")
    require(
        "VALIDATED_COMPATIBLE" not in allowed,
        "raster-only analysis may not grant relight authority",
    )
    require(
        illumination.get("current_pair_verdict") in RASTER_ONLY_VERDICTS,
        "current raster pair uses an inadmissible verdict",
    )
    require(
        illumination.get("calibration_evidence_for_both_assets") is False,
        "this raster-only contract may not claim calibration evidence",
    )
    require(
        strict_equal(illumination.get("calibration_records"), EXPECTED_CALIBRATION_RECORDS),
        "calibration records may not be invented or weakened",
    )
    calibration = False
    policy = illumination.get("protected_pixel_policy", {})
    require(
        illumination.get("raster_only_may_grant_relight_authority") is False,
        "raster-only path grants relight authority",
    )
    require(
        illumination.get("relight_authority") is False,
        "uncalibrated pair grants relight authority",
    )
    require(
        type(policy.get("max_abs_log_gain")) in (int, float)
        and policy.get("max_abs_log_gain") == 0,
        "protected-pixel max_abs_log_gain must be exactly zero",
    )
    require(
        policy.get("protected_low_frequency_band_must_equal_approved_input") is True,
        "protected low-frequency pixels are not locked to approved input",
    )
    require(
        policy.get("protected_low_frequency_band_source")
        == "approved_two_model_identity_pose_and_product_placement_reference",
        "protected low-frequency source drifted",
    )
    require(
        policy.get("chroma_import_allowed") is False,
        "uncalibrated pair permits protected chroma import",
    )
    require(
        policy.get("generator_derived_spatial_gain_allowed") is False,
        "uncalibrated pair permits generator-derived gain",
    )
    require(
        illumination.get("no_observed_contradiction_behaves_as_unresolvable") is True,
        "NO_OBSERVED_CONTRADICTION is not fail closed",
    )
    require(
        illumination.get("positive_relight_authority_requires")
        == "admissible_exact_rig_calibration_evidence_for_both_assets",
        "positive relight route is not exact-rig-only",
    )
    return {
        "calibration_evidence_for_both_assets": calibration,
        "current_pair_verdict": illumination["current_pair_verdict"],
        "relight_authority": illumination["relight_authority"],
        "max_abs_log_gain": policy["max_abs_log_gain"],
        "protected_low_frequency_source": policy["protected_low_frequency_band_source"],
    }


def validate_contract_semantics(contract: dict[str, Any]) -> None:
    require(
        contract.get("schema") == "skyyrose.native-scene-regeneration-planning-contract.v1",
        "wrong planning-contract schema",
    )
    require(contract.get("scene_id") == "LH-COMMERCE-1", "wrong scene")
    branch = contract.get("branch_decision", {})
    require(
        branch.get("selected_branch") == "NATIVE_SCENE_REGENERATION",
        "native-scene branch is not selected",
    )
    require(branch.get("selected_branch_alias") == "A", "wrong branch alias")
    require(
        branch.get("existing_approved_sources_are_read_only") is True,
        "approved source files are not read-only",
    )
    require(
        branch.get("candidate_must_be_written_to_new_path") is True,
        "candidate may overwrite a source",
    )

    illumination = contract.get("illumination_identifiability", {})
    require(
        illumination.get("current_pair_verdict") == "UNRESOLVABLE",
        "current raster pair must remain UNRESOLVABLE",
    )
    require(
        strict_equal(contract.get("native_scene_requirements"), EXPECTED_NATIVE_SCENE_REQUIREMENTS),
        "native-scene camera, floor, pose, occlusion, light, shadow, reflection, depth, grain, or hero-rose invariant drifted",
    )
    authorization = contract.get("authorization", {})
    require(
        authorization.get("prompt_planning_authorized") is True, "prompt planning is not authorized"
    )
    for field in (
        "generation_authorized",
        "binary_edit_authorized",
        "source_pixel_mutation_authorized",
        "v2_runtime_wiring_authorized",
        "legacy_runtime_changes_authorized",
        "deployment_authorized",
        "commit_authorized",
    ):
        require(authorization.get(field) is False, f"unauthorized state enabled: {field}")
    require(
        authorization.get("founder_reapproval_required") is True,
        "founder reapproval is not required",
    )

    safe_zones = contract.get("responsive_safe_zones", {})
    breakpoints = safe_zones.get("breakpoints", [])
    require(
        {item.get("id") for item in breakpoints} == EXPECTED_BREAKPOINTS,
        "responsive breakpoint coverage drifted",
    )
    require(
        safe_zones.get("coordinate_space") == "normalized_generation_frame",
        "safe zones use wrong coordinate space",
    )
    require(
        safe_zones.get("generation_blocked_until_measured") is True,
        "provisional safe zones do not block generation",
    )
    for breakpoint in breakpoints:
        require(breakpoint.get("keep_clear"), f"empty safe zones for {breakpoint.get('id')}")
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

    region_gates = contract.get("per_region_fidelity_checks", [])
    require(
        {item.get("id") for item in region_gates} == EXPECTED_REGION_GATES,
        "per-region fidelity gate coverage drifted",
    )
    require(
        all(item.get("unverifiable_is_failure") is True for item in region_gates),
        "an unverifiable product region may pass",
    )

    rejection_rules = contract.get("rejection_rules", [])
    require(
        {item.get("id") for item in rejection_rules} == EXPECTED_REJECTION_RULES,
        "automatic rejection coverage drifted",
    )
    require(
        all(item.get("fatal") is True for item in rejection_rules), "a rejection rule is non-fatal"
    )

    batch = contract.get("batch_and_review_contract", {})
    require(batch.get("batch_only") is True, "single-image generation is permitted")
    require(batch.get("candidate_count") == 9, "batch candidate count must remain 9")
    require(
        batch.get("matrix")
        == {"pose_relationship_variants": 3, "rose_framing_variants": 3, "seeds_per_cell": 1},
        "batch matrix drifted",
    )
    require(batch.get("contact_sheet", {}).get("required") is True, "contact sheet is not required")
    require(batch.get("contact_sheet", {}).get("layout") == "3x3", "contact sheet layout drifted")

    prompt = contract.get("prompt_payload", {})
    combined = f"{prompt.get('positive_prompt', '')} {prompt.get('negative_prompt', '')}".lower()
    for phrase in (
        "one coherent scene",
        "lustrous white satin body",
        "black lustrous satin raglan sleeves",
        "solid black cotton-fleece joggers",
        "solid white cotton-fleece joggers",
        "wearer-left thigh",
        "cracked red heart",
        "dark thorns",
        "three red roses",
        "green leaves",
        "enchanted rose",
        "desktop, tablet, and mobile ui-safe zones",
        "review candidate only",
    ):
        require(
            phrase in combined, f"prompt omits required native-scene or product phrase: {phrase}"
        )

    output = contract.get("output_contract", {})
    require(
        output.get("approval_state") == "CANDIDATE_ONLY_FOUNDER_REAPPROVAL_REQUIRED",
        "unsafe candidate approval state",
    )
    require(
        output.get("may_claim_visual_correctness_before_generation_and_review") is False,
        "contract permits an unsupported visual-correctness claim",
    )
    require(
        output.get("may_claim_product_pixel_identity") is False,
        "native regeneration may not claim source-pixel identity",
    )
    require(
        output.get("may_overwrite_any_bound_input") is False, "output may overwrite a bound input"
    )
    require(output.get("v2_wiring_state") == "FORBIDDEN", "V2 wiring is not forbidden")
    require(output.get("deployment_state") == "FORBIDDEN", "deployment is not forbidden")
    require(
        output.get("production_write_state") == "FORBIDDEN", "production writes are not forbidden"
    )
    for section, expected_hash in SEALED_SECTION_SHA256.items():
        require(
            canonical_json_sha256(contract.get(section)) == expected_hash,
            f"sealed prompt-contract section drifted: {section}",
        )


def generation_blockers(
    contract: dict[str, Any],
    contract_path: Path,
    source_audit: list[dict[str, Any]],
    lineage: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if contract.get("authorization", {}).get("generation_authorized") is not True:
        blockers.append("GENERATION_NOT_AUTHORIZED")
    if contract.get("status") != "READY_TO_GENERATE":
        blockers.append("CONTRACT_REQUIRES_OPUS_REVIEW")
    if (
        contract.get("pre_generation_gates", {}).get("current_state_generation_permitted")
        is not True
    ):
        blockers.append("CONTRACT_EXPLICITLY_BLOCKS_GENERATION")
    if (
        contract.get("responsive_safe_zones", {}).get("measurement_state")
        != "MEASURED_AND_VERIFIED"
    ):
        blockers.append("RESPONSIVE_SAFE_ZONES_ARE_PROVISIONAL")
    if not lineage.get("required_judges_live"):
        blockers.append("MANDATORY_TOURNAMENT_JUDGES_UNAVAILABLE")
    if not lineage.get("model_reference_machine_founder_approval_recorded"):
        blockers.append("MODEL_REFERENCE_MACHINE_FOUNDER_APPROVAL_NOT_RECORDED")
    untracked = sorted(item["path"] for item in source_audit if not item["git_tracked"])
    if untracked:
        blockers.append("UNTRACKED_BOUND_INPUTS:" + ",".join(untracked))
    if not is_git_tracked(contract_path):
        blockers.append("UNTRACKED_PROMPT_CONTRACT")
    blockers.append("PASS_READY_TO_GENERATE_RECEIPT_NOT_ISSUED")
    blockers.append("FRESH_FOUNDER_GENERATION_AUTHORIZATION_REQUIRED")
    return blockers


def validate(contract_path: Path) -> dict[str, Any]:
    contract_path = contract_path.resolve()
    require(contract_path.is_file(), f"planning contract missing: {contract_path}")
    require(contract_path.suffix.lower() == ".json", "planning contract must be JSON")
    require(
        contract_path == ROOT or ROOT in contract_path.parents,
        "planning contract escapes repository",
    )
    contract = load_json(contract_path)
    validate_contract_semantics(contract)

    bindings = contract.get("bindings", {})
    require(isinstance(bindings, dict), "bindings must be an object")
    validate_binding_manifest_contract(bindings)
    sot_item = bindings.get("current_product_sot", {})
    require(sot_item.get("usage") == "validation_only", "product SOT must be validation-only")
    product_sot_path = root_path(sot_item["path"])
    require(product_sot_path.is_file(), "current product SOT is missing")
    product_sot_hash = sha256(product_sot_path)
    require(
        product_sot_hash == sot_item.get("sha256"), "planning contract is stale against product SOT"
    )
    product_sot = load_json(product_sot_path)

    generator_items = bindings.get("generator_conditioning_references", [])
    evidence_items = bindings.get("validation_only_evidence", [])
    require(
        isinstance(generator_items, list) and isinstance(evidence_items, list),
        "binding lists are malformed",
    )
    require(
        canonical_json_sha256(generator_items) == SEALED_GENERATOR_REFERENCES_SHA256,
        "sealed ordered generator-conditioning references drifted",
    )
    generator_roles = [item.get("role") for item in generator_items]
    evidence_roles = [item.get("role") for item in evidence_items]
    require(len(generator_roles) == len(set(generator_roles)), "duplicate generator role")
    require(len(evidence_roles) == len(set(evidence_roles)), "duplicate evidence role")
    require(
        generator_roles == EXPECTED_GENERATOR_ROLE_ORDER,
        "ordered generator role sequence drifted",
    )
    require(set(generator_roles) == EXPECTED_GENERATOR_ROLES, "generator role set drifted")
    require(set(evidence_roles) == EXPECTED_EVIDENCE_ROLES, "evidence role set drifted")
    require(set(generator_roles).isdisjoint(evidence_roles), "generator and evidence roles overlap")
    generator_paths = [item.get("path") for item in generator_items]
    evidence_paths = [item.get("path") for item in evidence_items]
    require(
        len(generator_paths) == len(set(generator_paths)),
        "same path passed under multiple generator roles",
    )
    require(
        len(evidence_paths) == len(set(evidence_paths)),
        "same path passed under multiple validation-only roles",
    )
    require(
        set(generator_paths).isdisjoint(evidence_paths),
        "generator and validation-only paths overlap",
    )

    source_audit = [
        {
            "role": sot_item["role"],
            "usage": "validation_only",
            "path": sot_item["path"],
            "sha256": product_sot_hash,
            "bytes": product_sot_path.stat().st_size,
            "git_tracked": is_git_tracked(product_sot_path),
        }
    ]
    source_audit.extend(audit_binding(item, "generator_conditioning") for item in generator_items)
    source_audit.extend(
        audit_binding(
            item,
            "validation_only",
            rotating_hash_allowed=(
                item.get("role")
                in {"live_judge_availability_receipt", "mandatory_tournament_policy"}
            ),
        )
        for item in evidence_items
    )

    generator_by_role = {item["role"]: item for item in generator_items}
    evidence_by_role = {item["role"]: item for item in evidence_items}
    validate_product_bindings(contract, product_sot, generator_items)
    lineage = validate_receipt_lineage(evidence_by_role, generator_by_role, product_sot_hash)
    illumination = validate_illumination_invariant(contract)

    output_dir = root_path(contract["output_contract"]["candidate_directory"])
    bound_paths = {
        root_path(item["path"]) for item in [sot_item, *generator_items, *evidence_items]
    }
    require(output_dir not in bound_paths, "candidate output directory overlaps a bound input")
    require(
        all(output_dir not in path.parents for path in bound_paths),
        "candidate output directory contains a bound input",
    )

    blockers = generation_blockers(contract, contract_path, source_audit, lineage)
    return {
        "schema": "skyyrose.native-scene-regeneration-planning-validation.v1",
        "status": "PASS_PROMPT_PACKAGE_READY_FOR_OPUS_REVIEW",
        "validated_at": datetime.now(UTC).isoformat(),
        "contract": {
            "path": str(contract_path.relative_to(ROOT)),
            "sha256": sha256(contract_path),
        },
        "scene_id": contract["scene_id"],
        "selected_branch": contract["branch_decision"]["selected_branch"],
        "source_audit": source_audit,
        "lineage_checks": lineage,
        "round_2_invariant": illumination,
        "per_region_fidelity_gate_count": len(contract["per_region_fidelity_checks"]),
        "automatic_rejection_rule_count": len(contract["rejection_rules"]),
        "batch_candidate_count": contract["batch_and_review_contract"]["candidate_count"],
        "generation_permitted": False,
        "generation_blockers": blockers,
        "v2_wiring_authorized": False,
        "deployment_authorized": False,
        "visual_correctness_claimed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument(
        "--generation-gate",
        action="store_true",
        help=(
            "Fail closed and print planning-package blockers. This planning schema "
            "can never issue generation authority."
        ),
    )
    args = parser.parse_args()
    contract_path = args.contract if args.contract.is_absolute() else ROOT / args.contract
    try:
        receipt_path = resolve_receipt_path(args.receipt)
        receipt = validate(contract_path)
    except (KeyError, TypeError, ValidationError, json.JSONDecodeError, OSError) as error:
        print(f"BLOCKED_NATIVE_SCENE_PREFLIGHT {error}")
        return 1

    if args.generation_gate:
        print("BLOCKED_NATIVE_SCENE_GENERATION " + " | ".join(receipt["generation_blockers"]))
        return 1

    if args.write_receipt:
        write_json_atomic(receipt_path, receipt)
    print(
        "PASS_PROMPT_PACKAGE_READY_FOR_OPUS_REVIEW "
        f"contract_sha256={receipt['contract']['sha256']} "
        f"sources={len(receipt['source_audit'])} "
        f"generation_permitted={str(receipt['generation_permitted']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
