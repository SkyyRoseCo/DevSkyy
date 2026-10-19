<?php
/**
 * WooCommerce Integration
 *
 * Hooks, overrides, and customizations for WooCommerce product display,
 * cart fragments, gallery thumbnails, and related products.
 *
 * @package SkyyRose
 * @since   1.0.0
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/*
--------------------------------------------------------------
 * Constants
 *--------------------------------------------------------------*/

/**
 * Free shipping order threshold in dollars.
 * Change this one value to update all cart and policy displays site-wide.
 *
 * @since 1.1.0
 */
if ( ! defined( 'SKYYROSE_FREE_SHIPPING_THRESHOLD' ) ) {
	define( 'SKYYROSE_FREE_SHIPPING_THRESHOLD', 200 );
}

/*
--------------------------------------------------------------
 * WooCommerce Support Declaration
 *--------------------------------------------------------------*/

/**
 * Declare WooCommerce support and gallery features.
 *
 * @since 1.0.0
 * @return void
 */
function skyyrose_woocommerce_support() {
	add_theme_support( 'woocommerce' );
	add_theme_support( 'wc-product-gallery-zoom' );
	add_theme_support( 'wc-product-gallery-lightbox' );
	add_theme_support( 'wc-product-gallery-slider' );
}
add_action( 'after_setup_theme', 'skyyrose_woocommerce_support' );

/*
--------------------------------------------------------------
 * Product Grid Layout
 *--------------------------------------------------------------*/

/**
 * Set product loop columns: 4 on desktop.
 * CSS media queries handle mobile (2 columns) via the theme stylesheet.
 *
 * @since  3.0.0
 * @return int Number of columns.
 */
function skyyrose_woocommerce_loop_columns() {
	return 4;
}
// loop_shop_columns handled by skyyrose_editorial_shop_columns() in inc/fashion-chrome.php (3-col editorial grid).

/**
 * Set products per page (multiple of column count for even grids).
 *
 * @since  1.0.0
 * @return int Number of products per page.
 */
function skyyrose_woocommerce_products_per_page() {
	return 12;
}
add_filter( 'loop_shop_per_page', 'skyyrose_woocommerce_products_per_page' );

/*
--------------------------------------------------------------
 * Sidebar Removal
 *--------------------------------------------------------------*/

// Remove the default WooCommerce sidebar entirely.
remove_action( 'woocommerce_sidebar', 'woocommerce_get_sidebar', 10 );

/*
--------------------------------------------------------------
 * Content Wrappers
 *--------------------------------------------------------------*/

/**
 * Open the main content wrapper before WooCommerce output.
 *
 * @since 1.0.0
 * @return void
 */
function skyyrose_woocommerce_wrapper_before() {
	echo '<div id="primary" class="content-area"><main id="main" class="site-main" role="main">';
}
add_action( 'woocommerce_before_main_content', 'skyyrose_woocommerce_wrapper_before' );

/**
 * Close the main content wrapper after WooCommerce output.
 *
 * @since 1.0.0
 * @return void
 */
function skyyrose_woocommerce_wrapper_after() {
	echo '</main></div>';
}
add_action( 'woocommerce_after_main_content', 'skyyrose_woocommerce_wrapper_after' );

/*
--------------------------------------------------------------
 * Breadcrumb Override
 *--------------------------------------------------------------*/

// Remove default WooCommerce breadcrumbs (theme uses its own).
remove_action( 'woocommerce_before_main_content', 'woocommerce_breadcrumb', 20 );

/*
--------------------------------------------------------------
 * Product Gallery Thumbnails
 *--------------------------------------------------------------*/

/**
 * Custom product gallery thumbnail size (3:4 ratio matching product-card).
 *
 * @since  3.0.0
 * @return array Width, height, and crop settings.
 */
function skyyrose_woocommerce_gallery_thumbnail_size() {
	return array(
		'width'  => 150,
		'height' => 200,
		'crop'   => 1,
	);
}
add_filter( 'woocommerce_get_image_size_gallery_thumbnail', 'skyyrose_woocommerce_gallery_thumbnail_size' );

/**
 * Custom single product image size.
 *
 * @since  3.0.0
 * @return array Width, height, and crop settings.
 */
