<?php
/** Dependency-free renderer regression checks. Run: php scripts/test-express-checkout.php */
define( 'ABSPATH', __DIR__ . '/' );
$actions = array();
$removed = array();
$hook    = '';
function add_action( $name, $callback, $priority = 10 ) {
	global $actions;
	$actions[] = array( $name, $callback, $priority );
}
function current_filter() {
	global $hook;
	return $hook;
}
function remove_action( $name, $callback, $priority = 10 ) {
	global $removed;
	$removed[] = array( $name, $callback, $priority );
	return true;
}
class SkyyRose_Test_Wallet_Helper {
	public $eligible = true;
	public function should_show_express_checkout_button() {
		return $this->eligible;
	}
}
class WC_Payments {
	public static $gateway;
	public static $helper;
	public static function get_gateway() { return self::$gateway; }
	public static function get_express_checkout_helper() { return self::$helper; }
}
class WC_Stripe_Express_Checkout_Element {
	public static $renderer;
	public static function instance() { return self::$renderer; }
}
require dirname( __DIR__ ) . '/inc/express-checkout.php';
WC_Payments::$gateway = (object) array( 'enabled' => 'yes' );
WC_Payments::$helper  = new SkyyRose_Test_Wallet_Helper();
WC_Stripe_Express_Checkout_Element::$renderer = new stdClass();
$checks = 0;
foreach ( $actions as $action ) {
	$hook = $action[0];
	$removed = array();
	skyyrose2_single_express_wallet_row();
	$priority = 'woocommerce_proceed_to_checkout' === $hook ? 20 : 1;
	if ( 1 !== count( $removed ) || $removed[0] !== array( $hook, array( WC_Stripe_Express_Checkout_Element::$renderer, 'display_express_checkout_button_html' ), $priority ) || 0 !== $action[2] ) {
		throw new RuntimeException( 'Duplicate renderer was not removed at the correct hook/priority.' );
	}
	++$checks;
	foreach ( array( 'disabled', 'ineligible', 'missing_gateway', 'missing_helper', 'missing_stripe' ) as $case ) {
		$gateway = WC_Payments::$gateway;
		$helper  = WC_Payments::$helper;
		$stripe  = WC_Stripe_Express_Checkout_Element::$renderer;
		if ( 'disabled' === $case ) { WC_Payments::$gateway = (object) array( 'enabled' => 'no' ); }
		if ( 'ineligible' === $case ) { WC_Payments::$helper->eligible = false; }
		if ( 'missing_gateway' === $case ) { WC_Payments::$gateway = null; }
		if ( 'missing_helper' === $case ) { WC_Payments::$helper = null; }
		if ( 'missing_stripe' === $case ) { WC_Stripe_Express_Checkout_Element::$renderer = null; }
		$removed = array();
		skyyrose2_single_express_wallet_row();
		if ( $removed ) { throw new RuntimeException( 'Sole-provider fallback was removed: ' . $case ); }
		WC_Payments::$gateway = $gateway;
		WC_Payments::$helper = $helper;
		WC_Payments::$helper->eligible = true;
		WC_Stripe_Express_Checkout_Element::$renderer = $stripe;
		++$checks;
	}
}
if ( 3 !== count( $actions ) ) { throw new RuntimeException( 'Unexpected display scope.' ); }
echo 'PASS: ' . $checks . " renderer and fallback checks; no payment settings or gateway filters changed.\n";
