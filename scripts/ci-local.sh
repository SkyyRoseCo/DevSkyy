#!/usr/bin/env bash
# =============================================================================
# ci-local.sh — Offline mirror of .github/workflows/ci.yml gating jobs.
# =============================================================================
# GitHub Actions is billing-blocked, so this reproduces the SAME checks the
# CI/CD pipeline runs, locally, with no cloud dependency. It mirrors the six
# jobs the pipeline "summary" gates on:
#   lint · python-tests · security · frontend-tests · threejs-tests · wordpress-theme
#
# Cloud-only steps are intentionally skipped (they cannot run offline and do not
# validate code): Codecov upload, artifact upload, Docker build/push, Vercel /
# Render deploy, CodeQL, GitGuardian.
#
# Usage:
#   scripts/ci-local.sh                 # run all gating jobs
#   scripts/ci-local.sh wordpress-theme # run one job
#   scripts/ci-local.sh lint python-tests
#   FAST=1 scripts/ci-local.sh          # skip heavy installs; SKIP jobs whose deps are absent
#
# Exit code: 0 only if every NON-skipped job passes.
# =============================================================================
set -uo pipefail

# ROOT defaults to this script's repo (../). The pre-push hook overrides it with
# CI_LOCAL_ROOT="$PWD" so a single canonical script can check whichever worktree
# is being pushed, even on branches that don't have scripts/ci-local.sh yet.
ROOT="${CI_LOCAL_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT" || { echo "ci-local: cannot cd to ROOT=$ROOT" >&2; exit 2; }

# macOS fork-safety: block the _scproxy/Network.framework system-proxy lookup in
# test processes. Once Network.framework is armed in a multi-threaded Python
# parent, every subprocess fork child SIGSEGVs in nw_settings_child_has_forked()
# before exec (macOS 26.4 + CPython 3.14 fork path). Offline CI — no proxies.
if [[ "$(uname)" == "Darwin" ]]; then
  export no_proxy="${no_proxy:-*}"
  export NO_PROXY="${NO_PROXY:-*}"
fi

PHP_BIN="${PHP_BIN:-php}"
command -v "$PHP_BIN" >/dev/null 2>&1 || PHP_BIN="/opt/homebrew/bin/php"
THEME_DIR="wordpress-theme/skyyrose-flagship"   # source + built assets live here
THEME_PKG_DIR="wordpress-theme"                  # package.json + build scripts live here
THEME2_DIR="wordpress-theme/skyyrose-flagship-2" # self-contained: own package.json + scripts/build-assets.mjs
FAST="${FAST:-0}"

