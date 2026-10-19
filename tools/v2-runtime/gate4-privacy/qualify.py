"""Run the entire synthetic collector qualification without a live-site entry point."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

if not __debug__:
    raise RuntimeError("Privacy qualification requires assertions")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NODE = ROOT / ".artifacts/release-gates-20261019/toolchain/node-v22.23.2-darwin-arm64/bin/node"
PRIVATE = ROOT / ".artifacts/release-gates-20261019/gate4-privacy"
RUN = str(time.time_ns())
OUT = PRIVATE / RUN
OUT.mkdir(parents=True, exist_ok=False)
report = {
    "schema": "skyyrose.local-privacy-qualification.v1",
    "status": "INCOMPLETE",
    "run": RUN,
    "authentication": "NOT_APPLICABLE",
    "live_attempts": 0,
    "original_collector_repaired": False,
    "original_live_status": "FAIL",
    "original_unsupported_rows": "8 UNKNOWN",
    "commands": [],
}


def execute(arguments: list[str], name: str, timeout: int = 180) -> None:
    try:
        result = subprocess.run(
            arguments,
            cwd=ROOT,
            env={**os.environ, "SR_PRIVACY_RUN": RUN},
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        data = result.stdout + result.stderr
    except subprocess.TimeoutExpired as error:
        data = (error.stdout or b"") + (error.stderr or b"")
        (OUT / name).write_bytes(data)
        raise
    (OUT / name).write_bytes(data)
    report["commands"].append(
        {
            "receipt": name,
            "exit_code": result.returncode,
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        }
    )
    assert result.returncode == 0, name


try:
    execute([str(NODE), str(HERE / "run.cjs")], "capture-command.txt")
    for mode in ["clean", "tainted"]:
        execute([sys.executable, str(HERE / "sanitize.py"), RUN, mode], mode + "-seal-command.txt")
    execute([str(NODE), str(HERE / "test-network.cjs"), RUN], "network-controls-command.txt")
    execute([sys.executable, str(HERE / "test_artifacts.py"), RUN], "artifact-controls-command.txt")
    execute([str(NODE), str(HERE / "viewer.cjs"), RUN], "viewer-command.txt")
    expected = json.loads((OUT / "source-pins-at-capture-start.json").read_text())
    assert all(
        hashlib.sha256((HERE / name).read_bytes()).hexdigest() == pin
        for name, pin in expected.items()
    )
    report["source_pins"] = expected
    report["network_controls"] = len(
        json.loads((OUT / "network-controls.json").read_text())["controls"]
    )
    report["artifact_controls"] = len(
        json.loads((OUT / "artifact-controls.json").read_text())["controls"]
    )
    report["viewer"] = json.loads((OUT / "viewer-results.json").read_text())
    assert all(
        row["replayed_redacted_snapshot"] and row["errors"] == 0
        for row in report["viewer"]["results"]
    )
    report["status"] = "PASS_SYNTHETIC_PRIVACY_COLLECTOR_ONLY"
except BaseException as error:
    report["failure"] = {"type": type(error).__name__, "message": str(error)[:500]}
    raise
finally:
    (OUT / "qualification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"run": RUN, "status": report["status"]}))
