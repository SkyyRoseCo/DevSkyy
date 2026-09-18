#!/usr/bin/env bash
# scripts/deploy-theme.sh -- Production deploy script for SkyyRose WordPress theme
# Transfers built theme files to skyyrose.co with maintenance mode safety and cache flushing.
#
# Usage:
#   bash scripts/deploy-theme.sh              # Live deploy to production
#   bash scripts/deploy-theme.sh --dry-run    # Preview what would happen (no server contact)
#   bash scripts/deploy-theme.sh --help       # Show this help message
#
# Requirements:
#   - .env.wordpress with SSH/SFTP credentials (or set ENV_FILE to override path)
#   - sshpass installed (brew install hudochenkov/sshpass/sshpass)
#   - Theme directory at wordpress-theme/skyyrose-flagship/
#
# Safety:
#   - Maintenance mode is activated before file transfer and deactivated after
#   - trap cleanup EXIT INT TERM guarantees maintenance mode is disabled on failure
#   - WordPress auto-deactivates maintenance mode after 10 minutes as a fallback

set -euo pipefail

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
THEME_DIR="${THEME_DIR_OVERRIDE:-$PROJECT_ROOT/wordpress-theme/skyyrose-flagship}"
ENV_FILE="${ENV_FILE:-$PROJECT_ROOT/.env.wordpress}"

# ---------------------------------------------------------------------------
# State tracking
# ---------------------------------------------------------------------------
DRY_RUN=false
WITH_MAINTENANCE=false
MAINTENANCE_ACTIVE=false

# ---------------------------------------------------------------------------
# Color logging
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No color

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# ---------------------------------------------------------------------------
# Usage / help
# ---------------------------------------------------------------------------
usage() {
    echo "Usage: deploy-theme.sh [OPTIONS]"
    echo ""
    echo "Deploy the SkyyRose WordPress theme to production."
    echo ""
    echo "Options:"
    echo "  --dry-run            Preview what would happen without touching production"
    echo "  --with-maintenance   Enable wp maintenance-mode during deploy (legacy)."
    echo "                       Default is hot-swap, which avoids the Jetpack Uptime"
    echo "                       false-positive 503 window. Use --with-maintenance for"
    echo "                       deploys that include DB migrations or plugin changes."
    echo "  --help               Show this help message"
    echo ""
    echo "Environment:"
    echo "  ENV_FILE             Path to .env.wordpress (default: \$PROJECT_ROOT/.env.wordpress)"
    echo "  THEME_DIR_OVERRIDE   Override theme source directory"
    echo "  PUBLIC_URL           Verified URL for post-deploy check (default: https://skyyrose.co/)"
    echo ""
    echo "The script will:"
    echo "  1. Run preflight checks (credentials, tools, PHP syntax)"
    echo "  2. Transfer theme files via tar+scp with atomic hot-swap on remote"
    echo "     (or, with --with-maintenance, enable maintenance mode first)"
    echo "  3. Flush object/transient/rewrite caches"
    echo "  4. Verify the live site returns HTTP 200 with no PHP error markers"
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
            --with-maintenance)
                WITH_MAINTENANCE=true
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
# Source credentials
# ---------------------------------------------------------------------------
load_credentials() {
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Credential file not found: $ENV_FILE"
        log_error "Create .env.wordpress with SSH_HOST, SSH_USER, SSH_PASS, WP_THEME_PATH, SFTP_HOST, SFTP_USER, SFTP_PASS"
        exit 1
    fi
    # shellcheck source=/dev/null
    source "$ENV_FILE"
}

# ---------------------------------------------------------------------------
# Concurrency lock (DEPLOY-09 / bug-059)
#
# Two simultaneous deploys race on the remote `.old.$swap_id` rename and
# can leave the live theme pointing at a half-extracted tarball. flock
# acquires an exclusive, non-blocking lock held for the process lifetime.
# Stale PID in the lockfile is reclaimed if the owner is no longer alive.
# ---------------------------------------------------------------------------
DEPLOY_LOCK_FILE="${DEPLOY_LOCK_FILE:-/tmp/skyyrose-deploy.lock}"
DEPLOY_LOCK_HELD=0

acquire_deploy_lock() {
    if [[ -f "$DEPLOY_LOCK_FILE" ]]; then
        local stale_pid
        stale_pid="$(cat "$DEPLOY_LOCK_FILE" 2>/dev/null || echo "")"
        if [[ -n "$stale_pid" ]] && kill -0 "$stale_pid" 2>/dev/null; then
            log_error "Another deploy is already running (pid $stale_pid)"
            log_error "Lock file: $DEPLOY_LOCK_FILE"
            exit 2
        fi
        log_warn "Reclaiming stale deploy lock (pid $stale_pid not running)"
        rm -f "$DEPLOY_LOCK_FILE"
    fi
    # Use mkdir-style atomic create via noclobber; portable across macOS/Linux.
    if ! (set -o noclobber; echo "$$" > "$DEPLOY_LOCK_FILE") 2>/dev/null; then
        log_error "Failed to acquire deploy lock at $DEPLOY_LOCK_FILE"
        exit 2
    fi
    DEPLOY_LOCK_HELD=1
}

release_deploy_lock() {
    if (( DEPLOY_LOCK_HELD )); then
        rm -f "$DEPLOY_LOCK_FILE"
        DEPLOY_LOCK_HELD=0
    fi
}

# ---------------------------------------------------------------------------
# Deploy state — used by cleanup/rollback
# ---------------------------------------------------------------------------
REMOTE_SWAP_ID=""  # Set by try_rsync after successful hot-swap; consumed by auto_rollback.

# ---------------------------------------------------------------------------
# Structured log + phase timing (DEPLOY-10 / bug-062)
#
# Every deploy produces a timestamped log at $DEPLOY_LOG_FILE and prints
# a final summary line: "preflight=Ns tar=Ns upload=Ns swap=Ns verify=Ns
# total=Ns". Enables forensics without parsing noisy stdout.
# ---------------------------------------------------------------------------
DEPLOY_LOG_FILE="${DEPLOY_LOG_FILE:-/tmp/skyyrose-deploy-$(date +%Y%m%d-%H%M%S).log}"
DEPLOY_START_TS=$(date +%s)

# Plain scalars — bash 3.2 (macOS /bin/bash) lacks associative arrays.
# Variables PHASE_STARTED_<name> and PHASE_TIME_<name> are created on first
# use by phase_start via `printf -v` (no eval), and read via ${!var:-0}
# indirection in phase_end/phase_summary. No static initialization
# needed; the indirect read defaults to 0 when the phase never ran.

