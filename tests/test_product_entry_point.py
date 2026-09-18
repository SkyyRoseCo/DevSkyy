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
    ProductSourceMissingError,
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
    "authority",
    "gaps",
    "provenance",
)

CONTENT_FIELDS = ("description", "short_description", "seo_meta", "instagram", "tiktok")

# The 14 SKUs whose copy is still the registry base line rather than enriched
# editorial copy, as of 2026-09-17. Every SKU HAS a description -- this set is
# about which layer serves it. Pinned so that enriching one (good) or silently
# demoting one (a regression) both fail here and force a deliberate update.
KNOWN_UNENRICHED_SKUS = frozenset(
    {
        "br-009",
        "br-010",
        "br-011",
        "br-012",
        "br-014",
        "br-015",
        "kids-001",
        "kids-002",
        "lh-005",
        "sg-011",
        "sg-012",
        "sg-013",
        "sg-014",
        "sg-015",
    }
)


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
                assert f"content.{field}" in record["gaps"], (
                    f"{sku}: content.{field} is absent but not in gaps"
                )
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


def test_unenriched_skus_match_the_pinned_set(records: dict[str, dict]) -> None:
    """Which SKUs still need editorial copy is founder-facing; changes are deliberate."""
    actual = {
        sku
        for sku, record in records.items()
        if "content.description.enriched" in record["gaps"]
    }
    assert actual == KNOWN_UNENRICHED_SKUS, (
        f"unenriched set changed.\n  newly enriched: {sorted(KNOWN_UNENRICHED_SKUS - actual)}\n"
        f"  newly demoted:  {sorted(actual - KNOWN_UNENRICHED_SKUS)}\n"
        "Update KNOWN_UNENRICHED_SKUS when the founder adds editorial copy."
    )


def test_gap_report_matches_per_record_gaps(records: dict[str, dict]) -> None:
    report = gap_report()
    assert set(report) == {sku for sku, rec in records.items() if rec["gaps"]}
    for sku, gaps in report.items():
        assert gaps == records[sku]["gaps"]


def test_unknown_sku_raises_and_names_the_known_set() -> None:
    with pytest.raises(KeyError) as excinfo:
        get_product("zz-999")
    assert "br-001" in str(excinfo.value), "the error should list the known SKUs"


def test_absent_source_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """A missing authored source raises -- it never degrades to 'no content'."""
    monkeypatch.setattr(
        "skyyrose.core.product._CONTENT_JSON", tmp_path / "absent-product-content.json"
    )
    with pytest.raises(ProductSourceMissingError):
        get_product("br-001")


def test_provenance_names_every_source_with_a_digest() -> None:
    prov = provenance()
    assert prov["entry_point"] == "skyyrose.core.product.get_product"
    assert set(prov["sources"]) == {"registry", "content", "alt_text", "corrections"}
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
