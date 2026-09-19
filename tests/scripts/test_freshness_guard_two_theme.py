"""scripts/freshness-guard.sh covers BOTH themes.

skyyrose-flagship: style.css Version / functions.php SKYYROSE_VERSION /
readme.txt Stable tag, .min rebuilt via wordpress-theme/package.json.
skyyrose-flagship-2: style.css Version / functions.php SKYYROSE2_VERSION /
readme.txt Stable tag, .min rebuilt via its own scripts/build-assets.mjs.

Every case runs the real script inside a throwaway git repo (tmp_path) so the
pre-commit path is exercised end to end and each assertion can fail.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GUARD = PROJECT_ROOT / "scripts" / "freshness-guard.sh"

THEMES = {
    "skyyrose-flagship": ("SKYYROSE_VERSION", "1.0.0"),
    "skyyrose-flagship-2": ("SKYYROSE2_VERSION", "2.4.4"),
}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout


def write_triple(repo: Path, theme: str, version: str) -> None:
    const = THEMES[theme][0]
    base = repo / "wordpress-theme" / theme
    base.mkdir(parents=True, exist_ok=True)
    (base / "style.css").write_text(f"/*\nTheme Name: {theme}\nVersion: {version}\n*/\n")
    (base / "functions.php").write_text(f"<?php\ndefine( '{const}', '{version}' );\n")
    (base / "readme.txt").write_text(f"=== {theme} ===\nStable tag: {version}\n")


@pytest.fixture
def guard_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    git(repo, "config", "user.email", "guard@test")
    git(repo, "config", "user.name", "guard")
    (repo / "scripts" / "freshness-guard.sh").write_bytes(GUARD.read_bytes())
    for theme, (_, version) in THEMES.items():
        write_triple(repo, theme, version)
        css = repo / "wordpress-theme" / theme / "assets" / "css"
        css.mkdir(parents=True)
        (css / "theme.css").write_text("body {\n  color: red;\n}\n")
        (css / "theme.min.css").write_text("body{color:red}")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "init")
    return repo


def run_guard(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "scripts/freshness-guard.sh", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def bump_style(repo: Path, theme: str, old: str, new: str) -> None:
    style = repo / "wordpress-theme" / theme / "style.css"
    style.write_text(style.read_text().replace(f"Version: {old}", f"Version: {new}"))
    git(repo, "add", str(style.relative_to(repo)))


class TestVersionTriple:
    def test_in_sync_flagship2_passes(self, guard_repo: Path):
        style = guard_repo / "wordpress-theme" / "skyyrose-flagship-2" / "style.css"
        style.write_text(style.read_text() + "/* touched */\n")
        git(guard_repo, "add", "wordpress-theme/skyyrose-flagship-2/style.css")
        result = run_guard(guard_repo)
        assert result.returncode == 0, result.stdout
        assert "skyyrose-flagship-2 version synced (2.4.4)" in result.stdout

    def test_bumping_only_flagship2_style_css_fails(self, guard_repo: Path):
        bump_style(guard_repo, "skyyrose-flagship-2", "2.4.4", "2.4.5")
        result = run_guard(guard_repo)
        assert result.returncode == 1, result.stdout
        assert "skyyrose-flagship-2 VERSION DRIFT" in result.stdout
        assert "style.css=2.4.5" in result.stdout
        assert "functions.php(SKYYROSE2_VERSION)=2.4.4" in result.stdout
        # The other theme was not staged, so it is not reported at all.
        assert "skyyrose-flagship version synced" not in result.stdout
        assert "skyyrose-flagship VERSION DRIFT" not in result.stdout

    def test_bumping_only_flagship_style_css_still_fails(self, guard_repo: Path):
        bump_style(guard_repo, "skyyrose-flagship", "1.0.0", "1.0.1")
        result = run_guard(guard_repo)
        assert result.returncode == 1, result.stdout
        assert "skyyrose-flagship VERSION DRIFT" in result.stdout
        assert "functions.php(SKYYROSE_VERSION)=1.0.0" in result.stdout
        assert "skyyrose-flagship-2" not in result.stdout

    def test_flagship2_constant_does_not_satisfy_flagship_check(self, guard_repo: Path):
        # SKYYROSE_VERSION grep must not be satisfied by SKYYROSE2_VERSION.
        fn = guard_repo / "wordpress-theme" / "skyyrose-flagship" / "functions.php"
        fn.write_text("<?php\ndefine( 'SKYYROSE2_VERSION', '1.0.0' );\n")
        git(guard_repo, "add", "wordpress-theme/skyyrose-flagship/functions.php")
        result = run_guard(guard_repo)
        assert result.returncode == 1, result.stdout
        assert "skyyrose-flagship VERSION DRIFT" in result.stdout


class TestMinStaleness:
    @pytest.mark.parametrize(
        ("theme", "hint"),
        [
            (
                "skyyrose-flagship-2",
                "(cd wordpress-theme/skyyrose-flagship-2 && npm run build:assets)",
            ),
            ("skyyrose-flagship", "(cd wordpress-theme && npm run build)"),
        ],
    )
    def test_source_edit_without_min_fails_with_theme_specific_hint(
        self, guard_repo: Path, theme: str, hint: str
    ):
        css = guard_repo / "wordpress-theme" / theme / "assets" / "css" / "theme.css"
        css.write_text(css.read_text() + ".x {\n  color: blue;\n}\n")
        git(guard_repo, "add", f"wordpress-theme/{theme}/assets/css/theme.css")
        result = run_guard(guard_repo)
        assert result.returncode == 1, result.stdout
        assert (
            f"edited source not rebuilt: wordpress-theme/{theme}/assets/css/theme.css"
            in result.stdout
        )
        assert hint in result.stdout

    def test_source_edit_with_min_staged_passes(self, guard_repo: Path):
        base = guard_repo / "wordpress-theme" / "skyyrose-flagship-2" / "assets" / "css"
        (base / "theme.css").write_text("body {\n  color: red;\n}\n.x {\n  color: blue;\n}\n")
        (base / "theme.min.css").write_text("body{color:red}.x{color:blue}")
        git(guard_repo, "add", "wordpress-theme/skyyrose-flagship-2/assets/css")
        result = run_guard(guard_repo)
        assert result.returncode == 0, result.stdout
        assert "edited assets have their rebuilt .min staged" in result.stdout


PINS = {"clean-css": "5.3.3", "terser": "5.36.0"}


def install_theme2_builder(repo: Path, installed: dict[str, str]) -> None:
    """Give the throwaway repo a flagship-2 builder plus fake node_modules.

    ``installed`` maps package name -> the version node will resolve. The stub
    builder exits 0 in ``--check`` mode, so whether the guard reports the V2
    ``.min`` audit as run or skipped depends only on the version probe.
    """
    theme2 = repo / "wordpress-theme" / "skyyrose-flagship-2"
    (theme2 / "scripts").mkdir(parents=True, exist_ok=True)
    (theme2 / "scripts" / "build-assets.mjs").write_text(
        "const checkOnly = process.argv.includes('--check');\nprocess.exit(0);\n"
    )
    (theme2 / "package.json").write_text(
        json.dumps({"name": "stub", "devDependencies": PINS}) + "\n"
    )
    for name, version in installed.items():
        pkg_dir = theme2 / "node_modules" / name
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (pkg_dir / "package.json").write_text(json.dumps({"name": name, "version": version}))
        (pkg_dir / "index.js").write_text("module.exports = {};\n")


@pytest.mark.skipif(shutil.which("node") is None, reason="node missing")
class TestFlagship2PinnedToolchain:
    """freshness-guard must use the same exact-version probe as scripts/ci-local.sh.

    Any resolvable clean-css/terser is not enough: a different minifier version
    produces different bytes and the audit would report false drift (or, worse,
    false freshness). Mismatched versions must downgrade the check to a skip.
    """

    def test_pinned_versions_run_the_audit(self, guard_repo: Path):
        install_theme2_builder(guard_repo, PINS)
        result = run_guard(guard_repo, "--all")
        assert "skyyrose-flagship-2 .min build up to date" in result.stdout, result.stdout

    def test_mismatched_terser_version_skips_the_audit(self, guard_repo: Path):
        install_theme2_builder(guard_repo, {**PINS, "terser": "5.0.0"})
        result = run_guard(guard_repo, "--all")
        assert "skyyrose-flagship-2 .min build up to date" not in result.stdout, result.stdout
        assert "skyyrose-flagship-2 .min audit skipped" in result.stdout, result.stdout
        assert "pinned" in result.stdout, result.stdout

    def test_mismatched_clean_css_version_skips_the_audit(self, guard_repo: Path):
        install_theme2_builder(guard_repo, {**PINS, "clean-css": "4.2.4"})
        result = run_guard(guard_repo, "--all")
        assert "skyyrose-flagship-2 .min build up to date" not in result.stdout, result.stdout
        assert "skyyrose-flagship-2 .min audit skipped" in result.stdout, result.stdout

    def test_probe_matches_ci_local_verbatim(self):
        """The node probe is copied from ci-local.sh; drift between the two is the bug."""
        ci_local = (PROJECT_ROOT / "scripts" / "ci-local.sh").read_text()
        guard = GUARD.read_text()
        probe = "if (v !== pkg[name]) { console.error(`${name} ${v} != pinned ${pkg[name]}`); process.exit(1); }"
        assert probe in ci_local
        assert probe in guard

    def test_v2_logs_do_not_use_fixed_tmp_paths(self):
        guard = GUARD.read_text()
        assert "/tmp/fg_min2.log" not in guard
        assert "/tmp/fg_fix_min2.log" not in guard
        assert "mktemp -d" in guard
