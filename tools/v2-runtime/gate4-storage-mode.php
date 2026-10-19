<?php
/** Native storage authority only on the exact disposable synthetic clone. */
$root = dirname( __DIR__, 2 );
$expected = realpath( $root . '/.artifacts/release-gates-20261019/gate4-local/wordpress' );
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || realpath( ABSPATH ) !== $expected || DB_NAME !== 'sr_release_fixture' || $GLOBALS['wpdb']->get_var( 'SELECT @@socket' ) !== '/tmp/sr-gate4-01a0f768.sock' ) { throw new RuntimeException( 'Exact synthetic storage fixture required.' ); }
$mode = $args[0] ?? '';
if ( $mode === 'initialize' ) {
	$wpdb = $GLOBALS['wpdb'];
	if ( (string) $wpdb->get_var( "SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type IN ('shop_order','shop_order_refund','shop_order_placehold')" ) !== '0' ) { throw new RuntimeException( 'Order-empty fixture required before schema initialization.' ); }
	$tables = array( 'wc_orders', 'wc_order_addresses', 'wc_order_operational_data', 'wc_orders_meta', 'woocommerce_order_items', 'woocommerce_order_itemmeta' );
	foreach ( $tables as $suffix ) {
		$table = $wpdb->prefix . $suffix;
		$exists = (string) $wpdb->get_var( $wpdb->prepare( 'SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s', $table ) );
		if ( ! in_array( $exists, array( '0', '1' ), true ) || ( $exists === '1' && (string) $wpdb->get_var( "SELECT COUNT(*) FROM {$table}" ) !== '0' ) ) { throw new RuntimeException( 'Nonempty or unreadable order schema prohibits initialization.' ); }
	}
	$created = WC_Install::create_tables();
	if ( ! is_array( $created ) || $wpdb->last_error ) { throw new RuntimeException( 'Native base schema initialization failed.' ); }
	$synchronizer = wc_get_container()->get( Automattic\WooCommerce\Internal\DataStores\Orders\DataSynchronizer::class );
	if ( $synchronizer->create_database_tables() !== true || $wpdb->last_error ) { throw new RuntimeException( 'Native order schema initialization failed.' ); }
	$empty_schema = array();
	foreach ( $tables as $suffix ) {
		$table = $wpdb->prefix . $suffix;
		if ( (string) $wpdb->get_var( "SELECT COUNT(*) FROM {$table}" ) !== '0' ) { throw new RuntimeException( 'Fresh native order tables must all be empty.' ); }
		$empty_schema[ $suffix ] = 0;
	}
} elseif ( $mode === 'set' ) {
	$authority = $args[1] ?? ''; $sync = $args[2] ?? '';
	if ( ! in_array( $authority, array( 'yes', 'no' ), true ) || ! in_array( $sync, array( 'yes', 'no' ), true ) ) { throw new RuntimeException( 'Explicit synthetic yes/no settings required.' ); }
	update_option( 'woocommerce_custom_orders_table_enabled', $authority );
	update_option( 'woocommerce_custom_orders_table_data_sync_enabled', $sync );
} elseif ( $mode !== 'inspect' ) { throw new RuntimeException( 'Unknown fixture storage mode.' ); }
$order = new WC_Order();
echo wp_json_encode( array( 'ok' => true, 'authority_option' => get_option( 'woocommerce_custom_orders_table_enabled' ), 'sync_option' => get_option( 'woocommerce_custom_orders_table_data_sync_enabled' ), 'hpos' => Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled(), 'native_store_class' => $order->get_data_store()->get_current_class_name(), 'initialized_empty_tables' => $empty_schema ?? null, 'php_version' => PHP_VERSION, 'memory_limit' => ini_get( 'memory_limit' ), 'wp_version' => get_bloginfo( 'version' ), 'woocommerce_version' => WC_VERSION ) );
