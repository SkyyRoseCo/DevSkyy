"""
About Page Builder for SkyyRose

Generates brand storytelling page with:
- Parallax hero background
- Brand narrative sections
- Press timeline with publication logos
- Founder story
- Impact metrics

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

from typing import Any

from wordpress.data.press_mentions import get_featured_press
from wordpress.elementor import (
    SKYYROSE_BRAND_KIT,
    ElementorBuilder,
    ElementorConfig,
    ElementorTemplate,
    SectionLayout,
    WidgetType,
)


class AboutPageBuilder(ElementorBuilder):
    """
    Brand storytelling about page generator.

    Builds narrative-driven about pages with parallax effects and press coverage.
    """

    def __init__(self, config: ElementorConfig | None = None) -> None:
        """Initialize about page builder."""
        super().__init__(config or ElementorConfig(brand_kit=SKYYROSE_BRAND_KIT))

    def build_parallax_hero(self) -> list[dict[str, Any]]:
        """
        Build parallax hero section with 3D background.

        Returns:
            List of widget dicts
        """
        widgets = []

        widgets.append(self.spacer(100))

        widgets.append(
            self.heading(
                "SkyyRose",
                size="xxl",
                tag="h1",
                align="center",
            )
        )

        widgets.append(
            self.text(
                "<p>A love letter to Oakland. A revolution in streetwear.</p>",
                align="center",
            )
        )

        widgets.append(self.spacer(100))

        return widgets

    def build_brand_narrative(self) -> list[dict[str, Any]]:
        """
        Build multi-section brand narrative.

        Returns:
            List of widget dicts
        """
        widgets = []

        sections = [
            {
                "title": "Our Origin Story",
                "content": """
<p>SkyyRose was born from the heart of Oakland, where street culture meets luxury craftsmanship.</p>
<p>What started as a vision to honor heritage and celebrate identity has evolved into a global movement
for emotional expression through fashion.</p>
<p>Every piece tells a story. Every collection speaks to the soul.</p>
""",
            },
            {
                "title": "The Collections",
                "content": """
<p><strong>BLACK ROSE:</strong> Dark elegance meets modern luxury. Limited edition pieces that celebrate mystery and exclusivity.</p>
<p><strong>LOVE HURTS:</strong> Raw emotion transformed into high fashion. Bold statements for the courageous.</p>
<p><strong>SIGNATURE:</strong> Oakland-made essentials. Premium quality that lasts a lifetime.</p>
""",
            },
            {
                "title": "Our Commitment",
                "content": """
<p>Sustainable. Ethical. Transparent.</p>
<p>We believe luxury should never come at the expense of people or planet.
Every stitch, every material, every decision is made with intention.</p>
""",
            },
        ]

        for i, section in enumerate(sections):
            widgets.append(self.spacer(60))

            widgets.append(
                self.heading(
                    section["title"],
                    size="lg",
                    tag="h2",
                    align="center",
                )
            )

            widgets.append(self.spacer(24))

            widgets.append(self.text(section["content"], align="left"))

            if i < len(sections) - 1:
                widgets.append(self.spacer(40))

        widgets.append(self.spacer(60))

        return widgets

    def build_press_timeline(self) -> list[dict[str, Any]]:
        """
        Build press coverage timeline from centralized press mentions data.

        Uses press_mentions.py for data source, enabling dynamic updates
        without rebuilding templates.

        Returns:
            List of widget dicts
        """
        widgets = []

        widgets.append(self.spacer(80))

        widgets.append(
            self.heading(
                "Press & Recognition",
                size="xl",
                tag="h2",
                align="center",
            )
        )

        widgets.append(self.spacer(60))

        # Fetch featured press mentions from centralized data source
        press_mentions = get_featured_press(limit=3)

        for mention in press_mentions:
            widgets.append(
                self._widget(
                    WidgetType.TIMELINE,
                    {
                        "date": mention.month_year,
                        "title": mention.publication,
                        "description": mention.title,
                        "link": mention.link,
                        "image": mention.logo_url,
                    },
                )
            )

            widgets.append(self.spacer(32))

        widgets.append(self.spacer(60))

        return widgets

    def build_impact_metrics(self) -> list[dict[str, Any]]:
        """
        Build impact and community metrics.

        Returns:
            List of widget dicts
        """
        widgets = []

        widgets.append(self.spacer(80))

        widgets.append(
            self.heading(
                "Our Impact",
                size="xl",
                tag="h2",
                align="center",
            )
        )

        widgets.append(self.spacer(60))

        metrics = [
            {"number": "50K+", "label": "SkyyRose Community Members"},
            {"number": "15+", "label": "Countries Served"},
            {"number": "1000+", "label": "Pieces Crafted Annually"},
            {"number": "100%", "label": "Ethically Sourced Materials"},
        ]

        for metric in metrics:
            widgets.append(
                self._widget(
                    WidgetType.ICON_BOX,
                    {
                        "title": metric["number"],
                        "description": metric["label"],
                        "title_color": self.brand.colors.primary,
                        "description_color": self.brand.colors.text_light,
                    },
                )
            )

            widgets.append(self.spacer(32))

        widgets.append(self.spacer(80))

        return widgets

    def generate(self) -> ElementorTemplate:
        """
        Generate complete about page template.

        Returns:
            ElementorTemplate ready for export
        """
        template = ElementorTemplate(
            title="About SkyyRose",
            page_settings={
                "hide_title": "yes",
                "template": "elementor_canvas",
                "post_title": "About Us - SkyyRose Luxury Streetwear",
                "meta_description": "Learn the story behind SkyyRose: where Oakland heritage meets luxury fashion innovation.",
            },
        )

        # Section 1: Parallax hero
        hero_widgets = self.build_parallax_hero()
        template.add_section(
            hero_widgets,
            layout=SectionLayout.FULL_WIDTH,
            settings={
                "background_background": "gradient",
                "background_color_a": self.brand.colors.secondary,
                "background_color_b": self.brand.colors.background,
            },
        )

        # Section 2: Brand narrative
        narrative_widgets = self.build_brand_narrative()
        template.add_section(
            narrative_widgets,
            layout=SectionLayout.BOXED,
        )

        # Section 3: Press timeline
        press_widgets = self.build_press_timeline()
        template.add_section(
            press_widgets,
            layout=SectionLayout.BOXED,
            settings={
                "background_color": self.brand.colors.background_alt,
            },
        )

        # Section 4: Impact metrics
        impact_widgets = self.build_impact_metrics()
        template.add_section(
            impact_widgets,
            layout=SectionLayout.BOXED,
        )

        # Section 5: CTA
        cta_widgets = [
            self.spacer(80),
            self.heading("Ready to Join the Movement?", size="lg", tag="h2", align="center"),
            self.spacer(32),
            self.button("Shop Now", "/shop", style="primary", size="lg"),
            self.spacer(80),
        ]
        template.add_section(
            cta_widgets,
            layout=SectionLayout.FULL_WIDTH,
            settings={
                "background_color": self.brand.colors.primary,
            },
        )

        return template


__all__ = ["AboutPageBuilder"]
