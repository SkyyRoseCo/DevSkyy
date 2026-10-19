<?php
/** New run-owned synthetic fixture; no browser, provider or installed-runtime claim. */
// WP-CLI eval-file executes in a method scope; helpers must share the exact run context.
global $root, $run, $private, $mode, $state_file, $case;
$root = dirname( __DIR__, 2 );
$run = getenv( 'SR_POPULATED_RUN' );
if ( ! is_string( $run ) || ! preg_match( '/^[0-9]{19}$/D', $run ) ) { throw new RuntimeException( 'Exact run identity required.' ); }
$private = $root . '/.artifacts/release-gates-20261019/gate4-populated/run-' . $run;
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== 'sr_release_fixture' || realpath( ABSPATH ) !== realpath( $private . '/wordpress' ) || $GLOBALS['wpdb']->get_var( 'SELECT @@socket' ) !== ( '/tmp/sr-g4-pop-' . substr( $run, -12 ) . '.sock' ) || get_option( 'home' ) !== 'http://127.0.0.1:18362' ) { throw new RuntimeException( 'Exact disposable populated identity required.' ); }
$mode = $args[0] ?? '';
$state_file = $private . '/case.json';
$case = file_exists( $state_file ) ? json_decode( file_get_contents( $state_file ), true, 512, JSON_THROW_ON_ERROR ) : array( 'run' => $run, 'orders' => array(), 'products' => array(), 'created' => array(), 'deleted' => array(), 'writes_closed' => false );
if ( $case['run'] !== $run ) { throw new RuntimeException( 'Foreign case refused.' ); }
function g4p_json( $value, $flags = 0 ) { return wp_json_encode( $value, $flags | JSON_PRESERVE_ZERO_FRACTION | JSON_THROW_ON_ERROR ); }
function g4p_save() { global $case, $state_file; file_put_contents( $state_file, g4p_json( $case, JSON_THROW_ON_ERROR ), LOCK_EX ); chmod( $state_file, 0600 ); }
function g4p_event( $event, $id = 0 ) { global $private, $run; $row = array( 'run' => $run, 'request' => $GLOBALS['g4p_request'] ?? 'non-payment', 'event' => $event, 'order_id' => (int) $id, 'pid' => getmypid() ); file_put_contents( $private . '/events.jsonl', g4p_json( $row ) . "\n", FILE_APPEND | LOCK_EX ); }
function g4p_normalize( $value ) {
    if ( $value instanceof DateTimeInterface ) { return $value->format( 'c' ); }
    if ( $value instanceof WC_Meta_Data ) { $value = $value->get_data(); unset( $value['id'] ); }
    elseif ( is_object( $value ) && method_exists( $value, 'get_data' ) ) { $value = $value->get_data(); }
    if ( is_array( $value ) ) {
        $value = array_map( 'g4p_normalize', $value );
        if ( array_is_list( $value ) && $value && is_array( $value[0] ) && array_key_exists( 'key', $value[0] ) && array_key_exists( 'value', $value[0] ) ) { usort( $value, static fn( $a, $b ) => strcmp( g4p_json( $a ), g4p_json( $b ) ) ); }
        elseif ( ! array_is_list( $value ) ) { ksort( $value ); }
    }
    return $value;
}
function g4p_owned( $id ) { global $run; $order = wc_get_order( $id ); if ( ! $order || $order->get_meta( '_g4_owner', true ) !== $run ) { throw new RuntimeException( 'Native order ownership required.' ); } return $order; }
function g4p_immutable( $order ) {
    $items = array(); foreach ( $order->get_items( array( 'line_item', 'fee', 'shipping', 'tax', 'coupon' ) ) as $item ) { $data = $item->get_data(); unset( $data['meta_data'] ); $data['promise'] = $item->get_meta( '_skyyrose_preorder_snapshot', true ); $data['promise_rows'] = array_values( array_map( static fn( $meta ) => g4p_normalize( $meta->get_data()['value'] ), array_filter( $item->get_meta_data(), static fn( $meta ) => $meta->get_data()['key'] === '_skyyrose_preorder_snapshot' ) ) ); $items[ $item->get_id() ] = g4p_normalize( $data ); }
    return array( 'id' => $order->get_id(), 'parent_id' => $order->get_parent_id(), 'created' => $order->get_date_created()->getTimestamp(), 'currency' => $order->get_currency(), 'total' => $order->get_total(), 'tax' => $order->get_total_tax(), 'items' => $items );
}
function g4p_order_data( $order ) {
    global $wpdb;
    $items = array(); foreach ( $order->get_items( array( 'line_item', 'fee', 'shipping', 'tax', 'coupon' ) ) as $item ) { $items[ $item->get_id() ] = g4p_normalize( $item->get_data() ); }
    $data = $order->get_data(); $indexes = array(); $expected_indexes = array();
    if ( $order instanceof WC_Order ) {
        $hpos = is_a( $order->get_data_store()->get_current_class_name(), Automattic\WooCommerce\Internal\DataStores\Orders\OrdersTableDataStore::class, true );
        $table = $hpos ? $wpdb->prefix . 'wc_orders_meta' : $wpdb->postmeta; $id_column = $hpos ? 'order_id' : 'post_id'; $meta_id = $hpos ? 'id' : 'meta_id';
        foreach ( array( 'billing', 'shipping' ) as $address_type ) {
            $key = '_' . $address_type . '_address_index';
            // Native construction order and whitespace must precede normalized JSON sorting.
            $expected_indexes[ $key ] = implode( ' ', $order->get_address( $address_type ) );
            $indexes[ $key ] = $wpdb->get_col( $wpdb->prepare( "SELECT meta_value FROM {$table} WHERE {$id_column}=%d AND meta_key=%s ORDER BY {$meta_id}", $order->get_id(), $key ) );
            if ( $wpdb->last_error || $indexes[ $key ] !== array( $expected_indexes[ $key ] ) ) { throw new RuntimeException( 'Native-created fixture address index value/type/multiplicity mismatch.' ); }
            $exposed = array_values( array_filter( $data['meta_data'], static fn( $meta ) => $meta->get_data()['key'] === $key ) );
            if ( count( $exposed ) !== ( $hpos ? 1 : 0 ) || ( $exposed && $exposed[0]->get_data()['value'] !== $expected_indexes[ $key ] ) ) { throw new RuntimeException( 'Native representation address-index exposure changed.' ); }
        }
    }
    return array( 'items' => $items, 'data' => g4p_normalize( $data ), 'address_indexes' => $indexes, 'address_index_expectations' => $expected_indexes, 'stock_reduced' => $order instanceof WC_Order_Refund ? null : (bool) $order->get_data_store()->get_stock_reduced( $order->get_id() ), 'immutable' => g4p_immutable( $order ) );
}
function g4p_snapshot() {
    global $case; $result = array( 'orders' => array(), 'products' => array(), 'pending' => g4p_sync()->get_current_orders_pending_sync_count(), 'hpos' => Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled(), 'authority' => get_option( 'woocommerce_custom_orders_table_enabled' ), 'sync_option' => get_option( 'woocommerce_custom_orders_table_data_sync_enabled' ), 'runtime' => array( 'php' => PHP_VERSION, 'wordpress' => get_bloginfo( 'version' ), 'woocommerce' => WC_VERSION, 'database' => $GLOBALS['wpdb']->get_var( 'SELECT VERSION()' ), 'memory_limit' => ini_get( 'memory_limit' ), 'active_plugins' => get_option( 'active_plugins' ), 'datastore' => WC_Data_Store::load( 'order' )->get_current_class_name() ) );
    foreach ( $case['orders'] as $role => $id ) { if ( isset( $case['deleted'][ $id ] ) ) { continue; } $result['orders'][ $role ] = g4p_order_data( g4p_owned( $id ) ); }
    foreach ( $case['products'] as $role => $id ) { $product = wc_get_product( $id ); $result['products'][ $role ] = array( 'id' => $id, 'stock' => $product->get_stock_quantity(), 'status' => $product->get_stock_status(), 'children' => $product->get_children() ); }
    return $result;
}
function g4p_sync() { return wc_get_container()->get( Automattic\WooCommerce\Internal\DataStores\Orders\DataSynchronizer::class ); }
function g4p_new_order( $role, $product, $promise, $quantity = 1 ) {
    global $case, $run; if ( $case['writes_closed'] || isset( $case['orders'][ $role ] ) ) { throw new RuntimeException( 'Fresh admitted role required.' ); }
    $order = new WC_Order(); $order->set_customer_id( 1 ); $order->set_date_created( time() - 300 ); $order->set_currency( 'USD' );
    $order->set_address( array( 'first_name' => 'Synthetic', 'last_name' => 'Fixture', 'address_1' => '1 Test Way', 'city' => 'Oakland', 'state' => 'CA', 'postcode' => '94612', 'country' => 'US', 'email' => 'fixture@example.invalid' ), 'billing' ); $order->set_address( $order->get_address( 'billing' ), 'shipping' );
    $order->update_meta_data( '_g4_owner', $run ); $order->update_meta_data( '_g4_role', $role ); foreach ( array( 'repeat', 'repeat', 'different' ) as $value ) { $order->add_meta_data( '_g4_duplicate', $value, false ); }
    $item = new WC_Order_Item_Product(); $item->set_product( $product ); $item->set_quantity( $quantity ); $item->set_subtotal( 80 * $quantity ); $item->set_total( 80 * $quantity ); $item->add_meta_data( '_skyyrose_preorder_snapshot', $promise ); $item->add_meta_data( '_g4_typed', array( 'boolean' => true, 'integer' => 1, 'fractional' => 1.0 ) ); foreach ( array( 'repeat', 'repeat', 'different' ) as $value ) { $item->add_meta_data( '_g4_duplicate', $value, false ); } $order->add_item( $item ); $order->calculate_totals(); $order->save();
    $case['orders'][ $role ] = $order->get_id(); $case['created'][ $order->get_id() ] = array( 'run' => $run, 'role' => $role, 'type' => $order->get_type(), 'parent_id' => $order->get_parent_id() ); g4p_save(); return g4p_owned( $order->get_id() );
}
function g4p_product( $role ) {
    global $case, $run; $product = new WC_Product_Simple(); $product->set_name( 'Synthetic populated fixture ' . $role ); $product->set_sku( 'synthetic-gate4-pop-' . $run . '-' . $role ); $product->set_status( 'publish' ); $product->set_virtual( true ); $product->set_regular_price( '80' ); $product->set_manage_stock( true ); $product->set_stock_quantity( 30 ); $product->update_meta_data( '_g4_owner', $run ); $product->update_meta_data( '_is_preorder', '1' ); $product->update_meta_data( '_preorder_available', '30' ); $product->save(); $case['products'][ $role ] = $product->get_id(); g4p_save(); return $product;
}
function g4p_gateway_setup() {
    if ( ! class_exists( 'G4P_Offline_Gateway', false ) ) {
        class G4P_Offline_Gateway extends WC_Payment_Gateway {
            public function __construct() { $this->id = 'g4p_offline'; $this->enabled = 'yes'; $this->title = 'Synthetic offline'; $this->supports = array( 'products', 'refunds' ); }
            public function validate_fields() { g4p_event( 'validate_fields', $GLOBALS['g4p_pay_id'] ); return true; }
            public function process_payment( $id ) {
                g4p_event( 'processor_entered', $id ); $order = g4p_owned( $id ); $outcome = $GLOBALS['g4p_outcome'];
                $controller = new Automattic\WooCommerce\StoreApi\Utilities\OrderController();
                $controller->validate_existing_order_before_payment( $order );
                if ( $outcome !== 'unchecked-stock-probe' && $controller->get_failed_order_stock_error( $id ) ) { g4p_event( 'gateway_native_stock_refusal', $id ); wc_add_notice( 'Synthetic gateway native failed-stock refusal', 'error' ); return array( 'result' => 'failure' ); }
                if ( $outcome === 'failure' ) { $order->update_status( 'failed' ); g4p_event( 'gateway_failure', $id ); return array( 'result' => 'failure' ); }
                $completed = $order->payment_complete( 'g4p-offline-' . $id ); if ( $completed !== true ) { throw new RuntimeException( 'Native payment_complete did not return true.' ); } g4p_event( 'processor_completed', $id ); return array( 'result' => 'success', 'redirect' => $order->get_checkout_order_received_url() );
            }
            public function process_refund( $id, $amount = null, $reason = '' ) { g4p_event( 'fake_refund', $id ); return true; }
        }
    }
    add_filter( 'woocommerce_payment_gateways', static fn() => array( 'G4P_Offline_Gateway' ), PHP_INT_MAX );
    WC()->payment_gateways()->init(); $available = WC()->payment_gateways()->get_available_payment_gateways();
    if ( array_keys( $available ) !== array( 'g4p_offline' ) || get_class( $available['g4p_offline'] ) !== 'G4P_Offline_Gateway' ) { throw new RuntimeException( 'Only the local fake gateway may be available.' ); }
}
function g4p_batch_preflight( $batch ) {
    global $case, $run, $wpdb; $hpos = Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled();
    foreach ( $batch as $id ) {
        $ledger = $case['created'][ $id ] ?? null;
        if ( ! is_array( $ledger ) || $ledger['run'] !== $run || ( $case['orders'][ $ledger['role'] ] ?? null ) !== $id ) { throw new RuntimeException( 'Owned source creation ledger membership required.' ); }
        $expected_type = $ledger['type']; $expected_parent = $ledger['parent_id'];
        if ( isset( $case['deleted'][ $id ] ) ) { $deleted = $case['deleted'][ $id ]; if ( $deleted['run'] !== $run || $deleted['type'] !== $expected_type || $deleted['before']['data']['parent_id'] !== $expected_parent ) { throw new RuntimeException( 'Owned source tombstone ledger mismatch.' ); } $order = null; }
        else {
            $source_table = $hpos ? $wpdb->prefix . 'wc_orders' : $wpdb->posts; $source_type = $hpos ? 'type' : 'post_type'; $source_parent = $hpos ? 'parent_order_id' : 'post_parent';
            $source = $wpdb->get_row( $wpdb->prepare( "SELECT {$source_type} AS type, {$source_parent} AS parent_id FROM {$source_table} WHERE id=%d", $id ), ARRAY_A );
            if ( $wpdb->last_error || ! $source || $source['type'] !== $expected_type || (int) $source['parent_id'] !== $expected_parent ) { throw new RuntimeException( 'Owned source type/parent differs from creation ledger.' ); }
            $order = g4p_owned( $id ); if ( $order->get_type() !== $expected_type || $order->get_parent_id() !== $expected_parent ) { throw new RuntimeException( 'Owned source native object differs from creation ledger.' ); }
        }
        if ( ! in_array( $expected_type, array( 'shop_order', 'shop_order_refund' ), true ) ) { throw new RuntimeException( 'Owned source order type required.' ); }
        if ( $hpos ) {
            $type = $wpdb->get_var( $wpdb->prepare( "SELECT post_type FROM {$wpdb->posts} WHERE ID=%d", $id ) ); if ( $wpdb->last_error ) { throw new RuntimeException( 'Unreadable CPT destination refused.' ); }
            if ( $type && $type !== 'shop_order_placehold' ) {
                $owners = $wpdb->get_col( $wpdb->prepare( "SELECT meta_value FROM {$wpdb->postmeta} WHERE post_id=%d AND meta_key='_g4_owner'", $id ) );
                if ( $type !== $expected_type || $owners !== array( $run ) || $wpdb->last_error ) { throw new RuntimeException( 'Caller collision guard refused foreign CPT destination.' ); }
            }
        } else {
            $exists = $wpdb->get_var( $wpdb->prepare( "SELECT id FROM {$wpdb->prefix}wc_orders WHERE id=%d", $id ) ); if ( $wpdb->last_error ) { throw new RuntimeException( 'Unreadable HPOS destination refused.' ); }
            if ( $exists ) { $destination_type = $wpdb->get_var( $wpdb->prepare( "SELECT type FROM {$wpdb->prefix}wc_orders WHERE id=%d", $id ) ); if ( $wpdb->last_error || $destination_type !== $expected_type ) { throw new RuntimeException( 'Caller collision guard refused wrong HPOS destination type.' ); } $owners = $wpdb->get_col( $wpdb->prepare( "SELECT meta_value FROM {$wpdb->prefix}wc_orders_meta WHERE order_id=%d AND meta_key='_g4_owner'", $id ) ); if ( $owners !== array( $run ) || $wpdb->last_error ) { throw new RuntimeException( 'Caller collision guard refused foreign HPOS destination.' ); } }
        }
        if ( $order && $order->get_parent_id() && ! in_array( $order->get_parent_id(), array_values( $case['orders'] ), true ) ) { throw new RuntimeException( 'Foreign refund relationship refused.' ); }
    }
}
try {
    if ( $mode === 'initialize' ) {
        if ( file_exists( $state_file ) || (string) $GLOBALS['wpdb']->get_var( "SELECT COUNT(*) FROM {$GLOBALS['wpdb']->posts} WHERE post_type IN ('shop_order','shop_order_refund','shop_order_placehold')" ) !== '0' ) { throw new RuntimeException( 'Fresh order-empty native initialization only.' ); }
        foreach ( array( 'wc_orders', 'wc_order_addresses', 'wc_order_operational_data', 'wc_orders_meta', 'woocommerce_order_items', 'woocommerce_order_itemmeta' ) as $suffix ) { $table = $GLOBALS['wpdb']->prefix . $suffix; $exists = $GLOBALS['wpdb']->get_var( $GLOBALS['wpdb']->prepare( 'SHOW TABLES LIKE %s', $GLOBALS['wpdb']->esc_like( $table ) ) ); if ( $GLOBALS['wpdb']->last_error || ( $exists && (string) $GLOBALS['wpdb']->get_var( 'SELECT COUNT(*) FROM ' . $table ) !== '0' ) ) { throw new RuntimeException( 'Pre-DDL native tables must be absent or empty.' ); } }
        WC_Install::create_tables(); if ( g4p_sync()->create_database_tables() !== true ) { throw new RuntimeException( 'Native HPOS schema failed.' ); }
        foreach ( array( 'wc_orders', 'wc_order_addresses', 'wc_order_operational_data', 'wc_orders_meta', 'woocommerce_order_items', 'woocommerce_order_itemmeta' ) as $suffix ) { if ( (string) $GLOBALS['wpdb']->get_var( 'SELECT COUNT(*) FROM ' . $GLOBALS['wpdb']->prefix . $suffix ) !== '0' ) { throw new RuntimeException( 'Initial native schema is not empty/readable.' ); } }
        update_option( 'woocommerce_custom_orders_table_enabled', 'no' ); update_option( 'woocommerce_custom_orders_table_data_sync_enabled', 'no' ); g4p_save(); echo 'SR_G4_POP=' . g4p_json( array( 'ok' => true, 'empty_tables' => 6 ) ); return;
    }
    if ( ! file_exists( $state_file ) ) { throw new RuntimeException( 'Initialized run case required.' ); }
    if ( $mode === 'seed' ) {
        if ( $case['orders'] || $case['products'] ) { throw new RuntimeException( 'Fresh seed only.' ); }
        $function = $root . '/.artifacts/release-gates-20261019/gate4-populated/historical-producer-function.php'; $bytes = file_get_contents( $function );
        if ( hash( 'sha256', substr( $bytes, 6, -1 ) ) !== 'ad5444fd708f1d26eca843b0e6658f525718ffeaaff3460e5cec44e79c35e16b' ) { throw new RuntimeException( 'Exact historical producer required.' ); } require $function;
        foreach ( array( 'main' => array( 'v1_success', 'v1_retry', 'v1_malformed', 'v1_guard', 'v2_pending' ), 'stock' => array( 'v1_stock' ), 'probe' => array( 'v1_probe' ) ) as $product_role => $roles ) {
            $product = g4p_product( $product_role );
            $v1 = skyyrose_create_preorder_snapshot( array( 'product_id' => $product->get_id(), 'configuration_source_id' => $product->get_id(), 'allocation_source_id' => $product->get_id(), 'available' => 30 ) );
            if ( array_key_exists( 'sku', $v1 ) || array_key_exists( 'attributes', $v1 ) || array_key_exists( 'capture_point', $v1 ) || $v1['schema_version'] !== 1 ) { throw new RuntimeException( 'Historical schema changed.' ); }
            foreach ( $roles as $role ) { $promise = $role === 'v2_pending' ? skyyrose2_preorder_snapshot( skyyrose2_preorder_config( $product->get_id() ) ) : $v1; $order = g4p_new_order( $role, $product, $promise ); $case['original_immutable'][ $role ] = g4p_immutable( $order ); }
        }
        g4p_save(); file_put_contents( $private . '/pre-conversion-native.json', g4p_json( g4p_snapshot() ) );
    } elseif ( $mode === 'convert' ) {
        require_once __DIR__ . '/variation-migration-core-populated.php';
        foreach ( $case['products'] as $id ) { $product = wc_get_product( $id ); $row = array( 'id' => $id, 'sku' => $product->get_sku(), 'classification' => 'SIZE REQUIRED', 'canonical_sizes' => array( '2T', '3T', '4T', '5', '6', '7' ), 'registry_sha256' => hash_file( 'sha256', $root . '/logo-registry.json' ) ); $migration = new SkyyRose_Fenced_Size_Migration( $row ); $dry = $migration->run( array( 'mode' => 'dry-run' ) ); $result = $migration->run( array( 'mode' => 'apply', 'expected_sha256' => $dry['snapshot_sha256'] ) ); if ( count( $result['variation_ids'] ) !== 6 ) { throw new RuntimeException( 'Native conversion incomplete.' ); } }
        foreach ( $case['original_immutable'] as $role => $original ) { if ( g4p_immutable( g4p_owned( $case['orders'][ $role ] ) ) !== $original ) { throw new RuntimeException( 'Persisted historical promise/identity changed in conversion.' ); } }
    } elseif ( $mode === 'pay' ) {
        $role = $args[1] ?? ''; $outcome = $args[2] ?? ''; $request_kind = $args[3] ?? ''; $label = $args[4] ?? '';
        if ( ! isset( $case['orders'][ $role ] ) || ! in_array( $outcome, array( 'success', 'failure', 'unchecked-stock-probe' ), true ) || ! in_array( $request_kind, array( 'valid', 'bad-nonce', 'bad-key' ), true ) || ! preg_match( '/^[a-z0-9-]+$/D', $label ) ) { throw new RuntimeException( 'Bounded synthetic payment request required.' ); }
        $GLOBALS['g4p_request'] = $label; $GLOBALS['g4p_outcome'] = $outcome; $id = $case['orders'][ $role ]; $GLOBALS['g4p_pay_id'] = $id; g4p_owned( $id );
        wp_set_current_user( 1 ); WC()->initialize_session(); WC()->initialize_cart(); wc_clear_notices(); g4p_gateway_setup();
        add_action( 'woocommerce_before_pay_action', static fn( $order ) => g4p_event( 'before_pay', $order->get_id() ), 1 );
        add_action( 'woocommerce_payment_complete', static fn( $order_id ) => g4p_event( 'native_payment_complete_hook', $order_id ), PHP_INT_MAX );
        add_filter( 'wp_redirect', static function ( $url ) use ( $id ) { if ( ! str_starts_with( $url, 'http://127.0.0.1:18362/' ) ) { throw new RuntimeException( 'Nonlocal redirect refused.' ); } g4p_event( 'redirect', $id ); return $url; } );
        register_shutdown_function( static function () use ( $private, $label, $id, $run ) { file_put_contents( $private . '/request-' . $label . '.json', g4p_json( array( 'run' => $run, 'label' => $label, 'id' => $id, 'notices' => function_exists( 'wc_get_notices' ) ? wc_get_notices( 'error' ) : array(), 'last_error' => error_get_last() ) ) ); } );
        $order = g4p_owned( $id ); $_POST = array( 'woocommerce_pay' => '1', 'payment_method' => 'g4p_offline' ); $_GET = array( 'key' => $request_kind === 'bad-key' ? 'synthetic-wrong-key' : $order->get_order_key() ); $_REQUEST = array( 'woocommerce-pay-nonce' => $request_kind === 'bad-nonce' ? 'synthetic-invalid-nonce' : wp_create_nonce( 'woocommerce-pay' ) ); $GLOBALS['wp']->query_vars['order-pay'] = $id; WC_Form_Handler::pay_action(); g4p_event( 'handler_returned', $id ); echo 'SR_G4_POP=' . g4p_json( array( 'ok' => true, 'returned' => true ) ); return;
    } elseif ( $mode === 'prepare-stock' ) {
        $role = $args[1] ?? ''; if ( ! in_array( $role, array( 'stock', 'probe' ), true ) ) { throw new RuntimeException( 'Owned stock-control product required.' ); } $product = wc_get_product( $case['products'][ $role ] ); $product->set_stock_quantity( 0 ); $product->set_stock_status( 'outofstock' ); $product->save(); $order = g4p_owned( $case['orders'][ 'v1_' . $role ] ); $order->update_status( 'failed' );
    } elseif ( $mode === 'restore-stock' ) {
        $product = wc_get_product( $case['products']['stock'] ); $product->set_stock_quantity( 30 ); $product->set_stock_status( 'instock' ); $product->save();
    } elseif ( $mode === 'journal-control' ) {
        $option = 'skyyrose_v2_phase2_variations_' . $case['products']['main'];
        if ( ( $args[1] ?? '' ) === 'active' ) { if ( isset( $case['journal_preimage'] ) ) { throw new RuntimeException( 'One journal control at a time.' ); } $journal = get_option( $option ); if ( ! is_array( $journal ) || $journal['state'] !== 'COMPLETE' ) { throw new RuntimeException( 'Owned completed journal required.' ); } $case['journal_preimage'] = $journal; g4p_save(); $journal['state'] = 'APPLYING'; update_option( $option, $journal ); }
        elseif ( ( $args[1] ?? '' ) === 'restore' && isset( $case['journal_preimage'] ) ) { $current = get_option( $option ); $expected = $case['journal_preimage']; $expected['state'] = 'APPLYING'; if ( $current !== $expected ) { throw new RuntimeException( 'Journal control preimage changed.' ); } update_option( $option, $case['journal_preimage'] ); unset( $case['journal_preimage'] ); g4p_save(); }
        else { throw new RuntimeException( 'Bounded journal control required.' ); }
    } elseif ( $mode === 'financial' ) {
        update_option( 'woocommerce_calc_taxes', 'yes' );
        WC_Tax::_insert_tax_rate( array( 'tax_rate_country' => 'US', 'tax_rate_state' => 'CA', 'tax_rate' => '7.5000', 'tax_rate_name' => 'Synthetic tax', 'tax_rate_priority' => 1, 'tax_rate_compound' => 0, 'tax_rate_shipping' => 1, 'tax_rate_order' => 0, 'tax_rate_class' => '' ) );
        $parent = wc_get_product( $case['products']['main'] ); $child = wc_get_product( $parent->get_children()[0] ); $promise = skyyrose2_preorder_snapshot( skyyrose2_preorder_config( $parent->get_id(), $child->get_id(), array( 'attribute_size' => '2T' ) ) );
        $order = g4p_new_order( 'v2_financial', $child, $promise, 2 );
        $fee = new WC_Order_Item_Fee(); $fee->set_name( 'Synthetic fee' ); $fee->set_amount( 3 ); $fee->set_total( 3 ); $fee->set_tax_status( 'taxable' ); $order->add_item( $fee );
        $shipping = new WC_Order_Item_Shipping(); $shipping->set_method_title( 'Synthetic shipping' ); $shipping->set_method_id( 'g4p_offline' ); $shipping->set_total( 5 ); $order->add_item( $shipping );
        $order->calculate_taxes(); $order->calculate_totals(); $order->save(); if ( (float) $order->get_total_tax() <= 0 || count( $order->get_items( 'tax' ) ) !== 1 ) { throw new RuntimeException( 'Actual native financial/tax items required.' ); }
    } elseif ( $mode === 'refund' ) {
        $refund_suffix = $args[1] ?? ''; if ( ! in_array( $refund_suffix, array( '', 'hpos' ), true ) || ( $refund_suffix === 'hpos' && ! Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled() ) ) { throw new RuntimeException( 'Bounded native refund authority required.' ); } $refund_role = 'financial_refund' . ( $refund_suffix ? '_hpos' : '' );
        if ( isset( $case['orders'][ $refund_role ] ) ) { throw new RuntimeException( 'One native refund only.' ); } g4p_gateway_setup(); $order = g4p_owned( $case['orders']['v2_financial'] ); if ( ! $order->is_paid() ) { throw new RuntimeException( 'Paid financial order required.' ); } $item = current( $order->get_items() ); $taxes = $item->get_taxes(); $refund_taxes = array_map( static fn( $value ) => (float) $value / 2, $taxes['total'] );
        $refund = wc_create_refund( array( 'order_id' => $order->get_id(), 'amount' => (float) $item->get_total() / 2 + array_sum( $refund_taxes ), 'reason' => 'Synthetic native partial refund ' . $refund_suffix, 'refund_payment' => true, 'restock_items' => true, 'line_items' => array( $item->get_id() => array( 'qty' => 1, 'refund_total' => (float) $item->get_total() / 2, 'refund_tax' => $refund_taxes ) ) ) );
        if ( is_wp_error( $refund ) ) { throw new RuntimeException( 'Native refund failed.' ); } $refund->update_meta_data( '_g4_owner', $run ); $refund->update_meta_data( '_g4_role', $refund_role ); foreach ( array( 'repeat', 'repeat', 'different' ) as $value ) { $refund->add_meta_data( '_g4_duplicate', $value, false ); } $refund->save(); $case['orders'][ $refund_role ] = $refund->get_id(); $case['created'][ $refund->get_id() ] = array( 'run' => $run, 'role' => $refund_role, 'type' => $refund->get_type(), 'parent_id' => $refund->get_parent_id() ); g4p_save();
    } elseif ( $mode === 'make-delete' ) {
        $suffix = $args[1] ?? ''; if ( ! preg_match( '/^[a-z0-9-]+$/D', $suffix ) ) { throw new RuntimeException( 'Owned deletion-role label required.' ); } $parent = wc_get_product( $case['products']['main'] ); $child = wc_get_product( $parent->get_children()[0] ); $promise = skyyrose2_preorder_snapshot( skyyrose2_preorder_config( $parent->get_id(), $child->get_id(), array( 'attribute_size' => '2T' ) ) ); g4p_new_order( 'delete-' . $suffix, $child, $promise );
    } elseif ( $mode === 'delete' ) {
        $role = 'delete-' . ( $args[1] ?? '' ); if ( ! isset( $case['orders'][ $role ] ) ) { throw new RuntimeException( 'Owned deletion role required.' ); } $order = g4p_owned( $case['orders'][ $role ] ); $case['deleted'][ $order->get_id() ] = array( 'run' => $run, 'role' => $role, 'type' => $order->get_type(), 'before' => g4p_order_data( $order ) ); g4p_save(); $order->delete( true );
    } elseif ( $mode === 'type-control' ) {
        $order = g4p_owned( $case['orders']['v1_malformed'] ); $item = current( $order->get_items() ); $value = array( 'boolean' => true, 'integer' => 1, 'fractional' => 1.0 );
        if ( ( $args[1] ?? '' ) === 'bool-to-int' ) { $value['boolean'] = 1; } elseif ( ( $args[1] ?? '' ) === 'float-to-int' ) { $value['fractional'] = 1; } elseif ( ( $args[1] ?? '' ) !== 'restore' ) { throw new RuntimeException( 'Bounded native type control required.' ); }
        $item->update_meta_data( '_g4_typed', $value ); $item->save();
    } elseif ( $mode === 'mutate-v1' ) {
        $order = g4p_owned( $case['orders']['v1_malformed'] ); $item = current( $order->get_items() ); $promise = $case['original_immutable']['v1_malformed']['items'][ $item->get_id() ]['promise'];
        if ( ( $args[1] ?? '' ) === 'missing-id' ) { unset( $promise['configuration_source_id'] ); } elseif ( ( $args[1] ?? '' ) === 'ambiguous-sku' ) { $promise['sku'] = 'synthetic-invented-unknown'; } elseif ( ( $args[1] ?? '' ) !== 'restore' ) { throw new RuntimeException( 'Bounded mutation required.' ); } $item->update_meta_data( '_skyyrose_preorder_snapshot', $promise ); $item->save();
    } elseif ( $mode === 'next' ) {
        echo 'SR_G4_POP=' . g4p_json( array( 'ok' => true, 'pending' => g4p_sync()->get_current_orders_pending_sync_count(), 'batch' => g4p_sync()->get_next_batch_to_process( 2 ), 'hpos' => Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled() ) ); return;
    } elseif ( $mode === 'preflight' ) {
        if ( ! preg_match( '/^[1-9][0-9]*$/D', $args[1] ?? '' ) ) { throw new RuntimeException( 'One native selected ID required.' ); } g4p_batch_preflight( array( (int) $args[1] ) ); echo 'SR_G4_POP=' . g4p_json( array( 'ok' => true, 'preflight' => true ) ); return;
    } elseif ( $mode === 'stock-paths' ) {
        $order = g4p_owned( $case['orders']['v1_stock'] ); wp_set_current_user( 1 ); WC()->initialize_session(); WC()->initialize_cart(); wc_clear_notices(); g4p_gateway_setup(); $_GET = array( 'key' => $order->get_order_key(), 'pay_for_order' => 'true' ); $GLOBALS['wp']->query_vars['order-pay'] = $order->get_id();
        $controller = new Automattic\WooCommerce\StoreApi\Utilities\OrderController(); $stock_error = $controller->get_failed_order_stock_error( $order->get_id() ); ob_start(); WC_Shortcode_Checkout::output( array() ); $html = ob_get_clean(); file_put_contents( $private . '/stock-render.html', $html );
        echo 'SR_G4_POP=' . g4p_json( array( 'ok' => true, 'native_stock_error_present' => is_array( $stock_error ), 'rendered_payment_form' => strpos( $html, 'name="woocommerce_pay"' ) !== false || strpos( $html, "name='woocommerce_pay'" ) !== false, 'rendered_stock_error' => stripos( $html, 'stock' ) !== false, 'html_sha256' => hash( 'sha256', $html ), 'scope' => 'Native shortcode PHP rendering and separate StoreAPI utility; no HTTP/browser/handler enforcement claim' ) ); return;
    } elseif ( $mode === 'batch' || $mode === 'retry-refund' ) {
        $batch = $mode === 'batch' ? g4p_sync()->get_next_batch_to_process( 2 ) : array( $case['orders']['financial_refund_hpos'] ?? 0 );
        $hpos = Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled();
        if ( $mode === 'retry-refund' && ( ! $hpos || ! $case['writes_closed'] || g4p_sync()->has_orders_pending_sync() ) ) { throw new RuntimeException( 'Quiescent HPOS refund retry only.' ); }
        g4p_batch_preflight( $batch ); $messages = array(); $audit = null; $refund_id = $case['orders']['financial_refund_hpos'] ?? 0;
        if ( $hpos && $refund_id && in_array( $refund_id, $batch, true ) ) {
            $refund = g4p_owned( $refund_id );
            $audit = array( 'run' => $run, 'id' => $refund_id, 'ledger' => $case['created'][ $refund_id ], 'before_snapshot' => g4p_snapshot(), 'start_epoch' => microtime( true ), 'queries' => array(), 'refund_saves' => array() );
            $audit['cpt_type_before'] = get_post_type( $refund_id );
            $audit['cpt_refund_meta_before'] = $GLOBALS['wpdb']->get_results( $GLOBALS['wpdb']->prepare( "SELECT meta_key,meta_value FROM {$GLOBALS['wpdb']->postmeta} WHERE post_id=%d AND meta_key IN ('_refund_amount','_refunded_by','_refunded_payment','_refund_reason') ORDER BY meta_key,meta_id", $refund_id ), ARRAY_A );
            $audit['source_row_before'] = $GLOBALS['wpdb']->get_row( $GLOBALS['wpdb']->prepare( "SELECT * FROM {$GLOBALS['wpdb']->prefix}wc_orders WHERE id=%d", $refund_id ), ARRAY_A );
            $audit['source_unique_indexes'] = $GLOBALS['wpdb']->get_results( "SHOW INDEX FROM {$GLOBALS['wpdb']->prefix}wc_orders WHERE Non_unique=0", ARRAY_A );
            $audit['expected_cpt_refund_meta'] = array( '_refund_amount' => (string) $refund->get_amount( 'edit' ), '_refunded_by' => (string) $refund->get_refunded_by( 'edit' ), '_refunded_payment' => (string) $refund->get_refunded_payment( 'edit' ), '_refund_reason' => (string) $refund->get_reason( 'edit' ) );
            add_filter( 'query', static function ( $sql ) use ( &$audit ) { if ( preg_match( '/^\s*(UPDATE|INSERT|REPLACE|DELETE)\b/i', $sql ) && preg_match( '/\bwp_(wc_orders|wc_orders_meta|posts|postmeta)\b/i', $sql ) ) { $audit['queries'][] = array( 'sql' => $sql, 'epoch' => microtime( true ), 'stack' => debug_backtrace( DEBUG_BACKTRACE_IGNORE_ARGS, 80 ) ); } return $sql; }, PHP_INT_MAX );
            add_action( 'woocommerce_update_order_refund', static function ( $id, $object ) use ( &$audit, $refund_id ) { if ( $id === $refund_id ) { $audit['refund_saves'][] = array( 'id' => $id, 'epoch' => microtime( true ), 'modified' => $object->get_date_modified()->format( 'c' ), 'stack' => debug_backtrace( DEBUG_BACKTRACE_IGNORE_ARGS, 80 ) ); } }, PHP_INT_MAX, 2 );
        }
        add_filter( 'woocommerce_logger_log_message', static function ( $message, $level, $context, $handler ) use ( &$messages ) { $messages[] = array( 'level' => $level, 'message' => $message ); return $message; }, PHP_INT_MAX, 4 );
        g4p_sync()->process_batch( $batch );
        if ( is_array( $audit ) ) { $audit['end_epoch'] = microtime( true ); $audit['source_row_after'] = $GLOBALS['wpdb']->get_row( $GLOBALS['wpdb']->prepare( "SELECT * FROM {$GLOBALS['wpdb']->prefix}wc_orders WHERE id=%d", $refund_id ), ARRAY_A ); $audit['cpt_refund_meta_after'] = $GLOBALS['wpdb']->get_results( $GLOBALS['wpdb']->prepare( "SELECT meta_key,meta_value FROM {$GLOBALS['wpdb']->postmeta} WHERE post_id=%d AND meta_key IN ('_refund_amount','_refunded_by','_refunded_payment','_refund_reason') ORDER BY meta_key,meta_id", $refund_id ), ARRAY_A ); }
        echo 'SR_G4_POP=' . g4p_json( array( 'ok' => true, 'batch' => $batch, 'native_logs' => $messages, 'audit' => $audit, 'pending_after' => g4p_sync()->get_current_orders_pending_sync_count(), 'sql_audit_scope' => 'Attempted native DML and argument-free stacks; persisted changes established separately by SQL/native readbacks' ) ); return;
    } elseif ( $mode === 'writers' ) { if ( ! in_array( $args[1] ?? '', array( 'open', 'closed' ), true ) ) { throw new RuntimeException( 'Explicit writer admission state required.' ); } $case['writes_closed'] = $args[1] === 'closed'; g4p_save();
    } elseif ( $mode === 'switch' ) {
        $authority = $args[1] ?? ''; if ( ! in_array( $authority, array( 'yes', 'no' ), true ) ) { throw new RuntimeException( 'Explicit authority required.' ); }
        if ( ! $case['writes_closed'] && ! g4p_sync()->has_orders_pending_sync() ) { throw new RuntimeException( 'Quiescence required before a successful switch.' ); }
        try { update_option( 'woocommerce_custom_orders_table_enabled', $authority ); $refused = false; } catch ( Exception $error ) { $refused = true; $reason = $error->getMessage(); }
        echo 'SR_G4_POP=' . g4p_json( array( 'ok' => true, 'refused' => $refused, 'reason' => $reason ?? null, 'authority' => get_option( 'woocommerce_custom_orders_table_enabled' ), 'pending' => g4p_sync()->get_current_orders_pending_sync_count() ) ); return;
    } elseif ( $mode === 'compare' ) {
        $which = $args[1] ?? ''; if ( ! in_array( $which, array( 'cpt', 'hpos' ), true ) ) { throw new RuntimeException( 'Explicit read-only representation required.' ); }
        add_filter( 'woocommerce_hpos_enable_sync_on_read', '__return_false', PHP_INT_MAX );
        $store = $which === 'cpt' ? 'WC_Order_Data_Store_CPT' : Automattic\WooCommerce\Internal\DataStores\Orders\OrdersTableDataStore::class;
        $binding = $which === 'cpt' ? $store : wc_get_container()->get( $store );
        add_filter( 'woocommerce_order_data_store', static fn() => $binding, PHP_INT_MAX );
        $refund_class = $which === 'cpt' ? 'WC_Order_Refund_Data_Store_CPT' : Automattic\WooCommerce\Internal\DataStores\Orders\OrdersTableRefundDataStore::class;
        $refund_binding = $which === 'cpt' ? $refund_class : wc_get_container()->get( $refund_class );
        add_filter( 'woocommerce_order-refund_data_store', static fn() => $refund_binding, PHP_INT_MAX );
        add_filter( 'query', static function ( $sql ) { if ( preg_match( '/^\s*(INSERT|UPDATE|DELETE|REPLACE|ALTER|DROP|TRUNCATE)\b/i', $sql ) && preg_match( '/\bwp_(?:posts|postmeta|wc_orders|wc_order_addresses|wc_order_operational_data|wc_orders_meta|woocommerce_order_items|woocommerce_order_itemmeta)\b/i', $sql ) ) { throw new RuntimeException( 'Read-only representation inspection attempted DML.' ); } return $sql; }, PHP_INT_MAX );
        $orders = array(); foreach ( $case['orders'] as $role => $id ) { if ( isset( $case['deleted'][ $id ] ) ) { continue; } $type = get_post_type( $id ); $refund = str_contains( $role, 'refund' ); $order = $refund ? new WC_Order_Refund( $id ) : new WC_Order( $id ); $actual = $order->get_data_store()->get_current_class_name(); $expected = $refund ? $refund_class : $store; if ( $actual !== $expected || $order->get_meta( '_g4_owner', true ) !== $run ) { throw new RuntimeException( 'Independent representation binding/ownership failed.' ); } $orders[ $role ] = g4p_order_data( $order ); }
        echo 'SR_G4_POP=' . g4p_json( array( 'ok' => true, 'representation' => $which, 'orders' => $orders ) ); return;
    } elseif ( $mode === 'newer' ) {
        $suffix = $args[1] ?? ''; if ( ! preg_match( '/^[a-z0-9-]+$/D', $suffix ) ) { throw new RuntimeException( 'Fresh newer-role label required.' ); }
        $parent = wc_get_product( $case['products']['main'] ); $child = wc_get_product( $parent->get_children()[0] ); $promise = skyyrose2_preorder_snapshot( skyyrose2_preorder_config( $parent->get_id(), $child->get_id(), array( 'attribute_size' => '2T' ) ) ); g4p_new_order( 'newer-' . $suffix, $child, $promise ); $old = g4p_owned( $case['orders']['v2_pending'] ); $old->set_customer_note( 'Synthetic newer update ' . $suffix ); $old->update_meta_data( '_g4_newer', $suffix ); $old->save();
    } elseif ( $mode !== 'inspect' ) { throw new RuntimeException( 'Unknown bounded fixture operation.' ); }
    echo 'SR_G4_POP=' . g4p_json( array( 'ok' => true, 'snapshot' => g4p_snapshot(), 'case' => $case ) );
} catch ( Throwable $error ) { file_put_contents( $private . '/failure-' . $mode . '-' . getmypid() . '.json', g4p_json( array( 'run' => $run, 'mode' => $mode, 'type' => get_class( $error ), 'error' => $error->getMessage(), 'trace' => $error->getTraceAsString() ) ) ); echo 'SR_G4_POP=' . g4p_json( array( 'ok' => false, 'type' => get_class( $error ), 'error' => $error->getMessage() ) ); exit( 3 ); }
