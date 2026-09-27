<?php
/**
 * Marketplace presentation registry.
 *
 * This registry owns install-time routes, editable starter copy, navigation,
 * and WooCommerce page shells. It never owns products, prices, stock, orders,
 * media, or payment state.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/**
 * Validate the product-card media approval contract against the product SOT adapter.
 *
 * @param array<string,mixed> $manifest Product-card media manifest.
 * @param array<string,mixed> $registry Product presentation registry.
 * @return bool
 */
function skyyrose2_validate_product_card_media_contract( $manifest, $registry ) {
	if ( ! is_array( $manifest ) || ! is_array( $registry ) ) {
		return false;
	}
	$registry_hash = isset( $registry['product_sot_sha256'] ) ? (string) $registry['product_sot_sha256'] : '';
	$manifest_hash = isset( $manifest['product_sot_sha256'] ) ? (string) $manifest['product_sot_sha256'] : '';
	$records       = isset( $registry['products'] ) && is_array( $registry['products'] ) ? $registry['products'] : array();
	$media_records = isset( $manifest['products'] ) && is_array( $manifest['products'] ) ? $manifest['products'] : array();
	$media_hashes  = isset( $manifest['product_hashes'] ) && is_array( $manifest['product_hashes'] ) ? $manifest['product_hashes'] : array();
	$integrity     = isset( $manifest['asset_integrity'] ) && is_array( $manifest['asset_integrity'] ) ? $manifest['asset_integrity'] : array();
	if ( ! $registry_hash || ! $manifest_hash || ! hash_equals( $registry_hash, $manifest_hash ) ) {
		return false;
	}

	$registry_skus = array_keys( $records );
	$media_skus    = array_keys( $media_records );
	$hash_skus     = array_keys( $media_hashes );
	sort( $registry_skus );
	sort( $media_skus );
	sort( $hash_skus );
	if ( $registry_skus !== $media_skus || $registry_skus !== $hash_skus ) {
		return false;
	}

	$allowed_roles = array( 'on_model_front', 'on_model_back', 'mannequin_front', 'mannequin_back', 'render_3d', 'packshot' );
	$approved_skus = array();
	foreach ( $records as $sku => $record ) {
		$media_record  = isset( $media_records[ $sku ] ) && is_array( $media_records[ $sku ] ) ? $media_records[ $sku ] : array();
		$expected_hash = isset( $record['product_sot_hash'] ) ? (string) $record['product_sot_hash'] : '';
		$approved_hash = isset( $media_hashes[ $sku ] ) ? (string) $media_hashes[ $sku ] : '';
		$expected_collection = isset( $record['collection'] ) ? (string) $record['collection'] : '';
		$approved_collection = isset( $media_record['collection'] ) ? (string) $media_record['collection'] : '';
		if (
			! $expected_hash ||
			! $approved_hash ||
			! hash_equals( $expected_hash, $approved_hash ) ||
			! $expected_collection ||
			! hash_equals( $expected_collection, $approved_collection )
		) {
			return false;
		}

		$views = isset( $media_record['views'] ) && is_array( $media_record['views'] ) ? $media_record['views'] : array();
		if ( ! $views ) {
			if ( empty( $media_record['status'] ) || empty( $media_record['reason'] ) || isset( $integrity[ $sku ] ) ) {
				return false;
			}
			continue;
		}
		if ( ! empty( $media_record['status'] ) && 'APPROVED' !== $media_record['status'] ) {
			return false;
		}
		$roles = array();
		foreach ( $views as $view ) {
			$role = isset( $view['role'] ) ? (string) $view['role'] : '';
			if ( ! in_array( $role, $allowed_roles, true ) || isset( $roles[ $role ] ) ) {
				return false;
			}
			$roles[ $role ] = true;
		}
		if ( 'on_model_front' !== ( $views[0]['role'] ?? '' ) ) {
			return false;
		}
		$integrity_roles = isset( $integrity[ $sku ] ) && is_array( $integrity[ $sku ] ) ? array_keys( $integrity[ $sku ] ) : array();
		sort( $integrity_roles );
		$role_keys = array_keys( $roles );
		sort( $role_keys );
		if ( $integrity_roles !== $role_keys ) {
			return false;
		}
		$approved_skus[] = $sku;
	}

	$integrity_skus = array_keys( $integrity );
	sort( $approved_skus );
	sort( $integrity_skus );
	return $approved_skus === $integrity_skus;
}

