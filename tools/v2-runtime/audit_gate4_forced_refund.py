"""Offline disposition of a failed forced native replay; never a migration waiver."""

from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess

from gate4_refund_attribution import CPT_FILE, DATA_FILE, HPOS, HPOS_FILE, SYNC_FILE, ordered_chain

ROOT = Path(__file__).resolve().parents[2]
RUN = "1792436377553439000"
RAW = ROOT / "tasks/release-gates-20261019/gate4-populated" / ("run-" + RUN)
PRIVATE = ROOT / ".artifacts/release-gates-20261019/gate4-populated" / ("run-" + RUN)
KEYS = [
    "_order_currency",
    "_cart_discount",
    "_cart_discount_tax",
    "_order_shipping",
    "_order_shipping_tax",
    "_order_tax",
    "_order_total",
    "_order_version",
]
TAIL = [("backfill_post_record", HPOS, DATA_FILE), ("__call", "WC_Data_Store", SYNC_FILE)]
DELETE = [
    ("delete_post_meta", None, CPT_FILE),
    ("update_order_meta_from_object", "Abstract_WC_Order_Data_Store_CPT", HPOS_FILE),
    *TAIL,
]
INSERT = [
    ("update_post_meta", "WC_Order_Refund_Data_Store_CPT", CPT_FILE),
    ("update_order_meta_from_object", "Abstract_WC_Order_Data_Store_CPT", CPT_FILE),
    ("update_order_from_object", "Abstract_WC_Order_Data_Store_CPT", HPOS_FILE),
    *TAIL,
]
POST = [("update_order_from_object", "Abstract_WC_Order_Data_Store_CPT", HPOS_FILE), *TAIL]
if not __debug__:
    raise RuntimeError("Assertions required")


def pin(p):
    return {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}


def decode(p):
    return json.JSONDecoder().raw_decode(p.read_text().split("SR_G4_POP=")[-1])[0]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def fields(line):
    parts = line.rstrip(b"\n").split(b":")
    assert len(parts) == 4 and all(
        part == b"N" or re.fullmatch(rb"V(?:[0-9A-F]{2})*", part) for part in parts
    )
    return tuple(None if part == b"N" else bytes.fromhex(part[1:].decode()) for part in parts)


