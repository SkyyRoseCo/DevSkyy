<?php
/**
 * Lightweight WooCommerce stubs for pre-order unit tests.
 *
 * @package SkyyRose
 */

class WC_Product {

	protected $id;
	protected $parent_id;
	protected $meta;
	protected $price;

	public function __construct( $id, $meta = array(), $price = '0', $parent_id = 0 ) {
		$this->id        = (int) $id;
		$this->parent_id = (int) $parent_id;
		$this->meta      = $meta;
		$this->price     = (string) $price;
	}

	public function get_id() {
		return $this->id;
	}

	public function get_parent_id() {
		return $this->parent_id;
	}

	public function is_type( $type ) {
		return 'variation' === $type && $this->parent_id > 0;
	}

	public function meta_exists( $key ) {
		return array_key_exists( $key, $this->meta );
	}

	public function get_meta( $key, $single = true ) {
		return $this->meta[ $key ] ?? '';
	}

	public function update_meta_data( $key, $value ) {
		$this->meta[ $key ] = $value;
	}

	public function delete_meta_data( $key ) {
		unset( $this->meta[ $key ] );
	}

	public function get_price() {
		return $this->price;
	}
}

class WC_Order_Item_Product {

	private $meta = array();

	public function add_meta_data( $key, $value, $unique = false ) {
		$this->meta[ $key ] = $value;
	}

	public function get_meta( $key, $single = true ) {
		return $this->meta[ $key ] ?? '';
	}
}

class WC_Order {

	private $meta;
	private $coupon_codes;
	private $billing_email;
	private $status = 'pending';
	private $items  = array();
	public $save_count = 0;

	public function __construct( $meta = array(), $coupon_codes = array(), $billing_email = '' ) {
		$this->meta          = $meta;
		$this->coupon_codes  = $coupon_codes;
		$this->billing_email = $billing_email;
	}

	public function get_meta( $key, $single = true ) {
		return $this->meta[ $key ] ?? '';
	}

	public function update_meta_data( $key, $value ) {
		$this->meta[ $key ] = $value;
	}

	public function save() {
		++$this->save_count;
		return 1;
	}

	public function get_coupon_codes() {
		return $this->coupon_codes;
	}

	public function get_billing_email() {
		return $this->billing_email;
	}

	public function set_status( $status ) {
		$this->status = $status;
	}

	public function get_status() {
		return $this->status;
	}

	public function add_item( $item ) {
		$this->items[] = $item;
	}

	public function get_items() {
		return $this->items;
	}
}

class WC_Coupon {

	private $id;

	public function __construct( $code ) {
		$this->id = (int) ( $GLOBALS['skyyrose_test_coupons'][ $code ] ?? 0 );
	}

	public function get_id() {
		return $this->id;
	}
}

class SkyyRose_Test_Cart {

	private $items = array();

	public function get_cart() {
		return $this->items;
	}

	public function set_cart( $items ) {
		$this->items = $items;
	}
}

class SkyyRose_Test_WC_Container {

	public $cart;

	public function __construct() {
		$this->cart = new SkyyRose_Test_Cart();
	}
}

function WC() {
	return $GLOBALS['skyyrose_test_wc'];
}

function wc_get_product( $product_id ) {
	return $GLOBALS['skyyrose_test_products'][ (int) $product_id ] ?? false;
}

function wc_get_order( $order_id ) {
	return $GLOBALS['skyyrose_test_orders'][ (int) $order_id ] ?? false;
}

function wc_add_notice( $message, $type = 'success' ) {
	$GLOBALS['skyyrose_test_notices'][] = array(
		'message' => $message,
		'type'    => $type,
	);
}

function date_i18n( $format, $timestamp ) {
	return gmdate( $format, $timestamp );
}
