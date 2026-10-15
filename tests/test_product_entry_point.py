"""Gate for the single product entry point: one call, complete or declared.

The contract these tests defend: an agent calling
``skyyrose.core.product.get_product`` either receives a fact, or receives that
fact's name in ``gaps``. A silent blank is the failure mode -- an agent handed
an empty description writes copy from imagination (the contamination class
behind bug-096), and one handed a silently substituted front image renders the
wrong garment (lh-005). Both look like success to a caller, so they are tested
for explicitly here.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from skyyrose.core.paths import REPO_ROOT
from skyyrose.core.product import (
    IMAGE_ROLES,
    all_skus,
    gap_report,
    get_all_products,
    get_product,
    provenance,
)

REQUIRED_SECTIONS = (
    "sku",
    "name",
    "collection",
    "catalog",
    "garment",
    "dossier",
    "images",
    "render_sources",
    "logos",
    "content",
    "alt_text",
    "corrections",
    "render_policy",
    "authority",
    "gaps",
    "provenance",
)

CONTENT_FIELDS = ("description", "short_description", "seo_meta", "instagram", "tiktok")

# SKUs whose description is served from the registry's editorial layer
# (products[sku].content) rather than the catalog base line. Every SKU HAS a
# description -- this set is about which layer serves it. Pinned so that
# enriching one (good) or silently demoting one (a regression) both fail here
# and force a deliberate update.
#
# Empty since 2026-09-18: the 19 records in skyyrose/assets/data/product-content.json
# are no longer served. They were written by skyyrose/build/gemini-content.js from
# its own hard-coded 20-SKU table; 11 of 19 carry a different product name than
# the registry and 5 describe a different garment (lh-006 "The Fannie" on the
# white joggers). Copy returns through the registry once the founder approves it.
KNOWN_ENRICHED_SKUS: frozenset[str] = frozenset()

# The only two places product copy may come from: the registry's editorial layer
# and its catalog base line. Anything else is a side store leaking back in.
REGISTRY_COPY_SOURCES = frozenset({"registry.content", "registry.catalog.description"})


@pytest.fixture(scope="module")
def records() -> dict[str, dict]:
    """Every product record, assembled once."""
    return get_all_products()


def test_every_registry_sku_resolves(records: dict[str, dict]) -> None:
    assert set(records) == set(all_skus())
    assert len(records) >= 33, f"expected at least 33 SKUs, got {len(records)}"


def test_every_record_carries_every_section(records: dict[str, dict]) -> None:
    for sku, record in records.items():
        missing = [key for key in REQUIRED_SECTIONS if key not in record]
        assert not missing, f"{sku} is missing sections: {missing}"


def test_identity_fields_are_never_blank(records: dict[str, dict]) -> None:
    """Name and collection are load-bearing everywhere; they may never be empty."""
    for sku, record in records.items():
        assert record["name"], f"{sku} has no name"
        assert record["collection"], f"{sku} has no collection"
        assert record["sku"] == sku


def test_every_content_field_declares_its_layer(records: dict[str, dict]) -> None:
    """Copy is either absent-and-declared, or present with its source named."""
    for sku, record in records.items():
        for field in CONTENT_FIELDS:
            entry = record["content"][field]
            if entry is None:
                assert (
                    f"content.{field}" in record["gaps"]
                ), f"{sku}: content.{field} is absent but not in gaps"
                continue
            assert entry["value"].strip(), f"{sku}: content.{field} is whitespace"
            assert entry["source"], f"{sku}: content.{field} does not name its source"
            if not entry["enriched"]:
                assert f"content.{field}.enriched" in record["gaps"], (
                    f"{sku}: content.{field} came from {entry['source']} "
                    "without declaring it is the base layer"
                )


def test_every_sku_has_a_description(records: dict[str, dict]) -> None:
    """All 33 products carry a description -- this is the copy the store serves."""
    for sku, record in records.items():
        entry = record["content"]["description"]
        assert entry is not None, f"{sku} has no description from any layer"
        assert len(entry["value"]) > 20, f"{sku} description is too short to be real copy"


def test_every_absent_image_role_is_declared(records: dict[str, dict]) -> None:
    """An absent image role must be None AND named in gaps, never substituted."""
    for sku, record in records.items():
        for role in IMAGE_ROLES:
            entry = record["images"][role]
            if entry is None:
                assert (
                    f"images.{role}" in record["gaps"]
                ), f"{sku}: images.{role} is absent but not in gaps"
                continue
            assert entry["path"], f"{sku}: images.{role} has an empty path"
            assert not entry["path"].startswith("/"), f"{sku}: images.{role} path is absolute"
            if not entry["role_asset"]:
                assert (
                    f"images.{role}.fallback" in record["gaps"]
                ), f"{sku}: images.{role} fell back to {entry['source_key']} without declaring it"


def test_dossier_is_present_for_every_sku(records: dict[str, dict]) -> None:
    """Every SKU has the founder's design specification bound. Hard requirement."""
    for sku, record in records.items():
        dossier = record["dossier"]
        assert dossier, f"{sku} has an empty dossier"
        assert dossier.get("garment_type_lock"), f"{sku} dossier has no garment_type_lock"


