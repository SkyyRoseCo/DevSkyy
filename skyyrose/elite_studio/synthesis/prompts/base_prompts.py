"""Stage 1 prompts — clean garment, NO decoration.

The Stage 1 FLUX Kontext call must produce a clean garment shape with the
correct silhouette, fabric, and colorway — but NO decoration anywhere.
Decoration is applied separately in Stage 3 via masked inpainting.

This is the structural separation that prevents decoration drift: Stage 1
can't render decoration on a cuff if no decoration is described.
"""

from __future__ import annotations

import json

_VIEW_DIRECTION: dict[str, str] = {
    "front": (
        "Camera positioned DIRECTLY IN FRONT of the garment. "
        "Show the front panel, chest area, and any front construction details (zipper, front pockets, front collar). "
        "The back of the garment must NOT be visible."
    ),
    "back": (
        "Camera positioned DIRECTLY BEHIND the garment, showing the REAR panel ONLY. "
        "Show the back body, back of hood/collar, and rear construction. "
        "Do NOT show the front zipper, front chest panel, front pockets, or any front-facing element — "
        "those elements must be completely hidden by the rear of the garment."
    ),
}


def build_base_prompt(dossier: dict, *, view: str = "front") -> str:
    """Construct the Stage 1 (base render) prompt from a dossier.

    Deliberately omits the ``branding_block``. Includes garment_type_lock,
    fabric / colorway language extracted from the lock, a view direction
    instruction, a hard instruction to render no decoration, and the dossier
    NEGATIVE block as a structural prohibition so FLUX Kontext never generates
    garment features (e.g. front pockets) the product physically lacks.

    Args:
        dossier: parsed dossier dict with keys ``name``, ``garment_type_lock``,
            and optionally ``negative_block``.
        view: "front" or "back" — controls camera position sentence.

    Returns:
        Prompt string ready to pass to FLUX Kontext Pro.
    """
    name = dossier.get("name", "garment")
    lock = dossier.get("garment_type_lock", "")
    negative_block = dossier.get("negative_block", "").strip()
    view_direction = _VIEW_DIRECTION.get(view, _VIEW_DIRECTION["front"])

    negative_section = ""
    if negative_block:
        negative_section = (
            f"\n\nGARMENT STRUCTURAL PROHIBITIONS — these features are PHYSICALLY ABSENT "
            f"from this product and must NOT appear in the render under any circumstances:\n"
            f"{negative_block}"
        )

    return (
        f"Professional luxury fashion product render of a {name}. "
        f"GARMENT SPECIFICATION: {lock}\n\n"
        f"VIEW: {view_direction}\n\n"
        f"Render a clean, undecorated version of this garment — the correct "
        f"silhouette, fabric, color, and construction details (collar, cuffs, "
        f"seams, ribbing, drawstrings, zippers) but with NO logos, "
        f"NO embroidery, NO patches, NO printed graphics, NO emblems, "
        f"NO chest decoration, NO sleeve decoration, NO back decoration. "
        f"The garment surface must be entirely undecorated."
        f"{negative_section}\n\n"
        "PRODUCT CORRECTIONS (preserve authority; decoration is applied in the later stage):\n"
        f"{json.dumps(dossier.get('product_corrections', []), ensure_ascii=False)}\n\n"
        f"Output: pure white background, soft directional studio lighting, "
        f"hyper-realistic, true-to-fabric texture, ghost-mannequin product "
        f"photography style, sharp focus on fabric weave and construction."
    )
