"""Four independent order-empty storage fixtures; never switch populated stores."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import time
import subprocess
import gate4_restore_local as fixture
from gate4_finalize_restore import cleanup_database

if not __debug__:
    raise RuntimeError("Storage qualification requires assertions")
ROOT = fixture.ROOT
PRIVATE = fixture.PRIVATE
OUT = fixture.OUT
RUN = str(time.time_ns())
SAVED = PRIVATE / "storage-fixtures" / RUN
SOCKET = fixture.SOURCE_SOCKET
report = {
    "schema": "skyyrose.independent-native-storage-modes.v1",
    "status": "INCOMPLETE",
    "run": RUN,
    "authentication": "NOT_APPLICABLE",
    "modes": [],
    "limits": [
        "Four independently initialized order-empty fixtures; no populated-store authority transition or synchronization proof",
        "Available seven-commerce-plugin profile only, not full installed-stack or production parity",
        "Original populated clone and completed restore/coldbackup preserved; historical orphan untouched",
    ],
}
PLUGINS = [
    "woocommerce",
    "stripe-tax-for-woocommerce",
    "woocommerce-paypal-payments",
    "woocommerce-shipping",
    "woocommerce-gateway-stripe",
    "woocommerce-services",
    "woocommerce-payments",
]


def pin(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wp(*args):
    return fixture.command(
        [
            "/usr/bin/sandbox-exec",
            "-p",
            fixture.RUNTIME["profile"],
            "php",
            *fixture.RUNTIME["php_prefix"],
            "/opt/homebrew/bin/wp",
            "--path=" + str(PRIVATE / "wordpress"),
            "--skip-plugins=" + ",".join(fixture.RUNTIME["wp_skip_plugins"]),
            *args,
        ],
        timeout=120,
    )


def mode(mode, *args):
    value = json.loads(
        wp("eval-file", str(ROOT / "tools/v2-runtime/gate4-storage-mode.php"), mode, *args)
    )
    assert value["ok"]
    return value


def preserve_current(target):
    target.mkdir(parents=True, exist_ok=True)
    for name in ["wordpress", "mysql"]:
        path = PRIVATE / name
        if path.exists():
            assert not (target / name).exists()
            path.rename(target / name)


def preserve_populated(original, moved):
    original.mkdir(parents=True, exist_ok=False)
    for name in ["wordpress", "mysql"]:
        (PRIVATE / name).rename(original / name)
        moved.add(name)


def socket_stopped():
    return (
        subprocess.run(
            [
                "/opt/homebrew/bin/mariadb-admin",
                "--no-defaults",
                "--socket=" + SOCKET,
                "-uroot",
                "ping",
            ],
            capture_output=True,
            check=False,
            timeout=5,
        ).returncode
        != 0
    )


def finish_preservation(original, current, moved):
    errors = []
    # A failed preflight has no run-owned children and must never stop an
    # encountered service. Only start() appends this run's owned processes.
    if fixture.PROCESSES:
        errors.extend(cleanup_database(SOCKET))
    safe = all(child.poll() is not None for child in fixture.PROCESSES)
    if moved and safe:
        try:
            safe = socket_stopped()
        except (OSError, subprocess.SubprocessError):
            safe = False
    if moved and not safe:
        errors.append(
            {
                "step": "preservation-held-live-process",
                "preserved_original": str(original),
                "current_fixture": str(current),
            }
        )
        return errors, False
    for name in ["wordpress", "mysql"]:
        if name not in moved:
            continue
        try:
            destination = PRIVATE / name
            if destination.exists():
                assert current is not None and (current / "fixture-owner.json").is_file()
                assert json.loads((current / "fixture-owner.json").read_text())["run"] == RUN
                assert not (current / name).exists()
                destination.rename(current / name)
            (original / name).rename(destination)
        except (OSError, AssertionError) as error:
            errors.append(
                {"step": "restore-original-path", "name": name, "error": type(error).__name__}
            )
    return errors, safe


def main():
    lock = PRIVATE / ".sr-gate4-run-lock"
    lock.mkdir()
    original = SAVED / "preserved-populated"
    current = None
    moved_original = set()
    original_inventory = {}
    restore_cold = None
    errors = []
    complete = False
    try:
        assert (
            subprocess.run(
                [
                    "/opt/homebrew/bin/mariadb-admin",
                    "--no-defaults",
                    "--socket=" + SOCKET,
                    "-uroot",
                    "ping",
                ],
                capture_output=True,
                check=False,
                timeout=5,
            ).returncode
            != 0
        ), "Working service must be stopped"
        assert all(
            (PRIVATE / "wordpress/wp-content/plugins" / slug).is_dir() for slug in PLUGINS
        ), PLUGINS
        source_paths = [
            Path(__file__),
            Path(fixture.__file__),
            ROOT / "tools/v2-runtime/gate4-storage-mode.php",
            ROOT / "tools/v2-runtime/gate4-recovery-fixture.php",
            ROOT / "tools/v2-runtime/variation-migration-core-next.php",
            ROOT / "tools/v2-runtime/gate4_finalize_restore.py",
        ]
        report["source_pins_at_start"] = {str(p.relative_to(ROOT)): pin(p) for p in source_paths}
        for name in ["wordpress", "mysql"]:
            original_inventory[name] = fixture.inventory(PRIVATE / name)
        restore_cold = fixture.inventory(PRIVATE / "restore/mysql")
        SAVED.mkdir(parents=True)
        fixture.write_json(SAVED / "preserved-populated-inventory.json", original_inventory)
        report["preservation_manifest_sha256"] = pin(SAVED / "preserved-populated-inventory.json")
        preserve_populated(original, moved_original)
        for authority, sync in [("no", "no"), ("no", "yes"), ("yes", "no"), ("yes", "yes")]:
            label = (
                ("hpos" if authority == "yes" else "legacy")
                + "-"
                + ("sync" if sync == "yes" else "nosync")
            )
            current = SAVED / label
            current.mkdir()
            fixture.write_json(current / "fixture-owner.json", {"run": RUN, "mode": label})
            # All acquired code is preserved; old uploads are excluded from new
            # fixtures so no old order-to-file association can enter this test.
            shutil.copytree(
                original / "wordpress",
                PRIVATE / "wordpress",
                ignore=lambda directory, names: (
                    ["uploads"] if Path(directory) == original / "wordpress/wp-content" else []
                ),
            )
            (PRIVATE / "mysql").mkdir()
            fixture.command(
                [
                    "/usr/bin/sandbox-exec",
                    "-p",
                    "(version 1)(allow default)(deny network*)",
                    "/opt/homebrew/bin/mariadb-install-db",
                    "--no-defaults",
                    "--datadir=" + str(PRIVATE / "mysql"),
                    "--auth-root-authentication-method=normal",
                    "--skip-test-db",
                    "--skip-name-resolve",
                ]
            )
            fixture.start(SOCKET, PRIVATE / "mysql", False)
            fixture.sql(
                SOCKET,
                "CREATE DATABASE sr_release_fixture CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
                False,
            )
            wp(
                "core",
                "install",
                "--url=http://127.0.0.1:18362",
                "--title=Private synthetic storage fixture",
                "--admin_user=gate4_synthetic",
                "--admin_password=synthetic-local-only-no-remote-authority",
                "--admin_email=fixture@example.invalid",
                "--skip-email",
            )
            wp("plugin", "activate", *PLUGINS)
            wp("theme", "activate", "skyyrose-flagship-2")
            emptiness = (
                fixture.sql(
                    SOCKET,
                    "SELECT COUNT(*) FROM wp_posts WHERE post_type IN ('shop_order','shop_order_refund','shop_order_placehold'); SELECT COUNT(*) FROM wp_wc_orders; SELECT COUNT(*) FROM wp_woocommerce_order_items;",
                )
                .decode()
                .splitlines()
            )
            assert emptiness == ["0", "0", "0"], emptiness
            mode("set", authority, sync)
            observed = mode("inspect")
            expected = (
                "Automattic\\WooCommerce\\Internal\\DataStores\\Orders\\OrdersTableDataStore"
                if authority == "yes"
                else "WC_Order_Data_Store_CPT"
            )
            assert (
                observed["authority_option"] == authority
                and observed["sync_option"] == sync
                and observed["hpos"] == (authority == "yes")
                and observed["native_store_class"] == expected
            )
            fixture.SOURCE_CASE = PRIVATE / ("recovery-storage-" + RUN + "-" + label + ".json")
            seed = fixture.native("seed")
            assert (
                seed["snapshot"]["hpos"] == (authority == "yes")
                and seed["snapshot"]["sync_option"] == sync
            )
            assert fixture.native("pending-control")["pending_refused"] is True
            paid = fixture.native("post-backup")
            assert paid["snapshot"]["stock"] == 18
            assert fixture.native("inspect")["snapshot"] == paid["snapshot"]
            active = [
                value.split("/")[0]
                for value in json.loads(wp("option", "get", "active_plugins", "--format=json"))
            ]
            assert sorted(active) == sorted(PLUGINS)
            cleanup = cleanup_database(SOCKET)
            assert (
                not cleanup
                and all(child.poll() is not None for child in fixture.PROCESSES)
                and socket_stopped()
            ), cleanup
            state = current / "state"
            state.mkdir()
            for path in PRIVATE.glob(fixture.SOURCE_CASE.name + "*"):
                shutil.move(str(path), state / path.name)
            preserve_current(current)
            cold = fixture.inventory(current / "mysql")
            fixture.write_json(current / "cold-db-files.json", cold)
            report["modes"].append(
                {
                    "label": label,
                    "status": "PASS_NATIVE_HISTORY_PAYMENT_DUPLICATE_STOCK",
                    "initial_order_store_item_counts": [0, 0, 0],
                    "authority": authority,
                    "sync": sync,
                    "native_store_class": expected,
                    "active_plugins": active,
                    "parent_id": seed["case"]["parent_id"],
                    "baseline_orders": seed["case"]["orders"],
                    "new_order": json.loads((state / fixture.SOURCE_CASE.name).read_text())[
                        "post_backup_order_id"
                    ],
                    "stock_before": 20,
                    "stock_after": 18,
                    "snapshot_sha256": hashlib.sha256(
                        json.dumps(paid["snapshot"], sort_keys=True).encode()
                    ).hexdigest(),
                    "fixture": str(current.relative_to(ROOT)),
                    "cold_inventory_sha256": pin(current / "cold-db-files.json"),
                    "owned_service_stopped": True,
                }
            )
            fixture.write_json(OUT / "storage-results.json", report)
        complete = True
    except BaseException as error:
        report["failure"] = {"type": type(error).__name__, "message": str(error)[:1000]}
        raise
    finally:
        preservation_errors, safe_to_move = finish_preservation(original, current, moved_original)
        errors.extend(preservation_errors)
        try:
            if moved_original and safe_to_move:
                assert all(
                    fixture.inventory(PRIVATE / name) == expected
                    for name, expected in original_inventory.items()
                )
                report["populated_clone_full_file_bytes_modes_restored"] = True
            if restore_cold is not None:
                assert fixture.inventory(PRIVATE / "restore/mysql") == restore_cold
                report["completed_restore_cold_bytes_modes_unchanged"] = True
        except BaseException as error:
            errors.append(
                {
                    "step": "preservation-validation",
                    "error": type(error).__name__,
                    "message": str(error)[:500],
                }
            )
        report["cleanup_errors"] = errors
        report["owned_services_stopped"] = not errors
        if complete:
            report["status"] = (
                "PASS_FOUR_INDEPENDENT_NATIVE_STORAGE_MODES"
                if not errors
                and report.get("populated_clone_full_file_bytes_modes_restored")
                and report.get("completed_restore_cold_bytes_modes_unchanged")
                else "FAIL_CLEANUP"
            )
        try:
            fixture.write_json(OUT / ("storage-" + RUN + ".json"), report)
            fixture.write_json(OUT / "storage-results.json", report)
        finally:
            lock.rmdir()
    assert report["status"] == "PASS_FOUR_INDEPENDENT_NATIVE_STORAGE_MODES", report["status"]
    print(report["status"])


if __name__ == "__main__":
    main()
