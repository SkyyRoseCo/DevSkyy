<?php
/**
 * Read-only combined-theme registration check; never includes the module itself.
 * Run with wp eval-file after stream 1 loads the dependency in its V2 bootstrap.
 * This checks registration only, not storefront or order acceptance.
 *
 * @package SkyyRoseFlagship2
 */

if ( ! defined( 'WP_CLI' ) || ! WP_CLI ) {
	throw new RuntimeException( 'Run through WP-CLI on the selected candidate.' );
}
if ( 'skyyrose-flagship-2' !== get_stylesheet() || ! defined( 'WC_VERSION' ) || '11.1.2' !== WC_VERSION ) {
	WP_CLI::error( 'Requires active V2 and the reviewed WooCommerce 11.1.2 boundary.' );
}
$expected = array(
	'woocommerce_add_cart_item_data'                     => 'skyyrose2_preorder_add_cart_data',
	'woocommerce_add_cart_item'                          => 'skyyrose2_preorder_finalize_cart_item',
	'woocommerce_add_to_cart_validation'                 => 'skyyrose2_preorder_add_validation',
	'woocommerce_update_cart_validation'                 => 'skyyrose2_preorder_update_validation',
	'woocommerce_check_cart_items'                       => 'skyyrose2_preorder_check_cart',
	'woocommerce_store_api_cart_errors'                  => 'skyyrose2_preorder_store_cart_errors',
	'woocommerce_checkout_create_order'                  => 'skyyrose2_preorder_validate_new_order',
	'woocommerce_checkout_validate_order_before_payment' => 'skyyrose2_preorder_validate_order_payment',
	'woocommerce_before_pay_action'                      => 'skyyrose2_preorder_before_pay',
	'woocommerce_checkout_create_order_line_item'        => 'skyyrose2_preorder_persist_item',
	'woocommerce_get_item_data'                          => 'skyyrose2_preorder_display_cart_data',
	'woocommerce_order_item_get_formatted_meta_data'     => 'skyyrose2_preorder_display_order_meta',
	'woocommerce_checkout_order_created'                 => 'skyyrose2_preorder_capture_referral',
	'woocommerce_store_api_checkout_order_processed'     => 'skyyrose2_preorder_capture_referral',
);
foreach ( $expected as $tag => $function ) {
	$count = 0;
	foreach ( $GLOBALS['wp_filter'][ $tag ]->callbacks ?? array() as $priority => $callbacks ) {
		foreach ( $callbacks as $callback ) {
			if ( $function === $callback['function'] ) {
				++$count;
				if ( 10 !== $priority ) {
					WP_CLI::error( 'Unexpected callback priority: ' . $tag );
				}
			}
		}
	}
	if ( ! function_exists( $function ) || 1 !== $count ) {
		WP_CLI::error( 'Missing or duplicate callback: ' . $tag );
	}
}
$module = get_stylesheet_directory() . '/inc/woocommerce-compat.php';
if ( '98fb6726e5704a5ac741d9b20b2bc38bb1578633998cacbe2ecac79d7ed778a1' !== hash_file( 'sha256', $module ) ) {
	WP_CLI::error( 'Module differs from the reviewed dependency.' );
}
WP_CLI::success( 'V2 module hash and all 14 hook registrations match; behavior acceptance remains separate.' );
