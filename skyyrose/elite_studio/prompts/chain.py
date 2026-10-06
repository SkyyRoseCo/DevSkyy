"""
Prompt Chain — multi-step refinement pipeline.

Takes a raw human prompt and runs it through 5 stages:
1. Intent Classification
2. Context Expansion (fill gaps with smart defaults)
3. Domain Injection (fashion-specific knowledge)
4. Brand Injection (SkyyRose DNA)
5. Agent Optimization (format for target agent)
"""

from __future__ import annotations

from datetime import UTC, datetime

from skyyrose.elite_studio.prompts.analyzer import (
    _COLLECTIONS,
    _SKU_PREFIXES,
    PromptAnalyzer,
)
from skyyrose.elite_studio.prompts.templates import (
    BRAND_COLORS,
    BRAND_NAME,
    COLLECTION_DNA,
    PromptTemplateRegistry,
)

# ---------------------------------------------------------------------------
# Season detection from current date
# ---------------------------------------------------------------------------

_MONTH_TO_SEASON = {
    1: "SS",
    2: "SS",
    3: "SS",
    4: "SS",
    5: "SS",
    6: "SS",
    7: "FW",
    8: "FW",
    9: "FW",
    10: "FW",
    11: "FW",
    12: "FW",
}


def _current_season() -> str:
    """Return the current design season (e.g., 'FW26')."""
    now = datetime.now(UTC)
    prefix = _MONTH_TO_SEASON[now.month]
    year = now.year % 100
    return f"{prefix}{year}"


# ---------------------------------------------------------------------------
# Fabric knowledge for domain injection
# ---------------------------------------------------------------------------

_FABRIC_PROPERTIES: dict[str, str] = {
    "sherpa": "plush, textured, heavyweight warmth with visible pile",
    "french terry": "soft interior loops, smooth exterior, mid-weight comfort",
    "fleece": "brushed, insulating, soft hand feel",
    "mesh": "breathable, semi-transparent, athletic drape",
    "satin": "smooth, lustrous surface with fluid drape",
    "jersey knit": "stretchy, soft, comfortable everyday fabric",
    "cotton": "natural fiber, breathable, classic hand feel",
    "denim": "sturdy twill weave, structured, ages beautifully",
    "velvet": "plush pile, rich depth, luxurious texture",
}

_GARMENT_DEFAULTS: dict[str, dict[str, str]] = {
    "hoodie": {
        "fabric": "french terry",
        "construction": "kangaroo pocket, drawstring hood, ribbed cuffs and hem",
        "photography": "on-model, three-quarter view, dramatic lighting",
    },
    "crewneck": {
        "fabric": "french terry",
        "construction": "ribbed collar, cuffs and hem, set-in sleeves",
        "photography": "on-model or flat lay, clean lighting",
    },
    "joggers": {
        "fabric": "french terry",
        "construction": "elastic waist with drawstring, tapered leg, ribbed cuffs",
        "photography": "on-model, full length, movement-focused",
    },
    "jersey": {
        "fabric": "mesh",
        "construction": "sublimation print, v-neck or crew, athletic cut",
        "photography": "on-model, front and back, number visible",
    },
    "jacket": {
        "fabric": "sherpa",
        "construction": "full zip, lined interior, stand collar",
        "photography": "on-model, styled open, texture visible",
    },
    "shorts": {
        "fabric": "mesh",
        "construction": "elastic waist, side pockets, above-knee length",
        "photography": "on-model, active pose, movement",
    },
    "shirt": {
        "fabric": "cotton",
        "construction": "crew neck, relaxed fit, screen or sublimation print",
        "photography": "on-model or flat lay, graphic visible",
    },
    "beanie": {
        "fabric": "knit",
        "construction": "cuffed, fitted, embroidered logo",
        "photography": "on-model headshot, styled with outfit",
    },
}


def _detect_garment_type(text: str) -> str:
    """Detect garment type from text."""
    lower = text.lower()
    for gtype in _GARMENT_DEFAULTS:
        if gtype in lower:
            return gtype
    return "garment"


