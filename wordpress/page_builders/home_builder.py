"""
Home Page Builder for SkyyRose

Generates cinematic homepage with:
- Spinning SkyyRose logo (Lottie animation)
- 3D ambient background with particles
- Featured collections showcase
- Brand statement and CTA
- Newsletter signup

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

from typing import Any

from wordpress.elementor import (
    SKYYROSE_BRAND_KIT,
    ElementorBuilder,
    ElementorConfig,
    ElementorTemplate,
    SectionLayout,
    WidgetType,
)


class HomePageBuilder(ElementorBuilder):
    """
    Cinematic home page generator for SkyyRose.

    Builds hero section with spinning logo, featured collections,
    and brand storytelling elements.
    """

    def __init__(self, config: ElementorConfig | None = None) -> None:
        """Initialize home page builder."""
        super().__init__(config or ElementorConfig(brand_kit=SKYYROSE_BRAND_KIT))

    def build_spinning_logo_section(
        self,
        logo_json_url: str = "/wp-content/uploads/animations/skyyrose-logo-spinning.json",
        height: str = "400px",
    ) -> list[dict[str, Any]]:
        """
        Build spinning logo hero section.

        Args:
            logo_json_url: URL to Lottie JSON animation file
            height: Section height

        Returns:
            List of widget dicts
        """
        widgets = []

        # Spacer above logo
        widgets.append(self.spacer(60))

        # Spinning logo - Lottie animation
        widgets.append(
            self._widget(
                WidgetType.LOTTIE_ANIMATION,
                {
                    "lottie_url": logo_json_url,
                    "loop": "yes",
                    "speed": "1.0",
                    "reverse": "no",
                    "segments": "",
                    "autoplay": "yes",
                    "trigger": "none",
                    "width": {"size": 200, "unit": "px"},
                    "height": {"size": 200, "unit": "px"},
                    "align": "center",
                    "responsive_pause": "yes",
                },
            )
        )

        widgets.append(self.spacer(40))

        return widgets

    def build_3d_background_section(
        self,
        collection_slug: str = "black-rose",
    ) -> list[dict[str, Any]]:
        """
        Build 3D ambient background section.

        Args:
            collection_slug: Collection for theme colors

        Returns:
            List of widget dicts
        """
        widgets = []

        # Three.js background with particles
        widgets.append(
            self._widget(
                WidgetType.THREEJS_BACKGROUND,
                {
                    "scene_type": "ambient_particles",
                    "collection_slug": collection_slug,
                    "particle_count": "100",
                    "particle_speed": "0.5",
                    "background_color": self.brand.colors.background,
                    "height": {"size": 600, "unit": "px"},
                },
            )
        )

        return widgets

    def build_featured_collections_grid(self) -> list[dict[str, Any]]:
        """
        Build featured collections showcase.

        Returns:
            List of widget dicts with 3 collection cards
        """
        widgets = []

        widgets.append(self.spacer(80))

        # Section title
        widgets.append(
            self.heading(
                "Explore Our Collections",
                size="xl",
                tag="h2",
                align="center",
            )
        )

        widgets.append(
            self.text(
                "Where love meets luxury across three distinct experiences",
                align="center",
            )
        )

        widgets.append(self.spacer(60))

        # Collection cards
        collections = [
            {
                "title": "BLACK ROSE",
                "subtitle": "Dark Elegance & Mystery",
                "slug": "black-rose",
                "color": "#C0C0C0",
                "description": "Limited edition pieces with gothic luxury aesthetic",
            },
            {
                "title": "LOVE HURTS",
                "subtitle": "Emotional Expression",
                "slug": "love-hurts",
                "color": "#B76E79",
                "description": "Bold statements celebrating vulnerability and strength",
            },
            {
                "title": "SIGNATURE",
                "subtitle": "Premium Essentials",
                "slug": "signature",
                "color": "#C9A962",
                "description": "Oakland-made luxury streetwear fundamentals",
            },
        ]

        for collection in collections:
            widgets.append(
                self._widget(
                    WidgetType.COLLECTION_CARD,
                    {
                        "collection_slug": collection["slug"],
                        "title": collection["title"],
                        "subtitle": collection["subtitle"],
                        "description": collection["description"],
                        "color": collection["color"],
                        "link": f"/collection/{collection['slug']}",
                        "image_url": f"/wp-content/uploads/collections/{collection['slug']}-hero.jpg",
                        "hover_effect": "lift",
                    },
                )
            )

            widgets.append(self.spacer(24))

        widgets.append(self.spacer(60))

        return widgets

    def build_brand_statement(self) -> list[dict[str, Any]]:
        """
        Build brand narrative section.

        Returns:
            List of widget dicts
        """
        widgets = []

        widgets.append(self.spacer(80))

        widgets.append(
            self.heading(
                "Born from Oakland's streets — evolved for the world.",
                size="lg",
                tag="h2",
                align="center",
            )
        )

        widgets.append(self.spacer(32))

        widgets.append(
            self.text(
                "<p>SkyyRose is more than fashion. It's a movement.</p>"
                "<p>Each collection tells a story of identity, resilience, and luxury.</p>",
                align="center",
            )
        )

        widgets.append(self.spacer(48))

        # CTA buttons
        widgets.append(self.button("Shop Now", "/shop", style="primary", size="lg"))
        widgets.append(self.spacer(32))
        widgets.append(self.button("Read Our Story", "/about", style="secondary", size="lg"))

        widgets.append(self.spacer(80))

        return widgets

    def build_newsletter_section(self) -> list[dict[str, Any]]:
        """
        Build email signup section.

        Returns:
            List of widget dicts
        """
        widgets = []

        widgets.append(self.spacer(80))

        widgets.append(
            self.heading(
                "Stay in the Loop",
                size="lg",
                tag="h3",
                align="center",
            )
        )

        widgets.append(
            self.text(
                "Get exclusive drops, early access, and behind-the-scenes content.",
                align="center",
            )
        )

        widgets.append(self.spacer(32))

        # Email form (Elementor Pro Form widget)
        widgets.append(
            self._widget(
                WidgetType.FORM,
                {
                    "form_name": "newsletter",
                    "form_id": "newsletter_signup",
                    "form_fields": [
                        {
                            "field_type": "email",
                            "field_label": "Email Address",
                            "placeholder": "you@example.com",
                            "required": "yes",
                        }
                    ],
                    "submit_button_text": "Join the Movement",
                    "success_message": "Thank you for joining! Check your email.",
                },
            )
        )

        widgets.append(self.spacer(80))

        return widgets

    def generate(
        self,
        hero_title: str = "SkyyRose",
        collections: list[dict[str, str]] | None = None,
    ) -> ElementorTemplate:
        """
        Generate complete home page template.

        Args:
            hero_title: Main hero title
            collections: Optional custom collections list

        Returns:
            ElementorTemplate ready for export
        """
        template = ElementorTemplate(
            title="Home",
            page_settings={
                "hide_title": "yes",
                "template": "elementor_canvas",
                "post_title": "SkyyRose",
                "meta_description": "Cinematic 3D luxury streetwear from Oakland. Explore immersive collections with interactive 3D experiences.",
            },
        )

        # Section 1: Spinning logo hero
        spinning_logo_widgets = self.build_spinning_logo_section()
        template.add_section(
            spinning_logo_widgets,
            layout=SectionLayout.FULL_WIDTH,
            settings={
                "background_background": "gradient",
                "background_color": self.brand.colors.background,
            },
        )

        # Section 2: Featured collections
        collections_widgets = self.build_featured_collections_grid()
        template.add_section(
            collections_widgets,
            layout=SectionLayout.BOXED,
        )

        # Section 3: Brand statement
        statement_widgets = self.build_brand_statement()
        template.add_section(
            statement_widgets,
            layout=SectionLayout.FULL_WIDTH,
            settings={
                "background_background": "color",
                "background_color": self.brand.colors.background_alt,
            },
        )

        # Section 4: Newsletter signup
        newsletter_widgets = self.build_newsletter_section()
        template.add_section(
            newsletter_widgets,
            layout=SectionLayout.BOXED,
        )

        return template


__all__ = ["HomePageBuilder"]
