"""Additive HPOS-native V1 fakegateway coverage; no populated lifecycle replay."""

from __future__ import annotations
import json
import ctypes
import os
import stat
from pathlib import Path
import shutil
import subprocess
import sys
import test_gate4_populated as g4
from gate4_gateway_selection import validate as validate_gateway_selection
from gate4_gateway_selection import controls as gateway_selection_controls
from test_gate4_populated import (
    ROOT,
    PRIVATE,
    OUT,
    SOCKET,
    PROFILE,
    ORIGINAL,
    PLUGINS,
    pin,
    write,
    record,
    command,
    containment,
    wp,
    native,
    inspect,
    same,
    same_order,
    canonical,
    semantic_orders,
    has,
)

base = g4.base
RUN = g4.RUN
REPORT = g4.REPORT
REPORT.clear()
REPORT.update(
    {
        "schema": "skyyrose.private-hpos-v1-payments.v1",
        "run": RUN,
        "status": "INCOMPLETE",
        "authentication": "NOT_APPLICABLE",
        "steps": [],
        "limits": [
            "Seven-plugin PHP8.5.6/MariaDB13 fresh synthetic HPOS-native orders only",
            "Historical producer exact function; no real historical order or installed33-plugin parity",
            "Native PHP existing-order fakegateway only; no HTTP/browser/session or real gateway qualification",
            "Stock render/StoreAPI/fakeprocessor and bare-handler probe remain separate",
            "No populated synchronization lifecycle rerun or prior packet reclassification",
            "Three named notice refusals admit only attributed native gateway/date saves; customer-state writes retained, not physical NOOP",
        ],
    }
)
HPOS = "Automattic\\WooCommerce\\Internal\\DataStores\\Orders\\OrdersTableDataStore"
if not __debug__:
    raise RuntimeError("Assertions required")
ORIGINAL_NATIVE = g4.native
NAMED_REFUSALS = {"v1-missing-id", "v1-ambiguous-sku", "active-journal"}


def observed_native(mode, *args, expected=(0,), payment=False):
    if payment and mode == "pay" and args[-1] in NAMED_REFUSALS:
        return wp(
            "eval-file",
            str(ROOT / "tools/v2-runtime/gate4-hpos-v1-pay-observer.php"),
            mode,
            *map(str, args),
            expected=expected,
        ).returncode
    return ORIGINAL_NATIVE(mode, *args, expected=expected, payment=payment)


g4.native = observed_native


def assert_hpos(snapshot):
    assert (
        snapshot["hpos"]
        and snapshot["authority"] == "yes"
        and snapshot["runtime"]["datastore"] == HPOS
    )


def historical_payload(snapshot):
    """Exact fixture history, excluding only independently checked native stock rows."""
    orders = json.loads(canonical(snapshot["orders"]))
    for order in orders.values():
        for item in order["items"].values():
            rows = item["meta_data"]
            typed = [row["value"] for row in rows if row["key"] == "_g4_typed"]
            duplicate = [row["value"] for row in rows if row["key"] == "_g4_duplicate"]
            assert same(typed, [{"boolean": True, "fractional": 1.0, "integer": 1}])
            assert same(duplicate, ["different", "repeat", "repeat"])
            stock = [row for row in rows if row["key"] == "_reduced_stock"]
            expected = (
                [{"key": "_reduced_stock", "value": str(item["quantity"])}]
                if order["stock_reduced"]
                else []
            )
            assert same(stock, expected)
            item["meta_data"] = [row for row in rows if row["key"] != "_reduced_stock"]
    return {
        role: {
            "immutable": order["immutable"],
            "items": order["items"],
            "order_metadata": order["data"]["meta_data"],
        }
        for role, order in orders.items()
    }


def proof(label):
    result = wp("eval-file", str(ROOT / "tools/v2-runtime/gate4-hpos-v1-proof.php"))
    marker = b"SR_G4_HPOS="
    at = result.stdout.rfind(marker)
    assert at >= 0
    value = json.loads(result.stdout[at + len(marker) :])
    assert value["ok"] and value["run"] == RUN
    assert_hpos(value["helper_snapshot"])
    assert set(value["native_objects"]) == {
        "v1_success",
        "v1_retry",
        "v1_malformed",
        "v1_guard",
        "v1_stock",
        "v1_probe",
        "v2_pending",
    }
    assert all(row["datastore"] == HPOS for row in value["native_objects"].values())
    assert {role: row["id"] for role, row in value["native_objects"].items()} == {
        role: row["data"]["id"] for role, row in value["helper_snapshot"]["orders"].items()
    }
    ids = [row["id"] for row in value["native_objects"].values()]
    assert all(type(id) is int and id > 0 for id in ids) and len(set(ids)) == len(ids)
    write(OUT / ("hpos-object-proof-" + label + ".json"), value)
    record(
        "NATIVE_HPOS_OBJECT_AND_SQL_PROOF_" + label,
        receipt={
            "path": str((OUT / ("hpos-object-proof-" + label + ".json")).relative_to(ROOT)),
            **pin(OUT / ("hpos-object-proof-" + label + ".json")),
        },
    )
    return value


