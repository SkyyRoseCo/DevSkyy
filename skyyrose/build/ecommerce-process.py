#!/usr/bin/env python3
"""
SkyyRose — E-Commerce Product Image Processing Pipeline
========================================================
For each product photo:
  1. Remove background (rembg u2net model)
  2. Auto-crop to subject with smart padding
  3. Center on 2400×2400 white canvas (Amazon/Shopify standard)
  4. Flatten wrinkles / smooth fabric (bilateral filter + unsharp mask)
  5. Enhance exposure, contrast, color vibrancy
  6. Add subtle soft shadow beneath the product
  7. Export: master PNG (transparent), web JPEG (white bg), WebP (white bg)
  8. Also process promos/logos at full quality without bg removal

Usage:
  python3 build/ecommerce-process.py
  python3 build/ecommerce-process.py br-001      # single product
  python3 build/ecommerce-process.py --no-rembg  # skip bg removal
"""

import sys
import time
from pathlib import Path

try:
    from rembg import new_session, remove

    REMBG_OK = True
except ImportError:
    REMBG_OK = False
    print("⚠️  rembg not found — background removal disabled")

try:
    from PIL import Image, ImageEnhance, ImageFilter

    PIL_OK = True
except ImportError:
    PIL_OK = False
    print("❌ Pillow not found — run: pip3 install Pillow")
    sys.exit(1)

import io

# ── Paths ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
SRC_DIR = ROOT / "assets/images/source-products"
OUT_DIR = ROOT / "assets/images/products-ecom"

# ── Canvas standard (Amazon/Shopify: 2400×2400, white, product fills ~85%) ──
CANVAS_SIZE = 2400
PRODUCT_FILL = 0.85  # product occupies 85% of canvas
SHADOW_OPACITY = 60  # 0-255
SHADOW_BLUR = 30
SHADOW_OFFSET = (0, 40)

