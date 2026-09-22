#!/usr/bin/env python3
"""Require GPT vision review before the separate founder approval gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
THEME_DIR = Path(__file__).resolve().parent.parent
BASE = THEME_DIR / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1"
DEFAULT_PREFLIGHT = BASE / "preflight-v1/pass-ready-to-generate-receipt-v1.json"
DEFAULT_BATCH = BASE / "postflight-v1/generation-batch-manifest-v1.json"
DEFAULT_REVIEWS = BASE / "postflight-v1/adversarial-reviews"
DEFAULT_RECEIPT = BASE / "postflight-v1/pass-adversarial-verification-receipt-v1.json"
ALLOWED_VERDICTS = {"clean", "partially-improved", "no-improvement", "regressed"}
REQUIRED_VISION_JUDGES = ("gpt-5.5-pro",)


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
    require(ROOT in path.parents, f"path escapes repository: {value}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--batch", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--founder-override", type=Path)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    require(args.preflight.is_file(), "preflight receipt missing")
    require(args.batch.is_file(), "generation batch manifest missing")
    preflight = load_json(args.preflight)
    batch = load_json(args.batch)
    require(preflight["status"] == "PASS_READY_TO_GENERATE", "preflight receipt is not passing")
    require(
        batch["schema"] == "skyyrose.image-generation-batch.v1", "generation batch schema is stale"
    )
    require(
        batch["approval_state"] == "FOUNDER_REVIEW_REQUIRED",
        "generated batch has unsafe approval state",
    )
    require(
        batch["preflight_receipt_sha256"] == sha256(args.preflight),
        "batch is not bound to current preflight receipt",
    )
    require(
        batch["prompt_contract_sha256"] == preflight["prompt_contract"]["sha256"],
        "batch prompt hash disagrees with preflight",
    )
    require(
        batch["product_sot_sha256"] == preflight["product_sot"]["sha256"],
        "batch product SOT hash disagrees with preflight",
    )
    require(
        set(batch["jobs"]) == set(preflight["active_generation_jobs"]),
        "batch job set differs from preflight",
    )
    policy_path = root_path(preflight["tournament_policy"]["path"])
    require(
        sha256(policy_path) == preflight["tournament_policy"]["sha256"],
        "tournament policy changed after preflight",
    )
    policy = load_json(policy_path)
    require(
        tuple(policy["required_vision_judges"]) == REQUIRED_VISION_JUDGES,
        "tournament vision judges changed",
    )
    require(policy["synthesis_model"] is None, "post-generation synthesis must be disabled")
    require(policy["minimum_each_vision_score"] == 95, "GPT vision threshold changed")
    require(policy["minimum_final_score"] == 95, "final threshold changed")
    require(
        policy["required_hallucination_veto_result"] is False,
        "hallucination veto policy changed",
    )
    require(policy["all_judges_available"] is True, "judge availability policy changed")
    require(policy["unverifiable_required_regions"] == 0, "unverifiable-region policy changed")
    require(policy["source_hashes_current"] is True, "source-hash policy changed")
    require(
        policy.get("review_authorities") == ["gpt-5.5-pro", "founder"],
        "review authorities changed",
    )
    require(policy["founder_approval_required"] is True, "founder approval boundary changed")

    output_hashes: dict[str, str] = {}
    for job_id, job in batch["jobs"].items():
        output = job["output"]
        output_path = root_path(output["path"])
        require(output_path.is_file(), f"generated output missing for {job_id}")
        actual_hash = sha256(output_path)
        require(actual_hash == output["sha256"], f"generated output hash drift for {job_id}")
        require(output_path.suffix.lower() == ".png", f"generated output is not PNG for {job_id}")
        output_hashes[job_id] = actual_hash

    review_files = sorted(args.reviews.glob("*.json")) if args.reviews.is_dir() else []
    require(len(review_files) == 1, "exactly one GPT vision report is required")
    vision_reports: dict[str, tuple[Path, dict[str, Any]]] = {}
    machine_assessments: dict[str, dict[str, Any]] = {}
    batch_hash = sha256(args.batch)
    for review_file in review_files:
        review = load_json(review_file)
        require(
            review.get("generation_batch_manifest_sha256") == batch_hash,
            f"stale batch binding: {review_file.name}",
        )
        if review.get("schema") == "skyyrose.adversarial-vision-review.v1":
            reviewer = review.get("reviewer_id", "").strip()
            require(reviewer in REQUIRED_VISION_JUDGES, f"unexpected vision judge: {reviewer}")
            require(reviewer not in vision_reports, f"duplicate vision judge: {reviewer}")
            require(
                review.get("available") is True, f"required vision judge unavailable: {reviewer}"
            )
            require(
                review.get("independent_visual_inspection") is True,
                f"{reviewer} did not inspect pixels independently",
            )
            require(
                review.get("proof_board_visually_compared") is True,
                f"{reviewer} did not compare the proof board",
            )
            require(
                review.get("original_founder_corrections_verbatim", "").strip(),
                f"{reviewer} lacks original founder corrections",
            )
            require(
                review.get("reviewed_outputs") == output_hashes,
                f"{reviewer} did not review every exact output",
            )
            require(
                set(review.get("scores", {})) == set(output_hashes),
                f"{reviewer} did not score every job",
            )
            for job_id, score in review["scores"].items():
                require(
                    score.get("source_hashes_current") is True,
                    f"{reviewer}/{job_id} used stale source hashes",
                )
                require(
                    score.get("unverifiable_required_regions")
                    == policy["unverifiable_required_regions"]
                    == 0,
                    f"{reviewer}/{job_id} has unverifiable regions",
                )
                overall = score.get("overall")
                require(
                    type(overall) in (int, float),
                    f"{reviewer}/{job_id} vision score is invalid",
                )
                hallucination_veto = score.get("hallucination_veto")
                require(
                    type(hallucination_veto) is bool,
                    f"{reviewer}/{job_id} hallucination veto is missing",
                )
                require(
                    score.get("overall_verdict") in ALLOWED_VERDICTS,
                    f"{reviewer}/{job_id} has invalid verdict",
                )
                require(
                    type(score.get("recommend_ship")) is bool,
                    f"{reviewer}/{job_id} recommendation is missing",
                )
                require(
                    isinstance(score.get("evidence"), list) and score["evidence"],
                    f"{reviewer}/{job_id} has no evidence",
                )
                machine_passed = (
                    overall >= policy["minimum_each_vision_score"]
                    and hallucination_veto is policy["required_hallucination_veto_result"] is False
                    and score["overall_verdict"] == "clean"
                    and score["recommend_ship"] is True
                )
                machine_assessments[job_id] = {
                    "overall": overall,
                    "minimum_required": policy["minimum_each_vision_score"],
                    "hallucination_veto": hallucination_veto,
                    "overall_verdict": score["overall_verdict"],
                    "recommend_ship": score["recommend_ship"],
                    "passed_gpt_gate": machine_passed,
                }
            vision_reports[reviewer] = (review_file, review)
        else:
            require(False, f"stale or unknown review schema: {review_file.name}")

    require(
        set(vision_reports) == set(REQUIRED_VISION_JUDGES),
        "required GPT vision judge must be present",
    )
    rejected_outputs = {
        job_id: assessment
        for job_id, assessment in machine_assessments.items()
        if not assessment["passed_gpt_gate"]
    }
    founder_override: dict[str, Any] | None = None
    founder_override_path: Path | None = None
    approved_output_hashes: dict[str, str] = {}
    if rejected_outputs:
        require(
            args.founder_override is not None,
            "GPT review rejected outputs; an explicit founder override is required",
        )
        founder_override_path = args.founder_override.resolve()
        require(
            ROOT in founder_override_path.parents and founder_override_path.is_file(),
            "founder override is missing or outside repository",
        )
        founder_override = load_json(founder_override_path)
        require(
            founder_override.get("schema") == "skyyrose.founder-image-review-override.v1",
            "founder override schema is invalid",
        )
        require(
            founder_override.get("founder_override") is True, "founder override is not explicit"
        )
        require(
            founder_override.get("founder_approved") is True, "founder override is not approved"
        )
        require(
            founder_override.get("deployment_authorized") is False,
            "founder review override may not authorize deployment",
        )
        require(
            founder_override.get("generation_batch_manifest_sha256") == batch_hash,
            "founder override binds a stale generation batch",
        )
        gpt_review_path = vision_reports["gpt-5.5-pro"][0]
        require(
            founder_override.get("gpt_review_sha256") == sha256(gpt_review_path),
            "founder override does not preserve the exact GPT review",
        )
        selected_outputs = founder_override.get("selected_outputs")
        require(
            isinstance(selected_outputs, dict) and selected_outputs,
            "founder override has no selected outputs",
        )
        require(
            set(selected_outputs).issubset(rejected_outputs),
            "founder override may select only GPT-rejected outputs",
        )
        approved_output_hashes = {job_id: output_hashes[job_id] for job_id in selected_outputs}
        require(
            selected_outputs == approved_output_hashes,
            "founder override selected-output hashes drifted",
        )
        require(
            founder_override.get("machine_assessments")
            == {job_id: machine_assessments[job_id] for job_id in selected_outputs},
            "founder override rewrites or omits the GPT assessment",
        )
        require(
            isinstance(founder_override.get("founder_instruction_verbatim"), str)
            and founder_override["founder_instruction_verbatim"].strip(),
            "founder override lacks the verbatim founder instruction",
        )
        approved_at_raw = founder_override.get("approved_at")
        require(isinstance(approved_at_raw, str), "founder override timestamp is missing")
        try:
            approved_at = datetime.fromisoformat(approved_at_raw)
        except ValueError as error:
            raise SystemExit("FAIL founder override timestamp is invalid") from error
        require(approved_at.tzinfo is not None, "founder override timestamp lacks timezone")
        approved_at = approved_at.astimezone(UTC)
        now = datetime.now(UTC)
        require(approved_at <= now + timedelta(minutes=1), "founder override is future-dated")
        require(now - approved_at <= timedelta(hours=24), "founder override is stale")

    accepted_reviews = [
        {
            "reviewer_id": judge,
            "file": str(vision_reports[judge][0].relative_to(ROOT)),
            "sha256": sha256(vision_reports[judge][0]),
            "minimum_score": policy["minimum_each_vision_score"],
        }
        for judge in REQUIRED_VISION_JUDGES
    ]
    status = (
        "FOUNDER_OVERRIDE_RECORDED_GPT_REJECTION_PRESERVED"
        if founder_override is not None
        else "PASS_GPT_VISION_REVIEW"
    )
    downstream_state = (
        "COMPOSITOR_ALLOWED_FOR_EXPLICIT_FOUNDER_OVERRIDE_SELECTION_ONLY"
        if founder_override is not None
        else "BLOCKED_PENDING_EXPLICIT_FOUNDER_APPROVAL"
    )
    receipt = {
        "schema": "skyyrose.adversarial-image-verification-receipt.v1",
        "status": status,
        "generated_at": datetime.now(UTC).isoformat(),
        "preflight_receipt": {
            "path": str(args.preflight.relative_to(ROOT)),
            "sha256": sha256(args.preflight),
        },
        "generation_batch_manifest": {
            "path": str(args.batch.relative_to(ROOT)),
            "sha256": batch_hash,
        },
        "tournament_policy": {
            "path": str(policy_path.relative_to(ROOT)),
            "sha256": sha256(policy_path),
        },
        "reviewers": accepted_reviews,
        "reviewed_outputs": output_hashes,
        "machine_assessments": machine_assessments,
        "machine_rejected_outputs": rejected_outputs,
        "founder_approval_required": True,
        "founder_approval_recorded": founder_override is not None,
        "approved_output_hashes": approved_output_hashes,
        "downstream_state": downstream_state,
    }
    if founder_override is not None and founder_override_path is not None:
        receipt["founder_override"] = {
            "path": str(founder_override_path.relative_to(ROOT)),
            "sha256": sha256(founder_override_path),
            "gpt_rejection_preserved": True,
        }
    if args.write_receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"{status} judges=1 outputs={len(output_hashes)} batch_sha256={batch_hash}")
    if not args.write_receipt:
        print("NOTE receipt not written; rerun with --write-receipt before compositing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
