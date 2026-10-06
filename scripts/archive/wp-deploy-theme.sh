#!/bin/bash
# =============================================================================
# Deploy SkyyRose Flagship Theme to WordPress.com Atomic via SFTP + WP-CLI
# =============================================================================
#
# Syncs theme files AND configures WordPress end-to-end:
#   - SFTP mirror of theme directory
#   - WP-CLI: create pages, assign templates, build menus, set SEO, categories
#
# Usage:
#   ./scripts/wp-deploy-theme.sh                    # Full theme sync
#   ./scripts/wp-deploy-theme.sh --dry-run          # Preview without deploying
#   ./scripts/wp-deploy-theme.sh --file path        # Deploy single file
#   ./scripts/wp-deploy-theme.sh --setup            # Run full WordPress setup (pages, menus, SEO, categories)
#   ./scripts/wp-deploy-theme.sh --setup-pages      # Create/assign pages only
#   ./scripts/wp-deploy-theme.sh --setup-menus      # Create menus + nav only
#   ./scripts/wp-deploy-theme.sh --setup-seo        # Configure SEO settings only
#   ./scripts/wp-deploy-theme.sh --setup-woo        # Configure WooCommerce only
#   ./scripts/wp-deploy-theme.sh --flush-cache      # Flush all caches
#
# Requires:
#   - lftp (brew install lftp) for SFTP
#   - sshpass (brew install sshpass) for WP-CLI over SSH
#   - .env.wordpress with credentials
#
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
THEME_DIR="$PROJECT_ROOT/wordpress-theme/skyyrose-flagship"
ENV_FILE="$PROJECT_ROOT/.env.wordpress"

DRY_RUN=false
SINGLE_FILE=""
ACTION="deploy"  # deploy, setup, setup-pages, setup-menus, setup-seo, setup-woo, flush-cache

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
log_deploy()  { echo -e "${CYAN}[DEPLOY]${NC} $1"; }
log_wp()      { echo -e "${MAGENTA}[WP-CLI]${NC} $1"; }

# Load env
if [[ ! -f "$ENV_FILE" ]]; then
    log_error ".env.wordpress not found at $ENV_FILE"
    exit 1
fi

source "$ENV_FILE"

# Validate SFTP vars
validate_sftp() {
    for var in SFTP_HOST SFTP_PORT SFTP_USER SFTP_PASS WP_THEME_PATH; do
        if [[ -z "${!var:-}" || "${!var}" == "FILL_THIS_IN" ]]; then
            log_error "$var is not set in .env.wordpress"
            exit 1
        fi
    done
}

# Validate SSH/WP-CLI vars
validate_ssh() {
    for var in SSH_HOST SSH_USER SSH_PASS; do
        if [[ -z "${!var:-}" || "${!var}" == "FILL_THIS_IN" ]]; then
            log_error "$var is not set in .env.wordpress (needed for WP-CLI)"
            exit 1
        fi
    done
}

# Run WP-CLI command on remote server
wp_remote() {
    local cmd="$1"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] wp $cmd"
        return 0
    fi
    sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=accept-new "${SSH_USER}@${SSH_HOST}" "wp $cmd" 2>/dev/null
}

# =============================================================================
# SFTP DEPLOY
# =============================================================================

do_deploy() {
    validate_sftp

    if ! command -v lftp &>/dev/null; then
        log_error "lftp not installed. Run: brew install lftp"
        exit 1
    fi

    if [[ ! -d "$THEME_DIR" ]]; then
        log_error "Theme directory not found: $THEME_DIR"
        exit 1
    fi

    echo ""
    echo "=========================================="
    echo "  SKYYROSE THEME DEPLOYMENT (SFTP)"
    echo "=========================================="
    echo ""
    log_info "Host: $SFTP_HOST:$SFTP_PORT"
    log_info "User: $SFTP_USER"
    log_info "Remote: $WP_THEME_PATH"
    log_info "Local:  $THEME_DIR"
    echo ""

    if [[ -n "$SINGLE_FILE" ]]; then
        local_path="$THEME_DIR/$SINGLE_FILE"
        if [[ ! -f "$local_path" ]]; then
            log_error "File not found: $local_path"
            exit 1
        fi
        remote_dir=$(dirname "$WP_THEME_PATH/$SINGLE_FILE")
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY RUN] Would deploy: $SINGLE_FILE"
        else
            log_deploy "Uploading $SINGLE_FILE..."
            lftp -c "
