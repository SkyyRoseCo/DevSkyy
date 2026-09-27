#!/usr/bin/env python3
"""Build deterministic core and required-media archives from a verified V2 bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath

THEME_SLUG = "skyyrose-flagship-2"
MEDIA_EXTENSIONS = {
    ".glb",
    ".jpeg",
    ".jpg",
    ".mp4",
    ".png",
    ".wasm",
    ".webm",
    ".webp",
    ".woff2",
}
CORE_MEDIA_EXCEPTIONS = {f"{THEME_SLUG}/screenshot.png"}
FORBIDDEN_PARTS = {".git", "dist", "node_modules", "vendor"}
SECRET_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"(?:SSH_PASS|SFTP_PASS|OPENAI_API_KEY|STRIPE_SECRET_KEY)\s*="),
    re.compile(rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
)
TEXT_SCAN_LIMIT = 4 * 1024 * 1024
ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_payload_path(name: str) -> PurePosixPath:
    if "\\" in name or PureWindowsPath(name).drive or PureWindowsPath(name).is_absolute():
        raise ValueError(f"unsafe archive path: {name}")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"unsafe archive path: {name}")
    if path.parts[0] != THEME_SLUG:
        raise ValueError(f"unexpected archive root: {name}")
    if any(part in FORBIDDEN_PARTS or part.startswith(".env") for part in path.parts):
        raise ValueError(f"forbidden package path: {name}")
    return path


def classify(name: str) -> str:
    path = safe_payload_path(name)
    if name in CORE_MEDIA_EXCEPTIONS:
        return "core"
    if (
        len(path.parts) > 1
        and path.parts[1] == "assets"
        and path.suffix.lower() in MEDIA_EXTENSIONS
    ):
        return "required_brand_media"
    return "core"


def zip_entry(name: str, data: bytes) -> tuple[zipfile.ZipInfo, bytes]:
    info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.create_system = 3
    return info, data


def write_zip(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name in sorted(entries):
            info, data = zip_entry(name, entries[name])
            output.writestr(info, data)


def manifest(package: str, entries: dict[str, bytes]) -> dict[str, object]:
    return {
        "schema": "skyyrose.marketplace-split.v1",
        "package": package,
        "theme_slug": THEME_SLUG,
        "required_for_complete_storefront": package != "optional_demo",
        "files": {
            name: {"bytes": len(data), "sha256": sha256_bytes(data)}
            for name, data in sorted(entries.items())
        },
        "total_bytes": sum(len(data) for data in entries.values()),
    }


def scan_for_secrets(entries: dict[str, bytes]) -> None:
    for name, data in entries.items():
        if len(data) > TEXT_SCAN_LIMIT or b"\x00" in data[:8192]:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(data):
                raise ValueError(f"secret-shaped content found in {name}")


def build(full_zip: Path, output_dir: Path) -> dict[str, object]:
    expected_hash = sha256_bytes(full_zip.read_bytes())
    core: dict[str, bytes] = {}
    media: dict[str, bytes] = {}
    with zipfile.ZipFile(full_zip) as source:
        for info in source.infolist():
            if info.is_dir():
                continue
            safe_payload_path(info.filename)
            data = source.read(info)
            target = media if classify(info.filename) == "required_brand_media" else core
            if info.filename in target:
                raise ValueError(f"duplicate archive path: {info.filename}")
            target[info.filename] = data

    if set(core) & set(media):
        raise ValueError("core and required-media payloads overlap")
    scan_for_secrets(core)
    scan_for_secrets(media)

    output_dir = output_dir.resolve()
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    if output_dir.exists():
        if any(output_dir.iterdir()):
            raise ValueError(f"refusing to publish into nonempty output directory: {output_dir}")
        output_dir.rmdir()
    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}-", dir=output_dir.parent))
    try:
        core_zip = staging / f"{THEME_SLUG}-core.zip"
        media_zip = staging / f"{THEME_SLUG}-required-media.zip"
        write_zip(core_zip, core)
        write_zip(media_zip, media)

        manifests = {
            "core-manifest.json": manifest("core", core),
            "required-media-manifest.json": manifest("required_brand_media", media),
            "optional-demo-manifest.json": {
                "schema": "skyyrose.marketplace-split.v1",
                "package": "optional_demo",
                "theme_slug": THEME_SLUG,
                "required_for_complete_storefront": False,
                "files": {},
                "total_bytes": 0,
                "note": "No demo-only payload is present in the verified 2.4.4 bundle.",
            },
            "full-payload-manifest.json": {
                **manifest("verified_full_payload", {**core, **media}),
                "source_archive": full_zip.name,
                "source_archive_sha256": expected_hash,
                "partition": {
                    "core_files": len(core),
                    "required_brand_media_files": len(media),
                    "optional_demo_files": 0,
                },
            },
        }
        for filename, content in manifests.items():
            (staging / filename).write_text(json.dumps(content, indent=2, sort_keys=True) + "\n")
        installer_name = "install-required-media.py"
        shutil.copy2(
            Path(__file__).with_name("install_required_media.py"), staging / installer_name
        )
        release = {
            "schema": "skyyrose.marketplace-split-release.v1",
            "source_archive_sha256": expected_hash,
            "artifacts": {
                core_zip.name: sha256_bytes(core_zip.read_bytes()),
                media_zip.name: sha256_bytes(media_zip.read_bytes()),
                **{
                    filename: sha256_bytes((staging / filename).read_bytes())
                    for filename in manifests
                },
                installer_name: sha256_bytes((staging / installer_name).read_bytes()),
            },
        }
        (staging / "split-release.json").write_text(
            json.dumps(release, indent=2, sort_keys=True) + "\n"
        )
        staging.rename(output_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return release


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-zip", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    actual = sha256_bytes(args.full_zip.read_bytes())
    if args.expected_sha256 and actual != args.expected_sha256:
        raise SystemExit(
            f"verified bundle hash mismatch: expected {args.expected_sha256}, got {actual}"
        )
    release = build(args.full_zip, args.output_dir)
    print(json.dumps(release, sort_keys=True))


if __name__ == "__main__":
    main()
