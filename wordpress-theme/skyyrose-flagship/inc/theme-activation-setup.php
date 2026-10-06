<?php
/**
 * Theme Activation Setup
 *
 * Programmatically creates WordPress pages (with template assignments),
 * WooCommerce page settings, reading settings, and site options on
 * theme activation. Uses existence checks and versioned flags to
 * prevent duplicate creation.
 *
 * Runs on `after_switch_theme` (fresh activation) and once on `init`
 * via a versioned option flag (for sites already running the theme).
 *
 * @package SkyyRose
 * @since   4.0.0
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Version flag for this setup module.
 *
 * Bump this constant when adding new pages or changing setup logic.
 * The `init` runner uses this to determine if setup has already run.
 */
define( 'SKYYROSE_SETUP_VERSION', '4.5.0' );

/*
--------------------------------------------------------------
 * Page Definitions
 *--------------------------------------------------------------*/

/**
 * Get the list of pages the theme requires.
 *
 * Each entry maps a slug to a title, template, and optional content.
 * Templates use the WordPress `_wp_page_template` meta key.
 *
 * @since 4.0.0
 * @return array Associative array of slug => page data.
 */
function skyyrose_get_required_pages() {
	$policy_content = skyyrose_get_policy_starter_content();

	return array(
		// --- Core pages ---
		'home'                    => array(
			'title'    => __( 'Home', 'skyyrose' ),
			'template' => 'front-page.php',
			'content'  => '',
		),
		'about'                   => array(
			'title'    => __( 'About', 'skyyrose' ),
			'template' => 'template-about.php',
			'content'  => '',
		),
		'contact'                 => array(
			'title'    => __( 'Contact', 'skyyrose' ),
			'template' => 'template-contact.php',
			'content'  => '',
		),
		'pre-order'               => array(
			'title'    => __( 'Pre-Order', 'skyyrose' ),
			'template' => 'template-preorder-gateway.php',
			'content'  => '',
		),
		'collections'             => array(
			'title'    => __( 'Collections', 'skyyrose' ),
			'template' => 'page-collections.php',
			'content'  => '',
		),
		'collections-world'       => array(
			'title'    => __( 'Collections World', 'skyyrose' ),
			'template' => 'template-collections-world.php',
			'content'  => '',
		),

		// --- Collection pages ---
		'collection-black-rose'   => array(
			'title'    => __( 'Black Rose Collection', 'skyyrose' ),
			'template' => 'template-collection-black-rose.php',
			'content'  => '',
		),
		'collection-love-hurts'   => array(
			'title'    => __( 'Love Hurts Collection', 'skyyrose' ),
			'template' => 'template-collection-love-hurts.php',
			'content'  => '',
		),
		'collection-signature'    => array(
			'title'    => __( 'Signature Collection', 'skyyrose' ),
			'template' => 'template-collection-signature.php',
			'content'  => '',
		),
		'collection-kids-capsule' => array(
			'title'    => __( 'Kids Capsule', 'skyyrose' ),
			'template' => 'template-collection-kids-capsule.php',
			'content'  => '',
		),

		// --- Landing / drop pages (paid-media targets) ---
		'landing-black-rose'      => array(
			'title'    => __( 'Black Rose — Drop', 'skyyrose' ),
			'template' => 'template-landing-black-rose.php',
			'content'  => '',
		),
		'landing-love-hurts'      => array(
			'title'    => __( 'Love Hurts — Drop', 'skyyrose' ),
			'template' => 'template-landing-love-hurts.php',
			'content'  => '',
		),
		'landing-signature'       => array(
			'title'    => __( 'Signature — Drop', 'skyyrose' ),
			'template' => 'template-landing-signature.php',
			'content'  => '',
		),
		'landing-kids-capsule'    => array(
			'title'    => __( 'Kids Capsule — Drop', 'skyyrose' ),
			'template' => 'template-landing-kids-capsule.php',
			'content'  => '',
		),

		// --- Utility pages ---
		'wishlist'                => array(
			'title'    => __( 'Wishlist', 'skyyrose' ),
			'template' => 'page-wishlist.php',
			'content'  => '',
		),
		'faq'                     => array(
			'title'    => __( 'Frequently Asked Questions', 'skyyrose' ),
			'template' => 'template-faq.php',
			'content'  => '',
		),
		'shipping-returns'        => array(
			'title'    => __( 'Shipping & Returns', 'skyyrose' ),
			'template' => 'template-shipping-returns.php',
			'content'  => '',
		),
		'privacy-policy'          => array(
			'title'    => __( 'Privacy Policy', 'skyyrose' ),
			'template' => 'template-policy.php',
			'content'  => $policy_content['privacy-policy'],
		),
		'terms-of-service'        => array(
			'title'    => __( 'Terms of Service', 'skyyrose' ),
			'template' => 'template-policy.php',
			'content'  => $policy_content['terms-of-service'],
		),
		'refund-policy'           => array(
			'title'    => __( 'Refund Policy', 'skyyrose' ),
			'template' => 'template-policy.php',
			'content'  => $policy_content['refund-policy'],
		),
		'cookie-policy'           => array(
			'title'    => __( 'Cookie Policy', 'skyyrose' ),
			'template' => 'template-policy.php',
			'content'  => $policy_content['cookie-policy'],
		),
		'accessibility'           => array(
			'title'    => __( 'Accessibility Statement', 'skyyrose' ),
			'template' => 'template-policy.php',
			'content'  => $policy_content['accessibility'],
		),
		'track-order'             => array(
			'title'    => __( 'Track Your Order', 'skyyrose' ),
			'template' => 'default',
			'content'  => '<!-- wp:shortcode -->[woocommerce_order_tracking]<!-- /wp:shortcode -->',
		),
	);
}

