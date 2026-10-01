#!/usr/bin/env python3
"""
CLI wrapper for training SkyyRose LoRA models from WooCommerce products.

Usage:
    python scripts/train_lora_from_products.py \\
        --collections BLACK_ROSE SIGNATURE \\
        --max-products 50 \\
        --epochs 100 \\
        --version v1.1.0

Examples:
    # Train on all BLACK_ROSE products
    python scripts/train_lora_from_products.py --collections BLACK_ROSE

    # Preview dataset without training
    python scripts/train_lora_from_products.py --collections BLACK_ROSE --preview-only

    # Train with specific version
    python scripts/train_lora_from_products.py --collections BLACK_ROSE LOVE_HURTS --version v2.0.0
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from imagery.lora_trainer import SkyyRoseLoRATrainer
from imagery.product_training_dataset import fetch_products_from_woocommerce


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train SkyyRose LoRA from WooCommerce products",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--collections",
        nargs="+",
        choices=["BLACK_ROSE", "LOVE_HURTS", "SIGNATURE"],
        help="Product collections to include (space-separated)",
    )

    parser.add_argument(
        "--max-products",
        type=int,
        help="Maximum number of products to include",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of training epochs (default: 100)",
    )

    parser.add_argument(
        "--version",
        type=str,
        help="LoRA version string (e.g., v1.1.0). If omitted, auto-increments.",
    )

    parser.add_argument(
        "--min-quality",
        type=float,
        default=0.7,
        help="Minimum image quality score 0.0-1.0 (default: 0.7)",
    )

    parser.add_argument(
        "--preview-only",
        action="store_true",
        help="Preview dataset without training",
    )

    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path("./models/skyyrose-luxury-lora"),
        help="Path to save LoRA model (default: ./models/skyyrose-luxury-lora)",
    )

    parser.add_argument(
        "--progress-dir",
        type=Path,
        default=Path("./models/training-runs"),
        help="Directory for progress logs (default: ./models/training-runs)",
    )

    return parser.parse_args()


def print_banner() -> None:
    """Print CLI banner."""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   SkyyRose LoRA Training - Product-to-Model Pipeline        ║")
    print("║   SkyyRose model training            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()


def print_dataset_summary(products: list[Any]) -> None:
    """Print dataset summary statistics."""
    total_images = sum(len(p.image_urls) for p in products)
    collections_count: dict[str, int] = {}

    for p in products:
        collections_count[p.collection] = collections_count.get(p.collection, 0) + 1

    avg_quality = sum(p.quality_score for p in products) / len(products) if products else 0

    print("\n📊 Dataset Summary:")
    print(f"   Total Products: {len(products)}")
    print(f"   Total Images: {total_images}")
    print(f"   Average Quality: {avg_quality:.2f}")
    print("\n   Collections:")
    for collection, count in sorted(collections_count.items()):
        print(f"     • {collection}: {count} products")
    print()


async def preview_dataset(
    collections: list[str] | None,
    max_products: int | None,
    min_quality: float,
) -> None:
    """Preview dataset without training."""
    print("🔍 Fetching products from WooCommerce...")

    products = await fetch_products_from_woocommerce(
        collections=collections,
        max_products=max_products,
        min_images=2,
    )

    if not products:
        print("❌ No products found matching criteria")
        return

    print(f"✅ Found {len(products)} products")
    print_dataset_summary(products)

    # Show sample products
    print("📦 Sample Products:")
    for i, product in enumerate(products[:5], 1):
        print(f"\n   {i}. {product.name} (SKU: {product.sku})")
        print(f"      Collection: {product.collection}")
        print(f"      Images: {len(product.image_urls)}")
        print(f"      Quality: {product.quality_score:.2f}")

    if len(products) > 5:
        print(f"\n   ... and {len(products) - 5} more products")


async def monitor_progress(progress_file: Path) -> None:
    """Monitor training progress from JSON file."""
    import json

    last_epoch = -1
    start_time = time.time()

    print("\n🚀 Training Started")
    print("─" * 64)

    while True:
        try:
            if progress_file.exists():
                with open(progress_file) as f:
                    progress = json.load(f)

                status = progress.get("status", "unknown")

                if status == "completed":
                    elapsed = time.time() - start_time
                    print(f"\n✅ Training Completed in {elapsed / 3600:.1f} hours")
                    print(f"   Final Loss: {progress.get('loss', 0):.4f}")
                    print(f"   Model Path: {progress.get('model_path', 'N/A')}")
                    break

                elif status == "failed":
                    print(f"\n❌ Training Failed: {progress.get('error', 'Unknown error')}")
                    break

                elif status == "training":
                    current_epoch = progress.get("current_epoch", 0)
                    total_epochs = progress.get("total_epochs", 0)
                    loss = progress.get("loss", 0)
                    lr = progress.get("learning_rate", 0)
                    progress_pct = progress.get("progress_percentage", 0)
                    eta_seconds = progress.get("remaining_seconds", 0)

                    # Only print updates when epoch changes
                    if current_epoch != last_epoch:
                        eta_hours = eta_seconds / 3600
                        print(
                            f"   Epoch {current_epoch}/{total_epochs} "
                            f"({progress_pct:.1f}%) | "
                            f"Loss: {loss:.4f} | "
                            f"LR: {lr:.2e} | "
                            f"ETA: {eta_hours:.1f}h"
                        )
                        last_epoch = current_epoch

            await asyncio.sleep(5)  # Poll every 5 seconds

        except KeyboardInterrupt:
            print("\n⚠️  Monitoring stopped (training continues in background)")
            print(f"   Progress file: {progress_file}")
            print(
                "   Monitor at: https://huggingface.co/spaces/damBruh/skyyrose-lora-training-monitor"
            )
            break
        except Exception as e:
            print(f"⚠️  Error reading progress: {e}")
            await asyncio.sleep(5)


async def train(
    collections: list[str] | None,
    max_products: int | None,
    epochs: int,
    version: str | None,
    min_quality: float,
    model_path: Path,
    progress_dir: Path,
) -> None:
    """Execute training workflow."""
    print("🔧 Initializing LoRA trainer...")

    trainer = SkyyRoseLoRATrainer(
        model_path=str(model_path),
        base_model="stabilityai/stable-diffusion-xl-base-1.0",
    )

    print("📋 Training Configuration:")
    print(f"   Collections: {', '.join(collections) if collections else 'ALL'}")
    print(f"   Max Products: {max_products or 'No limit'}")
    print(f"   Epochs: {epochs}")
    print(f"   Min Quality: {min_quality}")
    print(f"   Version: {version or 'Auto-increment'}")
    print()

    print("⏳ Preparing dataset from WooCommerce products...")

    # Start training (this is async and returns immediately)
    model_path_result = await trainer.train_from_products(
        collections=collections,
        epochs=epochs,
        version=version,
    )

    print("\n✅ Training initiated successfully")
    print(f"   Model will be saved to: {model_path_result}")
    print(f"   Version: {version or 'Auto-generated'}")
    print()

    # Monitor progress
    version_used = version or "latest"
    progress_file = progress_dir / version_used / "progress.json"

    print(f"📊 Live monitoring from: {progress_file}")
    print(
        "🌐 HuggingFace Space: https://huggingface.co/spaces/damBruh/skyyrose-lora-training-monitor"
    )
    print()

    # Wait a moment for progress file to be created
    await asyncio.sleep(2)

    if progress_file.parent.exists():
        await monitor_progress(progress_file)
    else:
        print("⚠️  Progress file not found. Training may be running in background.")
        print(f"   Check: {progress_file}")


async def main() -> None:
    """Main entry point."""
    args = parse_args()

    print_banner()

    try:
        if args.preview_only:
            await preview_dataset(
                collections=args.collections,
                max_products=args.max_products,
                min_quality=args.min_quality,
            )
        else:
            await train(
                collections=args.collections,
                max_products=args.max_products,
                epochs=args.epochs,
                version=args.version,
                min_quality=args.min_quality,
                model_path=args.model_path,
                progress_dir=args.progress_dir,
            )

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
