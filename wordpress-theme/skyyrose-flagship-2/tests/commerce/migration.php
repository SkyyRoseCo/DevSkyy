<?php
/** Real native conversion/payment tests; included by the isolated fixture only. */
if ( ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || 'sr_release_fixture' !== DB_NAME || 'http://127.0.0.1:18362' !== get_option( 'home' ) ) {
	throw new RuntimeException( 'The release-only synthetic fixture is required.' );
}
require_once dirname( __DIR__, 4 ) . '/tools/v2-runtime/variation-migration-core.php';

function sr_migration_throws( $callback, $label, $expected_message = null ) {
	$caught = false;
	try {
		$callback();
	} catch ( Exception $error ) {
		$caught = null === $expected_message || $expected_message === $error->getMessage();
	}
	skyyrose2_fixture_assert( $caught, $label );
}

function sr_migration_product() {
	$product = skyyrose2_fixture_product( array( '_is_preorder' => '1', '_preorder_available' => '6' ) );
	$product->set_sku( 'synthetic-migration-' . wp_generate_uuid4() );
	$product->set_manage_stock( true );
	$product->set_stock_quantity( 8 );
	$product->save();
	return $product;
}

function sr_migration_plan( $product ) {
	return array( 'id' => $product->get_id(), 'sku' => $product->get_sku(), 'classification' => 'SIZE REQUIRED', 'canonical_sizes' => array( '2T', '3T', '4T', '5', '6', '7' ), 'registry_sha256' => hash_file( 'sha256', dirname( __DIR__, 4 ) . '/logo-registry.json' ) );
}

function sr_migration_payment_errors( $order ) {
	$errors = new WP_Error();
	skyyrose2_preorder_validate_order_payment( $order, $errors );
	return $errors;
}

