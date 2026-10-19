<?php
/** Synthetic native order/stock states for private point-in-time recovery. */
$restored_control = basename( __DIR__ ) === 'control' && basename( dirname( __DIR__ ) ) === 'restore';
$root = dirname( __DIR__, 2 );
$private = $restored_control ? dirname( __DIR__ ) : $root . '/.artifacts/release-gates-20261019/gate4-local';
$source = $restored_control ? false : realpath( $private . '/wordpress' );
$restore = $restored_control ? realpath( $private . '/wordpress' ) : false;
$here = realpath( ABSPATH );
$socket = $GLOBALS['wpdb']->get_var( 'SELECT @@socket' );
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== 'sr_release_fixture' || ! ( ( $here === $source && $socket === '/tmp/sr-gate4-01a0f768.sock' ) || ( $restore && $here === $restore && $socket === '/tmp/sr-gate4-restore-01a0f768.sock' ) ) ) {
	throw new RuntimeException( 'Exact isolated synthetic recovery identity required.' );
}
$case_name = getenv( 'SR_RECOVERY_CASE' ) ?: 'recovery-case.json';
if ( ! preg_match( '/^recovery-[a-z0-9-]+\.json$/D', $case_name ) ) { throw new RuntimeException( 'Bounded synthetic recovery case required.' ); }
$file = $private . ( $restored_control ? '/state/' : '/' ) . $case_name;
function sr_recovery_normalize( $value ) {
	if ( $value instanceof DateTimeInterface ) { return $value->format( 'c' ); }
	if ( is_object( $value ) && method_exists( $value, 'get_data' ) ) { $value = $value->get_data(); }
	if ( is_array( $value ) ) { $value = array_map( 'sr_recovery_normalize', $value ); if ( ! array_is_list( $value ) ) { ksort( $value ); } }
	return $value;
}
function sr_recovery_order( $id ) {
	$order = new WC_Order( $id );
	if ( $order->get_meta( '_gate4_synthetic' ) !== 'private-recovery-v1' ) { throw new RuntimeException( 'Synthetic ownership required.' ); }
	$out = array( 'data' => $order->get_data(), 'items' => array(), 'stock_reduced' => $order->get_data_store()->get_stock_reduced( $id ) );
	foreach ( $order->get_items() as $item ) { $out['items'][] = $item->get_data(); }
	return sr_recovery_normalize( $out );
}
function sr_recovery_new_order( $product, $snapshot ) {
	$order = new WC_Order(); $order->set_date_created( time() - 300 ); $order->set_billing_email( 'fixture@example.invalid' );
	$order->set_payment_method( 'gate4_offline_native' ); $order->update_meta_data( '_gate4_synthetic', 'private-recovery-v1' );
	$item = new WC_Order_Item_Product(); $item->set_product( $product ); $item->set_quantity( 1 ); $item->set_subtotal( '80' ); $item->set_total( '80' );
	$item->add_meta_data( '_skyyrose_preorder_snapshot', $snapshot ); $order->add_item( $item ); $order->calculate_totals(); $order->save();
	return new WC_Order( $order->get_id() );
}
function sr_recovery_assert_paid( $id ) {
	$order = new WC_Order( $id );
	if ( ! $order->is_paid() || ! $order->get_date_paid() || $order->get_transaction_id() !== 'synthetic-offline-' . $id ) { throw new RuntimeException( 'Exact native paid status, paid date and synthetic transaction required.' ); }
}
function sr_recovery_snapshot( $case ) {
	$product = new WC_Product_Variable( $case['parent_id'] );
	$out = array( 'parent_id' => $product->get_id(), 'stock' => $product->get_stock_quantity(), 'children' => array(), 'orders' => array(), 'hpos' => Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled(), 'sync_option' => get_option( 'woocommerce_custom_orders_table_data_sync_enabled' ), 'native_store' => get_class( ( new WC_Order() )->get_data_store() ) );
	foreach ( $case['children'] as $id ) { $out['children'][ $id ] = sr_recovery_normalize( ( new WC_Product_Variation( $id ) )->get_data() ); }
	foreach ( $case['orders'] as $id ) { $out['orders'][ $id ] = sr_recovery_order( $id ); }
	return $out;
}
try {
	$mode = $args[0] ?? '';
	if ( $mode === 'seed' ) {
		if ( $here !== $source || file_exists( $file ) ) { throw new RuntimeException( 'Fresh source-only synthetic seed required.' ); }
		$product = new WC_Product_Simple(); $product->set_name( 'Private synthetic recovery product' ); $product->set_sku( 'synthetic-gate4-recovery-' . wp_generate_uuid4() ); $product->set_regular_price( '80' ); $product->set_status( 'publish' ); $product->set_virtual( true ); $product->set_manage_stock( true ); $product->set_stock_quantity( 20 ); $product->update_meta_data( '_is_preorder', '1' ); $product->update_meta_data( '_preorder_available', '20' ); $product->save();
		$v2 = skyyrose2_preorder_snapshot( skyyrose2_preorder_config( $product->get_id() ) );
		$v1 = array( 'schema' => 'skyyrose.preorder-commercial-promise', 'schema_version' => 1, 'is_preorder' => true, 'product_id' => $product->get_id(), 'variation_id' => 0, 'configuration_source_id' => $product->get_id(), 'allocation_source_id' => $product->get_id(), 'edition_size' => null, 'available_at_add_to_cart' => 20, 'expected_ship_date' => '' );
		$old = sr_recovery_new_order( $product, $v2 ); $legacy = sr_recovery_new_order( $product, $v1 );
		$history = array( sr_recovery_order( $old->get_id() ), sr_recovery_order( $legacy->get_id() ) );
		require_once __DIR__ . '/variation-migration-core-next.php';
		$row = array( 'id' => $product->get_id(), 'sku' => $product->get_sku(), 'classification' => 'SIZE REQUIRED', 'canonical_sizes' => array( '2T', '3T', '4T', '5', '6', '7' ), 'registry_sha256' => hash_file( 'sha256', $root . '/logo-registry.json' ) );
		$m = new SkyyRose_Fenced_Size_Migration( $row ); $dry = $m->run( array( 'mode' => 'dry-run' ) ); $result = $m->run( array( 'mode' => 'apply', 'expected_sha256' => $dry['snapshot_sha256'] ) );
		foreach ( array( $old->get_id(), $legacy->get_id() ) as $i => $order_id ) {
			$errors = new WP_Error(); skyyrose2_preorder_validate_order_payment( new WC_Order( $order_id ), $errors );
			if ( $errors->has_errors() || sr_recovery_order( $order_id ) !== $history[ $i ] ) { throw new RuntimeException( 'Persisted V1/V2 history or native payment contract drifted.' ); }
		}
		$case = array( 'parent_id' => $product->get_id(), 'children' => $result['variation_ids'], 'orders' => array( $old->get_id(), $legacy->get_id() ), 'existing_order_id' => $old->get_id() );
		file_put_contents( $file, wp_json_encode( $case ) ); chmod( $file, 0600 );
		file_put_contents( $file . '.before.json', wp_json_encode( sr_recovery_snapshot( $case ) ) );
		echo wp_json_encode( array( 'ok' => true, 'case' => $case, 'snapshot' => sr_recovery_snapshot( $case ) ) ); return;
	}
	$case = json_decode( file_get_contents( $file ), true );
	if ( $mode === 'pending-control' ) {
		$order = new WC_Order( $case['existing_order_id'] );
		if ( $order->get_status() !== 'pending' ) { throw new RuntimeException( 'Pending native control required.' ); }
		try { sr_recovery_assert_paid( $order->get_id() ); } catch ( RuntimeException $expected ) { echo wp_json_encode( array( 'ok' => true, 'pending_refused' => true ) ); return; }
		throw new RuntimeException( 'Unpaid order accepted as paid.' );
	}
	if ( $mode === 'post-backup' ) {
		if ( $here !== $source || isset( $case['post_backup_order_id'] ) ) { throw new RuntimeException( 'One synthetic post-backup delta on source only.' ); }
		$child = new WC_Product_Variation( $case['children'][0] );
		$snapshot = skyyrose2_preorder_snapshot( skyyrose2_preorder_config( $case['parent_id'], $child->get_id(), array( 'attribute_size' => '2T' ) ) );
		$new = sr_recovery_new_order( $child, $snapshot ); $case['orders'][] = $new->get_id(); $case['post_backup_order_id'] = $new->get_id();
		foreach ( array( $case['existing_order_id'], $new->get_id() ) as $id ) {
			$order = new WC_Order( $id ); $errors = new WP_Error(); skyyrose2_preorder_validate_order_payment( $order, $errors );
			if ( $errors->has_errors() ) { throw new RuntimeException( 'Native payment guard refused synthetic saved order.' ); }
			$order->payment_complete( 'synthetic-offline-' . $id ); wc_reduce_stock_levels( $id );
			sr_recovery_assert_paid( $id );
			$paid = sr_recovery_order( $id );
			$again = new WC_Order( $id ); $again->payment_complete( 'synthetic-offline-' . $id ); wc_reduce_stock_levels( $id );
			sr_recovery_assert_paid( $id );
			if ( sr_recovery_order( $id ) !== $paid ) { throw new RuntimeException( 'Duplicate native payment changed persisted identity/payment state.' ); }
		}
		file_put_contents( $file, wp_json_encode( $case ) );
		$uploads = wp_upload_dir();
		if ( ! empty( $uploads['error'] ) ) { throw new RuntimeException( 'Synthetic upload directory unavailable.' ); }
		file_put_contents( $uploads['basedir'] . '/gate4-newer-order.txt', 'Synthetic order ' . $new->get_id() );
		$after = sr_recovery_snapshot( $case );
		if ( (int) $after['stock'] !== 18 ) { throw new RuntimeException( 'Native payment/duplicate stock reduction did not preserve exact pool.' ); }
		file_put_contents( $file . '.after.json', wp_json_encode( $after ) );
		echo wp_json_encode( array( 'ok' => true, 'snapshot' => $after ) ); return;
	}
	if ( $mode === 'inspect' || $mode === 'inspect-backup' ) { echo wp_json_encode( array( 'ok' => true, 'snapshot' => sr_recovery_snapshot( $case ) ) ); return; }
	throw new RuntimeException( 'Unknown private recovery mode.' );
} catch ( Throwable $error ) { echo wp_json_encode( array( 'ok' => false, 'error' => $error->getMessage() ) ); exit( 3 ); }
