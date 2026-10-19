"""Complete cold backup and bounded row-binlog reconciliation on synthetic clones.

This executable never accepts a remote target, credentials, arbitrary database,
or production path. All raw SQL/configuration/archive bytes stay private.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import time

if not __debug__:
    raise RuntimeError("Optimized execution cannot verify recovery")

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / ".artifacts/release-gates-20261019/gate4-local"
OUT = ROOT / "tasks/release-gates-20261019/gate4-local/evidence"
BACKUP = PRIVATE / "backup"
RESTORE = PRIVATE / "restore"
SOURCE_SOCKET = "/tmp/sr-gate4-01a0f768.sock"
RESTORE_SOCKET = "/tmp/sr-gate4-restore-01a0f768.sock"
MYSQL = "/opt/homebrew/bin/mariadb"
DAEMON = "/opt/homebrew/opt/mariadb/bin/mariadbd"
BINLOG = "/opt/homebrew/bin/mariadb-binlog"
DB = "sr_release_fixture"
RUNTIME = json.loads((PRIVATE / "runtime-profile.json").read_text())
REPORT: dict = {"status": "INCOMPLETE", "authentication": "NOT_APPLICABLE", "steps": [], "limits": ["Synthetic MariaDB13 private profile only; no production backup/restore or full installed-stack parity", "New binlog instrumentation cannot establish historical orphan ownership"]}
RUN_ID = str(time.time_ns())
SOURCE_CASE = PRIVATE / ("recovery-" + RUN_ID + ".json")
RUNS = OUT / "restore-runs"
RUNS.mkdir(exist_ok=True)
PROCESSES: list[subprocess.Popen] = []
SEQUENCE = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, data: dict) -> None:
    with path.open("w") as handle:
        handle.write(json.dumps(data, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def record(step: str, **fields: object) -> None:
    REPORT["steps"].append({"step": step, **fields})
    write_json(RUNS / (RUN_ID + ".json"), REPORT)
    write_json(OUT / "restore-results.json", REPORT)


def command(args: list[str], data: bytes | None = None, timeout: int = 120, env: dict | None = None) -> bytes:
    global SEQUENCE
    SEQUENCE += 1
    path = OUT / f"restore-{RUN_ID}-command-{SEQUENCE}.txt"
    try:
        result = subprocess.run(args, input=data, capture_output=True, timeout=timeout, check=False, env=env)
    except subprocess.TimeoutExpired as error:
        path.write_bytes((error.stdout or b"") + (error.stderr or b""))
        record("COMMAND_TIMEOUT", receipt=path.name, seconds=timeout, sha256=sha(path.read_bytes()))
        raise
    except OSError as error:
        path.write_text(type(error).__name__ + ": " + str(error))
        record("COMMAND_LAUNCH_FAILED", receipt=path.name, sha256=sha(path.read_bytes()))
        raise
    path.write_bytes(result.stdout + result.stderr)
    assert result.returncode == 0, (path.name, result.returncode)
    return result.stdout


def sql(socket: str, query: str, database: bool = True) -> bytes:
    assert socket in [SOURCE_SOCKET, RESTORE_SOCKET]
    args = [MYSQL, "--no-defaults", "--socket=" + socket, "-uroot", "--batch", "--skip-column-names", "--default-character-set=utf8mb4"]
    if database:
        args.append(DB)
    return command(args, ("SET time_zone='+00:00';\n" + query).encode())


def inventory(folder: Path) -> dict:
    result = {}
    for path in sorted(folder.rglob("*")):
        assert not path.is_symlink(), f"Unqualified symlink: {path.name}"
        if path.is_file():
            result[str(path.relative_to(folder))] = {"sha256": sha(path.read_bytes()), "bytes": path.stat().st_size, "mode": path.stat().st_mode & 0o777}
    return result


def state(socket: str) -> dict:
    identity = sql(socket, "SELECT @@datadir,@@socket,@@skip_networking,@@event_scheduler,VERSION();", False).decode().strip().split("\t")
    expected = PRIVATE / "mysql" if socket == SOURCE_SOCKET else RESTORE / "mysql"
    assert Path(identity[0]).resolve() == expected.resolve() and identity[1] == socket and identity[2] == "1" and identity[3] == "OFF"
    assert sql(socket, "SELECT option_value FROM wp_options WHERE option_name='home';").strip() == b"http://127.0.0.1:18362"
    names = sql(socket, "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() ORDER BY TABLE_NAME;").decode().splitlines()
    tables = {}
    for name in names:
        assert re.fullmatch(r"[A-Za-z0-9_]+", name)
        columns = sql(socket, f"SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='{name}' ORDER BY ORDINAL_POSITION;").decode().splitlines()
        assert all(re.fullmatch(r"[A-Za-z0-9_]+", column) for column in columns)
        schema = sql(socket, f"SHOW CREATE TABLE `{name}`;")
        encoded = "CONCAT_WS(':'," + ",".join(f"IF(`{column}` IS NULL,'N',CONCAT('V',HEX(CAST(`{column}` AS BINARY))))" for column in columns) + ")"
        rows = sql(socket, f"SELECT {encoded} AS encoded_row FROM `{name}` ORDER BY BINARY encoded_row;")
        info = sql(socket, f"SELECT ENGINE,COALESCE(AUTO_INCREMENT,0) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='{name}';").decode().strip().split("\t")
        assert info[0] == "InnoDB", (name, info[0])
        tables[name] = {"schema_sha256": sha(schema), "schema_without_highwater_sha256": sha(re.sub(rb"AUTO_INCREMENT=\d+", b"AUTO_INCREMENT=REVIEWED", schema)), "data_sha256": sha(rows), "row_count": int(sql(socket, f"SELECT COUNT(*) FROM `{name}`;").strip()), "auto_increment": int(info[1])}
    programmable = sql(socket, "SELECT TRIGGER_NAME,ACTION_STATEMENT FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE(); SELECT EVENT_NAME,EVENT_DEFINITION,STATUS FROM information_schema.EVENTS WHERE EVENT_SCHEMA=DATABASE(); SELECT ROUTINE_NAME,ROUTINE_DEFINITION FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=DATABASE();")
    assert not programmable, "Programmable database objects require separate qualification"
    return {"tables": tables, "programmable_sha256": sha(programmable), "identity": identity}


def app_equal(left: dict, right: dict) -> bool:
    return left["tables"] == right["tables"] and left["programmable_sha256"] == right["programmable_sha256"]


def stop(socket: str) -> None:
    observed = sql(socket, "SELECT @@datadir,@@socket;", False).decode().strip().split("\t")
    expected = PRIVATE / "mysql" if socket == SOURCE_SOCKET else RESTORE / "mysql"
    assert Path(observed[0]).resolve() == expected.resolve() and observed[1] == socket
    command(["/opt/homebrew/bin/mariadb-admin", "--no-defaults", "--socket=" + socket, "-uroot", "shutdown"])


def start(socket: str, datadir: Path, logging: bool) -> None:
    resolved = "/private" + socket
    profile = f'(version 1)(allow default)(deny network*)(allow network-bind (local unix-socket (literal "{resolved}")))(allow network-inbound (local unix-socket (literal "{resolved}")))'
    log = datadir.parent / ("server-source.log" if logging else "server-restore.log")
    args = ["/usr/bin/sandbox-exec", "-p", profile, DAEMON, "--no-defaults", "--datadir=" + str(datadir), "--socket=" + socket, "--pid-file=" + str(datadir.parent / ("source.pid" if logging else "restore.pid")), "--skip-networking", "--event-scheduler=OFF", "--log-error=" + str(log)]
    if logging:
        logs = PRIVATE / "binlogs"
        logs.mkdir(exist_ok=True)
        args += ["--server-id=42768", "--log-bin=" + str(logs / "source"), "--binlog-format=ROW", "--binlog-row-image=FULL"]
    else:
        args += ["--skip-log-bin", "--server-id=42769"]
    with log.open("ab") as output:
        child = subprocess.Popen(args, stdout=output, stderr=output)
    PROCESSES.append(child)
    deadline = time.monotonic() + 30
    while True:
        assert child.poll() is None, "Private DB failed to start"
        probe = subprocess.run(["/opt/homebrew/bin/mariadb-admin", "--no-defaults", "--socket=" + socket, "-uroot", "ping"], capture_output=True, check=False)
        if probe.returncode == 0:
            break
        assert time.monotonic() < deadline
        time.sleep(.1)


def native(mode: str, restore: bool = False) -> dict:
    socket = RESTORE_SOCKET if restore else SOURCE_SOCKET
    site = RESTORE / "wordpress" if restore else PRIVATE / "wordpress"
    profile = f'(version 1)(allow default)(deny network*)(allow network-outbound (remote unix-socket (literal "/private{socket}")))'
    worker = RESTORE / "control/gate4-recovery-fixture.php" if restore else ROOT / "tools/v2-runtime/gate4-recovery-fixture.php"
    if restore:
        assert sha(worker.read_bytes()) == MANIFEST["control_files"]["gate4-recovery-fixture.php"]["sha256"]
    raw = command(["/usr/bin/sandbox-exec", "-p", profile, "php", *RUNTIME["php_prefix"], "/opt/homebrew/bin/wp", "--path=" + str(site), "--skip-plugins=" + ",".join(RUNTIME["wp_skip_plugins"]), "eval-file", str(worker), mode], env={**os.environ, "SR_RECOVERY_CASE": "recovery-case.json" if restore else SOURCE_CASE.name})
    result = json.loads(raw)
    assert result["ok"]
    return result


def archive(folder: Path, path: Path) -> dict:
    before = inventory(folder)
    with tarfile.open(path, "w:gz", compresslevel=1) as output:
        output.add(folder, arcname=folder.name)
    assert before == inventory(folder), "Backup source changed while archiving"
    return before


def unpack(path: Path, destination: Path) -> None:
    assert sha(path.read_bytes()) == MANIFEST["archives"][path.name]
    with tarfile.open(path, "r:gz") as source:
        assert all(member.isfile() or member.isdir() for member in source.getmembers())
        source.extractall(destination, filter="data")
        # Python's data filter strips group-write; restore archived permission
        # bits only after safe-path extraction, never ownership or special bits.
        for member in source.getmembers():
            target = destination / member.name
            assert target.resolve().is_relative_to(destination.resolve())
            target.chmod(member.mode & 0o777)


def reset_restore(label: str) -> None:
    if (RESTORE / "mysql").exists():
        if subprocess.run(["/opt/homebrew/bin/mariadb-admin", "--no-defaults", "--socket=" + RESTORE_SOCKET, "-uroot", "ping"], capture_output=True, check=False).returncode == 0:
            stop(RESTORE_SOCKET)
        (RESTORE / "mysql").rename(RESTORE / ("mysql-retained-" + label))
    if (RESTORE / "wordpress").exists():
        # Only disposable materialization; immutable archive remains complete.
        assert (RESTORE / "fixture-owner.json").is_file()
        write_json(RESTORE / ("site-before-reset-" + label + ".json"), inventory(RESTORE / "wordpress"))
        shutil.rmtree(RESTORE / "wordpress")
    unpack(BACKUP / "mysql.tar.gz", RESTORE)
    unpack(BACKUP / "wordpress.tar.gz", RESTORE)
    assert inventory(RESTORE / "mysql") == MANIFEST["mysql_files"]
    assert inventory(RESTORE / "wordpress") == MANIFEST["site_files"]
    if (RESTORE / "state").exists():
        shutil.rmtree(RESTORE / "state")
    shutil.copytree(BACKUP / "state", RESTORE / "state")
    assert inventory(RESTORE / "state") == MANIFEST["state_files"]
    if (RESTORE / "control").exists():
        shutil.rmtree(RESTORE / "control")
    shutil.copytree(BACKUP / "control", RESTORE / "control")
    assert inventory(RESTORE / "control") == MANIFEST["control_files"]
    config = RESTORE / "wordpress/wp-config.php"
    before = config.read_bytes()
    assert before.count(SOURCE_SOCKET.encode()) == 1
    config.write_bytes(before.replace(SOURCE_SOCKET.encode(), RESTORE_SOCKET.encode()))
    config.chmod(0o600)
    start(RESTORE_SOCKET, RESTORE / "mysql", False)
    assert app_equal(state(RESTORE_SOCKET), MANIFEST["database"])
    record("RESTORED_PRE_BOOT", attempt=label, physical_files_verified=True, application_tables_verified=len(MANIFEST["database"]["tables"]), config_overlay="Only synthetic source socket replaced with isolated restore socket")


def expected_site(files: dict) -> dict:
    result = dict(files)
    with tarfile.open(BACKUP / "wordpress.tar.gz", "r:gz") as archive_file:
        member = archive_file.extractfile("wordpress/wp-config.php")
        assert member is not None
        config = member.read().replace(SOURCE_SOCKET.encode(), RESTORE_SOCKET.encode())
    result["wp-config.php"] = {**files["wp-config.php"], "sha256": sha(config), "bytes": len(config), "mode": 0o600}
    return result


def reconcile_precondition() -> None:
    assert app_equal(state(RESTORE_SOCKET), MANIFEST["database"]), "Unreviewed target DB preimage; never replay onto partial/colliding/newer state"
    assert inventory(RESTORE / "wordpress") == expected_site(MANIFEST["site_files"]), "Unreviewed filesystem preimage"
    assert inventory(RESTORE / "state") == MANIFEST["state_files"], "Unreviewed operational state preimage"
    assert inventory(RESTORE / "control") == MANIFEST["control_files"], "Unreviewed control code preimage"


def replay(stop_position: int) -> None:
    assert sha((BACKUP / "delta/source.bin").read_bytes()) == DELTA["sha256"]
    executable = command([BINLOG, "--start-position=" + str(DELTA["start_position"]), "--stop-position=" + str(stop_position), "--database=" + DB, str(BACKUP / "delta/source.bin")])
    command([MYSQL, "--no-defaults", "--socket=" + RESTORE_SOCKET, "-uroot", "--binary-mode", DB], executable)


def verify_checkpoint() -> dict:
    checkpoint = json.loads((RESTORE / "checkpoint.json").read_text())
    assert checkpoint["available"] is True
    assert sha((BACKUP / "delta/manifest.json").read_bytes()) == checkpoint["delta_sha256"]
    assert app_equal(state(RESTORE_SOCKET), checkpoint["database"])
    assert inventory(RESTORE / "wordpress") == checkpoint["site"]
    assert inventory(RESTORE / "state") == checkpoint["state"]
    assert inventory(RESTORE / "control") == checkpoint["control"]
    return {"status": "NOOP_EXACT_CHECKPOINT_AND_POSTIMAGE", "database_replay_performed": False}


def main() -> None:
    global MANIFEST, DELTA
    lock = PRIVATE / ".sr-gate4-run-lock"
    lock.mkdir()
    successful = False
    try:
        BACKUP.mkdir(exist_ok=False)
        (BACKUP / "state").mkdir()
        (BACKUP / "control").mkdir()
        (BACKUP / "delta/files").mkdir(parents=True)
        RESTORE.mkdir(exist_ok=False)
        write_json(RESTORE / "fixture-owner.json", {"owner": "Integration", "private_only": True})
        if subprocess.run(["/opt/homebrew/bin/mariadb-admin", "--no-defaults", "--socket=" + SOURCE_SOCKET, "-uroot", "ping"], capture_output=True, check=False).returncode == 0:
            state(SOURCE_SOCKET)  # Verify identity before stopping only this clone.
            stop(SOURCE_SOCKET)
        start(SOURCE_SOCKET, PRIVATE / "mysql", True)
        seeded = native("seed")
        assert native("pending-control")["pending_refused"] is True
        record("UNPAID_NATIVE_ORDER_CONTROL_REFUSED", order_id=seeded["case"]["existing_order_id"])
        shutil.copyfile(SOURCE_CASE, BACKUP / "state/recovery-case.json")
        shutil.copyfile(Path(str(SOURCE_CASE) + ".before.json"), BACKUP / "state/native-before.json")
        write_json(BACKUP / "state/runtime-profile.json", RUNTIME)
        for name in ["gate4-recovery-fixture.php", "gate4_restore_local.py", "variation-migration-core-next.php", "variation-migration-core.php"]:
            shutil.copyfile(ROOT / "tools/v2-runtime" / name, BACKUP / "control" / name)
        baseline = state(SOURCE_SOCKET)
        stop(SOURCE_SOCKET)
        database_files = archive(PRIVATE / "mysql", BACKUP / "mysql.tar.gz")
        site_files = archive(PRIVATE / "wordpress", BACKUP / "wordpress.tar.gz")
        for folder in ["process", "owned-repair"]:
            shutil.copytree(ROOT / ".artifacts/release-gates-20261019/runtime-official" / folder, BACKUP / "state" / folder)
        shutil.copytree(PRIVATE, BACKUP / "state/gate4-cases", ignore=lambda directory, names: [name for name in names if Path(directory) == PRIVATE and name in ["backup", "restore", "mysql", "wordpress", "binlogs", "plugin-archives"]])
        MANIFEST = {"schema": "skyyrose.complete-private-cold-backup.v1", "database": baseline, "mysql_files": database_files, "site_files": site_files, "state_files": inventory(BACKUP / "state"), "control_files": inventory(BACKUP / "control"), "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(), "source_pins": {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in [Path(__file__), ROOT / "tools/v2-runtime/gate4-recovery-fixture.php", ROOT / "tools/v2-runtime/variation-migration-core-next.php"]}, "archives": {name: sha((BACKUP / name).read_bytes()) for name in ["mysql.tar.gz", "wordpress.tar.gz"]}, "coverage": "Complete selected synthetic site/code/database/config/uploads/MU/state, all acquired inactive code included; no claim of installed/production completeness"}
        write_json(BACKUP / "manifest.json", MANIFEST)
        record("COMPLETE_COLD_BACKUP", manifest_sha256=sha((BACKUP / "manifest.json").read_bytes()), db_files=len(database_files), site_files=len(site_files), tables=len(baseline["tables"]))
        start(SOURCE_SOCKET, PRIVATE / "mysql", True)
        assert app_equal(state(SOURCE_SOCKET), baseline), "Unexpected app mutation across cold restart"
        start_boundary = sql(SOURCE_SOCKET, "SHOW MASTER STATUS;", False).decode().splitlines()[0].split("\t")
        after = native("post-backup")
        before_rollback = state(SOURCE_SOCKET)
        isolation = PRIVATE / "wordpress/wp-content/mu-plugins/00-gate4-isolation.php"
        original_code = isolation.read_bytes()
        isolation.write_bytes(original_code + b"\n/* Synthetic reversible code candidate. */\n")
        candidate_hash = sha(isolation.read_bytes())
        assert native("inspect")["snapshot"] == after["snapshot"]
        rollback_database = state(SOURCE_SOCKET)
        # Restore the selected changed code bytes from the immutable archive.
        with tarfile.open(BACKUP / "wordpress.tar.gz", "r:gz") as archived:
            restored_member = archived.extractfile("wordpress/wp-content/mu-plugins/00-gate4-isolation.php")
            assert restored_member is not None
            isolation.write_bytes(restored_member.read())
        assert isolation.read_bytes() == original_code
        assert app_equal(state(SOURCE_SOCKET), rollback_database)
        assert native("inspect")["snapshot"] == after["snapshot"]
        endpoint = state(SOURCE_SOCKET)
        after_files = inventory(PRIVATE / "wordpress")
        assert not (set(site_files) - set(after_files)), "Unreviewed filesystem deletion"
        filesystem_delta = {}
        for name, details in after_files.items():
            if site_files.get(name) != details:
                destination = BACKUP / "delta/files" / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(PRIVATE / "wordpress" / name, destination)
                filesystem_delta[name] = {"before": site_files.get(name), "after": details}
        end_boundary = sql(SOURCE_SOCKET, "SHOW MASTER STATUS;", False).decode().splitlines()[0].split("\t")
        assert start_boundary[0] == end_boundary[0] and re.fullmatch(r"source\.\d+", start_boundary[0])
        source_binlog = PRIVATE / "binlogs" / start_boundary[0]
        shutil.copyfile(source_binlog, BACKUP / "delta/source.bin")
        shutil.copyfile(SOURCE_CASE, BACKUP / "delta/recovery-case.json")
        DELTA = {"file": start_boundary[0], "start_position": int(start_boundary[1]), "end_position": int(end_boundary[1]), "sha256": sha((BACKUP / "delta/source.bin").read_bytes()), "endpoint": endpoint, "site_endpoint": after_files, "filesystem_delta": filesystem_delta, "native_endpoint": after["snapshot"], "state_delta": {"recovery-case.json": sha((BACKUP / "delta/recovery-case.json").read_bytes())}}
        inspection = command([BINLOG, "--base64-output=DECODE-ROWS", "-vv", "--start-position=" + str(DELTA["start_position"]), "--stop-position=" + str(DELTA["end_position"]), str(BACKUP / "delta/source.bin")])
        (BACKUP / "delta/inspection.txt").write_bytes(inspection)
        assert not re.search(rb"^\s*(?:CREATE|ALTER|DROP|GRANT|REVOKE|LOAD)\s", inspection, re.M | re.I), "Unreviewed DDL/privilege/file operation"
        mapped = re.findall(rb"Table_map: `([^`]+)`\.`([^`]+)`", inspection)
        assert mapped and all(db.decode() == DB and table.decode() in endpoint["tables"] for db, table in mapped)
        commits = [int(position) for position in re.findall(rb"end_log_pos (\d+)[^\n]*Xid", inspection)]
        assert commits and DELTA["start_position"] < commits[0] < DELTA["end_position"]
        write_json(BACKUP / "delta/manifest.json", DELTA)
        updated_case = json.loads(SOURCE_CASE.read_text())
        assert updated_case["post_backup_order_id"] not in seeded["case"]["orders"]
        record("POST_BACKUP_NATIVE_AND_CODE_ROLLBACK", existing_order=seeded["case"]["existing_order_id"], new_order=updated_case["post_backup_order_id"], stock=after["snapshot"]["stock"], native_snapshot_sha256=sha(json.dumps(after["snapshot"], sort_keys=True).encode()), delta_sha256=sha((BACKUP / "delta/manifest.json").read_bytes()), filesystem_delta_files=len(filesystem_delta), rollback_scope="Compatible comment-only code candidate booted, archive bytes restored, current DB retained; no arbitrary-version compatibility claim", candidate_sha256=candidate_hash, restored_sha256=sha(original_code), candidate_boot_changed_tables=[name for name in before_rollback["tables"] if before_rollback["tables"][name] != rollback_database["tables"][name]])
        reset_restore("native-baseline")
        assert native("inspect-backup", True)["snapshot"] == seeded["snapshot"]
        record("NATIVE_BASELINE_RESTORE_VERIFIED", baseline_native_ids_and_promises=True)
        reset_restore("after-native-probe")
        reconcile_precondition()
        replay(commits[0])
        assert not app_equal(state(RESTORE_SOCKET), baseline)
        try:
            reconcile_precondition()
        except AssertionError:
            record("INTERRUPTED_REPLAY_REFUSED", target_available=False, complete_transaction_boundary=commits[0])
        else:
            raise AssertionError("Partial replay was incorrectly resumable")
        reset_restore("after-partial")
        case = json.loads(SOURCE_CASE.read_text())
        new_id = int(case["post_backup_order_id"])
        assert sql(RESTORE_SOCKET, f"SELECT COUNT(*) FROM wp_posts WHERE ID={new_id};").strip() == b"0"
        columns = sql(RESTORE_SOCKET, "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='wp_posts' ORDER BY ORDINAL_POSITION;").decode().splitlines()
        assert all(re.fullmatch(r"[A-Za-z0-9_]+", column) for column in columns)
        selected = [str(new_id) if column == "ID" else "'gate4_collision'" if column == "post_type" else f"`{column}`" for column in columns]
        sql(RESTORE_SOCKET, "INSERT INTO wp_posts (" + ",".join(f"`{column}`" for column in columns) + ") SELECT " + ",".join(selected) + f" FROM wp_posts WHERE ID={int(case['parent_id'])};")
        try:
            reconcile_precondition()
        except AssertionError:
            record("NATIVE_ID_COLLISION_REFUSED", target_available=False, conflicting_id=new_id)
        else:
            raise AssertionError("Collision accepted")
        reset_restore("after-collision")
        reconcile_precondition()
        replay(DELTA["end_position"])
        current = state(RESTORE_SOCKET)
        assert set(current["tables"]) == set(endpoint["tables"])
        watermarks = []
        for name, details in endpoint["tables"].items():
            actual = current["tables"][name]
            assert actual["data_sha256"] == details["data_sha256"] and actual["schema_without_highwater_sha256"] == details["schema_without_highwater_sha256"]
            assert actual["auto_increment"] <= details["auto_increment"], "Target high-water exceeds reviewed source"
            if actual["auto_increment"] < details["auto_increment"]:
                sql(RESTORE_SOCKET, f"ALTER TABLE `{name}` AUTO_INCREMENT={details['auto_increment']};")
                watermarks.append(name)
        for name, change in filesystem_delta.items():
            target = RESTORE / "wordpress" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(BACKUP / "delta/files" / name, target)
            target.chmod(change["after"]["mode"])
        assert app_equal(state(RESTORE_SOCKET), endpoint)
        assert inventory(RESTORE / "wordpress") == expected_site(after_files)
        assert sha((BACKUP / "delta/recovery-case.json").read_bytes()) == DELTA["state_delta"]["recovery-case.json"]
        shutil.copyfile(BACKUP / "delta/recovery-case.json", RESTORE / "state/recovery-case.json")
        expected_state = {**MANIFEST["state_files"], "recovery-case.json": {**MANIFEST["state_files"]["recovery-case.json"], "sha256": DELTA["state_delta"]["recovery-case.json"], "bytes": (BACKUP / "delta/recovery-case.json").stat().st_size}}
        assert inventory(RESTORE / "state") == expected_state
        assert inventory(RESTORE / "control") == MANIFEST["control_files"]
        checkpoint = {"schema": "skyyrose.private-reconciled-checkpoint.v1", "database": endpoint, "site": expected_site(after_files), "state": expected_state, "control": MANIFEST["control_files"], "delta_sha256": sha((BACKUP / "delta/manifest.json").read_bytes()), "available": True}
        write_json(RESTORE / "checkpoint.json", checkpoint)
        # A checkpoint alone never authorizes replay or overwriting newer state.
        retry = json.loads(command([sys.executable, str(Path(__file__)), "--verify-checkpoint"]))
        assert retry["status"] == "NOOP_EXACT_CHECKPOINT_AND_POSTIMAGE"
        original_option = sql(RESTORE_SOCKET, "SELECT HEX(option_value) FROM wp_options WHERE option_name='blogdescription';").strip().decode()
        assert re.fullmatch(r"[A-Fa-f0-9]*", original_option)
        assert sql(RESTORE_SOCKET, "SELECT COUNT(*) FROM wp_options WHERE option_name='blogdescription';").strip() == b"1"
        sql(RESTORE_SOCKET, "UPDATE wp_options SET option_value=CONCAT(option_value,' synthetic-checkpoint-drift') WHERE option_name='blogdescription';")
        drift = state(RESTORE_SOCKET)
        refusal = subprocess.run([sys.executable, str(Path(__file__)), "--verify-checkpoint"], capture_output=True, check=False)
        refused_path = OUT / ("restore-" + RUN_ID + "-stale-checkpoint.txt")
        refused_path.write_bytes(refusal.stdout + refusal.stderr)
        assert refusal.returncode != 0 and app_equal(state(RESTORE_SOCKET), drift)
        record("STALE_CHECKPOINT_REFUSED", target_available=False, unchanged_drifted_target=True, receipt=refused_path.name, sha256=sha(refused_path.read_bytes()))
        sql(RESTORE_SOCKET, f"UPDATE wp_options SET option_value=UNHEX('{original_option}') WHERE option_name='blogdescription';")
        assert app_equal(state(RESTORE_SOCKET), endpoint)
        record("RECONCILIATION_EXACT_AND_RETRY_NOOP", tables=len(endpoint["tables"]), highwater_reconciled=watermarks, checkpoint_sha256=sha((RESTORE / "checkpoint.json").read_bytes()), duplicate_replay_performed=False)
        probe_before = state(RESTORE_SOCKET)
        verified = native("inspect", True)
        assert verified["snapshot"] == after["snapshot"]
        probe_after = state(RESTORE_SOCKET)
        record("NATIVE_NEWER_ORDER_STATE_VERIFIED", native_ids_payment_stock_promises_equal=True, post_probe_changed_tables=[name for name in probe_after["tables"] if probe_before["tables"][name] != probe_after["tables"][name]])
        assert app_equal(probe_before, probe_after), "Native probe changed database; review changes before declaring restored target available"
        assert json.loads(command([sys.executable, str(Path(__file__)), "--verify-checkpoint"]))["status"] == "NOOP_EXACT_CHECKPOINT_AND_POSTIMAGE"
        successful = True
    except BaseException as error:
        REPORT["failure"] = {"type": type(error).__name__, "message": str(error)[:1000]}
        raise
    finally:
        cleanup = []
        for socket in [RESTORE_SOCKET, SOURCE_SOCKET]:
            try:
                if subprocess.run(["/opt/homebrew/bin/mariadb-admin", "--no-defaults", "--socket=" + socket, "-uroot", "ping"], capture_output=True, check=False).returncode == 0:
                    stop(socket)
                cleanup.append({"socket": socket, "stopped": True})
            except (OSError, AssertionError, subprocess.SubprocessError) as error:
                cleanup.append({"socket": socket, "stopped": False, "error": type(error).__name__})
        for process in PROCESSES:
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                try:
                    process.terminate()
                    process.wait(timeout=10)
                except (OSError, subprocess.TimeoutExpired):
                    try:
                        process.kill()
                        process.wait(timeout=10)
                    except (OSError, subprocess.TimeoutExpired):
                        pass
                cleanup.append({"owned_child_terminated": process.pid, "stopped": False})
        REPORT["cleanup"] = cleanup
        if successful:
            REPORT["status"] = "PASS_PRIVATE_COLD_RESTORE_AND_REVIEWED_NEWER_STATE_RECONCILIATION" if all(row["stopped"] for row in cleanup) else "FAIL_CLEANUP"
        write_json(RUNS / (RUN_ID + ".json"), REPORT)
        write_json(OUT / "restore-results.json", REPORT)
        lock.rmdir()
    assert REPORT["status"] == "PASS_PRIVATE_COLD_RESTORE_AND_REVIEWED_NEWER_STATE_RECONCILIATION"
    print(REPORT["status"])


if __name__ == "__main__":
    if sys.argv[1:] == ["--verify-checkpoint"]:
        print(json.dumps(verify_checkpoint()))
    else:
        assert not sys.argv[1:]
        main()
