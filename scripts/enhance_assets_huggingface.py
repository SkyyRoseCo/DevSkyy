#!/usr/bin/env python3
"""
HuggingFace Asset Enhancement CLI
==================================

Production-grade CLI for enhancing SkyyRose product assets using HuggingFace models.

This script processes your product images and generates high-quality 3D models
using HuggingFace's best image-to-3D models (Hunyuan3D 2.0, InstantMesh, TripoSR).

Usage:
    # Enhance a single asset
    python scripts/enhance_assets_huggingface.py single \\
        --image "generated_assets/product_images/_Signature Collection_/hoodie.jpg" \\
        --name "SkyyRose Signature Hoodie" \\
        --collection "SIGNATURE"

    # Enhance entire collection
    python scripts/enhance_assets_huggingface.py collection \\
        --path "generated_assets/product_images/_Love Hurts Collection_/" \\
        --name "LOVE_HURTS"

    # Enhance all collections
    python scripts/enhance_assets_huggingface.py all \\
        --output-dir "generated_assets/3d_models"

    # List available models
    python scripts/enhance_assets_huggingface.py models

Environment Variables:
    HUGGINGFACE_API_TOKEN or HF_TOKEN: Your HuggingFace API token (required)
    HF_PRIMARY_MODEL: Primary 3D model (default: tencent/Hunyuan3D-2)
    HF_QUALITY: Quality preset (draft, standard, high, production)
    HF_OUTPUT_DIR: Output directory for 3D models

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def setup_logging() -> None:
    """Configure structured logging."""
    import structlog

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def print_banner() -> None:
    """Print CLI banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ╔═╗╦╔═╦ ╦╦ ╦╦═╗╔═╗╔═╗╔═╗                                                ║
║     ╚═╗╠╩╗╚╦╝╚╦╝╠╦╝║ ║╚═╗║╣                                                 ║
║     ╚═╝╩ ╩ ╩  ╩ ╩╚═╚═╝╚═╝╚═╝                                                ║
║                                                                              ║
║     HuggingFace Asset Enhancement Pipeline                                   ║
║     Generate high-quality 3D models from your product images                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_result_summary(result: Any) -> None:
    """Print a summary of enhancement results."""
    print("\n" + "=" * 60)
    print("ENHANCEMENT RESULTS")
    print("=" * 60)

    if hasattr(result, "collection_name"):
        # Collection result
        print(f"Collection: {result.collection_name}")
        print(f"Total Assets: {result.total_assets}")
        print(f"Successful: {result.successful}")
        print(f"Failed: {result.failed}")
        print(f"Duration: {result.duration_seconds:.2f}s")

        if result.results:
            print("\nGenerated Models:")
            for r in result.results:
                status_icon = "✓" if r.status == "completed" else "✗"
                print(f"  {status_icon} {r.product_name}")
                if r.glb_path:
                    print(f"      GLB: {r.glb_path}")
                if r.errors:
                    for err in r.errors:
                        print(f"      Error: {err.get('error', 'Unknown')}")
    else:
        # Single asset result
        status_icon = "✓" if result.status == "completed" else "✗"
        print(f"{status_icon} {result.product_name}")
        print(f"   Collection: {result.collection}")
        print(f"   Duration: {result.duration_seconds:.2f}s")
        if result.glb_path:
            print(f"   GLB Model: {result.glb_path}")
        if result.usdz_path:
            print(f"   USDZ Model: {result.usdz_path}")
        if result.thumbnail_path:
            print(f"   Thumbnail: {result.thumbnail_path}")

        if result.models_3d:
            print("\n   Generated Models:")
            for model in result.models_3d:
                print(f"     - {model.model_used}")
                print(f"       Quality: {model.quality_score:.1f}")
                print(f"       Time: {model.generation_time_ms:.0f}ms")

        if result.errors:
            print("\n   Errors:")
            for err in result.errors:
                print(f"     - {err.get('stage', 'unknown')}: {err.get('error', 'Unknown error')}")

    print("=" * 60 + "\n")


