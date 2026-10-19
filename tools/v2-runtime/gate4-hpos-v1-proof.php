<?php
/** Read-only native-object/SQL proof inside the unchanged exact disposable guard. */
add_filter( 'query', static function ( $sql ) { if ( preg_match( '/^\s*(INSERT|UPDATE|REPLACE|DELETE|CREATE|ALTER|DROP|TRUNCATE)\b/i', $sql ) ) { throw new RuntimeException( 'Read-only HPOS inspection refused DML.' ); } return $sql; }, PHP_INT_MAX );
$args = array( 'inspect' );
ob_start();
require __DIR__ . '/gate4-populated-fixture.php';
$included = ob_get_clean();
global $case, $run, $wpdb;
$at = strrpos( $included, 'SR_G4_POP=' );
if ( false === $at ) { throw new RuntimeException( 'Guarded helper snapshot absent.' ); }
$helper = json_decode( substr( $included, $at + strlen( 'SR_G4_POP=' ) ), true, 512, JSON_THROW_ON_ERROR );
if ( empty( $helper['ok'] ) || ! $helper['snapshot']['hpos'] || $helper['snapshot']['authority'] !== 'yes' ) { throw new RuntimeException( 'Native HPOS authority required.' ); }
$rows = array();
foreach ( $case['orders'] as $role => $id ) {
    $order = g4p_owned( $id );
    $store = $order->get_data_store()->get_current_class_name();
    if ( $store !== Automattic\WooCommerce\Internal\DataStores\Orders\OrdersTableDataStore::class ) { throw new RuntimeException( 'Actual native HPOS object datastore required.' ); }
    $row = $wpdb->get_row( $wpdb->prepare( "SELECT * FROM {$wpdb->prefix}wc_orders WHERE id=%d", $id ), ARRAY_A );
    $cpt = $wpdb->get_var( $wpdb->prepare( "SELECT post_type FROM {$wpdb->posts} WHERE ID=%d", $id ) );
    if ( $wpdb->last_error || ! is_array( $row ) || (int) $row['id'] !== $id || $row['type'] !== 'shop_order' || in_array( $cpt, array( 'shop_order', 'shop_order_refund' ), true ) ) { throw new RuntimeException( 'Native HPOS SQL identity/no CPT order fallback required.' ); }
    $rows[ $role ] = array( 'id' => $id, 'object_class' => get_class( $order ), 'datastore' => $store, 'hpos_row' => $row, 'cpt_type' => $cpt );
}
echo 'SR_G4_HPOS=' . g4p_json( array( 'ok' => true, 'run' => $run, 'native_objects' => $rows, 'helper_snapshot_sha256' => hash( 'sha256', $included ), 'helper_snapshot' => $helper['snapshot'], 'inspection_scope' => 'Post-bootstrap DML trap; native object datastore and raw HPOS SQL in one fresh process' ) );