/**
 * Editable starter copy for policy pages linked by the storefront.
 *
 * Existing page content is never overwritten. Merchants remain responsible
 * for reviewing these operational defaults against their legal requirements.
 *
 * @since 4.5.0
 * @return array<string,string>
 */
function skyyrose_get_policy_starter_content() {
	$pages = array(
		'privacy-policy'   => array(
			array( __( 'Information We Collect', 'skyyrose' ), __( 'We collect information you provide when you place an order, create an account, join our mailing list, contact support, or interact with the storefront. This may include contact, billing, shipping, order, and device information.', 'skyyrose' ) ),
			array( __( 'How We Use Information', 'skyyrose' ), __( 'We use information to process orders, provide customer support, prevent fraud, improve the storefront, and send marketing only where you have requested it or applicable law permits it.', 'skyyrose' ) ),
			array( __( 'Service Providers', 'skyyrose' ), __( 'We share only the information needed by payment, shipping, analytics, hosting, and customer-service providers to perform services for the store. We do not sell personal information.', 'skyyrose' ) ),
			array( __( 'Your Choices', 'skyyrose' ), __( 'You may request access, correction, or deletion of personal information, or unsubscribe from marketing at any time by contacting support@skyyrose.co.', 'skyyrose' ) ),
		),
		'terms-of-service' => array(
			array( __( 'Store Terms', 'skyyrose' ), __( 'By using this storefront or placing an order, you agree to these terms and to provide current, accurate account and payment information.', 'skyyrose' ) ),
			array( __( 'Orders and Pricing', 'skyyrose' ), __( 'Orders are subject to acceptance and product availability. We may correct pricing or description errors, limit quantities, or cancel and refund an order when necessary.', 'skyyrose' ) ),
			array( __( 'Intellectual Property', 'skyyrose' ), __( 'SkyyRose names, artwork, photography, product designs, and site content remain the property of The Skyy Rose Collection LLC or their respective licensors.', 'skyyrose' ) ),
			array( __( 'Responsible Use', 'skyyrose' ), __( 'Do not misuse the storefront, interfere with its security, submit fraudulent orders, scrape protected content, or use our work without permission.', 'skyyrose' ) ),
		),
		'refund-policy'    => array(
			array( __( 'Return Window', 'skyyrose' ), __( 'Eligible unworn items may be returned within 30 days of delivery in original condition, with tags attached and original packaging.', 'skyyrose' ) ),
			array( __( 'Exceptions', 'skyyrose' ), __( 'Final-sale items, gift cards, and worn, washed, altered, or tagless pieces are not eligible for return. Product-specific exceptions are shown before purchase.', 'skyyrose' ) ),
			array( __( 'Refund Timing', 'skyyrose' ), __( 'Approved refunds are sent to the original payment method after inspection. Bank processing times vary. Contact support@skyyrose.co with your order number to begin.', 'skyyrose' ) ),
		),
		'cookie-policy'    => array(
			array( __( 'Essential Cookies', 'skyyrose' ), __( 'Essential cookies keep the cart, checkout, account security, preferences, and fraud protection working. The storefront cannot operate correctly without them.', 'skyyrose' ) ),
			array( __( 'Analytics and Marketing', 'skyyrose' ), __( 'With consent where required, analytics and marketing technologies help us understand storefront use and measure campaigns. These tools may be provided by third parties.', 'skyyrose' ) ),
			array( __( 'Managing Cookies', 'skyyrose' ), __( 'Use the cookie controls shown on the storefront or your browser settings to change non-essential cookie choices. Blocking essential cookies may prevent checkout or account features from working.', 'skyyrose' ) ),
		),
		'accessibility'    => array(
			array( __( 'Our Commitment', 'skyyrose' ), __( 'SkyyRose works to provide an inclusive storefront aligned with WCAG 2.2 Level AA, including keyboard access, readable contrast, meaningful structure, and reduced-motion support.', 'skyyrose' ) ),
			array( __( 'Ongoing Work', 'skyyrose' ), __( 'We test core shopping journeys, improve content and components as standards evolve, and review third-party commerce integrations for accessibility barriers.', 'skyyrose' ) ),
			array( __( 'Accessibility Feedback', 'skyyrose' ), __( 'If you encounter a barrier, email support@skyyrose.co with the page, task, device, and assistive technology involved. We will work to provide an accessible alternative.', 'skyyrose' ) ),
		),
	);

	$content = array();
	foreach ( $pages as $slug => $sections ) {
		$content[ $slug ] = '';
		foreach ( $sections as $section ) {
			$content[ $slug ] .= '<!-- wp:heading --><h2 class="wp-block-heading">' . esc_html( $section[0] ) . '</h2><!-- /wp:heading -->';
			$content[ $slug ] .= '<!-- wp:paragraph --><p>' . esc_html( $section[1] ) . '</p><!-- /wp:paragraph -->';
		}
	}

	return $content;
}