/**
 * Convert titled sections into portable block markup.
 *
 * @param array<int,array{title:string,body:string}> $sections Content sections.
 * @return string
 */
function skyyrose2_marketplace_block_sections( $sections ) {
	$content = '';
	foreach ( $sections as $section ) {
		$content .= '<!-- wp:heading --><h2 class="wp-block-heading">' . esc_html( $section['title'] ) . '</h2><!-- /wp:heading -->';
		$content .= '<!-- wp:paragraph --><p>' . esc_html( $section['body'] ) . '</p><!-- /wp:paragraph -->';
	}
	return $content;
}

/**
 * Editable policy and service starter copy.
 *
 * The importer never overwrites existing merchant content. Marketplace buyers
 * must review these operational defaults for their jurisdiction and policies.
 *
 * @return array<string,string>
 */
function skyyrose2_marketplace_service_content() {
	return array(
		'faq'              => skyyrose2_marketplace_block_sections(
			array(
				array( 'title' => __( 'How do I choose a size?', 'skyyrose-flagship-2' ), 'body' => __( 'Use the measurements on the size guide and compare them with a piece you already own. Product-specific fit notes remain on the product page.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'When will a pre-order ship?', 'skyyrose-flagship-2' ), 'body' => __( 'Contact Client Services for a shipping estimate before ordering. A pre-order label does not establish a shipping date, stock reservation, or delayed payment.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'How do I get order help?', 'skyyrose-flagship-2' ), 'body' => __( 'Send Client Services your order number and the email used at checkout. Never send payment-card details by email.', 'skyyrose-flagship-2' ) ),
			)
		),
		'shipping-returns' => skyyrose2_marketplace_block_sections(
			array(
				array( 'title' => __( 'Order processing', 'skyyrose-flagship-2' ), 'body' => __( 'Your order status appears in your account. Contact Client Services with questions about processing and shipping.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'Shipping updates', 'skyyrose-flagship-2' ), 'body' => __( 'Tracking is emailed when the carrier accepts the parcel. Carrier scans and delivery estimates remain the carrier’s live authority.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'US return requests', 'skyyrose-flagship-2' ), 'body' => __( 'Eligible US returns must be started within 30 days of confirmed delivery. Email Client Services with the order number, item, and reason before sending anything back; on business days, the policy provides a prepaid USPS return label within 24 hours.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'Return eligibility and refunds', 'skyyrose-flagship-2' ), 'body' => __( 'Items must be unworn, unwashed, unaltered, with tags attached and original packaging. After receipt and inspection, approved refunds return to the original payment method within 5–7 business days. Original outbound shipping is not refunded unless the policy’s damaged, defective, or incorrect-item exception applies.', 'skyyrose-flagship-2' ) ),
			)
		),
		'returns-exchanges' => skyyrose2_marketplace_block_sections(
			array(
				array( 'title' => __( 'Before you send a piece back', 'skyyrose-flagship-2' ), 'body' => __( 'Start with Client Services before shipping anything. Eligible returns must be requested within 30 days of confirmed delivery and meet the policy’s unworn, unwashed, unaltered, tagged, and original-packaging requirements.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'What to include in your request', 'skyyrose-flagship-2' ), 'body' => __( 'Send the order number, the email used at checkout, the piece and size, and a brief reason for the request. Do not email payment-card details.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'Free US size or color exchanges', 'skyyrose-flagship-2' ), 'body' => __( 'US exchanges for a different size or color of the same style are free. Client Services confirms replacement availability, sends a prepaid USPS return label, and the original item must be shipped within 14 days of receiving that label. Once the original is received and inspected, the replacement ships at no additional charge.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'Exceptions and international exchanges', 'skyyrose-flagship-2' ), 'body' => __( 'Final Sale, customized or personalized, and ineligible-condition items cannot be returned or exchanged except where the policy’s damaged, defective, or incorrect-item exception applies. International customers pay return shipping to the US facility; after inspection, an eligible replacement ships at no additional charge.', 'skyyrose-flagship-2' ) ),
			)
		),
		'size-guide'       => skyyrose2_marketplace_block_sections(
			array(
				array( 'title' => __( 'Measure a piece you own', 'skyyrose-flagship-2' ), 'body' => __( 'Lay a similar garment flat without stretching it. Compare chest, body length, waist, rise, and inseam with the measurements published for the piece.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'Between sizes', 'skyyrose-flagship-2' ), 'body' => __( 'Choose based on the silhouette you want and the product-specific fit note. Client Services can help compare measurements before purchase.', 'skyyrose-flagship-2' ) ),
			)
		),
		'privacy-policy'   => skyyrose2_marketplace_block_sections(
			array(
				array( 'title' => __( 'Information collected', 'skyyrose-flagship-2' ), 'body' => __( 'The store processes information needed for orders, accounts, support, fraud prevention, and requested communications. This may include contact, billing, shipping, order, and device information.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'How information is used', 'skyyrose-flagship-2' ), 'body' => __( 'Information is used to operate the storefront, fulfill orders, provide support, protect customers, and improve service. Marketing is sent only where permission or applicable law allows it.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'Your choices', 'skyyrose-flagship-2' ), 'body' => __( 'Customers may request access, correction, or deletion where applicable, and may unsubscribe from marketing at any time.', 'skyyrose-flagship-2' ) ),
			)
		),
		'terms-of-service' => skyyrose2_marketplace_block_sections(
			array(
				array( 'title' => __( 'Store terms', 'skyyrose-flagship-2' ), 'body' => __( 'By using the storefront or placing an order, customers agree to provide current information and use the store lawfully.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'Orders and pricing', 'skyyrose-flagship-2' ), 'body' => __( 'Orders remain subject to acceptance, payment confirmation, and availability. Pricing or description errors may be corrected before fulfillment, with notice and an appropriate refund where required.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'Intellectual property', 'skyyrose-flagship-2' ), 'body' => __( 'Brand names, artwork, photography, product designs, and site content remain the property of their respective owners and licensors.', 'skyyrose-flagship-2' ) ),
			)
		),
		'accessibility'    => skyyrose2_marketplace_block_sections(
			array(
				array( 'title' => __( 'Our commitment', 'skyyrose-flagship-2' ), 'body' => __( 'SkyyRose works toward an inclusive shopping experience aligned with WCAG 2.2 Level AA, including keyboard access, readable contrast, meaningful structure, and reduced-motion support.', 'skyyrose-flagship-2' ) ),
				array( 'title' => __( 'Accessibility feedback', 'skyyrose-flagship-2' ), 'body' => __( 'If you encounter a barrier, contact Client Services with the page, task, device, browser, and assistive technology involved so an accessible alternative can be provided.', 'skyyrose-flagship-2' ) ),
			)
		),
	);
}

/**
 * Theme-owned page definitions for the one-click importer.
 *
 * @return array<string,array<string,mixed>>
 */
function skyyrose2_marketplace_pages() {
	$service = skyyrose2_marketplace_service_content();
	return array(
		'home'             => array( 'title' => __( 'Home', 'skyyrose-flagship-2' ), 'path' => 'home', 'template' => 'default', 'content' => '' ),
		'collections'      => array( 'title' => __( 'Collections', 'skyyrose-flagship-2' ), 'path' => 'collections', 'template' => 'default', 'content' => '' ),
		'signature'        => array( 'title' => __( 'Signature', 'skyyrose-flagship-2' ), 'path' => 'collections/signature', 'parent' => 'collections', 'template' => 'template-collection.php', 'content' => '' ),
		'black-rose'       => array( 'title' => __( 'Black Rose', 'skyyrose-flagship-2' ), 'path' => 'collections/black-rose', 'parent' => 'collections', 'template' => 'template-collection.php', 'content' => '' ),
		'love-hurts'       => array( 'title' => __( 'Love Hurts', 'skyyrose-flagship-2' ), 'path' => 'collections/love-hurts', 'parent' => 'collections', 'template' => 'template-collection.php', 'content' => '' ),
		'kids-capsule'     => array( 'title' => __( 'Kids Capsule', 'skyyrose-flagship-2' ), 'path' => 'collections/kids-capsule', 'parent' => 'collections', 'template' => 'template-collection.php', 'content' => '' ),
		'worlds'           => array( 'title' => __( 'Worlds', 'skyyrose-flagship-2' ), 'path' => 'worlds', 'slug' => 'worlds', 'template' => 'default', 'content' => '' ),
		'immersive-signature' => array( 'title' => __( 'Signature — Full Scene', 'skyyrose-flagship-2' ), 'path' => 'worlds/signature', 'slug' => 'signature', 'parent' => 'worlds', 'template' => 'template-immersive-signature.php', 'content' => '' ),
		'immersive-black-rose' => array( 'title' => __( 'Black Rose — Full Scene', 'skyyrose-flagship-2' ), 'path' => 'worlds/black-rose', 'slug' => 'black-rose', 'parent' => 'worlds', 'template' => 'template-immersive-black-rose.php', 'content' => '' ),
		'immersive-love-hurts' => array( 'title' => __( 'Love Hurts — Full Scene', 'skyyrose-flagship-2' ), 'path' => 'worlds/love-hurts', 'slug' => 'love-hurts', 'parent' => 'worlds', 'template' => 'template-immersive-love-hurts.php', 'content' => '' ),
		'immersive-kids-capsule' => array( 'title' => __( 'Kids Capsule — Full Scene', 'skyyrose-flagship-2' ), 'path' => 'worlds/kids-capsule', 'slug' => 'kids-capsule', 'parent' => 'worlds', 'template' => 'template-immersive-kids-capsule.php', 'content' => '' ),
		'pre-order'        => array( 'title' => __( 'Pre-Order', 'skyyrose-flagship-2' ), 'path' => 'pre-order', 'template' => 'default', 'content' => '' ),
		'about'            => array( 'title' => __( 'About', 'skyyrose-flagship-2' ), 'path' => 'about', 'template' => 'default', 'content' => '' ),
		'contact'          => array( 'title' => __( 'Contact', 'skyyrose-flagship-2' ), 'path' => 'contact', 'template' => 'default', 'content' => '' ),
		'journal'          => array( 'title' => __( 'Journal', 'skyyrose-flagship-2' ), 'path' => 'journal', 'template' => 'default', 'content' => '' ),
		'wishlist'         => array( 'title' => __( 'Wishlist', 'skyyrose-flagship-2' ), 'path' => 'wishlist', 'template' => 'page-wishlist.php', 'content' => '' ),
		'faq'              => array( 'title' => __( 'Frequently Asked Questions', 'skyyrose-flagship-2' ), 'path' => 'faq', 'template' => 'default', 'content' => $service['faq'] ),
		'shipping-returns' => array( 'title' => __( 'Shipping + Returns', 'skyyrose-flagship-2' ), 'path' => 'shipping-returns', 'template' => 'default', 'content' => $service['shipping-returns'] ),
		'returns-exchanges' => array( 'title' => __( 'Returns + Exchanges', 'skyyrose-flagship-2' ), 'path' => 'returns-exchanges', 'template' => 'default', 'content' => $service['returns-exchanges'] ),
		'size-guide'       => array( 'title' => __( 'Size Guide', 'skyyrose-flagship-2' ), 'path' => 'size-guide', 'template' => 'default', 'content' => $service['size-guide'] ),
		'privacy-policy'   => array( 'title' => __( 'Privacy Policy', 'skyyrose-flagship-2' ), 'path' => 'privacy-policy', 'template' => 'default', 'content' => $service['privacy-policy'] ),
		'terms-of-service' => array( 'title' => __( 'Terms of Service', 'skyyrose-flagship-2' ), 'path' => 'terms-of-service', 'template' => 'default', 'content' => $service['terms-of-service'] ),
		'accessibility'    => array( 'title' => __( 'Accessibility Statement', 'skyyrose-flagship-2' ), 'path' => 'accessibility', 'template' => 'default', 'content' => $service['accessibility'] ),
	);
}

/**
 * WooCommerce classic-page shells. WooCommerce remains the state authority.
 *
 * @return array<string,array<string,string>>
 */
function skyyrose2_marketplace_woocommerce_pages() {
	return array(
		'shop'       => array( 'title' => __( 'Shop', 'skyyrose-flagship-2' ), 'content' => '', 'option' => 'woocommerce_shop_page_id' ),
		'cart'       => array( 'title' => __( 'Bag', 'skyyrose-flagship-2' ), 'content' => '<!-- wp:shortcode -->[woocommerce_cart]<!-- /wp:shortcode -->', 'option' => 'woocommerce_cart_page_id' ),
		'checkout'   => array( 'title' => __( 'Checkout', 'skyyrose-flagship-2' ), 'content' => '<!-- wp:shortcode -->[woocommerce_checkout]<!-- /wp:shortcode -->', 'option' => 'woocommerce_checkout_page_id' ),
		'my-account' => array( 'title' => __( 'My Account', 'skyyrose-flagship-2' ), 'content' => '<!-- wp:shortcode -->[woocommerce_my_account]<!-- /wp:shortcode -->', 'option' => 'woocommerce_myaccount_page_id' ),
		'track-order' => array( 'title' => __( 'Track Order', 'skyyrose-flagship-2' ), 'content' => '<!-- wp:shortcode -->[woocommerce_order_tracking]<!-- /wp:shortcode -->', 'option' => '' ),
	);
}

/**
 * Navigation definitions consumed by the importer.
 *
 * @return array<string,array<string,mixed>>
 */
function skyyrose2_marketplace_menus() {
	return array(
		'primary' => array(
			'name'  => 'SkyyRose Primary',
			'items' => array(
				array( 'title' => __( 'Collections', 'skyyrose-flagship-2' ), 'page' => 'collections', 'children' => array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ) ),
				array( 'title' => __( 'Shop', 'skyyrose-flagship-2' ), 'page' => 'shop' ),
				array( 'title' => __( 'Pre-Order', 'skyyrose-flagship-2' ), 'page' => 'pre-order' ),
				array( 'title' => __( 'Journal', 'skyyrose-flagship-2' ), 'page' => 'journal' ),
				array( 'title' => __( 'About', 'skyyrose-flagship-2' ), 'page' => 'about' ),
				array( 'title' => __( 'Contact', 'skyyrose-flagship-2' ), 'page' => 'contact' ),
			),
		),
		'footer'  => array(
			'name'  => 'SkyyRose Footer',
			'items' => array(
				array( 'title' => __( 'Shipping + Returns', 'skyyrose-flagship-2' ), 'page' => 'shipping-returns' ),
				array( 'title' => __( 'Returns + Exchanges', 'skyyrose-flagship-2' ), 'page' => 'returns-exchanges' ),
				array( 'title' => __( 'Size Guide', 'skyyrose-flagship-2' ), 'page' => 'size-guide' ),
				array( 'title' => __( 'FAQ', 'skyyrose-flagship-2' ), 'page' => 'faq' ),
				array( 'title' => __( 'Privacy Policy', 'skyyrose-flagship-2' ), 'page' => 'privacy-policy' ),
				array( 'title' => __( 'Terms of Service', 'skyyrose-flagship-2' ), 'page' => 'terms-of-service' ),
				array( 'title' => __( 'Accessibility', 'skyyrose-flagship-2' ), 'page' => 'accessibility' ),
			),
		),
	);
}