skyyrose2_fixture_empty();
update_option( 'woocommerce_calc_taxes', 'no' );
$product = sr_migration_product();
$id = $product->get_id();
WC()->cart->add_to_cart( $id, 1 );
$old_order = skyyrose2_fixture_order();
$old_order->set_date_created( time() - 120 );
$old_order->set_billing_email( 'fixture@example.invalid' );
$old_order->set_address( array( 'first_name' => 'Synthetic', 'last_name' => 'Fixture', 'address_1' => '1 Test Way', 'city' => 'Oakland', 'state' => 'CA', 'postcode' => '94612', 'country' => 'US', 'email' => 'fixture@example.invalid' ), 'billing' );
$old_order->set_address( array( 'first_name' => 'Synthetic', 'last_name' => 'Fixture', 'address_1' => '1 Test Way', 'city' => 'Oakland', 'state' => 'CA', 'postcode' => '94612', 'country' => 'US' ), 'shipping' );
$old_order->save();
$old_item = current( $old_order->get_items() );
$history = array( $old_item->get_id(), $old_item->get_product_id(), $old_item->get_variation_id(), $old_item->get_meta( '_skyyrose_preorder_snapshot', true ), $old_item->get_total(), $old_order->get_total() );
$row = sr_migration_plan( $product );
$v1_order = new WC_Order();
$v1_order->set_date_created( time() - 120 );
$v1_order->set_address( $old_order->get_address( 'billing' ), 'billing' );
$v1_order->set_address( $old_order->get_address( 'shipping' ), 'shipping' );
$v1_item = new WC_Order_Item_Product();
$v1_item->set_product( $product );
$v1_item->set_quantity( 1 );
$v1_item->set_subtotal( '80' );
$v1_item->set_total( '80' );
// Exact v1 producer fields: 119146cef0, woocommerce-compat.php:101–113.
$v1_snapshot = array( 'schema' => 'skyyrose.preorder-commercial-promise', 'schema_version' => 1, 'is_preorder' => true, 'product_id' => $id, 'variation_id' => 0, 'configuration_source_id' => $id, 'allocation_source_id' => $id, 'edition_size' => null, 'available_at_add_to_cart' => 6, 'expected_ship_date' => '' );
$v1_item->add_meta_data( '_skyyrose_preorder_snapshot', $v1_snapshot );
$v1_order->add_item( $v1_item );
$v1_order->calculate_totals();
$v1_order->save();
$v1_history = array( $v1_item->get_id(), $id, 0, $v1_snapshot, $v1_item->get_total(), $v1_order->get_total() );
$bad_digest = $row;
$bad_digest['registry_sha256'] = str_repeat( '0', 64 );
sr_migration_throws( static fn() => new SkyyRose_Size_Migration( $bad_digest ), 'stale registry digest rejected before any journal claim' );
$canonical_row = array_merge( $row, array( 'sku' => 'kids-001', 'reader_sha256' => hash_file( 'sha256', dirname( __DIR__, 4 ) . '/skyyrose/core/product.py' ) ) );
$canonical_migration = new SkyyRose_Size_Migration( $canonical_row );
$bad_sizes = $canonical_row;
$bad_sizes['canonical_sizes'] = array( 'S', 'M' );
sr_migration_throws( static fn() => new SkyyRose_Size_Migration( $bad_sizes ), 'canonical reader rejects wrong SKU size plan before claim' );
$bad_sku = $canonical_row;
$bad_sku['sku'] = 'unknown-canonical-fixture';
sr_migration_throws( static fn() => new SkyyRose_Size_Migration( $bad_sku ), 'canonical reader rejects unknown SKU before claim' );
$bad_reader = $canonical_row;
$bad_reader['reader_sha256'] = str_repeat( '0', 64 );
sr_migration_throws( static fn() => new SkyyRose_Size_Migration( $bad_reader ), 'stale reader digest rejected before claim' );
skyyrose2_fixture_assert( false === get_option( 'skyyrose_v2_phase2_variations_' . $id ) && wc_get_product( $id )->is_type( 'simple' ), 'invalid source plans make zero journal or native product writes' );
$migration = new SkyyRose_Size_Migration( $row );
$dry = $migration->run( array( 'mode' => 'dry-run' ) );
skyyrose2_fixture_assert( false === $dry['order_records_read'] && false === $dry['changed'], 'migration dry-run reads no orders and changes no products' );
sr_migration_throws( static fn() => $migration->run( array( 'mode' => 'apply', 'expected_sha256' => str_repeat( '0', 64 ) ) ), 'unreviewed native preimage rejected' );
$result = $migration->run( array( 'mode' => 'apply', 'expected_sha256' => $dry['snapshot_sha256'] ) );
skyyrose2_fixture_assert( $result['changed'] && 'COMPLETE' === $result['journal']['state'] && 6 === count( $result['variation_ids'] ), 'durable completed marker follows exact six-child readback' );
$again = ( new SkyyRose_Size_Migration( $row ) )->run( array( 'mode' => 'apply' ) );
skyyrose2_fixture_assert( false === $again['changed'] && $result['variation_ids'] === $again['variation_ids'], 'completed retry is idempotent with exact child inventory' );
$actual_sizes = array();
foreach ( $result['variation_ids'] as $child_id ) {
	$child = new WC_Product_Variation( $child_id );
	$actual_sizes[] = $child->get_attributes()['size'];
	skyyrose2_fixture_assert( '' === $child->get_sku( 'edit' ) && $row['sku'] === $child->get_sku(), 'native child keeps blank own SKU and inherits parent identity' );
}
skyyrose2_fixture_assert( $row['canonical_sizes'] === $actual_sizes, 'Kids numeric-looking size strings survive strict mapping roundtrip' );
$fresh_order = new WC_Order( $old_order->get_id() );
$fresh_item = current( $fresh_order->get_items() );
skyyrose2_fixture_assert( $history === array( $fresh_item->get_id(), $fresh_item->get_product_id(), $fresh_item->get_variation_id(), $fresh_item->get_meta( '_skyyrose_preorder_snapshot', true ), $fresh_item->get_total(), $fresh_order->get_total() ), 'pre-conversion order identities snapshot and money remain byte-for-byte unchanged' );
skyyrose2_fixture_empty();
skyyrose2_fixture_assert( ! sr_migration_payment_errors( $fresh_order )->has_errors(), 'persisted pre-cutoff simple preorder passes completed-migration payment context' );
$controller = new Automattic\WooCommerce\StoreApi\Utilities\OrderController();
$controller->validate_existing_order_before_payment( $fresh_order );
skyyrose2_fixture_assert( true, 'actual Store API existing-order validation accepts historical identity' );
$v1_order = new WC_Order( $v1_order->get_id() );
$controller->validate_existing_order_before_payment( $v1_order );
skyyrose2_fixture_assert( ! sr_migration_payment_errors( $v1_order )->has_errors(), 'persisted exact v1 producer snapshot passes native existing-order validation' );
$v1_item = current( $v1_order->get_items() );
skyyrose2_fixture_assert( $v1_history === array( $v1_item->get_id(), $v1_item->get_product_id(), $v1_item->get_variation_id(), $v1_item->get_meta( '_skyyrose_preorder_snapshot', true ), $v1_item->get_total(), $v1_order->get_total() ), 'v1 native IDs snapshot money remain unchanged without invented SKU or size' );
foreach ( array( 'product_id', 'configuration_source_id', 'allocation_source_id' ) as $field ) {
	$broken_v1 = $v1_snapshot;
	unset( $broken_v1[ $field ] );
	$v1_item->update_meta_data( '_skyyrose_preorder_snapshot', $broken_v1 );
	$v1_item->save();
	skyyrose2_fixture_assert( sr_migration_payment_errors( new WC_Order( $v1_order->get_id() ) )->has_errors(), 'v1 missing ' . $field . ' rejected' );
}
$v1_item->update_meta_data( '_skyyrose_preorder_snapshot', $v1_snapshot );
$v1_item->save();
do_action( 'woocommerce_before_pay_action', $fresh_order );
skyyrose2_fixture_assert( 0 === wc_notice_count( 'error' ), 'classic existing-order adapter accepts historical identity' );
skyyrose2_fixture_assert( false === WC()->cart->add_to_cart( $id, 1 ), 'new purchase still rejects variable parent without a selected size child' );
skyyrose2_fixture_empty();
$key = WC()->cart->add_to_cart( $id, 1, $result['variation_ids'][0], array( 'attribute_size' => '2T' ) );
skyyrose2_fixture_assert( (bool) $key && $result['variation_ids'][0] === WC()->cart->get_cart()[ $key ]['variation_id'], 'new selected native child identity reaches the actual cart' );
$new_order = skyyrose2_fixture_order();
$new_item = current( $new_order->get_items() );
skyyrose2_fixture_assert( $result['variation_ids'][0] === $new_item->get_variation_id() && '2T' === $new_item->get_meta( '_skyyrose_preorder_snapshot', true )['attributes']['attribute_size'], 'new native order persists exact selected child and size' );
skyyrose2_fixture_empty();
$option = 'skyyrose_v2_phase2_variations_' . $id;
$complete = get_option( $option );
foreach ( array( 'IN_PROGRESS', 'FAILED', 'UNKNOWN' ) as $state ) {
	$blocked = $complete;
	$blocked['state'] = $state;
	update_option( $option, $blocked, false );
	skyyrose2_fixture_assert( false === WC()->cart->add_to_cart( $id, 1, $result['variation_ids'][0], array( 'attribute_size' => '2T' ) ), $state . ' blocks actual new cart additions' );
	skyyrose2_fixture_assert( sr_migration_payment_errors( $fresh_order )->has_errors(), $state . ' blocks persisted existing-order payment' );
}
update_option( $option, $complete, false );
delete_option( $option );
skyyrose2_fixture_assert( sr_migration_payment_errors( $fresh_order )->has_errors(), 'missing completed marker never admits historical variable-parent payment' );
update_option( $option, $complete, false );
$wrong = $complete;
$wrong['before']['sku'] = 'foreign-parent';
update_option( $option, $wrong, false );
skyyrose2_fixture_assert( sr_migration_payment_errors( $fresh_order )->has_errors(), 'foreign original identity marker rejected' );
update_option( $option, $complete, false );
$original_date = $fresh_order->get_date_created()->getTimestamp();
$fresh_order->set_date_created( strtotime( $complete['cutoff_utc'] ) );
$fresh_order->save();
skyyrose2_fixture_assert( sr_migration_payment_errors( $fresh_order )->has_errors(), 'order created exactly at cutoff rejected' );
$fresh_order->set_date_created( strtotime( $complete['cutoff_utc'] ) + 1 );
$fresh_order->save();
skyyrose2_fixture_assert( sr_migration_payment_errors( $fresh_order )->has_errors(), 'post-cutoff simple identity rejected' );
$fresh_order->set_date_created( $original_date );
$fresh_order->save();
$variable = new WC_Product_Variable( $id );
$variable->update_meta_data( '_is_preorder', '0' );
$variable->update_meta_data( '_preorder_available', 'not-a-number' );
$variable->save();
skyyrose2_fixture_assert( sr_migration_payment_errors( $fresh_order )->has_errors(), 'recorded preorder context validates malformed allocation even when current flag is off' );
$variable->update_meta_data( '_preorder_available', '0' );
$variable->save();
skyyrose2_fixture_assert( sr_migration_payment_errors( $fresh_order )->has_errors(), 'recorded preorder context rejects zero current allocation' );
$variable->update_meta_data( '_preorder_available', '6' );
$variable->update_meta_data( '_is_preorder', '1' );
$variable->set_stock_quantity( 7 );
$variable->save();
skyyrose2_fixture_assert( ! sr_migration_payment_errors( $fresh_order )->has_errors(), 'legitimate native stock change does not invalidate completed identity provenance' );
$tampered = new WC_Order( $fresh_order->get_id() );
$tampered_item = current( $tampered->get_items() );
$tampered_item->set_quantity( 2 );
skyyrose2_fixture_assert( sr_migration_payment_errors( $tampered )->has_errors(), 'unsaved caller line mutation cannot impersonate persisted history' );

