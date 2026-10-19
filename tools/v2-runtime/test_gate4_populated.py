"""New, contained native populated sync and historical payment qualification."""

from __future__ import annotations
import hashlib
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import gate4_restore_local as base

if not __debug__:
    raise RuntimeError("Assertions required")
ROOT = Path(__file__).resolve().parents[2]
RUN = str(time.time_ns())
PRIVATE = ROOT / ".artifacts/release-gates-20261019/gate4-populated" / ("run-" + RUN)
OUT = ROOT / "tasks/release-gates-20261019/gate4-populated" / ("run-" + RUN)
SOCKET = "/tmp/sr-g4-pop-" + RUN[-12:] + ".sock"
PROFILE = (
    '(version 1)(allow default)(deny network*)(allow network-outbound (remote unix-socket (literal "/private'
    + SOCKET
    + '")))'
)
ORIGINAL = ROOT / ".artifacts/release-gates-20261019/gate4-local"
PLUGINS = [
    "woocommerce",
    "stripe-tax-for-woocommerce",
    "woocommerce-paypal-payments",
    "woocommerce-shipping",
    "woocommerce-gateway-stripe",
    "woocommerce-services",
    "woocommerce-payments",
]
SEQUENCE = 0
REPORT = {
    "schema": "skyyrose.private-populated-native.v1",
    "run": RUN,
    "status": "INCOMPLETE",
    "authentication": "NOT_APPLICABLE",
    "steps": [],
    "limits": [
        "New synthetic seven-commerce-plugin PHP8.5.6/MariaDB13 fixture only; not installed parity",
        "PHP native existing-order entrypoint/fakegateway; no HTTP/browser or real payment qualification",
        "Bare classic handler and fakegateway native stock checks are separate",
        "First-table CHECK failure is not transaction-wide rollback proof",
        "Guard-only core derivative has no inherited31-case execution acceptance",
    ],
}


def pin(path):
    with path.open("rb") as f:
        return {
            "sha256": hashlib.file_digest(f, "sha256").hexdigest(),
            "bytes": path.stat().st_size,
        }


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def record(name, **data):
    REPORT["steps"].append({"step": name, **data})
    write(OUT / "results.json", REPORT)


def command(args, data=None, expected=(0,), timeout=120):
    global SEQUENCE
    SEQUENCE += 1
    p = OUT / f"command-{SEQUENCE:05}.txt"
    try:
        r = subprocess.run(
            args,
            input=data,
            capture_output=True,
            timeout=timeout,
            env={**os.environ, "SR_POPULATED_RUN": RUN},
        )
    except subprocess.TimeoutExpired as error:
        p.write_bytes((error.stdout or b"") + (error.stderr or b""))
        raise
    p.write_bytes(r.stdout + r.stderr)
    write(
        OUT / f"command-{SEQUENCE:05}.json",
        {"argv": args, "exit": r.returncode, "receipt": p.name, **pin(p)},
    )
    assert r.returncode in expected, (p.name, r.returncode)
    return r


def wp(*args, expected=(0,)):
    return command(
        [
            "/usr/bin/sandbox-exec",
            "-p",
            PROFILE,
            "php",
            "-d",
            "memory_limit=1G",
            "-d",
            "error_reporting=24575",
            "/opt/homebrew/bin/wp",
            "--path=" + str(PRIVATE / "wordpress"),
            "--skip-plugins=" + ",".join(base.RUNTIME["wp_skip_plugins"]),
            *args,
        ],
        expected=expected,
    )


def native(mode, *args, expected=(0,), payment=False):
    r = wp(
        "eval-file",
        str(ROOT / "tools/v2-runtime/gate4-populated-fixture.php"),
        mode,
        *map(str, args),
        expected=expected,
    )
    if payment:
        return r.returncode
    marker = b"SR_G4_POP="
    at = r.stdout.rfind(marker)
    assert at >= 0, r.stdout[-500:]
    value = json.loads(r.stdout[at + len(marker) :])
    assert value.get("ok") or r.returncode != 0, value
    return value


