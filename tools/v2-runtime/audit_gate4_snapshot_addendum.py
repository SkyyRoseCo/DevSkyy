"""Offline snapshot addendum. Never bootstrap recovered code or access a site."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / ".artifacts/release-gates-20261019/installed-snapshot-addendum"
PUBLIC = ROOT / "tasks/release-gates-20261019/gate4-installed-snapshot-addendum"
HISTORICAL = Path("/Users/theceo/Documents/Codex/2026-10-02/task")
BASELINE = ROOT / ".artifacts/release-gates-20261019/installed-baseline-raw-r2.json"
CODE = HISTORICAL / "commerce-release/tools/production-runtime/search-tracking-privacy.php"
GIT_COMMIT = "a662e707d698a687d7d1d2efed3975b9aa7325b9"
GIT_PATH = "tools/production-runtime/search-tracking-privacy.php"


def pin(body: bytes) -> dict:
    return {"sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}


def no_symlinks(path: Path) -> None:
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("Symlink ancestry refused")


def read(path: Path) -> bytes:
    no_symlinks(path)
    if not path.is_file():
        raise ValueError("Nonregular or symlink input refused")
    return path.read_bytes()


def exact(body: bytes, expected: dict) -> None:
    if pin(body) != {key: expected[key] for key in ("sha256", "bytes")}:
        raise ValueError("Recorded body mismatch")


def write(path: Path, value: dict) -> None:
    no_symlinks(path)
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")


def main() -> None:
    if not __debug__:
        raise RuntimeError("Optimized audit refused")
    if PRIVATE.exists() or PUBLIC.exists():
        raise RuntimeError("Existing additive evidence refused")
    baseline_bytes = read(BASELINE)
    if (
        pin(baseline_bytes)["sha256"]
        != "f2379c9d4fef40a53552279b26b2fea6a1c34110d09aee174de6b1531de5258e"
    ):
        raise ValueError("Installed snapshot changed")
    baseline = json.loads(baseline_bytes)
    expected = baseline["code_hashes"]["mu-plugins/skyyrose-search-tracking-privacy.php"]
    body = read(CODE)
    exact(body, expected)
    git_body = subprocess.check_output(["git", "show", GIT_COMMIT + ":" + GIT_PATH], cwd=ROOT)
    exact(git_body, expected)
    if git_body != body:
        raise ValueError("Independent source copies differ")
    controls = []
    for label, altered in [
        ("changed-byte", body[:-1] + b"!"),
        ("truncated", body[:-1]),
        ("extra-byte", body + b"\n"),
    ]:
        try:
            exact(altered, expected)
        except ValueError:
            controls.append({"mutation": label, "status": "PASS_REFUSED_MODIFIED_CODE_COPY"})
        else:
            raise RuntimeError("Modified body accepted")
    metadata = {}
    inputs = {str(BASELINE): pin(baseline_bytes), str(CODE): pin(body)}
    for filename, digest in [
        (
            "backup-ui-coverage-20261019T202328Z.json",
            "1e5a48bde10979bd1e8881bd407e94b776fe86166f8873eec6d0b6b205e02682",
        ),
        (
            "backup-service-metadata-20261019T201353Z.json",
            "72a275de5607e3c05f2240588de56ba16ce334447897be026ab1d2b81e6734cc",
        ),
    ]:
        source = Path("/Users/theceo/Documents/Codex/2026-10-19/task") / filename
        raw = read(source)
        if pin(raw)["sha256"] != digest:
            raise ValueError("Retained metadata identity changed")
        value = json.loads(raw)
        if value["site"]["url"] != "https://skyyrose.co":
            raise ValueError("Retained metadata target differs")
        inputs[str(source)] = pin(raw)
        metadata[filename] = value
    ui = metadata["backup-ui-coverage-20261019T202328Z.json"]
    service = metadata["backup-service-metadata-20261019T201353Z.json"]
    if ui["site"]["expected_id"] != 238510894 or service["site"]["id"] != 238510894:
        raise ValueError("Retained metadata site ID differs")
    older = {}
    for filename in [
        "native-merchant-environment.json",
        "staging-runtime-final.json",
        "cache-source-paths.txt",
        "edge-cache-source-readonly.php.txt",
    ]:
        source = HISTORICAL / filename
        raw = read(source)
        inputs[str(source)] = pin(raw)
        if filename == "native-merchant-environment.json":
            value = json.loads(raw)
            older[filename] = {key: value[key] for key in ("home", "wp", "woo", "db")}
            older[filename]["disposition"] = "LOCAL_SQLITE_FIXTURE_NOT_INSTALLED_MARIADB_RUNTIME"
        elif filename == "staging-runtime-final.json":
            value = json.loads(raw)
            older[filename] = {
                key: value[key] for key in ("target", "stylesheet", "version", "utc", "count")
            }
            older[filename][
                "disposition"
            ] = "DATED_STAGING_THEME_FILE_CENSUS_NOT_INSTALLED_PRODUCTION_RUNTIME"
        else:
            older[filename] = {
                "pin": pin(raw),
                "disposition": "DATED_SOURCE_OR_PATH_LIST_NOT_EFFECTIVE_SERVICE_CONFIGURATION",
            }
    no_symlinks(PRIVATE)
    no_symlinks(PUBLIC)
    PRIVATE.mkdir(mode=0o700, parents=True)
    PUBLIC.mkdir(parents=True)
    retained = PRIVATE / "skyyrose-search-tracking-privacy.php"
    no_symlinks(retained)
    with retained.open("xb") as stream:
        stream.write(body)
    retained.chmod(0o600)
    findings = {
        "schema": "skyyrose.offline-installed-snapshot-addendum.v1",
        "status": "EXACT_RECORDED_PRIVACY_MU_BODY_RECOVERED_ONLY",
        "authentication": "NOT_APPLICABLE_OFFLINE_AUDIT_NO_FRESH_AUTHENTICATED_ACCESS",
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "recovered": {
            "snapshot_field": "code_hashes.mu-plugins/skyyrose-search-tracking-privacy.php",
            "expected": expected,
            "historical_path": str(CODE),
            "git_commit": GIT_COMMIT,
            "git_path": GIT_PATH,
            "retained_path": str(retained.relative_to(ROOT)),
            "retained_pin": pin(body),
            "executed": False,
        },
        "controls": controls,
        "older_runtime_and_config_leads": older,
        "existing_metadata_receipts": {
            "observed_ui_utc": ui["observed_utc"],
            "observed_service_utc": service["observed_utc"],
            "verification_this_run": "LOCAL_RECEIPT_HASH_AND_SCHEMA_ONLY_NOT_REAUTHENTICATED",
            "principal_scope": "UI_REPORTED_DISPLAY_SKYYROSECO_NOT_NUMERIC_ID_OR_CONNECTOR_IDENTITY",
            "site_id": 238510894,
            "selected_backup_label": ui["selected_point"]["displayed_date"],
            "backup_count": service["backups"]["number_of_backups"],
            "five_plugin_directory_names": ui["coverage_metadata"][
                "five_missing_plugin_directories_listed"
            ],
            "scope": "DIRECTORY_METADATA_ONLY_NO_RECOVERED_PACKAGE_BYTES_SNAPSHOT_ID_CHECKSUM_OR_RESTORE_PROOF",
        },
        "remaining": [
            "Five named plugin bodies and complete installed package census",
            "Managed MU loader and cache drop-in bodies/service bindings",
            "Private effective configuration, PHP extensions/limits/ini and database/cache settings",
            "PHP8.4.26/MariaDB11.8.9 full installed-stack execution and isolated restore proof",
            "Privacy collector completeness/storage/race/sanitation and policy evidence",
            "Private synthetic orphan insertion ownership remains not established; untouched, no live orphan inference",
        ],
        "limits": [
            "Matching source does not prove activation, coexistence, dependencies, effective hook behavior or privacy policy success",
            "No SQL/customer/order/configuration value read; no recovered PHP executed",
            "Previously incomplete offline search stays incomplete; no global absence claim",
            "Backup metadata receipts are observations from another scoped run, not fresh authenticated actions here",
            "All prior frozen evidence retains its original verdict; local HPOS/CPT proof does not qualify the installed stack",
        ],
        "holds": [
            "Live conversion/sync/configuration/credentials/orders/payments/backup/export/restore",
            "Push/merge/deploy/activation/publication/cutover",
            "Paid/provider/media/GLB promotion",
        ],
    }
    write(PUBLIC / "findings.json", findings)
    write(PRIVATE / "input-index.json", inputs)
    write(
        PUBLIC / "evidence-index.json",
        {
            **inputs,
            str(retained): pin(read(retained)),
            str(PUBLIC / "findings.json"): pin(read(PUBLIC / "findings.json")),
            str(PRIVATE / "input-index.json"): pin(read(PRIVATE / "input-index.json")),
            str(Path(__file__).resolve()): pin(read(Path(__file__).resolve())),
        },
    )
    print(findings["status"])


if __name__ == "__main__":
    main()