# ── Product map (id → source files, per-product bg removal flag) ─────────
PRODUCTS = [
    # BLACK ROSE
    dict(
        id="br-001",
        name="BLACK Rose Crewneck",
        col="black-rose",
        files=["PhotoRoom_004_20230616_170635.PNG"],  # black colorway flat lay
        rembg=True,
    ),
    dict(
        id="br-002",
        name="BLACK Rose Joggers",
        col="black-rose",
        files=["PhotoRoom_010_20231221_160237.jpeg"],
        rembg=True,
    ),
    dict(
        id="br-003",
        name="BLACK is Beautiful Jersey",
        col="black-rose",
        files=[
            # Last Oakland (green/gold) — Pre-Order
            "5A8946B1-B51F-4144-BCBB-F028462077A0.jpg",  # last oakland front
            "266AD7B0-88A6-4489-AA58-AB72A575BD33 3.JPG",  # last oakland back
            # Black (black/white trim)
            "The BLACK Jersey (BLACK Rose Collection).jpg",  # black front
            # Giants (black/orange)
            "BLACK is Beautiful Giants Front.jpg",  # giants front
            "PhotoRoom_003_20230616_170635 (1).png",  # giants back
            # White (black trim)
            "PhotoRoom_011_20230616_170635.png",  # white front
            "PhotoRoom_000_20230616_170635.png",  # white back
        ],
        rembg=False,
    ),  # all PhotoRoom/clean shots already have no bg
    dict(
        id="br-004",
        name="BLACK Rose Hoodie",
        col="black-rose",
        files=["PhotoRoom_001_20230523_204834.PNG"],
        rembg=False,
    ),
    dict(
        id="br-005",
        name="BLACK Rose Hoodie — Signature Edition",
        col="black-rose",
        files=["PhotoRoom_008_20221210_093149.PNG"],
        rembg=False,
    ),
    dict(
        id="br-006",
        name="BLACK Rose Sherpa Jacket",
        col="black-rose",
        files=["The BLACK Rose Sherpa Front.jpg", "The BLACK Rose Sherpa Back.jpg"],
        rembg=True,
    ),
    dict(
        id="br-007",
        name="BLACK Rose × Love Hurts Basketball Shorts",
        col="black-rose",
        files=["PhotoRoom_20221110_201933.PNG", "PhotoRoom_20221110_202133.PNG"],
        rembg=False,
    ),
    dict(
        id="br-008",
        name="Women's BLACK Rose Hooded Dress",
        col="black-rose",
        files=["Womens Black Rose Hooded Dress.jpeg"],
        rembg=True,
    ),
    # LOVE HURTS
    dict(
        id="lh-001",
        name="The Fannie",
        col="love-hurts",
        files=["IMG_0117.jpeg", "4074E988-4DAF-4221-8446-4B93422AF437.jpg"],
        rembg=True,
    ),
    dict(
        id="lh-002",
        name="Love Hurts Joggers",
        col="love-hurts",
        files=["IMG_2102.png"],  # Black colorway
        rembg=False,
    ),
    dict(
        id="lh-002b",
        name="Love Hurts Joggers",
        col="love-hurts",
        files=["IMG_2103.png", "IMG_2105.png"],  # White colorway
        rembg=False,
    ),
    dict(
        id="lh-003",
        name="Love Hurts Basketball Shorts",
        col="love-hurts",
        files=[
            "PhotoRoom_004_20221110_200039.png",
            "PhotoRoom_003_20221110_200039.png",
            "PhotoRoom_018_20231221_160237.jpeg",
        ],
        rembg=False,
    ),
    dict(
        id="lh-004",
        name="Love Hurts Varsity Jacket",
        col="love-hurts",
        files=["Love-Hurts-Varsity-Jacket.jpg"],
        rembg=True,
    ),
    # SIGNATURE
    dict(
        id="sg-001",
        name="The Bay Set",
        col="signature",
        files=[
            "0F85F48C-364B-43CB-8297-E90BB7B8BB51 2.jpg",
            "24661692-0F81-43F4-AA69-7E026552914A.jpg",
        ],
        rembg=True,
    ),
    dict(
        id="sg-002",
        name="Stay Golden Set",
        col="signature",
        files=["562143CF-4A77-42B8-A58C-C77ED21E9B5E.jpg"],
        rembg=True,
    ),
    dict(
        id="sg-003",
        name="The Signature Tee",
        col="signature",
        files=["IMG_0553.JPG", "Signature T \u201cOrchard\u201d.jpeg"],  # Orchid colorway
        rembg=True,
    ),
    dict(
        id="sg-004",
        name="The Signature Tee",
        col="signature",
        files=["IMG_0554.JPG", "Signature T \u201cWhite\u201d.jpeg"],  # White colorway
        rembg=True,
    ),
    dict(
        id="sg-005",
        name="Stay Golden Tee",
        col="signature",
        files=["Photo Dec 18 2023, 6 09 21 PM.jpg"],
        rembg=True,
    ),
    dict(
        id="sg-006",
        name="Mint & Lavender Hoodie",
        col="signature",
        files=[
            "PhotoRoom_004_20231221_160237.jpeg",
            "Mint & Lavender Set (Sold Separately) .jpeg",
            "MINT & Lavender Set 2 .jpeg",
        ],
        rembg=False,
    ),
    dict(
        id="sg-007",
        name="The Signature Beanie",
        col="signature",
        files=[
            "Signature-Beanie-Red.jpg",  # Red colorway
            "Signature-Beanie-Purple.jpg",  # Purple colorway
            "Signature-Beanie-Black.jpg",
        ],  # Black colorway
        rembg=False,
    ),
    dict(
        id="sg-009",
        name="The Sherpa Jacket",
        col="signature",
        files=["PhotoRoom_002_20231221_072338.jpg", "PhotoRoom_003_20231221_072338.jpg"],
        rembg=True,
    ),
    dict(
        id="sg-010",
        name="The Bridge Series Shorts",
        col="signature",
        files=[
            "Bridge-Series-Bay-Bridge.jpg",  # Bay Bridge colorway
            "Bridge-Series-Golden-Gate.jpg",
        ],  # Golden Gate colorway
        rembg=False,
    ),
]


