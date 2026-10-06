<?php
/**
 * Page Upgrades
 *
 * Three reusable, page-aware conversion upgrades for public storefront views:
 * reading progress, contextual next action, and confidence/discovery links.
 *
 * @package SkyyRose
 * @since   7.1.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Resolve upgrade content for the current page.
 *
 * @return array<string,mixed>
 */
function skyyrose_page_upgrade_context() {
	$context = array(
		'eyebrow'         => __( 'Your Next Move', 'skyyrose' ),
		'title'           => __( 'Wear the story forward.', 'skyyrose' ),
		'body'            => __( 'Limited runs. Intentional details. Built in The Town.', 'skyyrose' ),
		'primary_label'   => __( 'Shop the Collection', 'skyyrose' ),
		'primary_url'     => home_url( '/shop/' ),
		'secondary_label' => __( 'Enter Collections World', 'skyyrose' ),
		'secondary_url'   => home_url( '/collections-world/' ),
	);

	if ( is_front_page() ) {
		$context['eyebrow']         = __( 'Start Here', 'skyyrose' );
		$context['title']           = __( 'SkyyRose', 'skyyrose' );
		$context['body']            = __( 'Discover limited garments shaped by Oakland, family, and the refusal to fold.', 'skyyrose' );
		$context['secondary_label'] = __( 'Read Our Story', 'skyyrose' );
		$context['secondary_url']   = home_url( '/about/' );
	} elseif ( function_exists( 'is_product' ) && is_product() ) {
		$context['eyebrow']         = __( 'Complete the Decision', 'skyyrose' );
		$context['title']           = __( 'Know the fit. Own the piece.', 'skyyrose' );
		$context['body']            = __( 'Check measurements before choosing your limited-run garment.', 'skyyrose' );
		$context['primary_label']   = __( 'View Size Guide', 'skyyrose' );
		$context['primary_url']     = home_url( '/size-guide/' );
		$context['secondary_label'] = __( 'Shipping & Returns', 'skyyrose' );
		$context['secondary_url']   = home_url( '/shipping-returns/' );
	} elseif ( function_exists( 'is_cart' ) && is_cart() ) {
		$context['eyebrow']         = __( 'Ready When You Are', 'skyyrose' );
		$context['title']           = __( 'Secure your limited run.', 'skyyrose' );
		$context['body']            = __( 'Review your pieces, then move through secure checkout.', 'skyyrose' );
		$context['primary_label']   = __( 'Continue to Checkout', 'skyyrose' );
		$context['primary_url']     = function_exists( 'wc_get_checkout_url' ) ? wc_get_checkout_url() : home_url( '/checkout/' );
		$context['secondary_label'] = __( 'Keep Shopping', 'skyyrose' );
		$context['secondary_url']   = home_url( '/shop/' );
	} elseif ( function_exists( 'is_checkout' ) && is_checkout() ) {
		$context['eyebrow']         = __( 'Purchase Confidence', 'skyyrose' );
		$context['title']           = __( 'Questions before you place the order?', 'skyyrose' );
		$context['body']            = __( 'Review delivery and return details or contact the team directly.', 'skyyrose' );
		$context['primary_label']   = __( 'Shipping & Returns', 'skyyrose' );
		$context['primary_url']     = home_url( '/shipping-returns/' );
		$context['secondary_label'] = __( 'Contact Support', 'skyyrose' );
		$context['secondary_url']   = home_url( '/contact/' );
	} elseif ( is_page( 'wishlist' ) ) {
		$context['eyebrow']         = __( 'Saved Pieces', 'skyyrose' );
		$context['title']           = __( 'Build the cart with intent.', 'skyyrose' );
		$context['body']            = __( 'Wishlist should shorten decision time, not stall it. Keep browsing or move to the shop.', 'skyyrose' );
		$context['primary_label']   = __( 'Shop All Pieces', 'skyyrose' );
		$context['primary_url']     = home_url( '/shop/' );
		$context['secondary_label'] = __( 'Size Guide', 'skyyrose' );
		$context['secondary_url']   = home_url( '/size-guide/' );
	} elseif ( function_exists( 'is_shop' ) && ( is_shop() || is_product_taxonomy() ) ) {
		$context['eyebrow']         = __( 'Marketplace Flow', 'skyyrose' );
		$context['title']           = __( 'Browse. Save. Fit. Buy.', 'skyyrose' );
		$context['body']            = __( 'Use the shop archive like a buying room: compare pieces, check fit, and keep support one tap away.', 'skyyrose' );
		$context['primary_label']   = __( 'Open Wishlist', 'skyyrose' );
		$context['primary_url']     = home_url( '/wishlist/' );
		$context['secondary_label'] = __( 'Size Guide', 'skyyrose' );
		$context['secondary_url']   = home_url( '/size-guide/' );
	} elseif ( is_search() || is_404() ) {
		$context['eyebrow']         = __( 'Find Your Way Back', 'skyyrose' );
		$context['title']           = __( 'The piece moved. The story did not.', 'skyyrose' );
		$context['body']            = __( 'Return to the full shop or explore every collection as one world.', 'skyyrose' );
		$context['primary_label']   = __( 'Browse All Pieces', 'skyyrose' );
		$context['secondary_label'] = __( 'Explore Collections', 'skyyrose' );
	} elseif ( is_page_template( 'template-about.php' ) ) {
		$context['eyebrow']         = __( 'From Story to Garment', 'skyyrose' );
		$context['title']           = __( 'Believe in the vision. Wear the proof.', 'skyyrose' );
		$context['body']            = __( 'A brand named after a daughter. Built by a father. Carried by The Town.', 'skyyrose' );
		$context['secondary_label'] = __( 'Meet Every Collection', 'skyyrose' );
		$context['secondary_url']   = home_url( '/collections/' );
	} elseif ( is_page_template( 'template-contact.php' ) || is_page_template( 'template-faq.php' ) ) {
		$context['eyebrow']         = __( 'Need More Help?', 'skyyrose' );
		$context['title']           = __( 'Real support. No runaround.', 'skyyrose' );
		$context['body']            = __( 'Get fit, order, delivery, and return answers before you commit.', 'skyyrose' );
		$context['primary_label']   = __( 'Read the FAQ', 'skyyrose' );
		$context['primary_url']     = home_url( '/faq/' );
		$context['secondary_label'] = __( 'View Size Guide', 'skyyrose' );
		$context['secondary_url']   = home_url( '/size-guide/' );
	} elseif ( is_page_template( 'template-policy.php' ) || is_page_template( 'template-shipping-returns.php' ) ) {
		$context['eyebrow']         = __( 'Clear Before Checkout', 'skyyrose' );
		$context['title']           = __( 'Know the terms. Choose with confidence.', 'skyyrose' );
		$context['body']            = __( 'Review the fit guide or contact SkyyRose before placing your order.', 'skyyrose' );
		$context['primary_label']   = __( 'View Size Guide', 'skyyrose' );
		$context['primary_url']     = home_url( '/size-guide/' );
		$context['secondary_label'] = __( 'Contact Support', 'skyyrose' );
		$context['secondary_url']   = home_url( '/contact/' );
	} elseif ( is_page_template( 'template-elementor-canvas.php' ) ) {
		$context['eyebrow']         = __( 'Builder Canvas', 'skyyrose' );
		$context['title']           = __( 'Custom page. Same brand lift.', 'skyyrose' );
		$context['body']            = __( 'Even blank-builder pages keep the progress bar, proof stack, and next-step rail.', 'skyyrose' );
		$context['primary_label']   = __( 'Shop Collections', 'skyyrose' );
		$context['primary_url']     = home_url( '/collections/' );
		$context['secondary_label'] = __( 'Contact Support', 'skyyrose' );
		$context['secondary_url']   = home_url( '/contact/' );
	}

	return apply_filters( 'skyyrose_page_upgrade_context', $context );
}

