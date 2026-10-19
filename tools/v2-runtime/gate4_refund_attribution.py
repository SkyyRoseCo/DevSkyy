"""Source-pinned offline validation of retained native refund writer traces.

This module never boots WordPress or connects to a database. Stack file entries
identify caller files. Native runtime qualification and this follow-up assertion
layer must retain their separate source/run identities.
"""

from __future__ import annotations

import hashlib
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
    ("backfill_post_record", HPOS, SYNC_FILE),
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
    start, end = audit["start_epoch"], audit["end_epoch"]
    assert start <= end
    witnesses = []
    for index, row in enumerate(audit["queries"]):
        sql = row["sql"]
        if not re.search(r"\bwp_wc_orders\b", sql, re.I) or not re.search(
            r"\bdate_updated_gmt\b", sql, re.I
        ):
            continue
        # Capture contains DML only. An unparseable timestamp writer cannot be
        # silently dropped as if it were proved unrelated to the target refund.
        assert re.search(r"^\s*UPDATE\s+`?wp_wc_orders`?\s+SET\b", sql, re.I), sql
        tail = re.search(r"\bWHERE\b(.*)\Z", sql, re.I | re.S)
        assert tail, "Missing timestamp writer scope"
        where = re.fullmatch(r"\s*`?id`?\s*=\s*([0-9]+)\s*;?\s*", tail[1])
        assert where, "Unattributed or compound timestamp writer scope"
        if int(where[1]) != target:
            continue
        value = re.search(r"`?date_updated_gmt`?\s*=\s*'([^']+)'", sql, re.I)
        assert value and value[1] == audit["source_row_after"]["date_updated_gmt"]
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
