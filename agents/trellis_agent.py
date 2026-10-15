"""TRELLIS.2 subprocess wrapper for image-to-3D generation.

TRELLIS.2 (microsoft/TRELLIS.2-4B) runs in an isolated conda environment
because it pulls a CUDA-pinned PyTorch + `o_voxel` + `trellis2` stack that
conflicts with the main `.venv`. This wrapper shells out to the `trellis2`
conda env, executes a temp runner script that loads the pipeline and
exports a GLB, and returns a result dict shaped like
`MeshyGenerationResult` so the round-table can dispatch uniformly.

Pattern mirrors the Blender GLB cleanup at
`skyyrose/elite_studio/agents/three_d_agent.py:252` — write temp script,
run via `subprocess.run` inside `asyncio.to_thread`, fail gracefully
when the env is absent.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


DEFAULT_OUTPUT_DIR = Path(os.environ.get("TRELLIS_OUTPUT_DIR", "renders/3d"))
DEFAULT_CONDA_ENV = os.environ.get("TRELLIS_CONDA_ENV", "trellis2")
DEFAULT_MODEL_REPO = os.environ.get("TRELLIS_MODEL_REPO", "microsoft/TRELLIS.2-4B")
DEFAULT_TIMEOUT_SECONDS = int(os.environ.get("TRELLIS_TIMEOUT_SECONDS", "600"))
DEFAULT_DECIMATION_TARGET = int(os.environ.get("TRELLIS_DECIMATION_TARGET", "1000000"))
DEFAULT_TEXTURE_SIZE = int(os.environ.get("TRELLIS_TEXTURE_SIZE", "4096"))


@dataclass
class TrellisRunResult:
    """Result of a TRELLIS.2 subprocess run."""

    task_id: str
    status: str
    model_urls: dict[str, str] = field(default_factory=dict)
    thumbnail_url: str | None = None
    local_path: str | None = None
    format: str = "glb"
    metadata: dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0

    def model_dump(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "model_urls": dict(self.model_urls),
            "thumbnail_url": self.thumbnail_url,
            "local_path": self.local_path,
            "format": self.format,
            "metadata": dict(self.metadata),
            "duration_seconds": self.duration_seconds,
        }


class TrellisAgentError(RuntimeError):
    """Raised when the TRELLIS.2 environment is missing or the run fails."""


class TrellisTimeoutError(TrellisAgentError):
    """Raised when the TRELLIS.2 subprocess exceeds its time budget.

    Distinct from ``TrellisAgentError`` so callers (specifically the
    round-table circuit breaker) can treat timeouts as a "retry once
    cold" signal — TRELLIS first-runs are slow because pipeline weights
    load lazily, but subsequent runs are fast. A permanent crash should
    keep marking the provider unhealthy; a single cold timeout should
    not.
    """


class TrellisAgent:
    """Local TRELLIS.2 image-to-3D wrapper.

    Resolves the `trellis2` conda env at first use, writes a temp runner
    script per call, and returns a `MeshyGenerationResult`-shaped dict.
    """

    def __init__(
        self,
        conda_env: str = DEFAULT_CONDA_ENV,
        model_repo: str = DEFAULT_MODEL_REPO,
        output_dir: Path | str = DEFAULT_OUTPUT_DIR,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        decimation_target: int = DEFAULT_DECIMATION_TARGET,
        texture_size: int = DEFAULT_TEXTURE_SIZE,
        trellis_repo_path: Path | str | None = None,
    ) -> None:
        self.conda_env = conda_env
        self.model_repo = model_repo
        self.output_dir = Path(output_dir)
        self.timeout_seconds = timeout_seconds
        self.decimation_target = decimation_target
        self.texture_size = texture_size
        repo_default = Path(__file__).resolve().parent.parent / "TRELLIS.2"
        self.trellis_repo_path = Path(trellis_repo_path or repo_default)
        self._python_path: str | None = None
        self._availability_checked = False
        self._available = False

    def is_available(self) -> bool:
        """Return True if conda env + TRELLIS repo are reachable."""
        if self._availability_checked:
            return self._available
        self._availability_checked = True
        if not self.trellis_repo_path.is_dir():
            logger.info(
                "trellis_agent: repo path %s missing",
                self.trellis_repo_path,
            )
            self._available = False
            return False
        python_path = self._resolve_conda_python(self.conda_env)
        if not python_path:
            logger.info("trellis_agent: conda env %r not found", self.conda_env)
            self._available = False
            return False
        self._python_path = python_path
        self._available = True
        logger.info(
            "trellis_agent: ready (python=%s, repo=%s)",
            python_path,
            self.trellis_repo_path,
        )
        return True

    @staticmethod
    def _resolve_conda_python(env_name: str) -> str | None:
        """Find the python executable for a named conda env, or None."""
        override = os.environ.get("TRELLIS_PYTHON")
        if override and Path(override).is_file():
            return override

        conda_exe = os.environ.get("CONDA_EXE") or shutil.which("conda")
        if conda_exe:
            try:
                result = subprocess.run(
                    [conda_exe, "run", "-n", env_name, "which", "python"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                candidate = result.stdout.strip().splitlines()[-1] if result.stdout else ""
                if candidate and Path(candidate).is_file():
                    return candidate
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass

        # Fallback: scan common conda install roots.
        candidates = [
            Path.home() / "miniconda3" / "envs" / env_name / "bin" / "python",
            Path.home() / "anaconda3" / "envs" / env_name / "bin" / "python",
            Path.home() / "opt" / "miniconda3" / "envs" / env_name / "bin" / "python",
            Path.home() / "opt" / "anaconda3" / "envs" / env_name / "bin" / "python",
            Path("/opt/conda/envs") / env_name / "bin" / "python",
        ]
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
        return None

    async def image_to_3d(
        self,
        image_path: str,
        product_name: str = "product",
        output_format: str = "glb",
        decimation_target: int | None = None,
        texture_size: int | None = None,
    ) -> dict[str, Any]:
        """Run TRELLIS.2 image-to-3D and return a MeshyGenerationResult-shaped dict.

        Raises TrellisAgentError when the env is unavailable or the
        subprocess fails. Callers (the round-table) catch this and mark
        the provider as unhealthy.
        """
        if output_format.lower() != "glb":
            raise TrellisAgentError(f"TRELLIS.2 wrapper only emits GLB, got {output_format!r}")
        if not self.is_available():
            raise TrellisAgentError(
                f"TRELLIS.2 conda env {self.conda_env!r} or repo {self.trellis_repo_path} missing"
            )
        if not image_path:
            raise TrellisAgentError("image_path is required")

        resolved_input = self._resolve_input(image_path)
        if not resolved_input.is_file():
            raise TrellisAgentError(f"input image not found: {resolved_input}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        task_id = f"trellis-{uuid.uuid4().hex[:12]}"
        safe_name = self._safe_filename(product_name)
        output_glb = (self.output_dir / f"{safe_name}_{task_id}.glb").resolve()

        runner_path = self._write_runner_script(
            input_image=resolved_input,
            output_glb=output_glb,
            decimation_target=decimation_target or self.decimation_target,
            texture_size=texture_size or self.texture_size,
        )

        start = time.time()
        try:
            stdout, stderr, returncode = await asyncio.to_thread(
                self._run_subprocess, runner_path, output_glb
            )
        finally:
            try:
                runner_path.unlink(missing_ok=True)
            except OSError:
                pass

        duration = time.time() - start

        if returncode != 0 or not output_glb.is_file():
            tail = stderr[-2000:] if stderr else ""
            raise TrellisAgentError(f"trellis subprocess failed (rc={returncode}): {tail}")

        size_bytes = output_glb.stat().st_size
        result = TrellisRunResult(
            task_id=task_id,
            status="completed",
            model_urls={"glb": f"file://{output_glb}"},
            local_path=str(output_glb),
            format="glb",
            metadata={
                "provider": "trellis2",
                "model_repo": self.model_repo,
                "source_image": str(resolved_input),
                "size_bytes": size_bytes,
                "decimation_target": decimation_target or self.decimation_target,
                "texture_size": texture_size or self.texture_size,
                "stdout_tail": (stdout or "")[-500:],
            },
            duration_seconds=duration,
        )
        logger.info(
            "trellis_agent: %s → %s (%.1fs, %.1f MB)",
            safe_name,
            output_glb.name,
            duration,
            size_bytes / 1_048_576,
        )
        return result.model_dump()

    def _run_subprocess(self, runner_path: Path, output_glb: Path) -> tuple[str, str, int]:
        assert self._python_path, "is_available() must be called first"
        env = {**os.environ, "OPENCV_IO_ENABLE_OPENEXR": "1"}
        try:
            proc = subprocess.run(
                [self._python_path, str(runner_path)],
                cwd=str(self.trellis_repo_path),
                env=env,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            return proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
            raise TrellisTimeoutError(
                f"trellis subprocess timed out after {self.timeout_seconds}s: {stderr[-2000:]}"
            ) from exc
        except FileNotFoundError as exc:
            raise TrellisAgentError(
                f"trellis python not found at {self._python_path}: {exc}"
            ) from exc

    def _write_runner_script(
        self,
        input_image: Path,
        output_glb: Path,
        decimation_target: int,
        texture_size: int,
    ) -> Path:
        script = self._build_runner_script(
            input_image=input_image,
            output_glb=output_glb,
            model_repo=self.model_repo,
            decimation_target=decimation_target,
            texture_size=texture_size,
        )
        fd, tmp_name = tempfile.mkstemp(suffix=".py", prefix="trellis_run_")
        with os.fdopen(fd, "w") as fh:
            fh.write(script)
        return Path(tmp_name)

    @staticmethod
    def _build_runner_script(
        input_image: Path,
        output_glb: Path,
        model_repo: str,
        decimation_target: int,
        texture_size: int,
    ) -> str:
        # NOTE: emitted as a standalone script — runs inside the trellis2
        # conda env with CWD set to the TRELLIS.2 repo (so relative
        # imports like `from trellis2.pipelines import ...` resolve).
        return f"""import os