phase_start() {
    printf -v "PHASE_STARTED_$1" '%s' "$(date +%s)"
}

phase_end() {
    local name="$1"
    local started_var="PHASE_STARTED_$name"
    local started="${!started_var:-$(date +%s)}"
    local elapsed=$(( $(date +%s) - started ))
    printf -v "PHASE_TIME_$name" '%s' "$elapsed"
}

phase_summary() {
    local total=$(( $(date +%s) - DEPLOY_START_TS ))
    local line="Deploy phases —"
    for phase in preflight tar upload swap cache verify; do
        local var="PHASE_TIME_$phase"
        line="$line ${phase}=${!var:-0}s"
    done
    line="$line total=${total}s"
    log_info "$line"
    log_info "Full log: $DEPLOY_LOG_FILE"
}

# ---------------------------------------------------------------------------
# Cleanup handler -- ALWAYS disables maintenance mode on exit (DEPLOY-07)
# Also: releases deploy lock and triggers auto-rollback if verify failed.
# ---------------------------------------------------------------------------
ROLLBACK_REQUESTED=false

cleanup() {
    local exit_code=$?
    if [[ "$MAINTENANCE_ACTIVE" == "true" ]]; then
        log_warn "Cleanup: disabling maintenance mode after unexpected exit..."
        wp_remote "maintenance-mode deactivate" || log_error "CRITICAL: Failed to deactivate maintenance mode -- check site manually"
        MAINTENANCE_ACTIVE=false
    fi
    if [[ "$ROLLBACK_REQUESTED" == "true" ]]; then
        if ! auto_rollback; then
            # Rollback itself failed — escalate so exit code reflects the
            # worst-case state (site broken AND backup unusable).
            exit_code=4
        fi
    fi
    release_deploy_lock
    unset SSHPASS
    return $exit_code
}

trap cleanup EXIT INT TERM

# ---------------------------------------------------------------------------
# Auto-rollback (DEPLOY-11 / bug-060)
#
# If post-deploy verification fails, rename the just-deployed theme aside
# as .failed.$ts and restore the previous .old.$ts backup into the live
# path. Then flush caches. Site returns to pre-deploy state automatically
# instead of serving a broken page until a human notices.
# ---------------------------------------------------------------------------
auto_rollback() {
    if [[ -z "$REMOTE_SWAP_ID" ]]; then
        log_error "Cannot auto-rollback: no swap ID recorded (deploy didn't reach swap phase)"
        return 1
    fi
    log_warn "Initiating auto-rollback to pre-deploy state (swap_id=$REMOTE_SWAP_ID)..."
    build_ssh_cmd
    # Single round-trip: existence check + both renames gated by `set -e`.
    # If the backup dir is missing (transient or gone), the inner script
    # exits non-zero before clobbering live with a non-existent source.
    if "${SSH_CMD[@]}" "${SSH_USER}@${SSH_HOST}" "set -e; [ -d '${WP_THEME_PATH}.old.${REMOTE_SWAP_ID}' ] && mv '${WP_THEME_PATH}' '${WP_THEME_PATH}.failed.${REMOTE_SWAP_ID}' && mv '${WP_THEME_PATH}.old.${REMOTE_SWAP_ID}' '${WP_THEME_PATH}'" 2>/dev/null; then
        wp_remote "cache flush" >/dev/null 2>&1 || true
        log_success "Auto-rollback complete — site restored to pre-deploy state"
        log_info "Failed deploy preserved at ${WP_THEME_PATH}.failed.${REMOTE_SWAP_ID} for forensics"
        return 0
    else
        log_error "Auto-rollback FAILED: backup dir missing, transient SSH error, or mv failed"
        log_error "Manual recovery required — site may be broken. Last deploy log: $DEPLOY_LOG_FILE"
        return 1
    fi
}

# ---------------------------------------------------------------------------
# SSH auth helper — key preferred, sshpass -e fallback (avoids ps exposure)
# SSHPASS is set just-in-time inside try_rsync() rather than at module
# load time so the secret doesn't linger in the environment for the
# whole deploy.
# ---------------------------------------------------------------------------
SSH_STRICT="${SSH_STRICT_HOST:-accept-new}"

# Extract the "Version:" header value from a WP style.css on stdin.
# Shared by the local-tree and live-site reads in verify_live().
extract_theme_version() {
    grep -m1 -iE "^[[:space:]]*Version:" | awk '{print $2}'
}

# Build an SSH command array with auth resolved once.
# Usage: "${SSH_CMD[@]}" user@host "command"
build_ssh_cmd() {
    local key_path="${SSH_KEY_PATH:-$HOME/.ssh/skyyrose-deploy}"
    SSH_CMD=( ssh -o "StrictHostKeyChecking=$SSH_STRICT" -o ConnectTimeout=15 -p "${SSH_PORT:-22}" )
    SCP_CMD=( scp -o "StrictHostKeyChecking=$SSH_STRICT" -P "${SSH_PORT:-22}" )
    if [[ -f "$key_path" ]]; then
        SSH_CMD+=( -i "$key_path" )
        SCP_CMD+=( -i "$key_path" )
    elif [[ -n "${SSH_PASS:-}" ]] && command -v sshpass &>/dev/null; then
        export SSHPASS="$SSH_PASS"
        SSH_CMD=( sshpass -e "${SSH_CMD[@]}" )
        SCP_CMD=( sshpass -e "${SCP_CMD[@]}" )
    fi
}

# ---------------------------------------------------------------------------
# WP-CLI over SSH (proven pattern from wp-deploy-theme.sh)
# ---------------------------------------------------------------------------
wp_remote() {
    local cmd="$1"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] wp $cmd"
        return 0
    fi
    "${SSH_CMD[@]}" "${SSH_USER}@${SSH_HOST}" "wp $cmd" 2>/dev/null
}

