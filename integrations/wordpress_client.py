"""
WordPress/WooCommerce REST API Client for SkyyRose Platform.

Supports both WordPress.com (managed) and self-hosted WordPress installations.
Handles product CRUD, media uploads, order management, and webhooks.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

from security.ssrf_protection import SSRFProtection

# Media source URLs (own-site media, CDNs, approved-render hosts) are not in
# the global singleton's narrow API allowlist — production restricts it to 5
# API hosts, which would reject EVERY real media URL (bug-234). Same pattern
# as services/three_d/replicate_provider.py: no domain allowlist, but keep
# every network-layer SSRF block (private IPs, localhost, metadata services).
_media_ssrf = SSRFProtection(
    allowed_domains=None,
    block_private_ips=True,
    block_localhost=True,
    block_metadata_services=True,
)

logger = logging.getLogger(__name__)


class APIType(StrEnum):
    """WordPress API types."""

    WPCOM = "wpcom"  # WordPress.com managed (uses index.php?rest_route=)
    SELF_HOSTED = "self_hosted"  # Self-hosted (uses /wp-json/)


class SkyyRoseCollection(StrEnum):
    """SkyyRose collection identifiers."""

    SIGNATURE = "signature"
    BLACK_ROSE = "black_rose"
    LOVE_HURTS = "love_hurts"


# Collection metadata mapping
COLLECTION_CONFIG = {
    SkyyRoseCollection.SIGNATURE: {
        "name": "Signature Collection",
        "category_id": 15,
        "tag_ids": [10, 11],
        "color_primary": "#D4AF37",
        "color_secondary": "#1A1A1A",
        "experience_page": "/experience/signature/",
        "catalog_page": "/experience/signature/shop/",
        "tagline": "Timeless Luxury",
        "icon": "◆",
    },
    SkyyRoseCollection.BLACK_ROSE: {
        "name": "Black Rose Collection",
        "category_id": 16,
        "tag_ids": [12, 13],
        "color_primary": "#8B0000",
        "color_secondary": "#0A0A0A",
        "experience_page": "/experience/black-rose/",
        "catalog_page": "/experience/black-rose/shop/",
        "tagline": "Dark Elegance",
        "icon": "🥀",
    },
    SkyyRoseCollection.LOVE_HURTS: {
        "name": "Love Hurts Collection",
        "category_id": 17,
        "tag_ids": [14, 15],
        "color_primary": "#B76E79",
        "color_secondary": "#2D1F21",
        "experience_page": "/experience/love-hurts/",
        "catalog_page": "/experience/love-hurts/shop/",
        "tagline": "Beautiful Pain",
        "icon": "💔",
    },
}

# Brand metadata for all products
BRAND_META = {
    "_skyyrose_brand": "SkyyRose",
    "_skyyrose_tagline": "",
    "_skyyrose_origin": "Oakland, CA",
}


class ProductData(BaseModel):
    """Product data model for WooCommerce sync."""

    name: str
    sku: str
    regular_price: str
    description: str
    short_description: str
    collection: SkyyRoseCollection
    image_urls: list[str] = Field(default_factory=list)
    gallery_urls: list[str] = Field(default_factory=list)
    stock_quantity: int = 100
    manage_stock: bool = True
    status: Literal["draft", "publish", "pending"] = "draft"
    asset_id: str | None = None
    model_3d_url: str | None = None

    class Config:
        use_enum_values = True


class VariationData(BaseModel):
    """Product variation data for variable products."""

    size: str
    color: str | None = None
    regular_price: str
    stock_quantity: int = 50
    sku_suffix: str | None = None


class VariableProductData(ProductData):
    """Variable product with size/color variations."""

    product_type: Literal["variable"] = "variable"
    sizes: list[str] = Field(default_factory=lambda: ["XS", "S", "M", "L", "XL"])
    colors: list[str] = Field(default_factory=list)
    variations: list[VariationData] = Field(default_factory=list)


class MediaUploadResult(BaseModel):
    """Result from media upload operation."""

    id: int
    url: str
    title: str
    alt_text: str
    mime_type: str


class WebhookPayload(BaseModel):
    """Incoming webhook payload from WooCommerce."""

    id: int
    status: str
    date_created: datetime
    date_modified: datetime
    data: dict[str, Any] = Field(default_factory=dict)


@dataclass
class WordPressClient:
    """
    WordPress/WooCommerce REST API client.

    Supports both WordPress.com (managed) and self-hosted installations.

    Usage:
        # WordPress.com
        client = WordPressClient(
            site_url="https://skyyrose.wordpress.com",
            consumer_key="ck_xxx",
            consumer_secret="cs_xxx",
            api_type=APIType.WPCOM
        )

        # Self-hosted
        client = WordPressClient(
            site_url="https://skyyrose.com",
            consumer_key="ck_xxx",
            consumer_secret="cs_xxx",
            api_type=APIType.SELF_HOSTED
        )
    """

    site_url: str
    consumer_key: str
    consumer_secret: str
    api_type: APIType = APIType.SELF_HOSTED
    wp_username: str | None = None
    wp_app_password: str | None = None
    timeout: float = 30.0
    _client: httpx.AsyncClient = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize HTTP client with auth headers."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict[str, str]:
        """Build authorization headers based on API type."""
        # WooCommerce uses consumer key/secret
        auth_string = f"{self.consumer_key}:{self.consumer_secret}"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()

        return {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_wp_headers(self) -> dict[str, str]:
        """Build headers for WordPress REST API (non-WooCommerce)."""
        if self.wp_username and self.wp_app_password:
            auth_string = f"{self.wp_username}:{self.wp_app_password}"
            auth_b64 = base64.b64encode(auth_string.encode()).decode()
            return {"Authorization": f"Basic {auth_b64}"}
        return self._build_headers()

    @property
    def wc_base_url(self) -> str:
        """WooCommerce REST API base URL."""
        if self.api_type == APIType.WPCOM:
            return f"{self.site_url}/index.php?rest_route=/wc/v3"
        return f"{self.site_url}/wp-json/wc/v3"

    @property
    def wp_base_url(self) -> str:
        """WordPress REST API base URL."""
        if self.api_type == APIType.WPCOM:
            return f"{self.site_url}/index.php?rest_route=/wp/v2"
        return f"{self.site_url}/wp-json/wp/v2"

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> WordPressClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    @classmethod
    def from_env(cls) -> WordPressClient:
        """Construct a client from environment credentials.

        Reads the URL under any of three conventions in this codebase
        (WORDPRESS_URL / WP_SITE_URL / WC_BASE_URL) and the key/secret under
        WC_CONSUMER_KEY/WOOCOMMERCE_KEY + WC_CONSUMER_SECRET/WOOCOMMERCE_SECRET.
        WC_BASE_URL is the full REST base (…/wp-json/wc/v3); this client wants
        the site root and appends the REST path itself, so any /wp-json/… suffix
        is stripped. Raises ValueError when creds are missing so callers can fall
        back gracefully instead of constructing a credential-less client.
        """
        raw_url = (
            os.getenv("WORDPRESS_URL") or os.getenv("WP_SITE_URL") or os.getenv("WC_BASE_URL") or ""
        )
        # Normalize a full REST base (…/wp-json/wc/v3) back to the site root.
        site_url = raw_url.split("/wp-json/")[0].rstrip("/")
        consumer_key = os.getenv("WC_CONSUMER_KEY") or os.getenv("WOOCOMMERCE_KEY") or ""
        consumer_secret = os.getenv("WC_CONSUMER_SECRET") or os.getenv("WOOCOMMERCE_SECRET") or ""
        if not (site_url and consumer_key and consumer_secret):
            raise ValueError(
                "WooCommerce credentials not configured (set the site URL via "
                "WORDPRESS_URL / WP_SITE_URL / WC_BASE_URL plus WC_CONSUMER_KEY "
                "and WC_CONSUMER_SECRET)"
            )
        api_type = APIType.WPCOM if "wordpress.com" in site_url else APIType.SELF_HOSTED
        return cls(
            site_url=site_url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            api_type=api_type,
        )

    # ==================== Product Operations ====================

    async def create_product(self, product: ProductData) -> dict[str, Any]:
        """
        Create a new product in WooCommerce.

        Args:
            product: Product data to create

        Returns:
            Created product data from API
        """
        collection_config = COLLECTION_CONFIG[SkyyRoseCollection(product.collection)]

        payload = {
            "name": product.name,
            "type": "simple",
            "regular_price": product.regular_price,
            "description": product.description,
            "short_description": product.short_description,
            "sku": product.sku,
            "manage_stock": product.manage_stock,
            "stock_quantity": product.stock_quantity,
            "status": product.status,
            "categories": [{"id": collection_config["category_id"]}],
            "tags": [{"id": tid} for tid in collection_config["tag_ids"]],
            "images": [{"src": url} for url in product.image_urls],
            "meta_data": [
                {"key": "_skyyrose_collection", "value": product.collection},
                {"key": "_skyyrose_asset_id", "value": product.asset_id or ""},
                {"key": "_skyyrose_3d_model", "value": product.model_3d_url or ""},
                *[{"key": k, "value": v} for k, v in BRAND_META.items()],
            ],
        }

        response = await self._client.post(
            f"{self.wc_base_url}/products",
            json=payload,
        )
        response.raise_for_status()

        logger.info(f"Created product: {product.name} (SKU: {product.sku})")
        return response.json()

    async def update_product(
        self,
        product_id: int,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an existing product."""
        response = await self._client.put(
            f"{self.wc_base_url}/products/{product_id}",
            json=updates,
        )
        response.raise_for_status()
        return response.json()

    async def get_product(self, product_id: int) -> dict[str, Any]:
        """Get a single product by ID."""
        response = await self._client.get(
            f"{self.wc_base_url}/products/{product_id}",
        )
        response.raise_for_status()
        return response.json()

    async def list_products(
        self,
        collection: SkyyRoseCollection | None = None,
        page: int = 1,
        per_page: int = 20,
        status: str = "any",
    ) -> list[dict[str, Any]]:
        """List products with optional filtering."""
        params: dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "status": status,
        }

        if collection:
            config = COLLECTION_CONFIG[collection]
            params["category"] = config["category_id"]

        response = await self._client.get(
            f"{self.wc_base_url}/products",
            params=params,
        )
        response.raise_for_status()
        return response.json()

    async def delete_product(self, product_id: int, force: bool = False) -> dict[str, Any]:
        """Delete a product (moves to trash unless force=True)."""
        response = await self._client.delete(
            f"{self.wc_base_url}/products/{product_id}",
            params={"force": force},
        )
        response.raise_for_status()
        return response.json()

    # ==================== Variable Products ====================

    async def create_variable_product(
        self,
        product: VariableProductData,
    ) -> dict[str, Any]:
        """Create a variable product with variations."""
        collection_config = COLLECTION_CONFIG[SkyyRoseCollection(product.collection)]

        # Build attributes
        attributes = [
            {
                "name": "Size",
                "visible": True,
                "variation": True,
                "options": product.sizes,
            },
        ]
        if product.colors:
            attributes.append(
                {
                    "name": "Color",
                    "visible": True,
                    "variation": True,
                    "options": product.colors,
                }
            )

        payload = {
            "name": product.name,
            "type": "variable",
            "description": product.description,
            "short_description": product.short_description,
            "sku": product.sku,
            "status": product.status,
            "categories": [{"id": collection_config["category_id"]}],
            "tags": [{"id": tid} for tid in collection_config["tag_ids"]],
            "images": [{"src": url} for url in product.image_urls],
            "attributes": attributes,
            "meta_data": [
                {"key": "_skyyrose_collection", "value": product.collection},
                {"key": "_skyyrose_3d_model", "value": product.model_3d_url or ""},
                *[{"key": k, "value": v} for k, v in BRAND_META.items()],
            ],
        }

        # Create parent product
        response = await self._client.post(
            f"{self.wc_base_url}/products",
            json=payload,
        )
        response.raise_for_status()
        parent = response.json()
        parent_id = parent["id"]

        # Create variations
        for variation in product.variations:
            var_attrs = [{"name": "Size", "option": variation.size}]
            if variation.color:
                var_attrs.append({"name": "Color", "option": variation.color})

            sku_suffix = variation.sku_suffix or f"{variation.size}"
            if variation.color:
                sku_suffix += f"-{variation.color}"

            var_payload = {
                "regular_price": variation.regular_price,
                "sku": f"{product.sku}-{sku_suffix}",
                "stock_quantity": variation.stock_quantity,
                "manage_stock": True,
                "attributes": var_attrs,
            }

            await self._client.post(
                f"{self.wc_base_url}/products/{parent_id}/variations",
                json=var_payload,
            )

        logger.info(
            f"Created variable product: {product.name} with {len(product.variations)} variations"
        )
        return parent

    # ==================== Media Operations ====================

    async def upload_media(
        self,
        image_data: bytes,
        filename: str,
        title: str,
        alt_text: str,
        caption: str | None = None,
    ) -> MediaUploadResult:
        """
        Upload media to WordPress media library.

        Args:
            image_data: Raw image bytes
            filename: Filename for the upload
            title: Media title
            alt_text: Alt text for accessibility
            caption: Optional caption

        Returns:
            MediaUploadResult with ID and URL
        """
        # Determine content type from filename
        ext = filename.split(".")[-1].lower()
        content_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
            "glb": "model/gltf-binary",
            "gltf": "model/gltf+json",
        }
        content_type = content_types.get(ext, "application/octet-stream")

        headers = {
            **self._build_wp_headers(),
            "Content-Type": content_type,
            "Content-Disposition": f'attachment; filename="{filename}"',
        }

        response = await self._client.post(
            f"{self.wp_base_url}/media",
            content=image_data,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

        # Update metadata
        await self._client.post(
            f"{self.wp_base_url}/media/{data['id']}",
            json={
                "title": title,
                "alt_text": alt_text,
                "caption": caption or "",
            },
            headers=self._build_wp_headers(),
        )

        return MediaUploadResult(
            id=data["id"],
            url=data["source_url"],
            title=title,
            alt_text=alt_text,
            mime_type=content_type,
        )

    async def upload_media_from_url(
        self,
        image_url: str,
        title: str,
        alt_text: str,
        caption: str | None = None,
    ) -> MediaUploadResult:
        """Upload media from a URL."""
        # Download image — validate against SSRF before fetching
        _media_ssrf.validate_url(image_url)
        async with httpx.AsyncClient() as download_client:
            response = await download_client.get(image_url)
            response.raise_for_status()
            image_data = response.content

        # Extract filename from URL
        filename = image_url.split("/")[-1].split("?")[0]
        if "." not in filename:
            filename = f"{title.replace(' ', '-').lower()}.jpg"

        return await self.upload_media(
            image_data=image_data,
            filename=filename,
            title=title,
            alt_text=alt_text,
            caption=caption,
        )

    # ==================== Page Operations ====================

    async def create_page(
        self,
        title: str,
        slug: str,
        content: str,
        parent_id: int | None = None,
        template: str | None = None,
        status: Literal["draft", "publish", "pending"] = "draft",
    ) -> dict[str, Any]:
        """Create a WordPress page."""
        payload: dict[str, Any] = {
            "title": title,
            "slug": slug,
            "content": content,
            "status": status,
        }

        if parent_id:
            payload["parent"] = parent_id

        if template:
            payload["template"] = template

        response = await self._client.post(
            f"{self.wp_base_url}/pages",
            json=payload,
            headers=self._build_wp_headers(),
        )
        response.raise_for_status()
        return response.json()

    async def get_page_by_slug(self, slug: str) -> dict[str, Any] | None:
        """Get a page by its slug."""
        response = await self._client.get(
            f"{self.wp_base_url}/pages",
            params={"slug": slug},
            headers=self._build_wp_headers(),
        )
        response.raise_for_status()
        pages = response.json()
        return pages[0] if pages else None

    async def update_page(
        self,
        page_id: int,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an existing page."""
        response = await self._client.post(
            f"{self.wp_base_url}/pages/{page_id}",
            json=updates,
            headers=self._build_wp_headers(),
        )
        response.raise_for_status()
        return response.json()

    # ==================== Order Operations ====================

    async def get_order(self, order_id: int) -> dict[str, Any]:
        """Get order details."""
        response = await self._client.get(
            f"{self.wc_base_url}/orders/{order_id}",
        )
        response.raise_for_status()
        return response.json()

    async def list_orders(
        self,
        status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> list[dict[str, Any]]:
        """List orders with optional filtering."""
        params: dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        if status:
            params["status"] = status

        response = await self._client.get(
            f"{self.wc_base_url}/orders",
            params=params,
        )
        response.raise_for_status()
        return response.json()

    async def update_order_status(
        self,
        order_id: int,
        status: str,
    ) -> dict[str, Any]:
        """Update order status."""
        response = await self._client.put(
            f"{self.wc_base_url}/orders/{order_id}",
            json={"status": status},
        )
        response.raise_for_status()
        return response.json()

    # ==================== Webhook Verification ====================

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        webhook_secret: str,
    ) -> bool:
        """
        Verify WooCommerce webhook signature.

        Args:
            payload: Raw request body
            signature: X-WC-Webhook-Signature header value
            webhook_secret: Webhook secret from WooCommerce settings

        Returns:
            True if signature is valid
        """
        expected = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).digest()
        expected_b64 = base64.b64encode(expected).decode()

        return hmac.compare_digest(signature, expected_b64)

    # ==================== Health Check ====================

    async def health_check(self) -> dict[str, Any]:
        """Check API connectivity and authentication."""
        try:
            # Test WooCommerce API
            response = await self._client.get(
                f"{self.wc_base_url}/system_status",
            )
            wc_status = response.status_code == 200

            # Test WordPress API
            wp_response = await self._client.get(
                f"{self.wp_base_url}/users/me",
                headers=self._build_wp_headers(),
            )
            wp_status = wp_response.status_code == 200

            return {
                "healthy": wc_status and wp_status,
                "woocommerce_api": wc_status,
                "wordpress_api": wp_status,
                "site_url": self.site_url,
                "api_type": self.api_type.value,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "site_url": self.site_url,
            }


# Backwards-compatible alias — consumers (agents/commerce_agent.py,
# api/dashboard.py) import the client under this name.
WordPressWooCommerceClient = WordPressClient