set sftp:auto-confirm yes
set net:max-retries 3
set net:reconnect-interval-base 5
open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST:$SFTP_PORT
mkdir -p $remote_dir
put $local_path -o $WP_THEME_PATH/$SINGLE_FILE
bye
"
            log_success "Deployed: $SINGLE_FILE"
        fi
    else
        EXCLUDE_ARGS=""
        EXCLUDE_ARGS+=" --exclude .DS_Store"
        EXCLUDE_ARGS+=" --exclude .git/"
        EXCLUDE_ARGS+=" --exclude .gitignore"
        EXCLUDE_ARGS+=" --exclude node_modules/"
        EXCLUDE_ARGS+=" --exclude package.json"
        EXCLUDE_ARGS+=" --exclude package-lock.json"
        EXCLUDE_ARGS+=" --exclude *.map"

        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY RUN] Previewing changes..."
            lftp -c "
set sftp:auto-confirm yes
set net:max-retries 3
open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST:$SFTP_PORT
mirror --reverse --dry-run --verbose $EXCLUDE_ARGS \
  $THEME_DIR/ \
  $WP_THEME_PATH/
bye
"
        else
            log_deploy "Syncing full theme..."
            lftp -c "
set sftp:auto-confirm yes
set net:max-retries 3
set net:reconnect-interval-base 5
open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST:$SFTP_PORT
mirror --reverse --verbose --only-newer $EXCLUDE_ARGS \
  $THEME_DIR/ \
  $WP_THEME_PATH/
bye
"
            log_success "Full theme sync complete"
        fi
    fi
}

# =============================================================================
# WORDPRESS SETUP: PAGES
# =============================================================================

do_setup_pages() {
    validate_ssh
    echo ""
    echo "=========================================="
    echo "  CREATING WORDPRESS PAGES + TEMPLATES"
    echo "=========================================="
    echo ""

    if ! command -v sshpass &>/dev/null; then
        log_error "sshpass not installed. Run: brew install sshpass"
        exit 1
    fi

    # Page definitions: "title|slug|template"
    local pages=(
        "Home|home|default"
        "About|about|template-about.php"
        "Black Rose Collection|collection-black-rose|template-collection-black-rose.php"
        "Love Hurts Collection|collection-love-hurts|template-collection-love-hurts.php"
        "Signature Collection|collection-signature|template-collection-signature.php"
        "Kids Capsule|collection-kids-capsule|template-collection-kids-capsule.php"
        "Black Rose Landing|landing-black-rose|template-landing-black-rose.php"
        "Love Hurts Landing|landing-love-hurts|template-landing-love-hurts.php"
        "Signature Landing|landing-signature|template-landing-signature.php"
        "Black Rose Experience|experience-black-rose|template-immersive-black-rose.php"
        "Love Hurts Experience|experience-love-hurts|template-immersive-love-hurts.php"
        "Signature Experience|experience-signature|template-immersive-signature.php"
        "Pre-Order|pre-order|template-preorder-gateway.php"
        "Contact|contact|template-contact.php"
        "Wishlist|wishlist|page-wishlist.php"
        "Style Quiz|style-quiz|template-style-quiz.php"
    )

    for entry in "${pages[@]}"; do
        IFS='|' read -r title slug template <<< "$entry"

        # Check if page exists
        existing=$(wp_remote "post list --post_type=page --name=$slug --format=ids" 2>/dev/null || echo "")

        if [[ -n "$existing" && "$existing" != "0" ]]; then
            log_info "Page exists: $title (ID: $existing) — updating template"
            if [[ "$template" != "default" ]]; then
                wp_remote "post meta update $existing _wp_page_template $template"
            fi
            log_success "Updated: $title → $template"
        else
            log_wp "Creating page: $title (/$slug/)"
            if [[ "$template" == "default" ]]; then
                new_id=$(wp_remote "post create --post_type=page --post_title='$title' --post_name='$slug' --post_status=publish --porcelain" 2>/dev/null || echo "")
            else
                new_id=$(wp_remote "post create --post_type=page --post_title='$title' --post_name='$slug' --post_status=publish --porcelain" 2>/dev/null || echo "")
                if [[ -n "$new_id" ]]; then
                    wp_remote "post meta update $new_id _wp_page_template $template"
                fi
            fi
            if [[ -n "$new_id" ]]; then
                log_success "Created: $title (ID: $new_id) → $template"
            else
                log_warn "Could not create: $title"
            fi
        fi
    done

    # Set static front page
    echo ""
    log_wp "Setting static front page..."
    home_id=$(wp_remote "post list --post_type=page --name=home --format=ids" 2>/dev/null || echo "")
    if [[ -n "$home_id" ]]; then
        wp_remote "option update show_on_front page"
        wp_remote "option update page_on_front $home_id"
        log_success "Static front page set to 'Home' (ID: $home_id)"
    else
        log_warn "Could not find Home page to set as front page"
    fi

    echo ""
    log_success "All pages created/verified"
}

