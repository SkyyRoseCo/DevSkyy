#!/usr/bin/env python3
"""
SkyyRose — Accurate Fashion Model Generation
Two-step pipeline:
  1. Visual learning: Gemini vision analyzes product flat lay → extracts
     exhaustive design description (every text, graphic, color, pattern)
  2. Embed + generate: product photo + extracted description → model photo
     wearing the EXACT product with 100% design fidelity

Model: gemini-2.5-flash-image (image gen) + gemini-2.5-flash (vision)
"""

import base64
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("✗ GEMINI_API_KEY missing")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

VISION_MODEL = "gemini-2.5-flash"
IMAGE_MODEL = "gemini-2.5-flash-image"

PRODUCTS_DIR = Path(__file__).parent.parent / "assets/images/products"
SOURCE_DIR = Path(__file__).parent.parent / "assets/images/source-products"

# ── Product catalog with best flat-lay reference photo ────────────────────────
PRODUCTS = [
    # BLACK ROSE
    {
        "id": "br-001",
        "name": "BLACK Rose Crewneck",
        "collection": "BLACK ROSE",
        "type": "crewneck sweatshirt",
        "ref": "br-001/br-001-product-2.jpg",
        "ref2": None,
        "style": "gothic garden at night, moonlit, dark roses in background",
        "model": "Black woman, mid 20s, confident, high-fashion editorial pose",
    },
    {
        "id": "br-002",
        "name": "BLACK Rose Joggers",
        "collection": "BLACK ROSE",
        "type": "jogger sweatpants",
        "ref": "br-002/br-002-product.jpg",
        "ref2": None,
        "style": "gothic garden at night, candlelight, dark florals",
        "model": "Black man, athletic build, streetwear editorial pose, full-length shot",
    },
    {
        "id": "br-003",
        "name": "BLACK is Beautiful Jersey",
        "collection": "BLACK ROSE",
        "type": "button-down mesh jersey",
        "ref": "br-003/br-003-product.jpg",
        "ref2": "br-003/br-003-product-2.jpg",
        "style": "dark urban street at night, gothic gate in background",
        "model": "Black man, mid 20s, confident streetwear pose, jersey open or styled",
    },
    {
        "id": "br-004",
        "name": "BLACK Rose Hoodie",
        "collection": "BLACK ROSE",
        "type": "pullover hoodie",
        "ref": "br-004/br-004-product-2.jpg",
        "ref2": None,
        "style": "gothic cathedral interior, candlelight, dramatic shadows",
        "model": "Black woman, early 20s, editorial fashion pose, hood up or down",
    },
    {
        "id": "br-006",
        "name": "BLACK Rose Sherpa Jacket",
        "collection": "BLACK ROSE",
        "type": "satin sherpa jacket",
        "ref": "br-006/br-006-product.jpg",
        "ref2": "br-006/br-006-product-2.jpg",
        "style": "moonlit gothic garden, wrought iron gates, dark roses",
        "model": "Black woman, 20s, luxury editorial pose, jacket styled open",
    },
    {
        "id": "br-008",
        "name": "Women's BLACK Rose Hooded Dress",
        "collection": "BLACK ROSE",
        "type": "hooded midi dress",
        "ref": "br-008/br-008-product.jpg",
        "ref2": None,
        "style": "gothic castle interior, stained glass, rose petals on floor",
        "model": "Black woman, 20s, editorial fashion, full-length silhouette",
    },
    # LOVE HURTS
    {
        "id": "lh-001",
        "name": "The Fannie",
        "collection": "LOVE HURTS",
        "type": "fanny pack / crossbody bag",
        "ref": "lh-001/lh-001-product.jpg",
        "ref2": "lh-001/lh-001-product-2.jpg",
        "style": "red-lit baroque ballroom, dramatic lighting, rose petals",
        "model": "Black woman, 20s, styled with the fanny pack worn crossbody, full-look editorial",
    },
    {
        "id": "lh-002",
        "name": "Love Hurts Joggers",
        "collection": "LOVE HURTS",
        "type": "jogger sweatpants",
        "ref": "lh-002/lh-002-product.jpg",
        "ref2": "lh-002b/lh-002b-product.jpg",
        "style": "gothic ballroom with chandeliers, deep crimson lighting",
        "model": "Black man, athletic build, full-length streetwear editorial",
    },
    {
        "id": "lh-003",
        "name": "Love Hurts Basketball Shorts",
        "collection": "LOVE HURTS",
        "type": "basketball shorts",
        "ref": "lh-003/lh-003-product.jpg",
        "ref2": "lh-003/lh-003-product-2.jpg",
        "style": "red velvet theater stage, dramatic spotlights",
        "model": "Black man, athletic build, dynamic pose, shorts styled with matching top",
    },
    # SIGNATURE
    {
        "id": "sg-001",
        "name": "The Bay Set",
        "collection": "SIGNATURE",
        "type": "matching tee and shorts set",
        "ref": "sg-001/sg-001-product.jpg",
        "ref2": "sg-001/sg-001-product-2.jpg",
        "style": "luxury fashion runway, white studio, glass ceiling, professional lighting",
        "model": "Black man, 20s, walking the runway in the full set, editorial confidence",
    },
    {
        "id": "sg-003",
        "name": "The Signature Tee — Orchid",
        "collection": "SIGNATURE",
        "type": "graphic t-shirt",
        "ref": "sg-003/sg-003-product.jpg",
        "ref2": "sg-003/sg-003-product-2.jpg",
        "style": "minimalist white luxury runway studio, champagne gold accent lighting",
        "model": "Black woman, 20s, editorial fashion pose, tee tucked or styled",
    },
    {
        "id": "sg-005",
        "name": "Stay Golden Tee",
        "collection": "SIGNATURE",
        "type": "graphic t-shirt",
        "ref": "sg-005/sg-005-product.jpg",
        "ref2": None,
        "style": "penthouse with city skyline, gold accent lighting, luxury setting",
        "model": "Black man, mid 20s, West Coast editorial pose",
    },
    {
        "id": "sg-006",
        "name": "Mint & Lavender Hoodie",
        "collection": "SIGNATURE",
        "type": "pullover hoodie",
        "ref": "sg-006/sg-006-product.jpg",
        "ref2": "sg-006/sg-006-product-2.jpg",
        "style": "luxury white runway studio, soft lavender accent lighting",
        "model": "Black woman, 20s, editorial fashion, relaxed luxury pose",
    },
    {
        "id": "sg-007",
        "name": "The Signature Beanie",
        "collection": "SIGNATURE",
        "type": "knit beanie",
        "ref": "sg-007/sg-007-product.jpg",
        "ref2": None,
        "style": "luxury street, West Coast cityscape background, golden hour",
        "model": "Black person, 20s, beanie worn naturally, lifestyle editorial pose",
    },
    {
        "id": "sg-009",
        "name": "The Sherpa Jacket",
        "collection": "SIGNATURE",
        "type": "sherpa jacket",
        "ref": "sg-009/sg-009-product-2.jpg",
        "ref2": "sg-009/sg-009-product.jpg",
        "style": "dark luxury runway, marble floors, LED runway lights",
        "model": "Black man, 20s, powerful editorial pose, jacket worn open or closed",
    },
]

