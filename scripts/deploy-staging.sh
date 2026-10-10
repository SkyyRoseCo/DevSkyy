#!/usr/bin/env bash
# scripts/deploy-staging.sh -- Deploy skyyrose-flagship-2 to the WP.com STAGING site
#
# Founder directive (2026-09-18): staging and production have separate entry
# points. This wrapper pins the target, then execs scripts/deploy-theme.sh:
#   DEPLOY_TARGET=staging
#   ENV_FILE=<repo>/.env.wordpress.staging
#   THEME_DIR_OVERRIDE=<repo>/wordpress-theme/skyyrose-flagship-2
#
# Usage:
#   bash scripts/deploy-staging.sh              # deploy to staging (STOP-AND-SHOW)
#   bash scripts/deploy-staging.sh --dry-run    # engine preflight only, no transfer
#   bash scripts/deploy-staging.sh --allow-new-theme-folder       # first deploy of a folder
#   bash scripts/deploy-staging.sh --allow-theme-identity-change  # replace a different live theme
#   bash scripts/deploy-staging.sh --help
#
# The two --allow-* flags are one-shot overrides consumed by this wrapper and
# handed to the engine as ALLOW_NEW_THEME_FOLDER=1 / ALLOW_THEME_IDENTITY_CHANGE=1
# (its internal mechanism); they never appear in the engine's argv.
#
# Refuses (exit 1) when .env.wordpress.staging is missing, when its
# PUBLIC_URL (else WORDPRESS_URL) host is not a *.wpcomstaging.com host or the
# URL carries userinfo ('@'), when its SSH_USER is not
# "<first label of that host>.wordpress.com" or SFTP_USER differs from
# SSH_USER, when its WP_THEME_PATH does not end in skyyrose-flagship-2, or when
# the caller already exported ENV_FILE / THEME_DIR_OVERRIDE / DEPLOY_TARGET /
# PUBLIC_URL / WORDPRESS_URL / ALLOW_NEW_THEME_FOLDER /
# ALLOW_THEME_IDENTITY_CHANGE / PREFLIGHT_SKIP_COMPLETENESS.
#
# Staging host [live 2026-09-18]: staging-7e48-skyyrose.wpcomstaging.com
# (staging.skyyrose.co / staging.skyyrose.com do not resolve).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# shellcheck source=scripts/deploy-target-lib.sh
source "$SCRIPT_DIR/deploy-target-lib.sh"

deploy_target_main staging \
    "$PROJECT_ROOT/.env.wordpress.staging" \
    "$PROJECT_ROOT/wordpress-theme/skyyrose-flagship-2" \
    "$@"
