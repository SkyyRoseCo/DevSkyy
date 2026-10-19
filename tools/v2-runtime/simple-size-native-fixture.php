<?php
/** PRIVATE SYNTHETIC fixture MU plugin. Never package or install on a real site. */
defined( 'ABSPATH' ) || exit;
function ss_assert_identity( $native = false ) {
	if ( ! defined( 'SR_SIMPLE_SIZE_FIXTURE_ROOT' ) || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== 'sr_simple_size_fixture' || realpath( ABSPATH ) !== realpath( SR_SIMPLE_SIZE_FIXTURE_ROOT . '/wordpress' ) || ! preg_match( '/^run-([0-9]{19})$/D', basename( SR_SIMPLE_SIZE_FIXTURE_ROOT ), $match ) || DB_HOST !== 'localhost:/private/tmp/sr-size-' . substr( $match[1], -12 ) . '.sock' ) { throw new RuntimeException( 'Exact private synthetic identity required.' ); }
	if ( $native ) {
		$row = $GLOBALS['wpdb']->get_row( 'SELECT @@socket AS socket,@@datadir AS datadir,@@skip_networking AS offline,@@event_scheduler AS scheduler', ARRAY_A );
		if ( ! $row || $row['socket'] !== substr( DB_HOST, 10 ) || realpath( $row['datadir'] ) !== realpath( SR_SIMPLE_SIZE_FIXTURE_ROOT . '/mysql' ) || '1' !== $row['offline'] || 'OFF' !== $row['scheduler'] || get_option( 'home' ) !== 'http://127.0.0.1:18368' ) { throw new RuntimeException( 'Exact native database/socket/home required.' ); }
	}
}
ss_assert_identity();
add_filter( 'pre_http_request', static fn() => new WP_Error( 'synthetic_offline', 'Outbound HTTP prohibited.' ), PHP_INT_MAX );
add_filter( 'pre_wp_mail', '__return_true', PHP_INT_MAX );
add_filter( 'woocommerce_webhook_should_deliver', '__return_false', PHP_INT_MAX );
add_filter( 'woocommerce_allow_tracking', '__return_false', PHP_INT_MAX );
add_filter( 'action_scheduler_allow_async_request_runner', '__return_false', PHP_INT_MAX );
add_filter( 'automatic_updater_disabled', '__return_true', PHP_INT_MAX );
function ss_event( $event, $data = array() ) {
	$body = wp_json_encode( array( 'event' => $event, 'pid' => getmypid(), 'data' => $data ), JSON_THROW_ON_ERROR ) . "\n";
	if ( strlen( $body ) !== file_put_contents( SR_SIMPLE_SIZE_FIXTURE_ROOT . '/events.jsonl', $body, FILE_APPEND | LOCK_EX ) ) { throw new RuntimeException( 'Synthetic event persistence failed.' ); }
}
add_action( 'plugins_loaded', static function() {
	if ( ! class_exists( 'WC_Payment_Gateway' ) ) { return; }
	class SS_Offline_Gateway extends WC_Payment_Gateway {
		public function __construct() { $this->id = 'ss_offline'; $this->enabled = 'yes'; $this->title = 'Synthetic offline'; $this->supports = array( 'products' ); }
		public function process_payment( $id ) {
			ss_event( 'processor_entered', array( 'id' => (int) $id ) );
			if ( get_option( 'ss_payment_outcome', 'failure' ) !== 'success' ) { return array( 'result' => 'failure' ); }
			$order = wc_get_order( $id ); $order->payment_complete( 'synthetic-size-' . $id );
			return array( 'result' => 'success', 'redirect' => $this->get_return_url( $order ) );
		}
	}
	add_filter( 'woocommerce_payment_gateways', static fn() => array( 'SS_Offline_Gateway' ), PHP_INT_MAX );
}, 30 );
add_action( 'woocommerce_checkout_create_order', static function( $order ) { $order->update_meta_data( '_ss_owner', basename( SR_SIMPLE_SIZE_FIXTURE_ROOT ) ); }, 90 );
add_action( 'woocommerce_store_api_checkout_order_created', static function( $order ) { $order->update_meta_data( '_ss_owner', basename( SR_SIMPLE_SIZE_FIXTURE_ROOT ) ); $order->save(); }, 90 );