def sql(query):
    return base.sql(SOCKET, query)


def inspect():
    return native("inspect")["snapshot"]


def events(label):
    p = PRIVATE / "events.jsonl"
    return (
        [
            json.loads(line)
            for line in p.read_text().splitlines()
            if json.loads(line)["request"] == label
        ]
        if p.exists()
        else []
    )


def pay(role, outcome, label, kind="valid"):
    before = inspect()
    native("pay", role, outcome, kind, label, payment=True)
    receipt = json.loads((PRIVATE / ("request-" + label + ".json")).read_text())
    assert receipt["run"] == RUN and receipt["label"] == label
    after = inspect()
    rows = events(label)
    write(
        OUT / ("payment-" + label + ".json"),
        {
            "role": role,
            "outcome": outcome,
            "request_kind": kind,
            "before": before,
            "after": after,
            "events": rows,
            "shutdown_receipt": str((PRIVATE / ("request-" + label + ".json")).relative_to(ROOT)),
        },
    )
    assert before["orders"][role]["immutable"] == after["orders"][role]["immutable"], label
    return before, after, rows


def has(rows, event):
    return sum(x["event"] == event for x in rows)


def scope():
    result = {}
    for suffix in [
        "posts",
        "postmeta",
        "wc_orders",
        "wc_order_addresses",
        "wc_order_operational_data",
        "wc_orders_meta",
        "woocommerce_order_items",
        "woocommerce_order_itemmeta",
    ]:
        table = "wp_" + suffix
        cols = (
            sql(
                "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='"
                + table
                + "' ORDER BY ORDINAL_POSITION;"
            )
            .decode()
            .splitlines()
        )
        assert cols and all(x.replace("_", "").isalnum() for x in cols)
        expr = (
            "CONCAT_WS(':',"
            + ",".join(
                "IF(`" + c + "` IS NULL,'N',CONCAT('V',HEX(CAST(`" + c + "` AS BINARY))))"
                for c in cols
            )
            + ")"
        )
        rows = sql("SELECT " + expr + " AS x FROM `" + table + "` ORDER BY BINARY x;")
        p = PRIVATE / "sql-preimages" / f"{SEQUENCE:05}-{table}.txt"
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(rows)
        result[table] = {
            "row_sha256": hashlib.sha256(rows).hexdigest(),
            "rows": len(rows.splitlines()),
            "preimage": str(p.relative_to(ROOT)),
        }
    return result


def row_pins(value):
    return {k: (v["row_sha256"], v["rows"]) for k, v in value.items()}


def next_batch():
    return native("next")


def batch():
    before = next_batch()
    assert before["pending"] > 0 and before["batch"], before
    value = native("batch")
    assert value["batch"] == before["batch"]
    return value


