<?php
/** Focused approved-front resolver test; does not require a WordPress fixture. */
define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_DIR', realpath( __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2' ) );
define( 'SKYYROSE2_URI', 'https://theme.invalid' );

class WC_Product {
	public function __construct( public string $sku, public int $image_id ) {}
	public function get_sku() { return $this->sku; }
	public function get_image_id() { return $this->image_id; }
}

function sanitize_key( $value ) { return strtolower( preg_replace( '/[^a-z0-9_\\-]/', '', (string) $value ) ); }
function wp_get_attachment_url( $id ) { return $GLOBALS['test_attachment_urls'][ $id ] ?? false; }
function esc_url( $value ) { return htmlspecialchars( $value, ENT_QUOTES ); }
function esc_attr( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES ); }
function esc_html__( $value, $domain = '' ) { return htmlspecialchars( $value, ENT_QUOTES ); }
function add_filter( ...$args ) {}
function add_action( ...$args ) {}

require SKYYROSE2_DIR . '/inc/approved-card-fronts.php';
require SKYYROSE2_DIR . '/inc/pdp-media-delivery.php';
require SKYYROSE2_DIR . '/inc/launch-readiness.php';

function check_approved_front( $condition, $message ) {
	if ( ! $condition ) {
		throw new RuntimeException( $message );
	}
}

