"""Static contract tests for wordpress-theme/skyyrose-flagship-2/functions.php (V2).

V2 is a different shape from V1: ``SKYYROSE2_*`` constants, five unconditional
``require_once`` lines (a missing file is a fatal on every request), and
~1400 lines of hook-registered functions. The tests parse the file rather than
execute it, and pin the failure modes that are silent or fatal in production.
"""

from __future__ import annotations

import re

import pytest

from tests.sparse_guard import REPO_ROOT, requires_tree

THEME_REL = "wordpress-theme/skyyrose-flagship-2"
THEME = REPO_ROOT / THEME_REL
FUNCTIONS = THEME / "functions.php"

pytestmark = requires_tree(f"{THEME_REL}/functions.php")


@pytest.fixture(scope="module")
def source() -> str:
    return FUNCTIONS.read_text(encoding="utf-8")


def _version(source: str) -> str:
    match = re.search(r"define\(\s*'SKYYROSE2_VERSION'\s*,\s*'([^']+)'\s*\)", source)
    assert match, "SKYYROSE2_VERSION define not found"
    return match.group(1)


def test_abspath_guard_precedes_any_define(source: str) -> None:
    guard = source.index("defined( 'ABSPATH' ) || exit;")
    assert guard < source.index("define( 'SKYYROSE2_")


def test_version_is_semver(source: str) -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", _version(source))


def test_version_triple_in_sync(source: str) -> None:
    """functions.php, style.css, readme.txt — the cache-bust param for V2 assets."""
    version = _version(source)
    style = re.search(r"^Version:\s*(\S+)", (THEME / "style.css").read_text(), re.M)
    readme = re.search(r"^Stable tag:\s*(\S+)", (THEME / "readme.txt").read_text(), re.M)
    assert style and style.group(1) == version, f"style.css {style and style.group(1)} != {version}"
    assert (
        readme and readme.group(1) == version
    ), f"readme.txt {readme and readme.group(1)} != {version}"


def test_core_constants_defined_once(source: str) -> None:
    for const in ("SKYYROSE2_VERSION", "SKYYROSE2_DIR", "SKYYROSE2_URI"):
        assert len(re.findall(rf"define\(\s*'{const}'", source)) == 1, const


def test_unconditional_requires_exist(source: str) -> None:
    """Bare require_once — a missing file is a fatal on every request."""
    required = re.findall(r"^require_once SKYYROSE2_DIR \. '(/inc/[^']+\.php)';", source, re.M)
    assert len(required) >= 5, "expected the 5 bootstrap includes"
    assert len(required) == len(set(required)), "duplicate require_once"
    missing = [r for r in required if not (THEME / r.lstrip("/")).is_file()]
    assert not missing, f"fatal on load, missing: {missing}"


def test_requires_precede_function_definitions(source: str) -> None:
    last_require = max(m.start() for m in re.finditer(r"^require_once SKYYROSE2_DIR", source, re.M))
    first_function = re.search(r"^function \w+", source, re.M)
    assert first_function and last_require < first_function.start()


def test_function_names_namespaced_and_unique(source: str) -> None:
    names = re.findall(r"^function (\w+)\s*\(", source, re.M)
    assert names, "no top-level functions parsed"
    bad = [n for n in names if not n.startswith("skyyrose2_")]
    assert not bad, f"un-prefixed functions collide with V1/core: {bad}"
    dupes = {n for n in names if names.count(n) > 1}
    assert not dupes, f"redeclared functions are a fatal: {sorted(dupes)}"


def test_hook_callbacks_are_defined(source: str) -> None:
    """add_action/add_filter naming a callback this file never declares is a silent no-op."""
    declared = set(re.findall(r"^function (\w+)\s*\(", source, re.M))
    hooked = re.findall(r"add_(?:action|filter)\(\s*'[^']+'\s*,\s*'(skyyrose2_\w+)'", source)
    assert hooked, "no hooks parsed"
    missing = sorted({h for h in hooked if h not in declared})
    assert not missing, f"hooked but not defined in functions.php: {missing}"


def test_core_hooks_registered(source: str) -> None:
    for hook, callback in (
        ("after_setup_theme", "skyyrose2_setup"),
        ("wp_enqueue_scripts", "skyyrose2_assets"),
        ("wp_head", "skyyrose2_seo_head"),
        ("wp_head", "skyyrose2_schema_head"),
    ):
        assert re.search(
            rf"add_action\(\s*'{hook}'\s*,\s*'{callback}'", source
        ), f"{hook} -> {callback}"


def test_no_debug_leftovers(source: str) -> None:
    found = re.findall(r"(?<![\w>:])(var_dump|print_r|error_log|die)\s*\(", source)
    assert not found, f"debug leftovers in functions.php: {sorted(set(found))}"


def test_no_closing_tag(source: str) -> None:
    assert source.startswith("<?php")
    assert not source.rstrip().endswith("?>"), "closing tag risks trailing-whitespace output"
