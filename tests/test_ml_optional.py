"""Proves main_enterprise imports without torch-class ML deps (pyproject `ml` extra).

A subprocess is required: the pytest process runs in the shared .venv which HAS
ml installed, so sys.modules already caches transformers/torch/etc — a meta-path
blocker in-process would be defeated by that cache. A fresh interpreter starts
with an empty sys.modules, so the blocker is authoritative there.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Each test below is one clean-interpreter subprocess import, and the subprocess
# budget is its real limit. The suite-wide pytest-timeout (pyproject: 10s) is
# sized for unit tests and silently preempted that budget whenever the machine
# was busy (bug-368). The per-test marker sits above the subprocess budget, so
# subprocess.run raises its own TimeoutExpired first, with the captured output.
_SUBPROCESS_TIMEOUT_S = 60
_TEST_TIMEOUT_S = _SUBPROCESS_TIMEOUT_S + 30

_BLOCKER_SCRIPT = """
import sys
import importlib.abc

BLOCKED = {
    "transformers", "sentence_transformers", "chromadb", "diffusers",
    "torch", "torchvision", "torchaudio",
}


class _MLBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in BLOCKED:
            raise ModuleNotFoundError(f"blocked by test: {fullname}")
        return None


sys.meta_path.insert(0, _MLBlocker())
import main_enterprise  # noqa: F401
print("ML_OPTIONAL_IMPORT_OK")
"""

_FAIL_LOUD_SCRIPT = """
import sys
import importlib.abc

BLOCKED = {
    "transformers", "sentence_transformers", "chromadb", "diffusers",
    "torch", "torchvision", "torchaudio",
}


class _MLBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in BLOCKED:
            raise ModuleNotFoundError(f"blocked by test: {fullname}")
        return None


sys.meta_path.insert(0, _MLBlocker())

from PIL import Image

from skyyrose.core.embeddings.clip import ClipEncoder
from skyyrose.core.embeddings.config import EmbeddingConfig
from skyyrose.core.embeddings.dino import DinoEncoder

img = Image.new("RGB", (4, 4), (1, 2, 3))

for label, fn in (
    ("clip.embed_text", lambda: ClipEncoder(EmbeddingConfig()).embed_text("hello")),
    ("clip.embed_image", lambda: ClipEncoder(EmbeddingConfig()).embed_image(img)),
    ("dino.embed_image", lambda: DinoEncoder(EmbeddingConfig()).embed_image(img)),
):
    try:
        fn()
        print(f"FAIL:{label}:did-not-raise")
    except ImportError as exc:
        if "'.[ml]'" in str(exc) or ".[ml]" in str(exc):
            print(f"OK:{label}")
        else:
            print(f"FAIL:{label}:wrong-message:{exc}")
    except Exception as exc:  # noqa: BLE001 - deliberately broad, this IS the assertion
        print(f"FAIL:{label}:wrong-exception-type:{type(exc).__name__}:{exc}")
"""


@pytest.mark.timeout(_TEST_TIMEOUT_S)
def test_main_enterprise_imports_without_ml_libs() -> None:
    """`import main_enterprise` must succeed with zero torch-class ML libs importable."""
    result = subprocess.run(
        [sys.executable, "-c", _BLOCKER_SCRIPT],
        # PYTHONPATH instead of cwd: cwd= forces subprocess onto the fork()
        # path on macOS, where fork after Network.framework arming SIGSEGVs
        # the child (bug-263); posix_spawn requires cwd=None.
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        timeout=_SUBPROCESS_TIMEOUT_S,
    )
    assert result.returncode == 0 and "ML_OPTIONAL_IMPORT_OK" in result.stdout, (
        "import main_enterprise failed without ML libs installed "
        "(transformers/sentence_transformers/chromadb/diffusers/torch/torchvision/torchaudio blocked).\n"
        f"returncode={result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


@pytest.mark.timeout(_TEST_TIMEOUT_S)
def test_encoders_fail_loud_with_ml_extra_message() -> None:
    """Calling embed_text/embed_image without the `ml` extra must raise ImportError
    naming `pip install -e '.[ml]'` — never a bare ModuleNotFoundError from a
    lazy `import torch`/`transformers` reaching the caller unguarded (no-silent-
    fallback: graceful at import time, fail-loud with an actionable message at
    use time)."""
    result = subprocess.run(
        [sys.executable, "-c", _FAIL_LOUD_SCRIPT],
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        timeout=_SUBPROCESS_TIMEOUT_S,
    )
    lines = [ln for ln in result.stdout.splitlines() if ln.startswith(("OK:", "FAIL:"))]
    failures = [ln for ln in lines if ln.startswith("FAIL:")]
    assert result.returncode == 0 and len(lines) == 3 and not failures, (
        "encoder fail-loud contract broken (expected 3 OK: lines, one per "
        "clip.embed_text / clip.embed_image / dino.embed_image).\n"
        f"returncode={result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
