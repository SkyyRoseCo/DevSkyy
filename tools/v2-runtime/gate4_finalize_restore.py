"""Exact post-relocation cache qualification; never a general transient exclusion."""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import time
import gate4_restore_local as g

if not __debug__:
    raise RuntimeError("Finalization requires assertions")
BASE = g.PRIVATE
CHECK = g.RESTORE / "postboot-checkpoint.json"
OUT = g.OUT
REPORT = {
    "schema": "skyyrose.private-postboot-restore.v1",
    "status": "INCOMPLETE",
    "authentication": "NOT_APPLICABLE",
    "steps": [],
    "limits": [
        "Synthetic local restore only, no live restore/release or installed runtime parity",
        "Pre-bootstrap exact150-table source equality remains separate from two exact relocated theme-cache insertions",
    ],
}


def pin(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    g.write_json(path, value)


def verify():
    value = json.loads(CHECK.read_text())
    assert value["verified"] is True
    assert (
        pin(g.BACKUP / "manifest.json") == value["backup_sha256"]
        and pin(g.BACKUP / "delta/manifest.json") == value["delta_sha256"]
    )
    assert pin(g.RESTORE / "checkpoint.json") == value["original_checkpoint_sha256"]
    assert g.app_equal(g.state(g.RESTORE_SOCKET), value["database"])
    for name in ["site", "state", "control"]:
        assert g.inventory(g.RESTORE / ("wordpress" if name == "site" else name)) == value[name]
    return {"status": "NOOP_EXACT_POSTBOOT_CHECKPOINT", "replay_performed": False}


def rows():
    return g.sql(
        g.RESTORE_SOCKET,
        "SELECT CONCAT_WS(':',CONCAT('V',HEX(CAST(option_id AS BINARY))),CONCAT('V',HEX(CAST(option_name AS BINARY))),IF(option_value IS NULL,'N',CONCAT('V',HEX(CAST(option_value AS BINARY)))),CONCAT('V',HEX(CAST(autoload AS BINARY)))) AS encoded_row FROM wp_options ORDER BY BINARY encoded_row;",
    )


def decode(row):
    return [None if cell == b"N" else bytes.fromhex(cell[1:].decode()) for cell in row.split(b":")]


def keyed(data):
    result = {}
    for row in data.splitlines():
        name = decode(row)[1]
        assert name not in result
        result[name] = row
    return result


def encoded(cells):
    return b":".join(b"N" if cell is None else b"V" + cell.hex().upper().encode() for cell in cells)


def literal(value):
    return "UNHEX('" + value.hex() + "')"


def validate_image(observed, source_rows, endpoint, first_id, start, end, ttl):
    values = keyed(rows())
    original = keyed(source_rows)
    suffix = hashlib.md5(
        str(g.RESTORE / "wordpress/wp-content/themes/skyyrose-flagship-2").encode()
    ).hexdigest()
    source_suffix = hashlib.md5(
        str(BASE / "wordpress/wp-content/themes/skyyrose-flagship-2").encode()
    ).hexdigest()
    cache = ("_site_transient_wp_theme_files_patterns-" + suffix).encode()
    timeout = ("_site_transient_timeout_wp_theme_files_patterns-" + suffix).encode()
    source_key = ("_site_transient_wp_theme_files_patterns-" + source_suffix).encode()
    assert cache not in original and timeout not in original and source_key in original
    assert set(values) == set(original) | {cache, timeout}
    assert all(values[name] == row for name, row in original.items()), "Unrelated options drifted"
    timeout_row = decode(values[timeout])
    cache_row = decode(values[cache])
    source_value = decode(original[source_key])[2]
    assert timeout_row[0] == str(first_id).encode() and cache_row[0] == str(first_id + 1).encode()
    assert timeout_row[3] == cache_row[3] == b"off" and cache_row[2] == source_value
    assert timeout_row[2].isdigit() and start <= int(timeout_row[2]) - ttl <= end
    expected = {
        **original,
        timeout: encoded([str(first_id).encode(), timeout, timeout_row[2], b"off"]),
        cache: encoded([str(first_id + 1).encode(), cache, source_value, b"off"]),
    }
    assert values == expected
    assert (
        set(observed["tables"]) == set(endpoint["tables"])
        and observed["programmable_sha256"] == endpoint["programmable_sha256"]
    )
    for name, source in endpoint["tables"].items():
        actual = observed["tables"][name]
        if name != "wp_options":
            assert actual == source, (name, "drift")
        else:
            assert (
                actual["schema_without_highwater_sha256"]
                == source["schema_without_highwater_sha256"]
            )
            assert (
                actual["auto_increment"] == first_id + 2
                and actual["row_count"] == source["row_count"] + 2
            )
            assert (
                actual["data_sha256"]
                == hashlib.sha256(b"\n".join(sorted(expected.values())) + b"\n").hexdigest()
            )
    return {timeout: values[timeout], cache: values[cache]}


def cleanup_database(socket):
    errors = []
    try:
        ping = subprocess.run(
            [
                "/opt/homebrew/bin/mariadb-admin",
                "--no-defaults",
                "--socket=" + socket,
                "-uroot",
                "ping",
            ],
            capture_output=True,
            check=False,
            timeout=5,
        )
        if ping.returncode == 0:
            g.stop(socket)
    except (OSError, AssertionError, subprocess.SubprocessError) as error:
        errors.append({"step": "shutdown", "error": type(error).__name__})
    for child in g.PROCESSES:
        try:
            child.wait(timeout=20)
        except subprocess.TimeoutExpired:
            errors.append({"step": "forced-child-stop", "pid": child.pid})
            try:
                child.terminate()
                child.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    child.kill()
                    child.wait(timeout=5)
                except (OSError, subprocess.TimeoutExpired):
                    errors.append({"step": "child-still-running", "pid": child.pid})
    return errors


def main():
    lock = BASE / ".sr-gate4-run-lock"
    lock.mkdir()
    overlay = g.RESTORE / "wordpress/wp-content/mu-plugins/00-gate4-restore-query-audit.php"
    audit = g.RESTORE / ("query-audit-" + g.RUN_ID + ".jsonl")
    checkpoint = None
    overlay_owned = False
    source_paths = [
        Path(__file__),
        Path(g.__file__),
        g.ROOT / "tools/v2-runtime/gate4-recovery-fixture.php",
        g.RESTORE / "control/gate4-recovery-fixture.php",
    ]
    REPORT["source_pins_at_start"] = {
        str(path.relative_to(g.ROOT)): pin(path) for path in source_paths
    }
    complete = False
    cleanup = False
    try:
        g.MANIFEST = json.loads((g.BACKUP / "manifest.json").read_text())
        delta = json.loads((g.BACKUP / "delta/manifest.json").read_text())
        endpoint = delta["endpoint"]
        original_checkpoint = json.loads((g.RESTORE / "checkpoint.json").read_text())
        original_pin = pin(g.RESTORE / "checkpoint.json")
        expected_pin = endpoint["tables"]["wp_options"]["data_sha256"]
        candidates = [
            path for path in OUT.glob("restore-*-command-*.txt") if pin(path) == expected_pin
        ]
        assert candidates
        source_rows = candidates[0].read_bytes()
        source_snapshot_pin = pin(candidates[0])
        prior = json.loads((OUT / "restore-results.json").read_text())
        assert prior["failure"]["message"].startswith("Native probe changed database")
        write(OUT / "restore-pre-postboot-incomplete.json", prior)
        g.start(g.RESTORE_SOCKET, g.RESTORE / "mysql", False)
        initial = g.state(g.RESTORE_SOCKET)
        native_receipts = []
        for receipt in OUT.glob("restore-1792422346756436000-command-*.txt"):
            if receipt.stat().st_size < 1000:
                continue
            try:
                value = json.loads(receipt.read_bytes())
            except (ValueError, UnicodeDecodeError):
                continue
            if isinstance(value, dict) and value.get("snapshot") == delta["native_endpoint"]:
                native_receipts.append(receipt)
        assert native_receipts
        last_native = max(native_receipts, key=lambda path: int(path.stem.rsplit("-", 1)[1]))
        initial_end = int(last_native.stat().st_mtime)
        REPORT["initial_native_receipt"] = {
            "name": last_native.name,
            "sha256": pin(last_native),
            "end_time": initial_end,
        }
        initial_rows = validate_image(
            initial,
            source_rows,
            endpoint,
            endpoint["tables"]["wp_options"]["auto_increment"],
            initial_end - 120,
            initial_end,
            1800,
        )
        assert g.inventory(g.RESTORE / "wordpress") == original_checkpoint["site"]
        assert (
            g.inventory(g.RESTORE / "state") == original_checkpoint["state"]
            and g.inventory(g.RESTORE / "control") == original_checkpoint["control"]
        )
        # Delete only the complete, guarded two-row cache preimages. No ID reset.
        predicates = []
        for row in initial_rows.values():
            cells = decode(row)
            predicates.append(
                "("
                + " AND ".join(
                    f"BINARY `{column}`=BINARY {literal(value)}"
                    for column, value in zip(
                        ["option_id", "option_name", "option_value", "autoload"], cells, strict=True
                    )
                )
                + ")"
            )
        affected = g.sql(
            g.RESTORE_SOCKET,
            "DELETE FROM wp_options WHERE " + " OR ".join(predicates) + "; SELECT ROW_COUNT();",
        ).strip()
        assert affected == b"2"
        before_water = int(
            g.sql(
                g.RESTORE_SOCKET,
                "SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='wp_options';",
            ).strip()
        )
        assert before_water == initial["tables"]["wp_options"]["auto_increment"]
        assert rows() == source_rows
        assert not overlay.exists()
        mu = """<?php
if (!defined('SKYYROSE_RELEASE_SYNTHETIC_FIXTURE') || !SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME!=='sr_release_fixture' || $GLOBALS['wpdb']->get_var('SELECT @@socket')!=='/tmp/sr-gate4-restore-01a0f768.sock') {throw new RuntimeException('Synthetic restore audit identity required');}
function sr_restore_query_audit($value) {
 if(preg_match('/^\\s*(INSERT|UPDATE|DELETE|REPLACE|ALTER)\\s/i',$value)) {file_put_contents(AUDIT_PATH, wp_json_encode(array('kind'=>'PRE_EXECUTION_WRITE_ATTEMPT','query'=>$value,'time'=>time(),'stack'=>debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS)))."\\n",FILE_APPEND);}
 return $value;
}
add_filter('query','sr_restore_query_audit',PHP_INT_MAX);
add_filter('wp_theme_files_cache_ttl',function($ttl,$kind){file_put_contents(AUDIT_PATH,wp_json_encode(array('kind'=>'NATIVE_TTL','ttl'=>$ttl,'cache_type'=>$kind,'time'=>time()))."\\n",FILE_APPEND);return $ttl;},PHP_INT_MAX,2);
""".replace("AUDIT_PATH", json.dumps(str(audit)))
        overlay.write_text(mu)
        overlay_owned = True
        REPORT["audit_overlay_sha256"] = pin(overlay)
        start = int(time.time())
        native = g.native("inspect", True)
        end = int(time.time())
        assert native["snapshot"] == delta["native_endpoint"]
        events = [json.loads(line) for line in audit.read_text().splitlines()]
        ttl = [row for row in events if row["kind"] == "NATIVE_TTL"]
        attempts = [row for row in events if row["kind"] == "PRE_EXECUTION_WRITE_ATTEMPT"]
        assert (
            len(ttl) == 1
            and ttl[0]["ttl"] == 1800
            and ttl[0]["cache_type"] == "theme_block_patterns"
        )
        assert len(attempts) == 2
        for row in attempts:
            assert row["query"].lstrip().startswith("INSERT INTO `wp_options`")
            assert any(
                frame.get("class") == "WP_Theme" and frame.get("function") == "set_pattern_cache"
                for frame in row["stack"]
            )
        after = g.state(g.RESTORE_SOCKET)
        confirmed = validate_image(
            after, source_rows, endpoint, before_water, start, end, ttl[0]["ttl"]
        )
        REPORT["steps"].append(
            {
                "step": "EXACT_RELOCATION_CACHE_REPRODUCED",
                "names": [name.decode() for name in confirmed],
                "first_id": before_water,
                "auto_increment": before_water + 2,
                "ttl": 1800,
                "window": [start, end],
                "write_attempts": 2,
                "confirmed_inserted_rows": 2,
                "source_options_receipt_sha256": source_snapshot_pin,
                "audit_file": (str(audit.relative_to(g.ROOT))),
                "audit_sha256": pin(audit),
                "all_other_rows_tables_schemas_unchanged": True,
            }
        )
        # Negative control changes only one existing synthetic option, never IDs.
        old = (
            g.sql(
                g.RESTORE_SOCKET,
                "SELECT HEX(option_value) FROM wp_options WHERE option_name='blogdescription';",
            )
            .strip()
            .decode()
        )
        altered = bytes.fromhex(old) + b" synthetic-owned-cache-validation-drift"
        assert (
            g.sql(
                g.RESTORE_SOCKET,
                f"UPDATE wp_options SET option_value={literal(altered)} WHERE option_name='blogdescription' AND BINARY option_value=BINARY UNHEX('{old}'); SELECT ROW_COUNT();",
            ).strip()
            == b"1"
        )
        try:
            validate_image(
                g.state(g.RESTORE_SOCKET), source_rows, endpoint, before_water, start, end, 1800
            )
        except AssertionError:
            REPORT["steps"].append(
                {"step": "UNRELATED_OPTION_DRIFT_REFUSED", "target_available": False}
            )
        else:
            raise AssertionError("Unrelated option accepted")
        assert (
            g.sql(
                g.RESTORE_SOCKET,
                f"UPDATE wp_options SET option_value=UNHEX('{old}') WHERE option_name='blogdescription' AND BINARY option_value=BINARY {literal(altered)}; SELECT ROW_COUNT();",
            ).strip()
            == b"1"
        )
        assert g.app_equal(g.state(g.RESTORE_SOCKET), after)
        assert pin(overlay) == REPORT["audit_overlay_sha256"]
        overlay.unlink()
        overlay_owned = False
        assert g.inventory(g.RESTORE / "wordpress") == original_checkpoint["site"]
        # This is the independent boot without query instrumentation.
        assert g.native("inspect", True)["snapshot"] == delta["native_endpoint"]
        final = g.state(g.RESTORE_SOCKET)
        assert g.app_equal(final, after)
        for name in ["site", "state", "control"]:
            assert (
                g.inventory(g.RESTORE / ("wordpress" if name == "site" else name))
                == original_checkpoint[name]
            )
        checkpoint = {
            "schema": "skyyrose.private-postboot-checkpoint.v1",
            "verified": True,
            "released": False,
            "database": final,
            "site": original_checkpoint["site"],
            "state": original_checkpoint["state"],
            "control": original_checkpoint["control"],
            "backup_sha256": pin(g.BACKUP / "manifest.json"),
            "delta_sha256": pin(g.BACKUP / "delta/manifest.json"),
            "original_checkpoint_sha256": original_pin,
            "source_pins": {str(Path(__file__).relative_to(g.ROOT)): pin(Path(__file__))},
        }
        write(CHECK, checkpoint)
        retry = json.loads(g.command([sys.executable, str(Path(__file__)), "--verify"]))
        assert retry["status"] == "NOOP_EXACT_POSTBOOT_CHECKPOINT"
        REPORT["steps"].append(
            {
                "step": "UNINSTRUMENTED_NATIVE_BOOT_AND_FRESH_CHECKPOINT_RETRY_EXACT",
                "native_orders_payment_stock_equal": True,
                "all150_tables_exact_postboot": True,
                "filesystem_state_control_exact": True,
                "replay_performed": False,
            }
        )
        complete = True
    except BaseException as error:
        REPORT["failure"] = {"type": type(error).__name__, "message": str(error)[:1000]}
        raise
    finally:
        cleanup_errors = []
        if overlay_owned:
            try:
                assert pin(overlay) == REPORT["audit_overlay_sha256"], "Owned overlay changed"
                overlay.unlink()
            except (OSError, AssertionError) as error:
                cleanup_errors.append({"step": "overlay-cleanup", "error": type(error).__name__})
        cleanup_errors.extend(cleanup_database(g.RESTORE_SOCKET))
        cleanup = not cleanup_errors
        REPORT["cleanup_errors"] = cleanup_errors
        REPORT["owned_service_stopped"] = cleanup
        try:
            if complete and cleanup:
                cold = g.inventory(g.RESTORE / "mysql")
                write(g.RESTORE / "final-cold-files.json", cold)
                REPORT["final_cold_inventory_sha256"] = pin(g.RESTORE / "final-cold-files.json")
                assert all(
                    pin(g.ROOT / path) == value
                    for path, value in REPORT["source_pins_at_start"].items()
                )
                REPORT["status"] = "PASS_PRIVATE_RESTORE_RECONCILIATION_AND_EXACT_POSTBOOT_STATE"
            elif complete:
                REPORT["status"] = "FAIL_CLEANUP"
            if checkpoint:
                checkpoint["released"] = False
                write(CHECK, checkpoint)
            write(OUT / ("restore-postboot-" + g.RUN_ID + ".json"), REPORT)
            write(OUT / "restore-postboot-results.json", REPORT)
            if checkpoint and complete and cleanup:
                checkpoint["released"] = True
                write(CHECK, checkpoint)
                REPORT["checkpoint_sha256"] = pin(CHECK)
                write(OUT / ("restore-postboot-" + g.RUN_ID + ".json"), REPORT)
                write(OUT / "restore-postboot-results.json", REPORT)
        except BaseException as error:
            REPORT["status"] = "FAIL_FINALIZATION"
            REPORT["finalization_error"] = type(error).__name__
            if checkpoint:
                checkpoint["released"] = False
                write(CHECK, checkpoint)
            write(OUT / ("restore-postboot-" + g.RUN_ID + ".json"), REPORT)
            write(OUT / "restore-postboot-results.json", REPORT)
            raise
        finally:
            lock.rmdir()
    assert (
        REPORT["status"] == "PASS_PRIVATE_RESTORE_RECONCILIATION_AND_EXACT_POSTBOOT_STATE"
    ), REPORT["status"]
    print(REPORT["status"])


if __name__ == "__main__":
    if sys.argv[1:] == ["--verify"]:
        print(json.dumps(verify()))
    else:
        assert not sys.argv[1:]
        main()
