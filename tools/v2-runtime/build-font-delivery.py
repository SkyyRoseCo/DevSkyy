"""Derive fixed-width page-font deliveries without changing font authority."""

import argparse
import hashlib
import io
import json
import os
import tempfile
from importlib.metadata import version
from pathlib import Path
from typing import NamedTuple

import brotli
from fontTools.ttLib import TTFont, woff2
from fontTools.varLib.instancer import instantiateVariableFont

THEME = Path(__file__).resolve().parents[2] / "wordpress-theme/skyyrose-flagship-2"
MANIFEST = "assets/derived/fonts/manifest.json"
VERSIONS = {"fonttools": "4.59.2", "brotli": "1.2.0"}


class Job(NamedTuple):
    """One width instance of one approved source font."""

    source: str
    source_sha: str
    axes: list
    fixed: dict
    destination: str


JOBS = (
    Job(
        "assets/sot/fonts/archivo-latin.woff2",
        "4c98b9d490d1698ec95f2ff17a6c7d0e72691864c0c5d7bc2a2c161b45afe5ad",
        [("wght", 100.0, 600.0, 900.0), ("wdth", 62.0, 100.0, 125.0)],
        {"wdth": 100},
        "assets/derived/fonts/archivo-normal-width.woff2",
    ),
    Job(
        "assets/sot/fonts/anybody-latin.woff2",
        "8c4a79f7434579408fe25290420de69609617728a61b45d0b12055c03d92bc4e",
        [("wdth", 50.0, 100.0, 150.0), ("wght", 100.0, 100.0, 900.0)],
        {"wdth": 50},
        "assets/derived/fonts/anybody-condensed.woff2",
    ),
    Job(
        "assets/sot/fonts/anybody-latin.woff2",
        "8c4a79f7434579408fe25290420de69609617728a61b45d0b12055c03d92bc4e",
        [("wdth", 50.0, 100.0, 150.0), ("wght", 100.0, 100.0, 900.0)],
        {"wdth": 150},
        "assets/derived/fonts/anybody-wide.woff2",
    ),
    Job(
        "assets/sot/fonts/martian-mono-latin.woff2",
        "fa6f2665175059db1410a3322cedf23328c06dae59c2e1b126bbb764fb69a1b0",
        [("wght", 100.0, 400.0, 800.0), ("wdth", 75.0, 112.5, 112.5)],
        {"wdth": 87.5},
        "assets/derived/fonts/martian-mono-narrow.woff2",
    ),
)


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


def retained(job: Job) -> list:
    """Axes the delivery keeps variable, in source order."""
    return [axis for axis in job.axes if axis[0] not in job.fixed]


def check_preserved(candidate: TTFont, original: TTFont) -> None:
    """Fail when instancing changed coverage, metrics or identity."""
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


def derive(raw: bytes, job: Job = JOBS[0]) -> bytes:
    """Fix the job's axes; retain glyph coverage, other axes, names and line metrics."""
    for package, expected in VERSIONS.items():
        if version(package) != expected:
            raise ValueError(f"Unpinned font generator: {package}")
    if woff2.brotli is not brotli:
        raise ValueError("Unpinned selected WOFF2 encoder")
    if hashlib.sha256(raw).hexdigest() != job.source_sha:
        raise ValueError(f"Approved source drift: {job.source}")
    original = TTFont(io.BytesIO(raw), recalcTimestamp=False)
    if axes(original) != job.axes:
        raise ValueError(f"Unexpected axes: {job.source}")
    candidate = instantiateVariableFont(
        original, job.fixed, inplace=False, static=False, updateFontNames=False
    )
    if axes(candidate) != retained(job):
        raise ValueError("Retained axis range changed")
    check_preserved(candidate, original)
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


def record(job: Job, payload: bytes) -> dict:
    """Manifest entry binding one delivery to its source."""
    return {
        "source": job.source,
        "source_sha256": job.source_sha,
        "fixed_axes": job.fixed,
        "retained_axes": {tag: [low, default, high] for tag, low, default, high in retained(job)},
        "unicode_subset": False,
        "output": job.destination,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
    }


def generate(check: bool = False) -> None:
    """Write only the derivatives; check mode never creates or repairs files."""
    sources = {job.source: safe_path(job.source).read_bytes() for job in JOBS}
    payloads = [(job, derive(sources[job.source], job)) for job in JOBS]
    manifest = {
        "schema": "skyyrose.font-delivery.v2",
        "versions": VERSIONS,
        "license": "OFL-1.1",
        "license_path": "assets/sot/fonts/OFL-1.1.txt",
        "deliveries": [record(job, payload) for job, payload in payloads],
    }
    outputs = {safe_path(job.destination): payload for job, payload in payloads}
    outputs[safe_path(MANIFEST)] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
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
    for relative, raw in sources.items():
        if safe_path(relative).read_bytes() != raw:
            raise ValueError("Original font changed")
    print(
        f"{'Verified' if check else 'Built'} {len(JOBS)} fixed-width font deliveries; "
        "full weights and sources preserved"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    generate(parser.parse_args().check)