# ---------------------------------------------------------------------------
# Source-completeness gate (bug-252) -- fail CLOSED
#
# Catches the two deploy-defect classes that actually shipped:
#   - version-triple drift (style.css / functions.php / readme.txt): stale
#     ?ver= keeps the WP.com edge cache serving old assets after deploy
#   - incomplete source tree (sparse worktree / missing binaries): the
#     remote hot-swap DELETES anything the source lacks (v1.10.3 shipped
#     without its tracked signature emblem -> live 404)
# Emergency override: PREFLIGHT_SKIP_COMPLETENESS=1 (logged loudly).
# ---------------------------------------------------------------------------
# Check 1/3 (preflight_completeness): the three version-carrying files must
# exist and agree. A MISSING file is checked explicitly first: awk/sed on an
# absent path exit non-zero, which under `set -e` would crash the script
# (raw "can't open file", exit 2) BEFORE the -z fail-closed handler below
# runs. The 2>/dev/null || true on the reads is defense-in-depth for the
# exists-but-unreadable (permissions) edge -> empty -> clean exit 1.
check_version_triple() {
    local vf v_style v_func v_readme
    for vf in style.css functions.php readme.txt; do
        if [[ ! -f "$THEME_DIR/$vf" ]]; then
            log_error "Version file missing from deploy source: $vf -- refusing to deploy"
            exit 1
        fi
    done
    v_style=$(awk '/^Version:/ {print $2; exit}' "$THEME_DIR/style.css" 2>/dev/null || true)
    v_func=$(sed -nE "s/^define\( 'SKYYROSE_VERSION', '([^']+)' \);.*/\1/p" "$THEME_DIR/functions.php" 2>/dev/null | head -1 || true)
    v_readme=$(awk '/^Stable tag:/ {print $3; exit}' "$THEME_DIR/readme.txt" 2>/dev/null || true)
    if [[ -z "$v_style" || -z "$v_func" || -z "$v_readme" ]]; then
        log_error "Version triple unreadable (style.css='${v_style:-?}' functions.php='${v_func:-?}' readme.txt='${v_readme:-?}') -- refusing to deploy"
        exit 1
    fi
    if [[ "$v_style" == "$v_func" && "$v_func" == "$v_readme" ]]; then
        log_success "Version triple in sync: $v_style"
    else
        log_error "Version triple DRIFT: style.css=$v_style functions.php=$v_func readme.txt=$v_readme -- sync all three before deploying"
        exit 1
    fi
}

# Check 2/3 (preflight_completeness): every git-tracked file must exist on
# disk (SOURCE-tree completeness). Catches sparse checkouts and
# deleted-but-uncommitted files. Extra untracked files are allowed (riders
# shipped that way for months). NOTE: "on disk" != "reaches production" -- a
# tracked file whose basename matches a tar/rsync exclude (CLAUDE.local.md,
# ._*, __pycache__) still passes here but is dropped from the artifact by
# design; this check asserts the source is whole, not the tarball.
check_tracked_files() {
    if ! git -C "$THEME_DIR" rev-parse --is-inside-work-tree &>/dev/null; then
        log_warn "Deploy source is not a git work tree -- relying on critical-asset floor only"
        return 0
    fi
    # Capture the list with explicit failure handling. A bare
    # `done < <(git ls-files)` process substitution does NOT propagate
    # git's exit status, so a corrupt index / permissions / disk-full read
    # would silently yield zero files -> false "0/0 OK" and pass the gate
    # (the bug-230 fail-open class). `if ! ls=$(...)` fails CLOSED.
    local ls_files missing=0 tracked=0 f
    if ! ls_files=$(git -C "$THEME_DIR" ls-files 2>/dev/null); then
        log_error "git ls-files failed -- cannot verify tracked-file completeness; refusing to deploy"
        exit 1
    fi
    while IFS= read -r f; do
        [[ -n "$f" ]] || continue
        tracked=$((tracked + 1))
        if [[ ! -e "$THEME_DIR/$f" ]]; then
            log_error "Tracked file missing from deploy source: $f"
            missing=$((missing + 1))
        fi
    done <<< "$ls_files"
    if (( missing > 0 )); then
        log_error "$missing tracked file(s) absent from the source tree -- the hot-swap would delete them from production"
        exit 1
    fi
    log_success "Tracked-file completeness: $tracked/$tracked on disk"
}

# Check 3/3 (preflight_completeness): critical-asset floor (git-independent;
# static minimums, not exact counts).
check_asset_floor() {
    local emblems fonts glb_state="MISSING"
    emblems=$({ find "$THEME_DIR/assets/images/emblems" -maxdepth 1 -name '*.webp' 2>/dev/null || true; } | wc -l | tr -d ' ')
    fonts=$({ find "$THEME_DIR/assets/fonts" -maxdepth 1 -name '*.woff2' 2>/dev/null || true; } | wc -l | tr -d ' ')
    if [[ -f "$THEME_DIR/assets/models/skyy.glb" ]]; then glb_state="present"; fi
    if (( emblems < 3 )) || (( fonts < 10 )) || [[ "$glb_state" == "MISSING" ]]; then
        log_error "Critical-asset floor FAILED: emblems=$emblems (need >=3), woff2=$fonts (need >=10), skyy.glb $glb_state"
        exit 1
    fi
    log_success "Critical-asset floor: $emblems emblem webp, $fonts woff2, mascot GLB $glb_state"
}

