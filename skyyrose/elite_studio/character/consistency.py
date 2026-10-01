"""
Character consistency utilities for SkyyRose Elite Studio.

Builds consistency anchors and manages character identity across
multiple generation requests.

"""

from __future__ import annotations

import uuid

from .models import CharacterSheet, CharacterSpec


def build_consistency_prompt(spec: CharacterSpec, additional_context: str = "") -> str:
    """Build a consistency anchor prompt from a CharacterSpec.

    This prompt block should be prepended to any follow-on generation
    request to maintain visual consistency with the reference sheet.

    Args:
        spec: The character specification to anchor from.
        additional_context: Optional extra context (scene, action, etc.)

    Returns:
        A prompt string suitable for prepending to any generation prompt.
    """
    brand_str = "; ".join(spec.brand_elements[:2]) if spec.brand_elements else ""
    base = (
        f"CONSISTENCY ANCHOR — Character: {spec.name}. "
        f"Style: {spec.style}. "
        f"Appearance: {spec.face_features[:120]} "
        f"Outfit: {spec.outfit_base[:120]} "
        f"Brand: {brand_str}. "
        "Maintain exact visual consistency with reference sheet. "
        "Same face, hair, skin tone, outfit, proportions as established character. "
    )
    if additional_context:
        base += f"Additional context: {additional_context}. "
    return base


def extract_face_description(sheet: CharacterSheet) -> str:
    """Extract a concise face description for use in subsequent prompts.

    Pulls the face features from the CharacterSpec within the sheet,
    trimmed to a concise usable prompt segment.

    Args:
        sheet: A completed CharacterSheet with populated spec.

    Returns:
        A concise face description string (≤200 chars).
    """
    face = sheet.spec.face_features
    # Trim to a concise, usable segment
    return face[:200].strip()


class ConsistencyManager:
    """Manages character consistency across multiple generation sessions.

    Characters are registered with their specs and retrieved by ID
    for consistent prompt generation. Thread-safe for single-process use.
    """

    def __init__(self) -> None:
        self._characters: dict[str, CharacterSpec] = {}

    def register_character(self, spec: CharacterSpec) -> str:
        """Register a character spec and return a stable character_id.

        If a character with the same name already exists, the existing
        registration is updated with the new spec.

        Args:
            spec: The character spec to register.

        Returns:
            character_id: A stable ID for future lookups.
        """
        # Use name-based ID for stability across sessions
        character_id = f"char-{spec.name.lower().replace(' ', '-')}-{str(uuid.uuid4())[:6]}"
        # Check if name already registered — update if so
        for existing_id, existing_spec in self._characters.items():
            if existing_spec.name == spec.name:
                self._characters[existing_id] = spec
                return existing_id
        self._characters[character_id] = spec
        return character_id

    def get_consistency_prompt(self, character_id: str) -> str:
        """Return a consistency anchor prompt for a registered character.

        Args:
            character_id: ID returned by register_character().

        Returns:
            Consistency prompt string, or empty string if not found.
        """
        spec = self._characters.get(character_id)
        if not spec:
            return ""
        return build_consistency_prompt(spec)

    def list_characters(self) -> list[dict]:
        """Return a list of all registered characters as dicts.

        Returns:
            List of dicts with keys: character_id, name, style.
        """
        return [
            {
                "character_id": cid,
                "name": spec.name,
                "style": spec.style,
                "embedding_path": spec.embedding_path,
            }
            for cid, spec in self._characters.items()
        ]

    def get_spec(self, character_id: str) -> CharacterSpec | None:
        """Return the CharacterSpec for a registered character."""
        return self._characters.get(character_id)

    def unregister(self, character_id: str) -> bool:
        """Remove a character registration. Returns True if found and removed."""
        if character_id in self._characters:
            del self._characters[character_id]
            return True
        return False
