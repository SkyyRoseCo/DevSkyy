#!/usr/bin/env python3
"""
Prepare SkyyRose LoRA Training Dataset.

Creates a comprehensive dataset with ALL brand knowledge:
- 39 enhanced product photos
- Collection-specific captions
- Brand DNA and style keywords
- Trigger words and concept tags

For training SDXL LoRA to generate authentic SkyyRose imagery.
"""

import json
import shutil
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent

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


def detect_collection(filename: str) -> str:
    """Detect collection from filename."""
    filename_lower = filename.lower()
    if "black" in filename_lower or "noir" in filename_lower:
        return "BLACK_ROSE"
    elif "love" in filename_lower or "heart" in filename_lower:
        return "LOVE_HURTS"
    else:
        return "SIGNATURE"


def detect_garment_details(filename: str) -> dict:
    """Extract detailed garment information from filename."""
    filename_lower = filename.lower()

    # Garment type
    if any(word in filename_lower for word in ["tee", "t-shirt"]):
        garment_type = "tee"
        garment_full = "luxury t-shirt"
    elif "hoodie" in filename_lower or "hooded" in filename_lower:
        garment_type = "hoodie"
        garment_full = "premium hoodie"
    elif "sweatshirt" in filename_lower or "crewneck" in filename_lower:
        garment_type = "sweatshirt"
        garment_full = "luxury crewneck sweatshirt"
    elif "shorts" in filename_lower:
        garment_type = "shorts"
        garment_full = "premium shorts"
    elif "sherpa" in filename_lower or "jacket" in filename_lower:
        garment_type = "sherpa"
        garment_full = "luxury sherpa jacket"
    elif "beanie" in filename_lower or "hat" in filename_lower:
        garment_type = "beanie"
        garment_full = "signature beanie"
    elif "dress" in filename_lower:
        garment_type = "dress"
        garment_full = "luxury hooded dress"
    else:
        garment_type = "apparel"
        garment_full = "premium streetwear"

    # Color/style details from filename
    details = []
    if "cotton candy" in filename_lower:
        details.append("cotton candy colorway")
    if "lavender" in filename_lower or "orchid" in filename_lower:
        details.append("lavender rose design")
    if "crop" in filename_lower:
        details.append("cropped fit")
    if "original label" in filename_lower:
        details.append("original label")
    if "red rose" in filename_lower:
        details.append("red rose embroidery")
    if "pink" in filename_lower:
        details.append("pink smoke colorway")
    if "mint" in filename_lower:
        details.append("mint and lavender")
    if "yay bridge" in filename_lower:
        details.append("yay bridge set")

    return {
        "type": garment_type,
        "full_name": garment_full,
        "details": details,
    }


def generate_training_caption(
    filename: str,
    collection: str,
    garment_info: dict,
) -> str:
    """
    Generate detailed training caption for LoRA.

    Format: trigger_word + collection + garment + details + style + quality
    """
    collection_data = BRAND_DNA["collections"][collection]

    # Base caption with trigger
    caption_parts = [
        collection_data["trigger"],  # e.g., "skyyrose signature collection"
        garment_info["full_name"],
    ]

    # Add specific details
    if garment_info["details"]:
        caption_parts.extend(garment_info["details"])

    # Add collection mood and keywords
    caption_parts.append(collection_data["mood"])
    caption_parts.extend(collection_data["keywords"][:3])  # Top 3 keywords

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

    # Join with commas
    caption = ", ".join(caption_parts)

    return caption


