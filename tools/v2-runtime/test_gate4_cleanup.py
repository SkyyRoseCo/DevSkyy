"""Controlled mocked terminal branches; no DB startup, replay, or cleanup fault injected."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / ".artifacts/release-gates-20261019/gate4-local"
OUT = ROOT / "tasks/release-gates-20261019/gate4-local/evidence"
if not __debug__:
    raise RuntimeError("Cleanup controls require assertions")


def child(kind, output):
    import gate4_finalize_restore as finalizer

    path = Path(output)
    path.mkdir()
    (path / "lock").mkdir()
    source = (
        ROOT
        / "tools/v2-runtime"
        / ("gate4_finalize_restore.py" if kind == "finalizer" else "test_gate4_storage.py")
    )
    tree = ast.parse(source.read_text())
    body = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"
    ).body
    index = next(i for i, node in enumerate(body) if isinstance(node, ast.Try) and node.finalbody)
    # Execute the actual source's terminal finally+guard, mocking only cleanup
    # after successful primary checks. Never import/execute storage's main body.
    terminal = ast.Module(body=body[index].finalbody + body[index + 1 :], type_ignores=[])
    ast.fix_missing_locations(terminal)
    data = {
        "schema": "skyyrose.mocked-cleanup-branch.v1",
        "status": "INCOMPLETE",
        "populated_clone_full_file_bytes_modes_restored": True,
        "completed_restore_cold_bytes_modes_unchanged": True,
    }
    namespace = dict(vars(finalizer))
    namespace.update(
        {
            "cleanup_database": lambda socket: [
                {"step": "controlled_mock_cleanup_failure", "error": "SYNTHETIC"}
            ],
            "complete": True,
            "checkpoint": {"verified": True, "released": True},
            "overlay_owned": False,
            "overlay": path / "absent.php",
            "REPORT": data,
            "report": data,
            "OUT": path,
            "CHECK": path / "checkpoint.json",
            "lock": path / "lock",
            "original": path / "not-preserved",
            "moved_original": set(),
            "finish_preservation": lambda *args: (
                [{"step": "controlled_mock_cleanup_failure", "error": "SYNTHETIC"}],
                True,
            ),
            "restore_cold": None,
            "current": None,
            "SAVED": path,
            "RUN": finalizer.g.RUN_ID,
            "SOCKET": finalizer.g.SOURCE_SOCKET,
            "PRIVATE": path / "working",
            "errors": [],
            "fixture": finalizer.g,
        }
    )
    exec(compile(terminal, str(source), "exec"), namespace)


if sys.argv[1:2] == ["--child"]:
    child(sys.argv[2], sys.argv[3])
else:
    assert not sys.argv[1:]
    run = str(time.time_ns())
    folder = PRIVATE / ("cleanup-controls-" + run)
    folder.mkdir()
    rows = []
    for kind in ["finalizer", "storage"]:
        target = folder / kind
        result = subprocess.run(
            [sys.executable, str(Path(__file__)), "--child", kind, str(target)],
            capture_output=True,
            check=False,
            timeout=30,
        )
        receipt = folder / (kind + ".txt")
        receipt.write_bytes(result.stdout + result.stderr)
        assert result.returncode != 0 and b"FAIL_CLEANUP" in receipt.read_bytes()
        report = json.loads(
            (
                target
                / (
                    "restore-postboot-results.json"
                    if kind == "finalizer"
                    else "storage-results.json"
                )
            ).read_text()
        )
        assert (
            report["status"] == "FAIL_CLEANUP"
            and report["cleanup_errors"]
            and not (target / "lock").exists()
        )
        if kind == "finalizer":
            assert json.loads((target / "checkpoint.json").read_text())["released"] is False
        rows.append(
            {
                "kind": kind,
                "exit_code": result.returncode,
                "terminal_status": report["status"],
                "lock_released": True,
                "checkpoint_unreleased": kind == "finalizer",
                "receipt": str(receipt.relative_to(ROOT)),
                "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
            }
        )
    pins = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [
            Path(__file__),
            ROOT / "tools/v2-runtime/gate4_finalize_restore.py",
            ROOT / "tools/v2-runtime/test_gate4_storage.py",
        ]
    }
    report = {
        "schema": "skyyrose.mocked-terminal-cleanup-control.v1",
        "status": "PASS_FAIL_CLOSED_CONTROLS",
        "authentication": "NOT_APPLICABLE",
        "method": "Actual source AST terminal finally and guard, primary-complete boolean and cleanup failure mocked; no native DB operation/replay performed",
        "source_pins": pins,
        "controls": rows,
    }
    (OUT / "cleanup-failure-controls.json").write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"])
