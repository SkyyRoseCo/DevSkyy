"""Generate responsive delivery copies without changing approved source authority."""

import argparse
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"
MANIFEST = THEME / "data/approved-card-fronts.json"
OUTPUT = THEME / "assets/derived/card-fronts"
WIDTHS = (320, 480, 768)


def write_output(destination: Path, payload: bytes) -> None:
    """Replace a generated entry without following a destination symlink."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(payload)
    try:
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def generate(check: bool = False) -> None:
    """Verify source hashes and generate uncropped, proportionate delivery copies."""
    for directory in (OUTPUT, *OUTPUT.parents):
        if directory.is_symlink():
            raise ValueError(f"Symlink output directory: {directory}")
        if directory == THEME:
            break
    OUTPUT.resolve().relative_to(THEME.resolve())
    source = json.loads(MANIFEST.read_text())
    result = {"schema": "skyyrose.card-renditions.v1", "products": {}}
    for sku, record in sorted(source["products"].items()):
        path = (THEME / record["src"]).resolve()
        path.relative_to((THEME / "assets").resolve())
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record["sha256"]:
            raise ValueError(f"Approved source drift: {sku}")
        if not sku or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in sku):
            raise ValueError("Invalid SKU")
        with Image.open(io.BytesIO(raw)) as original:
            if original.size != (record["width"], record["height"]):
                raise ValueError(f"Source dimensions changed: {sku}")
            images = []
            for width in WIDTHS:
                if width >= original.width:
                    continue
                height = round(original.height * width / original.width)
                resized = original.resize((width, height), Image.Resampling.LANCZOS)
                stream = io.BytesIO()
                resized.save(stream, format="WEBP", quality=90, method=6)
                payload = stream.getvalue()
                destination = OUTPUT / f"{sku}-{width}w.webp"
                if destination.is_symlink():
                    raise ValueError(f"Symlink rendition: {destination.name}")
                if check:
                    if not destination.is_file() or destination.read_bytes() != payload:
                        raise ValueError(f"Stale rendition: {destination.name}")
                else:
                    write_output(destination, payload)
                images.append(
                    {
                        "src": destination.relative_to(THEME).as_posix(),
                        "width": width,
                        "height": height,
                        "sha256": hashlib.sha256(payload).hexdigest(),
                    }
                )
            result["products"][sku] = {
                "source": record["src"],
                "source_sha256": record["sha256"],
                "renditions": images,
            }
    manifest = OUTPUT / "manifest.json"
    if manifest.is_symlink():
        raise ValueError("Symlink rendition manifest")
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if check:
        if not manifest.is_file() or manifest.read_text() != encoded:
            raise ValueError("Stale rendition manifest")
    else:
        write_output(manifest, encoded.encode())
    print(
        f"{'Verified' if check else 'Built'} responsive copies of {len(result['products'])} approved card fronts; originals unchanged"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    generate(parser.parse_args().check)