# =============================================================================
# WORDPRESS SETUP: MENUS & NAVIGATION
# =============================================================================

do_setup_menus() {
    validate_ssh
    echo ""
    echo "=========================================="
    echo "  BUILDING NAVIGATION MENUS"
    echo "=========================================="
    echo ""

    # ---------- PRIMARY NAVIGATION ----------
    log_wp "Creating Primary Navigation menu..."
    existing_menu=$(wp_remote "menu list --format=ids" 2>/dev/null | tr ' ' '\n' | head -1 || echo "")

    # Delete existing menus and recreate (cleanest approach)
    wp_remote "menu delete 'Primary Navigation'" 2>/dev/null || true
    wp_remote "menu create 'Primary Navigation'"

    wp_remote "menu item add-custom 'Primary Navigation' 'Home' '/' --porcelain"
    # Collections dropdown parent
    collections_id=$(wp_remote "menu item add-custom 'Primary Navigation' 'Collections' '#' --porcelain" 2>/dev/null || echo "")
    if [[ -n "$collections_id" ]]; then
        wp_remote "menu item add-custom 'Primary Navigation' 'Black Rose' '/collection-black-rose/' --parent-id=$collections_id --porcelain"
        wp_remote "menu item add-custom 'Primary Navigation' 'Love Hurts' '/collection-love-hurts/' --parent-id=$collections_id --porcelain"
        wp_remote "menu item add-custom 'Primary Navigation' 'Signature' '/collection-signature/' --parent-id=$collections_id --porcelain"
        wp_remote "menu item add-custom 'Primary Navigation' 'Kids Capsule' '/collection-kids-capsule/' --parent-id=$collections_id --porcelain"
    fi
    wp_remote "menu item add-custom 'Primary Navigation' 'About' '/about/' --porcelain"
    wp_remote "menu item add-custom 'Primary Navigation' 'Pre-Order' '/pre-order/' --porcelain"

    wp_remote "menu location assign 'Primary Navigation' primary"
    log_success "Primary Navigation: Home | Collections ▼ | About | Pre-Order"

    # ---------- FOOTER NAVIGATION ----------
    log_wp "Creating Footer Navigation menu..."
    wp_remote "menu delete 'Footer Navigation'" 2>/dev/null || true
    wp_remote "menu create 'Footer Navigation'"

    wp_remote "menu item add-custom 'Footer Navigation' 'Shop' '/pre-order/' --porcelain"
    wp_remote "menu item add-custom 'Footer Navigation' 'Collections' '/collection-black-rose/' --porcelain"
    wp_remote "menu item add-custom 'Footer Navigation' 'About' '/about/' --porcelain"
    wp_remote "menu item add-custom 'Footer Navigation' 'Contact' '/contact/' --porcelain"
    wp_remote "menu item add-custom 'Footer Navigation' 'FAQ' '/about/#faq' --porcelain"
    wp_remote "menu item add-custom 'Footer Navigation' 'Privacy Policy' '/privacy-policy/' --porcelain"
    wp_remote "menu item add-custom 'Footer Navigation' 'Terms of Service' '/terms-of-service/' --porcelain"

    wp_remote "menu location assign 'Footer Navigation' footer"
    log_success "Footer Navigation: Shop | Collections | About | Contact | FAQ | Privacy | Terms"

    # ---------- COLLECTION NAVIGATION ----------
    log_wp "Creating Collection Navigation menu..."
    wp_remote "menu delete 'Collection Navigation'" 2>/dev/null || true
    wp_remote "menu create 'Collection Navigation'"

    wp_remote "menu item add-custom 'Collection Navigation' 'Black Rose' '/collection-black-rose/' --porcelain"
    wp_remote "menu item add-custom 'Collection Navigation' 'Love Hurts' '/collection-love-hurts/' --porcelain"
    wp_remote "menu item add-custom 'Collection Navigation' 'Signature' '/collection-signature/' --porcelain"

    wp_remote "menu location assign 'Collection Navigation' collection"
    log_success "Collection Navigation: Black Rose | Love Hurts | Signature"

    echo ""
    log_success "All menus created and assigned to theme locations"
}

# =============================================================================
# WORDPRESS SETUP: SEO & SITE SETTINGS
# =============================================================================