# Activate the isolated CI python toolchain if present (ci-env/setup.sh creates it).
if [ -f "ci-env/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  . ci-env/.venv/bin/activate
fi

# ── result tracking ──────────────────────────────────────────────────────────
declare -a SUMMARY
OVERALL=0
_pass() { SUMMARY+=("PASS|$1"); printf '  \033[32m✓ PASS\033[0m  %s\n' "$1"; }
_fail() { SUMMARY+=("FAIL|$1"); printf '  \033[31m✗ FAIL\033[0m  %s\n' "$1"; OVERALL=1; }
_skip() { SUMMARY+=("SKIP|$1 — $2"); printf '  \033[33m- SKIP\033[0m  %s (%s)\n' "$1" "$2"; }
_hdr()  { printf '\n\033[1m── %s ───────────────────────────────────────\033[0m\n' "$1"; }
_have() { command -v "$1" >/dev/null 2>&1; }

# Run a command, capturing output; on failure print a trimmed tail.
_run() {
  local label="$1"; shift
  local out
  if out=$("$@" 2>&1); then
    return 0
  else
    printf '    \033[31m%s failed:\033[0m\n' "$label"
    printf '%s\n' "$out" | tail -n 25 | sed 's/^/      /'
    return 1
  fi
}

# ── Job: 🏗️ WordPress Theme ──────────────────────────────────────────────────
# Step CI-03: PHP syntax check across BOTH themes (mirrors ci.yml).
_wp_php_lint() {
  local php_errors=0 file out
  while IFS= read -r file; do
    if ! out=$("$PHP_BIN" -l "$file" 2>&1); then
      printf '    PHP syntax error: %s\n      %s\n' "$file" "$out"
      php_errors=$((php_errors + 1))
    fi
  done < <(find "$THEME_DIR" "$THEME2_DIR" -name '*.php' -not -path '*/node_modules/*' -not -path '*/vendor/*')
  if [ "$php_errors" -eq 0 ]; then _pass "wordpress-theme: php -l (both themes, all files)"; return 0; fi
  _fail "wordpress-theme: php -l ($php_errors error files)"; return 1
}

# skyyrose-flagship-2's builder pins clean-css/terser exactly (npm-shrinkwrap).
# Returns 0 when node resolves BOTH pinned versions (the theme's own
# node_modules, or the shared wordpress-theme/ install); WITH_BUILD=1 installs
# them via npm ci. scripts/freshness-guard.sh copies this probe verbatim.
_wp2_pinned_toolchain() {
  if _have node && ( cd "$THEME2_DIR" && node -e '
    const pkg = require("./package.json").devDependencies;
    for (const name of ["clean-css", "terser"]) {
      const v = require(name + "/package.json").version;
      if (v !== pkg[name]) { console.error(`${name} ${v} != pinned ${pkg[name]}`); process.exit(1); }
    }' ) >/dev/null 2>&1; then
    return 0
  fi
  if [ "${WITH_BUILD:-0}" = "1" ] && _have npm; then
    _run "flagship-2 npm ci" npm --prefix "$THEME2_DIR" ci --no-audit --no-fund && return 0
  fi
  return 1
}

# Step CI-05b: skyyrose-flagship-2 minified assets. Its builder has a
# read-only --check mode, so this is deterministic and never mutates the tree.
_wp2_check_assets() {
  if ! _wp2_pinned_toolchain; then
    _skip "wordpress-theme: skyyrose-flagship-2 check:assets" "pinned clean-css/terser not resolvable — WITH_BUILD=1 runs npm ci"
    return 0
  fi
  if _run "flagship-2 check:assets" npm --prefix "$THEME2_DIR" run check:assets; then
    _pass "wordpress-theme: skyyrose-flagship-2 .min assets match source (check:assets)"; return 0
  fi
  _fail "wordpress-theme: skyyrose-flagship-2 .min drift (cd $THEME2_DIR && npm run build:assets)"; return 1
}

# Step CI-04/05: build assets + minification-drift. OPT-IN only (WITH_BUILD=1).
# Why off by default: `npm run build` regenerates every .min.css/.min.js into
# the worktree, and minifier output is node-version-sensitive (local node may
# differ from CI's node 22) → the drift check fails SPURIOUSLY and the build
# mutates the tree. For diffs that don't touch source CSS/JS (e.g. deletions),
# php -l alone validates. Run `WITH_BUILD=1 ci-local.sh wordpress-theme` (ideally
# via the node-22 Docker/act env) when you actually changed buildable assets.
#
# NOTE: npm install/build run from THEME_PKG_DIR (package.json lives there, not
# in the skyyrose-flagship/ subdir). The min-drift check scopes to THEME_DIR
# because the built .min.* assets live under skyyrose-flagship/assets.
_wp_build_min_drift() {
  local ok=0
  if [ "${WITH_BUILD:-0}" != "1" ]; then
    _skip "wordpress-theme: build + min-drift" "opt-in: WITH_BUILD=1 (needs node-22 parity)"
    return 0
  fi
  [ -d "$THEME_PKG_DIR/node_modules" ] || _run "theme npm install" npm --prefix "$THEME_PKG_DIR" install --no-audit --no-fund
  if _run "theme npm run build" npm --prefix "$THEME_PKG_DIR" run build; then _pass "wordpress-theme: npm run build"; else _fail "wordpress-theme: npm run build"; ok=1; fi
  if git status --porcelain --untracked-files=all -- "$THEME_DIR" | grep -Eq '\.min\.(js|css)$'; then
    _fail "wordpress-theme: min-drift (rebuild differs from committed — check node version parity)"
    git status --porcelain --untracked-files=all -- "$THEME_DIR" | grep -E '\.min\.(js|css)$' | sed 's/^/      /'
    ok=1
  else
    _pass "wordpress-theme: no minification drift"
  fi
  return $ok
}

job_wordpress_theme() {
  _hdr "🏗️  WordPress Theme"
  local ok=1   # historical: 1 = clean, 0 = a step failed (OVERALL is set by _fail)
  _wp_php_lint || ok=0
  _wp2_check_assets || ok=0
  _wp_build_min_drift || ok=0
  return $ok
}

# ── Job: 🔍 Lint & Static Analysis (Python) ──────────────────────────────────
job_lint() {
  _hdr "🔍  Lint & Static Analysis (Python)"
  for t in ruff black isort mypy; do
    if ! _have "$t"; then _skip "lint: $t" "not installed — pip install $t"; continue; fi
    case "$t" in
      ruff)  _run "ruff"  ruff check .                         && _pass "lint: ruff"  || _fail "lint: ruff" ;;
      black) _run "black" black --check . --quiet              && _pass "lint: black" || _fail "lint: black" ;;
      isort) _run "isort" isort --check-only .                 && _pass "lint: isort" || _fail "lint: isort" ;;
      mypy)  _run "mypy"  mypy . --ignore-missing-imports --no-error-summary && _pass "lint: mypy" || _fail "lint: mypy" ;;
    esac
  done
}

