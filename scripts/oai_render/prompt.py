"""Prompt construction — the fixed, identical render procedure + per-SKU spec.

Every product uses the SAME procedure text so renders are visually consistent.
Per-SKU specificity comes from the product dossier (authored from the real
garment), which is injected verbatim — the same contract the prior pipeline
used ("the pipeline reads this file verbatim into the prompt").
"""

from __future__ import annotations

import functools
import json
import logging
import re
from pathlib import Path

from skyyrose.core.dossier_loader import DOSSIERS_DIR, load_dossier
from skyyrose.elite_studio.logo_registry import LogoRegistry

from . import config

log = logging.getLogger(__name__)

# ── Injection hygiene ────────────────────────────────────────────────────────
# Free text injected into the prompt (dossier bodies, CSV name field) can carry
# phrases the image model reads as COMPOSITION instructions. View-enumeration
# language ("front view, back view, detail view") is the confirmed trigger for
# multi-panel collage outputs; availability/styling language causes split
# palettes and phantom garments. Lines containing any of these are dropped from
# injected text (the pipeline's own PRESENTATION/VIEW directives are authored
# separately and never pass through this filter).
_BLOCKED_INJECTION_PATTERNS = (
    r"\bmultiple\s+(?:views?|angles?|panels?)\b",
    r"\breference\s+sheet\b",
    r"\b(?:shown|seen|viewed|photographed)\s+from\b",
    r"\bviews?\s+(?:of|from)\b",
    r"\bangles?\s*:",
    r"\b(?:available|comes)\s+in\b",
    r"\balso\s+available\b",
    r"\b(?:styled|paired|worn)\s+with\b",
    r"\bsplit[- ]screen\b",
    r"\bcollage\b",
    r"\bgrid\s+of\b",
)
_BLOCKED_INJECTION_RE = re.compile("|".join(_BLOCKED_INJECTION_PATTERNS), re.IGNORECASE)

# View-noun mentions are dangerous only when ENUMERATED ("front view, back view,
# detail view" → collage trigger). A single positional mention ("graphic sits on
# the LEFT thigh of the front view only") is legitimate placement spec and must
# survive — dropping it would itself cause drift. NOTE: "colorway" is deliberately
# NOT blocked: dossiers use it as a construction fact; availability language
# ("available in", "comes in") is the actual split-palette trigger and is blocked
# above.
_VIEW_MENTION_RE = re.compile(
    r"\b(?:front|back|side|rear|detail|three-quarter|3/4)[- ]views?\b", re.IGNORECASE
)
_MAX_VIEW_MENTIONS_PER_LINE = 1

# Safety-net ceiling on injected dossier text. Founder dossiers must inject
# WHOLE (truncation = fidelity regression); the largest real dossier is ~8.6k
# chars post-strip, so this only bounds a runaway/corrupted file.
MAX_DOSSIER_CHARS = 12000


def sanitize_injected_text(text: str, *, source: str) -> str:
    """Drop lines carrying composition/availability trigger phrases from injected text.

    Markdown headings are kept (they structure the spec); any other line that
    matches a blocked pattern is removed and logged so dossier authors can fix
    the source. This runs ON TOP of the Scene-direction strip — it is the
    general guard for trigger language anywhere in injected free text.
    """
    kept: list[str] = []
    for line in text.splitlines():
        if not line.lstrip().startswith("#") and (
            _BLOCKED_INJECTION_RE.search(line)
            or len(_VIEW_MENTION_RE.findall(line)) > _MAX_VIEW_MENTIONS_PER_LINE
        ):
            log.warning("Sanitized injected line from %s: %r", source, line.strip()[:96])
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def sanitize_name(name: str) -> str:
    """Clean a CSV product name for prompt injection: one line, no trigger phrases."""
    flat = " ".join(name.split())
    return _BLOCKED_INJECTION_RE.sub("", flat).strip(" -—·")[:120] or flat[:120]


