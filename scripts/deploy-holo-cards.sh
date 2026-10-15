#!/usr/bin/env bash
# scripts/deploy-holo-cards.sh -- Deploy Holo product card rollout to production
#
# Orchestrates the full pipeline: minify assets, lint PHP, deploy theme,
# verify holo card renders on all collection pages + WC shop.
#
# Usage:
#   bash scripts/deploy-holo-cards.sh              # Full deploy + verify
#   bash scripts/deploy-holo-cards.sh --dry-run    # Preview only (no server contact)
#   bash scripts/deploy-holo-cards.sh --minify     # Re-minify assets only
#   bash scripts/deploy-holo-cards.sh --verify     # Post-deploy verify only
#   bash scripts/deploy-holo-cards.sh --help       # Show help
#
# Requirements:
#   - npx (terser, csso-cli) for minification
#   - .env.wordpress for deploy credentials (pinned by deploy-production.sh,
#     the wrapper that execs the deploy-theme.sh engine; the engine refuses a
#     direct call without DEPLOY_TARGET)
#   - curl for post-deploy verification
#
# This is a PRODUCTION script (skyyrose.co).
#
# What changed in this rollout:
#   - assets/css/product-card-holo.min.css       (NEW — minified CSS)
#   - assets/js/product-card-holo.min.js         (NEW — minified JS)
#   - inc/enqueue.php                            (auto-selects .min, added shop-archive)
#   - template-parts/collection-page-v4.php      (catalog grid → holo cards)
#   - woocommerce/content-product.php            (WC loop → holo card)

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
THEME_DIR="$PROJECT_ROOT/wordpress-theme/skyyrose-flagship"
SITE_URL="${WORDPRESS_URL:-https://skyyrose.co}"

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[  OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[FAIL]${NC} $1" >&2; }

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
DRY_RUN=false
MINIFY_ONLY=false
VERIFY_ONLY=false

usage() {
    cat <<EOF
${BOLD}Holo Card Rollout Deploy${NC}

Usage:
  deploy-holo-cards.sh [OPTIONS]

Options:
  --dry-run    Preview what would happen (no server contact)
  --minify     Re-minify CSS/JS only (no deploy)
  --verify     Run post-deploy verification only
  --help       Show this help message

Environment:
  WORDPRESS_URL   Target site (default: https://skyyrose.co)

Pipeline:
  1. Minify   product-card-holo.css → .min.css  (csso)
  2. Minify   product-card-holo.js  → .min.js   (terser)
  3. Lint     PHP syntax on all changed files
  4. Deploy   via deploy-production.sh (wrapper around the deploy-theme.sh engine)
  5. Verify   holo card class present on all collection pages + shop, then
              verify-deploy.sh --env-file .env.wordpress
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)  DRY_RUN=true; shift ;;
            --minify)   MINIFY_ONLY=true; shift ;;
            --verify)   VERIFY_ONLY=true; shift ;;
            --help|-h)  usage; exit 0 ;;
            *)          log_error "Unknown option: $1"; usage; exit 1 ;;
        esac
    done
}

# ---------------------------------------------------------------------------
# 1. Minify holo card assets
# ---------------------------------------------------------------------------
minify_assets() {
    log_info "=== Minifying Holo Card Assets ==="

    local css_src="$THEME_DIR/assets/css/product-card-holo.css"
    local css_min="$THEME_DIR/assets/css/product-card-holo.min.css"
    local js_src="$THEME_DIR/assets/js/product-card-holo.js"
    local js_min="$THEME_DIR/assets/js/product-card-holo.min.js"

    # Check source files exist
    if [[ ! -f "$css_src" ]]; then
        log_error "CSS source not found: $css_src"
        exit 1
    fi
    if [[ ! -f "$js_src" ]]; then
        log_error "JS source not found: $js_src"
        exit 1
    fi

    # Check tools
    if ! npx csso-cli --version &>/dev/null; then
        log_error "csso-cli not available via npx"
        exit 1
    fi
    if ! npx terser --version &>/dev/null; then
        log_error "terser not available via npx"
        exit 1
    fi

    # Minify CSS
    local css_before css_after
    css_before=$(wc -c < "$css_src")
    npx csso-cli "$css_src" -o "$css_min"
    css_after=$(wc -c < "$css_min")
    local css_pct=$(( (css_before - css_after) * 100 / css_before ))
    log_success "CSS: ${css_before}B → ${css_after}B (${css_pct}% reduction)"

    # Minify JS
    local js_before js_after
    js_before=$(wc -c < "$js_src")
    npx terser "$js_src" -o "$js_min" --compress --mangle
    js_after=$(wc -c < "$js_min")
    local js_pct=$(( (js_before - js_after) * 100 / js_before ))
    log_success "JS:  ${js_before}B → ${js_after}B (${js_pct}% reduction)"
}

# ---------------------------------------------------------------------------
# 2. PHP lint on changed files
# ---------------------------------------------------------------------------
lint_php() {
    log_info "=== PHP Syntax Check ==="

    local changed_files=(
        "$THEME_DIR/inc/enqueue.php"
        "$THEME_DIR/template-parts/collection-page-v4.php"
        "$THEME_DIR/template-parts/product-card-holo.php"
        "$THEME_DIR/woocommerce/content-product.php"
    )

    local errors=0
    for f in "${changed_files[@]}"; do
        if [[ ! -f "$f" ]]; then
            log_error "File not found: $f"
            errors=$((errors + 1))
            continue
        fi
        if php -l "$f" &>/dev/null; then
            log_success "$(basename "$f")"
        else
            log_error "Syntax error: $(basename "$f")"
            php -l "$f" 2>&1 | tail -1
            errors=$((errors + 1))
        fi
    done

    if [[ "$errors" -gt 0 ]]; then
        log_error "$errors file(s) failed PHP lint — fix before deploying"
        exit 1
    fi

    log_success "All PHP files pass syntax check"
}

