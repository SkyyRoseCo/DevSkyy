"""SkyyRose HuggingFace Spaces Orchestrator.

Orchestrates HuggingFace Spaces for complete product pipeline using
free GPU inference for photography, 3D conversion, and virtual try-on.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from gradio_client import Client

logger = logging.getLogger(__name__)


@dataclass
class ProductSpecs:
    """Product specifications for pipeline."""

    name: str
    sku: str
    slug: str
    collection: str  # BLACK_ROSE, LOVE_HURTS, SIGNATURE
    garment_type: str
    color: str
    fabric: str
    price: float
    sizes: list[str] = field(default_factory=lambda: ["XS", "S", "M", "L", "XL", "2XL"])
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Result of product pipeline execution."""

    status: str
    url: str | None = None
    photos: dict[str, bytes] = field(default_factory=dict)
    model_3d: bytes | None = None
    errors: list[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=datetime.utcnow)


class WordPressAPI:
    """WordPress/WooCommerce API client."""

    def __init__(
        self,
        url: str | None = None,
        consumer_key: str | None = None,
        consumer_secret: str | None = None,
    ) -> None:
        """Initialize WordPress API client.

        Args:
            url: WordPress site URL
            consumer_key: WooCommerce consumer key
            consumer_secret: WooCommerce consumer secret
        """
        self.url = url or os.getenv("WORDPRESS_URL", "https://skyyrose.co")
        self.consumer_key = consumer_key or os.getenv("WOOCOMMERCE_KEY")
        self.consumer_secret = consumer_secret or os.getenv("WOOCOMMERCE_SECRET")
        self.api_base = f"{self.url}/wp-json/wc/v3"

    async def upload_media(
        self,
        file: bytes,
        filename: str,
        title: str | None = None,
    ) -> str | None:
        """Upload media file to WordPress.

        Args:
            file: File content as bytes
            filename: Name for the uploaded file
            title: Optional title for media

        Returns:
            Media URL or None on failure
        """
        try:
            media_url = f"{self.url}/wp-json/wp/v2/media"

            headers = {
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": self._get_content_type(filename),
            }

            response = requests.post(
                media_url,
                headers=headers,
                data=file,
                auth=(self.consumer_key, self.consumer_secret),
                timeout=60,
            )

            if response.status_code in (200, 201):
                data = response.json()
                logger.info(f"Uploaded media: {filename}")
                return data.get("source_url") or data.get("id")

            logger.error(f"Media upload failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Media upload error: {e}")
            return None

    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename."""
        ext = Path(filename).suffix.lower()
        content_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".glb": "model/gltf-binary",
            ".gltf": "model/gltf+json",
        }
        return content_types.get(ext, "application/octet-stream")

    async def create_product(
        self,
        name: str,
        sku: str,
        price: float,
        description: str,
        images: list[str],
        meta_data: list[dict] | None = None,
        categories: list[dict] | None = None,
    ) -> str | None:
        """Create WooCommerce product.

        Args:
            name: Product name
            sku: Stock keeping unit
            price: Product price
            description: Product description
            images: List of image IDs or URLs
            meta_data: Additional metadata
            categories: Product categories

        Returns:
            Product ID or None on failure
        """
        try:
            products_url = f"{self.api_base}/products"

            product_data = {
                "name": name,
                "type": "simple",
                "status": "publish",
                "regular_price": str(price),
                "description": description,
                "sku": sku,
                "images": [{"src": img} if isinstance(img, str) else {"id": img} for img in images],
                "meta_data": meta_data or [],
                "categories": categories or [],
            }

            response = requests.post(
                products_url,
                json=product_data,
                auth=(self.consumer_key, self.consumer_secret),
                timeout=30,
            )

            if response.status_code in (200, 201):
                data = response.json()
                logger.info(f"Created product: {name} (ID: {data.get('id')})")
                return data.get("id")

            logger.error(f"Product creation failed: {response.status_code} - {response.text}")
            return None

        except Exception as e:
            logger.error(f"Product creation error: {e}")
            return None


class SkyyRoseSpacesOrchestrator:
    """Orchestrates HuggingFace Spaces for complete product pipeline.

    Uses free GPU inference from HuggingFace Spaces for:
    - Product photography generation (SDXL)
    - 3D model conversion (TripoSR/InstantMesh)
    - Virtual try-on (IDM-VTON)

    Example:
        >>> orchestrator = SkyyRoseSpacesOrchestrator()
        >>> result = await orchestrator.full_product_pipeline({
        ...     'name': 'Essential Black Hoodie',
        ...     'sku': 'SRS-SIG-001',
        ...     'collection': 'SIGNATURE',
        ...     'garment_type': 'oversized hoodie',
        ...     'color': 'midnight black',
        ...     'fabric': 'premium brushed cotton fleece',
        ...     'price': 145.00
        ... })
    """

    COLLECTION_INTROS = {
        "BLACK_ROSE": "From the BLACK ROSE collection: where darkness meets elegance.",
        "LOVE_HURTS": "From the LOVE HURTS collection: emotional expression through wearable art.",
        "SIGNATURE": "From the SIGNATURE collection: refined essentials for elevated everyday wear.",
    }

    def __init__(
        self,
        hf_username: str | None = None,
        photo_space: str | None = None,
        model_3d_space: str | None = None,
        tryon_space: str | None = None,
    ) -> None:
        """Initialize orchestrator with HuggingFace Spaces.

        Args:
            hf_username: HuggingFace username for spaces
            photo_space: Custom photo generation space
            model_3d_space: Custom 3D conversion space
            tryon_space: Custom virtual try-on space
        """
        self.hf_username = hf_username or os.getenv("HF_USERNAME", "skyyrose")

        # Space endpoints (use public spaces as fallback)
        self._photo_space_id = photo_space or f"{self.hf_username}/skyyrose-product-photography"
        self._model_3d_space_id = model_3d_space or "stabilityai/TripoSR"
        self._tryon_space_id = tryon_space or "yisol/IDM-VTON"

        # Lazy-loaded clients
        self._photo_client = None
        self._model_3d_client = None
        self._tryon_client = None

        # WordPress API
        self.wp_api = WordPressAPI()

        logger.info("SkyyRose Spaces Orchestrator initialized")
        logger.info(f"  Photo Space: {self._photo_space_id}")
        logger.info(f"  3D Space: {self._model_3d_space_id}")
        logger.info(f"  Try-On Space: {self._tryon_space_id}")

    @property
    def photo_space(self) -> Client:
        """Lazy load photo generation space client."""
        if self._photo_client is None:
            try:
                self._photo_client = Client(self._photo_space_id)
            except Exception as e:
                logger.warning(f"Custom photo space not available: {e}")
                # Fallback to public SDXL space
                self._photo_client = Client("stabilityai/stable-diffusion-3-medium")
        return self._photo_client

    @property
    def model_3d_space(self) -> Client:
        """Lazy load 3D conversion space client."""
        if self._model_3d_client is None:
            self._model_3d_client = Client(self._model_3d_space_id)
        return self._model_3d_client

    @property
    def tryon_space(self) -> Client:
        """Lazy load virtual try-on space client."""
        if self._tryon_client is None:
            self._tryon_client = Client(self._tryon_space_id)
        return self._tryon_client

    async def full_product_pipeline(
        self,
        product_specs: ProductSpecs | dict,
    ) -> PipelineResult:
        """Complete automated pipeline using free HF Spaces.

        Args:
            product_specs: Product specifications

        Returns:
            PipelineResult with status and assets
        """
        # Convert dict to ProductSpecs if needed
        if isinstance(product_specs, dict):
            product_specs = ProductSpecs(
                name=product_specs["name"],
                sku=product_specs["sku"],
                slug=product_specs.get("slug", product_specs["sku"].lower()),
                collection=product_specs["collection"],
                garment_type=product_specs["garment_type"],
                color=product_specs["color"],
                fabric=product_specs["fabric"],
                price=product_specs["price"],
            )

        result = PipelineResult(status="in_progress")

        logger.info(f"🌹 Starting pipeline for: {product_specs.name}")

        try:
            # STAGE 1: Generate product photography
            logger.info("📸 Generating product photography...")
            photos = await self._generate_photos(product_specs)
            result.photos = photos

            if not photos:
                result.status = "failed"
                result.errors.append("Photo generation failed")
                return result

            # STAGE 2: Create 3D model
            logger.info("🎨 Creating 3D model...")
            hero_photo = photos.get("hero") or photos.get("angle_0")
            if hero_photo:
                model_3d = await self._create_3d_model(hero_photo)
                result.model_3d = model_3d
            else:
                logger.warning("No hero photo for 3D conversion")

            # STAGE 3: Deploy to WordPress
            logger.info("🚀 Deploying to skyyrose.co...")
            product_url = await self._deploy_to_wordpress(
                product_specs,
                photos,
                result.model_3d,
            )
            result.url = product_url

            if product_url:
                result.status = "deployed"
                logger.info(f"✅ Product live at: {product_url}")
            else:
                result.status = "partial"
                result.errors.append("WordPress deployment failed")

        except Exception as e:
            logger.exception(f"Pipeline error: {e}")
            result.status = "failed"
            result.errors.append(str(e))

        return result

    async def _generate_photos(self, specs: ProductSpecs) -> dict[str, bytes]:
        """Generate product photos via HF Space.

        Args:
            specs: Product specifications

        Returns:
            Dictionary of photo name to image bytes
        """
        photos = {}

        try:
            # Build prompt for SDXL
            prompt = self._build_photo_prompt(specs)

            # Generate multiple angles
            angles = [
                ("hero", "front view, hero shot"),
                ("front", "straight front view"),
                ("back", "back view"),
                ("side", "side profile view"),
                ("detail", "close-up fabric detail"),
            ]

            for angle_name, angle_desc in angles:
                full_prompt = f"{prompt}, {angle_desc}"

                try:
                    # Call HF Space
                    result = self.photo_space.predict(
                        prompt=full_prompt,
                        negative_prompt=self._negative_prompt(),
                        api_name="/generate",  # Adjust based on space API
                    )

                    # Handle result (could be path or URL)
                    if result:
                        if isinstance(result, str):
                            if result.startswith("http"):
                                response = requests.get(result, timeout=30)
                                photos[angle_name] = response.content
                            else:
                                # Local file path
                                with open(result, "rb") as f:
                                    photos[angle_name] = f.read()
                        elif isinstance(result, tuple):
                            # Some spaces return (image_path, ...)
                            img_path = result[0]
                            if isinstance(img_path, str):
                                if img_path.startswith("http"):
                                    response = requests.get(img_path, timeout=30)
                                    photos[angle_name] = response.content
                                else:
                                    with open(img_path, "rb") as f:
                                        photos[angle_name] = f.read()

                    logger.info(f"Generated {angle_name} photo")

                except Exception as e:
                    logger.warning(f"Failed to generate {angle_name}: {e}")

            # Set hero if we have any photos
            if photos and "hero" not in photos:
                first_key = next(iter(photos))
                photos["hero"] = photos[first_key]

        except Exception as e:
            logger.error(f"Photo generation failed: {e}")

        return photos

    def _build_photo_prompt(self, specs: ProductSpecs) -> str:
        """Build SDXL prompt for product photography."""
        collection_styles = {
            "BLACK_ROSE": "dark romantic aesthetic, gothic elegance, moody lighting",
            "LOVE_HURTS": "edgy romantic style, emotional depth, artistic expression",
            "SIGNATURE": "clean minimal aesthetic, timeless sophistication, classic luxury",
        }

        style = collection_styles.get(specs.collection, "luxury streetwear")

        return (
            f"Professional product photography of {specs.garment_type}, "
            f"{specs.color} colorway, {specs.fabric} fabric, "
            f"{style}, "
            f"studio lighting, white background, "
            f"8k, commercial fashion photography, luxury brand catalog, "
            f"SkyyRose aesthetic, Oakland streetwear meets high fashion"
        )

    def _negative_prompt(self) -> str:
        """Get negative prompt for generation."""
        return (
            "low quality, blurry, distorted, deformed, ugly, "
            "watermark, text, logo, mannequin, model, person wearing, "
            "wrinkled, dirty, amateur photography"
        )

    async def _create_3d_model(self, hero_image: bytes) -> bytes | None:
        """Convert image to 3D via HF Space.

        Args:
            hero_image: Hero image as bytes

        Returns:
            GLB model as bytes or None
        """
        try:
            import tempfile

            # Save image temporarily for upload
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(hero_image)
                tmp_path = tmp.name

            try:
                # Call TripoSR or similar space
                result = self.model_3d_space.predict(
                    tmp_path,
                    True,  # remove_background
                    api_name="/run",  # Adjust based on space API
                )

                # Result is typically (model_path, preview_path)
                if result:
                    model_path = result[0] if isinstance(result, tuple) else result

                    if isinstance(model_path, str):
                        if model_path.startswith("http"):
                            response = requests.get(model_path, timeout=60)
                            return response.content
                        else:
                            with open(model_path, "rb") as f:
                                return f.read()

                logger.info("3D model created successfully")

            finally:
                # Cleanup temp file
                Path(tmp_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"3D conversion failed: {e}")

        return None

    async def _deploy_to_wordpress(
        self,
        specs: ProductSpecs,
        photos: dict[str, bytes],
        model_3d: bytes | None,
    ) -> str | None:
        """Deploy product to WooCommerce.

        Args:
            specs: Product specifications
            photos: Generated photos
            model_3d: 3D model bytes

        Returns:
            Product URL or None
        """
        try:
            # Upload images
            image_urls = []
            for name, image_data in photos.items():
                filename = f"{specs.sku}_{name}.png"
                url = await self.wp_api.upload_media(
                    file=image_data,
                    filename=filename,
                    title=f"{specs.name} - {name}",
                )
                if url:
                    image_urls.append(url)

            if not image_urls:
                logger.warning("No images uploaded")
                return None

            # Upload 3D model
            model_url = None
            if model_3d:
                model_url = await self.wp_api.upload_media(
                    file=model_3d,
                    filename=f"{specs.sku}_model.glb",
                    title=f"{specs.name} - 3D Model",
                )

            # Create product
            description = self._generate_description(specs)
            meta_data = [
                {"key": "_collection", "value": specs.collection},
            ]

            if model_url:
                meta_data.append({"key": "_3d_model_url", "value": model_url})

            product_id = await self.wp_api.create_product(
                name=specs.name,
                sku=specs.sku,
                price=specs.price,
                description=description,
                images=image_urls,
                meta_data=meta_data,
                categories=[{"name": specs.collection}],
            )

            if product_id:
                return f"https://skyyrose.co/product/{specs.slug}"

        except Exception as e:
            logger.error(f"WordPress deployment failed: {e}")

        return None

    def _generate_description(self, specs: ProductSpecs) -> str:
        """Generate luxury product description.

        Args:
            specs: Product specifications

        Returns:
            Formatted product description
        """
        intro = self.COLLECTION_INTROS.get(specs.collection, "From SkyyRose.")

        return f"""
{intro}

