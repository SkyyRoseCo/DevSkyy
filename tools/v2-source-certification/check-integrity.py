"""Build/release integrity boundary; does not grant visual or commerce approval."""

import hashlib
import json
import platform
import subprocess
from collections import Counter
from pathlib import Path

from inputs import ROOT, garment_types, load_product_sot
from PIL import Image
from PIL import __version__ as pillow_version

THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"


def asset(raw, expected, width=None, height=None):
    if not isinstance(raw, str) or Path(raw).is_absolute() or ".." in Path(raw).parts:
        raise ValueError(f"Unsafe asset path: {raw!r}")
    path = THEME / raw
    path.resolve().relative_to((THEME / "assets").resolve())
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Asset hash drift: {raw}")
    if width is not None:
        with Image.open(path) as im:
            if im.size != (width, height):
                raise ValueError(f"Asset dimension drift: {raw}")


def main():
    contract = json.loads(Path(__file__).with_name("build-inputs.json").read_text())
    if platform.python_version() != contract["python"] or pillow_version != "12.3.0":
        raise ValueError("Use the declared Python 3.12.12 / Pillow 12.3.0 toolchain")
    for tool in ("node", "npm"):
        actual = subprocess.check_output([tool, "--version"], text=True).strip().lstrip("v")
        if actual != contract[tool]:
            raise ValueError(f"Use declared {tool} version {contract[tool]}, found {actual}")
    for relative, digest in contract["input_hashes"].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Build input changed without reconciliation: {relative}")
    manifest, _ = load_product_sot()
    garment_types(manifest)
    fronts = json.loads((THEME / "data/approved-card-fronts.json").read_text())
    if fronts["schema_version"] != 1 or set(fronts["products"]) != set(manifest["products"]):
        raise ValueError("Approved-front SKU/schema mismatch")
    for record in fronts["products"].values():
        asset(record["src"], record["sha256"], record["width"], record["height"])
    opening = json.loads((THEME / "data/opening-product-media.json").read_text())
    states = Counter(r.get("status", "APPROVED") for r in opening["products"].values())
    if states != {
        "STALE_PRODUCT_HASH": 16,
        "MISSING_APPROVED_ON_MODEL_FRONT": 9,
        "REJECTED_AUTHENTICITY": 5,
        "APPROVED": 3,
    }:
        raise ValueError(f"Media truth changed: {dict(states)}")
    motion = json.loads((THEME / "data/collection-scene-motion.json").read_text())
    if len(motion["scenes"]) != 9:
        raise ValueError("Motion scene set changed")
    for scene in motion["scenes"].values():
        for variant in scene["variants"]:
            asset("assets/scroll-world/" + variant["asset"], variant["sha256"])
    print("PASS 33 front hashes/dimensions; media states 16/9/5/3; 18 motion variant hashes")


if __name__ == "__main__":
    main()