do_setup_seo() {
    validate_ssh
    echo ""
    echo "=========================================="
    echo "  CONFIGURING SEO & SITE SETTINGS"
    echo "=========================================="
    echo ""

    # Site identity
    log_wp "Setting site identity..."
    wp_remote "option update blogname 'SkyyRose — Oakland Luxury Streetwear'"
    wp_remote "option update blogdescription 'Premium streetwear from Oakland, CA.'"
    log_success "Site title + tagline set"

    # Permalinks
    log_wp "Setting permalink structure..."
    wp_remote "rewrite structure '/%postname%/'"
    wp_remote "rewrite flush"
    log_success "Permalinks: /%postname%/"

    # Timezone
    log_wp "Setting timezone..."
    wp_remote "option update timezone_string 'America/Los_Angeles'"
    wp_remote "option update date_format 'F j, Y'"
    wp_remote "option update time_format 'g:i a'"
    log_success "Timezone: America/Los_Angeles"

    # Reading settings
    log_wp "Setting reading configuration..."
    wp_remote "option update show_on_front 'page'"
    wp_remote "option update posts_per_page 12"
    wp_remote "option update blog_public 1"
    log_success "Reading: static front page, 12 posts/page, public"

    # Discussion settings (reduce spam surface)
    log_wp "Setting discussion defaults..."
    wp_remote "option update default_pingback_flag ''"
    wp_remote "option update default_ping_status 'closed'"
    wp_remote "option update default_comment_status 'closed'"
    log_success "Discussion: pingbacks off, comments off by default"

    echo ""
    log_success "SEO & site settings configured"
}

# =============================================================================
# WORDPRESS SETUP: WOOCOMMERCE CATEGORIES + SETTINGS
# =============================================================================

do_setup_woo() {
    validate_ssh
    echo ""
    echo "=========================================="
    echo "  CONFIGURING WOOCOMMERCE"
    echo "=========================================="
    echo ""

    # Product categories
    log_wp "Creating product categories..."
    local categories=(
        "Black Rose|black-rose|Gothic luxury streetwear collection — Silver"
        "Love Hurts|love-hurts|Passionate crimson collection — Crimson"
        "Signature|signature|Bay Area gold essentials — Gold"
        "Kids Capsule|kids-capsule|Youth collection"
    )

    for entry in "${categories[@]}"; do
        IFS='|' read -r name slug desc <<< "$entry"
        existing=$(wp_remote "term list product_cat --slug=$slug --format=ids" 2>/dev/null || echo "")
        if [[ -n "$existing" && "$existing" != "0" ]]; then
            log_info "Category exists: $name (ID: $existing)"
        else
            wp_remote "term create product_cat '$name' --slug='$slug' --description='$desc'" 2>/dev/null || true
            log_success "Created category: $name (/$slug/)"
        fi
    done

    # WooCommerce page assignments
    echo ""
    log_wp "Setting WooCommerce page assignments..."

    cart_id=$(wp_remote "post list --post_type=page --name=cart --format=ids" 2>/dev/null || echo "")
    checkout_id=$(wp_remote "post list --post_type=page --name=checkout --format=ids" 2>/dev/null || echo "")
    account_id=$(wp_remote "post list --post_type=page --name=my-account --format=ids" 2>/dev/null || echo "")
    shop_id=$(wp_remote "post list --post_type=page --name=pre-order --format=ids" 2>/dev/null || echo "")

    # Create missing WooCommerce pages
    if [[ -z "$cart_id" ]]; then
        cart_id=$(wp_remote "post create --post_type=page --post_title='Cart' --post_name='cart' --post_status=publish --post_content='[woocommerce_cart]' --porcelain" 2>/dev/null || echo "")
        log_success "Created Cart page (ID: $cart_id)"
    fi
    if [[ -z "$checkout_id" ]]; then
        checkout_id=$(wp_remote "post create --post_type=page --post_title='Checkout' --post_name='checkout' --post_status=publish --post_content='[woocommerce_checkout]' --porcelain" 2>/dev/null || echo "")
        log_success "Created Checkout page (ID: $checkout_id)"
    fi
    if [[ -z "$account_id" ]]; then
        account_id=$(wp_remote "post create --post_type=page --post_title='My Account' --post_name='my-account' --post_status=publish --post_content='[woocommerce_my_account]' --porcelain" 2>/dev/null || echo "")
        log_success "Created My Account page (ID: $account_id)"
    fi

    # Assign pages to WooCommerce settings
    [[ -n "$cart_id" ]] && wp_remote "option update woocommerce_cart_page_id $cart_id"
    [[ -n "$checkout_id" ]] && wp_remote "option update woocommerce_checkout_page_id $checkout_id"
    [[ -n "$account_id" ]] && wp_remote "option update woocommerce_myaccount_page_id $account_id"
    [[ -n "$shop_id" ]] && wp_remote "option update woocommerce_shop_page_id $shop_id"
    log_success "WooCommerce pages assigned"

    # WooCommerce settings
    echo ""
    log_wp "Setting WooCommerce configuration..."
    wp_remote "option update woocommerce_currency 'USD'"
    wp_remote "option update woocommerce_enable_guest_checkout 'yes'"
    wp_remote "option update woocommerce_manage_stock 'yes'"
    wp_remote "option update woocommerce_thumbnail_cropping '3:4'"
    wp_remote "option update woocommerce_single_image_width 600"
    wp_remote "option update woocommerce_thumbnail_image_width 300"
    log_success "WooCommerce: USD, guest checkout, stock management, 3:4 thumbnails"

    echo ""
    log_success "WooCommerce configuration complete"
}

