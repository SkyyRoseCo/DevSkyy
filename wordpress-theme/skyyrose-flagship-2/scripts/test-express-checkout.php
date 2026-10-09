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
// Mirrors WP_Hook::remove_filter(): only an exact callback + priority match is removed.
function remove_action( $name, $callback, $priority = 10 ) {
	global $removed;
	$removed[] = array( $name, $callback, $priority );
	foreach ( $GLOBALS['wp_filter'][ $name ]->callbacks[ $priority ] ?? array() as $id => $entry ) {
		if ( $entry['function'] === $callback ) {
			unset( $GLOBALS['wp_filter'][ $name ]->callbacks[ $priority ][ $id ] );
			return true;
		}
	}
	return false;
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
	public static function get_gateway() {
		return self::$gateway; }
	public static function get_express_checkout_helper() {
		return self::$helper; }
}
class WC_Stripe_Express_Checkout_Element {
	public static $renderer;
	public static function instance() {
		return self::$renderer; }
}
/** Seed the hook as WP_Hook stores it: priority => id => array( 'function' => callable ). */
function skyyrose_test_seed( $name, $stripe, $other ) {
	$GLOBALS['wp_filter'][ $name ] = (object) array(
		'callbacks' => array(
			7  => array( 'render' => array( 'function' => array( $stripe, 'display_express_checkout_button_html' ) ) ),
			10 => array( 'other' => array( 'function' => $other ) ),
			33 => array(
				'sep'   => array( 'function' => array( $stripe, 'display_express_checkout_button_separator_html' ) ),
				'other' => array( 'function' => array( new stdClass(), 'display_express_checkout_button_html' ) ),
			),
		),
	);
}
require dirname( __DIR__ ) . '/inc/express-checkout.php';
WC_Payments::$gateway                         = (object) array( 'enabled' => 'yes' );
WC_Payments::$helper                          = new SkyyRose_Test_Wallet_Helper();
WC_Stripe_Express_Checkout_Element::$renderer = new stdClass();
$other                                        = 'unrelated_callback';
$checks                                       = 0;
function skyyrose_test_remaining( $name ) {
	$left = array();
	foreach ( $GLOBALS['wp_filter'][ $name ]->callbacks as $priority => $entries ) {
		foreach ( $entries as $id => $entry ) {
			$left[] = $priority . ':' . $id;
		}
	}
	sort( $left );
	return $left;
}
foreach ( $actions as $action ) {
	$hook    = $action[0];
	$stripe  = WC_Stripe_Express_Checkout_Element::$renderer;
	$removed = array();
	skyyrose_test_seed( $hook, $stripe, $other );
	skyyrose2_single_express_wallet_row();
	// Renderer (priority 7) and separator (priority 33) removed; unrelated callbacks survive.
	if ( 2 !== count( $removed ) || array( '10:other', '33:other' ) !== skyyrose_test_remaining( $hook ) || 0 !== $action[2] ) {
		throw new RuntimeException( 'Stripe callbacks not removed at their actual priorities, or unrelated callback removed: ' . $hook );
	}
	++$checks;
	// Missing hook object must be inert.
	unset( $GLOBALS['wp_filter'][ $hook ] );
	skyyrose2_single_express_wallet_row();
	++$checks;
	foreach ( array( 'disabled', 'ineligible', 'missing_gateway', 'missing_helper', 'missing_stripe' ) as $case ) {
		$gateway = WC_Payments::$gateway;
		$helper  = WC_Payments::$helper;
		$stripe  = WC_Stripe_Express_Checkout_Element::$renderer;
		if ( 'disabled' === $case ) {
			WC_Payments::$gateway = (object) array( 'enabled' => 'no' ); }
		if ( 'ineligible' === $case ) {
			WC_Payments::$helper->eligible = false; }
		if ( 'missing_gateway' === $case ) {
			WC_Payments::$gateway = null; }
		if ( 'missing_helper' === $case ) {
			WC_Payments::$helper = null; }
		if ( 'missing_stripe' === $case ) {
			WC_Stripe_Express_Checkout_Element::$renderer = null; }
		$removed = array();
		skyyrose_test_seed( $hook, $stripe, $other );
		skyyrose2_single_express_wallet_row();
		if ( $removed || 4 !== count( skyyrose_test_remaining( $hook ) ) ) {
			throw new RuntimeException( 'Sole-provider fallback was removed: ' . $case );
		}
		WC_Payments::$gateway                         = $gateway;
		WC_Payments::$helper                          = $helper;
		WC_Payments::$helper->eligible                = true;
		WC_Stripe_Express_Checkout_Element::$renderer = $stripe;
		++$checks;
	}
}
if ( 3 !== count( $actions ) ) {
	throw new RuntimeException( 'Unexpected display scope.' ); }
echo 'PASS: ' . $checks . " renderer and fallback checks; no payment settings or gateway filters changed.\n";
