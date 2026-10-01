<?php
/**
 * Destructive synthetic-fixture integration tests, never run on an external site.
 * wp eval-file <this-file> --path=<isolated-local-WordPress>
 * Requires actual WooCommerce 11.1.2; no simulated WC classes or order storage.
 *
 * @package SkyyRoseFlagship2
 */

if ( ! defined( 'WP_CLI' ) || ! WP_CLI || 'http://127.0.0.1:18362' !== get_option( 'home' ) || '11.1.2' !== WC_VERSION ) {
	throw new RuntimeException( 'Only the isolated loopback WooCommerce 11.1.2 fixture is permitted.' );
}
require_once dirname( __DIR__, 2 ) . '/inc/woocommerce-compat.php';
// This file deliberately leaves fixture records for inspection; no real SKU facts.
remove_all_actions( 'woocommerce_email' );
add_filter( 'pre_wp_mail', '__return_true' );
update_option( 'woocommerce_calc_taxes', 'no' );
update_option( 'woocommerce_enable_coupons', 'yes' );
update_option( 'woocommerce_currency', 'USD' );
WC()->initialize_session();
WC()->customer = new WC_Customer( 0, true );
WC()->cart     = new WC_Cart();

/**
 * Assert one actual runtime observation.
 *
 * @throws RuntimeException When the observation is false.
 */
function skyyrose2_fixture_assert( $condition, $label ) {
	if ( ! $condition ) {
		throw new RuntimeException( esc_html( 'FAIL: ' . $label ) );
	}
	echo esc_html( 'PASS: ' . $label ) . "\n";
}

function skyyrose2_fixture_product( $meta = array(), $type = 'simple' ) {
	$product = 'variable' === $type ? new WC_Product_Variable() : new WC_Product_Simple();
	$product->set_name( 'Synthetic preorder fixture' );
	$product->set_status( 'publish' );
	$product->set_regular_price( '80' );
	$product->set_virtual( true );
	foreach ( $meta as $key => $value ) {
		$product->update_meta_data( $key, $value );
	}
	$product->save();
	return $product;
}

function skyyrose2_fixture_empty() {
	WC()->cart->empty_cart();
	wc_clear_notices();
}

function skyyrose2_fixture_order() {
	WC()->cart->calculate_totals();
	$order = new WC_Order();
	WC()->checkout()->set_data_from_cart( $order );
	$order->calculate_totals();
	$order->save();
	return wc_get_order( $order->get_id() );
}