# =============================================================================
# FLUSH CACHES
# =============================================================================

do_flush_cache() {
    validate_ssh
    echo ""
    log_wp "Flushing all caches..."
    wp_remote "cache flush" 2>/dev/null && log_success "Object cache flushed" || log_warn "Object cache flush skipped"
    wp_remote "transient delete --all" 2>/dev/null && log_success "Transients cleared" || log_warn "Transient clear skipped"
    wp_remote "rewrite flush" 2>/dev/null && log_success "Permalinks flushed" || log_warn "Permalink flush skipped"
    echo ""
    log_success "All caches flushed"
}

# =============================================================================
# FULL SETUP (runs everything)
# =============================================================================

do_full_setup() {
    do_setup_pages
    do_setup_menus
    do_setup_seo
    do_setup_woo
    do_flush_cache
    echo ""
    echo "=========================================="
    log_success "FULL WORDPRESS SETUP COMPLETE"
    echo ""
    echo "  Pages:       16 pages created/verified with templates"
    echo "  Menus:       Primary + Footer + Collection navigation"
    echo "  SEO:         Title, tagline, permalinks, timezone"
    echo "  WooCommerce: Categories, pages, currency, stock mgmt"
    echo "  Cache:       All caches flushed"
    echo ""
    echo "  Next: Deploy theme files with: $0"
    echo "  Then: Visit https://skyyrose.co to verify"
    echo "=========================================="
}

# =============================================================================
# CLI ARGUMENT PARSING
# =============================================================================

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --file)
            SINGLE_FILE="$2"
            shift 2
            ;;
        --setup)
            ACTION="setup"
            shift
            ;;
        --setup-pages)
            ACTION="setup-pages"
            shift
            ;;
        --setup-menus)
            ACTION="setup-menus"
            shift
            ;;
        --setup-seo)
            ACTION="setup-seo"
            shift
            ;;
        --setup-woo)
            ACTION="setup-woo"
            shift
            ;;
        --flush-cache)
            ACTION="flush-cache"
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Deploy Options:"
            echo "  (no flags)        Full theme SFTP sync"
            echo "  --file PATH       Deploy single file (relative to theme dir)"
            echo "  --dry-run         Preview without deploying"
            echo ""
            echo "WordPress Setup Options:"
            echo "  --setup           Run FULL end-to-end WordPress setup"
            echo "  --setup-pages     Create pages + assign templates"
            echo "  --setup-menus     Build navigation menus"
            echo "  --setup-seo       Configure SEO + site settings"
            echo "  --setup-woo       Configure WooCommerce (categories, pages, settings)"
            echo "  --flush-cache     Flush all WordPress caches"
            echo ""
            echo "Credentials: .env.wordpress (SSH_HOST, SSH_USER, SSH_PASS, SFTP_*)"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1. Use --help for usage."
            exit 1
            ;;
    esac
done

# =============================================================================
# EXECUTE
# =============================================================================

case "$ACTION" in
    deploy)
        do_deploy
        ;;
    setup)
        do_full_setup
        ;;
    setup-pages)
        do_setup_pages
        ;;
    setup-menus)
        do_setup_menus
        ;;
    setup-seo)
        do_setup_seo
        ;;
    setup-woo)
        do_setup_woo
        ;;
    flush-cache)
        do_flush_cache
        ;;
esac

echo ""
if [[ "$DRY_RUN" == "true" ]]; then
    log_info "DRY RUN — no changes made"
else
    log_info "Site: https://skyyrose.co"
fi
echo ""