/** No remote processor: native Woo payment, stock and refund transitions only. */
class SR_Release_Fake_Gateway extends WC_Payment_Gateway {
	public static $outcome = 'success';
	public function __construct() {
		$this->id = 'sr_release_fake';
		$this->enabled = 'yes';
		$this->supports = array( 'products', 'refunds' );
	}
	public function process_payment( $order_id ) {
		$order = wc_get_order( $order_id );
		$controller = new Automattic\WooCommerce\StoreApi\Utilities\OrderController();
		$controller->validate_existing_order_before_payment( $order );
		if ( $controller->get_failed_order_stock_error( $order_id ) ) {
			throw new RuntimeException( 'Native failed-order stock validation rejected payment.' );
		}
		if ( 'failure' === self::$outcome ) {
			$order->update_status( 'failed' );
			return array( 'result' => 'failure' );
		}
		$order->payment_complete( 'synthetic-offline-' . $order_id );
		return array( 'result' => 'success' );
	}
	public function process_refund( $order_id, $amount = null, $reason = '' ) {
		return true;
	}
}
add_filter( 'woocommerce_payment_gateways', static fn() => array( 'SR_Release_Fake_Gateway' ), PHP_INT_MAX );
WC()->payment_gateways()->init();
$gateway = WC()->payment_gateways()->payment_gateways()['sr_release_fake'];
$v1_order = new WC_Order( $v1_order->get_id() );
$v1_order->set_payment_method( $gateway );
$v1_order->save();
$v1_stock = (int) wc_get_product( $id )->get_stock_quantity();
$v1_paid = $gateway->process_payment( $v1_order->get_id() );
skyyrose2_fixture_assert( 'success' === $v1_paid['result'] && $v1_stock - 1 === (int) wc_get_product( $id )->get_stock_quantity(), 'persisted v1 payment through fake gateway uses native stock' );
$v1_order = new WC_Order( $v1_order->get_id() );
$v1_order->update_status( 'cancelled' );
skyyrose2_fixture_assert( $v1_stock === (int) wc_get_product( $id )->get_stock_quantity(), 'v1 native cancellation restores parent stock without rewriting history' );
$fresh_order = new WC_Order( $old_order->get_id() );
$fresh_order->set_payment_method( $gateway );
$fresh_order->save();
$native_stock = (int) wc_get_product( $id )->get_stock_quantity();
SR_Release_Fake_Gateway::$outcome = 'failure';
$failed = $gateway->process_payment( $fresh_order->get_id() );
skyyrose2_fixture_assert( 'failure' === $failed['result'] && $native_stock === (int) wc_get_product( $id )->get_stock_quantity(), 'fake gateway failure leaves native stock unchanged' );
$variable = new WC_Product_Variable( $id );
$variable->set_stock_quantity( 0 );
$variable->save();
skyyrose2_fixture_assert( is_array( $controller->get_failed_order_stock_error( $fresh_order->get_id() ) ), 'actual native failed-order stock path rejects depleted parent pool' );
$variable->set_stock_quantity( $native_stock );
$variable->set_stock_status( 'instock' );
$variable->save();
SR_Release_Fake_Gateway::$outcome = 'success';
$paid = $gateway->process_payment( $fresh_order->get_id() );
skyyrose2_fixture_assert( 'success' === $paid['result'] && $native_stock - 1 === (int) wc_get_product( $id )->get_stock_quantity(), 'historical payment retry reduces native stock exactly once' );
wc_reduce_stock_levels( $fresh_order->get_id() );
skyyrose2_fixture_assert( $native_stock - 1 === (int) wc_get_product( $id )->get_stock_quantity(), 'repeated native stock reduction is idempotent' );
$fresh_order = new WC_Order( $fresh_order->get_id() );
$fresh_order->update_status( 'cancelled' );
skyyrose2_fixture_assert( $native_stock === (int) wc_get_product( $id )->get_stock_quantity(), 'native cancellation restores the original stock owner' );
$new_order = new WC_Order( $new_order->get_id() );
$new_order->set_address( $fresh_order->get_address( 'billing' ), 'billing' );
$new_order->set_address( $fresh_order->get_address( 'shipping' ), 'shipping' );
$new_order->set_payment_method( $gateway );
$new_order->save();
$gateway->process_payment( $new_order->get_id() );
skyyrose2_fixture_assert( $native_stock - 1 === (int) wc_get_product( $id )->get_stock_quantity(), 'selected child payment uses the same native parent stock pool' );
$new_item = current( $new_order->get_items() );
$refund = wc_create_refund( array( 'order_id' => $new_order->get_id(), 'amount' => $new_order->get_total(), 'refund_payment' => true, 'restock_items' => true, 'line_items' => array( $new_item->get_id() => array( 'qty' => 1, 'refund_total' => $new_item->get_total(), 'refund_tax' => array() ) ) ) );
skyyrose2_fixture_assert( ! is_wp_error( $refund ) && $native_stock === (int) wc_get_product( $id )->get_stock_quantity(), 'native refund through fake gateway restores the correct stock pool' );

