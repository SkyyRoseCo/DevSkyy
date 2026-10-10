<?php
/**
 * Keep one express wallet row when WooPayments and Stripe coexist.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/**
 * Prefer the eligible WooPayments wallet renderer on classic commerce pages.
 *
 * Only remove Stripe's duplicate renderer for this request. Its ordinary card
 * gateway, saved settings, scripts and payment processing remain available.
 * When WooPayments cannot render wallets, retain Stripe's normal renderer.
 * Every callback Stripe's express-checkout instance registered on the current
 * hook is removed, whatever its priority (renderer and separator alike).
 *
 * @return void
 */
function skyyrose2_single_express_wallet_row() {
	if ( ! is_callable( array( 'WC_Payments', 'get_gateway' ) ) ||
		! is_callable( array( 'WC_Payments', 'get_express_checkout_helper' ) ) ||
		! is_callable( array( 'WC_Stripe_Express_Checkout_Element', 'instance' ) ) ) {
		return;
	}

	$gateway = WC_Payments::get_gateway();
	$helper  = WC_Payments::get_express_checkout_helper();
	$stripe  = WC_Stripe_Express_Checkout_Element::instance();
	if ( ! $gateway || 'yes' !== $gateway->enabled || ! $helper || ! $stripe ) {
		return;
	}

	// WooPayments renders a row for its wallets (payment request / Amazon Pay) or for WooPay.
	$renders_row = ( is_callable( array( $helper, 'should_show_express_checkout_button' ) ) &&
		$helper->should_show_express_checkout_button() ) ||
		( is_callable( array( $helper, 'should_show_woopay_button' ) ) &&
		$helper->should_show_woopay_button() );
	if ( ! $renders_row ) {
		return;
	}

	// Stripe's renderer priorities differ per hook and across plugin versions, so
	// find every callback bound to its instance instead of guessing a priority.
	// See WP_Hook::$callbacks (priority => id => array( 'function' => $callback )).
	$hook = current_filter();
	if ( empty( $GLOBALS['wp_filter'][ $hook ]->callbacks ) ) {
		return;
	}

	foreach ( $GLOBALS['wp_filter'][ $hook ]->callbacks as $priority => $entries ) {
		foreach ( $entries as $entry ) {
			$callback = isset( $entry['function'] ) ? $entry['function'] : null;
			if ( is_array( $callback ) && isset( $callback[0] ) && $stripe === $callback[0] ) {
				remove_action( $hook, $callback, $priority );
			}
		}
	}
}

foreach ( array( 'woocommerce_after_add_to_cart_form', 'woocommerce_proceed_to_checkout', 'woocommerce_checkout_before_customer_details', 'woocommerce_pay_order_before_payment' ) as $skyyrose2_wallet_hook ) {
	add_action( $skyyrose2_wallet_hook, 'skyyrose2_single_express_wallet_row', 0 );
}
unset( $skyyrose2_wallet_hook );
