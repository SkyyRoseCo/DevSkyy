#!/usr/bin/env bash
# scripts/deploy-production.sh -- Deploy skyyrose-flagship-2 to PRODUCTION (skyyrose.co)
#
# Founder directive (2026-09-18): staging and production have separate entry
# points, and after cutover production runs folder skyyrose-flagship-2. This
# wrapper pins the target, then execs scripts/deploy-theme.sh:
#   DEPLOY_TARGET=production
#   ENV_FILE=<repo>/.env.wordpress
#   THEME_DIR_OVERRIDE=<repo>/wordpress-theme/skyyrose-flagship-2
#
# Usage:
#   bash scripts/deploy-production.sh              # deploy to production (STOP-AND-SHOW)
#   bash scripts/deploy-production.sh --dry-run    # engine preflight only, no transfer
#   bash scripts/deploy-production.sh --allow-new-theme-folder       # first deploy of a folder
#   bash scripts/deploy-production.sh --allow-theme-identity-change  # replace a different live theme
#   bash scripts/deploy-production.sh --help
#
# The two --allow-* flags are one-shot overrides consumed by this wrapper and
# handed to the engine as ALLOW_NEW_THEME_FOLDER=1 / ALLOW_THEME_IDENTITY_CHANGE=1
# (its internal mechanism); they never appear in the engine's argv.
#
# Refuses (exit 1) when .env.wordpress is missing, when its PUBLIC_URL (else
# WORDPRESS_URL) host is not skyyrose.co / www.skyyrose.co or the URL carries
# userinfo ('@'), when its SSH_USER is not skyyrose.wordpress.com (the host's
# own "<first label>.wordpress.com" account) or SFTP_USER differs from
# SSH_USER, when its WP_THEME_PATH does not end in skyyrose-flagship-2, or when
# the caller already exported ENV_FILE / THEME_DIR_OVERRIDE / DEPLOY_TARGET /
# PUBLIC_URL / WORDPRESS_URL / ALLOW_NEW_THEME_FOLDER /
# ALLOW_THEME_IDENTITY_CHANGE / PREFLIGHT_SKIP_COMPLETENESS.
#
# Until the founder-approved env switch, .env.wordpress still names the
# pre-cutover folder (skyyrose-flagship), so this script refuses by design and
# says so. Cutover = env switch -> deploy -> `wp theme activate
# skyyrose-flagship-2`, each step its own STOP-AND-SHOW.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# shellcheck source=scripts/deploy-target-lib.sh
source "$SCRIPT_DIR/deploy-target-lib.sh"

deploy_target_main production \
    "$PROJECT_ROOT/.env.wordpress" \
    "$PROJECT_ROOT/wordpress-theme/skyyrose-flagship-2" \
    "$@"
