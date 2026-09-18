"""Schema v2 fold: the side stores now live in the product registry, losslessly.

render-corrections.json, render-keepers.json, and the four collection
identity.json files were authored outside logo-registry.json. Their contents
moved into it (products[sku].corrections, products[sku].render_policy, the
top-level collections section, and authority_contract for their provenance).

Round-trip tests rebuilt each retired file from the registry and matched it value
for value against the committed original (PR #949, 74c2e14bf). With that proven,
the retired files were deleted with founder approval on 2026-09-18, and the
round-trips gave way to a test that the files stay gone: a second copy is a
second source.
"""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from scripts.organize_product_registry import check_schema
from skyyrose.core import product_registry
from skyyrose.core.product import get_product
from skyyrose.core.product_registry import load_registry, update_product_content

DATA = product_registry.PRODUCT_REGISTRY.resolve().parent
COLLECTION_SLUGS = ("black-rose", "kids-capsule", "love-hurts", "signature")
RETIRED_SIDE_STORES = (
    DATA / "render-corrections.json",
    DATA / "render-keepers.json",
    *(DATA / "collections" / slug / "identity.json" for slug in COLLECTION_SLUGS),
)

# The nine lines added 2026-06-12 in 31d4e40e4 ("anti-peony/two-rose render
# corrections"; the file's _meta.notes: "per Fable vision test"). Every other
# line is a founder review-board comment from 2026-06-09 (409187921).
TWO_ROSE = "[ghost] The Black Rose rose-cluster logo is a cluster of MULTIPLE"
CHEST_SCALE = "[ghost] Render the rose logo at the size and position shown"
AGENT_ADDED = {
    **{sku: [TWO_ROSE] for sku in ("br-002", "br-005", "br-007")},
    **{sku: [TWO_ROSE, CHEST_SCALE] for sku in ("br-001", "br-004", "br-006")},
}


@pytest.fixture(scope="module")
def registry() -> dict:
    return load_registry()


def test_schema_version_is_two(registry: dict) -> None:
    assert registry["product_registry_schema_version"] == 2


@pytest.mark.parametrize("path", RETIRED_SIDE_STORES, ids=lambda p: str(p.relative_to(DATA)))
def test_retired_side_stores_stay_deleted(path: Path) -> None:
    assert not path.exists(), (
        f"{path.relative_to(DATA)} was folded into logo-registry.json and retired. "
        "Edit the registry instead."
    )


def test_every_collection_is_in_the_registry(registry: dict) -> None:
    assert set(registry["collections"]) == set(COLLECTION_SLUGS)


def test_each_correction_names_who_wrote_it(registry: dict) -> None:
    """Agent-written lines are never labelled as the founder's words."""
    agent_added = {}
    for sku, product in registry["products"].items():
        for line in product.get("corrections") or []:
            if line["authority"] == "AGENT_ADDED":
                assert line["captured"] == "2026-06-12", (sku, line["text"][:40])
                agent_added.setdefault(sku, []).append(line["text"])
            else:
                assert line["authority"] == "FOUNDER_VERBATIM", (sku, line["authority"])
                assert line["captured"] == "2026-06-09", (sku, line["text"][:40])
    assert {sku: len(lines) for sku, lines in agent_added.items()} == {
        sku: len(prefixes) for sku, prefixes in AGENT_ADDED.items()
    }
    for sku, prefixes in AGENT_ADDED.items():
        for text, prefix in zip(agent_added[sku], prefixes, strict=True):
            assert text.startswith(prefix), (sku, text[:60])


def test_founder_review_lines_are_the_majority_and_verbatim(registry: dict) -> None:
    founder = [
        line
        for product in registry["products"].values()
        for line in product.get("corrections") or []
        if line["authority"] == "FOUNDER_VERBATIM"
    ]
    assert len(founder) == 32
    assert all(line["text"].startswith("[") for line in founder)


