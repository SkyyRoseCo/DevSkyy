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
#   4. Version sync  — style.css "Version", functions.php SKYYROSE_VERSION,
#                      readme.txt "Stable tag" must all agree.
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
  git -C "$ROOT" add -- "$THEME/assets/css/design-tokens.css" \
      "$THEME/data/collections" "$THEME/assets/css" "$THEME/assets/js" \
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
MIN_TRIGGER='wordpress-theme/skyyrose-flagship/assets/(css|js)/.*\.(css|js)$'
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
        c_ok ".min build up to date"
      fi
    else
      c_skip ".min audit skipped (npm/clean-css unavailable)"
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
        c_bad "edited source not rebuilt: $f  →  (cd wordpress-theme && npm run build) && git add $min"
        STALE_MIN=1
      fi
    done <<EOF
$(printf '%s\n' "$STAGED" | grep -E 'wordpress-theme/skyyrose-flagship/assets/(css|js)/.*\.(css|js)$' | grep -vE '\.min\.')
EOF
    [ "$STALE_MIN" -eq 0 ] && c_ok "edited assets have their rebuilt .min staged"
  fi
fi

# ── CHECK 4: theme version sync ─────────────────────────────────────────────
VER_TRIGGER='wordpress-theme/skyyrose-flagship/(style\.css|readme\.txt|functions\.php)'
if forced || staged_match "$VER_TRIGGER"; then
  hdr "4. Theme version sync"
  v_style="$(extract_ver '^Version:' "$THEME/style.css")"
  v_fn="$(grep -E "SKYYROSE_VERSION" "$THEME/functions.php" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
  v_rm="$(extract_ver 'stable tag' "$THEME/readme.txt")"
  if [ -n "$v_style" ] && [ "$v_style" = "$v_fn" ] && [ "$v_style" = "$v_rm" ]; then
    c_ok "version synced ($v_style)"
  else
    c_bad "VERSION DRIFT — style.css=$v_style  functions.php=$v_fn  readme.txt=$v_rm  (sync all three)"
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