function skyyrose_woocommerce_single_image_size() {
	return array(
		'width'  => 800,
		'height' => 1066,
		'crop'   => 1,
	);
}
add_filter( 'woocommerce_get_image_size_single', 'skyyrose_woocommerce_single_image_size' );

/**
 * Custom product catalog thumbnail size (3:4 ratio).
 *
 * @since  3.0.0
 * @return array Width, height, and crop settings.
 */
function skyyrose_woocommerce_thumbnail_size() {
	return array(
		'width'  => 400,
		'height' => 533,
		'crop'   => 1,
	);
}
add_filter( 'woocommerce_get_image_size_thumbnail', 'skyyrose_woocommerce_thumbnail_size' );

/*
--------------------------------------------------------------
 * AJAX Cart Fragments
 *--------------------------------------------------------------*/

/**
 * Update the header cart count badge via AJAX after add-to-cart.
 *
 * Replaces the .cart-count span with the current item count so the
 * header cart icon stays in sync without a full page reload.
 *
 * @since  1.0.0
 *
 * @param  array $fragments Existing fragments keyed by CSS selector.
 * @return array Updated fragments.
 */
function skyyrose_woocommerce_cart_fragments( $fragments ) {

	$cart = WC()->cart;
	if ( ! $cart instanceof WC_Cart ) {
		return $fragments;
	}

	$count = $cart->get_cart_contents_count();

	ob_start();
	?>
	<span class="cart-count<?php echo esc_attr( $count > 0 ? ' has-items' : '' ); ?>"><?php echo wp_kses_data( (string) $count ); ?></span>
	<?php
	$fragments['.cart-count'] = ob_get_clean();

	// Also provide the cart subtotal for mini-cart widgets.
	ob_start();
	?>
	<span class="cart-subtotal"><?php echo wp_kses_post( $cart->get_cart_subtotal() ); ?></span>
	<?php
	$fragments['.cart-subtotal'] = ob_get_clean();

	return $fragments;
}
add_filter( 'woocommerce_add_to_cart_fragments', 'skyyrose_woocommerce_cart_fragments' );

/*
--------------------------------------------------------------
 * Related Products
 *--------------------------------------------------------------*/

/**
 * Override related products display: 4 products in a 4-column grid.
 *
 * @since  1.0.0
 *
 * @param  array $args Default related products args.
 * @return array Modified args.
 */
function skyyrose_woocommerce_related_products_args( $args ) {
	return array_merge(
		$args,
		array(
			'posts_per_page' => 4,
			'columns'        => 4,
		)
	);
}
add_filter( 'woocommerce_output_related_products_args', 'skyyrose_woocommerce_related_products_args' );

/**
 * Disable the related-products block on single product pages (H4 launch decision).
 *
 * Removes the default WooCommerce action that outputs related products under
 * the summary. Keeps the args filter above intact so the block can be re-enabled
 * by deleting this remove_action call alone.
 *
 * @since 1.4.0
 * @return void
 */
function skyyrose_disable_related_products() {
	remove_action( 'woocommerce_after_single_product_summary', 'woocommerce_output_related_products', 20 );
}
// Hook on `wp` (after all plugins have bootstrapped) so the remove_action
// fires AFTER WooCommerce has registered the action. Hooking on `init`
// worked in practice but relied on ordering assumptions — `wp` is the
// canonical safe choice for conditional remove_action on WC template hooks.
add_action( 'wp', 'skyyrose_disable_related_products' );

/*
--------------------------------------------------------------
 * Cross-Sells
 *--------------------------------------------------------------*/

/**
 * Limit cross-sell products on the cart page to 4 in a 4-column grid.
 *
 * @since  3.0.0
 *
 * @param  int $columns Default column count.
 * @return int Column count.
 */
function skyyrose_woocommerce_cross_sells_columns( $columns ) {
	return 4;
}
add_filter( 'woocommerce_cross_sells_columns', 'skyyrose_woocommerce_cross_sells_columns' );

/**
 * Limit cross-sell products count.
 *
 * @since  3.0.0
 *
 * @param  int $limit Default limit.
 * @return int Product limit.
 */
function skyyrose_woocommerce_cross_sells_total( $limit ) {
	return 4;
}
add_filter( 'woocommerce_cross_sells_total', 'skyyrose_woocommerce_cross_sells_total' );

