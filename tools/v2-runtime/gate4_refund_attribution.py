"""Source-pinned offline validation of retained native refund writer traces.

This module never boots WordPress or connects to a database. Stack file entries
identify caller files. Native runtime qualification and this follow-up assertion
layer must retain their separate source/run identities.
"""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
import re

if not __debug__:
    raise RuntimeError("Optimized attribution validation is unsupported")

PREFIX = "Automattic\\WooCommerce\\Internal\\DataStores\\Orders\\"
HPOS = PREFIX + "OrdersTableDataStore"
REFUND = PREFIX + "OrdersTableRefundDataStore"
BASE = "wp-content/plugins/woocommerce/"
HPOS_FILE = BASE + "src/Internal/DataStores/Orders/OrdersTableDataStore.php"
REFUND_FILE = BASE + "src/Internal/DataStores/Orders/OrdersTableRefundDataStore.php"
CPT_FILE = BASE + "includes/data-stores/abstract-wc-order-data-store-cpt.php"
DATA_FILE = BASE + "includes/class-wc-data-store.php"
SYNC_FILE = BASE + "src/Internal/DataStores/Orders/DataSynchronizer.php"
# Required inner-to-outer ancestry. Intervening native wrappers are retained in
# full raw stacks. Exact classes and source-pinned caller files cannot reorder.
COMMON_CHAIN = [
    ("save", "WC_Abstract_Order", HPOS_FILE),
    ("after_meta_change", HPOS, HPOS_FILE),
    ("update_meta", HPOS, REFUND_FILE),
    ("update_order_meta", REFUND, HPOS_FILE),
    ("update_post_meta", HPOS, CPT_FILE),
    ("update_order_meta_from_object", "Abstract_WC_Order_Data_Store_CPT", HPOS_FILE),
    ("backfill_post_record", HPOS, DATA_FILE),
    ("__call", "WC_Data_Store", SYNC_FILE),
]
SAVE_CHAIN = [("update", REFUND, DATA_FILE), *COMMON_CHAIN]
QUERY_CHAIN = [("persist_order_to_db", HPOS, HPOS_FILE), *SAVE_CHAIN]
SOURCE_FILES = {
    HPOS_FILE,
    REFUND_FILE,
    CPT_FILE,
    DATA_FILE,
    SYNC_FILE,
    BASE + "includes/abstracts/abstract-wc-order.php",
    BASE + "includes/data-stores/class-wc-data-store-wp.php",
    BASE + "src/Internal/Utilities/DatabaseUtil.php",
}


def ordered_chain(stack, required, site):
    at = 0
    positions = []
    for index, frame in enumerate(stack):
        function, cls, relative = required[at]
        if (
            frame.get("function") == function
            and frame.get("class") == cls
            and frame.get("file") == str(site / relative)
        ):
            positions.append(index)
            at += 1
            if at == len(required):
                return positions
    raise AssertionError("Pinned native class/file call ancestry missing or reordered")


