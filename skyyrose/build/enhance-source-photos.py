#!/usr/bin/env python3
"""
Quick enhancement pipeline for all source product photos
Reads actual files from source-products/, applies ecommerce enhancements
"""

import sys
from pathlib import Path

try:
    from rembg import new_session, remove  # noqa: F401  (availability probe only)

    REMBG_OK = True
except ImportError:
    REMBG_OK = False
    print("⚠️  rembg not found — background removal disabled")

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    print("❌ Pillow required: pip3 install Pillow")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
SRC_DIR = ROOT / "assets/images/source-products"


# Enhancement functions (same as ecommerce-process.py)
def enhance_image(img):
    """Apply fabric smoothing + exposure/contrast enhancement"""
    # Bilateral filter to smooth wrinkles while preserving edges
    img_smooth = img.filter(ImageFilter.SMOOTH_MORE)

    # Enhance exposure
    enhancer = ImageEnhance.Brightness(img_smooth)
    img = enhancer.enhance(1.1)

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.15)

    # Enhance color vibrancy
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.2)

    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)

    return img


def process_image(path):
    """Process a single image: load → enhance → save"""
    try:
        img = Image.open(path).convert("RGB")

        # Apply enhancements
        img_enhanced = enhance_image(img)

        # Save back (overwrite original with enhanced version)
        img_enhanced.save(path, quality=95)

        print(f"  ✅ {path.name}")
        return True
    except Exception as e:
        print(f"  ❌ {path.name}: {e}")
        return False


# Find all product photos
collections = ["black-rose", "love-hurts", "signature", "kids-capsule"]
total = 0
processed = 0

print("\n🔧 Enhancing source product photos")
print("=" * 60)

for collection in collections:
    col_dir = SRC_DIR / collection
    if not col_dir.exists():
        continue

    # Find all image files (excluding AI concepts and extras)
    images = []
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        images.extend(col_dir.glob(ext))

    # Filter out AI concepts, PhotoRoom extras, tinywow
    images = [
        img
        for img in images
        if not any(x in img.name.lower() for x in ["skyyrosedad", "photoroom_0", "tinywow"])
    ]

    if not images:
        continue

    print(f"\n[{collection.upper()}]")
    for img_path in sorted(images):
        total += 1
        if process_image(img_path):
            processed += 1

print(f"\n{'=' * 60}")
print(f"✅ Done — {processed}/{total} processed")
print(f"Source: {SRC_DIR}\n")
