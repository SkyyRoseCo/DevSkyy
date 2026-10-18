"""One-off proof of the exact recorded pretransport branch; no API endpoint or refund UI."""

from __future__ import annotations

import asyncio
import hashlib
import importlib.metadata
import json
import subprocess
import types
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
import sys

sys.path.insert(0, str(ROOT))
from skyyrose.godmode_runtime.service import Runtime

if __name__ == "__main__":
    receipt = ROOT / "tasks/godmode-agent-workers-20261018/fashion-campaign-analysis-live.json"
    saved = json.loads(receipt.read_text())["run"]
    old = subprocess.check_output(
        ["git", "show", "e2efee812:skyyrose/godmode_runtime/agent_adapters.py"], cwd=ROOT
    )
    assert (
        hashlib.sha256(old).hexdigest() == saved["plan"]["agent_contract"]["implementation_sha256"]
    )
    assert (
        importlib.metadata.version("claude-agent-sdk")
        == saved["plan"]["agent_contract"]["claude_sdk_version"]
        == "0.2.82"
    )
    module = types.ModuleType("pretransport_source_proof")
    module.__file__ = str(ROOT / "skyyrose/godmode_runtime/agent_adapters.py")
    exec(compile(old, module.__file__, "exec"), module.__dict__)
    from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport

    connected = []

    async def forbidden_connect(*args, **kwargs):
        connected.append(True)
        raise AssertionError("No network or transport is permitted in this reproduction")

    try:
        with patch.object(SubprocessCLITransport, "connect", forbidden_connect):
            asyncio.run(
                module._claude(
                    {
                        "stage": "claude-worker",
                        "packet": {},
                        "worker": None,
                        "contract": {"claude_model": "claude-opus-5-5"},
                    },
                    "/tmp",
                )
            )
    except ValueError as exc:
        assert str(exc).startswith("can_use_tool callback requires streaming mode.")
    else:
        raise AssertionError("Exact pretransport failure not reproduced")
    assert not connected
    r = Runtime(
        ROOT,
        Path("/Users/theceo/plugins/fashion-theme-team"),
        Path.home() / "Library/Application Support/DevSkyy/god-mode/runtime.sqlite",
    )
    with r.transaction() as conn:
        row = r._get(conn, saved["id"])
        run = r.get(saved["id"])
        assert row["status"] == "FAILED" and len(run["steps"]) == 1
        step = run["steps"][0]
        assert step.get("error_code") == "supervisor_failed" and not step.get("artifact")
        reservation = next(e for e in run["events"] if e["kind"] == "AGENT_ALLOWANCE_RESERVED")
        proof = {
            "run_id": saved["id"],
            "reservation_event_id": reservation["seq"],
            "adapter_sha256": hashlib.sha256(old).hexdigest(),
            "sdk_version": "0.2.82",
            "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
            "branch": "string_prompt_with_can_use_tool_raises_before_transport",
            "observed_transport_connections": 0,
            "usage_confirmed": 0,
            "observer": "codex-current-chat:01a1284f",
            "reconciliation_id": "pretransport-e2efee812-01a1284f",
            "automatic_refund": False,
        }
        if not any(e["kind"] == "AGENT_NO_DISPATCH_CONFIRMED" for e in run["events"]):
            r.event(conn, saved["id"], "AGENT_NO_DISPATCH_CONFIRMED", proof["observer"], proof)
    (receipt.parent / "pretransport-proof.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(
        "Exact saved SDK branch reproduced before transport; original reservation retained with one idempotent zero-dispatch attestation. Unknown timeout remains counted."
    )