def test_enriched_skus_match_the_pinned_set(records: dict[str, dict]) -> None:
    """Which SKUs have editorial copy is founder-facing; changes are deliberate."""
    actual = {
        sku
        for sku, record in records.items()
        if "content.description.enriched" not in record["gaps"]
    }
    assert actual == KNOWN_ENRICHED_SKUS, (
        f"enriched set changed.\n  newly enriched: {sorted(actual - KNOWN_ENRICHED_SKUS)}\n"
        f"  newly demoted:  {sorted(KNOWN_ENRICHED_SKUS - actual)}\n"
        "Update KNOWN_ENRICHED_SKUS when the founder adds editorial copy."
    )


def test_copy_written_for_another_product_is_never_served(records: dict[str, dict]) -> None:
    """The retired side-store copy (lh-006 described as a fanny pack) cannot resurface."""
    lh006 = records["lh-006"]
    assert lh006["name"] == "Love Hurts Joggers (White)"
    served = " ".join(entry["value"] for entry in lh006["content"].values() if entry is not None)
    assert "Fannie" not in served and "fanny" not in served.lower()
    for sku, record in records.items():
        for field, entry in record["content"].items():
            if entry is not None:
                assert (
                    entry["source"] in REGISTRY_COPY_SOURCES
                ), f"{sku}: content.{field} came from {entry['source']}, outside the registry"


def test_gap_report_matches_per_record_gaps(records: dict[str, dict]) -> None:
    report = gap_report()
    assert set(report) == {sku for sku, rec in records.items() if rec["gaps"]}
    for sku, gaps in report.items():
        assert gaps == records[sku]["gaps"]


def test_unknown_sku_raises_and_names_the_known_set() -> None:
    with pytest.raises(KeyError) as excinfo:
        get_product("zz-999")
    assert "br-001" in str(excinfo.value), "the error should list the known SKUs"


def test_absent_registry_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """A missing registry raises -- it never degrades to 'no product facts'."""
    monkeypatch.setattr(
        "skyyrose.core.product_registry.PRODUCT_REGISTRY", tmp_path / "absent-registry.json"
    )
    with pytest.raises(FileNotFoundError):
        get_product("br-001")


def test_provenance_names_the_registry_as_the_only_source() -> None:
    prov = provenance()
    assert prov["entry_point"] == "skyyrose.core.product.get_product"
    assert set(prov["sources"]) == {"registry"}
    for label, source in prov["sources"].items():
        assert (REPO_ROOT / source["path"]).exists(), f"{label} path does not exist"
        assert len(source["sha256"]) == 16, f"{label} has no digest"
        assert source["bytes"] > 0, f"{label} is empty"


def test_cli_emits_the_same_record() -> None:
    """Non-Python agents shell out; the CLI must return the identical record."""
    result = subprocess.run(
        [sys.executable, "-m", "skyyrose.core.product", "br-001"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=True,
    )
    payload = json.loads(result.stdout)
    expected = get_product("br-001")
    assert payload["sku"] == expected["sku"]
    assert payload["catalog"] == expected["catalog"]
    assert payload["gaps"] == expected["gaps"]
    assert payload["images"] == expected["images"]


def test_cli_gaps_and_skus_modes() -> None:
    for flag in ("--gaps", "--skus"):
        result = subprocess.run(
            [sys.executable, "-m", "skyyrose.core.product", flag],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=True,
        )
        json.loads(result.stdout)
