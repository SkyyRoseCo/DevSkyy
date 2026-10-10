"""
Character Creation System — SkyyRose Elite Studio.

Provides character spec, sheet generation, pose generation,
consistency management, and sprite generation for the SkyyRose
mascot and custom brand characters.

"""

from __future__ import annotations

from .agent import CharacterCreationAgent
from .consistency import ConsistencyManager, build_consistency_prompt, extract_face_description
from .models import CharacterPose, CharacterSheet, CharacterSpec
from .sprite_generator import SpriteGenerator, SpriteResult, SpriteSpec

__all__ = [
    "CharacterSpec",
    "CharacterSheet",
    "CharacterPose",
    "CharacterCreationAgent",
    "ConsistencyManager",
    "build_consistency_prompt",
    "extract_face_description",
    "SpriteGenerator",
    "SpriteSpec",
    "SpriteResult",
]