# ── Job: 🐍 Python Tests ─────────────────────────────────────────────────────
job_python_tests() {
  _hdr "🐍  Python Tests"
  if ! _have pytest; then _skip "python-tests: pytest" "not installed — pip install pytest"; return; fi
  if PYTHONPATH="$ROOT" pytest tests/ -q --ignore=tests/e2e -p no:cacheprovider >/tmp/ci-pytest.log 2>&1; then
    _pass "python-tests: pytest"
    tail -n 1 /tmp/ci-pytest.log | sed 's/^/      /'
  else
    _fail "python-tests: pytest"
    tail -n 20 /tmp/ci-pytest.log | sed 's/^/      /'
  fi
}

# ── Job: 🔐 Security Scan ─────────────────────────────────────────────────────
job_security() {
  _hdr "🔐  Security Scan"
  if _have bandit; then
    # Mirror ci.yml: -ll (medium+), exclude tests/venv. HIGH+HIGH-confidence blocks.
    if bandit -r . -x ./tests,./venv,./.venv,./node_modules -ll -f json -o /tmp/ci-bandit.json >/dev/null 2>&1; then :; fi
    local crit
    crit=$(jq '[.results[] | select(.issue_severity=="HIGH" and .issue_confidence=="HIGH")] | length' /tmp/ci-bandit.json 2>/dev/null || echo 0)
    if [ "${crit:-0}" -gt 0 ]; then _fail "security: bandit ($crit HIGH/HIGH)"; else _pass "security: bandit (0 HIGH/HIGH)"; fi
  else
    _skip "security: bandit" "not installed — pip install bandit"
  fi
  if _have pip-audit; then
    # Mirror ci.yml's documented no-fix-available ignores. Keep this list in
    # sync with .github/workflows/ci.yml's IGNORE (single source of truth lives
    # there; this is the offline mirror).
    local ignore="--ignore-vuln CVE-2026-45829 --ignore-vuln PYSEC-2026-139 --ignore-vuln CVE-2025-3000 --ignore-vuln PYSEC-2025-217"
    # No --strict: the dev venv carries local path-installed packages (devskyy,
    # cli-anything-*) not on PyPI; --strict aborts on them before auditing any
    # real dependency. But dropping --strict alone would fail OPEN for any OTHER
    # uncollectable package (git pin, malformed req, yanked release) — the exact
    # fail-open pattern bug-230 forbids. So: run non-strict + --skip-editable,
    # then re-assert fail-closed ourselves — any package pip-audit skipped that
    # ISN'T one of the 3 known local dists fails the job, just as --strict would.
    local audit_ok=1
    # Parse the JSON report, NOT the text log: pip-audit's "Skipping <pkg>" lines
    # come only from the rich progress spinner, which writes nothing when stdout
    # is redirected to a file (non-TTY) unless FORCE_COLOR is set — so grepping
    # the log is fail-OPEN in a normal shell. The JSON marks every uncollectable
    # dep with a non-null skip_reason regardless of TTY.
    # shellcheck disable=SC2086
    pip-audit $ignore --skip-editable -f json -o /tmp/ci-pipaudit.json >/tmp/ci-pipaudit.log 2>&1 || audit_ok=0
    local skips unexpected_skips
    skips=$(jq -r '(.dependencies // .) | .[] | select(.skip_reason != null and .skip_reason != "") | .name' /tmp/ci-pipaudit.json 2>/dev/null | sort -u)
    unexpected_skips=$(printf '%s\n' "$skips" | grep -vxE 'devskyy|cli-anything-blender|cli-anything-gimp' | grep -v '^$' || true)
    if [ -z "$skips" ]; then
      # devskyy is always installed editable → there is ALWAYS ≥1 skip. An empty
      # set means the JSON parse failed or pip-audit changed format: fail closed,
      # never trust an unverifiable gate (bug-230).
      _fail "security: pip-audit (no editable skips parsed — guard cannot self-verify; see /tmp/ci-pipaudit.json)"
    elif [ -n "$unexpected_skips" ]; then
      _fail "security: pip-audit (unaudited package(s): $(printf '%s' "$unexpected_skips" | tr '\n' ' '))"
    elif [ "$audit_ok" = "1" ]; then
      _pass "security: pip-audit"
    else
      _fail "security: pip-audit (dependency vulns)"
    fi
  else
    _skip "security: pip-audit" "not installed — pip install pip-audit"
  fi
  _have semgrep && _skip "security: semgrep" "needs network (config=auto) — run in CI" || _skip "security: semgrep" "not installed"
}

