"""
Fashion ontology for SkyyRose Elite Studio.

Defines garment types, fabric properties, and the FashionKnowledgeBase
that ties them together. All objects are frozen (immutable).

""
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Brand constants (canonical — mirrors templates.py)
# ---------------------------------------------------------------------------

BRAND_TAGLINE = ""
BRAND_NAME = "SkyyRose"

# ---------------------------------------------------------------------------
# Frozen domain objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GarmentType:
    """Immutable descriptor for a single garment category."""

    name: str
    category: str  # tops, bottoms, outerwear, accessories, sets
    default_fabric: str
    construction_notes: str
    photography_style: str  # recommended photography approach
    sizing_notes: str


@dataclass(frozen=True)
class FabricProperties:
    """Immutable descriptor for a fabric's visual and physical traits."""

    name: str
    weight_range: str  # e.g. "280-380gsm"
    drape: str  # how the fabric falls and moves
    texture: str  # visual surface description
    rendering_notes: str  # AI rendering tips
    season_affinity: tuple[str, ...]  # ("FW",) or ("SS", "FW")


# ---------------------------------------------------------------------------
# Catalogue data
# ---------------------------------------------------------------------------

_GARMENT_CATALOGUE: tuple[GarmentType, ...] = (
    GarmentType(
        name="hoodie",
        category="tops",
        default_fabric="french terry",
        construction_notes=(
            "pullover or zip-up, kangaroo pocket, ribbed cuffs and hem, "
            "drawstring hood with metal grommets"
        ),
        photography_style=(
            "front + back flat lay or on-model half-body; "
            "hood down for front, hood up option for lifestyle"
        ),
        sizing_notes="S-3XL unisex relaxed fit; measure chest and body length",
    ),
    GarmentType(
        name="crewneck",
        category="tops",
        default_fabric="french terry",
        construction_notes=(
            "ribbed crew neck, ribbed cuffs and hem, double-needle stitching throughout"
        ),
        photography_style=(
            "front + back flat lay on clean background; on-model chest-up for lifestyle"
        ),
        sizing_notes="S-3XL unisex relaxed fit; chest + shoulder measurement key",
    ),
    GarmentType(
        name="jersey",
        category="tops",
        default_fabric="mesh",
        construction_notes=(
            "athletic-cut, number and lettering detail, sublimation or embroidery, "
            "side vents, self-fabric neck binding"
        ),
        photography_style=(
            "flat lay front + back to capture number detail; "
            "on-model mid-length shot for lifestyle; "
            "close-up on number/lettering for detail shots"
        ),
        sizing_notes="S-3XL unisex athletic fit; measure chest and body length",
    ),
    GarmentType(
        name="joggers",
        category="bottoms",
        default_fabric="french terry",
        construction_notes=(
            "elastic waistband with drawstring, tapered leg, ribbed ankle cuffs, side pockets"
        ),
        photography_style=(
            "flat lay front + back; on-model full-length for fit reference; waistband detail shot"
        ),
        sizing_notes="S-3XL unisex relaxed through thigh, tapered at ankle",
    ),
    GarmentType(
        name="sweatpants",
        category="bottoms",
        default_fabric="french terry",
        construction_notes=(
            "elastic waistband with drawstring, relaxed leg, "
            "ribbed ankle cuffs, side and back pockets"
        ),
        photography_style=(
            "flat lay front + back; on-model full-length; waistband and pocket detail"
        ),
        sizing_notes="S-3XL unisex relaxed fit throughout",
    ),
    GarmentType(
        name="shorts",
        category="bottoms",
        default_fabric="mesh",
        construction_notes=(
            "elastic waistband with drawstring, side pockets, "
            "inseam 7-9 inches, moisture-wicking lining optional"
        ),
        photography_style=(
            "flat lay front + back; on-model half-body for length reference; "
            "waistband and print detail shots"
        ),
        sizing_notes="S-3XL unisex athletic fit; waist and inseam critical",
    ),
    GarmentType(
        name="shirt",
        category="tops",
        default_fabric="cotton",
        construction_notes=(
            "crew or v-neck, short or long sleeve, "
            "taped seams for premium finish, heat-transfer or screen print graphics"
        ),
        photography_style=("front + back flat lay; on-model chest-up; graphic detail close-up"),
        sizing_notes="XS-2XL unisex regular fit; chest measurement primary",
    ),
    GarmentType(
        name="jacket",
        category="outerwear",
        default_fabric="sherpa",
        construction_notes=(
            "full-zip or snap closure, pockets, "
            "lining visible at collar and cuffs, embroidered or patch branding"
        ),
        photography_style=(
            "on-model 3/4 length shot, open and closed; "
            "flat lay for lining detail; "
            "collar and cuff detail shots"
        ),
        sizing_notes="S-3XL unisex; layer-friendly fit; chest and sleeve length key",
    ),
    GarmentType(
        name="varsity jacket",
        category="outerwear",
        default_fabric="satin",
        construction_notes=(
            "satin shell with wool-look sleeves or matching satin, "
            "snap or zip closure, ribbed collar/cuffs/hem, "
            "embroidered chenille lettering"
        ),
        photography_style=(
            "on-model full-body editorial; flat lay showing both sides; "
            "lettering and patch detail shots; "
            "sleeve and collar close-ups"
        ),
        sizing_notes="S-3XL; oversized styling recommended; chest + sleeve measurement",
    ),
    GarmentType(
        name="beanie",
        category="accessories",
        default_fabric="knit",
        construction_notes=(
            "double-layer rib knit, folded cuff, embroidered patch or woven label branding"
        ),
        photography_style=(
            "on-head 3/4 angle; flat lay showing inner label; embroidery detail close-up"
        ),
        sizing_notes="One Size; one-size-fits-most ribbed stretch",
    ),
    GarmentType(
        name="fanny pack",
        category="accessories",
        default_fabric="nylon",
        construction_notes=(
            "zippered main compartment, adjustable belt strap, "
            "embroidered branding, hardware clip closure"
        ),
        photography_style=(
            "flat lay on clean surface front + back; "
            "worn model shot for scale; "
            "zipper and embroidery detail"
        ),
        sizing_notes="One Size; adjustable strap fits waist 26-46 inches",
    ),
    GarmentType(
        name="set",
        category="sets",
        default_fabric="fleece",
        construction_notes=(
            "matching hoodie and jogger or shorts, "
            "coordinated branding placement, "
            "color-blocked or tonal design"
        ),
        photography_style=(
            "on-model full-body showing complete set; "
            "flat lay of both pieces; "
            "individual piece detail shots"
        ),
        sizing_notes="Kids 2T-7 or adult S-3XL; size chart per component",
    ),
)

