"""Recover one retained code package against the installed census, without execution."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = Path("/Users/theceo/.codex/worktrees/release-gates-20261019/DevSkyy")
BASELINE = ORIGINAL / ".artifacts/release-gates-20261019/installed-baseline-raw-r2.json"
BASELINE_SHA = "f2379c9d4fef40a53552279b26b2fea6a1c34110d09aee174de6b1531de5258e"
PRIVATE = ROOT / ".artifacts/release-gates-20261019/managed-snapshot-followup"
PUBLIC = ROOT / "tasks/release-gates-20261019/gate4-managed-snapshot-followup"
CANDIDATE = Path(
    "/Users/theceo/Documents/AutoSorted 2/Others/"
    "skyyrose_co_15May2025_1750254942/skyyrose_co_15May2025_1750254942/"
    "home1/jpllicmy/public_html/med/wp-content/upgrade/plugins/woo-update-manager"
)


def pin(body: bytes) -> dict:
    return {"sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}


def no_links(path: Path) -> None:
    if any(item.is_symlink() for item in (path, *path.parents)):
        raise ValueError("Symlink candidate or ancestor refused")


def read(path: Path) -> bytes:
    no_links(path)
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > 8 * 1024 * 1024:
        raise ValueError("Nonregular or oversized evidence input")
    return path.read_bytes()


def ref(path: Path) -> dict:
    return {"path": str(path), **pin(read(path))}


def write(path: Path, body: bytes, mode: int = 0o600) -> None:
    no_links(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("xb") as stream:
        os.fchmod(stream.fileno(), mode)
        stream.write(body)


def json_write(path: Path, value: dict) -> None:
    write(path, (json.dumps(value, indent=2) + "\n").encode())


def exact_package(files: dict[str, bytes], expected: dict) -> None:
    if files.keys() != expected.keys():
        raise ValueError("Package member census differs")
    for name, body in files.items():
        record = expected[name]
        if record.get("symlink") is not False or pin(body) != {
            key: record[key] for key in ("sha256", "bytes")
        }:
            raise ValueError("Package member body differs")


def walk_error(error: OSError) -> None:
    raise error


def package_files(candidate: Path, expected: dict, walker=os.walk) -> dict[str, bytes]:
    no_links(candidate)
    if not candidate.is_dir():
        raise ValueError("Package directory required")
    files: dict[str, bytes] = {}
    for current, directories, names in walker(candidate, followlinks=False, onerror=walk_error):
        for name in directories:
            no_links(Path(current) / name)
        for name in names:
            path = Path(current) / name
            relative = path.relative_to(candidate).as_posix()
            # Inspect member names before reading. No unrecorded package content read.
            if relative not in expected or len(files) >= 5:
                raise ValueError("Unrecorded package member")
            files[relative] = read(path)
    exact_package(files, expected)
    return files


def main() -> None:
    if not __debug__:
        raise RuntimeError("Optimized evidence execution refused")
    if PUBLIC.exists() or (PRIVATE / "recovered-woo-update-manager").exists():
        raise RuntimeError("Existing evidence output refused")
    baseline_body = read(BASELINE)
    if pin(baseline_body)["sha256"] != BASELINE_SHA:
        raise ValueError("Installed snapshot pin differs")
    baseline = json.loads(baseline_body)
    prefix = "plugins/woo-update-manager/"
    expected = {
        name[len(prefix) :]: value
        for name, value in baseline["code_hashes"].items()
        if name.startswith(prefix)
    }
    if len(expected) != 5 or sum(value["bytes"] for value in expected.values()) != 6915:
        raise ValueError("Unexpected installed package census")
    discovery = PRIVATE / "filename-discovery.json"
    comparison = PRIVATE / "candidate-comparisons.json"
    for path, digest in [
        (discovery, "f6989d74f599d9c55a06d6953e0ac1d62c04e92e19a1ca9062c0a584d6f3a984"),
        (comparison, "f189def780354b81a88965101debd09f69929e96a4fa18f07dfb75a0ad9e7c5e"),
    ]:
        if ref(path)["sha256"] != digest:
            raise ValueError("Retained discovery/comparison pin differs")
    files = package_files(CANDIDATE, expected)
    version = re.search(
        rb"(?mi)^\s*\*?\s*Version:\s*([0-9A-Za-z.+_-]{1,64})\s*$",
        files["woo-update-manager.php"][:8192],
    )
    recorded_version = baseline["plugins"]["woo-update-manager/woo-update-manager.php"]["version"]
    if (
        version is None
        or version.group(1).decode() != recorded_version
        or recorded_version != "1.0.3"
    ):
        raise ValueError("Package version differs")
    controls = []
    for label in ("changed-byte", "missing-member", "extra-member"):
        altered = dict(files)
        name = "woo-update-manager.php"
        if label == "changed-byte":
            altered[name] = altered[name][:-1] + b"!"
        elif label == "missing-member":
            del altered[name]
        else:
            altered["unrecorded.txt"] = b"illustrative negative control"
        try:
            exact_package(altered, expected)
        except ValueError:
            controls.append({"mutation": label, "status": "PASS_REFUSED"})
        else:
            raise RuntimeError("Modified package accepted")

    def denied_walk(_path, *, followlinks, onerror):
        if followlinks is not False:
            raise RuntimeError("Control unexpectedly follows links")
        onerror(PermissionError("Synthetic unreadable descendant control"))
        return iter(())

    try:
        package_files(CANDIDATE, expected, walker=denied_walk)
    except PermissionError:
        controls.append({"mutation": "mock-walker-permission-error", "status": "PASS_REFUSED"})
    else:
        raise RuntimeError("Incomplete traversal accepted")
    retained = {}
    for name, body in sorted(files.items()):
        path = PRIVATE / "recovered-woo-update-manager" / name
        write(path, body)
        retained[name] = ref(path)
    findings = {
        "schema": "skyyrose.retained-managed-package-recovery.v1",
        "status": "EXACT_RECORDED_WOO_UPDATE_MANAGER_PACKAGE_RECOVERED_ONLY",
        "authentication": "NOT_APPLICABLE_OFFLINE_NO_FRESH_AUTHENTICATED_ACCESS",
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "baseline": ref(BASELINE),
        "candidate_root": str(CANDIDATE),
        "component": "woo-update-manager",
        "recorded_version": recorded_version,
        "candidate_version": version.group(1).decode(),
        "recorded_files": len(expected),
        "recorded_bytes": sum(value["bytes"] for value in expected.values()),
        "exact_recorded_census_match": True,
        "retained": retained,
        "controls": controls,
        "other_candidates": json.loads(read(comparison))["comparisons"],
        "remaining_plugin_bodies": [
            "commercegurus-commercekit",
            "elementor-pro",
            "layout-grid",
            "big-sky",
        ],
        "limits": [
            "Exact recorded census only; source bytes were never executed, installed, activated or bootstrapped",
            "Older Elementor Pro 3.28.0 and cache bodies differ; they are not substitutes for installed bytes",
            "Managed loader hashes identify dereferenced readable bytes, not symlink text or link targets",
            "Managed loader/cache dependencies, effective private/service configuration and exact installed-stack runtime/isolated restore remain open",
            "Filename search covers its recorded roots/exclusions only; it is not an exhaustive content or absence proof",
            "Historical synthetic orphan ownership remains not established; original datadir untouched",
            "No SQL, configuration values, customer/order data, backup acquisition, services or external actions",
        ],
        "holds": "ALL_LIVE_CONVERSION_DEPLOYMENT_AND_EXISTING_HOLDS_REMAIN",
    }
    json_write(PUBLIC / "findings.json", findings)
    json_write(
        PUBLIC / "evidence-index.json",
        {
            "inputs": [ref(BASELINE), ref(discovery), ref(comparison), ref(Path(__file__))],
            "candidate_files": [ref(CANDIDATE / name) for name in sorted(files)],
            "results": [ref(PUBLIC / "findings.json"), *retained.values()],
        },
    )
    print(findings["status"])


if __name__ == "__main__":
    main()