RATE_LIMIT_DELAY = 8  # seconds between generations


def load_image_b64(rel_path: str) -> tuple[str, str] | None:
    """Load image from products dir, return (base64_data, mime_type)."""
    path = PRODUCTS_DIR / rel_path
    if not path.exists():
        return None
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode()
    mime = "image/jpeg" if str(path).lower().endswith((".jpg", ".jpeg")) else "image/png"
    return b64, mime


def analyze_product(product: dict, ref_b64: str, ref_mime: str) -> str:
    """Step 1: Visual learning — extract exhaustive product description."""
    print(f"   👁  Analyzing: {product['name']}...")

    prompt = f"""You are a luxury fashion design analyst. Study this product photograph with extreme precision.

Extract a COMPLETE, VERBATIM description of every visual element for use in fashion photography reproduction:

1. **ALL TEXT** — Copy every word, letter, number verbatim (slogans, brand names, graphics text, tags, labels)
2. **GRAPHIC ELEMENTS** — Describe every logo, illustration, embroidery, print, pattern in detail
3. **COLORS** — Exact colors of every element (garment body, trim, graphics, text, hardware)
4. **MATERIAL & TEXTURE** — Fabric type, finish, sheen, texture
5. **SILHOUETTE & CUT** — Fit type, length, proportions, key design details
6. **BRANDING DETAILS** — Logos, tags, labels, patches — exact placement and appearance
7. **UNIQUE IDENTIFIERS** — Anything distinctive that makes this specific product recognizable

Be exhaustive. Every design detail must be captured so a model can be photographed wearing this EXACT garment and it will be 100% recognizable as this specific product.

Product: {product["name"]} — {product["collection"]} Collection
Type: {product["type"]}"""

    try:
        response = client.models.generate_content(
            model=VISION_MODEL,
            contents=[
                types.Part.from_bytes(data=base64.b64decode(ref_b64), mime_type=ref_mime),
                types.Part.from_text(text=prompt),
            ],
        )
        description = response.text.strip()
        print(f"   ✓ Visual analysis complete ({len(description)} chars)")
        return description
    except Exception as e:
        print(f"   ✗ Analysis failed: {e}")
        return f"{product['type']} with embroidered rose design"


