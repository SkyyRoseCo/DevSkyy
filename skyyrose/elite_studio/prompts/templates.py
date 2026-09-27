"""
Prompt Template Registry — curated templates per creative intent.

Each template defines the structure that produces the best results for that
intent type, with SkyyRose brand DNA baked into every example.
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# SkyyRose brand constants for template injection
# ---------------------------------------------------------------------------

BRAND_NAME = "SkyyRose"
BRAND_TAGLINE = ""
BRAND_FOUNDER = "Corey Foster"
BRAND_LOCATION = "Oakland, California"

COLLECTION_DNA = {
    "black-rose": {
        "name": "Black Rose",
        "aesthetic": "gothic luxury, noir elegance, Oakland nightlife",
        "mood": "dark romance, refined edge, elevated darkness",
        "accent_color": "#C0C0C0 (silver)",
        "font": "SkyyRose Black Rose Script",
        "tagline": "where darkness meets elegance in limited edition form",
    },
    "love-hurts": {
        "name": "Love Hurts",
        "aesthetic": "raw emotion, vulnerability as strength, street passion",
        "mood": "authentic pain transformed into beauty, fire and devotion",
        "accent_color": "#DC143C (crimson)",
        "font": "SkyyRose Love Hurts Graffiti",
        "tagline": "emotional expression through wearable art, bearing the Hurts family legacy",
    },
    "signature": {
        "name": "Signature",
        "aesthetic": "everyday luxury, West Coast prestige, Bay Area pride",
        "mood": "understated confidence, daily elevation, versatile refinement",
        "accent_color": "#D4AF37 (gold)",
        "font": "Pinyon Script",
        "tagline": "refined essentials that form the foundation of elevated everyday wear",
    },
    "kids-capsule": {
        "name": "Kids Capsule",
        "aesthetic": "playful luxury, bold color blocks, next-generation style",
        "mood": "joyful, confident, family-forward",
        "accent_color": "#B76E79 (rose gold)",
        "font": "Grand Hotel",
        "tagline": "little ones deserve luxury too",
    },
}

BRAND_COLORS = {
    "rose_gold": "#B76E79",
    "dark": "#0A0A0A",
    "gold": "#D4AF37",
    "crimson": "#DC143C",
    "silver": "#C0C0C0",
    "charcoal": "#1C1C1C",
    "smoke": "#2D2D2D",
}


@dataclass(frozen=True)
class PromptTemplate:
    """Immutable prompt template for a creative intent."""

    intent: str
    name: str
    template: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    example_output: str


def _build_templates() -> dict[str, PromptTemplate]:
    """Build the complete template registry."""
    return {
        "product-render": PromptTemplate(
            intent="product-render",
            name="Product Imagery Render",
            template=(
                "Generate a {photography_style} product image of the {product_name} "
                "({sku}) from the {collection} collection. "
                "View: {view}. Garment: {garment_type} in {color}. "
                "Fabric: {fabric} with {construction_details}. "
                "Brand elements: {brand_elements}. "
                "Lighting: {lighting}. Background: {background}. "
                "Resolution: {resolution}. Aspect ratio: {aspect_ratio}. "
                "Collection aesthetic: {collection_aesthetic}."
            ),
            required_fields=("sku", "product_name", "collection", "view"),
            optional_fields=(
                "garment_type",
                "color",
                "fabric",
                "construction_details",
                "brand_elements",
                "lighting",
                "background",
                "resolution",
                "aspect_ratio",
                "photography_style",
                "collection_aesthetic",
            ),
            example_output=(
                "Generate an e-commerce product image of the BLACK Rose Hoodie — "
                "Signature Edition (br-005) from the Black Rose collection. "
                "View: front. Garment: hoodie in black. "
                "Fabric: heavyweight french terry with premium embroidered rose detail "
                "and numbered signature tag. "
                "Brand elements: embroidered black rose on chest, SkyyRose logo on sleeve, "
                "rose gold (#B76E79) accent stitching. "
                "Lighting: dramatic directional, cinematic shadows. "
                "Background: deep charcoal gradient (#1C1C1C to #0A0A0A). "
                "Resolution: 4K (2048x2730). Aspect ratio: 3:4. "
                "Collection aesthetic: gothic luxury, noir elegance — "
                "where darkness meets elegance in limited edition form."
            ),
        ),
        "3d-model": PromptTemplate(
            intent="3d-model",
            name="3D Model Generation",
            template=(
                "Generate a production-quality 3D model of the {product_name} ({sku}) "
                "from the {collection} collection. "
                "Garment type: {garment_type}. Primary color: {color}. "
                "Fabric simulation: {fabric} — {drape_notes}. "
                "Output format: {output_format}. Texture resolution: {texture_res}. "
                "PBR materials: {pbr}. "
                "Brand details to preserve: {brand_details}. "
                "Minimum fidelity: 95%."
            ),
            required_fields=("sku", "product_name", "collection"),
            optional_fields=(
                "garment_type",
                "color",
                "fabric",
                "drape_notes",
                "output_format",
                "texture_res",
                "pbr",
                "brand_details",
            ),
            example_output=(
                "Generate a production-quality 3D model of the BLACK Rose Sherpa "
                "Jacket (br-006) from the Black Rose collection. "
                "Garment type: jacket. Primary color: black satin exterior. "
                "Fabric simulation: satin shell with sherpa lining — smooth outer "
                "drape with plush interior volume visible at collar and cuffs. "
                "Output format: GLB. Texture resolution: 2048px. PBR materials: yes. "
                "Brand details to preserve: embroidered rose on back panel, "
                "silver (#C0C0C0) zipper hardware, SkyyRose woven label at neck. "
                "Minimum fidelity: 95%."
            ),
        ),
        "social-pack": PromptTemplate(
            intent="social-pack",
            name="Social Media Content Pack",
            template=(
                "Create a social media content pack for the {product_name} ({sku}) "
                "from the {collection} collection. "
                "Platforms: {platforms}. Content type: {content_type}. "
                "Brand voice: {brand_voice}. "
                "Key selling points: {selling_points}. "
                "Price: ${price}. "
                "Collection mood: {collection_mood}. "
                "Hashtag strategy: {hashtag_notes}. "
                "Call to action: {cta}."
            ),
            required_fields=("sku", "product_name", "collection", "platforms"),
            optional_fields=(
                "content_type",
                "brand_voice",
                "selling_points",
                "price",
                "collection_mood",
                "hashtag_notes",
                "cta",
            ),
            example_output=(
                "Create a social media content pack for the Love Hurts Varsity "
                "Jacket (lh-004) from the Love Hurts collection. "
                "Platforms: Instagram, TikTok, X. Content type: product_launch. "
                "Brand voice: confident without arrogance, Oakland-authentic, "
                "emotionally intelligent. "
                "Key selling points: satin shell, fire-red script, hidden rose "
                "garden embroidered in hood lining, $265 premium positioning. "
                "Price: $265. "
                "Collection mood: raw emotion, vulnerability as strength — "
                "emotional expression through wearable art. "
                "Hashtag strategy: #SkyyRose #LoveHurts #OaklandFashion "
                "#LuxuryStreetWear #VarsityJacket. "
                "Call to action: Pre-order now at skyyrose.co."
            ),
        ),
        "product-copy": PromptTemplate(
            intent="product-copy",
            name="Product Description & SEO Copy",
            template=(
                "Write product copy for the {product_name} ({sku}) from the "
                "{collection} collection. Price: ${price}. "
                "Garment: {garment_type} in {color}. Fabric: {fabric}. "
                "Sizes: {sizes}. {preorder_note} "
                "Collection context: {collection_context}. "
                "Brand voice: {brand_voice}. "
                "Include: short description (2-3 sentences), long description "
                "(paragraph), SEO meta title, meta description, 5 keywords."
            ),
            required_fields=("sku", "product_name", "collection", "price"),
            optional_fields=(
                "garment_type",
                "color",
                "fabric",
                "sizes",
                "preorder_note",
                "collection_context",
                "brand_voice",
            ),
            example_output=(
                "Write product copy for the BLACK Rose Joggers (br-002) from the "
                "Black Rose collection. Price: $50. "
                "Garment: joggers in black. Fabric: french terry. "
                "Sizes: S-3XL. Pre-order — limited to 250 pieces. "
                "Collection context: Gothic luxury, noir elegance — darkness meets "
                "elegance in limited edition form. "
                "Brand voice: confident, Oakland-authentic, emotionally intelligent. "
                "Include: short description (2-3 sentences), long description "
                "(paragraph), SEO meta title, meta description, 5 keywords."
            ),
        ),
        "design-ideation": PromptTemplate(
            intent="design-ideation",
            name="Design Concept Generation",
            template=(
                "Design a new {garment_type} for the {collection} collection, "
                "season {season}. Target retail: ${target_price}. "
                "Aesthetic direction: {aesthetic}. "
                "Fabric: {fabric}. Colorway: {colorway}. "
                "Inspirations: {inspirations}. "
                "Constraints: {constraints}. "
                "Collection DNA: {collection_dna}. "
                "Generate: design description, 3 colorway options, construction "
                "notes, estimated production cost, collection fit analysis."
            ),
            required_fields=("garment_type", "collection", "season"),
            optional_fields=(
                "target_price",
                "aesthetic",
                "fabric",
                "colorway",
                "inspirations",
                "constraints",
                "collection_dna",
            ),
            example_output=(
                "Design a new sherpa jacket for the Black Rose collection, season "
                "FW26. Target retail: $95. "
                "Aesthetic direction: gothic luxury, Oakland nightlife, noir elegance. "
                "Fabric: heavyweight sherpa fleece exterior, satin lining. "
                "Colorway: midnight black (#0A0A0A) with silver (#C0C0C0) hardware. "
                "Inspirations: br-006 Sherpa Jacket, br-005 Signature Edition detailing. "
                "Constraints: edition size 250, unisex sizing S-3XL. "
                "Collection DNA: where darkness meets elegance in limited edition form. "
                "Generate: design description, 3 colorway options, construction "
                "notes, estimated production cost, collection fit analysis."
            ),
        ),
        "mockup": PromptTemplate(
            intent="mockup",
            name="Product Mockup Generation",
            template=(
                "Create a {mockup_type} mockup of a {garment_type} for the "
                "{collection} collection. "
                "Description: {description}. "
                "Colorway: {colorway}. Fabric: {fabric}. "
                "Brand elements: {brand_elements}. "
                "Views: {views}. "
                "Style: {style}."
            ),
            required_fields=("garment_type", "collection", "description"),
            optional_fields=(
                "mockup_type",
                "colorway",
                "fabric",
                "brand_elements",
                "views",
                "style",
            ),
            example_output=(
                "Create a technical flat mockup of a hoodie for the Love Hurts "
                "collection. "
                "Description: oversized pullover hoodie with fire-red graffiti "
                "'Love Hurts' script across chest, hidden rose embroidery in hood. "
                "Colorway: black body, crimson (#DC143C) script. "
                "Fabric: 400gsm french terry. "
                "Brand elements: Love Hurts graffiti drip logo, embroidered rose "
                "in hood lining, SkyyRose woven label. "
                "Views: front, back. "
                "Style: technical flat drawing with construction callouts."
            ),
        ),
        "character-sheet": PromptTemplate(
            intent="character-sheet",
            name="Character Reference Sheet",
            template=(
                "Create a character reference sheet for '{character_name}'. "
                "Style: {style}. "
                "Physical description: {body_description}. "
                "Face: {face_features}. "
                "Default outfit: {outfit}. "
                "Brand elements: {brand_elements}. "
                "Views: front, side, back. "
                "Expression grid: happy, confident, playful, determined, "
                "mysterious, joyful."
            ),
            required_fields=("character_name", "style"),
            optional_fields=(
                "body_description",
                "face_features",
                "outfit",
                "brand_elements",
            ),
            example_output=(
                "Create a character reference sheet for 'Rosie'. "
                "Style: Pixar-quality 3D illustration, chibi proportions. "
                "Physical description: young Black girl, approximately 6 years old, "
                "natural hair in two afro puffs with rose gold (#B76E79) ribbons. "
                "Face: bright expressive eyes, warm smile, small beauty mark. "
                "Default outfit: miniature BLACK Rose Hoodie (br-004) in black "
                "with rose gold embroidered rose, matching joggers, fresh white sneakers. "
                "Brand elements: rose gold accents, SkyyRose logo on hoodie chest, "
                "tiny rose pin on one afro puff. "
                "Views: front, side, back. "
                "Expression grid: happy, confident, playful, determined, "
                "mysterious, joyful."
            ),
        ),
        "scene-composite": PromptTemplate(
            intent="scene-composite",
            name="Scene Composite Direction",
            template=(
                "Composite the {product_name} ({sku}) into a {scene_type} scene. "
                "Collection: {collection}. "
                "Scene: {scene_description}. "
                "Lighting: {lighting}. Time of day: {time_of_day}. "
                "Mood: {mood}. "
                "Model direction: {model_direction}. "
                "Camera: {camera_angle}."
            ),
            required_fields=("sku", "product_name", "collection", "scene_description"),
            optional_fields=(
                "scene_type",
                "lighting",
                "time_of_day",
                "mood",
                "model_direction",
                "camera_angle",
            ),
            example_output=(
                "Composite the Stay Golden Shirt (sg-002) into an editorial "
                "lifestyle scene. Collection: Signature. "
                "Scene: Golden Gate Bridge at golden hour, fog rolling through "
                "cables, warm light catching the gold (#D4AF37) accents on the shirt. "
                "Lighting: natural golden hour, warm directional. "
                "Time of day: sunset. "
                "Mood: West Coast prestige, understated confidence, Bay Area pride. "
                "Model direction: confident stance, looking toward the bridge, "
                "shirt catching the light. "
                "Camera: medium shot, slightly low angle for heroic framing."
            ),
        ),
        "collection-plan": PromptTemplate(
            intent="collection-plan",
            name="Collection Planning",
            template=(
                "Plan a {season} collection for {collection}. "
                "Target pieces: {piece_count}. Price range: ${price_low}-${price_high}. "
                "Aesthetic direction: {aesthetic}. "
                "Must include: {required_pieces}. "
                "Fabric palette: {fabrics}. "
                "Color story: {color_story}. "
                "Delivery cadence: {cadence}. "
                "Generate: line sheet, price architecture, piece breakdown, "
                "collection narrative, merchandising notes."
            ),
            required_fields=("season", "collection"),
            optional_fields=(
                "piece_count",
                "price_low",
                "price_high",
                "aesthetic",
                "required_pieces",
                "fabrics",
                "color_story",
                "cadence",
            ),
            example_output=(
                "Plan a FW26 collection for Black Rose. "
                "Target pieces: 8. Price range: $35-$115. "
                "Aesthetic direction: gothic luxury, noir, Oakland nightlife. "
                "Must include: hoodie, crewneck, joggers, jersey, outerwear. "
                "Fabric palette: french terry, sherpa, mesh, satin. "
                "Color story: midnight black base, silver (#C0C0C0) accents, "
                "rose gold (#B76E79) embroidery thread. "
                "Delivery cadence: core drop September, limited jersey November. "
                "Generate: line sheet, price architecture, piece breakdown, "
                "collection narrative, merchandising notes."
            ),
        ),
        "tech-pack": PromptTemplate(
            intent="tech-pack",
            name="Technical Specification Sheet",
            template=(
                "Generate a tech pack for the {product_name} ({sku}). "
                "Garment type: {garment_type}. "
                "Fabric: {fabric}, weight: {fabric_weight}. "
                "Construction: {construction}. "
                "Sizing: {sizes}. "
                "Colorway: {colorway}. "
                "Branding: {branding}. "
                "Hardware: {hardware}. "
                "Include: measurements table, construction details, "
                "material breakdown, branding placement, packaging specs."
            ),
            required_fields=("sku", "product_name", "garment_type"),
            optional_fields=(
                "fabric",
                "fabric_weight",
                "construction",
                "sizes",
                "colorway",
                "branding",
                "hardware",
            ),
            example_output=(
                "Generate a tech pack for the BLACK Rose Hoodie — Signature "
                "Edition (br-005). "
                "Garment type: pullover hoodie. "
                "Fabric: 380gsm french terry, 80/20 cotton/poly, brushed interior. "
                "Weight: 380gsm. "
                "Construction: double-needle stitching, reinforced kangaroo pocket, "
                "metal grommets on drawstring, ribbed cuffs and hem. "
                "Sizing: S-3XL, unisex relaxed fit. "
                "Colorway: black (#0A0A0A) body, rose gold (#B76E79) embroidery. "
                "Branding: chest embroidered rose (4cm), numbered tag inside collar, "
                "woven neck label, sleeve patch. "
                "Hardware: matte black drawstring tips, rose gold zipper pull on pocket. "
                "Include: measurements table, construction details, "
                "material breakdown, branding placement, packaging specs."
            ),
        ),
        "moodboard": PromptTemplate(
            intent="moodboard",
            name="Mood Board Composition",
            template=(
                "Create a mood board for {subject}. "
                "Collection: {collection}. Season: {season}. "
                "Mood: {mood}. "
                "Color palette: {colors}. "
                "Textures: {textures}. "
                "References: {references}. "
                "Typography: {typography}. "
                "Include: 6-9 reference images, color swatches, "
                "texture samples, typography samples, mood keywords."
            ),
            required_fields=("subject", "collection"),
            optional_fields=(
                "season",
                "mood",
                "colors",
                "textures",
                "references",
                "typography",
            ),
            example_output=(
                "Create a mood board for the FW26 Love Hurts drop. "
                "Collection: Love Hurts. Season: FW26. "
                "Mood: raw emotion, vulnerability as strength, fire and devotion, "
                "Oakland grit meets luxury. "
                "Color palette: deep black (#0A0A0A), crimson (#DC143C), "
                "rose gold (#B76E79), smoke (#2D2D2D). "
                "Textures: distressed satin, fire-scorched edges, velvet rose petals, "
                "graffiti-stained concrete. "
                "References: Gothic cathedrals, Oakland street murals, "
                "Beauty and the Beast enchanted rose, burning love letters. "
                "Typography: Archivo headlines with the SkyyRose Love Hurts Graffiti script for the collection name, hand-drawn graffiti accents. "
                "Include: 6-9 reference images, color swatches, "
                "texture samples, typography samples, mood keywords."
            ),
        ),
        "colorway-explore": PromptTemplate(
            intent="colorway-explore",
            name="Colorway Exploration",
            template=(
                "Explore colorway variations for the {product_name} ({sku}) "
                "from the {collection} collection. "
                "Base design: {base_description}. "
                "Current colorway: {current_colorway}. "
                "Explore: {num_variations} variations. "
                "Direction: {direction}. "
                "Constraints: {constraints}. "
                "Generate: color swatches, mockup per variation, "
                "name for each colorway, production feasibility notes."
            ),
            required_fields=("sku", "product_name", "collection"),
            optional_fields=(
                "base_description",
                "current_colorway",
                "num_variations",
                "direction",
                "constraints",
            ),
            example_output=(
                "Explore colorway variations for the Mint & Lavender Hoodie "
                "(sg-006) from the Signature collection. "
                "Base design: colorblock hoodie with signature rose embroidery. "
                "Current colorway: mint green body, lavender accents. "
                "Explore: 4 variations. "
                "Direction: seasonal palette expansion — keep the pastel DNA "
                "but explore new color pairings for SS27. "
                "Constraints: rose gold (#B76E79) embroidery must remain, "
                "brand label placement unchanged. "
                "Generate: color swatches, mockup per variation, "
                "name for each colorway, production feasibility notes."
            ),
        ),
    }


# Module-level constant — built once, shared across all registry instances
_TEMPLATES: dict[str, PromptTemplate] = _build_templates()


class PromptTemplateRegistry:
    """Registry of curated prompt templates per creative intent."""

    def __init__(self) -> None:
        self._templates = _TEMPLATES

    def get_template(self, intent: str) -> PromptTemplate | None:
        """Return the template for a creative intent, or None if not found."""
        return self._templates.get(intent)

    def list_templates(self) -> list[PromptTemplate]:
        """Return all available templates."""
        return list(self._templates.values())

    def list_intents(self) -> list[str]:
        """Return all registered intent names."""
        return list(self._templates.keys())

    def has_intent(self, intent: str) -> bool:
        """Check if a template exists for the given intent."""
        return intent in self._templates