def validate(before, after, native_before, native_after, receipt, site):
    audit = receipt["audit"]
    target = audit["id"]
    assert target == 45 and receipt["batch"] == [target] and receipt["pending_after"] == 0
    assert audit["run"] == RUN and audit["refund_saves"] == []
    assert (
        native_before["hpos"]
        and native_after["hpos"]
        and native_before["pending"] == native_after["pending"] == 0
    )
    assert canonical(native_before) == canonical(native_after)
    assert audit["source_row_before"] == audit["source_row_after"]
    assert audit["source_row_before"]["id"] == "45"
    assert audit["source_row_before"]["type"] == "shop_order_refund"
    assert audit["source_row_before"]["parent_order_id"] == "38"
    for snapshot in [native_before, native_after]:
        refund = snapshot["orders"]["financial_refund_hpos"]["data"]
        assert refund["id"] == 45 and refund["parent_id"] == 38
    assert audit["ledger"] == {
        "run": RUN,
        "role": "financial_refund_hpos",
        "type": "shop_order_refund",
        "parent_id": 38,
    }
    assert audit["before_snapshot"] == native_before
    assert set(before) == set(after) and len(before) == 8
    for table in before:
        if table != "wp_postmeta.txt":
            assert before[table] == after[table], table
    old, new = before["wp_postmeta.txt"], after["wp_postmeta.txt"]
    for rows in [old, new]:
        ids = [fields(line)[0] for line in rows]
        assert all(re.fullmatch(rb"[1-9][0-9]*", value) for value in ids)
        assert len(set(ids)) == len(ids)
    assert len(old) == len(new)
    target_bytes = str(target).encode()

    def selected(rows):
        picked = {}
        for line in rows:
            row = fields(line)
            if row[1] == target_bytes and row[2] is not None and row[2].decode() in KEYS:
                key = row[2].decode()
                assert key not in picked
                picked[key] = (line, row)
        assert set(picked) == set(KEYS)
        return picked

    a, b = selected(old), selected(new)
    assert Counter(old) - Counter(v[0] for v in a.values()) == Counter(new) - Counter(
        v[0] for v in b.values()
    )
    lineage = []
    queries = audit["queries"]
    assert len(queries) == 17
    for index, key in enumerate(KEYS):
        prior, current = a[key][1], b[key][1]
        assert prior[1:] == current[1:] and prior[0] != current[0]
        old_id, new_id = int(prior[0]), int(current[0])
        assert new_id > max(int(fields(row)[0]) for row in old)
        delete, insert = queries[index], queries[index + 8]
        assert delete["sql"] == "DELETE FROM wp_postmeta WHERE meta_id IN( " + str(old_id) + " )"
        assert prior[3] is not None
        value = prior[3].decode()
        assert re.fullmatch(r"[A-Za-z0-9_.-]+", value)
        assert (
            insert["sql"]
            == "INSERT INTO `wp_postmeta` (`post_id`, `meta_key`, `meta_value`) VALUES (45, '"
            + key
            + "', '"
            + value
            + "')"
        )
        for query, chain in [(delete, DELETE), (insert, INSERT)]:
            assert audit["start_epoch"] <= query["epoch"] <= audit["end_epoch"]
            ordered_chain(query["stack"], chain, site)
        lineage.append(
            {
                "key": key,
                "old_meta_id": old_id,
                "new_meta_id": new_id,
                "post_id": target,
                "value_sha256": hashlib.sha256(prior[3]).hexdigest(),
            }
        )
    final = queries[-1]
    literal = r"(?:-?[0-9]+(?:\.[0-9]+)?|'(?:[^'\\]|\\.)*'|NULL)"
    assignment = r"`[a-z_]+` = " + literal
    assert re.fullmatch(
        r"UPDATE `wp_posts` SET " + assignment + r"(?:, " + assignment + r")* WHERE `ID` = 45",
        final["sql"],
    )
    assert audit["start_epoch"] <= final["epoch"] <= audit["end_epoch"]
    ordered_chain(final["stack"], POST, site)
    return lineage


