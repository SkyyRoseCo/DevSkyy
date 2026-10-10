<?php
/**
 * Standalone structural test for marketplace page and menu definitions.
 *
 * @package SkyyRoseFlagship2
 */

define( 'ABSPATH', __DIR__ );

/**
 * Minimal translation stub for registry-only testing.
 *
 * @param string $text Text.
 * @param string $domain Text domain.
 * @return string
 */
function __( $text, $domain ) { // phpcs:ignore WordPress.NamingConventions.PrefixAllGlobals.NonPrefixedFunctionFound -- WordPress API test stub.
	if ( 'skyyrose-flagship-2' !== $domain ) {
		throw new RuntimeException( 'Unexpected translation domain.' );
	}
	return $text;
}

/**
 * Minimal escaping stub for block-markup generation.
 *
 * @param string $text Text.
 * @return string
 */
function esc_html( $text ) { // phpcs:ignore WordPress.NamingConventions.PrefixAllGlobals.NonPrefixedFunctionFound -- WordPress API test stub.
	return htmlspecialchars( $text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8' );
}

require dirname( __DIR__ ) . '/inc/presentation-registry.php';

/**
 * Fail with an actionable assertion message.
 *
 * @param bool   $condition Condition.
 * @param string $message Failure message.
 * @return void
 */
function skyyrose2_registry_assert( $condition, $message ) {
	if ( ! $condition ) {
		throw new RuntimeException( $message );
	}
}

$pages    = skyyrose2_marketplace_pages();
$woo      = skyyrose2_marketplace_woocommerce_pages();
$menus    = skyyrose2_marketplace_menus();
$required = array( 'home', 'collections', 'signature', 'black-rose', 'love-hurts', 'kids-capsule', 'worlds', 'immersive-signature', 'immersive-black-rose', 'immersive-love-hurts', 'immersive-kids-capsule', 'pre-order', 'about', 'contact', 'journal', 'wishlist' );

foreach ( $required as $key ) {
	skyyrose2_registry_assert( isset( $pages[ $key ] ), "Missing required page definition: {$key}" );
}

$service_content = skyyrose2_marketplace_service_content();
skyyrose2_registry_assert( str_contains( $service_content['shipping-returns'], 'within 30 days of confirmed delivery' ), 'Shipping and returns summary must retain the published 30-day US return window.' );
skyyrose2_registry_assert( str_contains( $service_content['shipping-returns'], 'prepaid USPS return label within 24 hours' ), 'Shipping and returns summary must retain the published prepaid US-label timing.' );
skyyrose2_registry_assert( str_contains( $service_content['shipping-returns'], 'unworn, unwashed, unaltered, with tags attached and original packaging' ), 'Shipping and returns summary must retain published return eligibility conditions.' );
skyyrose2_registry_assert( str_contains( $service_content['returns-exchanges'], 'Free US size or color exchanges' ), 'Returns summary must identify the published free US same-style exchange scope.' );
skyyrose2_registry_assert( str_contains( $service_content['returns-exchanges'], 'within 14 days of receiving that label' ), 'Returns summary must retain the published 14-day exchange-label window.' );
skyyrose2_registry_assert( str_contains( $service_content['returns-exchanges'], 'Final Sale, customized or personalized, and ineligible-condition items cannot be returned or exchanged' ), 'Returns summary must retain published exchange exceptions.' );
skyyrose2_registry_assert( ! str_contains( $service_content['returns-exchanges'], 'reviewed case by case' ), 'Returns summary must not contradict the published free US same-style exchange policy.' );

$paths = array();
foreach ( $pages as $key => $page ) {
	skyyrose2_registry_assert( ! empty( $page['path'] ), "Page path is empty: {$key}" );
	skyyrose2_registry_assert( ! isset( $paths[ $page['path'] ] ), "Duplicate page path: {$page['path']}" );
	$paths[ $page['path'] ] = true;
	if ( ! empty( $page['parent'] ) ) {
		skyyrose2_registry_assert( isset( $pages[ $page['parent'] ] ), "Unknown parent for {$key}" );
	}
	if ( ! empty( $page['slug'] ) ) {
		$path_parts = explode( '/', trim( $page['path'], '/' ) );
		skyyrose2_registry_assert( $page['slug'] === end( $path_parts ), "Slug/path mismatch for {$key}" );
	}
	if ( 'default' !== $page['template'] ) {
		skyyrose2_registry_assert( is_file( dirname( __DIR__ ) . '/' . $page['template'] ), "Missing page template: {$page['template']}" );
	}
}

$woo_options = array();
foreach ( $woo as $key => $page ) {
	if ( $page['option'] ) {
		skyyrose2_registry_assert( ! isset( $woo_options[ $page['option'] ] ), "Duplicate WooCommerce page option: {$page['option']}" );
		$woo_options[ $page['option'] ] = $key;
	}
}

foreach ( $menus as $location => $menu ) {
	skyyrose2_registry_assert( in_array( $location, array( 'primary', 'footer' ), true ), "Unsupported menu location: {$location}" );
	foreach ( $menu['items'] as $item ) {
		$page_key = $item['page'];
		skyyrose2_registry_assert( isset( $pages[ $page_key ] ) || isset( $woo[ $page_key ] ), "Menu references unknown page: {$page_key}" );
		foreach ( $item['children'] ?? array() as $child_key ) {
			skyyrose2_registry_assert( isset( $pages[ $child_key ] ), "Menu references unknown child page: {$child_key}" );
		}
	}
}

$theme_dir = dirname( __DIR__ );
$product_registry = json_decode( file_get_contents( $theme_dir . '/data/product-presentation-registry.json' ), true ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
$product_media    = json_decode( file_get_contents( $theme_dir . '/data/opening-product-media.json' ), true ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
skyyrose2_registry_assert( skyyrose2_validate_product_card_media_contract( $product_media, $product_registry ), 'Current product-card media contract must validate.' );

$stale_global = $product_media;
$stale_global['product_sot_sha256'] = str_repeat( '0', 64 );
skyyrose2_registry_assert( ! skyyrose2_validate_product_card_media_contract( $stale_global, $product_registry ), 'Stale global product SOT hash must fail closed.' );

$stale_sku = $product_media;
$stale_sku['product_hashes']['br-001'] = str_repeat( '0', 64 );
skyyrose2_registry_assert( ! skyyrose2_validate_product_card_media_contract( $stale_sku, $product_registry ), 'Stale per-SKU product hash must fail closed.' );

$missing_integrity = $product_media;
unset( $missing_integrity['asset_integrity']['br-006'] );
skyyrose2_registry_assert( ! skyyrose2_validate_product_card_media_contract( $missing_integrity, $product_registry ), 'Approved media without asset integrity must fail closed.' );

$wrong_opening_role = $product_media;
$wrong_opening_role['products']['br-006']['views'][0]['role'] = 'packshot';
skyyrose2_registry_assert( ! skyyrose2_validate_product_card_media_contract( $wrong_opening_role, $product_registry ), 'A product card that does not open on-model must fail closed.' );

echo "Marketplace registry structure passed.\n";