/*
--------------------------------------------------------------
 * Page Creation
 *--------------------------------------------------------------*/

/**
 * Create all required pages and assign templates.
 *
 * Checks for existing pages by slug before creating. Assigns the
 * `_wp_page_template` meta so WordPress routes to the correct
 * template file automatically.
 *
 * @since 4.0.0
 * @return array Map of slug => page ID for created/existing pages.
 */
function skyyrose_create_required_pages() {
	$pages    = skyyrose_get_required_pages();
	$page_ids = array();

	foreach ( $pages as $slug => $data ) {
		// Check if page already exists by slug.
		$existing = get_page_by_path( $slug );

		if ( $existing ) {
			$page_id = $existing->ID;

			// Ensure template is assigned even on existing pages.
			$current_template = get_post_meta( $page_id, '_wp_page_template', true );
			if ( empty( $current_template ) || 'default' === $current_template ) {
				update_post_meta( $page_id, '_wp_page_template', sanitize_file_name( $data['template'] ) );
			}
		} else {
			$page_id = wp_insert_post(
				array(
					'post_title'   => $data['title'],
					'post_name'    => $slug,
					'post_content' => $data['content'],
					'post_status'  => 'publish',
					'post_type'    => 'page',
					'post_author'  => 1,
					'meta_input'   => array(
						'_wp_page_template' => sanitize_file_name( $data['template'] ),
					),
				),
				true
			);

			if ( is_wp_error( $page_id ) ) {
				continue;
			}
		}

		$page_ids[ $slug ] = $page_id;
	}

	return $page_ids;
}

/*
--------------------------------------------------------------
 * Reading Settings (Static Front Page)
 *--------------------------------------------------------------*/

/**
 * Set the "Home" page as the static front page.
 *
 * Configures WordPress to use a static page (not latest posts)
 * as the front page, pointing to the "Home" page we created.
 *
 * @since 4.0.0
 * @param array $page_ids Map of slug => page ID from page creation.
 * @return void
 */
function skyyrose_configure_reading_settings( $page_ids ) {
	if ( empty( $page_ids['home'] ) ) {
		return;
	}

	$home_id = absint( $page_ids['home'] );

	// Set static front page.
	update_option( 'show_on_front', 'page' );
	update_option( 'page_on_front', $home_id );

	// No dedicated posts page (this is a product site, not a blog).
	// Only set if not already configured.
	if ( ! get_option( 'page_for_posts' ) ) {
		update_option( 'page_for_posts', 0 );
	}
}

/*
--------------------------------------------------------------
 * Site Identity & SEO Options
 *--------------------------------------------------------------*/

/**
 * Set site identity options for SEO and branding.
 *
 * Only sets options that are empty or have WordPress defaults.
 * Does NOT overwrite user-configured values.
 *
 * @since 4.0.0
 * @return void
 */
