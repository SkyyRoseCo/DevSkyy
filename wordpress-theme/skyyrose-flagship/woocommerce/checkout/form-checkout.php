<?php
/**
 * Checkout Form - Dark Luxury Multi-Step Design
 *
 * Overrides WooCommerce templates/checkout/form-checkout.php.
 * Features: 4-step progress bar, multi-step form, sticky order summary
 * sidebar (420px), dark glass panels, WooCommerce hook integration.
 *
 * @see     https://woocommerce.com/document/template-structure/
 * @package SkyyRose
 * @since   2.0.0
 * @version 9.4.0
 */

defined( 'ABSPATH' ) || exit;

// Guard against null cart object.
if ( ! function_exists( 'WC' ) || ! WC()->cart ) {
	return;
}

$checkout = WC()->checkout();

// Bail if cart empty and redirect to shop.
if ( WC()->cart->is_empty() && ! is_customize_preview() && apply_filters( 'woocommerce_checkout_redirect_empty_cart', true ) ) {
	return;
}

/**
 * Hook: woocommerce_before_checkout_form.
 *
 * @hooked woocommerce_checkout_login_form - 10
 * @hooked woocommerce_checkout_coupon_form - 10
 */
do_action( 'woocommerce_before_checkout_form', $checkout );

// If checkout registration is disabled and not logged in, the user cannot checkout.
if ( ! $checkout->is_registration_enabled() && $checkout->is_registration_required() && ! is_user_logged_in() ) {
	echo esc_html( apply_filters( 'woocommerce_checkout_must_be_logged_in_message', __( 'You must be logged in to checkout.', 'skyyrose' ) ) );
	return;
}
?>

