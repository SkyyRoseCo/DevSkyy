<?php
/** Exercise the theme's actual asset enqueue function on custom commerce pages. */

define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_URI', 'https://theme.invalid' );

class WooCommerce {}

$GLOBALS['route'] = array();
$GLOBALS['enqueued_scripts'] = array();
$GLOBALS['enqueued_styles'] = array();

function skyyrose2_asset_suffix() { return ''; }
function skyyrose2_asset_version( $path ) { return 'test-version'; }
function skyyrose2_collection_page_slug() { return $GLOBALS['route']['collection'] ?? ''; }
function skyyrose2_collection_world_enabled( $slug ) { return 'black-rose' === $slug; }
function skyyrose2_hero_bootstrap_inline() { return false; }
function skyyrose2_mascot_enabled() { return false; }
function is_front_page() { return false; }
function is_product() { return false; }
function is_shop() { return false; }
function is_product_taxonomy() { return false; }
function is_cart() { return false; }
function is_checkout() { return false; }
function is_account_page() { return false; }
function is_woocommerce() { return false; }
function is_page( $slugs ) { return in_array( $GLOBALS['route']['page'] ?? '', (array) $slugs, true ); }
function is_page_template( $templates ) { return in_array( $GLOBALS['route']['template'] ?? '', (array) $templates, true ); }
function wp_enqueue_script( $handle, ...$args ) { $GLOBALS['enqueued_scripts'][ $handle ] = $args; }
function wp_enqueue_style( $handle, ...$args ) { $GLOBALS['enqueued_styles'][ $handle ] = $args; }
function wp_register_script( $handle, ...$args ) { $GLOBALS['enqueued_scripts'][ $handle ] = $args; }
function wp_script_is( $handle, $state ) { return 'enqueued' === $state && isset( $GLOBALS['enqueued_scripts'][ $handle ] ); }
function wp_add_inline_script( ...$args ) {}

// Evaluate the exact function body from the theme. Loading all of functions.php
// would execute unrelated WordPress bootstrap work and obscure this route test.
$source = file_get_contents( __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/functions.php' );
$start = strpos( $source, 'function skyyrose2_assets() {' );
$marker = "add_action( 'wp_enqueue_scripts', 'skyyrose2_assets' );";
$end = false !== $start ? strpos( $source, $marker, $start ) : false;
if ( false === $start || false === $end ) {
	throw new RuntimeException( 'Could not locate the theme asset enqueue function.' );
}
eval( substr( $source, $start, $end - $start ) ); // phpcs:ignore Squiz.PHP.Eval.Discouraged -- Isolated test of actual theme function.

function assert_commerce_page_assets( $label ) {
	if ( is_woocommerce() ) {
		throw new RuntimeException( $label . ' fixture must be outside WooCommerce archive routing.' );
	}
	foreach ( array( 'wc-add-to-cart', 'wc-cart-fragments', 'skyyrose2-quick-view-commerce' ) as $handle ) {
		if ( ! isset( $GLOBALS['enqueued_scripts'][ $handle ] ) ) {
			throw new RuntimeException( $label . ' did not enqueue ' . $handle . '.' );
		}
	}
}

$GLOBALS['route'] = array( 'collection' => 'black-rose', 'page' => 'black-rose', 'template' => 'template-collection.php' );
skyyrose2_assets();
assert_commerce_page_assets( 'Custom collection' );

$GLOBALS['route'] = array( 'collection' => '', 'page' => 'pre-order', 'template' => '' );
$GLOBALS['enqueued_scripts'] = array();
$GLOBALS['enqueued_styles'] = array();
skyyrose2_assets();
assert_commerce_page_assets( 'Pre-order page' );

echo "PASS: custom collection and pre-order enqueue WooCommerce card actions outside is_woocommerce().\n";
