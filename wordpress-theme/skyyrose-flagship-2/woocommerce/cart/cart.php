<?php
/**
 * SkyyRose Flagship 2 cart.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

do_action( 'woocommerce_before_cart' );

if ( ! WC()->cart || WC()->cart->is_empty() ) :
	/**
	 * Keep the WooCommerce empty-cart lifecycle available to extensions.
	 * This template supplies the branded shell; plugins may still append their
	 * own recovery, analytics, or cleanup content through the standard hook.
	 */
	do_action( 'woocommerce_cart_is_empty' );
	?>
	<section class="sr2-cart sr2-cart--empty">
		<p><?php esc_html_e( 'Your bag', 'skyyrose-flagship-2' ); ?></p>
		<h1><?php esc_html_e( 'Nothing here yet.', 'skyyrose-flagship-2' ); ?></h1>
		<a class="sr2-page-action" href="<?php echo esc_url( wc_get_page_permalink( 'shop' ) ); ?>"><?php esc_html_e( 'Shop collections', 'skyyrose-flagship-2' ); ?></a>
	</section>
	<?php
else :
?>
<section class="sr2-cart">
	<header class="sr2-page-head"><p><?php esc_html_e( 'Your bag', 'skyyrose-flagship-2' ); ?></p><h1><?php esc_html_e( 'Keep your pieces close.', 'skyyrose-flagship-2' ); ?></h1></header>
	<div class="sr2-cart__layout">
		<form class="woocommerce-cart-form sr2-cart__items" action="<?php echo esc_url( wc_get_cart_url() ); ?>" method="post">
			<?php do_action( 'woocommerce_before_cart_table' ); ?>
			<?php do_action( 'woocommerce_before_cart_contents' ); ?>
			<?php foreach ( WC()->cart->get_cart() as $cart_item_key => $cart_item ) : ?>
				<?php
				$product = apply_filters( 'woocommerce_cart_item_product', $cart_item['data'], $cart_item, $cart_item_key );
				if ( ! $product || ! $product->exists() || $cart_item['quantity'] <= 0 || ! apply_filters( 'woocommerce_cart_item_visible', true, $cart_item, $cart_item_key ) ) {
					continue;
				}
				$product_id        = apply_filters( 'woocommerce_cart_item_product_id', $cart_item['product_id'], $cart_item, $cart_item_key );
				$product_permalink = apply_filters( 'woocommerce_cart_item_permalink', $product->is_visible() ? $product->get_permalink( $cart_item ) : '', $cart_item, $cart_item_key );
				$product_name      = apply_filters( 'woocommerce_cart_item_name', $product->get_name(), $cart_item, $cart_item_key );
				$product_thumbnail = apply_filters( 'woocommerce_cart_item_thumbnail', $product->get_image(), $cart_item, $cart_item_key );
				?>
				<article class="sr2-cart__item <?php echo esc_attr( apply_filters( 'woocommerce_cart_item_class', 'cart_item', $cart_item, $cart_item_key ) ); ?>" data-product-id="<?php echo esc_attr( $product_id ); ?>">
					<div class="sr2-cart__image">
						<?php
						if ( $product_permalink ) :
							?>
							<a href="<?php echo esc_url( $product_permalink ); ?>"><?php echo wp_kses_post( $product_thumbnail ); ?></a>
							<?php
else :
	?>
							<?php echo wp_kses_post( $product_thumbnail ); ?><?php endif; ?>
					</div>
					<div class="sr2-cart__item-copy">
						<h2>
						<?php
						if ( $product_permalink ) :
							?>
							<a href="<?php echo esc_url( $product_permalink ); ?>"><?php echo wp_kses_post( $product_name ); ?></a>
							<?php