async def enhance_single(args: argparse.Namespace) -> int:
    """Enhance a single product image."""
    from orchestration.huggingface_asset_enhancer import (
        EnhancerConfig,
        HuggingFaceAssetEnhancerWithTextures,
    )

    print(f"\nEnhancing single asset: {args.image}")
    print(f"Product: {args.name}")
    print(f"Collection: {args.collection}")

    config = EnhancerConfig.from_env()

    # Override with CLI args
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.quality:
        from orchestration.huggingface_asset_enhancer import HF3DQuality

        config.quality = HF3DQuality(args.quality)
    if args.no_texture_enhance:
        config.preprocessing_mode = "basic"

    enhancer = HuggingFaceAssetEnhancerWithTextures(config)

    try:
        result = await enhancer.enhance_asset_with_textures(
            image_path=args.image,
            product_name=args.name,
            collection=args.collection,
            enhance_source_texture=not args.no_texture_enhance,
        )

        print_result_summary(result)

        # Save result to JSON
        if args.save_metadata:
            metadata_path = Path(config.output_dir) / f"{result.asset_id}_metadata.json"
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_path, "w") as f:
                json.dump(result.model_dump(), f, indent=2, default=str)
            print(f"Metadata saved to: {metadata_path}")

        return 0 if result.status == "completed" else 1

    except Exception as e:
        print(f"\nError: {e}")
        return 1

    finally:
        await enhancer.close()


async def enhance_collection(args: argparse.Namespace) -> int:
    """Enhance all assets in a collection directory."""
    from orchestration.huggingface_asset_enhancer import (
        EnhancerConfig,
        HuggingFaceAssetEnhancer,
    )

    collection_path = Path(args.path)
    if not collection_path.exists():
        print(f"Error: Collection path not found: {args.path}")
        return 1

    # Auto-detect collection name from path
    collection_name = args.name or collection_path.name.strip("_").replace("_", " ")

    print(f"\nEnhancing collection: {collection_name}")
    print(f"Path: {args.path}")

    config = EnhancerConfig.from_env()

    # Override with CLI args
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.concurrency:
        config.batch_concurrency = args.concurrency

    enhancer = HuggingFaceAssetEnhancer(config)

    try:
        result = await enhancer.enhance_collection(
            collection_path=str(collection_path),
            collection_name=collection_name,
            output_dir=args.output_subdir,
        )

        print_result_summary(result)

        # Save collection metadata
        if args.save_metadata:
            metadata_path = (
                Path(config.output_dir)
                / collection_name.lower().replace(" ", "_")
                / "collection_metadata.json"
            )
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_path, "w") as f:
                json.dump(result.model_dump(), f, indent=2, default=str)
            print(f"Collection metadata saved to: {metadata_path}")

        return 0 if result.failed == 0 else 1

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        await enhancer.close()


async def enhance_all_collections(args: argparse.Namespace) -> int:
    """Enhance all collections in the generated_assets folder."""
    from orchestration.huggingface_asset_enhancer import (
        EnhancerConfig,
        HuggingFaceAssetEnhancer,
    )

    base_path = Path(args.base_path or "generated_assets/product_images")
    if not base_path.exists():
        print(f"Error: Base path not found: {base_path}")
        return 1

    # Find all collection directories
    collections = [d for d in base_path.iterdir() if d.is_dir()]

    if not collections:
        print(f"No collections found in: {base_path}")
        return 1

    print(f"\nFound {len(collections)} collections to enhance:")
    for c in collections:
        print(f"  - {c.name}")

    config = EnhancerConfig.from_env()
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.concurrency:
        config.batch_concurrency = args.concurrency

    enhancer = HuggingFaceAssetEnhancer(config)
    all_results = []
    total_successful = 0
    total_failed = 0

    try:
        for collection_dir in collections:
            collection_name = collection_dir.name.strip("_").replace("_", " ")
            print(f"\n{'=' * 60}")
            print(f"Processing: {collection_name}")
            print("=" * 60)

            try:
                result = await enhancer.enhance_collection(
                    collection_path=str(collection_dir),
                    collection_name=collection_name,
                )

                all_results.append(result)
                total_successful += result.successful
                total_failed += result.failed

                print(f"  ✓ Completed: {result.successful} successful, {result.failed} failed")

            except Exception as e:
                print(f"  ✗ Error processing collection: {e}")
                total_failed += 1

        # Print final summary
        print("\n" + "=" * 60)
        print("FINAL SUMMARY")
        print("=" * 60)
        print(f"Collections Processed: {len(collections)}")
        print(f"Total Successful: {total_successful}")
        print(f"Total Failed: {total_failed}")

        # Save summary
        if args.save_metadata:
            summary_path = Path(config.output_dir) / "enhancement_summary.json"
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            with open(summary_path, "w") as f:
                json.dump(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "collections_processed": len(collections),
                        "total_successful": total_successful,
                        "total_failed": total_failed,
                        "results": [r.model_dump() for r in all_results],
                    },
                    f,
                    indent=2,
                    default=str,
                )
            print(f"\nSummary saved to: {summary_path}")

        return 0 if total_failed == 0 else 1

    finally:
        await enhancer.close()


