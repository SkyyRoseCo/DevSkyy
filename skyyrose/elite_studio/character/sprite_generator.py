"""
Web sprite generation for SkyyRose Elite Studio characters.

Generates structured sprite prompts for web-deployable character animations,
including the canonical 7-pose SkyyRose mascot sprite sheet.

""
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sprite data models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpriteSpec:
    """Immutable specification for a character sprite sheet."""

    character_name: str
    poses: tuple[str, ...]  # e.g. ("walk_1", "walk_2", "idle", "wave", "point")
    style: str  # "2d", "3d-rendered", "illustrated"
    background: str  # "transparent", "white"


@dataclass(frozen=True)
class SpriteResult:
    """Immutable result from sprite prompt generation."""

    success: bool
    character_name: str
    sprite_prompts: dict[str, str]  # pose -> generation prompt
    css_animation_hint: str  # suggested CSS animation approach
    error: str = ""


# ---------------------------------------------------------------------------
# Standard mascot poses
# ---------------------------------------------------------------------------

_MASCOT_POSES = (
    "idle",
    "walk_1",
    "walk_2",
    "wave",
    "point",
    "celebrate",
    "think",
)

_POSE_DIRECTIONS: dict[str, str] = {
    "idle": (
        "neutral standing, weight on one leg, slight hip tilt, "
        "small confident smile, arms relaxed at sides"
    ),
    "walk_1": (
        "walking pose frame 1: right foot forward, left arm forward, "
        "body in mid-stride, slight forward lean"
    ),
    "walk_2": (
        "walking pose frame 2: left foot forward, right arm forward, "
        "body in mid-stride — opposite of walk_1 for looping animation"
    ),
    "wave": (
        "right arm raised and waving, big smile, "
        "left arm relaxed, body slightly angled toward camera"
    ),
    "point": (
        "right arm extended forward pointing, finger pointing toward viewer, "
        "confident expression, slight forward lean"
    ),
    "celebrate": (
        "both arms raised in celebration, slight jump or tippy-toes, "
        "huge grin, eyes bright with joy"
    ),
    "think": (
        "right index finger resting on chin, eyes looking upward-left, "
        "thoughtful expression, slight head tilt"
    ),
}

# CSS animation hints per pose combination
_CSS_HINT_WALK = (
    "CSS: Use walk_1 and walk_2 alternating at 200ms each in a loop for smooth walk cycle. "
    "Use `steps(1)` timing to switch frames crisply."
)

_CSS_HINT_IDLE = (
    "CSS: idle pose can have subtle breathing animation via scale (1.0 → 1.005 → 1.0) "
    "over 2s ease-in-out infinite loop."
)


class SpriteGenerator:
    """Generates sprite sheet prompts for SkyyRose characters.

    Produces generation-ready prompts for each pose in a sprite spec,
    plus CSS animation guidance for web deployment.
    """

    def generate_sprite_prompts(self, spec: SpriteSpec) -> SpriteResult:
        """Generate generation prompts for all poses in a SpriteSpec."""
        try:
            style_instructions = {
                "2d": (
                    "Flat 2D illustration style, clean vector-like art, "
                    "bold outlines, vibrant colors. "
                ),
                "3d-rendered": (
                    "3D rendered character, Pixar/Disney CGI quality, "
                    "subsurface scattering skin, detailed clothing. "
                ),
                "illustrated": (
                    "Professional character illustration, clean line art, "
                    "semi-flat color with subtle shading. "
                ),
            }
            style_prefix = style_instructions.get(spec.style, style_instructions["2d"])
            bg_note = (
                "transparent PNG background"
                if spec.background == "transparent"
                else "clean white background"
            )

            prompts: dict[str, str] = {}
            for pose in spec.poses:
                pose_desc = _POSE_DIRECTIONS.get(pose.lower(), pose)
                prompt = (
                    f"{style_prefix}"
                    f"Character: {spec.character_name}. "
                    f"Full body sprite, {pose} pose: {pose_desc}. "
                    f"{bg_note}. "
                    "Consistent character design — same face, hair, outfit as reference. "
                    "Web sprite quality — clean edges, suitable for animation. "
                    "Exact same scale and anchor point across all poses. "
                    "SkyyRose brand character, ''"
                )
                prompts[pose] = prompt

            # Build CSS hint
            has_walk = "walk_1" in spec.poses and "walk_2" in spec.poses
            has_idle = "idle" in spec.poses
            css_parts: list[str] = []
            if has_walk:
                css_parts.append(_CSS_HINT_WALK)
            if has_idle:
                css_parts.append(_CSS_HINT_IDLE)
            if not css_parts:
                css_parts.append(
                    "CSS: Animate sprite frames using background-position steps. "
                    "Each pose is a separate frame in the sprite strip."
                )
            css_hint = " | ".join(css_parts)

            return SpriteResult(
                success=True,
                character_name=spec.character_name,
                sprite_prompts=prompts,
                css_animation_hint=css_hint,
            )

        except Exception as exc:
            logger.exception("generate_sprite_prompts failed: %s", exc)
            return SpriteResult(
                success=False,
                character_name=spec.character_name,
                sprite_prompts={},
                css_animation_hint="",
                error=str(exc),
            )

    def generate_skyyrose_mascot_sprites(self) -> SpriteResult:
        """Generate sprite prompts for the canonical SkyyRose mascot Rosie.

        Generates all 7 standard mascot poses:
        idle, walk_1, walk_2, wave, point, celebrate, think.

        Returns:
            SpriteResult with all 7 pose prompts and CSS animation guidance.
        """
        spec = SpriteSpec(
            character_name="Rosie",
            poses=_MASCOT_POSES,
            style="3d-rendered",
            background="transparent",
        )

        # Build base result
        base_result = self.generate_sprite_prompts(spec)

        if not base_result.success:
            return base_result

        # Enrich each prompt with Rosie-specific brand details
        rosie_enriched: dict[str, str] = {}
        rosie_identity = (
            "Rosie — SkyyRose mascot: young Black girl (~6 years old), Pixar 3D quality, "
            "natural hair in two afro puffs with rose gold ribbons, "
            "mini BLACK Rose Hoodie (near-black #0A0A0A) with embroidered silver rose, "
            "black joggers, white sneakers with rose gold tips. "
            "Rose gold (#B76E79) brand accents throughout. "
            "Warm brown skin, bright dark eyes, joyful expression. "
            "Oakland CA luxury brand ambassador. "
        )

        for pose, prompt in base_result.sprite_prompts.items():
            # Insert Rosie's identity after the character name reference
            enriched = prompt.replace(
                "Character: Rosie. ",
                f"Character: {rosie_identity}",
            )
            rosie_enriched[pose] = enriched

        css_hint = (
            _CSS_HINT_WALK + " | " + _CSS_HINT_IDLE + " | "
            "wave and point poses trigger on user hover/interaction events. "
            "celebrate triggers on purchase confirmation or achievement unlock."
        )

        return SpriteResult(
            success=True,
            character_name="Rosie",
            sprite_prompts=rosie_enriched,
            css_animation_hint=css_hint,
        )