preflight_completeness() {
    if [[ "${PREFLIGHT_SKIP_COMPLETENESS:-0}" == "1" ]]; then
        log_warn "Source-completeness gate SKIPPED (PREFLIGHT_SKIP_COMPLETENESS=1) -- deploying an UNVERIFIED tree"
        return 0
    fi
    check_version_triple
    check_tracked_files
    check_asset_floor
}

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
preflight() {
    log_info "Running preflight checks..."

    # Verify required env vars
    local required_vars=(SSH_HOST SSH_USER SSH_PASS WP_THEME_PATH SFTP_HOST SFTP_USER SFTP_PASS)
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Missing required credential: $var"
            exit 1
        fi
    done
    log_success "All credentials present"

    # Verify SSH auth method (key preferred, sshpass fallback)
    if [[ -f "${SSH_KEY_PATH:-$HOME/.ssh/skyyrose-deploy}" ]]; then
        log_success "SSH key found: ${SSH_KEY_PATH:-$HOME/.ssh/skyyrose-deploy}"
    elif command -v sshpass &>/dev/null; then
        log_success "sshpass available (password auth)"
    else
        log_error "No SSH key at ~/.ssh/skyyrose-deploy and sshpass not installed"
        exit 1
    fi

    # Verify theme directory
    if [[ ! -d "$THEME_DIR" ]]; then
        log_error "Theme directory not found: $THEME_DIR"
        exit 1
    fi
    log_success "Theme directory exists: $THEME_DIR"

    # Source-completeness gate (bug-252) -- cheap checks before the PHP lint sweep.
    preflight_completeness

    # PHP syntax check — scope matches tarball (vendor/node_modules/tests
    # are gitignored and excluded from deploy, so don't lint them either).
    # Invariant: preflight scope == deploy scope. Linting paths that are
    # never shipped costs ~5 min/deploy for vendor/ alone (3,756 composer
    # files at ~0.36s per `php -l` fork).
    local php_bin
    php_bin="$(command -v php 2>/dev/null || echo /opt/homebrew/bin/php)"
    local php_errors=0
    local php_count=0
    while IFS= read -r -d '' phpfile; do
        php_count=$((php_count + 1))
        if ! "$php_bin" -l "$phpfile" &>/dev/null; then
            log_error "PHP syntax error: $phpfile"
            php_errors=$((php_errors + 1))
        fi
    done < <(find "$THEME_DIR" \
        \( -type d \( -name vendor -o -name node_modules -o -name tests -o -name '.git' \) -prune \) -o \
        \( -type f -name '*.php' -print0 \) 2>/dev/null)

    if [[ "$php_errors" -gt 0 ]]; then
        log_error "$php_errors PHP file(s) have syntax errors -- fix before deploying"
        exit 1
    fi
    log_success "PHP syntax check passed ($php_count files)"

    # Test SSH connectivity (skip in dry-run)
    if [[ "$DRY_RUN" == "false" ]]; then
        build_ssh_cmd
        if ! "${SSH_CMD[@]}" "${SSH_USER}@${SSH_HOST}" "echo ok" 2>/dev/null; then
            log_error "SSH connectivity test failed -- check credentials and network"
            exit 1
        fi
        log_success "SSH connectivity verified"
    else
        log_info "[DRY RUN] Skipping SSH connectivity test"
    fi

    log_success "All preflight checks passed"
}

