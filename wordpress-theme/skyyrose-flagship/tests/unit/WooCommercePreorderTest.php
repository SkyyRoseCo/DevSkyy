<?php
/**
 * Tests for the WooCommerce pre-order commercial-promise lifecycle.
 *
 * @package SkyyRose
 */

use PHPUnit\Framework\TestCase;

class WooCommercePreorderTest extends TestCase {

	protected function setUp(): void {
		parent::setUp();

		$GLOBALS['skyyrose_test_products']  = array();
		$GLOBALS['skyyrose_test_orders']    = array();
		$GLOBALS['skyyrose_test_coupons']   = array();
		$GLOBALS['skyyrose_test_notices']   = array();
		$GLOBALS['skyyrose_test_post_meta'] = array();
		$GLOBALS['skyyrose_test_user_meta'] = array();
		$GLOBALS['skyyrose_test_users']     = array();
		$GLOBALS['skyyrose_test_options']   = array();
		$GLOBALS['skyyrose_test_wc']        = new SkyyRose_Test_WC_Container();
	}

	private function registerProduct( $id, $meta = array(), $price = '0', $parent_id = 0 ) {
		$product = new WC_Product( $id, $meta, $price, $parent_id );
		$GLOBALS['skyyrose_test_products'][ $id ] = $product;
		return $product;
	}

	private function preorderMeta( $available = 5, $ship_date = '2027-03-15' ) {
		return array(
			'_is_preorder'            => '1',
			'_preorder_edition_size'  => '100',
			'_preorder_available'     => (string) $available,
			'_preorder_ship_date'     => $ship_date,
			'_preorder_price'         => '12.34',
		);
	}

	public function test_normal_product_has_no_preorder_snapshot(): void {
		$this->registerProduct( 10, array( '_is_preorder' => '0' ), '75' );

		$config = skyyrose_get_effective_preorder_config( 10 );
		$data   = skyyrose_add_preorder_cart_item_snapshot( array( 'gift' => true ), 10, 0, 1 );

		$this->assertFalse( $config['is_preorder'] );
		$this->assertSame( array( 'gift' => true ), $data );
		$this->assertSame( '$75.00', skyyrose_preorder_price_html( '$75.00', wc_get_product( 10 ) ) );
	}

	public function test_preorder_snapshot_captures_commercial_promise_without_price(): void {
		$this->registerProduct( 20, $this->preorderMeta(), '125' );

		$data     = skyyrose_add_preorder_cart_item_snapshot( array(), 20, 0, 2 );
		$snapshot = $data['skyyrose_preorder_snapshot'];

		$this->assertSame( 'skyyrose.preorder-commercial-promise', $snapshot['schema'] );
		$this->assertSame( 1, $snapshot['schema_version'] );
		$this->assertTrue( $snapshot['is_preorder'] );
		$this->assertSame( 5, $snapshot['available_at_add_to_cart'] );
		$this->assertSame( '2027-03-15', $snapshot['expected_ship_date'] );
		$this->assertArrayNotHasKey( 'price', $snapshot );
		$this->assertArrayNotHasKey( 'preorder_price', $snapshot );
	}

	public function test_variation_inherits_parent_and_overrides_its_own_allocation(): void {
		$this->registerProduct( 30, $this->preorderMeta( 8, '2027-04-01' ), '150' );
		$this->registerProduct(
			31,
			array(
				'_preorder_available' => '2',
				'_preorder_ship_date' => '2027-04-15',
			),
			'150',
			30
		);

		$config = skyyrose_get_effective_preorder_config( 30, 31 );

		$this->assertTrue( $config['is_preorder'] );
		$this->assertSame( 30, $config['configuration_source_id'] );
		$this->assertSame( 31, $config['allocation_source_id'] );
		$this->assertSame( 2, $config['available'] );
		$this->assertSame( '2027-04-15', $config['expected_ship_date'] );
	}

	public function test_variation_explicit_zero_allocation_overrides_parent_and_blocks(): void {
		$this->registerProduct( 32, $this->preorderMeta( 8 ), '150' );
		$this->registerProduct( 33, array( '_preorder_available' => '0' ), '150', 32 );

		$config = skyyrose_get_effective_preorder_config( 32, 33 );

		$this->assertSame( 33, $config['allocation_source_id'] );
		$this->assertSame( 0, $config['available'] );
		$this->assertFalse( skyyrose_validate_preorder_allocation( true, 32, 1, 33 ) );
	}

