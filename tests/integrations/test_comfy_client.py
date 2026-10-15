from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import httpx
import pytest
from PIL import Image

from Comfy.scripts.environment_plate_ooda import (
    FORBIDDEN_ENVIRONMENT_SUBJECTS,
    build_founder_approval_packet,
)
from skyyrose.integrations import comfy_client
from skyyrose.integrations.comfy_client import (
    DEFAULT_COMFY_BASE_URL,
    REQUIRED_BACKGROUND_MODEL,
    REQUIRED_SCENE_NODES,
    RUNWAY_APPROVAL_SCHEMA,
    ComfyClient,
    ComfyExecution,
    ComfyOutput,
    ComfyRuntimeError,
    ComfySubmission,
    ValidatedWorkflow,
    execution_receipt,
    runway_contract_sha256,
    runway_execution_fingerprint,
    workflow_sha256,
)


class FakeTransport(httpx.AsyncBaseTransport):
    def __init__(self, responses: list[httpx.Response]) -> None:
        self.responses = list(responses)
        self.requests: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.responses.pop(0)


def _response(payload: object, status: int = 200) -> httpx.Response:
    return httpx.Response(status, content=json.dumps(payload).encode("utf-8"))


def _stats() -> dict[str, object]:
    return {
        "system": {
            "comfyui_version": "0.34.2",
            "required_frontend_version": "1.49.6",
            "argv": [
                "ComfyUI/main.py",
                "--input-directory",
                "/runtime/input",
                "--output-directory",
                "/runtime/output",
                "--port",
                "8189",
            ],
        }
    }


@pytest.mark.asyncio
async def test_runtime_discovery_defaults_to_desktop_8189_and_checks_inventory() -> None:
    transport = FakeTransport(
        [
            _response(_stats()),
            _response({name: {} for name in REQUIRED_SCENE_NODES}),
            _response([REQUIRED_BACKGROUND_MODEL]),
        ]
    )
    async with ComfyClient(transport=transport) as client:
        snapshot = await client.inspect_runtime()

    assert snapshot.base_url == DEFAULT_COMFY_BASE_URL
    assert snapshot.comfyui_version == "0.34.2"
    assert snapshot.input_directory == "/runtime/input"
    assert snapshot.output_directory == "/runtime/output"
    assert set(snapshot.required_nodes) == REQUIRED_SCENE_NODES


@pytest.mark.asyncio
async def test_missing_birefnet_weights_blocks_runtime() -> None:
    transport = FakeTransport(
        [
            _response(_stats()),
            _response({name: {} for name in REQUIRED_SCENE_NODES}),
            _response([]),
        ]
    )
    async with ComfyClient(transport=transport) as client:
        with pytest.raises(ComfyRuntimeError, match="birefnet"):
            await client.inspect_runtime()


@pytest.mark.asyncio
async def test_workflow_validation_checks_live_node_inputs_and_links() -> None:
    object_info = {
        "LoadImage": {"input": {"required": {"image": ["COMBO", {}]}}},
        "SaveImage": {"input": {"required": {"images": ["IMAGE", {}]}}},
    }
    workflow = {
        "1": {"class_type": "LoadImage", "inputs": {"image": "source.png"}},
        "2": {"class_type": "SaveImage", "inputs": {"images": ["1", 0]}},
    }
    transport = FakeTransport([_response(object_info)])
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(workflow)

    assert sealed.node_classes == ("LoadImage", "SaveImage")
    assert sealed.expected_output_node_ids == ("2",)
    assert sealed.workflow_sha256
    assert transport.requests[0].url.path == "/object_info"


@pytest.mark.asyncio
async def test_workflow_validation_blocks_missing_required_input() -> None:
    object_info = {"LoadImage": {"input": {"required": {"image": ["COMBO", {}]}}}}
    transport = FakeTransport([_response(object_info)])
    async with ComfyClient(transport=transport) as client:
        with pytest.raises(ComfyRuntimeError, match="missing required inputs"):
            await client.validate_workflow({"1": {"class_type": "LoadImage", "inputs": {}}})