def test_get_product_serves_corrections_and_keepers() -> None:
    br006 = get_product("br-006")
    assert [c["authority"] for c in br006["corrections"]] == ["AGENT_ADDED", "AGENT_ADDED"]
    assert br006["render_policy"]["keepers"] == [
        {
            "style": "on-model",
            "view": "front",
            "asset": "wordpress-theme/skyyrose-flagship/assets/images/products/"
            "black-rose-sherpa-jacket-front-model.webp",
            "founder_note": "real product — approved 2026-06-10",
        }
    ]
    assert get_product("br-003")["render_policy"] == {"keepers": []}


# ── schema enforces the v2 sections ─────────────────────────────────────────


def test_live_registry_is_schema_valid(registry: dict) -> None:
    assert check_schema(registry) == []


@pytest.mark.parametrize(
    ("mutate", "where"),
    [
        (
            lambda r: r["products"]["br-001"]["corrections"][0].update(
                authority="FOUNDER_CONFIRMED"
            ),
            "corrections",
        ),
        (
            lambda r: r["products"]["br-006"]["render_policy"]["keepers"][0].pop("founder_note"),
            "render_policy",
        ),
        (lambda r: r["collections"]["signature"].pop("slug"), "collections"),
        (
            lambda r: r["products"]["br-001"].update(
                content={"description": {"value": "copy", "authority": "GEMINI"}}
            ),
            "content",
        ),
    ],
    ids=["unknown-correction-authority", "keeper-without-note", "collection-without-slug", "copy"],
)
def test_schema_rejects_malformed_v2_sections(registry: dict, mutate, where: str) -> None:
    broken = copy.deepcopy(registry)
    mutate(broken)
    findings = check_schema(broken)
    assert findings, f"schema accepted a malformed {where} section"


# ── copy is written into the registry, one field at a time ──────────────────


@pytest.fixture
def registry_copy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    target = tmp_path / "logo-registry.json"
    shutil.copy(product_registry.PRODUCT_REGISTRY.resolve(), target)
    monkeypatch.setattr(product_registry, "PRODUCT_REGISTRY", target)
    return target


def test_update_product_content_writes_one_field_with_its_author(registry_copy: Path) -> None:
    before = json.loads(registry_copy.read_text(encoding="utf-8"))
    previous = update_product_content(
        "br-001",
        "short_description",
        "Heavyweight black crewneck with the Black Rose cluster.",
        authority="AGENT_GENERATED",
        source="test",
        updated="2026-09-18",
    )
    assert previous is None
    after = json.loads(registry_copy.read_text(encoding="utf-8"))
    product = after["products"]["br-001"]
    assert product["content"] == {
        "short_description": {
            "value": "Heavyweight black crewneck with the Black Rose cluster.",
            "authority": "AGENT_GENERATED",
            "source": "test",
            "updated": "2026-09-18",
        }
    }
    keys = list(product)
    assert keys.index("content") < keys.index("authority")
    del product["content"]
    assert after == before, "a content write touched something other than its field"
    assert check_schema(json.loads(registry_copy.read_text(encoding="utf-8"))) == []

    record = get_product("br-001")
    entry = record["content"]["short_description"]
    assert entry["enriched"] is True
    assert entry["authority"] == "AGENT_GENERATED"
    assert "content.short_description.enriched" not in record["gaps"]


def test_update_product_content_returns_the_value_it_replaced(registry_copy: Path) -> None:
    kwargs = {"authority": "FOUNDER_AUTHORED", "source": "founder", "updated": "2026-09-18"}
    update_product_content("sg-007", "tiktok", "first", **kwargs)
    assert update_product_content("sg-007", "tiktok", "second", **kwargs) == "first"


@pytest.mark.parametrize(
    ("sku", "field", "value", "authority", "error"),
    [
        ("br-001", "name", "x", "AGENT_GENERATED", ValueError),
        ("br-001", "tiktok", "x", "GEMINI", ValueError),
        ("br-001", "tiktok", "   ", "AGENT_GENERATED", ValueError),
        ("zz-999", "tiktok", "x", "AGENT_GENERATED", KeyError),
    ],
    ids=["identity-field", "unknown-authority", "blank", "unknown-sku"],
)
def test_update_product_content_rejects_bad_writes(
    registry_copy: Path, sku: str, field: str, value: str, authority: str, error: type
) -> None:
    before = registry_copy.read_bytes()
    with pytest.raises(error):
        update_product_content(
            sku, field, value, authority=authority, source="test", updated="2026-09-18"
        )
    assert registry_copy.read_bytes() == before


