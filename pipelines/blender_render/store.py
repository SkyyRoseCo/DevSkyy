"""Queue + job-store wiring for render jobs, reusing the clothing_3d infrastructure.

Reused as-is:

- :class:`pipelines.clothing_3d.queue.InMemoryQueue` / :class:`RedisStreamsQueue` — the
  envelope only carries ``job_id``, so they are job-type agnostic. The Redis stream gets its
  own ``blender_render`` prefix so the clothing worker can never dequeue a render job.
- :class:`pipelines.clothing_3d.job_store.InMemoryJobStore` — it only touches ``job_id`` and
  ``submitted_at``, which :class:`RenderJobRecord` provides.

Adapted (thinnest possible): :class:`RedisJobStore` serialises via ``job.to_dict()`` but its
``get``/``list`` hard-code ``JobRecord.from_dict`` → ``PipelineRequest.model_validate``, so
those two readers are overridden here to decode :class:`RenderJobRecord` instead.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable

from pipelines.blender_render.models import RenderJobRecord
from pipelines.clothing_3d.job_store import InMemoryJobStore, RedisJobStore
from pipelines.clothing_3d.queue import InMemoryQueue, JobQueue, QueueMessage, RedisStreamsQueue

REDIS_PREFIX = "blender_render"


@runtime_checkable
class RenderJobStore(Protocol):
    async def put(self, job: RenderJobRecord) -> None: ...

    async def get(self, job_id: str) -> RenderJobRecord | None: ...

    async def update(self, job: RenderJobRecord) -> None: ...

    async def list(self, *, limit: int = 100) -> list[RenderJobRecord]: ...

    async def close(self) -> None: ...


class RedisRenderJobStore(RedisJobStore):
    """RedisJobStore with readers that decode :class:`RenderJobRecord`."""

    def __init__(self, *, url: str | None = None, ttl_seconds: int = 7 * 24 * 3600) -> None:
        super().__init__(url=url, prefix=REDIS_PREFIX, ttl_seconds=ttl_seconds)

    async def get(self, job_id: str) -> RenderJobRecord | None:  # type: ignore[override]
        client = await self._get_client()
        raw = await client.get(self._key(job_id))
        if not raw:
            return None
        return RenderJobRecord.from_dict(json.loads(raw))

    async def list(self, *, limit: int = 100) -> list[RenderJobRecord]:  # type: ignore[override]
        client = await self._get_client()
        ids = await client.zrevrange(self._index_key, 0, limit - 1)
        if not ids:
            return []
        payloads = await client.mget(*[self._key(job_id) for job_id in ids])
        return [RenderJobRecord.from_dict(json.loads(raw)) for raw in payloads if raw]


class RedisRenderQueue(RedisStreamsQueue):
    """Render deliveries retain pending entries until persisted completion.

    Integration qualification of recovery across multiple workers remains required.
    No MAXLEN trimming: removing accepted work requires an explicit retention policy.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("prefix", REDIS_PREFIX)
        kwargs.setdefault("reclaim_idle_ms", 3_600_000)
        super().__init__(**kwargs)

    async def enqueue(self, job_id: str) -> None:
        client = await self._get_client()
        await self._ensure_group()
        await client.xadd(
            self._stream, {"job_id": job_id, "enqueued_at": datetime.now(UTC).isoformat()}
        )

    async def dequeue(self, *, block_seconds: float = 5.0) -> QueueMessage | None:
        client = await self._get_client()
        await self._ensure_group()
        result = await client.xreadgroup(
            self._group, self._consumer_name, {self._stream: "0"}, count=1
        )
        if result and result[0][1]:
            delivery_id, fields = result[0][1][0]
            return QueueMessage(
                job_id=fields["job_id"],
                delivery_id=delivery_id,
                enqueued_at=datetime.fromisoformat(fields["enqueued_at"]),
                attempt=int(fields.get("attempt", 1)),
            )
        return await super().dequeue(block_seconds=block_seconds)

    async def nack(self, message: QueueMessage, *, requeue: bool = True) -> None:
        if not requeue:
            await self.ack(message)
            return
        client = await self._get_client()
        # Lua stops on an XADD error before any acknowledgement. The retry and
        # settlement are one server-side operation, without a client crash window.
        await client.eval(
            "local id = redis.call('XADD', KEYS[1], '*', 'job_id', ARGV[3], "
            "'enqueued_at', ARGV[4], 'attempt', ARGV[5]); "
            "redis.call('XACK', KEYS[1], ARGV[1], ARGV[2]); "
            "redis.call('XDEL', KEYS[1], ARGV[2]); return id",
            1,
            self._stream,
            self._group,
            message.delivery_id,
            message.job_id,
            datetime.now(UTC).isoformat(),
            message.attempt + 1,
        )


def build_render_queue() -> JobQueue:
    """``RENDER_QUEUE`` = ``memory`` | ``redis``; otherwise Redis iff ``REDIS_URL`` is set."""
    backend = os.getenv("RENDER_QUEUE")
    if backend == "memory":
        return InMemoryQueue()
    if backend == "redis" or os.getenv("REDIS_URL"):
        return RedisRenderQueue()
    return InMemoryQueue()


def build_render_job_store() -> RenderJobStore:
    """``RENDER_JOB_STORE`` = ``memory`` | ``redis``; otherwise Redis iff ``REDIS_URL`` is set."""
    backend = os.getenv("RENDER_JOB_STORE")
    if backend == "memory":
        return InMemoryJobStore()  # type: ignore[return-value]
    if backend == "redis" or os.getenv("REDIS_URL"):
        return RedisRenderJobStore()
    return InMemoryJobStore()  # type: ignore[return-value]


__all__ = [
    "REDIS_PREFIX",
    "InMemoryJobStore",
    "InMemoryQueue",
    "RedisRenderJobStore",
    "RenderJobStore",
    "build_render_job_store",
    "build_render_queue",
]
