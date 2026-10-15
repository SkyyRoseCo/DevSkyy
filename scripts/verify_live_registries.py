"""Page registries for scripts/verify_live_structure.py.

Which pages, DOM markers and global assertions each WordPress theme lineage must
render: V1 (text domain "skyyrose", wordpress-theme/skyyrose-flagship) and V2
("skyyrose-flagship-2", wordpress-theme/skyyrose-flagship-2). The checker picks one
with select_registry() from the LIVE theme's Text Domain; this module holds data and
builders only — no network, no CLI.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TEXT_DOMAIN_V1 = "skyyrose"
TEXT_DOMAIN_V2 = "skyyrose-flagship-2"
KNOWN_TEXT_DOMAINS = (TEXT_DOMAIN_V1, TEXT_DOMAIN_V2)

# Per-collection holo-card minimums (V1) derived from the canonical CSV at
# wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv.
# Floors are set ~20% below actual counts so adding/removing one SKU
# does not auto-fail the gate; the regression mode we are catching is
# "page rendered ZERO or ONE card", not "catalog drifted by 1".
COLLECTION_CARD_FLOORS = {
    "black-rose": 12,  # 15 actual
    "love-hurts": 3,  # 4 actual
    "signature": 10,  # 12 actual
    "kids-capsule": 2,  # 2 actual (cannot go lower without breaking)
}

# (slug, display name) for the collection pages; the first three also have
# immersive/world pages.
COLLECTIONS: tuple[tuple[str, str], ...] = (
    ("black-rose", "Black Rose"),
    ("love-hurts", "Love Hurts"),
    ("signature", "Signature"),
    ("kids-capsule", "Kids Capsule"),
)
WORLDS: tuple[tuple[str, str], ...] = COLLECTIONS[:3]

_TEXT_DOMAIN_RE = re.compile(r"^\s*Text Domain:\s*(?P<value>\S+)\s*$", re.IGNORECASE | re.MULTILINE)


@dataclass(frozen=True)
class Assertion:
    selector: str
    min_count: int
    label: str
    # When set, count must satisfy min_count <= actual <= max_count.
    # Used by the global assertions to assert error markers stay at 0.
    max_count: int | None = None

    def bounds_str(self) -> str:
        if self.max_count is not None and self.max_count == self.min_count:
            return f"exactly={self.min_count}"
        if self.max_count is not None:
            return f"min={self.min_count}, max={self.max_count}"
        return f"min={self.min_count}"


@dataclass(frozen=True)
class PricingCheck:
    """
    Text-content assertion for rendered price elements.

    Standard CSS selectors cannot assert on text content (no :contains()),
    so CNTR-04 pricing assertions use this separate dataclass + helper.
    """

    selector: str
    forbidden_texts: tuple[str, ...]
    label: str


@dataclass(frozen=True)
class Page:
    name: str
    path: str
    assertions: tuple[Assertion, ...]


@dataclass(frozen=True)
class Registry:
    """Everything the checker needs for one theme lineage."""

    text_domain: str
    pages: dict[str, Page]
    global_assertions: tuple[Assertion, ...]
    pricing_checks: tuple[PricingCheck, ...]


# ---------------------------------------------------------------------------
# Reusable assertion builders
# ---------------------------------------------------------------------------


def theme_css_assertion(theme_slug: str) -> Assertion:
    """The live theme's stylesheet must be enqueued -- proves the slug is active."""
    return Assertion(
        f"link[href*='{theme_slug}']",
        1,
        f"theme CSS enqueued ({theme_slug} active)",
    )


# Universal structural assertion applied to every page of both lineages.
# data-skyyrose-error is a project-wide beacon emitted by template parts that
# hit a "should not happen" branch (e.g. template-parts/collection/page.php
# when content config is missing).
_STRUCTURAL_ASSERTIONS: tuple[Assertion, ...] = (
    Assertion(
        "[data-skyyrose-error]",
        0,
        "no skyyrose render-error markers (universal regression beacon)",
        max_count=0,
    ),
)

