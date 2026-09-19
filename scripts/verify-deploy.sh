#!/usr/bin/env bash
# scripts/verify-deploy.sh -- Post-deploy deep content verification for a SkyyRose WP site
#
# Checks the live WordPress site for HTTP 200 AND page content markers.
# Catches "white screen of death", stuck maintenance mode, and partial deploy
# failures that return HTTP 200 but serve broken content.
#
# The target and the theme come from the environment -- there is no literal
# production default. The route table is selected by the LIVE theme's
# Text Domain (read from /wp-content/themes/<slug>/style.css), so the same
# script verifies the V1 theme ("skyyrose") and Flagship 2
# ("skyyrose-flagship-2") without guessing which one is live.
#
# Usage:
#   bash scripts/verify-deploy.sh --env-file .env.wordpress.staging   # URL + slug from the env file
#   WORDPRESS_URL=https://... WP_THEME_PATH=/.../skyyrose-flagship-2 bash scripts/verify-deploy.sh
#   bash scripts/verify-deploy.sh --url URL --theme SLUG
#   bash scripts/verify-deploy.sh --list       # Print both route tables (no HTTP)
#   bash scripts/verify-deploy.sh --help       # Show this help message
#
# Exit codes:
#   0 - All pages verified (HTTP 200 + content markers found; redirects land)
#   1 - One or more checks failed, or the target/theme could not be established
#
# Environment:
#   PUBLIC_URL      Target site URL (else WORDPRESS_URL -- same precedence as the
#                   deploy wrappers/engine); required unless --url/--env-file.
#                   Any ?query (e.g. a bypass token) is stripped and never printed.
#   WP_THEME_PATH   Live theme path; its basename is the slug (else THEME_SLUG / --theme)

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Site URL with any ?query/#fragment and trailing slash removed. A query on
# the site URL (a coming-soon bypass token, say) must neither reach the log
# nor be appended to every path, so it is dropped at every assignment site.
site_url_base() {
    local url="${1%%\?*}"
    url="${url%%#*}"
    printf '%s' "${url%/}"
}

SITE_URL="$(site_url_base "${PUBLIC_URL:-${WORDPRESS_URL:-}}")"
THEME_SLUG="${THEME_SLUG:-}"
if [[ -z "$THEME_SLUG" && -n "${WP_THEME_PATH:-}" ]]; then
    THEME_SLUG="$(basename "$WP_THEME_PATH")"
fi
TIMESTAMP="$(date +%s)"
FAILURES=0
CHECKS=0
LIVE_TEXT_DOMAIN=""

# ---------------------------------------------------------------------------
# Color logging (matches deploy-theme.sh pattern)
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No color

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
# shellcheck disable=SC2329,SC2317  # Part of standard logging interface (used by deploy-pipeline.sh)
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[FAIL]${NC} $1"; }

# ---------------------------------------------------------------------------
# Usage / help
# ---------------------------------------------------------------------------
usage() {
    echo "Usage: verify-deploy.sh [OPTIONS]"
    echo ""
    echo "Post-deploy deep content verification for a SkyyRose WordPress site."
    echo "Checks HTTP status AND response body content for each page, and that the"
    echo "legacy routes redirect where the live theme says they should."
    echo ""
    echo "Options:"
    echo "  --help             Show this help message"
    echo "  --list             Print both route tables without making HTTP requests"
    echo "  --url URL          Target site URL"
    echo "  --theme SLUG       Live theme folder name (e.g. skyyrose-flagship-2)"
    echo "  --env-file PATH    Read PUBLIC_URL/WORDPRESS_URL and WP_THEME_PATH from an"
    echo "                     env file (grep, not source -- no secrets are loaded)"
    echo ""
    echo "Environment:"
    echo "  PUBLIC_URL      Target site URL (else WORDPRESS_URL) -- no default; ?query stripped"
    echo "  WP_THEME_PATH   Live theme path; basename = slug (else THEME_SLUG)"
    echo ""
    echo "Route table is chosen by the live Text Domain:"
    echo "  skyyrose             V1: /collection-<slug>/, /experience-<slug>/, /experience/"
    echo "  skyyrose-flagship-2  V2: /collections/<slug>/, /worlds/<slug>/ (+ legacy 302s)"
}

