"""A11Y HTML integrity regression suite — A11Y-01 through A11Y-09.

Asserts that the accessibility fixes shipped in v1.1 (inc/accessibility-fix.php,
assets/css/accessibility.css) remain intact across future deploys.

Assertions run the current PHP output filter against unchanged historical HTML
captures. This verifies local behavior, not the current deployed site.
The PHP harness stubs only WordPress hooks and escaping; zero network calls.

Run: python -m pytest tests/test_a11y_html_integrity.py -v
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "a11y"

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _load(filename: str) -> BeautifulSoup:
    path = FIXTURES_DIR / filename
    assert path.is_file(), f"Fixture missing: {path}"
    root = Path(__file__).resolve().parents[1]
    rendered = subprocess.run(
        [
            "php",
            str(root / "tests/php/render_accessibility.php"),
            str(root / "wordpress-theme/skyyrose-flagship/inc/accessibility-fix.php"),
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return BeautifulSoup(rendered.stdout, "html.parser")


@pytest.fixture(scope="module")
def homepage() -> BeautifulSoup:
    return _load("homepage.html")


@pytest.fixture(scope="module")
def black_rose() -> BeautifulSoup:
    return _load("black_rose.html")


@pytest.fixture(scope="module")
def signature() -> BeautifulSoup:
    return _load("signature.html")


@pytest.fixture(scope="module")
def shop() -> BeautifulSoup:
    return _load("shop.html")


# ---------------------------------------------------------------------------
# A11Y-01: No button missing type attribute
# ---------------------------------------------------------------------------


def _assert_buttons_have_type(soup: BeautifulSoup, page: str) -> None:
    """Every <button> element must have an explicit type attribute."""
    bad = [str(btn)[:120] for btn in soup.find_all("button") if not btn.get("type")]
    assert (
        not bad
    ), f"[{page}] A11Y-01: {len(bad)} button(s) missing type= attribute:\n" + "\n".join(bad[:5])


def test_a11y_01_homepage(homepage: BeautifulSoup) -> None:
    _assert_buttons_have_type(homepage, "homepage")


def test_a11y_01_black_rose(black_rose: BeautifulSoup) -> None:
    _assert_buttons_have_type(black_rose, "black_rose")


def test_a11y_01_signature(signature: BeautifulSoup) -> None:
    _assert_buttons_have_type(signature, "signature")


def test_a11y_01_shop(shop: BeautifulSoup) -> None:
    _assert_buttons_have_type(shop, "shop")


# ---------------------------------------------------------------------------
# A11Y-02 + A11Y-08: All id attributes are unique (covers duplicate-id check)
# ---------------------------------------------------------------------------


def _assert_unique_ids(soup: BeautifulSoup, page: str) -> None:
    """Every id= value must appear exactly once in the document body.

    Scoped to <body> only — WordPress double-emits <link id="..."> stylesheet
    handles in <head> on cached pages.  WooCommerce also emits deferred-CSS
    <link> tags inline in <body> (inside <noscript> and as load-event loaders)
    which produce harmless CSS-infrastructure ID duplicates.  Both patterns are
    excluded: only non-<link> / non-<style> body elements are checked.
    """
    _css_tag_names = {"link", "style"}
    root = soup.body if soup.body is not None else soup
    ids = [tag["id"] for tag in root.find_all(id=True) if tag.name not in _css_tag_names]
    seen: set[str] = set()
    dupes: list[str] = []
    for id_val in ids:
        if id_val in seen:
            dupes.append(id_val)
        seen.add(id_val)
    assert not dupes, f"[{page}] A11Y-02/08: {len(dupes)} duplicate id(s) found: {dupes[:10]}"


def test_a11y_02_08_homepage(homepage: BeautifulSoup) -> None:
    _assert_unique_ids(homepage, "homepage")


def test_a11y_02_08_black_rose(black_rose: BeautifulSoup) -> None:
    _assert_unique_ids(black_rose, "black_rose")


def test_a11y_02_08_signature(signature: BeautifulSoup) -> None:
    _assert_unique_ids(signature, "signature")


def test_a11y_02_08_shop(shop: BeautifulSoup) -> None:
    _assert_unique_ids(shop, "shop")


# ---------------------------------------------------------------------------
# A11Y-03: Every heading has non-whitespace text OR aria-hidden="true"
# ---------------------------------------------------------------------------


def _is_in_display_none_subtree(tag: BeautifulSoup) -> bool:
    """Return True if the tag or any ancestor has inline style display:none."""
    for el in [tag, *tag.parents]:
        if el.name is None:
            break
        style = el.get("style", "") or ""
        # Normalize to handle spaces around colon/semicolon
        if "display" in style and "none" in style:
            # Basic check: display:none or display: none
            import re

            if re.search(r"display\s*:\s*none", style, re.IGNORECASE):
                return True
    return False


def _assert_headings_have_text(soup: BeautifulSoup, page: str) -> None:
    """Every h1-h6 must have visible text or be aria-hidden.

    Headings inside display:none subtrees are excluded — they are not
    rendered to screen and cannot be navigated by AT (covers Jetpack
    carousel overlay elements in the shop page).
    """
    bad: list[str] = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        if tag.get("aria-hidden") == "true":
            continue
        if _is_in_display_none_subtree(tag):
            continue
        text = tag.get_text(strip=True)
        if not text:
            bad.append(str(tag)[:120])
    assert (
        not bad
    ), f"[{page}] A11Y-03: {len(bad)} heading(s) with no text and no aria-hidden:\n" + "\n".join(
        bad[:5]
    )


def test_a11y_03_homepage(homepage: BeautifulSoup) -> None:
    _assert_headings_have_text(homepage, "homepage")


def test_a11y_03_black_rose(black_rose: BeautifulSoup) -> None:
    _assert_headings_have_text(black_rose, "black_rose")


def test_a11y_03_signature(signature: BeautifulSoup) -> None:
    _assert_headings_have_text(signature, "signature")


def test_a11y_03_shop(shop: BeautifulSoup) -> None:
    _assert_headings_have_text(shop, "shop")


# ---------------------------------------------------------------------------
# A11Y-04: Every <a> with empty visible text has a non-empty accessible label
# ---------------------------------------------------------------------------


def _assert_links_have_labels(soup: BeautifulSoup, page: str) -> None:
    """An <a> with no visible text must have aria-label, aria-labelledby,
    or a child <img> with a non-empty alt attribute (icon links pattern).

    Anchors with inline ``display: none`` are excluded — they are removed
    from the tab order and are not navigable by AT (covers Jetpack carousel
    download links in the shop page).
    """
    import re

    bad: list[str] = []
    for anchor in soup.find_all("a"):
        text = anchor.get_text(strip=True)
        if text:
            continue
        # Skip anchors with inline display:none — not in tab order
        style = anchor.get("style", "") or ""
        if re.search(r"display\s*:\s*none", style, re.IGNORECASE):
            continue
        # Check accessible label alternatives
        if anchor.get("aria-label", "").strip():
            continue
        if anchor.get("aria-labelledby", "").strip():
            continue
        # Accept img child with non-empty alt
        img_child = anchor.find("img")
        if img_child and img_child.get("alt", "").strip():
            continue
        # Accept aria-hidden anchor (decorative, not in tab order)
        if anchor.get("aria-hidden") == "true":
            continue
        bad.append(str(anchor)[:120])
    assert not bad, f"[{page}] A11Y-04: {len(bad)} link(s) with no accessible label:\n" + "\n".join(
        bad[:5]
    )


def test_a11y_04_homepage(homepage: BeautifulSoup) -> None:
    _assert_links_have_labels(homepage, "homepage")


def test_a11y_04_black_rose(black_rose: BeautifulSoup) -> None:
    _assert_links_have_labels(black_rose, "black_rose")


def test_a11y_04_signature(signature: BeautifulSoup) -> None:
    _assert_links_have_labels(signature, "signature")


def test_a11y_04_shop(shop: BeautifulSoup) -> None:
    _assert_links_have_labels(shop, "shop")


# ---------------------------------------------------------------------------
# A11Y-05: aria-hidden elements that are focusable must have tabindex="-1"
# ---------------------------------------------------------------------------

_FOCUSABLE_SELECTORS = {"a", "button", "input", "select", "textarea"}


def _assert_aria_hidden_not_focusable(soup: BeautifulSoup, page: str) -> None:
    """Any element with aria-hidden="true" that is also natively focusable
    (a[href], button, input, select, textarea) or has tabindex >= 0
    must declare tabindex="-1".
    """
    bad: list[str] = []
    for tag in soup.find_all(attrs={"aria-hidden": "true"}):
        is_native_focusable = tag.name in _FOCUSABLE_SELECTORS and (
            tag.name != "a" or tag.get("href") is not None
        )
        tabindex = tag.get("tabindex")
        has_explicit_tabindex = tabindex is not None
        is_removed_from_focus = tabindex == "-1"

        if is_native_focusable and not is_removed_from_focus:
            bad.append(str(tag)[:120])
            continue

        if has_explicit_tabindex and not is_removed_from_focus:
            # tabindex >= 0 makes any element focusable
            try:
                if int(tabindex) >= 0:
                    bad.append(str(tag)[:120])
            except ValueError:
                pass  # non-integer tabindex — ignore

    assert (
        not bad
    ), f"[{page}] A11Y-05: {len(bad)} aria-hidden element(s) still focusable:\n" + "\n".join(
        bad[:5]
    )


def test_a11y_05_homepage(homepage: BeautifulSoup) -> None:
    _assert_aria_hidden_not_focusable(homepage, "homepage")


def test_a11y_05_black_rose(black_rose: BeautifulSoup) -> None:
    _assert_aria_hidden_not_focusable(black_rose, "black_rose")


def test_a11y_05_signature(signature: BeautifulSoup) -> None:
    _assert_aria_hidden_not_focusable(signature, "signature")


def test_a11y_05_shop(shop: BeautifulSoup) -> None:
    _assert_aria_hidden_not_focusable(shop, "shop")


# ---------------------------------------------------------------------------
# A11Y-06: Every input (exc. hidden/submit/button) has a label
# ---------------------------------------------------------------------------


def _assert_inputs_have_labels(soup: BeautifulSoup, page: str) -> None:
    """Every <input> that is not type hidden/submit/button must have one of:
    - a <label for="input-id"> referencing its id
    - aria-label
    - aria-labelledby
    """
    _exempt_types = {"hidden", "submit", "button", "image", "reset"}
    bad: list[str] = []
    for inp in soup.find_all("input"):
        input_type = (inp.get("type") or "text").lower()
        if input_type in _exempt_types:
            continue
        if inp.get("aria-label", "").strip():
            continue
        if inp.get("aria-labelledby", "").strip():
            continue
        input_id = inp.get("id")
        if input_id and soup.find("label", attrs={"for": input_id}):
            continue
        bad.append(str(inp)[:120])
    assert (
        not bad
    ), f"[{page}] A11Y-06: {len(bad)} input(s) without accessible label:\n" + "\n".join(bad[:5])


def test_a11y_06_homepage(homepage: BeautifulSoup) -> None:
    _assert_inputs_have_labels(homepage, "homepage")


def test_a11y_06_black_rose(black_rose: BeautifulSoup) -> None:
    _assert_inputs_have_labels(black_rose, "black_rose")


def test_a11y_06_signature(signature: BeautifulSoup) -> None:
    _assert_inputs_have_labels(signature, "signature")


def test_a11y_06_shop(shop: BeautifulSoup) -> None:
    _assert_inputs_have_labels(shop, "shop")


# ---------------------------------------------------------------------------
# A11Y-07: Skip-link exists AND its href target id resolves in the document
# ---------------------------------------------------------------------------


def _assert_skip_link(soup: BeautifulSoup, page: str) -> None:
    """A .skip-link anchor must exist and its href="#<id>" target must be
    present in the document as id="<id>".
    """
    skip_link = soup.find("a", class_="skip-link")
    assert skip_link is not None, f"[{page}] A11Y-07: no element with class 'skip-link' found"
    href = skip_link.get("href", "")
    assert href.startswith(
        "#"
    ), f"[{page}] A11Y-07: skip-link href='{href}' does not start with '#'"
    target_id = href[1:]  # strip the leading '#'
    assert target_id, f"[{page}] A11Y-07: skip-link href is '#' with no id fragment"
    target_el = soup.find(id=target_id)
    assert (
        target_el is not None
    ), f"[{page}] A11Y-07: skip-link href='{href}' but id='{target_id}' not found in document"


def test_a11y_07_homepage(homepage: BeautifulSoup) -> None:
    _assert_skip_link(homepage, "homepage")


def test_a11y_07_black_rose(black_rose: BeautifulSoup) -> None:
    _assert_skip_link(black_rose, "black_rose")


def test_a11y_07_signature(signature: BeautifulSoup) -> None:
    _assert_skip_link(signature, "signature")


def test_a11y_07_shop(shop: BeautifulSoup) -> None:
    _assert_skip_link(shop, "shop")


# ---------------------------------------------------------------------------
# A11Y-09: Image loading strategy (homepage only)
# ---------------------------------------------------------------------------


def test_a11y_09_image_loading(homepage: BeautifulSoup) -> None:
    """A11Y-09 (homepage only): all <img> elements that are not hero/logo/brand/monogram
    images must have loading="lazy".

    inc/accessibility-fix.php Section 8 adds loading="lazy" to every <img> that:
      - does not already have a loading= attribute, AND
      - does not have a class matching hero|logo|brand|monogram

    There is NO first-img-eager logic in the PHP fix — all non-hero images get lazy.
    """
    import re

    imgs = homepage.find_all("img")
    if not imgs:
        pytest.skip("No <img> elements found in homepage fixture")

    _hero_pattern = re.compile(r"\b(hero|logo|brand|monogram)\b", re.IGNORECASE)

    bad: list[str] = []
    for img in imgs:
        class_str = " ".join(img.get("class") or [])
        if _hero_pattern.search(class_str):
            # Hero/logo/brand/monogram images are exempt from lazy loading
            continue
        if img.get("loading") != "lazy":
            bad.append(f"  src={img.get('src', '')[:80]}  class='{class_str}'")

    assert not bad, f"A11Y-09: {len(bad)} non-hero img(s) missing loading='lazy':\n" + "\n".join(
        bad[:5]
    )


def test_historical_shop_capture_reproduces_original_defects() -> None:
    raw = BeautifulSoup((FIXTURES_DIR / "shop.html").read_text(encoding="utf-8"), "html.parser")
    with pytest.raises(AssertionError, match="duplicate id"):
        _assert_unique_ids(raw, "historical shop")
    with pytest.raises(AssertionError, match="without accessible label"):
        _assert_inputs_have_labels(raw, "historical shop")


@pytest.mark.parametrize(
    ("markup", "expected_label"),
    [
        ('<input type="search" class="search-overlay__input" />', "Search the collection"),
        ('<input class="search-overlay__input" aria-label="Find pieces">', "Find pieces"),
        ('<input class="search-overlay__input" aria-labelledby="label">', None),
        ('<input id="search-overlay-input" class="search-overlay__input">', None),
        ('<input type="search" class="other-search">', None),
        ('<input data-class="search-overlay__input">', None),
        ('<input class="search-overlay__input-extra">', None),
        ('<input class="search-overlay__input" data-id="hint">', "Search the collection"),
        ("<input data-hint=' class=\"search-overlay__input\"'>", None),
        ("<input class='search-overlay__input' data-hint=\" id='hint'\">", "Search the collection"),
        ("<input CLASS='search-overlay__input' ARIA-LABEL='Search here'>", "Search here"),
        ('<input class="search-overlay__input" data-hint="a > b" aria-label="Keep me">', "Keep me"),
    ],
)
def test_legacy_search_label_preserves_existing_authority(
    tmp_path: Path, markup: str, expected_label: str | None
) -> None:
    capture = tmp_path / "overlay.html"
    capture.write_text(
        '<html><head></head><body><span id="label">Search</span>'
        + markup
        + "<!--"
        + "padding" * 40
        + "--></body></html>",
        encoding="utf-8",
    )
    rendered = _load(str(capture))
    assert rendered.input.get("class") == BeautifulSoup(markup, "html.parser").input.get("class")
    assert rendered.input.get("aria-label") == expected_label
