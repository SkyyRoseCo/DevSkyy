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
from typing import Protocol, runtime_checkable

from pipelines.blender_render.models import RenderJobRecord
from pipelines.clothing_3d.job_store import InMemoryJobStore, RedisJobStore
from pipelines.clothing_3d.queue import InMemoryQueue, JobQueue, RedisStreamsQueue

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


def build_render_queue() -> JobQueue:
    """``RENDER_QUEUE`` = ``memory`` | ``redis``; otherwise Redis iff ``REDIS_URL`` is set."""
    backend = os.getenv("RENDER_QUEUE")
    if backend == "memory":
        return InMemoryQueue()
    if backend == "redis" or os.getenv("REDIS_URL"):
        return RedisStreamsQueue(prefix=REDIS_PREFIX)
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