def collision_control(label):
    pending = next_batch()
    assert pending["batch"]
    order_id = int(pending["batch"][0])
    before = scope()
    foreign = "synthetic-foreign-" + RUN
    restoration = {}
    if pending["hpos"]:
        old_type = (
            sql("SELECT post_type FROM wp_posts WHERE ID=" + str(order_id) + ";").decode().strip()
        )
        assert old_type in ["shop_order", "shop_order_refund", "shop_order_placehold"]
        sql(
            "UPDATE wp_posts SET post_type='post' WHERE ID="
            + str(order_id)
            + " AND post_type='"
            + old_type
            + "';"
        )
        restoration = {"kind": "post_type", "old_type": old_type}
    else:
        exists = sql("SELECT COUNT(*) FROM wp_wc_orders WHERE id=" + str(order_id) + ";").strip()
        if exists == b"1":
            meta_id = (
                sql(
                    "SELECT id FROM wp_wc_orders_meta WHERE order_id="
                    + str(order_id)
                    + " AND meta_key='_g4_owner' AND meta_value='"
                    + RUN
                    + "';"
                )
                .decode()
                .strip()
            )
            assert meta_id.isdigit()
            sql(
                "UPDATE wp_wc_orders_meta SET meta_value='"
                + foreign
                + "' WHERE id="
                + meta_id
                + " AND meta_value='"
                + RUN
                + "';"
            )
            restoration = {"kind": "owner_value", "meta_id": int(meta_id)}
        else:
            assert exists == b"0"
            sql(
                "INSERT INTO wp_wc_orders(id,type,status,currency,total_amount) VALUES("
                + str(order_id)
                + ",'shop_order','wc-pending','USD',0);"
            )
            meta_id = (
                sql(
                    "INSERT INTO wp_wc_orders_meta(order_id,meta_key,meta_value) VALUES("
                    + str(order_id)
                    + ",'_g4_owner','"
                    + foreign
                    + "'); SELECT LAST_INSERT_ID();"
                )
                .decode()
                .strip()
            )
            assert meta_id.isdigit()
            restoration = {"kind": "inserted_foreign", "meta_id": int(meta_id)}
    held = scope()
    result = native("preflight", order_id, expected=(3,))
    assert not result["ok"] and "Caller collision guard" in result["error"]
    assert row_pins(held) == row_pins(scope()), "Refusal changed controlled rows"
    if restoration["kind"] == "post_type":
        sql(
            "UPDATE wp_posts SET post_type='"
            + restoration["old_type"]
            + "' WHERE ID="
            + str(order_id)
            + " AND post_type='post'; SELECT ROW_COUNT();"
        )
    else:
        meta_id = str(restoration["meta_id"])
        if restoration["kind"] == "owner_value":
            result_rows = sql(
                "UPDATE wp_wc_orders_meta SET meta_value='"
                + RUN
                + "' WHERE id="
                + meta_id
                + " AND order_id="
                + str(order_id)
                + " AND meta_key='_g4_owner' AND meta_value='"
                + foreign
                + "'; SELECT ROW_COUNT();"
            )
            assert result_rows.strip() == b"1"
        else:
            result_rows = sql(
                "DELETE FROM wp_wc_orders_meta WHERE id="
                + meta_id
                + " AND order_id="
                + str(order_id)
                + " AND meta_key='_g4_owner' AND meta_value='"
                + foreign
                + "'; SELECT ROW_COUNT();"
            )
            assert result_rows.strip() == b"1"
            result_rows = sql(
                "DELETE FROM wp_wc_orders WHERE id="
                + str(order_id)
                + " AND type='shop_order' AND status='wc-pending' AND currency='USD' AND total_amount=0; SELECT ROW_COUNT();"
            )
            assert result_rows.strip() == b"1"
    after = scope()
    assert row_pins(before) == row_pins(after), "Collision preimage not restored"
    record(
        "CALLER_DESTINATION_COLLISION_REFUSED_" + label,
        order_id=order_id,
        result=result,
        before=before,
        held=held,
        after=after,
        limits="Common native-batch caller preflight tested; not a native ownership-rejection claim; allocator never lowered",
    )


def drain(label):
    batches = []
    for _ in range(100):
        pending = next_batch()
        if pending["pending"] == 0:
            assert pending["batch"] == []
            break
        batches.append(batch())
    else:
        raise AssertionError("Native drain bound exceeded")
    record("NATIVE_DRAIN_" + label, batches=batches, terminal=next_batch())


def equivalence(label):
    before = scope()
    left = native("compare", "cpt")["orders"]
    middle = scope()
    right = native("compare", "hpos")["orders"]
    after = scope()
    write(
        OUT / ("equivalence-" + label + ".json"),
        {"cpt": left, "hpos": right, "before": before, "middle": middle, "after": after},
    )
    assert (
        row_pins(before) == row_pins(middle) == row_pins(after)
    ), "Representation reads wrote order data"
    assert left == right, "Native cross-store semantic mismatch: " + label
    return left


