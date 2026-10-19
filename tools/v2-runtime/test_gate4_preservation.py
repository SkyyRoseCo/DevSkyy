"""Private filesystem/process mocks for storage-fixture preservation failures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import time
from unittest.mock import patch
import test_gate4_storage as source

ROOT = source.ROOT
folder = source.PRIVATE / ("preservation-controls-" + str(time.time_ns()))
folder.mkdir()
controls = []


def initialize(label):
    case = folder / label
    case.mkdir()
    working = case / "working"
    working.mkdir()
    for name in ["wordpress", "mysql"]:
        (working / name).mkdir()
        (working / name / "original").write_bytes(("original-" + name).encode())
    return case, working


def verify_original(working):
    for name in ["wordpress", "mysql"]:
        assert (working / name / "original").read_bytes() == ("original-" + name).encode()


case, working = initialize("failed-preflight")
with (
    patch.object(source, "PRIVATE", working),
    patch.object(source.fixture, "PROCESSES", []),
    patch.object(
        source, "cleanup_database", side_effect=AssertionError("Must not stop pre-existing service")
    ) as stop,
    patch.object(
        source, "socket_stopped", side_effect=AssertionError("Must not probe failed preflight")
    ),
):
    errors, safe = source.finish_preservation(case / "absent", None, set())
    assert not errors and safe
    stop.assert_not_called()
    verify_original(working)
controls.append(
    {
        "name": "failed preflight never stops encountered unowned service or moves originals",
        "status": "PASS",
    }
)
case, working = initialize("second-rename-failure")
original = case / "preserved"
moved = set()
rename = Path.rename
with patch.object(source, "PRIVATE", working):

    def fail_second(path, target):
        if path == working / "mysql" and target == original / "mysql":
            raise OSError("SYNTHETIC_SECOND_RENAME_FAILURE")
        return rename(path, target)

    with patch.object(Path, "rename", fail_second):
        try:
            source.preserve_populated(original, moved)
        except OSError:
            pass
        else:
            raise AssertionError("Second rename must fail")
    assert moved == {"wordpress"} and (working / "mysql/original").exists()
    with (
        patch.object(source.fixture, "PROCESSES", []),
        patch.object(source, "socket_stopped", return_value=True),
    ):
        errors, safe = source.finish_preservation(original, None, moved)
        assert not errors and safe
    verify_original(working)
controls.append(
    {
        "name": "failed second initial rename restores only moved original path, untouched mysql remains original",
        "status": "PASS",
    }
)
for label, live in [("surviving-daemon", True), ("one-quarantine-rename-failure", False)]:
    case, working = initialize(label)
    original = case / "preserved"
    current = case / "fixture"
    current.mkdir()
    (current / "fixture-owner.json").write_text(json.dumps({"run": source.RUN}))
    moved = set()
    with patch.object(source, "PRIVATE", working):
        source.preserve_populated(original, moved)
        for name in ["wordpress", "mysql"]:
            (working / name).mkdir()
            (working / name / "fresh").write_bytes(b"fresh-disposable")
        if live:
            with (
                patch.object(source.fixture, "PROCESSES", [SimpleNamespace(poll=lambda: None)]),
                patch.object(
                    source, "cleanup_database", return_value=[{"step": "MOCKED_UNSTOPPABLE_CHILD"}]
                ),
                patch.object(
                    source,
                    "socket_stopped",
                    side_effect=AssertionError("Live child prevents path moves"),
                ),
            ):
                errors, safe = source.finish_preservation(original, current, moved)
                assert errors and not safe
            verify_original(original)
            assert all(
                (working / name / "fresh").read_bytes() == b"fresh-disposable"
                for name in ["wordpress", "mysql"]
            )
        else:

            def fail_wordpress(path, target, working=working, current=current):
                if path == working / "wordpress" and target == current / "wordpress":
                    raise OSError("SYNTHETIC_QUARANTINE_RENAME_FAILURE")
                return rename(path, target)

            with (
                patch.object(source.fixture, "PROCESSES", []),
                patch.object(source, "socket_stopped", return_value=True),
                patch.object(Path, "rename", fail_wordpress),
            ):
                errors, safe = source.finish_preservation(original, current, moved)
                assert errors and safe
            assert (original / "wordpress/original").read_bytes() == b"original-wordpress"
            assert (working / "mysql/original").read_bytes() == b"original-mysql"
    controls.append({"name": label, "status": "PASS_FAIL_CLOSED", "services_started": False})
report = {
    "schema": "skyyrose.storage-preservation-mock-controls.v1",
    "status": "PASS_MOCKED_PRESERVATION_CONTROLS",
    "authentication": "NOT_APPLICABLE",
    "method": "Actual source preservation helpers with temporary private filesystem and mocked process outcomes; no native database startup",
    "controls": controls,
    "source_pins": {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [Path(__file__), Path(source.__file__)]
    },
    "private_fixture": str(folder.relative_to(ROOT)),
}
(source.OUT / "storage-preservation-controls.json").write_text(json.dumps(report, indent=2) + "\n")
print(report["status"])
