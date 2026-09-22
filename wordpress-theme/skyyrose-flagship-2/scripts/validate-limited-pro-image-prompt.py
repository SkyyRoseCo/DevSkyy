#!/usr/bin/env python3
"""Certify one founder-authorized interactive Pro image prompt without API judges."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
THEME_DIR = Path(__file__).resolve().parent.parent
SCENE_ROOT = THEME_DIR / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1"
DEFAULT_PROMPT = (
    SCENE_ROOT / "preflight-v1/vision-authored-prompts/lh-commerce-1-limited-pro-v1.json"
)
RECEIPT = SCENE_ROOT / "preflight-v1/limited-pro-preflight-receipt-v1.json"
PRODUCT_SOT = ROOT / "data/product-sot.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(prompt_path: Path) -> dict[str, Any]:
    prompt = load_json(prompt_path)
    require(prompt.get("schema") == "skyyrose.limited-pro-vision-prompt.v1", "wrong schema")
    authorization = prompt.get("authorization", {})
    require(
        authorization.get("full_three_provider_tournament_waived_for_this_candidate") is True,
        "limited waiver is not explicit",
    )
    require(
        authorization.get("founder_visual_approval_still_required") is True,
        "founder approval must remain required",
    )
    require(
        authorization.get("deployment_authorized") is False,
        "limited prompt cannot authorize deployment",
    )

    product_sot = load_json(PRODUCT_SOT)
    require(prompt["product_sot"]["sha256"] == sha256(PRODUCT_SOT), "product SOT hash drift")
    for sku, expected_hash in prompt["product_bindings"].items():
        product = product_sot.get("products", {}).get(sku)
        require(isinstance(product, dict), f"missing product record: {sku}")
        require(product.get("product_hash") == expected_hash, f"stale product binding: {sku}")

    reviewed_files: list[dict[str, str]] = []
    roles: set[str] = set()
    for item in prompt.get("input_images", []):
        path = ROOT / item["path"]
        require(path.is_file(), f"missing input: {item['path']}")
        actual = sha256(path)
        require(actual == item["sha256"], f"input hash drift: {item['path']}")
        roles.add(item["role"])
        reviewed_files.append({"path": item["path"], "sha256": actual})

    required_roles = {
        "edit_target_composition_only",
        "canonical_lh-004_physical_satin_bomber",
        "canonical_lh-002_black_joggers",
        "canonical_lh-006_white_joggers",
        "canonical_exact_heart_shaped_base_logo",
    }
    require(required_roles <= roles, "required visual proof roles are incomplete")
    require(len(prompt.get("visual_observations", [])) >= 5, "visual observations are incomplete")
    require(len(prompt.get("positive_prompt", "")) >= 1000, "positive prompt is too shallow")
    require(len(prompt.get("negative_prompt", "")) >= 400, "negative prompt is too shallow")
    require(len(prompt.get("invariants", [])) >= 9, "invariant list is incomplete")

    combined = " ".join(
        [prompt["positive_prompt"], prompt["negative_prompt"], *prompt["invariants"]]
    ).lower()
    for phrase in (
        "satin",
        "wearer-left",
        "cracked red heart",
        "three red rose",
        "dark",
        "thorn",
        "green leaves",
        "true alpha",
        "generic rose",
        "rose-on-cloud",
    ):
        require(phrase in combined, f"required product truth absent from prompt: {phrase}")

    output = prompt.get("output", {})
    require(output.get("format") == "png", "output must be PNG")
    require(output.get("color_mode") == "RGBA", "output must request RGBA")
    require(output.get("background") == "transparent", "output must request transparency")
    require(
        output.get("approval_state") == "FOUNDER_REVIEW_REQUIRED",
        "output must remain founder-review gated",
    )
    require(
        output.get("v2_wiring_allowed_before_founder_approval") is False,
        "candidate cannot be wired before founder approval",
    )

    return {
        "schema": "skyyrose.limited-pro-preflight.v1",
        "status": "PASS_LIMITED_PRO_READY_FOR_ONE_GENERATION",
        "certified_at": datetime.now(UTC).isoformat(),
        "prompt": {
            "path": str(prompt_path.relative_to(ROOT)),
            "sha256": sha256(prompt_path),
        },
        "product_sot": {
            "path": str(PRODUCT_SOT.relative_to(ROOT)),
            "sha256": sha256(PRODUCT_SOT),
        },
        "reviewed_files": reviewed_files,
        "generation_limit": 1,
        "external_api_tournament_complete": False,
        "founder_visual_approval_required": True,
        "deployment_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    prompt_path = args.prompt if args.prompt.is_absolute() else ROOT / args.prompt
    try:
        receipt = validate(prompt_path)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        RECEIPT.unlink(missing_ok=True)
        print(f"BLOCKED_LIMITED_PRO_PREFLIGHT {error}")
        return 1
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        "PASS_LIMITED_PRO_READY_FOR_ONE_GENERATION "
        f"prompt_sha256={receipt['prompt']['sha256']} reviewed_files={len(receipt['reviewed_files'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
