#!/usr/bin/env python3
"""Generate Stage 3 FLUX decoration inpaint prompt files for all product dossiers.

Reads each dossier markdown file, extracts branding entries (region, technique,
color, description), calls the canonical build_decoration_prompt() function
for each entry, and writes renders/prompts-preview/{dossier_slug}/stage3-decoration.txt.

Usage:
    python3 scripts/generate_stage3_prompts.py
    python3 scripts/generate_stage3_prompts.py --dry-run   # print to stdout only
    python3 scripts/generate_stage3_prompts.py --slug black-rose-crewneck  # single product
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DOSSIER_DIR = REPO_ROOT / "wordpress-theme/skyyrose-flagship/data/dossiers"
OUTPUT_DIR = REPO_ROOT / "renders/prompts-preview"

# Ensure repo root is on sys.path so we can import from the package tree.
sys.path.insert(0, str(REPO_ROOT))

from skyyrose.core.product_registry import RETAINED_DOSSIERS  # noqa: E402
from skyyrose.elite_studio.synthesis.prompts.decoration_prompts import (  # noqa: E402
    build_decoration_prompt,
)

# ---------------------------------------------------------------------------
# Region parsing helpers
# ---------------------------------------------------------------------------

# Controlled region vocabulary from the dossier template.
KNOWN_REGIONS = {
    "front-chest",
    "front-left-chest",
    "front-right-chest",
    "front-belly",
    "front-hem",
    "front-pocket",
    "back-upper",
    "back-center",
    "back-lower",
    "back-yoke",
    "back-neck",
    "back-body",
    "front-body",
    "left-sleeve",
    "right-sleeve",
    "left-cuff",
    "right-cuff",
    "collar-outside",
    "collar-inside",
    "collar",
    "neck-tape",
    "hem",
    "side-seam",
    "left-thigh",
    "right-thigh",
    "hood-back",
    "hood-inside",
    "drawstring",
    "hat-front",
    "hat-side",
    "hat-back",
    "inside-waistband",
    "waistband",
    # composite / freeform regions that appear in practice
    "front-left-hem",
    "front-belly-lower-left",
    "front-placket",
    "front-placket-binding",
    "front-placket-buttons",
    "collar-binding",
    "v-neck-binding",
    "left-sleeve-patch",
    "right-sleeve-patch",
    "back-number",
    "front-number",
}

# Controlled technique vocabulary (from decoration_prompts.py TECHNIQUE_PHYSICS keys +
# template extras).  We map aliases to canonical names.
TECHNIQUE_ALIASES: dict[str, str] = {
    "silicone-appliqué": "silicone-applique",
    "silicone-applique": "silicone-applique",
    "silicone": "silicone-applique",
    "patch (sewn-on button hardware)": "patch",
    "embroidered patch": "embroidered-patch",
}

# Dossier entries we skip — they describe construction/fabric, not branding
# decoration. We skip "stitched" (construction stitching) and pure structural
# elements because build_decoration_prompt() for those would produce generic
# fabric prompts with no meaningful value for Stage 3 inpainting.
SKIP_TECHNIQUES = {"stitched"}

# Similarly skip pure structural regions with no decoration value.
SKIP_REGIONS = {
    "front-body",
    "back-body",
    "left-sleeve",
    "right-sleeve",
    "left-cuff",
    "right-cuff",
    "collar",
    "waistband",
    "hem",
    "front-placket",
    "front-placket-binding",
    "side-seam",
    "v-neck-binding",
    "collar-binding",
    "collar-outside",
    "drawstring",
}


def normalize_technique(raw: str) -> str:
    """Map raw technique text to the controlled vocabulary key."""
    t = raw.strip().lower()
    if t in TECHNIQUE_ALIASES:
        return TECHNIQUE_ALIASES[t]
    return t


def extract_frontmatter(text: str) -> dict[str, str]:
    """Parse the YAML frontmatter block (--- ... ---) into a simple dict."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm


def extract_branding_entries(dossier_text: str) -> list[dict]:
    """Extract individual branding bullet entries from a dossier markdown file.

    Each bullet under '## Branding' that has a **Technique:** field is
    returned as a dict with keys: region, technique, color, description,
    raw_line.

    Entries under ## Negative and ## Scene direction are ignored.
    """
    # Isolate the Branding section — stop at ## Negative or ## Scene
    branding_match = re.search(
        r"## Branding.*?(?=\n## Negative|\n## Scene direction|\Z)",
        dossier_text,
        re.DOTALL | re.IGNORECASE,
    )
    if not branding_match:
        return []

    branding_text = branding_match.group(0)

    entries: list[dict] = []

    # Each top-level bullet starts with "- **{region}**" (possibly with
    # dimension notes in parens).  The bullet may span multiple lines via
    # continuation.  We split on lines that start with "- **" to segment
    # individual entries.
    # Collect bullet blocks
    bullet_blocks: list[str] = []
    current: list[str] = []
    for line in branding_text.splitlines():
        if re.match(r"^- \*\*", line):
            if current:
                bullet_blocks.append("\n".join(current))
            current = [line]
        elif current and (line.startswith("  ") or line.strip().startswith("**")):
            # continuation of previous bullet
            current.append(line)
        else:
            if current:
                bullet_blocks.append("\n".join(current))
                current = []

    if current:
        bullet_blocks.append("\n".join(current))

    for block in bullet_blocks:
        # Extract region — first **bold** token in the bullet
        region_match = re.match(r"^- \*\*([^*]+)\*\*", block)
        if not region_match:
            continue
        region_raw = region_match.group(1)
        # Strip parenthetical dimension info from the region token
        region = re.split(r"\s*\(", region_raw)[0].strip().lower()

        # Skip pure structural / construction regions
        if region in SKIP_REGIONS:
            continue

        # Extract Technique
        tech_match = re.search(r"\*\*Technique:\*\*\s*([^.\n]+)", block, re.IGNORECASE)
        if not tech_match:
            continue
        technique_raw = tech_match.group(1).strip().rstrip(".")
        technique = normalize_technique(technique_raw)

        # Skip construction-only techniques
        if technique in SKIP_TECHNIQUES:
            continue

        # Extract Color (also covers Color/Colorway).
        # Color values can span multiple continuation lines in the block, so
        # we capture everything from the Color: marker up to the next **bold**
        # field marker or end-of-block.  We then collapse whitespace.
        color_match = re.search(
            r"\*\*Color(?:/Colorway)?:\*\*\s*(.*?)(?=\s*\*\*|\Z)",
            block,
            re.IGNORECASE | re.DOTALL,
        )
        if color_match:
            color = re.sub(r"\s+", " ", color_match.group(1)).strip().rstrip(".")
        else:
            color = "unspecified"

        # Extract description — everything between the region header and the
        # first **Technique:** marker (minus dimension annotation).
        desc_match = re.match(
            r"^- \*\*[^*]+\*\*(?:\s*\([^)]+\))?:?\s*(.*?)(?:\*\*Technique|\Z)",
            block,
            re.DOTALL,
        )
        if desc_match:
            desc_raw = desc_match.group(1)
        else:
            desc_raw = block

        # Clean up description — collapse whitespace, strip markdown bold markers
        desc = re.sub(r"\s+", " ", desc_raw).strip()
        desc = re.sub(r"\*\*[^*]+\*\*:.*", "", desc).strip()
        desc = desc.strip(":").strip()

        # If description is empty or just whitespace, use the region + technique
        if not desc or len(desc) < 5:
            desc = f"{region} {technique} decoration"

        entries.append(
            {
                "region": region,
                "technique": technique,
                "color": color,
                "description": desc,
                "raw_line": block[:120].replace("\n", " "),
            }
        )

    return entries


def section_label(region: str) -> str:
    """Return a human-readable section heading for a region."""
    front_set = {
        "front-chest",
        "front-left-chest",
        "front-right-chest",
        "front-belly",
        "front-hem",
        "front-pocket",
        "front-left-hem",
        "front-belly-lower-left",
        "front-number",
    }
    back_set = {
        "back-upper",
        "back-center",
        "back-lower",
        "back-yoke",
        "back-neck",
        "back-number",
    }
    sleeve_set = {"left-sleeve-patch", "right-sleeve-patch"}
    collar_set = {"collar-inside", "neck-tape"}
    hat_set = {"hat-front", "hat-side", "hat-back"}
    misc_set = {
        "left-thigh",
        "right-thigh",
        "inside-waistband",
        "hood-back",
        "hood-inside",
    }

    if region in front_set:
        return "FRONT"
    if region in back_set:
        return "BACK"
    if region in sleeve_set:
        return "SLEEVE"
    if region in collar_set:
        return "COLLAR / INTERIOR"
    if region in hat_set:
        return "HAT"
    if region in misc_set:
        return "OTHER"
    return "OTHER"


