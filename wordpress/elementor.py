"""
Elementor Template Builder
==========================

Generate Elementor-compatible templates programmatically.

Features:
- BrandKit: Design tokens (colors, typography, spacing)
- PageSpec: Page type definitions
- Template generation for various page types
- JSON export in Elementor Kit format

Compatible with:
- Elementor Pro 3.32+
- Shoptimizer 2.9.0 theme

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class WidgetType(StrEnum):
    """Elementor widget types."""

    HEADING = "heading"
    TEXT_EDITOR = "text-editor"
    IMAGE = "image"
    IMAGE_BOX = "image-box"
    BUTTON = "button"
    ICON = "icon"
    ICON_BOX = "icon-box"
    SPACER = "spacer"
    DIVIDER = "divider"
    VIDEO = "video"

    # WooCommerce
    PRODUCTS = "woocommerce-products"
    PRODUCT_IMAGES = "woocommerce-product-images"
    PRODUCT_TITLE = "woocommerce-product-title"
    PRODUCT_PRICE = "woocommerce-product-price"
    ADD_TO_CART = "woocommerce-product-add-to-cart"

    # Pro
    LOOP_GRID = "loop-grid"
    POSTS = "posts"
    GALLERY = "gallery"
    FORM = "form"
    SLIDES = "slides"
    NAV_MENU = "nav-menu"

    # SkyyRose 3D Widgets (Custom)
    THREEJS_VIEWER = "skyyrose-3d-viewer"  # Single product 3D viewer
    THREEJS_COLLECTION = "skyyrose-collection"  # Full collection experience
    AR_QUICK_LOOK = "skyyrose-ar-button"  # iOS AR Quick Look button
    PRODUCT_CONFIGURATOR = "skyyrose-configurator"  # Color/size selector
    MODEL_VIEWER = "skyyrose-model-viewer"  # Google Model Viewer widget

    # SkyyRose Animation Widgets (Custom)
    LOTTIE_ANIMATION = "skyyrose-lottie"  # Lottie animations (spinning logo, etc.)
    THREEJS_BACKGROUND = "skyyrose-3d-background"  # 3D ambient background particles

    # SkyyRose Collection Widgets (Custom)
    COLLECTION_CARD = "skyyrose-collection-card"  # Featured collection card
    PRODUCT_HOTSPOT_VIEWER = "skyyrose-hotspot-viewer"  # Interactive hotspot viewer

    # SkyyRose Pre-Order Widgets (Custom)
    COUNTDOWN_TIMER = "skyyrose-countdown"  # Server-synced countdown timer
    PREORDER_FORM = "skyyrose-preorder-form"  # Pre-order notification form
    JETPOPUP_TRIGGER = "skyyrose-jetpopup-trigger"  # JetPopup integration

    # SkyyRose Timeline & Press (Custom)
    TIMELINE = "skyyrose-timeline"  # Timeline widget for milestones
    PRESS_MENTION = "skyyrose-press-mention"  # Press mention/article card
    LOOP_CONTROLS = "loop-controls"  # Post loop controls/filters
    TABS = "tabs"  # Tab widget for content organization


class SectionLayout(StrEnum):
    """Section layout types."""

    BOXED = "boxed"
    FULL_WIDTH = "full_width"
    FULL_SCREEN = "full_screen"


class PageType(StrEnum):
    """Page types for template generation."""

    HOME = "home"
    COLLECTION = "collection"
    PRODUCT = "product"
    ABOUT = "about"
    CONTACT = "contact"
    LOOKBOOK = "lookbook"


# =============================================================================
# BrandKit
# =============================================================================


@dataclass
class BrandColors:
    """Brand color palette with luxury enhancements."""

    # Primary brand color
    primary: str = "#D4AF37"  # Rose gold
    # Secondary brand color
    secondary: str = "#0D0D0D"  # Obsidian black
    # Accent/highlight color
    accent: str = "#F5F5F0"  # Ivory
    # Text colors
    text: str = "#1A1A1A"
    text_light: str = "#666666"
    # Background colors
    background: str = "#FFFFFF"
    background_alt: str = "#F9F9F9"
    # Luxury additions
    dark: str = "#0D0D0D"  # Dark color for text/backgrounds
    light: str = "#F5F5F0"  # Light color for backgrounds
    glow: str = "rgba(183, 110, 121, 0.3)"  # Glow effect color (for hovers)


@dataclass
class BrandTypography:
    """Brand typography settings."""

    heading_font: str = "Playfair Display"
    body_font: str = "Inter"
    heading_weight: int = 700
    body_weight: int = 400
    base_size: int = 16
    line_height: float = 1.6
    letter_spacing: str = "0.02em"


@dataclass
class BrandSpacing:
    """Brand spacing system."""

    unit: int = 8  # Base unit in pixels
    xs: int = 8
    sm: int = 16
    md: int = 24
    lg: int = 48
    xl: int = 80
    xxl: int = 120


@dataclass
class BrandImagery:
    """Brand imagery guidelines."""

    aspect_ratio_product: str = "3:4"
    aspect_ratio_hero: str = "16:9"
    aspect_ratio_square: str = "1:1"
    default_placeholder: str = ""
    logo_url: str = ""
    favicon_url: str = ""


@dataclass
class BrandVoice:
    """Brand voice and copy guidelines."""

    tagline: str = ""
    tone: str = "sophisticated, elevated, authentic"
    cta_primary: str = "Shop Now"
    cta_secondary: str = "Discover More"


@dataclass
class BrandKit:
    """
    Complete brand design system.

    Contains all design tokens needed for consistent template generation.
    """

    name: str = "SkyyRose"
    colors: BrandColors = field(default_factory=BrandColors)
    typography: BrandTypography = field(default_factory=BrandTypography)
    spacing: BrandSpacing = field(default_factory=BrandSpacing)
    imagery: BrandImagery = field(default_factory=BrandImagery)
    voice: BrandVoice = field(default_factory=BrandVoice)

    def to_css_vars(self) -> dict[str, str]:
        """Export as CSS custom properties."""
        return {
            "--color-primary": self.colors.primary,
            "--color-secondary": self.colors.secondary,
            "--color-accent": self.colors.accent,
            "--color-text": self.colors.text,
            "--color-text-light": self.colors.text_light,
            "--color-bg": self.colors.background,
            "--color-bg-alt": self.colors.background_alt,
            "--font-heading": self.typography.heading_font,
            "--font-body": self.typography.body_font,
            "--spacing-unit": f"{self.spacing.unit}px",
        }

    def to_elementor_globals(self) -> dict[str, Any]:
        """Export as Elementor global settings."""
        return {
            "colors": [
                {"_id": "primary", "title": "Primary", "color": self.colors.primary},
                {"_id": "secondary", "title": "Secondary", "color": self.colors.secondary},
                {"_id": "accent", "title": "Accent", "color": self.colors.accent},
                {"_id": "text", "title": "Text", "color": self.colors.text},
            ],
            "typography": [
                {
                    "_id": "heading",
                    "title": "Heading",
                    "typography_font_family": self.typography.heading_font,
                    "typography_font_weight": str(self.typography.heading_weight),
                },
                {
                    "_id": "body",
                    "title": "Body",
                    "typography_font_family": self.typography.body_font,
                    "typography_font_weight": str(self.typography.body_weight),
                },
            ],
        }


# Default SkyyRose brand kit
SKYYROSE_BRAND_KIT = BrandKit()

# Collection-specific brand kits with luxury color palettes
COLLECTION_BRAND_KITS = {
    "signature": BrandKit(
        name="Signature Collection",
        colors=BrandColors(
            primary="#C9A962",  # Rose gold
            secondary="#B76E79",  # Pink cloud
            accent="#FFD700",  # Gold
            text="#1A1A1A",
            text_light="#666666",
            background="#FFFFFF",
            background_alt="#F9F9F9",
            dark="#0D0D0D",
            light="#F5F5F0",
            glow="rgba(201, 169, 98, 0.3)",
        ),
    ),
    "love-hurts": BrandKit(
        name="Love Hurts Collection",
        colors=BrandColors(
            primary="#B76E79",  # Deep rose
            secondary="#DC143C",  # Crimson
            accent="#1a1a2e",  # Midnight
            text="#1A1A1A",
            text_light="#666666",
            background="#FFFFFF",
            background_alt="#F9F9F9",
            dark="#0D0D0D",
            light="#F5F5F0",
            glow="rgba(220, 20, 60, 0.3)",
        ),
    ),
    "black-rose": BrandKit(
        name="Black Rose Collection",
        colors=BrandColors(
            primary="#C0C0C0",  # Cosmic silver
            secondary="#0A0A0A",  # Obsidian
            accent="#c8c8dc",  # Moonlight
            text="#1A1A1A",
            text_light="#666666",
            background="#FFFFFF",
            background_alt="#F9F9F9",
            dark="#0D0D0D",
            light="#F5F5F0",
            glow="rgba(192, 192, 192, 0.3)",
        ),
    ),
}


# =============================================================================
# PageSpec
# =============================================================================


@dataclass
class PageSpec:
    """
    Page specification for template generation.

    Defines the structure and content requirements for a page type.
    """

    page_type: PageType
    title: str
    slug: str
    description: str = ""

    # Layout
    sections: list[str] = field(default_factory=list)
    layout: SectionLayout = SectionLayout.FULL_WIDTH

    # Content
    hero_enabled: bool = True
    hero_title: str = ""
    hero_subtitle: str = ""
    hero_cta: str = ""
    hero_image: str = ""

    # SEO
    meta_title: str = ""
    meta_description: str = ""

    # Template settings
    template: str = "elementor_canvas"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "page_type": self.page_type.value,
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "sections": self.sections,
            "layout": self.layout.value,
            "hero": {
                "enabled": self.hero_enabled,
                "title": self.hero_title,
                "subtitle": self.hero_subtitle,
                "cta": self.hero_cta,
                "image": self.hero_image,
            },
            "seo": {
                "meta_title": self.meta_title,
                "meta_description": self.meta_description,
            },
        }


# =============================================================================
# Elementor Template
# =============================================================================


class ElementorTemplate(BaseModel):
    """Elementor template data structure."""

    version: str = "0.4"
    title: str = ""
    type: str = "page"
    content: list[dict[str, Any]] = Field(default_factory=list)
    page_settings: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_section(
        self,
        widgets: list[dict[str, Any]],
        layout: SectionLayout = SectionLayout.BOXED,
        settings: dict[str, Any] | None = None,
    ) -> str:
        """Add a section with widgets."""
        section_id = f"s{uuid.uuid4().hex[:7]}"

        section = {
            "id": section_id,
            "elType": "section",
            "settings": {
                "layout": layout.value,
                "content_width": (
                    {"size": 1200, "unit": "px"} if layout == SectionLayout.BOXED else {}
                ),
                **(settings or {}),
            },
            "elements": [
                {
                    "id": f"c{uuid.uuid4().hex[:7]}",
                    "elType": "column",
                    "settings": {"_column_size": 100},
                    "elements": widgets,
                }
            ],
        }

        self.content.append(section)
        return section_id

    def to_json(self) -> str:
        """Export as JSON string."""
        return json.dumps(self.model_dump(), indent=2)

    def to_file(self, filepath: str) -> None:
        """Export to file."""
        with open(filepath, "w") as f:
            f.write(self.to_json())


# =============================================================================
# ElementorConfig
# =============================================================================


@dataclass
class ElementorConfig:
    """Elementor generation configuration."""

    brand_kit: BrandKit = field(default_factory=lambda: SKYYROSE_BRAND_KIT)
    elementor_version: str = "3.32.0"
    shoptimizer_version: str = "2.9.0"
    output_dir: str = "./templates/elementor"


# =============================================================================
# Elementor Builder
# =============================================================================


class ElementorBuilder:
    """
    Elementor template generator.

    Usage:
        builder = ElementorBuilder()

        # Generate home page
        template = builder.generate_home_page(
            hero_title="SkyyRose",
            hero_subtitle="",
            collections=["BLACK_ROSE", "LOVE_HURTS", "SIGNATURE"],
        )

        # Generate PDP template
        template = builder.generate_product_page()

        # Export
        template.to_file("home.json")
    """

    def __init__(self, config: ElementorConfig | None = None) -> None:
        self.config = config or ElementorConfig()
        self.brand = self.config.brand_kit

    # -------------------------------------------------------------------------
    # Widget Builders
    # -------------------------------------------------------------------------

    def _widget(
        self,
        widget_type: WidgetType,
        settings: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a widget element."""
        return {
            "id": f"w{uuid.uuid4().hex[:7]}",
            "elType": "widget",
            "widgetType": widget_type.value,
            "settings": settings,
        }

    def heading(
        self,
        text: str,
        size: str = "xl",
        tag: str = "h2",
        align: str = "center",
    ) -> dict[str, Any]:
        """Create heading widget."""
        size_map = {"sm": "small", "md": "medium", "lg": "large", "xl": "xl", "xxl": "xxl"}
        return self._widget(
            WidgetType.HEADING,
            {
                "title": text,
                "size": size_map.get(size, "large"),
                "header_size": tag,
                "align": align,
                "title_color": self.brand.colors.text,
                "typography_font_family": self.brand.typography.heading_font,
                "typography_font_weight": str(self.brand.typography.heading_weight),
            },
        )

    def text(self, content: str, align: str = "center") -> dict[str, Any]:
        """Create text editor widget."""
        return self._widget(
            WidgetType.TEXT_EDITOR,
            {
                "editor": content,
                "align": align,
                "text_color": self.brand.colors.text_light,
                "typography_font_family": self.brand.typography.body_font,
            },
        )

    def button(
        self,
        text: str,
        link: str = "#",
        style: str = "primary",
        size: str = "md",
    ) -> dict[str, Any]:
        """Create button widget."""
        bg_color = self.brand.colors.primary if style == "primary" else "transparent"
        text_color = "#FFFFFF" if style == "primary" else self.brand.colors.primary

        return self._widget(
            WidgetType.BUTTON,
            {
                "text": text,
                "link": {"url": link, "is_external": False},
                "size": size,
                "button_background_color": bg_color,
                "button_text_color": text_color,
                "button_border_border": "solid" if style != "primary" else "",
                "button_border_width": (
                    {"top": "1", "right": "1", "bottom": "1", "left": "1"}
                    if style != "primary"
                    else {}
                ),
                "button_border_color": self.brand.colors.primary if style != "primary" else "",
                "typography_font_family": self.brand.typography.body_font,
                "typography_font_weight": "600",
                "typography_letter_spacing": {"size": 1, "unit": "px"},
            },
        )

    def image(
        self,
        url: str,
        alt: str = "",
        size: str = "full",
        align: str = "center",
    ) -> dict[str, Any]:
        """Create image widget."""
        return self._widget(
            WidgetType.IMAGE,
            {
                "image": {"url": url, "alt": alt},
                "image_size": size,
                "align": align,
            },
        )

    def spacer(self, size: int = 48) -> dict[str, Any]:
        """Create spacer widget."""
        return self._widget(
            WidgetType.SPACER,
            {"space": {"size": size, "unit": "px"}},
        )

    def products_grid(
        self,
        columns: int = 4,
        rows: int = 2,
        category: str = "",
    ) -> dict[str, Any]:
        """Create WooCommerce products grid."""
        return self._widget(
            WidgetType.PRODUCTS,
            {
                "columns": str(columns),
                "rows": str(rows),
                "query_post_type": "product",
                "query_product_cat_ids": [category] if category else [],
                "paginate": "yes",
            },
        )

    # -------------------------------------------------------------------------
    # 3D Widget Builders (SkyyRose Custom)
    # -------------------------------------------------------------------------

    def threejs_viewer(
        self,
        product_id: int | str,
        glb_url: str,
        usdz_url: str = "",
        width: str = "100%",
        height: str = "500px",
        auto_rotate: bool = True,
        enable_zoom: bool = True,
        show_ar_button: bool = True,
        background_color: str = "#000000",
    ) -> dict[str, Any]:
        """
        Create 3D product viewer widget.

        Uses Three.js/model-viewer for WebGL rendering and USDZ for iOS AR.

        Args:
            product_id: WooCommerce product ID
            glb_url: URL to GLB model file
            usdz_url: URL to USDZ model for iOS AR
            width: Widget width
            height: Widget height
            auto_rotate: Enable auto-rotation
            enable_zoom: Enable zoom controls
            show_ar_button: Show AR Quick Look button on iOS
            background_color: Viewer background color

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.THREEJS_VIEWER,
            {
                "product_id": str(product_id),
                "glb_url": glb_url,
                "usdz_url": usdz_url,
                "viewer_width": width,
                "viewer_height": height,
                "auto_rotate": "yes" if auto_rotate else "no",
                "enable_zoom": "yes" if enable_zoom else "no",
                "show_ar_button": "yes" if show_ar_button else "no",
                "background_color": background_color,
                # Three.js specific
                "camera_controls": "yes",
                "shadow_intensity": "1",
                "environment_image": "neutral",
                # Loading
                "poster_url": "",
                "loading_animation": "dots",
            },
        )

    def collection_experience(
        self,
        collection_slug: str,
        experience_type: str = "showroom",
        enable_navigation: bool = True,
        enable_cart: bool = True,
        spotlight_color: str = "#B76E79",
        ambient_sound: str = "",
    ) -> dict[str, Any]:
        """
        Create immersive 3D collection experience widget.

        Full Three.js experience with multiple products, navigation, and cart.

        Args:
            collection_slug: WordPress collection/category slug
            experience_type: Type of experience (showroom, runway, gallery, etc.)
            enable_navigation: Allow 3D space navigation
            enable_cart: Enable add-to-cart from 3D experience
            spotlight_color: Product spotlight color (SkyyRose brand)
            ambient_sound: Optional ambient audio URL

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.THREEJS_COLLECTION,
            {
                "collection_slug": collection_slug,
                "experience_type": experience_type,
                "enable_navigation": "yes" if enable_navigation else "no",
                "enable_cart": "yes" if enable_cart else "no",
                "spotlight_color": spotlight_color,
                "ambient_sound": ambient_sound,
                # Layout
                "aspect_ratio": "16:9",
                "fullscreen_button": "yes",
                "loading_screen": "branded",
                # Performance
                "lod_enabled": "yes",
                "shadow_quality": "medium",
                "antialiasing": "yes",
            },
        )

    def ar_quick_look_button(
        self,
        product_id: int | str,
        usdz_url: str,
        button_text: str = "View in AR",
        button_style: str = "primary",
        show_on_ios_only: bool = True,
    ) -> dict[str, Any]:
        """
        Create AR Quick Look button for iOS Safari.

        Uses rel="ar" link with USDZ format.

        Args:
            product_id: WooCommerce product ID
            usdz_url: URL to USDZ model
            button_text: Button label
            button_style: primary or secondary
            show_on_ios_only: Only display on iOS devices

        Returns:
            Widget configuration dict
        """
        bg_color = self.brand.colors.primary if button_style == "primary" else "transparent"
        text_color = "#FFFFFF" if button_style == "primary" else self.brand.colors.primary

        return self._widget(
            WidgetType.AR_QUICK_LOOK,
            {
                "product_id": str(product_id),
                "usdz_url": usdz_url,
                "button_text": button_text,
                "show_on_ios_only": "yes" if show_on_ios_only else "no",
                # Styling
                "button_background_color": bg_color,
                "button_text_color": text_color,
                "button_border_radius": {"size": 4, "unit": "px"},
                "button_padding": {"top": "12", "right": "24", "bottom": "12", "left": "24"},
                # AR options
                "ar_scale": "fixed",  # #allowsContentScaling=0
                "ar_placement": "floor",
            },
        )

    def product_configurator(
        self,
        product_id: int | str,
        glb_url: str,
        available_colors: list[str] | None = None,
        available_sizes: list[str] | None = None,
        show_price: bool = True,
        show_stock: bool = True,
    ) -> dict[str, Any]:
        """
        Create product configurator widget.

        Real-time 3D model with color/size selection and price updates.

        Args:
            product_id: WooCommerce product ID
            glb_url: URL to GLB model
            available_colors: List of hex colors for material swapping
            available_sizes: List of size options
            show_price: Display price (updates with variation)
            show_stock: Display stock status

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.PRODUCT_CONFIGURATOR,
            {
                "product_id": str(product_id),
                "glb_url": glb_url,
                "colors": available_colors or ["#000000", "#FFFFFF", "#B76E79"],
                "sizes": available_sizes or ["XS", "S", "M", "L", "XL"],
                "show_price": "yes" if show_price else "no",
                "show_stock": "yes" if show_stock else "no",
                # UI
                "color_selector_style": "swatches",
                "size_selector_style": "buttons",
                "add_to_cart_button": "yes",
                # 3D
                "auto_rotate": "yes",
                "enable_zoom": "yes",
                "viewer_height": "400px",
            },
        )

    def model_viewer(
        self,
        src: str,
        ios_src: str = "",
        alt: str = "3D Model",
        ar: bool = True,
        auto_rotate: bool = True,
        camera_controls: bool = True,
        poster: str = "",
        reveal: str = "auto",
    ) -> dict[str, Any]:
        """
        Create Google Model Viewer widget.

        Uses <model-viewer> web component for cross-platform 3D.

        Args:
            src: GLB/GLTF model URL
            ios_src: USDZ model URL for iOS
            alt: Accessibility text
            ar: Enable AR on supported devices
            auto_rotate: Enable auto-rotation
            camera_controls: Enable orbit controls
            poster: Preview image URL
            reveal: Loading behavior (auto, manual, interaction)

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.MODEL_VIEWER,
            {
                "src": src,
                "ios_src": ios_src,
                "alt": alt,
                "ar": "yes" if ar else "no",
                "ar_modes": "webxr scene-viewer quick-look",
                "auto_rotate": "yes" if auto_rotate else "no",
                "camera_controls": "yes" if camera_controls else "no",
                "poster": poster,
                "reveal": reveal,
                "shadow_intensity": "1",
                "exposure": "1",
                "environment_image": "neutral",
            },
        )

    # -------------------------------------------------------------------------
    # Animation Widgets (Lottie, 3D Backgrounds)
    # -------------------------------------------------------------------------

    def lottie_animation(
        self,
        json_url: str,
        loop: bool = True,
        speed: float = 1.0,
        reverse: bool = False,
        width: str = "auto",
        height: str = "auto",
        align: str = "center",
    ) -> dict[str, Any]:
        """
        Create Lottie animation widget.

        Args:
            json_url: URL to Lottie JSON animation file
            loop: Enable looping
            speed: Animation speed multiplier
            reverse: Play animation in reverse
            width: Widget width
            height: Widget height
            align: Alignment (left, center, right)

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.LOTTIE_ANIMATION,
            {
                "lottie_url": json_url,
                "loop": "yes" if loop else "no",
                "speed": str(speed),
                "reverse": "yes" if reverse else "no",
                "autoplay": "yes",
                "trigger": "none",
                "width": {"size": width, "unit": "px"} if width != "auto" else {},
                "height": {"size": height, "unit": "px"} if height != "auto" else {},
                "align": align,
            },
        )

    def threejs_background(
        self,
        scene_type: str = "ambient_particles",
        collection_slug: str = "signature",
        particle_count: int = 100,
        height: str = "400px",
    ) -> dict[str, Any]:
        """
        Create Three.js background scene widget.

        Args:
            scene_type: Type of scene (ambient_particles, etc.)
            collection_slug: Collection for color theme
            particle_count: Number of particles
            height: Section height

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.THREEJS_BACKGROUND,
            {
                "scene_type": scene_type,
                "collection_slug": collection_slug,
                "particle_count": str(particle_count),
                "particle_speed": "0.5",
                "background_color": self.brand.colors.background,
                "height": {"size": height, "unit": "px"},
                "enable_interaction": "yes",
            },
        )

    # -------------------------------------------------------------------------
    # Collection & Product Widgets
    # -------------------------------------------------------------------------

    def collection_card(
        self,
        collection_slug: str,
        title: str,
        subtitle: str = "",
        description: str = "",
        color: str = "",
        image_url: str = "",
        link: str = "#",
    ) -> dict[str, Any]:
        """
        Create collection card widget.

        Args:
            collection_slug: Collection identifier
            title: Card title
            subtitle: Card subtitle
            description: Card description
            color: Brand color
            image_url: Hero image URL
            link: Card link

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.COLLECTION_CARD,
            {
                "collection_slug": collection_slug,
                "title": title,
                "subtitle": subtitle,
                "description": description,
                "color": color or self.brand.colors.primary,
                "image_url": image_url,
                "link": link,
                "hover_effect": "lift",
            },
        )

    def product_hotspot_viewer(
        self,
        collection_slug: str,
        hotspot_config_url: str,
        enable_cart: bool = True,
        enable_wishlist: bool = True,
    ) -> dict[str, Any]:
        """
        Create interactive product hotspot viewer.

        Args:
            collection_slug: Collection identifier
            hotspot_config_url: URL to hotspot config JSON
            enable_cart: Enable add-to-cart functionality
            enable_wishlist: Enable wishlist button

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.PRODUCT_HOTSPOT_VIEWER,
            {
                "collection_slug": collection_slug,
                "hotspot_config_url": hotspot_config_url,
                "auto_load_products": "yes",
                "enable_cart": "yes" if enable_cart else "no",
                "enable_wishlist": "yes" if enable_wishlist else "no",
                "card_style": "floating",
            },
        )

    # -------------------------------------------------------------------------
    # Pre-Order & Countdown Widgets
    # -------------------------------------------------------------------------

    def countdown_timer(
        self,
        product_id: int | str,
        target_date: str,
        display_format: str = "compact",
        on_complete: str = "hide",
    ) -> dict[str, Any]:
        """
        Create server-synced countdown timer widget.

        Args:
            product_id: WooCommerce product ID
            target_date: ISO 8601 target date
            display_format: compact | detailed
            on_complete: hide | show-message

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.COUNTDOWN_TIMER,
            {
                "product_id": str(product_id),
                "target_date": target_date,
                "display_format": display_format,
                "on_complete": on_complete,
                "complete_message": "Now Blooming - Available to Purchase",
                "timezone": "auto",
                "sync_with_server": "yes",
            },
        )

    def preorder_form(
        self,
        product_id: int | str,
        klaviyo_list_id: str = "",
    ) -> dict[str, Any]:
        """
        Create pre-order notification form.

        Args:
            product_id: WooCommerce product ID
            klaviyo_list_id: Klaviyo list ID for email capture

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.PREORDER_FORM,
            {
                "form_name": "preorder_notify",
                "product_id": str(product_id),
                "form_fields": [
                    {
                        "field_type": "email",
                        "field_label": "Email",
                        "placeholder": "Get notified at launch",
                        "required": "yes",
                    }
                ],
                "submit_button_text": "Notify Me",
                "integration": "klaviyo",
                "klaviyo_list": klaviyo_list_id,
            },
        )

    # -------------------------------------------------------------------------
    # Timeline & Press Widgets
    # -------------------------------------------------------------------------

    def timeline_item(
        self,
        date: str,
        title: str,
        description: str = "",
        link: str = "",
        image_url: str = "",
    ) -> dict[str, Any]:
        """
        Create timeline item widget.

        Args:
            date: Date label
            title: Item title
            description: Item description
            link: Link URL
            image_url: Optional image URL

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.TIMELINE,
            {
                "date": date,
                "title": title,
                "description": description,
                "link": link,
                "image": image_url,
            },
        )

    def press_mention(
        self,
        publication: str,
        title: str,
        link: str = "",
        logo_url: str = "",
    ) -> dict[str, Any]:
        """
        Create press mention/article card.

        Args:
            publication: Publication name
            title: Article title
            link: Article URL
            logo_url: Publication logo URL

        Returns:
            Widget configuration dict
        """
        return self._widget(
            WidgetType.PRESS_MENTION,
            {
                "publication": publication,
                "title": title,
                "link": link,
                "logo_url": logo_url,
            },
        )

    # -------------------------------------------------------------------------
    # 3D Section Builders
    # -------------------------------------------------------------------------

    def product_3d_section(
        self,
        product_id: int | str,
        glb_url: str,
        usdz_url: str = "",
        title: str = "",
        enable_configurator: bool = False,
        available_colors: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Build complete 3D product section with viewer and optional configurator.

        Args:
            product_id: WooCommerce product ID
            glb_url: GLB model URL
            usdz_url: USDZ model URL for AR
            title: Optional section title
            enable_configurator: Include color/size configurator
            available_colors: Colors for configurator

        Returns:
            List of widget dicts for section
        """
        widgets = []

        if title:
            widgets.append(self.heading(title, size="lg", tag="h2"))
            widgets.append(self.spacer(24))

        if enable_configurator:
            widgets.append(
                self.product_configurator(
                    product_id=product_id,
                    glb_url=glb_url,
                    available_colors=available_colors,
                )
            )
        else:
            widgets.append(
                self.threejs_viewer(
                    product_id=product_id,
                    glb_url=glb_url,
                    usdz_url=usdz_url,
                )
            )

        if usdz_url:
            widgets.append(self.spacer(16))
            widgets.append(
                self.ar_quick_look_button(
                    product_id=product_id,
                    usdz_url=usdz_url,
                )
            )

        widgets.append(self.spacer(32))
        return widgets

    # -------------------------------------------------------------------------
    # Section Builders
    # -------------------------------------------------------------------------

    def hero_section(
        self,
        title: str,
        subtitle: str = "",
        cta_text: str = "",
        cta_link: str = "",
        background_image: str = "",
    ) -> list[dict[str, Any]]:
        """Build hero section widgets."""
        widgets = []

        widgets.append(self.spacer(80))
        widgets.append(self.heading(title, size="xxl", tag="h1"))

        if subtitle:
            widgets.append(self.text(f"<p>{subtitle}</p>"))

        if cta_text:
            widgets.append(self.spacer(24))
            widgets.append(self.button(cta_text, cta_link))

        widgets.append(self.spacer(80))

        return widgets

    def collection_section(
        self,
        title: str,
        subtitle: str = "",
        category_slug: str = "",
        columns: int = 4,
    ) -> list[dict[str, Any]]:
        """Build collection section widgets."""
        widgets = []

        widgets.append(self.spacer(60))
        widgets.append(self.heading(title, size="xl"))

        if subtitle:
            widgets.append(self.text(f"<p>{subtitle}</p>"))

        widgets.append(self.spacer(32))
        widgets.append(self.products_grid(columns=columns, category=category_slug))
        widgets.append(self.spacer(60))

        return widgets

    # -------------------------------------------------------------------------
    # Template Generators
    # -------------------------------------------------------------------------

    def generate_home_page(
        self,
        hero_title: str = "",
        hero_subtitle: str = "",
        hero_cta: str = "",
        hero_link: str = "/shop",
        hero_image: str = "",
        collections: list[dict[str, str]] | None = None,
    ) -> ElementorTemplate:
        """Generate home page template."""
        template = ElementorTemplate(
            title="Home",
            page_settings={
                "hide_title": "yes",
                "template": "elementor_canvas",
            },
        )

        # Hero section
        hero_widgets = self.hero_section(
            title=hero_title or self.brand.name,
            subtitle=hero_subtitle or self.brand.voice.tagline,
            cta_text=hero_cta or self.brand.voice.cta_primary,
            cta_link=hero_link,
            background_image=hero_image,
        )
        template.add_section(hero_widgets, layout=SectionLayout.FULL_WIDTH)

        # Collection sections
        if collections:
            for col in collections:
                col_widgets = self.collection_section(
                    title=col.get("title", "Collection"),
                    subtitle=col.get("subtitle", ""),
                    category_slug=col.get("slug", ""),
                )
                template.add_section(col_widgets)

        return template

    def generate_collection_page(
        self,
        title: str,
        description: str = "",
        category_slug: str = "",
    ) -> ElementorTemplate:
        """Generate collection/archive page template."""
        template = ElementorTemplate(
            title=title,
            page_settings={"template": "elementor_header_footer"},
        )

        # Header
        header_widgets = [
            self.spacer(48),
            self.heading(title, size="xl", tag="h1"),
        ]
        if description:
            header_widgets.append(self.text(f"<p>{description}</p>"))
        header_widgets.append(self.spacer(32))

        template.add_section(header_widgets)

        # Products
        products_widgets = [
            self.products_grid(columns=4, rows=4, category=category_slug),
            self.spacer(48),
        ]
        template.add_section(products_widgets)

        return template

    def generate_product_page(self) -> ElementorTemplate:
        """Generate single product page template."""
        template = ElementorTemplate(
            title="Single Product",
            type="single",
            page_settings={"template": "elementor_header_footer"},
        )

        # Product images (left column would be handled differently)
        product_widgets = [
            self._widget(WidgetType.PRODUCT_IMAGES, {}),
            self._widget(WidgetType.PRODUCT_TITLE, {}),
            self._widget(WidgetType.PRODUCT_PRICE, {}),
            self._widget(WidgetType.ADD_TO_CART, {}),
        ]

        template.add_section(product_widgets)

        return template