# ── rembg session (load once) ─────────────────────────────────────────────
rembg_session = None


def get_rembg_session():
    global rembg_session
    if rembg_session is None and REMBG_OK:
        print("  Loading rembg model (u2net)…", end=" ", flush=True)
        rembg_session = new_session("u2net")
        print("ready")
    return rembg_session


# ── Core processing ───────────────────────────────────────────────────────


def load_image(path: Path) -> Image.Image:
    """Load image, convert to RGBA."""
    img = Image.open(path).convert("RGBA")
    return img


def remove_background(img: Image.Image) -> Image.Image:
    """Run rembg background removal."""
    session = get_rembg_session()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    result = remove(buf.read(), session=session)
    return Image.open(io.BytesIO(result)).convert("RGBA")


def smooth_fabric(img: Image.Image) -> Image.Image:
    """
    Flatten flatlay wrinkles / smooth fabric texture while preserving edges.
    Uses a sequence of bilateral-like filters:
      1. Mild blur to soften wrinkles
      2. Unsharp mask to restore edge detail & print clarity
      3. Slight contrast lift
    """
    rgb = img.convert("RGB")

    # 1. Smooth wrinkles (reduce radius = gentler, won't damage print)
    smoothed = rgb.filter(ImageFilter.GaussianBlur(radius=0.6))

    # 2. Restore edge sharpness (amount, radius, threshold)
    sharp = smoothed.filter(ImageFilter.UnsharpMask(radius=1.8, percent=140, threshold=3))

    # 3. Lift contrast slightly for product pop
    sharp = ImageEnhance.Contrast(sharp).enhance(1.08)

    # 4. Vibrancy boost
    sharp = ImageEnhance.Color(sharp).enhance(1.18)

    # 5. Brightness micro-lift
    sharp = ImageEnhance.Brightness(sharp).enhance(1.04)

    # Restore alpha from original
    result = sharp.convert("RGBA")
    result.putalpha(img.split()[3])
    return result


def has_existing_white_bg(img: Image.Image) -> bool:
    """Detect if image already has a clean white/near-white background (PhotoRoom etc.)."""
    rgb = img.convert("RGB")
    w, h = rgb.size
    corners = [
        rgb.getpixel((10, 10)),
        rgb.getpixel((w - 10, 10)),
        rgb.getpixel((10, h - 10)),
        rgb.getpixel((w - 10, h - 10)),
    ]
    whites = sum(1 for r, g, b in corners if r > 240 and g > 240 and b > 240)
    return whites >= 3