import sys
import traceback

os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

INPUT_IMAGE = {str(input_image)!r}
OUTPUT_GLB = {str(output_glb)!r}
MODEL_REPO = {model_repo!r}
DECIMATION_TARGET = {decimation_target}
TEXTURE_SIZE = {texture_size}

try:
    import o_voxel
    import torch
    from PIL import Image
    from trellis2.pipelines import Trellis2ImageTo3DPipeline

    pipeline = Trellis2ImageTo3DPipeline.from_pretrained(MODEL_REPO)  # nosec B615 — HF model ID constant; well-known public model from trusted org
    pipeline.cuda()

    image = Image.open(INPUT_IMAGE).convert("RGBA")
    mesh = pipeline.run(image)[0]
    mesh.simplify(16777216)  # nvdiffrast limit

    glb = o_voxel.postprocess.to_glb(
        vertices=mesh.vertices,
        faces=mesh.faces,
        attr_volume=mesh.attrs,
        coords=mesh.coords,
        attr_layout=mesh.layout,
        voxel_size=mesh.voxel_size,
        aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
        decimation_target=DECIMATION_TARGET,
        texture_size=TEXTURE_SIZE,
        remesh=True,
        remesh_band=1,
        remesh_project=0,
        verbose=False,
    )
    glb.export(OUTPUT_GLB, extension_webp=True)
    print(f"OK {{OUTPUT_GLB}}", flush=True)
except Exception:
    traceback.print_exc()
    sys.exit(2)
"""

    @staticmethod
    def _safe_filename(name: str) -> str:
        cleaned = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in name.lower())
        cleaned = cleaned.strip("-_") or "product"
        return cleaned[:48]

    @staticmethod
    def _resolve_input(image_path: str) -> Path:
        candidate = Path(image_path)
        if candidate.is_absolute():
            return candidate
        # Allow project-relative paths.
        project_root = Path(__file__).resolve().parent.parent
        return (project_root / candidate).resolve()


__all__ = [
    "TrellisAgent",
    "TrellisAgentError",
    "TrellisTimeoutError",
    "TrellisRunResult",
]
