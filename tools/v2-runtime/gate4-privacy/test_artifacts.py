"""Decisive privacy archive controls using actual synthetic capture bytes."""

from __future__ import annotations
import copy
import json
from pathlib import Path
import re
import sys
import time
import zipfile
import warnings
from sanitize import (
    PRIVATE,
    MARKER,
    read_archive,
    transform,
    scan,
    seal,
    validate_resources,
    encoded,
    digest,
)

if not __debug__:
    raise RuntimeError("Privacy controls require assertions")
assert len(sys.argv) == 2 and re.fullmatch(r"\d+", sys.argv[1])
base = PRIVATE / sys.argv[1]
control = base / ("artifact-controls-" + str(time.time_ns()))
control.mkdir()
raw = read_archive(base / "tainted/raw-trace.zip")
controls = []


def refusal(name, callback, message=None):
    try:
        callback()
    except (AssertionError, ValueError, KeyError, zipfile.BadZipFile) as error:
        assert message is None or str(error) == message, (name, str(error))
        controls.append({"name": name, "status": "PASS_FAIL_CLOSED"})
    else:
        raise AssertionError("Unsafe control accepted: " + name)


for label, blob in [
    ("raw trace", b"".join(raw.values())),
    ("raw log", (base / "tainted/raw-log.json").read_bytes()),
    ("raw network", (base / "tainted/raw-network.json").read_bytes()),
    ("raw storage", (base / "tainted/raw-storage.json").read_bytes()),
]:
    refusal(label + " marker contamination rejected", lambda data=blob: scan(data))
import base64

for label, blob in [
    ("base64", base64.b64encode(MARKER)),
    ("hex", MARKER.hex().encode()),
    ("percent", b"".join(b"%%%02X" % c for c in MARKER)),
]:
    refusal("encoded " + label + " marker rejected", lambda data=blob: scan(data))


def bad_archive(name, members):
    target = control / (name + ".zip")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(target, "w") as archive:
            for key, value in members:
                archive.writestr(key, value)
    return target


refusal(
    "duplicate ZIP member",
    lambda: read_archive(
        bad_archive("duplicate", list(raw.items()) + [("trace.trace", raw["trace.trace"])])
    ),
)
refusal(
    "path traversal ZIP member",
    lambda: read_archive(bad_archive("traversal", list(raw.items()) + [("../escape", b"bad")])),
)
refusal(
    "unsupported binary ZIP member",
    lambda: read_archive(
        bad_archive("binary", list(raw.items()) + [("resources/private.png", b"bad")])
    ),
)
refusal(
    "oversized ZIP member",
    lambda: read_archive(
        bad_archive(
            "oversized", list(raw.items()) + [("resources/" + "a" * 40 + ".html", b"x" * 8_000_001)]
        )
    ),
)
truncated = control / "truncated.zip"
truncated.write_bytes((base / "tainted/raw-trace.zip").read_bytes()[:-100])
refusal("truncated ZIP", lambda: read_archive(truncated))
changed = copy.deepcopy(raw)
changed["trace.trace"] = changed["trace.trace"][:-1]
refusal("truncated JSONL", lambda: transform(changed))
changed = copy.deepcopy(raw)
lines = [json.loads(line) for line in changed["trace.trace"].splitlines()]
lines[0]["version"] = 9
changed["trace.trace"] = b"".join(encoded(line) for line in lines)
refusal("unsupported trace format", lambda: transform(changed))
changed = copy.deepcopy(raw)
del changed[next(key for key in changed if key.startswith("resources/"))]
refusal("dangling input resource", lambda: transform(changed))
changed = copy.deepcopy(raw)
changed["resources/" + "a" * 40 + ".json"] = b"{}"
refusal("orphan resource", lambda: transform(changed))


def mutated_trace(label, mutation):
    changed = copy.deepcopy(raw)
    rows = [json.loads(line) for line in changed["trace.trace"].splitlines()]
    mutation(rows)
    changed["trace.trace"] = b"".join(encoded(row) for row in rows)
    refusal(label, lambda: transform(changed))


mutated_trace("missing context record", lambda rows: rows.pop(0))
mutated_trace("duplicate context record", lambda rows: rows.append(copy.deepcopy(rows[0])))
mutated_trace(
    "orphan log call",
    lambda rows: rows.append({"type": "log", "callId": "orphan", "time": 1, "message": "private"}),
)
mutated_trace(
    "missing action after",
    lambda rows: rows.pop(next(i for i, row in enumerate(rows) if row["type"] == "after")),
)