# Presentation styles — view-agnostic; the VIEW directive sets front/back.
PRESENTATIONS = {
    "ghost": (
        "PRESENTATION: clean GHOST-MANNEQUIN / invisible-form — the garment is filled out into "
        "its full three-dimensional WORN shape: shoulders, chest, sleeves, and hem holding real "
        "volume as if on an invisible body, photographed standing in the round with NO visible "
        "person, hanger, or mannequin. The garment MUST read as dimensional and worn — natural "
        "drape, soft interior shadow inside the neckline and sleeves, fabric falling under "
        "gravity. This is NOT a flatlay, NOT a top-down shot, NOT a garment laid flat, NOT a flat "
        "technical drawing. RE-POSE any flat or laid-flat reference into this standing 3D form — "
        "the reference images define the garment's GRAPHICS, COLOUR, and CONSTRUCTION ONLY, never "
        "its flatness or layout. Exactly ONE garment — never a flat multi-panel technical diagram "
        "or multiple views in one frame."
    ),
    "on-model": (
        "PRESENTATION: worn by a single full-body fashion model, natural confident pose, neutral "
        "expression, professional styling. Exactly ONE garment / one look — never a flat diagram "
        "or multiple views in one frame."
    ),
    "flatlay": (
        "PRESENTATION: the single garment laid flat, top-down, neatly arranged on a seamless "
        "surface. Exactly ONE garment — never a multi-panel technical diagram."
    ),
}
DEFAULT_STYLE = "ghost"

# Ghost + flatlay → clean product-card backdrop (these feed the product cards).
GHOST_BACKGROUND = (
    "BACKGROUND: seamless, uncluttered neutral light-grey studio backdrop — no props, no text, no "
    "scene, no logos other than those physically on the garment. Clean product-card aesthetic."
)

# On-model only → collection-specific scene/environment (founder-directed brand atmosphere).
COLLECTION_SCENES = {
    "black-rose": (
        "the Bay Bridge silhouetted behind, shot from the Oakland shore at blue hour, framed by a "
        "moody black-rose garden — dark romantic luxury, dramatic low light, roses in deep shadow"
    ),
    "love-hurts": (
        "a darkly romantic Beauty-and-the-Beast setting seen from the Beast's point of view — a "
        "candlelit gothic château interior, ornate and brooding, shadow-heavy, emotionally intense"
    ),
    "signature": (
        "the Golden Gate Bridge and Bay Area skyline at golden hour — confident West-Coast "
        "street-luxury energy, warm sunlight, effortless swag"
    ),
    "kids-capsule": (
        "a regal throne room, 'the heir to the throne' — opulent gold-and-velvet palace setting, "
        "playful young-royalty grandeur, warm cinematic light"
    ),
}


class SceneError(ValueError):
    """Raised when an on-model render has no defined collection scene (no generic fallback)."""


def _background_for(style: str, collection: str) -> str:
    """Ghost/flatlay → clean studio; on-model → collection-specific scene (no generic fallback)."""
    if style == "on-model":
        scene = COLLECTION_SCENES.get(collection)
        if not scene:
            raise SceneError(
                f"No on-model scene for collection {collection!r}; refusing a generic fallback. "
                f"Add it to COLLECTION_SCENES. Known: {sorted(COLLECTION_SCENES)}"
            )
        return (
            f"BACKGROUND / SCENE: {scene}. The model is photographed within this environment; keep "
            "the garment sharp, correctly lit, and fully unobstructed — the scene is atmosphere, "
            "never covering or recoloring the product."
        )
    return GHOST_BACKGROUND


# Which face of the garment to render; the opposite tech flat is construction-only.
_VIEW_DIRECTIVES = {
    "front": (
        "VIEW: render the FRONT of the garment, front-facing. Any BACK tech-flat reference is "
        "construction-only — do NOT render a back view or a second panel; output a single FRONT view."
    ),
    "back": (
        "VIEW: render the BACK of the garment, rear-facing — camera positioned directly behind "
        "the garment, centered. Use the BACK tech-flat reference as the authority for everything "
        "on the back panel. Do NOT mirror or replicate the front [the back has its own distinct "
        "layout — render that layout]. Any FRONT tech-flat reference is construction-only — do "
        "NOT render a front view or a second panel; output a single BACK view."
    ),
}