# ---------------------------------------------------------------------------
# Health check definitions: "name|path|content_marker"
# ---------------------------------------------------------------------------
# V1 -- text domain "skyyrose" (wordpress-theme/skyyrose-flagship).
HEALTH_CHECKS_V1=(
    "Homepage|/|SKYY ROSE"
    "REST API|/index.php?rest_route=/|namespaces"
    "Collection: Black Rose|/collection-black-rose/|Black Rose"
    "Collection: Love Hurts|/collection-love-hurts/|Love Hurts"
    "Collection: Signature|/collection-signature/|Signature"
    "About|/about/|SkyyRose"
    "Immersive: Black Rose|/experience-black-rose/|immersive-black-rose"
    "Immersive: Love Hurts|/experience-love-hurts/|immersive-love-hurts"
    "Immersive: Signature|/experience-signature/|immersive-signature"
    "Pre-Order Gateway|/pre-order/|pre-order"
    "Experiences Hub|/experience/|Immersive Experiences"
)

# V2 -- text domain "skyyrose-flagship-2" (wordpress-theme/skyyrose-flagship-2).
# Routes and markers read from staging-7e48-skyyrose.wpcomstaging.com on
# 2026-09-19 [live]: every path below returned 200 with the marker present;
# the world pages carry their template name in the <body> class.
HEALTH_CHECKS_V2=(
    "Homepage|/|SkyyRose"
    "REST API|/index.php?rest_route=/|namespaces"
    "Collection: Black Rose|/collections/black-rose/|Black Rose"
    "Collection: Love Hurts|/collections/love-hurts/|Love Hurts"
    "Collection: Signature|/collections/signature/|Signature"
    "Collection: Kids Capsule|/collections/kids-capsule/|Kids Capsule"
    "About|/about/|SkyyRose"
    "World: Black Rose|/worlds/black-rose/|template-immersive-black-rose"
    "World: Love Hurts|/worlds/love-hurts/|template-immersive-love-hurts"
    "World: Signature|/worlds/signature/|template-immersive-signature"
    "Pre-Order Gateway|/pre-order/|Pre-Order"
)

# V2 legacy routes: "name|path|expected_redirect_path" -- each 302s on staging
# [live 2026-09-19]. A 200 here would mean the V1 template is still answering.
REDIRECT_CHECKS_V2=(
    "Legacy collection: Black Rose|/collection-black-rose/|/collections/black-rose/"
    "Legacy collection: Love Hurts|/collection-love-hurts/|/collections/love-hurts/"
    "Legacy collection: Signature|/collection-signature/|/collections/signature/"
    "Legacy collection: Kids Capsule|/collection-kids-capsule/|/collections/kids-capsule/"
    "Legacy experience: Black Rose|/experience-black-rose/|/worlds/black-rose/"
    "Legacy experience: Love Hurts|/experience-love-hurts/|/worlds/love-hurts/"
    "Legacy experience: Signature|/experience-signature/|/worlds/signature/"
)

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
# KEY=value from an env file without sourcing it (last assignment wins).
env_value() {
    local raw
    raw="$(grep -E "^[[:space:]]*(export[[:space:]]+)?$2=" "$1" | tail -1 || true)"
    [[ -n "$raw" ]] || return 0
    raw="${raw#*=}"
    raw="${raw%\"}"; raw="${raw#\"}"
    raw="${raw%\'}"; raw="${raw#\'}"
    printf '%s' "$raw"
}

load_env_file() {
    local file="$1" url path
    if [[ ! -f "$file" ]]; then
        log_error "--env-file: $file not found"
        exit 1
    fi
    url="$(env_value "$file" PUBLIC_URL)"
    [[ -n "$url" ]] || url="$(env_value "$file" WORDPRESS_URL)"
    path="$(env_value "$file" WP_THEME_PATH)"
    [[ -n "$url" ]] && SITE_URL="$(site_url_base "$url")"
    [[ -n "$path" ]] && THEME_SLUG="$(basename "$path")"
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                usage
                exit 0
                ;;
            --list)
                list_checks
                exit 0
                ;;
            --url)
                [[ -n "${2:-}" ]] || { log_error "--url requires a URL argument"; exit 1; }
                SITE_URL="$(site_url_base "$2")"
                shift 2
                ;;
            --theme)
                [[ -n "${2:-}" ]] || { log_error "--theme requires a slug argument"; exit 1; }
                THEME_SLUG="$2"
                shift 2
                ;;
            --env-file)
                [[ -n "${2:-}" ]] || { log_error "--env-file requires a path argument"; exit 1; }
                load_env_file "$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# ---------------------------------------------------------------------------