/**
 * Enqueue the small progressive-enhancement layer.
 *
 * @return void
 */
function skyyrose_enqueue_page_upgrades() {
	if ( is_admin() || is_page_template( 'template-coming-soon.php' ) ) {
		return;
	}

	wp_enqueue_style(
		'skyyrose-page-upgrades',
		SKYYROSE_ASSETS_URI . '/css/page-upgrades.min.css',
		array(),
		SKYYROSE_VERSION
	);
	wp_enqueue_script(
		'skyyrose-page-upgrades',
		SKYYROSE_ASSETS_URI . '/js/page-upgrades.min.js',
		array(),
		SKYYROSE_VERSION,
		true
	);
}
add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_page_upgrades', 30 );

/**
 * Render upgrades once, before the footer when possible.
 *
 * @return void
 */
function skyyrose_render_page_upgrades() {
	static $rendered = false;

	if ( $rendered || is_admin() || is_feed() || is_page_template( 'template-coming-soon.php' ) ) {
		return;
	}
	$rendered = true;
	$context  = skyyrose_page_upgrade_context();
	?>
	<div class="sr-progress" data-sr-progress aria-hidden="true"><span></span></div>
	<aside class="sr-upgrades" aria-labelledby="sr-upgrades-title">
		<div class="sr-upgrades__action">
			<p class="sr-upgrades__eyebrow"><?php echo esc_html( $context['eyebrow'] ); ?></p>
			<h2 id="sr-upgrades-title"><?php echo esc_html( $context['title'] ); ?></h2>
			<p><?php echo esc_html( $context['body'] ); ?></p>
			<div class="sr-upgrades__buttons">
				<a class="sr-upgrades__primary" href="<?php echo esc_url( $context['primary_url'] ); ?>"><?php echo esc_html( $context['primary_label'] ); ?></a>
				<a class="sr-upgrades__secondary" href="<?php echo esc_url( $context['secondary_url'] ); ?>"><?php echo esc_html( $context['secondary_label'] ); ?></a>
			</div>
		</div>
		<ul class="sr-upgrades__proof" aria-label="<?php esc_attr_e( 'Shopping confidence', 'skyyrose' ); ?>">
			<li><strong><?php esc_html_e( 'Limited Runs', 'skyyrose' ); ?></strong><span><?php esc_html_e( 'Numbered pieces. No mass production.', 'skyyrose' ); ?></span></li>
			<li><strong><?php esc_html_e( '30-Day Returns', 'skyyrose' ); ?></strong><span><?php esc_html_e( 'Unworn pieces can come back.', 'skyyrose' ); ?></span></li>
			<li><strong><?php esc_html_e( 'Secure Checkout', 'skyyrose' ); ?></strong><span><?php esc_html_e( 'Protected payment from cart to confirmation.', 'skyyrose' ); ?></span></li>
		</ul>
		<nav class="sr-upgrades__discover" aria-label="<?php esc_attr_e( 'Continue exploring', 'skyyrose' ); ?>">
			<span><?php esc_html_e( 'Continue exploring', 'skyyrose' ); ?></span>
			<?php foreach ( skyyrose_get_marketplace_navigation_items() as $item ) : ?>
				<a href="<?php echo esc_url( home_url( $item['url'] ) ); ?>"><?php echo esc_html( $item['title'] ); ?></a>
			<?php endforeach; ?>
		</nav>
	</aside>
	<?php
}
add_action( 'get_footer', 'skyyrose_render_page_upgrades', 5 );
add_action( 'wp_footer', 'skyyrose_render_page_upgrades', 5 );