def _detect_collection_from_sku(text: str) -> str | None:
    """Detect collection from SKU prefix."""
    for prefix, collection in _SKU_PREFIXES.items():
        if prefix in text.lower():
            return collection
    return None


def _detect_collection_from_name(text: str) -> str | None:
    """Detect collection from collection name mention using canonical _COLLECTIONS dict."""
    lower = text.lower()
    for name, slug in _COLLECTIONS.items():
        if name in lower:
            return slug
    return None


class PromptChain:
    """Multi-step prompt refinement pipeline with SkyyRose brand DNA injection."""

    def __init__(self) -> None:
        self._analyzer = PromptAnalyzer()
        self._registry = PromptTemplateRegistry()

    def enhance(
        self,
        prompt: str,
        intent: str | None = None,
        fashion_context: dict | None = None,
        brand_context: dict | None = None,
    ) -> dict:
        """Run the full 5-stage enhancement chain.

        Returns a dict with keys: enhanced, intent, context_added, template_used.
        """
        context_added: list[str] = []

        # Stage 1: Intent Classification — use analysis.missing to drive expansion
        analysis = self._analyzer.analyze(prompt)
        resolved_intent = intent or analysis.intent
        if resolved_intent == "unknown":
            resolved_intent = "product-render"
            context_added.append("defaulted intent to product-render")

        # Pre-compute shared detections (avoid redundant calls across stages)
        garment = _detect_garment_type(prompt)
        collection = _detect_collection_from_sku(prompt) or _detect_collection_from_name(prompt)
        missing_set = frozenset(analysis.missing)

        # Stage 2: Context Expansion
        expanded = self._expand_context(
            prompt, resolved_intent, garment, collection, missing_set, context_added
        )

        # Stage 3: Domain Injection
        domain_enriched = self._inject_domain(expanded, resolved_intent, garment, context_added)

        # Stage 4: Brand Injection
        branded = self._inject_brand(
            domain_enriched,
            resolved_intent,
            collection,
            fashion_context,
            brand_context,
            context_added,
        )

        # Stage 5: Agent Optimization
        optimized = self._optimize_for_agent(branded, resolved_intent, context_added)

        template = self._registry.get_template(resolved_intent)
        template_name = template.name if template else "freeform"

        return {
            "enhanced": optimized,
            "intent": resolved_intent,
            "context_added": context_added,
            "template_used": template_name,
        }

    def _expand_context(
        self,
        prompt: str,
        intent: str,
        garment: str,
        collection: str | None,
        missing: frozenset[str],
        added: list[str],
    ) -> str:
        """Fill gaps with smart defaults using analysis.missing instead of private methods."""
        parts = [prompt.rstrip(".")]

        # Add season if missing (check via analysis.missing keys)
        if any("season" in m for m in missing):
            season = _current_season()
            parts.append(f"Season: {season}")
            added.append(f"added season {season}")

        # Add collection from SKU/name if detectable
        if collection and collection not in prompt.lower().replace("-", " ").replace("_", " "):
            coll_data = COLLECTION_DNA.get(collection, {})
            coll_name = coll_data.get("name", collection)
            parts.append(f"Collection: {coll_name}")
            added.append(f"detected collection {coll_name}")

        # Add garment defaults if garment type detected
        if garment != "garment" and garment in _GARMENT_DEFAULTS:
            defaults = _GARMENT_DEFAULTS[garment]
            if any("fabric" in m for m in missing):
                parts.append(f"Fabric: {defaults['fabric']}")
                added.append(f"added default fabric {defaults['fabric']}")

        # Add resolution default for render intents (not tracked in missing — check raw prompt)
        if intent in ("product-render", "mockup", "scene-composite"):
            lower = prompt.lower()
            has_dims = any(d in lower for d in ("4k", "2k", "1080", "1024", "2048", "resolution"))
            if not has_dims:
                parts.append("Resolution: 4K (2048x2730)")
                added.append("added 4K resolution default")

        return ". ".join(parts) + "."

    def _inject_domain(self, prompt: str, intent: str, garment: str, added: list[str]) -> str:
        """Inject fashion-specific domain knowledge."""
        parts = [prompt.rstrip(".")]

        if garment in _GARMENT_DEFAULTS:
            fabric = _GARMENT_DEFAULTS[garment].get("fabric", "")
            if fabric in _FABRIC_PROPERTIES:
                prop = _FABRIC_PROPERTIES[fabric]
                parts.append(f"Fabric rendering notes: {prop}")
                added.append(f"injected {fabric} rendering properties")

        # Inject photography direction for visual intents
        if intent in ("product-render", "scene-composite", "mockup"):
            if garment in _GARMENT_DEFAULTS:
                photo = _GARMENT_DEFAULTS[garment].get("photography", "")
                if photo:
                    parts.append(f"Photography direction: {photo}")
                    added.append("injected photography direction")

        # Inject construction details for tech-oriented intents
        if intent in ("tech-pack", "design-ideation", "mockup"):
            if garment in _GARMENT_DEFAULTS:
                construction = _GARMENT_DEFAULTS[garment].get("construction", "")
                if construction:
                    parts.append(f"Construction: {construction}")
                    added.append("injected construction details")

        return ". ".join(parts) + "."

    def _inject_brand(
        self,
        prompt: str,
        intent: str,
        collection: str | None,
        fashion_context: dict | None,
        brand_context: dict | None,
        added: list[str],
    ) -> str:
        """Inject SkyyRose brand DNA using pre-computed collection."""
        parts = [prompt.rstrip(".")]

        # Use fashion_context if provided
        if fashion_context and "collection_dna" in fashion_context:
            parts.append(f"Collection DNA: {fashion_context['collection_dna']}")
            added.append("injected collection DNA from fashion context")
        elif collection and collection in COLLECTION_DNA:
            dna = COLLECTION_DNA[collection]
            parts.append(
                f"Collection DNA: {dna['name']} — {dna['aesthetic']}. "
                f"Mood: {dna['mood']}. Accent: {dna['accent_color']}"
            )
            added.append(f"injected {dna['name']} collection DNA")

        # Brand identity injection
        if brand_context:
            brand_note = brand_context.get("brand_note", "")
            if brand_note:
                parts.append(brand_note)
                added.append("injected custom brand context")
        else:
            parts.append(
                f"Brand: {BRAND_NAME} — "
                f"Oakland luxury streetwear. Rose gold accent: {BRAND_COLORS['rose_gold']}"
            )
            added.append("injected SkyyRose brand identity")

        return ". ".join(parts) + "."

    def _optimize_for_agent(self, prompt: str, intent: str, added: list[str]) -> str:
        """Format the prompt for the target agent's strengths."""
        # For image generation intents, ensure the prompt is descriptive and visual
        if intent in ("product-render", "scene-composite", "mockup", "character-sheet"):
            if not prompt.startswith(("Generate", "Create", "Design", "Render")):
                action_map = {
                    "product-render": "Generate a product image:",
                    "scene-composite": "Composite into a scene:",
                    "mockup": "Create a mockup:",
                    "character-sheet": "Create a character reference sheet:",
                }
                prefix = action_map.get(intent, "Generate:")
                prompt = f"{prefix} {prompt}"
                added.append("added action prefix for image agent")

        # For text generation intents, ensure structure
        if intent in ("product-copy", "social-pack"):
            if "include:" not in prompt.lower():
                if intent == "product-copy":
                    prompt += (
                        " Include: short description (2-3 sentences), "
                        "long description (paragraph), SEO meta title, "
                        "meta description, 5 keywords."
                    )
                elif intent == "social-pack":
                    prompt += (
                        " Include: platform-specific caption, hashtag set, "
                        "posting time recommendation, media direction."
                    )
                added.append("added output structure requirements")

        # Ensure prompt ends cleanly
        prompt = prompt.strip()
        if not prompt.endswith("."):
            prompt += "."

        return prompt
