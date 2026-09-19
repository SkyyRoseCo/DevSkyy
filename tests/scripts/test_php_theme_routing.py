"""Per-theme PHP formatting.

Two themes live under wordpress-theme/: skyyrose-flagship (text domain
``skyyrose``, prefix ``skyyrose``) and skyyrose-flagship-2 (text domain
``skyyrose-flagship-2``, prefix ``skyyrose2``). scripts/php-format.sh must
route every staged PHP file to ITS theme's own ruleset, skip a theme that has
none with a notice, and never apply one theme's standard to the other.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
THEMES = PROJECT_ROOT / "wordpress-theme"
FLAGSHIP = THEMES / "skyyrose-flagship"
FLAGSHIP2 = THEMES / "skyyrose-flagship-2"
PHPCBF = FLAGSHIP / "vendor" / "bin" / "phpcbf"
PHPCS = FLAGSHIP / "vendor" / "bin" / "phpcs"
FORMAT_SH = PROJECT_ROOT / "scripts" / "php-format.sh"
LINT_SH = PROJECT_ROOT / "scripts" / "php-lint.sh"
LINT_STAGED = PROJECT_ROOT / "lint-staged.config.mjs"
SAMPLE = FLAGSHIP2 / "inc" / "presentation-registry.php"

needs_phpcs = pytest.mark.skipif(
    not (PHPCBF.exists() and PHPCS.exists()),
    reason="flagship vendor/bin/phpcbf + phpcs not installed (composer install)",
)
needs_php = pytest.mark.skipif(shutil.which("php") is None, reason="php not on PATH")


RULESET_NAMES = (".phpcs.xml", "phpcs.xml", ".phpcs.xml.dist", "phpcs.xml.dist")


def ruleset_path(theme: Path) -> Path:
    """The ruleset a theme declares, in the same order php-format.sh (and PHPCS) resolve it."""
    for name in RULESET_NAMES:
        if (theme / name).is_file():
            return theme / name
    raise AssertionError(f"{theme.name} declares no PHPCS ruleset ({' / '.join(RULESET_NAMES)})")


def ruleset(path: Path) -> tuple[list[str], list[str]]:
    """(text domains, prefixes) a PHPCS ruleset declares."""
    root = ET.parse(path).getroot()
    domains = [
        el.attrib["value"]
        for rule in root.findall("rule")
        if rule.attrib.get("ref") == "WordPress.WP.I18n"
        for prop in rule.iter("property")
        if prop.attrib.get("name") == "text_domain"
        for el in prop.findall("element")
    ]
    prefixes = [
        p
        for cfg in root.findall("config")
        if cfg.attrib.get("name") == "prefixes"
        for p in cfg.attrib["value"].split(",")
    ]
    return domains, prefixes


def style_text_domain(theme: Path) -> str:
    match = re.search(r"^Text Domain:\s*(\S+)", (theme / "style.css").read_text(), re.M)
    assert match, f"{theme.name}/style.css declares no Text Domain"
    return match.group(1)


def phpcs_source_report(standard: Path, file: Path) -> str:
    return subprocess.run(
        [str(PHPCS), f"--standard={standard}", "--report=source", str(file)],
        capture_output=True,
        text=True,
        check=False,
    ).stdout


class TestRulesets:
    def test_each_theme_resolves_exactly_one_ruleset(self):
        # Lead decision: one tracked ruleset per theme (flagship → .phpcs.xml,
        # flagship-2 → phpcs.xml). A second file would shadow it silently.
        assert ruleset_path(FLAGSHIP).name == ".phpcs.xml"
        assert ruleset_path(FLAGSHIP2).name == "phpcs.xml"
        for theme in (FLAGSHIP, FLAGSHIP2):
            present = [name for name in RULESET_NAMES if (theme / name).is_file()]
            assert len(present) == 1, f"{theme.name} has duplicate rulesets: {present}"

    def test_flagship2_declares_its_own_identity(self):
        domains, prefixes = ruleset(ruleset_path(FLAGSHIP2))
        assert domains == [style_text_domain(FLAGSHIP2)] == ["skyyrose-flagship-2"]
        assert "skyyrose2" in prefixes
        assert "skyyrose" not in prefixes, "flagship prefix must not leak into flagship-2"

    def test_flagship_ruleset_untouched(self):
        domains, prefixes = ruleset(ruleset_path(FLAGSHIP))
        assert domains == [style_text_domain(FLAGSHIP)] == ["skyyrose"]
        assert prefixes == ["skyyrose"]

    @needs_phpcs
    def test_flagship2_file_has_zero_text_domain_mismatch_under_its_ruleset(self, tmp_path):
        copy = tmp_path / "presentation-registry.php"
        shutil.copy(SAMPLE, copy)
        wrong = phpcs_source_report(ruleset_path(FLAGSHIP), copy)
        right = phpcs_source_report(ruleset_path(FLAGSHIP2), copy)
        # RED counterpart: the flagship standard DOES flag the file, so the
        # assertion below can fail if the routing ever regresses.
        assert "WordPress.WP.I18n.TextDomainMismatch" in wrong
        assert "TextDomainMismatch" not in right
        assert "ShortPrefixPassed" not in right, "WPCS rejected a configured prefix"


@pytest.fixture
def scratch_repo(tmp_path: Path) -> Path:
    """A throwaway repo mirroring wordpress-theme/<theme>/ layout + the wrapper."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    shutil.copy(FORMAT_SH, repo / "scripts" / "php-format.sh")
    for theme in (FLAGSHIP, FLAGSHIP2):
        dest = repo / "wordpress-theme" / theme.name
        (dest / "inc").mkdir(parents=True)
        source = ruleset_path(theme)
        shutil.copy(source, dest / source.name)
    shutil.copy(SAMPLE, repo / "wordpress-theme" / FLAGSHIP2.name / "inc" / SAMPLE.name)
    (repo / "wordpress-theme" / FLAGSHIP.name / "inc" / "v1.php").write_text(
        "<?php\necho esc_html__( 'x', 'skyyrose' );\n"
    )
    orphan = repo / "wordpress-theme" / "no-ruleset-theme" / "inc"
    orphan.mkdir(parents=True)
    shutil.copy(SAMPLE, orphan / "orphan.php")
    return repo