def validate_attribution(audit, site, site_inventory):
    site = Path(site).resolve()
    assert site.is_dir()
    sources = {}
    for relative in sorted(SOURCE_FILES):
        file = site / relative
        assert file.is_file() and not file.is_symlink()
        actual = {
            "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
            "bytes": file.stat().st_size,
            "mode": file.stat().st_mode & 0o777,
        }
        assert actual == site_inventory[relative], relative
        sources[relative] = actual
    target = audit["id"]
    assert type(target) is int and target > 0
    for row in [audit["source_row_before"], audit["source_row_after"]]:
        assert row["id"] == str(target) and row["type"] == "shop_order_refund"
    # The upsert must conflict with the existing ledger-owned ID, not insert a
    # missing refund or conflict with a different unique key.
    unique = audit["source_unique_indexes"]
    assert len(unique) == 1
    assert unique[0]["Key_name"] == "PRIMARY" and unique[0]["Column_name"] == "id"
    assert str(unique[0]["Seq_in_index"]) == "1" and str(unique[0]["Non_unique"]) == "0"
    start, end = audit["start_epoch"], audit["end_epoch"]
    assert start <= end
    modified = audit["source_row_after"]["date_updated_gmt"]
    parsed = datetime.datetime.strptime(modified, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.UTC)
    assert parsed.strftime("%Y-%m-%d %H:%M:%S") == modified
    assert int(start) <= parsed.timestamp() <= int(end) + 1
    witnesses = []
    for index, row in enumerate(audit["queries"]):
        sql = row["sql"]
        if not re.search(r"\bwp_wc_orders\b", sql, re.I):
            continue
        # No intervening unqualified source-table write may destroy the
        # existing-row premise of the observed duplicate-key update.
        assert re.search(r"\bdate_updated_gmt\b", sql, re.I), "Unqualified source-table DML"
        # Capture contains DML only. An unparseable timestamp writer cannot be
        # silently dropped as if it were proved unrelated to the target refund.
        # This pinned native version persists a refund change with a single-row
        # INSERT ... ON DUPLICATE KEY UPDATE. Match the entire statement, not
        # merely an embedded ID or VALUES expression. Unknown shapes fail closed.
        upsert = re.fullmatch(
            r"\s*INSERT INTO wp_wc_orders\s*\(\s*`date_updated_gmt`,\s*`id`,\s*`type`\s*\)"
            r"\s*VALUES\s*\(\s*'([^']+)',\s*([0-9]+),\s*(?-i:'shop_order_refund')\s*\)"
            r"\s*ON DUPLICATE KEY UPDATE\s*`date_updated_gmt`\s*=\s*VALUES\(\s*`date_updated_gmt`\s*\),"
            r"\s*`id`\s*=\s*VALUES\(\s*`id`\s*\),\s*`type`\s*=\s*VALUES\(\s*`type`\s*\)\s*;?\s*",
            sql,
            re.I,
        )
        update = re.fullmatch(
            r"\s*UPDATE\s+`?wp_wc_orders`?\s+SET\s+`?date_updated_gmt`?\s*=\s*'([^']+)'"
            r"\s+WHERE\s+`?id`?\s*=\s*([0-9]+)\s*;?\s*",
            sql,
            re.I,
        )
        writer = upsert or update
        assert writer, "Unattributed or compound timestamp writer statement"
        if int(writer[2]) != target:
            continue
        assert writer[1] == audit["source_row_after"]["date_updated_gmt"]
        assert start <= row["epoch"] <= end
        positions = ordered_chain(row["stack"], QUERY_CHAIN, site)
        witnesses.append({"query_index": index, "required_frame_positions": positions})
    assert witnesses, "No qualified target timestamp writer"
    saves = []
    for index, row in enumerate(audit["refund_saves"]):
        assert type(row["id"]) is int and row["id"] == target
        assert start <= row["epoch"] <= end
        saves.append(
            {
                "save_index": index,
                "required_frame_positions": ordered_chain(row["stack"], SAVE_CHAIN, site),
            }
        )
    assert saves, "No qualified native refund save"
    return {
        "status": "PASS_ORDERED_PINNED_NATIVE_ATTRIBUTION",
        "target_refund_id": target,
        "timestamp_writers": witnesses,
        "refund_saves": saves,
        "native_source_pins": sources,
        "limits": "Attempted SQL and argument-free native stacks; persisted outcome is checked separately by SQL/native readbacks",
    }