# ---------------------------------------------------------------------------
# data/ fail-closed allowlist (bug-230 class)
#
# The static data/ excludes below are a belt; this is the gate. Enumerate
# EVERY file under data/ at deploy time and exclude anything not explicitly
# runtime-read, so a new file dropped into data/ is excluded BY DEFAULT
# instead of shipping world-readable (the fail-open that let 36 dossiers,
# _orphans.json, identity.schema.json and README.md reach production).
# Allowlist + file:line evidence: architecture-census.md + fix-log Wave 1b.
# ---------------------------------------------------------------------------
skyyrose_data_extra_excludes() {
    local f rel
    [[ -d "$THEME_DIR/data" ]] || return 0
    while IFS= read -r f; do
        rel="${f#"$THEME_DIR"/}"
        case "$rel" in
            data/skyyrose-catalog.csv | data/v7-cards.json | data/site-guide.json | data/editorial-index.json | data/collections/*/sot.json) ;;
            *) printf -- '--exclude=%s\n' "$rel" ;;
        esac
    done < <(find "$THEME_DIR/data" -type f | LC_ALL=C sort)
}

# ---------------------------------------------------------------------------
# Exclude lists shared by BOTH transfer paths -- tar/sftp (try_rsync, the
# LIVE path; WP.com doesn't support the rsync protocol) and lftp/sftp mirror
# (try_lftp, fallback only). Previously two hand-maintained arrays with a
# comment demanding "keep in sync" and nothing enforcing it -- they had
# drifted: RSYNC_EXCLUDES additionally excluded package.json/
# package-lock.json/composer.json/composer.lock/webpack.config.js/
# generate_models.js that tar_excludes did not (so those files currently
# ship via the live tar path); tar_excludes additionally excluded
# _archive/.serena that RSYNC_EXCLUDES did not. Both asymmetries are
# preserved below as explicit per-consumer arrays rather than silently
# unified -- unifying would change what reaches production, a separate
# decision from deduping the list mechanics (tasks/todo.md, 2026-08-01).
#
# Static-analysis config is dev-only. phpstan/constants.php exists purely so
# PHPStan can discover SKYYROSE_DIR/_URI; WordPress never loads it, and a
# stray phpstan/ directory is a marketplace-review flag.
#
# data/ ships ONLY runtime-read files (allowlist + file:line evidence in
# tasks/wp-commercial-theme/architecture-census.md + fix-log.md Wave 1b):
# skyyrose-catalog.csv, v7-cards.json, site-guide.json, collections/*/sot.json,
# editorial-index.json. Everything below is internal (dossiers = Corey-authored
# render specs, previously world-readable — 2026-07-19) or build-time-only.
# ---------------------------------------------------------------------------
SKYY_EXCLUDE_COMMON_DIRS=(
    node_modules vendor tests test-results scripts
    .deploy-archives phpstan playwright-report screenshots
)
SKYY_EXCLUDE_COMMON_PATTERNS=(
    '.git' '.env*' '*.map' '*.log' '.DS_Store' 'deploy.sh'
    'CLAUDE.md' 'CLAUDE.local.md' '._*' '__pycache__'
    'IMMERSIVE-WORLDS-PLAN.md' '.gitignore' '.phpcs.xml'
    'phpstan.neon' 'phpstan-baseline.neon'
    '.eslintrc*' '.prettierrc*' '.editorconfig' 'phpunit.xml'
    'data/dossiers' 'data/brand' 'data/brand-logos' 'data/product-references'
    'data/*.py' 'data/*.bak*' 'data/*.schema.json' 'data/product-embeddings.json'
    'data/product-similarities.json' 'data/logo-registry.json'
    'data/render-corrections.json' 'data/render-keepers.json'
    'data/visual-manifest.json' 'data/collections/*/copy.md'
    'data/collections/*/identity.json' 'data/collections/*/index.html'
)
# Historically present in RSYNC_EXCLUDES only -- these currently DO ship via
# the live tar path (see divergence note above).
SKYY_EXCLUDE_RSYNC_ONLY=(
    '.git/' 'package.json' 'package-lock.json' 'composer.json'
    'composer.lock' 'webpack.config.js' 'generate_models.js'
)
# Historically present in tar_excludes only.
SKYY_EXCLUDE_TAR_ONLY=( '_archive' '.serena' )

# Render the shared lists into --exclude= flags per transfer tool. Directory
# entries get a trailing '/' for rsync/lftp (directory-only match per
# rsync(1)) and no trailing slash for tar (no such syntax there).
skyyrose_render_rsync_excludes() {
    local d p
    for d in "${SKYY_EXCLUDE_COMMON_DIRS[@]}"; do printf -- '--exclude=%s/\n' "$d"; done
    for p in "${SKYY_EXCLUDE_COMMON_PATTERNS[@]}" "${SKYY_EXCLUDE_RSYNC_ONLY[@]}"; do
        printf -- '--exclude=%s\n' "$p"
    done
}

skyyrose_render_tar_excludes() {
    local d p
    for d in "${SKYY_EXCLUDE_COMMON_DIRS[@]}"; do printf -- '--exclude=%s\n' "$d"; done
    for p in "${SKYY_EXCLUDE_COMMON_PATTERNS[@]}" "${SKYY_EXCLUDE_TAR_ONLY[@]}"; do
        printf -- '--exclude=%s\n' "$p"
    done
}

# ---------------------------------------------------------------------------
# Rsync exclude list (comprehensive -- prevents dev files from reaching production)
# ---------------------------------------------------------------------------
RSYNC_EXCLUDES=()
while IFS= read -r _skyy_exc; do
    RSYNC_EXCLUDES+=("$_skyy_exc")
done < <(skyyrose_render_rsync_excludes)
unset _skyy_exc

# Fail-closed gate: per-file excludes for everything in data/ outside the
# runtime allowlist (see skyyrose_data_extra_excludes above).
while IFS= read -r _skyy_exc; do
    RSYNC_EXCLUDES+=("$_skyy_exc")
done < <(skyyrose_data_extra_excludes)
unset _skyy_exc

# ---------------------------------------------------------------------------
# File transfer: rsync with lftp SFTP fallback (DEPLOY-01)
# ---------------------------------------------------------------------------
transfer_files() {
    log_info "Starting file transfer from $THEME_DIR to $WP_THEME_PATH..."

    if try_rsync; then
        log_success "File transfer completed via rsync"
        return 0
    fi

    log_warn "rsync failed or unavailable -- falling back to lftp SFTP mirror"

    if try_lftp; then
        log_success "File transfer completed via lftp SFTP"
        return 0
    fi

    log_error "Both rsync and lftp transfer failed"
    return 1
}

try_rsync() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] sftp upload $THEME_DIR/ -> ${SSH_USER}@${SSH_HOST}:${WP_THEME_PATH}/"
        return 0
    fi

    # WordPress.com doesn't support rsync protocol — use sftp batch upload.
    # Tar compression: 316 MB of the ~380 MB payload is already-compressed
    # media (WebP/GLB/JPG/PNG) on which gzip gets ~0% reduction but costs
    # 10–30s CPU. Use zstd -1 when available (5x faster, similar ratio),
    # falling back to plain -cf (no compression) when zstd missing.
    phase_start tar
    log_info "Creating upload archive..."
    local tmpzip remote_tar_name zstd_flag
    if tar --help 2>&1 | grep -q -- '--zstd' && command -v zstd &>/dev/null; then
        zstd_flag="--zstd"
        tmpzip="/tmp/skyyrose-flagship-deploy.tar.zst"
        remote_tar_name="skyyrose-deploy.tar.zst"
        log_info "Using zstd compression (fast path)"
    else
        zstd_flag=""
        tmpzip="/tmp/skyyrose-flagship-deploy.tar"
        remote_tar_name="skyyrose-deploy.tar"
        log_info "Using uncompressed tar (zstd unavailable — skipping gzip waste on pre-compressed media)"
    fi

    # Rendered from the shared exclude lists defined above RSYNC_EXCLUDES
    # (SKYY_EXCLUDE_COMMON_DIRS/PATTERNS + SKYY_EXCLUDE_TAR_ONLY) -- see the
    # divergence note there for what differs from the rsync/lftp form.
    local tar_excludes=()
    local _skyy_texc
    while IFS= read -r _skyy_texc; do
        tar_excludes+=("$_skyy_texc")
    done < <(skyyrose_render_tar_excludes)

    # Fail-closed gate (mirrors RSYNC_EXCLUDES): per-file excludes for every
    # data/ file outside the runtime allowlist — new data/ files never ship
    # by default.
    local _skyy_exc
    while IFS= read -r _skyy_exc; do
        tar_excludes+=("$_skyy_exc")
    done < <(skyyrose_data_extra_excludes)

    # shellcheck disable=SC2086  # zstd_flag is intentionally word-split
    tar $zstd_flag -cf "$tmpzip" "${tar_excludes[@]}" \
        -C "$(dirname "$THEME_DIR")" "$(basename "$THEME_DIR")"

    local archive_size
    archive_size="$(du -h "$tmpzip" | cut -f1)"
    log_info "Archive: $tmpzip ($archive_size)"
    phase_end tar

    # Build SSH cmd then set SSHPASS just-in-time (reduces env exposure
    # window from entire deploy to upload+extract phase only).
    build_ssh_cmd
    if [[ -n "${SSH_PASS:-}" ]] && command -v sshpass &>/dev/null \
        && [[ ! -f "${SSH_KEY_PATH:-$HOME/.ssh/skyyrose-deploy}" ]]; then
        export SSHPASS="$SSH_PASS"
    fi

    # try_rsync is invoked as an `if` condition, which suppresses errexit for
    # the whole function body — every failure below MUST be checked explicitly
    # or the script sails past it (bug-086: scp died mid-transfer, the
    # truncated tar failed to extract, and the deploy still reported success).
    phase_start upload
    log_info "Uploading via scp..."
    local local_size remote_size attempt upload_ok=0
    local_size=$(stat -f%z "$tmpzip" 2>/dev/null || stat -c%s "$tmpzip")
    for attempt in 1 2 3; do
        if "${SCP_CMD[@]}" "$tmpzip" "${SSH_USER}@${SSH_HOST}:/tmp/${remote_tar_name}"; then
            remote_size=$("${SSH_CMD[@]}" "${SSH_USER}@${SSH_HOST}" \
                "stat -c%s /tmp/${remote_tar_name} 2>/dev/null || wc -c < /tmp/${remote_tar_name}" \
                2>/dev/null | tr -d '[:space:]')
            if [[ "$remote_size" == "$local_size" ]]; then
                upload_ok=1
                break
            fi
            log_warn "Upload size mismatch (local=$local_size remote=${remote_size:-unknown}) — attempt $attempt/3"
        else
            log_warn "scp transfer failed — attempt $attempt/3"
        fi
    done
    if (( ! upload_ok )); then
        log_error "Upload failed after 3 attempts — aborting before extract (live theme untouched)"
        rm -f "$tmpzip"
        phase_end upload
        return 1
    fi
    phase_end upload

    phase_start swap
    log_info "Extracting on remote (atomic hot-swap)..."
    # Hot-swap deploy (DEPLOY-08): rename current theme aside, then rename new
    # theme into place. The live path is unreachable only between two consecutive
    # rename(2) syscalls — microseconds, not the ~60 seconds the old `rm -rf && mv`
    # pattern produced with maintenance mode. Jetpack Uptime stops firing
    # false-positive "site is down" alerts during routine code-only deploys.
    #
    # CHANGE (bug-060): no longer rm `.old.$swap_id` immediately after swap.
    # Keep it as an auto-rollback anchor; deterministic cleanup retains only
    # the 2 most recent generations (see trim step below).
    local swap_id
    swap_id="$(date +%s)-$$"
    # Swap + prune old backups (keep most recent 2) in one remote round-trip.
    # Retention is load-bearing for auto_rollback: zero backups → no anchor.
    local parent_dir theme_name
    parent_dir="$(dirname "$WP_THEME_PATH")"
    theme_name="$(basename "$WP_THEME_PATH")"
    if ! "${SSH_CMD[@]}" "${SSH_USER}@${SSH_HOST}" "set -e; cd /tmp && tar ${zstd_flag} -xf ${remote_tar_name} && (if [ -d '${WP_THEME_PATH}' ]; then mv '${WP_THEME_PATH}' '${WP_THEME_PATH}.old.${swap_id}'; fi) && mv skyyrose-flagship '${WP_THEME_PATH}' && rm -f ${remote_tar_name} && (cd '${parent_dir}' && ls -1dt '${theme_name}.old.'* 2>/dev/null | tail -n +3 | xargs -I {} rm -rf {} 2>/dev/null; true)"; then
        log_error "Remote extract/swap FAILED — live theme was not swapped"
        rm -f "$tmpzip"
        phase_end swap
        return 1
    fi
    # Only record the swap ID once the swap actually happened — auto_rollback
    # uses it as the anchor, and a pre-swap failure must not trigger a bogus
    # rollback against a backup dir that was never created.
    REMOTE_SWAP_ID="$swap_id"
    phase_end swap

    # SSHPASS stays in env until cleanup(); subsequent wp_remote calls
    # (cache flush, verify) need it. Unsetting here breaks those. The
    # original "defer until just-in-time" win is that preflight and tar
    # (which run before build_ssh_cmd) never see SSHPASS.
    rm -f "$tmpzip"
    log_success "Theme uploaded and extracted"
}