$manifest = json_decode( file_get_contents( SKYYROSE2_DIR . '/data/approved-card-fronts.json' ), true, 512, JSON_THROW_ON_ERROR );
check_approved_front( 33 === count( $manifest['products'] ?? array() ), 'Expected 33 approved product fronts.' );
foreach ( $manifest['products'] as $sku => $record ) {
	$id = 1000 + count( $GLOBALS['test_attachment_urls'] ?? array() );
	$product = new WC_Product( $sku, $id );
	$front = skyyrose2_approved_card_front( $product );
	check_approved_front( 'FOUNDER_APPROVED_V2_CARD' === ( $front['scene_status'] ?? '' ), 'Approval status missing for ' . $sku . '.' );
	check_approved_front( ( $record['sha256'] ?? '' ) === ( $front['sha256'] ?? '' ), 'Front source hash mismatch for ' . $sku . '.' );
	check_approved_front( SKYYROSE2_URI . '/' . $record['src'] === ( $front['src'] ?? '' ), 'Resolver must retain the absolute approved original URL for ' . $sku . '.' );
	check_approved_front( str_ends_with( strtolower( $front['alt'] ?? '' ), 'front on model' ), 'Front alt text does not identify the model-front view for ' . $sku . '.' );
}
$rendition_manifest = json_decode( file_get_contents( SKYYROSE2_DIR . '/assets/derived/card-fronts/manifest.json' ), true, 512, JSON_THROW_ON_ERROR );
$integrity_product = new WC_Product( 'br-001', 9001 );
$integrity_front = skyyrose2_approved_card_front( $integrity_product );
$tampered_delivery = $rendition_manifest['products']['br-001'];
foreach ( $tampered_delivery['renditions'] as &$candidate ) {
	if ( 480 === (int) $candidate['width'] ) {
		$candidate['sha256'] = str_repeat( '0', 64 );
	}
}
unset( $candidate );
$integrity_source = $integrity_front;
unset( $integrity_source['card_src'], $integrity_source['card_width'], $integrity_source['card_height'], $integrity_source['srcset'], $integrity_source['sizes'] );
$filtered_delivery = skyyrose2_approved_card_front_renditions( 'br-001', $integrity_source, $tampered_delivery, $integrity_front['src'] );
$integrity_fallback_src = $filtered_delivery['card_src'] ?? $integrity_front['src'];
check_approved_front( $integrity_fallback_src === $integrity_front['src'] && ! isset( $filtered_delivery['card_src'] ), 'A wrong-hash 480w file must never become the displayed fallback source.' );
check_approved_front( ! str_contains( $filtered_delivery['srcset'] ?? '', 'br-001-480w.webp' ) && str_contains( $filtered_delivery['srcset'] ?? '', 'https://theme.invalid/assets/derived/card-fronts/br-001-320w.webp 320w' ) && str_contains( $filtered_delivery['srcset'] ?? '', 'https://theme.invalid/assets/derived/card-fronts/br-001-768w.webp 768w' ) && str_contains( $filtered_delivery['srcset'] ?? '', $integrity_front['src'] . ' 1024w' ), 'A wrong-hash rendition must be excluded while valid absolute sizes and the absolute original remain available.' );
$expected = array( 'br-002', 'br-005', 'kids-002', 'lh-003', 'sg-014' );
$ghost_failures = array();
foreach ( $expected as $sku ) {
	$id = 2000 + count( $ghost_failures );
	$GLOBALS['test_attachment_urls'][ $id ] = 'https://uploads.invalid/' . $sku . '-ghost-front.webp';
	$product = new WC_Product( $sku, $id );
	$front = skyyrose2_approved_card_front( $product );
	$html = skyyrose2_pdp_approved_ghost_front_html( '<div>original ghost</div>', $id, $product );
	check_approved_front( str_contains( $html, $front['src'] ) && str_contains( $html, esc_attr( $front['alt'] ) ) && ! str_contains( $html, 'original ghost' ), 'Ghost primary was not replaced for ' . $sku . '.' );
	$expected_sizes = skyyrose2_pdp_gallery_sizes( $front['width'], $front['height'] );
	check_approved_front( str_contains( $html, 'data-large_image="' . $front['src'] . '"' ) && str_contains( $html, 'sizes="' . $expected_sizes . '"' ), 'PDP full-view or contained-gallery responsive sizing missing for ' . $sku . '.' );
	$variation_image = skyyrose2_pdp_approved_ghost_front_variation_image( array( 'src' => 'ghost-small', 'full_src' => 'ghost-full', 'alt' => 'ghost alt' ), $id, $product );
	check_approved_front( ( $front['card_src'] ?? $front['src'] ) === $variation_image['src'] && $front['src'] === $variation_image['full_src'] && $front['alt'] === $variation_image['alt'] && $expected_sizes === $variation_image['sizes'], 'Variation image data must retain the approved model front and PDP slot size for ' . $sku . '.' );
	$ghost_failures[] = $sku;
}
sort( $ghost_failures );
sort( $expected );
check_approved_front( $ghost_failures === $expected, 'The exact five PDP ghost-primary products must be covered.' );
$fallback_products = array( 'br-001', 'br-003', 'br-004', 'br-007', 'br-011' );
foreach ( $fallback_products as $sku ) {
	$product = new WC_Product( $sku, 3000 + count( $fallback_products ) );
	$front = skyyrose2_approved_card_front( $product );
	ob_start();
	$result = skyyrose2_render_approved_pdp_styling_view( $product );
	$html = ob_get_clean();
	$expected_sizes = skyyrose2_pdp_gallery_sizes( $front['width'], $front['height'] );
	check_approved_front( $result && str_contains( $html, 'src="' . $front['card_src'] . '"' ) && str_contains( $html, 'width="' . $front['card_width'] . '" height="' . $front['card_height'] . '"' ), 'Fallback styling view must start at its validated responsive rendition for ' . $sku . '.' );
	check_approved_front( str_contains( $html, 'srcset="' . esc_attr( $front['srcset'] ) . '"' ) && str_contains( $html, 'sizes="' . esc_attr( $expected_sizes ) . '"' ) && str_contains( $front['srcset'], $front['src'] . ' ' . $front['width'] . 'w' ), 'Fallback must expose verified same-source responsive derivatives and retain the full approved original for ' . $sku . '.' );
	check_approved_front( str_contains( $html, 'fetchpriority="high"' ) && str_contains( $html, esc_attr( $front['alt'] ) ) && ! str_contains( $html, 'data-large_image=' ), 'Fallback keeps its existing above-fold display and does not invent gallery/lightbox semantics for ' . $sku . '.' );
}
$original_only_front = skyyrose2_approved_card_front( new WC_Product( 'br-002', 9100 ) );
unset( $original_only_front['card_src'], $original_only_front['card_width'], $original_only_front['card_height'], $original_only_front['srcset'], $original_only_front['sizes'] );
$original_only_front['pdp_src'] = $original_only_front['src'];
$original_only_front['pdp_width'] = $original_only_front['width'];
$original_only_front['pdp_height'] = $original_only_front['height'];
$original_only_front['pdp_sizes'] = skyyrose2_pdp_gallery_sizes( $original_only_front['width'], $original_only_front['height'] );
$original_only_gallery = skyyrose2_pdp_approved_ghost_front_markup( $original_only_front );
check_approved_front( str_contains( $original_only_gallery, 'src="' . $original_only_front['src'] . '"' ) && str_contains( $original_only_gallery, 'data-large_image="' . $original_only_front['src'] . '"' ) && ! str_contains( $original_only_gallery, 'srcset=' ), 'PDP ghost replacement must remain usable at the approved original when every derivative is unavailable.' );
$variation_original_only = skyyrose2_pdp_variation_image_from_approved_front( array( 'src' => 'ghost-small', 'srcset' => 'ghost-320w.webp 320w', 'sizes' => 'ghost-slot', 'full_src' => 'ghost-full', 'gallery_thumbnail_src' => 'ghost-thumb' ), $original_only_front );
check_approved_front( $variation_original_only['src'] === $original_only_front['src'] && $variation_original_only['full_src'] === $original_only_front['src'] && '' === $variation_original_only['srcset'] && '' === $variation_original_only['sizes'], 'Original-only variation data must clear stale ghost srcset/sizes with explicit empty strings.' );
ob_start();
$original_only_rendered = skyyrose2_render_approved_pdp_styling_front( 'br-002', $original_only_front );
$original_only_styling = ob_get_clean();
check_approved_front( $original_only_rendered && str_contains( $original_only_styling, 'src="' . $original_only_front['src'] . '"' ) && ! str_contains( $original_only_styling, 'srcset=' ), 'Styling fallback must remain usable at the approved original when every derivative is unavailable.' );
$wrong_product = new WC_Product( 'br-005', 2000 );
$GLOBALS['test_attachment_urls'][2000] = 'https://uploads.invalid/br-002-ghost-front.webp';
check_approved_front( '<div>original ghost</div>' === skyyrose2_pdp_approved_ghost_front_html( '<div>original ghost</div>', 2000, $wrong_product ), 'A different SKU ghost must never be relabeled.' );
$non_ghost = new WC_Product( 'br-002', 2001 );
$GLOBALS['test_attachment_urls'][2001] = 'https://uploads.invalid/br-002-onmodel.webp';
check_approved_front( '<div>existing view</div>' === skyyrose2_pdp_approved_ghost_front_html( '<div>existing view</div>', 2001, $non_ghost ), 'A non-ghost native view must remain unchanged.' );
echo "PASS: 33 approved fronts hash-verified; exact five ghost primaries replaced; five approved PDP fallbacks use same-source responsive derivatives; mismatched SKUs and model views preserved.\n";