{specs.name} embodies SkyyRose's philosophy: Oakland street authenticity meets luxury craftsmanship.

• Premium {specs.fabric}
• {specs.color} colorway
• Gender-neutral design
• Limited availability
• Designed in Oakland, CA
""".strip()

    async def virtual_tryon(
        self,
        garment_image: bytes,
        person_image: bytes,
    ) -> bytes | None:
        """Perform virtual try-on using HF Space.

        Args:
            garment_image: Garment image bytes
            person_image: Person image bytes

        Returns:
            Try-on result image bytes or None
        """
        try:
            import tempfile

            # Save images temporarily
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as garment_tmp:
                garment_tmp.write(garment_image)
                garment_path = garment_tmp.name

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as person_tmp:
                person_tmp.write(person_image)
                person_path = person_tmp.name

            try:
                # Call IDM-VTON space
                result = self.tryon_space.predict(
                    person_path,
                    garment_path,
                    "upper_body",  # category
                    True,  # denoise
                    30,  # steps
                    api_name="/tryon",  # Adjust based on space API
                )

                if result:
                    result_path = result[0] if isinstance(result, tuple) else result

                    if isinstance(result_path, str):
                        if result_path.startswith("http"):
                            response = requests.get(result_path, timeout=60)
                            return response.content
                        else:
                            with open(result_path, "rb") as f:
                                return f.read()

            finally:
                Path(garment_path).unlink(missing_ok=True)
                Path(person_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Virtual try-on failed: {e}")

        return None


# Convenience function for direct usage
async def deploy_product(product_specs: dict) -> PipelineResult:
    """Deploy a product using the orchestrator.

    Args:
        product_specs: Product specification dictionary

    Returns:
        PipelineResult with deployment status
    """
    orchestrator = SkyyRoseSpacesOrchestrator()
    return await orchestrator.full_product_pipeline(product_specs)


# CLI entry point
async def main():
    """Example usage of the orchestrator."""
    orchestrator = SkyyRoseSpacesOrchestrator()

    result = await orchestrator.full_product_pipeline(
        {
            "name": "Essential Black Hoodie",
            "sku": "SRS-SIG-001",
            "slug": "essential-black-hoodie",
            "collection": "SIGNATURE",
            "garment_type": "oversized hoodie",
            "color": "midnight black",
            "fabric": "premium brushed cotton fleece",
            "price": 145.00,
        }
    )

    print("\nPipeline Result:")
    print(f"  Status: {result.status}")
    print(f"  URL: {result.url}")
    print(f"  Photos: {len(result.photos)}")
    print(f"  3D Model: {'Yes' if result.model_3d else 'No'}")

    if result.errors:
        print(f"  Errors: {result.errors}")

    return result


if __name__ == "__main__":
    asyncio.run(main())
