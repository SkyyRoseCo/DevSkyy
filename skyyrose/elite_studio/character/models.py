"""
Character system data models for SkyyRose Elite Studio.

Frozen dataclasses for character specs, sheets, and poses.
All objects are immutable.

"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterSpec:
    """Immutable specification for a SkyyRose character."""

    name: str
    style: str  # "pixar-chibi", "realistic", "illustration"
    body_description: str
    face_features: str
    outfit_base: str
    brand_elements: tuple[str, ...]
    reference_paths: tuple[str, ...]
    embedding_path: str = ""


@dataclass(frozen=True)
class CharacterSheet:
    """Immutable reference sheet for a character — all generation prompts."""

    success: bool
    spec: CharacterSpec
    front_view_prompt: str
    side_view_prompt: str
    back_view_prompt: str
    expression_grid_prompt: str  # 2x3 grid of 6 expressions
    sprite_description: str  # description for web sprite generation
    error: str = ""


@dataclass(frozen=True)
class CharacterPose:
    """Immutable result for a character in a specific pose."""

    success: bool
    character_name: str
    pose: str
    product_sku: str  # product the character is wearing (if any)
    generation_prompt: str
    output_path: str = ""
    error: str = ""
