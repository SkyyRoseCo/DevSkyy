"""Fabric-aware glTF material extensions for garment GLBs (KHR_materials_sheen / anisotropy).

The fabric class is derived from the founder's registry prose
(``products[sku].garment.materials.specification``) — the product SOT. The presets below
are RENDERING parameters chosen per fabric class; they are not product facts and are never
written back to the registry.

Classification rules:

* Negated clauses are removed first (founder dossiers use ``NOT a fleece hoodie`` to rule
  things out). A negation inside parentheses ends at the closing parenthesis; otherwise it
  ends at the next ``.``/``;`` at parenthesis depth 0. Matching is case-insensitive so an
  over-strip can only produce an *unclassified* error, never a silent misclassification.
* When several classes match, the exterior shell wins, in this precedence:
  faux_leather > satin > nylon > jersey > fleece > knit > cotton.
* No match → ``UnclassifiedFabricError`` (fail closed; there is no default fabric).

**Known limitation — precedence is keyword order, not sentence structure.** A lining or trim
word can outrank the shell it is attached to: "cotton fleece hoodie with a mesh-lined hood"
classifies as JERSEY because ``mesh`` precedes ``fleece``. Every one of the 33 registry SKUs
was read against its prose and classifies correctly today (sg-009's "nylon-windbreaker-style
exterior shell" beats its sherpa lining exactly as intended), and
``test_golden_fabric_class_per_registry_sku`` pins each SKU to its verified class — so a
reworded specification that flips a preset fails that test instead of shipping a wrong sheen.
Sheen is applied to EVERY material and the web gate demands it on every material, which suits
the single-atlas Meshy/Tripo output this pipeline consumes; a multi-material GLB with, say, a
metal zipper material would need a per-material allowlist first.

Sheen presets (neutral-gray sheen color scalar, sheen roughness):

==============  =====  =========  ===========================================================
class           color  roughness  rationale
==============  =====  =========  ===========================================================
satin           0.15   0.30       tight weave, low pile → narrow, bright rim highlight
nylon           0.10   0.40       smooth filament shell; subtle glancing sheen only
jersey          0.15   0.50       polyester/mesh athletic knits; moderate soft rim
fleece          0.35   0.90       brushed/sherpa pile → broad, strong velvet-like rim
knit            0.30   0.85       ribbed yarn knit; fibrous, diffuse rim
cotton          0.20   0.80       plain cotton jersey tees; soft, low-intensity rim
faux_leather    —      —          coated/PU surface has no fiber pile → no sheen extension
==============  =====  =========  ===========================================================

Anisotropy is opt-in only: Meshy/Tripo atlases have no coherent tangent direction across UV
islands, so a blanket anisotropy lobe would streak in random directions per island.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from .glb_container import read_glb, write_glb

SHEEN_EXTENSION = "KHR_materials_sheen"
ANISOTROPY_EXTENSION = "KHR_materials_anisotropy"


class FabricClass(StrEnum):
    FAUX_LEATHER = "faux_leather"
    SATIN = "satin"
    NYLON = "nylon"
    JERSEY = "jersey"
    FLEECE = "fleece"
    KNIT = "knit"
    COTTON = "cotton"


class UnclassifiedFabricError(ValueError):
    """The specification names no recognised fabric once negations are removed."""


class MaterialPatchError(ValueError):
    """The GLB cannot carry fabric extensions (no materials / malformed materials)."""


@dataclass(frozen=True)
class FabricMatch:
    fabric_class: FabricClass
    keyword: str


def _unit(name: str, value: float) -> None:
    if not (math.isfinite(value) and 0.0 <= value <= 1.0):
        raise ValueError(f"{name} must be within [0, 1], got {value!r}")


@dataclass(frozen=True)
class SheenPreset:
    color: float
    roughness: float

    def __post_init__(self) -> None:
        _unit("sheen color", self.color)
        _unit("sheen roughness", self.roughness)

    def to_extension(self) -> dict[str, Any]:
        return {
            "sheenColorFactor": [self.color, self.color, self.color],
            "sheenRoughnessFactor": self.roughness,
        }


@dataclass(frozen=True)
class AnisotropyParams:
    strength: float
    rotation: float = 0.0

    def __post_init__(self) -> None:
        _unit("anisotropy strength", self.strength)
        if not math.isfinite(self.rotation):
            raise ValueError(f"anisotropy rotation must be finite, got {self.rotation!r}")

    def to_extension(self) -> dict[str, Any]:
        return {"anisotropyStrength": self.strength, "anisotropyRotation": self.rotation}


SHEEN_PRESETS: Mapping[FabricClass, SheenPreset | None] = MappingProxyType(
    {
        FabricClass.FAUX_LEATHER: None,
        FabricClass.SATIN: SheenPreset(0.15, 0.30),
        FabricClass.NYLON: SheenPreset(0.10, 0.40),
        FabricClass.JERSEY: SheenPreset(0.15, 0.50),
        FabricClass.FLEECE: SheenPreset(0.35, 0.90),
        FabricClass.KNIT: SheenPreset(0.30, 0.85),
        FabricClass.COTTON: SheenPreset(0.20, 0.80),
    }
)

# Precedence order = dict order (exterior shell first).
_FABRIC_PATTERNS: Mapping[FabricClass, re.Pattern[str]] = MappingProxyType(
    {
        FabricClass.FAUX_LEATHER: re.compile(r"faux[- ]leather|\bpu leather\b|\bvegan leather\b"),
        FabricClass.SATIN: re.compile(r"\bsat(?:in|een)\b"),
        FabricClass.NYLON: re.compile(r"\bnylon\b|\bripstop\b"),
        FabricClass.JERSEY: re.compile(r"\bjersey\b|\bmesh\b|\bpolyester\b|\btank\b"),
        FabricClass.FLEECE: re.compile(r"\bfleece\b|\bsherpa\b|\bterry\b"),
        FabricClass.KNIT: re.compile(r"\bknit\b|\bbeanie\b|\bacrylic\b"),
        FabricClass.COTTON: re.compile(r"\bcotton\b"),
    }
)

# Every negation form seen in founder prose, plus the ones a future edit could introduce.
# Boundaries are letter-lookarounds, not \b, so "_NOT_ a fleece hoodie" (underscore is a word
# char, which defeats \b) still strips. A marker removes the rest of its clause, so an
# over-strip can only end in UnclassifiedFabricError — never a wrongly-selected class.
_NEGATION = re.compile(
    r"(?<![a-z])(?:not|no|non(?=[- ])|never|without|unlike|isn't|isnt|"
    r"instead of|rather than|distinct from|as opposed to)(?![a-z])",
    re.IGNORECASE,
)
_WHITESPACE = re.compile(r"\s+")


def _normalise(text: str) -> str:
    return _WHITESPACE.sub(" ", text.replace("**", "")).strip()


def _enclosing_paren_close(text: str, start: int) -> int:
    level = 0
    for index in range(start, len(text)):
        if text[index] == "(":
            level += 1
        elif text[index] == ")":
            if level == 0:
                return index
            level -= 1
    return len(text)


def _clause_end(text: str, start: int) -> int:
    level = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "(":
            level += 1
        elif char == ")":
            level = max(0, level - 1)
        elif char in ".;" and level == 0:
            if index + 1 == len(text) or text[index + 1].isspace():
                return index + 1
    return len(text)


def _negation_end(text: str, start: int) -> int:
    depth = text.count("(", 0, start) - text.count(")", 0, start)
    if depth > 0:
        return _enclosing_paren_close(text, start)
    return _clause_end(text, start)


def strip_negations(specification: str) -> str:
    """Remove every negated clause so ruled-out fabrics can never classify."""
    cleaned = _normalise(specification)
    while match := _NEGATION.search(cleaned):
        end = _negation_end(cleaned, match.start())
        cleaned = f"{cleaned[: match.start()]} {cleaned[end:]}"
    return _normalise(cleaned)


def classify_fabric(specification: str) -> FabricMatch:
    """Classify the exterior fabric from founder prose; raise if nothing matches."""
    affirmative = strip_negations(specification).lower()
    for fabric_class, pattern in _FABRIC_PATTERNS.items():
        found = pattern.search(affirmative)
        if found:
            return FabricMatch(fabric_class=fabric_class, keyword=found.group(0))
    raise UnclassifiedFabricError(f"no recognised fabric in specification: {specification!r}")


def classify_product(product: Mapping[str, Any]) -> FabricMatch:
    """Classify a registry ``products[sku]`` record; a missing specification fails closed."""
    materials = product.get("garment", {}).get("materials") or {}
    specification = materials.get("specification")
    if not isinstance(specification, str) or not specification.strip():
        raise UnclassifiedFabricError("registry record has no garment.materials.specification")
    return classify_fabric(specification)


_SHEEN_FACTOR_KEYS = frozenset({"sheenColorFactor", "sheenRoughnessFactor"})


def _check_patchable(materials: list[Any], document: Mapping[str, Any]) -> None:
    """Refuse to patch a document where writing the preset would destroy existing data."""
    declared = document.get("extensionsUsed", [])
    if not isinstance(declared, list):
        raise MaterialPatchError(f"extensionsUsed is {type(declared).__name__}, expected a list")
    for index, material in enumerate(materials):
        extensions = material.get("extensions", {})
        if not isinstance(extensions, dict):
            raise MaterialPatchError(
                f"material {index} extensions is {type(extensions).__name__}, expected an object"
            )
        existing = extensions.get(SHEEN_EXTENSION)
        if existing is None:
            continue
        if not isinstance(existing, dict):
            raise MaterialPatchError(f"material {index} has a non-object KHR_materials_sheen")
        extra = sorted(set(existing) - _SHEEN_FACTOR_KEYS)
        if extra:
            raise MaterialPatchError(
                f"material {index} sheen carries {', '.join(extra)}; a preset overwrite would "
                "drop it — re-author that material instead of patching it"
            )


def apply_fabric_extensions(
    glb_bytes: bytes,
    preset: SheenPreset,
    *,
    anisotropy: AnisotropyParams | None = None,
) -> bytes:
    """Attach sheen (and opt-in anisotropy) to every material; payload bytes untouched."""
    container = read_glb(glb_bytes)
    materials = container.document.get("materials")
    if not isinstance(materials, list) or not materials:
        raise MaterialPatchError("GLB has no materials to patch")
    if not all(isinstance(material, dict) for material in materials):
        raise MaterialPatchError("GLB materials array contains a non-object entry")
    _check_patchable(materials, container.document)
    additions: dict[str, dict[str, Any]] = {SHEEN_EXTENSION: preset.to_extension()}
    if anisotropy is not None:
        additions[ANISOTROPY_EXTENSION] = anisotropy.to_extension()
    patched = [
        {**material, "extensions": {**material.get("extensions", {}), **additions}}
        for material in materials
    ]
    declared = container.document.get("extensionsUsed", [])
    used = sorted(set(declared) | set(additions))
    document = {**container.document, "materials": patched, "extensionsUsed": used}
    return write_glb(document, container.tail)