# List health checks (no HTTP requests)
# ---------------------------------------------------------------------------
list_table() {
    local label="$1" entry name path value
    shift
    for entry in "$@"; do
        IFS='|' read -r name path value <<< "$entry"
        echo "  $name"
        echo "    URL:    ${SITE_URL}${path}"
        echo "    ${label} $value"
        echo ""
    done
}

list_checks() {
    echo "Both route tables are listed. At run time ONE is selected from the live"
    echo "Text Domain in ${SITE_URL:-<site-url>}/wp-content/themes/${THEME_SLUG:-<theme-slug>}/style.css"
    echo ""
    echo "=== Health Check Pages -- V1 (text domain: skyyrose) ==="
    echo ""
    list_table "Marker:" "${HEALTH_CHECKS_V1[@]}"
    echo "Total: ${#HEALTH_CHECKS_V1[@]} checks"
    echo ""
    echo "=== Health Check Pages -- V2 (text domain: skyyrose-flagship-2) ==="
    echo ""
    list_table "Marker:" "${HEALTH_CHECKS_V2[@]}"
    list_table "Redirects to:" "${REDIRECT_CHECKS_V2[@]}"
    echo "Total: $(( ${#HEALTH_CHECKS_V2[@]} + ${#REDIRECT_CHECKS_V2[@]} )) checks"
}

# ---------------------------------------------------------------------------
# Live theme detection -- fail CLOSED
# ---------------------------------------------------------------------------
require_target() {
    if [[ -z "$SITE_URL" ]]; then
        log_error "No target URL: set PUBLIC_URL (or WORDPRESS_URL), pass --url, or --env-file"
        exit 1
    fi
    if [[ -z "$THEME_SLUG" ]]; then
        log_error "No theme slug: set WP_THEME_PATH (basename is the slug), THEME_SLUG, --theme, or --env-file"
        exit 1
    fi
    SITE_URL="$(site_url_base "$SITE_URL")"
}

detect_text_domain() {
    local url tmpfile http_code
    url="${SITE_URL}/wp-content/themes/${THEME_SLUG}/style.css?_verify=${TIMESTAMP}"
    tmpfile=$(mktemp)
    http_code=$(curl -sS -o "$tmpfile" -w "%{http_code}" \
        --connect-timeout 10 --max-time 30 "$url" 2>/dev/null) || http_code="000"
    if [[ "$http_code" != "200" ]]; then
        rm -f "$tmpfile"
        log_error "Live theme style.css unreadable (HTTP $http_code) -- $url"
        log_error "Cannot establish which theme is live; refusing to guess a route table"
        exit 1
    fi
    # `|| true`: under pipefail a missing header would otherwise kill the script
    # here, silently, before the case below can refuse with a reason.
    LIVE_TEXT_DOMAIN="$({ grep -m1 -iE '^[[:space:]]*Text Domain:' "$tmpfile" || true; } \
        | sed -E 's/^[^:]*:[[:space:]]*//; s/[[:space:]]+$//' | tr -d '\r')"
    rm -f "$tmpfile"
    case "$LIVE_TEXT_DOMAIN" in
        skyyrose|skyyrose-flagship-2)
            log_success "Live theme '${THEME_SLUG}' has text domain '${LIVE_TEXT_DOMAIN}'"
            ;;
        *)
            log_error "Live theme '${THEME_SLUG}' has unrecognised text domain '${LIVE_TEXT_DOMAIN:-<none>}' -- no route table for it; refusing"
            exit 1
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Deep content verification for a single page
# ---------------------------------------------------------------------------
verify_page() {
    local name="$1"
    local url="$2"
    local marker="$3"

    CHECKS=$((CHECKS + 1))

    # Build cache-busting URL: use & if URL already has ?, otherwise use ?
    local full_url
    if [[ "$url" == *"?"* ]]; then
        full_url="${url}&_verify=${TIMESTAMP}"
    else
        full_url="${url}?_verify=${TIMESTAMP}"
    fi

    # Fetch page with retry support (use temp file to avoid echo/pipe size issues)
    local tmpfile http_code
    tmpfile=$(mktemp)
    http_code=$(curl -sSL -o "$tmpfile" -w "%{http_code}" \
        --connect-timeout 10 --max-time 30 \
        --retry 2 --retry-delay 3 \
        "$full_url" 2>/dev/null) || http_code="000"

    # Check HTTP status
    if [[ "$http_code" -ne 200 ]]; then
        log_error "$name: HTTP $http_code (expected 200) -- $full_url"
        rm -f "$tmpfile"
        FAILURES=$((FAILURES + 1))
        return 1
    fi

    # Check content marker (case-insensitive) directly on file
    if ! grep -qi "$marker" "$tmpfile"; then
        log_error "$name: Content marker '$marker' not found -- $full_url"
        rm -f "$tmpfile"
        FAILURES=$((FAILURES + 1))
        return 1
    fi

    rm -f "$tmpfile"

    log_success "$name: HTTP 200 + content verified"
    return 0
}