def pay(role, outcome, label, kind="valid"):
    before, after, rows = g4.pay(role, outcome, label, kind)
    assert_hpos(before)
    assert_hpos(after)
    assert same(historical_payload(before), historical_payload(after)), label
    assert set(before["orders"]) == set(after["orders"])
    for other in before["orders"]:
        if other != role or (not has(rows, "processor_entered") and label not in NAMED_REFUSALS):
            assert same_order(before["orders"][other], after["orders"][other]), label
    if not has(rows, "processor_entered"):
        assert same(before["products"], after["products"]), label
    if label in NAMED_REFUSALS:
        audit_file = PRIVATE / ("gateway-selection-" + label + ".json")
        audit = json.loads(audit_file.read_text())
        receipt = json.loads((PRIVATE / ("request-" + label + ".json")).read_text())
        arguments = (
            audit,
            before,
            after,
            role,
            label,
            rows,
            receipt,
            PRIVATE / "wordpress",
            json.loads((PRIVATE / "site-at-start.json").read_text()),
            RUN,
        )
        validated = validate_gateway_selection(*arguments)
        controls = gateway_selection_controls(*arguments)
        record(
            "ATTRIBUTED_NATIVE_GATEWAY_SAVE_BEFORE_REFUSAL_" + label,
            attribution=validated,
            controls=controls,
            audit_receipt={"path": str(audit_file.relative_to(ROOT)), **pin(audit_file)},
        )
    return before, after, rows


def clone_private_code(expected_source):
    """APFS independent copy-on-write files; never hardlinks or fallback copies."""
    reserve = 1024**3
    free_before = shutil.disk_usage(PRIVATE).free
    assert free_before >= reserve, "Insufficient private fixture reserve"
    library = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
    clone = library.clonefile
    clone.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    clone.restype = ctypes.c_int

    def regular_clone(source, destination):
        source, destination = Path(source), Path(destination)
        assert source.is_file() and not source.is_symlink()
        assert not source.stat().st_mode & (stat.S_ISUID | stat.S_ISGID)
        assert not destination.exists() and not destination.is_symlink()
        if clone(os.fsencode(source), os.fsencode(destination), 0) != 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))
        assert source.stat().st_ino != destination.stat().st_ino
        assert stat.S_IMODE(source.stat().st_mode) == stat.S_IMODE(destination.stat().st_mode)
        return str(destination)

    canary = PRIVATE / "clone-isolation-canary"
    canary.mkdir()
    source = canary / "source.bin"
    source.write_bytes(b"Synthetic private clone isolation\n" * 4096)
    source.chmod(0o600)
    destination = canary / "clone.bin"
    source_pin = pin(source)
    regular_clone(source, destination)
    assert pin(destination) == source_pin
    destination.write_bytes(b"Changed clone only\n")
    assert pin(source) == source_pin and source.stat().st_mode & 0o777 == 0o600
    assert pin(destination) != source_pin

    original = (ORIGINAL / "wordpress").resolve()
    target = PRIVATE / "wordpress"
    expected = {
        name: row
        for name, row in expected_source.items()
        if not name.startswith("wp-content/uploads/")
    }
    count = 0
    for directory, directories, files in os.walk(original, followlinks=False):
        if Path(directory) == original / "wp-content":
            directories[:] = [name for name in directories if name != "uploads"]
        assert not any((Path(directory) / name).is_symlink() for name in directories + files)

    def copy_file(src, dst):
        nonlocal count
        src, dst = Path(src), Path(dst)
        assert src.resolve().is_relative_to(original)
        assert dst.parent.resolve().is_relative_to(target.resolve())
        result = regular_clone(src, dst)
        count += 1
        return result

    shutil.copytree(
        original,
        target,
        ignore=lambda directory, names: (
            ["uploads"] if Path(directory) == original / "wp-content" else []
        ),
        copy_function=copy_file,
    )
    assert count == len(expected) and base.inventory(target) == expected
    evidence = PRIVATE / "code-clone-verification.json"
    write(
        evidence,
        {
            "method": "macOS clonefile flags0; no fallback",
            "files": expected,
            "cloned_regular_files": count,
            "source_and_destination_file_census_equal_before_config_edit": True,
            "write_isolation_canary": {
                "source_unchanged": source_pin,
                "clone_after_write": pin(destination),
                "distinct_inodes": True,
                "source_mode": "0600",
            },
            "filesystem_available_before": free_before,
            "filesystem_available_after_clone": shutil.disk_usage(PRIVATE).free,
            "reserve_bytes": reserve,
            "limits": "Concurrent filesystem use; reserve cannot prevent later ENOSPC. File bytes and modes verified; ACLs/shared OS-library bytes not qualified.",
        },
    )
    record(
        "APFS_PRIVATE_CODE_CLONE_ISOLATION_AND_COMPLETE_FILE_CENSUS",
        receipt={"path": str(evidence.relative_to(ROOT)), **pin(evidence)},
    )


