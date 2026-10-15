<?php
/** Real V2 media/templates; offline adapters do not verify live commerce. */
ob_start();
require __DIR__ . '/render-all33-cards.php';
ob_end_clean();
function skyyrose2_presentation_registry() { return $GLOBALS['fixture_presentation']; }
function esc_attr_e( $text ) { echo esc_attr( $text ); }
function esc_html__( $text ) { return esc_html( $text ); }
function sanitize_key( $text ) { return preg_replace( '/[^a-z0-9_-]/', '', strtolower( $text ) ); }
function sanitize_html_class( $text ) { return sanitize_key( $text ); }
function sanitize_text_field( $text ) { return strip_tags( $text ); }
function wp_json_encode( $value, $flags = 0 ) { return json_encode( $value, $flags ); }
function wp_generate_uuid4() { return '00000000-0000-4000-8000-000000000001'; }
function get_template_part( $template, $name = null, $args = array() ) { include SKYYROSE2_DIR . '/' . $template . '.php'; }
function skyyrose2_collection_url( $slug ) { return '/collections/' . $slug . '/'; }
function skyyrose2_immersive_url( $slug ) { return '/experience/' . $slug . '/'; }
function skyyrose2_shop_url() { return '/shop/'; }
function add_query_arg( $key, $value, $url ) { return $url . '?' . rawurlencode( $key ) . '=' . rawurlencode( $value ); }
function skyyrose2_get_products( $limit = -1, $collection = '' ) {
	return array_values( array_filter( $GLOBALS['placement_products'], static fn( $p ) => 'pre-order' === $collection ? skyyrose2_is_transaction_preorder_product( $p ) : ! skyyrose2_is_transaction_preorder_product( $p ) && ( ! $collection || $GLOBALS['fixture_presentation']['products'][ $p->sku ]['collection'] === $collection ) ) );
}
$source = file_get_contents( SKYYROSE2_DIR . '/functions.php' );
$start = strpos( $source, 'function skyyrose2_collections()' );
$end = strpos( $source, '/**', $start );
eval( str_replace( 'function skyyrose2_collections()', 'function placement_native_collections()', substr( $source, $start, $end - $start ) ) );
$GLOBALS['fixture_collections'] = placement_native_collections();
$GLOBALS['placement_products'] = array();
foreach ( $registry['products'] as $sku => $item ) { $GLOBALS['placement_products'][ $sku ] = new WC_Product( $sku, $item['catalog'] ); }
require SKYYROSE2_DIR . '/inc/collection-presentation.php';
require SKYYROSE2_DIR . '/inc/pdp-media-delivery.php';
$route = $argv[1] ?? 'love-hurts';
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V2 placement review · <?php echo esc_html( $route ); ?></title>
<?php foreach ( array( 'design-tokens', 'controls', 'theme', 'collection-world', 'home-page', 'content-page', 'product-page', 'premium-commerce' ) as $sheet ) : ?><link rel="stylesheet" href="/wordpress-theme/skyyrose-flagship-2/assets/css/<?php echo esc_attr( $sheet ); ?>.css"><?php endforeach; ?>
<style>body{margin:0;background:#0a0a0a;color:#f4f0ea}.placement-header{height:72px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;border-bottom:1px solid #302a26}.placement-header strong{font-size:20px;letter-spacing:.2em}.placement-header span{font-size:11px;letter-spacing:.08em}.placement-pdp{display:grid;grid-template-columns:1fr 1fr;gap:48px;padding:40px 32px;align-items:center;border-top:1px solid #39322c}.placement-pdp .product{height:740px;min-width:0}.placement-pdp .woocommerce-product-gallery,.placement-pdp .woocommerce-product-gallery__wrapper,.placement-pdp .woocommerce-product-gallery__image,.placement-pdp .woocommerce-product-gallery a{display:block;height:100%}.placement-pdp img{display:block;width:100%;height:100%;object-fit:contain}.placement-pdp h2{font:500 clamp(2rem,4vw,4rem)/1.1 var(--sr2-font-display)}.placement-pdp p{font:400 16px/1.6 var(--sr2-font-body)}@media(max-width:767px){.placement-pdp{grid-template-columns:1fr;padding:24px 16px;gap:16px}.placement-pdp .product{height:540px}.placement-pdp h2{font-size:2rem}.placement-header span{max-width:45%;text-align:right}}</style>
</head><body><header class="placement-header"><strong>SKYYROSE</strong><span>V2 · offline placement review</span></header>
<?php
ob_start();
if ( 'pre-order' === $route ) {
	include SKYYROSE2_DIR . '/template-parts/v2-preorder.php';
} elseif ( 'pdp' === $route ) {
	foreach ( $GLOBALS['placement_products'] as $sku => $product ) {
		echo '<section class="placement-pdp" data-pdp-sku="' . esc_attr( $sku ) . '"><div class="product">';
		echo skyyrose2_pdp_v2_gallery_markup( skyyrose2_approved_pdp_front( $product ) );
		echo '</div><div><p class="sr2-eyebrow">' . esc_html( $GLOBALS['fixture_collections'][ $registry['products'][ $sku ]['catalog']['collection'] ]['name'] ) . '</p><h2>' . esc_html( $product->get_name() ) . '</h2><p>' . esc_html( $registry['products'][ $sku ]['catalog']['description'] ) . '</p></div></section>';
	}
} elseif ( 'index' === $route ) {
	include SKYYROSE2_DIR . '/template-parts/collections/index.php';
} elseif ( 'home' === $route ) {
	$args = array( 'collections' => $GLOBALS['fixture_collections'], 'products' => array() );
	include SKYYROSE2_DIR . '/template-parts/home/editorial-collection.php';
} elseif ( isset( $GLOBALS['fixture_collections'][ $route ] ) ) {
	$args = array( 'slug' => $route, 'collection' => $GLOBALS['fixture_collections'][ $route ], 'presentation' => skyyrose2_collection_presentation( $route ), 'products' => skyyrose2_get_products( -1, $route ) );
	echo '<main class="sr2-collection-world" data-collection="' . esc_attr( $route ) . '">';
	include SKYYROSE2_DIR . '/template-parts/collections/arrival.php';
	if ( 'kids-capsule' !== $route ) { include SKYYROSE2_DIR . '/template-parts/collections/editorial.php'; }
	include SKYYROSE2_DIR . '/template-parts/collections/story.php';
	echo '</main>';
} else { throw new RuntimeException( 'Unknown offline placement route' ); }
echo skyyrose2_media_filter_html( ob_get_clean() );
?></body></html>
