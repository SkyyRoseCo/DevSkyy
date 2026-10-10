"""Web delivery for garment GLBs: gltfpack compression + a fail-closed delivery gate.

gltfpack (meshoptimizer) emits ``EXT_meshopt_compression`` geometry and, with ``-tc``,
KTX2/BasisU textures (``KHR_texture_basisu``). It does not produce Draco — meshopt is the
codec here, and gltfpack 1.2 preserves ``KHR_materials_sheen``/``anisotropy`` through
``-cc -tc`` (verified 2026-09-17 on renders/3d/br-006.glb). Viewers must register a
MeshoptDecoder and a KTX2 transcoder.

Binary resolution fails closed: ``GLTFPACK_BIN`` (if set, it must exist and be executable —
no silent fall-through to PATH), else ``gltfpack`` on PATH, else ``GltfpackNotFoundError``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .glb_container import GlbFormatError, read_glb

WEB_BUDGET_BYTES = 3_000_000
_MESHOPT = "EXT_meshopt_compression"
REQUIRED_WEB_EXTENSIONS = (_MESHOPT, "KHR_texture_basisu")
WEB_PACK_FLAGS = ("-cc", "-tc")
_KTX2_MIME = "image/ktx2"
_STDERR_TAIL = 800


class GltfpackNotFoundError(RuntimeError):
    """No usable gltfpack executable could be resolved."""


class GltfpackError(RuntimeError):
    """gltfpack ran but did not produce a valid output."""


@dataclass(frozen=True)
class GateResult:
    path: Path
    size_bytes: int | None
    violations: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.violations


def _executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def resolve_gltfpack() -> Path:
    """Locate gltfpack; never guess, never fall back past an explicit but broken override."""
    override = os.environ.get("GLTFPACK_BIN")
    if override:
        candidate = Path(override)
        if not _executable(candidate):
            raise GltfpackNotFoundError(f"GLTFPACK_BIN={override} is not an executable file")
        return candidate
    found = shutil.which("gltfpack")
    if not found:
        raise GltfpackNotFoundError(
            "gltfpack not found: set GLTFPACK_BIN or install it "
            "(https://github.com/zeux/meshoptimizer/releases)"
        )
    return Path(found)


def gltfpack_version(binary: Path) -> str:
    """First line of ``gltfpack -v`` (recorded in build reports for reproducibility)."""
    result = subprocess.run(
        [str(binary), "-v"], capture_output=True, text=True, timeout=30, check=False
    )
    lines = (result.stdout or result.stderr).strip().splitlines()
    return lines[0] if lines else "unknown"


def pack_for_web(src: Path, dst: Path, *, binary: Path | None = None, timeout: int = 900) -> Path:
    """Compress ``src`` into ``dst`` with meshopt geometry + KTX2 textures."""
    if not src.is_file():
        raise FileNotFoundError(f"source GLB not found: {src}")
    executable = binary or resolve_gltfpack()
    dst.parent.mkdir(parents=True, exist_ok=True)
    command = [str(executable), "-i", str(src), "-o", str(dst), *WEB_PACK_FLAGS]
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    if result.returncode != 0:
        tail = (result.stderr or result.stdout).strip()[-_STDERR_TAIL:]
        raise GltfpackError(f"gltfpack exited {result.returncode}: {tail}")
    if not dst.is_file() or dst.stat().st_size == 0:
        raise GltfpackError(f"gltfpack reported success but wrote no output at {dst}")
    return dst


def _unit_factor(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and 0.0 <= value <= 1.0


def _sheen_violation(index: int, material: dict[str, Any]) -> str | None:
    """A declared-but-empty sheen renders as no sheen, so the values are checked, not the key."""
    sheen = (material.get("extensions") or {}).get("KHR_materials_sheen")
    if sheen is None:
        return f"material {index} lacks KHR_materials_sheen"
    if not isinstance(sheen, dict):
        return f"material {index} KHR_materials_sheen is {type(sheen).__name__}, expected an object"
    colour = sheen.get("sheenColorFactor")
    if not (isinstance(colour, list) and len(colour) == 3 and all(map(_unit_factor, colour))):
        return f"material {index} sheenColorFactor is not three factors in [0,1]: {colour!r}"
    if not _unit_factor(sheen.get("sheenRoughnessFactor")):
        return (
            f"material {index} sheenRoughnessFactor is not a factor in [0,1]: "
            f"{sheen.get('sheenRoughnessFactor')!r}"
        )
    return None


def _material_violations(document: dict[str, Any]) -> list[str]:
    materials = document.get("materials")
    if not isinstance(materials, list) or not materials:
        return ["no materials (KHR_materials_sheen required)"]
    if not all(isinstance(material, dict) for material in materials):
        return ["materials array contains a non-object entry"]
    found = (_sheen_violation(index, material) for index, material in enumerate(materials))
    return [violation for violation in found if violation]


def _compression_violations(document: dict[str, Any]) -> list[str]:
    """Declaring meshopt is not using it — a legacy file can name the extension and ship raw."""
    required = set(document.get("extensionsRequired") or [])
    if _MESHOPT not in required:
        return [f"{_MESHOPT} is not in extensionsRequired (a viewer would ignore the payload)"]
    views = document.get("bufferViews") or []
    if not isinstance(views, list):
        return [f"bufferViews is {type(views).__name__}, expected a list"]
    compressed = sum(
        1 for view in views if isinstance(view, dict) and _MESHOPT in (view.get("extensions") or {})
    )
    if not compressed:
        return [f"no bufferView carries {_MESHOPT}; geometry is uncompressed"]
    return []


def _document_violations(document: dict[str, Any], *, require_sheen: bool) -> list[str]:
    used = set(document.get("extensionsUsed") or [])
    violations = [
        f"missing extension {name}" for name in REQUIRED_WEB_EXTENSIONS if name not in used
    ]
    violations.extend(_compression_violations(document))
    if require_sheen:
        violations.extend(_material_violations(document))
    violations.extend(
        f"image {index} is {image.get('mimeType')}, expected {_KTX2_MIME}"
        for index, image in enumerate(document.get("images") or [])
        if image.get("mimeType") != _KTX2_MIME
    )
    return violations


def web_gate(
    path: Path, *, max_bytes: int = WEB_BUDGET_BYTES, require_sheen: bool = True
) -> GateResult:
    """Check a GLB is fit for the CDN. Unreadable input is a failure, never a pass."""
    try:
        data = path.read_bytes()
        document = read_glb(data).document
    except (OSError, GlbFormatError) as exc:
        return GateResult(path=path, size_bytes=None, violations=(f"unreadable: {exc}",))
    violations = []
    if len(data) > max_bytes:
        violations.append(f"size {len(data)} bytes exceeds budget {max_bytes}")
    violations.extend(_document_violations(document, require_sheen=require_sheen))
    return GateResult(path=path, size_bytes=len(data), violations=tuple(violations))
