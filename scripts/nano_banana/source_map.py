"""Source image mapping — maps every SKU to its correct front/back techflat.

This is the AUTHORITATIVE mapping. The product catalog references this
instead of guessing from filenames. Every product has explicit front
and back source paths (or None if unavailable).

Split techflats live in: assets/techflats/split/{collection}/
Original sources live in: wordpress-theme/skyyrose-flagship/assets/images/products/
"""

from __future__ import annotations

from pathlib import Path

from skyyrose.core.paths import REPO_ROOT, WP_PRODUCTS_DIR

PROJECT_ROOT = REPO_ROOT
SPLIT_DIR = PROJECT_ROOT / "assets" / "techflats" / "split"
PRODUCTS_DIR = WP_PRODUCTS_DIR


# ── AUTHORITATIVE SOURCE MAP ────────────────────────────────────────────────
# Format: SKU → { "front": Path, "back": Path | None }
# "front" is used for front view generation
# "back" is used for back view generation
# Both are used as reference for branding/editorial views


def get_source_map() -> dict[str, dict[str, Path | None]]:
    """Return the complete source image mapping for all products."""

    S = SPLIT_DIR  # Split techflats (individual front/back)
    P = PRODUCTS_DIR  # Original product photos

    return {
        # ══════════════════════════════════════════════════════════════
        # BLACK ROSE COLLECTION
        # ══════════════════════════════════════════════════════════════
        # br-001: BLACK Rose Crewneck — FIXED: was mapped to bomber, now correct crewneck
        "br-001": {
            "front": S / "black-rose" / "br-crewneck-front.jpeg",
            "back": S / "black-rose" / "br-crewneck-back.jpeg",
        },
        # br-002: BLACK Rose Joggers — FIXED: was mapped to bomber, now correct joggers
        "br-002": {
            "front": S / "black-rose" / "br-joggers-front.jpeg",
            "back": S / "black-rose" / "br-joggers-back.jpeg",
        },
        # br-003: BLACK is Beautiful Jersey (black base)
        "br-003": {
            "front": S / "black-rose" / "br-jersey-baseball-black-front.jpeg",
            "back": S / "black-rose" / "br-jersey-baseball-black-back.jpeg",
        },
        # br-003 variants — split from composite techflats
        "br-014": {
            "front": S / "black-rose" / "br-jersey-baseball-giants-front.jpeg",
            "back": S / "black-rose" / "br-jersey-baseball-giants-back.jpeg",
        },
        "br-015": {
            "front": S / "black-rose" / "br-jersey-baseball-white-front.jpeg",
            "back": S / "black-rose" / "br-jersey-baseball-white-back.jpeg",
        },
        # br-004: BLACK Rose Hoodie — centered large rose embroidery, kangaroo pocket
        # User confirmed: large rose center chest, different from Signature Edition
        "br-004": {
            "front": P / "black-rose-hoodie-source.jpg",  # waiting for user to save upload to disk
            "back": None,
        },
        # br-005: BLACK Rose Hoodie Signature Edition
        # Small silicone cutout rose on chest + large embroidered rose on hoodie SIDE + rose-print hood lining
        "br-005": {
            "front": P
            / "black-rose-hoodie-signature-edition-hoodie-ltd-source.jpg",  # waiting for user to save upload to disk
            "back": None,
        },
        # br-006: BLACK Rose Sherpa Jacket (satin shell, sherpa lining)
        "br-006": {
            "front": P / "black-rose-sherpa-jacket-sherpa-product.jpg",
            "back": None,
        },
        # br-007: BLACK Rose x Love Hurts Basketball Shorts
        # Real product photos supplied — black mesh, OAKLAND + Love Hurts silver script, tonal rose
        "br-007": {
            "front": P / "br-007-real-front.jpg",
            "back": P / "br-007-real-back.jpg",
        },
        # br-008: SF Inspired Football Jersey — use split techflat
        "br-008": {
            "front": S / "black-rose" / "br-jersey-football-sf-front.jpeg",
            "back": S / "black-rose" / "br-jersey-football-sf-back.jpeg",
        },
        # br-009: Last Oakland Football Jersey
        "br-009": {
            "front": S / "black-rose" / "br-jersey-football-oakland-front.jpeg",
            "back": S / "black-rose" / "br-jersey-football-oakland-back.jpeg",
        },
        # br-010: The Bay Basketball Jersey
        "br-010": {
            "front": S / "black-rose" / "br-jersey-basketball-front.jpeg",
            "back": S / "black-rose" / "br-jersey-basketball-back.jpeg",
        },
        # br-011: The Rose Hockey Jersey (Sharks Edition)
        "br-011": {
            "front": S / "black-rose" / "br-jersey-hockey-front.jpeg",
            "back": S / "black-rose" / "br-jersey-hockey-back.jpeg",
        },
        # br-012: Last Oakland Baseball Jersey — green/gold A's-inspired,
        # "BLACK IS BEAUTIFUL" arched in gold, button-front, rose logo on back, gold piping
        # User uploaded photo — waiting for file to be saved to disk
        "br-012": {
            "front": P / "last-oakland-baseball-jersey-front.jpeg",
            "back": None,
        },
        # ══════════════════════════════════════════════════════════════
        # LOVE HURTS COLLECTION
        # ══════════════════════════════════════════════════════════════
        # lh-002: Love Hurts Joggers
        "lh-002": {
            "front": S / "love-hurts" / "lh-joggers-front.jpeg",
            "back": None,  # no back in the composite
        },
        # lh-003: Love Hurts Basketball Shorts
        # Real product photos supplied — white mesh, orange-red rose clusters, Love Hurts dripping script
        "lh-003": {
            "front": P / "lh-003-real-front.jpg",
            "back": P / "lh-003-real-back.jpg",
        },
        # lh-004: Love Hurts Varsity Jacket
        "lh-004": {
            "front": S / "love-hurts" / "lh-bomber-front.jpeg",
            "back": S / "love-hurts" / "lh-bomber-back.jpeg",
        },
        # lh-006: The Fannie (fanny pack)
        "lh-006": {
            "front": P / "the-fannie-pack-photo.jpg",
            "back": None,
        },
        # ══════════════════════════════════════════════════════════════
        # SIGNATURE COLLECTION
        # ══════════════════════════════════════════════════════════════
        # sg-001: The Bay Bridge Shorts
        "sg-001": {
            "front": S / "signature" / "sg-bridge-shorts-bay-front.jpeg",
            "back": S / "signature" / "sg-bridge-shorts-bay-back.jpeg",
        },
        # sg-002: Stay Golden Shirt
        "sg-002": {
            "front": S / "signature" / "sg-bridge-tee-golden-front.jpeg",
            "back": S / "signature" / "sg-bridge-tee-golden-back.jpeg",
        },
        # sg-003: Stay Golden Shorts
        "sg-003": {
            "front": S / "signature" / "sg-bridge-shorts-golden-front.jpeg",
            "back": S / "signature" / "sg-bridge-shorts-golden-back.jpeg",
        },
        # sg-004: The Signature Hoodie
        "sg-004": {
            "front": P / "signature-hoodie-techflat.jpeg",
            "back": None,
        },
        # sg-005: The Bay Bridge Shirt — white crewneck tee, blue rose with Bay Bridge
        # imagery inside petals, blue clouds at base, SR monogram at collar
        "sg-005": {
            "front": P / "bay-bridge-shirt-front.jpg",
            "back": None,
        },
        # sg-006: Mint & Lavender Hoodie
        "sg-006": {
            "front": S / "signature" / "sg-mint-lav-hoodie-front.jpeg",
            "back": None,
        },
        # sg-007: The Signature Beanie — use purple variant
        "sg-007": {
            "front": S / "signature" / "sg-beanie-purple.jpeg",
            "back": None,
        },
        # sg-009: Signature Sherpa Jacket — black nylon shell, white sherpa lining,
        # small red/green rose embroidery on left chest, zip-front
        # DIFFERENT from br-006 (satin hooded bomber)
        "sg-009": {
            "front": P / "sherpa-jacket-front.jpg",
            "back": None,
        },
        # sg-011: Original Label Tee (White)
        "sg-011": {
            "front": P / "original-label-tee-white-front.webp",
            "back": None,
        },
        # sg-012: Original Label Tee (Orchid)
        "sg-012": {
            "front": P / "original-label-tee-orchid-front.webp",
            "back": None,
        },
        # sg-013: Mint & Lavender Crewneck
        "sg-013": {
            "front": S / "signature" / "sg-mint-lav-crewneck-front.jpeg",
            "back": S / "signature" / "sg-mint-lav-crewneck-back.jpeg",
        },
        # sg-014: Mint & Lavender Sweatpants
        "sg-014": {
            "front": S / "signature" / "sg-mint-lav-sweats-front.jpeg",
            "back": S / "signature" / "sg-mint-lav-sweats-back.jpeg",
        },
        # ══════════════════════════════════════════════════════════════
        # KIDS CAPSULE — individual pieces, not sets
        # ══════════════════════════════════════════════════════════════
        # kids-001: Kids Red Set → split into hoodie + joggers
        "kids-001": {
            "front": S / "kids-capsule" / "kids-red-hoodie-front.jpeg",
            "back": S / "kids-capsule" / "kids-red-hoodie-back.jpeg",
        },
        "kids-001-joggers": {
            "front": S / "kids-capsule" / "kids-red-joggers-front.jpeg",
            "back": S / "kids-capsule" / "kids-red-joggers-back.jpeg",
        },
        # kids-002: Kids Purple Set → split
        "kids-002": {
            "front": S / "kids-capsule" / "kids-purple-hoodie-front.jpeg",
            "back": S / "kids-capsule" / "kids-purple-hoodie-back.jpeg",
        },
        "kids-002-joggers": {
            "front": S / "kids-capsule" / "kids-purple-joggers-front.jpeg",
            "back": S / "kids-capsule" / "kids-purple-joggers-back.jpeg",
        },
    }


