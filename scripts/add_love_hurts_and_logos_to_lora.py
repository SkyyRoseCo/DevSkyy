#!/usr/bin/env python3
"""
Add LOVE HURTS Collection and Logos to LoRA Dataset.

Processes:
1. LOVE HURTS collection products (51 images)
2. All brand logos (5 logos)
3. Enhances with Lanczos 4x upscaling
4. Generates detailed brand DNA captions
5. Appends to existing LoRA dataset

Usage:
    python3 scripts/add_love_hurts_and_logos_to_lora.py
"""

import asyncio
import json
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# SkyyRose Brand DNA (COMPLETE)
BRAND_DNA = {
    "name": "SkyyRose",
    "tagline": "",
    "trigger_word": "skyyrose",
    "core_values": [
        "authentic luxury",
        "emotional depth",
        "rebellious elegance",
        "premium streetwear",
        "artistic craftsmanship",
    ],
    "visual_identity": {
        "colors": {
            "primary": "#B76E79",  # Rose
            "secondary": "#1A1A1A",  # Black
            "accent": "#E6B8C0",  # Light Rose
        },
        "aesthetic": "gothic luxury meets streetwear elegance",
        "photography_style": "dramatic lighting, emotional depth, premium quality",
    },
    "collections": {
        "BLACK_ROSE": {
            "theme": "Gothic luxury, dark elegance, rebellious sophistication",
            "mood": "mysterious, powerful, unapologetically bold",
            "colors": "black, deep rose, charcoal, midnight tones",
            "keywords": ["gothic", "noir", "dark luxury", "rebellious", "dramatic"],
            "trigger": "skyyrose black_rose collection",
        },
        "LOVE_HURTS": {
            "theme": "Emotional authenticity, vulnerable strength, artistic passion",
            "mood": "raw emotion, authentic, artistically refined, heartfelt",
            "colors": "deep rose, burgundy, warm earth tones, emotional reds",
            "keywords": ["emotional", "authentic", "passionate", "heartfelt", "artistic"],
            "trigger": "skyyrose love_hurts collection",
        },
        "SIGNATURE": {
            "theme": "Understated luxury, confident elegance, everyday excellence",
            "mood": "confident, sophisticated, effortlessly premium, timeless",
            "colors": "rose, lavender, orchid, cotton candy pastels, premium whites",
            "keywords": ["luxury", "signature", "premium", "elegant", "timeless"],
            "trigger": "skyyrose signature collection",
        },
    },
}


def luxury_post_process(image: Image.Image) -> Image.Image:
    """Apply luxury finishing touches to product photos."""
    # Subtle sharpening for crisp details
    image = image.filter(ImageFilter.UnsharpMask(radius=2.0, percent=120, threshold=3))

    # Slight contrast enhancement
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.03)

    # Color accuracy refinement
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(1.02)

    # Brightness adjustment for product clarity
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.01)

    return image


