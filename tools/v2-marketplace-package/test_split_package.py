#!/usr/bin/env python3
"""Regression tests for the V2 marketplace package split and installer."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from build_split_package import THEME_SLUG, build
from install_required_media import install, verify_tree

ROOT = Path(__file__).resolve().parents[2]
FULL_ZIP = ROOT / "wordpress-theme" / THEME_SLUG / "dist" / f"{THEME_SLUG}.zip"
EXPECTED_FULL_SHA = "e1a35cc901854714f471e1256e6f2aa60a4610788c07f033a65f7cc65f67ce5d"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SplitPackageTest(unittest.TestCase):
    def test_split_union_and_atomic_install(self) -> None:
        self.assertEqual(EXPECTED_FULL_SHA, sha(FULL_ZIP))
        with tempfile.TemporaryDirectory(prefix="skyyrose-package-test-") as temporary:
            root = Path(temporary)
            output = root / "artifacts"
            first_release = build(FULL_ZIP, output)
            first_hashes = first_release["artifacts"]
            second = root / "artifacts-second"
            second_release = build(FULL_ZIP, second)
            self.assertEqual(first_hashes, second_release["artifacts"])

            core_manifest = json.loads((output / "core-manifest.json").read_text())
            media_manifest = json.loads((output / "required-media-manifest.json").read_text())
            full_manifest = json.loads((output / "full-payload-manifest.json").read_text())
            optional_manifest = json.loads((output / "optional-demo-manifest.json").read_text())
            core_files = set(core_manifest["files"])
            media_files = set(media_manifest["files"])
            full_files = set(full_manifest["files"])

            self.assertFalse(core_files & media_files)
            self.assertEqual(full_files, core_files | media_files)
            self.assertFalse(optional_manifest["required_for_complete_storefront"])
            self.assertEqual({}, optional_manifest["files"])
            self.assertTrue(media_manifest["required_for_complete_storefront"])
            self.assertIn(
                f"{THEME_SLUG}/assets/approved-card-fronts/br-002-onmodel.webp", media_files
            )
            self.assertTrue(
                any(path.endswith(".mp4") and "/assets/video/" in path for path in media_files)
            )
            self.assertIn(f"{THEME_SLUG}/assets/css/theme.min.css", core_files)
            self.assertIn(f"{THEME_SLUG}/screenshot.png", core_files)
            self.assertFalse(
                any(
                    "node_modules" in path or "/dist/" in path or ".env" in path
                    for path in full_files
                )
            )

            install_root = root / "wp-content" / "themes"
            install_root.mkdir(parents=True)
            with zipfile.ZipFile(output / f"{THEME_SLUG}-core.zip") as archive:
                archive.extractall(install_root)
            theme_dir = install_root / THEME_SLUG
            self.assertFalse(
                (theme_dir / "assets/approved-card-fronts/br-002-onmodel.webp").exists()
            )
            backup = install(
                theme_dir,
                output / f"{THEME_SLUG}-required-media.zip",
                output / "required-media-manifest.json",
                output / "full-payload-manifest.json",
                output / "split-release.json",
                sha(output / "split-release.json"),
            )
            verify_tree(theme_dir, full_manifest)
            self.assertTrue(
                (theme_dir / "assets/approved-card-fronts/br-002-onmodel.webp").is_file()
            )
            self.assertTrue(backup.is_dir())

            rebuilt = {
                f"{THEME_SLUG}/{path.relative_to(theme_dir).as_posix()}": hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in theme_dir.rglob("*")
                if path.is_file()
            }
            self.assertEqual(
                {name: record["sha256"] for name, record in full_manifest["files"].items()},
                rebuilt,
            )
            shutil.rmtree(backup)

    def test_tampered_media_is_rejected_without_mutating_core(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skyyrose-package-negative-") as temporary:
            root = Path(temporary)
            output = root / "artifacts"
            build(FULL_ZIP, output)
            install_root = root / "wp-content" / "themes"
            install_root.mkdir(parents=True)
            with zipfile.ZipFile(output / f"{THEME_SLUG}-core.zip") as archive:
                archive.extractall(install_root)
            theme_dir = install_root / THEME_SLUG
            original_style_hash = sha(theme_dir / "style.css")

            bad_dir = root / "tampered"
            bad_dir.mkdir()
            bad_zip = bad_dir / f"{THEME_SLUG}-required-media.zip"
            shutil.copy2(output / f"{THEME_SLUG}-required-media.zip", bad_zip)
            with zipfile.ZipFile(bad_zip, "a") as archive:
                archive.writestr(f"{THEME_SLUG}/unexpected.php", b"<?php echo 'unexpected';")
            with self.assertRaisesRegex(ValueError, "split release artifact hash mismatch"):
                install(
                    theme_dir,
                    bad_zip,
                    output / "required-media-manifest.json",
                    output / "full-payload-manifest.json",
                    output / "split-release.json",
                    sha(output / "split-release.json"),
                )
            self.assertEqual(original_style_hash, sha(theme_dir / "style.css"))
            self.assertFalse((theme_dir / "unexpected.php").exists())
            self.assertFalse((install_root / f".{THEME_SLUG}-rollback").exists())

    def test_windows_traversal_and_stale_publication_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skyyrose-package-paths-") as temporary:
            root = Path(temporary)
            output = root / "artifacts"
            output.mkdir()
            (output / "obsolete-release.zip").write_bytes(b"old")
            with self.assertRaisesRegex(ValueError, "nonempty output directory"):
                build(FULL_ZIP, output)

            from build_split_package import safe_payload_path
            from install_required_media import validate_archive_path

            malicious = f"{THEME_SLUG}/assets\\..\\..\\evil.php"
            with self.assertRaisesRegex(ValueError, "unsafe archive path"):
                safe_payload_path(malicious)
            with self.assertRaisesRegex(ValueError, "unsafe archive path"):
                validate_archive_path(malicious)


if __name__ == "__main__":
    unittest.main()
