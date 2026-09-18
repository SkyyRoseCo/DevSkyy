"""Blender headless render worker — ``python -m pipelines.blender_render.worker``.

Loop: dequeue → load :class:`RenderJobRecord` → mark RUNNING → execute in a per-job temp dir
→ publish outputs to the keyed artifact store → mark SUCCEEDED/FAILED with error detail → ACK.

Fail-closed rules (every one is a job FAILURE, never a silent pass):

- Blender non-zero exit, timeout (process killed), missing ``report.json`` or any still.
- A still that is the wrong size, fully transparent, or whose OPAQUE pixels are uniform in
  RGB (stddev below :data:`MIN_PIXEL_STDDEV`) — a black silhouette from failed lights or a
  frame the camera missed both fail; the alpha edge alone can never make a frame pass.
- ``optimize_web``: unclassifiable fabric, gltfpack error, or a web-gate violation. A GLB that
  fails the gate is NOT published.
- Outputs are published all-or-nothing: a failed upload rolls back the frames already put.

Delivery semantics (at-least-once, bounded):

- A *render* failure is deterministic for its input → FAILED record, message ACKed.
- An *infrastructure* failure (job store or queue raising around the render) → the delivery
  is NACKed for retry up to :data:`MAX_INFRA_ATTEMPTS`, then ACKed and logged loudly; the
  loop itself never dies on a job.
- Queues exposing ``reclaim_pending`` (Redis Streams) get a janitor task so a message left
  pending by a crashed worker is re-delivered instead of stranding the job in RUNNING.
- SIGTERM/SIGINT cancels the in-flight job: the Blender child is killed, the record is marked
  FAILED ("worker shutdown"), the message ACKed, then the loop exits.

Jobs run sequentially: one Cycles render saturates every core, so worker concurrency is
achieved by running more worker containers, not more tasks per worker.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import socket
import tempfile
import time
import uuid
from collections.abc import Awaitable, Callable
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat

from pipelines.blender_render.artifacts import KeyedArtifactStore, build_artifact_store
from pipelines.blender_render.models import (
    ArtifactRef,
    JobStatus,
    OptimizeWebJob,
    OptimizeWebResult,
    RenderJobRecord,
    RenderStillsJob,
    RenderStillsResult,
)
from pipelines.blender_render.store import (
    RenderJobStore,
    build_render_job_store,
    build_render_queue,
)
from pipelines.clothing_3d.queue import JobQueue, QueueMessage
from skyyrose.core.product_registry import load_registry
from skyyrose.elite_studio.pipeline3d.glb_materials import (
    SHEEN_PRESETS,
    AnisotropyParams,
    MaterialPatchError,
    apply_fabric_extensions,
    classify_product,
)
from skyyrose.elite_studio.pipeline3d.glb_optimize import (
    gltfpack_version,
    pack_for_web,
    resolve_gltfpack,
    web_gate,
)

logger = logging.getLogger(__name__)

RENDER_SCRIPT = Path(__file__).resolve().parent / "render_stills.py"
STILL_NAME = "still_{index:02d}.png"
REPORT_NAME = "report.json"
MIN_PIXEL_STDDEV = 2.0
OPAQUE_ALPHA = 200
MAX_INFRA_ATTEMPTS = 3
SHUTDOWN_ERROR = "worker shutdown before completion"
_OUTPUT_TAIL = 1200


class RenderFailure(RuntimeError):
    """A job-level failure with an operator-readable reason."""


@dataclass(frozen=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


BlenderRunner = Callable[[list[str], float], Awaitable[RunResult]]


async def _kill(proc: asyncio.subprocess.Process) -> None:
    if proc.returncode is None:
        with suppress(ProcessLookupError):
            proc.kill()
        with suppress(ProcessLookupError):
            await proc.wait()


async def subprocess_runner(command: list[str], timeout_seconds: float) -> RunResult:
    """Run Blender as a child; kill it on timeout (reported) or on task cancellation (re-raised)."""
    proc = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
    except TimeoutError:
        await _kill(proc)
        return RunResult(returncode=-1, stdout="", stderr="", timed_out=True)
    except asyncio.CancelledError:
        await _kill(proc)
        raise
    return RunResult(
        returncode=proc.returncode if proc.returncode is not None else -1,
        stdout=out.decode("utf-8", errors="replace"),
        stderr=err.decode("utf-8", errors="replace"),
    )


def build_blender_command(
    blender_bin: str, payload: dict[str, Any], *, script: Path = RENDER_SCRIPT
) -> list[str]:
    """Exact argv handed to Blender; ``--python-exit-code 1`` makes script exceptions fatal."""
    return [
        blender_bin,
        "-b",
        "--factory-startup",
        "--python-exit-code",
        "1",
        "--python",
        str(script),
        "--",
        json.dumps(payload, separators=(",", ":")),
    ]


def stills_payload(job: RenderStillsJob, source: Path, out_dir: Path) -> dict[str, Any]:
    return {
        "source": str(source),
        "out_dir": str(out_dir),
        "count": job.count,
        "resolution": job.resolution,
        "samples": job.samples,
        "camera": job.camera,
        "margin": job.margin,
    }


def check_still(path: Path, resolution: int) -> None:
    """Reject a missing, mis-sized, empty, or uniform-over-opaque-pixels frame."""
    if not path.is_file() or path.stat().st_size == 0:
        raise RenderFailure(f"still missing or empty: {path.name}")
    with Image.open(path) as opened:
        image = opened.convert("RGBA")
    if image.size != (resolution, resolution):
        raise RenderFailure(f"{path.name} is {image.size}, expected {(resolution, resolution)}")
    opaque = image.getchannel("A").point(lambda alpha: 255 if alpha >= OPAQUE_ALPHA else 0)
    stats = ImageStat.Stat(image.convert("RGB"), mask=opaque)
    if not stats.count or stats.count[0] == 0:
        raise RenderFailure(
            f"{path.name} is fully transparent (no opaque pixels) — nothing was rendered"
        )
    spread = max(stats.stddev)
    if spread < MIN_PIXEL_STDDEV:
        raise RenderFailure(f"{path.name} is a uniform silhouette (opaque RGB stddev {spread:.2f})")


def _tail(text: str) -> str:
    return text.strip()[-_OUTPUT_TAIL:]


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class WorkerConfig:
    blender_bin: str
    timeout_seconds: float
    output_prefix: str
    gltfpack_bin: Path | None = None

    @classmethod
    def from_env(cls) -> WorkerConfig:
        override = os.getenv("GLTFPACK_BIN")
        return cls(
            blender_bin=os.getenv("BLENDER_BIN", "blender"),
            timeout_seconds=float(os.getenv("RENDER_JOB_TIMEOUT_SECONDS", "1800")),
            output_prefix=os.getenv("RENDER_OUTPUT_PREFIX", "render-jobs").strip("/"),
            gltfpack_bin=Path(override) if override else None,
        )


class RenderWorker:
    """Sequential job consumer. All collaborators are injectable for tests."""

    def __init__(
        self,
        *,
        queue: JobQueue | None = None,
        store: RenderJobStore | None = None,
        artifacts: KeyedArtifactStore | None = None,
        runner: BlenderRunner = subprocess_runner,
        config: WorkerConfig | None = None,
        worker_id: str | None = None,
        poll_block_seconds: float = 5.0,
        reclaim_interval_seconds: float = 30.0,
    ) -> None:
        self.queue = queue or build_render_queue()
        self.store = store or build_render_job_store()
        self.artifacts = artifacts or build_artifact_store()
        self.runner = runner
        self.config = config or WorkerConfig.from_env()
        self.worker_id = worker_id or f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:6]}"
        self.poll_block_seconds = poll_block_seconds
        self.reclaim_interval_seconds = reclaim_interval_seconds
        self._stop = asyncio.Event()
        self._current: asyncio.Task[Any] | None = None

    # ------------------------------------------------------------------ lifecycle

    async def run(self) -> None:
        logger.info("render-worker.start id=%s blender=%s", self.worker_id, self.config.blender_bin)
        reclaim_task: asyncio.Task[Any] | None = None
        if callable(getattr(self.queue, "reclaim_pending", None)):
            reclaim_task = asyncio.create_task(self._reclaim_loop(), name="render-reclaim")
        try:
            while not self._stop.is_set():
                msg = await self.queue.dequeue(block_seconds=self.poll_block_seconds)
                if msg is None:
                    continue
                await self._run_current(msg)
        finally:
            if reclaim_task is not None:
                reclaim_task.cancel()
                with suppress(asyncio.CancelledError):
                    await reclaim_task
        logger.info("render-worker.stopped id=%s", self.worker_id)

    async def _run_current(self, msg: QueueMessage) -> None:
        self._current = asyncio.create_task(self.process_one(msg), name=f"render-{msg.job_id}")
        try:
            await self._current
        except asyncio.CancelledError:
            if not self._stop.is_set():
                raise
        except Exception:  # noqa: BLE001 — the loop must outlive any single job
            logger.exception("render-worker.unhandled job_id=%s", msg.job_id)
        finally:
            self._current = None

    async def shutdown(self) -> None:
        """Stop after the current job is aborted (child killed, record FAILED, message ACKed)."""
        self._stop.set()
        if self._current is not None and not self._current.done():
            self._current.cancel()

    async def _reclaim_loop(self) -> None:
        reclaim = self.queue.reclaim_pending  # type: ignore[attr-defined]
        while not self._stop.is_set():
            try:
                count = await reclaim()
                if count:
                    logger.info("render-worker.reclaimed count=%s", count)
            except Exception:  # noqa: BLE001
                logger.exception("render-worker.reclaim_failed")
            with suppress(TimeoutError):
                await asyncio.wait_for(self._stop.wait(), timeout=self.reclaim_interval_seconds)

    # ------------------------------------------------------------------ one job

    async def process_one(self, msg: QueueMessage) -> RenderJobRecord | None:
        running: RenderJobRecord | None = None
        try:
            job = await self.store.get(msg.job_id)
            if job is None:
                logger.warning("render-worker.job_missing job_id=%s", msg.job_id)
                await self._settle(msg, ack=True)
                return None
            running = job.with_status(
                JobStatus.RUNNING, started_at=_now(), attempt=msg.attempt, worker_id=self.worker_id
            )
            await self.store.update(running)
            final = await self._run_job(running)
            await self.store.update(final)
        except asyncio.CancelledError:
            await self._abort(msg, running)
            raise
        except Exception as exc:  # noqa: BLE001 — store/queue trouble, not a render failure
            logger.exception(
                "render-worker.infra_error job_id=%s attempt=%s", msg.job_id, msg.attempt
            )
            await self._infra_failure(msg, running, exc)
            return None
        await self._settle(msg, ack=True)
        return final

    async def _run_job(self, running: RenderJobRecord) -> RenderJobRecord:
        try:
            result = await self.execute(running)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — every render failure becomes a FAILED record
            logger.exception("render-worker.job_failed job_id=%s", running.job_id)
            return running.with_status(
                JobStatus.FAILED, error=f"{type(exc).__name__}: {exc}"[:2000], finished_at=_now()
            )
        return running.with_status(
            JobStatus.SUCCEEDED, result=result, error=None, finished_at=_now()
        )

    async def _abort(self, msg: QueueMessage, running: RenderJobRecord | None) -> None:
        """Shutdown mid-job: the runner already killed the child; record it and ACK."""
        logger.warning("render-worker.aborted job_id=%s", msg.job_id)
        if running is not None:
            failed = running.with_status(JobStatus.FAILED, error=SHUTDOWN_ERROR, finished_at=_now())
            try:
                await self.store.update(failed)
            except Exception:  # noqa: BLE001
                logger.exception("render-worker.abort_record_failed job_id=%s", msg.job_id)
        await self._settle(msg, ack=True)

    async def _infra_failure(
        self, msg: QueueMessage, running: RenderJobRecord | None, exc: Exception
    ) -> None:
        """Retry the delivery while attempts remain; after that, give up loudly but ACK."""
        if running is not None:
            failed = running.with_status(
                JobStatus.FAILED,
                error=f"infrastructure: {type(exc).__name__}: {exc}"[:2000],
                finished_at=_now(),
            )
            with suppress(Exception):
                await self.store.update(failed)
        requeue = msg.attempt < MAX_INFRA_ATTEMPTS
        if not requeue:
            logger.error(
                "render-worker.giving_up job_id=%s after %s attempts", msg.job_id, msg.attempt
            )
        await self._settle(msg, ack=not requeue)

    async def _settle(self, msg: QueueMessage, *, ack: bool) -> None:
        try:
            if ack:
                await self.queue.ack(msg)
            else:
                await self.queue.nack(msg, requeue=True)
        except Exception:  # noqa: BLE001 — a dead queue must not take the loop down
            logger.exception("render-worker.settle_failed job_id=%s ack=%s", msg.job_id, ack)

    async def execute(self, job: RenderJobRecord) -> OptimizeWebResult | RenderStillsResult:
        with tempfile.TemporaryDirectory(prefix=f"render-{job.job_id}-") as tmp:
            workdir = Path(tmp)
            request = job.request
            if isinstance(request, RenderStillsJob):
                return await self._render_stills(job.job_id, request, workdir)
            if isinstance(request, OptimizeWebJob):
                return await self._optimize_web(job.job_id, request, workdir)
            raise RenderFailure(f"unsupported job type {type(request).__name__}")

    # ------------------------------------------------------------------ publishing

    async def _publish_all(self, items: list[tuple[Path, str, str]]) -> list[ArtifactRef]:
        """Put every (path, key, content_type); on any failure delete what was already put."""
        published: list[ArtifactRef] = []
        try:
            for path, key, content_type in items:
                published.append(await self.artifacts.put(path, key, content_type=content_type))
        except BaseException:
            for ref in published:
                with suppress(Exception):
                    await self.artifacts.delete(ref.key)
            raise
        return published

    # ------------------------------------------------------------------ stills

    async def _render_stills(
        self, job_id: str, request: RenderStillsJob, workdir: Path
    ) -> RenderStillsResult:
        source = await self.artifacts.fetch(request.source_key, workdir / "source.glb")
        out_dir = workdir / "stills"
        command = build_blender_command(
            self.config.blender_bin, stills_payload(request, source, out_dir)
        )
        started = time.perf_counter()
        run = await self.runner(command, self.config.timeout_seconds)
        duration = time.perf_counter() - started
        if run.timed_out:
            raise RenderFailure(f"blender timed out after {self.config.timeout_seconds:.0f}s")
        if run.returncode != 0:
            raise RenderFailure(
                f"blender exited {run.returncode}: {_tail(run.stderr or run.stdout)}"
            )
        report_path = out_dir / REPORT_NAME
        if not report_path.is_file():
            raise RenderFailure("blender exited 0 but wrote no report.json")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        # Validate every frame BEFORE uploading any, so a bad frame publishes nothing.
        names = [STILL_NAME.format(index=index) for index in range(request.count)]
        for name in names:
            check_still(out_dir / name, request.resolution)
        prefix = f"{self.config.output_prefix}/{job_id}/stills"
        items = [(out_dir / name, f"{prefix}/{name}", "image/png") for name in names]
        items.append((report_path, f"{prefix}/{REPORT_NAME}", "application/json"))
        refs = await self._publish_all(items)
        return RenderStillsResult(
            stills=tuple(refs[:-1]),
            report=refs[-1],
            blender_version=str(report.get("blender", "unknown")),
            duration_seconds=round(duration, 3),
        )

    # ------------------------------------------------------------ optimize_web

    async def _optimize_web(
        self, job_id: str, request: OptimizeWebJob, workdir: Path
    ) -> OptimizeWebResult:
        source = await self.artifacts.fetch(request.source_key, workdir / "source.glb")
        products = load_registry()["products"]
        if request.sku not in products:
            raise RenderFailure(f"sku {request.sku} vanished from the registry")
        match = classify_product(products[request.sku])
        preset = SHEEN_PRESETS[match.fabric_class]
        anisotropy = (
            AnisotropyParams(strength=request.anisotropy_strength)
            if request.anisotropy_strength is not None
            else None
        )
        if preset is None and anisotropy is not None:
            raise MaterialPatchError("anisotropy requested for a fabric class without sheen")
        data = source.read_bytes()
        patched = (
            data if preset is None else apply_fabric_extensions(data, preset, anisotropy=anisotropy)
        )
        staged = workdir / "patched.glb"
        staged.write_bytes(patched)
        packed = workdir / "web" / f"{request.sku}.glb"
        binary = self.config.gltfpack_bin or resolve_gltfpack()
        await asyncio.to_thread(
            pack_for_web, staged, packed, binary=binary, timeout=int(self.config.timeout_seconds)
        )
        gate = web_gate(packed, max_bytes=request.max_bytes, require_sheen=preset is not None)
        if not gate.passed:
            raise RenderFailure("web gate failed: " + "; ".join(gate.violations))
        key = f"{self.config.output_prefix}/{job_id}/web/{request.sku}.glb"
        (ref,) = await self._publish_all([(packed, key, "model/gltf-binary")])
        sheen = None
        if preset is not None:
            sheen = {"sheen_color": preset.color, "sheen_roughness": preset.roughness}
            if anisotropy is not None:
                sheen["anisotropy_strength"] = anisotropy.strength
        return OptimizeWebResult(
            fabric_class=match.fabric_class.value,
            matched_keyword=match.keyword,
            sheen=sheen,
            web_glb=ref,
            source_bytes=len(data),
            gltfpack_version=await asyncio.to_thread(gltfpack_version, binary),
        )


# ---------------------------------------------------------------------- CLI


async def _run_worker(log_level: str, poll_seconds: float) -> int:
    logging.basicConfig(level=log_level.upper(), format="%(asctime)s %(levelname)s %(message)s")
    worker = RenderWorker(poll_block_seconds=poll_seconds)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(worker.shutdown()))
    await worker.run()
    return 0


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="blender_render.worker")
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    args = parser.parse_args(argv)
    return asyncio.run(_run_worker(args.log_level, args.poll_seconds))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "MAX_INFRA_ATTEMPTS",
    "MIN_PIXEL_STDDEV",
    "RENDER_SCRIPT",
    "SHUTDOWN_ERROR",
    "BlenderRunner",
    "RenderFailure",
    "RenderWorker",
    "RunResult",
    "WorkerConfig",
    "build_blender_command",
    "check_still",
    "main",
    "stills_payload",
    "subprocess_runner",
]
