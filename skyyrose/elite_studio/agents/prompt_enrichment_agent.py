"""Rule-based prompt enrichment for SkyyRose Elite Studio imagery pipeline.

Pulls branding_summary verbatim from the canonical catalog so the rendered
prompt always reflects the locked spec rather than the generator's
interpretation of a reference image. Style-conditional photography
instructions (ghost mannequin vs flat lay) are emitted so the downstream
generator receives explicit framing rather than an ambient hint.
"""

from __future__ import annotations

import logging

from skyyrose.elite_studio.catalog import Catalog
from skyyrose.elite_studio.models import EnrichedPrompt

logger = logging.getLogger(__name__)

_COLLECTION_DNA: dict[str, str] = {
    "br": (
        "black-rose collection | East Oakland Deep East industrial canon | "
        "armor not flower — a conviction | concrete is the only soil that matters | "
        "beauty forces through cracks | silver-on-black palette | midnight tones | "
        " | Bay Bridge night seen from Oakland side | "
        "cinematic FOG-style restraint, no warm tones"
    ),
    "lh": (
        "love-hurts collection | gothic cathedral atmosphere | "
        "enchanted rose under glass dome — protected, fragile, kept | "
        "Beauty and the Beast cadence — Cocteau not Disney | "
        "crimson #DC143C accent, deep purple bruises-that-became-wisdom, burgundy | "
        "three generations of Hurts | passionate romantic darkness"
    ),
    "sg": (
        "signature collection | Bay Bridge from the Oakland side — the bridge is Oakland's | "
        "golden hour, gold #D4AF37 accent, neutral palette | "
        "foundation wardrobe, blueprints not basics | gender-neutral by default | "
        "Kith editorial framing, magazine-grid restraint | "
        "the origin chapter — drew the first rose at 4 AM"
    ),
    "kids": (
        "kids-capsule collection | playful vibrant energy | bright optimistic palette | "
        "youthful luxury streetwear | the heir chapter"
    ),
}

_STYLE_MODIFIERS: tuple[str, ...] = (
    "editorial lighting",
    "luxury brand aesthetic",
    "SkyyRose brand DNA",
)

_SPEC_PRIMACY_MARKER = (
    "[SPEC IS AUTHORITATIVE] The branding block below overrides any "
    "competing detail inferred from reference imagery."
)

_GHOST_MANNEQUIN_DIRECTIVES = (
    "ghost mannequin photography",
    "invisible mannequin presentation — garment holds its full three-dimensional shape",
    "hollow man interior visible at neckline and cuffs",
    "no human figure, no visible mannequin form",
    "studio softbox lighting, seamless white backdrop",
)

_FLAT_LAY_DIRECTIVES = (
    "flat lay top-down composition",
    "garment fully laid flat with natural drape preserved",
    "neutral backdrop, even diffused lighting",
)


class PromptEnrichmentAgent:
    """Enrich a vision spec with catalog branding, collection DNA, and style directives."""

    def enrich(self, sku: str, vision_spec: str, style: str = "flat_lay") -> EnrichedPrompt:
        """Return an enriched prompt or a failure result on internal error.

        Style values:
            "ghost_mannequin" → emits ghost-mannequin photography directives.
            "flat_lay" (default) → emits flat-lay directives only.
        """
        try:
            return self._enrich(sku=sku, vision_spec=vision_spec, style=style)
        except Exception as exc:  # noqa: BLE001
            logger.exception("PromptEnrichmentAgent._enrich failed for sku=%s", sku)
            return EnrichedPrompt(success=False, original_spec=vision_spec, error=str(exc))

    def _enrich(self, sku: str, vision_spec: str, style: str) -> EnrichedPrompt:
        catalog = Catalog.load()
        try:
            product = catalog.require(sku)
        except KeyError:
            # Unknown SKU is non-fatal at the prompt layer — style modifiers and
            # vision spec are still emitted so the renderer has something to work
            # with. Branding-block and collection-DNA enrichment are skipped.
            # The 3D pipeline (which DOES hard-fail on missing dossier) is a
            # separate concern, gated upstream.
            product = None

        branding_summary = getattr(product, "branding_summary", "") if product else ""
        product_name = getattr(product, "name", "") if product else ""
        product_name = product_name or sku
        collection = getattr(product, "collection", "") if product else ""

        additions: list[str] = []
        parts: list[str] = [f"[SKU: {sku}]", f"[PRODUCT: {product_name}]"]

        # Spec primacy — must precede any reference-derived content.
        parts.append(_SPEC_PRIMACY_MARKER)
        additions.append("spec_primacy_marker")

        # Branding block — verbatim from catalog so the renderer cannot drift.
        if branding_summary:
            parts.append(f"[BRANDING BLOCK]\n{branding_summary}")
            additions.append("branding_block_from_catalog")

        # Style-conditional photography directives.
        if style == "ghost_mannequin":
            parts.append("[STYLE: ghost_mannequin]")
            parts.extend(_GHOST_MANNEQUIN_DIRECTIVES)
            additions.append("ghost_mannequin_directives")
        else:
            parts.append(f"[STYLE: {style}]")
            parts.extend(_FLAT_LAY_DIRECTIVES)
            additions.append("flat_lay_directives")

        if vision_spec:
            parts.append(f"[VISION SPEC]\n{vision_spec}")

        prefix = sku.split("-")[0].lower()
        dna = _COLLECTION_DNA.get(prefix)
        if dna:
            parts.append(f"[COLLECTION DNA] {dna}")
            additions.append(f"collection_dna:{prefix}")
        if collection:
            additions.append(f"collection:{collection}")

        for modifier in _STYLE_MODIFIERS:
            parts.append(modifier)
            additions.append(f"style_modifier:{modifier}")

        enriched = " | ".join(parts)

        return EnrichedPrompt(
            success=True,
            original_spec=vision_spec,
            enriched_spec=enriched,
            additions=tuple(additions),
        )
