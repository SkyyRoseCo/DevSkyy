#!/usr/bin/env bash
# scripts/deploy-pipeline.sh -- Single-command deploy pipeline for SkyyRose WordPress theme
#
# Orchestrates three steps sequentially:
#   [1/3] Build   -- npm run build (local-only, always runs including dry-run)
#   [2/3] Deploy  -- deploy-production.sh (the production wrapper; it pins
#                    DEPLOY_TARGET=production + .env.wordpress and execs the
#                    engine, deploy-theme.sh, which refuses direct calls)
#   [3/3] Verify  -- verify-deploy.sh --env-file .env.wordpress (HTTP 200 +
#                    content markers; route table chosen by the live theme)
#
# This is a PRODUCTION script (skyyrose.co). Callers: agents/wordpress_theme_builder/agent.ts.
#
# Usage:
#   bash scripts/deploy-pipeline.sh              # Full pipeline (build + deploy + verify)
#   bash scripts/deploy-pipeline.sh --dry-run    # Build runs, deploy previews, verify skipped
#   bash scripts/deploy-pipeline.sh --help       # Show this help message
#
# Each step must succeed before the next runs. In --dry-run mode:
#   - Build step runs normally (local-only, catches build errors early)
#   - Deploy step passes --dry-run to deploy-production.sh, which execs
#     deploy-theme.sh --dry-run (no server contact beyond one identity GET)
#   - Verify step is skipped (nothing was deployed)
#
# Exit codes:
#   0 - All steps completed successfully
#   1 - A step failed or dependency missing

set -euo pipefail

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
THEME_DIR="${THEME_DIR_OVERRIDE:-$PROJECT_ROOT/wordpress-theme/skyyrose-flagship}"

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
DRY_RUN=false

# ---------------------------------------------------------------------------
# Color logging (matches deploy-theme.sh pattern)
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No color

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# ---------------------------------------------------------------------------
# Usage / help
# ---------------------------------------------------------------------------
usage() {
    echo "Usage: deploy-pipeline.sh [OPTIONS]"
    echo ""
    echo "Single-command deploy pipeline for the SkyyRose WordPress theme."
    echo "Chains build, deploy, and verify into one command."
    echo ""
    echo "Steps:"
    echo "  [1/3] Build   Run npm run build in the theme directory (local-only)"
    echo "  [2/3] Deploy  Transfer files to production via deploy-production.sh"
    echo "                (the wrapper around the deploy-theme.sh engine)"
    echo "  [3/3] Verify  HTTP 200 + content via verify-deploy.sh --env-file .env.wordpress"
    echo ""
    echo "Options:"
    echo "  --dry-run    Build runs, deploy previews, verify is skipped"
    echo "  --help       Show this help message"
    echo ""
    echo "Environment:"
    echo "  THEME_DIR_OVERRIDE   Override theme source directory"
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --help|-h)
                usage
                exit 0
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
# Dependency checks -- verify scripts exist before running
# ---------------------------------------------------------------------------
check_dependencies() {
    local missing=0

    if [[ ! -f "$SCRIPT_DIR/deploy-production.sh" ]]; then
        log_error "Missing dependency: $SCRIPT_DIR/deploy-production.sh"
        missing=$((missing + 1))
    fi

    # The wrapper execs the engine; both must be present.
    if [[ ! -f "$SCRIPT_DIR/deploy-theme.sh" ]]; then
        log_error "Missing dependency: $SCRIPT_DIR/deploy-theme.sh"
        missing=$((missing + 1))
    fi

    if [[ ! -f "$SCRIPT_DIR/verify-deploy.sh" ]]; then
        log_error "Missing dependency: $SCRIPT_DIR/verify-deploy.sh"
        missing=$((missing + 1))
    fi

    if [[ ! -d "$THEME_DIR" ]]; then
        log_error "Theme directory not found: $THEME_DIR"
        missing=$((missing + 1))
    fi

    if [[ "$missing" -gt 0 ]]; then
        log_error "$missing dependency check(s) failed"
        exit 1
    fi

    log_success "All dependencies present"
}

# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
main() {
    parse_args "$@"

    echo ""
    echo "=== SkyyRose Deploy Pipeline ==="
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Pipeline will build, preview deploy, and skip verification"
    fi

    # Check dependencies
    check_dependencies

    # -----------------------------------------------------------------------
    # Step 1: Build (ALWAYS runs -- local-only, catches build errors early)
    # -----------------------------------------------------------------------
    log_info "[1/3] Building theme assets..."
    (cd "$THEME_DIR" && npm run build)
    log_success "[1/3] Build complete"

    # -----------------------------------------------------------------------
    # Step 2: Deploy (passes --dry-run if set) via the production wrapper
    # -----------------------------------------------------------------------
    log_info "[2/3] Deploying to production..."
    if [[ "$DRY_RUN" == "true" ]]; then
        bash "$SCRIPT_DIR/deploy-production.sh" --dry-run
    else
        bash "$SCRIPT_DIR/deploy-production.sh"
    fi
    log_success "[2/3] Deploy complete"

    # -----------------------------------------------------------------------
    # Step 3: Verify (skipped in dry-run -- nothing was deployed)
    # -----------------------------------------------------------------------
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[3/3] [DRY RUN] Skipping verification (no deploy occurred)"
        log_info "[DRY RUN] Would verify: homepage, collections, REST API, about page"
    else
        log_info "[3/3] Verifying deployment..."
        bash "$SCRIPT_DIR/verify-deploy.sh" --env-file "$PROJECT_ROOT/.env.wordpress"
        log_success "[3/3] Verification passed"
    fi

    # -----------------------------------------------------------------------
    # Done
    # -----------------------------------------------------------------------
    echo ""
    echo "=== Pipeline complete ==="
}

main "$@"