def auto_crop_subject(img: Image.Image, padding_pct: float = 0.04) -> Image.Image:
    """Crop tight to the non-transparent/non-white subject, add small padding."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    alpha = img.split()[3]
    bbox = alpha.getbbox()
    if bbox is None:
        return img

    pad_x = int((bbox[2] - bbox[0]) * padding_pct)
    pad_y = int((bbox[3] - bbox[1]) * padding_pct)
    w, h = img.size
    bbox = (
        max(0, bbox[0] - pad_x),
        max(0, bbox[1] - pad_y),
        min(w, bbox[2] + pad_x),
        min(h, bbox[3] + pad_y),
    )
    return img.crop(bbox)


def add_shadow(canvas: Image.Image, subject: Image.Image, position: tuple) -> Image.Image:
    """Add a realistic soft shadow beneath the product."""
    # Create shadow from subject alpha
    shadow_color = (20, 20, 20, SHADOW_OPACITY)
    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))

    # Place shadow offset downward
    sx = position[0] + SHADOW_OFFSET[0]
    sy = position[1] + SHADOW_OFFSET[1]

    # Build shadow shape from subject alpha
    shadow_img = Image.new("RGBA", subject.size, shadow_color[:3] + (0,))
    if subject.mode == "RGBA":
        alpha = subject.split()[3]
        # Fill shadow with shadow_color where subject is opaque
        shadow_fill = Image.new("RGBA", subject.size, shadow_color)
        shadow_img = Image.composite(shadow_fill, shadow_img, alpha)

    # Blur shadow
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=SHADOW_BLUR))
    shadow_layer.paste(shadow_img, (sx, sy), shadow_img)

    # Composite: white base → shadow → (handled externally)
    result = Image.alpha_composite(canvas, shadow_layer)
    return result


def place_on_canvas(subject: Image.Image, canvas_size: int, fill_ratio: float) -> Image.Image:
    """Center subject on square white canvas with proportional scaling."""
    subject = auto_crop_subject(subject)
    sw, sh = subject.size
    target = int(canvas_size * fill_ratio)

    # Scale to fit inside target square, preserving aspect
    scale = min(target / sw, target / sh)
    new_w = int(sw * scale)
    new_h = int(sh * scale)
    subject = subject.resize((new_w, new_h), Image.LANCZOS)

    # White canvas
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 255))

    # Add shadow first
    paste_x = (canvas_size - new_w) // 2
    paste_y = (canvas_size - new_h) // 2
    canvas = add_shadow(canvas, subject, (paste_x, paste_y))

    # Paste subject
    canvas.paste(subject, (paste_x, paste_y), subject)
    return canvas


def process_image(
    src_path: Path, out_stem: str, out_dir: Path, do_rembg: bool = True, is_flatlay: bool = True
) -> dict:
    """Full e-commerce processing pipeline for one image."""
    out_dir.mkdir(parents=True, exist_ok=True)

    img = load_image(src_path)

    # Detect if bg already removed (PhotoRoom etc.)
    already_clean = (
        src_path.suffix.lower() == ".png" and has_existing_white_bg(img.convert("RGB")) is False
    )

    # ── Step 1: Background removal ────────────────────────────────────────
    if do_rembg and REMBG_OK and not already_clean:
        try:
            img = remove_background(img)
        except Exception as e:
            print(f"    ⚠️  rembg failed: {e}")
    elif src_path.suffix.lower() == ".png":
        # Already has transparency from PhotoRoom - keep it
        pass
    else:
        # White bg detection / convert
        pass

    # ── Step 2: Fabric smoothing (for flatlay/ghosted items) ─────────────
    if is_flatlay:
        img = smooth_fabric(img)

    # ── Step 3: Place on e-commerce canvas ───────────────────────────────
    final = place_on_canvas(img, CANVAS_SIZE, PRODUCT_FILL)

    # ── Step 4: Final sharpening pass ────────────────────────────────────
    final_rgb = final.convert("RGB")
    final_rgb = final_rgb.filter(ImageFilter.UnsharpMask(radius=1.0, percent=80, threshold=2))

    # ── Step 5: Export ────────────────────────────────────────────────────
    # Master transparent PNG
    png_path = out_dir / f"{out_stem}-master.png"
    final.save(png_path, "PNG", optimize=True)

    # Web JPEG (white bg)
    jpg_path = out_dir / f"{out_stem}-web.jpg"
    final_rgb.save(jpg_path, "JPEG", quality=94, optimize=True, progressive=True)

    # WebP (white bg, smaller)
    webp_path = out_dir / f"{out_stem}-web.webp"
    final_rgb.save(webp_path, "WEBP", quality=88, method=6)

    sizes = {
        "png_kb": png_path.stat().st_size // 1024,
        "jpg_kb": jpg_path.stat().st_size // 1024,
        "webp_kb": webp_path.stat().st_size // 1024,
    }
    return sizes


# ── Promo / Logo processing (no bg removal, just quality enhance) ─────────


def process_promo(src_path: Path, out_dir: Path) -> dict:
    """Enhance promo/ad photos: color, sharpness, quality output only."""
    out_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(src_path).convert("RGB")

    # Enhancement
    img = ImageEnhance.Contrast(img).enhance(1.06)
    img = ImageEnhance.Color(img).enhance(1.12)
    img = ImageEnhance.Brightness(img).enhance(1.03)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=100, threshold=3))

    stem = src_path.stem
    # JPEG
    jpg_path = out_dir / f"{stem}.jpg"
    img.save(jpg_path, "JPEG", quality=95, optimize=True, progressive=True)
    # WebP
    webp_path = out_dir / f"{stem}.webp"
    img.save(webp_path, "WEBP", quality=90, method=6)

    return {"jpg_kb": jpg_path.stat().st_size // 1024, "webp_kb": webp_path.stat().st_size // 1024}


# ── Main ──────────────────────────────────────────────────────────────────


def main():
    no_rembg = "--no-rembg" in sys.argv
    target = next((a for a in sys.argv[1:] if not a.startswith("--")), None)

    print("\n SkyyRose — E-Commerce Image Processing Pipeline")
    print("=" * 60)
    if no_rembg:
        print("  Mode: no background removal")
    print(f"  Canvas: {CANVAS_SIZE}×{CANVAS_SIZE}px | Fill: {int(PRODUCT_FILL * 100)}%")
    print("  Outputs: master PNG + web JPEG (94%) + WebP (88%)")
    print()

    # Pre-load model once
    if not no_rembg and REMBG_OK:
        get_rembg_session()

    products_to_run = [p for p in PRODUCTS if target is None or p["id"] == target]
    total_ok = 0
    total_fail = 0

    for prod in products_to_run:
        col_label = {
            "black-rose": "BLACK ROSE",
            "love-hurts": "LOVE HURTS",
            "signature": "SIGNATURE",
        }.get(prod["col"], prod["col"])
        print(f"\n  [{col_label}] {prod['id']} — {prod['name']}")

        out_dir = OUT_DIR / prod["id"]
        for i, fname in enumerate(prod["files"]):
            src = SRC_DIR / prod["col"] / fname
            if not src.exists():
                print(f"    ⚠️  Not found: {fname}")
                continue

            suffix = "product" if i == 0 else f"product-{i + 1}"
            out_stem = f"{prod['id']}-{suffix}"
            do_rembg = prod["rembg"] and not no_rembg

            try:
                t0 = time.time()
                sizes = process_image(src, out_stem, out_dir, do_rembg=do_rembg, is_flatlay=True)
                elapsed = time.time() - t0
                rembg_tag = " [bg removed]" if do_rembg else ""
                print(f"    ✅ {fname[:55]}{rembg_tag}")
                print(
                    f"       PNG:{sizes['png_kb']}KB  JPG:{sizes['jpg_kb']}KB  WebP:{sizes['webp_kb']}KB  ({elapsed:.1f}s)"
                )
                total_ok += 1
            except Exception as e:
                print(f"    ❌ {fname} — {e}")
                total_fail += 1

    # ── Promos ────────────────────────────────────────────────────────────
    if target is None:
        print("\n  [ PROMOS / ADS ]")
        promo_src = SRC_DIR / "promos"
        promo_out = OUT_DIR / "_promos"
        if promo_src.exists():
            for f in sorted(promo_src.iterdir()):
                if f.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                    continue
                try:
                    sizes = process_promo(f, promo_out)
                    print(
                        f"    ✅ {f.name[:55]}  JPG:{sizes['jpg_kb']}KB  WebP:{sizes['webp_kb']}KB"
                    )
                    total_ok += 1
                except Exception as e:
                    print(f"    ❌ {f.name} — {e}")
                    total_fail += 1

        print("\n  [ LOGOS ]")
        logo_src = SRC_DIR / "logos"
        logo_out = OUT_DIR / "_logos"
        if logo_src.exists():
            for f in sorted(logo_src.iterdir()):
                if f.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                    continue
                try:
                    sizes = process_promo(f, logo_out)
                    print(
                        f"    ✅ {f.name[:55]}  JPG:{sizes['jpg_kb']}KB  WebP:{sizes['webp_kb']}KB"
                    )
                    total_ok += 1
                except Exception as e:
                    print(f"    ❌ {f.name} — {e}")
                    total_fail += 1

    print("\n" + "=" * 60)
    print(f"  Done — {total_ok} processed, {total_fail} failed")
    print(f"  Output: {OUT_DIR.relative_to(ROOT)}/\n")


if __name__ == "__main__":
    main()
