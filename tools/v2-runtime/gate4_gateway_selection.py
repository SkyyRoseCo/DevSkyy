"""Narrow native gateway-save attribution; no bootstrap/database activity here."""

from __future__ import annotations
import datetime
import copy
import hashlib
import json
from pathlib import Path
import re
from gate4_refund_attribution import ordered_chain

if not __debug__:
    raise RuntimeError("Optimized gateway attribution unsupported")
HPOS = "Automattic\\WooCommerce\\Internal\\DataStores\\Orders\\OrdersTableDataStore"
WC = "wp-content/plugins/woocommerce/"
HPOS_FILE = WC + "src/Internal/DataStores/Orders/OrdersTableDataStore.php"
HANDLER = WC + "includes/class-wc-form-handler.php"
NOTICES = {
    "v1-missing-id": "The saved product selection needs review before payment.",
    "v1-ambiguous-sku": "The saved product selection needs review before payment.",
    "active-journal": "This product is being updated. Review it again before checkout.",
}


def same(left, right):
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(
        right, sort_keys=True, allow_nan=False
    )


def validate(audit, before, after, role, label, events, receipt, site, inventory, run):
    site = Path(site)
    assert label in NOTICES and audit["label"] == label and audit["run"] == run
    target = before["orders"][role]["data"]["id"]
    assert type(target) is int and target > 0 and type(audit["id"]) is int and audit["id"] == target
    assert [row["event"] for row in events] == ["before_pay", "validate_fields", "handler_returned"]
    assert all(row["order_id"] == target and row["run"] == run for row in events)
    assert receipt["run"] == run and receipt["id"] == target and receipt["label"] == label
    assert receipt["notices"] == [{"notice": NOTICES[label], "data": []}]
    assert not audit.get("observer_failure")
    assert audit["last_error"] == audit["error_at_start"]
    if audit["last_error"]:
        assert audit["last_error"]["type"] == 8192
        assert (
            audit["last_error"]["message"]
            == "Case statements followed by a semicolon (;) are deprecated, use a colon (:) instead"
        )
        assert (
            audit["last_error"]["file"]
            == "phar:///opt/homebrew/Cellar/wp-cli/2.12.0/bin/wp/vendor/react/promise/src/functions.php"
        )
        assert audit["last_error"]["line"] == 369
    assert same(before["products"], after["products"])
    allowed = {"payment_method", "payment_method_title", "date_modified"}
    adjusted = json.loads(json.dumps(after["orders"]))
    for key in allowed:
        adjusted[role]["data"][key] = before["orders"][role]["data"][key]
    assert same(before["orders"], adjusted)
    data = after["orders"][role]["data"]
    assert (
        data["payment_method"] == "g4p_offline"
        and data["payment_method_title"] == "Synthetic offline"
    )
    assert (
        not data["date_paid"]
        and not data["transaction_id"]
        and not after["orders"][role]["stock_reduced"]
    )
    start, end = audit["start_epoch"], audit["end_epoch"]
    assert start <= end and end - start <= 120
    modified = datetime.datetime.fromisoformat(data["date_modified"])
    assert modified.utcoffset() == datetime.timedelta(0)
    assert int(start) <= modified.timestamp() <= int(end)
    assert modified >= datetime.datetime.fromisoformat(
        before["orders"][role]["data"]["date_modified"]
    )
    raw_before, raw_after = audit["raw_before"], audit["raw_after"]
    assert raw_before["id"] == raw_after["id"] == str(target)
    assert raw_before["type"] == raw_after["type"] == "shop_order"
    raw_allowed = {"payment_method", "payment_method_title", "date_updated_gmt"}
    assert same(
        {k: v for k, v in raw_before.items() if k not in raw_allowed},
        {k: v for k, v in raw_after.items() if k not in raw_allowed},
    )
    for raw, snapshot in [(raw_before, before), (raw_after, after)]:
        d = snapshot["orders"][role]["data"]
        assert (
            raw["payment_method"] == d["payment_method"]
            and raw["payment_method_title"] == d["payment_method_title"]
        )
        assert raw["date_updated_gmt"] == datetime.datetime.fromisoformat(
            d["date_modified"]
        ).strftime("%Y-%m-%d %H:%M:%S")
    indexes = audit["unique_indexes"]
    assert (
        len(indexes) == 1
        and indexes[0]["Key_name"] == "PRIMARY"
        and indexes[0]["Column_name"] == "id"
    )
    assert str(indexes[0]["Non_unique"]) == "0" and str(indexes[0]["Seq_in_index"]) == "1"
    assert set(audit["source_pins"]) == {
        HANDLER,
        HPOS_FILE,
        WC + "includes/class-wc-order.php",
        WC + "includes/abstracts/abstract-wc-order.php",
        WC + "includes/class-wc-data-store.php",
        WC + "src/Internal/Utilities/DatabaseUtil.php",
        "wp-content/themes/skyyrose-flagship-2/inc/woocommerce-compat.php",
    }
    for name, expected in audit["source_pins"].items():
        p = site / name
        actual = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
        assert actual == expected == {k: inventory[name][k] for k in ["sha256", "bytes"]}
    assert {HPOS_FILE, HANDLER, WC + "includes/class-wc-data-store.php"}.issubset(
        audit["source_pins"]
    )
    # Caller-file identity is retained in full raw stacks; helper file is outside site.
    save_chain = [
        ("save", "WC_Abstract_Order", WC + "includes/class-wc-order.php"),
        ("save", "WC_Order", HANDLER),
        (
            "pay_action",
            "WC_Form_Handler",
            str(site.parents[4] / "tools/v2-runtime/gate4-populated-fixture.php"),
        ),
    ]
    query_chain = [
        ("persist_order_to_db", HPOS, HPOS_FILE),
        ("persist_updates", HPOS, HPOS_FILE),
        ("update", HPOS, WC + "includes/class-wc-data-store.php"),
        ("__call", "WC_Data_Store", WC + "includes/abstracts/abstract-wc-order.php"),
        *save_chain,
    ]
    assert [row["phase"] for row in audit["saves"]] == ["before", "after"]
    for row in audit["saves"]:
        assert row["id"] == target and start <= row["epoch"] <= end
        ordered_chain(row["stack"], save_chain, site)
    save_start, save_end = (row["epoch"] for row in audit["saves"])
    assert save_start <= save_end
    writers = []
    for i, row in enumerate(audit["queries"]):
        assert start <= row["epoch"] <= end
        sql = row["sql"]
        target_table = re.match(
            r"\s*(?:INSERT(?: IGNORE)? INTO|REPLACE INTO|UPDATE|DELETE FROM)\s+`?([A-Za-z0-9_]+)`?(?=\s|\()",
            sql,
            re.I,
        )
        assert target_table, "Unsupported DML operation"
        table = target_table[1]
        # This is an explicit exclusion for retained customer/session/options
        # effects, never a fallback for arbitrary or legacy commerce writes.
        if table in {"wp_users", "wp_usermeta", "wp_options", "wp_woocommerce_sessions"}:
            unquoted = re.sub(r"'(?:[^'\\]|\\.)*'", "''", sql)
            assert ";" not in unquoted.rstrip().rstrip(";")
            assert set(re.findall(r"\bwp_[A-Za-z0-9_]+\b", unquoted)) == {table}
            assert not re.search(
                r"\b(?:JOIN|USING|SELECT|UNION|WITH|RETURNING)\b|\b[A-Za-z_][A-Za-z0-9_]*\s*\.",
                unquoted,
                re.I,
            )
            simple_table = re.escape(table)
            assert re.match(
                r"\s*(?:UPDATE\s+`?"
                + simple_table
                + r"`?\s+SET\s+|DELETE FROM\s+`?"
                + simple_table
                + r"`?\s+WHERE\s+|(?:INSERT(?: IGNORE)?|REPLACE) INTO\s+`?"
                + simple_table
                + r"`?\s*\([^()]+\)\s*VALUES\s*\()",
                unquoted,
                re.I,
            )
            continue
        assert table == "wp_wc_orders", "Unattributed commerce or unknown table writer"
        assert save_start <= row["epoch"] <= save_end
        match = re.fullmatch(
            r"\s*INSERT INTO wp_wc_orders\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)\s*ON DUPLICATE KEY UPDATE\s*(.*?)\s*",
            sql,
            re.S,
        )
        assert match, "Unsupported order writer statement"
        columns = [part.strip() for part in match[1].split(",")]
        assert all(re.fullmatch(r"`[a-z_]+`", col) for col in columns)
        names = [col[1:-1] for col in columns]
        assert len(set(names)) == len(names) and {"id", "type", "date_updated_gmt"}.issubset(names)
        assert set(names) <= raw_allowed | {"id", "type"}
        changed = {name for name in raw_before if raw_before[name] != raw_after[name]}
        assert changed <= set(names), "Native statement omits changed raw column"
        values = [part.strip() for part in match[2].split(",")]
        assert len(names) == len(values)
        assert all(re.fullmatch(r"'[A-Za-z0-9_: -]*'|[1-9][0-9]*", value) for value in values)
        decoded = [value[1:-1] if value.startswith("'") else value for value in values]
        assert dict(zip(names, decoded, strict=True)) == {name: raw_after[name] for name in names}
        expected_update = ", ".join(col + " = VALUES( " + col + " )" for col in columns)
        assert match[3] == expected_update
        positions = ordered_chain(row["stack"], query_chain, site)
        writers.append({"query_index": i, "positions": positions})
    assert len(writers) <= 1
    assert writers or same(raw_before, raw_after)
    return {
        "status": "PASS_NAMED_REFUSAL_NATIVE_GATEWAY_SELECTION",
        "label": label,
        "order_id": target,
        "writers": writers,
        "physical_noop": False,
        "scope": "Exact named refusal prevents processor/payment/stock changes; native gateway/date save and customer-state side effects remain explicit",
    }