# Base procedure applied to EVERY SKU; placeholders filled per style/view/collection.
_BASE_PROCEDURE = (
    "Produce a single, photorealistic luxury e-commerce product photograph of ONE garment.\n"
    "FRAMING: vertical 4:5 portrait, garment centered, full garment in frame with even margins.\n"
    "{presentation}\n"
    "{view_directive}\n"
    "LIGHTING: soft, even studio light, gentle directional key, subtle natural drop shadow.\n"
    "{background}\n"
    "FIDELITY: reproduce the garment EXACTLY as shown in the reference images — silhouette, "
    "fabric, color, every graphic, logo, embroidery, label, and sport patch in its exact position "
    "and size. Do NOT invent, omit, resize, recolor, duplicate, or reposition any element.\n"
    "MATERIAL: render the true surface texture named in the spec — satin must read glossy and "
    "light-catching, sherpa must show visible pile, nylon must look smooth and technical, fleece "
    "must look soft and matte. A garment rendered in the wrong material is an invalid result.\n"
    "PHOTOREALISM: some references are FLAT vector technical drawings (tech flats). They define "
    "construction and graphics ONLY — the output must be a fully photorealistic photograph of the "
    "real manufactured garment: dimensional fabric with natural drape, real seams, real texture, "
    "true studio lighting. A flat, illustrated, or vector-styled output is an invalid result.\n"
    "CONSISTENCY: identical catalog styling across every product in the same presentation style."
)

NEGATIVE_GUARDRAILS = (
    "DO NOT add text, watermarks, mockup labels, size tags, price tags, multiple garments, "
    "collage panels, or any branding not physically present on the garment. DO NOT crop out any "
    "part of the garment or its graphics.\n"
    "BRANDING IS EXHAUSTIVE: the references and spec show EVERY logo and graphic this garment "
    "carries. If a panel (for example the back) shows no logo in its reference, render that panel "
    "with NO logo — a blank panel is correct; an added logo is an invalid result.\n"
    "OUTPUT FORMAT: one single full-bleed photograph [the entire frame is ONE continuous "
    "photo]. No reference sheet. No multiple panels. No collage. No grid. No split-screen."
)

# Paired looks intentionally show TWO garments — forbid EXTRA garments, not "multiple".
PAIR_NEGATIVE_GUARDRAILS = (
    "DO NOT add text, watermarks, mockup labels, size tags, price tags, collage panels, any extra "
    "garments beyond the two specified, or any branding not physically present on the garments. DO "
    "NOT crop out any part of either garment or its graphics, and do NOT merge the two garments.\n"
    "BRANDING IS EXHAUSTIVE: the references and specs show EVERY logo and graphic these garments "
    "carry — render no logo that is not in them; a blank panel is correct when its reference is "
    "blank.\n"
    "OUTPUT FORMAT: one single full-bleed photograph of one model [the entire frame is ONE "
    "continuous photo]. No reference sheet. No multiple panels. No collage. No grid. No "
    "split-screen."
)