async def list_models(args: argparse.Namespace) -> int:
    """List available HuggingFace 3D models."""
    from orchestration.huggingface_asset_enhancer import HuggingFaceAssetEnhancer

    enhancer = HuggingFaceAssetEnhancer()

    try:
        models = await enhancer.list_available_models()

        print("\nAvailable HuggingFace 3D Models:")
        print("=" * 60)

        for model in models:
            print(f"\n  {model['name']}")
            print(f"    ID: {model['id']}")
            print(f"    Types: {', '.join(model['type'])}")
            print(f"    Quality: {model['quality']}")
            print(f"    Speed: {model['speed']}")
            print(f"    Has Textures: {'Yes' if model['has_textures'] else 'No'}")

        print("\n" + "=" * 60)
        print("\nRecommendations:")
        print("  - For best quality: Hunyuan3D 2.0 (tencent/Hunyuan3D-2)")
        print("  - For complex geometry: InstantMesh (TencentARC/InstantMesh)")
        print("  - For speed: TripoSR (stabilityai/TripoSR)")

        return 0

    finally:
        await enhancer.close()


async def check_environment(args: argparse.Namespace) -> int:
    """Check environment and dependencies."""
    print("\nEnvironment Check")
    print("=" * 60)

    all_ok = True

    # Check API token
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_TOKEN")
    print(f"\n  HuggingFace Token: {'✓ Set' if hf_token else '✗ NOT SET'}")
    if not hf_token:
        print("    ╭─────────────────────────────────────────────────────────╮")
        print("    │  To get your HuggingFace token:                        │")
        print("    │  1. Go to https://huggingface.co/settings/tokens       │")
        print("    │  2. Create a token with 'Read' access                  │")
        print("    │  3. Set it in your environment:                        │")
        print("    │     export HUGGINGFACE_API_TOKEN=hf_your_token_here    │")
        print("    │  Or add to .env file:                                  │")
        print("    │     HUGGINGFACE_API_TOKEN=hf_your_token_here           │")
        print("    ╰─────────────────────────────────────────────────────────╯")
        all_ok = False

    # Check Python dependencies
    print("\n  Python Dependencies:")
    dependencies = [
        ("aiohttp", "HTTP client"),
        ("pydantic", "Data validation"),
        ("structlog", "Logging"),
        ("PIL", "Image processing (Pillow)"),
        ("rembg", "Background removal"),
        ("huggingface_hub", "HuggingFace API"),
    ]

    missing_deps = []
    for module, desc in dependencies:
        try:
            if module == "PIL":
                __import__("PIL")
            else:
                __import__(module)
            print(f"    ✓ {module} ({desc})")
        except ImportError:
            print(f"    ✗ {module} ({desc}) - NOT INSTALLED")
            missing_deps.append(module.replace("PIL", "pillow"))
            all_ok = False

    if missing_deps:
        print(f"\n    Install missing: pip install {' '.join(missing_deps)}")

    # Check network connectivity
    print("\n  Network Connectivity:")
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://huggingface.co/api/models?limit=1",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        print("    ✓ HuggingFace API reachable")
                    else:
                        print(f"    ○ HuggingFace API returned status {resp.status}")
            except Exception as e:
                print(f"    ✗ Cannot reach HuggingFace API: {type(e).__name__}")
                print("      Check your network connection")
                all_ok = False
    except ImportError:
        print("    ○ Cannot test (aiohttp not installed)")

    # Check directories
    print("\n  Directories:")
    dirs_to_check = [
        "generated_assets/product_images",
        "generated_assets/3d_models",
        "hf_enhancement_cache",
    ]

    for d in dirs_to_check:
        path = Path(d)
        exists = path.exists()
        print(f"    {'✓' if exists else '○'} {d}")
        if not exists and args.create_dirs:
            path.mkdir(parents=True, exist_ok=True)
            print("      Created directory")

    # Count available assets
    print("\n  Available Assets:")
    product_images_path = Path("generated_assets/product_images")
    if product_images_path.exists():
        collections = [d for d in product_images_path.iterdir() if d.is_dir()]
        total_assets = 0
        for collection in collections:
            images = (
                list(collection.glob("*.jpg"))
                + list(collection.glob("*.jpeg"))
                + list(collection.glob("*.png"))
                + list(collection.glob("*.JPG"))
                + list(collection.glob("*.JPEG"))
                + list(collection.glob("*.PNG"))
            )
            count = len(images)
            total_assets += count
            print(f"    {collection.name}: {count} images")
        print(f"    Total: {total_assets} assets ready for enhancement")
    else:
        print("    No product images directory found")

    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("  ✓ Environment ready for asset enhancement!")
        print("\n  Run enhancement with:")
        print("    python scripts/enhance_assets_huggingface.py all")
    else:
        print("  ✗ Please fix the issues above before running enhancement")
    print("=" * 60)

    return 0 if all_ok else 1


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="HuggingFace Asset Enhancement CLI for SkyyRose",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enhance a single product image
  python enhance_assets_huggingface.py single \\
      --image "product.jpg" --name "My Product" --collection "SIGNATURE"

  # Enhance entire collection
  python enhance_assets_huggingface.py collection \\
      --path "generated_assets/product_images/_Love Hurts Collection_/"

  # Enhance all collections
  python enhance_assets_huggingface.py all

  # Check environment
  python enhance_assets_huggingface.py check --create-dirs