# A11Y post-deploy gate -- applied to every page checked by --all / --page.
#   A11Y-05: aria-hidden focusables carry tabindex="-1" (V1: accessibility-fix.php
#            Section 5; V2: the <main> itself). Selector returns 0 if absent.
#   A11Y-07: skip-link exists (Pojo Accessibility plugin on the V1 site only --
#            NO V2 page on staging emits a.skip-link [live 2026-09-19]).
#   A11Y-09: >=1 loading="lazy" image; 0 means template failure or fix not run.
_A11Y_TABINDEX = Assertion(
    "[tabindex='-1']",
    1,
    "A11Y-05: at least 1 tabindex='-1' element present (aria-hidden focusable fix active)",
)
_A11Y_SKIP_LINK = Assertion(
    "a.skip-link", 1, "A11Y-07: skip-link anchor exists (Pojo Accessibility plugin active)"
)
_A11Y_LAZY_IMG = Assertion(
    "img[loading='lazy']",
    1,
    "A11Y-09: at least 1 lazy-loaded image (inc/accessibility-fix.php Section 8 active)",
)
GLOBAL_ASSERTIONS_V1 = _STRUCTURAL_ASSERTIONS + (_A11Y_TABINDEX, _A11Y_SKIP_LINK, _A11Y_LAZY_IMG)
GLOBAL_ASSERTIONS_V2 = _STRUCTURAL_ASSERTIONS + (_A11Y_TABINDEX, _A11Y_LAZY_IMG)

# CNTR-04: Pricing text gate (V1 holo cards). Pre-order SKUs must NOT show
# "$0" / "$0.00" in their rendered price elements -- those placeholders mean
# WooCommerce returned a zero-price product instead of the theme's
# "Pre-Order" display string.
PRICING_CHECKS_V1: tuple[PricingCheck, ...] = (
    PricingCheck(
        selector=".holo-card .product-price, .holo-card .price, .product-card .price",
        forbidden_texts=("$0", "$0.00"),
        label="CNTR-04: no $0/$0.00 prices on holo-card pre-order SKUs",
    ),
)


def _main_assertion(class_name: str, what_ran: str) -> Assertion:
    """Build a `<main class="X">` assertion with a consistent label format."""
    return Assertion(
        f"main#primary.{class_name}",
        1,
        f"<main class='{class_name}'> ({what_ran})",
    )


# ---------------------------------------------------------------------------
# V1 registry -- text domain "skyyrose" (wordpress-theme/skyyrose-flagship)
# ---------------------------------------------------------------------------

# Hero background image filename for each collection, as deployed to the CDN.
# Verified against inc/collection-content.php hero_bg keys and
# assets/branding/ directory. Used in collection_assertions() below.
COLLECTION_HERO_ASSETS: dict[str, str] = {
    "black-rose": "sr-collection-black-rose.webp",
    "love-hurts": "sr-collection-love-hurts.webp",
    "signature": "sr-collection-signature.webp",
    "kids-capsule": "sr-collection-kids-capsule.webp",
}


def collection_assertions(slug: str, theme_slug: str) -> tuple[Assertion, ...]:
    """Build assertion tuple for a V1 collection page (BR/LH/SIG/Kids)."""
    floor = COLLECTION_CARD_FLOORS[slug]
    base_assertions: tuple[Assertion, ...] = (
        Assertion(
            f"div.col-page[data-collection='{slug}']",
            1,
            f"<div class='col-page' data-collection='{slug}'>",
        ),
        Assertion("section.col-hero", 1, "<section class='col-hero'> (collection hero)"),
        Assertion(
            "div.holo",
            floor,
            f">= {floor} <.holo> product cards (universal grid rendered)",
        ),
        Assertion(
            f"div.holo--{slug}",
            floor,
            f">= {floor} <.holo--{slug}> cards (collection-specific rendered)",
        ),
        theme_css_assertion(theme_slug),
    )
    hero_asset = COLLECTION_HERO_ASSETS.get(slug)
    if hero_asset:
        return base_assertions + (
            Assertion(
                f"img[src*='{hero_asset}']",
                1,
                f"collection hero <img src> contains {hero_asset} (DATA-01)",
            ),
        )
    return base_assertions


def immersive_assertions(name: str, theme_slug: str) -> tuple[Assertion, ...]:
    """Build assertion tuple for the 3 V1 immersive 3D pages.

    `name` is the human-readable collection name (e.g., "Black Rose")
    used only in the label, not in any selector. All 3 immersive pages
    share the same template-emitted markup.
    """
    return (
        _main_assertion("immersive-page", f"immersive template ran for {name}"),
        theme_css_assertion(theme_slug),
    )