def controls(audit, before, after, role, label, events, receipt, site, inventory, run):
    result = []
    for mutation in [
        "wrong-id",
        "out-of-window",
        "unexpected-order-dml",
        "wrong-native-caller",
        "paid-status",
        "product-stock",
        "processor-entry",
        "missing-save",
        "changed-source-pin",
        "legacy-order-post-write",
        "legacy-product-meta-write",
        "unknown-table-write",
        "missing-handler-frame",
        "missing-order-save-frame",
        "reordered-save-chain",
        "unprefixed-cross-table-customer-write",
    ]:
        a, b, c, e = copy.deepcopy((audit, before, after, events))
        if mutation == "wrong-id":
            a["id"] += 1
        elif mutation == "out-of-window":
            a["start_epoch"] = a["end_epoch"] = 0
        elif mutation == "unexpected-order-dml":
            a["queries"].append(
                {
                    "sql": "UPDATE wp_wc_orders SET status='completed'",
                    "epoch": a["start_epoch"],
                    "stack": [],
                }
            )
        elif mutation == "wrong-native-caller":
            for row in a["saves"] + a["queries"]:
                for frame in row["stack"]:
                    frame["file"] = "/unattributed.php"
        elif mutation == "paid-status":
            c["orders"][role]["data"]["status"] = "completed"
        elif mutation == "product-stock":
            c["products"]["main"]["stock"] -= 1
        elif mutation == "processor-entry":
            e.append({"event": "processor_entered"})
        elif mutation == "missing-save":
            a["saves"] = []
        elif mutation == "changed-source-pin":
            a["source_pins"][HANDLER]["sha256"] = "0" * 64
        elif mutation in {
            "legacy-order-post-write",
            "legacy-product-meta-write",
            "unknown-table-write",
        }:
            table = {
                "legacy-order-post-write": "wp_posts",
                "legacy-product-meta-write": "wp_postmeta",
                "unknown-table-write": "wp_unknown",
            }[mutation]
            a["queries"].append(
                {
                    "sql": "DELETE FROM " + table + " WHERE id=1",
                    "epoch": a["start_epoch"],
                    "stack": [],
                }
            )
        elif mutation in {"missing-handler-frame", "missing-order-save-frame"}:
            for row in a["saves"] + a["queries"]:
                row["stack"] = [
                    frame
                    for frame in row["stack"]
                    if not (
                        frame.get("function")
                        == ("pay_action" if mutation == "missing-handler-frame" else "save")
                        and frame.get("class")
                        == (
                            "WC_Form_Handler" if mutation == "missing-handler-frame" else "WC_Order"
                        )
                    )
                ]
        elif mutation == "reordered-save-chain":
            for row in a["saves"] + a["queries"]:
                row["stack"].reverse()
        elif mutation == "unprefixed-cross-table-customer-write":
            a["queries"].append(
                {
                    "sql": "UPDATE wp_users JOIN other_table ON wp_users.ID=other_table.id SET other_table.x=1",
                    "epoch": a["start_epoch"],
                    "stack": [],
                }
            )
        try:
            validate(a, b, c, role, label, e, receipt, site, inventory, run)
        except AssertionError:
            result.append(
                {"mutation": mutation, "status": "PASS_REFUSED_MODIFIED_RETAINED_GATEWAY_AUDIT"}
            )
        else:
            raise AssertionError("Gateway attribution accepted " + mutation)
    changed_gateway = [
        name
        for name in ["payment_method", "payment_method_title"]
        if audit["raw_before"][name] != audit["raw_after"][name]
    ]
    if changed_gateway:
        a = copy.deepcopy(audit)
        drop = changed_gateway[0]
        for row in a["queries"]:
            if re.search(r"INSERT INTO wp_wc_orders\b", row["sql"]):
                parsed = re.fullmatch(
                    r"\s*INSERT INTO wp_wc_orders\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)\s*ON DUPLICATE KEY UPDATE\s*(.*?)\s*",
                    row["sql"],
                    re.S,
                )
                assert parsed
                columns = [value.strip() for value in parsed[1].split(",")]
                values = [value.strip() for value in parsed[2].split(",")]
                pairs = [
                    (column, value)
                    for column, value in zip(columns, values, strict=True)
                    if column != "`" + drop + "`"
                ]
                row["sql"] = (
                    "INSERT INTO wp_wc_orders ( "
                    + ", ".join(column for column, _ in pairs)
                    + " ) VALUES ( "
                    + ", ".join(value for _, value in pairs)
                    + " ) ON DUPLICATE KEY UPDATE "
                    + ", ".join(column + " = VALUES( " + column + " )" for column, _ in pairs)
                )
        try:
            validate(a, before, after, role, label, events, receipt, site, inventory, run)
        except AssertionError:
            result.append(
                {
                    "mutation": "changed-gateway-column-omitted",
                    "status": "PASS_REFUSED_MODIFIED_RETAINED_GATEWAY_AUDIT",
                }
            )
        else:
            raise AssertionError("Gateway attribution accepted missing changed gateway column")
    else:
        result.append(
            {
                "mutation": "changed-gateway-column-omitted",
                "status": "NOT_APPLICABLE_ALREADY_SELECTED_GATEWAY",
            }
        )
    return result