# Convert one rsync exclude glob into an lftp-compatible extended regex
# (lftp mirror's -x/--exclude takes a REGEX, matched per lftp(1); rsync's
# excludes are GLOBS -- passing them straight through breaks the mirror,
# e.g. lftp aborts on '*.map' with "Invalid preceding regular expression",
# 2026-07-02 deploy failure).
#
# rsync's own anchoring rules, ported to regex:
#   - a leading '/', or a '/' anywhere but trailing, anchors the pattern to
#     the start of the relative path (rsync matches these against the full
#     path from the transfer root).
#   - no '/' at all, or only a trailing '/', matches a whole path SEGMENT
#     at any depth (rsync matches these against the final path component,
#     but at any depth in the tree).
# A naive escape-dots-only conversion leaves the regex unanchored, so it
# matches as a substring anywhere: 'node_modules' would also exclude
# 'assets/js/lib/fake_node_modules_shim.js', and '.git' would exclude
# 'assets/legit.github-badge.png'. Anchoring to path segments fixes both.
#
# A trailing '/' in the source glob marks a directory-only exclude in
# rsync; lftp appends '/' when testing a directory's path against
# --exclude (per lftp(1)), so requiring a literal trailing '/' in the
# regex reproduces that directory-only behavior (a same-named plain file
# is left alone).
rsync_glob_to_lftp_regex() {
    local raw="$1" is_dir=0 anchored=0

    [[ "$raw" == */ ]] && { is_dir=1; raw="${raw%/}"; }
    [[ "$raw" == /* ]] && { anchored=1; raw="${raw#/}"; }
    [[ "$raw" == */* ]] && anchored=1

    # Placeholder the glob wildcards before escaping so the escape step
    # below leaves them alone, then swap in their regex equivalents.
    raw="${raw//\*\*/$'\x01'}"
    raw="${raw//\*/$'\x02'}"
    # ']' must lead the class to be a literal member (POSIX bracket-
    # expression rule) -- this escapes every other ERE metachar.
    raw="$(printf '%s' "$raw" | sed -E 's/[]^$.+?(){}|\[]/\\&/g')"
    raw="${raw//$'\x01'/.*}"
    raw="${raw//$'\x02'/[^/]*}"

    local prefix suffix
    [[ "$anchored" -eq 1 ]] && prefix="^" || prefix="(^|/)"
    [[ "$is_dir" -eq 1 ]] && suffix="/" || suffix='($|/)'
    printf '%s%s%s' "$prefix" "$raw" "$suffix"
}

try_lftp() {
    if ! command -v lftp &>/dev/null; then
        log_warn "lftp not installed -- cannot use SFTP fallback"
        return 1
    fi

    # Convert rsync excludes (GLOBS) to lftp exclude format (REGEX) via
    # rsync_glob_to_lftp_regex (above). Each regex is single-quoted going
    # into the lftp -c script since anchored regexes now contain '(', '|',
    # '$' -- characters lftp's own command tokenizer shouldn't have to
    # guess about.
    local lftp_excludes=""
    for exc in "${RSYNC_EXCLUDES[@]}"; do
        local pattern="${exc#--exclude=}"
        pattern="${pattern//\'/}"
        local regex
        regex="$(rsync_glob_to_lftp_regex "$pattern")"
        lftp_excludes="$lftp_excludes --exclude '$regex'"
    done

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] lftp SFTP mirror $THEME_DIR/ -> $WP_THEME_PATH/"
        return 0
    fi

    local key_path="${SSH_KEY_PATH:-$HOME/.ssh/skyyrose-deploy}"
    # shellcheck disable=SC2086
    lftp -c "