def main():
    report = json.loads((RAW / "results.json").read_text())
    assert (
        report["status"] == "FAIL_EXECUTION"
        and report["source_head"] == "ae17d6eb5e9ba2726e448f276814dd0d3684a11d"
    )
    assert (
        report["owned_services_stopped"]
        and report["protected_originals_unchanged"]
        and report["cleanup_errors"] == []
    )
    inputs = [RAW / "results.json", PRIVATE / "site-at-start.json"]
    for number in [210, 211, 212]:
        meta, text = RAW / f"command-{number:05}.json", RAW / f"command-{number:05}.txt"
        record = json.loads(meta.read_text())
        assert record["receipt"] == text.name and pin(text) == {
            k: record[k] for k in ["sha256", "bytes"]
        }
        assert record["argv"][-1] == ("retry-refund" if number == 211 else "inspect")
        inputs += [meta, text]
    receipt = decode(RAW / "command-00211.txt")
    before_native, after_native = [
        decode(RAW / f"command-{n:05}.txt")["snapshot"] for n in [210, 212]
    ]
    site = PRIVATE / "wordpress"
    inventory = json.loads((PRIVATE / "site-at-start.json").read_text())
    native_sources = {
        CPT_FILE,
        DATA_FILE,
        HPOS_FILE,
        SYNC_FILE,
        "wp-content/plugins/woocommerce/src/Internal/DataStores/Orders/OrdersTableRefundDataStore.php",
        "wp-content/plugins/woocommerce/includes/data-stores/class-wc-order-refund-data-store-cpt.php",
        "wp-content/plugins/woocommerce/includes/data-stores/class-wc-data-store-wp.php",
        "wp-includes/meta.php",
        "wp-includes/post.php",
        "wp-includes/class-wpdb.php",
    }
    for relative in native_sources:
        p = site / relative
        assert {**pin(p), "mode": p.stat().st_mode & 0o777} == inventory[relative]
        inputs.append(p)
    assert pin(PRIVATE / "site-at-start.json") == report["site_code_at_start"]
    snapshots = []
    for number in [46, 47]:
        folder = PRIVATE / "sql-preimages" / f"snapshot-{number:06}"
        assert len(list(folder.iterdir())) == 8
        snapshots.append(
            {p.name: p.read_bytes().splitlines(keepends=True) for p in folder.iterdir()}
        )
        inputs.extend(folder.iterdir())
    lineage = validate(*snapshots, before_native, after_native, receipt, site)
    controls = []
    for mutation in [
        "other-table",
        "changed-value",
        "extra-row",
        "wrong-post-id",
        "unattributed-delete",
        "extra-writer",
        "changed-native-field",
        "duplicate-new-meta-id",
        "null-to-empty-string",
    ]:
        old, new = copy.deepcopy(snapshots)
        nb, na, value = (
            copy.deepcopy(before_native),
            copy.deepcopy(after_native),
            copy.deepcopy(receipt),
        )
        if mutation == "other-table":
            new["wp_wc_orders.txt"].append(b"unexpected")
        elif mutation == "changed-value":
            new["wp_postmeta.txt"] = [
                (
                    line.replace(b"V555344", b"V455552")
                    if fields(line)[1:3] == (b"45", b"_order_currency")
                    else line
                )
                for line in new["wp_postmeta.txt"]
            ]
        elif mutation == "extra-row":
            new["wp_postmeta.txt"].append(new["wp_postmeta.txt"][0])
        elif mutation == "wrong-post-id":
            value["audit"]["id"] = 46
        elif mutation == "unattributed-delete":
            value["audit"]["queries"][0]["stack"] = []
        elif mutation == "extra-writer":
            value["audit"]["queries"].append(value["audit"]["queries"][0])
        elif mutation == "null-to-empty-string":
            index = next(
                i for i, line in enumerate(new["wp_postmeta.txt"]) if line.endswith(b":N\n")
            )
            new["wp_postmeta.txt"][index] = new["wp_postmeta.txt"][index][:-3] + b":V\n"
        elif mutation == "duplicate-new-meta-id":
            selected = [
                fields(line)
                for line in new["wp_postmeta.txt"]
                if fields(line)[1:3] == (b"45", b"_order_currency")
            ][0]
            duplicate = b"V" + selected[0].hex().upper().encode()
            new["wp_postmeta.txt"] = [
                (
                    duplicate + b":" + line.split(b":", 1)[1]
                    if fields(line)[1] == b"45" and fields(line)[2].decode() in KEYS
                    else line
                )
                for line in new["wp_postmeta.txt"]
            ]
        else:
            na["products"]["main"]["stock"] += 1
        try:
            validate(old, new, nb, na, value, site)
        except AssertionError:
            controls.append(
                {"mutation": mutation, "status": "PASS_REFUSED_MODIFIED_RETAINED_OBSERVATION"}
            )
        else:
            raise AssertionError("Accepted " + mutation)
    output = ROOT / "tasks/release-gates-20261019/gate4-populated/forced-replay-observation.json"
    result = {
        "status": "OBSERVED_NATIVE_FORCED_REFUND_PHYSICAL_REWRITE",
        "original_run_status": report["status"],
        "authentication": "NOT_APPLICABLE",
        "run": RUN,
        "native_source": report["source_head"],
        "offline_source": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "lineage": lineage,
        "controls": controls,
        "input_pins": {str(p.relative_to(ROOT)): pin(p) for p in inputs},
        "source_pins": {
            str(p.relative_to(ROOT)): pin(p)
            for p in [Path(__file__), ROOT / "tools/v2-runtime/gate4_refund_attribution.py"]
        },
        "limits": [
            "Original failed physical-NOOP test remains FAIL; no migration waiver or installed parity",
            "Private raw preimages have post-run retention hashes only; failed driver never closed its capture-time SQL index",
            "Ordinary selected-empty retry and previously unreached rollback/final checks require separate execution",
            "All other raw rows/tables, values/types/multiplicity, dates, native order/payment/refund/item/product/stock data remain exact",
        ],
    }
    with output.open("x") as f:
        f.write(json.dumps(result, indent=2) + "\n")
    print(result["status"], len(lineage), len(controls), pin(output))


if __name__ == "__main__":
    main()