@pytest.mark.asyncio
async def test_upload_submit_history_and_output_are_api_bound(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    source.write_bytes(b"source-bytes")
    transport = FakeTransport(
        [
            _response({"name": "source.png", "subfolder": "skyyrose", "type": "input"}),
            _response(
                {
                    "LoadImage": {"input": {"required": {"image": ["COMBO", {}]}}},
                    "SaveImage": {"input": {"required": {"images": ["IMAGE", {}]}}},
                }
            ),
            _response({"prompt_id": "prompt-1", "number": 1}),
            _response(
                {
                    "prompt-1": {
                        "status": {"status_str": "success"},
                        "prompt": [
                            1,
                            "prompt-1",
                            {
                                "1": {"class_type": "LoadImage", "inputs": {"image": "source.png"}},
                                "9": {"class_type": "SaveImage", "inputs": {"images": ["1", 0]}},
                            },
                        ],
                        "outputs": {
                            "9": {
                                "images": [
                                    {
                                        "filename": "scene.png",
                                        "subfolder": "skyyrose",
                                        "type": "output",
                                    }
                                ]
                            }
                        },
                    }
                }
            ),
            httpx.Response(200, content=b"output-bytes"),
        ]
    )
    workflow = {
        "1": {"class_type": "LoadImage", "inputs": {"image": "source.png"}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["1", 0]}},
    }
    async with ComfyClient(transport=transport) as client:
        uploaded = await client.upload_input(source)
        sealed = await client.validate_workflow(workflow)
        submission = await client.submit_prompt(sealed, client_id="test-client")
        execution = await client.wait_for_outputs(submission, sleep=lambda _: _no_sleep())
        output_bytes = await client.download_output(execution, execution.outputs[0])

    assert uploaded.source_sha256 == hashlib.sha256(b"source-bytes").hexdigest()
    assert submission.prompt_id == "prompt-1"
    assert execution.outputs == (ComfyOutput("9", "scene.png", "skyyrose", "output"),)
    assert output_bytes == b"output-bytes"
    assert transport.requests[0].url.path == "/upload/image"
    assert transport.requests[1].url.path == "/object_info"
    assert transport.requests[2].url.path == "/prompt"
    assert transport.requests[3].url.path == "/history/prompt-1"
    assert transport.requests[4].url.path == "/view"


async def _no_sleep() -> None:
    return None


def _write_runway_governance(
    tmp_path: Path,
    *,
    sealed: ValidatedWorkflow,
    marker: Path,
) -> tuple[Path, Path]:
    inspiration = tmp_path / "world.png"
    inspiration.write_bytes(b"composition-inspiration")
    output = tmp_path / "background.png"
    approval_path = tmp_path / "runway-approval.json"
    contract_path = tmp_path / "runway-contract.json"
    payload = sealed.payload()
    runway_node = next(
        node for node in payload.values() if node.get("class_type") == "RunwayTextToImageNode"
    )
    save_node = next(node for node in payload.values() if node.get("class_type") == "SaveImage")
    request = {
        "ratio": runway_node["inputs"].get("ratio", "1920:1080"),
        "num_outputs": 1,
        "prompt": runway_node["inputs"]["prompt"],
        "prompt_source": "local test fixture; no source pixels are uploaded",
    }
    contract = {
        "schema": "skyyrose.runway-environment-plate/1",
        "candidate_id": "LH-COMMERCE-2-RUNWAY-ENVIRONMENT-A1",
        "scene_id": "LH-COMMERCE-2",
        "provider": {
            "name": "runway",
            "route": "comfy_partner_node",
            "node": "RunwayTextToImageNode",
            "model": "gen-4",
            "comfy_base_url": DEFAULT_COMFY_BASE_URL,
        },
        "provider_inputs": {
            "mode": "prompt_only",
            "reference_image": None,
            "protected_assets_sent": [],
        },
        "local_composition_inspiration": [
            {
                "path": str(inspiration),
                "sha256": hashlib.sha256(inspiration.read_bytes()).hexdigest(),
                "authority_role": "COMPOSITION_ATMOSPHERE_ONLY",
                "sent_to_runway": False,
            }
        ],
        "request": request,
        "forbidden_plate_content": list(FORBIDDEN_ENVIRONMENT_SUBJECTS),
        "comfy_local_postprocess": {
            "birefnet_evidence": {
                "schema": "skyyrose.birefnet-edge-confidence/1",
                "model_sha256": "9ab37426bf4de0567af6b5d21b16151357149139362e6e8992021b8ce356a154",
                "role": "ALPHA_AND_EDGE_CONFIDENCE_ONLY",
                "generative_use_allowed": False,
                "independent_visual_review_required": True,
            }
        },
        "credit_control": {
            "max_live_price_usd": sealed.paid_price_usd,
            "max_paid_generations": 1,
            "paid_generations_recorded": 0,
            "automatic_paid_retries": False,
            "approval_receipt": None,
        },
        "execution_blockers": [],
        "output": {
            "candidate_path": str(output),
            "filename_prefix": save_node["inputs"].get("filename_prefix"),
            "approval_path": str(approval_path),
            "attempt_marker": str(marker),
            "promotion_allowed": False,
            "wiring_allowed": False,
            "deployment_allowed": False,
        },
        "post_merge_execution_gate": {"required": False, "action": "SATISFIED"},
    }
    approval = {
        "schema": RUNWAY_APPROVAL_SCHEMA,
        "scene_id": contract["scene_id"],
        "candidate_id": contract["candidate_id"],
        "execution_fingerprint": runway_execution_fingerprint(contract, workflow=sealed),
        "contract_sha256": runway_contract_sha256(contract),
        "approved": True,
        "approver_role": "founder",
        "workflow_sha256": sealed.workflow_sha256,
        "request_sha256": workflow_sha256(request),
        "prompt_sha256": hashlib.sha256(request["prompt"].encode()).hexdigest(),
        "live_node_schema_sha256": sealed.live_schema_sha256,
        "local_composition_inspiration_sha256s": [
            contract["local_composition_inspiration"][0]["sha256"]
        ],
        "output_path": str(output),
        "max_paid_generations": 1,
        "observed_live_price_usd": sealed.paid_price_usd,
        "max_price_usd": sealed.paid_price_usd,
        "attempt_marker_path": str(marker),
        "approved_by": "founder",
        "approved_at": "2026-09-02T00:00:00Z",
    }
    approval_path.write_text(json.dumps(approval), encoding="utf-8")
    contract["credit_control"]["approval_receipt"] = {
        "path": str(approval_path),
        "sha256": hashlib.sha256(approval_path.read_bytes()).hexdigest(),
    }
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    return contract_path, approval_path


