#!/usr/bin/env python3
"""Author an image-edit prompt only after two vision models inspect product proof.

This script does not generate imagery. GPT and Gemini independently inspect the
canonical physical references, then Opus reconciles their structured reports
against the canonical product SOT. The resulting JSON remains a review draft
until a separate pre-generation gate certifies it.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
THEME_DIR = Path(__file__).resolve().parent.parent
SCENE_ROOT = THEME_DIR / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1"
PROMPT_CONTRACT = SCENE_ROOT / "image-model-prompts-v1.json"
PRODUCT_SOT = ROOT / "data/product-sot.json"
OUTPUT_DIR = SCENE_ROOT / "preflight-v1/vision-authored-prompts"

GPT_MODEL = "gpt-5.5-pro"
GEMINI_MODEL = "gemini-3.1-pro-preview"
OPUS_MODEL = "claude-opus-5"

ENV_FILES = (
    ".env.judge-gpt-vision",
    ".env.judge-gemini-vision",
    ".env.judge-opus-thinking",
    ".env",
    ".env.secrets",
)

VISION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sku": {"type": "string"},
                    "garment_type": {"type": "string"},
                    "materials": {"type": "array", "items": {"type": "string"}},
                    "base_colors": {"type": "array", "items": {"type": "string"}},
                    "construction": {"type": "array", "items": {"type": "string"}},
                    "branding": {"type": "array", "items": {"type": "string"}},
                    "text": {"type": "array", "items": {"type": "string"}},
                    "logo_placements": {"type": "array", "items": {"type": "string"}},
                    "must_preserve": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "sku",
                    "garment_type",
                    "materials",
                    "base_colors",
                    "construction",
                    "branding",
                    "text",
                    "logo_placements",
                    "must_preserve",
                ],
                "additionalProperties": False,
            },
        },
        "cross_reference_findings": {"type": "array", "items": {"type": "string"}},
        "uncertainties": {"type": "array", "items": {"type": "string"}},
        "unsupported_claims_rejected": {"type": "array", "items": {"type": "string"}},
        "positive_prompt": {"type": "string"},
        "negative_prompt": {"type": "string"},
        "invariants": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "products",
        "cross_reference_findings",
        "uncertainties",
        "unsupported_claims_rejected",
        "positive_prompt",
        "negative_prompt",
        "invariants",
    ],
    "additionalProperties": False,
}

SYNTHESIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "consensus_product_truth": {"type": "array", "items": {"type": "string"}},
        "conflicts": {"type": "array", "items": {"type": "string"}},
        "unverifiable_details": {"type": "array", "items": {"type": "string"}},
        "positive_prompt": {"type": "string"},
        "negative_prompt": {"type": "string"},
        "invariants": {"type": "array", "items": {"type": "string"}},
        "source_only_instruction": {"type": "string"},
        "ready_for_human_review": {"type": "boolean"},
    },
    "required": [
        "consensus_product_truth",
        "conflicts",
        "unverifiable_details",
        "positive_prompt",
        "negative_prompt",
        "invariants",
        "source_only_instruction",
        "ready_for_human_review",
    ],
    "additionalProperties": False,
}


def load_environment() -> None:
    for name in ENV_FILES:
        path = ROOT / name
        if not path.is_file():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def first_key(*names: str) -> str:
    return next((os.getenv(name, "").strip() for name in names if os.getenv(name, "").strip()), "")


def safe_failure_reason(error: BaseException) -> str:
    """Classify provider failures without storing provider response bodies."""
    message = str(error).lower()
    if any(
        marker in message
        for marker in (
            "insufficient_quota",
            "credit balance",
            "no credits remaining",
            "quota exceeded",
            "resource_exhausted",
        )
    ):
        return "inference_quota_or_credit_exhausted"
    if "rate limit" in message or type(error).__name__ == "RateLimitError":
        return "inference_rate_limited"
    return f"model_inference_failed:{type(error).__name__}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def parse_json_text(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    value = json.loads(cleaned.strip())
    if not isinstance(value, dict):
        raise ValueError("model response was not a JSON object")
    return value


def mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    if suffix == ".png":
        return "image/png"
    raise ValueError(f"unsupported proof image type: {path}")


def canonical_records(product_sot: dict[str, Any], bindings: dict[str, str]) -> dict[str, Any]:
    products = product_sot["products"]
    result: dict[str, Any] = {}
    for sku, expected_hash in bindings.items():
        record = products.get(sku)
        if not isinstance(record, dict):
            raise ValueError(f"missing product SOT record: {sku}")
        if record.get("product_hash") != expected_hash:
            raise ValueError(f"stale product binding for {sku}")
        result[sku] = record
    return result


def proof_inputs(job: dict[str, Any]) -> list[dict[str, Any]]:
    proofs: list[dict[str, Any]] = []
    for item in job["input_images"]:
        if item["role"] == "edit_target":
            continue
        path = ROOT / item["path"]
        if not path.is_file():
            raise ValueError(f"missing proof image: {item['path']}")
        actual_hash = sha256(path)
        if actual_hash != item["sha256"]:
            raise ValueError(f"stale proof hash: {item['path']}")
        proofs.append({**item, "absolute_path": path, "actual_sha256": actual_hash})
    if not proofs:
        raise ValueError("job has no canonical proof images")
    return proofs


def vision_instruction(
    job_id: str,
    proofs: list[dict[str, Any]],
    records: dict[str, Any],
) -> str:
    labels = "\n".join(
        f"IMAGE {index}: role={item['role']}; path={item['path']}; sha256={item['sha256']}"
        for index, item in enumerate(proofs, 1)
    )
    return f"""You are a forensic product-visual analyst and image-edit prompt author.