$product = skyyrose2_fixture_product(
	array(
		'_is_preorder'           => '1',
		'_preorder_available'    => '3',
		'_preorder_edition_size' => '25',
		'_preorder_ship_date'    => '2027-01-15',
		'_preorder_price'        => '1',
	)
);
$id      = $product->get_id();
$key     = WC()->cart->add_to_cart(
	$id,
	2,
	0,
	array(),
	array(
		'skyyrose_preorder_snapshot' => array(
			'expected_ship_date' => '2099-01-01',
			'price'              => 1,
		),
	)
);
skyyrose2_fixture_assert( (bool) $key, 'direct core add positive simple product' );
$values   = WC()->cart->get_cart()[ $key ];
$snapshot = $values['skyyrose_preorder_snapshot'];
skyyrose2_fixture_assert( 2 === $snapshot['schema_version'] && '2027-01-15' === $snapshot['expected_ship_date'] && ! isset( $snapshot['price'] ), 'server replaces tampered snapshot and excludes price' );
skyyrose2_fixture_assert( false === WC()->cart->add_to_cart( $id, 2 ), 'direct core add rejects insufficient pool without fatal' );
skyyrose2_fixture_assert( 2 === WC()->cart->get_cart()[ $key ]['quantity'], 'failed direct add preserves stored quantity' );
skyyrose2_fixture_assert( true === apply_filters( 'woocommerce_update_cart_validation', true, $key, $values, 3 ), 'quantity update excludes old line' );
skyyrose2_fixture_assert( false === apply_filters( 'woocommerce_update_cart_validation', true, $key, $values, 4 ), 'quantity update rejects over allocation' );
WC()->cart->set_quantity( $key, 3, false );
skyyrose2_fixture_assert( 3 === WC()->cart->get_cart()[ $key ]['quantity'], 'native quantity edit stores validated replacement' );
WC()->cart->set_quantity( $key, 2, false );
skyyrose2_fixture_assert( false === WC()->cart->add_to_cart( $id, 0.5 ), 'direct core rejects fractional quantity' );
skyyrose2_fixture_assert( false === WC()->cart->add_to_cart( $id, 0 ), 'native zero add rejected' );
foreach ( array( -1, 0.5, 'tampered', INF ) as $bad ) {
	skyyrose2_fixture_assert( false === skyyrose2_preorder_add_validation( true, $id, $bad ), 'invalid request quantity ' . (string) $bad );
}
skyyrose2_fixture_assert( true === skyyrose2_preorder_update_validation( true, $key, $values, 0 ), 'zero quantity permits removal' );
skyyrose2_fixture_assert( false === skyyrose2_preorder_add_validation( false, $id, 1 ), 'prior permission denial preserved' );
wc_clear_notices();
skyyrose2_fixture_assert( array() === skyyrose2_preorder_cart_errors( WC()->cart ), 'valid cart has no promise/allocation errors' );
$formatted = wc_get_formatted_cart_item_data( $values );
skyyrose2_fixture_assert( false !== strpos( $formatted, '2027-01-15' ), 'native checkout display includes recorded promise' );
$restored = apply_filters( 'woocommerce_get_cart_item_from_session', $values, $values, $key );
skyyrose2_fixture_assert( $snapshot === $restored['skyyrose_preorder_snapshot'], 'session restore preserves exact recorded promise' );
$session = new WC_Cart_Session( WC()->cart );
$session->set_session();
$session_data = WC()->session->get( 'cart' );
skyyrose2_fixture_assert( $session_data[ $key ]['skyyrose_preorder_snapshot'] === $snapshot, 'native session serialization stores exact snapshot' );
WC()->cart = new WC_Cart();
$session   = new WC_Cart_Session( WC()->cart );
$session->get_cart_from_session();
skyyrose2_fixture_assert( WC()->cart->get_cart()[ $key ]['skyyrose_preorder_snapshot'] === $snapshot, 'native session restoration retains exact snapshot' );
$product->update_meta_data( '_preorder_ship_date', '2027-02-20' );
$product->save();
skyyrose2_fixture_assert( count( skyyrose2_preorder_cart_errors( WC()->cart ) ) > 0, 'product promise edit blocks checkout' );
skyyrose2_fixture_assert( WC()->cart->get_cart()[ $key ]['skyyrose_preorder_snapshot'] === $snapshot, 'promise change never rewrites stored cart history' );
$errors = new WP_Error();
do_action( 'woocommerce_store_api_cart_errors', $errors, WC()->cart );
skyyrose2_fixture_assert( $errors->has_errors(), 'Store API returns structured stale promise error' );
$legacy = $values;
unset( $legacy['skyyrose_preorder_snapshot'] );
WC()->cart->cart_contents[ $key ] = $legacy;
skyyrose2_fixture_assert( count( skyyrose2_preorder_cart_errors( WC()->cart ) ) > 0, 'legacy cart requires explicit product review' );
skyyrose2_fixture_empty();
$key    = WC()->cart->add_to_cart( $id, 1 );
$values = WC()->cart->get_cart()[ $key ];
$product->set_regular_price( '95' );
$product->save();
// Native session restoration refreshes product objects on the next request.
WC()->cart->cart_contents[ $key ]['data'] = wc_get_product( $id );
WC()->cart->calculate_totals();
skyyrose2_fixture_assert( array() === skyyrose2_preorder_cart_errors( WC()->cart ) && 95.0 === (float) WC()->cart->get_total( 'edit' ), 'native price change updates totals without descriptive promise drift' );

