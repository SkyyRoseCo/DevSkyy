"""Hash-bound adapter for the local Comfy Desktop HTTP API."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import io
import json
import os
import time
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx
from PIL import Image, UnidentifiedImageError

DEFAULT_COMFY_BASE_URL = "http://127.0.0.1:8189"
REQUIRED_SCENE_NODES = frozenset(
    {
        "RunwayTextToImageNode",
        "LoadBackgroundRemovalModel",
        "RemoveBackground",
        "LoadImage",
        "ImageScale",
        "ResizeImageMaskNode",
        "ImageCompositeMasked",
        "JoinImageWithAlpha",
        "MaskToImage",
        "ImageToMask",
        "GrowMask",
        "ImageBlur",
        "EmptyImage",
        "SaveImage",
    }
)
REQUIRED_BACKGROUND_MODEL = "birefnet.safetensors"
PAID_PARTNER_NODES = frozenset({"RunwayTextToImageNode"})
RUNWAY_APPROVAL_SCHEMA = "skyyrose.runway-background-paid-approval/1"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SCENE_CONTRACTS: dict[str, Path] = {
    "LH-COMMERCE-2": PROJECT_ROOT
    / "Comfy/scene-contracts/lh-commerce-2-higgsfield-comfy-ooda.json",
}


class ComfyRuntimeError(RuntimeError):
    """Raised when local Comfy state cannot satisfy the scene contract."""


@dataclass(frozen=True)
class ComfyRuntimeSnapshot:
    base_url: str
    comfyui_version: str
    frontend_version: str
    input_directory: str | None
    output_directory: str | None
    required_nodes: tuple[str, ...]
    background_models: tuple[str, ...]


@dataclass(frozen=True)
class ComfyUpload:
    name: str
    subfolder: str
    type: str
    source_sha256: str


@dataclass(frozen=True)
class ComfyOutput:
    node_id: str
    filename: str
    subfolder: str
    type: str


@dataclass(frozen=True)
class ValidatedWorkflow:
    """Canonical workflow sealed to the live node schemas and expected outputs."""

    canonical_json: str
    workflow_sha256: str
    node_classes: tuple[str, ...]
    expected_output_node_ids: tuple[str, ...]
    live_schema_sha256: str
    paid_partner_nodes: tuple[str, ...]
    paid_price_usd: float
    governing_scene_id: str | None
    governing_scene_contract_path: str | None
    governing_scene_contract_sha256: str | None
    seal: str

    def payload(self) -> dict[str, Any]:
        return json.loads(self.canonical_json)


@dataclass(frozen=True)
class ComfySubmission:
    prompt_id: str
    client_id: str
    workflow: ValidatedWorkflow


@dataclass(frozen=True)
class ComfyExecution:
    submission: ComfySubmission
    outputs: tuple[ComfyOutput, ...]
    history_sha256: str
    status: str


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def workflow_sha256(workflow: Mapping[str, Any]) -> str:
    encoded = json.dumps(workflow, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def verify_protected_foreground_rgb(
    *,
    source_bytes: bytes,
    protected_rgba_bytes: bytes,
    alpha_mask_bytes: bytes,
    governing_scene_id: str,
    expected_scene_contract_sha256: str,
) -> dict[str, Any]:
    """Recompute alpha-only proof from a scene-bound, independently reviewed baseline."""
    contract_path = CANONICAL_SCENE_CONTRACTS.get(governing_scene_id)
    if contract_path is None:
        raise ComfyRuntimeError("scene is not registered as a canonical segmentation authority")
    contract_path = contract_path.expanduser().resolve()
    if not contract_path.is_file():
        raise ComfyRuntimeError("governing scene contract is missing")
    contract_bytes = contract_path.read_bytes()
    if sha256_bytes(contract_bytes) != expected_scene_contract_sha256:
        raise ComfyRuntimeError("canonical governing scene contract is hash-stale")
    try:
        contract = json.loads(contract_bytes)
    except json.JSONDecodeError as exc:
        raise ComfyRuntimeError("governing scene contract is invalid JSON") from exc
    segmentation = contract.get("native_scene_workflow", {}).get("segmentation")
    authority_binding = (
        segmentation.get("coverage_authority") if isinstance(segmentation, Mapping) else None
    )
    if (
        contract.get("schema") != "skyyrose.scene-ooda/1"
        or not isinstance(contract.get("scene_id"), str)
        or not isinstance(authority_binding, Mapping)
    ):
        raise ComfyRuntimeError("scene contract does not bind foreground coverage authority")
    authority_path = _bound_path(contract_path, authority_binding.get("path"))
    coverage_authority_sha256 = authority_binding.get("sha256")
    if not isinstance(coverage_authority_sha256, str) or len(coverage_authority_sha256) != 64:
        raise ComfyRuntimeError("scene contract contains an invalid coverage authority hash")
    if not authority_path.is_file():
        raise ComfyRuntimeError("foreground coverage authority is missing")
    authority_bytes = authority_path.read_bytes()
    if sha256_bytes(authority_bytes) != coverage_authority_sha256:
        raise ComfyRuntimeError("foreground coverage authority hash mismatch")
    try:
        authority = json.loads(authority_bytes)
    except json.JSONDecodeError as exc:
        raise ComfyRuntimeError("foreground coverage authority is invalid JSON") from exc
    source_sha256 = sha256_bytes(source_bytes)
    minimum_coverage = authority.get("minimum_coverage_ratio")
    maximum_coverage = authority.get("maximum_coverage_ratio")
    segmentation_model = authority.get("segmentation_model")
    baseline_binding = authority.get("independent_baseline_receipt")
    if not (
        authority.get("schema") == "skyyrose.foreground-coverage-authority/1"
        and authority.get("state") == "APPROVED"
        and authority.get("scene_id") == contract["scene_id"]
        and authority.get("source_sha256") == source_sha256
        and isinstance(minimum_coverage, (int, float))
        and not isinstance(minimum_coverage, bool)
        and isinstance(maximum_coverage, (int, float))
        and not isinstance(maximum_coverage, bool)
        and 0.05 <= float(minimum_coverage) <= float(maximum_coverage) <= 1
        and isinstance(segmentation_model, Mapping)
        and segmentation_model.get("id") == "birefnet"
        and isinstance(segmentation_model.get("path"), str)
        and isinstance(segmentation_model.get("sha256"), str)
        and len(segmentation_model["sha256"]) == 64
        and isinstance(baseline_binding, Mapping)
    ):
        raise ComfyRuntimeError("foreground coverage authority is invalid or source-stale")
    baseline_path = _bound_path(contract_path, baseline_binding.get("path"))
    baseline_sha256 = baseline_binding.get("sha256")
    if not isinstance(baseline_sha256, str) or len(baseline_sha256) != 64:
        raise ComfyRuntimeError("foreground baseline receipt hash is invalid")
    if not baseline_path.is_file() or sha256_bytes(baseline_path.read_bytes()) != baseline_sha256:
        raise ComfyRuntimeError("foreground baseline receipt is missing or hash-stale")
    try:
        baseline = json.loads(baseline_path.read_bytes())
    except json.JSONDecodeError as exc:
        raise ComfyRuntimeError("foreground baseline receipt is invalid JSON") from exc
    if not (
        baseline.get("schema") == "skyyrose.foreground-coverage-baseline/1"
        and baseline.get("scene_id") == contract["scene_id"]
        and baseline.get("source_sha256") == source_sha256
        and baseline.get("reviewer_role") == "visual-commerce-qa"
        and baseline.get("verdict") == "PASS"
        and baseline.get("minimum_coverage_ratio") == minimum_coverage
        and baseline.get("maximum_coverage_ratio") == maximum_coverage
    ):
        raise ComfyRuntimeError("foreground baseline is not an independent passing source match")
    model_path = _readonly_authority_path(contract_path, segmentation_model["path"])
    if (
        not model_path.is_file()
        or sha256_bytes(model_path.read_bytes()) != segmentation_model["sha256"]
    ):
        raise ComfyRuntimeError("BiRefNet model is missing or hash-stale")
    try:
        with Image.open(io.BytesIO(source_bytes)) as source_image:
            source_image.verify()
        with Image.open(io.BytesIO(protected_rgba_bytes)) as protected_image:
            protected_image.verify()
        with Image.open(io.BytesIO(alpha_mask_bytes)) as mask_image:
            mask_image.verify()
        with (
            Image.open(io.BytesIO(source_bytes)) as source_image,
            Image.open(io.BytesIO(protected_rgba_bytes)) as protected_image,
            Image.open(io.BytesIO(alpha_mask_bytes)) as mask_image,
        ):
            source = source_image.convert("RGB")
            protected = protected_image.convert("RGBA")
            mask = mask_image.convert("L")
            source_pixels = list(source.getdata())
            protected_pixels = list(protected.getdata())
            mask_pixels = list(mask.getdata())
    except (OSError, SyntaxError, UnidentifiedImageError) as exc:
        raise ComfyRuntimeError("protected foreground evidence contains an invalid image") from exc
    if source.size != protected.size or source.size != mask.size:
        raise ComfyRuntimeError("source, protected output, and alpha mask geometry must match")
    changed_pixels = 0
    max_channel_delta = 0
    alpha_mismatches = 0
    protected_pixel_count = 0
    transition_values: list[int] = []
    diff = bytearray()
    for source_pixel, protected_pixel, mask_value in zip(
        source_pixels, protected_pixels, mask_pixels, strict=True
    ):
        deltas = tuple(
            abs(left - right) for left, right in zip(source_pixel, protected_pixel[:3], strict=True)
        )
        pixel_delta = max(deltas)
        changed_pixels += int(pixel_delta != 0)
        max_channel_delta = max(max_channel_delta, pixel_delta)
        alpha_mismatches += int(protected_pixel[3] != mask_value)
        protected_pixel_count += int(protected_pixel[3] > 0)
        if 0 < protected_pixel[3] < 255:
            transition_values.append(protected_pixel[3])
        diff.extend(deltas)
    total_pixels = len(source_pixels)
    coverage_ratio = protected_pixel_count / total_pixels
    coverage_pass = protected_pixel_count > 0 and float(
        minimum_coverage
    ) <= coverage_ratio <= float(maximum_coverage)
    status = (
        "PASS" if changed_pixels == 0 and alpha_mismatches == 0 and coverage_pass else "BLOCKED"
    )
    ambiguous_edge_count = sum(32 <= value <= 223 for value in transition_values)
    transition_pixel_count = len(transition_values)
    ambiguous_edge_ratio = (
        ambiguous_edge_count / transition_pixel_count if transition_pixel_count else 0.0
    )
    mean_edge_certainty = (
        sum(abs(value - 127.5) / 127.5 for value in transition_values) / transition_pixel_count
        if transition_pixel_count
        else 1.0
    )
    return {
        "schema": "skyyrose.protected-rgb-verification/1",
        "status": status,
        "policy": "ALPHA_ONLY_INTERIOR_RGB_BYTE_IDENTICAL",
        "source_sha256": source_sha256,
        "protected_output_sha256": sha256_bytes(protected_rgba_bytes),
        "alpha_mask_sha256": sha256_bytes(alpha_mask_bytes),
        "dimensions": {"width": source.size[0], "height": source.size[1]},
        "protected_pixel_count": protected_pixel_count,
        "total_pixel_count": total_pixels,
        "coverage_ratio": coverage_ratio,
        "coverage_pass": coverage_pass,
        "coverage_authority_path": str(authority_path),
        "coverage_authority_sha256": coverage_authority_sha256,
        "governing_scene_contract_path": str(contract_path),
        "governing_scene_contract_sha256": sha256_bytes(contract_bytes),
        "independent_baseline_receipt": {
            "path": str(baseline_path),
            "sha256": baseline_sha256,
            "reviewer_role": baseline["reviewer_role"],
            "verdict": baseline["verdict"],
        },
        "segmentation_model": dict(segmentation_model),
        "edge_confidence": {
            "transition_pixel_count": transition_pixel_count,
            "ambiguous_edge_count": ambiguous_edge_count,
            "ambiguous_edge_ratio": ambiguous_edge_ratio,
            "mean_edge_certainty": mean_edge_certainty,
        },
        "changed_pixel_count": changed_pixels,
        "maximum_channel_delta": max_channel_delta,
        "alpha_mismatch_count": alpha_mismatches,
        "diff_sha256": sha256_bytes(bytes(diff)),
    }


def _runtime_directory(argv: list[Any], flag: str) -> str | None:
    for index, item in enumerate(argv[:-1]):
        if item == flag and isinstance(argv[index + 1], str):
            return argv[index + 1]
    return None


class ComfyClient:
    """Async API client that never assumes project and runtime folders match."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_COMFY_BASE_URL,
        timeout_seconds: float = 30.0,
        poll_interval_seconds: float = 1.0,
        max_poll_seconds: float = 600.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = _validated_local_base_url(base_url)
        self._poll_interval = poll_interval_seconds
        self._max_poll = max_poll_seconds
        self._seal_key = os.urandom(32)
        kwargs: dict[str, Any] = {"base_url": self.base_url, "timeout": timeout_seconds}
        if transport is not None:
            kwargs["transport"] = transport
        self._client = httpx.AsyncClient(**kwargs)

    async def __aenter__(self) -> ComfyClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def _json_get(self, path: str) -> Any:
        try:
            response = await self._client.get(path)
        except httpx.HTTPError as exc:
            raise ComfyRuntimeError(f"Comfy request failed for {path}: {exc}") from exc
        if response.status_code != 200:
            raise ComfyRuntimeError(f"Comfy {path} failed with HTTP {response.status_code}")
        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise ComfyRuntimeError(f"Comfy {path} returned invalid JSON") from exc

    async def inspect_runtime(
        self,
        *,
        required_nodes: frozenset[str] = REQUIRED_SCENE_NODES,
    ) -> ComfyRuntimeSnapshot:
        stats = await self._json_get("/system_stats")
        object_info = await self._json_get("/object_info")
        background_models = await self._json_get("/models/background_removal")
        if not isinstance(stats, dict) or not isinstance(stats.get("system"), dict):
            raise ComfyRuntimeError("Comfy system_stats response is malformed")
        if not isinstance(object_info, dict):
            raise ComfyRuntimeError("Comfy object_info response is malformed")
        if not isinstance(background_models, list) or not all(
            isinstance(item, str) for item in background_models
        ):
            raise ComfyRuntimeError("Comfy background-removal model inventory is malformed")
        missing = sorted(required_nodes - set(object_info))
        if missing:
            raise ComfyRuntimeError(f"Comfy required node inventory is incomplete: {missing}")
        if REQUIRED_BACKGROUND_MODEL not in background_models:
            raise ComfyRuntimeError(
                f"Comfy background-removal model is missing: {REQUIRED_BACKGROUND_MODEL}"
            )
        system = stats["system"]
        argv = system.get("argv", [])
        if not isinstance(argv, list):
            argv = []
        return ComfyRuntimeSnapshot(
            base_url=self.base_url,
            comfyui_version=str(system.get("comfyui_version", "")),
            frontend_version=str(system.get("required_frontend_version", "")),
            input_directory=_runtime_directory(argv, "--input-directory"),
            output_directory=_runtime_directory(argv, "--output-directory"),
            required_nodes=tuple(sorted(required_nodes)),
            background_models=tuple(sorted(background_models)),
        )

    async def upload_input(
        self,
        path: Path,
        *,
        subfolder: str = "skyyrose",
    ) -> ComfyUpload:
        source = path.expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        payload = source.read_bytes()
        if not payload:
            raise ValueError("Comfy input must not be empty")
        try:
            response = await self._client.post(
                "/upload/image",
                files={"image": (source.name, payload, "application/octet-stream")},
                data={"type": "input", "subfolder": subfolder, "overwrite": "false"},
            )
        except httpx.HTTPError as exc:
            raise ComfyRuntimeError(f"Comfy input upload failed: {exc}") from exc
        if response.status_code not in {200, 201}:
            raise ComfyRuntimeError(f"Comfy input upload failed with HTTP {response.status_code}")
        body = response.json()
        if not isinstance(body, dict) or not isinstance(body.get("name"), str):
            raise ComfyRuntimeError("Comfy input upload returned an invalid response")
        return ComfyUpload(
            name=body["name"],
            subfolder=str(body.get("subfolder", "")),
            type=str(body.get("type", "input")),
            source_sha256=sha256_bytes(payload),
        )

    async def validate_workflow(
        self,
        workflow: Mapping[str, Any],
        *,
        expected_output_node_ids: tuple[str, ...] | None = None,
        governing_scene_id: str | None = None,
    ) -> ValidatedWorkflow:
        """Validate node classes, required inputs, and links without submitting a prompt."""
        if not workflow:
            raise ValueError("Comfy workflow must not be empty")
        object_info = await self._json_get("/object_info")
        if not isinstance(object_info, dict):
            raise ComfyRuntimeError("Comfy object_info response is malformed")
        classes: list[str] = []
        output_nodes: list[str] = []
        used_schemas: dict[str, Any] = {}
        node_ids = {str(node_id) for node_id in workflow}
        for raw_node_id, raw_node in workflow.items():
            node_id = str(raw_node_id)
            if not isinstance(raw_node, Mapping):
                raise ComfyRuntimeError(f"Comfy workflow node {node_id} is malformed")
            class_type = raw_node.get("class_type")
            inputs = raw_node.get("inputs")
            if not isinstance(class_type, str) or class_type not in object_info:
                raise ComfyRuntimeError(
                    f"Comfy workflow node {node_id} uses unavailable class {class_type!r}"
                )
            if not isinstance(inputs, Mapping):
                raise ComfyRuntimeError(f"Comfy workflow node {node_id} has invalid inputs")
            class_info = object_info[class_type]
            used_schemas[class_type] = class_info
            input_schema = class_info.get("input") if isinstance(class_info, Mapping) else None
            required = input_schema.get("required") if isinstance(input_schema, Mapping) else None
            if isinstance(required, Mapping):
                missing = sorted(str(name) for name in required if name not in inputs)
                if missing:
                    raise ComfyRuntimeError(
                        f"Comfy workflow node {node_id} ({class_type}) is missing required inputs: "
                        f"{missing}"
                    )
            for name, value in inputs.items():
                if (
                    isinstance(value, list)
                    and len(value) == 2
                    and isinstance(value[0], str)
                    and isinstance(value[1], int)
                    and value[0] not in node_ids
                ):
                    raise ComfyRuntimeError(
                        f"Comfy workflow node {node_id} input {name!r} references missing node "
                        f"{value[0]!r}"
                    )
            classes.append(class_type)
            if class_type == "SaveImage":
                output_nodes.append(node_id)
        expected = tuple(sorted(expected_output_node_ids or tuple(output_nodes)))
        if not expected:
            raise ComfyRuntimeError("Comfy workflow has no expected SaveImage output nodes")
        if any(node_id not in output_nodes for node_id in expected):
            raise ComfyRuntimeError("expected outputs must reference SaveImage nodes")
        canonical_json = json.dumps(workflow, sort_keys=True, separators=(",", ":"))
        governing_path: Path | None = None
        governing_sha256: str | None = None
        if "JoinImageWithAlpha" in classes:
            governing_path = CANONICAL_SCENE_CONTRACTS.get(governing_scene_id or "")
            if governing_path is None:
                raise ComfyRuntimeError(
                    "segmentation workflow requires a registered governing scene ID"
                )
            governing_path = governing_path.expanduser().resolve()
            if not governing_path.is_file():
                raise ComfyRuntimeError("canonical governing scene contract is missing")
            governing_bytes = governing_path.read_bytes()
            try:
                governing_contract = json.loads(governing_bytes)
            except json.JSONDecodeError as exc:
                raise ComfyRuntimeError(
                    "canonical governing scene contract is invalid JSON"
                ) from exc
            segmentation = governing_contract.get("native_scene_workflow", {}).get("segmentation")
            if not (
                governing_contract.get("schema") == "skyyrose.scene-ooda/1"
                and governing_contract.get("scene_id") == governing_scene_id
                and isinstance(segmentation, Mapping)
                and segmentation.get("workflow_sha256")
                == sha256_bytes(canonical_json.encode("utf-8"))
            ):
                raise ComfyRuntimeError(
                    "segmentation workflow does not match its canonical scene contract"
                )
            governing_sha256 = sha256_bytes(governing_bytes)
        elif governing_scene_id is not None:
            raise ComfyRuntimeError("governing scene ID is only valid for segmentation workflows")
        paid_node_instances = [name for name in classes if name in PAID_PARTNER_NODES]
        if len(paid_node_instances) > 1:
            raise ComfyRuntimeError("governed Comfy workflow may contain only one paid node")
        paid_price_usd = sum(_paid_node_price(object_info[name]) for name in paid_node_instances)
        fields = {
            "canonical_json": canonical_json,
            "workflow_sha256": sha256_bytes(canonical_json.encode("utf-8")),
            "node_classes": tuple(sorted(classes)),
            "expected_output_node_ids": expected,
            "live_schema_sha256": workflow_sha256(used_schemas),
            "paid_partner_nodes": tuple(sorted(paid_node_instances)),
            "paid_price_usd": paid_price_usd,
            "governing_scene_id": governing_scene_id,
            "governing_scene_contract_path": (
                str(governing_path) if governing_path is not None else None
            ),
            "governing_scene_contract_sha256": governing_sha256,
        }
        seal = self._workflow_seal(fields)
        return ValidatedWorkflow(
            **fields,
            seal=seal,
        )

    async def submit_prompt(
        self,
        workflow: ValidatedWorkflow,
        *,
        client_id: str | None = None,
        paid_contract_path: Path | None = None,
        paid_approval_receipt: Path | None = None,
        paid_attempt_marker: Path | None = None,
    ) -> ComfySubmission:
        if not isinstance(workflow, ValidatedWorkflow):
            raise TypeError("submit_prompt requires a validated sealed workflow")
        self._verify_workflow_seal(workflow)
        if workflow.paid_partner_nodes:
            if (
                paid_contract_path is None
                or paid_approval_receipt is None
                or paid_attempt_marker is None
            ):
                raise ComfyRuntimeError(
                    "paid Comfy partner workflow requires a governing contract, file-backed "
                    "candidate-bound approval, and an attempt marker"
                )
            await self._refresh_paid_workflow_price(workflow)
            approval, approval_sha256 = _load_runway_approval(
                contract_path=paid_contract_path,
                approval_path=paid_approval_receipt,
                attempt_marker=paid_attempt_marker,
                workflow=workflow,
            )
            _consume_paid_workflow_attempt(
                marker_path=paid_attempt_marker,
                workflow=workflow,
                approval=approval,
                contract_path=paid_contract_path,
                approval_path=paid_approval_receipt,
                approval_sha256=approval_sha256,
            )
        resolved_client_id = client_id or str(uuid.uuid4())
        payload = {"prompt": workflow.payload(), "client_id": resolved_client_id}
        try:
            response = await self._client.post("/prompt", json=payload)
        except httpx.HTTPError as exc:
            raise ComfyRuntimeError(f"Comfy prompt submission failed: {exc}") from exc
        if response.status_code not in {200, 201}:
            raise ComfyRuntimeError(
                f"Comfy prompt submission failed with HTTP {response.status_code}"
            )
        body = response.json()
        prompt_id = body.get("prompt_id") if isinstance(body, dict) else None
        if not isinstance(prompt_id, str) or not prompt_id:
            raise ComfyRuntimeError("Comfy prompt submission returned no prompt_id")
        return ComfySubmission(
            prompt_id=prompt_id,
            client_id=resolved_client_id,
            workflow=workflow,
        )

    def _workflow_seal(self, fields: Mapping[str, Any]) -> str:
        payload = json.dumps(fields, sort_keys=True, separators=(",", ":"), default=list).encode(
            "utf-8"
        )
        return hmac.new(self._seal_key, payload, hashlib.sha256).hexdigest()

    def _verify_workflow_seal(self, workflow: ValidatedWorkflow) -> None:
        try:
            parsed = json.loads(workflow.canonical_json)
        except json.JSONDecodeError as exc:
            raise ComfyRuntimeError("sealed Comfy workflow JSON is invalid") from exc
        canonical = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        classes = tuple(
            sorted(
                node.get("class_type")
                for node in parsed.values()
                if isinstance(node, dict) and isinstance(node.get("class_type"), str)
            )
        )
        output_nodes = tuple(
            sorted(
                str(node_id)
                for node_id, node in parsed.items()
                if isinstance(node, dict) and node.get("class_type") == "SaveImage"
            )
        )
        paid_nodes = tuple(sorted(name for name in classes if name in PAID_PARTNER_NODES))
        canonical_governing_path = CANONICAL_SCENE_CONTRACTS.get(workflow.governing_scene_id or "")
        governance_valid = (
            workflow.governing_scene_id is None
            and workflow.governing_scene_contract_path is None
            and workflow.governing_scene_contract_sha256 is None
        ) or (
            canonical_governing_path is not None
            and canonical_governing_path.resolve()
            == Path(workflow.governing_scene_contract_path or "").resolve()
            and canonical_governing_path.is_file()
            and sha256_bytes(canonical_governing_path.read_bytes())
            == workflow.governing_scene_contract_sha256
        )
        fields = {
            "canonical_json": workflow.canonical_json,
            "workflow_sha256": workflow.workflow_sha256,
            "node_classes": workflow.node_classes,
            "expected_output_node_ids": workflow.expected_output_node_ids,
            "live_schema_sha256": workflow.live_schema_sha256,
            "paid_partner_nodes": workflow.paid_partner_nodes,
            "paid_price_usd": workflow.paid_price_usd,
            "governing_scene_id": workflow.governing_scene_id,
            "governing_scene_contract_path": workflow.governing_scene_contract_path,
            "governing_scene_contract_sha256": workflow.governing_scene_contract_sha256,
        }
        metadata_valid = (
            canonical == workflow.canonical_json
            and sha256_bytes(canonical.encode("utf-8")) == workflow.workflow_sha256
            and classes == workflow.node_classes
            and set(workflow.expected_output_node_ids).issubset(output_nodes)
            and paid_nodes == workflow.paid_partner_nodes
            and governance_valid
        )
        expected_seal = self._workflow_seal(fields)
        if not metadata_valid or not hmac.compare_digest(expected_seal, workflow.seal):
            raise ComfyRuntimeError("Comfy workflow seal is invalid or metadata was forged")

    async def _refresh_paid_workflow_price(self, workflow: ValidatedWorkflow) -> None:
        """Close the validation-to-submit race for live partner-node pricing."""
        object_info = await self._json_get("/object_info")
        if not isinstance(object_info, dict):
            raise ComfyRuntimeError("Comfy object_info response is malformed")
        unique_classes = sorted(set(workflow.node_classes))
        if any(name not in object_info for name in unique_classes):
            raise ComfyRuntimeError("Comfy paid workflow node schema changed before submission")
        live_schemas = {name: object_info[name] for name in unique_classes}
        if workflow_sha256(live_schemas) != workflow.live_schema_sha256:
            raise ComfyRuntimeError("Comfy paid workflow node schema changed before submission")
        current_price = sum(
            _paid_node_price(object_info[name]) for name in workflow.paid_partner_nodes
        )
        if current_price != workflow.paid_price_usd:
            raise ComfyRuntimeError("Comfy paid workflow live price changed before submission")

    async def wait_for_outputs(
        self,
        submission: ComfySubmission,
        *,
        sleep: Any = asyncio.sleep,
    ) -> ComfyExecution:
        if not isinstance(submission, ComfySubmission):
            raise TypeError("wait_for_outputs requires a bound Comfy submission")
        prompt_id = submission.prompt_id
        deadline = time.monotonic() + self._max_poll
        while True:
            history = await self._json_get(f"/history/{prompt_id}")
            entry = history.get(prompt_id) if isinstance(history, dict) else None
            if isinstance(entry, dict):
                status = entry.get("status")
                if isinstance(status, dict) and status.get("status_str") == "error":
                    raise ComfyRuntimeError(f"Comfy prompt {prompt_id} failed")
                if isinstance(status, dict) and status.get("status_str") == "success":
                    self._verify_history_prompt(entry, submission)
                    outputs = self._parse_outputs(
                        entry,
                        expected_node_ids=submission.workflow.expected_output_node_ids,
                    )
                    output_counts = {
                        node_id: sum(output.node_id == node_id for output in outputs)
                        for node_id in submission.workflow.expected_output_node_ids
                    }
                    if any(count != 1 for count in output_counts.values()):
                        raise ComfyRuntimeError(
                            f"Comfy prompt {prompt_id} did not return exactly one image from "
                            f"every expected output node: {output_counts}"
                        )
                    return ComfyExecution(
                        submission=submission,
                        outputs=outputs,
                        history_sha256=workflow_sha256(entry),
                        status="success",
                    )
            if time.monotonic() >= deadline:
                raise ComfyRuntimeError(
                    f"Comfy prompt {prompt_id} produced no outputs within {self._max_poll}s"
                )
            await sleep(self._poll_interval)

    @staticmethod
    def _verify_history_prompt(entry: Mapping[str, Any], submission: ComfySubmission) -> None:
        prompt = entry.get("prompt")
        if (
            not isinstance(prompt, list)
            or len(prompt) < 3
            or prompt[1] != submission.prompt_id
            or not isinstance(prompt[2], Mapping)
            or workflow_sha256(prompt[2]) != submission.workflow.workflow_sha256
        ):
            raise ComfyRuntimeError("Comfy history is not bound to the submitted workflow")

    @staticmethod
    def _parse_outputs(
        entry: Mapping[str, Any], *, expected_node_ids: tuple[str, ...]
    ) -> tuple[ComfyOutput, ...]:
        found: list[ComfyOutput] = []
        outputs = entry.get("outputs")
        if not isinstance(outputs, dict):
            return ()
        for node_id, node_output in outputs.items():
            if str(node_id) not in expected_node_ids:
                continue
            if not isinstance(node_output, dict):
                continue
            images = node_output.get("images")
            if not isinstance(images, list):
                continue
            for image in images:
                if not isinstance(image, dict) or not isinstance(image.get("filename"), str):
                    continue
                found.append(
                    ComfyOutput(
                        node_id=str(node_id),
                        filename=image["filename"],
                        subfolder=str(image.get("subfolder", "")),
                        type=str(image.get("type", "output")),
                    )
                )
        return tuple(found)

    async def download_output(self, execution: ComfyExecution, output: ComfyOutput) -> bytes:
        if output not in execution.outputs:
            raise ComfyRuntimeError("requested output is not bound to this Comfy execution")
        try:
            response = await self._client.get(
                "/view",
                params={
                    "filename": output.filename,
                    "subfolder": output.subfolder,
                    "type": output.type,
                },
            )
        except httpx.HTTPError as exc:
            raise ComfyRuntimeError(f"Comfy output download failed: {exc}") from exc
        if response.status_code != 200 or not response.content:
            raise ComfyRuntimeError(
                f"Comfy output download failed with HTTP {response.status_code}"
            )
        return response.content


