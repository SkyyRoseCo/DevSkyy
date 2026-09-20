"""CI + local-CI + Prettier config cover both WordPress themes.

- .github/workflows/ci.yml: php -l and minification-drift steps run for
  skyyrose-flagship AND skyyrose-flagship-2 (the latter via its own package.json
  in read-only ``check:assets`` mode); the staging environment points at the
  real WP.com staging host.
- scripts/ci-local.sh mirrors the same scope offline.
- prettier really does ignore the files a program owns. The registry that
  declares them, and its parity with .prettierignore and lint-staged, is
  covered by tests/test_machine_managed_files.py.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CI_YML = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
CI_LOCAL = PROJECT_ROOT / "scripts" / "ci-local.sh"
FLAGSHIP2 = PROJECT_ROOT / "wordpress-theme" / "skyyrose-flagship-2"
PRETTIER = PROJECT_ROOT / "node_modules" / ".bin" / "prettier"
STAGING_URL = "https://staging-7e48-skyyrose.wpcomstaging.com"


@pytest.fixture(scope="module")
def workflow() -> dict:
    return yaml.safe_load(CI_YML.read_text())


def step(job: dict, name: str) -> dict:
    matches = [s for s in job["steps"] if s.get("name") == name]
    assert matches, f"step {name!r} missing; have {[s.get('name') for s in job['steps']]}"
    return matches[0]


class TestCiWorkflow:
    def test_php_lint_covers_both_themes(self, workflow: dict):
        run = step(workflow["jobs"]["wordpress-theme"], "PHP syntax check (CI-03)")["run"]
        find_line = next(line for line in run.splitlines() if "find " in line)
        assert "wordpress-theme/skyyrose-flagship " in find_line + " "
        assert "wordpress-theme/skyyrose-flagship-2" in find_line

    def test_flagship_min_drift_scope_unchanged(self, workflow: dict):
        run = step(workflow["jobs"]["wordpress-theme"], "Check for minification drift (CI-05)")[
            "run"
        ]
        assert "-- wordpress-theme/skyyrose-flagship " in run.replace("\\\n", " ")

    def test_flagship2_min_drift_uses_its_own_build(self, workflow: dict):
        job = workflow["jobs"]["wordpress-theme"]
        install = step(job, "Install Flagship 2 theme dependencies")
        assert install["working-directory"] == "wordpress-theme/skyyrose-flagship-2"
        assert install["run"].strip() == "npm ci"
        check = step(job, "Check Flagship 2 minification drift (CI-05b)")
        assert check["working-directory"] == "wordpress-theme/skyyrose-flagship-2"
        assert "npm run check:assets" in check["run"]
        assert "exit 1" in check["run"]

    def test_flagship2_build_contract_exists(self):
        scripts = json.loads((FLAGSHIP2 / "package.json").read_text())["scripts"]
        assert scripts["check:assets"] == "node scripts/build-assets.mjs --check"
        assert scripts["build:assets"] == "node scripts/build-assets.mjs"
        assert (FLAGSHIP2 / "npm-shrinkwrap.json").exists(), "npm ci needs a lockfile"
        assert "--check" in (FLAGSHIP2 / "scripts" / "build-assets.mjs").read_text()

    def test_staging_environment_url(self, workflow: dict):
        envs = [
            job["environment"]
            for job in workflow["jobs"].values()
            if isinstance(job.get("environment"), dict)
            and job["environment"].get("name") == "staging"
        ]
        assert envs, "no job declares the staging environment"
        assert all(env["url"] == STAGING_URL for env in envs), envs
        assert "staging.skyyrose.com" not in CI_YML.read_text()


# Every environment variable scripts/ci-local.sh reads. The subprocess test
# below scrubs them so a caller's shell (WITH_BUILD=1 → npm ci / npm run build
# in the REAL tree, CI_LOCAL_ROOT → another checkout, FAST/PHP_BIN → skips or
# a different php) cannot change what the test exercises.
CI_LOCAL_ENV_VARS = ("WITH_BUILD", "CI_LOCAL_ROOT", "FAST", "PHP_BIN")


def shell_functions(source: str) -> dict[str, int]:
    """Map each top-level ``name() {`` function in a bash script to its line count."""
    lengths: dict[str, int] = {}
    current: str | None = None
    start = 0
    for lineno, line in enumerate(source.splitlines(), 1):
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\(\)\s*\{", line)
        if match and current is None:
            current, start = match.group(1), lineno
        elif line == "}" and current is not None:
            lengths[current] = lineno - start + 1
            current = None
    return lengths


class TestCiLocal:
    def test_php_lint_scope_includes_flagship2(self):
        source = CI_LOCAL.read_text()
        assert 'THEME2_DIR="wordpress-theme/skyyrose-flagship-2"' in source
        assert 'find "$THEME_DIR" "$THEME2_DIR" -name \'*.php\'' in source
        assert "run check:assets" in source

    def test_env_vars_list_matches_script(self):
        source = CI_LOCAL.read_text()
        read_vars = set(re.findall(r"\$\{(WITH_BUILD|CI_LOCAL_ROOT|FAST|PHP_BIN)[:}]", source))
        assert read_vars == set(CI_LOCAL_ENV_VARS)

    def test_wordpress_theme_job_functions_are_under_50_lines(self):
        # job_wordpress_theme + its _wp* helpers (job_security is 51 lines,
        # pre-existing and outside the two-theme scope).
        lengths = shell_functions(CI_LOCAL.read_text())
        family = {
            n: c for n, c in lengths.items() if n == "job_wordpress_theme" or n.startswith("_wp")
        }
        assert "job_wordpress_theme" in family, lengths
        too_long = {name: n for name, n in family.items() if n >= 50}
        assert not too_long, too_long

    @pytest.mark.skipif(
        shutil.which("php") is None and not Path("/opt/homebrew/bin/php").exists(),
        reason="php missing",
    )
    @pytest.mark.timeout(300)  # php -l over both themes + check:assets exceeds the 10 s default
    def test_wordpress_theme_job_passes(self):
        env = {k: v for k, v in os.environ.items() if k not in CI_LOCAL_ENV_VARS}
        result = subprocess.run(
            ["bash", str(CI_LOCAL), "wordpress-theme"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=600,
            env=env,
        )
        plain = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
        assert result.returncode == 0, plain[-3000:]
        assert "✓ PASS  wordpress-theme: php -l (both themes, all files)" in plain
        assert "✗ FAIL" not in plain
        # Whether the flagship-2 asset check ran or was skipped (deps unresolvable) is reported either way.
        assert re.search(r"(PASS|SKIP)\s+wordpress-theme: skyyrose-flagship-2", plain), plain


# Kept deliberately hand-written rather than derived from
# data/machine-managed-files.json: an independently-authored sample list does
# not share the registry's failure mode, so it still catches a registry that
# lost an entry. Do not "simplify" it into a loop over the registry.
SAMPLES = [
    "plugins/fashion-theme-team/README.md",
    "Comfy/receipts/sample.json",
    "Comfy/quarantine/sample.json",
    "skyyrose/elite_studio/assets/golden/br-001/placement.md",
    "logo-registry.json",
    "wordpress-theme/skyyrose-flagship/data/dossiers/br-001.md",
]


class TestPrettierIgnoreParity:
    """Does prettier ACTUALLY ignore a machine-managed file?

    The list-vs-list parity checks that used to live here scraped the managed
    paths back out of lint-staged.config.mjs's regexes and compared them with
    .prettierignore. lint-staged now reads data/machine-managed-files.json, so
    there is no second list to compare — and the scraper returning nothing made
    one of those checks pass while testing nothing. Registry-vs-.prettierignore
    parity moved to tests/test_machine_managed_files.py, which fails closed in
    both directions; the behavioural checks below stay because asking the real
    prettier binary is evidence no amount of config parsing can give.
    """

    @pytest.mark.skipif(
        not PRETTIER.exists(), reason="root node_modules/.bin/prettier not installed"
    )
    @pytest.mark.parametrize("sample", SAMPLES)
    def test_prettier_reports_sample_ignored(self, sample: str):
        info = subprocess.run(
            [str(PRETTIER), "--file-info", sample],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert json.loads(info)["ignored"] is True, info

    @pytest.mark.skipif(
        not PRETTIER.exists(), reason="root node_modules/.bin/prettier not installed"
    )
    def test_prettier_still_formats_ordinary_markdown(self):
        info = subprocess.run(
            [str(PRETTIER), "--file-info", "README.md"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert json.loads(info)["ignored"] is False, info
