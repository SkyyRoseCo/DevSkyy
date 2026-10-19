"""Follow-up assertion layer over complete retained synthetic native receipts."""

from __future__ import annotations

import ast
import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time

from gate4_refund_attribution import validate_attribution

if not __debug__:
    raise RuntimeError("Optimized offline verification is unsupported")
ROOT = Path(__file__).resolve().parents[2]
NATIVE_SOURCE = "2cd09fd0cd19fa72790dd32d718026c8ac4ee7db"


def pin(p):
    return {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}


def decode(p):
    body = p.read_text()
    marker = "SR_G4_POP="
    at = body.rfind(marker)
    assert at >= 0
    return json.JSONDecoder().raw_decode(body[at + len(marker) :])[0]


def main():
    run = sys.argv[1]
    assert re.fullmatch(r"[0-9]{19}", run)
    private = ROOT / ".artifacts/release-gates-20261019/gate4-populated" / ("run-" + run)
    raw = ROOT / "tasks/release-gates-20261019/gate4-populated" / ("run-" + run)
    output = (
        ROOT
        / "tasks/release-gates-20261019/gate4-populated"
        / ("attribution-" + run + "-" + str(time.time_ns()))
    )
    output.mkdir()
    result = {
        "status": "INCOMPLETE",
        "authentication": "NOT_APPLICABLE",
        "native_run": run,
        "native_executed_source": NATIVE_SOURCE,
        "offline_validation_source": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "limits": "New offline assertions on complete retained native captures; no WordPress/database execution or retroactive claim that native driver had these stronger assertions",
    }
    try:
        report_path = raw / "results.json"
        report = json.loads(report_path.read_text())
        assert report["source_head"] == NATIVE_SOURCE
        assert (
            report["status"]
            == "PASS_PRIVATE_POPULATED_SYNC_AND_HISTORICAL_PAYMENTS_WITH_EXPLICIT_STOCK_PATH_LIMIT"
        )
        assert report["owned_services_stopped"] and report["protected_originals_unchanged"]
        assert report["cleanup_errors"] == report["service_cleanup_errors"] == []
        rows = [
            s
            for s in report["steps"]
            if s["step"] == "NATIVE_HPOS_REFUND_FIRST_BACKFILL_AUDIT_TRANSITION"
        ]
        assert len(rows) == 1
        captured = []
        for meta_path in sorted(raw.glob("command-*.json")):
            meta = json.loads(meta_path.read_text())
            if meta["argv"][-1] != "batch":
                continue
            receipt = raw / meta["receipt"]
            value = decode(receipt)
            if value.get("audit") is not None:
                captured.append((meta_path, receipt, value))
        assert len(captured) == 1
        meta_path, receipt, value = captured[0]
        number = int(meta_path.stem.split("-")[-1])
        after_meta = raw / (f"command-{number + 1:05}.json")
        after_receipt = raw / (f"command-{number + 1:05}.txt")
        assert json.loads(after_meta.read_text())["argv"][-1] == "inspect"
        after = decode(after_receipt)["snapshot"]
        body = subprocess.check_output(
            ["git", "show", NATIVE_SOURCE + ":tools/v2-runtime/test_gate4_populated.py"], cwd=ROOT
        )
        assert (
            hashlib.sha256(body).hexdigest()
            == report["source_pins"]["tools/v2-runtime/test_gate4_populated.py"]["sha256"]
        )
        native_copy = private / "native-executed-driver.py"
        if native_copy.exists():
            assert native_copy.read_bytes() == body
        else:
            native_copy.write_bytes(body)
        names = {"canonical", "same", "semantic_orders", "same_orders", "validate_refund_audit"}
        tree = ast.parse(body)
        selected = [
            node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names
        ]
        assert len(selected) == len(names)
        namespace = {"RUN": run, "json": json, "datetime": datetime, "math": math, "re": re}
        exec(
            compile(ast.Module(body=selected, type_ignores=[]), str(native_copy), "exec"), namespace
        )
        transition = namespace["validate_refund_audit"](
            value["audit"]["before_snapshot"], after, value
        )
        assert namespace["same"](transition, rows[0]["transition"])
        site = private / "wordpress"
        site_manifest = private / "site-at-start.json"
        inventory = json.loads(site_manifest.read_text())
        attribution = validate_attribution(value["audit"], site, inventory)
        controls = []
        witness = attribution["timestamp_writers"][0]
        for mutation in [
            "wrong-class",
            "wrong-file",
            "reordered-chain",
            "extra-unattributed-writer",
        ]:
            bad = json.loads(json.dumps(value["audit"]))
            query = bad["queries"][witness["query_index"]]
            positions = witness["required_frame_positions"]
            if mutation == "wrong-class":
                query["stack"][positions[3]]["class"] = "Wrong_Native_Class"
            elif mutation == "wrong-file":
                query["stack"][positions[3]]["file"] += ".wrong"
            elif mutation == "reordered-chain":
                a, b = positions[3:5]
                query["stack"][a], query["stack"][b] = query["stack"][b], query["stack"][a]
            else:
                extra = json.loads(json.dumps(query))
                extra["stack"] = []
                bad["queries"].append(extra)
            try:
                validate_attribution(bad, site, inventory)
            except AssertionError:
                controls.append(
                    {"mutation": mutation, "status": "PASS_REFUSED_MODIFIED_RETAINED_TRACE"}
                )
            else:
                raise AssertionError("Attribution accepted " + mutation)
        inputs = [
            report_path,
            meta_path,
            receipt,
            after_meta,
            after_receipt,
            site_manifest,
            native_copy,
        ]
        result.update(
            {
                "status": "PASS_SEPARATE_ORDERED_CLASS_FILE_ALL_WRITERS_VALIDATION",
                "attribution": attribution,
                "controls": controls,
                "input_pins": {str(p.relative_to(ROOT)): pin(p) for p in inputs},
                "source_pins": {
                    str(p.relative_to(ROOT)): pin(p)
                    for p in [Path(__file__), ROOT / "tools/v2-runtime/gate4_refund_attribution.py"]
                },
            }
        )
    except BaseException as error:
        result["status"] = "FAIL_OFFLINE_VALIDATION"
        result["failure"] = {"type": type(error).__name__, "message": str(error)[:1500]}
        raise
    finally:
        (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(str(output.relative_to(ROOT)))
    print(result["status"])


if __name__ == "__main__":
    main()