_FABRIC_CATALOGUE: tuple[FabricProperties, ...] = (
    FabricProperties(
        name="french terry",
        weight_range="280-400gsm",
        drape="structured with soft hand-feel, holds shape well, slight body",
        texture=(
            "smooth face, looped pile on reverse; "
            "subtle surface variation visible under directional lighting"
        ),
        rendering_notes=(
            "render with soft matte surface sheen; visible ribbing at cuffs and hem; "
            "weight and structure should read as premium knit, not thin jersey"
        ),
        season_affinity=("FW", "SS"),
    ),
    FabricProperties(
        name="sherpa",
        weight_range="400-600gsm",
        drape="voluminous, low drape, holds lofted shape",
        texture="dense visible pile, cloud-like surface, deep shadow between fibers",
        rendering_notes=(
            "CRITICAL: render visible pile texture — individual fiber clusters must be apparent; "
            "avoid flat or smooth appearance; "
            "pile casts micro-shadows creating depth; "
            "collar and cuff edges show pile profile"
        ),
        season_affinity=("FW",),
    ),
    FabricProperties(
        name="mesh",
        weight_range="100-180gsm",
        drape="minimal drape, slight stiffness, athletic structure",
        texture="open-weave grid pattern; semi-transparent; visible underlayer",
        rendering_notes=(
            "render open-hole grid pattern clearly visible; "
            "slight sheen on synthetic mesh; "
            "grid scale varies — standard athletic mesh is 2-4mm openings; "
            "avoid solid flat color — texture is key"
        ),
        season_affinity=("SS", "FW"),
    ),
    FabricProperties(
        name="satin",
        weight_range="80-150gsm",
        drape="fluid, high drape, luxurious movement",
        texture="high-gloss face with matte reverse; catches and reflects light dramatically",
        rendering_notes=(
            "render high-gloss specular highlights on face; "
            "matte reverse visible at rolled edges and interior; "
            "fluid wrinkle folds with sharp highlight ridges; "
            "color appears darker in shadow, brighter at peaks"
        ),
        season_affinity=("FW", "SS"),
    ),
    FabricProperties(
        name="jersey knit",
        weight_range="150-220gsm",
        drape="soft drape, excellent stretch and recovery",
        texture="fine single-jersey face, smooth and uniform; slight sheen on synthetic",
        rendering_notes=(
            "render fine smooth texture with subtle horizontal rib structure; "
            "soft drape wrinkles at natural fold points; "
            "avoid over-texturing — cleaner than fleece or terry"
        ),
        season_affinity=("SS", "FW"),
    ),
    FabricProperties(
        name="cotton",
        weight_range="140-200gsm",
        drape="moderate drape, relaxed hand-feel",
        texture="flat woven or jersey; matte surface; slight natural fiber variation",
        rendering_notes=(
            "render matte surface without specular highlights; "
            "natural drape wrinkles; "
            "slight texture variation vs synthetic — adds premium feel"
        ),
        season_affinity=("SS", "FW"),
    ),
    FabricProperties(
        name="fleece",
        weight_range="200-400gsm",
        drape="light loft, moderate drape, structured",
        texture="brushed surface with visible nap; soft pile less dense than sherpa",
        rendering_notes=(
            "render soft brushed nap texture; "
            "lighter and less structured than sherpa; "
            "color appears slightly desaturated due to surface fuzz; "
            "visible at seam edges and folds"
        ),
        season_affinity=("FW",),
    ),
    FabricProperties(
        name="knit",
        weight_range="180-280gsm",
        drape="stretchy, moderate drape, rib structure visible",
        texture="interlocked loop structure; visible wale ribs on ribbed sections",
        rendering_notes=(
            "render distinct rib wale structure on cuffs and hem; "
            "body may be smoother single-jersey texture; "
            "slight stretch distortion at worn areas"
        ),
        season_affinity=("FW", "SS"),
    ),
    FabricProperties(
        name="nylon",
        weight_range="80-140gsm",
        drape="stiff to moderate drape, dimensional stability",
        texture="smooth to slight weave visible; slight sheen; crisp edges",
        rendering_notes=(
            "render with slight synthetic sheen; "
            "crisp flat panels; "
            "stitching and zipper hardware are prominent detail elements; "
            "avoid fabric wrinkles — nylon holds shape"
        ),
        season_affinity=("SS", "FW"),
    ),
)

