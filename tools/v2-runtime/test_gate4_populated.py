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
SNAPSHOT = 0
RAW_PINS = {}
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
        "Only two source-verified native address-search index exposures are partitioned; raw values/type/multiplicity and all other metadata remain strict",
        "Exact one-index-row requirement belongs to this native-created fixture, not arbitrary installed historical rows",
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
    assert same(before["orders"][role]["immutable"], after["orders"][role]["immutable"]), label
    assert all(row["order_id"] == after["orders"][role]["data"]["id"] for row in rows), label
    assert has(rows, "processor_entered") <= 1 and has(rows, "processor_completed") <= 1
    if has(rows, "processor_completed"):
        assert all(
            has(rows, event) == 1
            for event in [
                "before_pay",
                "validate_fields",
                "processor_entered",
                "native_payment_complete_hook",
                "redirect",
            ]
        )
        paid = after["orders"][role]
        assert has(rows, "handler_returned") == 0 and paid["data"]["date_paid"]
        assert paid["data"]["status"] in ["processing", "completed"]
        assert paid["data"]["transaction_id"] == "g4p-offline-" + str(paid["data"]["id"])
        assert paid["stock_reduced"] is True
    else:
        assert has(rows, "native_payment_complete_hook") == has(rows, "redirect") == 0
        assert has(rows, "handler_returned") == 1
    if kind != "valid":
        assert all(
            has(rows, event) == 0
            for event in [
                "before_pay",
                "validate_fields",
                "processor_entered",
                "processor_completed",
            ]
        )
    return before, after, rows


def has(rows, event):
    return sum(x["event"] == event for x in rows)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def same(left, right):
    return canonical(left) == canonical(right)


def semantic_orders(orders):
    # Retain the unmodified native payload in receipts. Partition only the two
    # source-verified native search indexes; their physical values remain checked.
    result = json.loads(canonical(orders))
    keys = {"_billing_address_index", "_shipping_address_index"}
    for value in result.values():
        expected = value["address_index_expectations"]
        indexes = value["address_indexes"]
        rows = value["data"]["meta_data"]
        if "billing" in value["data"]:
            assert set(expected) == keys and set(indexes) == keys
            for key in keys:
                assert type(expected[key]) is str
                assert same(indexes[key], [expected[key]])
                exposed = [row for row in rows if row["key"] == key]
                assert len(exposed) <= 1
                if exposed:
                    assert type(exposed[0]["value"]) is str and exposed[0]["value"] == expected[key]
        else:
            assert not expected and not indexes
            assert not any(row["key"] in keys for row in rows), "Refund index exemption prohibited"
        value["data"]["meta_data"] = [row for row in rows if row["key"] not in keys]
    return result


def same_orders(left, right):
    return same(semantic_orders(left), semantic_orders(right))


def same_order(left, right):
    return same_orders({"order": left}, {"order": right})


def scope(exclude_order=None, exclude_items=None):
    global SNAPSHOT
    SNAPSHOT += 1
    folder = PRIVATE / "sql-preimages" / f"snapshot-{SNAPSHOT:06}"
    folder.mkdir(parents=True, exist_ok=False)
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
        where = ""
        if exclude_order is not None:
            field = (
                "ID"
                if suffix == "posts"
                else (
                    "id"
                    if suffix == "wc_orders"
                    else "post_id" if suffix == "postmeta" else "order_id"
                )
            )
            if suffix == "woocommerce_order_itemmeta":
                assert exclude_items and all(isinstance(n, int) and n > 0 for n in exclude_items)
                where = " WHERE order_item_id NOT IN (" + ",".join(map(str, exclude_items)) + ")"
            else:
                where = " WHERE `" + field + "`<>" + str(int(exclude_order))
        rows = sql("SELECT " + expr + " AS x FROM `" + table + "`" + where + " ORDER BY BINARY x;")
        p = folder / (table + ".txt")
        with p.open("xb") as output:
            output.write(rows)
        RAW_PINS[str(p.relative_to(ROOT))] = pin(p)
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


