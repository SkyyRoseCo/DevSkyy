"""Read-only V2 size projection from the single product entry point."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile

from skyyrose.core import product, product_registry

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "wordpress-theme/skyyrose-flagship/data/logo-registry.json"
OUTPUT = ROOT / "wordpress-theme/skyyrose-flagship-2/data/simple-product-sizes.json"


def encoded(value: object) -> bytes:
    """One deterministic UTF-8 representation shared with the PHP consumer."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def build() -> dict:
    """Bind exact string sizes to a coherent canonical registry/reader snapshot."""
    before = CANONICAL.read_bytes()
    digest = hashlib.sha256(before).hexdigest()
    source = json.loads(before)
    skus = sorted(product.all_skus())
    if not isinstance(source.get("products"), dict) or skus != sorted(source["products"]):
        raise ValueError("Unified canonical product membership differs")
    records = {}
    for sku in skus:
        record = product.get_product(sku)
        sizes = record["garment"]["available_sizes"]
        if (
            not isinstance(sizes, list)
            or not sizes
            or any(
                not isinstance(size, str)
                or not size
                or len(size) > 64
                or any(ord(char) < 32 for char in size)
                for size in sizes
            )
            or len(set(sizes)) != len(sizes)
        ):
            raise ValueError(f"Canonical size strings missing or malformed: {sku}")
        if record["provenance"]["sources"]["registry"]["sha256"] != digest[:16]:
            raise ValueError("Reader returned a different registry snapshot")
        records[sku] = {"sizes": sizes}
    if CANONICAL.read_bytes() != before:
        raise ValueError("Registry changed during size projection")
    return {
        "schema": "skyyrose.simple-product-sizes.v1",
        "product_registry_sha256": digest,
        "source_reader_sha256": hashlib.sha256(Path(product.__file__).read_bytes()).hexdigest(),
        "products_sha256": hashlib.sha256(encoded(records)).hexdigest(),
        "products": records,
    }


def reconcile(check: bool, output: Path = OUTPUT) -> list[str]:
    """Participate in canonical sync/check; never alter a fixture registry."""
    if product_registry.PRODUCT_REGISTRY != CANONICAL:
        return []
    if any(path.is_symlink() for path in (output, *output.parents)):
        raise ValueError("Size projection symlink path refused")
    body = (json.dumps(build(), ensure_ascii=False, indent=2) + "\n").encode()
    if output.is_file() and output.read_bytes() == body:
        return []
    if not check:
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as stream:
                temporary = Path(stream.name)
                os.fchmod(stream.fileno(), 0o644)
                stream.write(body)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, output)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink()
    return [str(output)]