def prepare_dataset() -> dict:
    """
    Prepare complete LoRA training dataset.

    Returns:
        Dataset metadata
    """
    # Load enhanced products manifest
    manifest_path = project_root / "assets" / "enhanced_products" / "all" / "manifest.json"

    with open(manifest_path) as f:
        products = json.load(f)

    print("=== SkyyRose LoRA Dataset Preparation ===\n")
    print(f"Processing {len(products)} products\n")
    print("Brand DNA:")
    print(f"  Trigger word: {BRAND_DNA['trigger_word']}")
    print(f"  Collections: {', '.join(BRAND_DNA['collections'].keys())}")
    print(f"  Core values: {', '.join(BRAND_DNA['core_values'][:3])}")

    # Output directory
    dataset_dir = project_root / "datasets" / "skyyrose_lora_v1"
    images_dir = dataset_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Prepare dataset records
    dataset_records = []
    collection_counts = {"BLACK_ROSE": 0, "LOVE_HURTS": 0, "SIGNATURE": 0}

    for idx, product_data in enumerate(products):
        if not product_data["success"]:
            continue

        # Source image
        source_image = Path(product_data["enhanced"])

        # Detect collection and garment details
        collection = product_data.get("collection", detect_collection(source_image.name))
        garment_info = detect_garment_details(source_image.name)

        # Generate caption
        caption = generate_training_caption(source_image.name, collection, garment_info)

        # Copy image to dataset
        image_filename = f"{idx:04d}_{source_image.stem}.jpg"
        dest_image = images_dir / image_filename
        shutil.copy2(source_image, dest_image)

        # Create dataset record
        record = {
            "file_name": image_filename,
            "text": caption,
            "collection": collection,
            "garment_type": garment_info["type"],
            "source": str(source_image),
        }

        dataset_records.append(record)
        collection_counts[collection] += 1

        print(f"  [{idx + 1}/{len(products)}] {collection}: {garment_info['full_name']}")

    # Save metadata.jsonl (required for diffusers training)
    metadata_path = dataset_dir / "metadata.jsonl"
    with open(metadata_path, "w") as f:
        for record in dataset_records:
            # Only include file_name and text for training
            training_record = {
                "file_name": record["file_name"],
                "text": record["text"],
            }
            f.write(json.dumps(training_record) + "\n")

    # Save full dataset manifest
    manifest = {
        "version": "v1.0.0",
        "created": "2026-01-08",
        "brand": BRAND_DNA,
        "total_images": len(dataset_records),
        "collections": collection_counts,
        "records": dataset_records,
    }

    manifest_path = dataset_dir / "dataset_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Create training config
    training_config = {
        "model_name": "stabilityai/stable-diffusion-xl-base-1.0",
        "vae_name": "madebyollin/sdxl-vae-fp16-fix",
        "dataset_dir": str(dataset_dir),
        "output_dir": str(project_root / "models" / "skyyrose_lora_v1"),
        "resolution": 1024,
        "train_batch_size": 1,
        "num_train_epochs": 100,
        "learning_rate": 1e-4,
        "lr_scheduler": "constant",
        "mixed_precision": "fp16",
        "gradient_accumulation_steps": 4,
        "checkpointing_steps": 500,
        "validation_prompt": f"{BRAND_DNA['trigger_word']} signature collection luxury hoodie, premium streetwear, professional photography",
        "lora_rank": 64,
        "seed": 42,
    }

    config_path = dataset_dir / "training_config.json"
    with open(config_path, "w") as f:
        json.dump(training_config, f, indent=2)

    print(f"\n{'=' * 60}")
    print("✅ Dataset Preparation Complete!")
    print(f"{'=' * 60}")
    print(f"\nDataset location: {dataset_dir}")
    print(f"Total images: {len(dataset_records)}")
    print("Collections:")
    for collection, count in collection_counts.items():
        print(f"  {collection}: {count} images")
    print(f"\nMetadata: {metadata_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Training config: {config_path}")

    print("\n📋 Next Steps:")
    print("  1. Review captions in metadata.jsonl")
    print("  2. Copy dataset to lora-training-monitor Space")
    print("  3. Start training with training_config.json")
    print("  4. Monitor progress in HuggingFace Space")

    return manifest


if __name__ == "__main__":
    prepare_dataset()
