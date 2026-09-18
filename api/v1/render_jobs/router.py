"""FastAPI router for Blender render jobs (``/api/v1/render-jobs`` once mounted).

Endpoints:

- ``POST /render-jobs``            enqueue → ``202`` + ``job_id`` + ``status_url``
- ``GET  /render-jobs/{job_id}``   poll one job (``404`` unknown)
- ``GET  /render-jobs``            list recent jobs (capped at 100)
- ``GET  /render-jobs/health``     queue + job store + artifact store reachable (``503`` if not)

Auth posture: identical to ``api/v1/clothing_3d`` — public, no JWT dependency. The surface
is bounded instead of gated: inputs are artifact-store KEYS (no URLs, so no SSRF), the SKU
must exist in the product registry, every render knob is range-limited by the Pydantic
models, and the in-memory queue is capacity-capped. Cost is CPU minutes on the worker, not a
paid API. If this ever fronts a public network, add ``Depends(get_current_user)`` here.

Production wiring mirrors clothing_3d: ``REDIS_URL`` set → Redis Streams queue + Redis job
store shared with ``python -m pipelines.blender_render.worker``; unset → in-process
InMemory queue/store (jobs are lost on restart, and nothing consumes them unless a worker
runs in the same process).
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status

from api.v1.render_jobs.schemas import (
    JobAcceptedResponse,
    JobListResponse,
    JobStatusResponse,
    JobSummary,
)
from pipelines.blender_render.artifacts import (
    ArtifactStoreConfigError,
    KeyedArtifactStore,
    build_artifact_store,
)
from pipelines.blender_render.models import (
    JobStatus,
    OptimizeWebJob,
    RenderJobRecord,
    RenderStillsJob,
)
from pipelines.blender_render.store import (
    RenderJobStore,
    build_render_job_store,
    build_render_queue,
)
from pipelines.clothing_3d.queue import JobQueue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/render-jobs", tags=["Blender Render Jobs"])

_queue: JobQueue | None = None
_store: RenderJobStore | None = None
_artifacts: KeyedArtifactStore | None = None


def get_queue() -> JobQueue:
    global _queue
    if _queue is None:
        _queue = build_render_queue()
    return _queue


def get_store() -> RenderJobStore:
    global _store
    if _store is None:
        _store = build_render_job_store()
    return _store


def get_artifacts() -> KeyedArtifactStore:
    global _artifacts
    if _artifacts is None:
        try:
            _artifacts = build_artifact_store()
        except ArtifactStoreConfigError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"artifact store not configured: {exc}",
            ) from exc
    return _artifacts


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _status_response(job: RenderJobRecord) -> JobStatusResponse:
    return JobStatusResponse(
        ok=job.status != JobStatus.FAILED,
        job_id=job.job_id,
        status=job.status.value,
        job_type=job.request.job_type,
        sku=job.request.sku,
        result=job.result,
        error=job.error,
        submitted_at=job.submitted_at.isoformat(),
        started_at=_iso(job.started_at),
        finished_at=_iso(job.finished_at),
        attempt=job.attempt,
        worker_id=job.worker_id,
    )


RenderJobBody = Annotated[OptimizeWebJob | RenderStillsJob, Body(discriminator="job_type")]


@router.post(
    "",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit an optimize_web or render_stills job",
)
async def submit_render_job(
    body: RenderJobBody,
    request: Request,
    queue: Annotated[JobQueue, Depends(get_queue)],
    store: Annotated[RenderJobStore, Depends(get_store)],
    artifacts: Annotated[KeyedArtifactStore, Depends(get_artifacts)],
) -> JobAcceptedResponse:
    """Validate the source exists, persist the record, enqueue for the worker."""
    if not await artifacts.exists(body.source_key):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"source_key not found in artifact store: {body.source_key}",
        )
    job_id = f"rj_{uuid.uuid4().hex[:16]}"
    record = RenderJobRecord(job_id=job_id, request=body)
    await store.put(record)
    try:
        await queue.enqueue(job_id)
    except Exception as exc:  # noqa: BLE001 — failed enqueue = failed job, surfaced as 503
        await store.update(
            record.with_status(
                JobStatus.FAILED, error=f"enqueue failed: {exc}", finished_at=datetime.now(UTC)
            )
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Queue unavailable: {exc}",
        ) from exc
    base = str(request.url).rstrip("/")
    return JobAcceptedResponse(job_id=job_id, status_url=f"{base}/{job_id}")


@router.get("/health", summary="Readiness — queue, job store and artifact store reachable")
async def render_jobs_health(
    queue: Annotated[JobQueue, Depends(get_queue)],
    store: Annotated[RenderJobStore, Depends(get_store)],
    artifacts: Annotated[KeyedArtifactStore, Depends(get_artifacts)],
) -> Any:
    """An unconfigured artifact store short-circuits to 503 via ``get_artifacts`` itself."""
    detail: dict[str, Any] = {"artifacts": type(artifacts).__name__}
    ok = True
    try:
        detail["queue"] = type(queue).__name__
        detail["queue_depth"] = await queue.depth()
    except Exception as exc:  # noqa: BLE001
        ok, detail["queue_error"] = False, str(exc)
    try:
        await store.list(limit=1)
        detail["store"] = type(store).__name__
    except Exception as exc:  # noqa: BLE001
        ok, detail["store_error"] = False, str(exc)
    if not ok:
        return Response(
            content=json.dumps({"ok": False, **detail}),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
        )
    return {"ok": True, **detail}


@router.get("", response_model=JobListResponse, summary="List recent render jobs")
async def list_render_jobs(
    store: Annotated[RenderJobStore, Depends(get_store)],
    limit: int = 50,
) -> JobListResponse:
    jobs = await store.list(limit=min(max(limit, 1), 100))
    return JobListResponse(
        count=len(jobs),
        jobs=[
            JobSummary(
                job_id=job.job_id,
                status=job.status.value,
                job_type=job.request.job_type,
                sku=job.request.sku,
                submitted_at=job.submitted_at.isoformat(),
                finished_at=_iso(job.finished_at),
                worker_id=job.worker_id,
                error=job.error,
            )
            for job in jobs
        ],
    )


@router.get("/{job_id}", response_model=JobStatusResponse, summary="Fetch one render job")
async def get_render_job(
    job_id: str,
    store: Annotated[RenderJobStore, Depends(get_store)],
) -> JobStatusResponse:
    job = await store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"job not found: {job_id}")
    return _status_response(job)


__all__ = ["router", "get_queue", "get_store", "get_artifacts"]
