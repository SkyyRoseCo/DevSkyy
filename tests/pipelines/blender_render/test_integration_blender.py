"""Real-Blender integration: render 2 turntable stills of a generated GLB at 256px.

Run explicitly (deselected by default via ``-m "not integration"``)::

    .venv/bin/python -m pytest tests/pipelines/blender_render/test_integration_blender.py -m integration
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from PIL import Image, ImageStat

from pipelines.blender_render.artifacts import LocalKeyedStore
from pipelines.blender_render.models import JobStatus, RenderJobRecord, RenderStillsJob
from pipelines.blender_render.store import InMemoryJobStore, InMemoryQueue
from pipelines.blender_render.worker import MIN_PIXEL_STDDEV, RenderWorker, WorkerConfig
from tests.pipelines.blender_render.glb_fixture import write_box_glb

BLENDER_CANDIDATES = (
    os.getenv("BLENDER_BIN"),
    "/opt/homebrew/bin/blender",
    shutil.which("blender"),
)
BLENDER = next((path for path in BLENDER_CANDIDATES if path and Path(path).is_file()), None)

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


@pytest.mark.skipif(
    BLENDER is None,
    reason="Blender binary not found (BLENDER_BIN / /opt/homebrew/bin/blender / PATH)",
)
async def test_real_blender_renders_two_stills(tmp_path: Path) -> None:
    artifacts = LocalKeyedStore(tmp_path / "store")
    write_box_glb(tmp_path / "store" / "src/br-006.glb")
    queue, store = InMemoryQueue(), InMemoryJobStore()
    worker = RenderWorker(
        queue=queue,
        store=store,
        artifacts=artifacts,
        config=WorkerConfig(
            blender_bin=str(BLENDER), timeout_seconds=240.0, output_prefix="render-jobs"
        ),
    )
    job = RenderStillsJob(
        job_type="render_stills",
        sku="br-006",
        source_key="src/br-006.glb",
        count=2,
        resolution=256,
        samples=4,
    )
    await store.put(RenderJobRecord(job_id="rj_real", request=job))
    await queue.enqueue("rj_real")
    msg = await queue.dequeue(block_seconds=1.0)
    final = await worker.process_one(msg)

    assert final is not None and final.status is JobStatus.SUCCEEDED, final.error
    assert final.result is not None and len(final.result.stills) == 2
    assert final.result.blender_version.startswith("5.")
    for ref in final.result.stills:
        with Image.open(tmp_path / "store" / ref.key) as image:
            rgba = image.convert("RGBA")
        assert rgba.size == (256, 256)
        assert max(ImageStat.Stat(rgba).stddev) >= MIN_PIXEL_STDDEV
        assert rgba.getchannel("A").getextrema() == (0, 255)  # transparent film + opaque garment