foreach ( array( get_option( 'woocommerce_custom_orders_table_enabled', 'no' ) ) as $hpos ) {
	$order = skyyrose2_fixture_order();
	$item  = current( $order->get_items() );
	$store = $order->get_data_store()->get_current_class_name();
	skyyrose2_fixture_assert( 'yes' === $hpos ? false !== strpos( $store, 'OrdersTableDataStore' ) : 'WC_Order_Data_Store_CPT' === $store, 'actual active order data store ' . $store );
	$stored = $item->get_meta( '_skyyrose_preorder_snapshot', true );
	skyyrose2_fixture_assert( 'recorded' === skyyrose2_preorder_read_item( $item )['status'] && 95.0 === (float) $order->get_total(), 'real order storage ' . $hpos . ' promise and native total' );
	$product->update_meta_data( '_preorder_ship_date', '2028-03-01' );
	$product->save();
	skyyrose2_preorder_persist_item( $item, $key, $values, $order );
	$item->save();
	$reloaded = new WC_Order_Item_Product( $item->get_id() );
	skyyrose2_fixture_assert( $stored === $reloaded->get_meta( '_skyyrose_preorder_snapshot', true ), 'post-order edits and repeated hook preserve snapshot ' . $hpos );
	$order->set_status( 'failed' );
	$order->save();
	$order->set_status( 'cancelled' );
	$order->save();
	skyyrose2_fixture_assert( '3' === (string) wc_get_product( $id )->get_meta( '_preorder_available' ), 'failure/cancellation does not decrement or restore custom allocation ' . $hpos );
	$refund = wc_create_refund(
		array(
			'order_id'       => $order->get_id(),
			'amount'         => 10,
			'refund_payment' => false,
			'restock_items'  => false,
		)
	);
	skyyrose2_fixture_assert( ! is_wp_error( $refund ) && '3' === (string) wc_get_product( $id )->get_meta( '_preorder_available' ), 'local non-payment refund preserves custom allocation ' . $hpos );
	$display = $reloaded->get_formatted_meta_data();
	skyyrose2_fixture_assert( false !== strpos( wp_json_encode( $display ), '2027-02-20' ), 'native order/email display uses order history ' . $hpos );
	$product->update_meta_data( '_preorder_ship_date', '2027-02-20' );
	$product->save();
}

$old = new WC_Order_Item_Product();
skyyrose2_fixture_assert( 'legacy_unknown' === skyyrose2_preorder_read_item( $old )['status'], 'historical no-snapshot order remains unknown' );
$old->add_meta_data(
	'_skyyrose_preorder_snapshot',
	array(
		'schema'             => 'skyyrose.preorder-commercial-promise',
		'schema_version'     => 1,
		'is_preorder'        => true,
		'expected_ship_date' => '2025-01-01',
	),
	true
);
skyyrose2_fixture_assert( 'recorded' === skyyrose2_preorder_read_item( $old )['status'], 'v1 historical schema readable without current product' );
$old->update_meta_data(
	'_skyyrose_preorder_snapshot',
	array(
		'schema'         => 'future',
		'schema_version' => 99,
	)
);
skyyrose2_fixture_assert( 'unsupported_schema' === skyyrose2_preorder_read_item( $old )['status'], 'future order schema retained without fabrication' );
$historical_order = new WC_Order();
$historical_item  = new WC_Order_Item_Product();
$historical_item->set_product( wc_get_product( $id ) );
$historical_item->set_quantity( 1 );
$historical_order->add_item( $historical_item );
$historical_order->save();
skyyrose2_preorder_persist_item( $historical_item, $key, $values );
skyyrose2_fixture_assert( ! $historical_item->meta_exists( '_skyyrose_preorder_snapshot' ), 'persisted historical item is never backfilled' );

