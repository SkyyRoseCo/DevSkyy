<?php
/** Actual V2 bootstrap/resolver; synthetic loopback fixture only, no asset approval. */
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || 'http://127.0.0.1:18362' !== get_option( 'home' ) || '11.1.2' !== WC_VERSION || 'skyyrose-flagship-2' !== get_stylesheet() ) {
	throw new RuntimeException( 'Only the isolated active V2/WooCommerce fixture is permitted.' );
}
function integration_glb_assert( $condition, $label ) {
	if ( ! $condition ) {
		throw new RuntimeException( 'FAIL: ' . $label );
	}
	echo 'PASS: ' . $label . "\n";
}
integration_glb_assert( 35 === has_action( 'woocommerce_single_product_summary', 'skyyrose2_glb_product_view' ), 'real theme mount registered' );
integration_glb_assert( array() === skyyrose2_glb_manifest(), 'no accepted registry bindings remain unavailable' );
$registry = skyyrose2_presentation_registry();
integration_glb_assert( 64 === strlen( $registry['product_registry_sha256'] ), 'server owns full registry digest' );
$server = rest_get_server();
do_action( 'rest_api_init', $server );
integration_glb_assert( isset( $server->get_routes()['/skyyrose/v1/product-view'] ), 'real read-only resolver registered' );
$request = new WP_REST_Request( 'POST', '/skyyrose/v1/product-view' );
$request->set_param( 'sku', 'unknown-fixture-sku' );
integration_glb_assert( 409 === $server->dispatch( $request )->get_status(), 'unknown canonical SKU rejected' );
$request->set_param( 'variation_id', -1 );
integration_glb_assert( 400 === $server->dispatch( $request )->get_status(), 'negative variation rejected at route boundary' );
$sku = 'br-007';
if ( wc_get_product_id_by_sku( $sku ) ) {
	throw new RuntimeException( 'Synthetic fixture requires an unused canonical SKU; no existing product is overwritten.' );
}
$item = new WC_Product_Simple();
$item->set_name( 'SYNTHETIC INTEGRATION TEST ONLY' );
$item->set_sku( $sku );
$item->set_status( 'publish' );
$item->set_regular_price( '12' );
$item->set_virtual( true );
$item->save();
$term = term_exists( 'black-rose', 'product_cat' );
if ( ! $term ) {
	$term = wp_insert_term( 'Black Rose', 'product_cat', array( 'slug' => 'black-rose' ) );
}
wp_set_object_terms( $item->get_id(), (int) $term['term_id'], 'product_cat' );
$request->set_param( 'sku', $sku );
$request->set_param( 'variation_id', 0 );
$request->set_param( 'attributes', array() );
$request->set_param( 'product_id', 999999 );
$response = $server->dispatch( $request );
integration_glb_assert( 200 === $response->get_status() && $item->get_id() === $response->get_data()['product_id'], 'client product ID ignored; native canonical lookup owns identity' );
integration_glb_assert( $registry['product_registry_sha256'] === $response->get_data()['registry_sha256'], 'resolver owns registry identity' );
integration_glb_assert( 'no-store' === $response->get_headers()['Cache-Control'], 'fresh resolver response cannot be cached' );
$GLOBALS['product'] = $item;
ob_start();
skyyrose2_glb_product_view();
$output = ob_get_clean();
integration_glb_assert( '' === $output, 'absent accepted assets render no empty mount or renderer' );
$item->set_stock_status( 'outofstock' );
$item->save();
integration_glb_assert( 409 === $server->dispatch( $request )->get_status(), 'current unavailable native product rejected' );
$item->set_stock_status( 'instock' );
$item->set_status( 'draft' );
$item->save();
integration_glb_assert( 409 === $server->dispatch( $request )->get_status(), 'draft product rejected' );
$item->delete( true );
echo "INTEGRATED GLB BOUNDARY COMPLETE; no accepted assets, orders, or provider calls\n";
