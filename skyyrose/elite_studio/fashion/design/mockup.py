"""
Mockup generation tools for SkyyRose Elite Studio.

MockupGenerator produces structured prompts and specifications for
AI-generated product mockups.

""
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class MockupResult:
    """Immutable result from mockup generation planning."""

    mockup_id: str
    sku: str
    garment_type: str
    collection: str
    view: str  # "front", "back", "detail", "lifestyle"
    generation_prompt: str
    texture_requirements: tuple[str, ...]
    avoid_requirements: tuple[str, ...]
    photography_spec: str
    color_spec: str
    brand_elements: tuple[str, ...]
    quality_checks: tuple[str, ...]


class MockupGenerator:
    """Generates structured mockup specifications for SkyyRose products.

    Produces generation-ready prompts and QA requirements for each view type.
    """

    def __init__(self) -> None:
        from ..colorway import ColorAdvisor
        from ..knowledge import FashionKnowledgeBase
        from ..materials import MaterialsExpert
        from ..photography import PhotographyDirector
        from ..qa_rules import FashionQA

        self._kb = FashionKnowledgeBase()
        self._color = ColorAdvisor()
        self._materials = MaterialsExpert()
        self._photography = PhotographyDirector()
        self._qa = FashionQA()

    def generate_mockup_spec(
        self,
        sku: str,
        garment_type: str,
        collection: str,
        view: str = "front",
    ) -> MockupResult:
        """Generate a complete mockup specification for a product view."""
        mockup_id = str(uuid.uuid4())[:8]

        # Resolve fabric
        fabric = self._kb.get_default_fabric_for_garment(garment_type)

        # Texture and avoid keywords
        texture_kws = self._materials.get_prompt_keywords(fabric)
        avoid_kws = self._materials.get_avoid_keywords(fabric)

        # Photography spec
        style = self._photography.recommend_style(garment_type, collection)
        std = self._photography.get_standard(style)
        photo_spec = (
            f"{style}: {std.camera_angle} | {std.lighting}" if std else f"{style} photography"
        )

        # Color spec
        palette = self._color.get_collection_palette(collection)
        color_spec = (
            f"Primary {palette.primary}, secondary {palette.secondary}, accent {palette.accent}"
        )

        # Brand elements
        brand_elements = (
            "SkyyRose embroidered rose detail",
            f"{collection.replace('-', ' ').title()} collection aesthetic",
            "'' brand DNA",
        )

        # QA checks from garment rules
        qa_rules = self._qa.get_rules_for_garment(garment_type)
        qa_checks = tuple(r.pass_criteria for r in qa_rules[:4])

        # Build generation prompt
        texture_str = ", ".join(texture_kws[:3]) if texture_kws else "premium fabric texture"
        avoid_str = ", ".join(avoid_kws[:2]) if avoid_kws else ""
        avoid_clause = f"Avoid: {avoid_str}. " if avoid_str else ""

        generation_prompt = (
            f"SkyyRose luxury streetwear {garment_type}, "
            f"{collection.replace('-', ' ').title()} collection, "
            f"{view} view. "
            f"Color: {palette.primary} primary with {palette.accent} accent. "
            f"Fabric: {texture_str}. "
            f"{avoid_clause}"
            f"{style.capitalize()} photography. "
            f"Premium quality, '' Oakland streetwear brand. "
            f"Photorealistic product render."
        )

        return MockupResult(
            mockup_id=mockup_id,
            sku=sku,
            garment_type=garment_type,
            collection=collection,
            view=view,
            generation_prompt=generation_prompt,
            texture_requirements=texture_kws,
            avoid_requirements=avoid_kws,
            photography_spec=photo_spec,
            color_spec=color_spec,
            brand_elements=brand_elements,
            quality_checks=qa_checks,
        )

    def generate_all_views(
        self, sku: str, garment_type: str, collection: str
    ) -> list[MockupResult]:
        """Generate mockup specs for all standard views of a product."""
        views = ["front", "back", "detail", "lifestyle"]
        return [self.generate_mockup_spec(sku, garment_type, collection, view) for view in views]
