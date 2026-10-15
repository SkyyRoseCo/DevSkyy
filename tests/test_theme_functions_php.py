"""Static contract tests for wordpress-theme/skyyrose-flagship/functions.php.

functions.php cannot be executed under PHPUnit (it ``define()``s constants the
PHPUnit bootstrap already defines, and ``require_once``s ~60 WordPress-dependent
modules), so these tests parse it. They pin the things that break silently in
production: the version triple, the kill-switch defaults, load order, and
include lists that name files which no longer exist.
"""

from __future__ import annotations

import re

import pytest

from tests.sparse_guard import REPO_ROOT, requires_tree

THEME_REL = "wordpress-theme/skyyrose-flagship"
THEME = REPO_ROOT / THEME_REL
FUNCTIONS = THEME / "functions.php"

# Generated from assets/brand/brand.yaml at build; deliberately untracked
# (see theme CLAUDE.md "Brand constants"), so it is absent from a fresh checkout.
GENERATED_INCLUDES = {"/inc/brand.generated.php"}

pytestmark = requires_tree(f"{THEME_REL}/functions.php")


@pytest.fixture(scope="module")
def source() -> str:
    return FUNCTIONS.read_text(encoding="utf-8")


def _array_entries(source: str, var: str) -> list[str]:
    """String entries of ``$var = array( ... );`` in source order."""
    match = re.search(rf"\${var}\s*=\s*array\((.*?)\n\s*\);", source, re.DOTALL)
    assert match, f"${var} array not found in functions.php"
    # Strip // line comments so commented-out paths are not counted.
    body = re.sub(r"//[^\n]*", "", match.group(1))
    return re.findall(r"'(/inc/[^']+\.php)'", body)


def _version_define(source: str) -> str:
    match = re.search(r"define\(\s*'SKYYROSE_VERSION'\s*,\s*'([^']+)'\s*\)", source)
    assert match, "SKYYROSE_VERSION define not found"
    return match.group(1)


def test_abspath_guard_precedes_any_code(source: str) -> None:
    guard = source.index("defined( 'ABSPATH' )")
    first_define = source.index("define(")
    assert guard < first_define, "ABSPATH guard must run before any define()"
    assert "exit;" in source[guard:first_define]


def test_version_is_semver(source: str) -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", _version_define(source))


def test_version_triple_in_sync(source: str) -> None:
    """functions.php, style.css, readme.txt — the cache-bust param on ~52 enqueues."""
    version = _version_define(source)
    style = re.search(r"^Version:\s*(\S+)", (THEME / "style.css").read_text(), re.M)
    readme = re.search(r"^Stable tag:\s*(\S+)", (THEME / "readme.txt").read_text(), re.M)
    assert style and style.group(1) == version, f"style.css {style and style.group(1)} != {version}"
    assert (
        readme and readme.group(1) == version
    ), f"readme.txt {readme and readme.group(1)} != {version}"


def test_legacy_constant_aliases_defined(source: str) -> None:
    for const in (
        "SKYYROSE_DIR",
        "SKYYROSE_URI",
        "SKYYROSE_THEME_DIR",
        "SKYYROSE_THEME_URI",
        "SKYYROSE_ASSETS_URI",
    ):
        assert re.search(rf"define\(\s*'{const}'", source), f"{const} not defined"


def test_coming_soon_mode_defaults_off(source: str) -> None:
    """true => HTTP 503 for every public visitor; must never ship on by default."""
    match = re.search(r"define\(\s*'SKYYROSE_COMING_SOON_MODE'\s*,\s*(\w+)\s*\)", source)
    assert match and match.group(1) == "false"


def test_concatenation_stays_disabled(source: str) -> None:
    """Intentional WP.com MIME/404 workaround — do not 'fix'."""
    assert re.search(r"define\(\s*'CONCATENATE_SCRIPTS'\s*,\s*false\s*\)", source)
    assert "$GLOBALS['concatenate_scripts'] = false;" in source


def test_both_overrides_are_overridable(source: str) -> None:
    assert "! defined( 'SKYYROSE_COMING_SOON_MODE' )" in source
    assert "! defined( 'CONCATENATE_SCRIPTS' )" in source


def test_core_includes_load_brand_first(source: str) -> None:
    core = _array_entries(source, "skyyrose_core_includes")
    assert core[0] == "/inc/brand.generated.php"


@pytest.mark.parametrize("var", ["skyyrose_core_includes", "skyyrose_woo_includes"])
def test_include_lists_have_no_duplicates(source: str, var: str) -> None:
    entries = _array_entries(source, var)
    assert entries, f"${var} parsed empty"
    dupes = {e for e in entries if entries.count(e) > 1}
    assert not dupes, f"duplicate includes in ${var}: {sorted(dupes)}"


def test_no_include_listed_in_both_core_and_woo(source: str) -> None:
    core = set(_array_entries(source, "skyyrose_core_includes"))
    woo = set(_array_entries(source, "skyyrose_woo_includes"))
    assert not core & woo


@pytest.mark.parametrize(
    "var", ["skyyrose_core_includes", "skyyrose_woo_includes", "skyyrose_builder_stubs"]
)
def test_listed_includes_exist_on_disk(source: str, var: str) -> None:
    """The loader silently skips missing files — a deleted module becomes a dead feature."""
    missing = [
        e
        for e in _array_entries(source, var)
        if e not in GENERATED_INCLUDES and not (THEME / e.lstrip("/")).is_file()
    ]
    assert not missing, f"${var} names files that do not exist: {missing}"


def test_unconditional_builder_requires_exist(source: str) -> None:
    """These are bare require_once — a missing file is a fatal on every request."""
    required = re.findall(r"^require_once SKYYROSE_DIR \. '(/inc/[^']+\.php)';", source, re.M)
    assert required, "no unconditional require_once lines found"
    missing = [r for r in required if not (THEME / r.lstrip("/")).is_file()]
    assert not missing, f"fatal on load, missing: {missing}"


def test_elementor_files_load_on_elementor_loaded(source: str) -> None:
    assert re.search(r"add_action\(\s*'elementor/loaded'", source)
    for rel in ("/inc/builders/elementor.php", "/inc/builders/elementor-compat.php"):
        assert rel in source
        assert (THEME / rel.lstrip("/")).is_file(), f"{rel} missing"


def test_woo_includes_gated_on_woocommerce_class(source: str) -> None:
    gate = source.index("class_exists( 'WooCommerce' )")
    woo_var = source.index("$skyyrose_woo_includes")
    assert gate < woo_var


def test_no_debug_leftovers(source: str) -> None:
    found = re.findall(r"(?<![\w>:])(var_dump|print_r|error_log|die)\s*\(", source)
    assert not found, f"debug leftovers in functions.php: {sorted(set(found))}"


def test_php_syntax_markers_balanced(source: str) -> None:
    assert source.startswith("<?php")
    assert not source.rstrip().endswith("?>"), "closing tag risks trailing-whitespace output"
    assert source.count("(") == source.count(")")