def execution_receipt(
    *,
    snapshot: ComfyRuntimeSnapshot,
    execution: ComfyExecution,
    output: ComfyOutput,
    output_bytes: bytes,
    protected_source_upload: ComfyUpload | None = None,
    protected_source_bytes: bytes | None = None,
    protected_mask_output: ComfyOutput | None = None,
    protected_mask_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Build the credential-free runtime evidence required by scene OODA."""
    if output not in execution.outputs:
        raise ComfyRuntimeError("receipt output is not bound to the completed execution")
    sealed = execution.submission.workflow
    output_sha256 = sha256_bytes(output_bytes)
    protected_required = "JoinImageWithAlpha" in sealed.node_classes
    protected_values = (
        protected_source_upload,
        protected_source_bytes,
        protected_mask_output,
        protected_mask_bytes,
        sealed.governing_scene_id,
        sealed.governing_scene_contract_path,
        sealed.governing_scene_contract_sha256,
    )
    if protected_required and any(value is None for value in protected_values):
        raise ComfyRuntimeError("segmentation receipt requires complete protected RGB evidence")
    protected_rgb_verification: dict[str, Any] | None = None
    if any(value is not None for value in protected_values):
        if (
            protected_source_upload is None
            or protected_source_bytes is None
            or protected_mask_output is None
            or protected_mask_bytes is None
            or sealed.governing_scene_id is None
            or sealed.governing_scene_contract_path is None
            or sealed.governing_scene_contract_sha256 is None
            or protected_mask_output not in execution.outputs
            or protected_mask_output == output
            or protected_source_upload.source_sha256 != sha256_bytes(protected_source_bytes)
        ):
            raise ComfyRuntimeError("protected RGB verification does not bind this execution")
        workflow_payload = sealed.payload()
        upload_name = (
            f"{protected_source_upload.subfolder}/{protected_source_upload.name}"
            if protected_source_upload.subfolder
            else protected_source_upload.name
        )
        load_matches = [
            str(node_id)
            for node_id, node in workflow_payload.items()
            if isinstance(node, Mapping)
            and node.get("class_type") == "LoadImage"
            and node.get("inputs", {}).get("image") == upload_name
        ]
        foreground_nodes = _save_nodes_from_class(workflow_payload, "JoinImageWithAlpha")
        mask_nodes = _save_nodes_from_class(workflow_payload, "MaskToImage")
        if (
            len(load_matches) != 1
            or output.node_id not in foreground_nodes
            or protected_mask_output.node_id not in mask_nodes
        ):
            raise ComfyRuntimeError(
                "protected source and outputs do not match the sealed segmentation graph"
            )
        protected_rgb_verification = verify_protected_foreground_rgb(
            source_bytes=protected_source_bytes,
            protected_rgba_bytes=output_bytes,
            alpha_mask_bytes=protected_mask_bytes,
            governing_scene_id=sealed.governing_scene_id,
            expected_scene_contract_sha256=sealed.governing_scene_contract_sha256,
        )
        if protected_rgb_verification["status"] != "PASS":
            raise ComfyRuntimeError("protected RGB verification failed")
    receipt = {
        "schema": "skyyrose.comfy-execution-receipt/1",
        "base_url": snapshot.base_url,
        "comfyui_version": snapshot.comfyui_version,
        "frontend_version": snapshot.frontend_version,
        "required_nodes": list(snapshot.required_nodes),
        "background_models": list(snapshot.background_models),
        "workflow_sha256": sealed.workflow_sha256,
        "live_schema_sha256": sealed.live_schema_sha256,
        "node_classes": list(sealed.node_classes),
        "expected_output_node_ids": list(sealed.expected_output_node_ids),
        "paid_partner_nodes": list(sealed.paid_partner_nodes),
        "prompt_id": execution.submission.prompt_id,
        "history_sha256": execution.history_sha256,
        "history_status": execution.status,
        "output": {
            "node_id": output.node_id,
            "filename": output.filename,
            "subfolder": output.subfolder,
            "type": output.type,
            "sha256": output_sha256,
        },
        "runtime_paths": {
            "input_directory": snapshot.input_directory,
            "output_directory": snapshot.output_directory,
        },
    }
    if protected_rgb_verification is not None:
        assert protected_source_upload is not None
        assert protected_mask_output is not None
        assert protected_mask_bytes is not None
        receipt["protected_asset"] = {
            "source_upload": {
                "name": protected_source_upload.name,
                "subfolder": protected_source_upload.subfolder,
                "type": protected_source_upload.type,
                "sha256": protected_source_upload.source_sha256,
            },
            "foreground_output": receipt["output"],
            "mask_output": {
                "node_id": protected_mask_output.node_id,
                "filename": protected_mask_output.filename,
                "subfolder": protected_mask_output.subfolder,
                "type": protected_mask_output.type,
                "sha256": sha256_bytes(protected_mask_bytes),
            },
            "verification": dict(protected_rgb_verification),
        }
    return receipt


def _save_nodes_from_class(workflow: Mapping[str, Any], source_class: str) -> set[str]:
    source_ids = {
        str(node_id)
        for node_id, node in workflow.items()
        if isinstance(node, Mapping) and node.get("class_type") == source_class
    }
    return {
        str(node_id)
        for node_id, node in workflow.items()
        if isinstance(node, Mapping)
        and node.get("class_type") == "SaveImage"
        and isinstance(node.get("inputs", {}).get("images"), list)
        and str(node["inputs"]["images"][0]) in source_ids
    }


def _validated_local_base_url(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.port != 8189
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Comfy base URL must be exactly http://127.0.0.1:8189")
    return DEFAULT_COMFY_BASE_URL


def _paid_node_price(class_info: Any) -> float:
    if not isinstance(class_info, Mapping):
        raise ComfyRuntimeError("paid Comfy node schema is malformed")
    price_badge = class_info.get("price_badge")
    expression = price_badge.get("expr") if isinstance(price_badge, Mapping) else None
    try:
        price = json.loads(expression)["usd"] if isinstance(expression, str) else None
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ComfyRuntimeError("paid Comfy node has no parseable live USD price") from exc
    if isinstance(price, bool) or not isinstance(price, (int, float)) or price <= 0:
        raise ComfyRuntimeError("paid Comfy node has no positive live USD price")
    return float(price)


def runway_contract_sha256(contract: Mapping[str, Any]) -> str:
    """Hash execution inputs and gate state, excluding the approval binding."""
    normalized = json.loads(json.dumps(contract))
    control = normalized.setdefault("credit_control", {})
    control["approval_receipt"] = None
    # Bind merge readiness exactly as preflight does; stale approvals cannot unlock it.
    return workflow_sha256(normalized)


def runway_execution_fingerprint(
    contract: Mapping[str, Any], *, workflow: ValidatedWorkflow
) -> str:
    """Bind the paid action to contract, prompt, live schema, price, and output paths."""
    output = contract.get("output", {})
    prompt = contract.get("request", {}).get("prompt", "")
    material = {
        "schema": "skyyrose.runway-environment-execution-fingerprint/1",
        "scene_id": contract.get("scene_id"),
        "candidate_id": contract.get("candidate_id"),
        "contract_sha256": runway_contract_sha256(contract),
        "workflow_sha256": workflow.workflow_sha256,
        "prompt_sha256": sha256_bytes(str(prompt).encode("utf-8")),
        "live_node_schema_sha256": workflow.live_schema_sha256,
        "live_price_usd": workflow.paid_price_usd,
        "approval_path": output.get("approval_path"),
        "attempt_marker": output.get("attempt_marker"),
        "max_paid_generations": 1,
    }
    return workflow_sha256(material)


def _runway_project_root(contract_path: Path) -> Path:
    path = contract_path.expanduser().resolve()
    if path.parent.name == "scene-contracts" and path.parent.parent.name == "Comfy":
        return path.parent.parent.parent
    return path.parent


def _bound_path(contract_path: Path, raw: Any) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ComfyRuntimeError("Runway contract contains an invalid path binding")
    root = _runway_project_root(contract_path)
    candidate = Path(raw).expanduser()
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    if not resolved.is_relative_to(root):
        raise ComfyRuntimeError("Runway contract path escapes its project root")
    return resolved


def _load_runway_approval(
    *,
    contract_path: Path,
    approval_path: Path,
    attempt_marker: Path,
    workflow: ValidatedWorkflow,
) -> tuple[dict[str, Any], str]:
    governing_path = contract_path.expanduser().resolve()
    if not governing_path.is_file():
        raise ComfyRuntimeError("Runway governing contract is missing")
    contract_payload = governing_path.read_bytes()
    try:
        contract = json.loads(contract_payload)
    except json.JSONDecodeError as exc:
        raise ComfyRuntimeError("Runway governing contract is invalid JSON") from exc
    if contract.get("schema") != "skyyrose.runway-environment-plate/1":
        raise ComfyRuntimeError("Runway governing contract schema is invalid")
    from Comfy.scripts.environment_plate_ooda import validate_contract

    contract_failures = validate_contract(
        contract,
        contract_path=governing_path,
        execution_ready=True,
    )
    if contract_failures:
        raise ComfyRuntimeError(
            "Runway governing contract is not execution-safe: " + "; ".join(contract_failures)
        )
    contract_fingerprint = runway_execution_fingerprint(contract, workflow=workflow)
    inspirations = contract.get("local_composition_inspiration")
    if not isinstance(inspirations, list) or not inspirations:
        raise ComfyRuntimeError(
            "Runway governing contract must keep composition inspiration out of the provider request"
        )
    inspiration_hashes: list[str] = []
    for inspiration in inspirations:
        if not isinstance(inspiration, Mapping) or inspiration.get("sent_to_runway") is not False:
            raise ComfyRuntimeError(
                "Runway governing contract must keep composition inspiration out of the provider request"
            )
        inspiration_path = _readonly_authority_path(contract_path, inspiration.get("path"))
        inspiration_hash = (
            sha256_bytes(inspiration_path.read_bytes()) if inspiration_path.is_file() else None
        )
        if (
            not isinstance(inspiration_hash, str)
            or len(inspiration_hash) != 64
            or inspiration_hash != inspiration.get("sha256")
        ):
            raise ComfyRuntimeError("Runway composition inspiration is missing or hash-stale")
        inspiration_hashes.append(inspiration_hash)
    output_path = _bound_path(contract_path, contract.get("output", {}).get("candidate_path"))
    contract_marker_path = _bound_path(
        contract_path, contract.get("output", {}).get("attempt_marker")
    )
    approval_binding = contract.get("credit_control", {}).get("approval_receipt")
    if not isinstance(approval_binding, Mapping):
        raise ComfyRuntimeError("Runway governing contract has no paid approval binding")
    path = approval_path.expanduser().resolve()
    bound_approval_path = _bound_path(contract_path, approval_binding.get("path"))
    configured_approval_path = _bound_path(
        contract_path, contract.get("output", {}).get("approval_path")
    )
    if path != bound_approval_path or path != configured_approval_path or not path.is_file():
        raise ComfyRuntimeError("Runway paid approval receipt is missing")
    payload = path.read_bytes()
    approval_hash = sha256_bytes(payload)
    if approval_binding.get("sha256") != approval_hash:
        raise ComfyRuntimeError("Runway paid approval receipt hash does not match its contract")
    try:
        approval = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ComfyRuntimeError("Runway paid approval receipt is invalid JSON") from exc
    marker = attempt_marker.expanduser().resolve()
    configured_marker = approval.get("attempt_marker_path")
    try:
        approval_marker_path = Path(str(configured_marker)).expanduser().resolve()
    except (OSError, ValueError) as exc:
        raise ComfyRuntimeError("Runway approval has an invalid attempt marker") from exc
    try:
        approved_at = datetime.fromisoformat(
            str(approval.get("approved_at", "")).replace("Z", "+00:00")
        )
    except ValueError:
        approved_at = None
    request_sha256 = workflow_sha256(contract.get("request", {}))
    prompt_sha256 = sha256_bytes(str(contract.get("request", {}).get("prompt", "")).encode())
    contract_price = contract.get("credit_control", {}).get("max_live_price_usd")
    _validate_product_free_runway_workflow(workflow.payload())
    expected_workflow = _expected_environment_workflow(contract)
    valid = (
        approval.get("schema") == RUNWAY_APPROVAL_SCHEMA
        and approval.get("approved") is True
        and approval.get("approver_role") == "founder"
        and str(approval.get("approved_by", "")).strip() != ""
        and approved_at is not None
        and approved_at.tzinfo is not None
        and approval.get("scene_id") == contract.get("scene_id")
        and approval.get("candidate_id") == contract.get("candidate_id")
        and approval.get("execution_fingerprint") == contract_fingerprint
        and approval.get("contract_sha256") == runway_contract_sha256(contract)
        and approval.get("workflow_sha256") == workflow.workflow_sha256
        and workflow_sha256(expected_workflow) == workflow.workflow_sha256
        and approval.get("request_sha256") == request_sha256
        and approval.get("prompt_sha256") == prompt_sha256
        and approval.get("live_node_schema_sha256") == workflow.live_schema_sha256
        and approval.get("local_composition_inspiration_sha256s") == inspiration_hashes
        and _bound_path(contract_path, approval.get("output_path")) == output_path
        and approval.get("max_paid_generations") == 1
        and approval_marker_path == marker == contract_marker_path
        and isinstance(approval.get("observed_live_price_usd"), (int, float))
        and float(approval["observed_live_price_usd"]) == workflow.paid_price_usd
        and isinstance(contract_price, (int, float))
        and workflow.paid_price_usd <= float(contract_price)
        and isinstance(approval.get("max_price_usd"), (int, float))
        and workflow.paid_price_usd <= float(approval["max_price_usd"])
        and contract.get("execution_blockers") == []
        and contract.get("post_merge_execution_gate", {}).get("required") is False
    )
    if not valid:
        raise ComfyRuntimeError(
            "paid Comfy partner workflow requires a file-backed approval at the exact live price"
        )
    return approval, approval_hash


def _expected_environment_workflow(contract: Mapping[str, Any]) -> dict[str, Any]:
    request = contract.get("request")
    output = contract.get("output")
    if not isinstance(request, Mapping) or not isinstance(output, Mapping):
        raise ComfyRuntimeError("Runway environment contract request/output is malformed")
    return {
        "1": {
            "class_type": "RunwayTextToImageNode",
            "inputs": {"prompt": request.get("prompt"), "ratio": request.get("ratio")},
            "_meta": {"title": f"{contract.get('scene_id')} product-free environment only"},
        },
        "2": {
            "class_type": "ResizeImageMaskNode",
            "inputs": {
                "input": ["1", 0],
                "resize_type": {
                    "resize_type": "scale dimensions",
                    "width": 2048,
                    "height": 1152,
                    "crop": "disabled",
                },
                "scale_method": "lanczos",
            },
        },
        "3": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["2", 0],
                "filename_prefix": output.get("filename_prefix"),
            },
        },
    }


def _readonly_authority_path(contract_path: Path, raw: Any) -> Path:
    """Resolve a hash-bound, local-only authority without granting it write-path authority."""
    if not isinstance(raw, str) or not raw.strip():
        raise ComfyRuntimeError("Runway contract contains an invalid authority path")
    candidate = Path(raw).expanduser()
    return (
        candidate if candidate.is_absolute() else _runway_project_root(contract_path) / candidate
    ).resolve()


def _validate_product_free_runway_workflow(workflow: Mapping[str, Any]) -> None:
    """Reject any provider-bound image reference in the environment-only Runway route."""
    runway_nodes = [
        node
        for node in workflow.values()
        if isinstance(node, Mapping) and node.get("class_type") == "RunwayTextToImageNode"
    ]
    if len(runway_nodes) != 1:
        raise ComfyRuntimeError("Runway background workflow must contain exactly one Runway node")
    if any(
        isinstance(node, Mapping) and node.get("class_type") == "LoadImage"
        for node in workflow.values()
    ):
        raise ComfyRuntimeError("Runway background workflow must not upload a visual reference")
    inputs = runway_nodes[0].get("inputs")
    if not isinstance(inputs, Mapping):
        raise ComfyRuntimeError("Runway background workflow inputs are malformed")
    for name, value in inputs.items():
        normalized = str(name).casefold()
        if (
            ("image" in normalized or "reference" in normalized)
            and value is not None
            and value != ""
        ):
            raise ComfyRuntimeError("Runway background workflow must be prompt-only")


def _consume_paid_workflow_attempt(
    *,
    marker_path: Path,
    workflow: ValidatedWorkflow,
    approval: Mapping[str, Any],
    contract_path: Path,
    approval_path: Path,
    approval_sha256: str,
) -> None:
    marker = marker_path.expanduser().resolve()
    marker.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "schema": "skyyrose.comfy-paid-attempt-marker/1",
        "workflow_sha256": workflow.workflow_sha256,
        "contract_path": str(contract_path.expanduser().resolve()),
        "contract_sha256": sha256_bytes(contract_path.expanduser().resolve().read_bytes()),
        "approval_path": str(approval_path.expanduser().resolve()),
        "approval_sha256": approval_sha256,
        "scene_id": approval["scene_id"],
        "candidate_id": approval["candidate_id"],
        "execution_fingerprint": approval["execution_fingerprint"],
        "live_price_usd": workflow.paid_price_usd,
        "paid_partner_nodes": list(workflow.paid_partner_nodes),
        "state": "CONSUMED_BEFORE_SUBMISSION",
        "automatic_retry": False,
        "immutable": True,
    }
    try:
        with marker.open("x", encoding="utf-8") as handle:
            json.dump(document, handle, indent=2)
            handle.write("\n")
    except FileExistsError as exc:
        raise ComfyRuntimeError("paid Comfy attempt has already been consumed") from exc
