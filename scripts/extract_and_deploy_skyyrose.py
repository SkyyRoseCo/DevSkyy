#!/usr/bin/env python3
"""
SkyyRose Site Extraction & Deployment Orchestrator.

This script orchestrates the complete SkyyRose WordPress site deployment:
1. Extract assets from updev 4/
2. Generate 3D models using ProductAssetPipeline
3. Generate Elementor templates
4. Deploy to WordPress
5. Configure WooCommerce
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wordpress.collection_page_manager import (
    CollectionType,
    WordPressCollectionPageManager,
    WordPressConfig,
)
from wordpress.elementor import SKYYROSE_BRAND_KIT, ElementorConfig, ElementorTemplate
from wordpress.page_builders import (
    AboutPageBuilder,
    BlogPageBuilder,
    CollectionExperienceBuilder,
    HomePageBuilder,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Directories
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
TEMPLATES_DIR = PROJECT_ROOT / "wordpress" / "elementor_templates"
SPECS_DIR = ASSETS_DIR / "specifications"


class SkyyRoseDeploymentOrchestrator:
    """Orchestrate complete SkyyRose WordPress deployment."""

    def __init__(
        self,
        wordpress_url: str | None = None,
        wordpress_username: str | None = None,
        wordpress_app_password: str | None = None,
    ) -> None:
        """Initialize orchestrator with WordPress credentials."""
        self.wordpress_url = wordpress_url
        self.wordpress_username = wordpress_username
        self.wordpress_app_password = wordpress_app_password

        # Initialize WordPress client only if credentials provided
        if wordpress_url and wordpress_username and wordpress_app_password:
            wp_config = WordPressConfig(
                wp_url=wordpress_url,
                username=wordpress_username,
                app_password=wordpress_app_password,
            )
            self.wp_manager = WordPressCollectionPageManager(config=wp_config)
        else:
            self.wp_manager = None
            logger.warning(
                "WordPress credentials not provided - Phase 3 deployment will be skipped"
            )

    async def phase_1_5_generate_3d_models(self) -> dict[str, str]:
        """Phase 1.5: Generate 3D models from extracted product images.

        Uses Tripo3D API to convert product reference images to GLB/USDZ
        models for web and AR (Apple Quick Look).

        Requires: TRIPO_API_KEY environment variable
        """
        logger.info("Phase 1.5: Generating 3D models from extracted images...")

        try:
            from agents.tripo_agent import TripoAssetAgent, TripoConfig

            PROJECT_ROOT = Path(__file__).parent.parent
            ASSETS_DIR = PROJECT_ROOT / "assets"
            EXTRACTED_DIR = ASSETS_DIR / "3d-models"
            OUTPUT_DIR = ASSETS_DIR / "3d-models-generated"

            # Check if images exist
            if not EXTRACTED_DIR.exists():
                logger.warning("No extracted assets found. Skipping Phase 1.5.")
                return {"status": "skipped", "reason": "no_assets"}

            # Initialize Tripo agent
            tripo_config = TripoConfig.from_env()
            TripoAssetAgent(config=tripo_config)

            logger.info("✓ Tripo3D agent initialized")
            logger.info(f"  Input directory: {EXTRACTED_DIR}")
            logger.info(f"  Output directory: {OUTPUT_DIR}")

            return {
                "status": "ready",
                "message": "Run: python3 scripts/generate_3d_models_from_assets.py to generate 3D models",
            }

        except ImportError as e:
            logger.warning(f"Skipping Phase 1.5 - missing dependency: {e}")
            return {"status": "skipped", "reason": "missing_dependency"}
        except Exception as e:
            logger.error(f"Phase 1.5 failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def phase_2_generate_templates(self) -> dict[str, ElementorTemplate]:
        """Phase 2: Generate Elementor templates for all page types."""
        logger.info("Phase 2: Generating Elementor templates...")
        templates = {}

        # Create ElementorConfig with SkyyRose brand kit
        config = ElementorConfig(brand_kit=SKYYROSE_BRAND_KIT)

        try:
            # Homepage
            logger.info("  Generating homepage template...")
            home_builder = HomePageBuilder(config=config)
            home_template = home_builder.generate()
            templates["home"] = home_template

            # Product page (requires specific product_id and glb_url, so we'll template it)
            logger.info("  Preparing product page template...")
            # Note: Product pages are generated per-product with specific GLB URLs
            # Skipping for now as a template; will be generated per-product during deployment
            logger.info("    (Product pages generated per-product with specific 3D models)")

            # Collection pages (3 variants)
            for collection_type in CollectionType:
                logger.info(f"  Generating {collection_type.value} collection template...")
                collection_builder = CollectionExperienceBuilder(config=config)
                # Experience URLs map to the Three.js HTML experiences in wordpress/collection_templates/
                experience_url = f"https://skyyrose.local/experiences/{collection_type.value.lower()}-collection/"
                collection_template = collection_builder.generate(
                    collection_type=collection_type,
                    experience_url=experience_url,
                )
                templates[collection_type.value] = collection_template

            # About page
            logger.info("  Generating about page template...")
            about_builder = AboutPageBuilder(config=config)
            about_template = about_builder.generate()
            templates["about"] = about_template

            # Blog page
            logger.info("  Generating blog page template...")
            blog_builder = BlogPageBuilder(config=config)
            blog_template = blog_builder.generate()
            templates["blog"] = blog_template

            logger.info(f"✓ Generated {len(templates)} templates")
            return templates

        except Exception as e:
            logger.error(f"✗ Template generation failed: {e}")
            raise

    async def phase_3_deploy_pages(self, templates: dict[str, ElementorTemplate]) -> None:
        """Phase 3: Deploy pages to WordPress."""
        if not self.wp_manager:
            logger.warning("Skipping Phase 3 - WordPress credentials not provided")
            return

        logger.info("Phase 3: Deploying pages to WordPress...")

        try:
            # Deploy homepage
            logger.info("  Deploying homepage...")
            await self.wp_manager.create_page(
                title="SkyyRose",
                slug="home",
                template_json=templates["home"].to_json(),
            )

            # Deploy collection pages
            for collection_type in CollectionType:
                logger.info(f"  Deploying {collection_type.value} collection page...")
                await self.wp_manager.create_collection_page(
                    collection_type=collection_type,
                    html_file_path=str(
                        PROJECT_ROOT
                        / "wordpress"
                        / "collection_templates"
                        / f"skyyrose-{collection_type.value.lower()}-garden-production.html"
                    ),
                )

            # Deploy about page
            logger.info("  Deploying about page...")
            await self.wp_manager.create_page(
                title="About SkyyRose",
                slug="about",
                template_json=templates["about"].to_json(),
            )

            # Deploy blog page
            logger.info("  Deploying blog page...")
            await self.wp_manager.create_page(
                title="Journal",
                slug="blog",
                template_json=templates["blog"].to_json(),
            )

            logger.info("✓ All pages deployed to WordPress")

        except Exception as e:
            logger.error(f"✗ WordPress deployment failed: {e}")
            raise

    async def run(self) -> None:
        """Execute full deployment pipeline."""
        logger.info("=" * 80)
        logger.info("SkyyRose Cinematic WordPress Site - Deployment Orchestrator")
        logger.info("=" * 80)

        try:
            # Create output directories
            TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

            # Phase 1.5: Generate 3D models (optional, requires Tripo API key)
            model_result = await self.phase_1_5_generate_3d_models()
            if model_result.get("status") == "ready":
                logger.info("✓ Phase 1.5: 3D model generation ready")
            elif model_result.get("status") == "failed":
                logger.error(f"Phase 1.5 failed: {model_result.get('error')}")

            # Phase 2: Generate templates
            templates = await self.phase_2_generate_templates()

            # Export templates to files for manual review
            for name, template in templates.items():
                output_path = TEMPLATES_DIR / f"{name}.json"
                template.to_file(str(output_path))
                logger.info(f"  Saved template: {output_path}")

            # Phase 3: Deploy pages (requires WordPress credentials)
            if self.wordpress_url and self.wordpress_username and self.wordpress_app_password:
                await self.phase_3_deploy_pages(templates)
            else:
                logger.warning("WordPress credentials not provided - skipping Phase 3 deployment")

            logger.info("=" * 80)
            logger.info("✓ Deployment completed successfully!")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"✗ Deployment failed: {e}")
            raise


async def main():
    """Main entry point."""
    # For now, just generate templates without WordPress deployment
    # User can provide credentials to enable Phase 3

    orchestrator = SkyyRoseDeploymentOrchestrator(
        wordpress_url=None,
        wordpress_username=None,
        wordpress_app_password=None,
    )

    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())
