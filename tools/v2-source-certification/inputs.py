"""Verify historical media bindings against the current unified product registry."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from skyyrose.core.product import all_skus, get_product, provenance  # noqa: E402

CONTRACT = Path(__file__).with_name("build-inputs.json")
SOT = Path(__file__).with_name("inputs") / "product-sot.json"


def verify_registry_binding(contract):
    """The release sidecar must name the registry the consumer actually reads."""
    actual = provenance()["sources"]["registry"]["path"]
    if contract.get("catalog_authority") != actual:
        raise ValueError("Contract catalog authority differs from product entry point")
    digest = hashlib.sha256((ROOT / actual).read_bytes()).hexdigest()
    if (
        contract.get("current_registry_sha256") != digest
        or contract.get("input_hashes", {}).get(actual) != digest
    ):
        raise ValueError("Current registry hash requires contract reconciliation")
    if (
        contract.get("garment_source")
        != "skyyrose.core.product.get_product#catalog.garment_type_lock"
    ):
        raise ValueError("Contract garment source differs from product entry point")


def load_product_sot():
    contract = json.loads(CONTRACT.read_text())
    verify_registry_binding(contract)
    raw = SOT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != contract["product_sot_sha256"]:
        raise ValueError("Pinned upstream product SOT artifact changed")
    manifest = json.loads(raw)
    if manifest["sources"]["catalog_sha256"] != contract["catalog_sha256"]:
        raise ValueError("Upstream catalog identity changed")
    for sku, product in manifest["products"].items():
        payload = {k: v for k, v in product.items() if k != "product_hash"}
        encoded = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
        if hashlib.sha256(encoded).hexdigest() != product["product_hash"]:
            raise ValueError(f"Invalid upstream product hash: {sku}")
    return manifest, raw.decode("utf-8")


def garment_types(manifest):
    """Read current product facts from the unified registry, not historical CSVs.

    The pinned snapshot is retained only as the existing media receipt identity.
    Its commerce binding must still agree with the current founder registry.
    """
    contract = json.loads(CONTRACT.read_text())
    verify_registry_binding(contract)
    by_sku = {sku: get_product(sku)["catalog"] for sku in all_skus()}
    verify_registry_binding(contract)
    if set(by_sku) != set(manifest["products"]):
        raise ValueError("Registry SKU identity differs from media receipt")
    for sku, product in manifest["products"].items():
        row = by_sku[sku]
        expected = {
            "price": row["price"].strip(),
            "sizes": [s.strip() for s in row["sizes"].split("|") if s.strip()],
            "colors": [s.strip() for s in row["color"].split("|") if s.strip()],
            "edition_size": row["edition_size"].strip(),
            "published": row["published"].strip() == "1",
            "is_preorder": row["is_preorder"].strip() == "1",
        }
        if (
            product["commerce"] != expected
            or product["identity"]["collection"] != row["collection"].strip()
        ):
            raise ValueError(f"Current registry requires media-binding reconciliation: {sku}")
    return {sku: row["garment_type_lock"].strip().lower() for sku, row in by_sku.items()}