def setup(expected_source):
    containment()
    clone_private_code(expected_source)
    config = PRIVATE / "wordpress/wp-config.php"
    body = config.read_text()
    assert body.count("/tmp/sr-gate4-01a0f768.sock") == 1
    config.write_text(body.replace("/tmp/sr-gate4-01a0f768.sock", SOCKET))
    (PRIVATE / "mysql").mkdir()
    assert shutil.disk_usage(PRIVATE).free >= 1024**3, "Insufficient fresh database reserve"
    command(
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
    base.start(SOCKET, PRIVATE / "mysql", False)
    base.sql(
        SOCKET,
        "CREATE DATABASE sr_release_fixture CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        False,
    )
    query = (
        "<?php $m=new mysqli('localhost','root','','sr_release_fixture',0,"
        + json.dumps(SOCKET)
        + ");echo json_encode($m->query('SELECT @@socket,@@skip_networking,@@event_scheduler')->fetch_row());"
    )
    p = PRIVATE / "sql-canary.php"
    p.write_text(query)
    observed = json.loads(command(["/usr/bin/sandbox-exec", "-p", PROFILE, "php", str(p)]).stdout)
    assert observed == [SOCKET, "1", "OFF"]
    record("PREBOOTSTRAP_CONTAINMENT_AND_PRIVATE_SQL", sql_identity=observed)
    wp(
        "core",
        "install",
        "--url=http://127.0.0.1:18362",
        "--title=Synthetic populated fixture",
        "--admin_user=gate4_synthetic",
        "--admin_password=synthetic-local-only-no-remote-authority",
        "--admin_email=fixture@example.invalid",
        "--skip-email",
    )
    wp("plugin", "activate", *PLUGINS)
    wp("theme", "activate", "skyyrose-flagship-2")
    native("initialize")
    native("writers", "closed")
    switched = native("switch", "yes")
    assert switched["authority"] == "yes" and not switched["refused"] and switched["pending"] == 0
    empty = inspect()
    # The unchanged PHP helper encodes its empty array as JSON [], before any role exists.
    assert empty["hpos"] and empty["authority"] == "yes" and empty["orders"] == []
    assert empty["runtime"]["datastore"] == HPOS
    record("FRESH_EMPTY_HPOS_AUTHORITY_VERIFIED", switch=switched, snapshot=empty)
    native("writers", "open")
    write(PRIVATE / "site-at-start.json", base.inventory(PRIVATE / "wordpress"))
    REPORT["site_code_at_start"] = pin(PRIVATE / "site-at-start.json")
    REPORT["toolchain"] = {
        name: {
            "resolved_path": str(Path(shutil.which(name)).resolve()),
            **pin(Path(shutil.which(name)).resolve()),
        }
        for name in ["php", "mariadb", "mariadbd", "wp", "python3"]
    }
    assert Path(base.DAEMON).resolve() == Path(REPORT["toolchain"]["mariadbd"]["resolved_path"])
    assert pin(Path(sys.executable).resolve()) == {
        k: v for k, v in REPORT["toolchain"]["python3"].items() if k != "resolved_path"
    }
    REPORT["executing_python"] = {
        "resolved_path": str(Path(sys.executable).resolve()),
        "version": sys.version,
    }


def cases():
    native("seed")
    seed = inspect()
    assert_hpos(seed)
    proof("seed-pre-conversion")
    seed_history = historical_payload(seed)
    history_controls = []
    for mutation in ["bool-to-int", "duplicate-removed", "order-metadata-added", "stock-row-added"]:
        altered = json.loads(canonical(seed))
        order = altered["orders"]["v1_malformed"]
        item = next(iter(order["items"].values()))
        if mutation == "bool-to-int":
            next(row for row in item["meta_data"] if row["key"] == "_g4_typed")["value"][
                "boolean"
            ] = 1
        elif mutation == "duplicate-removed":
            item["meta_data"].remove({"key": "_g4_duplicate", "value": "repeat"})
        elif mutation == "order-metadata-added":
            order["data"]["meta_data"].append({"key": "_unexpected", "value": "change"})
        else:
            item["meta_data"].append({"key": "_reduced_stock", "value": "1"})
        try:
            assert same(seed_history, historical_payload(altered))
        except AssertionError:
            history_controls.append({"mutation": mutation, "status": "PASS_REFUSED_HISTORY_CHANGE"})
        else:
            raise AssertionError("Historical payload validator accepted " + mutation)
    write(
        OUT / "historical-payload-controls.json",
        {"status": "PASS_RETAINED_PAYLOAD_COPY_CONTROLS", "controls": history_controls},
    )
    index_controls = []
    for mutation in [
        "changed-value",
        "duplicate-value",
        "missing-row",
        "changed-public-value",
        "duplicate-public-key",
    ]:
        bad = json.loads(canonical(seed["orders"]))
        order = bad["v1_malformed"]
        key = "_billing_address_index"
        if mutation == "changed-value":
            order["address_indexes"][key][0] += "changed"
        elif mutation == "duplicate-value":
            order["address_indexes"][key] *= 2
        elif mutation == "missing-row":
            order["address_indexes"][key] = []
        elif mutation == "changed-public-value":
            order["data"]["meta_data"].append({"key": key, "value": "changed"})
        else:
            order["data"]["meta_data"].extend(
                [{"key": key, "value": order["address_index_expectations"][key]}] * 2
            )
        try:
            semantic_orders(bad)
        except AssertionError:
            index_controls.append(
                {
                    "mutation": mutation,
                    "status": "PASS_REFUSED_MODIFIED_RETAINED_NATIVE_PAYLOAD",
                }
            )
        else:
            raise AssertionError("Address index validator accepted " + mutation)
    semantic_orders(seed["orders"])
    write(
        OUT / "address-index-negative-controls.json",
        {
            "status": "PASS_PAYLOAD_VALIDATOR_CONTROLS",
            "authentication": "NOT_APPLICABLE",
            "controls": index_controls,
            "scope": "Modified copies of actual native fresh-read payload; no new native database corruption controls",
        },
    )
    type_controls = []
    for mutation in ["bool-to-int", "float-to-int"]:
        native("type-control", mutation)
        observed = inspect()
        assert not same(
            seed["orders"]["v1_malformed"]["items"], observed["orders"]["v1_malformed"]["items"]
        )
        type_controls.append(
            {"mutation": mutation, "status": "PASS_REFUSED_TYPED_NATIVE_ROUNDTRIP"}
        )
        native("type-control", "restore")
        assert same(
            seed["orders"]["v1_malformed"]["items"],
            inspect()["orders"]["v1_malformed"]["items"],
        )
    assert not same({"value": True}, {"value": 1}) and not same({"value": 1.0}, {"value": 1})
    assert not same(["repeat", "repeat", "different"], ["repeat", "different"])
    write(
        OUT / "typed-comparison-controls.json",
        {
            "status": "PASS_NATIVE_PERSISTENCE_ENCODING_DECODING_TYPED_COMPARISON",
            "controls": type_controls,
            "negative_multiplicity_refused": True,
        },
    )
    native("convert")
    converted = inspect()
    assert same(seed_history, historical_payload(converted))
    assert same(
        {k: v["immutable"] for k, v in seed["orders"].items()},
        {k: v["immutable"] for k, v in converted["orders"].items()},
    )
    record("EXACT_V1_V2_PERSISTED_AND_CONVERTED", snapshot=converted)
    for role, label, kind in [
        ("v1_success", "bad-nonce", "bad-nonce"),
        ("v1_success", "bad-key", "bad-key"),
    ]:
        before, after, rows = pay(role, "success", label, kind)
        assert has(rows, "processor_entered") == 0 and same_order(
            before["orders"][role], after["orders"][role]
        )
        record("REQUEST_REFUSED_" + label, events=rows)
    for mutation in ["missing-id", "ambiguous-sku"]:
        native("mutate-v1", mutation)
        before, after, rows = pay("v1_malformed", "success", "v1-" + mutation)
        assert (
            has(rows, "processor_entered") == 0
            and not after["orders"]["v1_malformed"]["data"]["date_paid"]
        )
        native("mutate-v1", "restore")
        record("RECORDED_V1_IDENTITY_REFUSED_" + mutation, events=rows)
    native("journal-control", "active")
    before, after, rows = pay("v1_guard", "success", "active-journal")
    assert has(rows, "processor_entered") == 0
    native("journal-control", "restore")
    record("ACTIVE_JOURNAL_PAYMENT_REFUSED", events=rows)
    before, after, rows = pay("v1_success", "success", "v1-success")
    assert (
        has(rows, "processor_entered")
        == has(rows, "processor_completed")
        == has(rows, "redirect")
        == 1
    )
    assert after["orders"]["v1_success"]["data"]["date_paid"] and after["orders"]["v1_success"][
        "data"
    ]["transaction_id"] == "g4p-offline-" + str(after["orders"]["v1_success"]["data"]["id"])
    assert (
        after["orders"]["v1_success"]["stock_reduced"]
        and after["products"]["main"]["stock"] == before["products"]["main"]["stock"] - 1
    )
    paid = after["orders"]["v1_success"]
    before, after, rows = pay("v1_success", "success", "v1-duplicate")
    assert (
        has(rows, "processor_entered") == 0
        and same_order(after["orders"]["v1_success"], paid)
        and same(after["products"], before["products"])
    )
    record("ACTUAL_V1_PAYMENT_DUPLICATE_NATIVE_STOCK", events=rows, paid=paid)
    before, after, rows = pay("v1_retry", "failure", "v1-failure")
    assert (
        has(rows, "processor_entered") == 1
        and has(rows, "processor_completed") == 0
        and same(after["products"], before["products"])
        and not after["orders"]["v1_retry"]["data"]["date_paid"]
    )
    before, after, rows = pay("v1_retry", "success", "v1-retry")
    assert (
        has(rows, "processor_completed") == 1
        and after["orders"]["v1_retry"]["stock_reduced"]
        and after["products"]["main"]["stock"] == before["products"]["main"]["stock"] - 1
    )
    record("V1_FAILURE_RETRY_NATIVE_STOCK", events=rows)
    native("prepare-stock", "stock")
    paths = native("stock-paths")
    assert (
        paths["native_stock_error_present"]
        and not paths["rendered_payment_form"]
        and paths["rendered_stock_error"]
    )
    record("CLASSIC_RENDER_AND_STORE_API_STOCK_SEPARATE", evidence=paths)
    before, after, rows = pay("v1_stock", "success", "v1-stock-refusal")
    assert (
        has(rows, "processor_entered") == has(rows, "gateway_native_stock_refusal") == 1
        and has(rows, "processor_completed") == 0
        and same(after["products"], before["products"])
        and not after["orders"]["v1_stock"]["data"]["date_paid"]
    )
    record("GATEWAY_LAYER_NATIVE_STOCK_REFUSED_NOT_HANDLER", events=rows)
    native("restore-stock")
    before, after, rows = pay("v1_stock", "success", "v1-stock-retry")
    assert (
        has(rows, "processor_completed") == 1
        and after["products"]["stock"]["stock"] == before["products"]["stock"]["stock"] - 1
    )
    native("prepare-stock", "probe")
    before, after, rows = pay("v1_probe", "unchecked-stock-probe", "bare-handler-probe")
    record(
        "BARE_CLASSIC_HANDLER_STOCK_OBSERVATION",
        processor_entries=has(rows, "processor_entered"),
        completed=has(rows, "processor_completed"),
        before_stock=before["products"]["probe"]["stock"],
        after_stock=after["products"]["probe"]["stock"],
        paid=bool(after["orders"]["v1_probe"]["data"]["date_paid"]),
        meaning="Fake processor bypasses only the failed-stock check and retains existing-order validation; no native-handler stock enforcement or real gateway behavior inferred",
    )
    final = inspect()
    assert_hpos(final)
    assert same(seed_history, historical_payload(final))
    assert same(
        {k: v["immutable"] for k, v in seed["orders"].items()},
        {k: v["immutable"] for k, v in final["orders"].items()},
    )
    proof("final-paid-and-refused")
    record("HPOS_V1_REQUEST_MATRIX_COMPLETE", snapshot=final)


def main():
    PRIVATE.mkdir(parents=True, exist_ok=False)
    OUT.mkdir(parents=True, exist_ok=False)
    g4.configure()
    protected = {
        name: base.inventory(ORIGINAL / name) for name in ["wordpress", "mysql", "restore/mysql"]
    }
    original_cold = ROOT / ".artifacts/release-gates-20261019/runtime-official/mysql"
    original_pins = base.inventory(original_cold)
    prior = (
        ROOT
        / ".artifacts/release-gates-20261019/gate4-populated/qualified-retention-1792437370289798000.json"
    )
    prior_manifest = (
        ROOT
        / "tasks/release-gates-20261019/gate4-populated/packet-1792437370289798000/continuation-manifest.json"
    )
    prior_index = prior_manifest.with_name("evidence-index.json")
    assert (
        pin(prior_manifest)["sha256"]
        == "decc5b48f8edf93fcf54ecda1bd8609dea73d9b1eb59004653072214f69a17f8"
    )
    assert pin(prior_index) == json.loads(prior_manifest.read_text())["evidence_index"]
    prior_pin = pin(prior)
    assert prior_pin == json.loads(prior_index.read_text())[str(prior.relative_to(ROOT))]
    prior_files = json.loads(prior.read_text())["files"]
    sources = [
        Path(__file__),
        Path(g4.__file__),
        prior_manifest,
        prior_index,
        Path(base.__file__),
        ROOT / "tools/v2-runtime/gate4-hpos-v1-proof.php",
        ROOT / "tools/v2-runtime/gate4-hpos-v1-pay-observer.php",
        ROOT / "tools/v2-runtime/gate4_gateway_selection.py",
        ROOT / "tools/v2-runtime/gate4-populated-fixture.php",
        ROOT / "tools/v2-runtime/gate4_refund_attribution.py",
        ROOT / "tools/v2-runtime/variation-migration-core-populated.php",
        ROOT / "logo-registry.json",
        ROOT / "skyyrose/core/product.py",
        ROOT / ".artifacts/release-gates-20261019/gate4-populated/historical-producer-function.php",
        ROOT / ".artifacts/release-gates-20261019/gate4-populated/historical-producer-blob.php",
        ROOT
        / ".artifacts/release-gates-20261019/gate4-populated/historical-producer-provenance.json",
        ROOT / "tasks/release-gates-20261019/gate4-hpos-v1/PLAN.md",
    ]
    REPORT["source_head"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    REPORT["source_pins"] = {str(p.relative_to(ROOT)): pin(p) for p in sources}
    REPORT["prior_qualified_index"] = {"path": str(prior.relative_to(ROOT)), **prior_pin}
    complete = False
    errors = []
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
            ).returncode
            != 0
        )
        setup(protected["wordpress"])
        cases()
        assert all(pin(ROOT / p) == value for p, value in REPORT["source_pins"].items())
        complete = True
    except BaseException as error:
        REPORT["failure"] = {"type": type(error).__name__, "message": str(error)[:1500]}
        raise
    finally:
        service = g4.cleanup_owned()
        REPORT["service_cleanup_errors"] = service
        REPORT["owned_services_stopped"] = not service
        errors.extend(service)
        REPORT["protected_originals_unchanged"] = False
        REPORT["prior_qualified_fixture_unchanged"] = False
        try:
            assert protected == {name: base.inventory(ORIGINAL / name) for name in protected}
            assert original_pins == base.inventory(original_cold)
            REPORT["protected_originals_unchanged"] = True
            assert pin(prior) == prior_pin
            for relative, expected in prior_files.items():
                p = ROOT / relative
                assert {**pin(p), "mode": p.stat().st_mode & 0o777} == expected, relative
            REPORT["prior_qualified_fixture_unchanged"] = True
        except BaseException as error:
            errors.append({"step": "protected-inventories", "error": type(error).__name__})
        REPORT["cleanup_errors"] = errors
        REPORT["status"] = (
            "FAIL_CLEANUP"
            if errors
            else ("PASS_PRIVATE_HPOS_NATIVE_V1_PAYMENTS" if complete else "FAIL_EXECUTION")
        )
        write(OUT / "results.json", REPORT)
        if errors:
            raise RuntimeError("Owned cleanup/protected evidence failure")
    print(REPORT["status"])


if __name__ == "__main__":
    main()