# =============================================================================
# Convenience Function
# =============================================================================


def generate_template(
    page_spec: PageSpec,
    brand_kit: BrandKit | None = None,
) -> ElementorTemplate:
    """
    Generate template from page specification.

    Args:
        page_spec: Page specification
        brand_kit: Brand design tokens

    Returns:
        ElementorTemplate ready for export
    """
    config = ElementorConfig(brand_kit=brand_kit or SKYYROSE_BRAND_KIT)
    builder = ElementorBuilder(config)

    if page_spec.page_type == PageType.HOME:
        return builder.generate_home_page(
            hero_title=page_spec.hero_title,
            hero_subtitle=page_spec.hero_subtitle,
            hero_cta=page_spec.hero_cta,
            hero_image=page_spec.hero_image,
        )
    elif page_spec.page_type == PageType.COLLECTION:
        return builder.generate_collection_page(
            title=page_spec.title,
            description=page_spec.description,
        )
    elif page_spec.page_type == PageType.PRODUCT:
        return builder.generate_product_page()
    else:
        # Default to basic page
        template = ElementorTemplate(title=page_spec.title)
        return template


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ElementorBuilder",
    "ElementorConfig",
    "ElementorTemplate",
    "BrandKit",
    "BrandColors",
    "BrandTypography",
    "BrandSpacing",
    "BrandImagery",
    "BrandVoice",
    "PageSpec",
    "PageType",
    "WidgetType",
    "SectionLayout",
    "SKYYROSE_BRAND_KIT",
    "generate_template",
]
