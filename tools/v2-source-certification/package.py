"""Deterministic runtime allowlist packager. Call through npm run package:theme."""

import hashlib
import json
import os
import platform
import re
import subprocess
import zipfile
import zlib
from pathlib import Path

from inputs import ROOT

HERE = Path(__file__).resolve().parent
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    boundary = json.loads((HERE / "package-boundary.json").read_text())["files"]
    expected = set(boundary)
    actual = {
        p.relative_to(THEME).as_posix()
        for p in THEME.rglob("*")
        if p.is_file()
        and not set(p.relative_to(THEME).parts) & {"node_modules", "dist", "__pycache__"}
        and p.name not in {".DS_Store", "package-lock.json"}
    }
    if actual != expected:
        raise ValueError(f"Unclassified or missing theme source: {sorted(actual ^ expected)}")
    out = THEME / "dist"
    out.mkdir(exist_ok=True)
    archive = out / "skyyrose-flagship-2.zip"
    selected = [p for p in sorted(boundary) if boundary[p]["release"]]
    # Stored ZIP avoids platform-specific compressor bytes; media is precompressed.
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as bundle:
        for relative in selected:
            if any(
                part in {".DS_Store", "__MACOSX"} or part.startswith("._")
                for part in Path(relative).parts
            ):
                raise ValueError(f"Filesystem metadata is not a runtime asset: {relative}")
            path = THEME / relative
            if path.is_symlink():
                raise ValueError(f"Symlink not permitted: {relative}")
            path.resolve().relative_to(THEME.resolve())
            if any(x in Path(relative).parts for x in (".git", "node_modules", "qa", "scripts")):
                raise ValueError(f"Internal file in package: {relative}")
            content = path.read_bytes()
            if path.suffix in {".php", ".css", ".js", ".json", ".html"}:
                if re.search(rb"""(?:["'\s])/(?:Users|home)/""", content):
                    raise ValueError(f"Workstation path in package: {relative}")
            entry = zipfile.ZipInfo("skyyrose-flagship-2/" + relative, (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            bundle.writestr(entry, content)
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None or len(bundle.namelist()) != len(selected):
            raise ValueError("ZIP integrity failed")
        for relative in selected:
            if hashlib.sha256(bundle.read("skyyrose-flagship-2/" + relative)).hexdigest() != sha(
                THEME / relative
            ):
                raise ValueError(f"ZIP content drift: {relative}")
    source_tree = os.environ.get("V2_SOURCE_TREE")
    if source_tree:
        if not re.fullmatch("[0-9a-f]{40}", source_tree):
            raise ValueError("V2_SOURCE_TREE must identify a Git tree export")
        commit, clean = None, None
    else:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True
        )
        clean = not bool(status.strip())
    inputs = json.loads((HERE / "build-inputs.json").read_text())
    release = {
        "schema": "skyyrose.v2.release-manifest.v1",
        "git_commit": commit,
        "source_tree": source_tree,
        "source_clean": clean,
        "deployment_authorized": False,
        "build_id": sha(HERE / "build-inputs.json"),
        "artifact_sha256": sha(archive),
        "theme_slug": "skyyrose-flagship-2",
        "theme_version": json.loads((THEME / "package.json").read_text())["version"],
        "toolchain": {
            "node": subprocess.check_output(["node", "--version"], text=True).strip(),
            "npm": subprocess.check_output(["npm", "--version"], text=True).strip(),
            "python": platform.python_version(),
            "zlib": zlib.ZLIB_VERSION,
            "zip_compression": "STORED",
        },
        "historical_catalog_sha256": inputs["catalog_sha256"],
        "current_registry_sha256": inputs["current_registry_sha256"],
        "product_sot_scope": "historical_media_binding_only",
        "product_sot_sha256": inputs["product_sot_sha256"],
        "registry_sha256": sha(THEME / "data/product-presentation-registry.json"),
        "runtime_manifests": {p: sha(THEME / p) for p in selected if p.startswith("data/")},
        "files": {p: sha(THEME / p) for p in selected},
    }
    (out / "release-manifest.json").write_text(json.dumps(release, indent=2, sort_keys=True) + "\n")
    print(f"Validated {len(selected)} runtime package entries; SHA-256 {sha(archive)}")


if __name__ == "__main__":
    main()
