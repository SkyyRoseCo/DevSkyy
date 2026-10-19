<?php
/** WP-CLI controls, fixed fresh synthetic fixture only. */
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SR_SIMPLE_SIZE_FIXTURE_ROOT' ) || DB_NAME !== 'sr_simple_size_fixture' || realpath( ABSPATH ) !== realpath( SR_SIMPLE_SIZE_FIXTURE_ROOT . '/wordpress' ) ) { throw new RuntimeException( 'Fresh synthetic CLI identity required.' ); }
ss_assert_identity( true );
function ss_owned_order( $id ) {
	$order = new WC_Order( $id );
	if ( $order->get_meta( '_ss_owner' ) !== basename( SR_SIMPLE_SIZE_FIXTURE_ROOT ) ) { throw new RuntimeException( 'Owned native order required.' ); }
	return $order;
}
function ss_raw_results( $sql ) {
    global $wpdb;
    $rows = $wpdb->get_results( $sql, ARRAY_A );
    if ( $wpdb->last_error || ! is_array( $rows ) ) { throw new RuntimeException( 'Raw native evidence query failed.' ); }
    return $rows;
}
function ss_order_data( $order ) {
	global $wpdb;
	$items = array(); foreach ( $order->get_items() as $item ) { $items[] = $item->get_data(); }
	$raw = array(); foreach ( $items as $item ) { $raw = array_merge( $raw, ss_raw_results( $wpdb->prepare( "SELECT meta_id,order_item_id,meta_key,meta_value FROM {$wpdb->prefix}woocommerce_order_itemmeta WHERE order_item_id=%d AND meta_key IN ('_skyyrose_simple_size_v1','Size') ORDER BY meta_id", $item['id'] ) ) ); }
	$generation_raw = ss_raw_results( $wpdb->prepare( "SELECT id,order_id,meta_key,meta_value FROM {$wpdb->prefix}wc_orders_meta WHERE order_id=%d AND meta_key='_skyyrose_simple_size_generation_v1' ORDER BY id", $order->get_id() ) );
	return array( 'id' => $order->get_id(), 'status' => $order->get_status(), 'key' => $order->get_order_key(), 'items' => $items, 'generation' => skyyrose2_simple_size_meta_values( $order, '_skyyrose_simple_size_generation_v1' ), 'raw_size_rows' => $raw, 'raw_generation_rows' => $generation_raw, 'paid' => (bool) $order->get_date_paid(), 'cart_hash' => $order->get_cart_hash(), 'data_store' => $order->get_data_store()->get_current_class_name() );
}
$mode = $args[0] ?? '';
$result = array();
if ( 'init' === $mode ) {
	if ( get_option( 'ss_products' ) || get_option( 'skyyrose2_simple_size_history_v1' ) ) { throw new RuntimeException( 'Fresh fixture only; no inventory adoption.' ); }
	WC_Install::install();
	update_option( 'woocommerce_custom_orders_table_enabled', 'yes' );
	update_option( 'woocommerce_custom_orders_table_data_sync_enabled', 'no' );
	update_option( 'woocommerce_currency', 'USD' ); update_option( 'woocommerce_default_country', 'US:CA' ); update_option( 'woocommerce_calc_taxes', 'no' );
	foreach ( array( 'cart' => '[woocommerce_cart]', 'checkout' => '[woocommerce_checkout]', 'myaccount' => '[woocommerce_my_account]' ) as $slug => $content ) { $id = wp_insert_post( array( 'post_title' => $slug, 'post_name' => $slug, 'post_content' => $content, 'post_status' => 'publish', 'post_type' => 'page' ) ); update_option( 'woocommerce_' . $slug . '_page_id', $id ); }
	$products = array();
	foreach ( array( 'br-001', 'kids-002', 'sg-007' ) as $sku ) {
		$p = new WC_Product_Simple(); $p->set_name( 'Synthetic size fixture ' . $sku ); $p->set_sku( $sku ); $p->set_status( 'publish' ); $p->set_virtual( true ); $p->set_regular_price( '80' ); $p->set_manage_stock( true ); $p->set_stock_quantity( 30 ); $p->update_meta_data( '_is_preorder', '1' ); $p->update_meta_data( '_preorder_available', '5' ); $p->save(); $products[ $sku ] = $p->get_id();
	}
	$p = new WC_Product_Variable(); $p->set_name( 'Synthetic native variable' ); $p->set_status( 'publish' ); $p->set_virtual( true ); $a = new WC_Product_Attribute(); $a->set_name( 'native_option' ); $a->set_options( array( 'A', 'B' ) ); $a->set_variation( true ); $p->set_attributes( array( $a ) ); $p->save();
	$products['variable'] = $p->get_id();
	foreach ( array( 'A', 'B' ) as $value ) { $v = new WC_Product_Variation(); $v->set_parent_id( $p->get_id() ); $v->set_attributes( array( 'native_option' => $value ) ); $v->set_regular_price( '90' ); $v->set_virtual( true ); $v->set_status( 'publish' ); $v->save(); $products[ 'variation-' . $value ] = $v->get_id(); }
	WC_Product_Variable::sync( $p->get_id() ); update_option( 'ss_products', $products );
	// Explicit native prior-order inventory, created BEFORE enabling size history.
	$order = new WC_Order(); $order->set_customer_id( 1 ); $order->set_date_created( time() - 300 ); $order->set_billing_email( 'fixture@example.invalid' ); $order->update_meta_data( '_ss_owner', basename( SR_SIMPLE_SIZE_FIXTURE_ROOT ) );
	$item = new WC_Order_Item_Product(); $item->set_product( wc_get_product( $products['br-001'] ) ); $item->set_quantity( 1 ); $item->set_total( 80 ); $item->set_subtotal( 80 );
	$item->add_meta_data( '_skyyrose_preorder_snapshot', array( 'schema' => 'skyyrose.preorder-commercial-promise', 'schema_version' => 1, 'is_preorder' => true, 'product_id' => $products['br-001'], 'variation_id' => 0, 'configuration_source_id' => $products['br-001'], 'allocation_source_id' => $products['br-001'], 'edition_size' => null, 'available' => 5, 'expected_ship_date' => '' ), true );
	$item->add_meta_data( 'Synthetic custom history', 'preserve exactly', false ); $order->add_item( $item ); $order->calculate_totals(); $order->save(); update_option( 'ss_legacy_id', $order->get_id() );
	$state = array( 'schema' => 'skyyrose.simple-size-history.v1', 'site' => untrailingslashit( get_option( 'home' ) ), 'generation' => 'skyyrose.simple-size-order.v1', 'legacy_orders' => array( $order->get_id() => skyyrose2_simple_size_legacy_fingerprint( $order ) ) );
	add_option( 'skyyrose2_simple_size_history_v1', wp_json_encode( $state ), '', false );
	$result = array( 'products' => $products, 'legacy' => ss_order_data( $order ), 'runtime' => array( 'php' => PHP_VERSION, 'wp' => get_bloginfo( 'version' ), 'woo' => WC_VERSION, 'database' => $GLOBALS['wpdb']->get_var( 'SELECT VERSION()' ), 'socket' => $GLOBALS['wpdb']->get_var( 'SELECT @@socket' ), 'plugins' => get_option( 'active_plugins' ) ), 'sizes' => skyyrose2_simple_size_projection()['products'] );
} elseif ( 'orders' === $mode ) {
	foreach ( wc_get_orders( array( 'limit' => -1, 'orderby' => 'ID', 'order' => 'ASC', 'status' => array_keys( wc_get_order_statuses() ) ) ) as $order ) { if ( $order->get_meta( '_ss_owner' ) === basename( SR_SIMPLE_SIZE_FIXTURE_ROOT ) ) { $result[] = ss_order_data( $order ); } }
} elseif ( 'option' === $mode ) {
	$key = $args[1] ?? ''; $value = $args[2] ?? '';
	if ( ! in_array( $key, array( 'ss_drop_mode', 'ss_payment_outcome' ), true ) || ! in_array( $value, array( '', 'selected', 'generation', 'both', 'failure', 'success' ), true ) ) { throw new RuntimeException( 'Bounded option control required.' ); }
	update_option( $key, $value ); $result = array( 'ok' => true );
} elseif ( 'mutate' === $mode ) {
	$order = ss_owned_order( (int) $args[1] ); $kind = $args[2] ?? ''; $items = $order->get_items(); $item = reset( $items );
	if ( 'both' === $kind ) { $order->delete_meta_data( '_skyyrose_simple_size_generation_v1' ); $item->delete_meta_data( '_skyyrose_simple_size_v1' ); $item->delete_meta_data( 'Size' ); }
	elseif ( 'duplicate' === $kind ) { $item->add_meta_data( 'Size', $item->get_meta( 'Size' ), false ); }
	elseif ( 'conflict' === $kind ) { $item->update_meta_data( 'Size', 'INVALID' ); }
	elseif ( 'quantity' === $kind ) { $item->set_quantity( $item->get_quantity() + 1 ); }
	elseif ( 'draft' === $kind ) { $order->set_status( 'checkout-draft' ); }
	elseif ( 'completed' === $kind ) { $order->set_status( 'completed' ); }
	else { throw new RuntimeException( 'Bounded owned mutation required.' ); }
	$item->save(); $order->save(); $result = ss_order_data( new WC_Order( $order->get_id() ) );
} elseif ( 'payment-check' === $mode ) {
	$order = ss_owned_order( (int) $args[1] ); $errors = new WP_Error(); do_action( 'woocommerce_checkout_validate_order_before_payment', $order, $errors );
	$result = array( 'errors' => $errors->get_error_codes(), 'order' => ss_order_data( new WC_Order( $order->get_id() ) ) );
} elseif ( 'readback' === $mode ) {
	$order = ss_owned_order( (int) $args[1] ); wp_set_current_user( 1 );
	$admin = ''; foreach ( $order->get_items() as $item ) { $admin .= wc_display_item_meta( $item, array( 'echo' => false ) ); }
	$email = wc_get_email_order_items( $order, array( 'plain_text' => false, 'sent_to_admin' => false ) );
	$request = new WP_REST_Request( 'GET', '/wc/v3/orders/' . $order->get_id() ); $response = rest_do_request( $request );
	$result = array( 'admin_html' => $admin, 'email_html' => $email, 'rest_status' => $response->get_status(), 'rest' => $response->get_data(), 'order' => ss_order_data( new WC_Order( $order->get_id() ) ) );
} elseif ( 'pay' === $mode ) {
	$order = ss_owned_order( (int) $args[1] ); wp_set_current_user( 1 ); WC()->initialize_session(); WC()->initialize_cart(); wc_clear_notices();
	register_shutdown_function( static function() use ( $order ) { file_put_contents( SR_SIMPLE_SIZE_FIXTURE_ROOT . '/last-pay.json', wp_json_encode( array( 'notices' => wc_get_notices(), 'order' => ss_order_data( new WC_Order( $order->get_id() ) ) ) ) ); } );
	$_POST = array( 'woocommerce_pay' => '1', 'payment_method' => 'ss_offline' ); $_GET = array( 'key' => $order->get_order_key() ); $_REQUEST = array( 'woocommerce-pay-nonce' => wp_create_nonce( 'woocommerce-pay' ) ); $GLOBALS['wp']->query_vars['order-pay'] = $order->get_id(); WC_Form_Handler::pay_action(); $result = array( 'returned' => true, 'notices' => wc_get_notices() );
} else { throw new RuntimeException( 'Unknown private mode.' ); }
echo 'SS_RESULT=' . wp_json_encode( $result, JSON_THROW_ON_ERROR ) . "\n";
