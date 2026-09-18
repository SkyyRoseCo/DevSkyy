"""Strict-validation tests for the render job models (registry SKU, key traversal, bounds)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pipelines.blender_render.models import (
    MAX_SAMPLE_PIXELS,
    ArtifactRef,
    JobStatus,
    OptimizeWebJob,
    RenderJobRecord,
    RenderStillsJob,
    RenderStillsResult,
    known_skus,
    request_adapter,
    validate_artifact_key,
)

SKU = "br-006"
KEY = "renders/3d/br-006.glb"


def test_registry_skus_load_and_include_known_sku() -> None:
    assert SKU in known_skus()
    assert len(known_skus()) > 10


def test_render_stills_defaults_are_within_bounds() -> None:
    job = RenderStillsJob(job_type="render_stills", sku=SKU, source_key=KEY)
    assert (job.count, job.resolution, job.samples, job.camera) == (8, 1024, 64, "perspective")
    assert job.margin == pytest.approx(0.1)


@pytest.mark.parametrize("sku", ["zz-999", "BR-006", "br-6", "../br-006", "", "br-006 "])
def test_unknown_or_malformed_sku_rejected(sku: str) -> None:
    with pytest.raises(ValidationError):
        RenderStillsJob(job_type="render_stills", sku=sku, source_key=KEY)


@pytest.mark.parametrize(
    "key",
    [
        "../br-006.glb",
        "/abs/br-006.glb",
        "a/../b.glb",
        "a//b.glb",
        ".hidden/br-006.glb",
        "renders/.br-006.glb",
        "http://evil.example/x.glb",
        "renders\\br-006.glb",
        "renders/br-006.png",
        "renders/br-006.GLB",
        "",
        "x" * 600 + ".glb",
        "renders/br 006.glb",
    ],
)
def test_traversal_or_non_glb_keys_rejected(key: str) -> None:
    with pytest.raises(ValueError):
        validate_artifact_key(key)
    with pytest.raises(ValidationError):
        OptimizeWebJob(job_type="optimize_web", sku=SKU, source_key=key)


@pytest.mark.parametrize(
    "field, value",
    [
        ("count", 0),
        ("count", 37),
        ("resolution", 255),
        ("resolution", 2049),
        ("samples", 0),
        ("samples", 1025),
        ("margin", -0.1),
        ("margin", 1.01),
        ("camera", "fisheye"),
    ],
)
def test_render_stills_bounds(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        RenderStillsJob(job_type="render_stills", sku=SKU, source_key=KEY, **{field: value})


@pytest.mark.parametrize(
    "field, value",
    [("anisotropy_strength", 1.1), ("anisotropy_strength", -0.1), ("max_bytes", 99_999)],
)
def test_optimize_web_bounds(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        OptimizeWebJob(job_type="optimize_web", sku=SKU, source_key=KEY, **{field: value})


def test_extra_fields_forbidden_and_models_frozen() -> None:
    with pytest.raises(ValidationError):
        RenderStillsJob(job_type="render_stills", sku=SKU, source_key=KEY, image_url="http://x")
    job = RenderStillsJob(job_type="render_stills", sku=SKU, source_key=KEY)
    with pytest.raises(ValidationError):
        job.count = 3  # type: ignore[misc]


def test_discriminated_union_dispatches_on_job_type() -> None:
    stills = request_adapter.validate_python(
        {"job_type": "render_stills", "sku": SKU, "source_key": KEY, "count": 4}
    )
    assert isinstance(stills, RenderStillsJob) and stills.count == 4
    web = request_adapter.validate_python(
        {"job_type": "optimize_web", "sku": SKU, "source_key": KEY}
    )
    assert isinstance(web, OptimizeWebJob)
    with pytest.raises(ValidationError):
        request_adapter.validate_python({"job_type": "bake_normals", "sku": SKU, "source_key": KEY})


def test_record_round_trips_through_dict_with_result() -> None:
    job = RenderStillsJob(job_type="render_stills", sku=SKU, source_key=KEY, count=2)
    record = RenderJobRecord(job_id="rj_test", request=job)
    still = ArtifactRef(
        key="render-jobs/rj_test/stills/still_00.png", bytes=10, content_type="image/png"
    )
    report = ArtifactRef(
        key="render-jobs/rj_test/stills/report.json", bytes=5, content_type="application/json"
    )
    done = record.with_status(
        JobStatus.SUCCEEDED,
        result=RenderStillsResult(
            stills=(still, still), report=report, blender_version="5.2.0 LTS", duration_seconds=1.5
        ),
    )
    restored = RenderJobRecord.from_dict(done.to_dict())
    assert restored == done
    assert restored.status is JobStatus.SUCCEEDED
    assert isinstance(restored.request, RenderStillsJob)
    assert isinstance(restored.result, RenderStillsResult)
    assert record.status is JobStatus.PENDING  # original untouched (immutable)


@pytest.mark.parametrize(
    "count, resolution, samples",
    [(36, 2048, 1024), (1, 2048, 1024), (36, 1024, 64), (8, 2048, 64)],
)
def test_render_budget_rejects_oversized_jobs(count: int, resolution: int, samples: int) -> None:
    assert count * resolution * resolution * samples > MAX_SAMPLE_PIXELS
    with pytest.raises(ValidationError, match="budget"):
        RenderStillsJob(
            job_type="render_stills",
            sku=SKU,
            source_key=KEY,
            count=count,
            resolution=resolution,
            samples=samples,
        )


@pytest.mark.parametrize(
    "count, resolution, samples",
    [(8, 1024, 64), (36, 512, 64), (4, 2048, 64), (1, 2048, 256)],
)
def test_render_budget_accepts_jobs_within_cap(count: int, resolution: int, samples: int) -> None:
    job = RenderStillsJob(
        job_type="render_stills",
        sku=SKU,
        source_key=KEY,
        count=count,
        resolution=resolution,
        samples=samples,
    )
    assert job.sample_pixels <= MAX_SAMPLE_PIXELS