For more information, visit: https://github.com/skyyrose/devskyy
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Single asset command
    single_parser = subparsers.add_parser("single", help="Enhance a single asset")
    single_parser.add_argument("--image", "-i", required=True, help="Path to product image")
    single_parser.add_argument("--name", "-n", required=True, help="Product name")
    single_parser.add_argument(
        "--collection",
        "-c",
        default="SIGNATURE",
        choices=["SIGNATURE", "LOVE_HURTS", "BLACK_ROSE"],
        help="Collection name",
    )
    single_parser.add_argument("--output-dir", "-o", help="Output directory")
    single_parser.add_argument(
        "--quality",
        "-q",
        choices=["draft", "standard", "high", "production"],
        default="production",
        help="Quality preset",
    )
    single_parser.add_argument(
        "--no-texture-enhance",
        action="store_true",
        help="Skip texture enhancement",
    )
    single_parser.add_argument(
        "--save-metadata",
        "-m",
        action="store_true",
        default=True,
        help="Save metadata JSON",
    )

    # Collection command
    collection_parser = subparsers.add_parser("collection", help="Enhance a collection")
    collection_parser.add_argument(
        "--path", "-p", required=True, help="Path to collection directory"
    )
    collection_parser.add_argument(
        "--name", "-n", help="Collection name (auto-detected if not provided)"
    )
    collection_parser.add_argument("--output-dir", "-o", help="Output directory")
    collection_parser.add_argument("--output-subdir", help="Output subdirectory")
    collection_parser.add_argument(
        "--concurrency", "-c", type=int, default=3, help="Concurrent operations"
    )
    collection_parser.add_argument(
        "--save-metadata", "-m", action="store_true", default=True, help="Save metadata"
    )

    # All collections command
    all_parser = subparsers.add_parser("all", help="Enhance all collections")
    all_parser.add_argument(
        "--base-path",
        "-b",
        default="generated_assets/product_images",
        help="Base path containing collections",
    )
    all_parser.add_argument("--output-dir", "-o", help="Output directory")
    all_parser.add_argument(
        "--concurrency", "-c", type=int, default=3, help="Concurrent operations"
    )
    all_parser.add_argument(
        "--save-metadata", "-m", action="store_true", default=True, help="Save metadata"
    )

    # Models command
    subparsers.add_parser("models", help="List available HuggingFace 3D models")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check environment and dependencies")
    check_parser.add_argument(
        "--create-dirs", action="store_true", help="Create missing directories"
    )

    return parser


async def main() -> int:
    """Main entry point."""
    setup_logging()
    print_banner()

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "single": enhance_single,
        "collection": enhance_collection,
        "all": enhance_all_collections,
        "models": list_models,
        "check": check_environment,
    }

    handler = handlers.get(args.command)
    if handler:
        return await handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