# ── the dashboard's deployment replica is a projection like any other ───────


def test_dashboard_replica_is_the_catalog_projection() -> None:
    replica = product_registry.FRONTEND_CATALOG_REPLICA
    projection = DATA / "skyyrose-catalog.csv"
    assert replica.read_bytes() == projection.read_bytes()
    assert product_registry.export_compatibility(check=True) == []


def test_a_stale_dashboard_replica_fails_the_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stale = tmp_path / "skyyrose-catalog.csv"
    stale.write_text("sku,name\nbr-001,BLACK Rose Crewneck\n", encoding="utf-8")
    monkeypatch.setattr(product_registry, "FRONTEND_CATALOG_REPLICA", stale)
    assert product_registry.export_compatibility(check=True) == [str(stale)]
    assert stale.read_text(encoding="utf-8") == "sku,name\nbr-001,BLACK Rose Crewneck\n"


def test_corrections_provenance_statement_matches_the_labels(registry: dict) -> None:
    """The folded authorship note must not claim founder authorship of agent lines."""
    authorship = registry["authority_contract"]["render_corrections_source"]["authorship"]
    assert "every correction line is the founder" not in authorship
    assert "32 lines" in authorship and "FOUNDER_VERBATIM" in authorship
    assert "9 lines" in authorship and "AGENT_ADDED" in authorship


# ── alt text: only for images the registry binds to the product ─────────────


def test_alt_text_is_written_for_a_bound_image(registry_copy: Path) -> None:
    from skyyrose.core.product_registry import update_product_alt_text

    stem = Path(load_registry()["products"]["br-001"]["images"]["image"]["path"]).stem
    update_product_alt_text(
        "br-001",
        stem,
        "Black crewneck with the Black Rose cluster at the chest.",
        authority="FOUNDER_AUTHORED",
        source="founder",
        updated="2026-09-18",
    )
    record = get_product("br-001")
    assert record["alt_text"][stem]["value"].startswith("Black crewneck")
    assert record["alt_text"][stem]["authority"] == "FOUNDER_AUTHORED"
    assert "content.alt_text" not in record["gaps"]
    assert check_schema(json.loads(registry_copy.read_text(encoding="utf-8"))) == []


def test_alt_text_for_an_unbound_image_is_refused(registry_copy: Path) -> None:
    from skyyrose.core.product_registry import update_product_alt_text

    before = registry_copy.read_bytes()
    # The retired alt-text.json keyed br-002 to "br-002-product", an image the
    # registry never bound (it described a hoodie on the joggers SKU).
    with pytest.raises(ValueError, match="not an image bound to br-002"):
        update_product_alt_text(
            "br-002",
            "br-002-product",
            "Black hoodie featuring a white winged rose.",
            authority="AGENT_GENERATED",
            source="test",
            updated="2026-09-18",
        )
    assert registry_copy.read_bytes() == before


def test_catalog_update_reports_only_the_fields_it_changed(registry_copy: Path) -> None:
    from skyyrose.core.product_registry import update_catalog_fields

    current = load_registry()["products"]["br-001"]["catalog"]
    changed = update_catalog_fields(
        "br-001", {"name": current["name"], "badge": "TEST-BADGE"}, registry_copy
    )
    assert changed == ["badge"]


def test_a_registry_copy_never_rewrites_the_tracked_replica(registry_copy: Path) -> None:
    """A write against a copy (a test, a tool run) leaves the real replica alone."""
    from skyyrose.core.product_registry import update_catalog_fields

    replica = product_registry.FRONTEND_CATALOG_REPLICA
    before = replica.read_bytes()
    update_catalog_fields("br-001", {"badge": "COPY-ONLY"}, registry_copy)
    assert replica.read_bytes() == before
    assert "COPY-ONLY" in (registry_copy.parent / "skyyrose-catalog.csv").read_text()