JOB: {job_id}

Inspect every supplied founder flatlay, physical product photograph, techflat, and exact logo
reference before writing the prompt. The pixels are primary truth. The canonical product records
below may clarify technique, placement, and names, but they must never override a visible physical
reference. Do not use general fashion knowledge. Do not invent an unseen side, back, closure, logo,
wordmark, material, color, trim, or construction detail. State uncertainty when the proof cannot
establish a detail. Treat each logo reference as exact artwork, not inspiration.

IMAGE LABELS:
{labels}

CANONICAL PRODUCT RECORDS:
{json.dumps(records, indent=2)}

Write a precise edit prompt that tells an image editor to reproduce these products as replicas while
preserving all model identity, anatomy, pose, and already-correct pixels. Separate what you observed
from what remains uncertain. Explicitly reject all unsupported additions and substitutions. Return
only JSON matching the required schema."""


def call_gpt(key: str, instruction: str, proofs: list[dict[str, Any]]) -> dict[str, Any]:
    from openai import OpenAI

    content: list[dict[str, Any]] = [{"type": "input_text", "text": instruction}]
    for index, item in enumerate(proofs, 1):
        path = item["absolute_path"]
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        content.append({"type": "input_text", "text": f"IMAGE {index}: {item['role']}"})
        content.append(
            {
                "type": "input_image",
                "image_url": f"data:{mime_type(path)};base64,{encoded}",
                "detail": "high",
            }
        )
    response = OpenAI(api_key=key, timeout=240).responses.create(
        model=GPT_MODEL,
        reasoning={"effort": "high"},
        max_output_tokens=16384,
        text={
            "format": {
                "type": "json_schema",
                "name": "vision_grounded_prompt",
                "strict": True,
                "schema": VISION_SCHEMA,
            }
        },
        input=[{"role": "user", "content": content}],
    )
    return parse_json_text(response.output_text or "")


def call_gemini(key: str, instruction: str, proofs: list[dict[str, Any]]) -> dict[str, Any]:
    from google import genai
    from google.genai import types

    contents: list[Any] = [instruction]
    for index, item in enumerate(proofs, 1):
        path = item["absolute_path"]
        contents.append(f"IMAGE {index}: {item['role']}")
        contents.append(types.Part.from_bytes(data=path.read_bytes(), mime_type=mime_type(path)))
    response = genai.Client(api_key=key, http_options={"timeout": 240_000}).models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=VISION_SCHEMA,
            max_output_tokens=16384,
            temperature=1.0,
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
        ),
    )
    return parse_json_text(response.text or "")


def synthesis_instruction(
    job_id: str,
    records: dict[str, Any],
    gpt_report: dict[str, Any],
    gemini_report: dict[str, Any],
) -> str:
    return f"""You are the synthesis editor for a fail-closed luxury product-imagery workflow.
You do not see the images. Two independent vision models inspected the canonical physical proof and
authored reports. Reconcile only details supported by both reports or explicitly supported by the
canonical product records. If the reports conflict, omit the disputed claim and list it as a conflict.
If a detail cannot be verified, list it and do not instruct the image model to invent it. Exact logo
artwork must be copied from the supplied reference, never described as stylistic inspiration.

JOB: {job_id}

CANONICAL PRODUCT RECORDS:
{json.dumps(records, indent=2)}

GPT VISION REPORT:
{json.dumps(gpt_report, indent=2)}

GEMINI VISION REPORT:
{json.dumps(gemini_report, indent=2)}

