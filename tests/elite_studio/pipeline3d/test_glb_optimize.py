"""gltfpack wrapper (fail-closed binary resolution) and the web delivery gate."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

from skyyrose.elite_studio.pipeline3d.glb_container import read_glb
from skyyrose.elite_studio.pipeline3d.glb_materials import SheenPreset, apply_fabric_extensions
from skyyrose.elite_studio.pipeline3d.glb_optimize import (
    GltfpackError,
    GltfpackNotFoundError,
    pack_for_web,
    resolve_gltfpack,
    web_gate,
)
from tests.elite_studio.pipeline3d.glb_fixture import (
    build_triangle_glb,
    pack_glb,
    web_ready_document,
)


def _fake_binary(tmp_path: Path, script: str) -> Path:
    path = tmp_path / "gltfpack"
    path.write_text("#!/bin/sh\n" + script + "\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def _write(tmp_path: Path, name: str, data: bytes) -> Path:
    path = tmp_path / name
    path.write_bytes(data)
    return path


# ── binary resolution ────────────────────────────────────────────────────────


def test_env_binary_wins(tmp_path, monkeypatch):
    binary = _fake_binary(tmp_path, "exit 0")
    monkeypatch.setenv("GLTFPACK_BIN", str(binary))
    assert resolve_gltfpack() == binary


def test_env_binary_missing_fails_closed_without_path_fallback(tmp_path, monkeypatch):
    monkeypatch.setenv("GLTFPACK_BIN", str(tmp_path / "nope"))
    monkeypatch.setattr(shutil, "which", lambda _name: "/usr/bin/true")
    with pytest.raises(GltfpackNotFoundError):
        resolve_gltfpack()


def test_env_binary_not_executable_fails_closed(tmp_path, monkeypatch):
    plain = tmp_path / "gltfpack"
    plain.write_text("not executable")
    monkeypatch.setenv("GLTFPACK_BIN", str(plain))
    with pytest.raises(GltfpackNotFoundError):
        resolve_gltfpack()


def test_absent_everywhere_fails_closed(monkeypatch):
    monkeypatch.delenv("GLTFPACK_BIN", raising=False)
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    with pytest.raises(GltfpackNotFoundError):
        resolve_gltfpack()


def test_path_lookup_used_when_env_unset(tmp_path, monkeypatch):
    binary = _fake_binary(tmp_path, "exit 0")
    monkeypatch.delenv("GLTFPACK_BIN", raising=False)
    monkeypatch.setattr(shutil, "which", lambda _name: str(binary))
    assert resolve_gltfpack() == binary


# ── packing ──────────────────────────────────────────────────────────────────


def test_pack_passes_web_flags_as_argument_list(tmp_path):
    log = tmp_path / "args.txt"
    binary = _fake_binary(tmp_path, f'echo "$@" > "{log}"\ncp "$2" "$4"')
    src = _write(tmp_path, "in.glb", build_triangle_glb())
    dst = tmp_path / "out" / "out.glb"
    assert pack_for_web(src, dst, binary=binary) == dst
    assert log.read_text().split() == ["-i", str(src), "-o", str(dst), "-cc", "-tc"]
    assert dst.read_bytes() == src.read_bytes()


def test_pack_nonzero_exit_raises_with_stderr_tail(tmp_path):
    binary = _fake_binary(tmp_path, 'echo "Error: bad texture" >&2\nexit 3')
    src = _write(tmp_path, "in.glb", build_triangle_glb())
    with pytest.raises(GltfpackError, match="bad texture"):
        pack_for_web(src, tmp_path / "out.glb", binary=binary)


def test_pack_zero_exit_without_output_fails_closed(tmp_path):
    binary = _fake_binary(tmp_path, "exit 0")
    src = _write(tmp_path, "in.glb", build_triangle_glb())
    with pytest.raises(GltfpackError, match="no output"):
        pack_for_web(src, tmp_path / "out.glb", binary=binary)


def test_pack_missing_source_fails_before_running(tmp_path):
    binary = _fake_binary(tmp_path, "exit 0")
    with pytest.raises(FileNotFoundError):
        pack_for_web(tmp_path / "missing.glb", tmp_path / "out.glb", binary=binary)


# ── gate ─────────────────────────────────────────────────────────────────────


def test_gate_passes_web_ready_asset(tmp_path):
    path = _write(tmp_path, "ok.glb", pack_glb(web_ready_document(), b"\x00" * 4))
    result = web_gate(path)
    assert result.passed, result.violations
    assert result.size_bytes == path.stat().st_size


def test_gate_flags_size_budget(tmp_path):
    path = _write(tmp_path, "big.glb", pack_glb(web_ready_document(), b"\x00" * 4))
    result = web_gate(path, max_bytes=10)
    assert not result.passed
    assert any("budget" in v for v in result.violations)


@pytest.mark.parametrize("missing", ["EXT_meshopt_compression", "KHR_texture_basisu"])
def test_gate_flags_missing_compression_extension(tmp_path, missing):
    doc = web_ready_document()
    doc = {**doc, "extensionsUsed": [e for e in doc["extensionsUsed"] if e != missing]}
    result = web_gate(_write(tmp_path, "x.glb", pack_glb(doc, b"\x00" * 4)))
    assert any(missing in v for v in result.violations)


def test_gate_flags_material_without_sheen(tmp_path):
    path = _write(tmp_path, "x.glb", pack_glb(web_ready_document(sheen=False), b"\x00" * 4))
    assert any("KHR_materials_sheen" in v for v in web_gate(path).violations)
    assert web_gate(path, require_sheen=False).passed


def test_gate_flags_non_ktx2_image(tmp_path):
    path = _write(tmp_path, "x.glb", pack_glb(web_ready_document(mime="image/jpeg"), b"\x00" * 4))
    assert any("image/jpeg" in v for v in web_gate(path).violations)


def test_gate_requires_sheen_on_glb_without_materials(tmp_path):
    doc = {k: v for k, v in web_ready_document().items() if k != "materials"}
    result = web_gate(_write(tmp_path, "x.glb", pack_glb(doc, b"\x00" * 4)))
    assert any("no materials" in v for v in result.violations)


def test_gate_fails_closed_on_unreadable_file(tmp_path):
    path = _write(tmp_path, "junk.glb", b"not a glb at all")
    result = web_gate(path)
    assert not result.passed
    assert any("unreadable" in v for v in result.violations)


def test_gate_fails_closed_on_missing_file(tmp_path):
    result = web_gate(tmp_path / "absent.glb")
    assert not result.passed


# ── real gltfpack (integration) ──────────────────────────────────────────────


def _real_gltfpack() -> Path | None:
    env = os.environ.get("GLTFPACK_BIN")
    if env and Path(env).is_file():
        return Path(env)
    found = shutil.which("gltfpack")
    return Path(found) if found else None


def test_real_gltfpack_preserves_sheen_through_meshopt(tmp_path):
    binary = _real_gltfpack()
    if binary is None:
        pytest.skip("gltfpack binary not available (set GLTFPACK_BIN)")
    patched = apply_fabric_extensions(build_triangle_glb(), SheenPreset(0.35, 0.9))
    src = _write(tmp_path, "tri.glb", patched)
    out = pack_for_web(src, tmp_path / "tri.web.glb", binary=binary)
    document = read_glb(out.read_bytes()).document
    assert "EXT_meshopt_compression" in document["extensionsUsed"]
    # gltfpack re-serialises factors as float32, so compare at float32 precision.
    sheen = document["materials"][0]["extensions"]["KHR_materials_sheen"]
    assert sheen["sheenColorFactor"] == pytest.approx([0.35, 0.35, 0.35], abs=1e-6)
    assert sheen["sheenRoughnessFactor"] == pytest.approx(0.9, abs=1e-6)
    # One triangle has no textures, so basisu is legitimately absent → gate names only that.
    assert web_gate(out).violations == ("missing extension KHR_texture_basisu",)


@pytest.mark.parametrize(
    ("sheen", "fragment"),
    [
        (None, "lacks KHR_materials_sheen"),
        (7, "expected an object"),
        ({}, "sheenColorFactor is not three factors"),
        ({"sheenColorFactor": [0.2, 0.2]}, "sheenColorFactor is not three factors"),
        ({"sheenColorFactor": [0.2, 0.2, 4.0]}, "sheenColorFactor is not three factors"),
        ({"sheenColorFactor": [0.2, 0.2, 0.2]}, "sheenRoughnessFactor is not a factor"),
    ],
)
def test_gate_rejects_sheen_that_would_not_render(tmp_path, sheen, fragment):
    document = web_ready_document(sheen=False)
    if sheen is not None:
        document["materials"][0]["extensions"] = {"KHR_materials_sheen": sheen}
    path = tmp_path / "declared.glb"
    path.write_bytes(pack_glb(document, b"\x00" * 4))
    gate = web_gate(path)
    assert not gate.passed
    assert any(fragment in violation for violation in gate.violations), gate.violations


@pytest.mark.parametrize(
    ("kwargs", "fragment"),
    [
        ({"required": False}, "not in extensionsRequired"),
        ({"compressed_view": False}, "geometry is uncompressed"),
    ],
)
def test_gate_rejects_compression_that_is_only_declared(tmp_path, kwargs, fragment):
    path = tmp_path / "declared.glb"
    path.write_bytes(pack_glb(web_ready_document(**kwargs), b"\x00" * 4))
    gate = web_gate(path)
    assert not gate.passed
    assert any(fragment in violation for violation in gate.violations), gate.violations


def test_pack_for_web_times_out_without_publishing(tmp_path, monkeypatch):
    binary = tmp_path / "slow-gltfpack"
    binary.write_text("#!/bin/sh\nsleep 5\n")
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
    src = tmp_path / "src.glb"
    src.write_bytes(build_triangle_glb())
    dst = tmp_path / "out.glb"
    with pytest.raises(subprocess.TimeoutExpired):
        pack_for_web(src, dst, binary=binary, timeout=1)
    assert not dst.exists()
