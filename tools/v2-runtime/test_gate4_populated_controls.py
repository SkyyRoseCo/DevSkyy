"""Mock-only source controls; no fixture import, database, network or service action."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools/v2-runtime/test_gate4_populated.py"
TREE = ast.parse(SOURCE.read_text())


def functions(*names):
    return ast.Module(
        body=[n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name in names],
        type_ignores=[],
    )


def child(output, kind="service-failure"):
    path = Path(output)
    path.mkdir()
    calls = []

    class Process:
        def __init__(self, pid, broken):
            self.pid, self.broken = pid, broken

        def poll(self):
            calls.append([self.pid, "poll"])
            return None if self.broken else 0

        def wait(self, **kwargs):
            calls.append([self.pid, "wait"])
            if self.broken:
                raise RuntimeError("controlled wait failure")

        def terminate(self):
            calls.append([self.pid, "terminate"])
            raise ProcessLookupError("controlled terminate failure")

        def kill(self):
            calls.append([self.pid, "kill"])
            raise PermissionError("controlled kill failure")

    def stop(socket):
        calls.append(["stop", socket])
        raise RuntimeError("controlled graceful failure")

    def inventory(target):
        calls.append(["inventory", str(target)])
        if kind == "inventory-failure":
            raise RuntimeError("controlled inventory failure")
        return {"preserved": True}

    data = {"status": "INCOMPLETE"}
    namespace = {
        "base": SimpleNamespace(
            PROCESSES=[Process(1, kind == "service-failure"), Process(2, False)],
            stop=stop,
            inventory=inventory,
        ),
        "subprocess": SimpleNamespace(run=lambda *a, **kw: SimpleNamespace(returncode=1)),
        "SOCKET": "mock-only-no-socket",
        "OUT": path,
        "ORIGINAL": path,
        "original_cold": path / "original",
        "protected": {"wordpress": {"preserved": True}},
        "original_pins": {"preserved": True},
        "REPORT": data,
        "complete": True,
        "cleanup": [],
        "write": lambda p, value: p.write_text(json.dumps(value)),
    }
    exec(compile(functions("cleanup_owned"), str(SOURCE), "exec"), namespace)
    main = next(n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    at = next(i for i, n in enumerate(main.body) if isinstance(n, ast.Try) and n.finalbody)
    terminal = ast.Module(body=main.body[at].finalbody + main.body[at + 1 :], type_ignores=[])
    try:
        exec(compile(terminal, str(SOURCE), "exec"), namespace)
    finally:
        (path / "calls.json").write_text(json.dumps(calls))


def main():
    folder = (
        ROOT
        / ".artifacts/release-gates-20261019/gate4-populated"
        / ("controls-" + str(time.time_ns()))
    )
    folder.mkdir()
    result = subprocess.run(
        [sys.executable, str(Path(__file__)), "--child", str(folder / "terminal")],
        capture_output=True,
        timeout=20,
    )
    (folder / "terminal.txt").write_bytes(result.stdout + result.stderr)
    report = json.loads((folder / "terminal/results.json").read_text())
    calls = json.loads((folder / "terminal/calls.json").read_text())
    assert result.returncode != 0 and report["status"] == "FAIL_CLEANUP"
    assert report["protected_originals_unchanged"] and not report["owned_services_stopped"]
    assert [2, "wait"] in calls and [1, "kill"] in calls
    assert {entry["step"] for entry in report["cleanup_errors"]} == {
        "graceful-shutdown",
        "initial-child-wait",
        "child-terminate",
        "child-kill",
        "owned-child-survived",
    }
    inventory_result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__)),
            "--child",
            str(folder / "inventory-terminal"),
            "inventory-failure",
        ],
        capture_output=True,
        timeout=20,
    )
    (folder / "inventory-terminal.txt").write_bytes(
        inventory_result.stdout + inventory_result.stderr
    )
    inventory_report = json.loads((folder / "inventory-terminal/results.json").read_text())
    assert inventory_result.returncode != 0 and inventory_report["status"] == "FAIL_CLEANUP"
    assert (
        inventory_report["owned_services_stopped"]
        and not inventory_report["protected_originals_unchanged"]
    )
    assert inventory_report["service_cleanup_errors"] == []
    assert inventory_report["cleanup_errors"] == [
        {"step": "protected-inventories", "error": "RuntimeError"}
    ]
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        namespace = {
            "PRIVATE": root,
            "ROOT": root,
            "SNAPSHOT": 0,
            "RAW_PINS": {},
            "hashlib": hashlib,
            "json": json,
            "sql": lambda query: b"id\n" if "COLUMN_NAME" in query else b"V31\n",
        }
        exec(
            compile(functions("scope", "pin", "canonical", "same"), str(SOURCE), "exec"), namespace
        )
        one, two = namespace["scope"](), namespace["scope"]()
        assert set(v["preimage"] for v in one.values()).isdisjoint(
            v["preimage"] for v in two.values()
        )
        assert len(namespace["RAW_PINS"]) == 16
        assert all(
            namespace["pin"](root / p) == value for p, value in namespace["RAW_PINS"].items()
        )
        same = namespace["same"]
        assert not same(True, 1) and not same(1.0, 1) and not same(["x", "x"], ["x"])
    result = {
        "status": "PASS_MOCK_ONLY_SOURCE_CONTROLS",
        "authentication": "NOT_APPLICABLE",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "control_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "controls": [
            "cleanup_failures_preserve_reporting_and_nonzero_exit",
            "inventory_failure_distinct_from_successful_service_stop",
            "all_children_attempted_despite_fallback_errors",
            "protected_inventory_checks_after_cleanup_failure",
            "unique_exclusive_sql_preimages_and_pins",
            "boolean_float_and_multiplicity_differences_refused",
        ],
        "limits": "AST extracted actual functions and terminal block with mocked dependencies; no native runtime claim",
        "terminal_exit": result.returncode,
    }
    (folder / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(str(folder.relative_to(ROOT)))
    print(result["status"])


if __name__ == "__main__":
    if sys.argv[1:2] == ["--child"]:
        child(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "service-failure")
    else:
        main()
