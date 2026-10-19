"""Pinned synthetic Playwright8 archive transformation; accepts no live target.

All content-bearing fields are replaced, never searched-and-replaced in place.
A replayable redacted trace preserves observed action timing/reference structure,
not the original visual/content evidence. Raw captures remain private quarantine.
"""

from __future__ import annotations

import base64
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import zipfile

from PIL import Image

if not __debug__:
    raise RuntimeError("Optimized privacy execution is forbidden")

MARKER = b"SYNTHETIC_GATE4_PRIVATE_01a0f768"
ROOT = Path(__file__).resolve().parents[3]
PRIVATE = ROOT / ".artifacts/release-gates-20261019/gate4-privacy"
SAFE_HTML = b'<!doctype html><html><head></head><body style="margin:0;background:#808080;width:800px;height:600px">[redacted]</body></html>'
SAFE_JSON = b'{"content":"[redacted]"}'


def encoded(data: object) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scan(data: bytes) -> None:
    # Independent marker controls include raw, base64, hex and percent encoding.
    variants = [
        MARKER,
        base64.b64encode(MARKER),
        MARKER.hex().encode(),
        b"".join(b"%%%02X" % c for c in MARKER),
    ]
    assert not any(
        value.lower() in data.lower() for value in variants
    ), "Synthetic private marker in persisted bytes"


