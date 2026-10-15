#!/usr/bin/env python3
"""Asset SOT census: every media file in the repository must have an owning ledger.

The census enumerates media (images, video, 3D models, fonts, audio and asset PDFs)
that Git tracks, plus untracked files that are present and not ignored. It then
resolves which existing ledger references each file. It never writes a ledger and
never touches a binary: ledgers own references, binaries keep their paths.

Ledgers (declared in ``DEFAULT_LEDGERS``; see ``SOT.md``):

* authority   - ``logo-registry.json`` (products), ``visual-manifest.json``
                (non-product imagery), ``typography.json`` (fonts)
* projection  - registry-generated views: ``data/sot-images.json``,
                ``assets/products/manifest.json``, ``assets/products/catalog/**/index.json``,
                ``assets/hub/manifest.json``. Reported for consistency, but never owners:
                a stale view must not keep an asset its authority dropped
* theme-v2    - Flagship 2 media ledgers under ``skyyrose-flagship-2/data`` and its
                delivery ``assets/**/manifest.json`` files
* review      - ``tasks/catalog-reconciliation/image-library/inventory.json``, the
                review-area inventory for unverified, other-design and non-product media

A file is *owned* when a non-projection ledger references its path, or when its bytes
are identical to an owned file (a byte copy, or a symlink to one, carries the identity of
the referenced original).
Out-of-scope paths (dependencies, test fixtures, QA captures, documentation figures,
agent tooling, ledger-regenerated derivatives) are excluded with an explicit reason.

Fails closed: a declared ledger that is missing or unreadable is an error (exit 2),
never an empty ledger.

Usage::

    python scripts/asset_sot_census.py --check    # exit 1 if any in-scope asset is orphaned
    python scripts/asset_sot_census.py --report   # full JSON report on stdout
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import subprocess
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
V1 = "wordpress-theme/skyyrose-flagship"
V2 = "wordpress-theme/skyyrose-flagship-2"

MEDIA_EXTENSIONS = frozenset(
    {
        # raster / vector imagery
        "png", "jpg", "jpeg", "webp", "gif", "avif", "svg", "ico", "bmp", "tif", "tiff",
        "heic", "psd", "hdr", "exr", "ktx2",
        # video
        "mp4", "webm", "mov", "m4v",
        # 3D
        "glb", "gltf", "fbx", "obj", "usdz", "blend",
        # fonts
        "woff", "woff2", "ttf", "otf", "eot",
        # audio
        "mp3", "wav", "ogg", "m4a",
        # documents used as assets (only under an ``assets/`` folder; see ``scope_reason``)
        "pdf",
    }
)  # fmt: skip

# Any path segment named here is dependency, cache or build output.
EXCLUDED_SEGMENTS = {
    "node_modules": "dependency",
    "vendor": "dependency",
    "site-packages": "dependency",
    ".venv": "dependency",
    "venv": "dependency",
    "__pycache__": "build-output",
    ".next": "build-output",
    "dist": "build-output",
    "build": "build-output",
    ".git": "build-output",
    "evidence": "qa-capture",
    "baseline-evidence": "qa-capture",
    "qa-captures": "qa-capture",
}

# Path prefixes that hold no shippable or source asset, each with its reason.
EXCLUDED_PREFIXES: tuple[tuple[str, str], ...] = (
    ("tests/", "test-fixture"),
    (".wolf/", "qa-capture"),
    ("screenshots/", "qa-capture"),
    (".devskyy/", "qa-capture"),
    ("docs/", "documentation"),
    (".claude/", "agent-tooling"),
    ("plugins/", "agent-tooling"),
    ("skyyrose-suite/", "agent-tooling"),
)


@dataclass(frozen=True)
class Ledger:
    """A declared ledger: the files that hold it and how its path strings resolve.

    ``bases`` are tried in order; ``"@dir"`` means the ledger file's own folder.
    ``parser`` is ``"paths"`` (every string key/value that names a media file) or
    ``"visual-manifest"`` (``path`` + ``formats`` entries under the V1 assets folder).
    """

    name: str
    role: str
    files: tuple[str, ...]
    bases: tuple[str, ...] = ("",)
    parser: str = "paths"


# Owned only by this ledger = parked in the review area awaiting a founder decision.
REVIEW_LEDGER = "review-inventory"
# Generated views of an authority: checked for resolution, never counted as owners.
PROJECTION = "projection"


DEFAULT_LEDGERS: tuple[Ledger, ...] = (
    Ledger(
        "product-registry",
        "authority",
        (f"{V1}/data/logo-registry.json",),
        ("", V1, f"{V1}/assets", V2),
    ),
    Ledger(
        "visual-manifest",
        "authority",
        (f"{V1}/data/visual-manifest.json",),
        (f"{V1}/assets",),
        "visual-manifest",
    ),
    Ledger("typography", "authority", (f"{V1}/data/brand/typography.json",), (V1, "")),
    Ledger("sot-images", PROJECTION, ("data/sot-images.json",), (V1, "")),
    Ledger("product-asset-manifest", PROJECTION, ("assets/products/manifest.json",)),
    Ledger("product-library", PROJECTION, ("assets/products/catalog/**/index.json",), ("", "@dir")),
    Ledger("asset-hub", PROJECTION, ("assets/hub/manifest.json",), ("assets/hub", "", V1)),
    Ledger(
        "flagship-2-media",
        "theme-v2",
        (
            f"{V2}/data/*.json",
            f"{V2}/data/v2-media-reviews/*.json",
            f"{V2}/assets/**/manifest.json",
        ),
        ("@dir", V2, f"{V2}/assets", ""),  # manifest-local names win over broader bases
    ),
    Ledger(
        REVIEW_LEDGER,
        "review",
        ("tasks/catalog-reconciliation/image-library/inventory.json",),
    ),
)


class LedgerError(RuntimeError):
    """A declared ledger is missing or unreadable — the census cannot pass."""


def extension(path: str) -> str:
    """Lower-case extension of ``path`` without the dot ('' when none)."""
    name = path.rsplit("/", 1)[-1]
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def is_media(path: str) -> bool:
    return extension(path) in MEDIA_EXTENSIONS


def scope_reason(path: str) -> str | None:
    """Why ``path`` is out of census scope, or ``None`` when it is in scope."""
    for segment in path.split("/")[:-1]:
        if segment in EXCLUDED_SEGMENTS:
            return EXCLUDED_SEGMENTS[segment]
    for prefix, reason in EXCLUDED_PREFIXES:
        if path.startswith(prefix):
            return reason
    if path.endswith((".min.svg", ".min.css")):
        return "build-output"
    if "/standardized/" in path and path.startswith("assets/products/catalog/"):
        return "regenerated-derivative"
    if extension(path) == "pdf" and "assets" not in path.split("/")[:-1]:
        return "document"
    return None


def _git_paths(root: Path, *args: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", *args],
            capture_output=True,
            check=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LedgerError(f"git ls-files failed in {root}: {exc}") from exc
    return [p for p in result.stdout.split("\0") if p]


def discover(root: Path) -> dict[str, list[str]]:
    """Media paths grouped as ``tracked`` / ``untracked`` / ``ignored`` (present only)."""
    tracked = [p for p in _git_paths(root) if is_media(p)]
    untracked = [p for p in _git_paths(root, "--others", "--exclude-standard") if is_media(p)]
    ignored = [
        p
        for p in _git_paths(root, "--others", "--ignored", "--exclude-standard")
        if is_media(p) and scope_reason(p) is None
    ]
    return {
        "tracked": sorted(p for p in tracked if (root / p).is_file()),
        "missing_tracked": sorted(
            p for p in tracked if not (root / p).is_file() and scope_reason(p) is None
        ),
        "untracked": sorted(p for p in untracked if (root / p).is_file()),
        "ignored": sorted(p for p in ignored if (root / p).is_file()),
    }


def ledger_files(root: Path, ledger: Ledger) -> list[Path]:
    """Every file holding ``ledger``; fails closed when a declared pattern matches nothing."""
    found: list[Path] = []
    for pattern in ledger.files:
        matches = sorted(p for p in root.glob(pattern) if p.is_file())
        if not matches:
            raise LedgerError(f"{ledger.name}: no file matches {pattern}")
        found.extend(matches)
    return sorted(set(found))


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LedgerError(f"unreadable ledger {path}: {exc}") from exc


def iter_strings(node: object) -> Iterator[str]:
    """Every string key and string value in a JSON document."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from iter_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_strings(value)
    elif isinstance(node, str):
        yield node