	public function test_mixed_cart_surfaces_snapshot_only_for_preorders(): void {
		$this->registerProduct( 40, array( '_is_preorder' => '0' ), '50' );
		$this->registerProduct( 41, $this->preorderMeta(), '90' );

		$normal   = skyyrose_add_preorder_cart_item_snapshot( array(), 40, 0, 1 );
		$preorder = skyyrose_add_preorder_cart_item_snapshot( array(), 41, 0, 1 );
		$display  = skyyrose_display_preorder_cart_item_data( array(), $preorder );

		$this->assertSame( array(), skyyrose_display_preorder_cart_item_data( array(), $normal ) );
		$this->assertSame( 'Pre-Order', $display[0]['key'] );
		$this->assertSame( 'Yes', $display[0]['value'] );
		$this->assertSame( 'Expected ship date', $display[1]['key'] );
		$this->assertSame( 'March 15, 2027', $display[1]['value'] );
	}

	public function test_zero_allocation_is_rejected_server_side(): void {
		$this->registerProduct( 50, $this->preorderMeta( 0 ), '100' );

		$this->assertFalse( skyyrose_validate_preorder_allocation( true, 50, 1 ) );
		$this->assertSame( 'error', $GLOBALS['skyyrose_test_notices'][0]['type'] );
	}

	public function test_missing_legacy_allocation_remains_uncapped(): void {
		$this->registerProduct( 52, array( '_is_preorder' => '1' ), '100' );

		$config = skyyrose_get_effective_preorder_config( 52 );

		$this->assertNull( $config['available'] );
		$this->assertTrue( skyyrose_validate_preorder_allocation( true, 52, 99 ) );
	}

	public function test_snapshot_filter_does_not_throw_when_allocation_is_zero(): void {
		$this->registerProduct( 51, $this->preorderMeta( 0 ), '100' );

		$data = skyyrose_add_preorder_cart_item_snapshot( array(), 51, 0, 1 );

		$this->assertTrue( $data['skyyrose_preorder_snapshot']['is_preorder'] );
		$this->assertSame( 0, $data['skyyrose_preorder_snapshot']['available_at_add_to_cart'] );
	}

	public function test_legacy_cart_session_is_hydrated_without_replacing_existing_snapshot(): void {
		$this->registerProduct( 53, $this->preorderMeta( 4, '2027-06-01' ), '100' );
		$legacy = array(
			'product_id'   => 53,
			'variation_id' => 0,
			'quantity'     => 1,
		);

		$hydrated = skyyrose_hydrate_preorder_cart_item_snapshot( $legacy, $legacy, 'legacy-53' );
		$this->assertSame( '2027-06-01', $hydrated['skyyrose_preorder_snapshot']['expected_ship_date'] );

		$hydrated['skyyrose_preorder_snapshot']['expected_ship_date'] = '2027-01-01';
		$restored = skyyrose_hydrate_preorder_cart_item_snapshot( $hydrated, $legacy, 'legacy-53' );
		$this->assertSame( '2027-01-01', $restored['skyyrose_preorder_snapshot']['expected_ship_date'] );
	}

	public function test_existing_cart_quantity_is_included_in_allocation_validation(): void {
		$this->registerProduct( 60, $this->preorderMeta( 3 ), '100' );
		$existing = skyyrose_add_preorder_cart_item_snapshot( array(), 60, 0, 2 );
		$existing['product_id']  = 60;
		$existing['variation_id'] = 0;
		$existing['quantity']    = 2;
		WC()->cart->set_cart( array( 'preorder-60' => $existing ) );

		$this->assertFalse( skyyrose_validate_preorder_allocation( true, 60, 2 ) );
		$this->assertTrue( skyyrose_validate_preorder_allocation( true, 60, 1 ) );
	}

	public function test_checkout_revalidates_current_allocation_without_decrementing_it(): void {
		$product = $this->registerProduct( 61, $this->preorderMeta( 2 ), '100' );
		$cart_item = skyyrose_add_preorder_cart_item_snapshot( array(), 61, 0, 2 );
		$cart_item['product_id']   = 61;
		$cart_item['variation_id'] = 0;
		$cart_item['quantity']     = 2;
		WC()->cart->set_cart( array( 'preorder-61' => $cart_item ) );

		$product->update_meta_data( '_preorder_available', '0' );
		$GLOBALS['skyyrose_test_notices'] = array();
		skyyrose_validate_preorder_cart_allocations();

		$this->assertSame( 'error', $GLOBALS['skyyrose_test_notices'][0]['type'] );
		$this->assertSame( '0', $product->get_meta( '_preorder_available', true ) );
		$this->assertSame( 2, $cart_item['skyyrose_preorder_snapshot']['available_at_add_to_cart'] );
	}

