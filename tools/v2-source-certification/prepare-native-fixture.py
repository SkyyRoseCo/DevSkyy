"""Fetch only the hash-pinned native files needed by the database-free gallery test."""

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
PINS = ROOT / "tools/v2-runtime/fixtures/pdp-native-template-hashes.json"
SOURCES = {
    "wp-includes/plugin.php": "https://core.svn.wordpress.org/tags/7.1/wp-includes/plugin.php",
    "wp-includes/class-wp-hook.php": "https://core.svn.wordpress.org/tags/7.1/wp-includes/class-wp-hook.php",
    "wp-includes/class-wp-filter-sentinel.php": "https://core.svn.wordpress.org/tags/7.1/wp-includes/class-wp-filter-sentinel.php",
    "wp-content/plugins/woocommerce/includes/wc-template-functions.php": "https://raw.githubusercontent.com/woocommerce/woocommerce/11.1.0/plugins/woocommerce/includes/wc-template-functions.php",
    "wp-content/plugins/woocommerce/templates/single-product/product-image.php": "https://raw.githubusercontent.com/woocommerce/woocommerce/11.1.0/plugins/woocommerce/templates/single-product/product-image.php",
    "wp-content/plugins/woocommerce/templates/single-product/product-thumbnails.php": "https://raw.githubusercontent.com/woocommerce/woocommerce/11.1.0/plugins/woocommerce/templates/single-product/product-thumbnails.php",
    "wp-content/plugins/woocommerce/templates/single-product/add-to-cart/variable.php": "https://raw.githubusercontent.com/woocommerce/woocommerce/11.1.0/plugins/woocommerce/templates/single-product/add-to-cart/variable.php",
}


def prepare(destination: Path) -> None:
    """Validate every downloaded byte before creating a new isolated fixture root."""
    pins = json.loads(PINS.read_text())
    if (
        pins.get("schema") != "skyyrose.pdp-native-template-hashes.v1"
        or pins.get("wordpress") != "7.1"
        or pins.get("woocommerce") != "11.1.0"
        or set(pins.get("files", {})) != set(SOURCES)
    ):
        raise ValueError("Native fixture manifest differs from the declared versions/files")
    if destination.exists() or destination.is_symlink():
        raise ValueError("Fixture destination must not already exist")
    files = {}
    for relative, url in SOURCES.items():
        with urlopen(url, timeout=30) as response:
            data = response.read(2_000_001)
        if len(data) > 2_000_000 or hashlib.sha256(data).hexdigest() != pins["files"][relative]:
            raise ValueError(f"Native fixture SHA-256 mismatch: {relative}")
        files[relative] = data
    destination.mkdir(parents=True, exist_ok=False)
    for relative, data in files.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"PASS {len(files)} native fixture hashes; WordPress 7.1 / WooCommerce 11.1.0")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    prepare(parser.parse_args().destination)