def read_archive(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as source:
        names = source.namelist()
        assert len(names) == len(set(names)) and len(names) <= 128
        result = {}
        for item in source.infolist():
            assert item.file_size <= 8_000_000 and item.compress_size <= 8_000_000
            assert not item.is_dir() and not item.flag_bits & 1
            assert item.filename in {
                "trace.trace",
                "trace.network",
                "trace.stacks",
            } or re.fullmatch(r"resources/[a-f0-9]{40}\.(html|json)", item.filename)
            result[item.filename] = source.read(item)  # Includes native CRC verification.
        assert {"trace.trace", "trace.network", "trace.stacks"} <= set(result)
        assert sum(map(len, result.values())) <= 16_000_000
        return result


def jsonl(data: bytes) -> list[dict]:
    assert data.endswith(b"\n"), "Truncated JSONL"
    result = [json.loads(line) for line in data.splitlines()]
    assert result and all(isinstance(row, dict) for row in result)
    return result


def numeric(value: object) -> float | int:
    assert type(value) in (int, float) and math.isfinite(value)
    return value


def transform(source: dict[str, bytes]) -> dict[str, bytes]:
    maps: dict[str, dict[str, str]] = {}

    def identity(kind: str, value: str) -> str:
        assert isinstance(value, str) and len(value) <= 512
        group = maps.setdefault(kind, {})
        if value not in group:
            group[value] = kind + "@" + str(len(group) + 1)
        return group[value]

    urls: dict[str, str] = {"about:blank": "about:blank"}

    def url(value: str) -> str:
        assert isinstance(value, str) and len(value) <= 8192
        if value not in urls:
            assert value.startswith("http://127.0.0.1:18472/"), "Unsupported resource origin"
            urls[value] = "http://redacted.invalid/resource/" + str(len(urls))
        return urls[value]

    def snapname(value: str) -> str:
        assert re.fullmatch(r"(before|after)@call@\d+", value)
        phase, call = value.split("@", 1)
        return phase + "@" + identity("call", call)

    network = []
    resources = {}
    used_original = set()
    for row in jsonl(source["trace.network"]):
        assert set(row) == {"type", "snapshot"} and row["type"] == "resource-snapshot"
        snap = row["snapshot"]
        request, response = snap["request"], snap["response"]
        assert request["method"] == "GET" and type(response["status"]) is int
        content = response["content"]
        original = "resources/" + content["_sha1"]
        assert original in source, "Dangling original resource reference"
        assert hashlib.sha1(source[original]).hexdigest() == original.split("/")[1].split(".")[0]
        used_original.add(original)
        mime = content["mimeType"]
        assert mime in ["text/html", "application/json"]
        body, suffix = (SAFE_HTML, ".html") if mime == "text/html" else (SAFE_JSON, ".json")
        key = hashlib.sha1(body).hexdigest() + suffix
        resources["resources/" + key] = body
        network.append(
            {
                "type": "resource-snapshot",
                "snapshot": {
                    "pageref": identity("page", snap["pageref"]),
                    "_frameref": identity("frame", snap["_frameref"]),
                    "startedDateTime": "1970-01-01T00:00:00.000Z",
                    "time": numeric(snap["time"]),
                    "_monotonicTime": numeric(snap["_monotonicTime"]),
                    "request": {
                        "method": "GET",
                        "url": url(request["url"]),
                        "httpVersion": "HTTP/1.1",
                        "headers": [],
                        "cookies": [],
                        "queryString": [],
                        "headersSize": -1,
                        "bodySize": 0,
                    },
                    "response": {
                        "status": response["status"],
                        "statusText": "[redacted]",
                        "httpVersion": "HTTP/1.1",
                        "headers": [{"name": "Content-Type", "value": mime}],
                        "cookies": [],
                        "content": {"size": len(body), "mimeType": mime, "_sha1": key},
                        "headersSize": -1,
                        "bodySize": len(body),
                        "redirectURL": "",
                    },
                    "cache": {},
                    "timings": {"send": 0, "wait": 0, "receive": 0},
                },
            }
        )
    assert used_original == {
        key for key in source if key.startswith("resources/")
    }, "Orphan raw resource"
    traces = []
    allowed_calls = {
        ("BrowserContext", "newPage"),
        ("BrowserContext", "newCDPSession"),
        ("BrowserContext", "addCookies"),
        ("BrowserContext", "storageState"),
        ("Frame", "goto"),
        ("Frame", "waitForFunction"),
        ("Frame", "waitForTimeout"),
        ("Frame", "evaluateExpression"),
        ("Page", "screenshot"),
    }
    before, after, snapshots, refs = set(), set(), set(), set()
    calls, log_calls, snapshot_calls, page_events, frame_pages = {}, [], [], set(), set()
    raw_trace = jsonl(source["trace.trace"])
    assert (
        raw_trace[0].get("type") == "context-options"
        and sum(row.get("type") == "context-options" for row in raw_trace) == 1
    ), "Unique leading context required"
    for position, row in enumerate(raw_trace):
        kind = row["type"]
        if kind == "context-options":
            assert row["version"] == 8 and row["playwrightVersion"] == "1.58.2"
            safe = {
                "version": 8,
                "type": kind,
                "origin": "library",
                "browserName": "chromium",
                "playwrightVersion": "1.58.2",
                "options": {"viewport": {"width": 800, "height": 600}, "serviceWorkers": "block"},
                "platform": "darwin",
                "wallTime": numeric(row["wallTime"]),
                "monotonicTime": numeric(row["monotonicTime"]),
                "sdkLanguage": "javascript",
                "testIdAttributeName": "data-testid",
                "contextId": identity("browser-context", row["contextId"]),
            }
        elif kind in ["before", "after", "log"]:
            call = identity("call", row["callId"])
            safe = {"type": kind, "callId": call}
            if kind == "before":
                assert (row["class"], row["method"]) in allowed_calls
                assert call not in before
                before.add(call)
                calls[call] = {"before": position, "start": numeric(row["startTime"])}
                safe.update(
                    {
                        "startTime": numeric(row["startTime"]),
                        "class": row["class"],
                        "method": row["method"],
                        "params": {},
                    }
                )
            elif kind == "after":
                assert call not in after
                after.add(call)
                assert call in calls and calls[call]["before"] < position
                calls[call]["end"] = numeric(row["endTime"])
                assert calls[call]["start"] <= calls[call]["end"]
                safe["endTime"] = numeric(row["endTime"])
                if "error" in row:
                    safe["error"] = {"name": "Error", "message": "[redacted]"}
            else:
                log_calls.append((call, numeric(row["time"])))
                safe.update({"time": numeric(row["time"]), "message": "[redacted]"})
            if "pageId" in row:
                safe["pageId"] = identity("page", row["pageId"])
            for key in ["beforeSnapshot", "afterSnapshot"]:
                if key in row:
                    safe[key] = snapname(row[key])
                    refs.add(safe[key])
                    assert safe[key].endswith("@" + call), "Snapshot belongs to another call"
        elif kind == "event":
            assert row["class"] == "BrowserContext" and row["method"] in ["page", "pageError"]
            safe = {
                "type": kind,
                "time": numeric(row["time"]),
                "class": "BrowserContext",
                "method": row["method"],
                "params": {},
            }
            if row["method"] == "page":
                safe["params"]["pageId"] = identity("page", row["params"]["pageId"])
                page_events.add(safe["params"]["pageId"])
            else:
                safe["params"]["error"] = {
                    "name": "Error",
                    "message": "[redacted]",
                    "stack": "[redacted]",
                }
            if "pageId" in row:
                safe["pageId"] = identity("page", row["pageId"])
        elif kind == "console":
            assert row["messageType"] in ["error", "warning", "warn", "info", "log"]
            safe = {
                "type": kind,
                "messageType": row["messageType"],
                "text": "[redacted]",
                "args": [],
                "location": {"url": "", "lineNumber": 0, "columnNumber": 0},
                "time": numeric(row["time"]),
                "pageId": identity("page", row["pageId"]),
            }
        elif kind == "frame-snapshot":
            snap = row["snapshot"]
            name = snapname(snap["snapshotName"])
            assert name not in snapshots and snap["isMainFrame"] is True
            snapshots.add(name)
            call = identity("call", snap["callId"])
            assert name.endswith("@" + call), "Snapshot call/name mismatch"
            snapshot_calls.append(call)
            frame_pages.add(identity("page", snap["pageId"]))
            safe = {
                "type": kind,
                "snapshot": {
                    "callId": identity("call", snap["callId"]),
                    "snapshotName": name,
                    "pageId": identity("page", snap["pageId"]),
                    "frameId": identity("frame", snap["frameId"]),
                    "frameUrl": url(snap["frameUrl"]),
                    "html": [
                        "HTML",
                        {},
                        ["HEAD", {}],
                        ["BODY", {"style": "background:#808080"}, "[redacted]"],
                    ],
                    "viewport": {"width": 800, "height": 600},
                    "timestamp": numeric(snap["timestamp"]),
                    "wallTime": numeric(snap["wallTime"]),
                    "collectionTime": 0,
                    "resourceOverrides": [],
                    "isMainFrame": True,
                },
            }
        else:
            raise AssertionError("Unsupported trace record type")
        traces.append(safe)
    assert before and before == after and refs == snapshots and len(maps.get("page", {})) == 1
    assert (
        page_events == frame_pages == set(maps["page"].values()) and len(maps.get("frame", {})) == 1
    )
    assert all(
        call in before and calls[call]["start"] <= timestamp <= calls[call]["end"]
        for call, timestamp in log_calls
    ), "Orphan/out-of-order log"
    assert all(call in before for call in snapshot_calls), "Orphan snapshot call"
    # Source stacks contain host paths; source inspection intentionally unavailable.
    json.loads(source["trace.stacks"])
    result = {
        "trace.trace": b"".join(encoded(row) for row in traces),
        "trace.network": b"".join(encoded(row) for row in network),
        "trace.stacks": encoded({"files": [], "stacks": []}),
        **resources,
    }
    for name, data in result.items():
        scan(name.encode())
        scan(data)
    validate_resources(result)
    return result


def validate_resources(members: dict[str, bytes]) -> None:
    references = set(re.findall(rb'"_sha1":"([^"\\]+)"', members["trace.network"]))
    assert {"resources/" + item.decode() for item in references} == {
        key for key in members if key.startswith("resources/")
    }
    for item in references:
        key = item.decode()
        assert hashlib.sha1(members["resources/" + key]).hexdigest() == key.split(".")[0]


def seal(raw: Path, output: Path) -> dict:
    assert not output.exists() and raw.resolve().is_relative_to(PRIVATE.resolve())
    stage = output.with_name(output.name + ".unsealed")
    stage.mkdir(parents=True, exist_ok=False)
    capture = json.loads((raw / "capture.json").read_text())
    raw_names = [
        "raw-trace.zip",
        "raw-network.json",
        "raw-log.json",
        "raw-storage.json",
        "masked.png",
    ]
    assert set(capture["raw_pins"]) == set(raw_names)
    assert all(
        digest((raw / name).read_bytes()) == capture["raw_pins"][name] for name in raw_names
    ), "Raw capture receipt mismatch"
    original = read_archive(raw / "raw-trace.zip")
    journal = json.loads((raw / "raw-network.json").read_text())
    requests, responses = {}, {}
    for event in journal["events"]:
        key = (event["session"], event["value"]["requestId"])
        if event["kind"] == "requestWillBeSent":
            assert key not in requests
            requests[key] = event["value"]["request"]
        if event["kind"] == "responseReceived":
            assert key not in responses
            responses[key] = event["value"]["response"]
    assert requests.keys() == responses.keys(), "Independent trace/CDP request closure differs"
    observed = Counter(
        (value["method"], value["url"], responses[key]["status"]) for key, value in requests.items()
    )
    traced = Counter(
        (
            row["snapshot"]["request"]["method"],
            row["snapshot"]["request"]["url"],
            row["snapshot"]["response"]["status"],
        )
        for row in jsonl(original["trace.network"])
    )
    assert observed and observed == traced, "Independent trace/CDP request inventories differ"
    members = transform(original)
    with zipfile.ZipFile(stage / "trace.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(members.items()):
            entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    assert read_archive(stage / "trace.zip") == members
    node = ROOT / ".artifacts/release-gates-20261019/toolchain/node-v22.23.2-darwin-arm64/bin/node"
    projected = subprocess.run(
        [
            "/usr/bin/sandbox-exec",
            "-p",
            "(version 1)(allow default)(deny network*)",
            str(node),
            str(Path(__file__).with_name("collector.cjs")),
            "--reduce",
            str(raw / "raw-network.json"),
        ],
        capture_output=True,
        check=True,
        timeout=10,
    )
    network = json.loads(projected.stdout)
    assert network == json.loads(
        (raw / "network.json").read_text()
    ), "Projection differs from observed journal"
    assert network["complete"] is True, "Incomplete capture cannot be sealed"
    (stage / "network.json").write_bytes(encoded(network))
    storage = json.loads((raw / "raw-storage.json").read_text())
    (stage / "storage.json").write_bytes(
        encoded(
            {
                "schema": "skyyrose.redacted-storage.v1",
                "cookie_count": len(storage["cookies"]),
                "local_storage_count": len(storage["local"]),
                "session_storage_count": len(storage["session"]),
                "values_retained": False,
                "scope": "Single observed origin cookies/localStorage/sessionStorage; excludes IndexedDB/cache storage",
            }
        )
    )
    logs = json.loads((raw / "raw-log.json").read_text())
    assert all(row["kind"] in ["console", "pageerror"] for row in logs)
    (stage / "log.json").write_bytes(
        encoded(
            {
                "schema": "skyyrose.redacted-log.v1",
                "entry_count": len(logs),
                "entries": [
                    {"sequence": i + 1, "kind": row["kind"], "text": "[redacted]"}
                    for i, row in enumerate(logs)
                ],
            }
        )
    )
    journal = json.loads((raw / "raw-network.json").read_text())
    assert (
        capture["event_count"]
        == capture["traceEndSequence"]
        == journal["traceEndSequence"]
        == len(journal["events"])
    ), "Capture/journal terminal counters differ"
    assert (
        capture["logs"] == len(logs)
        and capture["storage_cookie_count"] == len(storage["cookies"])
        and capture["local_storage_count"] == len(storage["local"])
        and capture["session_storage_count"] == len(storage["session"])
    )
    assert (
        capture["schema"] == "skyyrose.synthetic-capture.v1"
        and capture["mode"] in ["clean", "tainted", "cancelled"]
        and capture["playwright"] == "1.58.2"
    )
    assert re.fullmatch(r"[0-9.]{1,64}", capture["browser"]) and capture["closed"] is True
    denial_keys = ["tcp", "udp", "inherited_child_tcp", "inherited_child_udp", "other_loopback"]
    assert all(capture["denial"][key] == "EPERM" for key in denial_keys)
    count_keys = [
        "event_count",
        "traceEndSequence",
        "logs",
        "storage_cookie_count",
        "local_storage_count",
        "session_storage_count",
        "late_log_count",
    ]
    assert all(type(capture[key]) is int and capture[key] >= 0 for key in count_keys)
    (stage / "capture.json").write_bytes(
        encoded(
            {
                "schema": capture["schema"],
                "mode": capture["mode"],
                "raw_pins": {key: digest((raw / key).read_bytes()) for key in raw_names},
                "playwright": "1.58.2",
                "browser": capture["browser"],
                "closed": True,
                "denial": dict.fromkeys(denial_keys, "EPERM"),
                **{key: capture[key] for key in count_keys},
            }
        )
    )
    with Image.open(raw / "masked.png") as image:
        assert (
            image.format == "PNG"
            and getattr(image, "n_frames", 1) == 1
            and image.size == (800, 600)
            and image.convert("RGB").getextrema() == ((128, 128),) * 3
        ), "Unmasked screenshot pixels"
        assert "A" not in image.getbands() or image.getchannel("A").getextrema() == (
            255,
            255,
        ), "Nonopaque screenshot"
        assert image.mode in ["RGB", "RGBA"], "Unsupported screenshot representation"
    # Never copy input PNG chunks, compressed metadata, alpha or trailing bytes.
    Image.new("RGB", (800, 600), (128, 128, 128)).save(stage / "screenshot.png", format="PNG")
    artifacts = {}
    for file in sorted(stage.iterdir()):
        data = file.read_bytes()
        scan(file.name.encode())
        scan(data)
        artifacts[file.name] = {"sha256": digest(data), "bytes": len(data)}
    manifest = {
        "schema": "skyyrose.sealed-synthetic-privacy.v1",
        "sealed": True,
        "authentication": "NOT_APPLICABLE",
        "policy": network["policy"],
        "artifacts": artifacts,
        "archive_members": {
            key: {"sha256": digest(value), "bytes": len(value)}
            for key, value in sorted(members.items())
        },
        "limits": [
            "Local synthetic successor only; original consumed live capture FAIL and eight UNKNOWN rows remain",
            "All page/resource/log/storage content redacted; screenshot fully opaque, no creative or visual acceptance",
            "Replayable trace structure is pinned to Playwright1.58.2 traceversion8; generic-site/installed parity not qualified",
            "Storage scope excludes IndexedDB/cache storage",
        ],
    }
    (stage / "manifest.json").write_bytes(encoded(manifest))
    scan((stage / "manifest.json").read_bytes())
    stage.rename(output)
    return manifest


if __name__ == "__main__":
    assert (
        len(sys.argv) == 3
        and re.fullmatch(r"\d+", sys.argv[1])
        and sys.argv[2] in ["clean", "tainted", "cancelled"]
    )
    source = PRIVATE / sys.argv[1] / sys.argv[2]
    print(json.dumps(seal(source, source.parent / (sys.argv[2] + "-accepted"))))