def upscale_with_lanczos(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """High-quality Lanczos resampling to 1024x1024."""
    current_max = max(image.width, image.height)

    if current_max < max_size:
        # Calculate scale to reach max_size
        scale = max_size / current_max
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
    else:
        # Already large enough, just resize to max
        if image.width > image.height:
            new_width = max_size
            new_height = int(image.height * (max_size / image.width))
        else:
            new_height = max_size
            new_width = int(image.width * (max_size / image.height))

    return image.resize((new_width, new_height), Image.LANCZOS)


def detect_garment_type(filename: str) -> dict[str, any]:
    """Detect garment type from filename."""
    filename_lower = filename.lower()

    # Specific garment patterns
    if "jogger" in filename_lower or "pants" in filename_lower:
        return {
            "type": "luxury joggers",
            "full_name": "premium athletic joggers",
            "details": ["comfortable fit", "athletic streetwear"],
        }
    elif "windbreaker" in filename_lower and "jacket" in filename_lower:
        return {
            "type": "windbreaker jacket",
            "full_name": "premium windbreaker jacket",
            "details": ["weather resistant", "lightweight", "packable"],
        }
    elif "windbreaker" in filename_lower and "short" in filename_lower:
        return {
            "type": "windbreaker shorts",
            "full_name": "athletic windbreaker shorts",
            "details": ["quick dry", "athletic fit"],
        }
    elif "hoodie" in filename_lower or "hooded" in filename_lower:
        return {
            "type": "premium hoodie",
            "full_name": "luxury hooded sweatshirt",
            "details": ["soft fleece interior", "adjustable hood"],
        }
    elif "tee" in filename_lower or "t-shirt" in filename_lower:
        return {
            "type": "luxury t-shirt",
            "full_name": "premium graphic t-shirt",
            "details": ["soft cotton blend", "screen printed design"],
        }
    elif "short" in filename_lower:
        return {
            "type": "premium shorts",
            "full_name": "luxury athletic shorts",
            "details": ["comfortable waistband", "breathable fabric"],
        }
    elif "beanie" in filename_lower:
        return {
            "type": "signature beanie",
            "full_name": "embroidered beanie",
            "details": ["soft knit", "embroidered logo"],
        }
    elif "sherpa" in filename_lower:
        return {
            "type": "luxury sherpa jacket",
            "full_name": "premium sherpa fleece jacket",
            "details": ["ultra soft sherpa", "full zip closure"],
        }
    elif "crewneck" in filename_lower or "sweatshirt" in filename_lower:
        return {
            "type": "luxury crewneck sweatshirt",
            "full_name": "premium crewneck pullover",
            "details": ["fleece lined", "ribbed cuffs"],
        }
    else:
        return {
            "type": "premium streetwear",
            "full_name": "luxury streetwear piece",
            "details": ["high quality construction", "premium materials"],
        }


def generate_training_caption(
    filename: str, collection: str, garment_info: dict, is_logo: bool = False
) -> str:
    """Generate detailed training caption for LoRA."""
    collection_data = BRAND_DNA["collections"][collection]

    if is_logo:
        # Logo caption
        caption_parts = [
            f"{BRAND_DNA['trigger_word']} logo",
            f"{collection.lower().replace('_', ' ')} collection logo",
            collection_data["mood"],
        ]
        caption_parts.extend(collection_data["keywords"][:3])
        caption_parts.extend(
            [
                "brand identity",
                "luxury streetwear brand",
                "professional design",
                "vector quality",
            ]
        )
    else:
        # Product caption
        caption_parts = [
            collection_data["trigger"],  # e.g., "skyyrose love_hurts collection"
            garment_info["full_name"],
        ]

        # Add specific details
        if garment_info["details"]:
            caption_parts.extend(garment_info["details"])

        # Add collection mood and keywords
        caption_parts.append(collection_data["mood"])
        caption_parts.extend(collection_data["keywords"][:3])

        # Add quality descriptors
        caption_parts.extend(
            [
                "professional product photography",
                "studio lighting",
                "ultra detailed",
                "premium quality",
                "luxury streetwear brand",
            ]
        )

    return ", ".join(caption_parts)


async def enhance_and_add_to_dataset(
    input_path: Path, collection: str, dataset_dir: Path, is_logo: bool = False
) -> dict:
    """Enhance image and add to dataset."""
    print(f"  Processing: {input_path.name}")

    # Load image
    image = Image.open(input_path)

    # Convert to RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Upscale to 1024x1024
    enhanced = upscale_with_lanczos(image, max_size=1024)

    # Apply luxury post-processing
    enhanced = luxury_post_process(enhanced)

    # Detect garment type
    garment_info = detect_garment_type(input_path.name) if not is_logo else {}

    # Generate caption
    caption = generate_training_caption(input_path.name, collection, garment_info, is_logo)

    # Save enhanced image
    output_filename = f"{collection.lower()}_{input_path.stem}.jpg"
    output_path = dataset_dir / output_filename
    enhanced.save(output_path, "JPEG", quality=95, optimize=True)

    print(f"    ✓ Saved: {output_filename}")
    print(f"    Caption: {caption[:100]}...")

    return {
        "file_name": output_filename,
        "text": caption,
        "collection": collection,
        "original_file": str(input_path),
        "is_logo": is_logo,
    }


async def main():
    """Add LOVE HURTS products and logos to LoRA dataset."""

    print("=== Adding LOVE HURTS Collection + Logos to LoRA Dataset ===\n")

    # Dataset directory
    dataset_dir = project_root / "datasets" / "skyyrose_lora_v1"

    # Load existing metadata
    metadata_path = dataset_dir / "metadata.jsonl"
    existing_entries = []
    if metadata_path.exists():
        with open(metadata_path) as f:
            existing_entries = [json.loads(line) for line in f]

    print(f"Existing dataset: {len(existing_entries)} images\n")

    new_entries = []

    # Process LOVE HURTS collection
    print("=== Processing LOVE HURTS Collection ===")
    love_hurts_dir = Path(
        "/tmp/love_hurts_extraction/Love Hurts X SkyyRose Collection"
    )  # nosec B108 — one-shot extraction script

    love_hurts_images = []
    for ext in ["jpg", "jpeg", "png"]:
        love_hurts_images.extend(love_hurts_dir.rglob(f"*.{ext}"))

    # Filter out installers
    love_hurts_images = [
        img
        for img in love_hurts_images
        if not any(x in img.name.lower() for x in ["installer", ".pkg", ".dmg", "linear"])
    ]

    print(f"Found {len(love_hurts_images)} LOVE HURTS products\n")

    for img_path in love_hurts_images:
        try:
            entry = await enhance_and_add_to_dataset(img_path, "LOVE_HURTS", dataset_dir)
            new_entries.append(entry)
        except Exception as e:
            print(f"    ✗ Failed: {e}")

    # Process logos
    print("\n=== Processing Brand Logos ===")
    logo_paths = [
        project_root / "frontend/public/assets/logos/love-hurts-text-logo.png",
        project_root / "frontend/public/assets/logos/black-rose-trophy-cosmic.png",
        project_root / "frontend/public/assets/logos/signature-rose-rosegold.png",
        project_root / "frontend/public/assets/logos/love-hurts-trophy-red.png",
        project_root / "frontend/public/assets/logos/sr-monogram-rosegold.png",
    ]

    logo_collections = {
        "love-hurts-text-logo.png": "LOVE_HURTS",
        "black-rose-trophy-cosmic.png": "BLACK_ROSE",
        "signature-rose-rosegold.png": "SIGNATURE",
        "love-hurts-trophy-red.png": "LOVE_HURTS",
        "sr-monogram-rosegold.png": "SIGNATURE",
    }

    print(f"Found {len(logo_paths)} logos\n")

    for logo_path in logo_paths:
        if logo_path.exists():
            try:
                collection = logo_collections.get(logo_path.name, "SIGNATURE")
                entry = await enhance_and_add_to_dataset(
                    logo_path, collection, dataset_dir, is_logo=True
                )
                new_entries.append(entry)
            except Exception as e:
                print(f"    ✗ Failed {logo_path.name}: {e}")

    # Append to metadata
    print("\n=== Updating Dataset Metadata ===")
    with open(metadata_path, "a") as f:
        for entry in new_entries:
            f.write(json.dumps(entry) + "\n")

    # Update manifest
    manifest_path = dataset_dir / "dataset_manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    manifest["total_images"] = len(existing_entries) + len(new_entries)
    manifest["collections_count"] = {
        "BLACK_ROSE": sum(1 for e in existing_entries if e.get("collection") == "BLACK_ROSE")
        + sum(1 for e in new_entries if e.get("collection") == "BLACK_ROSE"),
        "LOVE_HURTS": sum(1 for e in new_entries if e.get("collection") == "LOVE_HURTS"),
        "SIGNATURE": sum(1 for e in existing_entries if e.get("collection") == "SIGNATURE")
        + sum(1 for e in new_entries if e.get("collection") == "SIGNATURE"),
    }
    manifest["includes_logos"] = True
    manifest["logo_count"] = sum(1 for e in new_entries if e.get("is_logo"))

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{'=' * 60}")
    print("✅ Dataset Updated Successfully!")
    print(f"{'=' * 60}")
    print(f"\nTotal images: {manifest['total_images']}")
    print(f"  SIGNATURE: {manifest['collections_count']['SIGNATURE']} images")
    print(f"  BLACK_ROSE: {manifest['collections_count']['BLACK_ROSE']} images")
    print(f"  LOVE_HURTS: {manifest['collections_count']['LOVE_HURTS']} images")
    print(f"  Brand logos: {manifest['logo_count']} images")

    print(f"\nNew additions: {len(new_entries)} images")
    print(
        f"  LOVE_HURTS products: {sum(1 for e in new_entries if e.get('collection') == 'LOVE_HURTS' and not e.get('is_logo'))}"
    )
    print(f"  Logos: {sum(1 for e in new_entries if e.get('is_logo'))}")

    print("\n📋 Dataset ready for LoRA training!")
    print(f"Location: {dataset_dir}")


if __name__ == "__main__":
    asyncio.run(main())