/*
--------------------------------------------------------------
 * WooCommerce Script Localization
 *--------------------------------------------------------------*/

/**
 * Localize WooCommerce scripts with AJAX data and nonces.
 *
 * @since 1.0.0
 * @return void
 */
function skyyrose_woocommerce_localize_scripts() {

	if ( ! wp_script_is( 'skyyrose-template-woocommerce', 'enqueued' ) ) {
		return;
	}

	if ( ! function_exists( 'wc_get_cart_url' ) ) {
		return;
	}

	wp_localize_script(
		'skyyrose-template-woocommerce',
		'skyyRoseWoo',
		array(
			'ajaxUrl'         => admin_url( 'admin-ajax.php' ),
			'nonce'           => wp_create_nonce( 'skyyrose-woo-nonce' ),
			'cartUrl'         => wc_get_cart_url(),
			'checkoutUrl'     => wc_get_checkout_url(),
			'addedToCartText' => esc_html__( 'Added to cart', 'skyyrose' ),
			'currency'        => get_woocommerce_currency_symbol(),
		)
	);
}
add_action( 'wp_enqueue_scripts', 'skyyrose_woocommerce_localize_scripts', 25 );

/*
--------------------------------------------------------------
 * Pagination
 *--------------------------------------------------------------*/

/**
 * Customize WooCommerce pagination text.
 *
 * @since  1.0.0
 *
 * @param  array $args Default pagination arguments.
 * @return array Modified arguments.
 */
function skyyrose_woocommerce_pagination_args( $args ) {
	return array_merge(
		$args,
		array(
			'prev_text' => esc_html__( 'Previous', 'skyyrose' ),
			'next_text' => esc_html__( 'Next', 'skyyrose' ),
		)
	);
}
add_filter( 'woocommerce_pagination_args', 'skyyrose_woocommerce_pagination_args' );

/*
--------------------------------------------------------------
 * 3D Model Viewer (Product Meta Box)
 *--------------------------------------------------------------*/

/**
 * Display 3D model viewer button on single product pages.
 *
 * Printed by woocommerce/single-product.php inside the gallery column (that
 * template does not run woocommerce_single_product_summary); the hook below
 * covers any product view that still does (WooCommerce core's
 * content-single-product.php, [product_page] shortcode). The viewer script is
 * enqueued here, right before printing, so it follows the button wherever it
 * renders — a button without its script is dead UI. Prints at most once per
 * request. URL policy + enqueue live in inc/product-3d-model.php.
 *
 * @since 1.0.0
 * @return void
 */
function skyyrose_woocommerce_3d_model_button() {
	static $printed = false;

	if ( $printed ) {
		return;
	}

	$model_file = skyyrose_get_product_3d_model_url( get_the_ID() );

	if ( '' === $model_file || ! skyyrose_enqueue_product_3d_viewer() ) {
		return;
	}

	$printed = true;
	printf(
		'<div class="product-3d-viewer"><button type="button" class="button view-3d-model" data-model="%s" data-product-name="%s">%s</button></div>',
		esc_url( $model_file ),
		esc_attr( get_the_title() ),
		esc_html__( 'View in 3D', 'skyyrose' )
	);
}
add_action( 'woocommerce_single_product_summary', 'skyyrose_woocommerce_3d_model_button', 25 );

/**
 * Register the 3D model meta box on product edit screens.
 *
 * @since 1.0.0
 * @return void
 */
function skyyrose_add_product_meta_box() {
	add_meta_box(
		'skyyrose_product_3d_model',
		esc_html__( '3D Model', 'skyyrose' ),
		'skyyrose_product_3d_model_callback',
		'product',
		'side',
		'default'
	);
}
add_action( 'add_meta_boxes', 'skyyrose_add_product_meta_box' );

/**
 * Render the 3D model meta box UI.
 *
 * @since 1.0.0
 *
 * @param WP_Post $post Current post object.
 * @return void
 */