/** Controlled dropped persistence, not an in-memory mutation of the validator's input. */
add_filter( 'query', static function( $sql ) {
	$mode = $GLOBALS['ss_drop_mode'] ?? null;
	if ( ! $mode || ! preg_match( '/^\s*INSERT\s+INTO\s+`?wp_(?:wc_orders_meta|postmeta|woocommerce_order_itemmeta)`?\s/i', $sql ) ) { return $sql; }
	$keys = 'selected' === $mode ? array( '_skyyrose_simple_size_v1' ) : ( 'generation' === $mode ? array( '_skyyrose_simple_size_generation_v1' ) : array( '_skyyrose_simple_size_v1', '_skyyrose_simple_size_generation_v1', 'Size' ) );
	foreach ( $keys as $key ) {
		if ( str_contains( $sql, "'" . $key . "'" ) ) {
			ss_event( 'dropped_persistence', array( 'key' => $key, 'sql_sha256' => hash( 'sha256', $sql ) ) );
			return 'SELECT 1';
		}
	}
	return $sql;
}, PHP_INT_MAX );
add_action( 'init', static function() { $GLOBALS['ss_drop_mode'] = get_option( 'ss_drop_mode', '' ); }, 1 );

/** Private controls for a loopback-only disposable server. All identities synthetic. */
add_action( 'template_redirect', static function() {
	if ( ! isset( $_GET['ss_control'] ) ) { return; }
	if ( ! in_array( $_SERVER['REMOTE_ADDR'] ?? '', array( '127.0.0.1', '::1' ), true ) ) { status_header( 403 ); exit; }
	ss_assert_identity( true );
	WC()->initialize_session(); WC()->initialize_cart();
	WC()->session->set_customer_session_cookie( true );
	$mode = $_GET['ss_control'];
	if ( 'inspect' === $mode ) {
		$cart = array(); foreach ( WC()->cart->get_cart() as $key => $value ) { $cart[] = array( 'key' => $key, 'id' => $value['product_id'], 'variation_id' => $value['variation_id'], 'quantity' => $value['quantity'], 'size' => $value['skyyrose_simple_size'] ?? null, 'promise' => $value['skyyrose_preorder_snapshot'] ?? null ); }
		wp_send_json( array( 'cart' => $cart, 'nonce' => wp_create_nonce( 'woocommerce-process_checkout' ), 'store_nonce' => wp_create_nonce( 'wc_store_api' ), 'notices' => wc_get_notices(), 'session_id' => WC()->session->get_customer_id(), 'draft' => WC()->session->get( 'store_api_draft_order', 0 ) ) );
	}
	if ( 'empty' === $mode ) { WC()->cart->empty_cart(); WC()->session->set( 'store_api_draft_order', 0 ); WC()->session->set( 'order_awaiting_payment', 0 ); wc_clear_notices(); wp_send_json( array( 'ok' => true ) ); }
	if ( 'tamper' === $mode ) {
		foreach ( WC()->cart->get_cart() as $key => $value ) { unset( WC()->cart->cart_contents[ $key ]['skyyrose_simple_size'] ); }
		WC()->cart->set_session(); wp_send_json( array( 'ok' => true ) );
	}
	if ( 'draft' === $mode ) { WC()->session->set( 'store_api_draft_order', absint( $_GET['id'] ?? 0 ) ); wp_send_json( array( 'ok' => true ) ); }
	if ( 'login' === $mode ) { wp_set_current_user( 1 ); wp_set_auth_cookie( 1 ); wp_send_json( array( 'ok' => true ) ); }
	if ( 'again-url' === $mode ) { wp_send_json( array( 'url' => wc_get_endpoint_url( 'orders', '', wc_get_page_permalink( 'myaccount' ) ), 'nonce' => wp_create_nonce( 'woocommerce-order_again' ) ) ); }
	wp_send_json_error( 'Unknown private control', 400 );
}, 0 );