def build_output(dossier_slug: str, name: str, sku: str, entries: list[dict]) -> str:
    """Build the full stage3-decoration.txt content for one product."""
    lines: list[str] = [
        f"# Stage 3 Decoration Prompts — {name}",
        f"# SKU: {sku} | View: front+back",
        "# Generated offline by scripts/generate_stage3_prompts.py; not render approval",
        "",
    ]

    if not entries:
        lines.append("# (No decoration entries extracted from this dossier)")
        return "\n".join(lines)

    current_section = ""
    for entry in entries:
        section = section_label(entry["region"])
        if section != current_section:
            if current_section:
                lines.append("")
            lines.append(f"## {section} — {entry['region']}")
            current_section = section
        else:
            lines.append("")
            lines.append(f"### {entry['region']}")

        prompt = build_decoration_prompt(
            decoration_description=entry["description"],
            technique=entry["technique"],
            region=entry["region"],
            color=entry["color"],
        )
        lines.append(prompt)

    return "\n".join(lines)


def process_dossier(path: Path, dry_run: bool = False) -> tuple[str, int]:
    """Process one dossier file and write (or print) its stage3-decoration.txt."""
    text = path.read_text(encoding="utf-8")
    fm = extract_frontmatter(text)
    sku = fm.get("sku", "unknown")
    name = fm.get("name", path.stem)
    dossier_slug = path.stem

    entries = extract_branding_entries(text)
    output = build_output(dossier_slug, name, sku, entries)

    if dry_run:
        print(f"\n{'=' * 80}")
        print(f"DOSSIER: {dossier_slug}  ({sku})  —  {len(entries)} entries")
        print(f"{'=' * 80}")
        print(output)
    else:
        out_dir = OUTPUT_DIR / dossier_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "stage3-decoration.txt"
        out_file.write_text(output, encoding="utf-8")

    return dossier_slug, len(entries)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Stage 3 decoration prompt files")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout, don't write files")
    parser.add_argument("--slug", help="Process only this dossier slug (e.g. black-rose-crewneck)")
    args = parser.parse_args()

    dossier_files = sorted(
        f for f in DOSSIER_DIR.glob("*.md") if not f.name.startswith("_") and f.name != "CLAUDE.md"
    )
    # Dossiers kept by founder decision outside the registry are not a product's
    # spec; rendering them would emit a second prompt set for an existing SKU.
    dossier_files = [
        f for f in dossier_files if f.name != "_template.md" and f.name not in RETAINED_DOSSIERS
    ]

    if args.slug:
        dossier_files = [f for f in dossier_files if f.stem == args.slug]
        if not dossier_files:
            print(f"ERROR: No dossier found with slug '{args.slug}'", file=sys.stderr)
            sys.exit(1)

    print(f"Processing {len(dossier_files)} dossier(s)...")

    results: list[tuple[str, int]] = []
    errors: list[tuple[str, str]] = []

    for dossier_path in dossier_files:
        try:
            slug, count = process_dossier(dossier_path, dry_run=args.dry_run)
            results.append((slug, count))
            status = "stdout" if args.dry_run else "written"
            print(f"  {status:7s}  {slug}  ({count} entries)")
        except Exception as exc:  # noqa: BLE001
            errors.append((dossier_path.stem, str(exc)))
            print(f"  ERROR    {dossier_path.stem}: {exc}", file=sys.stderr)

    print(
        f"\n{'DRY RUN — ' if args.dry_run else ''}Done: {len(results)} files, {len(errors)} errors"
    )
    if errors:
        print("\nFailed slugs:")
        for slug, msg in errors:
            print(f"  {slug}: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