<div class="skyy-checkout" data-skyy-checkout>

	<!-- 4-STEP PROGRESS BAR -->
	<div class="skyy-checkout__progress" role="navigation" aria-label="<?php esc_attr_e( 'Checkout progress', 'skyyrose' ); ?>">
		<ol class="skyy-checkout__progress-steps">
			<li class="skyy-checkout__progress-step is-active is-complete" data-step="0">
				<span class="skyy-checkout__progress-number">1</span>
				<span class="skyy-checkout__progress-label"><?php esc_html_e( 'Cart', 'skyyrose' ); ?></span>
			</li>
			<li class="skyy-checkout__progress-step is-active" data-step="1">
				<span class="skyy-checkout__progress-number">2</span>
				<span class="skyy-checkout__progress-label"><?php esc_html_e( 'Information', 'skyyrose' ); ?></span>
			</li>
			<li class="skyy-checkout__progress-step" data-step="2">
				<span class="skyy-checkout__progress-number">3</span>
				<span class="skyy-checkout__progress-label"><?php esc_html_e( 'Payment', 'skyyrose' ); ?></span>
			</li>
			<li class="skyy-checkout__progress-step" data-step="3">
				<span class="skyy-checkout__progress-number">4</span>
				<span class="skyy-checkout__progress-label"><?php esc_html_e( 'Confirmation', 'skyyrose' ); ?></span>
			</li>
		</ol>
		<div class="skyy-checkout__progress-bar">
			<div class="skyy-checkout__progress-fill" data-skyy-progress-fill style="width: 25%;"></div>
		</div>
	</div>

	<div class="skyy-checkout__layout">

		<!-- MAIN FORM AREA -->
		<div class="skyy-checkout__main">
			<form name="checkout"
					method="post"
					class="checkout woocommerce-checkout skyy-checkout__form"
					action="<?php echo esc_url( wc_get_checkout_url() ); ?>"
					enctype="multipart/form-data"
					aria-label="<?php echo esc_attr__( 'Checkout', 'skyyrose' ); ?>"
					data-skyy-checkout-form>

				<?php
				/**
				 * Hook: woocommerce_checkout_before_customer_details.
				 */
				do_action( 'woocommerce_checkout_before_customer_details' );
				?>

				<!-- STEP 1: Contact Information -->
				<div class="skyy-checkout__step skyy-checkout__step--active" data-skyy-step="1">
					<div class="skyy-checkout__panel">
						<h2 class="skyy-checkout__panel-title">
							<?php esc_html_e( 'Contact Information', 'skyyrose' ); ?>
						</h2>
						<p class="skyy-checkout__panel-subtitle">
							<?php esc_html_e( 'We\'ll use this email for order updates and tracking.', 'skyyrose' ); ?>
						</p>

						<div class="skyy-checkout__field-group stagger-grid">
							<?php
							woocommerce_form_field(
								'billing_email',
								array(
									'type'        => 'email',
									'label'       => esc_html__( 'Email Address', 'skyyrose' ),
									'required'    => true,
									'class'       => array( 'skyy-checkout__field', 'form-row-wide' ),
									'input_class' => array( 'skyy-checkout__input' ),
									'placeholder' => esc_attr__( 'your@email.com', 'skyyrose' ),
								),
								$checkout->get_value( 'billing_email' )
							);
							?>

							<?php if ( 'no' === get_option( 'woocommerce_registration_generate_password' ) ) : ?>
								<?php
								woocommerce_form_field(
									'billing_phone',
									array(
										'type'        => 'tel',
										'label'       => esc_html__( 'Phone (optional)', 'skyyrose' ),
										'required'    => false,
										'class'       => array( 'skyy-checkout__field', 'form-row-wide' ),
										'input_class' => array( 'skyy-checkout__input' ),
										'placeholder' => esc_attr__( '+1 (555) 000-0000', 'skyyrose' ),
									),
									$checkout->get_value( 'billing_phone' )
								);
								?>
							<?php endif; ?>
						</div>

						<div class="skyy-checkout__step-nav">
							<a href="<?php echo esc_url( wc_get_cart_url() ); ?>" class="skyy-checkout__back-btn">
								<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
									<path d="M10 12l-4-4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
								<?php esc_html_e( 'Back to Cart', 'skyyrose' ); ?>
							</a>
							<button type="button"
									class="skyy-checkout__next-btn"
									data-skyy-next-step="2">
								<?php esc_html_e( 'Continue to Shipping', 'skyyrose' ); ?>
							</button>
						</div>
					</div>
				</div>

				<!-- STEP 2: Shipping Address -->
				<div class="skyy-checkout__step" data-skyy-step="2">
					<div class="skyy-checkout__panel">
						<h2 class="skyy-checkout__panel-title">
							<?php esc_html_e( 'Shipping Address', 'skyyrose' ); ?>
						</h2>

						<div class="skyy-checkout__field-group">
							<div class="skyy-checkout__field-row">
								<?php
								woocommerce_form_field(
									'billing_first_name',
									array(
										'type'        => 'text',
										'label'       => esc_html__( 'First Name', 'skyyrose' ),
										'required'    => true,
										'class'       => array( 'skyy-checkout__field', 'form-row-first' ),
										'input_class' => array( 'skyy-checkout__input' ),
										'placeholder' => '',
									),
									$checkout->get_value( 'billing_first_name' )
								);

								woocommerce_form_field(
									'billing_last_name',
									array(
										'type'        => 'text',
										'label'       => esc_html__( 'Last Name', 'skyyrose' ),
										'required'    => true,
										'class'       => array( 'skyy-checkout__field', 'form-row-last' ),
										'input_class' => array( 'skyy-checkout__input' ),
										'placeholder' => '',
									),
									$checkout->get_value( 'billing_last_name' )
								);
								?>
							</div>

							<?php
							woocommerce_form_field(
								'billing_address_1',
								array(
									'type'        => 'text',
									'label'       => esc_html__( 'Street Address', 'skyyrose' ),
									'required'    => true,
									'class'       => array( 'skyy-checkout__field', 'form-row-wide' ),
									'input_class' => array( 'skyy-checkout__input' ),
									'placeholder' => esc_attr__( '123 Main Street', 'skyyrose' ),
								),
								$checkout->get_value( 'billing_address_1' )
							);

							woocommerce_form_field(
								'billing_address_2',
								array(
									'type'        => 'text',
									'label'       => esc_html__( 'Apartment, Suite, etc. (optional)', 'skyyrose' ),
									'required'    => false,
									'class'       => array( 'skyy-checkout__field', 'form-row-wide' ),
									'input_class' => array( 'skyy-checkout__input' ),
									'placeholder' => '',
								),
								$checkout->get_value( 'billing_address_2' )
							);
							?>

							<div class="skyy-checkout__field-row">
								<?php
								woocommerce_form_field(
									'billing_city',
									array(
										'type'        => 'text',
										'label'       => esc_html__( 'City', 'skyyrose' ),
										'required'    => true,
										'class'       => array( 'skyy-checkout__field', 'form-row-first' ),
										'input_class' => array( 'skyy-checkout__input' ),
										'placeholder' => '',
									),
									$checkout->get_value( 'billing_city' )
								);

								woocommerce_form_field(
									'billing_state',
									array(
										'type'        => 'state',
										'label'       => esc_html__( 'State / Province', 'skyyrose' ),
										'required'    => true,
										'class'       => array( 'skyy-checkout__field', 'form-row-last' ),
										'input_class' => array( 'skyy-checkout__input' ),
									),
									$checkout->get_value( 'billing_state' )
								);
								?>
							</div>

							<div class="skyy-checkout__field-row">
								<?php
								woocommerce_form_field(
									'billing_postcode',
									array(
										'type'        => 'text',
										'label'       => esc_html__( 'ZIP / Postal Code', 'skyyrose' ),
										'required'    => true,
										'class'       => array( 'skyy-checkout__field', 'form-row-first' ),
										'input_class' => array( 'skyy-checkout__input' ),
										'placeholder' => '',
									),
									$checkout->get_value( 'billing_postcode' )
								);

								woocommerce_form_field(
									'billing_country',
									array(
										'type'        => 'country',
										'label'       => esc_html__( 'Country', 'skyyrose' ),
										'required'    => true,
										'class'       => array( 'skyy-checkout__field', 'form-row-last' ),
										'input_class' => array( 'skyy-checkout__input' ),
									),
									$checkout->get_value( 'billing_country' )
								);
								?>
							</div>

							<?php
							woocommerce_form_field(
								'billing_phone',
								array(
									'type'        => 'tel',
									'label'       => esc_html__( 'Phone', 'skyyrose' ),
									'required'    => true,
									'class'       => array( 'skyy-checkout__field', 'form-row-wide' ),
									'input_class' => array( 'skyy-checkout__input' ),
									'placeholder' => esc_attr__( '+1 (555) 000-0000', 'skyyrose' ),
								),
								$checkout->get_value( 'billing_phone' )
							);
							?>
						</div>

						<?php
						/**
						 * Hook: woocommerce_checkout_shipping.
						 *
						 * @hooked woocommerce_checkout_form_shipping - 10
						 */
						do_action( 'woocommerce_checkout_shipping' );
						?>

						<!-- Ship to different address -->
						<?php if ( WC()->cart->needs_shipping() && WC()->cart->show_shipping() ) : ?>
							<div class="skyy-checkout__shipping-methods">
								<h3 class="skyy-checkout__shipping-methods-title">
									<?php esc_html_e( 'Shipping Method', 'skyyrose' ); ?>
								</h3>
								<?php wc_cart_totals_shipping_html(); ?>
							</div>
						<?php endif; ?>

						<div class="skyy-checkout__step-nav">
							<button type="button"
									class="skyy-checkout__back-btn"
									data-skyy-prev-step="1">
								<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
									<path d="M10 12l-4-4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
								<?php esc_html_e( 'Back', 'skyyrose' ); ?>
							</button>
							<button type="button"
									class="skyy-checkout__next-btn"
									data-skyy-next-step="3">
								<?php esc_html_e( 'Continue to Payment', 'skyyrose' ); ?>
							</button>
						</div>
					</div>
				</div>

				<?php
				/**
				 * Hook: woocommerce_checkout_after_customer_details.
				 */
				do_action( 'woocommerce_checkout_after_customer_details' );
				?>

				<!-- STEP 3: Payment -->
				<div class="skyy-checkout__step" data-skyy-step="3">
					<div class="skyy-checkout__panel">
						<h2 class="skyy-checkout__panel-title">
							<?php esc_html_e( 'Payment', 'skyyrose' ); ?>
						</h2>
						<p class="skyy-checkout__panel-subtitle">
							<?php esc_html_e( 'All transactions are secure and encrypted.', 'skyyrose' ); ?>
						</p>

						<?php if ( WC()->cart->needs_payment() ) : ?>
							<div id="payment" class="skyy-checkout__payment woocommerce-checkout-payment">
								<?php
								/**
								 * Hook: woocommerce_checkout_before_order_review_heading.
								 */
								do_action( 'woocommerce_checkout_before_order_review_heading' );
								?>

								<ul class="skyy-checkout__payment-methods rv-blur wc_payment_methods payment_methods methods">
									<?php
									if ( ! empty( $available_gateways = WC()->payment_gateways()->get_available_payment_gateways() ) ) :
										$first = true;
										foreach ( $available_gateways as $gateway ) :
											?>
											<li class="skyy-checkout__payment-method wc_payment_method payment_method_<?php echo esc_attr( $gateway->id ); ?>">
												<input id="payment_method_<?php echo esc_attr( $gateway->id ); ?>"
														type="radio"
														class="input-radio"
														name="payment_method"
														value="<?php echo esc_attr( $gateway->id ); ?>"
														<?php checked( $first, true ); ?>
														data-order_button_text="<?php echo esc_attr( $gateway->order_button_text ); ?>" />

												<label for="payment_method_<?php echo esc_attr( $gateway->id ); ?>"
														class="skyy-checkout__payment-method-label">
													<?php echo wp_kses_post( $gateway->get_title() ); ?>
													<?php echo wp_kses_post( $gateway->get_icon() ); ?>
												</label>

												<?php if ( $gateway->has_fields() || $gateway->get_description() ) : ?>
													<div class="skyy-checkout__payment-method-fields payment_box payment_method_<?php echo esc_attr( $gateway->id ); ?>"
														<?php
														if ( ! $first ) :
															?>
															style="display:none;"<?php endif; ?>>
														<?php $gateway->payment_fields(); ?>
													</div>
												<?php endif; ?>
											</li>
											<?php
											$first = false;
										endforeach;
									else :
										?>
										<li class="skyy-checkout__payment-method--none">
											<p><?php echo wp_kses_post( apply_filters( 'woocommerce_no_available_payment_methods_message', __( 'Payment options unavailable right now. Reach us at support@skyyrose.co and we will sort it.', 'skyyrose' ) ) ); ?></p>
										</li>
									<?php endif; ?>
								</ul>
							</div>
						<?php endif; ?>

						<div class="skyy-checkout__step-nav">
							<button type="button"
									class="skyy-checkout__back-btn"
									data-skyy-prev-step="2">
								<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
									<path d="M10 12l-4-4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
								<?php esc_html_e( 'Back', 'skyyrose' ); ?>
							</button>
							<button type="button"
									class="skyy-checkout__next-btn"
									data-skyy-next-step="4">
								<?php esc_html_e( 'Review Order', 'skyyrose' ); ?>
							</button>
						</div>
					</div>
				</div>

				<!-- STEP 4: Review & Confirm -->
				<div class="skyy-checkout__step" data-skyy-step="4">
					<div class="skyy-checkout__panel">
						<h2 class="skyy-checkout__panel-title">
							<?php esc_html_e( 'Review & Confirm', 'skyyrose' ); ?>
						</h2>

						<!-- Review: Contact -->
						<div class="skyy-checkout__review-section">
							<div class="skyy-checkout__review-header">
								<h3 class="skyy-checkout__review-heading">
									<?php esc_html_e( 'Contact', 'skyyrose' ); ?>
								</h3>
								<button type="button"
										class="skyy-checkout__review-edit"
										data-skyy-goto-step="1">
									<?php esc_html_e( 'Edit', 'skyyrose' ); ?>
								</button>
							</div>
							<p class="skyy-checkout__review-value" data-skyy-review-email></p>
						</div>

						<!-- Review: Shipping -->
						<div class="skyy-checkout__review-section">
							<div class="skyy-checkout__review-header">
								<h3 class="skyy-checkout__review-heading">
									<?php esc_html_e( 'Ship to', 'skyyrose' ); ?>
								</h3>
								<button type="button"
										class="skyy-checkout__review-edit"
										data-skyy-goto-step="2">
									<?php esc_html_e( 'Edit', 'skyyrose' ); ?>
								</button>
							</div>
							<p class="skyy-checkout__review-value" data-skyy-review-address></p>
						</div>

						<!-- Review: Payment -->
						<div class="skyy-checkout__review-section">
							<div class="skyy-checkout__review-header">
								<h3 class="skyy-checkout__review-heading">
									<?php esc_html_e( 'Payment', 'skyyrose' ); ?>
								</h3>
								<button type="button"
										class="skyy-checkout__review-edit"
										data-skyy-goto-step="3">
									<?php esc_html_e( 'Edit', 'skyyrose' ); ?>
								</button>
							</div>
							<p class="skyy-checkout__review-value" data-skyy-review-payment></p>
						</div>

						<!-- Order notes -->
						<div class="skyy-checkout__order-notes">
							<?php
							woocommerce_form_field(
								'order_comments',
								array(
									'type'        => 'textarea',
									'label'       => esc_html__( 'Order Notes (optional)', 'skyyrose' ),
									'class'       => array( 'skyy-checkout__field', 'form-row-wide' ),
									'input_class' => array( 'skyy-checkout__input', 'skyy-checkout__textarea' ),
									'placeholder' => esc_attr__( 'Notes about your order, e.g. special notes for delivery.', 'skyyrose' ),
								),
								$checkout->get_value( 'order_comments' )
							);
							?>
						</div>

						<?php
						/**
						 * Hook: woocommerce_review_order_before_submit.
						 */
						do_action( 'woocommerce_review_order_before_submit' );
						?>

						<!-- Terms & Conditions -->
						<?php wc_get_template( 'checkout/terms.php' ); ?>

						<div class="skyy-checkout__step-nav">
							<button type="button"
									class="skyy-checkout__back-btn"
									data-skyy-prev-step="3">
								<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
									<path d="M10 12l-4-4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
								<?php esc_html_e( 'Back', 'skyyrose' ); ?>
							</button>

							<?php
							echo wp_kses_post(
								apply_filters(
									'woocommerce_order_button_html',
									'<button type="submit"
										 class="skyy-checkout__place-order-btn magnetic btn-sweep button alt"
										 name="woocommerce_checkout_place_order"
										 id="place_order"
										 value="' . esc_attr__( 'Place Order', 'skyyrose' ) . '"
										 data-value="' . esc_attr__( 'Place Order', 'skyyrose' ) . '">' .
									esc_html__( 'Place Order', 'skyyrose' ) .
									'</button>'
								)
							);
							?>
						</div>

						<?php
						/**
						 * Hook: woocommerce_review_order_after_submit.
						 */
						do_action( 'woocommerce_review_order_after_submit' );
						?>

						<?php wp_nonce_field( 'woocommerce-process_checkout', 'woocommerce-process-checkout-nonce' ); ?>

					</div>
				</div>

			</form>
		</div>

		<!-- STICKY ORDER SUMMARY SIDEBAR (420px) -->
		<aside class="skyy-checkout__sidebar rv-clip-right" data-skyy-checkout-sidebar>
			<div class="skyy-checkout__sidebar-inner">
				<h2 class="skyy-checkout__sidebar-title">
					<?php esc_html_e( 'Order Summary', 'skyyrose' ); ?>
				</h2>

				<?php
				/**
				 * Hook: woocommerce_checkout_before_order_review.
				 */
				do_action( 'woocommerce_checkout_before_order_review' );
				?>

				<!-- Cart Items in Sidebar -->
				<div class="skyy-checkout__sidebar-items">
					<?php
					foreach ( WC()->cart->get_cart() as $cart_item_key => $cart_item ) :
						$_product   = apply_filters( 'woocommerce_cart_item_product', $cart_item['data'], $cart_item, $cart_item_key );
						$product_id = apply_filters( 'woocommerce_cart_item_product_id', $cart_item['product_id'], $cart_item, $cart_item_key );

						if ( ! $_product || ! $_product->exists() || $cart_item['quantity'] <= 0 ) {
							continue;
						}

						if ( ! apply_filters( 'woocommerce_cart_item_visible', true, $cart_item, $cart_item_key ) ) {
							continue;
						}
						?>
						<div class="skyy-checkout__sidebar-item">
							<div class="skyy-checkout__sidebar-item-img">
								<?php echo wp_kses_post( $_product->get_image( array( 64, 64 ) ) ); ?>
								<span class="skyy-checkout__sidebar-item-qty">
									<?php echo esc_html( $cart_item['quantity'] ); ?>
								</span>
							</div>
							<div class="skyy-checkout__sidebar-item-info">
								<span class="skyy-checkout__sidebar-item-name">
									<?php echo wp_kses_post( apply_filters( 'woocommerce_cart_item_name', $_product->get_name(), $cart_item, $cart_item_key ) ); ?>
								</span>
								<?php $formatted_item_data = wc_get_formatted_cart_item_data( $cart_item ); ?>
								<?php if ( $formatted_item_data ) : ?>
									<div class="skyy-checkout__sidebar-item-meta">
										<?php echo wp_kses_post( $formatted_item_data ); ?>
									</div>
								<?php endif; ?>
							</div>
							<span class="skyy-checkout__sidebar-item-price">
								<?php echo wp_kses_post( apply_filters( 'woocommerce_cart_item_subtotal', WC()->cart->get_product_subtotal( $_product, $cart_item['quantity'] ), $cart_item, $cart_item_key ) ); ?>
							</span>
						</div>
					<?php endforeach; ?>
				</div>

				<!-- Totals -->
				<div class="skyy-checkout__sidebar-totals">
					<div class="skyy-checkout__sidebar-row">
						<span><?php esc_html_e( 'Subtotal', 'skyyrose' ); ?></span>
						<span><?php wc_cart_totals_subtotal_html(); ?></span>
					</div>

					<?php foreach ( WC()->cart->get_coupons() as $code => $coupon ) : ?>
						<div class="skyy-checkout__sidebar-row skyy-checkout__sidebar-row--coupon">
							<span>
								<?php
								/* translators: %s: coupon code */
								printf( esc_html__( 'Coupon: %s', 'skyyrose' ), esc_html( $code ) );
								?>
							</span>
							<span><?php wc_cart_totals_coupon_html( $coupon ); ?></span>
						</div>
					<?php endforeach; ?>

					<?php if ( WC()->cart->needs_shipping() && WC()->cart->show_shipping() ) : ?>
						<div class="skyy-checkout__sidebar-row">
							<span><?php esc_html_e( 'Shipping', 'skyyrose' ); ?></span>
							<span><?php wc_cart_totals_shipping_html(); ?></span>
						</div>
					<?php endif; ?>

					<?php foreach ( WC()->cart->get_fees() as $fee ) : ?>
						<div class="skyy-checkout__sidebar-row">
							<span><?php echo esc_html( $fee->name ); ?></span>
							<span><?php wc_cart_totals_fee_html( $fee ); ?></span>
						</div>
					<?php endforeach; ?>

					<?php if ( wc_tax_enabled() && ! WC()->cart->display_prices_including_tax() ) : ?>
						<?php foreach ( WC()->cart->get_tax_totals() as $tax_code => $tax ) : ?>
							<div class="skyy-checkout__sidebar-row">
								<span><?php echo esc_html( $tax->label ); ?></span>
								<span><?php echo wp_kses_post( $tax->formatted_amount ); ?></span>
							</div>
						<?php endforeach; ?>
					<?php endif; ?>
				</div>

				<div class="skyy-checkout__sidebar-total">
					<span><?php esc_html_e( 'Total', 'skyyrose' ); ?></span>
					<span><?php wc_cart_totals_order_total_html(); ?></span>
				</div>

				<?php
				/**
				 * Hook: woocommerce_checkout_after_order_review.
				 */
				do_action( 'woocommerce_checkout_after_order_review' );
				?>

			</div>
		</aside>

	</div><!-- .skyy-checkout__layout -->

</div><!-- .skyy-checkout -->

<?php
/**
 * Hook: woocommerce_after_checkout_form.
 */
do_action( 'woocommerce_after_checkout_form', $checkout );
