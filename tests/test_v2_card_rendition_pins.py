"""The card-front rendition builder, its manifest and the media gate agree byte-for-byte.

inc/v2-media-eligibility.php admits a card-front rendition only when the
manifest's builder_sha256 equals a constant in PHP and the manifest's own sha256
equals the pin in v2-media-eligibility.json. Reformatting the builder (one blank
line from isort did it) or rebuilding with a different builder rejects every
rendition at runtime while each file still looks fine on its own.
"""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"
BUILDER = ROOT / "tools/v2-runtime/build-card-renditions.py"
MANIFEST = THEME / "assets/derived/card-fronts/manifest.json"
ELIGIBILITY = THEME / "data/v2-media-eligibility.json"
GATE = THEME / "inc/v2-media-eligibility.php"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _gate_builder_sha() -> str:
    found = re.findall(r"'builder_sha256' => '([a-f0-9]{64})'", GATE.read_text(encoding="utf-8"))
    assert len(found) == 1, found
    return found[0]


def test_builder_bytes_match_the_gate():
    assert _sha256(BUILDER) == _gate_builder_sha()


def test_manifest_records_the_gated_builder():
    products = json.loads(MANIFEST.read_text(encoding="utf-8"))["products"]
    assert products
    recorded = {entry["encoding"]["builder_sha256"] for entry in products.values()}
    assert recorded == {_gate_builder_sha()}


def test_eligibility_pins_the_current_manifest():
    assets = json.loads(ELIGIBILITY.read_text(encoding="utf-8"))["assets"]
    pins = {
        record["delivery_manifest"]["sha256"]
        for record in assets.values()
        if isinstance(record.get("delivery_manifest"), dict)
    }
    assert pins == {_sha256(MANIFEST)}
