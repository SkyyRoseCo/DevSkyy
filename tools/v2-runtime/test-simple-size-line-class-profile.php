<?php
/** Offline source-bound Stripe Tax product-line pass-through; no WordPress/DB/network. */
define( 'ABSPATH', __DIR__ . '/' );
define( 'STRIPE_TAX_FOR_WOOCOMMERCE_DB_PREFIX', 'synthetic_' );
$source = $argv[1] ?? '';
$destination = $argv[2] ?? '';
if ( ! is_dir( $source ) || file_exists( $destination ) || ! str_starts_with( $destination, dirname( __DIR__, 2 ) . '/.artifacts/' ) ) { throw new RuntimeException( 'Retained source and fresh owned output required.' ); }
mkdir( $destination, 0700, true );
define( 'WP_PLUGIN_DIR', $destination );
$root = WP_PLUGIN_DIR . '/stripe-tax-for-woocommerce/';
foreach ( array( 'WordPress/class-hooks.php', 'WordPress/class-hook-handlers.php', 'WordPress/class-options.php', 'WooCommerce/Hook_Handlers/class-order-tax-calculation.php' ) as $file ) {
	$target = $root . $file;
	if ( ! is_dir( dirname( $target ) ) ) { mkdir( dirname( $target ), 0700, true ); }
	copy( $source . '/' . $file, $target );
}
function add_action( ...$unused ) {}
function add_filter( ...$unused ) {}
function wp_cache_get( ...$unused ) { return array( 'live_mode_enabled' => (object) array( 'option_value' => $GLOBALS['tax_enabled'] ? '1' : '0' ) ); }
function wc_tax_enabled() { return true; }
require $root . 'WordPress/class-options.php';
require $root . 'WordPress/class-hook-handlers.php';
require $root . 'WordPress/class-hooks.php';
require $root . 'WooCommerce/Hook_Handlers/class-order-tax-calculation.php';
require dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2/inc/simple-product-sizes.php';
$first = array( 'Stripe\\StripeTaxForWooCommerce\\WordPress\\Hooks', 'filter_woocommerce_get_order_item_classname' );
$second = array( 'Stripe\\StripeTaxForWooCommerce\\WooCommerce\\Hook_Handlers\\Order_Tax_Calculation', 'get_order_item_classname' );
$native = 'WC_Order_Item_Product';
foreach ( array( false, true ) as $enabled ) {
	$GLOBALS['tax_enabled'] = $enabled;
	foreach ( array( $first, $second ) as $callback ) {
		if ( call_user_func( $callback, $native, 'line_item' ) !== $native ) { throw new RuntimeException( 'Product class changed.' ); }
	}
	$tax = call_user_func( $second, 'WC_Order_Item_Tax', 'tax' );
	if ( $tax !== ( $enabled ? 'Stripe\\StripeTaxForWooCommerce\\WooCommerce\\StripeOrderItemTax' : 'WC_Order_Item_Tax' ) ) { throw new RuntimeException( 'Actual tax branch not exercised.' ); }
}
$chain = array( 5 => array( 'first' => array( 'function' => $first, 'accepted_args' => 2 ) ), 100 => array( 'second' => array( 'function' => $second, 'accepted_args' => 4 ) ) );
function ss_class_expect_refused() {
	try { skyyrose2_simple_size_line_class_profile(); } catch ( RuntimeException $error ) { return; }
	throw new RuntimeException( 'Unqualified callback admitted.' );
}
$wp_filter = array( 'woocommerce_get_order_item_classname' => (object) array( 'callbacks' => $chain ) );
skyyrose2_simple_size_line_class_profile();
$wp_filter['woocommerce_get_order_item_classname']->callbacks[999]['extra'] = array( 'function' => static fn( $value ) => $value, 'accepted_args' => 1 ); ss_class_expect_refused();
$wp_filter['woocommerce_get_order_item_classname']->callbacks = $chain; $wp_filter['woocommerce_get_order_item_classname']->callbacks[100]['second']['accepted_args'] = 2; ss_class_expect_refused();
$wp_filter['woocommerce_get_order_item_classname']->callbacks = $chain; $wp_filter['woocommerce_get_order_item_classname']->callbacks[5]['first']['function'][1] = 'unknown'; ss_class_expect_refused();
$wp_filter['woocommerce_get_order_item_classname']->callbacks = $chain;
$file = $root . 'WordPress/class-options.php'; $preimage = file_get_contents( $file );
try { file_put_contents( $file, $preimage . "\n" ); ss_class_expect_refused(); } finally { file_put_contents( $file, $preimage ); }
skyyrose2_simple_size_line_class_profile();
$wp_filter['woocommerce_get_order_item_classname']->callbacks = array(); skyyrose2_simple_size_line_class_profile();
echo "PASS actual retained tax callbacks: enabled/disabled product passthrough, native tax branch, exact chain, altered/extra/source negatives; offline only\n";
