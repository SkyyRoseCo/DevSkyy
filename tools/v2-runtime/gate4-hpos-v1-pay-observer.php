<?php
/** Request-bound attribution of native gateway selection before a named refusal. */
$g4o_root = dirname( __DIR__, 2 );
$g4o_run = getenv( 'SR_POPULATED_RUN' );
if ( ! is_string( $g4o_run ) || ! preg_match( '/^[0-9]{19}$/D', $g4o_run ) ) { throw new RuntimeException( 'Exact observer run required.' ); }
$g4o_private = $g4o_root . '/.artifacts/release-gates-20261019/gate4-populated/run-' . $g4o_run;
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== 'sr_release_fixture' || realpath( ABSPATH ) !== realpath( $g4o_private . '/wordpress' ) || $GLOBALS['wpdb']->get_var( 'SELECT @@socket' ) !== '/tmp/sr-g4-pop-' . substr( $g4o_run, -12 ) . '.sock' || get_option( 'home' ) !== 'http://127.0.0.1:18362' || ! Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled() ) { throw new RuntimeException( 'Exact private HPOS observer identity required.' ); }
$g4o_label = $args[4] ?? '';
if ( ( $args[0] ?? '' ) !== 'pay' || ! in_array( $g4o_label, array( 'v1-missing-id', 'v1-ambiguous-sku', 'active-journal' ), true ) ) { throw new RuntimeException( 'Named refusal observer only.' ); }
$g4o_case = json_decode( file_get_contents( $g4o_private . '/case.json' ), true, 512, JSON_THROW_ON_ERROR );
$g4o_id = $g4o_case['orders'][ $args[1] ?? '' ] ?? 0;
$g4o_order = wc_get_order( $g4o_id );
if ( ! $g4o_id || $g4o_case['run'] !== $g4o_run || ! $g4o_order || $g4o_order->get_meta( '_g4_owner', true ) !== $g4o_run || $g4o_order->get_data_store()->get_current_class_name() !== Automattic\WooCommerce\Internal\DataStores\Orders\OrdersTableDataStore::class ) { throw new RuntimeException( 'Owned native HPOS order required.' ); }
$g4o_trace = static function () { return array_map( static fn( $frame ) => array_intersect_key( $frame, array_flip( array( 'file', 'line', 'function', 'class', 'type' ) ) ), debug_backtrace( DEBUG_BACKTRACE_IGNORE_ARGS ) ); };
$g4o_read = static function () use ( $g4o_id ) { global $wpdb; $row = $wpdb->get_row( $wpdb->prepare( "SELECT * FROM {$wpdb->prefix}wc_orders WHERE id=%d", $g4o_id ), ARRAY_A ); if ( $wpdb->last_error || ! is_array( $row ) || $row['id'] !== (string) $g4o_id || $row['type'] !== 'shop_order' ) { throw new RuntimeException( 'Observer raw owned order missing.' ); } return $row; };
$g4o_audit = array( 'run' => $g4o_run, 'label' => $g4o_label, 'id' => $g4o_id, 'start_epoch' => microtime( true ), 'raw_before' => $g4o_read(), 'queries' => array(), 'saves' => array(), 'source_pins' => array() );
$g4o_audit['unique_indexes'] = $GLOBALS['wpdb']->get_results( "SHOW INDEX FROM {$GLOBALS['wpdb']->prefix}wc_orders WHERE Non_unique=0", ARRAY_A );
$g4o_audit['error_at_start'] = error_get_last();
foreach ( array( 'wp-content/plugins/woocommerce/includes/class-wc-form-handler.php', 'wp-content/plugins/woocommerce/includes/class-wc-order.php', 'wp-content/plugins/woocommerce/includes/abstracts/abstract-wc-order.php', 'wp-content/plugins/woocommerce/includes/class-wc-data-store.php', 'wp-content/plugins/woocommerce/src/Internal/DataStores/Orders/OrdersTableDataStore.php', 'wp-content/plugins/woocommerce/src/Internal/Utilities/DatabaseUtil.php', 'wp-content/themes/skyyrose-flagship-2/inc/woocommerce-compat.php' ) as $g4o_source ) { $g4o_file = ABSPATH . $g4o_source; $g4o_audit['source_pins'][ $g4o_source ] = array( 'sha256' => hash_file( 'sha256', $g4o_file ), 'bytes' => filesize( $g4o_file ) ); }
add_filter( 'query', static function ( $sql ) use ( &$g4o_audit, $g4o_trace ) { if ( preg_match( '/^\s*(INSERT|UPDATE|REPLACE|DELETE|CREATE|ALTER|DROP|TRUNCATE)\b/i', $sql ) ) { if ( count( $g4o_audit['queries'] ) >= 500 ) { throw new RuntimeException( 'Observer DML budget exceeded.' ); } $g4o_audit['queries'][] = array( 'sql' => $sql, 'epoch' => microtime( true ), 'stack' => $g4o_trace() ); } return $sql; }, PHP_INT_MAX );
foreach ( array( 'before', 'after' ) as $g4o_phase ) { add_action( 'woocommerce_' . $g4o_phase . '_order_object_save', static function ( $order ) use ( &$g4o_audit, $g4o_trace, $g4o_phase ) { $g4o_audit['saves'][] = array( 'phase' => $g4o_phase, 'id' => $order->get_id(), 'epoch' => microtime( true ), 'stack' => $g4o_trace() ); }, PHP_INT_MAX ); }
register_shutdown_function( static function () use ( &$g4o_audit, $g4o_read, $g4o_private, $g4o_label ) {
    try { $g4o_audit['raw_after'] = $g4o_read(); $g4o_audit['end_epoch'] = microtime( true ); $g4o_audit['last_error'] = error_get_last(); }
    catch ( Throwable $error ) { $g4o_audit['observer_failure'] = get_class( $error ); }
    $file = fopen( $g4o_private . '/gateway-selection-' . $g4o_label . '.json', 'x' );
    if ( false === $file ) { throw new RuntimeException( 'Observer receipt already exists or cannot be written.' ); }
    fwrite( $file, wp_json_encode( $g4o_audit, JSON_THROW_ON_ERROR | JSON_PRESERVE_ZERO_FRACTION ) . "\n" ); fclose( $file ); chmod( $g4o_private . '/gateway-selection-' . $g4o_label . '.json', 0600 );
} );
require __DIR__ . '/gate4-populated-fixture.php';
