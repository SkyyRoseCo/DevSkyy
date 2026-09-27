"""Generate a read-only completion sheet from the canonical product entry point."""

import csv
import json
from pathlib import Path

from skyyrose.core.product import get_all_products

output = Path(__file__).resolve().parent
products = get_all_products()
with (output / "completion-sheet.csv").open("w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(
        [
            "sku",
            "name",
            "status",
            "item_weight_g",
            "packed_weight_g",
            "packed_length_cm",
            "packed_width_cm",
            "packed_height_cm",
            "packaging_reference",
            "missing_fields",
        ]
    )
    for sku, product in products.items():
        shipping = product["shipping"]
        parcel = shipping["packed_parcel"]
        dimensions = parcel["dimensions"]
        gaps = [gap for gap in product["gaps"] if gap.startswith("shipping")]
        writer.writerow(
            [
                sku,
                product["name"],
                "MISSING" if gaps else "RECORDED",
                shipping["item_weight"]["value"],
                parcel["weight"]["value"],
                dimensions["length"],
                dimensions["width"],
                dimensions["height"],
                parcel["packaging_reference"],
                " | ".join(gaps),
            ]
        )
(output / "shipping-records.json").write_text(
    json.dumps(
        {
            "authority": "Generated consumer; edit only canonical registry through its update API",
            "records": {
                sku: {
                    "shipping": p["shipping"],
                    "gaps": [g for g in p["gaps"] if g.startswith("shipping")],
                }
                for sku, p in products.items()
            },
        },
        indent=2,
    )
    + "\n"
)
