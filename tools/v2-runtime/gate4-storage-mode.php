<?php
/** Native storage authority only on the exact disposable synthetic clone. */
$root = dirname( __DIR__, 2 );
$expected = realpath( $root . '/.artifacts/release-gates-20261019/gate4-local/wordpress' );
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || realpath( ABSPATH ) !== $expected || DB_NAME !== 'sr_release_fixture' || $GLOBALS['wpdb']->get_var( 'SELECT @@socket' ) !== '/tmp/sr-gate4-01a0f768.sock' ) { throw new RuntimeException( 'Exact synthetic storage fixture required.' ); }
$mode = $args[0] ?? '';
if ( $mode === 'set' ) {
	$authority = $args[1] ?? ''; $sync = $args[2] ?? '';
	if ( ! in_array( $authority, array( 'yes', 'no' ), true ) || ! in_array( $sync, array( 'yes', 'no' ), true ) ) { throw new RuntimeException( 'Explicit synthetic yes/no settings required.' ); }
	update_option( 'woocommerce_custom_orders_table_enabled', $authority );
	update_option( 'woocommerce_custom_orders_table_data_sync_enabled', $sync );
} elseif ( $mode !== 'inspect' ) { throw new RuntimeException( 'Unknown fixture storage mode.' ); }
$order = new WC_Order();
echo wp_json_encode( array( 'ok' => true, 'authority_option' => get_option( 'woocommerce_custom_orders_table_enabled' ), 'sync_option' => get_option( 'woocommerce_custom_orders_table_data_sync_enabled' ), 'hpos' => Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled(), 'native_store_class' => $order->get_data_store()->get_current_class_name() ) );
