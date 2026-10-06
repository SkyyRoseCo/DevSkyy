"""
Luxury Homepage Builder for SkyyRose.

Generates luxury fashion homepage with editorial layouts following NET-A-PORTER/SSENSE standards.
Enhanced with 2025 Interactive Vibes:
- GSAP ScrollTrigger animations
- View Transitions API
- Glassmorphism cards
- Magnetic hover effects
- Custom cursor
- Parallax scrolling

Author: DevSkyy Platform Team
Version: 2.0.0
"""

from dataclasses import dataclass
from typing import Any

from wordpress.elementor import COLLECTION_BRAND_KITS, BrandKit, ElementorPageBuilder
from wordpress.page_builders.gsap_animations import (
    AnimationType,
    GSAPAnimationBuilder,
    GSAPConfig,
)


@dataclass
class LuxuryHomePageBuilder(ElementorPageBuilder):
    """
    Generates luxury fashion homepage with hero, collections grid, editorial sections.

    Enhanced with GSAP ScrollTrigger animations and 2025 interactive effects.
    """

    def __post_init__(self) -> None:
        """Initialize GSAP animation builder."""
        self.gsap_builder = GSAPAnimationBuilder(
            GSAPConfig(
                duration=0.8,
                stagger=0.15,
                scroll_trigger_start="top 80%",
            )
        )
        self._animations: list[dict[str, Any]] = []

    def build_hero_section(self, brand_kit: BrandKit) -> dict[str, Any]:
        """
        Full-bleed hero with video background and minimal text overlay.

        Enhanced with GSAP animations:
        - Split text reveal for headline
        - Fade in up for subtitle
        - Magnetic effect on CTA button

        Args:
            brand_kit: Collection brand kit for colors and content

        Returns:
            Elementor section configuration dict
        """
        # Register GSAP animations for hero
        self._animations.extend(
            [
                self.gsap_builder.build_split_text_animation(
                    ".hero-headline",
                    split_type="chars,words",
                ),
                self.gsap_builder.build_scroll_animation(
                    AnimationType.FADE_IN_UP,
                    ".hero-subtitle",
                ),
                self.gsap_builder.build_magnetic_button(".hero-cta"),
            ]
        )

        return {
            "elType": "section",
            "settings": {
                "layout": "full_width",
                "height": "100vh",
                "background_video_link": "/wp-content/uploads/hero/skyyrose-hero.mp4",
                "background_video_poster": "/wp-content/uploads/hero/skyyrose-hero-poster.webp",
                "background_overlay": "yes",
                "background_overlay_opacity": 0.4,
                "background_overlay_color": "linear-gradient(180deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.8) 100%)",
                "padding": {"top": 0, "bottom": 0},
                "_css_classes": "skyyrose-hero glass-hero",
                "data_settings": {"view_transition": "hero"},
            },
            "elements": [
                {
                    "elType": "column",
                    "settings": {
                        "_column_size": 100,
                        "content_position": "center",
                    },
                    "elements": [
                        # Hero headline with split text animation (Playfair Display)
                        {
                            "elType": "widget",
                            "widgetType": "heading",
                            "settings": {
                                "title": brand_kit.name,
                                "typography_font_family": "Playfair Display",
                                "typography_font_size": {"size": 82, "unit": "px"},
                                "typography_font_size_tablet": {"size": 56, "unit": "px"},
                                "typography_font_size_mobile": {"size": 36, "unit": "px"},
                                "typography_font_weight": 700,
                                "typography_line_height": {"size": 1.1, "unit": "em"},
                                "color": "#FFFFFF",
                                "text_align": "center",
                                "_css_classes": "hero-headline",
                                "_animation": "",  # Handled by GSAP
                            },
                        },
                        # Subtitle with fade animation (Inter)
                        {
                            "elType": "widget",
                            "widgetType": "text-editor",
                            "settings": {
                                "editor": f"<p>{brand_kit.name}</p>",
                                "typography_font_family": "Inter",
                                "typography_font_size": {"size": 20, "unit": "px"},
                                "typography_font_weight": 300,
                                "typography_letter_spacing": {"size": 0.2, "unit": "em"},
                                "color": "#F5F5F0",
                                "text_align": "center",
                                "_css_classes": "hero-subtitle",
                                "_margin": {"top": 24, "bottom": 40, "unit": "px"},
                            },
                        },
                        # CTA button with magnetic effect
                        {
                            "elType": "widget",
                            "widgetType": "button",
                            "settings": {
                                "text": "Explore Collections",
                                "link": {"url": "/collections"},
                                "typography_font_family": "Inter",
                                "typography_font_weight": 600,
                                "typography_font_size": {"size": 14, "unit": "px"},
                                "typography_text_transform": "uppercase",
                                "typography_letter_spacing": {"size": 0.15, "unit": "em"},
                                "button_background_color": "rgba(183, 110, 121, 0.2)",
                                "button_hover_background_color": "rgba(183, 110, 121, 0.4)",
                                "button_text_color": "#FFFFFF",
                                "button_hover_text_color": "#FFFFFF",
                                "button_border_width": {"size": 1, "unit": "px"},
                                "button_border_color": "rgba(183, 110, 121, 0.6)",
                                "button_hover_border_color": brand_kit.colors.primary,
                                "button_border_radius": {"size": 12, "unit": "px"},
                                "button_padding": {
                                    "top": 18,
                                    "right": 36,
                                    "bottom": 18,
                                    "left": 36,
                                    "unit": "px",
                                },
                                "_css_classes": "hero-cta glass-button",
                                "motion_fx_enabled": "yes",
                            },
                        },
                        # Scroll indicator
                        {
                            "elType": "widget",
                            "widgetType": "icon",
                            "settings": {
                                "icon": {"value": "fas fa-chevron-down", "library": "fa-solid"},
                                "icon_size": {"size": 24, "unit": "px"},
                                "primary_color": "rgba(255, 255, 255, 0.6)",
                                "align": "center",
                                "_css_classes": "scroll-indicator",
                                "_animation": "skyyrose-bounce",
                                "_position": {"type": "absolute", "bottom": 40, "unit": "px"},
                            },
                        },
                    ],
                }
            ],
        }

    def build_collections_grid(self) -> dict[str, Any]:
        """
        3-column collections grid with hover effects and GSAP stagger animations.

        Returns:
            Elementor section configuration dict
        """
        collections = ["signature", "love-hurts", "black-rose"]

        # Register stagger animation for collection cards
        self._animations.append(
            self.gsap_builder.build_scroll_animation(
                AnimationType.SCALE_IN,
                ".collection-card",
                custom_from={"opacity": 0, "scale": 0.9, "y": 40},
                custom_to={"opacity": 1, "scale": 1, "y": 0},
            )
        )

        return {
            "elType": "section",
            "settings": {
                "layout": "boxed",
                "gap": "extended",  # 48px gap (luxury spacing)
                "padding": {"top": 120, "bottom": 120, "unit": "px"},
                "background_color": "#0A0A0A",
                "_css_classes": "collections-section",
            },
            "elements": [
                {
                    "elType": "widget",
                    "widgetType": "heading",
                    "settings": {
                        "title": "The Collections",
                        "typography_font_family": "Playfair Display",
                        "typography_font_size": {"size": 48, "unit": "px"},
                        "typography_font_weight": 400,
                        "typography_letter_spacing": {"size": 0.05, "unit": "em"},
                        "color": "#FFFFFF",
                        "text_align": "center",
                        "_css_classes": "section-title",
                        "_margin": {"bottom": 60, "unit": "px"},
                    },
                },
                {
                    "elType": "container",
                    "settings": {
                        "flex_direction": "row",
                        "flex_gap": {"size": 32, "unit": "px"},
                        "content_width": "boxed",
                    },
                    "elements": [
                        {
                            "elType": "column",
                            "settings": {"_column_size": 33},
                            "elements": [self._build_collection_card(coll, idx)],
                        }
                        for idx, coll in enumerate(collections)
                    ],
                },
            ],
        }

    def _build_collection_card(
        self,
        collection_slug: str,
        index: int = 0,
    ) -> dict[str, Any]:
        """
        Individual collection card with glassmorphism, GSAP animations, and hover effects.

        Args:
            collection_slug: Collection identifier (signature, love-hurts, black-rose)
            index: Card index for stagger animation

        Returns:
            Widget configuration dict
        """
        brand_kit = COLLECTION_BRAND_KITS[collection_slug]

        # Collection-specific descriptions
        descriptions = {
            "signature": "Timeless elegance meets modern sophistication",
            "love-hurts": "Bold statements for the fearless soul",
            "black-rose": "Dark romance in every thread",
        }

        return {
            "elType": "container",
            "settings": {
                "_css_classes": f"collection-card glass-card stagger-{index + 1}",
                "data_settings": {
                    "view_transition": "card",
                    "cursor_hover": True,
                    "product_image": f"/wp-content/uploads/collections/{collection_slug}-preview.webp",
                },
                "border_radius": {"size": 20, "unit": "px"},
                "overflow": "hidden",
            },
            "elements": [
                {
                    "elType": "widget",
                    "widgetType": "image",
                    "settings": {
                        "image": {
                            "url": f"/wp-content/uploads/collections/{collection_slug}-hero.webp"
                        },
                        "image_size": "full",
                        "width": {"size": 100, "unit": "%"},
                        "height": {"size": 480, "unit": "px"},
                        "object_fit": "cover",
                        "_css_classes": "collection-image",
                        "hover_animation": "none",  # Handled by GSAP
                    },
                },
                {
                    "elType": "container",
                    "settings": {
                        "_css_classes": "collection-overlay",
                        "position": "absolute",
                        "inset": {"bottom": 0, "left": 0, "right": 0},
                        "background_gradient": f"linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.8) 50%, {brand_kit.colors.dark} 100%)",
                        "padding": {"top": 80, "right": 24, "bottom": 32, "left": 24, "unit": "px"},
                    },
                    "elements": [
                        {
                            "elType": "widget",
                            "widgetType": "heading",
                            "settings": {
                                "title": brand_kit.name,
                                "typography_font_family": "Playfair Display",
                                "typography_font_size": {"size": 28, "unit": "px"},
                                "typography_font_weight": 500,
                                "typography_letter_spacing": {"size": 0.05, "unit": "em"},
                                "color": "#FFFFFF",
                                "_margin": {"bottom": 8, "unit": "px"},
                            },
                        },
                        {
                            "elType": "widget",
                            "widgetType": "text-editor",
                            "settings": {
                                "editor": f"<p>{descriptions.get(collection_slug, '')}</p>",
                                "typography_font_family": "Inter",
                                "typography_font_size": {"size": 14, "unit": "px"},
                                "typography_font_weight": 300,
                                "color": "rgba(255, 255, 255, 0.7)",
                                "_margin": {"bottom": 16, "unit": "px"},
                            },
                        },
                        {
                            "elType": "widget",
                            "widgetType": "button",
                            "settings": {
                                "text": "Explore",
                                "link": {"url": f"/collections/{collection_slug}"},
                                "typography_font_family": "Inter",
                                "typography_font_size": {"size": 12, "unit": "px"},
                                "typography_font_weight": 600,
                                "typography_text_transform": "uppercase",
                                "typography_letter_spacing": {"size": 0.2, "unit": "em"},
                                "button_background_color": "transparent",
                                "button_text_color": brand_kit.colors.primary,
                                "button_border_width": {"size": 0, "unit": "px"},
                                "icon": {"value": "fas fa-arrow-right", "library": "fa-solid"},
                                "icon_position": "after",
                                "icon_spacing": {"size": 8, "unit": "px"},
                                "_css_classes": "collection-cta",
                            },
                        },
                    ],
                },
            ],
        }

    def build_parallax_section(self) -> dict[str, Any]:
        """
        Build parallax showcase section using 2.5D assets.

        Returns:
            Elementor section configuration dict
        """
        # Register parallax animation
        self._animations.append(self.gsap_builder.build_parallax(".parallax-layer", speed=0.3))

        return {
            "elType": "section",
            "settings": {
                "layout": "full_width",
                "height": {"size": 80, "unit": "vh"},
                "background_color": "#000000",
                "overflow": "hidden",
                "_css_classes": "parallax-section",
            },
            "elements": [
                {
                    "elType": "widget",
                    "widgetType": "image",
                    "settings": {
                        "image": {"url": "/assets/2d-25d-assets/black_rose_depth_1.webp"},
                        "_css_classes": "parallax-layer parallax-back",
                        "position": "absolute",
                        "object_fit": "cover",
                    },
                },
                {
                    "elType": "widget",
                    "widgetType": "image",
                    "settings": {
                        "image": {"url": "/assets/2d-25d-assets/black_rose_depth_2.webp"},
                        "_css_classes": "parallax-layer parallax-mid",
                        "position": "absolute",
                        "object_fit": "cover",
                    },
                },
                {
                    "elType": "widget",
                    "widgetType": "image",
                    "settings": {
                        "image": {"url": "/assets/2d-25d-assets/black_rose_depth_3.webp"},
                        "_css_classes": "parallax-layer parallax-front",
                        "position": "absolute",
                        "object_fit": "cover",
                    },
                },
            ],
        }

    def build_instagram_section(self) -> dict[str, Any]:
        """
        Build Instagram feed section with stagger animation.

        Returns:
            Elementor section configuration dict
        """
        self._animations.append(
            self.gsap_builder.build_scroll_animation(
                AnimationType.FADE_IN_UP,
                ".instagram-item",
            )
        )

        return {
            "elType": "section",
            "settings": {
                "layout": "boxed",
                "padding": {"top": 100, "bottom": 100, "unit": "px"},
                "background_color": "#0A0A0A",
            },
            "elements": [
                {
                    "elType": "widget",
                    "widgetType": "heading",
                    "settings": {
                        "title": "Follow @SkyyRose",
                        "typography_font_family": "Playfair Display",
                        "typography_font_size": {"size": 36, "unit": "px"},
                        "color": "#FFFFFF",
                        "text_align": "center",
                        "_margin": {"bottom": 40, "unit": "px"},
                    },
                },
                {
                    "elType": "widget",
                    "widgetType": "shortcode",
                    "settings": {
                        "shortcode": "[instagram-feed num=6 cols=6 showheader=false showbutton=false]",
                        "_css_classes": "instagram-grid",
                    },
                },
            ],
        }

    def generate(self) -> dict[str, Any]:
        """
        Generate complete luxury homepage with GSAP animations.

        Returns:
            Complete Elementor template configuration dict with embedded scripts
        """
        brand_kit = COLLECTION_BRAND_KITS["signature"]  # Default brand

        # Build all sections (this populates self._animations)
        sections = [
            self.build_hero_section(brand_kit),
            self.build_collections_grid(),
            self.build_parallax_section(),
            self.build_instagram_section(),
        ]

        # Generate GSAP script with all registered animations
        gsap_script = self.gsap_builder.generate_gsap_script(self._animations)
        view_transitions_css = self.gsap_builder.generate_view_transitions_css()
        glassmorphism_css = self.gsap_builder.generate_glassmorphism_css()
        custom_cursor_script = self.gsap_builder.generate_custom_cursor_script()

        # Append scripts/styles as HTML widget
        scripts_section = {
            "elType": "section",
            "settings": {"_element_id": "skyyrose-scripts"},
            "elements": [
                {
                    "elType": "widget",
                    "widgetType": "html",
                    "settings": {
                        "html": f"""
{view_transitions_css}
{glassmorphism_css}
{gsap_script}
{custom_cursor_script}

<style>
/* SkyyRose 2025 Interactive Vibes */
.scroll-indicator {{
  animation: skyyrose-bounce 2s infinite;
}}

@keyframes skyyrose-bounce {{
  0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
  40% {{ transform: translateY(-10px); }}
  60% {{ transform: translateY(-5px); }}
}}

/* Collection card hover effects */
.collection-card:hover .collection-image {{
  transform: scale(1.05);
}}

.collection-card .collection-image {{
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}}

.collection-card:hover .collection-cta {{
  transform: translateX(8px);
}}

.collection-cta {{
  transition: transform 0.3s ease;
}}

/* Parallax layers */
.parallax-back {{ transform: translateZ(-2px) scale(1.5); }}
.parallax-mid {{ transform: translateZ(-1px) scale(1.25); }}
.parallax-front {{ transform: translateZ(0); }}
</style>
""",
                    },
                },
            ],
        }

        sections.append(scripts_section)

        return {
            "content": sections,
            "page_settings": {
                "post_title": "Home - SkyyRose",
                "template": "elementor_canvas",  # Full-width, no header/footer chrome
                "meta_description": "SkyyRose - Luxury fashion. Explore our signature collections including Black Rose, Love Hurts, and Signature lines.",
            },
        }
