"""
Tech pack generation for SkyyRose Elite Studio.

TechPackGenerator produces structured technical specification documents
for garment production and manufacturing reference.

"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class TechPack:
    """Immutable technical pack for a SkyyRose garment."""

    tech_pack_id: str
    sku: str
    garment_type: str
    collection: str
    season: str
    product_name: str
    fabric_specification: str
    construction_notes: str
    colorway: tuple[str, ...]  # primary, secondary, accent hex
    size_range: str
    size_chart: dict[str, dict[str, str]]
    branding_placement: tuple[str, ...]  # where logos/embroidery go
    hardware_details: tuple[str, ...]  # zippers, grommets, drawstrings
    care_instructions: tuple[str, ...]
    render_requirements: tuple[str, ...]
    quality_checklist: tuple[str, ...]


class TechPackGenerator:
    """Generates technical packs for SkyyRose product development.

    Combines fashion knowledge base data into production-ready spec documents.
    """

    def __init__(self) -> None:
        from ..colorway import ColorAdvisor
        from ..knowledge import FashionKnowledgeBase
        from ..materials import MaterialsExpert
        from ..qa_rules import FashionQA
        from ..sizing import SizingAdvisor

        self._kb = FashionKnowledgeBase()
        self._color = ColorAdvisor()
        self._sizing = SizingAdvisor()
        self._materials = MaterialsExpert()
        self._qa = FashionQA()

    def generate(
        self,
        sku: str,
        garment_type: str,
        collection: str,
        product_name: str,
        season: str = "FW26",
    ) -> TechPack:
        """Generate a tech pack for a product."""
        tech_pack_id = str(uuid.uuid4())[:8]

        # Garment and fabric
        garment = self._kb.get_garment(garment_type)
        fabric = (
            garment.default_fabric
            if garment
            else self._kb.get_default_fabric_for_garment(garment_type)
        )
        construction = garment.construction_notes if garment else "Standard construction"

        # Fabric spec
        spec = self._materials.get_rendering_spec(fabric)
        fabric_spec = (
            f"{fabric.upper()} | Weight: {self._kb.get_fabric(fabric).weight_range if self._kb.get_fabric(fabric) else 'N/A'} | "
            f"{self._kb.get_fabric(fabric).texture if self._kb.get_fabric(fabric) else ''}"
        )

        # Color
        palette = self._color.get_collection_palette(collection)
        colorway = (palette.primary, palette.secondary, palette.accent)

        # Sizing
        sizing_guide = self._sizing.get_guideline(garment_type, collection)
        size_chart = self._sizing.get_size_chart(garment_type)

        # Branding placement
        branding_map = {
            "hoodie": (
                "Left chest: SkyyRose rose embroidery (3 inch)",
                "Back yoke: optional SkyyRose wordmark",
                "Inner label: woven brand label at center back neck",
                "Drawstring tips: metal aglets with SR engraving",
            ),
            "crewneck": (
                "Left chest: SkyyRose rose embroidery (3 inch)",
                "Inner label: woven brand label at center back neck",
            ),
            "jersey": (
                "Front center: number placement with alternating rose fill",
                "Back center: number + name lettering",
                "Left chest: SkyyRose rose mark (2 inch)",
                "Neck tape: SkyyRose woven label",
            ),
            "joggers": (
                "Left hip: SkyyRose rose embroidery (2 inch)",
                "Waistband inner: woven brand label",
            ),
            "shorts": (
                "Left leg: SkyyRose rose embroidery or heat transfer (2 inch)",
                "Waistband inner: woven brand label",
            ),
            "jacket": (
                "Left chest: SkyyRose rose embroidery (3 inch)",
                "Back center: optional large back embroidery or graphic",
                "Inner label: woven brand label",
                "Zipper pull: custom SR branded pull",
            ),
            "varsity jacket": (
                "Left chest: SkyyRose rose chenille embroidery (4 inch)",
                "Right sleeve: optional patch or emblem",
                "Back: large chenille lettering — collection name",
                "Inner label: woven brand label",
                "Hood interior: hidden rose garden embroidery",
            ),
        }
        branding = branding_map.get(
            garment_type.lower(),
            (
                "Left chest: SkyyRose rose embroidery (2-3 inch)",
                "Inner label: woven brand label",
            ),
        )

        # Hardware
        hardware_map = {
            "hoodie": ("Metal drawstring aglets", "Metal grommets at drawstring eyelets"),
            "jacket": ("YKK full-zip or snap closure", "Metal zipper pull"),
            "varsity jacket": ("Snap closure", "Ribbed collar/cuff/hem contrast"),
            "joggers": ("Flat drawstring with aglets", "Elastic waistband"),
            "sweatpants": ("Flat drawstring with aglets", "Elastic waistband"),
            "shorts": ("Flat drawstring with aglets", "Elastic waistband"),
            "fanny pack": ("Clip-release buckle hardware", "YKK zipper main compartment"),
        }
        hardware = hardware_map.get(garment_type.lower(), ("Standard hardware per garment type",))

        # Care instructions
        care = (
            "Machine wash cold, gentle cycle",
            "Tumble dry low or lay flat to dry",
            "Do not bleach",
            "Cool iron if needed — do not iron on embroidery",
            "Do not dry clean",
        )

        # Render requirements
        render_reqs: list[str] = []
        if spec:
            render_reqs.extend(list(spec.texture_keywords[:3]))
        render_reqs.append(f"Color accurate: primary {colorway[0]}, accent {colorway[2]}")
        render_reqs.append("Branding placement must match tech pack specification")
        render_reqs.append("Construction details (seams, ribbing, hardware) visible")

        # QA checklist
        qa_rules = self._qa.get_rules_for_garment(garment_type)
        qa_checklist = tuple(
            f"[{r.category.upper()}] {r.name}: {r.pass_criteria[:80]}" for r in qa_rules[:5]
        )

        return TechPack(
            tech_pack_id=tech_pack_id,
            sku=sku,
            garment_type=garment_type,
            collection=collection,
            season=season,
            product_name=product_name,
            fabric_specification=fabric_spec,
            construction_notes=construction,
            colorway=colorway,
            size_range=sizing_guide.size_range,
            size_chart=size_chart,
            branding_placement=branding,
            hardware_details=hardware,
            care_instructions=care,
            render_requirements=tuple(render_reqs),
            quality_checklist=qa_checklist,
        )