function skyyrose_product_3d_model_callback( $post ) {

	wp_nonce_field( 'skyyrose_product_3d_model_nonce', 'skyyrose_product_3d_model_nonce' );

	$value = get_post_meta( $post->ID, '_product_3d_model', true );
	?>
	<p>
		<label for="skyyrose_product_3d_model">
			<?php esc_html_e( '3D Model File URL (GLB/GLTF)', 'skyyrose' ); ?>
		</label>
		<?php // type="text", not "url": browser constraint validation rejects the site-relative form this field documents. Server-side validation is skyyrose_sanitize_3d_model_url(). ?>
		<input
			type="text"
			id="skyyrose_product_3d_model"
			name="skyyrose_product_3d_model"
			value="<?php echo esc_url( $value ); ?>"
			style="width: 100%;"
			spellcheck="false"
		/>
	</p>
	<p class="description">
		<?php esc_html_e( 'Same-site path (/wp-content/…/model.glb) or https URL ending in .glb or .gltf. Anything else is discarded on save.', 'skyyrose' ); ?>
	</p>
	<?php
}

/**
 * Save 3D model meta box data.
 *
 * @since 1.0.0
 *
 * @param int $post_id Post ID.
 * @return void
 */
function skyyrose_save_product_3d_model( $post_id ) {

	// Verify nonce.
	if ( ! isset( $_POST['skyyrose_product_3d_model_nonce'] ) ) {
		return;
	}

	if ( ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['skyyrose_product_3d_model_nonce'] ) ), 'skyyrose_product_3d_model_nonce' ) ) {
		return;
	}

	// Bail on autosave.
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
		return;
	}

	// Check capabilities.
	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}

	if ( isset( $_POST['skyyrose_product_3d_model'] ) ) {
		$url = skyyrose_sanitize_3d_model_url( sanitize_text_field( wp_unslash( $_POST['skyyrose_product_3d_model'] ) ) );
		if ( '' === $url ) {
			delete_post_meta( $post_id, '_product_3d_model' );
		} else {
			update_post_meta( $post_id, '_product_3d_model', $url );
		}
	}
}
add_action( 'save_post_product', 'skyyrose_save_product_3d_model' );

/*
--------------------------------------------------------------
 * Product Search Form
 *--------------------------------------------------------------*/

/**
 * Custom product search form markup.
 *
 * @since  1.0.0
 * @return string Search form HTML.
 */
function skyyrose_product_search_form() {
	ob_start();
	?>
	<form role="search" method="get" class="woocommerce-product-search" action="<?php echo esc_url( home_url( '/' ) ); ?>">
		<label class="screen-reader-text" for="woocommerce-product-search-field">
			<?php esc_html_e( 'Search for:', 'skyyrose' ); ?>
		</label>
		<input
			type="search"
			id="woocommerce-product-search-field"
			class="search-field"
			placeholder="<?php echo esc_attr__( 'Search products&hellip;', 'skyyrose' ); ?>"
			value="<?php echo esc_attr( get_search_query() ); ?>"
			name="s"
		/>
		<button type="submit" value="<?php echo esc_attr_x( 'Search', 'submit button', 'skyyrose' ); ?>">
			<?php echo esc_html_x( 'Search', 'submit button', 'skyyrose' ); ?>
		</button>
		<input type="hidden" name="post_type" value="product" />
	</form>
	<?php
	return ob_get_clean();
}

/*
--------------------------------------------------------------
 * AJAX Cart Count Handler
 *--------------------------------------------------------------*/

/**
 * Return the current cart item count via AJAX.
 *
 * Called from woocommerce.js after add-to-cart and cart updates
 * to keep the header cart badge in sync.
 *
 * @since  3.0.0
 * @return void
 */
function skyyrose_ajax_get_cart_count() {

	check_ajax_referer( 'skyyrose-woo-nonce', 'nonce' );

	$cart  = WC()->cart;
	$count = $cart instanceof WC_Cart ? $cart->get_cart_contents_count() : 0;

	wp_send_json_success(
		array(
			'count' => $count,
		)
	);
}
add_action( 'wp_ajax_skyyrose_get_cart_count', 'skyyrose_ajax_get_cart_count' );
add_action( 'wp_ajax_nopriv_skyyrose_get_cart_count', 'skyyrose_ajax_get_cart_count' );

/*
--------------------------------------------------------------
 * Complete the Look — single product cross-sell
 *--------------------------------------------------------------*/