def build_registry_v1(theme_slug: str) -> Registry:
    css = theme_css_assertion(theme_slug)
    homepage: tuple[Assertion, ...] = (
        Assertion("body.home", 1, "<body class='home'> (WP routed to front page)"),
        _main_assertion("homepage-v3", "front-page.php template ran"),
        Assertion("header#masthead", 1, "<header id='masthead'> (standard site header rendered)"),
        Assertion("section.hp-hero", 1, "<section class='hp-hero'> (hero section emitted)"),
        css,
        Assertion("meta[name='generator']", 1, "<meta name='generator'> (WordPress emitted)"),
        # CURS-01/CURS-03: luxury cursor JS must be present on front-page.
        Assertion(
            "script[src*='luxury-cursor']",
            1,
            "CURS-01/CURS-03 — luxury cursor JS present on front-page (global enqueue confirmed)",
        ),
    )
    about: tuple[Assertion, ...] = (
        _main_assertion("abt-page", "about template ran"),
        Assertion("section.abt-hero", 1, "<section class='abt-hero'> (about hero section)"),
        css,
    )
    preorder: tuple[Assertion, ...] = (
        _main_assertion("preorder-gateway", "preorder template ran"),
        Assertion("section#hero", 1, "<section id='hero'>"),
        Assertion("section#showcase", 1, "<section id='showcase'> (preorder showcase)"),
        css,
    )
    pages: dict[str, Page] = {
        "home": Page("Homepage", "/", homepage),
        "about": Page("About", "/about/", about),
        "preorder": Page("Pre-Order Gateway", "/pre-order/", preorder),
    }
    for slug, name in COLLECTIONS:
        pages[slug] = Page(
            f"Collection: {name}", f"/collection-{slug}/", collection_assertions(slug, theme_slug)
        )
    for slug, name in WORLDS:
        pages[f"experience-{slug}"] = Page(
            f"Immersive: {name}", f"/experience-{slug}/", immersive_assertions(name, theme_slug)
        )
    return Registry(TEXT_DOMAIN_V1, pages, GLOBAL_ASSERTIONS_V1, PRICING_CHECKS_V1)


# ---------------------------------------------------------------------------
# V2 registry -- text domain "skyyrose-flagship-2" (wordpress-theme/skyyrose-flagship-2)
# Routes + DOM markers read from staging-7e48-skyyrose.wpcomstaging.com,
# 2026-09-19 [live]: / -> main.sr2-archive; /collections/<slug>/ ->
# main.sr2-collection-world[data-collection]; /worlds/<slug>/ -> body
# .page-template-template-immersive-<slug>; /about/ and /pre-order/ ->
# main.sr2-page--{about,pre-order}. Legacy /collection-* and /experience-*
# 302 there (checked by verify-deploy.sh). No V2 card floor yet (selector not
# pinned from evidence -- follow-up).
# ---------------------------------------------------------------------------


def _v2_collection_page(slug: str, name: str, css: Assertion) -> Page:
    world = Assertion(
        f"main#primary.sr2-collection-world[data-collection='{slug}']",
        1,
        f"<main class='sr2-collection-world' data-collection='{slug}'> (V2 collection world)",
    )
    return Page(f"Collection: {name}", f"/collections/{slug}/", (world, css))


def _v2_world_page(slug: str, name: str, css: Assertion) -> Page:
    template = Assertion(
        f"body.page-template-template-immersive-{slug}",
        1,
        f"<body class='page-template-template-immersive-{slug}'> (V2 world template ran)",
    )
    return Page(f"World: {name}", f"/worlds/{slug}/", (template, css))


def build_registry_v2(theme_slug: str) -> Registry:
    css = theme_css_assertion(theme_slug)
    pages: dict[str, Page] = {
        "home": Page(
            "Homepage",
            "/",
            (
                Assertion("body.home", 1, "<body class='home'> (WP routed to front page)"),
                _main_assertion("sr2-archive", "front-page.php (V2) template ran"),
                css,
                Assertion(
                    "meta[name='generator']", 1, "<meta name='generator'> (WordPress emitted)"
                ),
            ),
        ),
        "about": Page(
            "About",
            "/about/",
            (_main_assertion("sr2-page--about", "V2 about template ran"), css),
        ),
        "preorder": Page(
            "Pre-Order Gateway",
            "/pre-order/",
            (_main_assertion("sr2-page--pre-order", "V2 pre-order gateway template ran"), css),
        ),
        **{slug: _v2_collection_page(slug, name, css) for slug, name in COLLECTIONS},
        **{f"world-{slug}": _v2_world_page(slug, name, css) for slug, name in WORLDS},
    }
    return Registry(TEXT_DOMAIN_V2, pages, GLOBAL_ASSERTIONS_V2, ())


def select_registry(text_domain: str, theme_slug: str) -> Registry:
    """Pick the registry for a live Text Domain; unknown domains raise ValueError."""
    if text_domain == TEXT_DOMAIN_V1:
        return build_registry_v1(theme_slug)
    if text_domain == TEXT_DOMAIN_V2:
        return build_registry_v2(theme_slug)
    raise ValueError(
        f"unrecognised text domain {text_domain!r}; known: {', '.join(KNOWN_TEXT_DOMAINS)}"
    )


def parse_text_domain(style_css: str) -> str | None:
    """Return the `Text Domain:` header value of a style.css body, or None."""
    match = _TEXT_DOMAIN_RE.search(style_css)
    return match.group("value") if match else None