# ── Job: ⚛️ Frontend Tests ───────────────────────────────────────────────────
job_frontend_tests() {
  _hdr "⚛️  Frontend Tests"
  if [ ! -d frontend ]; then _skip "frontend-tests" "no frontend/ dir"; return; fi
  if [ "$FAST" = "1" ] && [ ! -d frontend/node_modules ]; then _skip "frontend-tests" "FAST=1 and node_modules absent"; return; fi
  [ -d frontend/node_modules ] || _run "frontend npm ci" npm --prefix frontend ci
  ( cd frontend && npm run lint )        >/tmp/ci-fe-lint.log 2>&1 && _pass "frontend: eslint"     || { _fail "frontend: eslint";     tail -n 15 /tmp/ci-fe-lint.log | sed 's/^/      /'; }
  ( cd frontend && npm run type-check )  >/tmp/ci-fe-tc.log   2>&1 && _pass "frontend: type-check" || { _fail "frontend: type-check"; tail -n 15 /tmp/ci-fe-tc.log   | sed 's/^/      /'; }
  ( cd frontend && NEXT_TELEMETRY_DISABLED=1 npm run build ) >/tmp/ci-fe-build.log 2>&1 && _pass "frontend: build" || { _fail "frontend: build"; tail -n 20 /tmp/ci-fe-build.log | sed 's/^/      /'; }
}

# ── Job: 🎮 Three.js Tests ───────────────────────────────────────────────────
job_threejs_tests() {
  _hdr "🎮  Three.js Tests"
  if ! jq -e '.scripts["test:collections"]' package.json >/dev/null 2>&1; then
    _skip "threejs-tests" "no test:collections script in root package.json"; return
  fi
  if [ "$FAST" = "1" ] && [ ! -d node_modules ]; then _skip "threejs-tests" "FAST=1 and node_modules absent"; return; fi
  # Root has no committed package-lock.json (gitignored), so `npm ci` cannot
  # work in a clean checkout — ci.yml's threejs job uses `npm install` for the
  # same reason. Mirror it, and fail the job if the install itself fails.
  if [ ! -d node_modules ]; then
    if ! _run "root npm install" npm install --no-audit --no-fund; then
      _fail "threejs-tests: npm install"; return
    fi
  fi
  if npm run test:collections >/tmp/ci-threejs.log 2>&1; then _pass "threejs-tests"; else _fail "threejs-tests"; tail -n 20 /tmp/ci-threejs.log | sed 's/^/      /'; fi
}

# ── dispatch ─────────────────────────────────────────────────────────────────
JOBS=("$@")
[ ${#JOBS[@]} -eq 0 ] && JOBS=(wordpress-theme lint python-tests security frontend-tests threejs-tests)

printf '\033[1mci-local — offline mirror of GitHub Actions ci.yml (gating jobs)\033[0m\n'
printf 'repo: %s   FAST=%s\n' "$ROOT" "$FAST"

for job in "${JOBS[@]}"; do
  case "$job" in
    wordpress-theme) job_wordpress_theme || true ;;
    lint)            job_lint ;;
    python-tests)    job_python_tests ;;
    security)        job_security ;;
    frontend-tests)  job_frontend_tests ;;
    threejs-tests)   job_threejs_tests ;;
    all)             ;; # handled by default expansion
    *) printf 'unknown job: %s\n' "$job"; OVERALL=1 ;;
  esac
done

# ── summary ──────────────────────────────────────────────────────────────────
_hdr "📊  Summary"
for row in "${SUMMARY[@]}"; do
  st="${row%%|*}"; msg="${row#*|}"
  case "$st" in
    PASS) printf '  \033[32m%-5s\033[0m %s\n' "$st" "$msg" ;;
    FAIL) printf '  \033[31m%-5s\033[0m %s\n' "$st" "$msg" ;;
    SKIP) printf '  \033[33m%-5s\033[0m %s\n' "$st" "$msg" ;;
  esac
done
printf '\n'
if [ "$OVERALL" -eq 0 ]; then
  printf '\033[32m✓ ci-local: all non-skipped checks passed\033[0m\n'
else
  printf '\033[31m✗ ci-local: failures present (see above)\033[0m\n'
fi
exit "$OVERALL"
