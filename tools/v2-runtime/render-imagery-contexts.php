<?php
/** Real V2 imagery consumers with registry-derived, offline commerce fixtures. */
ob_start();
require __DIR__ . '/render-all33-cards.php';
$all_cards = ob_get_clean();
define( 'SKYYROSE2_VERSION', '2.5.0' );
function esc_attr_e( $value ) { echo esc_attr( $value ); }
function esc_html__( $value ) { return esc_html( $value ); }
function sanitize_key( $value ) { return preg_replace( '/[^a-z0-9_-]/', '', strtolower( $value ) ); }
function sanitize_html_class( $value ) { return sanitize_key( $value ); }
function sanitize_text_field( $value ) { return strip_tags( $value ); }
function wp_generate_uuid4() { return '00000000-0000-4000-8000-000000000001'; }
function wp_json_encode( $value, $flags = 0 ) { return json_encode( $value, $flags ); }
function wp_enqueue_style( ...$args ) {} function wp_enqueue_script( ...$args ) {}
function get_header() {} function get_footer() {}
function skyyrose2_collection_commerce_scenes() { return array(); }
function skyyrose2_collection_url( $slug ) { return '/collections/' . $slug . '/'; }
function skyyrose2_immersive_url( $slug ) { return '/experience/' . $slug . '/'; }
function skyyrose2_shop_url() { return '/shop/'; }
function add_query_arg( $key, $value, $url ) { return $url . '?' . rawurlencode( $key ) . '=' . rawurlencode( $value ); }
function skyyrose2_presentation_registry() { return $GLOBALS['fixture_presentation']; }
function skyyrose2_sot_asset_uri( $path ) { return skyyrose2_media_uri( 'assets/sot/' . $path ); }
function wc_get_product_id_by_sku( $sku ) { return $GLOBALS['imagery_ids'][ $sku ] ?? 0; }
function wc_get_product( $id ) { return $GLOBALS['imagery_products'][ $id ] ?? null; }
function get_permalink( $id ) { return wc_get_product( $id )?->get_permalink() ?? ''; }
class ImageryFixtureProduct extends WC_Product {
	public function get_status() { return 'publish'; }
	public function get_id() { return $GLOBALS['imagery_ids'][ $this->sku ]; }
}
$products = array();
foreach ( $GLOBALS['fixture_presentation']['products'] as $sku => $record ) {
	$id = count( $products ) + 1;
	$GLOBALS['imagery_ids'][ $sku ] = $id;
	$products[ $sku ] = new ImageryFixtureProduct( $sku, $registry['products'][ $sku ]['catalog'] );
	$GLOBALS['imagery_products'][ $id ] = $products[ $sku ];
}
$imagery_all_products = $products;
// Read the actual collection copy factory; this fixture owns no marketing copy.
$collection_source = file_get_contents( SKYYROSE2_DIR . '/functions.php' );
$collection_start = strpos( $collection_source, 'function skyyrose2_collections()' );
$collection_end = strpos( $collection_source, '/**', $collection_start );
eval( str_replace( 'function skyyrose2_collections()', 'function imagery_native_collections()', substr( $collection_source, $collection_start, $collection_end - $collection_start ) ) );
$GLOBALS['fixture_collections'] = imagery_native_collections();
$standard = array_filter( $products, static fn( $product ) => ! skyyrose2_is_transaction_preorder_product( $product ) );
require SKYYROSE2_DIR . '/inc/pdp-media-delivery.php';
ob_start();
echo '<section id="imagery-contexts"><h2>Image delivery contexts · offline verification</h2><p>Real templates and source gates. Commerce adapters are offline; withheld scene roles remain withheld.</p>';
$args = array( 'products' => $standard );
include SKYYROSE2_DIR . '/template-parts/home/editorial-film.php';
foreach ( array( 'black-rose', 'love-hurts', 'signature' ) as $slug ) {
	$args = array( 'slug' => $slug, 'collection' => $GLOBALS['fixture_collections'][ $slug ], 'products' => array_values( $standard ) );
	include SKYYROSE2_DIR . '/template-parts/collections/editorial.php';
}
$args = array( 'collection' => $GLOBALS['fixture_collections']['kids-capsule'], 'products' => $standard );
include SKYYROSE2_DIR . '/template-parts/home/kids-capsule-reveal.php';
$args = array( 'collection_slug' => 'love-hurts', 'collection_name' => $GLOBALS['fixture_collections']['love-hurts']['name'], 'world_name' => 'Offline image delivery fixture', 'world_type' => 'love-hurts', 'poster' => 'images/immersive/scene-love-hurts-chapter1.webp', 'chapters' => array( array( 'id' => 'fixture', 'label' => 'Product hotspot', 'hotspots' => array( array( 'sku' => 'lh-004' ) ) ) ) );
include SKYYROSE2_DIR . '/template-parts/immersive/world.php';
echo '<div class="product imagery-pdp" id="imagery-pdp">';
$front = skyyrose2_approved_pdp_front( $imagery_all_products['lh-004'] );
echo skyyrose2_pdp_v2_gallery_markup( $front );
echo '</div><div id="imagery-thumbnails">';
foreach ( array( 'lh-004', 'kids-002', 'sg-015' ) as $sku ) {
	echo skyyrose2_product_v2_thumbnail( '', $imagery_all_products[ $sku ] );
}
echo '</div></section>';
$contexts = skyyrose2_media_filter_html( ob_get_clean() );
$styles = '<link rel="stylesheet" href="' . SKYYROSE2_URI . '/assets/css/home-page.css"><link rel="stylesheet" href="' . SKYYROSE2_URI . '/assets/css/collection-world.css"><link rel="stylesheet" href="' . SKYYROSE2_URI . '/assets/css/immersive.css"><style>#imagery-contexts{overflow:hidden}#imagery-thumbnails img{width:96px;height:auto}.imagery-pdp{height:clamp(28rem,64svh,44rem)}.imagery-pdp .woocommerce-product-gallery,.imagery-pdp .woocommerce-product-gallery__wrapper,.imagery-pdp .woocommerce-product-gallery__image,.imagery-pdp a{display:block;height:100%}.imagery-pdp img{width:100%;height:100%;object-fit:contain}@media(max-width:767px){.imagery-pdp{height:clamp(20rem,52svh,30rem)}}</style>';
echo str_replace( '</head>', $styles . '</head>', str_replace( '</main></body>', $contexts . '</main></body>', $all_cards ) );
