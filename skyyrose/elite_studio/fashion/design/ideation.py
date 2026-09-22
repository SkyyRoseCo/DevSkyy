"""
Design ideation tools for SkyyRose Elite Studio.

DesignIdeationAgent generates structured design concepts from briefs,
using fashion knowledge base, color advisor, and trend advisor.

""
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class DesignBrief:
    """Immutable design brief input for ideation."""

    collection: str  # black-rose, love-hurts, signature, kids-capsule
    garment_type: str  # hoodie, jersey, joggers, etc.
    season: str  # FW26, SS27
    target_price_usd: float
    design_intent: str  # freeform description of the design intent
    colorway_preference: str = ""  # optional preferred colorway
    reference_tags: tuple[str, ...] = ()  # mood tags: "gothic", "athletic", "pastel"


@dataclass(frozen=True)
class DesignConcept:
    """Immutable design concept output from ideation."""

    concept_id: str
    brief: DesignBrief
    concept_name: str
    headline_description: str  # 1-sentence concept summary
    full_description: str  # detailed design description
    colorway_hex: tuple[str, ...]  # primary, secondary, accent hex values
    key_design_elements: tuple[str, ...]  # branding, print, embroidery details
    fabric_specification: str  # recommended fabric with rendering notes
    styling_direction: str  # how to wear and style
    trend_alignment_notes: str  # which current trends this supports
    photography_direction: str  # recommended photography approach
    generation_prompt: str  # ready-to-use AI generation prompt


class DesignIdeationAgent:
    """Generates SkyyRose design concepts from structured briefs.

    Uses all fashion intelligence modules to produce complete, production-
    ready design concepts with generation prompts.
    """

    def __init__(self) -> None:
        from ..colorway import ColorAdvisor
        from ..editorial import EditorialDirector
        from ..knowledge import FashionKnowledgeBase
        from ..materials import MaterialsExpert
        from ..photography import PhotographyDirector
        from ..trends import TrendAdvisor

        self._kb = FashionKnowledgeBase()
        self._color = ColorAdvisor()
        self._trends = TrendAdvisor()
        self._materials = MaterialsExpert()
        self._editorial = EditorialDirector()
        self._photography = PhotographyDirector()

    def generate_concept(self, brief: DesignBrief) -> DesignConcept:
        """Generate a design concept from a brief."""
        concept_id = str(uuid.uuid4())[:8]

        # Resolve color palette
        palette = self._color.get_collection_palette(brief.collection)
        colorway = (palette.primary, palette.secondary, palette.accent)

        # Resolve fabric
        garment = self._kb.get_garment(brief.garment_type)
        fabric = (
            garment.default_fabric
            if garment
            else self._kb.get_default_fabric_for_garment(brief.garment_type)
        )

        # Material spec
        mat_spec = self._materials.get_rendering_spec(fabric)
        fabric_spec = (
            f"{fabric}: {mat_spec.reference_description}"
            if mat_spec
            else f"{fabric}: standard construction"
        )

        # Trend alignment
        trend_notes = self._trends.get_trend_notes_for_garment(brief.garment_type)
        trend_str = (
            "; ".join(trend_notes[:2]) if trend_notes else "Aligns with sport-luxury crossover"
        )

        # Styling direction
        styling_rule = self._editorial.get_styling(brief.garment_type, brief.collection)
        styling_dir = f"{styling_rule.occasion}. {styling_rule.layering_notes}"

        # Photography
        photo_style = self._photography.recommend_style(brief.garment_type, brief.collection)
        photo_std = self._photography.get_standard(photo_style)
        photo_dir = (
            f"{photo_style.upper()} style: {photo_std.lighting}"
            if photo_std
            else f"{photo_style.upper()} style photography"
        )

        # Collection DNA for concept name and description
        collection_names = {
            "black-rose": "BLACK Rose",
            "love-hurts": "Love Hurts",
            "signature": "Signature",
            "kids-capsule": "Kids Capsule",
        }
        collection_display = collection_names.get(brief.collection, brief.collection.title())

        concept_name = f"{collection_display} {brief.garment_type.title()} — {brief.season}"

        headline = (
            f"{brief.design_intent} in {collection_display} aesthetic with {fabric} construction."
        )

        full_description = (
            f"A {brief.garment_type} design rooted in {collection_display} DNA: "
            f"{brief.design_intent}. "
            f"Primary colorway {colorway[0]} with {colorway[1]} secondary and "
            f"{colorway[2]} accent. "
            f"Constructed in {fabric} ({fabric_spec.split(':')[0]}). "
            f"Target retail: ${brief.target_price_usd:.0f}."
        )

        # Key design elements
        elements: list[str] = [
            f"Primary fabric: {fabric}",
            f"Primary color: {colorway[0]}",
            f"Collection accent: {colorway[2]}",
        ]
        if brief.colorway_preference:
            elements.append(f"Colorway preference: {brief.colorway_preference}")
        if brief.reference_tags:
            elements.append(f"Reference tags: {', '.join(brief.reference_tags)}")
        elements.append("Embroidered SkyyRose rose detail")

        # Generation prompt
        texture_segment = self._materials.build_texture_prompt_segment(fabric)
        generation_prompt = (
            f"SkyyRose luxury streetwear {brief.garment_type}, {collection_display} collection. "
            f"{brief.design_intent}. "
            f"Primary color {colorway[0]}, secondary {colorway[1]}, accent {colorway[2]}. "
            f"{texture_segment} "
            f"Photography: {photo_style} style. "
            f"'' Oakland luxury brand. High-end premium quality."
        )

        return DesignConcept(
            concept_id=concept_id,
            brief=brief,
            concept_name=concept_name,
            headline_description=headline,
            full_description=full_description,
            colorway_hex=colorway,
            key_design_elements=tuple(elements),
            fabric_specification=fabric_spec,
            styling_direction=styling_dir,
            trend_alignment_notes=trend_str,
            photography_direction=photo_dir,
            generation_prompt=generation_prompt,
        )

    def generate_alternatives(self, brief: DesignBrief, n: int = 3) -> list[DesignConcept]:
        """Generate n alternative concepts for a brief using different colorways."""
        palettes = self._color.suggest_colorways(brief.garment_type, brief.collection, n=n)
        concepts: list[DesignConcept] = []

        for i, palette in enumerate(palettes[:n]):
            # Modify brief with the alternative colorway name
            alt_brief = DesignBrief(
                collection=brief.collection,
                garment_type=brief.garment_type,
                season=brief.season,
                target_price_usd=brief.target_price_usd,
                design_intent=f"{brief.design_intent} (alternative {i + 1}: {palette.name})",
                colorway_preference=palette.name,
                reference_tags=brief.reference_tags,
            )
            concepts.append(self.generate_concept(alt_brief))

        return concepts
