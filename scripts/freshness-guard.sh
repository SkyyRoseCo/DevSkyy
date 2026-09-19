#!/usr/bin/env bash
#
# scripts/freshness-guard.sh — keep derived files in sync with their sources.
#
# Stops the recurring "stale file" failure mode: someone edits a MASTER
# (product registry, catalog CSV, theme CSS/JS, version) and forgets
# to regenerate the file that derives from it, so the site / build / docs ship
# stale. This guard makes that un-committable.
#
# Checks (each independent; a check only runs when its trigger file is staged,
# unless --all/--fix forces all):
#   1. SOT drift     — data/collections/<slug>/{sot.json,index.html} + design-tokens.css
#                      must match the masters (logo-registry.json incl. its collections,
#                      catalog.csv, visual-manifest.json).
#   2. Lookbook SOT drift — lookbook-manifest.json drives scripts/build-lookbook-sot.py,
#                      then from-sot to docs/campaigns/sot-lookbook.html.
#   3. .min staleness — every assets/css|js source has an up-to-date *.min.*
#                      (production serves .min; a stale .min = an inert fix).
#                      Both themes: skyyrose-flagship builds via wordpress-theme/
#                      package.json; skyyrose-flagship-2 via its own
#                      scripts/build-assets.mjs (--check mode is read-only).
#   4. Version sync  — style.css "Version", functions.php version constant,
#                      readme.txt "Stable tag" must all agree — per theme:
#                      skyyrose-flagship → SKYYROSE_VERSION,
#                      skyyrose-flagship-2 → SKYYROSE2_VERSION.
#   5. Retired refs  — no code points at retired masters (product-masters/
#                      catalog.yaml, manifest.json, data/product-catalog.csv,
#                      products.json, the deleted flat data/collections/*.json).
#
# Modes:
#   (default)  check staged files only — fast; used by the pre-commit hook.
#   --all      check the whole repo regardless of staging — used in CI / on demand.
#   --fix      regenerate the SOT, rebuild .min, and re-stage them; then re-check.
#
# Exit 0 = everything fresh. Exit 1 = stale (with the exact fix command).
# Missing tooling (no venv / no npm) downgrades a check to a skip, never a fail.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THEME="$ROOT/wordpress-theme/skyyrose-flagship"
THEME2="$ROOT/wordpress-theme/skyyrose-flagship-2"
WP="$ROOT/wordpress-theme"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || true)"

MODE="${1:-check}"
FAIL=0

c_ok()   { printf '\033[32m  ✓\033[0m %s\n' "$1"; }
c_bad()  { printf '\033[31m  ✗\033[0m %s\n' "$1"; FAIL=1; }
c_skip() { printf '\033[33m  ·\033[0m %s\n' "$1"; }
hdr()    { printf '\n\033[1m%s\033[0m\n' "$1"; }

# Staged file list (ACMR). --all/--fix consider the whole tree.
if [ "$MODE" = "--all" ] || [ "$MODE" = "--fix" ]; then
  STAGED="$(git -C "$ROOT" ls-files)"
else
  STAGED="$(git -C "$ROOT" diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)"
