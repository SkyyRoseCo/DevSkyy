"""scripts/build_web_glbs.py — batch patch → gltfpack → gate, fail-closed at every step."""

from __future__ import annotations

import json
import stat
from pathlib import Path

import build_web_glbs as cli
import pytest

from skyyrose.elite_studio.pipeline3d.glb_container import read_glb
from tests.elite_studio.pipeline3d.glb_fixture import (
    build_triangle_glb,
    pack_glb,
)
from tests.elite_studio.pipeline3d.glb_fixture import triangle_document as build_triangle_document
from tests.elite_studio.pipeline3d.glb_fixture import (
    web_ready_document,
)

SATIN = "**lustrous black satin** exterior fabric. NOT a fleece hoodie."
LEATHER = "black PU/faux-leather fanny pack with nylon webbing strap. NOT a leather handbag."


def _registry(tmp_path: Path, specs: dict[str, str]) -> Path:
    products = {
        sku: {
            "catalog": {"sku": sku, "name": f"Product {sku}"},
            "garment": {"materials": {"specification": spec}},
        }
        for sku, spec in specs.items()
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"products": products}))
    return path


def _fake_gltfpack(tmp_path: Path, monkeypatch, *, output: bytes | None) -> Path:
    """Fake binary: records the patched input it received, emits `output` (or fails)."""
    seen = tmp_path / "seen"
    seen.mkdir()
    ready = tmp_path / "ready.glb"
    body = f'cp "$2" "{seen}/$(basename "$2")"\n'
    if output is None:
        body += 'echo "Error: simulated failure" >&2\nexit 1'
    else:
        ready.write_bytes(output)
        body += f'cp "{ready}" "$4"'
    binary = tmp_path / "gltfpack"
    binary.write_text("#!/bin/sh\n" + body + "\n")
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("GLTFPACK_BIN", str(binary))
    return seen


def _sources(tmp_path: Path, skus: list[str]) -> Path:
    src = tmp_path / "src"
    src.mkdir()
    for sku in skus:
        (src / f"{sku}.glb").write_bytes(build_triangle_glb())
    return src


def _run(tmp_path: Path, registry: Path, src: Path, *extra: str) -> tuple[int, dict]:
    out = tmp_path / "web-v2"
    argv = ["--registry", str(registry), "--src-dir", str(src), "--out-dir", str(out), *extra]
    code = cli.main(argv)
    report_path = out / "build_report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    return code, report


def test_refuses_legacy_web_dir_as_output(tmp_path, capsys):
    registry = _registry(tmp_path, {"br-006": SATIN})
    forbidden = cli.PROJECT_ROOT / "renders" / "3d" / "web"
    code = cli.main(["--registry", str(registry), "--out-dir", str(forbidden)])
    assert code == 2
    assert "refusing" in capsys.readouterr().err


def test_refuses_output_equal_to_source_dir(tmp_path):
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    code = cli.main(["--registry", str(registry), "--src-dir", str(src), "--out-dir", str(src)])
    assert code == 2
    assert read_glb((src / "br-006.glb").read_bytes()).document.get("extensionsUsed") is None


