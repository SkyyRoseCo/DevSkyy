"""Per-product design dossier loader — shared by all four catalog readers.

Reads founder-authored dossier markdown embedded in ``logo-registry.json`` and parses it
into a structured dict consumed by:
  - skyyrose.core.catalog_loader.get_product_with_dossier()
  - nano_banana.catalog
  - skyyrose.elite_studio.catalog
  - skyyrose.elite_studio.agents.three_d_agent (RAS prompt construction)

Hard-fails on missing dossier (H1 from plan): the legacy CSV's thin
`branding_spec` column is NOT a fallback — adding one is a backdoor that lets
us forget to author.

The parser is deliberately tolerant of the markdown indentation inside list
items but strict on the section headings and the technique vocabulary (caught
upstream by scripts/validate_dossier.py).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from skyyrose.core.catalog_loader import CATALOG_CSV, read_catalog_rows
from skyyrose.core.product_registry import load_registry

DOSSIERS_DIR = CATALOG_CSV.parent / "dossiers"


class DossierMissingError(FileNotFoundError):
    """Raised when a product's dossier markdown file is not found.

    The pipeline fails loudly rather than fall back to the thin CSV
    `branding_spec` column. Author the dossier before rendering.
    """


@dataclass
class Dossier:
    sku: str
    name: str
    collection: str
    slug: str
    garment_type_lock: str
    branding_block: str
    negative_block: str
    scene_pose: str = ""
    scene_setting: str = ""
    logo_reference: str = ""
    extra_logos: list[str] = field(default_factory=list)
    reference_image: str = ""
    extra_references: list[str] = field(default_factory=list)
    raw: str = field(default="", repr=False)

    def to_dict(self) -> dict:
        return {
            "sku": self.sku,
            "name": self.name,
            "collection": self.collection,
            "slug": self.slug,
            "garment_type_lock": self.garment_type_lock,
            "branding_block": self.branding_block,
            "negative_block": self.negative_block,
            "scene_pose": self.scene_pose,
            "scene_setting": self.scene_setting,
            "logo_reference": self.logo_reference,
            "extra_logos": list(self.extra_logos),
            "reference_image": self.reference_image,
            "extra_references": list(self.extra_references),
        }


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip()
    rest = text[end + 4 :].lstrip("\n")
    fm: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm, rest


# Compiled once at module load. The list-key pattern matches a YAML key
# followed by one-or-more indented bullets; the item pattern then extracts
# each bullet's value from the captured block.
_FRONTMATTER_LIST_KEY_RE = re.compile(
    r"^(\w[\w\-]*):\s*\n((?:[ \t]+-\s+.+\n?)+)",
    re.MULTILINE,
)
_FRONTMATTER_LIST_ITEM_RE = re.compile(
    r"^[ \t]+-\s+(.+?)\s*$",
    re.MULTILINE,
)


def _parse_frontmatter_lists(text: str) -> dict[str, list[str]]:
    """Extract YAML-list-style frontmatter values that `_parse_frontmatter` skips.

    Matches the canonical pattern:
        key:
          - item-one
          - item-two

    Returns a dict mapping key → list of stripped item strings. Keys whose
    values are scalar (already captured by `_parse_frontmatter`) are not
    returned here.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    out: dict[str, list[str]] = {}
    for match in _FRONTMATTER_LIST_KEY_RE.finditer(block):
        key = match.group(1)
        bullets_block = match.group(2)
        items = [
            m.group(1).strip().strip('"').strip("'")
            for m in _FRONTMATTER_LIST_ITEM_RE.finditer(bullets_block)
        ]
        if items:
            out[key] = items
    return out


