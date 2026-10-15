"""Router tests for /api/v1/render-jobs using InMemoryQueue + LocalKeyedStore (no Redis, no Blender)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from PIL import Image

from api.v1.render_jobs import router as render_jobs_router
from api.v1.render_jobs.router import get_artifacts, get_queue, get_store
from pipelines.blender_render.artifacts import LocalKeyedStore
from pipelines.blender_render.store import InMemoryJobStore, InMemoryQueue
from pipelines.blender_render.worker import RenderWorker, RunResult, WorkerConfig
from tests.pipelines.blender_render.glb_fixture import write_box_glb

SKU = "br-006"
SOURCE_KEY = "sources/br-006.glb"
BASE = "/api/v1/render-jobs"


@pytest.fixture
def stack(tmp_path: Path):
    artifacts = LocalKeyedStore(tmp_path / "store")
    write_box_glb(tmp_path / "store" / SOURCE_KEY)
    queue, store = InMemoryQueue(), InMemoryJobStore()
    app = FastAPI()
    app.include_router(render_jobs_router, prefix="/api/v1")
    app.dependency_overrides[get_queue] = lambda: queue
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_artifacts] = lambda: artifacts
    return app, queue, store, artifacts, tmp_path


@pytest.fixture
async def client(stack):
    app = stack[0]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http


def stills_body(**overrides) -> dict:
    return {
        "job_type": "render_stills",
        "sku": SKU,
        "source_key": SOURCE_KEY,
        "count": 2,
        "resolution": 256,
        **overrides,
    }


async def test_submit_returns_202_and_job_is_pollable(client, stack) -> None:
    _, queue, store, _, _ = stack
    response = await client.post(BASE, json=stills_body())
    assert response.status_code == 202, response.text
    accepted = response.json()
    assert accepted["ok"] is True and accepted["job_id"].startswith("rj_")
    assert accepted["status_url"] == f"http://test{BASE}/{accepted['job_id']}"
    assert await queue.depth() == 1

    status = await client.get(f"{BASE}/{accepted['job_id']}")
    assert status.status_code == 200
    body = status.json()
    assert (
        body["status"] == "pending" and body["job_type"] == "render_stills" and body["sku"] == SKU
    )
    assert body["result"] is None and body["error"] is None

    listing = await client.get(BASE)
    assert listing.status_code == 200
    assert (
        listing.json()["count"] == 1 and listing.json()["jobs"][0]["job_id"] == accepted["job_id"]
    )


async def test_submit_optimize_web_variant_accepted(client) -> None:
    response = await client.post(
        BASE,
        json={
            "job_type": "optimize_web",
            "sku": SKU,
            "source_key": SOURCE_KEY,
            "anisotropy_strength": 0.3,
        },
    )
    assert response.status_code == 202, response.text


@pytest.mark.parametrize(
    "body, fragment",
    [
        (stills_body(source_key="sources/missing.glb"), "not found in artifact store"),
        (stills_body(source_key="../etc/passwd.glb"), "traversal"),
        (stills_body(sku="zz-999"), "not in the product registry"),
        (stills_body(job_type="bake"), "job_type"),
        (stills_body(count=99), "less than or equal to 36"),
        (stills_body(resolution=4096), "less than or equal to 2048"),
        (stills_body(image_url="http://169.254.169.254/"), "Extra inputs"),
        ({"job_type": "render_stills", "sku": SKU}, "source_key"),
    ],
)
async def test_invalid_submissions_are_422(client, body: dict, fragment: str) -> None:
    response = await client.post(BASE, json=body)
    assert response.status_code == 422, response.text
    assert fragment in json.dumps(response.json())


async def test_unknown_job_is_404(client) -> None:
    response = await client.get(f"{BASE}/rj_doesnotexist")
    assert response.status_code == 404
    assert "job not found" in response.json()["detail"]


async def test_health_reports_queue_store_and_artifacts(client) -> None:
    response = await client.get(f"{BASE}/health")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["ok"] is True
    assert body["queue"] == "InMemoryQueue" and body["queue_depth"] == 0
    assert body["store"] == "InMemoryJobStore"


async def test_worker_completes_submitted_job_end_to_end(client, stack) -> None:
    _, queue, store, artifacts, tmp_path = stack

    async def fake_blender(command: list[str], timeout_seconds: float) -> RunResult:
        payload = json.loads(command[command.index("--") + 1])
        out = Path(payload["out_dir"])
        out.mkdir(parents=True, exist_ok=True)
        size = payload["resolution"]
        for index in range(payload["count"]):
            Image.frombytes("RGBA", (size, size), os.urandom(size * size * 4)).save(
                out / f"still_{index:02d}.png"
            )
        (out / "report.json").write_text(json.dumps({"blender": "5.2.0 LTS"}))
        return RunResult(returncode=0, stdout="", stderr="")

    accepted = (await client.post(BASE, json=stills_body())).json()
    worker = RenderWorker(
        queue=queue,
        store=store,
        artifacts=artifacts,
        runner=fake_blender,
        config=WorkerConfig(blender_bin="fake", timeout_seconds=5.0, output_prefix="render-jobs"),
    )
    msg = await queue.dequeue(block_seconds=1.0)
    await worker.process_one(msg)

    status = (await client.get(f"{BASE}/{accepted['job_id']}")).json()
    assert status["status"] == "succeeded", status
    assert status["ok"] is True and status["worker_id"]
    assert [still["key"] for still in status["result"]["stills"]] == [
        f"render-jobs/{accepted['job_id']}/stills/still_00.png",
        f"render-jobs/{accepted['job_id']}/stills/still_01.png",
    ]
    assert (tmp_path / "store" / status["result"]["report"]["key"]).is_file()
