#!/usr/bin/env python3
"""Record exact protected outputs for the current receipt-bound generation batch."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
THEME_DIR = Path(__file__).resolve().parent.parent
BASE = THEME_DIR / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1"
DEFAULT_PREFLIGHT = BASE / "preflight-v1/pass-ready-to-generate-receipt-v1.json"
DEFAULT_PROMPT = BASE / "image-model-prompts-v1.json"
DEFAULT_OUTPUT = BASE / "postflight-v1/generation-batch-manifest-v1.json"


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


def parse_output(value: str) -> tuple[str, Path]:
    require("=" in value, f"output must use JOB_ID=PATH: {value}")
    job_id, path = value.split("=", 1)
    require(job_id and path, f"output must use JOB_ID=PATH: {value}")
    return job_id, Path(path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--output", action="append", default=[], metavar="JOB_ID=PATH")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    require(args.preflight.is_file(), "passing preflight receipt missing")
    require(args.prompt.is_file(), "prompt contract missing")
    preflight = load_json(args.preflight)
    prompt = load_json(args.prompt)
    require(preflight["status"] == "PASS_READY_TO_GENERATE", "preflight is not passing")
    require(
        preflight["prompt_contract"]["sha256"] == sha256(args.prompt),
        "prompt changed after preflight",
    )
    product_sot_path = ROOT / preflight["product_sot"]["path"]
    require(
        sha256(product_sot_path) == preflight["product_sot"]["sha256"],
        "product SOT changed after preflight",
    )

    outputs = dict(parse_output(value) for value in args.output)
    require(len(outputs) == len(args.output), "duplicate output job ID")
    expected_jobs = set(preflight["active_generation_jobs"])
    require(set(outputs) == expected_jobs, f"outputs must cover exactly {sorted(expected_jobs)}")
    jobs: dict[str, Any] = {}
    for job_id in preflight["active_generation_jobs"]:
        output = outputs[job_id]
        require(ROOT in output.parents, f"output escapes repository: {output}")
        require(output.is_file(), f"output missing for {job_id}: {output}")
        require(output.suffix.lower() == ".png", f"output must be PNG for {job_id}")
        receipt_path = output.with_suffix(".receipt.json")
        require(receipt_path.is_file(), f"protected-layer receipt missing for {job_id}")
        protected = load_json(receipt_path)
        require(
            protected["schema"] == "skyyrose.protected-model-layer.v1",
            f"stale protected-layer receipt for {job_id}",
        )
        require(
            protected["output_sha256"] == sha256(output),
            f"protected output hash mismatch for {job_id}",
        )
        source_path = Path(protected["source"])
        if not source_path.is_absolute():
            source_path = (ROOT / source_path).resolve()
        require(source_path.is_file(), f"raw generated source missing for {job_id}")
        require(
            protected["source_sha256"] == sha256(source_path),
            f"raw generated source hash mismatch for {job_id}",
        )
        require(
            protected["rgb_preserved"] is True,
            f"protected layer changed generated RGB for {job_id}",
        )
        with Image.open(output) as image:
            require(image.mode == "RGBA", f"output lacks real RGBA transparency for {job_id}")
            alpha_extrema = list(image.getchannel("A").getextrema())
            require(
                alpha_extrema == [0, 255],
                f"output alpha is not meaningful for {job_id}: {alpha_extrema}",
            )
            dimensions = list(image.size)
        job = prompt["generation_jobs"][job_id]
        jobs[job_id] = {
            "scene_id": job["scene_id"],
            "model": job["model"],
            "operation": job["operation"],
            "prompt_contract_job_sha256": hashlib.sha256(
                json.dumps(job, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
            "raw_generated_source": {
                "path": str(source_path.relative_to(ROOT)),
                "sha256": sha256(source_path),
            },
            "output": {
                "path": str(output.relative_to(ROOT)),
                "sha256": sha256(output),
                "dimensions": dimensions,
                "alpha_extrema": alpha_extrema,
                "protected_layer_receipt": str(receipt_path.relative_to(ROOT)),
                "protected_layer_receipt_sha256": sha256(receipt_path),
            },
            "product_bindings": job["product_bindings"],
            "approval_state": "FOUNDER_REVIEW_REQUIRED",
        }

    manifest = {
        "schema": "skyyrose.image-generation-batch.v1",
        "approval_state": "FOUNDER_REVIEW_REQUIRED",
        "founder_approval_required": True,
        "preflight_receipt": str(args.preflight.relative_to(ROOT)),
        "preflight_receipt_sha256": sha256(args.preflight),
        "prompt_contract": str(args.prompt.relative_to(ROOT)),
        "prompt_contract_sha256": sha256(args.prompt),
        "product_sot_sha256": preflight["product_sot"]["sha256"],
        "tournament_policy": preflight["tournament_policy"],
        "jobs": jobs,
        "downstream_state": "BLOCKED_PENDING_ADVERSARIAL_TOURNAMENT",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"RECORDED_FOUNDER_REVIEW_BATCH jobs={len(jobs)} manifest_sha256={sha256(args.manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
