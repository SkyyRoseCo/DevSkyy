<?php
/**
 * Status-aware order acknowledgement, retaining native gateway/order hooks.
 *
 * @package SkyyRoseFlagship2
 * @var WC_Order|false $order
 */
defined( 'ABSPATH' ) || exit;
?>
<section class="sr2-thankyou sr2-c-service" data-sr2-route="checkout">
	<?php if ( $order ) : ?>
		<?php
		do_action( 'woocommerce_before_thankyou', $order->get_id() );
		$sr2_messages = array(
			'failed'     => __( 'Payment was not completed. Check your payment provider for any pending authorization before trying again.', 'skyyrose-flagship-2' ),
			'pending'    => __( 'Payment is pending. Your order has not yet been confirmed as paid.', 'skyyrose-flagship-2' ),
			'on-hold'    => __( 'Your order is on hold. Review the payment instructions and order updates below.', 'skyyrose-flagship-2' ),
			'processing' => __( 'Your order is being processed. Check your account for order updates.', 'skyyrose-flagship-2' ),
			'completed'  => __( 'Your order is complete. Review the order details below.', 'skyyrose-flagship-2' ),
			'cancelled'  => __( 'Your order was cancelled. Contact Client Services with any payment questions.', 'skyyrose-flagship-2' ),
			'refunded'   => __( 'Your order is marked refunded. Your payment provider determines when the funds become available.', 'skyyrose-flagship-2' ),
		);
		$sr2_message = $sr2_messages[ $order->get_status() ] ?? __( 'Review your current order status and details below.', 'skyyrose-flagship-2' );
		?>
		<h1><?php esc_html_e( 'Order status', 'skyyrose-flagship-2' ); ?></h1>
		<p class="sr2-c-status" data-state="<?php echo $order->has_status( 'failed' ) ? 'error' : 'info'; ?>"><?php echo esc_html( $sr2_message ); ?></p>
		<?php if ( $order->has_status( array( 'failed', 'pending' ) ) ) : ?>
			<p><a class="sr2-c-action" href="<?php echo esc_url( $order->get_checkout_payment_url() ); ?>"><?php esc_html_e( 'Review payment options', 'skyyrose-flagship-2' ); ?></a></p>
		<?php endif; ?>
		<dl class="sr2-thankyou__details">
			<div><dt><?php esc_html_e( 'Order', 'skyyrose-flagship-2' ); ?></dt><dd><?php echo esc_html( $order->get_order_number() ); ?></dd></div>
			<?php if ( $order->get_date_created() ) : ?><div><dt><?php esc_html_e( 'Date', 'skyyrose-flagship-2' ); ?></dt><dd><?php echo esc_html( wc_format_datetime( $order->get_date_created() ) ); ?></dd></div><?php endif; ?>
			<div><dt><?php esc_html_e( 'Total', 'skyyrose-flagship-2' ); ?></dt><dd><?php echo wp_kses_post( $order->get_formatted_order_total() ); ?></dd></div>
		</dl>
		<?php
		// WooCommerce owns order details and gateway-specific instructions.
		do_action( 'woocommerce_thankyou_' . $order->get_payment_method(), $order->get_id() );
		do_action( 'woocommerce_thankyou', $order->get_id() );
		?>
	<?php else : ?>
		<p><?php esc_html_e( 'Check your account or contact Client Services to confirm your order status.', 'skyyrose-flagship-2' ); ?></p>
	<?php endif; ?>
</section>