fi
forced() { [ "$MODE" = "--all" ] || [ "$MODE" = "--fix" ]; }
staged_match() { printf '%s\n' "$STAGED" | grep -qE "$1"; }
extract_ver() { grep -iE "$1" "$2" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1; }
# skyyrose-flagship-2 builds with its own scripts/build-assets.mjs; node resolves
# clean-css + terser from the theme's node_modules or the shared wordpress-theme/.
# The versions must equal the theme's pins EXACTLY (npm-shrinkwrap.json /
# package.json devDependencies): a different minifier version emits different
# bytes, so an unpinned toolchain would report false drift or false freshness.
# This probe is copied verbatim from scripts/ci-local.sh (Step CI-05b) — keep
# the two identical.
theme2_build_ready() {
  [ -f "$THEME2/scripts/build-assets.mjs" ] && command -v node >/dev/null 2>&1 \
    && ( cd "$THEME2" && node -e '
    const pkg = require("./package.json").devDependencies;
    for (const name of ["clean-css", "terser"]) {
      const v = require(name + "/package.json").version;
      if (v !== pkg[name]) { console.error(`${name} ${v} != pinned ${pkg[name]}`); process.exit(1); }
    }' ) >/dev/null 2>&1
}
# Per-run scratch dir for the flagship-2 build logs (the older /tmp/fg_*.log
# paths above/below predate this and are left as they are).
FG_TMP="$(mktemp -d)"

hdr "freshness-guard ($MODE)"

# ── --fix: regenerate before checking ───────────────────────────────────────
if [ "$MODE" = "--fix" ]; then
  if [ -x "$PY" ]; then
    ( cd "$THEME" && "$PY" data/gen-design-tokens.py && "$PY" data/build-collection-sot.py \
        && "$PY" data/gen-collection-hub.py ) >/tmp/fg_fix_sot.log 2>&1 \
      && c_ok "regenerated collection SOTs (design-tokens + collection sot.json + hubs)" \
      || { c_bad "SOT regeneration failed (see /tmp/fg_fix_sot.log)"; tail -8 /tmp/fg_fix_sot.log | sed 's/^/    /'; }
    ( cd "$ROOT" && "$PY" scripts/build-lookbook-sot.py ) >/tmp/fg_fix_lookbook_sot.log 2>&1 \
      && c_ok "regenerated lookbook-sot.json" \
      || { c_bad "lookbook SOT regeneration failed (see /tmp/fg_fix_lookbook_sot.log)"; tail -8 /tmp/fg_fix_lookbook_sot.log | sed 's/^/    /'; }
    ( cd "$ROOT" && "$PY" scripts/build-lookbook-from-sot.py ) >/tmp/fg_fix_lookbook_html.log 2>&1 \
      && c_ok "regenerated docs/campaigns/sot-lookbook.html" \
      || { c_bad "lookbook HTML regeneration failed (see /tmp/fg_fix_lookbook_html.log)"; tail -8 /tmp/fg_fix_lookbook_html.log | sed 's/^/    /'; }
  fi
  if command -v npm >/dev/null 2>&1 && [ -d "$WP/node_modules/clean-css" ]; then
    ( cd "$WP" && npm run build ) >/tmp/fg_fix_min.log 2>&1 \
      && { c_ok "rebuilt .min (css + js)"; MIN_REBUILT=1; } \
      || c_bad "min rebuild failed (see /tmp/fg_fix_min.log)"
  fi
  if theme2_build_ready; then
    ( cd "$THEME2" && node scripts/build-assets.mjs ) >"$FG_TMP/fix_min2.log" 2>&1 \
      && c_ok "rebuilt skyyrose-flagship-2 .min (css + js)" \
      || c_bad "skyyrose-flagship-2 min rebuild failed (see $FG_TMP/fix_min2.log)"
  fi
  git -C "$ROOT" add -- "$THEME/assets/css/design-tokens.css" \
      "$THEME/data/collections" "$THEME/assets/css" "$THEME/assets/js" \
      "$THEME2/assets/css" "$THEME2/assets/js" \
      "$ROOT/scripts/lookbook-manifest.json" "$ROOT/wordpress-theme/skyyrose-flagship/data/lookbook-sot.json" \
      "$ROOT/docs/campaigns/sot-lookbook.html" 2>/dev/null || true
  c_ok "re-staged regenerated derived files — review then commit"
fi

# ── CHECK 1: SOT drift ──────────────────────────────────────────────────────
SOT_TRIGGER='wordpress-theme/skyyrose-flagship/data/(skyyrose-catalog\.csv|visual-manifest\.json|logo-registry\.json|collections/)|wordpress-theme/skyyrose-flagship/assets/css/design-tokens\.css'
if forced || staged_match "$SOT_TRIGGER"; then
  hdr "1. Collection SOT ↔ masters"
  if [ -x "$PY" ] && [ -f "$THEME/data/verify-collection-sot.py" ]; then
    if ( cd "$THEME" && "$PY" data/verify-collection-sot.py ) >/tmp/fg_sot.log 2>&1; then
      c_ok "SOT in sync ($(grep -cE 'SKUs, 0 broken' /tmp/fg_sot.log) collections verified)"
    else
      c_bad "SOT DRIFT — run: bash scripts/freshness-guard.sh --fix   (then git add + recommit)"
      grep -E '✗|missing|drift|not in' /tmp/fg_sot.log | head -8 | sed 's/^/    /'
    fi
  else
    c_skip "SOT check skipped (no .venv python / verifier)"
  fi
fi

# ── CHECK 2: Lookbook SOT + HTML drift ──────────────────────────────────────
LOOKBOOK_TRIGGER='scripts/lookbook-manifest\.json|scripts/build-lookbook-sot\.py|scripts/build-lookbook-from-sot\.py|wordpress-theme/skyyrose-flagship/data/lookbook-sot\.json|docs/campaigns/sot-lookbook\.html'
if forced || staged_match "$LOOKBOOK_TRIGGER"; then
  hdr "2. Lookbook SOT ↔ derived HTML"
  if [ -x "$PY" ]; then
    if "$PY" scripts/validate_catalog_consistency.py --checks lookbook_sot_current,lookbook_html_current >/tmp/fg_lookbook_guard.log 2>&1; then
      c_ok "lookbook-sot.json and sot-lookbook.html are in sync"
    else
      c_bad "lookbook drift — run: bash scripts/freshness-guard.sh --fix   (then git add + recommit)"
      sed 's/^/    /' /tmp/fg_lookbook_guard.log
    fi
  else
    c_skip "Lookbook SOT checks skipped (python unavailable)"
  fi
fi

# ── CHECK 3: .min staleness ─────────────────────────────────────────────────
MIN_TRIGGER='wordpress-theme/skyyrose-flagship(-2)?/assets/(css|js)/.*\.(css|js)$'
if forced || staged_match "$MIN_TRIGGER"; then
  hdr "3. Minified assets ↔ source"
  if forced; then
    # --all/--fix audit: rebuild, surface any .min that differs from the build
    # (also catches toolchain drift), then restore the tree (read-only audit).
    if command -v npm >/dev/null 2>&1 && [ -d "$WP/node_modules/clean-css" ]; then
      # --fix already rebuilt above; avoid a second redundant minification pass.
      [ "${MIN_REBUILT:-0}" = "1" ] || ( cd "$WP" && npm run build ) >/tmp/fg_min.log 2>&1 || true
      DRIFTED="$(git -C "$ROOT" diff --name-only -- '*.min.css' '*.min.js' 2>/dev/null)"
      [ "$MODE" = "--fix" ] || git -C "$ROOT" checkout -- '*.min.css' '*.min.js' 2>/dev/null || true
      if [ -n "$DRIFTED" ]; then
        c_bad "$(printf '%s\n' "$DRIFTED" | grep -c . ) .min file(s) differ from the build — run: bash scripts/freshness-guard.sh --fix && git add"
        printf '%s\n' "$DRIFTED" | head -6 | sed 's/^/    /'
      else
        c_ok "skyyrose-flagship .min build up to date"
      fi
    else
      c_skip "skyyrose-flagship .min audit skipped (npm/clean-css unavailable)"
    fi
    # skyyrose-flagship-2: its builder has a read-only --check mode (no tree mutation).
    if theme2_build_ready; then
      if ( cd "$THEME2" && node scripts/build-assets.mjs --check ) >"$FG_TMP/min2.log" 2>&1; then
        c_ok "skyyrose-flagship-2 .min build up to date"
      else
        c_bad "skyyrose-flagship-2 .min stale — run: (cd wordpress-theme/skyyrose-flagship-2 && npm run build:assets) && git add"
        grep -E '^\s+- ' "$FG_TMP/min2.log" | head -6 | sed 's/^/    /'
      fi
    else
      c_skip "skyyrose-flagship-2 .min audit skipped (node unavailable, or clean-css/terser not at the versions pinned in its package.json — cd wordpress-theme/skyyrose-flagship-2 && npm ci)"
    fi
  else
    # pre-commit path: precise, no rebuild, no tree mutation — a staged source
    # whose .min already exists MUST restage that .min in the same commit.
    STALE_MIN=0
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      min="${f%.*}.min.${f##*.}"
      [ -f "$ROOT/$min" ] || continue          # source isn't a built asset → skip
      if ! printf '%s\n' "$STAGED" | grep -qxF "$min"; then
        # Comment/whitespace-only source edits rebuild to a byte-identical
        # .min — there is nothing to stage and the presence check can never
        # be satisfied. Detect that case precisely: strip comments+whitespace
        # from the staged source and HEAD's copy; identical => cosmetic-only
        # edit, .min is fresh by definition. (Checking the .min against HEAD
        # alone would also pass for a stale un-rebuilt .min — insufficient.)
        if command -v perl >/dev/null 2>&1; then
          norm() { perl -0777 -pe 's{/\*.*?\*/}{}gs; s{^\s*//[^\n]*$}{}gm; s/\s+//g'; }
          staged_sig=$(git -C "$ROOT" show ":$f" 2>/dev/null | norm | git hash-object --stdin)
          head_sig=$(git -C "$ROOT" show "HEAD:$f" 2>/dev/null | norm | git hash-object --stdin)
          if [ -n "$staged_sig" ] && [ "$staged_sig" = "$head_sig" ]; then
            continue
          fi
        fi
        case "$f" in
          wordpress-theme/skyyrose-flagship-2/*) build_hint="(cd wordpress-theme/skyyrose-flagship-2 && npm run build:assets)" ;;
          *) build_hint="(cd wordpress-theme && npm run build)" ;;
        esac
        c_bad "edited source not rebuilt: $f  →  $build_hint && git add $min"
        STALE_MIN=1
      fi
    done <<EOF
$(printf '%s\n' "$STAGED" | grep -E "$MIN_TRIGGER" | grep -vE '\.min\.')
EOF
    [ "$STALE_MIN" -eq 0 ] && c_ok "edited assets have their rebuilt .min staged"
  fi
fi

# ── CHECK 4: theme version sync ─────────────────────────────────────────────
# check_version_triple <theme dir> <functions.php version constant> <label>
check_version_triple() {
  local dir="$1" const="$2" label="$3" v_style v_fn v_rm
  v_style="$(extract_ver '^Version:' "$dir/style.css")"
  v_fn="$(grep -E "$const" "$dir/functions.php" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
  v_rm="$(extract_ver 'stable tag' "$dir/readme.txt")"
  if [ -n "$v_style" ] && [ "$v_style" = "$v_fn" ] && [ "$v_style" = "$v_rm" ]; then
    c_ok "$label version synced ($v_style)"
  else
    c_bad "$label VERSION DRIFT — style.css=$v_style  functions.php($const)=$v_fn  readme.txt=$v_rm  (sync all three)"
  fi
}
VER_TRIGGER='wordpress-theme/skyyrose-flagship/(style\.css|readme\.txt|functions\.php)'
VER2_TRIGGER='wordpress-theme/skyyrose-flagship-2/(style\.css|readme\.txt|functions\.php)'
if forced || staged_match "$VER_TRIGGER" || staged_match "$VER2_TRIGGER"; then
  hdr "4. Theme version sync"
  if forced || staged_match "$VER_TRIGGER"; then
    check_version_triple "$THEME" 'SKYYROSE_VERSION' 'skyyrose-flagship'
  fi
  if forced || staged_match "$VER2_TRIGGER"; then
    check_version_triple "$THEME2" 'SKYYROSE2_VERSION' 'skyyrose-flagship-2'
  fi
fi

# ── CHECK 5: retired-master references ──────────────────────────────────────
RETIRED='product-masters/(catalog\.yaml|manifest\.json)|data/product-catalog\.csv|/products\.json|data/collections/(black-rose|love-hurts|signature|kids-capsule)\.json|data/collections/[a-z-]+/identity\.json|render-(corrections|keepers)\.json'
hdr "5. Retired-master references"
if forced; then
  HITS="$(git -C "$ROOT" grep -nIE "$RETIRED" -- '*.py' '*.php' '*.js' ':!*test*' ':!*/tests/*' ':!*/docs/*' ':!*.min.*' 2>/dev/null || true)"
else
  CODE="$(printf '%s\n' "$STAGED" | grep -E '\.(py|php|js)$' | grep -vE 'test|/tests/|/docs/|\.min\.' || true)"
  HITS=""
  # NUL-delimit the path list so filenames with spaces, globs, or a leading
  # dash cannot word-split or inject grep flags ('--' terminates options).
  [ -n "$CODE" ] && HITS="$(cd "$ROOT" && printf '%s\n' "$CODE" | tr '\n' '\0' \
    | xargs -0 grep -nIE "$RETIRED" -- 2>/dev/null || true)"
fi
if [ -n "$HITS" ]; then
  c_bad "retired-master reference(s) — repoint to the catalog CSV / per-collection SOT:"
  printf '%s\n' "$HITS" | head -12 | sed 's/^/    /'
else
  c_ok "no retired-master references"
fi

# ── Summary ─────────────────────────────────────────────────────────────────
echo
if [ "$FAIL" -eq 0 ]; then
  printf '\033[32mfreshness-guard: all derived files fresh\033[0m\n'
else
  printf '\033[31mfreshness-guard: STALE — fix above, or run: bash scripts/freshness-guard.sh --fix\033[0m\n'
fi
exit "$FAIL"
