"""Tests for scripts/build-site-guide.py — the Skyy mascot guide-brain generator.

Covers the pure extraction functions against small fixture strings (so a
regex regression is caught without depending on the real theme files staying
byte-identical) plus an integration test against the real repo source (so a
PHP reformat that silently breaks the regexes is caught too).

The generator lives in ``scripts/`` (not an importable package, and its
filename has a hyphen), so it is loaded by file path — same mechanism used
by tests/test_v7_cards_generator.py.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _load(mod_name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(mod_name, _REPO_ROOT / rel_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


guide = _load("build_site_guide", "scripts/build-site-guide.py")

THEME_DIR = _REPO_ROOT / "wordpress-theme" / "skyyrose-flagship"


# ---------------------------------------------------------------------------
# slugify / title_case_slug
# ---------------------------------------------------------------------------


def test_slugify_basic() -> None:
    assert guide.slugify("Black Rose") == "black-rose"


def test_slugify_idempotent_on_existing_slug() -> None:
    assert guide.slugify("black-rose") == "black-rose"


def test_slugify_strips_punctuation_and_collapses_spaces() -> None:
    assert guide.slugify("  Kids   Capsule! ") == "kids-capsule"


def test_title_case_slug() -> None:
    assert guide.title_case_slug("kids-capsule") == "Kids Capsule"


# ---------------------------------------------------------------------------
# extract_menu_items
# ---------------------------------------------------------------------------

_MENU_FIXTURE = """
function skyyrose_get_menu_definitions() {
	return array(
		'primary' => array(
			'name'  => __( 'Primary Menu', 'skyyrose' ),
			'items' => array(
				array(
					'title' => __( 'Home', 'skyyrose' ),
					'url'   => '/',
				),
				array(
					'title'    => __( 'Collections', 'skyyrose' ),
					'url'      => '/collections/',
					'children' => array(
						array(
							'title' => __( 'Black Rose', 'skyyrose' ),
							'url'   => '/collection-black-rose/',
						),
					),
				),
			),
		),
		'footer' => array(
			'name'  => __( 'Footer Menu', 'skyyrose' ),
			'items' => array(
				array(
					'title' => __( 'FAQ', 'skyyrose' ),
					'url'   => '/contact/#faq',
				),
			),
		),
	);
}
"""


def test_extract_menu_items_flattens_parent_and_children() -> None:
    items = guide.extract_menu_items(_MENU_FIXTURE)
    urls = {item["url"]: item["title"] for item in items}
    assert urls["/"] == "Home"
    assert urls["/collections/"] == "Collections"
    assert urls["/collection-black-rose/"] == "Black Rose"


def test_extract_menu_items_excludes_anchor_only_urls() -> None:
    items = guide.extract_menu_items(_MENU_FIXTURE)
    assert all("#" not in item["url"] for item in items)
    assert not any(item["title"] == "FAQ" for item in items)


# ---------------------------------------------------------------------------
# extract_page_registry
# ---------------------------------------------------------------------------

_REGISTRY_FIXTURE = """
function skyyrose_get_required_pages() {
	return array(
		'about' => array(
			'title'    => __( 'About', 'skyyrose' ),
			'template' => 'template-about.php',
			'content'  => '',
		),
		'pre-order' => array(
			'title'    => __( 'Pre-Order', 'skyyrose' ),
			'template' => 'template-preorder-gateway.php',
			'content'  => '',
		),
	);
}

