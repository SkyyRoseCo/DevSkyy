"""Prove current card bindings and generate the one V2 media lookup and SKU audit."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from skyyrose.core.media_usage import validated_usage_roles  # noqa: E402
from skyyrose.core.product import all_skus, get_product  # noqa: E402

THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"
INDEX = THEME / "data/v2-product-media-index.json"
AUDIT = ROOT / "docs/creative/V2-PRODUCT-CARD-AUDIT.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_audit() -> tuple[dict, str]:
    canonical = (ROOT / "logo-registry.json").resolve()
    before = sha(canonical)
    inputs = [
        canonical,
        THEME / "data/v2-media-eligibility.json",
        THEME / "data/approved-card-fronts.json",
        THEME / "data/product-presentation-registry.json",
        THEME / "assets/derived/card-fronts/manifest.json",
        THEME / "inc/approved-card-fronts.php",
        THEME / "inc/v2-media-eligibility.php",
        THEME / "inc/pdp-media-delivery.php",
        THEME / "inc/performance.php",
        THEME / "inc/global-shell.php",
        THEME / "inc/seo-indexing.php",
        THEME / "inc/launch-readiness.php",
        THEME / "functions.php",
        THEME / "template-parts/collections/arrival.php",
        THEME / "template-parts/collections/story.php",
        THEME / "template-parts/collections/index.php",
        THEME / "template-parts/v2-preorder.php",
        THEME / "template-parts/home/editorial-collection.php",
        THEME / "template-parts/commerce/product-card.php",
        THEME / "template-parts/collections/editorial.php",
        THEME / "template-parts/home/editorial-film.php",
        THEME / "template-parts/home/kids-capsule-reveal.php",
        THEME / "template-parts/immersive/world.php",
        THEME / "assets/js/theme.js",
        THEME / "assets/js/quick-view-commerce.js",
        THEME / "assets/css/quick-view-commerce.css",
        ROOT / "tools/v2-runtime/build-card-renditions.py",
        ROOT / "skyyrose/core/media_usage.py",
        ROOT / "tools/v2-source-certification/package.py",
        ROOT / "tools/v2-runtime/test-pdp-approved-fronts.php",
        Path(__file__),
    ]
    input_hashes = {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs}
    process = subprocess.run(
        ["php", str(ROOT / "tools/v2-runtime/test-pdp-approved-fronts.php"), "--json"],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )
    runtime = json.loads(process.stdout)
    skus = sorted(all_skus())
    if len(skus) != 33 or sorted(runtime["cards"]) != skus:
        raise ValueError("Current registry and actual runtime must cover exactly the same 33 SKUs")
    expected_delivery = {
        f"assets/derived/card-fronts/{sku}-{width}w.webp"
        for sku in skus
        for width in sorted(
            {
                w
                for w in (160, 320, 480, 768, 1024, 1280, 1536)
                if w <= runtime["cards"][sku]["width"]
            }
            | {runtime["cards"][sku]["width"]}
        )
    }
    if (
        not isinstance(runtime.get("eligible_card_renditions"), dict)
        or set(runtime["eligible_card_renditions"]) != expected_delivery
    ):
        raise ValueError(
            "Actual runtime must admit the exact bounded responsive renditions for every current card"
        )
    inventory = json.loads((THEME / "data/v2-media-eligibility.json").read_text())
    presentation = json.loads((THEME / "data/product-presentation-registry.json").read_text())
    uses = inventory.get("usage_adoptions", {})
    if uses != presentation.get("media_usage_adoptions", {}):
        raise ValueError("Canonical projection and runtime usage grants differ")
    for binding in uses.values():
        receipt = THEME / binding["path"]
        if sha(receipt) != binding["sha256"]:
            raise ValueError("Additional-use receipt changed")
        input_hashes[receipt.relative_to(ROOT).as_posix()] = sha(receipt)
        grant = json.loads(receipt.read_text())
        authority = THEME / grant["authorization"]["path"]
        if sha(authority) != grant["authorization"]["sha256"]:
            raise ValueError("Additional-use owner authorization changed")
        input_hashes[authority.relative_to(ROOT).as_posix()] = sha(authority)
    delivery = json.loads((THEME / "assets/derived/card-fronts/manifest.json").read_text())
    if sorted(delivery["products"]) != skus:
        raise ValueError("Responsive delivery must cover every current SKU")
    rows = {}
    counts = Counter()
    for sku in skus:
        product = get_product(sku)
        front = product["images"]["card_front"]
        resolved = runtime["cards"][sku]
        path = f"assets/v2-original/products/{sku}.png"
        image = THEME / path
        if not front or front["path"] != path or resolved["path"] != path or image.is_symlink():
            raise ValueError(f"Missing exact current master: {sku}")
        digest = sha(image)
        if (
            digest != front["sha256"]
            or digest != front["source_sha256"]
            or digest != resolved["sha256"]
        ):
            raise ValueError(f"Current SKU/master hash disagreement: {sku}")
        entry = inventory["assets"][path]
        if (
            entry["review"] != front["review"]
            or entry["status"] != front["current_fidelity_status"]
            or entry["skus"] != [sku]
            or entry["collections"] != [product["collection"]]
        ):
            raise ValueError(f"Current SKU/collection/review disagreement: {sku}")
        derivatives = delivery["products"][sku]
        expected_widths = sorted(
            {w for w in (160, 320, 480, 768, 1024, 1280, 1536) if w <= resolved["width"]}
            | {resolved["width"]}
        )
        if (
            derivatives["source"] != path
            or derivatives["source_sha256"] != digest
            or len(derivatives["renditions"]) != len(expected_widths)
        ):
            raise ValueError(f"Missing current responsive delivery: {sku}")
        if sorted(copy.get("width") for copy in derivatives["renditions"]) != expected_widths:
            raise ValueError(
                f"Responsive delivery needs exact bounded thumbnail through native widths: {sku}"
            )
        if len({copy.get("src") for copy in derivatives["renditions"]}) != len(expected_widths):
            raise ValueError(f"Duplicate responsive delivery paths: {sku}")
        runtime_srcset = {
            fragment.strip().rsplit(" ", 1)[1]: fragment.strip().rsplit(" ", 1)[0]
            for fragment in resolved.get("srcset", "").split(",")
            if " " in fragment.strip()
        }
        for copy in derivatives["renditions"]:
            expected_path = f'assets/derived/card-fronts/{sku}-{copy["width"]}w.webp'
            eligible = runtime["eligible_card_renditions"].get(expected_path)
            delivered_url = urlparse(runtime_srcset.get(f'{copy["width"]}w', ""))
            if (
                copy["src"] != expected_path
                or copy["height"] != round(resolved["height"] * copy["width"] / resolved["width"])
                or sha(THEME / copy["src"]) != copy["sha256"]
                or not eligible
                or eligible["sha256"] != copy["sha256"]
                or eligible["source_sha256"] != digest
                or eligible["skus"] != [sku]
                or eligible["collections"] != [product["collection"]]
                or not delivered_url.path.endswith("/" + expected_path)
                or parse_qs(delivered_url.query).get("v") != [copy["sha256"]]
            ):
                raise ValueError(f"Derivative changed: {sku}")
        card_url = urlparse(resolved.get("card_src", ""))
        card_digest = inventory["assets"][f"assets/derived/card-fronts/{sku}-480w.webp"]["sha256"]
        if (
            resolved.get("card_width") != 480
            or not card_url.path.endswith(f"/assets/derived/card-fronts/{sku}-480w.webp")
            or parse_qs(card_url.query).get("v") != [card_digest]
        ):
            raise ValueError(f"Actual card is missing its current responsive front: {sku}")
        master_url = urlparse(resolved.get("src", ""))
        if not master_url.path.endswith("/" + path) or parse_qs(master_url.query).get("v") != [
            digest
        ]:
            raise ValueError(f"Actual card master is missing its current cache identity: {sku}")
        pre = product["catalog"]["is_preorder"] == "1"
        listing = "pre-order" if pre else "standard"
        counts[(product["collection"], listing)] += 1
        approved_roles = [
            {
                "path": name,
                "sha256": media["sha256"],
                "roles": media["roles"],
                "status": media["status"],
                "review": media["review"],
            }
            for name, media in runtime["current_reviewed_media"].items()
            if media.get("kind") == "photograph"
            and media.get("skus") == [sku]
            and name != path
            and media.get("status") in {"INDEPENDENT_VISUAL_PASS", "FOUNDER_ACCEPTED"}
            and "review" in media
        ]
        rows[sku] = {
            "sku": sku,
            "name": product["name"],
            "collection": product["collection"],
            "listing": listing,
            "listing_route": "/pre-order/" if pre else f'/collections/{product["collection"]}/',
            "card_front": {
                "path": path,
                "sha256": digest,
                "width": resolved["width"],
                "height": resolved["height"],
                "approval": entry["status"],
                "review": entry["review"],
            },
            "pdp_front": (
                {
                    "path": runtime["pdp_on_model_front"][sku]["path"],
                    "sha256": runtime["pdp_on_model_front"][sku]["sha256"],
                    "width": runtime["pdp_on_model_front"][sku]["width"],
                    "height": runtime["pdp_on_model_front"][sku]["height"],
                    "approval": entry["status"],
                    "review": entry["review"],
                }
                if sku in runtime["pdp_on_model_front"]
                else None
            ),
            "effective_roles": sorted(
                set(entry["roles"]) | set(validated_usage_roles(path, entry, uses, THEME))
            ),
            "additional_usage_grant": uses.get(path),
            "responsive_renditions": derivatives["renditions"],
            "other_current_reviewed_media": approved_roles,
            "garment_highlight_state": (
                "CURRENT_SOURCE_BOUND"
                if product.get("presentation", {})
                .get("garment_highlight", {})
                .get("source", {})
                .get("sha256")
                == digest
                else "CURRENT_SOURCE_REVIEW_REQUIRED"
            ),
        }
    if (
        sum(v for (c, listing), v in counts.items() if listing == "standard") != 18
        or sum(v for (c, listing), v in counts.items() if listing == "pre-order") != 15
    ):
        raise ValueError(
            "Current registry partition differs from the reviewed 18 standard / 15 pre-order scope"
        )
    if sha(canonical) != before:
        raise ValueError("Registry changed during audit")
    if any(sha(ROOT / name) != digest for name, digest in input_hashes.items()):
        raise ValueError("Card audit inputs changed during verification")
    index = {
        "schema": "skyyrose.v2.product-media-index.v1",
        "generated_consumer_not_editable_authority": True,
        "authority": canonical.relative_to(ROOT).as_posix(),
        "source_hashes": input_hashes,
        "scope": "LOCAL_CURRENT_THEME_CARD_BINDINGS",
        "card_count": 33,
        "standard_count": 18,
        "preorder_count": 15,
        "responsive_rendition_count": len(expected_delivery),
        "pdp_front_count_separate": runtime["counts"]["pdp_on_model_front"],
        "collection_placements": {
            slug: {
                role: item
                for role, item in record.get("imagery", {}).items()
                if role in {"collection_hero", "collection_story", "merchandise_scene"}
            }
            for slug, record in presentation["collections"].items()
        },
        "media_usage_adoptions": uses,
        "staging_deployment": "NOT_ESTABLISHED_BY_LOCAL_AUDIT",
        "release": "SEPARATE_MEDIA_AND_IMMERSIVE_GATES",
        "products": rows,
    }
    lines = [
        "# Current V2 product card proof",
        "",
        "Generated from the sole registry and the actual PHP V2 resolver. This is local",
        "source/runtime evidence; staging deployment and the full media/immersive release",
        "are separate gates. Run `python tools/v2-runtime/audit-all33-cards.py --check`",
        "to detect drift. Do not edit this generated document or its media index.",
        "",
        "**33 current SKU cards resolve. 18 standard collection listings; 15 pre-order",
        f"listings, each separated by collection. {len(expected_delivery)} source-bound responsive renditions.**",
        "",
        "Approved current masters: `wordpress-theme/skyyrose-flagship-2/assets/v2-original/products/`.",
        "Sole editable bindings: `logo-registry.json`. Lookup: [V2 media index](../../wordpress-theme/skyyrose-flagship-2/data/v2-product-media-index.json).",
        "Contract: [V2 product media contract](V2-PRODUCT-MEDIA-CONTRACT.md).",
        "",
        "| Collection | Standard | Pre-order | Total |",
        "| --- | ---: | ---: | ---: |",
    ]
    for collection in sorted({c for c, _ in counts}):
        standard, pre = counts[(collection, "standard")], counts[(collection, "pre-order")]
        lines.append(f"| {collection} | {standard} | {pre} | {standard + pre} |")
    lines += [
        "",
        "Each row passed exact SKU/collection, master SHA-256, current review receipt,",
        "native dimensions, actual runtime eligibility and responsive source/byte checks.",
        "Founder acceptance remains distinct from independent pixel review. The index",
        "records separate mask-review state; card completeness does not certify walking",
        "clips, unreviewed masks or live stock/checkout.",
        f"All {runtime['counts']['pdp_on_model_front']} current PDP fronts now resolve; 15 additional uses",
        "have separate exact-source owner grants, leaving original card-only receipts unchanged.",
        "Four collection heroes, four collection stories and three collection-specific",
        "pre-order features are recorded in the same media index. These are authorized",
        "placements of unchanged accepted images; context review and staging proof are",
        "recorded in [the placement report](V2-REMAINING-IMAGE-PLACEMENTS.md).",
        "",
        "| SKU | Product | Listing | Approval | Current master SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for sku, row in rows.items():
        lines.append(
            f'| {sku.upper()} | {row["name"]} | {row["listing_route"]} | {row["card_front"]["approval"]} | `{row["card_front"]["sha256"]}` |'
        )
    lines += [
        "",
        "[All 33 cards in the production template](../../tasks/v2-creative-review/v2-imagery-reset-20261002/v2-card-placement-review-20261006/all33-current-review-20261006/index-file.html)",
        "and [390/768/1440 render observations](../../tasks/v2-creative-review/v2-imagery-reset-20261002/v2-card-placement-review-20261006/all33-current-review-20261006/render-checks.json)",
        "are retained as local visual evidence; native commerce values were fixtures.",
        "[Desktop/mobile imagery delivery proof](V2-IMAGERY-OPTIMIZATION.md) records",
        "the current responsive delivery recipe, high-density screen checks and separate hood correction.",
        "",
        "Input evidence hashes are recorded in the generated index. Historical gallery",
        "counts and candidate boards are superseded for current card-completeness claims.",
        "",
    ]
    return index, "\n".join(lines)


def main_locked() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    index, document = build_audit()
    outputs = {INDEX: json.dumps(index, indent=2, sort_keys=True) + "\n", AUDIT: document}
    for path, content in outputs.items():
        if args.check:
            if not path.is_file() or path.read_text() != content:
                raise ValueError(f"Current V2 card proof is stale: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    print(
        f"PASS exact 33 V2 cards, 18/15 listing split, {index["responsive_rendition_count"]} responsive copies, current master/review hashes"
    )
    return 0


def main() -> int:
    canonical = (ROOT / "logo-registry.json").resolve()
    with canonical.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
        return main_locked()


if __name__ == "__main__":
    raise SystemExit(main())