set sftp:auto-confirm yes
set sftp:connect-program 'ssh -i $key_path -o StrictHostKeyChecking=yes'
set net:max-retries 3
set net:reconnect-interval-base 5
open -u $SFTP_USER, sftp://$SFTP_HOST:${SFTP_PORT:-22}
mirror --reverse --verbose --only-newer --delete $lftp_excludes \
  $THEME_DIR/ \
  $WP_THEME_PATH/
bye
"
}

# ---------------------------------------------------------------------------
# Cache flush (DEPLOY-03)
# ---------------------------------------------------------------------------
flush_caches() {
    log_info "Flushing all caches..."
    wp_remote "cache flush"
    wp_remote "transient delete --all"
    wp_remote "rewrite flush"
    log_success "All caches flushed"
}

# ---------------------------------------------------------------------------
# Post-deploy verification (DEPLOY-08)
#
# Boris Cherny's #1 tip for Claude Code: "Give Claude a way to verify its
# work. If Claude has that feedback loop, it will 2-3x the quality of the
# final result."
#
# We curl the live homepage with a cache-buster query string (bypasses
# Jetpack Boost page cache) and assert: HTTP 200, response size >= 50 KB
# (an error page or half-rendered fatal is typically much smaller), and
# no PHP error markers leaking through to the HTML body. Exits non-zero
# on any failure so the caller knows the deploy didn't really land.
#
# Override the verified URL via the PUBLIC_URL env var.
# ---------------------------------------------------------------------------
verify_live() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Skipping live verification"
        return 0
    fi

    local public_url="${PUBLIC_URL:-https://skyyrose.co/}"
    local expected_status="${EXPECTED_STATUS:-200}"
    # Use '&' as query separator when PUBLIC_URL already carries a query string
    # (e.g. ?bypass-coming-soon=<token>); otherwise '?'. This keeps the cache
    # buster from colliding with intentional query args used during veiled deploys.
    local sep="?"
    [[ "$public_url" == *"?"* ]] && sep="&"
    local bust_url
    bust_url="${public_url}${sep}deploy_verify=$(date +%s)"
    local tmpfile
    tmpfile="$(mktemp)"
    # shellcheck disable=SC2064
    trap "rm -f '$tmpfile'" RETURN

    log_info "Running post-deploy verification: $bust_url (expected HTTP $expected_status)"

    local http_code
    http_code=$(curl -sS -o "$tmpfile" -w "%{http_code}" \
        -A "DevSkyy-deploy-verify/1.0" \
        --max-time 30 \
        "$bust_url" 2>/dev/null || echo "000")

    if [[ "$http_code" != "$expected_status" ]]; then
        log_error "Verification FAILED: homepage returned HTTP $http_code (expected $expected_status)"
        return 1
    fi

    local size min_size
    size=$(wc -c < "$tmpfile" | tr -d ' ')
    min_size="${MIN_RESPONSE_BYTES:-50000}"
    if [[ "${size:-0}" -lt "$min_size" ]]; then
        log_error "Verification FAILED: homepage response too small (${size:-0} bytes, expected >= $min_size)"
        return 1
    fi

    if grep -qE "Fatal error|Parse error|Call to undefined|There has been a critical error" "$tmpfile"; then
        log_error "Verification FAILED: PHP error markers found in homepage response:"
        grep -oE "(Fatal error|Parse error|Call to undefined|There has been a critical error)[^<]{0,100}" "$tmpfile" | head -3 >&2
        return 1
    fi

    # Version-stamp assertion (bug-086): the live theme's style.css must carry
    # the same Version: as the local tree. A 200-OK homepage proves nothing
    # about the swap — WP serves the OLD theme just fine when the transfer
    # died before the rename. style.css is fetched directly from the theme
    # path, bypassing page caches via the query param.
    local base_url local_version live_version
    base_url="${public_url%%\?*}"
    local_version=$(extract_theme_version < "$THEME_DIR/style.css")
    live_version=$(curl -sS --max-time 15 \
        "${base_url%/}/wp-content/themes/$(basename "$WP_THEME_PATH")/style.css?deploy_verify=$(date +%s)" \
        2>/dev/null | extract_theme_version)
    if [[ -n "$local_version" && "$live_version" != "$local_version" ]]; then
        log_error "Verification FAILED: live theme version '${live_version:-unreadable}' != local '$local_version' — deploy did not land"
        return 1
    fi
    log_success "Version stamp verified: live style.css reports $local_version"

    # Deep per-page + content-marker verification lives in verify-deploy.sh
    # (called by deploy-pipeline.sh). Keep this function's scope narrow:
    # homepage-200 + no-PHP-errors is the last-ditch safety when someone
    # runs deploy-theme.sh directly. For full post-deploy checks, run
    # `bash scripts/verify-deploy.sh` or `bash scripts/deploy-pipeline.sh`.
    log_success "Post-deploy verification passed (HTTP $http_code, $size bytes)"

    # Structural DOM verification (Scrapling) — runs AFTER the curl gate.
    # Asserts template-specific markers like <main class="homepage-v2">,
    # <nav id="mainNav">, <section id="hero">, <div id="loader">, plus a
    # universal [data-skyyrose-error] count-must-be-0 beacon. Catches
    # regressions where WP returns 200 but front-page.php fell back or
    # stripped a critical section.
    #
    # Default: WARN-ONLY (logs failures, does NOT block deploy).
    # Set STRUCTURE_CHECK_STRICT=1 to promote structural failures into
    # full deploy failures (triggers auto-rollback via cleanup trap).
    structural_verify_live "$public_url"

    # JS-runtime deep verify (Playwright) — sees pageerrors and broken animation
    # lifecycles that curl/Scrapling cannot. Blocks (→ auto_rollback) when a spec
    # is provided and a surface regresses. No-op for plain manual deploys.
    if ! playwright_verify_live; then
        return 1
    fi
    return 0
}

