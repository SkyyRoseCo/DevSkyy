#!/usr/bin/env python3
"""Atomically reconstruct a complete theme from core plus required brand media."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

THEME_SLUG = "skyyrose-flagship-2"
MAX_MEDIA_BYTES = 512 * 1024 * 1024
MAX_ENTRY_BYTES = 256 * 1024 * 1024
MAX_COMPRESSION_RATIO = 250


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def load_manifest(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text())
    if (
        data.get("schema") != "skyyrose.marketplace-split.v1"
        or data.get("theme_slug") != THEME_SLUG
    ):
        raise ValueError(f"unsupported manifest: {path}")
    if (
        not isinstance(data.get("package"), str)
        or not isinstance(data.get("files"), dict)
        or not isinstance(data.get("required_for_complete_storefront"), bool)
        or not isinstance(data.get("total_bytes"), int)
        or data["total_bytes"] < 0
    ):
        raise ValueError(f"malformed manifest: {path}")
    byte_total = 0
    for name, record in data["files"].items():
        validate_archive_path(name)
        if (
            not isinstance(record, dict)
            or not isinstance(record.get("bytes"), int)
            or record["bytes"] < 0
            or not isinstance(record.get("sha256"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", record["sha256"])
        ):
            raise ValueError(f"malformed manifest record: {name}")
        byte_total += record["bytes"]
    if byte_total != data["total_bytes"]:
        raise ValueError(f"manifest byte total mismatch: {path}")
    return data


def validate_archive_path(name: str) -> PurePosixPath:
    if not isinstance(name, str) or "\\" in name:
        raise ValueError(f"unsafe archive path: {name}")
    windows = PureWindowsPath(name)
    path = PurePosixPath(name)
    if (
        windows.drive
        or windows.is_absolute()
        or path.is_absolute()
        or ".." in path.parts
        or not path.parts
        or path.parts[0] != THEME_SLUG
    ):
        raise ValueError(f"unsafe archive path: {name}")
    return path


def verify_tree(root: Path, manifest: dict[str, object], *, exact: bool = False) -> None:
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("manifest files must be an object")
    for archive_path, record in files.items():
        path = validate_archive_path(archive_path)
        target = root.joinpath(*path.parts[1:])
        if not target.is_file() or target.is_symlink():
            raise ValueError(f"missing or unsafe installed file: {archive_path}")
        if target.stat().st_size != record["bytes"] or digest(target) != record["sha256"]:
            raise ValueError(f"installed file integrity mismatch: {archive_path}")
    if exact:
        actual = {
            f"{THEME_SLUG}/{path.relative_to(root).as_posix()}"
            for path in root.rglob("*")
            if path.is_file() and not path.is_symlink()
        }
        if actual != set(files):
            extras = sorted(actual - set(files))
            missing = sorted(set(files) - actual)
            raise ValueError(
                f"installed payload membership mismatch: extras={extras}, missing={missing}"
            )


def safe_extract(archive: zipfile.ZipFile, staging_theme: Path, allowed: dict[str, object]) -> None:
    entries = [info for info in archive.infolist() if not info.is_dir()]
    names = [info.filename for info in entries]
    if len(names) != len(set(names)):
        raise ValueError("media archive contains duplicate paths")
    allowed_paths = set(allowed)
    actual_paths = set(names)
    if actual_paths != allowed_paths:
        raise ValueError(
            f"media archive membership mismatch: extras={sorted(actual_paths - allowed_paths)}, "
            f"missing={sorted(allowed_paths - actual_paths)}"
        )
    total = 0
    staging_resolved = staging_theme.resolve()
    for info in entries:
        path = validate_archive_path(info.filename)
        mode = info.external_attr >> 16
        if mode and (mode & 0o170000) not in (0, 0o100000):
            raise ValueError(f"non-regular archive entry: {info.filename}")
        expected = allowed[info.filename]
        if info.file_size != expected["bytes"] or info.file_size > MAX_ENTRY_BYTES:
            raise ValueError(f"media archive size mismatch: {info.filename}")
        if (
            info.file_size
            and info.compress_size
            and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO
        ):
            raise ValueError(f"media archive compression ratio rejected: {info.filename}")
        total += info.file_size
        if total > MAX_MEDIA_BYTES:
            raise ValueError("media archive expanded size exceeds safety cap")
        destination = staging_theme.joinpath(*path.parts[1:])
        if not destination.resolve(strict=False).is_relative_to(staging_resolved):
            raise ValueError(f"archive path escapes staging root: {info.filename}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(info) as source, destination.open("wb") as output:
            remaining = info.file_size
            while remaining:
                block = source.read(min(1024 * 1024, remaining))
                if not block:
                    raise ValueError(f"truncated media archive entry: {info.filename}")
                output.write(block)
                remaining -= len(block)
            if source.read(1):
                raise ValueError(f"oversized media archive entry: {info.filename}")


def install(
    theme_dir: Path,
    media_zip: Path,
    media_manifest_path: Path,
    full_manifest_path: Path,
    release_path: Path,
    expected_release_sha256: str,
) -> Path:
    theme_dir = theme_dir.resolve()
    if theme_dir.name != THEME_SLUG or not (theme_dir / "style.css").is_file():
        raise ValueError(f"not an installed {THEME_SLUG} core theme: {theme_dir}")
    media_manifest = load_manifest(media_manifest_path)
    full_manifest = load_manifest(full_manifest_path)
    if (
        media_manifest.get("package") != "required_brand_media"
        or media_manifest.get("required_for_complete_storefront") is not True
        or full_manifest.get("package") != "verified_full_payload"
        or full_manifest.get("required_for_complete_storefront") is not True
    ):
        raise ValueError("manifest package roles are invalid")
    if not expected_release_sha256 or digest(release_path) != expected_release_sha256:
        raise ValueError("split release manifest hash mismatch")
    release = json.loads(release_path.read_text())
    artifacts = release.get("artifacts")
    if release.get("schema") != "skyyrose.marketplace-split-release.v1" or not isinstance(
        artifacts, dict
    ):
        raise ValueError("unsupported split release manifest")
    expected_artifacts = {
        media_zip.name: digest(media_zip),
        media_manifest_path.name: digest(media_manifest_path),
        full_manifest_path.name: digest(full_manifest_path),
    }
    if any(artifacts.get(name) != value for name, value in expected_artifacts.items()):
        raise ValueError("split release artifact hash mismatch")
    if full_manifest.get("source_archive_sha256") != release.get("source_archive_sha256"):
        raise ValueError("full payload source identity mismatch")

    parent = theme_dir.parent
    staging_root = Path(tempfile.mkdtemp(prefix=f".{THEME_SLUG}-install-", dir=parent))
    staging_theme = staging_root / THEME_SLUG
    backup = parent / f".{THEME_SLUG}-rollback"
    if backup.exists():
        raise ValueError(f"rollback path already exists: {backup}")
    try:
        shutil.copytree(theme_dir, staging_theme, symlinks=False)
        with zipfile.ZipFile(media_zip) as archive:
            safe_extract(archive, staging_theme, media_manifest["files"])
        verify_tree(staging_theme, media_manifest)
        verify_tree(staging_theme, full_manifest, exact=True)
        os.replace(theme_dir, backup)
        try:
            os.replace(staging_theme, theme_dir)
        except Exception:
            os.replace(backup, theme_dir)
            raise
        return backup
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme-dir", type=Path, required=True)
    parser.add_argument("--media-zip", type=Path, required=True)
    parser.add_argument("--media-manifest", type=Path, required=True)
    parser.add_argument("--full-manifest", type=Path, required=True)
    parser.add_argument("--release-manifest", type=Path, required=True)
    parser.add_argument("--expected-release-sha256", required=True)
    args = parser.parse_args()
    backup = install(
        args.theme_dir,
        args.media_zip,
        args.media_manifest,
        args.full_manifest,
        args.release_manifest,
        args.expected_release_sha256,
    )
    print(f"Required brand media installed and verified. Rollback copy: {backup}")


if __name__ == "__main__":
    main()