	public function test_checkout_order_line_persists_versioned_snapshot(): void {
		$this->registerProduct( 70, $this->preorderMeta(), '120' );
		$values = skyyrose_add_preorder_cart_item_snapshot( array(), 70, 0, 1 );
		$item   = new WC_Order_Item_Product();
		$order  = new WC_Order();

		skyyrose_persist_preorder_order_item_snapshot( $item, 'line-70', $values, $order );

		$this->assertSame( $values['skyyrose_preorder_snapshot'], $item->get_meta( '_skyyrose_preorder_snapshot', true ) );
		$this->assertSame( 'skyyrose.preorder-commercial-promise', $item->get_meta( '_skyyrose_preorder_schema', true ) );
		$this->assertSame( '1', $item->get_meta( '_skyyrose_preorder_schema_version', true ) );
	}

	public function test_order_line_builds_fallback_snapshot_for_legacy_cart_item(): void {
		$this->registerProduct( 71, $this->preorderMeta( 3, '2027-07-01' ), '120' );
		$values = array(
			'product_id'   => 71,
			'variation_id' => 0,
			'quantity'     => 1,
		);
		$item = new WC_Order_Item_Product();

		skyyrose_persist_preorder_order_item_snapshot( $item, 'legacy-71', $values, new WC_Order() );

		$this->assertSame( '2027-07-01', $item->get_meta( '_skyyrose_preorder_snapshot', true )['expected_ship_date'] );
		$this->assertSame( '1', $item->get_meta( '_skyyrose_preorder_schema_version', true ) );
	}

	public function test_historical_order_snapshot_survives_product_edits(): void {
		$product = $this->registerProduct( 80, $this->preorderMeta( 4, '2027-05-01' ), '130' );
		$values  = skyyrose_add_preorder_cart_item_snapshot( array(), 80, 0, 1 );
		$item    = new WC_Order_Item_Product();

		skyyrose_persist_preorder_order_item_snapshot( $item, 'line-80', $values, new WC_Order() );
		$product->update_meta_data( '_preorder_available', '0' );
		$product->update_meta_data( '_preorder_ship_date', '2027-12-31' );

		$stored = $item->get_meta( '_skyyrose_preorder_snapshot', true );
		$this->assertSame( 4, $stored['available_at_add_to_cart'] );
		$this->assertSame( '2027-05-01', $stored['expected_ship_date'] );
	}

	public function test_cancellation_and_refund_statuses_preserve_order_line_snapshot(): void {
		$this->registerProduct( 90, $this->preorderMeta(), '140' );
		$values = skyyrose_add_preorder_cart_item_snapshot( array(), 90, 0, 1 );
		$item   = new WC_Order_Item_Product();
		$order  = new WC_Order();

		skyyrose_persist_preorder_order_item_snapshot( $item, 'line-90', $values, $order );
		$order->add_item( $item );
		$order->set_status( 'cancelled' );
		$this->assertSame( '1', $item->get_meta( '_skyyrose_preorder_schema_version', true ) );

		$order->set_status( 'refunded' );
		$this->assertSame( $values['skyyrose_preorder_snapshot'], $item->get_meta( '_skyyrose_preorder_snapshot', true ) );
	}

	public function test_deprecated_preorder_price_never_overrides_woocommerce_price(): void {
		$priced = $this->registerProduct( 100, $this->preorderMeta(), '200' );
		$zero   = $this->registerProduct( 101, $this->preorderMeta(), '0' );

		$this->assertSame( '$200.00', skyyrose_preorder_price_html( '$200.00', $priced ) );
		$this->assertStringNotContainsString( '12.34', skyyrose_preorder_price_html( '$0.00', $zero ) );
		$this->assertStringContainsString( 'Pre-Order', skyyrose_preorder_price_html( '$0.00', $zero ) );
	}

	public function test_referral_order_metadata_uses_order_crud_and_saves_once(): void {
		$order = new WC_Order( array(), array( 'SKYYTEST' ), 'buyer@example.com' );
		$GLOBALS['skyyrose_test_orders'][110] = $order;
		$GLOBALS['skyyrose_test_coupons']['SKYYTEST'] = 111;
		$GLOBALS['skyyrose_test_post_meta'][111]['_skyyrose_referral_owner_email'] = 'owner@example.com';
		$GLOBALS['skyyrose_test_post_meta'][110]['_skyyrose_referral_credited'] = 'legacy-post-meta-must-be-ignored';
		$GLOBALS['skyyrose_test_users']['owner@example.com'] = (object) array( 'ID' => 112 );

		skyyrose_woo_credit_referrer( 110 );

		$this->assertSame( '1', $order->get_meta( '_skyyrose_referral_credited', true ) );
		$this->assertSame( 'SKYYTEST', $order->get_meta( '_skyyrose_referral_code_used', true ) );
		$this->assertSame( 1, $order->save_count );
		$this->assertSame( 1, $GLOBALS['skyyrose_test_user_meta'][112]['_skyyrose_referral_count'] );
	}
}
