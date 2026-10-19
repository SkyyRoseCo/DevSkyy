"""Compare retained offline code to the dated installed census; never bootstrap WP."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / ".artifacts/release-gates-20261019/installed-evidence"
OUT = ROOT / "tasks/release-gates-20261019/gate4-installed-evidence"
BASELINE = ROOT / ".artifacts/release-gates-20261019/installed-baseline-raw-r2.json"
ACCEPTED = "481b1406b376ca302f270f17663d641d10ada04d"
AJAX_COMMIT = "ef683c7941ff5a88b8a48ede1d24fba7335139ed"


def sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def no_symlinks(path: Path) -> None:
    if any(item.is_symlink() for item in (path, *path.parents)):
        raise ValueError("Symlink path ancestor refused")


def pin(path: Path) -> dict:
    no_symlinks(path)
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"sha256": digest, "bytes": path.stat().st_size}


def load(path: Path):
    no_symlinks(path)
    return json.loads(path.read_text())


def write(path: Path, data) -> None:
    no_symlinks(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def retain(path: Path, body: bytes) -> None:
    """Only create owned candidates, or verify an identical earlier retained copy."""
    no_symlinks(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("Symlink destination refused")
    if path.exists():
        if path.read_bytes() != body:
            raise ValueError("Existing retained candidate differs")
    else:
        with path.open("xb") as stream:
            stream.write(body)


def compare(slug: str, files: dict[str, bytes], baseline: dict) -> dict:
    prefix = "plugins/" + slug + "/"
    expected = {k[len(prefix) :]: v for k, v in baseline.items() if k.startswith(prefix)}
    if not expected:
        raise ValueError("No recorded component census")
    actual = {k: {"sha256": sha(v), "bytes": len(v)} for k, v in files.items()}
    different = [
        k
        for k in expected.keys() & actual.keys()
        if any(actual[k][field] != expected[k][field] for field in ["sha256", "bytes"])
    ]
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    return {
        "recorded_files": len(expected),
        "candidate_files": len(actual),
        "missing": missing,
        "different": sorted(different),
        "unrecorded_extra": extra,
        "exact_recorded_census_match": not missing and not different and not extra,
        "files": actual,
        "scope": "Exact recorded census only; installed collector managed/symlink exclusions remain",
    }


def archive_files(path: Path, slug: str) -> dict[str, bytes]:
    no_symlinks(path)
    if path.is_symlink():
        raise ValueError("Archive symlink refused")
    files = {}
    seen = set()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if len(infos) > 512 or sum(info.file_size for info in infos) > 64 * 1024 * 1024:
            raise ValueError("Archive aggregate member/expanded-byte bound exceeded")
        for info in infos:
            raw = info.filename.rstrip("/")
            name = PurePosixPath(raw)
            if (
                name.is_absolute()
                or ".." in name.parts
                or "\\" in raw
                or str(name) != raw
                or raw in seen
                or stat.S_ISLNK(info.external_attr >> 16)
            ):
                raise ValueError("Ambiguous/unsafe archive member refused")
            seen.add(raw)
            if info.is_dir():
                continue
            if not raw.startswith(slug + "/"):
                raise ValueError("Unexpected component root")
            if info.file_size > 32 * 1024 * 1024 or info.flag_bits & 1:
                raise ValueError("Oversize/encrypted target member refused")
            files[raw[len(slug) + 1 :]] = archive.read(info)
    return files


def main() -> None:
    baseline_pin = pin(BASELINE)
    if baseline_pin["sha256"] != "f2379c9d4fef40a53552279b26b2fea6a1c34110d09aee174de6b1531de5258e":
        raise ValueError("Installed census identity changed")
    baseline = load(BASELINE)
    if baseline["site"] != "https://skyyrose.co":
        raise ValueError("Snapshot target mismatch")
    inputs = {str(BASELINE.relative_to(ROOT)): baseline_pin}
    recovered = []
    for slug, archive_name in [
        ("skyyrose-immersive", "skyyrose-immersive-1.0.0.zip"),
        ("skyyrose-scene-installer", "skyyrose-scene-installer.zip"),
    ]:
        archive = Path("/Users/theceo/Downloads") / archive_name
        directory = archive.parent / slug
        if directory.is_symlink():
            raise ValueError("Component directory symlink refused")
        files = archive_files(archive, slug)
        directory_files = {}
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise ValueError("Component symlink refused")
            if path.is_file():
                directory_files[str(path.relative_to(directory))] = path.read_bytes()
        if files != directory_files:
            raise ValueError("ZIP and directory candidate disagree")
        comparison = compare(slug, files, baseline["code_hashes"])
        if not comparison["exact_recorded_census_match"]:
            raise ValueError("Located candidate differs from recorded census")
        inputs[str(archive)] = pin(archive)
        retain(PRIVATE / "recovered-archives" / archive_name, archive.read_bytes())
        for name, body in files.items():
            retain(PRIVATE / "recovered-code" / slug / name, body)
        recovered.append({"component": slug, "archive": str(archive), **comparison})

    ajax_path = "wordpress/mu-plugins/skyyrose-ally-ajax-guard.php"
    body = subprocess.check_output(["git", "show", AJAX_COMMIT + ":" + ajax_path], cwd=ROOT)
    recorded_ajax = baseline["code_hashes"]["mu-plugins/skyyrose-ally-ajax-guard.php"]
    if sha(body) != recorded_ajax["sha256"] or len(body) != recorded_ajax["bytes"]:
        raise ValueError("Historical AJAX source does not match installed census")
    retain(PRIVATE / "recovered-code/mu-plugins/skyyrose-ally-ajax-guard.php", body)
    ajax = {
        "component": "skyyrose-ally-ajax-guard.php",
        "git_commit": AJAX_COMMIT,
        "git_path": ajax_path,
        "sha256": sha(body),
        "bytes": len(body),
        "status": "EXACT_RECORDED_FILE_RECOVERED_CURRENT_SOURCE_UNCHANGED",
    }

    old_root = Path("/Users/theceo/Documents/studio-backup-skyyroseco-2025-07-15-15-14-27 3")
    old_meta = old_root / "meta.json"
    studio = load(old_meta)
    inputs[str(old_meta)] = pin(old_meta)
    historical = {
        "studio": {
            "site": studio["siteUrl"],
            "php_version": studio["phpVersion"],
            "wp_version": studio["wordpressVersion"],
            "status": "OLDER_LOCAL_SITE_NOT_INSTALLED_RUNTIME_EVIDENCE",
            "configuration_values_or_sql_read": False,
        }
    }
    old_task = Path("/Users/theceo/Documents/Codex/2026-10-02/task")
    cache_path = old_task / "cache-capability-readonly.json"
    cache = load(cache_path)
    if cache["home"] != baseline["site"]:
        raise ValueError("Historical cache receipt reports another site")
    functions = [x["name"] for x in cache["functions"]]
    if not all(re.fullmatch(r"[A-Za-z_\\][A-Za-z_0-9\\]*", name) for name in functions):
        raise ValueError("Unexpected function-name value")
    inputs[str(cache_path)] = pin(cache_path)
    historical["cache"] = {
        "reported_site": cache["home"],
        "retained_task_date": "2026-10-02",
        "functions": functions,
        "active_plugin_count": len(cache["plugin_names"]),
        "status": "DATED_RECORDED_CAPABILITY_ONLY_NOT_CACHE_SERVICE_CONFIGURATION_OR_EXECUTION",
        "authentication": "NOT_REAUTHENTICATED_OFFLINE_RECEIPT",
    }
    native_path = ROOT / ".artifacts/release-gates-20261019/installed-native-storage-readonly.txt"
    native = json.loads(native_path.read_text().removeprefix("SR_READONLY_BASELINE="))
    allowed_native = [
        "site",
        "wp",
        "woo",
        "php",
        "wpdb_class",
        "hpos_authority",
        "native_order_store",
        "orders_pending_sync",
    ]
    if native["site"] != baseline["site"] or set(native) != set(allowed_native):
        raise ValueError("Native receipt target/schema mismatch")
    inputs[str(native_path.relative_to(ROOT))] = pin(native_path)
    prior_path = (
        ROOT / "tasks/release-gates-20261019/gate4-local/evidence/installed-component-coverage.json"
    )
    prior = load(prior_path)
    inputs[str(prior_path.relative_to(ROOT))] = pin(prior_path)
    still_missing = [
        x["plugin"]
        for x in prior["plugins"]
        if x["available_files"] == 0
        and x["plugin"].split("/")[0] not in {x["component"] for x in recovered}
    ]
    private_index = {}
    for name in [
        "discovery.json",
        "secondary-discovery.json",
        "archive-target-search.json",
        "archive-source-index.json",
        "ajax-git-history-search.json",
        "search-coverage-limits.json",
    ]:
        path = PRIVATE / name
        inputs[str(path.relative_to(ROOT))] = pin(path)
    for path in sorted((PRIVATE / "recovered-code").rglob("*")):
        if path.is_file():
            private_index[str(path.relative_to(ROOT))] = pin(path)
    for path in sorted((PRIVATE / "recovered-archives").iterdir()):
        private_index[str(path.relative_to(ROOT))] = pin(path)
    write(OUT / "retained-code-index.json", private_index)
    write(
        OUT / "snapshot-findings.json",
        {
            "schema": "skyyrose.offline-installed-evidence.v1",
            "status": "RECOVERED_RECORDED_CODE_COVERAGE_ONLY",
            "authentication": "NOT_APPLICABLE_OFFLINE_COMPARISON; historical authenticated snapshot retained, no fresh sign-in",
            "source_head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "source_pin": pin(Path(__file__)),
            "prior_accepted_packet": ACCEPTED,
            "baseline": {
                k: baseline[k]
                for k in [
                    "site",
                    "observed_utc",
                    "classification",
                    "wp_version",
                    "php_version",
                    "db_version",
                    "storage_options",
                ]
            },
            "native_storage_receipt": native,
            "native_storage_note": "pending orders is a native runtime backlog observation, not the data-sync option; null option and pending=true remain distinct",
            "recovered_plugins": recovered,
            "recovered_ajax_guard": ajax,
            "historical_receipts": historical,
            "inputs": inputs,
            "limits": [
                "No plugin/bootstrap/service/DB execution, fresh authentication, live query or secret/customer/order-data read",
                "Exact component-relative file matches cover the recorded census only; managed/symlink/global completeness exclusions remain",
                "Matching candidates from separate local/Git sources do not prove coexistence, activation, configuration or operational behavior",
                "Existing closed fixture profiles were not modified or rerun; recovered bytes are inert private candidates",
                "Broad content search was incomplete on inaccessible offline snapshot files; no universal absence claim",
            ],
        },
    )
    write(
        OUT / "remaining-installed-gaps.json",
        {
            "schema": "skyyrose.installed-evidence-gaps.v1",
            "status": "INSTALLED_ENVIRONMENT_AND_RELEASE_HOLD",
            "prior_accepted_packet": ACCEPTED,
            "closed_evidence_gaps": [
                "Two previously unavailable plugin bodies now exact-match28recordedfiles",
                "Historical AJAX guard exact installed1566byte source recovered",
            ],
            "remaining_unavailable_components": still_missing,
            "remaining": [
                "Full privacy MU body, managed MU loaders and two cache drop-in bodies not recovered in completed bounded searches",
                "Full managed plugin file census and exact readable installed package trees remain absent; matching public versions are insufficient",
                "Private installed service/config bindings, effective PHP limits/extensions/ini, DB settings and object/edge cache service configuration not exported",
                "PHP8.4.26 and MariaDB11.8.9 runtime execution parity remains unqualified; older local Studio backup is PHP8.3/WP6.8.2",
                "Full installed33plugin/MU/drop-in synthetic profile not executed; earlier available full-profile timeout remains unresolved",
                "No current installed activation/configuration/runtime success follows from offline evidence",
            ],
            "separate_open_gates": [
                "Historical orphan1292 insertion ownership unestablished; original datadir never started, child unadopted/undeleted",
                "Populated native synchronization and actual V1 payment qualification remain separate authorized local work",
                "Original live privacy FAIL/eightUNKNOWN preserved; accepted loopback-only collector is not a qualified real-site successor",
                "Installed backup/restore, full immersive acceptance, target-scoped media authority and final production/release authority remain separate",
            ],
            "holds": [
                "Live conversion/sync/config/credentials/orders/payments/backup/restore",
                "Push/merge/deploy/activation/publication/cutover",
                "Paid/provider/media generation/GLB promotion",
            ],
            "owner_decision_needed_for_this_offline_evidence_work": False,
        },
    )
    print("PASS_OFFLINE_RECORDED_CODE_RECOVERY_28_PLUGIN_FILES_PLUS_AJAX_GUARD")


if __name__ == "__main__":
    main()