# ---------------------------------------------------------------------------
# 3. Deploy via existing pipeline
# ---------------------------------------------------------------------------
deploy() {
    log_info "=== Deploying Theme ==="

    # The production wrapper pins DEPLOY_TARGET=production + .env.wordpress and
    # execs the engine (deploy-theme.sh), which refuses a direct call.
    local deploy_script="$SCRIPT_DIR/deploy-production.sh"
    if [[ ! -f "$deploy_script" ]]; then
        log_error "deploy-production.sh not found at $deploy_script"
        exit 1
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Calling deploy-production.sh --dry-run"
        bash "$deploy_script" --dry-run
    else
        bash "$deploy_script"
    fi
}

# ---------------------------------------------------------------------------
# 4. Post-deploy verification — holo card on all collection pages + shop
# ---------------------------------------------------------------------------
verify_holo() {
    log_info "=== Holo Card Verification ==="

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would verify holo card rendering on:"
        log_info "  ${SITE_URL}/collection-black-rose/"
        log_info "  ${SITE_URL}/collection-love-hurts/"
        log_info "  ${SITE_URL}/collection-signature/"
        log_info "  ${SITE_URL}/collection-kids-capsule/"
        log_info "  ${SITE_URL}/shop/"
        return 0
    fi

    local timestamp
    timestamp="$(date +%s)"

    # Pages to verify: name|path|content_marker
    local pages=(
        "Black Rose|/collection-black-rose/|holo__body"
        "Love Hurts|/collection-love-hurts/|holo__body"
        "Signature|/collection-signature/|holo__body"
        "Kids Capsule|/collection-kids-capsule/|holo__body"
        "WC Shop|/shop/|holo__body"
    )

    local checks=0
    local failures=0

    for entry in "${pages[@]}"; do
        IFS='|' read -r name path marker <<< "$entry"
        checks=$((checks + 1))

        local url="${SITE_URL}${path}?_holo_verify=${timestamp}"
        local tmpfile http_code
        tmpfile=$(mktemp)

        http_code=$(curl -sSL -o "$tmpfile" -w "%{http_code}" \
            --connect-timeout 10 --max-time 30 \
            --retry 2 --retry-delay 3 \
            "$url" 2>/dev/null || echo "000")

        if [[ "$http_code" -ne 200 ]]; then
            log_error "$name: HTTP $http_code (expected 200)"
            rm -f "$tmpfile"
            failures=$((failures + 1))
            continue
        fi

        if ! grep -qi "$marker" "$tmpfile"; then
            log_error "$name: Holo card marker '$marker' not found in response"
            rm -f "$tmpfile"
            failures=$((failures + 1))
            continue
        fi

        rm -f "$tmpfile"
        log_success "$name: holo card rendering confirmed"
    done

    # Also verify .min.css and .min.js are being served (check for enqueued handle)
    log_info "Checking minified asset enqueue..."
    local homepage_tmp
    homepage_tmp=$(mktemp)
    curl -sSL -o "$homepage_tmp" --connect-timeout 10 --max-time 30 \
        "${SITE_URL}/collection-black-rose/?_asset_check=${timestamp}" 2>/dev/null || true

    if grep -q "product-card-holo" "$homepage_tmp"; then
        if grep -q "product-card-holo.min" "$homepage_tmp"; then
            log_success "Minified assets are being served"
        else
            log_warn "Assets loaded but .min files not detected (SCRIPT_DEBUG may be on)"
        fi
    else
        log_warn "Could not verify asset enqueue in page source"
    fi
    rm -f "$homepage_tmp"

    # Summary
    echo ""
    log_info "Holo Verification: $checks checks, $((checks - failures)) passed, $failures failed"
    if [[ "$failures" -gt 0 ]]; then
        log_error "$failures page(s) missing holo card rendering"
        return 1
    fi
    log_success "All pages confirmed rendering holo cards"
}

# ---------------------------------------------------------------------------
# 5. Run existing verify-deploy.sh for full-site health
# ---------------------------------------------------------------------------
verify_full_site() {
    local verify_script="$SCRIPT_DIR/verify-deploy.sh"
    if [[ -f "$verify_script" && "$DRY_RUN" == "false" ]]; then
        log_info "=== Full-Site Verification ==="
        bash "$verify_script" --env-file "$PROJECT_ROOT/.env.wordpress" \
            || log_warn "Some full-site checks failed (see above)"
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    parse_args "$@"

    echo ""
    echo -e "${BOLD}  Holo Product Card — Rollout Deploy${NC}"
    echo -e "  Target: ${SITE_URL}"
    echo -e "  Theme:  ${THEME_DIR}"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "  Mode:   ${YELLOW}DRY RUN${NC}"
    fi
    echo ""

    if [[ "$VERIFY_ONLY" == "true" ]]; then
        verify_holo
        verify_full_site
        return 0
    fi

    # Step 1: Minify
    minify_assets

    if [[ "$MINIFY_ONLY" == "true" ]]; then
        log_success "Minification complete. Exiting (--minify mode)."
        return 0
    fi

    # Step 2: Lint
    lint_php

    # Step 3: Deploy
    deploy

    # Step 4: Verify holo cards
    verify_holo

    # Step 5: Full-site verify
    verify_full_site

    echo ""
    log_success "=== Holo Card Rollout Complete ==="
}

main "$@"
