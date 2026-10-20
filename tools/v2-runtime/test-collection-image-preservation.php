<?php
/** Execute the real composition: adult merchandise stays, atmosphere chapters do not. */
define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_DIR', __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2' );
class WC_Product { public function is_visible() { return true; } }
function __( $value ) { return $value; }
function esc_html( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $value ) { return esc_html( $value ); }
function esc_url( $value ) { return esc_html( $value ); }
function esc_html_e( $value ) { echo esc_html( $value ); }
function add_query_arg( $key, $value, $url ) { return $url . '?' . $key . '=' . $value; }
function skyyrose2_shop_url() { return '/shop/'; }
function skyyrose2_get_products() { return array( new WC_Product() ); }
function skyyrose2_collection_presentation() { return array( 'composition' => 'fixture', 'next_slug' => 'signature', 'focal' => '50% 50%', 'focal_mobile' => '50% 50%', 'arrival_alt' => 'Fixture arrival', 'ordinal' => '01' ); }
function skyyrose2_collection_commerce_scenes( $slug ) { return 'kids-capsule' === $slug ? array() : array( array( 'fixture' => true ) ); }
function skyyrose2_collection_hero_motion() { return array(); }
function skyyrose2_collection_cinema() { return array(); }
// Explicit illustrative media denial for this composition-only fixture. Real
// role admission and pixels are checked by the separate imagery/Kids suites.
function skyyrose2_collection_media( $slug, $role ) {
	if ( 'kids-capsule' !== $slug || 'collection_hero' !== $role ) { throw new Exception( 'Unexpected media binding requested by composition fixture' ); }
	$GLOBALS['denied_media'][] = array( $slug, $role ); return array();
}
function skyyrose2_collection_media_markup() { return ''; }
function skyyrose2_sot_asset_uri( $path ) { return '/theme/assets/sot/' . $path; }
function get_template_part( $path, $name = null, $args = array() ) {
	$GLOBALS['called'][] = $path;
	if ( in_array( $path, array( 'template-parts/collections/arrival', 'template-parts/collections/arrival-product' ), true ) ) { include SKYYROSE2_DIR . '/' . $path . '.php'; }
	if ( str_ends_with( $path, '/editorial' ) ) { echo '<section id="world" data-merchandise-editorial></section>'; }
	if ( str_ends_with( $path, '/chapters' ) ) { echo '<section id="world" data-atmosphere-chapters></section>'; }
	if ( str_ends_with( $path, '/scroll-world' ) && 'kids-capsule' !== $args['slug'] ) { echo '<section data-shopping-scenes></section>'; }
}
$functions = file_get_contents( SKYYROSE2_DIR . '/functions.php' );
$start = strpos( $functions, 'function skyyrose2_collections()' );
$end = strpos( $functions, '/**', $start );
if ( false === $start || false === $end ) { throw new Exception( 'Missing canonical collection definitions' ); }
eval( substr( $functions, $start, $end - $start ) );
foreach ( skyyrose2_collections() as $slug => $collection ) {
	$GLOBALS['called'] = array();
	$GLOBALS['denied_media'] = array();
	$args = array( 'slug' => $slug, 'collection' => $collection, 'collections' => skyyrose2_collections() );
	ob_start();
	include SKYYROSE2_DIR . '/template-parts/collections/world.php';
	$html = ob_get_clean();
	$adult = in_array( $slug, array( 'signature', 'black-rose', 'love-hurts' ), true );
	if ( ( $adult ? 1 : 0 ) !== substr_count( $html, 'id="world"' ) || 1 !== substr_count( $html, 'id="shop"' ) || ! in_array( 'template-parts/collections/product-edit', $GLOBALS['called'], true ) ) { throw new Exception( 'Merchandise/anchors lost: ' . $slug ); }
	if ( str_contains( $html, 'data-atmosphere-chapters' ) ) { throw new Exception( 'Non-product chapters rendered: ' . $slug ); }
	if ( $adult && ( ! str_contains( $html, 'data-shopping-scenes' ) || ! str_contains( $html, 'data-merchandise-editorial' ) || ! str_contains( $html, 'href="#world">Explore the pieces' ) ) ) { throw new Exception( 'Adult non-product chapters rendered: ' . $slug ); }
	if ( ! $adult && ( str_contains( $html, 'data-shopping-scenes' ) || str_contains( $html, 'data-merchandise-editorial' ) || ! str_contains( $html, 'href="#shop">Explore the pieces' ) ) ) { throw new Exception( 'Kids composition unexpectedly changed' ); }
	if ( ! $adult && ( array( array( 'kids-capsule', 'collection_hero' ) ) !== $GLOBALS['denied_media'] || ! in_array( 'template-parts/collections/arrival-product', $GLOBALS['called'], true ) || ! str_contains( $html, 'data-product-arrival' ) || ! str_contains( $html, 'data-media-state="unavailable"' ) || ! str_contains( $html, esc_html( $collection['name'] ) . '</h1>' ) ) ) { throw new Exception( 'Kids product arrival/title/denied-media fallback lost' ); }
	// Assets remain available as background inspiration; removing rendering never deletes them.
	foreach ( $collection['world'] as $scene ) {
		$file = SKYYROSE2_DIR . '/assets/' . ( 'scroll-world' === ( $scene['source'] ?? '' ) ? 'scroll-world/' : 'sot/' ) . $scene['image'];
		if ( ! getimagesize( $file ) ) { throw new Exception( 'Original source inspiration asset lost: ' . $slug ); }
	}
}
$editorial = file_get_contents( SKYYROSE2_DIR . '/template-parts/collections/editorial.php' );
if ( 1 !== substr_count( $editorial, 'id="world"' ) || ! str_contains( $editorial, 'skyyrose2_immersive_url( $editorial_slug )' ) ) { throw new Exception( 'Merchandise editorial anchor/immersive link lost' ); }
// Source-consumer boundary: the shared exact-SKU resolver is exercised by the
// all-SKU contract fixture. These surfaces must not reopen assigned Woo imagery.
foreach ( array( 'template-parts/home/kids-capsule-reveal.php', 'template-parts/immersive/world.php' ) as $relative ) {
	$consumer = file_get_contents( SKYYROSE2_DIR . '/' . $relative );
	if ( ! str_contains( $consumer, 'skyyrose2_approved_card_front( $product )' ) ) { throw new Exception( 'Exact-SKU product media consumer lost: ' . $relative ); }
	$consumer_tokens = token_get_all( $consumer );
	foreach ( $consumer_tokens as $token ) {
		if ( is_array( $token ) && T_STRING === $token[0] && in_array( strtolower( $token[1] ), array( 'get_image_id', 'wp_get_attachment_image', 'wp_get_attachment_image_url', 'wp_get_attachment_url' ), true ) ) { throw new Exception( 'Assigned-media fallback reopened: ' . $relative ); }
	}
}
echo "PASS actual four collection compositions: zero atmosphere chapters; adult editorial/shopping/edit preserved; Kids shop anchor/no invented editorial or rail; source assets retained\n";
echo "PASS Kids and immersive source consumers: exact-SKU approved fronts, zero assigned-media fallback\n";
echo "Scope: composition-only explicit illustrative media denial; governed admission and pixels remain separately qualified.\n";
