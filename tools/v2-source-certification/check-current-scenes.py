"""Validate the recovered K1 runtime; legacy pixel-edit verification stays available.

Every chapter must resolve to its hash-bound motion poster and explicit cast.
This certifies recovered source identity, not new visual approval or deployment.
"""

import hashlib
import json
from pathlib import Path

from inputs import ROOT, load_product_sot

THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"
HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def main():
    contract = read(HERE / "current-scenes.json")
    raw = (THEME / "data/collection-scene-motion.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != contract["motion_manifest_sha256"]:
        raise ValueError("Motion contract changed; source reconciliation required")
    motion = json.loads(raw)
    blueprints = read(THEME / "data/scene-narrative-blueprints.json")
    composition = read(THEME / "data/hero-commerce-scenes-c1.json")
    sot, raw_sot = load_product_sot()
    if blueprints["product_sot_sha256"] != hashlib.sha256(raw_sot.encode()).hexdigest():
        raise ValueError("Blueprint product SOT binding drift")
    chapters = {}
    for collection, block in blueprints["collections"].items():
        for chapter in block.get("commerce_scene_chapters", []):
            sid = chapter["scene_id"]
            if sid in chapters:
                raise ValueError("Duplicate scene")
            chapters[sid] = (collection, chapter)
    if set(chapters) != set(contract["scenes"]) or set(chapters) != set(motion["scenes"]):
        raise ValueError("Nine-scene identity mismatch")
    for sid, expected in contract["scenes"].items():
        collection, chapter = chapters[sid]
        record = motion["scenes"][sid]
        if collection != expected["collection"] or collection != record["collection"]:
            raise ValueError(f"Collection drift: {sid}")
        if not chapter["plate_approval_state"].startswith("FOUNDER_APPROVED"):
            raise ValueError(f"Runtime chapter gate fails: {sid}")
        cast = composition["scenes"].get(sid, chapter)["product_bindings"]
        if (
            cast != expected["product_bindings"]
            or chapter["product_bindings"] != expected["blueprint_cast"]
        ):
            raise ValueError(f"Explicit cast drift: {sid}")
        if len(cast) != len(set(cast)) or not cast:
            raise ValueError(f"Invalid cast: {sid}")
        if any(sot["products"][sku]["identity"]["collection"] != collection for sku in cast):
            raise ValueError(f"Cross-collection cast: {sid}")
        if (
            record["founder_approved_visual"] is not True
            or record["local_wiring_authorized"] is not True
        ):
            raise ValueError(f"Existing wiring authorization changed: {sid}")
        if record["poster"] != expected["poster"]:
            raise ValueError(f"Poster binding changed: {sid}")
        for key in ("poster", "desktop", "mobile"):
            raw_path = record[key]
            path = THEME / "assets/scroll-world" / raw_path
            if Path(raw_path).is_absolute() or ".." in Path(raw_path).parts or path.is_symlink():
                raise ValueError(f"Unsafe motion path: {sid}")
            path.resolve().relative_to((THEME / "assets/scroll-world").resolve())
            if not path.is_file():
                raise ValueError(f"Missing current runtime asset: {sid} {key}")
        poster = THEME / "assets/scroll-world" / record["poster"]
        if hashlib.sha256(poster.read_bytes()).hexdigest() != expected["poster_sha256"]:
            raise ValueError(f"Poster hash drift: {sid}")
        if {v["asset"] for v in record["variants"]} != {record["desktop"], record["mobile"]}:
            raise ValueError(f"Unbound motion rendition: {sid}")
    # Require explicitly recorded runtime hashes; Phase 2 repairs update only their
    # affected entries, with baseline lineage and regression evidence in tasks/.
    for relative, digest in read(HERE / "runtime-php-baseline.json").items():
        if hashlib.sha256((THEME / relative).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Runtime PHP differs from recorded baseline: {relative}")
    print("PASS current K1 scenes, posters, SKU casts, SOT binding and hash-bound runtime PHP")


if __name__ == "__main__":
    main()