def run_format(repo: Path, *files: str, phpcbf: Path = PHPCBF) -> subprocess.CompletedProcess:
    env = {**os.environ, "PHPCBF": str(phpcbf)}
    return subprocess.run(
        ["bash", "scripts/php-format.sh", *files],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


class TestPhpFormatRouting:
    @needs_phpcs
    def test_each_theme_gets_its_own_ruleset(self, scratch_repo: Path):
        f2 = f"wordpress-theme/{FLAGSHIP2.name}/inc/{SAMPLE.name}"
        v1 = f"wordpress-theme/{FLAGSHIP.name}/inc/v1.php"
        orphan = "wordpress-theme/no-ruleset-theme/inc/orphan.php"
        before_lines = len(SAMPLE.read_text().splitlines())
        before_domain = SAMPLE.read_text().count("'skyyrose-flagship-2'")

        result = run_format(scratch_repo, f2, orphan, v1)

        assert result.returncode == 0, result.stderr
        for theme in (FLAGSHIP2, FLAGSHIP):
            own = ruleset_path(theme).name
            assert (
                f"wordpress-theme/{theme.name} → wordpress-theme/{theme.name}/{own}"
                in result.stdout
            )
        assert (
            "NOTICE — wordpress-theme/no-ruleset-theme has no PHPCS ruleset (.phpcs.xml / phpcs.xml / *.dist)"
            in result.stderr
        )

        formatted = (scratch_repo / f2).read_text()
        # Text domain never rewritten toward the flagship's.
        assert formatted.count("'skyyrose'") == 0
        assert formatted.count("'skyyrose-flagship-2'") >= before_domain
        # Under its own ruleset the formatted file is clean of domain errors.
        assert "TextDomainMismatch" not in phpcs_source_report(
            ruleset_path(FLAGSHIP2), scratch_repo / f2
        )
        # The ruleset-less theme is byte-identical: no foreign standard applied.
        assert (scratch_repo / orphan).read_bytes() == SAMPLE.read_bytes()
        after_lines = len(formatted.splitlines())
        print(f"flagship-2 sample: {before_lines} → {after_lines} lines under its own ruleset")

    def test_missing_phpcbf_fails_closed(self, scratch_repo: Path):
        f2 = f"wordpress-theme/{FLAGSHIP2.name}/inc/{SAMPLE.name}"
        result = run_format(scratch_repo, f2, phpcbf=scratch_repo / "missing" / "phpcbf")
        assert result.returncode == 2
        assert "PHP formatter missing" in result.stderr
        assert (scratch_repo / f2).read_bytes() == SAMPLE.read_bytes()

    @needs_phpcs
    def test_php_outside_a_theme_is_skipped_unchanged(self, scratch_repo: Path):
        loose = scratch_repo / "wordpress-theme" / "loose.php"
        loose.write_text("<?php\n$a=array( 'k'=>1 );\n")
        result = run_format(scratch_repo, "wordpress-theme/loose.php")
        assert result.returncode == 0
        assert "not under wordpress-theme/<theme>/" in result.stderr
        assert loose.read_text() == "<?php\n$a=array( 'k'=>1 );\n"

    def test_lint_staged_php_entry_routes_through_the_wrappers(self):
        source = LINT_STAGED.read_text()
        entry = re.search(
            r"'wordpress-theme/\*\*/\*\.php':\s*files\s*=>\s*commandsFor\(\[(.*?)\]", source, re.S
        )
        assert entry, "lint-staged PHP entry missing"
        assert "bash scripts/php-format.sh" in entry.group(1)
        assert "bash scripts/php-lint.sh" in entry.group(1)


class TestPhpLint:
    def test_missing_interpreter_fails_closed(self):
        source = LINT_SH.read_text()
        branch = re.search(r"php not found.*?\n\s*exit (\d)", source, re.S)
        assert branch, "php-lint.sh has no explicit missing-interpreter branch"
        assert branch.group(1) == "2", "a missing php must not be reported as a passing lint"

    @needs_php
    def test_syntax_error_is_reported(self, tmp_path: Path):
        good = tmp_path / "good.php"
        bad = tmp_path / "bad.php"
        good.write_text("<?php\necho 'ok';\n")
        bad.write_text("<?php\necho 'broken'\n")
        ok = subprocess.run(
            ["bash", str(LINT_SH), str(good)], capture_output=True, text=True, check=False
        )
        assert ok.returncode == 0, ok.stdout + ok.stderr
        fail = subprocess.run(
            ["bash", str(LINT_SH), str(bad)], capture_output=True, text=True, check=False
        )
        assert fail.returncode == 1
        assert "FAIL" in fail.stdout
