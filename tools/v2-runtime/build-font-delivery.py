"""Derive Archivo at its existing default width without changing font authority."""

import argparse
import hashlib
import io
import json
import os
import tempfile
from importlib.metadata import version
from pathlib import Path

import brotli
from fontTools.ttLib import TTFont, woff2
from fontTools.varLib.instancer import instantiateVariableFont

THEME = Path(__file__).resolve().parents[2] / "wordpress-theme/skyyrose-flagship-2"
SOURCE = "assets/sot/fonts/archivo-latin.woff2"
SOURCE_SHA = "4c98b9d490d1698ec95f2ff17a6c7d0e72691864c0c5d7bc2a2c161b45afe5ad"
DESTINATION = "assets/derived/fonts/archivo-normal-width.woff2"
VERSIONS = {"fonttools": "4.59.2", "brotli": "1.2.0"}
AXES = [("wght", 100.0, 600.0, 900.0), ("wdth", 62.0, 100.0, 125.0)]


def axes(font: TTFont) -> list:
    """Return the complete variable axis contract."""
    return [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes]


def unicode_maps(font: TTFont) -> dict:
    """Bind every Unicode subtable, including non-preferred mappings."""
    return {
        (table.platformID, table.platEncID, table.language, table.format): table.cmap
        for table in font["cmap"].tables
        if table.isUnicode()
    }


def derive(raw: bytes) -> bytes:
    """Retain glyph coverage, weight variation, names and line metrics."""
    for package, expected in VERSIONS.items():
        if version(package) != expected:
            raise ValueError(f"Unpinned font generator: {package}")
    if woff2.brotli is not brotli:
        raise ValueError("Unpinned selected WOFF2 encoder")
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("Approved Archivo source drift")
    original = TTFont(io.BytesIO(raw), recalcTimestamp=False)
    if axes(original) != AXES:
        raise ValueError("Unexpected Archivo axes")
    candidate = instantiateVariableFont(
        original, {"wdth": 100}, inplace=False, static=False, updateFontNames=False
    )
    if axes(candidate) != AXES[:1]:
        raise ValueError("Weight range changed")
    if (
        unicode_maps(candidate) != unicode_maps(original)
        or candidate.getGlyphOrder() != original.getGlyphOrder()
    ):
        raise ValueError("Font coverage changed")
    for table, fields in {
        "head": ("unitsPerEm", "created", "modified"),
        "hhea": ("ascent", "descent", "lineGap"),
        "OS/2": ("sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent"),
    }.items():
        if any(
            getattr(candidate[table], field) != getattr(original[table], field) for field in fields
        ):
            raise ValueError("Font metrics changed")
    for name_id in (0, 1, 2, 4, 6, 13, 14, 16, 17):
        if candidate["name"].getDebugName(name_id) != original["name"].getDebugName(name_id):
            raise ValueError("Font identity or license changed")
    candidate.flavor = "woff2"
    stream = io.BytesIO()
    candidate.save(stream, reorderTables=True)
    return stream.getvalue()


def safe_path(relative: str) -> Path:
    """Refuse symlinks at every controlled output boundary."""
    path = THEME / relative
    path.relative_to(THEME)
    for item in (path, *path.parents):
        if item.is_symlink():
            raise ValueError(f"Symlink font path: {item}")
        if item == THEME:
            break
    return path


def generate(check: bool = False) -> None:
    """Write only the derivative; check mode never creates or repairs files."""
    raw = safe_path(SOURCE).read_bytes()
    payload = derive(raw)
    manifest = {
        "schema": "skyyrose.font-delivery.v1",
        "source": SOURCE,
        "source_sha256": SOURCE_SHA,
        "fixed_axes": {"wdth": 100},
        "retained_axes": {"wght": [100, 600, 900]},
        "unicode_subset": False,
        "versions": VERSIONS,
        "output": DESTINATION,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "license": "OFL-1.1",
        "license_path": "assets/sot/fonts/OFL-1.1.txt",
    }
    outputs = {
        safe_path(DESTINATION): payload,
        safe_path("assets/derived/fonts/manifest.json"): (
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        ).encode(),
    }
    for path, data in outputs.items():
        if check:
            if not path.is_file() or path.read_bytes() != data:
                raise ValueError(f"Stale font delivery: {path.name}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        try:
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    if safe_path(SOURCE).read_bytes() != raw:
        raise ValueError("Original font changed")
    print(
        f"{'Verified' if check else 'Built'} Archivo default-width delivery; full weights and source preserved"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    generate(parser.parse_args().check)
