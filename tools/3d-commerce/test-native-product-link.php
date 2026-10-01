<?php
/**
 * Actual local Woo getters + exact owner module, synthetic fixture products only.
 *
 * @package SkyyRoseFlagship2
 */

if ( ! defined( 'WP_CLI' ) || ! WP_CLI || 'http://127.0.0.1:18362' !== get_option( 'home' ) || '11.1.2' !== WC_VERSION ) {
	throw new RuntimeException( 'Only the isolated loopback WooCommerce 11.1.2 fixture is permitted.' );
}
$owner = getenv( 'SKYYROSE3D_OWNER_MODULE' );
if ( ! $owner || '98fb6726e5704a5ac741d9b20b2bc38bb1578633998cacbe2ecac79d7ed778a1' !== hash_file( 'sha256', $owner ) ) {
	throw new RuntimeException( 'Exact f16f179 owner module required.' );
}
require_once $owner;
if ( ! function_exists( 'skyyrose2_glb_native_product_link' ) ) {
	require_once __DIR__ . '/native-product-link.php';
}
add_filter( 'action_scheduler_allow_async_request_runner', '__return_false' );
add_filter(
	'pre_http_request',
	static function () {
		throw new RuntimeException( 'Network prohibited in local test.' );
	}
);
$GLOBALS['viewer_assert_count'] = 0;
// SQLite fixture limitation: isolate display-only taxonomy count-cache writes during
// synthetic publication transitions. Native stock/product/category getters remain active.
remove_filter( 'get_terms', 'wc_change_term_counts', 10 );
function skyyrose2_viewer_expect( $condition, $message ) {

	if ( ! $condition ) {
		throw new RuntimeException( esc_html( 'FAIL: ' . $message ) ); }
	++$GLOBALS['viewer_assert_count'];
	echo esc_html( 'PASS: ' . $message ) . "\n";
}
function skyyrose2_viewer_reject( $callback, $message ) {
	try {
		$callback();
	} catch ( Exception $error ) {
		skyyrose2_viewer_expect( true, $message );
		return; }
	throw new RuntimeException( esc_html( 'FAIL: accepted ' . $message ) );
}
$suffix = strtolower( uniqid() );
$term   = wp_insert_term( 'Viewer fixture ' . $suffix, 'product_cat', array( 'slug' => 'viewer-fixture-' . $suffix ) );
if ( is_wp_error( $term ) ) {
	throw new RuntimeException( esc_html( $term->get_error_message() ) ); }
