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
	if ( ! $gateway || 'yes' !== $gateway->enabled || ! $helper || ! $stripe ||
		! is_callable( array( $helper, 'should_show_express_checkout_button' ) ) ||
		! $helper->should_show_express_checkout_button() ) {
		return;
	}

	$hook     = current_filter();
	$priority = 'woocommerce_proceed_to_checkout' === $hook ? 20 : 1;
	remove_action( $hook, array( $stripe, 'display_express_checkout_button_html' ), $priority );
}

foreach ( array( 'woocommerce_after_add_to_cart_form', 'woocommerce_proceed_to_checkout', 'woocommerce_checkout_before_customer_details' ) as $skyyrose2_wallet_hook ) {
	add_action( $skyyrose2_wallet_hook, 'skyyrose2_single_express_wallet_row', 0 );
}
unset( $skyyrose2_wallet_hook );