function skyyrose_configure_site_options() {
	// Site title — only if still default "Just another WordPress site" or empty.
	$current_desc = get_option( 'blogdescription' );
	if ( empty( $current_desc ) || 'Just another WordPress site' === $current_desc ) {
		update_option( 'blogdescription', __( 'Premium streetwear from Oakland, CA.', 'skyyrose' ) );
	}

	// Permalink structure — pretty permalinks.
	$current_permalink = get_option( 'permalink_structure' );
	if ( empty( $current_permalink ) ) {
		update_option( 'permalink_structure', '/%postname%/' );
		flush_rewrite_rules();
	}

	// Timezone.
	if ( ! get_option( 'timezone_string' ) ) {
		update_option( 'timezone_string', 'America/Los_Angeles' );
	}

	// Date format.
	update_option( 'date_format', 'F j, Y' );

	// Pre-order deadline default (30 days from now).
	if ( ! get_option( 'skyyrose_preorder_deadline' ) ) {
		update_option( 'skyyrose_preorder_deadline', gmdate( 'Y-m-d', strtotime( '+30 days' ) ) );
	}
}

/*
--------------------------------------------------------------
 * WooCommerce Page Assignments
 *--------------------------------------------------------------*/

/**
 * Assign WooCommerce-required pages (shop, cart, checkout, my-account).
 *
 * WooCommerce creates these pages on its own activation, but if they
 * don't exist or aren't assigned, this ensures they are.
 *
 * @since 4.0.0
 * @param array $page_ids Map of slug => page ID.
 * @return void
 */
function skyyrose_configure_woocommerce_settings( $page_ids ) {
	if ( ! class_exists( 'WooCommerce' ) ) {
		return;
	}

	// WooCommerce pages — only create if they don't already exist.
	$wc_pages = array(
		'shop'       => array(
			'title'  => __( 'Shop', 'skyyrose' ),
			'option' => 'woocommerce_shop_page_id',
		),
		'cart'       => array(
			'title'  => __( 'Cart', 'skyyrose' ),
			'option' => 'woocommerce_cart_page_id',
		),
		'checkout'   => array(
			'title'  => __( 'Checkout', 'skyyrose' ),
			'option' => 'woocommerce_checkout_page_id',
		),
		'my-account' => array(
			'title'  => __( 'My Account', 'skyyrose' ),
			'option' => 'woocommerce_myaccount_page_id',
		),
	);

	foreach ( $wc_pages as $slug => $wc_data ) {
		$current_page_id = absint( get_option( $wc_data['option'] ) );

		// If the option is set and the page exists, skip.
		if ( $current_page_id > 0 && get_post( $current_page_id ) ) {
			continue;
		}

		// Check if page exists by slug.
		$existing = get_page_by_path( $slug );
		if ( $existing ) {
			update_option( $wc_data['option'], $existing->ID );
			continue;
		}

		// Create the page.
		$new_id = wp_insert_post(
			array(
				'post_title'   => $wc_data['title'],
				'post_name'    => $slug,
				'post_content' => '',
				'post_status'  => 'publish',
				'post_type'    => 'page',
				'post_author'  => 1,
			),
			true
		);

		if ( ! is_wp_error( $new_id ) ) {
			update_option( $wc_data['option'], $new_id );
		}
	}

	// WooCommerce general settings.
	update_option( 'woocommerce_currency', 'USD' );
	update_option( 'woocommerce_enable_guest_checkout', 'yes' );
	update_option( 'woocommerce_enable_signup_and_login_from_checkout', 'yes' );
	update_option( 'woocommerce_manage_stock', 'yes' );

	// Image sizes for luxury product display.
	update_option( 'woocommerce_single_image_width', 600 );
	update_option( 'woocommerce_thumbnail_image_width', 300 );
}

/*
--------------------------------------------------------------
 * Master Orchestrator
 *--------------------------------------------------------------*/

/**
 * Run the full theme activation setup.
 *
 * Orchestrates page creation, reading settings, site options,
 * and WooCommerce configuration in the correct order.
 *
 * @since 4.0.0
 * @return void
 */
function skyyrose_run_activation_setup() {
	// 1. Create all required pages.
	$page_ids = skyyrose_create_required_pages();

	// 2. Set static front page.
	skyyrose_configure_reading_settings( $page_ids );

	// 3. Set site identity defaults.
	skyyrose_configure_site_options();

	// 4. Configure WooCommerce pages and settings.
	skyyrose_configure_woocommerce_settings( $page_ids );
}

// Run on theme activation.
add_action( 'after_switch_theme', 'skyyrose_run_activation_setup' );

// Run once on `init` for sites already running the theme.
// Versioned flag ensures it runs exactly once per setup version.
add_action(
	'init',
	function () {
		if ( get_option( 'skyyrose_activation_setup_version' ) === SKYYROSE_SETUP_VERSION ) {
			return;
		}
		skyyrose_run_activation_setup();
		update_option( 'skyyrose_activation_setup_version', SKYYROSE_SETUP_VERSION );
	},
	30 // After product-taxonomy.php (priority 20) so WC categories exist.
);