skyyrose2_fixture_empty();
$parent    = skyyrose2_fixture_product(
	array(
		'_is_preorder'        => '1',
		'_preorder_available' => '1',
	),
	'variable'
);
$attribute = new WC_Product_Attribute();
$attribute->set_name( 'Size' );
$attribute->set_options( array( 'M', 'L' ) );
$attribute->set_variation( true );
$parent->set_attributes( array( $attribute ) );
$parent->save();
$variations = array();
foreach ( array( 'M', 'L' ) as $size ) {
	$variation = new WC_Product_Variation();
	$variation->set_parent_id( $parent->get_id() );
	$variation->set_attributes( array( 'size' => $size ) );
	$variation->set_regular_price( '70' );
	$variation->set_virtual( true );
	$variation->save();
	$variations[] = $variation;
}
WC_Product_Variable::sync( $parent );
$first = WC()->cart->add_to_cart( $parent->get_id(), 1, $variations[0]->get_id(), array( 'attribute_size' => 'M' ) );
skyyrose2_fixture_assert( (bool) $first, 'variation inherits parent preorder/allocation' );
skyyrose2_fixture_assert( false === WC()->cart->add_to_cart( $parent->get_id(), 1, $variations[1]->get_id(), array( 'attribute_size' => 'L' ) ), 'sibling variations share parent allocation pool' );
$variation_order    = skyyrose2_fixture_order();
$variation_item     = current( $variation_order->get_items() );
$variation_snapshot = $variation_item->get_meta( '_skyyrose_preorder_snapshot', true );
skyyrose2_fixture_assert( $variations[0]->get_id() === $variation_snapshot['variation_id'] && 'M' === $variation_snapshot['attributes']['attribute_size'], 'variation order stores stable selected identity' );
$variations[1]->update_meta_data( '_preorder_available', '0' );
$variations[1]->save();
skyyrose2_fixture_assert( false === WC()->cart->add_to_cart( $parent->get_id(), 1, $variations[1]->get_id(), array( 'attribute_size' => 'L' ) ), 'explicit variation zero blocks addition' );
skyyrose2_fixture_assert( false === skyyrose2_preorder_add_validation( true, $id, 1, $variations[0]->get_id() ), 'unrelated variation rejected' );
skyyrose2_fixture_empty();
$variations[0]->set_attributes( array( 'size' => '' ) );
$variations[0]->save();
WC_Product_Variable::sync( $parent );
$wildcard = WC()->cart->add_to_cart( $parent->get_id(), 1, $variations[0]->get_id(), array( 'attribute_size' => 'L' ) );
skyyrose2_fixture_assert( (bool) $wildcard && 'L' === WC()->cart->get_cart()[ $wildcard ]['skyyrose_preorder_snapshot']['attributes']['attribute_size'], 'wildcard variation captures resolved selected size' );
skyyrose2_fixture_assert( false === WC()->cart->add_to_cart( $parent->get_id(), 1, $variations[0]->get_id(), array( 'attribute_size' => 'L' ) ), 'repeated wildcard add checks shared allocation before merge' );
skyyrose2_fixture_assert( array() === skyyrose2_preorder_cart_errors( WC()->cart ), 'wildcard selection remains valid at checkout' );
skyyrose2_fixture_empty();
$uncapped = skyyrose2_fixture_product( array( '_is_preorder' => '1' ) );
skyyrose2_fixture_assert( (bool) WC()->cart->add_to_cart( $uncapped->get_id(), 5 ), 'absent legacy allocation remains uncapped' );
$uncapped->update_meta_data( '_preorder_available', '-2' );
$uncapped->save();
skyyrose2_fixture_assert( count( skyyrose2_preorder_cart_errors( WC()->cart ) ) > 0, 'malformed allocation fails closed' );

// Real Store API order builder, not invocation of an assumed hook.
skyyrose2_fixture_empty();
WC()->cart->add_to_cart( $id, 1 );
$controller = new Automattic\WooCommerce\StoreApi\Utilities\OrderController();
$api_order  = $controller->create_order_from_cart();
$api_order->save();
$api_item = current( wc_get_order( $api_order->get_id() )->get_items() );
skyyrose2_fixture_assert( 'recorded' === skyyrose2_preorder_read_item( $api_item )['status'], 'real Store API order builder persists promise' );
$product->update_meta_data( '_preorder_available', '0' );
$product->save();
$errors = new WP_Error();
skyyrose2_fixture_empty();
do_action( 'woocommerce_checkout_validate_order_before_payment', $api_order, $errors );
skyyrose2_fixture_assert( $errors->has_errors(), 'existing Store API order revalidates availability with empty cart' );
wc_clear_notices();
do_action( 'woocommerce_before_pay_action', $api_order );
skyyrose2_fixture_assert( wc_notice_count( 'error' ) > 0, 'classic pay-for-order emits handled allocation error' );
$product->update_meta_data( '_preorder_available', '3' );
$product->save();
WC()->cart->cart_contents['unrelated'] = array(
	'product_id'   => $uncapped->get_id(),
	'variation_id' => 0,
	'quantity'     => 1,
	'data'         => $uncapped,
);
$errors                                = new WP_Error();
do_action( 'woocommerce_checkout_validate_order_before_payment', $api_order, $errors );
skyyrose2_fixture_assert( ! $errors->has_errors(), 'existing-order payment isolates unrelated invalid cart' );

