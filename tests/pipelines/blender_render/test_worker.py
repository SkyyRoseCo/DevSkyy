"""Worker tests with a fake Blender runner: command construction + every fail-closed path."""

from __future__ import annotations

import asyncio
import json
import os
import stat
from pathlib import Path

import pytest
from PIL import Image

from pipelines.blender_render.artifacts import LocalKeyedStore
from pipelines.blender_render.models import (
    JobStatus,
    OptimizeWebJob,
    RenderJobRecord,
    RenderStillsJob,
)
from pipelines.blender_render.store import InMemoryJobStore, InMemoryQueue
from pipelines.blender_render.worker import (
    MAX_INFRA_ATTEMPTS,
    RENDER_SCRIPT,
    SHUTDOWN_ERROR,
    RenderFailure,
    RenderWorker,
    RunResult,
    WorkerConfig,
    build_blender_command,
    check_still,
    stills_payload,
    subprocess_runner,
)
from tests.pipelines.blender_render.glb_fixture import write_box_glb

SKU = "br-006"
SOURCE_KEY = "src/br-006.glb"


def write_noise_png(path: Path, size: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.frombytes("RGBA", (size, size), os.urandom(size * size * 4))
    image.save(path)
    return path


def write_flat_png(path: Path, size: int, rgba: tuple[int, int, int, int]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (size, size), rgba).save(path)
    return path


def payload_of(command: list[str]) -> dict:
    return json.loads(command[command.index("--") + 1])


def fake_runner(
    *, returncode: int = 0, timed_out: bool = False, frames: str = "noise", report: bool = True
):
    """Build a runner that mimics Blender writing (or failing to write) stills."""

    async def _run(command: list[str], timeout_seconds: float) -> RunResult:
        payload = payload_of(command)
        out = Path(payload["out_dir"])
        if frames != "none":
            for index in range(payload["count"]):
                target = out / f"still_{index:02d}.png"
                if frames == "noise":
                    write_noise_png(target, payload["resolution"])
                elif frames == "flat":
                    write_flat_png(target, payload["resolution"], (30, 30, 30, 255))
                elif frames == "transparent":
                    write_flat_png(target, payload["resolution"], (0, 0, 0, 0))
        if report and frames != "none":
            out.mkdir(parents=True, exist_ok=True)
            (out / "report.json").write_text(json.dumps({"blender": "fake 5.2", "stills": []}))
        return RunResult(
            returncode=returncode, stdout="", stderr="fake stderr", timed_out=timed_out
        )

    return _run


@pytest.fixture
def harness(tmp_path: Path):
    artifacts = LocalKeyedStore(tmp_path / "store")
    write_box_glb(tmp_path / "store" / SOURCE_KEY)
    queue = InMemoryQueue()
    store = InMemoryJobStore()
    config = WorkerConfig(
        blender_bin="blender-fake", timeout_seconds=5.0, output_prefix="render-jobs"
    )
    return artifacts, queue, store, config, tmp_path


async def run_job(harness, request, runner) -> tuple[RenderJobRecord, Path]:
    artifacts, queue, store, config, tmp_path = harness
    worker = RenderWorker(
        queue=queue, store=store, artifacts=artifacts, runner=runner, config=config, worker_id="w1"
    )
    record = RenderJobRecord(job_id="rj_test", request=request)
    await store.put(record)
    await queue.enqueue(record.job_id)
    msg = await queue.dequeue(block_seconds=1.0)
    assert msg is not None
    final = await worker.process_one(msg)
    assert final is not None
    assert await queue.depth() == 0  # acked either way
    stored = await store.get("rj_test")
    assert stored == final
    return final, tmp_path / "store"


def stills_job(**overrides) -> RenderStillsJob:
    base = {
        "job_type": "render_stills",
        "sku": SKU,
        "source_key": SOURCE_KEY,
        "count": 2,
        "resolution": 256,
    }
    return RenderStillsJob(**{**base, **overrides})


# ----------------------------------------------------------------- unit helpers


def test_build_blender_command_exact_argv(tmp_path: Path) -> None:
    payload = stills_payload(stills_job(), tmp_path / "s.glb", tmp_path / "out")
    command = build_blender_command("/opt/blender/blender", payload)
    assert command[:7] == [
        "/opt/blender/blender",
        "-b",
        "--factory-startup",
        "--python-exit-code",
        "1",
        "--python",
        str(RENDER_SCRIPT),
    ]
    assert command[7] == "--"
    assert json.loads(command[8]) == payload
    assert RENDER_SCRIPT.is_file()


def test_check_still_rejects_uniform_transparent_missing_and_wrong_size(tmp_path: Path) -> None:
    with pytest.raises(RenderFailure, match="missing"):
        check_still(tmp_path / "nope.png", 256)
    with pytest.raises(RenderFailure, match="uniform"):
        check_still(write_flat_png(tmp_path / "flat.png", 256, (12, 12, 12, 255)), 256)
    with pytest.raises(RenderFailure, match="transparent"):
        check_still(write_flat_png(tmp_path / "clear.png", 256, (0, 0, 0, 0)), 256)
    with pytest.raises(RenderFailure, match="expected"):
        check_still(write_noise_png(tmp_path / "small.png", 128), 256)
    check_still(write_noise_png(tmp_path / "ok.png", 256), 256)


# ----------------------------------------------------------------- worker paths


async def test_render_stills_success_publishes_all_frames(harness) -> None:
    final, store_dir = await run_job(harness, stills_job(count=3), fake_runner())
    assert final.status is JobStatus.SUCCEEDED, final.error
    assert final.worker_id == "w1" and final.attempt == 1
    assert final.started_at is not None and final.finished_at is not None
    result = final.result
    assert result is not None and result.job_type == "render_stills"
    assert [ref.key for ref in result.stills] == [
        f"render-jobs/rj_test/stills/still_{index:02d}.png" for index in range(3)
    ]
    assert result.report.key == "render-jobs/rj_test/stills/report.json"
    assert result.blender_version == "fake 5.2"
    for ref in result.stills:
        assert (store_dir / ref.key).stat().st_size == ref.bytes > 0


async def test_nonzero_exit_fails_with_stderr_tail(harness) -> None:
    final, store_dir = await run_job(harness, stills_job(), fake_runner(returncode=2))
    assert final.status is JobStatus.FAILED
    assert "exited 2" in final.error and "fake stderr" in final.error
    assert not (store_dir / "render-jobs").exists()


async def test_timeout_fails_closed(harness) -> None:
    final, _ = await run_job(harness, stills_job(), fake_runner(returncode=-1, timed_out=True))
    assert final.status is JobStatus.FAILED and "timed out" in final.error


async def test_exit_zero_without_output_fails(harness) -> None:
    final, _ = await run_job(harness, stills_job(), fake_runner(frames="none"))
    assert final.status is JobStatus.FAILED and "report.json" in final.error


async def test_uniform_frame_fails_and_publishes_nothing(harness) -> None:
    final, store_dir = await run_job(harness, stills_job(), fake_runner(frames="flat"))
    assert final.status is JobStatus.FAILED and "uniform" in final.error
    assert not (store_dir / "render-jobs").exists()


async def test_transparent_frame_fails(harness) -> None:
    final, _ = await run_job(harness, stills_job(), fake_runner(frames="transparent"))
    assert final.status is JobStatus.FAILED and "transparent" in final.error


async def test_source_vanished_after_validation_fails(harness) -> None:
    artifacts, _, _, _, tmp_path = harness
    (tmp_path / "store" / SOURCE_KEY).unlink()
    final, _ = await run_job(harness, stills_job(), fake_runner())
    assert final.status is JobStatus.FAILED and "ArtifactNotFoundError" in final.error


async def test_missing_job_record_is_acked_and_skipped(harness) -> None:
    artifacts, queue, store, config, _ = harness
    worker = RenderWorker(
        queue=queue, store=store, artifacts=artifacts, runner=fake_runner(), config=config
    )
    await queue.enqueue("rj_ghost")
    msg = await queue.dequeue(block_seconds=1.0)
    assert await worker.process_one(msg) is None
    assert await queue.depth() == 0


async def test_optimize_web_gate_failure_publishes_nothing(harness, tmp_path: Path) -> None:
    """A gltfpack that merely copies its input yields no meshopt/KTX2 → the gate must block."""
    fake_pack = tmp_path / "gltfpack"
    fake_pack.write_text(
        '#!/bin/sh\nwhile [ $# -gt 0 ]; do case "$1" in -i) i="$2"; shift;; -o) o="$2"; shift;; esac; shift; done\ncp "$i" "$o"\n'
    )
    fake_pack.chmod(fake_pack.stat().st_mode | stat.S_IXUSR)
    artifacts, queue, store, config, _ = harness
    config = WorkerConfig(
        blender_bin=config.blender_bin,
        timeout_seconds=config.timeout_seconds,
        output_prefix=config.output_prefix,
        gltfpack_bin=fake_pack,
    )
    job = OptimizeWebJob(job_type="optimize_web", sku=SKU, source_key=SOURCE_KEY)
    final, store_dir = await run_job(
        (artifacts, queue, store, config, tmp_path), job, fake_runner()
    )
    assert final.status is JobStatus.FAILED
    assert "web gate failed" in final.error and "EXT_meshopt_compression" in final.error
    assert not (store_dir / "render-jobs").exists()


async def test_optimize_web_missing_gltfpack_fails_closed(
    harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GLTFPACK_BIN", "/nonexistent/gltfpack")
    job = OptimizeWebJob(job_type="optimize_web", sku=SKU, source_key=SOURCE_KEY)
    final, _ = await run_job(harness, job, fake_runner())
    assert final.status is JobStatus.FAILED and "GltfpackNotFoundError" in final.error


# ----------------------------------------------------------- review regressions


def test_black_silhouette_frame_fails(tmp_path: Path) -> None:
    """Opaque all-black garment on a transparent background: alpha varies, RGB does not → FAIL."""
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    for y in range(64, 192):
        for x in range(64, 192):
            image.putpixel((x, y), (0, 0, 0, 255))
    path = tmp_path / "silhouette.png"
    image.save(path)
    with pytest.raises(RenderFailure, match="uniform silhouette"):
        check_still(path, 256)


class FailingStore(InMemoryJobStore):
    """update() always raises — simulates a Redis outage mid-job."""

    async def update(self, job) -> None:  # type: ignore[override]
        raise ConnectionError("redis down")


async def test_store_outage_survives_requeues_then_gives_up(harness) -> None:
    artifacts, queue, _, config, tmp_path = harness
    store = FailingStore()
    await InMemoryJobStore.put(store, RenderJobRecord(job_id="rj_test", request=stills_job()))
    worker = RenderWorker(
        queue=queue, store=store, artifacts=artifacts, runner=fake_runner(), config=config
    )
    await queue.enqueue("rj_test")
    seen: list[int] = []
    for _ in range(MAX_INFRA_ATTEMPTS):
        msg = await queue.dequeue(block_seconds=1.0)
        assert msg is not None
        seen.append(msg.attempt)
        assert await worker.process_one(msg) is None  # loop-safe: returns, never raises
    assert seen == [1, 2, 3]
    assert await queue.depth() == 0  # attempts 1-2 were NACKed/requeued, attempt 3 ACKed


class ReclaimingQueue(InMemoryQueue):
    def __init__(self) -> None:
        super().__init__()
        self.reclaims = 0

    async def reclaim_pending(self) -> int:
        self.reclaims += 1
        return 0


async def test_run_starts_reclaim_loop_when_queue_supports_it(harness) -> None:
    artifacts, _, store, config, _ = harness
    queue = ReclaimingQueue()
    worker = RenderWorker(
        queue=queue,
        store=store,
        artifacts=artifacts,
        runner=fake_runner(),
        config=config,
        poll_block_seconds=0.05,
        reclaim_interval_seconds=0.02,
    )
    task = asyncio.create_task(worker.run())
    await asyncio.sleep(0.2)
    await worker.shutdown()
    await asyncio.wait_for(task, timeout=2.0)
    assert queue.reclaims >= 2


async def test_shutdown_mid_job_marks_failed_and_acks(harness) -> None:
    artifacts, queue, store, config, _ = harness
    started = asyncio.Event()

    async def slow_runner(command: list[str], timeout_seconds: float) -> RunResult:
        started.set()
        await asyncio.sleep(30)  # cancelled by shutdown()
        return RunResult(returncode=0, stdout="", stderr="")

    worker = RenderWorker(
        queue=queue,
        store=store,
        artifacts=artifacts,
        runner=slow_runner,
        config=config,
        poll_block_seconds=0.05,
    )
    await store.put(RenderJobRecord(job_id="rj_test", request=stills_job()))
    await queue.enqueue("rj_test")
    task = asyncio.create_task(worker.run())
    await asyncio.wait_for(started.wait(), timeout=2.0)
    await worker.shutdown()
    await asyncio.wait_for(task, timeout=2.0)
    final = await store.get("rj_test")
    assert final is not None and final.status is JobStatus.FAILED
    assert final.error == SHUTDOWN_ERROR
    assert await queue.depth() == 0


async def test_subprocess_runner_kills_child_on_cancel() -> None:
    marker = f"30.{os.getpid()}"
    task = asyncio.create_task(subprocess_runner(["sleep", marker], 60.0))
    await asyncio.sleep(0.3)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    await asyncio.sleep(0.1)
    probe = await asyncio.create_subprocess_exec(
        "pgrep", "-f", f"sleep {marker}", stdout=asyncio.subprocess.PIPE
    )
    out, _ = await probe.communicate()
    assert out.strip() == b"", f"child survived cancellation: {out!r}"


class FlakyArtifacts:
    """Delegates to a LocalKeyedStore but fails the Nth put — exercises all-or-nothing rollback."""

    def __init__(self, inner: LocalKeyedStore, fail_on_put: int) -> None:
        self.inner, self.fail_on_put, self.puts = inner, fail_on_put, 0

    async def fetch(self, key, dest):
        return await self.inner.fetch(key, dest)

    async def exists(self, key):
        return await self.inner.exists(key)

    async def delete(self, key):
        return await self.inner.delete(key)

    async def put(self, src, key, *, content_type):
        self.puts += 1
        if self.puts == self.fail_on_put:
            raise OSError("disk full")
        return await self.inner.put(src, key, content_type=content_type)


async def test_frame_upload_failure_rolls_back_published_frames(harness) -> None:
    artifacts, queue, store, config, tmp_path = harness
    flaky = FlakyArtifacts(artifacts, fail_on_put=3)
    final, store_dir = await run_job(
        (flaky, queue, store, config, tmp_path), stills_job(count=3), fake_runner()
    )
    assert final.status is JobStatus.FAILED and "disk full" in final.error
    assert flaky.puts == 3
    assert not (store_dir / "render-jobs").exists() or not any(
        (store_dir / "render-jobs").rglob("*.png")
    )
