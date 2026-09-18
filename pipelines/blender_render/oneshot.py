"""Run ONE render job in-process and exit — no Redis, no API, no long-lived worker.

Used for local/Docker end-to-end checks and for ad-hoc renders::

    RENDER_ARTIFACT_DIR=/path/to/store python -m pipelines.blender_render.oneshot \
        --job-type render_stills --sku br-006 --source-key sources/br-006.glb \
        --count 4 --resolution 768

    RENDER_ARTIFACT_DIR=/path/to/store GLTFPACK_BIN=/path/to/gltfpack \
        python -m pipelines.blender_render.oneshot \
        --job-type optimize_web --sku br-006 --source-key sources/br-006.glb

The artifact store, Blender and gltfpack come from the same env the worker reads
(``RENDER_ARTIFACT_STORE``/``RENDER_ARTIFACT_DIR``/``BLENDER_BIN``/``GLTFPACK_BIN``). The final
job record is printed as JSON; exit status is 0 only when the job SUCCEEDED.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Any

from pipelines.blender_render.artifacts import build_artifact_store
from pipelines.blender_render.models import JobStatus, RenderJobRecord, request_adapter
from pipelines.blender_render.store import InMemoryJobStore, InMemoryQueue
from pipelines.blender_render.worker import RenderWorker


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="blender_render.oneshot", description=__doc__.split("\n")[0]
    )
    parser.add_argument("--job-type", required=True, choices=["render_stills", "optimize_web"])
    parser.add_argument("--sku", required=True)
    parser.add_argument("--source-key", required=True)
    parser.add_argument("--count", type=int)
    parser.add_argument("--resolution", type=int)
    parser.add_argument("--samples", type=int)
    parser.add_argument("--camera", choices=["perspective", "orthographic"])
    parser.add_argument("--margin", type=float)
    parser.add_argument("--anisotropy-strength", type=float)
    parser.add_argument("--max-bytes", type=int)
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def request_payload(args: argparse.Namespace) -> dict[str, Any]:
    """Only pass explicitly supplied knobs so the model defaults stay authoritative."""
    optional = {
        "count": args.count,
        "resolution": args.resolution,
        "samples": args.samples,
        "camera": args.camera,
        "margin": args.margin,
        "anisotropy_strength": args.anisotropy_strength,
        "max_bytes": args.max_bytes,
    }
    payload: dict[str, Any] = {
        "job_type": args.job_type,
        "sku": args.sku,
        "source_key": args.source_key,
    }
    return {**payload, **{key: value for key, value in optional.items() if value is not None}}


async def run_once(payload: dict[str, Any]) -> RenderJobRecord:
    request = request_adapter.validate_python(payload)
    queue, store = InMemoryQueue(), InMemoryJobStore()
    worker = RenderWorker(queue=queue, store=store, artifacts=build_artifact_store())
    record = RenderJobRecord(job_id=f"rj_{uuid.uuid4().hex[:16]}", request=request)
    await store.put(record)
    await queue.enqueue(record.job_id)
    message = await queue.dequeue(block_seconds=1.0)
    if message is None:
        raise RuntimeError("in-memory queue returned nothing for the job just enqueued")
    final = await worker.process_one(message)
    if final is None:
        raise RuntimeError("job record vanished from the in-memory store")
    return final


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(message)s"
    )
    final = asyncio.run(run_once(request_payload(args)))
    print(json.dumps(final.to_dict(), indent=2))
    return 0 if final.status is JobStatus.SUCCEEDED else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())


__all__ = ["main", "request_payload", "run_once"]