def _extract_section(body: str, heading_pattern: str) -> str:
    pattern = rf"^##\s+{heading_pattern}.*?$(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, body, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_garment_lock(body: str) -> str:
    match = re.search(r"\*\*Garment type lock:\*\*\s*(.+?)(?:\n\n|\n##|\Z)", body, re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_scene_field(scene_section: str, label: str) -> str:
    pattern = rf"\*\*{re.escape(label)}:\*\*\s*(.+?)(?:\n-|\n\n|\Z)"
    match = re.search(pattern, scene_section, re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_dossier_markdown(text: str) -> Dossier:
    """Parse a dossier markdown string into a structured Dossier object."""
    fm, body = _parse_frontmatter(text)
    fm_lists = _parse_frontmatter_lists(text)

    branding_section = _extract_section(body, r"Branding")
    negative_section = _extract_section(body, r"Negative")
    scene_section = _extract_section(body, r"Scene direction")

    garment_lock = _extract_garment_lock(body)

    return Dossier(
        sku=fm.get("sku", ""),
        name=fm.get("name", ""),
        collection=fm.get("collection", ""),
        slug=fm.get("slug", ""),
        garment_type_lock=garment_lock,
        branding_block=branding_section,
        negative_block=negative_section,
        scene_pose=_extract_scene_field(scene_section, "Pose"),
        scene_setting=_extract_scene_field(scene_section, "Setting"),
        logo_reference=fm.get("logo_reference", ""),
        extra_logos=fm_lists.get("extra_logos", []),
        reference_image=fm.get("reference_image", ""),
        extra_references=fm_lists.get("extra_references", []),
        raw=text,
    )


def project_registry_dossier(product: dict) -> Dossier:
    """Project a registry record's dossier exactly as the founder authored it.

    The dossier is the founder's design specification. Its **Garment type lock**
    prose is the authoritative garment description, and it is consumed verbatim
    by render prompts (nano_banana spec builder, asset scaffolding, the asset
    manifest). It is returned unchanged -- never rewritten, never prefixed.

    The registry's structured ``garment`` fields (fit, materials, features) are
    machine extractions from that same prose, not fields the founder stated
    separately, and the split is imperfect in places. They must not override the
    prose they were derived from, and they must not be injected into a
    prompt-bearing field. Callers that want them read ``product["garment"]``
    (or ``skyyrose.core.product.get_product(sku)["garment"]``), where their
    ``source`` records that they are derived.
    """
    entry = product.get("dossier", {})
    content = entry.get("content")
    slug = entry.get("slug", "")
    if not isinstance(content, str) or not content.strip():
        raise DossierMissingError(f"No dossier {slug!r} content in the product registry.")
    dossier = parse_dossier_markdown(content)
    if not dossier.slug:
        dossier.slug = slug
    return dossier


def load_dossier(slug: str, dossiers_dir: Path | None = None) -> Dossier:
    """Load and parse a dossier by slug. Raises DossierMissingError if absent.

    Default reads use the editable product registry, never generated dossier
    mirrors. An explicit noncanonical directory supports isolated fixtures.
    Reload on each call so a founder correction is immediately observable.
    """
    if dossiers_dir is not None and dossiers_dir.resolve() != DOSSIERS_DIR.resolve():
        path = dossiers_dir / f"{slug}.md"
        if not path.exists():
            raise DossierMissingError(f"No fixture dossier at {path}.")
        text = path.read_text(encoding="utf-8")
    else:
        for product in load_registry()["products"].values():
            entry = product.get("dossier", {})
            if entry.get("slug") == slug:
                return project_registry_dossier(product)
        raise DossierMissingError(
            f"No dossier {slug!r} in the product registry. "
            "Author its dossier content before rendering; generated mirrors "
            "and branding_spec are not fallbacks."
        )
    dossier = parse_dossier_markdown(text)
    if not dossier.slug:
        dossier.slug = slug
    return dossier


def get_product_with_dossier(sku: str) -> dict:
    """Return the registry catalog row for `sku` merged with its parsed dossier.

    Raises:
        KeyError if SKU is not in the registry catalog.
        DossierMissingError if the registry dossier content does not exist.
    """
    rows = {row["sku"]: row for row in read_catalog_rows()}
    if sku not in rows:
        raise KeyError(f"SKU {sku!r} not found in the product registry")
    row = rows[sku]
    slug = (row.get("dossier_slug") or "").strip()
    if not slug:
        raise DossierMissingError(
            f"SKU {sku!r} has no dossier_slug in the product registry. "
            "Add the product's dossier binding before loading."
        )
    dossier = load_dossier(slug)
    return {**row, "dossier": dossier.to_dict(), "_dossier": dossier}


__all__ = [
    "DOSSIERS_DIR",
    "Dossier",
    "DossierMissingError",
    "parse_dossier_markdown",
    "project_registry_dossier",
    "load_dossier",
    "get_product_with_dossier",
]