def cold(label):
    base.stop(SOCKET)
    for child in base.PROCESSES:
        child.wait(timeout=20)
    assert all(child.poll() is not None for child in base.PROCESSES)
    target = PRIVATE / ("cold-" + label)
    shutil.copytree(PRIVATE / "mysql", target)
    source = base.inventory(PRIVATE / "mysql")
    assert source == base.inventory(target)
    write(PRIVATE / ("cold-" + label + ".json"), source)
    base.start(SOCKET, PRIVATE / "mysql", False)
    record(
        "OWNED_COLD_CHECKPOINT_" + label,
        files=len(source),
        inventory=pin(PRIVATE / ("cold-" + label + ".json")),
    )


def containment():
    fn = """function probe() { $out=[]; foreach(['tcp://203.0.113.1:443','tcp://127.0.0.1:18499'] as $target){$e=0;$s=@stream_socket_client($target,$e,$m,1);if($s!==false||$e!==1){throw new Exception('TCP denial not EPERM');}$out[]=$e;} $s=socket_create(AF_INET,SOCK_DGRAM,SOL_UDP);$r=@socket_sendto($s,'x',1,0,'203.0.113.1',443);$e=socket_last_error($s);if($r!==false||$e!==1){throw new Exception('UDP denial not EPERM');}socket_close($s);$out[]=$e;return $out;}"""
    child = fn + " echo json_encode(probe());"
    code = (
        fn
        + "$p=probe();$spec=[1=>['pipe','w'],2=>['pipe','w']];$c=proc_open([PHP_BINARY,'-r',"
        + "base64_decode('"
        + base64.b64encode(child.encode()).decode()
        + "')"
        + "],$spec,$pipes);$body=stream_get_contents($pipes[1]);$err=stream_get_contents($pipes[2]);$exit=proc_close($c);if($exit!==0){throw new Exception('Inherited child denial failed');}echo json_encode(['parent'=>$p,'child'=>json_decode($body,true)]);"
    )
    result = command(["/usr/bin/sandbox-exec", "-p", PROFILE, "php", "-r", code])
    value = json.loads(result.stdout)
    assert value == {"parent": [1, 1, 1], "child": [1, 1, 1]}
    write(
        OUT / "containment.json",
        {"profile": PROFILE, "prebootstrap_denials": value, "authentication": "NOT_APPLICABLE"},
    )


def configure():
    base.PRIVATE = PRIVATE
    base.OUT = OUT
    base.RUNS = OUT / "command-failures"
    base.RUNS.mkdir()
    base.SOURCE_SOCKET = SOCKET
    base.RESTORE_SOCKET = "/tmp/unused-g4-pop-" + RUN[-12:] + ".sock"
    base.RESTORE = PRIVATE / "unused-restore"
    base.RUN_ID = RUN
    base.REPORT = REPORT


