"""Pydantic v2 job contracts for the Blender headless render worker.

Two job types, discriminated on ``job_type``:

- ``optimize_web`` — source GLB → fabric sheen patch (class from the product registry) →
  gltfpack (meshopt + KTX2) → web gate → web GLB artifact + gate report.
- ``render_stills`` — source GLB → N evenly spaced turntable PNG stills (Cycles CPU).

Inputs are artifact-store KEYS, never URLs (no SSRF surface). Keys are validated against
traversal, the SKU must exist in the product registry (``logo-registry.json``, the single
product SOT, read only through :func:`skyyrose.core.product_registry.load_registry`), every
numeric knob is range-limited, and ``render_stills`` additionally enforces a total
``count · resolution² · samples`` budget (:data:`MAX_SAMPLE_PIXELS`) derived from measured
render throughput so one job cannot exceed the worker's timeout.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import StrEnum
from functools import lru_cache
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)

from skyyrose.core.product_registry import load_registry
from skyyrose.elite_studio.pipeline3d.glb_optimize import WEB_BUDGET_BYTES

MAX_KEY_LENGTH = 512
_KEY_CHARS = re.compile(r"^[A-Za-z0-9._/-]+$")
_SKU_RE = re.compile(r"^[a-z]{2}-\d{3}$")


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@lru_cache(maxsize=1)
def known_skus() -> frozenset[str]:
    """SKUs in the product registry. Cached per process; ``known_skus.cache_clear()`` refreshes."""
    return frozenset(load_registry()["products"])


def validate_artifact_key(key: str) -> str:
    """Reject anything that is not a plain relative object key ending in ``.glb``."""
    if not key or len(key) > MAX_KEY_LENGTH:
        raise ValueError(f"key must be 1..{MAX_KEY_LENGTH} characters")
    if not _KEY_CHARS.match(key):
        raise ValueError("key may only contain [A-Za-z0-9._/-]")
    if key.startswith("/"):
        raise ValueError("key must be relative (no leading '/')")
    segments = key.split("/")
    if any(segment in {"", ".", ".."} or segment.startswith(".") for segment in segments):
        raise ValueError("key contains an empty, dot or traversal segment")
    if not key.endswith(".glb"):
        raise ValueError("key must reference a .glb object")
    return key


class _JobBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    sku: str = Field(description="Registry SKU, e.g. br-006")
    source_key: str = Field(description="Artifact-store key of the SOURCE (uncompressed) GLB")

    @field_validator("sku")
    @classmethod
    def _sku_in_registry(cls, value: str) -> str:
        if not _SKU_RE.match(value):
            raise ValueError("sku must look like xx-000")
        if value not in known_skus():
            raise ValueError(f"sku {value!r} is not in the product registry")
        return value

    @field_validator("source_key")
    @classmethod
    def _key_is_safe(cls, value: str) -> str:
        return validate_artifact_key(value)


class OptimizeWebJob(_JobBase):
    job_type: Literal["optimize_web"]
    anisotropy_strength: float | None = Field(default=None, ge=0.0, le=1.0)
    max_bytes: int = Field(default=WEB_BUDGET_BYTES, ge=100_000, le=WEB_BUDGET_BYTES)


# Per-job render budget in "sample-pixels" = count · resolution² · samples. Measured
# 2026-09-17 on br-006 (8.7 MB source, Apple M-series, 8 threads, Cycles CPU): 4 × 768² × 64
# = 151 M sample-pixels rendered in 8.4 s wall ≈ 18 M/s. At the 2 G cap that is ≈ 110 s
# natively; even a worker 10× slower (emulated linux/amd64 on Apple Silicon) stays ≈ 1100 s,
# inside the 1800 s default RENDER_JOB_TIMEOUT_SECONDS. Defaults (8 × 1024² × 64 = 537 M)
# fit; the per-field maxima do NOT combine (36 × 2048² × 1024 = 155 G is rejected).
MAX_SAMPLE_PIXELS = 2_000_000_000


class RenderStillsJob(_JobBase):
    job_type: Literal["render_stills"]
    count: int = Field(default=8, ge=1, le=36)
    resolution: int = Field(default=1024, ge=256, le=2048)
    samples: int = Field(default=64, ge=1, le=1024)
    camera: Literal["perspective", "orthographic"] = "perspective"
    margin: float = Field(default=0.1, ge=0.0, le=1.0)

    @property
    def sample_pixels(self) -> int:
        return self.count * self.resolution * self.resolution * self.samples

    @model_validator(mode="after")
    def _within_render_budget(self) -> RenderStillsJob:
        if self.sample_pixels > MAX_SAMPLE_PIXELS:
            raise ValueError(
                f"count·resolution²·samples = {self.sample_pixels:,} exceeds the per-job "
                f"budget of {MAX_SAMPLE_PIXELS:,} sample-pixels; lower count, resolution or samples"
            )
        return self


RenderJobRequest = Annotated[OptimizeWebJob | RenderStillsJob, Field(discriminator="job_type")]
request_adapter: TypeAdapter[OptimizeWebJob | RenderStillsJob] = TypeAdapter(RenderJobRequest)


class ArtifactRef(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: str
    bytes: int = Field(ge=0)
    content_type: str


class OptimizeWebResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    job_type: Literal["optimize_web"] = "optimize_web"
    fabric_class: str
    matched_keyword: str
    sheen: dict[str, float] | None
    web_glb: ArtifactRef
    source_bytes: int
    gltfpack_version: str
    gate_violations: tuple[str, ...] = ()


class RenderStillsResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    job_type: Literal["render_stills"] = "render_stills"
    stills: tuple[ArtifactRef, ...]
    report: ArtifactRef
    blender_version: str
    duration_seconds: float


RenderJobResult = Annotated[OptimizeWebResult | RenderStillsResult, Field(discriminator="job_type")]


class RenderJobRecord(BaseModel):
    """Persisted job state. Immutable — advance it with :meth:`model_copy`."""

    model_config = ConfigDict(frozen=True)

    job_id: str
    request: RenderJobRequest
    status: JobStatus = JobStatus.PENDING
    result: RenderJobResult | None = None
    error: str | None = None
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    finished_at: datetime | None = None
    attempt: int = 0
    worker_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RenderJobRecord:
        return cls.model_validate(payload)

    def with_status(self, status: JobStatus, **changes: Any) -> RenderJobRecord:
        return self.model_copy(update={"status": status, **changes})


__all__ = [
    "MAX_SAMPLE_PIXELS",
    "ArtifactRef",
    "JobStatus",
    "OptimizeWebJob",
    "OptimizeWebResult",
    "RenderJobRecord",
    "RenderJobRequest",
    "RenderJobResult",
    "RenderStillsJob",
    "RenderStillsResult",
    "known_skus",
    "request_adapter",
    "validate_artifact_key",
]
