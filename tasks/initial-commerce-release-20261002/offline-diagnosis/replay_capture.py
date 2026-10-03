"""Replay only a hash-pinned pure classifier from consumed receipts, never its runner."""

import ast
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PACKET = Path(
    "/Users/theceo/.codex/worktrees/4035/DevSkyy/tasks/production-readiness-redteam-20261001/final-clearance/v1-operational-checkpoint-actual-failure-packet-e526b1b5.json"
)
packet = json.loads(PACKET.read_text())
root = Path(packet["output_path"]) / "checkpoint"
source = root / "native-network-capture.py"
raw = source.read_bytes()
assert (
    hashlib.sha256(raw).hexdigest()
    == packet["output_files"]["checkpoint/native-network-capture.py"]["sha256"]
)
tree = ast.parse(raw)
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "classify_row")
names = {"CAPTURED", "DISK", "MEMORY", "CSP", "UNKNOWN"}
constants = [
    n
    for n in tree.body
    if isinstance(n, ast.Assign)
    and len(n.targets) == 1
    and isinstance(n.targets[0], ast.Name)
    and n.targets[0].id in names
]
assert len(constants) == 5 and all(
    isinstance(n.value, ast.Constant) and isinstance(n.value.value, str) for n in constants
)
namespace = {"Any": Any, "math": math}
exec(compile(ast.Module(body=constants + [fn], type_ignores=[]), str(source), "exec"), namespace)
results = []
for profile in ("desktop", "mobile"):
    path = root / profile / "receipt.json"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == packet["output_files"][f"checkpoint/{profile}/receipt.json"]["sha256"]
    receipt = json.loads(path.read_text())
    counts = Counter()
    unsupported = []
    for row in receipt["requests"]:
        failures = []

        def trace(frame, event, argument, failures=failures):
            if (
                event == "exception"
                and frame.f_code.co_name == "classify_row"
                and argument[0] in (AssertionError, KeyError, TypeError)
            ):
                failures.append(frame.f_lineno)
            return trace

        sys.settrace(trace)
        try:
            disposition, cookies = namespace["classify_row"](row)
        finally:
            sys.settrace(None)
        counts[disposition] += 1
        if disposition == namespace["UNKNOWN"]:
            assertions = [
                n for n in ast.walk(fn) if isinstance(n, ast.Assert) and n.lineno in failures
            ]
            unsupported.append(
                {
                    "request_id": row["request_id"],
                    "url": row["url"],
                    "type": row["type"],
                    "sequence": row["sequence"],
                    "requests": row["requests"],
                    "request_extra_count": len(row["extras"]),
                    "response_extra_count": len(row["response_extras"]),
                    "responses": row["responses"],
                    "finished": row["finished"],
                    "failed": row["failed"],
                    "cache_events": row["cache_events"],
                    "original_exported_disposition": row["disposition"],
                    "pure_classifier_disposition": disposition,
                    "failing_assertions": [
                        ast.get_source_segment(raw.decode(), n) for n in assertions
                    ],
                    "cookie_absence_proven": False,
                }
            )
    assert len(unsupported) == 4
    results.append(
        {
            "profile": profile,
            "receipt_sha256": digest,
            "original_exported_counts": dict(
                Counter(r["disposition"] for r in receipt["requests"])
            ),
            "pure_classifier_counts": dict(counts),
            "unsupported_rows": unsupported,
        }
    )
output = {
    "status": "PASS_OFFLINE_DIAGNOSIS_ONLY",
    "packet_sha256": hashlib.sha256(PACKET.read_bytes()).hexdigest(),
    "classifier_source_sha256": hashlib.sha256(raw).hexdigest(),
    "profiles": results,
    "authority": "Consumed checkpoint remains FAIL; no runner/browser/provider invoked and no retry authority inferred.",
    "limits": "Pure per-row replay does not qualify globally failed capture or convert missing cookie evidence into absence.",
}
Path(__file__).with_name("capture-replay.json").write_text(json.dumps(output, indent=2) + "\n")
print(
    json.dumps(
        [
            {
                "profile": r["profile"],
                "original": r["original_exported_counts"],
                "pure": r["pure_classifier_counts"],
                "unsupported": len(r["unsupported_rows"]),
            }
            for r in results
        ]
    )
)