def test_happy_path_publishes_gated_output_and_report(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    seen = _fake_gltfpack(tmp_path, monkeypatch, output=pack_glb(web_ready_document(), b"\0" * 4))
    code, report = _run(tmp_path, registry, src)
    assert code == 0
    entry = report["entries"][0]
    assert entry["sku"] == "br-006"
    assert (entry["fabric_class"], entry["matched_keyword"]) == ("satin", "satin")
    assert entry["preset"] == {"sheen_color": 0.15, "sheen_roughness": 0.3, "anisotropy": None}
    assert entry["gate_pass"] is True and entry["violations"] == []
    assert entry["out_bytes"] == (tmp_path / "web-v2" / "br-006.glb").stat().st_size
    patched = read_glb((seen / "br-006.glb").read_bytes()).document
    assert "KHR_materials_sheen" in patched["materials"][0]["extensions"]


def test_gate_failure_is_not_published(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    _fake_gltfpack(tmp_path, monkeypatch, output=build_triangle_glb())
    code, report = _run(tmp_path, registry, src)
    assert code == 1
    assert report["entries"][0]["gate_pass"] is False
    assert not (tmp_path / "web-v2" / "br-006.glb").exists()


def test_missing_source_recorded_not_skipped(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-006": SATIN, "sg-011": "White 100% cotton."})
    src = _sources(tmp_path, ["br-006"])
    _fake_gltfpack(tmp_path, monkeypatch, output=pack_glb(web_ready_document(), b"\0" * 4))
    code, report = _run(tmp_path, registry, src)
    assert code == 1
    statuses = {e["sku"]: e["status"] for e in report["entries"]}
    assert statuses == {"br-006": "ok", "sg-011": "missing_source"}


def test_unclassified_fabric_fails_closed(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-003": "Solid BLACK base fabric."})
    src = _sources(tmp_path, ["br-003"])
    _fake_gltfpack(tmp_path, monkeypatch, output=pack_glb(web_ready_document(), b"\0" * 4))
    code, report = _run(tmp_path, registry, src)
    assert code == 1
    assert report["entries"][0]["status"] == "unclassified"


def test_pack_failure_recorded(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    _fake_gltfpack(tmp_path, monkeypatch, output=None)
    code, report = _run(tmp_path, registry, src)
    assert code == 1
    entry = report["entries"][0]
    assert entry["status"] == "pack_failed"
    assert "simulated failure" in entry["violations"][0]


def test_faux_leather_skips_sheen_and_gate_requirement(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"lh-005": LEATHER})
    src = _sources(tmp_path, ["lh-005"])
    ready = pack_glb(web_ready_document(sheen=False), b"\0" * 4)
    seen = _fake_gltfpack(tmp_path, monkeypatch, output=ready)
    code, report = _run(tmp_path, registry, src)
    assert code == 0
    assert report["entries"][0]["preset"] is None
    assert "extensionsUsed" not in read_glb((seen / "lh-005.glb").read_bytes()).document


def test_anisotropy_is_opt_in_per_sku(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    seen = _fake_gltfpack(tmp_path, monkeypatch, output=pack_glb(web_ready_document(), b"\0" * 4))
    code, report = _run(tmp_path, registry, src, "--anisotropy-sku", "br-006=0.4")
    assert code == 0
    assert report["entries"][0]["preset"]["anisotropy"] == 0.4
    material = read_glb((seen / "br-006.glb").read_bytes()).document["materials"][0]
    assert material["extensions"]["KHR_materials_anisotropy"]["anisotropyStrength"] == 0.4


@pytest.mark.parametrize("bad", ["br-006", "br-006=high", "br-006=2.0", "zz-999=0.4"])
def test_invalid_anisotropy_argument_rejected(tmp_path, monkeypatch, bad):
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    _fake_gltfpack(tmp_path, monkeypatch, output=pack_glb(web_ready_document(), b"\0" * 4))
    code, _ = _run(tmp_path, registry, src, "--anisotropy-sku", bad)
    assert code == 2


def test_unknown_sku_rejected(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    _fake_gltfpack(tmp_path, monkeypatch, output=pack_glb(web_ready_document(), b"\0" * 4))
    code, _ = _run(tmp_path, registry, src, "--sku", "zz-999")
    assert code == 2


def test_missing_gltfpack_fails_closed_before_any_output(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    monkeypatch.setenv("GLTFPACK_BIN", str(tmp_path / "absent"))
    code, _ = _run(tmp_path, registry, src)
    assert code == 2
    assert not (tmp_path / "web-v2").exists()


def _prepacked(tmp_path: Path, sku: str, payload: bytes) -> Path:
    prepacked = tmp_path / "legacy-web"
    prepacked.mkdir(exist_ok=True)
    (prepacked / f"{sku}.glb").write_bytes(payload)
    return prepacked


def test_prepacked_fallback_patches_json_without_repacking(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-001": SATIN})
    src = _sources(tmp_path, [])
    packed_input = pack_glb(web_ready_document(sheen=False), b"\x00" * 4)
    prepacked = _prepacked(tmp_path, "br-001", packed_input)
    seen = _fake_gltfpack(tmp_path, monkeypatch, output=None)

    code, report = _run(tmp_path, registry, src, "--prepacked-dir", str(prepacked))

    entry = report["entries"][0]
    assert code == 0
    assert entry["status"] == "ok" and entry["source_kind"] == "prepacked"
    assert list(seen.iterdir()) == []  # gltfpack never ran on an already-packed file
    published = read_glb((tmp_path / "web-v2" / "br-001.glb").read_bytes())
    assert "KHR_materials_sheen" in published.document["materials"][0]["extensions"]
    assert published.tail == read_glb(packed_input).tail
    assert (prepacked / "br-001.glb").read_bytes() == packed_input  # legacy copy untouched


def test_missing_source_without_prepacked_flag_still_fails(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-001": SATIN})
    src = _sources(tmp_path, [])
    _prepacked(tmp_path, "br-001", pack_glb(web_ready_document(sheen=False), b"\x00" * 4))
    _fake_gltfpack(tmp_path, monkeypatch, output=None)

    code, report = _run(tmp_path, registry, src)

    assert code == 1
    assert report["entries"][0]["status"] == "missing_source"


def test_prepacked_file_that_is_not_web_ready_fails_gate(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-001": SATIN})
    src = _sources(tmp_path, [])
    prepacked = _prepacked(tmp_path, "br-001", build_triangle_glb())
    _fake_gltfpack(tmp_path, monkeypatch, output=None)

    code, report = _run(tmp_path, registry, src, "--prepacked-dir", str(prepacked))

    entry = report["entries"][0]
    assert code == 1
    assert entry["status"] == "gate_failed" and entry["source_kind"] == "prepacked"
    assert not (tmp_path / "web-v2" / "br-001.glb").exists()


def test_source_glb_takes_precedence_over_prepacked(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    prepacked = _prepacked(tmp_path, "br-006", build_triangle_glb())
    output = pack_glb(web_ready_document(sheen=True), b"\x00" * 4)
    seen = _fake_gltfpack(tmp_path, monkeypatch, output=output)

    code, report = _run(tmp_path, registry, src, "--prepacked-dir", str(prepacked))

    assert code == 0
    assert report["entries"][0]["source_kind"] == "source"
    assert [p.name for p in seen.iterdir()] == ["br-006.glb"]


def test_unexpected_error_on_one_sku_does_not_abort_the_batch(tmp_path, monkeypatch):
    """A malformed material must cost ONE sku, not the run — and the report must still land."""
    registry = _registry(tmp_path, {"br-006": SATIN, "sg-011": "White 100% cotton construction."})
    src = _sources(tmp_path, ["sg-011"])
    broken = pack_glb(_document_with_null_extensions(), b"\x00" * 9)
    (src / "br-006.glb").write_bytes(broken)
    output = pack_glb(web_ready_document(sheen=True), b"\x00" * 4)
    _fake_gltfpack(tmp_path, monkeypatch, output=output)

    code, report = _run(tmp_path, registry, src)

    by_sku = {entry["sku"]: entry for entry in report["entries"]}
    assert code == 1
    assert by_sku["br-006"]["status"] in {"patch_failed", "error"}
    assert by_sku["br-006"]["gate_pass"] is False
    assert by_sku["sg-011"]["status"] == "ok"  # the healthy SKU still published
    assert (tmp_path / "web-v2" / "sg-011.glb").exists()
    assert not (tmp_path / "web-v2" / "br-006.glb").exists()


def _document_with_null_extensions() -> dict:
    document = build_triangle_document(9)
    document["materials"][0]["extensions"] = None
    return document


def test_prepacked_refuses_to_downgrade_a_source_built_output(tmp_path, monkeypatch):
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    output = pack_glb(web_ready_document(sheen=True), b"\x00" * 4)
    _fake_gltfpack(tmp_path, monkeypatch, output=output)
    first_code, first_report = _run(tmp_path, registry, src)
    assert first_code == 0 and first_report["entries"][0]["source_kind"] == "source"

    # Source disappears; only the legacy packed copy is left.
    (src / "br-006.glb").unlink()
    prepacked = _prepacked(
        tmp_path, "br-006", pack_glb(web_ready_document(sheen=False), b"\x00" * 4)
    )

    code, report = _run(tmp_path, registry, src, "--prepacked-dir", str(prepacked))
    assert code == 1
    assert report["entries"][0]["status"] == "refused_downgrade"

    forced_code, forced_report = _run(
        tmp_path, registry, src, "--prepacked-dir", str(prepacked), "--force"
    )
    assert forced_code == 0
    assert forced_report["entries"][0]["source_kind"] == "prepacked"


def test_broken_gltfpack_publishes_nothing_and_still_writes_the_report(tmp_path, monkeypatch):
    """A binary that always fails: every SKU is recorded, nothing lands, exit 1."""
    registry = _registry(tmp_path, {"br-006": SATIN})
    src = _sources(tmp_path, ["br-006"])
    binary = tmp_path / "gltfpack"
    binary.write_text("#!/bin/sh\nexit 3\n")
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("GLTFPACK_BIN", str(binary))

    code, report = _run(tmp_path, registry, src)

    assert code == 1
    assert report["entries"][0]["status"] == "pack_failed"
    assert report["tool"]["version"] == "unknown"
    assert not (tmp_path / "web-v2" / "br-006.glb").exists()