def invalid_order(rows):
    first = next(i for i, row in enumerate(rows) if row["type"] == "before")
    last = next(
        i
        for i, row in enumerate(rows)
        if row["type"] == "after" and row["callId"] == rows[first]["callId"]
    )
    rows[first], rows[last] = rows[last], rows[first]


mutated_trace("action after before start", invalid_order)


def orphan_snapshot(rows):
    snap = next(row["snapshot"] for row in rows if row["type"] == "frame-snapshot")
    snap["callId"] = "call@999999"


mutated_trace("orphan snapshot call", orphan_snapshot)
safe = transform(raw)
del safe[next(key for key in safe if key.startswith("resources/"))]
refusal("dangling sanitized resource", lambda: validate_resources(safe))
output = control / "cancelled-accepted"
refusal("incomplete capture never sealed", lambda: seal(base / "cancelled", output))
assert not output.exists() and output.with_name(output.name + ".unsealed").exists()
controls.append(
    {
        "name": "sanitizer failure leaves only unsealed quarantine, no accepted packet",
        "status": "PASS",
    }
)


def verify_packet(folder):
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["sealed"] is True
    expected_files = {
        "capture.json",
        "log.json",
        "network.json",
        "screenshot.png",
        "storage.json",
        "trace.zip",
    }
    assert set(manifest["artifacts"]) == expected_files
    assert all(not item.is_symlink() for item in folder.rglob("*"))
    assert {
        str(item.relative_to(folder)) for item in folder.rglob("*") if item.is_file()
    } == expected_files | {"manifest.json"}
    for name, pin in manifest["artifacts"].items():
        data = (folder / name).read_bytes()
        assert digest(data) == pin["sha256"] and len(data) == pin["bytes"]
        scan(data)
    members = read_archive(folder / "trace.zip")
    assert set(members) == set(manifest["archive_members"])
    validate_resources(members)
    for name, data in members.items():
        scan(name.encode())
        scan(data)
        assert manifest["archive_members"][name] == {"sha256": digest(data), "bytes": len(data)}
    return manifest


for mode in ["clean", "tainted"]:
    manifest = verify_packet(base / (mode + "-accepted"))
    assert manifest["policy"] == (
        "PASS_NO_COOKIES" if mode == "clean" else "FAIL_FORBIDDEN_COOKIES"
    )
    controls.append(
        {"name": mode + " exact recursive artifact/member inventories verified", "status": "PASS"}
    )
# Mutated complete captures must not gain acceptance through copied counters/pixels.
import shutil
from PIL import Image, PngImagePlugin

for label in ["counter", "alpha", "metadata", "apng"]:
    fixture = control / ("fixture-" + label)
    shutil.copytree(base / "clean", fixture)
    candidate = control / (label + "-accepted")
    if label == "counter":
        capture = json.loads((fixture / "capture.json").read_text())
        capture["event_count"] += 1
        (fixture / "capture.json").write_bytes(encoded(capture))
        refusal(
            "capture counter mismatch never sealed",
            lambda fixture=fixture, candidate=candidate: seal(fixture, candidate),
        )
        assert not candidate.exists()
    elif label == "alpha":
        Image.new("RGBA", (800, 600), (128, 128, 128, 0)).save(fixture / "masked.png")
        receipt = json.loads((fixture / "capture.json").read_text())
        receipt["raw_pins"]["masked.png"] = digest((fixture / "masked.png").read_bytes())
        (fixture / "capture.json").write_bytes(encoded(receipt))
        refusal(
            "transparent screenshot refused",
            lambda fixture=fixture, candidate=candidate: seal(fixture, candidate),
        )
        assert not candidate.exists()
    elif label == "apng":
        Image.new("RGB", (800, 600), (128, 128, 128)).save(
            fixture / "masked.png",
            save_all=True,
            append_images=[Image.new("RGB", (800, 600), (255, 0, 0))],
            duration=100,
            loop=0,
        )
        receipt = json.loads((fixture / "capture.json").read_text())
        receipt["raw_pins"]["masked.png"] = digest((fixture / "masked.png").read_bytes())
        (fixture / "capture.json").write_bytes(encoded(receipt))
        refusal(
            "multiframe PNG refused",
            lambda fixture=fixture, candidate=candidate: seal(fixture, candidate),
        )
        assert not candidate.exists()
    else:
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("private", MARKER.decode(), zip=True)
        Image.new("RGB", (800, 600), (128, 128, 128)).save(fixture / "masked.png", pnginfo=metadata)
        with (fixture / "masked.png").open("ab") as output_file:
            output_file.write(MARKER)
        receipt = json.loads((fixture / "capture.json").read_text())
        receipt["raw_pins"]["masked.png"] = digest((fixture / "masked.png").read_bytes())
        (fixture / "capture.json").write_bytes(encoded(receipt))
        sealed = seal(fixture, candidate)
        with Image.open(candidate / "screenshot.png") as final_image:
            assert (
                final_image.mode == "RGB"
                and not final_image.info
                and final_image.getextrema() == ((128, 128),) * 3
            )
        scan((candidate / "screenshot.png").read_bytes())
        controls.append(
            {
                "name": "compressed PNG text/trailing marker discarded by fresh opaque RGB encoding",
                "status": "PASS",
            }
        )