/*
 * "Complete the Look" cross-sell removed 2026-05-27 per founder canon: no
 * related products on PDP, garment is the protagonist. Template part,
 * enqueue, and similarity-fallback wiring removed in the same commit.
 */

/*
Pre-order meta, notices, pricing, and referral credit logic moved to
	inc/woocommerce-preorder.php in v6.3.0 for maintainability. */

/**
 * Inject product collection data on WooCommerce native loop items.
 *
 * Outputs a hidden element with data-product-id, data-collection, and
 * data-name on shop/archive pages that don't use the holo card template,
 * so experience-analyzer.js and smart-showcase.js can identify products.
 *
 * Part of the Experience Engine, Phase 3.
 */
function skyyrose_wc_inject_product_attrs(): void {
	$product_id = get_the_ID();
	if ( ! $product_id ) {
		return;
	}

	$collection = function_exists( 'skyyrose_get_product_collection' )
		? skyyrose_get_product_collection( $product_id )
		: '';

	$product = wc_get_product( $product_id );
	$name    = $product ? $product->get_name() : '';

	printf(
		'<div class="skyy-product-meta" hidden data-product-id="%s" data-collection="%s" data-name="%s"></div>',
		esc_attr( (string) $product_id ),
		esc_attr( $collection ),
		esc_attr( $name )
	);
}
add_action( 'woocommerce_before_shop_loop_item_title', 'skyyrose_wc_inject_product_attrs', 5 );

/**
 * Substitute the catalog ghost-mannequin render for WooCommerce products that
 * have no featured image set, so the classic /shop loop (and any get_image()
 * consumer) shows the garment instead of the generic WooCommerce placeholder.
 *
 * Guarded to act ONLY when the product has no featured image — never overrides
 * a real featured photo the founder uploaded. Skips wp-admin so the media
 * library and product-edit thumbnails stay intact. Ghost-first (front_model_image),
 * byte-parity with skyyrose_catalog_to_static_card() and the holo-card fallback.
 *
 * @since 6.7.0
 *
 * @param  string     $html    Existing image HTML (placeholder when no featured image).
 * @param  WC_Product $product Product being rendered.
 * @param  mixed      $size    Requested image size (unused — render is fixed-size).
 * @return string               Ghost render markup when available, else original $html.
 */
function skyyrose_wc_ghost_loop_image( $html, $product, $size ) {
	unset( $size );
	if ( is_admin() ) {
		return $html;
	}
	if ( $product->get_image_id() ) {
		return $html; // Real featured image exists — leave it untouched.
	}
	if ( ! function_exists( 'skyyrose_get_product' )
		|| ! function_exists( 'skyyrose_normalize_sku' )
		|| ! function_exists( 'skyyrose_product_image_uri' ) ) {
		return $html;
	}
	$sku = $product->get_sku();
	if ( '' === $sku ) {
		return $html;
	}
	$catalog_product = skyyrose_get_product( skyyrose_normalize_sku( $sku ) );
	if ( ! $catalog_product ) {
		return $html;
	}
	$render = ( $catalog_product['front_model_image'] ?? '' ) ?: ( $catalog_product['image'] ?? '' );
	if ( '' === $render ) {
		return $html;
	}
	$url = skyyrose_product_image_uri( $render );
	if ( '' === $url ) {
		return $html;
	}
	return sprintf(
		'<img src="%s" alt="%s" class="skyy-ghost-loop-img" loading="lazy" decoding="async" />',
		esc_url( $url ),
		esc_attr( $product->get_name() )
	);
}
add_filter( 'woocommerce_product_get_image', 'skyyrose_wc_ghost_loop_image', 10, 3 );

/*
--------------------------------------------------------------
 * WC 9.9 Product Collection Filters
 *--------------------------------------------------------------*/

/**
 * Set collection-aware default filter presets for WC 9.9 product filters.
 *
 * When viewing a collection page, pre-selects the matching product
 * category so filters are scoped to the current collection.
 *
 * @since 6.6.0
 *
 * @param  array $args Default filter arguments.
 * @return array Modified arguments with collection preset.
 */
