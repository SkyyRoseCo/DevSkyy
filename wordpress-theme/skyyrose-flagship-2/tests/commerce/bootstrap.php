<?php
/**
 * Full-theme bootstrap and presentation/transaction agreement on synthetic CRUD.
 * Run using wp eval-file, with the theme already active and no manual include.
 * Authentication: not applicable; isolated loopback fixture only.
 *
 * @package SkyyRoseFlagship2
 */

if ( ! defined( 'WP_CLI' ) || ! WP_CLI || 'http://127.0.0.1:18362' !== get_option( 'home' ) || ! defined( 'WC_VERSION' ) || '11.1.2' !== WC_VERSION ) {
	throw new RuntimeException( 'Only the isolated loopback WooCommerce 11.1.2 fixture is permitted.' );
}
function skyyrose2_bootstrap_assert( $condition, $label ) {
	if ( ! $condition ) {
		throw new RuntimeException( 'FAIL: ' . esc_html( $label ) );
	}
	echo esc_html( 'PASS: ' . $label ) . "\n";
}
skyyrose2_bootstrap_assert( function_exists( 'skyyrose2_preorder_config' ), 'compatibility loaded through full theme before test includes' );
$bootstrap = file_get_contents( SKYYROSE2_DIR . '/functions.php' ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- Local source read, never remote.
skyyrose2_bootstrap_assert( 1 === substr_count( $bootstrap, "require_once SKYYROSE2_DIR . '/inc/woocommerce-compat.php';" ), 'exactly one bootstrap include statement' );
$path = realpath( SKYYROSE2_DIR . '/inc/woocommerce-compat.php' );
skyyrose2_bootstrap_assert( 1 === count( array_filter( get_included_files(), static fn( $file ) => realpath( $file ) === $path ) ), 'compatibility file included exactly once' );
foreach ( array(
	'woocommerce_add_cart_item_data'              => 'skyyrose2_preorder_add_cart_data',
	'woocommerce_check_cart_items'                => 'skyyrose2_preorder_check_cart',
	'woocommerce_checkout_create_order_line_item' => 'skyyrose2_preorder_persist_item',
) as $hook => $callback ) {
	$count = 0;
	foreach ( $GLOBALS['wp_filter'][ $hook ]->callbacks ?? array() as $callbacks ) {
		foreach ( $callbacks as $entry ) {
			$count += $callback === $entry['function'] ? 1 : 0;
		}
	}
	skyyrose2_bootstrap_assert( 1 === $count, 'theme registers exactly one ' . $callback );
}
// Read current presentation consumers; never write canonical product facts.
$records = skyyrose2_presentation_registry()['products'];
$skus    = array(
	'regular'  => '',
	'preorder' => '',
);
foreach ( $records as $sku => $record ) {
	$kind = empty( $record['is_preorder'] ) ? 'regular' : 'preorder';
	if ( ! $skus[ $kind ] && ! wc_get_product_id_by_sku( $sku ) ) {
		$skus[ $kind ] = $sku;
	}
}
skyyrose2_bootstrap_assert( (bool) $skus['regular'] && (bool) $skus['preorder'], 'fixture has unused canonical regular and preorder SKUs' );
foreach ( $skus as $kind => $sku ) {
	$parent = new WC_Product_Variable();
	$parent->set_name( 'Synthetic classification fixture ' . $kind );
	$parent->set_sku( $sku );
	$parent->set_status( 'publish' );
	$attribute = new WC_Product_Attribute();
	$attribute->set_name( 'Size' );
	$attribute->set_options( array( 'S', 'M' ) );
	$attribute->set_variation( true );
	$parent->set_attributes( array( $attribute ) );
	$parent->update_meta_data( '_is_preorder', '1' );
	$parent->update_meta_data( '_preorder_ship_date', '2027-01-15' );
	$parent->save();
	foreach ( array( 'inherited', 'explicit-zero' ) as $mode ) {
		$variation = new WC_Product_Variation();
		$variation->set_parent_id( $parent->get_id() );
		$variation->set_sku( 'synthetic-' . $kind . '-' . $mode . '-' . $parent->get_id() );
		$variation->set_attributes( array( 'size' => 'inherited' === $mode ? 'S' : 'M' ) );
		$variation->set_regular_price( '80' );
		$variation->set_status( 'publish' );
		if ( 'explicit-zero' === $mode ) {
			$variation->update_meta_data( '_is_preorder', '0' );
		}
		$variation->save();
		$config   = skyyrose2_preorder_config( $parent->get_id(), $variation->get_id() );
		$expected = 'preorder' === $kind || 'inherited' === $mode;
		skyyrose2_bootstrap_assert( (bool) $expected === $config['is_preorder'], $kind . ' ' . $mode . ' transaction classification' );
		skyyrose2_bootstrap_assert( $variation->get_sku() === $config['sku'] && $variation->get_variation_attributes() === $config['attributes'], 'snapshot keeps native variation SKU and selected size' );
		skyyrose2_bootstrap_assert( skyyrose2_is_transaction_preorder_product( $variation ) === (bool) $expected, $kind . ' ' . $mode . ' display matches transaction' );
		$data  = apply_filters( 'woocommerce_available_variation', array( 'availability_html' => '<p>Native stock</p>' ), $parent, $variation );
		$label = $expected ? 'Pre-order option.' : 'Standard order option.';
		skyyrose2_bootstrap_assert( false !== strpos( $data['availability_html'], $label ) && false !== strpos( $data['availability_html'], 'Native stock' ), 'native variation response shows selected classification and retains stock' );
	}
	if ( 'regular' === $kind ) {
		$parent->update_meta_data( '_is_preorder', '0' );
		$parent->save();
		$variation->update_meta_data( '_is_preorder', '1' );
		$variation->save();
		$config = skyyrose2_preorder_config( $parent->get_id(), $variation->get_id() );
		skyyrose2_bootstrap_assert( $config['is_preorder'] && skyyrose2_is_transaction_preorder_product( $variation ) && ! skyyrose2_is_transaction_preorder_product( $parent ), 'preorder child of regular parent retains option-dependent classification' );
		$parent->update_meta_data( '_is_preorder', '1' );
		$parent->save();
	}
	skyyrose2_bootstrap_assert( true === skyyrose2_is_transaction_preorder_product( $parent ), 'parent display inherits Woo preorder metadata' );
}
echo "FULL THEME BOOTSTRAP COMPLETE\n";