$referrer_id = wp_insert_user(
	array(
		'user_login' => 'fixture-referrer-' . wp_generate_uuid4(),
		'user_email' => 'referrer-' . wp_generate_uuid4() . '@example.test',
		'user_pass'  => wp_generate_password(),
	)
);
$referrer    = get_user_by( 'id', $referrer_id );
$coupon      = new WC_Coupon();
$coupon->set_code( 'SKYY-fixture-' . wp_generate_uuid4() );
$coupon->set_amount( '5' );
$coupon->set_discount_type( 'fixed_cart' );
$coupon->update_meta_data( '_skyyrose_referral_owner_email', $referrer->user_email );
$coupon->save();
skyyrose2_fixture_empty();
WC()->cart->add_to_cart( $id, 1 );
skyyrose2_fixture_assert( WC()->cart->apply_coupon( $coupon->get_code() ), 'native coupon applies to snapshot cart' );
$discounted = skyyrose2_fixture_order();
skyyrose2_fixture_assert( 90.0 === (float) $discounted->get_total(), 'native discount remains authoritative in stored order total' );
do_action( 'woocommerce_checkout_order_created', $discounted );
skyyrose2_fixture_assert( $discounted->meta_exists( '_skyyrose_referral_attribution' ), 'real cart coupon survives through order attribution' );
$referral_order = new WC_Order();
$referral_order->set_billing_email( 'buyer@example.test' );
$coupon_item = new WC_Order_Item_Coupon();
$coupon_item->set_code( $coupon->get_code() );
$referral_order->add_item( $coupon_item );
$referral_order->save();
do_action( 'woocommerce_checkout_order_created', $referral_order );
$referral_order = wc_get_order( $referral_order->get_id() );
$attribution    = $referral_order->get_meta( '_skyyrose_referral_attribution', true );
skyyrose2_fixture_assert( (int) $referrer_id === $attribution['referrer_id'] && ! isset( $attribution['email'] ), 'CRUD referral attribution stored without email' );
do_action( 'woocommerce_store_api_checkout_order_processed', $referral_order );
skyyrose2_fixture_assert( $attribution === $referral_order->get_meta( '_skyyrose_referral_attribution', true ), 'repeated lifecycle event retains referral identity' );
$self_order = new WC_Order();
$self_order->set_billing_email( $referrer->user_email );
$self_coupon = new WC_Order_Item_Coupon();
$self_coupon->set_code( $coupon->get_code() );
$self_order->add_item( $self_coupon );
$self_order->save();
skyyrose2_preorder_capture_referral( $self_order );
skyyrose2_fixture_assert( ! $self_order->meta_exists( '_skyyrose_referral_attribution' ), 'self referral receives no attribution' );
// Two independent carts can both validate the last custom allocation: validation
// does not reserve it. This explicitly demonstrates the unresolved ownership gate.
skyyrose2_fixture_empty();
$last      = skyyrose2_fixture_product(
	array(
		'_is_preorder'        => '1',
		'_preorder_available' => '1',
	)
);
$cart_a    = WC()->cart;
$key_a     = $cart_a->add_to_cart( $last->get_id(), 1 );
WC()->cart = new WC_Cart();
$key_b     = WC()->cart->add_to_cart( $last->get_id(), 1 );
skyyrose2_fixture_assert( (bool) $key_a && (bool) $key_b && '1' === (string) wc_get_product( $last->get_id() )->get_meta( '_preorder_available' ), 'ownership gap reproduced: independent carts do not reserve custom allocation' );
echo "LOCAL INTEGRATION COMPLETE; no external order/payment/provider calls\n";
