"""Recovery regressions: Redis deliveries survive store outages and reach execution."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from pipelines.blender_render.models import JobStatus, RenderJobRecord, RenderStillsJob
from pipelines.blender_render.worker import RenderWorker, WorkerConfig
from pipelines.clothing_3d.queue import QueueMessage


async def test_abort_store_failure_does_not_ack_delivery():
    store = AsyncMock()
    store.update.side_effect = OSError("store unavailable")
    queue = AsyncMock()
    worker = RenderWorker(
        store=store,
        queue=queue,
        artifacts=AsyncMock(),
        config=WorkerConfig(blender_bin="unused", timeout_seconds=1, output_prefix="test"),
    )
    message = QueueMessage("job", "1-0", datetime.now(UTC))
    running = RenderJobRecord(
        job_id="job",
        request=RenderStillsJob(job_type="render_stills", sku="br-006", source_key="source.glb"),
    ).with_status(JobStatus.RUNNING)
    await worker._abort(message, running)
    queue.ack.assert_not_called()
    queue.nack.assert_not_called()


async def test_redis_render_queue_delivers_owned_pending_before_new_messages():
    from pipelines.blender_render.store import RedisRenderQueue

    queue = RedisRenderQueue(url="redis://unused")
    client = AsyncMock()
    queue._client = client
    queue._group_ensured = True
    client.xreadgroup.return_value = [
        (
            "blender_render:queue",
            [("1-0", {"job_id": "reclaimed", "enqueued_at": "2026-10-10T00:00:00+00:00"})],
        )
    ]
    message = await queue.dequeue(block_seconds=0.01)
    assert message is not None and message.job_id == "reclaimed"
    assert client.xreadgroup.call_args.args[2] == {queue._stream: "0"}
    assert client.xreadgroup.await_count == 1


async def test_redis_render_queue_reads_new_when_owned_pending_is_empty():
    from pipelines.blender_render.store import RedisRenderQueue

    queue = RedisRenderQueue(url="redis://unused")
    client = AsyncMock()
    queue._client = client
    queue._group_ensured = True
    client.xreadgroup.side_effect = [[("blender_render:queue", [])], []]
    assert await queue.dequeue(block_seconds=0.01) is None
    assert client.xreadgroup.call_args.args[2] == {queue._stream: ">"}


@pytest.mark.parametrize("method,path", [("get", ""), ("get", "/health"), ("post", "")])
def test_render_routes_reject_anonymous_requests(method, path):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from api.v1.render_jobs import router

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    with TestClient(app, raise_server_exceptions=False) as client:
        response = getattr(client, method)("/api/v1/render-jobs" + path)
    assert response.status_code in (401, 403)


async def test_terminal_replay_does_not_render_again():
    job = RenderJobRecord(
        job_id="job",
        request=RenderStillsJob(job_type="render_stills", sku="br-006", source_key="source.glb"),
    ).with_status(JobStatus.SUCCEEDED)
    store, queue = AsyncMock(), AsyncMock()
    store.get.return_value = job
    worker = RenderWorker(store=store, queue=queue, artifacts=AsyncMock())
    worker.execute = AsyncMock()
    message = QueueMessage("job", "1-0", datetime.now(UTC))
    assert await worker.process_one(message) is job
    worker.execute.assert_not_called()
    store.update.assert_not_called()
    queue.ack.assert_awaited_once_with(message)


@pytest.mark.parametrize("allowed,status", [(False, 403), (True, 200)])
def test_render_routes_require_admin_role(monkeypatch, allowed, status):
    from types import SimpleNamespace

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from api.v1.render_jobs import router
    from api.v1.render_jobs.router import get_store
    from security import jwt_oauth2_auth

    monkeypatch.setattr(
        jwt_oauth2_auth.jwt_manager,
        "validate_token",
        lambda token: SimpleNamespace(has_any_role=lambda roles: allowed),
    )
    store = AsyncMock()
    store.list.return_value = []
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as client:
        response = client.get(
            "/render-jobs", headers={"Authorization": "Bearer synthetic-test-token"}
        )
    assert response.status_code == status
    if not allowed:
        store.list.assert_not_called()


async def test_render_enqueue_does_not_trim_accepted_work():
    from pipelines.blender_render.store import RedisRenderQueue

    queue = RedisRenderQueue(url="redis://unused")
    queue._client = AsyncMock()
    queue._group_ensured = True
    await queue.enqueue("job")
    assert "maxlen" not in queue._client.xadd.call_args.kwargs