# ---------------------------------------------------------------------------
# Redirect verification: legacy path must 301/302 to the expected V2 path on
# THIS site -- the Location (query stripped) must equal SITE_URL + expected
# exactly; a suffix match would pass https://evil.invalid/collections/... or
# /es/collections/... . curl is NOT told to follow here -- a 200 means the
# old template answered.
# ---------------------------------------------------------------------------
verify_redirect() {
    local name="$1" path="$2" expected="$3"
    local full_url result http_code location
    CHECKS=$((CHECKS + 1))
    full_url="${SITE_URL}${path}?_verify=${TIMESTAMP}"
    result=$(curl -sS -o /dev/null -w "%{http_code}|%{redirect_url}" \
        --connect-timeout 10 --max-time 30 "$full_url" 2>/dev/null) || result="000|"
    http_code="${result%%|*}"
    location="${result#*|}"
    location="${location%%\?*}"
    if [[ "$http_code" != "301" && "$http_code" != "302" ]]; then
        log_error "$name: HTTP $http_code (expected 301/302 -> $expected) -- $full_url"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
    if [[ "$location" != "${SITE_URL}${expected}" ]]; then
        log_error "$name: redirects to '$location' (expected exactly ${SITE_URL}${expected}) -- $full_url"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
    log_success "$name: HTTP $http_code -> $expected"
    return 0
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
run_table() {
    local entry name path marker
    for entry in "$@"; do
        IFS='|' read -r name path marker <<< "$entry"
        verify_page "$name" "${SITE_URL}${path}" "$marker" || true
    done
}

main() {
    parse_args "$@"
    require_target

    echo ""
    log_info "=== SkyyRose Post-Deploy Verification ==="
    log_info "Target: $SITE_URL  (theme folder: $THEME_SLUG)"
    log_info "Cache-bust: _verify=$TIMESTAMP"
    echo ""

    detect_text_domain

    # Run all health checks -- collect failures, do not exit on first
    local entry name path target
    case "$LIVE_TEXT_DOMAIN" in
        skyyrose)
            run_table "${HEALTH_CHECKS_V1[@]}"
            ;;
        skyyrose-flagship-2)
            run_table "${HEALTH_CHECKS_V2[@]}"
            for entry in "${REDIRECT_CHECKS_V2[@]}"; do
                IFS='|' read -r name path target <<< "$entry"
                verify_redirect "$name" "$path" "$target" || true
            done
            ;;
    esac

    # Summary
    echo ""
    log_info "=== Verification Summary ==="
    log_info "Checks: $CHECKS  Passed: $((CHECKS - FAILURES))  Failed: $FAILURES"

    if [[ "$FAILURES" -eq 0 ]]; then
        echo ""
        log_success "All $CHECKS checks verified successfully"
        exit 0
    else
        echo ""
        log_error "$FAILURES of $CHECKS checks failed verification"
        exit 1
    fi
}

main "$@"
