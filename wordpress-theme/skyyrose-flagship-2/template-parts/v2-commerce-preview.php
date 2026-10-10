<?php
/**
 * Local-only commerce state preview.
 *
 * The installed WooCommerce templates remain authoritative in production. This
 * fixture lets the review inspect the bag, checkout, account, and tracking shells
 * with the same class contract WooCommerce renders (form-row, input-text,
 * shop_table, payment, MyAccount navigation) without inventing a live order or
 * payment. Forms submit with GET back to the fixture; nothing is written.
 * `?state=empty` (cart) and `?state=dashboard` (account) expose alternate states;
 * `sr2_preview_submit=1` renders the WooCommerce required-field error state.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

global $route, $preview_state;
$preview_route = is_string( $route ) ? $route : 'cart';
$preview_mode  = is_string( $preview_state ) ? $preview_state : '';
$preview_sent  = (bool) filter_input( INPUT_GET, 'sr2_preview_submit', FILTER_VALIDATE_INT );
$preview_self  = '/tools/v2-theme-preview.php';
$preview_shop  = wc_get_page_permalink( 'shop' );
$preview_items = array_slice( wc_get_products(), 0, 2 );

get_header();
?>
<main id="primary" tabindex="-1" class="sr2-page sr2-page--<?php echo esc_attr( $preview_route ); ?> sr2-commerce-preview" data-sr2-route="<?php echo esc_attr( $preview_route ); ?>">
<div class="woocommerce">
<?php if ( 'cart' === $preview_route ) : ?>
	<?php if ( 'empty' === $preview_mode || ! $preview_items ) : ?>
		<section class="sr2-cart sr2-cart--empty">
			<div class="sr2-band__head">
				<div>
					<p class="sr2-eyebrow">Your bag</p>
					<h1 class="sr2-title-display">Nothing here yet.</h1>
					<p class="sr2-lede">Choose a piece from a collection and it will wait for you here, with its live price and availability.</p>
				</div>
				<a class="sr2-control sr2-control--primary" href="<?php echo esc_url( $preview_shop ); ?>">Shop collections</a>
			</div>
		</section>
	<?php else : ?>
		<section class="sr2-cart">
			<header class="sr2-band__head sr2-cart__head">
				<div><p class="sr2-eyebrow">Your bag</p><h1 class="sr2-title-display">Keep your pieces close.</h1></div>
				<a class="sr2-editorial-link" href="<?php echo esc_url( $preview_shop ); ?>">Continue shopping<span aria-hidden="true">→</span></a>
			</header>
			<div class="sr2-cart__layout">
				<form class="woocommerce-cart-form sr2-cart__items" action="<?php echo esc_url( $preview_self ); ?>" method="get">
					<input type="hidden" name="route" value="cart">
					<?php foreach ( $preview_items as $preview_index => $preview_item ) : ?>
						<article class="sr2-cart__item cart_item" data-product-id="<?php echo esc_attr( (string) $preview_item->get_id() ); ?>">
							<div class="sr2-cart__image"><a href="<?php echo esc_url( $preview_item->get_permalink() ); ?>"><?php echo wp_kses_post( wp_get_attachment_image( $preview_item->get_image_id(), 'thumbnail' ) ); ?></a></div>
							<div class="sr2-cart__item-copy">
								<h2><a href="<?php echo esc_url( $preview_item->get_permalink() ); ?>"><?php echo esc_html( $preview_item->get_name() ); ?></a></h2>
								<dl class="variation"><dt class="variation-Size">Size:</dt><dd class="variation-Size"><p>M</p></dd></dl>
								<span class="sr2-cart__unit-price">Each <?php echo wp_kses_post( $preview_item->get_price_html() ); ?></span>
								<p class="sr2-cart__line-total"><span>Line subtotal</span> <strong><?php echo wp_kses_post( $preview_item->get_price_html() ); ?></strong></p>
							</div>
							<div class="sr2-cart__controls">
								<div class="quantity">
									<label class="screen-reader-text" for="sr2-preview-qty-<?php echo esc_attr( (string) $preview_index ); ?>"><?php echo esc_html( $preview_item->get_name() ); ?> quantity</label>
									<input id="sr2-preview-qty-<?php echo esc_attr( (string) $preview_index ); ?>" class="input-text qty text" type="number" name="cart[<?php echo esc_attr( (string) $preview_item->get_id() ); ?>][qty]" value="1" min="0" max="8" step="1" inputmode="numeric" autocomplete="off">
								</div>
								<a class="sr2-cart__remove" href="<?php echo esc_url( $preview_self . '?route=cart&state=empty' ); ?>" aria-label="Remove <?php echo esc_attr( $preview_item->get_name() ); ?> from your bag">Remove</a>
							</div>
						</article>
					<?php endforeach; ?>
					<div class="sr2-cart__actions">
						<label for="coupon_code">Code</label><input id="coupon_code" type="text" name="coupon_code" value="" placeholder="Gift code"><button class="button sr2-cart__quiet-action" type="submit" name="apply_coupon" value="Apply">Apply</button>
						<button class="button sr2-cart__quiet-action" type="submit" name="update_cart" value="Update bag">Update bag</button>
					</div>
				</form>
				<aside class="sr2-cart__summary">
					<div class="cart_totals">
						<h2 class="sr2-title-editorial">Bag total</h2>
						<table class="shop_table shop_table_responsive">
							<tbody>
								<tr class="cart-subtotal"><th>Subtotal</th><td data-title="Subtotal"><span class="woocommerce-Price-amount amount">$256.00</span></td></tr>
								<tr class="woocommerce-shipping-totals shipping"><th>Shipping</th><td data-title="Shipping">Calculated at checkout</td></tr>
								<tr class="order-total"><th>Total</th><td data-title="Total"><strong><span class="woocommerce-Price-amount amount">$256.00</span></strong></td></tr>
							</tbody>
						</table>
						<div class="wc-proceed-to-checkout"><a href="<?php echo esc_url( wc_get_checkout_url() ); ?>" class="checkout-button button alt wc-forward">Proceed to checkout</a></div>
					</div>
				</aside>
			</div>
		</section>
	<?php endif; ?>
<?php elseif ( 'checkout' === $preview_route ) : ?>
	<?php
	$preview_fields  = array(
		'billing_first_name' => array(
			'label'        => 'First name',
			'type'         => 'text',
			'autocomplete' => 'given-name',
			'row'          => 'form-row-first',
			'required'     => true,
		),
		'billing_last_name'  => array(
			'label'        => 'Last name',
			'type'         => 'text',
			'autocomplete' => 'family-name',
			'row'          => 'form-row-last',
			'required'     => true,
		),
		'billing_country'    => array(
			'label'        => 'Country / Region',
			'type'         => 'select',
			'autocomplete' => 'country',
			'row'          => 'form-row-wide',
			'required'     => true,
			'options'      => array(
				'US' => 'United States (US)',
				'CA' => 'Canada',
				'GB' => 'United Kingdom (UK)',
			),
		),
		'billing_address_1'  => array(
			'label'        => 'Street address',
			'type'         => 'text',
			'autocomplete' => 'address-line1',
			'row'          => 'form-row-wide',
			'required'     => true,
			'placeholder'  => 'House number and street name',
		),
		'billing_address_2'  => array(
			'label'        => 'Apartment, suite, unit, etc.',
			'type'         => 'text',
			'autocomplete' => 'address-line2',
			'row'          => 'form-row-wide',
			'required'     => false,
		),
		'billing_city'       => array(
			'label'        => 'Town / City',
			'type'         => 'text',
			'autocomplete' => 'address-level2',
			'row'          => 'form-row-wide',
			'required'     => true,
		),
		'billing_state'      => array(
			'label'        => 'State',
			'type'         => 'select',
			'autocomplete' => 'address-level1',
			'row'          => 'form-row-first',
			'required'     => true,
			'options'      => array(
				'CA' => 'California',
				'NY' => 'New York',
				'TX' => 'Texas',
			),
		),
		'billing_postcode'   => array(
			'label'        => 'ZIP Code',
			'type'         => 'text',
			'autocomplete' => 'postal-code',
			'row'          => 'form-row-last',
			'required'     => true,
		),
		'billing_phone'      => array(
			'label'        => 'Phone',
			'type'         => 'tel',
			'autocomplete' => 'tel',
			'row'          => 'form-row-wide',
			'required'     => true,
		),
		'billing_email'      => array(
			'label'        => 'Email address',
			'type'         => 'email',
			'autocomplete' => 'email',
			'row'          => 'form-row-wide',
			'required'     => true,
		),
	);
	$preview_invalid = array();
	if ( $preview_sent ) {
		foreach ( $preview_fields as $preview_key => $preview_field ) {
			if ( $preview_field['required'] && '' === trim( (string) filter_input( INPUT_GET, $preview_key, FILTER_DEFAULT ) ) ) {
				$preview_invalid[ $preview_key ] = $preview_field['label'];
			}
		}
	}
	?>
	<?php if ( $preview_invalid ) : ?>
		<div class="woocommerce-NoticeGroup woocommerce-NoticeGroup-checkout">
			<ul class="woocommerce-error" role="alert">
				<?php foreach ( $preview_invalid as $preview_key => $preview_label ) : ?>
					<li data-id="<?php echo esc_attr( $preview_key ); ?>"><a href="#<?php echo esc_attr( $preview_key ); ?>_field"><strong>Billing <?php echo esc_html( $preview_label ); ?></strong> is a required field.</a></li>
				<?php endforeach; ?>
			</ul>
		</div>
	<?php endif; ?>
	<section class="sr2-checkout sr2-commerce-shell" data-sr2-route="checkout">
		<header class="sr2-band__head sr2-checkout__head"><div><p class="sr2-c-kicker sr2-eyebrow">Secure checkout</p><h1 class="sr2-title-display">Your pieces are almost home.</h1></div></header>
		<form name="checkout" method="get" class="checkout woocommerce-checkout sr2-c-checkout" action="<?php echo esc_url( $preview_self ); ?>" novalidate="novalidate" aria-label="Checkout">
			<input type="hidden" name="route" value="checkout"><input type="hidden" name="sr2_preview_submit" value="1">
			<div class="sr2-c-checkout__grid">
				<div class="sr2-c-checkout__details">
					<h2 class="sr2-title-editorial">Your details</h2>
					<div id="customer_details">
						<div class="col-1">
							<div class="woocommerce-billing-fields">
								<h3>Billing details</h3>
								<div class="woocommerce-billing-fields__field-wrapper">
									<?php foreach ( $preview_fields as $preview_key => $preview_field ) : ?>
										<?php $preview_row_state = isset( $preview_invalid[ $preview_key ] ) ? ' woocommerce-invalid woocommerce-invalid-required-field' : ''; ?>
										<p class="form-row <?php echo esc_attr( $preview_field['row'] ); ?><?php echo $preview_field['required'] ? ' validate-required' : ''; ?><?php echo esc_attr( $preview_row_state ); ?>" id="<?php echo esc_attr( $preview_key ); ?>_field">
											<label for="<?php echo esc_attr( $preview_key ); ?>"><?php echo esc_html( $preview_field['label'] ); ?>&nbsp;
											<?php
											if ( $preview_field['required'] ) :
												?>
												<abbr class="required" title="required">*</abbr>
												<?php
else :
	?>
												<span class="optional">(optional)</span><?php endif; ?></label>
											<span class="woocommerce-input-wrapper">
												<?php if ( 'select' === $preview_field['type'] ) : ?>
													<select name="<?php echo esc_attr( $preview_key ); ?>" id="<?php echo esc_attr( $preview_key ); ?>" class="country_to_state country_select" autocomplete="<?php echo esc_attr( $preview_field['autocomplete'] ); ?>"<?php echo isset( $preview_invalid[ $preview_key ] ) ? ' aria-invalid="true"' : ''; ?>><option value="">Select an option…</option>
													<?php
													foreach ( $preview_field['options'] as $preview_value => $preview_option ) :
														?>
														<option value="<?php echo esc_attr( $preview_value ); ?>"><?php echo esc_html( $preview_option ); ?></option><?php endforeach; ?></select>
												<?php else : ?>
													<input type="<?php echo esc_attr( $preview_field['type'] ); ?>" class="input-text" name="<?php echo esc_attr( $preview_key ); ?>" id="<?php echo esc_attr( $preview_key ); ?>" autocomplete="<?php echo esc_attr( $preview_field['autocomplete'] ); ?>"<?php echo isset( $preview_field['placeholder'] ) ? ' placeholder="' . esc_attr( $preview_field['placeholder'] ) . '"' : ''; ?><?php echo isset( $preview_invalid[ $preview_key ] ) ? ' aria-invalid="true"' : ''; ?>>
												<?php endif; ?>
											</span>
										</p>
									<?php endforeach; ?>
								</div>
							</div>
						</div>
						<div class="col-2">
							<div class="woocommerce-shipping-fields">
								<h3 id="ship-to-different-address"><label class="woocommerce-form__label woocommerce-form__label-for-checkbox checkbox"><input id="ship-to-different-address-checkbox" class="woocommerce-form__input woocommerce-form__input-checkbox input-checkbox" type="checkbox" name="ship_to_different_address" value="1"> <span>Ship to a different address?</span></label></h3>
							</div>
							<div class="woocommerce-additional-fields">
								<h3>Additional information</h3>
								<div class="woocommerce-additional-fields__field-wrapper">
									<p class="form-row notes" id="order_comments_field"><label for="order_comments">Order notes&nbsp;<span class="optional">(optional)</span></label><span class="woocommerce-input-wrapper"><textarea name="order_comments" class="input-text" id="order_comments" placeholder="Notes about your order, e.g. special notes for delivery." rows="2" cols="5"></textarea></span></p>
								</div>
							</div>
						</div>
					</div>
				</div>
				<aside class="sr2-c-checkout__summary">
					<h2 id="order_review_heading" class="sr2-title-editorial">Order summary</h2>
					<div id="order_review" class="woocommerce-checkout-review-order">
						<table class="shop_table woocommerce-checkout-review-order-table">
							<thead><tr><th class="product-name">Product</th><th class="product-total">Subtotal</th></tr></thead>
							<tbody>
								<?php foreach ( $preview_items as $preview_item ) : ?>
									<tr class="cart_item"><td class="product-name"><?php echo esc_html( $preview_item->get_name() ); ?>&nbsp;<strong class="product-quantity">×&nbsp;1</strong><dl class="variation"><dt class="variation-Size">Size:</dt><dd class="variation-Size"><p>M</p></dd></dl></td><td class="product-total"><?php echo wp_kses_post( $preview_item->get_price_html() ); ?></td></tr>
								<?php endforeach; ?>
							</tbody>
							<tfoot>
								<tr class="cart-subtotal"><th>Subtotal</th><td><span class="woocommerce-Price-amount amount">$256.00</span></td></tr>
								<tr class="woocommerce-shipping-totals shipping"><th>Shipping</th><td><ul id="shipping_method" class="woocommerce-shipping-methods"><li><input type="radio" name="shipping_method[0]" data-index="0" id="shipping_method_0_flat_rate1" value="flat_rate:1" class="shipping_method" checked><label for="shipping_method_0_flat_rate1">Tracked delivery: <span class="woocommerce-Price-amount amount">$12.00</span></label></li></ul></td></tr>
								<tr class="order-total"><th>Total</th><td><strong><span class="woocommerce-Price-amount amount">$268.00</span></strong></td></tr>
							</tfoot>
						</table>
						<div id="payment" class="woocommerce-checkout-payment">
							<ul class="wc_payment_methods payment_methods methods">
								<li class="wc_payment_method payment_method_preview"><input id="payment_method_preview" type="radio" class="input-radio" name="payment_method" value="preview" checked><label for="payment_method_preview">Card</label><div class="payment_box payment_method_preview"><p>The live payment provider renders its own secure fields here.</p></div></li>
							</ul>
							<div class="form-row place-order">
								<div class="woocommerce-terms-and-conditions-wrapper"><p class="form-row validate-required"><label class="woocommerce-form__label woocommerce-form__label-for-checkbox checkbox"><input type="checkbox" class="woocommerce-form__input woocommerce-form__input-checkbox input-checkbox" name="terms" id="terms"> <span class="woocommerce-terms-and-conditions-checkbox-text">I have read and agree to the website <a href="<?php echo esc_url( home_url( '/terms-of-service/' ) ); ?>" class="woocommerce-terms-and-conditions-link" target="_blank">terms and conditions</a></span>&nbsp;<abbr class="required" title="required">*</abbr></label></p></div>
								<button type="submit" class="button alt" name="woocommerce_checkout_place_order" id="place_order" value="Place order" data-value="Place order">Place order</button>
							</div>
						</div>
					</div>
				</aside>
			</div>
		</form>
	</section>
<?php elseif ( 'order-tracking' === $preview_route ) : ?>
	<section class="sr2-generic-page sr2-c-service" data-sr2-route="service">
		<header class="sr2-generic-head"><p class="sr2-eyebrow">Client services</p><h1>Order tracking</h1></header>
		<div class="sr2-generic-page__body">
			<div class="sr2-page-copy sr2-page-copy--generic">
				<form action="<?php echo esc_url( $preview_self ); ?>" method="get" class="woocommerce-form woocommerce-form-track-order track_order">
					<input type="hidden" name="route" value="order-tracking">
					<p>To track your order please enter your Order ID in the box below and press the “Track” button. This was given to you on your receipt and in the confirmation email you should have received.</p>
					<p class="form-row form-row-first"><label for="orderid">Order ID</label><input class="input-text" type="text" name="orderid" id="orderid" placeholder="Found in your order confirmation email." autocomplete="off"></p>
					<p class="form-row form-row-last"><label for="order_email">Billing email</label><input class="input-text" type="email" name="order_email" id="order_email" placeholder="Email you used during checkout." autocomplete="email"></p>
					<div class="clear"></div>
					<p class="form-row"><button type="submit" class="button" name="track" value="Track">Track</button></p>
				</form>
			</div>
		</div>
	</section>
<?php else : ?>
	<section class="sr2-generic-page sr2-c-account" data-sr2-route="account">
		<header class="sr2-generic-head"><p class="sr2-eyebrow">Client account</p><h1>My account</h1></header>
		<div class="sr2-generic-page__body<?php echo 'dashboard' === $preview_mode ? ' sr2-generic-page__body--wide' : ''; ?>">
			<div class="sr2-page-copy sr2-page-copy--generic">
				<div class="woocommerce">
				<?php if ( 'dashboard' === $preview_mode ) : ?>
					<nav class="woocommerce-MyAccount-navigation" aria-label="Account pages">
						<ul>
							<li class="woocommerce-MyAccount-navigation-link woocommerce-MyAccount-navigation-link--dashboard is-active"><a href="<?php echo esc_url( $preview_self . '?route=account&state=dashboard' ); ?>" aria-current="page">Dashboard</a></li>
							<li class="woocommerce-MyAccount-navigation-link woocommerce-MyAccount-navigation-link--orders"><a href="<?php echo esc_url( $preview_self . '?route=account&state=dashboard' ); ?>">Orders</a></li>
							<li class="woocommerce-MyAccount-navigation-link woocommerce-MyAccount-navigation-link--edit-address"><a href="<?php echo esc_url( $preview_self . '?route=account&state=dashboard' ); ?>">Addresses</a></li>
							<li class="woocommerce-MyAccount-navigation-link woocommerce-MyAccount-navigation-link--edit-account"><a href="<?php echo esc_url( $preview_self . '?route=account&state=dashboard' ); ?>">Account details</a></li>
							<li class="woocommerce-MyAccount-navigation-link woocommerce-MyAccount-navigation-link--customer-logout"><a href="<?php echo esc_url( $preview_self . '?route=account' ); ?>">Log out</a></li>
						</ul>
					</nav>
					<div class="woocommerce-MyAccount-content">
						<p>Hello <strong>Skyy</strong> (not Skyy? <a href="<?php echo esc_url( $preview_self . '?route=account' ); ?>">Log out</a>)</p>
						<p>From your account dashboard you can view your <a href="<?php echo esc_url( $preview_self . '?route=account&state=dashboard' ); ?>">recent orders</a>, manage your <a href="<?php echo esc_url( $preview_self . '?route=account&state=dashboard' ); ?>">shipping and billing addresses</a>, and <a href="<?php echo esc_url( $preview_self . '?route=account&state=dashboard' ); ?>">edit your password and account details</a>.</p>
					</div>
				<?php else : ?>
					<form class="woocommerce-form woocommerce-form-login login" method="get" action="<?php echo esc_url( $preview_self ); ?>">
						<input type="hidden" name="route" value="account"><input type="hidden" name="state" value="dashboard">
						<p class="form-row form-row-wide"><label for="username">Username or email address&nbsp;<span class="required">*</span></label><input type="text" class="woocommerce-Input woocommerce-Input--text input-text" name="username" id="username" autocomplete="username"></p>
						<p class="form-row form-row-wide"><label for="password">Password&nbsp;<span class="required">*</span></label><span class="password-input"><input class="woocommerce-Input woocommerce-Input--text input-text" type="password" name="password" id="password" autocomplete="current-password"><button type="button" class="show-password-input" aria-label="Show password" aria-describedby="password"></button></span></p>
						<p class="form-row"><label class="woocommerce-form__label woocommerce-form__label-for-checkbox woocommerce-form-login__rememberme"><input class="woocommerce-form__input woocommerce-form__input-checkbox" name="rememberme" type="checkbox" id="rememberme" value="forever"> <span>Remember me</span></label><button type="submit" class="woocommerce-button button woocommerce-form-login__submit" name="login" value="Log in">Log in</button></p>
						<p class="woocommerce-LostPassword lost_password"><a href="<?php echo esc_url( $preview_self . '?route=account' ); ?>">Lost your password?</a></p>
					</form>
				<?php endif; ?>
				</div>
			</div>
		</div>
	</section>
<?php endif; ?>
</div>
</main>
<?php get_footer(); ?>