def iter_visual_manifest(node: object) -> Iterator[str]:
    """Asset-relative file names declared by visual-manifest ``path`` + ``formats`` entries."""
    if isinstance(node, dict):
        if "path" in node and "formats" in node:
            for fmt in node["formats"]:
                separator = "-" if fmt[:1].isdigit() else "."
                yield f"{node['path']}{separator}{fmt}"
            return
        for value in node.values():
            yield from iter_visual_manifest(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_visual_manifest(value)


def clean_reference(text: str) -> str | None:
    """Normalise a ledger string to a relative media path, or ``None`` if it is not one."""
    candidate = text.strip().split("?", 1)[0].split("#", 1)[0]
    if not candidate or "\n" in candidate or "://" in candidate or not is_media(candidate):
        return None
    candidate = posixpath.normpath(candidate.lstrip("/"))
    while candidate.startswith("./"):
        candidate = candidate[2:]
    return None if candidate.startswith("..") else candidate


def resolve(reference: str, bases: Iterable[str], universe: set[str]) -> str | None:
    """First ``base/reference`` that is a known media path."""
    for base in bases:
        joined = posixpath.normpath(posixpath.join(base, reference)) if base else reference
        if joined in universe:
            return joined
    return None


def ledger_references(root: Path, ledger: Ledger, universe: set[str]) -> tuple[set[str], int]:
    """Paths ``ledger`` owns within ``universe`` and the count of references that resolve nowhere."""
    owned: set[str] = set()
    unresolved = 0
    for path in ledger_files(root, ledger):
        document = load_json(path)
        own_dir = path.parent.relative_to(root).as_posix()
        bases = tuple(own_dir if base == "@dir" else base for base in ledger.bases)
        strings = (
            iter_visual_manifest(document)
            if ledger.parser == "visual-manifest"
            else iter_strings(document)
        )
        for text in strings:
            reference = clean_reference(text)
            if reference is None:
                continue
            hit = resolve(reference, bases, universe)
            if hit is None:
                unresolved += 1
            else:
                owned.add(hit)
    return owned, unresolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def byte_copies(root: Path, orphans: Iterable[str], owned: Iterable[str]) -> dict[str, str]:
    """Map each orphan whose bytes equal an owned file to that owned file's path."""
    orphan_list = sorted(orphans)
    sizes = {(root / p).stat().st_size for p in orphan_list}
    by_hash: dict[str, str] = {}
    for path in sorted(owned):
        if (root / path).stat().st_size in sizes:
            by_hash.setdefault(sha256(root / path), path)
    copies: dict[str, str] = {}
    for path in orphan_list:
        original = by_hash.get(sha256(root / path))
        if original is not None:
            copies[path] = original
    return copies


def _partition_scope(paths: Iterable[str]) -> tuple[list[str], dict[str, list[str]]]:
    in_scope: list[str] = []
    excluded: dict[str, list[str]] = {}
    for path in paths:
        reason = scope_reason(path)
        if reason is None:
            in_scope.append(path)
        else:
            excluded.setdefault(reason, []).append(path)
    return sorted(in_scope), excluded


def _owners(
    root: Path, ledgers: Iterable[Ledger], universe: set[str]
) -> tuple[dict[str, list[str]], list[dict]]:
    owners: dict[str, list[str]] = {}
    summary: list[dict] = []
    for ledger in ledgers:
        owned, unresolved = ledger_references(root, ledger, universe)
        if ledger.role != PROJECTION:
            for path in owned:
                owners.setdefault(path, []).append(ledger.name)
        summary.append(
            {
                "name": ledger.name,
                "role": ledger.role,
                "files": [p.relative_to(root).as_posix() for p in ledger_files(root, ledger)],
                "owned_in_scope": len(owned),
                "unresolved_references": unresolved,
            }
        )
    return owners, summary


def run_census(root: Path, ledgers: Iterable[Ledger] = DEFAULT_LEDGERS) -> dict:
    """Build the deterministic census report for ``root``."""
    root = root.resolve()
    found = discover(root)
    present = sorted(set(found["tracked"]) | set(found["untracked"]))
    in_scope, excluded = _partition_scope(present)
    universe = set(in_scope)
    owners, ledger_summary = _owners(root, ledgers, universe)
    unowned = [p for p in in_scope if p not in owners]
    copies = byte_copies(root, unowned, owners)
    orphans = [p for p in unowned if p not in copies]
    untracked = set(found["untracked"])
    by_ledger: dict[str, int] = {}
    for names in owners.values():
        for name in names:
            by_ledger[name] = by_ledger.get(name, 0) + 1
    return {
        "root": root.as_posix(),
        "totals": {
            "present_media": len(present),
            "in_scope": len(in_scope),
            "owned_by_reference": len(owners),
            "owned_by_byte_copy": len(copies),
            "review_only": sum(1 for names in owners.values() if names == [REVIEW_LEDGER]),
            "orphans": len(orphans),
            "excluded": sum(len(v) for v in excluded.values()),
            "tracked_missing_on_disk": len(found["missing_tracked"]),
            "ignored_present": len(found["ignored"]),
        },
        "owned_by_ledger": dict(sorted(by_ledger.items())),
        "ledgers": ledger_summary,
        "excluded_by_reason": {k: len(v) for k, v in sorted(excluded.items())},
        "orphans": [_describe(root, p, p in untracked) for p in orphans],
        "byte_copies": dict(sorted(copies.items())),
        "owners": {p: sorted(owners[p]) for p in sorted(owners)},
        "ignored_present": [_describe(root, p, True) for p in found["ignored"]],
        "tracked_missing_on_disk": found["missing_tracked"],
    }


def _describe(root: Path, path: str, untracked: bool) -> dict:
    return {"path": path, "bytes": (root / path).stat().st_size, "tracked": not untracked}


def main(argv: list[str] | None = None, ledgers: Iterable[Ledger] = DEFAULT_LEDGERS) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="exit 1 when any asset is orphaned")
    mode.add_argument("--report", action="store_true", help="print the JSON report")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    args = parser.parse_args(argv)
    try:
        report = run_census(args.root, ledgers)
    except LedgerError as exc:
        print(f"FAIL (ledger error): {exc}", file=sys.stderr)
        return 2
    if args.report:
        print(json.dumps(report, indent=2, sort_keys=False))
        return 0
    totals = report["totals"]
    if report["orphans"]:
        print(
            f"FAIL: {totals['orphans']} in-scope asset(s) have no owning ledger:", file=sys.stderr
        )
        for row in report["orphans"]:
            print(f"  - {row['path']} ({row['bytes']} bytes)", file=sys.stderr)
        return 1
    if report["tracked_missing_on_disk"]:
        print(
            f"FAIL: {totals['tracked_missing_on_disk']} tracked media file(s) are absent on disk "
            "(sparse or incomplete checkout); the census cannot vouch for them.",
            file=sys.stderr,
        )
        return 1
    print(
        f"PASS: {totals['in_scope']} in-scope assets owned "
        f"({totals['owned_by_reference']} by reference, {totals['owned_by_byte_copy']} byte copies); "
        f"{totals['excluded']} excluded by scope rule."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