def validate_source_map() -> dict:
    """Validate all paths exist. Returns stats."""
    smap = get_source_map()
    total = 0
    found = 0
    missing_front = []
    missing_back = []
    has_both = 0

    for sku, paths in smap.items():
        total += 1
        front = paths.get("front")
        back = paths.get("back")

        if front and front.exists():
            found += 1
            if back and back.exists():
                has_both += 1
            elif back:
                missing_back.append(sku)
        elif front:
            missing_front.append(f"{sku} (path exists but file missing: {front.name})")
        else:
            missing_front.append(f"{sku} (no source mapped)")

    return {
        "total_skus": total,
        "with_front": found,
        "with_both": has_both,
        "missing_front": missing_front,
        "missing_back": missing_back,
    }


if __name__ == "__main__":
    stats = validate_source_map()
    print("Source Map Validation")
    print(f"{'=' * 50}")
    print(f"Total SKUs:       {stats['total_skus']}")
    print(f"With front:       {stats['with_front']}")
    print(f"With front+back:  {stats['with_both']}")
    print(f"\nMissing front ({len(stats['missing_front'])}):")
    for m in stats["missing_front"]:
        print(f"  - {m}")
    if stats["missing_back"]:
        print(f"\nHas front but missing back ({len(stats['missing_back'])}):")
        for m in stats["missing_back"]:
            print(f"  - {m}")