def _strip_frontmatter_and_comments(text: str) -> str:
    """Return the dossier body: drop YAML frontmatter and HTML authoring comments."""
    body = text
    if body.startswith("---"):
        end = body.find("---", 3)
        if end != -1:
            body = body[end + 3 :]
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)  # remove HTML comments
    # Strip the "## Scene direction" section. Pose / view / setting is owned by the pipeline
    # (PRESENTATION + VIEW + scene); multi-view pose text here is the CONFIRMED cause of
    # multi-panel renders (it lands under the authoritative spec header and outranks the
    # later override). Remove from the heading to the next "## " heading or end of body.
    body = re.sub(
        r"(?:^|\n)##\s+Scene\s+direction\b.*?(?=\n##\s|\Z)",
        "",
        body,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return body.strip()


def read_dossier(dossier_path: Path | None) -> str | None:
    """Read a dossier markdown file and return its sanitized prose body, or None.

    Sanitization order: frontmatter/comments strip → Scene-direction strip →
    blocked-phrase line filter → length cap. Only construction/material prose
    survives into the prompt.
    """
    if dossier_path is None:
        return None
    if dossier_path.parent.resolve() == DOSSIERS_DIR.resolve():
        # Canonical paths are logical identifiers; mirrors may be stale or absent.
        raw = load_dossier(dossier_path.stem).raw
    else:
        try:
            raw = dossier_path.read_text(encoding="utf-8")
        except OSError:
            return None
    body = _strip_frontmatter_and_comments(raw)
    if not body:
        return None
    body = sanitize_injected_text(body, source=dossier_path.name)
    if len(body) > MAX_DOSSIER_CHARS:
        log.warning(
            "Dossier %s truncated %d → %d chars for prompt injection",
            dossier_path.name,
            len(body),
            MAX_DOSSIER_CHARS,
        )
        body = body[:MAX_DOSSIER_CHARS].rsplit("\n", 1)[0]
    return body or None


_VIEW_SECTION_HEADER = {"front": "### Front", "back": "### Back"}


def extract_view_branding(dossier_text: str | None, view: str) -> str:
    """Return the dossier's branding bullets for one view ("front"/"back"), or "".

    Feeds the QC judge per-view ground truth so a deliberately blank panel
    (e.g. "back-body: no decoration") is not failed for "missing branding".
    The text is repo-controlled dossier markdown, not user input.
    """
    if not dossier_text:
        return ""
    header = _VIEW_SECTION_HEADER.get(view)
    if header is None:
        return ""
    idx = dossier_text.find(header)
    if idx == -1:
        return ""
    section = dossier_text[idx + len(header) :]
    cuts = [c for c in (section.find("\n### "), section.find("\n## ")) if c != -1]
    if cuts:
        section = section[: min(cuts)]
    return section.strip()


@functools.lru_cache(maxsize=1)
def _load_corrections_file(path_str: str) -> dict[str, list[str]]:
    """Load the founder corrections JSON (sku → verbatim correction lines)."""
    path = Path(path_str)
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        raw = doc.get("corrections", {})
        return {
            sku: [str(line) for line in lines]
            for sku, lines in raw.items()
            if isinstance(lines, list)
        }
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("Could not load corrections file %s: %s", path, exc)
        return {}


def corrections_for(sku: str) -> list[str]:
    """Founder's verbatim review corrections for a SKU (empty when none).

    Lines are prefixed ``[view]`` mechanically; the words after the prefix are
    the founder's own, written while rejecting a prior render of this product.
    """
    return _load_corrections_file(str(config.CORRECTIONS_JSON)).get(sku, [])


def _corrections_block(sku: str) -> list[str]:
    """Prompt lines for the founder-corrections section (empty list when none)."""
    lines = [
        sanitize_injected_text(line, source=f"corrections:{sku}") for line in corrections_for(sku)
    ]
    lines = [ln for ln in lines if ln]
    if not lines:
        return []
    block = [
        "FOUNDER CORRECTIONS — the founder rejected a previous render of THIS exact product "
        "and wrote these notes. They are authoritative and OVERRIDE any conflicting line in "
        "the spec above ([ghost]/[ghost-back]/[on-model] marks which render the note "
        "addresses — [ghost-back] notes govern the BACK of the garment, others the front):"
    ]
    block.extend(f"  - {ln}" for ln in lines)
    block.append("")
    return block


def build_prompt(
    *,
    name: str,
    sku: str,
    collection: str,
    reference_labels: list[str],
    dossier_text: str | None,
    is_patch: bool,
    style: str | None = None,
    view: str = "front",
    scene: dict | None = None,
    style_reference: bool = False,
) -> str:
    """Assemble the full edit prompt for one SKU in the chosen style + view.

    When ``style_reference`` is True, the FINAL reference image is treated as an
    environment/lighting/mood anchor only (e.g. a lookbook frame) — never a source
    of garments, graphics, or text.
    """
    style_key = style or DEFAULT_STYLE
    if style_key not in PRESENTATIONS:
        raise ValueError(f"Unknown style {style_key!r}. Valid: {sorted(PRESENTATIONS)}")
    if view not in _VIEW_DIRECTIVES:
        raise ValueError(f"Unknown view {view!r}. Valid: {sorted(_VIEW_DIRECTIVES)}")
    presentation = PRESENTATIONS[style_key]
    view_directive = _VIEW_DIRECTIVES[view]
    if scene is not None and style_key == "on-model":
        # On-model: the scene JSON carries the founder-approved collection
        # environment, so it is authoritative for environment + lighting + camera.
        background = (
            "OVERRIDE — ENVIRONMENT, LIGHTING, AND CAMERA: the SCENE SPEC (JSON) block "
            "below is the authoritative source for all three. The generic LIGHTING directive "
            "at the top of this prompt is superseded by the 'lighting' object in the SCENE SPEC."
        )
    elif scene is not None:
        # Ghost / flatlay: keep the clean product-card BACKGROUND guardrails
        # (no props, no scene); the scene JSON still drives lighting + camera.
        background = (
            f"{GHOST_BACKGROUND} The SCENE SPEC (JSON) 'lighting' and 'camera' objects below "
            "are authoritative for light and lens; keep this clean product-card background."
        )
    else:
        background = _background_for(style_key, collection)
    parts: list[str] = [
        _BASE_PROCEDURE.format(
            presentation=presentation, view_directive=view_directive, background=background
        ),
        "",
    ]
    parts.append(
        f"PRODUCT: {sanitize_name(name)} (SKU {sku}) — "
        f"{collection.replace('-', ' ').title()} collection."
    )
    parts.append("")

    if scene is not None:
        from .scene_schema import scene_to_prompt_block

        parts.append(scene_to_prompt_block(scene))
        parts.append("")

    if reference_labels:
        parts.append(
            'REFERENCE IMAGES — provided in this exact order; "image 1" is the first '
            'image attached, "image 2" the second, and so on:'
        )
        parts.extend(f"  {label}" for label in reference_labels)
        parts.append("")

    if style_reference:
        parts.append(
            "STYLE & COMPOSITION REFERENCE: the FINAL reference image is an ENVIRONMENT, "
            "LIGHTING, PALETTE, and MOOD anchor ONLY. Match its setting, atmosphere, color "
            "grade, camera feel, and overall composition. Do NOT copy, trace, or borrow any "
            "garment, logo, graphic, text, person, or product from it — every garment comes "
            "SOLELY from the product reference image(s) above and the SCENE SPEC. Treat it as "
            "the mood board for the scene, never as a source of what is worn."
        )
        parts.append("")

    if dossier_text:
        parts.append(
            "EXACT PRODUCT SPEC — CONSTRUCTION AND MATERIALS ONLY (replicate the physical garment "
            "details — fabric, colorway, graphics, logos, patches, labels — precisely; pose, scene, "
            "framing, and layout are governed ONLY by the PRESENTATION and VIEW directives above):"
        )
        parts.append(dossier_text)
        parts.append("")
        parts.append(
            "PRESENTATION OVERRIDE: use the PRESENTATION + VIEW lines at the top for framing/pose; "
            "IGNORE any conflicting pose, setting, or scene direction in the spec above. The spec "
            "governs WHAT is on the garment, not how it is photographed."
        )
        parts.append("")

    parts.extend(_corrections_block(sku))
    parts.append(LogoRegistry.load().prompt_instructions(sku, require_sizing=is_patch))
    parts.append("")

    if is_patch and view == "front":
        parts.append(
            "CRITICAL — SPORT PATCH FIDELITY: this is a sports jersey. The embroidered sport PATCH "
            "shown in the patch reference image MUST be present, sharp, and in its exact placement. "
            "Reproduce EVERY element INSIDE the patch verbatim from the patch close-up — the FULL "
            "patch, top half AND bottom half: all text, numerals, lettering, emblems, and outline. "
            "Render the lower portion of the patch with the same precision as the upper portion. Do "
            "NOT approximate, simplify, blur, truncate, or invent any sub-detail anywhere inside the "
            "patch. A jersey rendered without its patch, or with a hallucinated / incomplete patch "
            "interior, is a rejected, invalid result."
        )
        parts.append("")

    parts.append(NEGATIVE_GUARDRAILS)
    return "\n".join(parts).strip()


# Paired-look base — ONE model wearing TWO coordinating garments (sold separately).
_PAIR_BASE_PROCEDURE = (
    "Produce a single, photorealistic luxury e-commerce fashion photograph: ONE full-body fashion "
    "model, front-facing, natural confident pose, neutral expression, professional styling, wearing "
    "TWO coordinating garments together as a single styled outfit.\n"
    "FRAMING: vertical 4:5 portrait, the model centered, BOTH garments fully visible head-to-hem.\n"
    "COORDINATED LOOK: the model wears BOTH garments at once as one cohesive outfit — the pieces are "
    "sold separately but photographed together. One person, one continuous look. This is NOT a "
    "split-screen, collage, multi-panel, diptych, or side-by-side of separate items.\n"
    "{background}\n"
    "FIDELITY: reproduce EACH garment EXACTLY as shown in its own reference images — silhouette, "
    "fabric, color, every graphic, logo, embroidery, label, and patch in exact position and size. Do "
    "NOT invent, omit, resize, recolor, duplicate, or reposition any element of either garment, and "
    "do NOT blend the two garments into one.\n"
    "CONSISTENCY: identical catalog styling across every paired look in the line."
)


def build_pair_prompt(
    *,
    pair_label: str,
    collection: str,
    garments: list[dict],
    style: str = "on-model",
) -> str:
    """Assemble a paired-look on-model prompt: one model wearing BOTH garments (sold separately).

    ``garments`` is a list of dicts (one per garment), each with: name, sku,
    reference_labels (list[str]), dossier_text (str | None), is_patch (bool).
    Raises SceneError when the collection has no on-model scene (no generic fallback).
    """
    if style != "on-model":
        raise ValueError(f"Paired looks are on-model only; got style {style!r}.")
    background = _background_for("on-model", collection)
    parts: list[str] = [_PAIR_BASE_PROCEDURE.format(background=background), ""]
    parts.append(
        f"PAIRED LOOK: {pair_label} — {collection.replace('-', ' ').title()} collection. "
        "The model wears BOTH of these together:"
    )
    body_zones = ("worn on the upper body/torso", "worn on the lower body/legs")
    for i, g in enumerate(garments):
        zone = f" — {body_zones[i]}" if i < len(body_zones) and len(garments) == 2 else ""
        parts.append(f"  GARMENT {chr(65 + i)} — {sanitize_name(g['name'])} (SKU {g['sku']}){zone}")
    parts.append(
        "BOTH garments MUST be visible on the model simultaneously — a result missing either "
        "garment is invalid."
    )
    parts.append("")

    for i, g in enumerate(garments):
        labels = g.get("reference_labels") or []
        if labels:
            parts.append(f"REFERENCE IMAGES — GARMENT {chr(65 + i)} ({g['name']}):")
            parts.extend(f"  {label}" for label in labels)
            parts.append("")

    for i, g in enumerate(garments):
        if g.get("dossier_text"):
            parts.append(
                f"GARMENT {chr(65 + i)} SPEC — CONSTRUCTION AND MATERIALS ONLY (replicate physical "
                "details precisely; pose/scene/framing governed ONLY by the directives above):"
            )
            parts.append(g["dossier_text"])
            parts.append("")

    parts.append(
        "PRESENTATION OVERRIDE: framing, pose, scene, and layout are governed ONLY by the directives "
        "at the top; IGNORE any pose/scene/view language inside the specs above."
    )
    parts.append("")

    for g in garments:
        parts.extend(_corrections_block(g["sku"]))
        parts.append(
            LogoRegistry.load().prompt_instructions(
                g["sku"], require_sizing=bool(g.get("is_patch"))
            )
        )

    for i, g in enumerate(garments):
        if g.get("is_patch"):
            parts.append(
                f"CRITICAL — GARMENT {chr(65 + i)} is a sports jersey: its embroidered sport PATCH "
                "must be present, sharp, and complete (top AND bottom of the patch), reproduced "
                "verbatim from its patch close-up. Do NOT approximate or omit any sub-detail."
            )
            parts.append("")

    parts.append(PAIR_NEGATIVE_GUARDRAILS)
    return "\n".join(parts).strip()