function skyyrose_configure_woocommerce_settings( $page_ids ) {
	$wc_pages = array(
		'shop' => array(
			'title'  => __( 'Shop', 'skyyrose' ),
			'option' => 'woocommerce_shop_page_id',
		),
		'my-account' => array(
			'title'  => __( 'My Account', 'skyyrose' ),
			'option' => 'woocommerce_myaccount_page_id',
		),
	);
}
"""


def test_extract_page_registry_covers_required_and_wc_pages() -> None:
    registry = guide.extract_page_registry(_REGISTRY_FIXTURE)
    assert registry == {
        "about": "About",
        "pre-order": "Pre-Order",
        "shop": "Shop",
        "my-account": "My Account",
    }


# ---------------------------------------------------------------------------
# extract_footer_legal_links
# ---------------------------------------------------------------------------

_FOOTER_FIXTURE = """
<li><a href="<?php echo esc_url( home_url( '/faq/' ) ); ?>"><?php esc_html_e( 'FAQ', 'skyyrose' ); ?></a></li>
<li><a href="<?php echo esc_url( home_url( '/shipping-returns/' ) ); ?>"><?php esc_html_e( 'Shipping & Returns', 'skyyrose' ); ?></a></li>
<li><a href="<?php echo esc_url( home_url( '/contact/#size-guide' ) ); ?>"><?php esc_html_e( 'Size Guide', 'skyyrose' ); ?></a></li>
"""


def test_extract_footer_legal_links() -> None:
    links = guide.extract_footer_legal_links(_FOOTER_FIXTURE)
    assert links == {"faq": "FAQ", "shipping-returns": "Shipping & Returns"}


def test_extract_footer_legal_links_excludes_anchors() -> None:
    links = guide.extract_footer_legal_links(_FOOTER_FIXTURE)
    assert "contact" not in links


# ---------------------------------------------------------------------------
# registry_collections
# ---------------------------------------------------------------------------


def _fake_registry(monkeypatch, collections_by_sku: dict[str, str | None]) -> None:
    monkeypatch.setattr(guide, "all_skus", lambda: sorted(collections_by_sku))
    monkeypatch.setattr(
        guide, "get_product", lambda sku: {"sku": sku, "collection": collections_by_sku[sku]}
    )


def test_registry_collections_returns_sorted_distinct(monkeypatch) -> None:
    _fake_registry(
        monkeypatch, {"lh-001": "love-hurts", "br-001": "black-rose", "br-002": "black-rose"}
    )
    assert guide.registry_collections() == ["black-rose", "love-hurts"]


def test_registry_collections_drops_blank_values(monkeypatch) -> None:
    _fake_registry(monkeypatch, {"br-001": "", "br-002": None, "br-003": "  "})
    assert guide.registry_collections() == []


def test_generate_reads_collections_from_the_registry(monkeypatch) -> None:
    """With no explicit list, generate() sources collections through get_product."""
    _fake_registry(monkeypatch, {"zz-001": "zz-registry-only"})
    pages = guide.generate(theme_dir=THEME_DIR)["pages"]
    assert pages["collection-zz-registry-only"]["url"] == "/collections/zz-registry-only/"


def test_real_registry_has_the_four_collections() -> None:
    assert guide.registry_collections() == [
        "black-rose",
        "kids-capsule",
        "love-hurts",
        "signature",
    ]


# ---------------------------------------------------------------------------
# build_pages
# ---------------------------------------------------------------------------


def test_build_pages_merges_all_sources() -> None:
    pages = guide.build_pages(
        menu_items=[{"title": "Home", "url": "/"}],
        page_registry={"home": "Home", "faq": "FAQ"},
        legal_links={"shipping-returns": "Shipping & Returns"},
        collections=["black-rose"],
    )
    assert set(pages) == {"home", "faq", "shipping-returns", "collection-black-rose"}
    assert pages["collection-black-rose"]["url"] == "/collections/black-rose/"
    assert pages["faq"]["tips"] == []


def test_build_pages_home_url_forced_to_root() -> None:
    """'home' is the static front page — served at '/', never literal '/home/'."""
    pages = guide.build_pages(
        menu_items=[{"title": "Home", "url": "/"}],
        page_registry={"home": "Home"},
        legal_links={},
        collections=[],
    )
    assert pages["home"]["url"] == "/"


def test_build_pages_first_writer_wins_no_duplicate_overwrite() -> None:
    pages = guide.build_pages(
        menu_items=[{"title": "About Us (menu label)", "url": "/about/"}],
        page_registry={"about": "About"},
        legal_links={},
        collections=[],
    )
    # page_registry is higher priority than menu_items — title stays "About".
    assert pages["about"]["title"] == "About"


# ---------------------------------------------------------------------------
# build_intents
# ---------------------------------------------------------------------------


def test_build_intents_only_emits_when_target_page_exists() -> None:
    pages = {
        "collection-black-rose": {
            "title": "Black Rose Collection",
            "url": "/collection-black-rose/",
            "tips": [],
        },
        "faq": {"title": "FAQ", "url": "/faq/", "tips": []},
        # shop / pre-order / shipping-returns / my-account deliberately absent.
    }
    intents = guide.build_intents(pages, collections=["black-rose"])
    ids = {intent["id"] for intent in intents}
    assert "where-black-rose" in ids
    assert "sizing" in ids
    assert "where-shop" not in ids
    assert "shipping" not in ids
    assert "order-tracking" not in ids


def test_build_intents_link_matches_page_url() -> None:
    pages = {
        "faq": {"title": "FAQ", "url": "/faq/", "tips": []},
    }
    intents = guide.build_intents(pages, collections=[])
    sizing = next(i for i in intents if i["id"] == "sizing")
    assert sizing["link"] == "/faq/"
    assert sizing["patterns"]  # non-empty


# ---------------------------------------------------------------------------
# generate() — fail-loud behaviour on broken/empty sources
# ---------------------------------------------------------------------------


def _write_minimal_theme_fixture(tmp_path: Path) -> Path:
    theme_dir = tmp_path / "skyyrose-flagship"
    (theme_dir / "inc").mkdir(parents=True)
    (theme_dir / "data").mkdir(parents=True)

    (theme_dir / "inc" / "menu-setup.php").write_text(_MENU_FIXTURE, encoding="utf-8")
    (theme_dir / "inc" / "theme-activation-setup.php").write_text(
        _REGISTRY_FIXTURE, encoding="utf-8"
    )
    (theme_dir / "footer.php").write_text(_FOOTER_FIXTURE, encoding="utf-8")
    return theme_dir


def test_generate_raises_when_catalog_has_zero_collections(tmp_path: Path) -> None:
    theme_dir = _write_minimal_theme_fixture(tmp_path)
    with pytest.raises(SystemExit, match="0 collections"):
        guide.generate(theme_dir=theme_dir, collections=[])


def test_generate_raises_when_required_page_missing(tmp_path: Path) -> None:
    """Registry/footer have enough entries to pass the size checks, but none
    of them is 'faq' / 'shipping-returns' / 'my-account' / 'pre-order' /
    'shop' — must still fail loud rather than ship a guide missing a
    required intent target.
    """
    theme_dir = tmp_path / "skyyrose-flagship"
    (theme_dir / "inc").mkdir(parents=True)
    (theme_dir / "data").mkdir(parents=True)
    (theme_dir / "inc" / "menu-setup.php").write_text(_MENU_FIXTURE, encoding="utf-8")
    (theme_dir / "inc" / "theme-activation-setup.php").write_text(
        "function x() { return array( "
        "'home' => array( 'title' => __( 'Home', 'skyyrose' ) ), "
        "'about' => array( 'title' => __( 'About', 'skyyrose' ) ), "
        "'contact' => array( 'title' => __( 'Contact', 'skyyrose' ) ), "
        "'wishlist' => array( 'title' => __( 'Wishlist', 'skyyrose' ) ) "
        "); }",
        encoding="utf-8",
    )
    (theme_dir / "footer.php").write_text(
        "<li><a href=\"<?php echo esc_url( home_url( '/privacy-policy/' ) ); ?>\">"
        "<?php esc_html_e( 'Privacy Policy', 'skyyrose' ); ?></a></li>",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="required page"):
        guide.generate(theme_dir=theme_dir, collections=["black-rose"])


def test_generate_raises_when_page_registry_too_small(tmp_path: Path) -> None:
    theme_dir = tmp_path / "skyyrose-flagship"
    (theme_dir / "inc").mkdir(parents=True)
    (theme_dir / "data").mkdir(parents=True)
    (theme_dir / "inc" / "menu-setup.php").write_text(_MENU_FIXTURE, encoding="utf-8")
    (theme_dir / "inc" / "theme-activation-setup.php").write_text(
        "function x() { return array( 'about' => array( 'title' => __( 'About', 'skyyrose' ) ) ); }",
        encoding="utf-8",
    )
    (theme_dir / "footer.php").write_text(_FOOTER_FIXTURE, encoding="utf-8")
    with pytest.raises(SystemExit, match="registered pages parsed"):
        guide.generate(theme_dir=theme_dir, collections=["black-rose"])


def test_generate_raises_when_footer_has_no_legal_links(tmp_path: Path) -> None:
    theme_dir = _write_minimal_theme_fixture(tmp_path)
    (theme_dir / "footer.php").write_text("<p>no legal links here</p>", encoding="utf-8")
    with pytest.raises(SystemExit, match="footer legal links"):
        guide.generate(theme_dir=theme_dir, collections=["black-rose"])


# ---------------------------------------------------------------------------
# generate() — integration test against the real repo source
# ---------------------------------------------------------------------------


def test_generate_against_real_theme_source() -> None:
    """Guards against the regexes silently drifting out of sync with the
    real PHP files as the theme evolves — the whole point of a generator
    that must fail loud rather than ship a partial JSON.
    """
    data = guide.generate(theme_dir=THEME_DIR)

    assert set(data.keys()) == {"pages", "intents"}
    assert len(data["pages"]) >= 10
    assert len(data["intents"]) >= 5

    for slug in ("home", "faq", "shipping-returns", "my-account", "pre-order", "shop"):
        assert slug in data["pages"], f"expected page slug {slug!r} in generated pages"

    assert data["pages"]["home"]["url"] == "/"

    for collection_slug in ("black-rose", "love-hurts", "signature", "kids-capsule"):
        page_slug = "collection-" + collection_slug
        assert page_slug in data["pages"]
        assert data["pages"][page_slug]["url"] == f"/collections/{collection_slug}/"

    # Every intent link must resolve to a real page's url — no dangling guesses.
    urls = {p["url"] for p in data["pages"].values()}
    for intent in data["intents"]:
        assert intent["link"] in urls

    # Must be JSON-serialisable (this is what main() writes to disk).
    json.dumps(data)


def test_committed_site_guide_json_matches_generator_output() -> None:
    """The committed data/site-guide.json is a generated artifact — regenerate
    it with `python3 scripts/build-site-guide.py` after any nav/page change.
    """
    output_path = THEME_DIR / "data" / "site-guide.json"
    assert output_path.exists(), "run scripts/build-site-guide.py to generate it"

    committed = json.loads(output_path.read_text(encoding="utf-8"))
    fresh = guide.generate(theme_dir=THEME_DIR)
    assert committed == fresh