function skyyrose_product_filter_defaults( $args ) {
	if ( ! is_page() || ! function_exists( 'skyyrose_get_collections_config' ) ) {
		return $args;
	}

	$template = get_page_template_slug();
	if ( empty( $template ) ) {
		return $args;
	}

	// Map template slugs to collection slugs.
	$collections = skyyrose_get_collections_config();
	foreach ( $collections as $slug => $config ) {
		$template_name = 'template-collection-' . $slug . '.php';
		if ( $template === $template_name ) {
			// Pre-select collection category in product filters.
			$term = get_term_by( 'slug', $slug, 'product_cat' );
			if ( $term ) {
				$args['product_cat'] = $term->term_id;
			}

			// Set collection-specific sort order.
			if ( ! empty( $config['palette'] ) ) {
				$args['collection_slug']  = $slug;
				$args['collection_label'] = $config['label'];
			}
			break;
		}
	}

	return $args;
}
add_filter( 'woocommerce_product_filters_default_args', 'skyyrose_product_filter_defaults' );

/**
 * Render the My Account UI when the page content does not.
 *
 * Live page 9710 (/my-account/) holds only the placeholder paragraph "This page
 * uses the SkyyRose Flagship theme template. Content is rendered by the theme."
 * — no [woocommerce_my_account] shortcode, no block equivalent, and the theme
 * ships no woocommerce/myaccount/ override. Verified against production 2026-07-27:
 * logged out OR in, visitors got no login form, no orders, no addresses. The page
 * content explicitly delegates rendering to the theme, so the theme must render it.
 *
 * Runs at priority 9 — BEFORE core's do_shortcode() at 11 — so the returned
 * shortcode is expanded normally by the existing filter chain. Idempotent: if the
 * content ever gains the shortcode (or a block equivalent) this yields to it, so
 * a later content fix does not double-render.
 *
 * Zero production DB writes, matching the template_include remedies in
 * inc/redirects.php used for the stale-meta Collections/Cart/Checkout pages.
 *
 * @since 1.12.9
 * @param string $content Post content.
 * @return string
 */
function skyyrose_account_content_fallback( $content ) {
	if ( ! function_exists( 'is_account_page' ) || ! is_account_page() ) {
		return $content;
	}

	// Only the main page body — never excerpts, widgets, or secondary loops.
	if ( ! in_the_loop() || ! is_main_query() ) {
		return $content;
	}

	// Already renders the account UI (shortcode or WC block) — leave it alone.
	if ( has_shortcode( $content, 'woocommerce_my_account' )
		|| has_block( 'woocommerce/customer-account', $content ) ) {
		return $content;
	}

	return '[woocommerce_my_account]';
}
add_filter( 'the_content', 'skyyrose_account_content_fallback', 9 );

/*
--------------------------------------------------------------
 * Cart "Wears With" Cross-Sell Helper
 *--------------------------------------------------------------*/

/**
 * Suggest a single cross-sell product for the cart page.
 *
 * Counts collections among cart SKUs, picks the dominant collection,
 * and returns the first published product from that collection that
 * is NOT already in the cart.
 *
 * @since 7.2.0
 *
 * @param  array $cart_skus Array of SKUs currently in the cart.
 * @return array|null       Single product array from the catalog, or null.
 */
function skyyrose_get_cart_wears_with( $cart_skus ) {
	if ( empty( $cart_skus ) || ! function_exists( 'skyyrose_get_product' ) ) {
		return null;
	}

	// Tally collections.
	$counts = array();
	foreach ( $cart_skus as $sku ) {
		$product = skyyrose_get_product( $sku );
		if ( $product && ! empty( $product['collection'] ) ) {
			$col            = $product['collection'];
			$counts[ $col ] = ( $counts[ $col ] ?? 0 ) + 1;
		}
	}

	if ( empty( $counts ) ) {
		return null;
	}

	// Pick dominant collection.
	arsort( $counts );
	$dominant = array_key_first( $counts );

	// Find first published product not already in cart.
	$collection_products = function_exists( 'skyyrose_get_collection_products' )
		? skyyrose_get_collection_products( $dominant )
		: array();

	foreach ( $collection_products as $product ) {
		if ( ! $product['published'] ) {
			continue;
		}
		if ( in_array( $product['sku'], $cart_skus, true ) ) {
			continue;
		}
		return $product;
	}

	return null;
}

/*
Pre-order meta, notices, pricing, and referral credit logic moved to
	inc/woocommerce-preorder.php in v6.3.0 for maintainability. */