fixture = control / "fixture-missing-complete-action"
shutil.copytree(base / "clean", fixture)
changed = read_archive(fixture / "raw-trace.zip")
rows = [json.loads(line) for line in changed["trace.trace"].splitlines()]
call = next(row["callId"] for row in rows if row.get("method") == "newCDPSession")
rows = [row for row in rows if row.get("callId") != call]
changed["trace.trace"] = b"".join(encoded(row) for row in rows)
with zipfile.ZipFile(fixture / "raw-trace.zip", "w") as archive:
    for key, value in changed.items():
        archive.writestr(key, value)
refusal(
    "whole action pair removed differs from bound raw capture receipt",
    lambda: seal(fixture, control / "missing-action-accepted"),
)
assert not (control / "missing-action-accepted").exists()
fixture = control / "fixture-missing-request-group"
shutil.copytree(base / "clean", fixture)
journal = json.loads((fixture / "raw-network.json").read_text())
omitted = journal["events"][-1]["value"]["requestId"]
journal["events"] = [event for event in journal["events"] if event["value"]["requestId"] != omitted]
for i, event in enumerate(journal["events"]):
    event["seq"] = i + 1
journal["traceEndSequence"] = len(journal["events"])
(fixture / "raw-network.json").write_bytes(encoded(journal))
capture = json.loads((fixture / "capture.json").read_text())
capture["event_count"] = capture["traceEndSequence"] = len(journal["events"])
capture["raw_pins"]["raw-network.json"] = digest((fixture / "raw-network.json").read_bytes())
(fixture / "capture.json").write_bytes(encoded(capture))
import subprocess

node = (
    Path(__file__).resolve().parents[3]
    / ".artifacts/release-gates-20261019/toolchain/node-v22.23.2-darwin-arm64/bin/node"
)
projection = subprocess.check_output(
    [
        "/usr/bin/sandbox-exec",
        "-p",
        "(version 1)(allow default)(deny network*)",
        str(node),
        str(Path(__file__).with_name("collector.cjs")),
        "--reduce",
        str(fixture / "raw-network.json"),
    ]
)
(fixture / "network.json").write_bytes(projection)
assert json.loads(projection)["complete"] is True
refusal(
    "whole request group omitted with recomputed counters/pins differs from independent trace",
    lambda: seal(fixture, control / "missing-request-accepted"),
    "Independent trace/CDP request inventories differ",
)
assert not (control / "missing-request-accepted").exists()
for label in ["extra-file", "extra-manifest-member"]:
    folder = control / label
    shutil.copytree(base / "clean-accepted", folder)
    if label == "extra-file":
        (folder / "unlisted-private.txt").write_bytes(MARKER)
    else:
        manifest = json.loads((folder / "manifest.json").read_text())
        manifest["archive_members"]["resources/missing.json"] = {"sha256": "0" * 64, "bytes": 0}
        (folder / "manifest.json").write_bytes(encoded(manifest))
    refusal(label + " exact inventory refusal", lambda folder=folder: verify_packet(folder))
result = {"schema": "skyyrose.privacy-artifact-controls.v1", "status": "PASS", "controls": controls}
(base / "artifact-controls.json").write_bytes(encoded(result))
print(json.dumps({"status": "PASS", "controls": len(controls)}))
