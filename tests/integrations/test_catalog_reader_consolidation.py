"""Static regression guards — every catalog reader must route through the
canonical `skyyrose.core.catalog_loader.read_catalog_rows`.

Closes D8 of the plan. The read-only adapters below project catalog rows from
the canonical reader instead of parsing the CSV themselves; these tests keep
the divergent pattern from creeping back in. (The original divergent reader,
`scripts/nano-banana-vton.py`, was deleted with the retired render engine.)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.mark.parametrize(
    "relative_path",
    [
        "scripts/nano_banana/catalog.py",
        "scripts/openai_feed/catalog.py",
        "scripts/oai_render/references.py",
        "skyyrose/elite_studio/fashion/context.py",
    ],
)
def test_read_only_catalog_adapters_use_canonical_reader(relative_path: str) -> None:
    """Read-only adapters must project catalog rows instead of parsing CSV themselves."""
    source = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
    assert "csv.DictReader" not in source, f"{relative_path} parses the catalog directly"
    assert re.search(
        r"from skyyrose\.core\.catalog_loader import [^\n]*\bread_catalog_rows\b", source
    ), f"{relative_path} must import the canonical reader"
    assert re.search(
        r"\bread_catalog_rows\s*\(", source
    ), f"{relative_path} imports but does not call the canonical reader"
    assert not re.search(
        r"^\s*(?:import\s+csv\b|from\s+csv\b)", source, re.MULTILINE
    ), f"{relative_path} must not import a local CSV parser"
    assert not re.search(
        r"\b(?:open|read_text)\s*\([^)]*catalog[^)]*\.csv",
        source,
        re.IGNORECASE | re.DOTALL,
    ), f"{relative_path} must not open a catalog CSV directly"


def test_read_only_catalog_adapters_filter_blank_skus(monkeypatch, tmp_path: Path) -> None:
    """Adapters preserve the canonical reader's blank-row safety guarantee."""
    from scripts.nano_banana import catalog as nano_catalog
    from scripts.oai_render import config as oai_config
    from scripts.oai_render import references as oai_references
    from scripts.openai_feed import catalog as feed_catalog
    from skyyrose.elite_studio.fashion import context as fashion_context

    canonical_rows = [
        {
            "sku": "   ",
            "name": "ignored",
            "collection": "ignored",
            "is_preorder": "0",
            "render_output_slug": "",
            "render_is_tech_flat": "0",
            "render_is_accessory": "0",
            "render_source_override": "",
            "render_back_source_override": "",
        },
        {
            "sku": "br-001",
            "name": "BLACK Rose Crewneck",
            "collection": "black-rose",
            "is_preorder": "0",
            "render_output_slug": "",
            "render_is_tech_flat": "1",
            "render_is_accessory": "0",
            "render_source_override": "",
            "render_back_source_override": "",
        },
    ]
    catalog_path = tmp_path / "catalog.csv"
    catalog_path.write_text("sku\n", encoding="utf-8")

    monkeypatch.setattr(nano_catalog, "read_catalog_rows", lambda _path: canonical_rows)
    monkeypatch.setattr(feed_catalog, "read_catalog_rows", lambda _path: canonical_rows)
    monkeypatch.setattr(oai_references, "read_catalog_rows", lambda _path: canonical_rows)
    monkeypatch.setattr(fashion_context, "read_catalog_rows", lambda _path: canonical_rows)
    monkeypatch.setattr(oai_config, "CATALOG_CSV", catalog_path)
    monkeypatch.setattr(fashion_context, "_catalog_cache", None)

    assert set(nano_catalog.load_catalog()) == {"br-001"}
    assert set(feed_catalog.load_catalog(catalog_path)) == {"br-001"}
    assert set(oai_references.load_catalog()) == {"br-001"}
    assert set(fashion_context._load_catalog()) == {"br-001"}


class TestCanonicalReaderAuthority:
    """The canonical reader at skyyrose.core.catalog_loader must remain authoritative."""

    def test_canonical_reader_exists(self) -> None:
        from skyyrose.core.catalog_loader import read_catalog_rows

        rows = read_catalog_rows()
        assert isinstance(rows, list)
        assert len(rows) > 0, "canonical reader returned empty catalog"

    def test_canonical_returns_sku_keyed_rows(self) -> None:
        from skyyrose.core.catalog_loader import read_catalog_rows

        rows = read_catalog_rows()
        assert all("sku" in row for row in rows), "every catalog row must have a sku field"


class TestValidateDossierReadersCoverage:
    """validate_dossier_readers() must include every importable catalog-reading module."""

    def test_audit_includes_all_three_readers(self) -> None:
        from skyyrose.elite_studio.config import validate_dossier_readers

        results = validate_dossier_readers(sku="br-001")
        # Three readers per D8 plan: core, elite_studio, nano_banana
        expected_readers = {
            "skyyrose.core.catalog_loader",
            "skyyrose.elite_studio.catalog",
            "scripts.nano_banana.catalog",
        }
        actual_readers = set(results.keys())
        assert expected_readers.issubset(actual_readers), (
            f"validate_dossier_readers() missing readers: "
            f"{expected_readers - actual_readers}. "
            f"Got: {sorted(actual_readers)}"
        )