def generate_model_photo(
    product: dict, ref_b64: str, ref_mime: str, visual_desc: str
) -> bytes | None:
    """Step 2: Generate model photo wearing exact product."""
    print(f"   🎨 Generating: {product['name']}...")

    generation_prompt = f"""Create an ultra-realistic editorial fashion photograph for {product["collection"]} Collection by SkyyRose.

THE MODEL:
{product["model"]}

THE GARMENT — reproduce with 100% accuracy, every detail exactly as shown in the reference image:
{visual_desc}

PHOTOGRAPHY DIRECTION:
- Setting: {product["style"]}
- Quality: Vogue / Harper's Bazaar editorial standard, 8K ultra-high resolution
- Lighting: Professional fashion photography, dramatic and atmospheric
- The garment design, text, graphics, colors, and branding must be PERFECTLY ACCURATE to the reference image
- Show the complete garment clearly — all design details visible
- Editorial pose that shows off the garment

CRITICAL: Every piece of text, graphic, embroidery, color, and design element on the garment must match the reference photograph exactly. Do not invent or alter any design elements."""

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[
                types.Part.from_bytes(data=base64.b64decode(ref_b64), mime_type=ref_mime),
                types.Part.from_text(text=generation_prompt),
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data

        print("   ✗ No image in response")
        return None

    except Exception as e:
        print(f"   ✗ Generation failed: {e}")
        return None


def run(product_ids: list[str] | None = None):
    targets = [p for p in PRODUCTS if (product_ids is None or p["id"] in product_ids)]
    print("\n🌹 SkyyRose — Accurate Fashion Model Generation")
    print("🔬 Pipeline: Visual Learning → Embedded Description → Image Generation")
    print(f"🤖 Vision: {VISION_MODEL}  |  Image Gen: {IMAGE_MODEL}")
    print("=" * 70)
    print(f"📋 Generating {len(targets)} products\n")

    results = []
    for i, product in enumerate(targets):
        print(f"[{i + 1}/{len(targets)}] {product['name']} ({product['collection']})")
        print("─" * 70)

        # Load reference image
        ref = load_image_b64(product["ref"])
        if not ref:
            print(f"   ✗ Reference image not found: {product['ref']}")
            results.append({"id": product["id"], "success": False, "error": "ref image missing"})
            continue
        ref_b64, ref_mime = ref

        # Step 1: Visual learning
        visual_desc = analyze_product(product, ref_b64, ref_mime)

        # Save visual description for reference
        desc_path = PRODUCTS_DIR / product["id"] / f"{product['id']}-visual-desc.txt"
        desc_path.write_text(visual_desc)

        time.sleep(2)

        # Step 2: Generate model photo
        img_data = generate_model_photo(product, ref_b64, ref_mime, visual_desc)

        if img_data:
            out_path = PRODUCTS_DIR / product["id"] / f"{product['id']}-model.jpg"
            out_path.write_bytes(img_data)
            size_kb = len(img_data) // 1024
            print(f"   ✅ Saved: {out_path.name} ({size_kb}KB)")
            results.append({"id": product["id"], "success": True, "size_kb": size_kb})
        else:
            results.append({"id": product["id"], "success": False, "error": "no image returned"})

        if i < len(targets) - 1:
            print(f"\n   ⏸  Rate limiting: {RATE_LIMIT_DELAY}s...\n")
            time.sleep(RATE_LIMIT_DELAY)

    # Summary
    print("\n" + "=" * 70)
    ok = [r for r in results if r["success"]]
    fail = [r for r in results if not r["success"]]
    print(f"✅ {len(ok)}/{len(results)} successful")
    if fail:
        print(f"❌ Failed: {[r['id'] for r in fail]}")

    report = PRODUCTS_DIR / "ACCURATE_MODELS_REPORT.json"
    report.write_text(json.dumps(results, indent=2))
    print(f"📄 Report: {report}")


if __name__ == "__main__":
    ids = sys.argv[1:] or None
    run(ids)