def _runway_object_info(price: float = 0.11) -> dict[str, object]:
    return {
        "RunwayTextToImageNode": {
            "input": {"required": {"prompt": ["STRING", {}], "ratio": ["COMBO", {}]}},
            "price_badge": {"expr": json.dumps({"type": "usd", "usd": price})},
            "name": "RunwayTextToImageNode",
            "display_name": "Runway Text to Image",
            "description": "Runway Gen-4 environment generation — cinéma",
            "python_module": "comfy_api_nodes.nodes_runway",
            "api_node": True,
        },
        "ResizeImageMaskNode": {
            "input": {
                "required": {
                    "input": ["IMAGE", {}],
                    "resize_type": ["RESIZE", {}],
                    "scale_method": ["COMBO", {}],
                }
            }
        },
        "SaveImage": {
            "input": {"required": {"images": ["IMAGE", {}], "filename_prefix": ["STRING", {}]}}
        },
    }


def _runway_workflow(
    prompt: str = (
        "Environment only. No people, no garments, no products, no text, no wordmarks, "
        "no signage, no hearts, no roses, no sculptures, no monuments, no robed figures, "
        "no Beast characters, no ballrooms, no flower walls."
    ),
) -> dict[str, object]:
    return {
        "1": {
            "class_type": "RunwayTextToImageNode",
            "inputs": {"prompt": prompt, "ratio": "1920:1080"},
            "_meta": {"title": "LH-COMMERCE-2 product-free environment only"},
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
            "inputs": {"images": ["2", 0], "filename_prefix": "test/environment-a1"},
        },
    }


def test_execution_receipt_binds_workflow_runtime_prompt_and_output() -> None:
    from skyyrose.integrations.comfy_client import ComfyRuntimeSnapshot

    snapshot = ComfyRuntimeSnapshot(
        base_url=DEFAULT_COMFY_BASE_URL,
        comfyui_version="0.34.2",
        frontend_version="1.49.6",
        input_directory="/runtime/input",
        output_directory="/runtime/output",
        required_nodes=tuple(sorted(REQUIRED_SCENE_NODES)),
        background_models=(REQUIRED_BACKGROUND_MODEL,),
    )
    workflow = {"1": {"class_type": "SaveImage", "inputs": {}}}
    canonical = json.dumps(workflow, sort_keys=True, separators=(",", ":"))
    sealed = ValidatedWorkflow(
        canonical_json=canonical,
        workflow_sha256=hashlib.sha256(canonical.encode()).hexdigest(),
        node_classes=("SaveImage",),
        expected_output_node_ids=("1",),
        live_schema_sha256="schema-hash",
        paid_partner_nodes=(),
        paid_price_usd=0.0,
        governing_scene_id=None,
        governing_scene_contract_path=None,
        governing_scene_contract_sha256=None,
        seal="receipt-only-test",
    )
    submission = ComfySubmission("prompt-1", "client-1", sealed)
    output = ComfyOutput("1", "scene.png", "", "output")
    execution = ComfyExecution(submission, (output,), "history-hash", "success")

    receipt = execution_receipt(
        snapshot=snapshot,
        execution=execution,
        output=output,
        output_bytes=b"scene",
    )

    assert receipt["prompt_id"] == "prompt-1"
    assert receipt["workflow_sha256"]
    assert receipt["output"]["sha256"] == hashlib.sha256(b"scene").hexdigest()
    assert receipt["runtime_paths"]["input_directory"] == "/runtime/input"
    assert receipt["history_sha256"] == "history-hash"