// A caught interruption is distinct from the separate process-kill qualification.
$partial = sr_migration_product();
$partial_row = sr_migration_plan( $partial );
$partial_migration = new SkyyRose_Size_Migration( $partial_row );
$preimage = $partial_migration->run( array( 'mode' => 'dry-run' ) );
$interrupt = static function ( $step, $parent_id ) use ( $partial ) {
	if ( $parent_id === $partial->get_id() && 'after-parent' === $step ) {
		throw new RuntimeException( 'Synthetic caught interruption after parent save.' );
	}
};
add_action( 'skyyrose_size_migration_checkpoint', $interrupt, 10, 2 );
sr_migration_throws( static fn() => $partial_migration->run( array( 'mode' => 'apply', 'expected_sha256' => $preimage['snapshot_sha256'] ) ), 'caught post-parent interruption retains a durable failed operation' );
remove_action( 'skyyrose_size_migration_checkpoint', $interrupt, 10 );
$reconciled = ( new SkyyRose_Size_Migration( $partial_row ) )->run( array( 'mode' => 'reconcile' ) );
skyyrose2_fixture_assert( 'FAILED' === $reconciled['journal']['state'] && 'variable' === $reconciled['snapshot']['runtime_type'], 'fresh reconciliation observes the actual incomplete native parent' );
sr_migration_throws( static fn() => ( new SkyyRose_Size_Migration( $partial_row ) )->run( array( 'mode' => 'apply' ) ), 'ordinary retry cannot take over an incomplete operation' );
$resumed = ( new SkyyRose_Size_Migration( $partial_row ) )->run( array( 'mode' => 'resume', 'expected_current_sha256' => $reconciled['snapshot_sha256'] ) );
skyyrose2_fixture_assert( 'COMPLETE' === $resumed['journal']['state'] && 6 === count( $resumed['variation_ids'] ), 'explicit reviewed resume completes the interrupted parent without duplicates' );
$drifted = new WC_Product_Variation( $resumed['variation_ids'][0] );
$drifted->set_regular_price( '1' );
$drifted->save();
sr_migration_throws( static fn() => ( new SkyyRose_Size_Migration( $partial_row ) )->run( array( 'mode' => 'apply' ) ), 'completed retry rejects child-only price drift' );
sr_migration_throws( static fn() => ( new SkyyRose_Size_Migration( $partial_row ) )->run( array( 'mode' => 'rollback' ) ), 'automatic child deletion rollback remains disabled' );
// Real child-save hooks can mutate the parent after its initial verification.
$mutated = sr_migration_product();
$mutated_row = sr_migration_plan( $mutated );
$mutated_migration = new SkyyRose_Size_Migration( $mutated_row );
$mutated_preimage = $mutated_migration->run( array( 'mode' => 'dry-run' ) );
$mutation_observed = array( 'called' => false, 'dirty' => false );
$mutate_parent = static function ( $parent ) use ( $mutated, &$mutation_observed ) {
	if ( $parent->get_id() !== $mutated->get_id() ) { return; }
	$mutation_observed['called'] = true;
	$attributes = $parent->get_attributes( 'edit' );
	$replacement = clone $attributes['size'];
	$replacement->set_options( array( 'incorrect-synthetic-option' ) );
	$attributes['size'] = $replacement;
	$parent->set_attributes( $attributes );
	$mutation_observed['dirty'] = array_key_exists( 'attributes', $parent->get_changes() );
};
add_action( 'woocommerce_variable_product_sync_data', $mutate_parent );
sr_migration_throws( static fn() => $mutated_migration->run( array( 'mode' => 'apply', 'expected_sha256' => $mutated_preimage['snapshot_sha256'] ) ), 'final readback rejects parent size-option mutation during native synchronization', 'Parent size attributes conflict with the reviewed plan.' );
remove_action( 'woocommerce_variable_product_sync_data', $mutate_parent );
$mutated_state = ( new SkyyRose_Size_Migration( $mutated_row ) )->run( array( 'mode' => 'reconcile' ) );
skyyrose2_fixture_assert( $mutation_observed['called'] && $mutation_observed['dirty'] && array( 'incorrect-synthetic-option' ) === ( new WC_Product_Variable( $mutated->get_id() ) )->get_attributes()['size']->get_options(), 'native sync hook actually persisted the injected size drift' );
skyyrose2_fixture_assert( 'FAILED' === $mutated_state['journal']['state'] && 6 === count( $mutated_state['snapshot']['runtime_children'] ), 'parent-size drift retains incomplete guard and native children without automatic repair or deletion' );
$race = sr_migration_product();
$race_row = sr_migration_plan( $race );
$race_migration = new SkyyRose_Size_Migration( $race_row );
$race_before = $race_migration->run( array( 'mode' => 'dry-run' ) );
$raced = false;
$finish_before_lock = static function ( $step, $parent_id ) use ( $race_row, $race_before, &$raced ) {
	if ( 'before-lock' === $step && $parent_id === $race_row['id'] && ! $raced ) {
		$raced = true;
		( new SkyyRose_Size_Migration( $race_row ) )->run( array( 'mode' => 'apply', 'expected_sha256' => $race_before['snapshot_sha256'] ) );
	}
};
add_action( 'skyyrose_size_migration_checkpoint', $finish_before_lock, 10, 2 );
$race_result = $race_migration->run( array( 'mode' => 'apply', 'expected_sha256' => $race_before['snapshot_sha256'] ) );
remove_action( 'skyyrose_size_migration_checkpoint', $finish_before_lock, 10 );
$race_fresh = ( new SkyyRose_Size_Migration( $race_row ) )->run( array( 'mode' => 'reconcile' ) );
skyyrose2_fixture_assert( $raced && false === $race_result['changed'] && 'COMPLETE' === $race_result['journal']['state'], 'completion between pre-lock snapshot and claim returns current completed journal' );
skyyrose2_fixture_assert( $race_result['snapshot'] === $race_fresh['snapshot'] && $race_result['snapshot_sha256'] === $race_fresh['snapshot_sha256'] && 6 === count( $race_result['variation_ids'] ), 'concurrent completed retry returns exact locked final snapshot and child IDs' );
echo "MIGRATION IDENTITY/RECOVERY QUALIFICATION COMPLETE; synthetic native records only\n";