else :
	?>
							<?php echo wp_kses_post( $product_name ); ?><?php endif; ?></h2>
						<?php do_action( 'woocommerce_after_cart_item_name', $cart_item, $cart_item_key ); ?>
						<span class="sr2-cart__unit-price"><?php esc_html_e( 'Each', 'skyyrose-flagship-2' ); ?> <?php echo wp_kses_post( apply_filters( 'woocommerce_cart_item_price', WC()->cart->get_product_price( $product ), $cart_item, $cart_item_key ) ); ?></span>
						<?php echo wp_kses_post( wc_get_formatted_cart_item_data( $cart_item ) ); ?>
						<?php
						if ( $product->backorders_require_notification() && $product->is_on_backorder( $cart_item['quantity'] ) ) {
							echo wp_kses_post( apply_filters( 'woocommerce_cart_item_backorder_notification', '<p class="backorder_notification">' . esc_html__( 'Available on backorder', 'skyyrose-flagship-2' ) . '</p>', $product_id ) );
						}
						?>
						<p class="sr2-cart__line-total"><span><?php esc_html_e( 'Line subtotal', 'skyyrose-flagship-2' ); ?></span> <strong><?php echo wp_kses_post( apply_filters( 'woocommerce_cart_item_subtotal', WC()->cart->get_product_subtotal( $product, $cart_item['quantity'] ), $cart_item, $cart_item_key ) ); ?></strong></p>
					</div>
					<div class="sr2-cart__controls">
						<?php
						// WooCommerce escapes its native control; post-content KSES removes inputs.
						$quantity = woocommerce_quantity_input(
							array(
								'input_name'  => "cart[{$cart_item_key}][qty]",
								'input_value' => $cart_item['quantity'],
								'max_value'   => $product->is_sold_individually() ? 1 : $product->get_max_purchase_quantity(),
								'min_value'   => $product->is_sold_individually() ? 1 : 0,
								'product_name' => $product_name,
							),
							$product,
							false
						);
						echo apply_filters( 'woocommerce_cart_item_quantity', $quantity, $cart_item_key, $cart_item ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Native Woo control/filter; KSES strips required inputs.
						?>
						<?php
						/* translators: %s: product name. */
						$remove_label = sprintf( __( 'Remove %s from your bag', 'skyyrose-flagship-2' ), wp_strip_all_tags( $product_name ) );
						?>
						<?php
						$remove_link = sprintf( '<a class="sr2-cart__remove" href="%s" aria-label="%s" data-product_id="%s" data-product_sku="%s">%s</a>', esc_url( wc_get_cart_remove_url( $cart_item_key ) ), esc_attr( $remove_label ), esc_attr( $product_id ), esc_attr( $product->get_sku() ), esc_html__( 'Remove', 'skyyrose-flagship-2' ) );
						echo wp_kses_post( apply_filters( 'woocommerce_cart_item_remove_link', $remove_link, $cart_item_key ) );
						?>
					</div>
				</article>
			<?php endforeach; ?>
			<?php do_action( 'woocommerce_cart_contents' ); ?>
			<?php do_action( 'woocommerce_after_cart_contents' ); ?>
			<div class="sr2-cart__actions">
				<?php
				if ( wc_coupons_enabled() ) :
					?>
					<label for="coupon_code"><?php esc_html_e( 'Code', 'skyyrose-flagship-2' ); ?></label><input id="coupon_code" type="text" name="coupon_code" value="" placeholder="<?php esc_attr_e( 'Gift code', 'skyyrose-flagship-2' ); ?>"><button class="button sr2-page-action" type="submit" name="apply_coupon" value="<?php esc_attr_e( 'Apply', 'skyyrose-flagship-2' ); ?>"><?php esc_html_e( 'Apply', 'skyyrose-flagship-2' ); ?></button><?php do_action( 'woocommerce_cart_coupon' ); ?><?php endif; ?>
				<button class="button sr2-page-action" type="submit" name="update_cart" value="<?php esc_attr_e( 'Update bag', 'skyyrose-flagship-2' ); ?>"><?php esc_html_e( 'Update bag', 'skyyrose-flagship-2' ); ?></button>
				<?php wp_nonce_field( 'woocommerce-cart', 'woocommerce-cart-nonce' ); ?>
			</div>
			<?php do_action( 'woocommerce_cart_actions' ); ?>
			<?php do_action( 'woocommerce_after_cart_table' ); ?>
		</form>
		<aside class="sr2-cart__summary"><?php do_action( 'woocommerce_cart_collaterals' ); ?></aside>
	</div>
</section>
<?php endif; ?>
<?php do_action( 'woocommerce_after_cart' ); ?>