Produce the strictest shared prompt. The source_only_instruction must explicitly say that the image
editor may use only the labelled source pixels and exact referenced artwork, must preserve all
unrequested pixels, and must stop rather than improvise. Return JSON only."""


def call_opus(
    key: str,
    instruction: str,
) -> dict[str, Any]:
    from anthropic import Anthropic

    schema_text = json.dumps(SYNTHESIS_SCHEMA, indent=2)
    response = Anthropic(api_key=key, timeout=240).messages.create(
        model=OPUS_MODEL,
        max_tokens=8192,
        thinking={"type": "adaptive", "display": "summarized"},
        output_config={"effort": "xhigh"},
        messages=[
            {
                "role": "user",
                "content": f"{instruction}\n\nREQUIRED JSON SCHEMA:\n{schema_text}",
            }
        ],
    )
    text = "\n".join(
        getattr(block, "text", "") or ""
        for block in response.content
        if getattr(block, "type", None) == "text"
    )
    return parse_json_text(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, help="Job key in image-model-prompts-v1.json")
    args = parser.parse_args()

    load_environment()
    openai_key = first_key("OPENAI_API_KEY", "OPENAI_AGENT107_KEY", "OPENAI_FEB19")
    gemini_key = first_key("GOOGLE_API_KEY_2", "GOOGLE_API_KEY", "GEMINI_API_KEY")
    anthropic_key = first_key("ANTHROPIC_API_KEY")
    if not all((openai_key, gemini_key, anthropic_key)):
        raise SystemExit("BLOCKED required model credential missing")

    prompt_contract = load_json(PROMPT_CONTRACT)
    job = prompt_contract.get("generation_jobs", {}).get(args.job)
    if not isinstance(job, dict):
        raise SystemExit(f"BLOCKED unknown job: {args.job}")
    product_sot = load_json(PRODUCT_SOT)
    records = canonical_records(product_sot, job["product_bindings"])
    proofs = proof_inputs(job)
    instruction = vision_instruction(args.job, proofs, records)

    output = OUTPUT_DIR / f"{args.job}-vision-authored-prompt-v1.json"

    # Sequential on purpose: a failed mandatory provider halts the run before
    # more paid work occurs. The receipt records only the provider and error
    # class; credential values and provider response bodies never reach disk.
    try:
        gpt_report = call_gpt(openai_key, instruction, proofs)
        gemini_report = call_gemini(gemini_key, instruction, proofs)
        synthesis = call_opus(
            anthropic_key,
            synthesis_instruction(args.job, records, gpt_report, gemini_report),
        )
    except BaseException as error:
        blocked = {
            "schema": "skyyrose.vision-grounded-image-prompt.v1",
            "status": "BLOCKED_REQUIRED_MODEL_INFERENCE_FAILED",
            "created_at": datetime.now(UTC).isoformat(),
            "job": args.job,
            "failed_model_stage": (
                GPT_MODEL
                if "gpt_report" not in locals()
                else GEMINI_MODEL if "gemini_report" not in locals() else OPUS_MODEL
            ),
            "failure_reason": safe_failure_reason(error),
            "generation_permitted": False,
            "secrets_in_receipt": False,
        }
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(blocked, indent=2) + "\n", encoding="utf-8")
        print(
            "BLOCKED_REQUIRED_MODEL_INFERENCE_FAILED "
            f"model={blocked['failed_model_stage']} reason={blocked['failure_reason']}"
        )
        print(f"BLOCKED_RECEIPT output={output.relative_to(ROOT)}")
        return 1

    receipt = {
        "schema": "skyyrose.vision-grounded-image-prompt.v1",
        "status": "DRAFT_VISION_AUTHORED_NOT_GENERATION_APPROVED",
        "created_at": datetime.now(UTC).isoformat(),
        "job": args.job,
        "models": {
            "vision": [GPT_MODEL, GEMINI_MODEL],
            "synthesis": OPUS_MODEL,
        },
        "inputs": {
            "prompt_contract": {
                "path": str(PROMPT_CONTRACT.relative_to(ROOT)),
                "sha256": sha256(PROMPT_CONTRACT),
            },
            "product_sot": {
                "path": str(PRODUCT_SOT.relative_to(ROOT)),
                "sha256": sha256(PRODUCT_SOT),
            },
            "proof_images": [
                {
                    "role": item["role"],
                    "path": item["path"],
                    "sha256": item["actual_sha256"],
                }
                for item in proofs
            ],
            "product_bindings": job["product_bindings"],
        },
        "vision_reports": {
            GPT_MODEL: gpt_report,
            GEMINI_MODEL: gemini_report,
        },
        "synthesis": synthesis,
        "generation_permitted": False,
        "next_gate": "human review followed by full transitive preflight certification",
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"PASS_VISION_PROMPT_DRAFT job={args.job} output={output.relative_to(ROOT)}")
    print("GENERATION_DISABLED pending human review and preflight certification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