def validate_controls(audit, site, inventory):
    """Negative cases modify a retained trace, never a database or native code."""
    proof = validate_attribution(audit, site, inventory)
    witness = proof["timestamp_writers"][0]
    controls = []
    for mutation in [
        "wrong-class",
        "wrong-file",
        "reordered-chain",
        "extra-unattributed-writer",
        "foreign-or-target-scope",
        "target-or-foreign-scope",
        "multirow-upsert",
        "wrong-refund-type",
        "extra-upsert-assignment",
        "mismatched-values-assignment",
        "extra-upsert-column",
        "wrong-owned-source-id",
        "other-unique-key",
        "wrong-writer-id",
        "target-delete-before-upsert",
        "target-replace-before-upsert",
        "unqualified-source-update",
    ]:
        bad = json.loads(json.dumps(audit))
        query = bad["queries"][witness["query_index"]]
        positions = witness["required_frame_positions"]
        if mutation == "wrong-class":
            query["stack"][positions[3]]["class"] = "Wrong_Native_Class"
        elif mutation == "wrong-file":
            query["stack"][positions[3]]["file"] += ".wrong"
        elif mutation == "reordered-chain":
            a, b = positions[3:5]
            query["stack"][a], query["stack"][b] = query["stack"][b], query["stack"][a]
        elif mutation == "extra-unattributed-writer":
            extra = json.loads(json.dumps(query))
            extra["stack"] = []
            bad["queries"].append(extra)
        elif mutation in ["foreign-or-target-scope", "target-or-foreign-scope"]:
            target = bad["id"]
            first, second = (
                (target + 100000, target)
                if mutation.startswith("foreign")
                else (target, target + 100000)
            )
            query["sql"] = (
                "UPDATE wp_wc_orders SET date_updated_gmt='"
                + bad["source_row_after"]["date_updated_gmt"]
                + "' WHERE id="
                + str(first)
                + " OR id="
                + str(second)
            )
        elif mutation == "multirow-upsert":
            query["sql"] = query["sql"].replace(
                "ON DUPLICATE", ", ('2026-10-19 00:00:00', 99999, 'shop_order_refund') ON DUPLICATE"
            )
        elif mutation == "wrong-refund-type":
            query["sql"] = query["sql"].replace("'shop_order_refund'", "'shop_order'")
        elif mutation == "extra-upsert-assignment":
            query["sql"] += ", `total_amount`=0"
        elif mutation == "mismatched-values-assignment":
            query["sql"] = query["sql"].replace("VALUES( `id` )", "VALUES( `type` )")
        elif mutation == "extra-upsert-column":
            query["sql"] = query["sql"].replace(
                "`date_updated_gmt`, `id`, `type`",
                "`date_updated_gmt`, `id`, `type`, `total_amount`",
            )
        elif mutation == "wrong-owned-source-id":
            bad["source_row_before"]["id"] = str(bad["id"] + 1)
        elif mutation in [
            "target-delete-before-upsert",
            "target-replace-before-upsert",
            "unqualified-source-update",
        ]:
            extra = json.loads(json.dumps(query))
            target = str(bad["id"])
            extra["sql"] = (
                "DELETE FROM wp_wc_orders WHERE id=" + target
                if mutation == "target-delete-before-upsert"
                else (
                    "REPLACE INTO wp_wc_orders (id,type) VALUES ("
                    + target
                    + ", 'shop_order_refund')"
                    if mutation == "target-replace-before-upsert"
                    else "UPDATE wp_wc_orders SET total_amount=0 WHERE id=" + target
                )
            )
            bad["queries"].insert(0, extra)
        elif mutation == "wrong-writer-id":
            query["sql"] = query["sql"].replace(
                ", " + str(bad["id"]) + ",", ", " + str(bad["id"] + 1) + ","
            )
        else:
            bad["source_unique_indexes"].append(
                dict(
                    bad["source_unique_indexes"][0], Key_name="other", Column_name="parent_order_id"
                )
            )
        try:
            validate_attribution(bad, site, inventory)
        except AssertionError:
            controls.append(
                {"mutation": mutation, "status": "PASS_REFUSED_MODIFIED_RETAINED_TRACE"}
            )
        else:
            raise AssertionError("Attribution accepted " + mutation)
    return controls