def wrong_type_control(label, order_id):
    hpos = next_batch()["hpos"]
    source_table, source_field = ("wp_wc_orders", "type") if hpos else ("wp_posts", "post_type")
    target_table, target_field = ("wp_posts", "post_type") if hpos else ("wp_wc_orders", "type")
    native("preflight", order_id)
    expected = (
        sql(
            "SELECT "
            + source_field
            + " FROM "
            + source_table
            + " WHERE "
            + ("id" if hpos else "ID")
            + "="
            + str(order_id)
            + ";"
        )
        .decode()
        .strip()
    )
    assert expected in ["shop_order", "shop_order_refund"]
    actual = (
        sql("SELECT " + target_field + " FROM " + target_table + " WHERE id=" + str(order_id) + ";")
        .decode()
        .strip()
    )
    assert actual == expected
    wrong = "shop_order_refund" if expected == "shop_order" else "shop_order"
    before = scope()
    assert (
        sql(
            "UPDATE "
            + target_table
            + " SET "
            + target_field
            + "='"
            + wrong
            + "' WHERE id="
            + str(order_id)
            + " AND "
            + target_field
            + "='"
            + expected
            + "'; SELECT ROW_COUNT();"
        ).strip()
        == b"1"
    )
    held = scope()
    refusal = native("preflight", order_id, expected=(3,))
    assert not refusal["ok"] and "Caller collision guard" in refusal["error"]
    assert row_pins(held) == row_pins(scope())
    assert (
        sql(
            "UPDATE "
            + target_table
            + " SET "
            + target_field
            + "='"
            + expected
            + "' WHERE id="
            + str(order_id)
            + " AND "
            + target_field
            + "='"
            + wrong
            + "'; SELECT ROW_COUNT();"
        ).strip()
        == b"1"
    )
    after = scope()
    assert row_pins(before) == row_pins(after)
    record(
        "CALLER_OWNED_WRONG_TYPE_REFUSED_" + label,
        order_id=order_id,
        expected=expected,
        wrong=wrong,
        refusal=refusal,
        before=before,
        held=held,
        after=after,
        limits="Caller preflight control, not native ownership/type protection",
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
    assert same_orders(left, right), "Native cross-store semantic mismatch: " + label
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


def verify_deleted(label, order_id, item_ids, unrelated_before):
    case = json.loads((PRIVATE / "case.json").read_text())
    entry = case["deleted"][str(order_id)]
    assert (
        entry["run"] == RUN
        and entry["type"] == "shop_order"
        and entry["before"]["data"]["id"] == order_id
    )
    counts = {}
    for table, field in [
        ("wp_posts", "ID"),
        ("wp_postmeta", "post_id"),
        ("wp_wc_orders", "id"),
        ("wp_wc_orders_meta", "order_id"),
        ("wp_wc_order_addresses", "order_id"),
        ("wp_wc_order_operational_data", "order_id"),
        ("wp_woocommerce_order_items", "order_id"),
    ]:
        count = sql(
            "SELECT COUNT(*) FROM " + table + " WHERE " + field + "=" + str(order_id) + ";"
        ).strip()
        assert count == b"0", (table, count)
        counts[table] = 0
    count = sql(
        "SELECT COUNT(*) FROM wp_woocommerce_order_itemmeta WHERE order_item_id IN ("
        + ",".join(map(str, item_ids))
        + ");"
    ).strip()
    assert count == b"0"
    counts["wp_woocommerce_order_itemmeta"] = 0
    after = scope(order_id, item_ids)
    assert row_pins(unrelated_before) == row_pins(
        after
    ), "Deletion changed unrelated order/product rows"
    record(
        "EXACT_NATIVE_DELETION_AND_TOMBSTONE_CLEANUP_" + label,
        order_id=order_id,
        item_ids=item_ids,
        absent=counts,
        unrelated_before=unrelated_before,
        unrelated_after=after,
    )


def cleanup_owned():
    errors = []
    if not base.PROCESSES:
        return errors
    try:
        if any(child.poll() is None for child in base.PROCESSES):
            base.stop(SOCKET)
    except BaseException as error:
        errors.append({"step": "graceful-shutdown", "error": type(error).__name__})
    for child in base.PROCESSES:
        try:
            child.wait(timeout=20)
        except BaseException as error:
            errors.append(
                {"step": "initial-child-wait", "pid": child.pid, "error": type(error).__name__}
            )
            try:
                if child.poll() is None:
                    child.terminate()
                    child.wait(timeout=5)
            except BaseException as terminate_error:
                errors.append(
                    {
                        "step": "child-terminate",
                        "pid": child.pid,
                        "error": type(terminate_error).__name__,
                    }
                )
            try:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=5)
            except BaseException as kill_error:
                errors.append(
                    {"step": "child-kill", "pid": child.pid, "error": type(kill_error).__name__}
                )
        try:
            if child.poll() is None:
                errors.append({"step": "owned-child-survived", "pid": child.pid})
        except BaseException as error:
            errors.append(
                {"step": "child-liveness-unknown", "pid": child.pid, "error": type(error).__name__}
            )
    try:
        result = subprocess.run(
            [
                "/opt/homebrew/bin/mariadb-admin",
                "--no-defaults",
                "--socket=" + SOCKET,
                "-uroot",
                "ping",
            ],
            capture_output=True,
            timeout=5,
        )
        if result.returncode == 0:
            errors.append({"step": "owned-socket-still-live"})
    except BaseException as error:
        errors.append({"step": "socket-liveness-unknown", "error": type(error).__name__})
    return errors


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
        ROOT / "logo-registry.json",
        ROOT / "skyyrose/core/product.py",
        ROOT / ".artifacts/release-gates-20261019/gate4-populated/historical-producer-blob.php",
        ROOT / ".artifacts/release-gates-20261019/gate4-populated/historical-producer-function.php",
        ROOT
        / ".artifacts/release-gates-20261019/gate4-populated/historical-producer-provenance.json",
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
            if direction == "hpos-to-cpt":
                before_refund = inspect()
                assert before_refund["hpos"]
                after_refund = native("refund", "hpos")["snapshot"]
                assert (
                    after_refund["products"]["main"]["stock"]
                    == before_refund["products"]["main"]["stock"] + 1
                )
                assert (
                    after_refund["orders"]["financial_refund_hpos"]["data"]["parent_id"]
                    == before_refund["orders"]["v2_financial"]["data"]["id"]
                )
                assert same(
                    before_refund["orders"]["v2_financial"]["immutable"],
                    after_refund["orders"]["v2_financial"]["immutable"],
                )
                assert (
                    after_refund["orders"]["v2_financial"]["data"]["transaction_id"]
                    == before_refund["orders"]["v2_financial"]["data"]["transaction_id"]
                )
                record("ACTUAL_HPOS_ORIGIN_NATIVE_PARTIAL_REFUND_RESTOCK", snapshot=after_refund)

            for suffix in ["initial-a", "initial-b", "initial-c"]:
                native("newer", direction + "-" + suffix)
            pending = next_batch()
            assert pending["pending"] > 0
            assert native("switch", target)["refused"]
            before_first = inspect()
            first = batch()
            after_first = inspect()
            assert same_orders(before_first["orders"], after_first["orders"]) and same(
                before_first["products"], after_first["products"]
            ), "First native batch changed authoritative business invariants"
            remaining = next_batch()
            assert (
                remaining["pending"] > 0 and remaining["batch"]
            ), "Interruption needs real work remaining"
            record("INTERRUPTED_BETWEEN_BATCHES_" + direction, first=first, remaining=remaining)
            wrong_type_control(direction, int(first["batch"][0]))
            time.sleep(1.1)
            native("newer", direction + "-paused")
            newer = inspect()
            collision_control(direction)
            assert same_orders(newer["orders"], inspect()["orders"]) and same(
                newer["products"], inspect()["products"]
            )
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
                assert bad in outcome["batch"]
                failures = [
                    row
                    for row in outcome["native_logs"]
                    if "g4p_owned_check" in str(row["message"])
                ]
                assert failures, "Native constraint rejection attribution missing"
                after_fault = scope()
                assert row_pins(before_fault) == row_pins(after_fault)
                assert next_batch()["pending"] > 0 and native("switch", target)["refused"]
                sql("ALTER TABLE wp_wc_orders DROP CONSTRAINT g4p_owned_check;")
                record(
                    "NATIVE_FIRST_TABLE_CHECK_FAILURE_NO_PROMOTION",
                    batch=outcome,
                    rejected_native_id=bad,
                    constraint_logs=failures,
                    before=before_fault,
                    after=after_fault,
                )
            drain(direction)
            surviving = inspect()
            assert same_orders(newer["orders"], surviving["orders"]) and same(
                newer["products"], surviving["products"]
            ), "Synchronization changed authoritative business invariants"
            equivalence(direction)
            native("make-delete", direction)
            expected_delete = inspect()
            drain(direction + "-pre-delete")
            assert same_orders(expected_delete["orders"], inspect()["orders"]) and same(
                expected_delete["products"], inspect()["products"]
            )
            delete_role = "delete-" + direction
            delete_id = int(expected_delete["orders"][delete_role]["data"]["id"])
            item_ids = [
                int(n)
                for n in sql(
                    "SELECT order_item_id FROM wp_woocommerce_order_items WHERE order_id="
                    + str(delete_id)
                    + ";"
                )
                .decode()
                .splitlines()
            ]
            assert item_ids
            unrelated_before = scope(delete_id, item_ids)
            native("delete", direction)
            expected_delete["orders"].pop(delete_role)
            drain(direction + "-native-delete")
            verify_deleted(direction, delete_id, item_ids, unrelated_before)
            assert same_orders(expected_delete["orders"], inspect()["orders"]) and same(
                expected_delete["products"], inspect()["products"]
            )
            equivalence(direction + "-after-delete")
            current = inspect()
            assert same(
                current["orders"]["newer-" + direction + "-paused"]["immutable"],
                newer["orders"]["newer-" + direction + "-paused"]["immutable"],
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
            assert same_orders(current["orders"], fresh["orders"]) and same(
                current["products"], fresh["products"]
            ), "Authority switch/rollback changed payments/history/refunds/items/stock"

            record("NATIVE_AUTHORITY_SWITCH_" + direction, switch=switched, snapshot=fresh)
            cold(direction)
        before = scope()
        value = native("batch")
        assert value["batch"] == [] and value["pending_after"] == 0
        after = scope()
        assert row_pins(before) == row_pins(after)
        record("FRESH_EMPTY_RETRY_NOOP")
        assert all(pin(ROOT / path) == value for path, value in REPORT["source_pins"].items())
        assert all(pin(ROOT / path) == value for path, value in RAW_PINS.items())
        write(PRIVATE / "sql-preimages-index.json", RAW_PINS)
        REPORT["raw_sql_index"] = {
            "path": str((PRIVATE / "sql-preimages-index.json").relative_to(ROOT)),
            **pin(PRIVATE / "sql-preimages-index.json"),
            "files": len(RAW_PINS),
        }
        complete = True
    except BaseException as error:
        REPORT["failure"] = {"type": type(error).__name__, "message": str(error)[:1500]}
        raise
    finally:
        service_errors = cleanup_owned()
        REPORT["service_cleanup_errors"] = service_errors
        REPORT["owned_services_stopped"] = not service_errors
        cleanup.extend(service_errors)
        REPORT["protected_originals_unchanged"] = False
        try:
            assert protected == {name: base.inventory(ORIGINAL / name) for name in protected}
            assert original_pins == base.inventory(original_cold)
            REPORT["protected_originals_unchanged"] = True
        except BaseException as error:
            cleanup.append({"step": "protected-inventories", "error": type(error).__name__})
        REPORT["cleanup_errors"] = cleanup
        REPORT["status"] = "FAIL_CLEANUP" if cleanup else "FAIL_EXECUTION"
        if complete and not cleanup:
            REPORT["status"] = (
                "PASS_PRIVATE_POPULATED_SYNC_AND_HISTORICAL_PAYMENTS_WITH_EXPLICIT_STOCK_PATH_LIMIT"
            )
        write(OUT / "results.json", REPORT)
    assert complete and not cleanup, REPORT
    print(REPORT["status"])


if __name__ == "__main__":
    main()