def _png_bytes(mode: str, pixels: list[object], size: tuple[int, int] = (2, 1)) -> bytes:
    image = Image.new(mode, size)
    image.putdata(pixels)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_segmentation_receipt_requires_source_foreground_and_mask_binding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from skyyrose.integrations.comfy_client import ComfyRuntimeSnapshot, ComfyUpload

    source_bytes = _png_bytes("RGB", [(10, 20, 30), (40, 50, 60)])
    foreground_bytes = _png_bytes("RGBA", [(10, 20, 30, 255), (40, 50, 60, 0)])
    mask_bytes = _png_bytes("L", [255, 0])
    model = tmp_path / "birefnet.safetensors"
    model.write_bytes(b"test-birefnet-weights")
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    baseline = tmp_path / "coverage-baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "schema": "skyyrose.foreground-coverage-baseline/1",
                "scene_id": "LH-COMMERCE-2",
                "source_sha256": source_sha256,
                "reviewer_role": "visual-commerce-qa",
                "verdict": "PASS",
                "minimum_coverage_ratio": 0.5,
                "maximum_coverage_ratio": 0.75,
            }
        ),
        encoding="utf-8",
    )
    coverage = tmp_path / "coverage.json"
    coverage.write_text(
        json.dumps(
            {
                "schema": "skyyrose.foreground-coverage-authority/1",
                "state": "APPROVED",
                "scene_id": "LH-COMMERCE-2",
                "source_sha256": source_sha256,
                "minimum_coverage_ratio": 0.5,
                "maximum_coverage_ratio": 0.75,
                "independent_baseline_receipt": {
                    "path": str(baseline),
                    "sha256": hashlib.sha256(baseline.read_bytes()).hexdigest(),
                },
                "segmentation_model": {
                    "id": "birefnet",
                    "path": str(model),
                    "sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
                },
            }
        ),
        encoding="utf-8",
    )
    scene_contract = tmp_path / "scene.json"
    scene_contract.write_text(
        json.dumps(
            {
                "schema": "skyyrose.scene-ooda/1",
                "scene_id": "LH-COMMERCE-2",
                "native_scene_workflow": {
                    "segmentation": {
                        "coverage_authority": {
                            "path": str(coverage),
                            "sha256": hashlib.sha256(coverage.read_bytes()).hexdigest(),
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setitem(comfy_client.CANONICAL_SCENE_CONTRACTS, "LH-COMMERCE-2", scene_contract)
    scene_contract_sha256 = hashlib.sha256(scene_contract.read_bytes()).hexdigest()
    canonical = json.dumps(
        {
            "1": {
                "class_type": "LoadImage",
                "inputs": {"image": "skyyrose/source.png"},
            },
            "2": {
                "class_type": "JoinImageWithAlpha",
                "inputs": {"image": ["1", 0], "alpha": ["4", 0]},
            },
            "3": {"class_type": "SaveImage", "inputs": {"images": ["2", 0]}},
            "4": {"class_type": "RemoveBackground", "inputs": {}},
            "5": {"class_type": "MaskToImage", "inputs": {"mask": ["4", 0]}},
            "6": {"class_type": "SaveImage", "inputs": {"images": ["5", 0]}},
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    sealed = ValidatedWorkflow(
        canonical_json=canonical,
        workflow_sha256=hashlib.sha256(canonical.encode()).hexdigest(),
        node_classes=(
            "JoinImageWithAlpha",
            "LoadImage",
            "MaskToImage",
            "RemoveBackground",
            "SaveImage",
            "SaveImage",
        ),
        expected_output_node_ids=("3", "6"),
        live_schema_sha256="schema-hash",
        paid_partner_nodes=(),
        paid_price_usd=0.0,
        governing_scene_id="LH-COMMERCE-2",
        governing_scene_contract_path=str(scene_contract),
        governing_scene_contract_sha256=scene_contract_sha256,
        seal="receipt-only-test",
    )
    foreground = ComfyOutput("3", "foreground.png", "", "output")
    mask = ComfyOutput("6", "mask.png", "", "output")
    execution = ComfyExecution(
        ComfySubmission("prompt-segment", "client", sealed),
        (foreground, mask),
        "history-hash",
        "success",
    )
    snapshot = ComfyRuntimeSnapshot(
        base_url=DEFAULT_COMFY_BASE_URL,
        comfyui_version="0.34.2",
        frontend_version="1.49.6",
        input_directory="/runtime/input",
        output_directory="/runtime/output",
        required_nodes=tuple(sorted(REQUIRED_SCENE_NODES)),
        background_models=(REQUIRED_BACKGROUND_MODEL,),
    )
    upload = ComfyUpload(
        "source.png", "skyyrose", "input", hashlib.sha256(source_bytes).hexdigest()
    )
    with pytest.raises(ComfyRuntimeError, match="complete protected RGB evidence"):
        execution_receipt(
            snapshot=snapshot,
            execution=execution,
            output=foreground,
            output_bytes=foreground_bytes,
        )
    receipt = execution_receipt(
        snapshot=snapshot,
        execution=execution,
        output=foreground,
        output_bytes=foreground_bytes,
        protected_source_upload=upload,
        protected_source_bytes=source_bytes,
        protected_mask_output=mask,
        protected_mask_bytes=mask_bytes,
    )
    assert receipt["protected_asset"]["mask_output"]["filename"] == "mask.png"
    assert receipt["protected_asset"]["verification"]["changed_pixel_count"] == 0

    with pytest.raises(ComfyRuntimeError, match="verification failed"):
        execution_receipt(
            snapshot=snapshot,
            execution=execution,
            output=foreground,
            output_bytes=_png_bytes("RGBA", [(99, 99, 99, 255), (40, 50, 60, 0)]),
            protected_source_upload=upload,
            protected_source_bytes=source_bytes,
            protected_mask_output=mask,
            protected_mask_bytes=mask_bytes,
        )

    uncontracted = tmp_path / "uncontracted-coverage.json"
    uncontracted.write_text(
        json.dumps(
            {
                "schema": "skyyrose.foreground-coverage-authority/1",
                "state": "APPROVED",
                "scene_id": "LH-COMMERCE-2",
                "source_sha256": source_sha256,
                "minimum_coverage_ratio": 0.05,
                "maximum_coverage_ratio": 0.98,
            }
        ),
        encoding="utf-8",
    )
    alternate_contract = tmp_path / "alternate-scene.json"
    alternate_contract.write_text(
        scene_contract.read_text(encoding="utf-8").replace(str(coverage), str(uncontracted)),
        encoding="utf-8",
    )
    with pytest.raises(ComfyRuntimeError, match="hash-stale"):
        monkeypatch.setitem(
            comfy_client.CANONICAL_SCENE_CONTRACTS, "LH-COMMERCE-2", alternate_contract
        )
        execution_receipt(
            snapshot=snapshot,
            execution=execution,
            output=foreground,
            output_bytes=foreground_bytes,
            protected_source_upload=upload,
            protected_source_bytes=source_bytes,
            protected_mask_output=mask,
            protected_mask_bytes=mask_bytes,
        )


@pytest.mark.parametrize(
    "base_url",
    [
        "https://127.0.0.1:8189",
        "http://localhost:8189",
        "http://[::1]:8189",
        "http://127.0.0.1:8188",
        "http://user:pass@127.0.0.1:8189",
        "http://127.0.0.1:8189/api",
        "file:///tmp/comfy",
        "http://example.com:8189",
    ],
)
def test_client_rejects_every_non_pinned_local_origin(base_url: str) -> None:
    with pytest.raises(ValueError, match="exactly"):
        ComfyClient(base_url=base_url)


@pytest.mark.asyncio
async def test_paid_partner_workflow_requires_hash_bound_approval(tmp_path: Path) -> None:
    object_info = _runway_object_info()
    workflow = _runway_workflow()
    transport = FakeTransport(
        [_response(object_info), _response(object_info), _response({"prompt_id": "paid-1"})]
    )
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(workflow)
        with pytest.raises(ComfyRuntimeError, match="candidate-bound"):
            await client.submit_prompt(sealed)
        marker = tmp_path / "runway-attempt.json"
        contract_path, approval_path = _write_runway_governance(
            tmp_path, sealed=sealed, marker=marker
        )
        submission = await client.submit_prompt(
            sealed,
            paid_contract_path=contract_path,
            paid_approval_receipt=approval_path,
            paid_attempt_marker=marker,
        )
    assert submission.prompt_id == "paid-1"
    assert (tmp_path / "runway-attempt.json").is_file()


@pytest.mark.asyncio
async def test_paid_partner_attempt_remains_consumed_after_ambiguous_post(tmp_path: Path) -> None:
    object_info = _runway_object_info()

    class AmbiguousTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            if request.url.path == "/object_info":
                return _response(object_info)
            raise httpx.ConnectError("unknown submission outcome", request=request)

    workflow = _runway_workflow()
    marker = tmp_path / "runway-attempt.json"
    async with ComfyClient(transport=AmbiguousTransport()) as client:
        sealed = await client.validate_workflow(workflow)
        contract_path, approval_path = _write_runway_governance(
            tmp_path, sealed=sealed, marker=marker
        )
        with pytest.raises(ComfyRuntimeError, match="submission failed"):
            await client.submit_prompt(
                sealed,
                paid_contract_path=contract_path,
                paid_approval_receipt=approval_path,
                paid_attempt_marker=marker,
            )
        assert marker.is_file()
        with pytest.raises(ComfyRuntimeError, match="already been consumed"):
            await client.submit_prompt(
                sealed,
                paid_contract_path=contract_path,
                paid_approval_receipt=approval_path,
                paid_attempt_marker=marker,
            )


@pytest.mark.asyncio
async def test_paid_partner_rejects_approval_not_bound_to_contract(tmp_path: Path) -> None:
    object_info = _runway_object_info()
    workflow = _runway_workflow()
    transport = FakeTransport([_response(object_info), _response(object_info)])
    marker = tmp_path / "attempt.json"
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(workflow)
        contract, approval = _write_runway_governance(tmp_path, sealed=sealed, marker=marker)
        document = json.loads(approval.read_text(encoding="utf-8"))
        document["scene_id"] = "ARBITRARY"
        approval.write_text(json.dumps(document), encoding="utf-8")
        with pytest.raises(ComfyRuntimeError, match="hash does not match"):
            await client.submit_prompt(
                sealed,
                paid_contract_path=contract,
                paid_approval_receipt=approval,
                paid_attempt_marker=marker,
            )
    assert marker.exists() is False
    assert all(request.url.path != "/prompt" for request in transport.requests)


@pytest.mark.asyncio
async def test_paid_partner_rechecks_live_price_before_consuming_attempt(tmp_path: Path) -> None:
    initial_info = _runway_object_info()
    changed_info = _runway_object_info(price=0.22)
    workflow = _runway_workflow()
    transport = FakeTransport([_response(initial_info), _response(changed_info)])
    marker = tmp_path / "attempt.json"
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(workflow)
        contract, approval = _write_runway_governance(tmp_path, sealed=sealed, marker=marker)
        with pytest.raises(ComfyRuntimeError, match="schema changed|price changed"):
            await client.submit_prompt(
                sealed,
                paid_contract_path=contract,
                paid_approval_receipt=approval,
                paid_attempt_marker=marker,
            )
    assert marker.exists() is False
    assert all(request.url.path != "/prompt" for request in transport.requests)


@pytest.mark.asyncio
async def test_runway_background_rejects_provider_bound_visual_reference(tmp_path: Path) -> None:
    object_info = {
        "LoadImage": {"input": {"required": {"image": ["COMBO", {}]}}},
        "RunwayTextToImageNode": {
            "input": {
                "required": {
                    "prompt": ["STRING", {}],
                    "reference_image": ["IMAGE", {}],
                }
            },
            "price_badge": {"expr": '{"type":"usd","usd":0.11}'},
        },
        "SaveImage": {"input": {"required": {"images": ["IMAGE", {}]}}},
    }
    valid_prompt = str(_runway_workflow()["1"]["inputs"]["prompt"])
    workflow = {
        "1": {"class_type": "LoadImage", "inputs": {"image": "world.png"}},
        "2": {
            "class_type": "RunwayTextToImageNode",
            "inputs": {"prompt": valid_prompt, "reference_image": ["1", 0]},
        },
        "3": {"class_type": "SaveImage", "inputs": {"images": ["2", 0]}},
    }
    transport = FakeTransport([_response(object_info), _response(object_info)])
    marker = tmp_path / "attempt.json"
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(workflow)
        contract, approval = _write_runway_governance(tmp_path, sealed=sealed, marker=marker)
        with pytest.raises(ComfyRuntimeError, match="must not upload|prompt-only"):
            await client.submit_prompt(
                sealed,
                paid_contract_path=contract,
                paid_approval_receipt=approval,
                paid_attempt_marker=marker,
            )
    assert marker.exists() is False
    assert all(request.url.path != "/prompt" for request in transport.requests)


@pytest.mark.asyncio
async def test_paid_sink_rejects_hash_bound_product_generation_prompt(tmp_path: Path) -> None:
    malicious = (
        "Fashion model wearing LH-003 product pants with logo and text. "
        "No people, no garments, no products, no text, no wordmarks, no signage, no hearts, "
        "no roses, no sculptures, no monuments, no robed figures, no Beast characters, "
        "no ballrooms, no flower walls. Environment only."
    )
    object_info = _runway_object_info()
    workflow = _runway_workflow(malicious)
    transport = FakeTransport([_response(object_info), _response(object_info)])
    marker = tmp_path / "attempt.json"
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(workflow)
        contract, approval = _write_runway_governance(tmp_path, sealed=sealed, marker=marker)
        with pytest.raises(ComfyRuntimeError, match="positively requests forbidden content"):
            await client.submit_prompt(
                sealed,
                paid_contract_path=contract,
                paid_approval_receipt=approval,
                paid_attempt_marker=marker,
            )
    assert marker.exists() is False
    assert all(request.url.path != "/prompt" for request in transport.requests)


@pytest.mark.asyncio
async def test_paid_partner_rejects_unsatisfied_gate_with_matching_fingerprint(
    tmp_path: Path,
) -> None:
    object_info = _runway_object_info()
    transport = FakeTransport([_response(object_info), _response(object_info)])
    marker = tmp_path / "attempt.json"
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(_runway_workflow())
        contract_path, approval = _write_runway_governance(tmp_path, sealed=sealed, marker=marker)
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        contract["post_merge_execution_gate"]["required"] = True
        receipt = json.loads(approval.read_text(encoding="utf-8"))
        receipt["contract_sha256"] = runway_contract_sha256(contract)
        receipt["execution_fingerprint"] = runway_execution_fingerprint(contract, workflow=sealed)
        approval.write_text(json.dumps(receipt), encoding="utf-8")
        contract["credit_control"]["approval_receipt"]["sha256"] = hashlib.sha256(
            approval.read_bytes()
        ).hexdigest()
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        with pytest.raises(
            ComfyRuntimeError, match="paid execution merge/restart state is invalid"
        ):
            await client.submit_prompt(
                sealed,
                paid_contract_path=contract_path,
                paid_approval_receipt=approval,
                paid_attempt_marker=marker,
            )
    assert not marker.exists()
    assert all(request.url.path != "/prompt" for request in transport.requests)


@pytest.mark.asyncio
async def test_paid_partner_rejects_premerge_approval_after_gate_transition(tmp_path: Path) -> None:
    object_info = _runway_object_info()
    transport = FakeTransport([_response(object_info), _response(object_info)])
    marker = tmp_path / "attempt.json"
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(_runway_workflow())
        contract_path, approval = _write_runway_governance(tmp_path, sealed=sealed, marker=marker)
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        contract["post_merge_execution_gate"] = {
            "required": True,
            "action": "REBASE_OR_RESTART_FROM_MERGED_MAIN",
        }
        receipt = json.loads(approval.read_text(encoding="utf-8"))
        receipt["contract_sha256"] = runway_contract_sha256(contract)
        receipt["execution_fingerprint"] = runway_execution_fingerprint(contract, workflow=sealed)
        approval.write_text(json.dumps(receipt), encoding="utf-8")
        contract["credit_control"]["approval_receipt"]["sha256"] = hashlib.sha256(
            approval.read_bytes()
        ).hexdigest()
        contract["post_merge_execution_gate"] = {"required": False, "action": "SATISFIED"}
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        with pytest.raises(ComfyRuntimeError, match="file-backed approval"):
            await client.submit_prompt(
                sealed,
                paid_contract_path=contract_path,
                paid_approval_receipt=approval,
                paid_attempt_marker=marker,
            )
    assert not marker.exists()
    assert all(request.url.path != "/prompt" for request in transport.requests)


@pytest.mark.asyncio
async def test_environment_preflight_and_paid_client_share_exact_fingerprint(
    tmp_path: Path,
) -> None:
    object_info = _runway_object_info()
    workflow = _runway_workflow()
    transport = FakeTransport([_response(object_info)])
    marker = tmp_path / "attempt.json"
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(workflow)
    contract_path, _ = _write_runway_governance(tmp_path, sealed=sealed, marker=marker)
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract["credit_control"]["approval_receipt"] = None
    contract["post_merge_execution_gate"] = {
        "required": True,
        "action": "REBASE_OR_RESTART_FROM_MERGED_MAIN",
    }
    packet = build_founder_approval_packet(
        contract=contract,
        contract_path=contract_path,
        live_object_info=object_info,
    )

    assert packet["live_partner_node"]["schema_sha256"] == sealed.live_schema_sha256
    assert packet["workflow_sha256"] == sealed.workflow_sha256
    assert packet["contract_sha256"] == runway_contract_sha256(contract)
    assert packet["execution_fingerprint"] == runway_execution_fingerprint(
        contract, workflow=sealed
    )


@pytest.mark.asyncio
async def test_caller_cannot_forge_a_free_seal_around_paid_runway_json() -> None:
    workflow = {
        "1": {"class_type": "RunwayTextToImageNode", "inputs": {"prompt": "paid"}},
        "2": {"class_type": "SaveImage", "inputs": {"images": ["1", 0]}},
    }
    canonical = json.dumps(workflow, sort_keys=True, separators=(",", ":"))
    forged = ValidatedWorkflow(
        canonical_json=canonical,
        workflow_sha256=hashlib.sha256(canonical.encode()).hexdigest(),
        node_classes=("RunwayTextToImageNode", "SaveImage"),
        expected_output_node_ids=("2",),
        live_schema_sha256="forged",
        paid_partner_nodes=(),
        paid_price_usd=0.0,
        governing_scene_id=None,
        governing_scene_contract_path=None,
        governing_scene_contract_sha256=None,
        seal="forged",
    )
    transport = FakeTransport([])
    async with ComfyClient(transport=transport) as client:
        with pytest.raises(ComfyRuntimeError, match="metadata was forged"):
            await client.submit_prompt(forged)
    assert transport.requests == []


@pytest.mark.asyncio
async def test_history_must_match_the_sealed_submitted_workflow() -> None:
    object_info = {
        "LoadImage": {"input": {"required": {"image": ["COMBO", {}]}}},
        "SaveImage": {"input": {"required": {"images": ["IMAGE", {}]}}},
    }
    workflow = {
        "1": {"class_type": "LoadImage", "inputs": {"image": "source.png"}},
        "2": {"class_type": "SaveImage", "inputs": {"images": ["1", 0]}},
    }
    history = {
        "prompt-1": {
            "status": {"status_str": "success"},
            "prompt": [1, "prompt-1", {"2": {"class_type": "SaveImage", "inputs": {}}}],
            "outputs": {"2": {"images": [{"filename": "scene.png", "type": "output"}]}},
        }
    }
    transport = FakeTransport(
        [_response(object_info), _response({"prompt_id": "prompt-1"}), _response(history)]
    )
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(workflow)
        submission = await client.submit_prompt(sealed)
        with pytest.raises(ComfyRuntimeError, match="history is not bound"):
            await client.wait_for_outputs(submission, sleep=lambda _: _no_sleep())


@pytest.mark.asyncio
async def test_multi_output_workflow_requires_every_expected_output_node() -> None:
    object_info = {
        "LoadImage": {"input": {"required": {"image": ["COMBO", {}]}}},
        "SaveImage": {"input": {"required": {"images": ["IMAGE", {}]}}},
    }
    workflow = {
        "1": {"class_type": "LoadImage", "inputs": {"image": "source.png"}},
        "2": {"class_type": "SaveImage", "inputs": {"images": ["1", 0]}},
        "3": {"class_type": "SaveImage", "inputs": {"images": ["1", 0]}},
    }
    history = {
        "prompt-1": {
            "status": {"status_str": "success"},
            "prompt": [1, "prompt-1", workflow],
            "outputs": {"3": {"images": [{"filename": "mask.png", "type": "output"}]}},
        }
    }
    transport = FakeTransport(
        [_response(object_info), _response({"prompt_id": "prompt-1"}), _response(history)]
    )
    async with ComfyClient(transport=transport) as client:
        sealed = await client.validate_workflow(workflow)
        submission = await client.submit_prompt(sealed)
        with pytest.raises(ComfyRuntimeError, match="every expected output node"):
            await client.wait_for_outputs(submission, sleep=lambda _: _no_sleep())