# ---------------------------------------------------------------------------
# Structural verification gate (Scrapling-backed)
#
# Exit-code contract from scripts/verify_live_structure.py:
#   0 - all structural assertions passed
#   2 - one or more assertions failed (real regression)
#   3 - environment problem (scrapling missing, network unreachable)
#       NEVER blocks deploy; logged as warning only.
#
# Returns 0 always in warn-only mode (default). Returns 1 only when
# STRUCTURE_CHECK_STRICT=1 AND the script exits 2 (real failure).
# ---------------------------------------------------------------------------
structural_verify_live() {
    local public_url="$1"
    local script_path="$SCRIPT_DIR/verify_live_structure.py"
    local strict="${STRUCTURE_CHECK_STRICT:-0}"

    # Veiled deploys (coming-soon) intentionally serve a template that lacks the
    # baseline structural markers (homepage-v2, mainNav, hero, loader). Skip the
    # structural check entirely when SKIP_STRUCTURAL_VERIFY=1 is set.
    if [[ "${SKIP_STRUCTURAL_VERIFY:-0}" == "1" ]]; then
        log_info "Structural verification skipped (SKIP_STRUCTURAL_VERIFY=1)"
        return 0
    fi

    if [[ ! -f "$script_path" ]]; then
        log_warn "Structural check skipped: $script_path not found"
        return 0
    fi

    # Prefer the project venv's Python (where scrapling is installed).
    # Fall back to system python3 only if scrapling happens to be there.
    local py_bin=""
    if [[ -x "$PROJECT_ROOT/.venv/bin/python3" ]]; then
        py_bin="$PROJECT_ROOT/.venv/bin/python3"
    elif command -v python3 >/dev/null 2>&1; then
        py_bin="$(command -v python3)"
    else
        log_warn "Structural check skipped: no python3 found"
        return 0
    fi

    log_info "Running structural verification (Scrapling) against $public_url ..."
    local rc=0
    "$py_bin" "$script_path" --url "$public_url" --timeout 25 || rc=$?

    case "$rc" in
        0)
            log_success "Structural verification passed (Scrapling)"
            return 0
            ;;
        3)
            log_warn "Structural check skipped: environment unavailable (exit 3)"
            return 0
            ;;
        2)
            if [[ "$strict" == "1" ]]; then
                log_error "Structural verification FAILED (strict mode) — triggering rollback"
                return 1
            fi
            log_warn "Structural verification reported failures (warn-only mode — set STRUCTURE_CHECK_STRICT=1 to enforce)"
            return 0
            ;;
        *)
            log_warn "Structural check exited unexpectedly (rc=$rc) — treating as warning"
            return 0
            ;;
    esac
}

# ---------------------------------------------------------------------------
# JS-runtime deep verify gate (Playwright)
#
# The piece curl + Scrapling cannot provide: a real browser loads each surface,
# counts pageerrors (minus an allowlist of known pre-existing noise), and runs
# DOM lifecycle assertions. This is the gate that would have caught the v1.5.21
# black-flash / dead-title / broken-scroll-reveal trio that shipped "green".
#
# Only runs when a spec is provided (autopilot/CI set PW_VERIFY_SPEC[_FILE]);
# plain manual deploys skip it. Exit contract from verify-live-playwright.mjs:
#   0 - all surfaces clean
#   1 - a surface regressed  → BLOCKS, returns 1 → main() sets ROLLBACK_REQUESTED
#   3 - environment problem (playwright/browser missing) → warn-only, never blocks
# ---------------------------------------------------------------------------
playwright_verify_live() {
    if [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi
    if [[ -z "${PW_VERIFY_SPEC:-}${PW_VERIFY_SPEC_FILE:-}" ]]; then
        return 0
    fi
    local node_bin
    node_bin="$(command -v node 2>/dev/null || echo node)"
    log_info "Running JS-runtime deep verify (Playwright)..."
    local rc=0
    "$node_bin" "$SCRIPT_DIR/verify-live-playwright.mjs" || rc=$?
    case "$rc" in
        0) log_success "Playwright deep verify passed"; return 0 ;;
        3) log_warn "Playwright deep verify skipped: environment unavailable (exit 3)"; return 0 ;;
        *) log_error "Playwright deep verify FAILED (rc=$rc) — triggering rollback"; return 1 ;;
    esac
}

# ---------------------------------------------------------------------------
# Main deploy pipeline
# ---------------------------------------------------------------------------
main() {
    parse_args "$@"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "=== DRY RUN MODE -- no changes will be made ==="
    fi

    # Tee all stdout+stderr to the per-deploy log file so a single command
    # captures both the console summary and the forensic trail.
    if [[ "$DRY_RUN" != "true" ]]; then
        exec > >(tee -a "$DEPLOY_LOG_FILE") 2>&1
    fi

    log_info "=== SkyyRose Theme Deploy ==="
    log_info "Theme: $THEME_DIR"
    log_info "Target: ${ENV_FILE##*/}"
    log_info "Log:    $DEPLOY_LOG_FILE"

    # 0. Concurrency lock — refuses to start if another deploy is running
    acquire_deploy_lock

    # Load credentials (validates file exists)
    load_credentials

    # 1. Preflight checks
    phase_start preflight
    preflight
    phase_end preflight

    # 2. Maintenance mode — OPT-IN via --with-maintenance (DEPLOY-02)
    # Hot-swap (the default transfer path) makes maintenance mode unnecessary
    # for code-only deploys and eliminates the Jetpack Uptime false-positive
    # alert window. Pass --with-maintenance when deploying DB migrations or
    # plugin changes that require the site to be locked.
    if [[ "$WITH_MAINTENANCE" == "true" ]]; then
        log_info "Activating maintenance mode (--with-maintenance)..."
        wp_remote "maintenance-mode activate"
        MAINTENANCE_ACTIVE=true
        log_success "Maintenance mode active"
    else
        log_info "Skipping maintenance mode (hot-swap default) — pass --with-maintenance to opt in"
    fi

    # 3. Transfer files (DEPLOY-01) — phase timing for tar/upload/swap is set inside try_rsync
    transfer_files

    # 4. Disable maintenance mode if it was enabled (DEPLOY-03)
    if [[ "$MAINTENANCE_ACTIVE" == "true" ]]; then
        log_info "Deactivating maintenance mode..."
        wp_remote "maintenance-mode deactivate"
        MAINTENANCE_ACTIVE=false
        log_success "Maintenance mode deactivated"
    fi

    # 5. Flush caches (DEPLOY-03)
    phase_start cache
    flush_caches
    phase_end cache

    # 6. Post-deploy verification gate (DEPLOY-08 — Boris Cherny tip #14)
    # On failure, set ROLLBACK_REQUESTED so the EXIT trap's cleanup() fires
    # auto_rollback before releasing the deploy lock.
    phase_start verify
    if ! verify_live; then
        phase_end verify
        log_error "=== Deploy FAILED post-verification ==="
        ROLLBACK_REQUESTED=true
        phase_summary
        exit 3
    fi
    phase_end verify

    phase_summary
    log_success "=== Deploy complete (verified live) ==="
}

main "$@"
