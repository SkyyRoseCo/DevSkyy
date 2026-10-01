"""Bounded receipt validation and safe projections of declared local runs.

Raw audit prose and review names are never projected. Bookkeeping and pixel
checks do not authenticate an owner, grant release, or prove provider execution.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from PIL import Image

from skyyrose.core.context_resolver import ResolutionRequest, SourceReference
from skyyrose.core.creative_job import (
    JobContract,
    VerificationRecord,
    assess_artifact,
    audit_bundle,
    build_job,
    contract_payload,
    digest,
    execution_bundle,
)

from .governor_reporting import identifier
from .local_composite import AssetRef, CompositeRequest, Placement, verify_composite


class ReceiptError(ValueError):
    """Missing, escaped, oversized, stale or inconsistent local evidence."""


def _path(root: Path, value: str | Path) -> Path:
    candidate = root / value
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(root) or resolved == root:
        raise ReceiptError("Receipt path escapes declared artifact root")
    # Reject symlinks even when their present target is inside the root.
    relative = candidate.absolute().relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ReceiptError("Symlinked receipt paths are unsupported")
    return resolved


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReceiptError("Duplicate receipt JSON keys")
        result[key] = value
    return result


def _read(root: Path, path: Path, max_json_bytes: int) -> dict:
    path = _path(root, path)
    if not path.is_file() or path.stat().st_size > max_json_bytes:
        raise ReceiptError("Receipt JSON exceeds bounded read size")
    with path.open("rb") as stream:
        data = stream.read(max_json_bytes + 1)
    if len(data) > max_json_bytes:
        raise ReceiptError("Receipt JSON exceeds bounded read size")
    try:
        value = json.loads(data, object_pairs_hook=_unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReceiptError("Invalid receipt JSON") from exc
    if not isinstance(value, dict):
        raise ReceiptError("Receipt object required")
    return value


def _bounded_run_files(root: Path, directory: Path, max_files: int, max_json_bytes: int) -> None:
    """Stream directory entries; do not materialize an unbounded recursive glob."""
    pending, count = [directory], 0
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                count += 1
                if count > max_files:
                    raise ReceiptError("Run exceeds bounded file count")
                path = _path(root, Path(entry.path))
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                elif path.suffix == ".json" and path.stat().st_size > max_json_bytes:
                    raise ReceiptError("Run JSON exceeds bounded read size")


def read_receipt_run(
    root: Path,
    run_directory: Path,
    *,
    max_files: int = 64,
    max_json_bytes: int = 1_048_576,
    max_asset_bytes: int = 16_777_216,
) -> dict:
    """Read exactly one declared directory; never discover arbitrary run roots.

    These are local evidence checks. All owner acceptance stays BLOCKED until a
    separate authenticated owner system consumes and approves this exact hash.
    """
    if not (
        type(max_files) is int
        and 1 <= max_files <= 256
        and type(max_json_bytes) is int
        and 1 <= max_json_bytes <= 4_194_304
        and type(max_asset_bytes) is int
        and 1 <= max_asset_bytes <= 67_108_864
    ):
        raise ReceiptError("Bounded receipt limits required")
    root = Path(root).resolve(strict=True)
    directory = _path(root, run_directory)
    if not directory.is_dir():
        raise ReceiptError("Declared run directory required")
    _bounded_run_files(root, directory, max_files, max_json_bytes)
    try:
        link = _read(root, directory / "context-link.json", max_json_bytes)
        execution = _read(root, directory / "execution.json", max_json_bytes)
        audit = _read(root, directory / "audit.json", max_json_bytes)
        production = _read(root, directory / "production.json", max_json_bytes)
        if set(link) != {"execution_sha256", "audit_sha256"}:
            raise ReceiptError("Invalid context linkage schema")
        if link != {"execution_sha256": digest(execution), "audit_sha256": digest(audit)}:
            raise ReceiptError("Context execution/audit hash mismatch")
        if production.get("context") != link:
            raise ReceiptError("Production/context linkage mismatch")
        job = JobContract.model_validate(audit["job"])
        if (
            digest(contract_payload(job.context, job.plan, job.blockers)) != job.contract_id
            or execution != execution_bundle(job)
            or audit != audit_bundle(job)
            or production.get("job_id") != job.job_id
        ):
            raise ReceiptError("Job/contract identity mismatch")
        for ref in (
            job.plan.production_method.inputs
            + job.plan.production_method.feasibility_evidence
            + job.plan.saturation_evidence
        ):
            source = _path(root, ref.path)
            if not source.is_file() or source.stat().st_size > max_asset_bytes:
                raise ReceiptError("Contract source exceeds bounded regular-file read")
        fresh = build_job(ResolutionRequest.model_validate(job.context.request_snapshot), job.plan)
        if fresh.contract_id != job.contract_id or job.blockers:
            raise ReceiptError("Stale or blocked job contract")
        candidates = production["candidates"]
        if not isinstance(candidates, list) or not 1 <= len(candidates) <= 3:
            raise ReceiptError("Bounded candidate set required")
        artifacts, identities = [], set()
        for candidate in candidates:
            receipt = candidate["receipt"]
            data = receipt["request"]
            request = CompositeRequest(
                job_id=data["job_id"],
                source=AssetRef(**data["source"]),
                mask=AssetRef(**data["mask"]),
                background=AssetRef(**data["background"]),
                placement=Placement(**data["placement"]),
                output_path=data["output_path"],
            )
            if request.job_id != job.job_id or receipt.get("job_id") != job.job_id:
                raise ReceiptError("Receipt/job identity mismatch")
            supplied = {(ref.path, ref.sha256) for ref in job.plan.production_method.inputs}
            if (request.source.path, request.source.sha256) not in supplied:
                raise ReceiptError("Source not bound to audited job contract")
            output = _path(root, request.output_path)
            if output.parent != directory:
                raise ReceiptError("Artifact outside declared run")
            for ref in (request.source, request.mask, request.background):
                asset = _path(root, ref.path)
                if not asset.is_file() or asset.stat().st_size > max_asset_bytes:
                    raise ReceiptError("Asset exceeds bounded read size")
                with Image.open(asset) as image:
                    if image.width * image.height > 4_194_304:
                        raise ReceiptError("Asset exceeds bounded decoded pixel count")
            if not output.is_file() or output.stat().st_size > max_asset_bytes:
                raise ReceiptError("Artifact exceeds bounded read size")
            with Image.open(output) as image:
                if image.width * image.height > 4_194_304:
                    raise ReceiptError("Artifact exceeds bounded decoded pixel count")
            sha = hashlib.sha256(output.read_bytes()).hexdigest()
            if sha != receipt.get("output_sha256") or sha in identities:
                raise ReceiptError("Changed or duplicated artifact identity")
            identities.add(sha)
            sidecar = _read(root, output.with_suffix(".png.manifest.json"), max_json_bytes)
            if sidecar != receipt:
                raise ReceiptError("Production/sidecar receipt mismatch")
            technical = verify_composite(request, receipt, root=root)
            stored = _read(
                root,
                directory / f"{identifier(candidate['direction'])}-verification.json",
                max_json_bytes,
            )
            if technical != stored or candidate.get("technical_verification") != technical:
                raise ReceiptError("Stale or changed pixel verification")
            if technical["status"] != "PASS":
                raise ReceiptError("Artifact pixel verification failed")
            artifacts.append(
                {
                    "artifact_sha256": sha,
                    "technical_status": "PASS",
                    "review_state": "MISSING",
                }
            )
        review_path = directory / "review.json"
        if review_path.exists():
            review = _read(root, review_path, max_json_bytes)
            records = [
                VerificationRecord.model_validate(item) for item in review.get("records", [])
            ]
            for artifact in artifacts:
                candidate = next(
                    c
                    for c in candidates
                    if c["receipt"]["output_sha256"] == artifact["artifact_sha256"]
                )
                assessment = assess_artifact(
                    job,
                    SourceReference(
                        path=candidate["receipt"]["output_path"], sha256=artifact["artifact_sha256"]
                    ),
                    records,
                    novelty_evidence=[],
                    experiment_evidence=[],
                    experiment_applicability_reason="Local receipt inspection only",
                    root=root,
                )
                artifact["review_state"] = (
                    "RECORDED_UNAUTHENTICATED" if assessment.release_ready else "BLOCKED_OR_STALE"
                )
        return {
            "schema_version": "1.0",
            "evidence_mode": (
                "SIMULATED" if production.get("evidence_mode") == "SIMULATED" else "LOCAL_ONLY"
            ),
            "job_id": identifier(job.job_id),
            "contract_id": job.contract_id,
            "receipt_state": "VERIFIED",
            "artifacts": artifacts,
            "owner_acceptance": "BLOCKED",
            "publication_authorized": False,
            "spend_authorized": False,
            "actual_spend": None,
            "current_provider_execution": None,
        }
    except (OSError, KeyError, TypeError, ValueError, Image.DecompressionBombError) as exc:
        if isinstance(exc, ReceiptError):
            raise
        raise ReceiptError("Invalid or incomplete linked receipt evidence") from exc
