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
function ss_normalize( $value ) {
	if ( $value instanceof DateTimeInterface ) { return $value->format( 'c' ); }
	if ( $value instanceof WC_Meta_Data ) { $value = $value->get_data(); }
	return is_array( $value ) ? array_map( 'ss_normalize', $value ) : $value;
}
function ss_order_data( $order ) {
	global $wpdb;
	ss_assert_identity( true );
	$items = array(); foreach ( $order->get_items() as $item ) { $items[] = $item->get_data(); }
	$raw = array(); foreach ( $items as $item ) { $raw = array_merge( $raw, ss_raw_results( $wpdb->prepare( "SELECT meta_id,order_item_id,meta_key,meta_value FROM {$wpdb->prefix}woocommerce_order_itemmeta WHERE order_item_id=%d AND meta_key IN ('_skyyrose_simple_size_v1','Size') ORDER BY meta_id", $item['id'] ) ) ); }
	$hpos = Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled();
	$generation_sql = $hpos ? "SELECT id,order_id,meta_key,meta_value FROM {$wpdb->prefix}wc_orders_meta WHERE order_id=%d AND meta_key='_skyyrose_simple_size_generation_v1' ORDER BY id" : "SELECT meta_id AS id,post_id AS order_id,meta_key,meta_value FROM {$wpdb->postmeta} WHERE post_id=%d AND meta_key='_skyyrose_simple_size_generation_v1' ORDER BY meta_id";
	$generation_raw = ss_raw_results( $wpdb->prepare( $generation_sql, $order->get_id() ) );
	$stock = array(); foreach ( $order->get_items() as $item ) { $product = wc_get_product( $item->get_product_id() ); $stock[ $item->get_product_id() ] = $product ? $product->get_stock_quantity() : null; }
	$date = $order->get_date_paid();
	$store = $order->get_data_store()->get_current_class_name();
	if ( $store !== ( SR_SIMPLE_SIZE_STORAGE === 'hpos' ? 'Automattic\\WooCommerce\\Internal\\DataStores\\Orders\\OrdersTableDataStore' : 'WC_Order_Data_Store_CPT' ) ) { throw new RuntimeException( 'Observed order datastore differs.' ); }
	return array( 'id' => $order->get_id(), 'status' => $order->get_status(), 'key' => $order->get_order_key(), 'items' => ss_normalize( $items ), 'native_data' => ss_normalize( $order->get_data() ), 'fixture_order_meta' => array_values( array_map( static fn( $meta ) => ss_normalize( $meta->get_data() ), array_filter( $order->get_meta_data(), static fn( $meta ) => str_starts_with( $meta->get_data()['key'], '_ss_' ) ) ) ), 'generation' => skyyrose2_simple_size_meta_values( $order, '_skyyrose_simple_size_generation_v1' ), 'raw_size_rows' => $raw, 'raw_generation_rows' => $generation_raw, 'paid' => (bool) $date, 'paid_timestamp' => $date ? $date->getTimestamp() : null, 'transaction_id' => $order->get_transaction_id( 'edit' ), 'total' => $order->get_total( 'edit' ), 'stock' => $stock, 'stock_reduced' => (bool) $order->get_data_store()->get_stock_reduced( $order->get_id() ), 'cart_hash' => $order->get_cart_hash(), 'data_store' => $store );
}
$mode = $args[0] ?? '';
$result = array();
if ( 'init' === $mode ) {
	if ( get_option( 'ss_products' ) || get_option( 'skyyrose2_simple_size_history_v1' ) ) { throw new RuntimeException( 'Fresh fixture only; no inventory adoption.' ); }
	WC_Install::install();
	update_option( 'woocommerce_custom_orders_table_enabled', SR_SIMPLE_SIZE_STORAGE === 'hpos' ? 'yes' : 'no' );
	update_option( 'woocommerce_custom_orders_table_data_sync_enabled', 'no' );
	update_option( 'woocommerce_currency', 'USD' ); update_option( 'woocommerce_default_country', 'US:CA' ); update_option( 'woocommerce_calc_taxes', 'no' );
	foreach ( array( 'cart' => '[woocommerce_cart]', 'checkout' => '[woocommerce_checkout]', 'myaccount' => '[woocommerce_my_account]' ) as $slug => $content ) { $id = wp_insert_post( array( 'post_title' => $slug, 'post_name' => $slug, 'post_content' => $content, 'post_status' => 'publish', 'post_type' => 'page' ) ); update_option( 'woocommerce_' . $slug . '_page_id', $id ); }
	$products = array();
	foreach ( array( 'br-001', 'kids-002', 'sg-007' ) as $sku ) {
		$p = new WC_Product_Simple(); $p->set_name( 'Synthetic size fixture ' . $sku ); $p->set_sku( $sku ); $p->set_status( 'publish' ); $p->set_virtual( true ); $p->set_regular_price( '80' ); $p->set_manage_stock( true ); $p->set_stock_quantity( 120 ); $p->update_meta_data( '_is_preorder', '1' ); $p->update_meta_data( '_preorder_available', '5' ); $p->save(); $products[ $sku ] = $p->get_id();
	}
	$p = new WC_Product_Variable(); $p->set_name( 'Synthetic native variable' ); $p->set_status( 'publish' ); $p->set_virtual( true ); $a = new WC_Product_Attribute(); $a->set_name( 'native_option' ); $a->set_options( array( 'A', 'B' ) ); $a->set_variation( true ); $p->set_attributes( array( $a ) ); $p->save();
	$products['variable'] = $p->get_id();
	foreach ( array( 'A', 'B' ) as $value ) { $v = new WC_Product_Variation(); $v->set_parent_id( $p->get_id() ); $v->set_attributes( array( 'native_option' => $value ) ); $v->set_regular_price( '90' ); $v->set_virtual( true ); $v->set_status( 'publish' ); $v->save(); $products[ 'variation-' . $value ] = $v->get_id(); }
	WC_Product_Variable::sync( $p->get_id() ); update_option( 'ss_products', $products );
	// Explicit native prior-order inventory, created BEFORE enabling size history.
	$producer = __DIR__ . '/fixtures/historical-preorder-producer.php';
	$producer_bytes = file_get_contents( $producer );
	if ( ! is_string( $producer_bytes ) || hash( 'sha256', $producer_bytes ) !== 'b7dd7bc02c3167803f986d05e13975e40e064cd4ddeb23ea6081b4192e34a42a' || hash( 'sha256', substr( $producer_bytes, 6, -1 ) ) !== 'ad5444fd708f1d26eca843b0e6658f525718ffeaaff3460e5cec44e79c35e16b' || function_exists( 'skyyrose_create_preorder_snapshot' ) || ! function_exists( 'absint' ) ) { throw new RuntimeException( 'Exact isolated historical producer and native dependency required.' ); }
	require $producer;
	$promise = skyyrose_create_preorder_snapshot( array( 'product_id' => $products['br-001'], 'configuration_source_id' => $products['br-001'], 'allocation_source_id' => $products['br-001'], 'available' => 5 ) );
	if ( $promise['available_at_add_to_cart'] !== 5 || $promise['schema_version'] !== 1 || isset( $promise['available'] ) || isset( $promise['sku'] ) || isset( $promise['attributes'] ) || isset( $promise['capture_point'] ) ) { throw new RuntimeException( 'Historical producer schema changed.' ); }
	$order = new WC_Order(); $order->set_customer_id( 1 ); $order->set_date_created( time() - 300 ); $order->set_billing_email( 'fixture@example.invalid' ); ss_new_order_history( $order );
	$item = new WC_Order_Item_Product(); $item->set_product( wc_get_product( $products['br-001'] ) ); $item->set_quantity( 1 ); $item->set_total( 80 ); $item->set_subtotal( 80 );
	$item->add_meta_data( '_skyyrose_preorder_snapshot', $promise, true );
	$item->add_meta_data( 'Synthetic custom history', 'preserve exactly', false ); $item->add_meta_data( '_ss_typed_history', array( 'boolean' => true, 'fractional' => 1.0, 'integer' => 1 ), true ); $order->add_item( $item ); $order->calculate_totals(); $order->save(); update_option( 'ss_legacy_id', $order->get_id() );
	$state = array( 'schema' => 'skyyrose.simple-size-history.v1', 'site' => untrailingslashit( get_option( 'home' ) ), 'generation' => 'skyyrose.simple-size-order.v1', 'legacy_orders' => array( $order->get_id() => skyyrose2_simple_size_legacy_fingerprint( $order ) ) );
	add_option( 'skyyrose2_simple_size_history_v1', wp_json_encode( $state ), '', false );
	$result = array( 'products' => $products, 'legacy' => ss_order_data( $order ), 'historical_producer' => array( 'wrapper_sha256' => hash( 'sha256', $producer_bytes ), 'function_sha256' => hash( 'sha256', substr( $producer_bytes, 6, -1 ) ), 'old_hooks_loaded' => false, 'promise' => $promise ), 'runtime' => array( 'php' => PHP_VERSION, 'wp' => get_bloginfo( 'version' ), 'woo' => WC_VERSION, 'database' => $GLOBALS['wpdb']->get_var( 'SELECT VERSION()' ), 'socket' => $GLOBALS['wpdb']->get_var( 'SELECT @@socket' ), 'plugins' => get_option( 'active_plugins' ) ), 'sizes' => skyyrose2_simple_size_projection()['products'] );
} elseif ( 'orders' === $mode ) {
	foreach ( wc_get_orders( array( 'limit' => -1, 'orderby' => 'ID', 'order' => 'ASC', 'status' => array_keys( wc_get_order_statuses() ) ) ) as $order ) { if ( $order->get_meta( '_ss_owner' ) === basename( SR_SIMPLE_SIZE_FIXTURE_ROOT ) ) { $result[] = ss_order_data( $order ); } }
} elseif ( 'order' === $mode ) {
	$result = ss_order_data( ss_owned_order( (int) $args[1] ) );
} elseif ( 'history' === $mode ) {
	$path = SR_SIMPLE_SIZE_FIXTURE_ROOT . '/history-preimage.json';
	if ( 'remove' === ( $args[1] ?? '' ) ) {
		$raw = $GLOBALS['wpdb']->get_var( "SELECT option_value FROM {$GLOBALS['wpdb']->options} WHERE option_name='skyyrose2_simple_size_history_v1'" );
		if ( ! is_string( $raw ) || file_exists( $path ) || is_link( $path ) ) { throw new RuntimeException( 'Exact history preimage required.' ); }
		$handle = fopen( $path, 'x' ); if ( ! $handle || strlen( $raw ) !== fwrite( $handle, $raw ) || ! fflush( $handle ) || ! fsync( $handle ) ) { throw new RuntimeException( 'History preimage persistence failed.' ); } fclose( $handle );
		if ( ! delete_option( 'skyyrose2_simple_size_history_v1' ) ) { throw new RuntimeException( 'History removal failed.' ); }
		$result = array( 'removed' => true, 'preimage_sha256' => hash( 'sha256', $raw ) );
	} elseif ( 'restore' === ( $args[1] ?? '' ) && ! get_option( 'skyyrose2_simple_size_history_v1' ) && is_file( $path ) ) {
		$raw = file_get_contents( $path ); add_option( 'skyyrose2_simple_size_history_v1', $raw, '', false );
		$actual = $GLOBALS['wpdb']->get_var( "SELECT option_value FROM {$GLOBALS['wpdb']->options} WHERE option_name='skyyrose2_simple_size_history_v1'" );
		if ( $actual !== $raw ) { throw new RuntimeException( 'History preimage restore differs.' ); }
		$result = array( 'restored' => true, 'preimage_sha256' => hash( 'sha256', $raw ) );
	} else { throw new RuntimeException( 'One bounded history control required.' ); }
} elseif ( 'pool' === $mode ) {
	$products = get_option( 'ss_products' ); $product = wc_get_product( $products['br-001'] ); $value = $args[1] ?? '';
	if ( ! in_array( $value, array( '1', '5' ), true ) ) { throw new RuntimeException( 'Bounded pool control required.' ); }
	$product->update_meta_data( '_preorder_available', $value ); $product->save(); $result = array( 'available' => $value );
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
	elseif ( 'variable-remove' === $kind || 'variable-alter' === $kind ) {
		$found = false; foreach ( $items as $candidate ) { if ( $candidate->get_variation_id() ) { $found = true; if ( 'variable-remove' === $kind ) { $order->remove_item( $candidate->get_id() ); } else { $products = get_option( 'ss_products' ); $candidate->set_variation_id( $products['variation-B'] ); $candidate->set_quantity( $candidate->get_quantity() + 1 ); $candidate->save(); } break; } }
		if ( ! $found ) { throw new RuntimeException( 'Mixed order variable line required.' ); }
	}
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
	$label = $args[2] ?? ''; if ( ! preg_match( '/^pay-[0-9]+$/D', $label ) ) { throw new RuntimeException( 'Unique bounded payment label required.' ); }
	$path = SR_SIMPLE_SIZE_FIXTURE_ROOT . '/' . $label . '.json'; if ( file_exists( $path ) ) { throw new RuntimeException( 'Payment receipt already exists.' ); }
	ss_event( 'native_pay_started', array( 'id' => $order->get_id(), 'label' => $label, 'at' => time() ) );
	register_shutdown_function( static function() use ( $order, $path, $label ) { ss_event( 'native_pay_finished', array( 'id' => $order->get_id(), 'label' => $label, 'at' => time() ) ); $body = wp_json_encode( array( 'notices' => wc_get_notices(), 'order' => ss_order_data( new WC_Order( $order->get_id() ) ) ), JSON_THROW_ON_ERROR | JSON_PRESERVE_ZERO_FRACTION ); $handle = fopen( $path, 'x' ); if ( ! $handle || strlen( $body ) !== fwrite( $handle, $body ) || ! fflush( $handle ) || ! fsync( $handle ) ) { throw new RuntimeException( 'Payment evidence persistence failed.' ); } fclose( $handle ); } );
	add_action( 'woocommerce_before_order_object_save', static function( $saved ) use ( $order ) { if ( $saved->get_id() === $order->get_id() ) { ss_event( 'native_pay_order_save', array( 'id' => $saved->get_id(), 'fields' => array_keys( $saved->get_changes() ), 'stack' => array_map( static fn( $frame ) => array( 'class' => $frame['class'] ?? '', 'function' => $frame['function'] ?? '' ), debug_backtrace( DEBUG_BACKTRACE_IGNORE_ARGS, 40 ) ) ) ); } }, PHP_INT_MAX );
	add_action( 'woocommerce_after_order_object_save', static function( $saved ) use ( $order, $label ) { if ( $saved->get_id() === $order->get_id() ) { ss_event( 'native_pay_order_saved', array( 'id' => $saved->get_id(), 'label' => $label, 'at' => time(), 'values' => ss_normalize( $saved->get_data() ), 'stack' => array_map( static fn( $frame ) => array( 'class' => $frame['class'] ?? '', 'function' => $frame['function'] ?? '' ), debug_backtrace( DEBUG_BACKTRACE_IGNORE_ARGS, 40 ) ) ) ); } }, PHP_INT_MAX );
	$_POST = array( 'woocommerce_pay' => '1', 'payment_method' => 'ss_offline' ); $_GET = array( 'key' => $order->get_order_key() ); $_REQUEST = array( 'woocommerce-pay-nonce' => wp_create_nonce( 'woocommerce-pay' ) ); $GLOBALS['wp']->query_vars['order-pay'] = $order->get_id(); WC_Form_Handler::pay_action(); $result = array( 'returned' => true, 'notices' => wc_get_notices() );
} else { throw new RuntimeException( 'Unknown private mode.' ); }
echo 'SS_RESULT=' . wp_json_encode( $result, JSON_THROW_ON_ERROR | JSON_PRESERVE_ZERO_FRACTION ) . "\n";