$collection = 'viewer-fixture-' . $suffix;
$sku        = 'viewer-simple-' . $suffix;
$parent     = new WC_Product_Simple();
$parent->set_name( 'Synthetic viewer fixture' );
$parent->set_sku( $sku );
$parent->set_status( 'publish' );
$parent->set_regular_price( '80' );
$parent->set_category_ids( array( $term['term_id'] ) );
$parent->save();
$catalog = array( $sku => array( 'collection' => $collection ) );
$hash    = str_repeat( 'a', 64 );
$link    = skyyrose2_glb_native_product_link( $parent->get_id(), 0, array(), $sku, $catalog, $hash );
skyyrose2_viewer_expect( $link['sku'] === $sku && $link['url'] === $parent->get_permalink() && $link['available'], 'simple native identity and permalink' );
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( 9999999, 0, array(), $sku, $catalog, $hash ), 'unknown native ID' );
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $parent->get_id(), 0, array(), 'unknown', $catalog, $hash ), 'unknown canonical SKU' );
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $parent->get_id(), 0, array(), $sku, $catalog, 'short' ), 'non-full registry digest' );
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $parent->get_id(), 0, array(), $sku, array( $sku => array( 'collection' => 'wrong' ) ), $hash ), 'wrong collection' );
$parent->set_status( 'draft' );
$parent->save();
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $parent->get_id(), 0, array(), $sku, $catalog, $hash ), 'unpublished parent' );
$parent->set_status( 'publish' );
$parent->set_stock_status( 'outofstock' );
$parent->save();
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $parent->get_id(), 0, array(), $sku, $catalog, $hash ), 'sold-out native stock' );
$parent->set_stock_status( 'instock' );
$parent->update_meta_data( '_is_preorder', '1' );
$parent->update_meta_data( '_preorder_available', '0' );
$parent->save();
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $parent->get_id(), 0, array(), $sku, $catalog, $hash ), 'zero preorder availability' );
$parent->update_meta_data( '_preorder_available', '3' );
$parent->save();
$promise = skyyrose2_preorder_snapshot( skyyrose2_preorder_config( $parent->get_id() ) );
$parent->update_meta_data( '_preorder_ship_date', '2027-01-15' );
$parent->save();
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $parent->get_id(), 0, array(), $sku, $catalog, $hash, $promise ), 'stale owner promise' );
$variable = new WC_Product_Variable();
$variable->set_name( 'Synthetic variable viewer fixture' );
$variable->set_sku( 'viewer-variable-' . $suffix );
$variable->set_status( 'publish' );
$variable->set_category_ids( array( $term['term_id'] ) );
$attribute = new WC_Product_Attribute();
$attribute->set_name( 'size' );
$attribute->set_options( array( 'small', 'large' ) );
$attribute->set_variation( true );
$variable->set_attributes( array( $attribute ) );
$variable->save();
$variation = new WC_Product_Variation();
$variation->set_parent_id( $variable->get_id() );
$variation->set_status( 'publish' );
$variation->set_regular_price( '90' );
$variation->set_sku( 'viewer-variation-' . $suffix );
$variation->set_attributes( array( 'size' => 'small' ) );
$variation->save();
$wildcard = new WC_Product_Variation();
$wildcard->set_parent_id( $variable->get_id() );
$wildcard->set_status( 'publish' );
$wildcard->set_regular_price( '90' );
$wildcard->set_sku( 'viewer-wildcard-' . $suffix );
$wildcard->set_attributes( array( 'size' => '' ) );
$wildcard->save();
$variable_sku             = $variable->get_sku();
$catalog[ $variable_sku ] = array( 'collection' => $collection );
$small                    = array( 'attribute_size' => 'small' );
$link                     = skyyrose2_glb_native_product_link( $variable->get_id(), $variation->get_id(), $small, $variable_sku, $catalog, $hash );
skyyrose2_viewer_expect( $link['native_sku'] === $variation->get_sku() && $link['variation_id'] === $variation->get_id() && $link['attributes'] === $small && $link['url'] === $variation->get_permalink(), 'exact selected variation and native selected URL' );
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $parent->get_id(), $variation->get_id(), $small, $sku, $catalog, $hash ), 'foreign-parent variation' );
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $variable->get_id(), 0, array(), $variable_sku, $catalog, $hash ), 'variable product without selection' );
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $variable->get_id(), $variation->get_id(), array(), $variable_sku, $catalog, $hash ), 'missing variation attribute' );
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $variable->get_id(), $variation->get_id(), array( 'attribute_size' => 'large' ), $variable_sku, $catalog, $hash ), 'wrong exact variation attribute' );
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $variable->get_id(), $wildcard->get_id(), array( 'attribute_size' => 'invented' ), $variable_sku, $catalog, $hash ), 'invalid wildcard choice' );
$large = array( 'attribute_size' => 'large' );
$link  = skyyrose2_glb_native_product_link( $variable->get_id(), $wildcard->get_id(), $large, $variable_sku, $catalog, $hash );
skyyrose2_viewer_expect( $link['attributes'] === $large && $link['variation_id'] === $wildcard->get_id(), 'valid native wildcard choice' );
skyyrose2_viewer_expect( $link['url'] === $wildcard->get_permalink( array( 'variation' => $large ) ) && str_contains( $link['url'], 'attribute_size=large' ), 'wildcard selection persists in native product URL' );
$variation->set_status( 'private' );
$variation->save();
skyyrose2_viewer_reject( static fn() => skyyrose2_glb_native_product_link( $variable->get_id(), $variation->get_id(), $small, $variable_sku, $catalog, $hash ), 'inactive variation' );
echo 'PASS ' . (int) $GLOBALS['viewer_assert_count'] . " assertions; synthetic products only, no cart/order/payment calls.\n";