# Lookup maps
_GARMENT_MAP: dict[str, GarmentType] = {g.name: g for g in _GARMENT_CATALOGUE}
_FABRIC_MAP: dict[str, FabricProperties] = {f.name: f for f in _FABRIC_CATALOGUE}

# Default fabric assignments per garment type
_DEFAULT_FABRIC_MAP: dict[str, str] = {
    "hoodie": "french terry",
    "crewneck": "french terry",
    "jersey": "mesh",
    "joggers": "french terry",
    "sweatpants": "french terry",
    "shorts": "mesh",
    "shirt": "cotton",
    "jacket": "sherpa",
    "varsity jacket": "satin",
    "beanie": "knit",
    "fanny pack": "nylon",
    "set": "fleece",
}


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------


class FashionKnowledgeBase:
    """Authoritative fashion domain knowledge for SkyyRose products.

    All data is static — instantiation is lightweight and safe to cache.
    """

    def get_garment(self, name: str) -> GarmentType | None:
        """Return garment type by name (case-insensitive), or None if unknown."""
        return _GARMENT_MAP.get(name.lower())

    def get_fabric(self, name: str) -> FabricProperties | None:
        """Return fabric properties by name (case-insensitive), or None if unknown."""
        return _FABRIC_MAP.get(name.lower())

    def get_default_fabric_for_garment(self, garment: str) -> str:
        """Return the default fabric name for a garment type.

        Falls back to 'cotton' for unknown garment types.
        """
        return _DEFAULT_FABRIC_MAP.get(garment.lower(), "cotton")

    def list_garments(self) -> list[GarmentType]:
        """Return all registered garment types."""
        return list(_GARMENT_CATALOGUE)

    def list_fabrics(self) -> list[FabricProperties]:
        """Return all registered fabric types."""
        return list(_FABRIC_CATALOGUE)

    def garment_names(self) -> list[str]:
        """Return all registered garment names."""
        return list(_GARMENT_MAP.keys())

    def fabric_names(self) -> list[str]:
        """Return all registered fabric names."""
        return list(_FABRIC_MAP.keys())
