"""API schemas for ``/render-jobs`` — thin envelopes over the pipeline models."""

from __future__ import annotations

from pydantic import BaseModel

from pipelines.blender_render.models import OptimizeWebResult, RenderStillsResult


class JobAcceptedResponse(BaseModel):
    ok: bool = True
    job_id: str
    status_url: str


class JobStatusResponse(BaseModel):
    ok: bool
    job_id: str
    status: str
    job_type: str
    sku: str
    result: OptimizeWebResult | RenderStillsResult | None = None
    error: str | None = None
    submitted_at: str
    started_at: str | None = None
    finished_at: str | None = None
    attempt: int
    worker_id: str | None = None


class JobSummary(BaseModel):
    job_id: str
    status: str
    job_type: str
    sku: str
    submitted_at: str
    finished_at: str | None = None
    worker_id: str | None = None
    error: str | None = None


class JobListResponse(BaseModel):
    ok: bool = True
    count: int
    jobs: list[JobSummary]