def main():
    PRIVATE.mkdir(parents=True, exist_ok=False)
    OUT.mkdir(parents=True, exist_ok=False)
    configure()
    protected = {
        name: base.inventory(ORIGINAL / name) for name in ["wordpress", "mysql", "restore/mysql"]
    }
    original_cold = ROOT / ".artifacts/release-gates-20261019/runtime-official/mysql"
    original_pins = base.inventory(original_cold)
    sources = [
        Path(__file__),
        ROOT / "tools/v2-runtime/gate4-populated-fixture.php",
        ROOT / "tools/v2-runtime/variation-migration-core-populated.php",
        Path(base.__file__),
    ]
    REPORT["source_head"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    REPORT["source_pins"] = {str(p.relative_to(ROOT)): pin(p) for p in sources}
    REPORT["profile"] = PROFILE
    complete = False
    cleanup = []
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
        containment()
        shutil.copytree(
            ORIGINAL / "wordpress",
            PRIVATE / "wordpress",
            ignore=lambda directory, names: (
                ["uploads"] if Path(directory) == ORIGINAL / "wordpress/wp-content" else []
            ),
        )
        config = PRIVATE / "wordpress/wp-config.php"
        body = config.read_text()
        assert body.count("/tmp/sr-gate4-01a0f768.sock") == 1
        config.write_text(body.replace("/tmp/sr-gate4-01a0f768.sock", SOCKET))
        (PRIVATE / "mysql").mkdir()
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
        observed = json.loads(
            command(["/usr/bin/sandbox-exec", "-p", PROFILE, "php", str(p)]).stdout
        )
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
        write(PRIVATE / "site-at-start.json", base.inventory(PRIVATE / "wordpress"))
        REPORT["site_code_at_start"] = pin(PRIVATE / "site-at-start.json")
        REPORT["toolchain"] = {
            name: pin(Path(shutil.which(name)).resolve())
            for name in ["php", "mariadb", "mariadbd", "wp", "python3"]
        }
        native("seed")
        seed = inspect()
        native("convert")
        converted = inspect()
        assert {k: v["immutable"] for k, v in seed["orders"].items()} == {
            k: v["immutable"] for k, v in converted["orders"].items()
        }
        record("EXACT_V1_V2_PERSISTED_AND_CONVERTED", snapshot=converted)
        for role, label, kind in [
            ("v1_success", "bad-nonce", "bad-nonce"),
            ("v1_success", "bad-key", "bad-key"),
        ]:
            before, after, rows = pay(role, "success", label, kind)
            assert (
                has(rows, "processor_entered") == 0
                and before["orders"][role] == after["orders"][role]
            )
            record("REQUEST_REFUSED_" + label, events=rows)
        for mutation in ["missing-id", "ambiguous-sku"]:
            native("mutate-v1", mutation)
            _, after, rows = pay("v1_malformed", "success", "v1-" + mutation)
            assert (
                has(rows, "processor_entered") == 0
                and not after["orders"]["v1_malformed"]["data"]["date_paid"]
            )
            native("mutate-v1", "restore")
            record("RECORDED_V1_IDENTITY_REFUSED_" + mutation, events=rows)
        native("journal-control", "active")
        _, after, rows = pay("v1_guard", "success", "active-journal")
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
            and after["orders"]["v1_success"] == paid
            and after["products"] == before["products"]
        )
        record("ACTUAL_V1_PAYMENT_DUPLICATE_NATIVE_STOCK", events=rows, paid=paid)
        before, after, rows = pay("v1_retry", "failure", "v1-failure")
        assert (
            has(rows, "processor_entered") == 1
            and has(rows, "processor_completed") == 0
            and after["products"] == before["products"]
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
            and after["products"] == before["products"]
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
            meaning="No native-handler stock enforcement inferred; intentionally unguarded fake processor, not real gateway behavior",
        )
        native("financial")
        before, after, rows = pay("v2_financial", "success", "v2-financial")
        assert (
            has(rows, "processor_completed") == 1
            and after["products"]["main"]["stock"] == before["products"]["main"]["stock"] - 2
        )
        before = after
        refunded = native("refund")["snapshot"]
        assert refunded["products"]["main"]["stock"] == before["products"]["main"]["stock"] + 1
        record("NATIVE_V2_FINANCIAL_REFUND", snapshot=refunded)
        cold("before-populated-sync")
        for direction, target in [("cpt-to-hpos", "yes"), ("hpos-to-cpt", "no")]:
            native("writers", "open")

            for suffix in ["initial-a", "initial-b", "initial-c"]:
                native("newer", direction + "-" + suffix)
            pending = next_batch()
            assert pending["pending"] > 0
            assert native("switch", target)["refused"]
            first = batch()
            record("INTERRUPTED_BETWEEN_BATCHES_" + direction, first=first, remaining=next_batch())
            time.sleep(1.1)
            native("newer", direction + "-paused")
            newer = inspect()
            collision_control(direction)
            if direction == "cpt-to-hpos":
                selected = next_batch()
                assert selected["batch"]
                bad = int(selected["batch"][0])
                sql(
                    "ALTER TABLE wp_wc_orders ADD CONSTRAINT g4p_owned_check CHECK(id <> "
                    + str(bad)
                    + ");"
                )
                assert sql("SELECT @@check_constraint_checks;").strip() == b"1"
                before_fault = scope()
                outcome = batch()
                after_fault = scope()
                assert row_pins(before_fault) == row_pins(after_fault)
                assert next_batch()["pending"] > 0 and native("switch", target)["refused"]
                sql("ALTER TABLE wp_wc_orders DROP CONSTRAINT g4p_owned_check;")
                record(
                    "NATIVE_FIRST_TABLE_CHECK_FAILURE_NO_PROMOTION",
                    batch=outcome,
                    before=before_fault,
                    after=after_fault,
                )
            drain(direction)
            equivalence(direction)
            native("make-delete", direction)
            drain(direction + "-pre-delete")
            native("delete", direction)
            drain(direction + "-native-delete")
            equivalence(direction + "-after-delete")
            current = inspect()
            assert (
                current["orders"]["newer-" + direction + "-paused"]["immutable"]
                == newer["orders"]["newer-" + direction + "-paused"]["immutable"]
            )
            assert (
                current["orders"]["v2_pending"]["data"]["customer_note"]
                == newer["orders"]["v2_pending"]["data"]["customer_note"]
            )
            native("writers", "closed")
            assert not next_batch()["batch"]
            equivalence(direction + "-quiescent")
            switched = native("switch", target)
            assert not switched["refused"] and switched["authority"] == target
            fresh = inspect()
            assert fresh["hpos"] == (target == "yes")
            record("NATIVE_AUTHORITY_SWITCH_" + direction, switch=switched, snapshot=fresh)
            cold(direction)
        before = scope()
        value = native("batch")
        assert value["batch"] == [] and value["pending_after"] == 0
        after = scope()
        assert row_pins(before) == row_pins(after)
        record("FRESH_EMPTY_RETRY_NOOP")
        assert all(pin(ROOT / path) == value for path, value in REPORT["source_pins"].items())
        complete = True
    except BaseException as error:
        REPORT["failure"] = {"type": type(error).__name__, "message": str(error)[:1500]}
        raise
    finally:
        if base.PROCESSES:
            try:
                live = [p for p in base.PROCESSES if p.poll() is None]
                if live:
                    base.stop(SOCKET)
                for p in base.PROCESSES:
                    p.wait(timeout=20)
            except BaseException as error:
                cleanup.append({"step": "stop-owned", "error": type(error).__name__})
            for child in base.PROCESSES:
                if child.poll() is None:
                    child.terminate()
                    try:
                        child.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait(timeout=10)
        if any(p.poll() is None for p in base.PROCESSES):
            cleanup.append({"step": "owned-child-survived"})
        try:
            assert protected == {name: base.inventory(ORIGINAL / name) for name in protected}
            assert original_pins == base.inventory(original_cold)
            REPORT["protected_originals_unchanged"] = True
        except BaseException as error:
            cleanup.append({"step": "protected-inventories", "error": type(error).__name__})
        REPORT["cleanup_errors"] = cleanup
        REPORT["owned_services_stopped"] = not cleanup
        if complete and not cleanup:
            REPORT["status"] = (
                "PASS_PRIVATE_POPULATED_SYNC_AND_HISTORICAL_PAYMENTS_WITH_EXPLICIT_STOCK_PATH_LIMIT"
            )
        write(OUT / "results.json", REPORT)
    assert complete and not cleanup, REPORT
    print(REPORT["status"])


if __name__ == "__main__":
    main()
