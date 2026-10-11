<?php
/** Offline native-source validator and real shared-card rendering regressions. */
define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_DIR', realpath( __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2' ) );
require SKYYROSE2_DIR . '/inc/card-garment-highlight.php';
function check_highlight( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
$manifest = json_decode( file_get_contents( SKYYROSE2_DIR . '/data/approved-card-fronts.json' ), true );
$entry = $manifest['products']['sg-009'];
$front = array( 'path' => $entry['src'], 'sha256' => $entry['sha256'], 'width' => $entry['width'], 'height' => $entry['height'], 'src' => 'https://example.test/' . $entry['src'], 'alt' => 'Accepted front' );
// Illustrative geometry is exclusively a validator fixture, never approved or published.
$polygon = array( 'outer' => array( array( 100, 100 ), array( 900, 100 ), array( 900, 1000 ), array( 100, 1000 ) ), 'holes' => array( array( array( 300, 300 ), array( 500, 300 ), array( 500, 500 ), array( 300, 500 ) ) ) );
function fixture_annotation( $front, $polygons ) {
	$paths = array_map( static fn( $polygon ) => implode( ' ', array_map( 'skyyrose2_highlight_ring_path', array_merge( array( $polygon['outer'] ), $polygon['holes'] ) ) ), $polygons );
	return array( 'sku' => 'sg-009', 'status' => 'INDEPENDENT_VISUAL_PASS', 'source' => array_intersect_key( $front, array_flip( array( 'path', 'sha256', 'width', 'height' ) ) ), 'review' => array( 'evidence_sha256' => str_repeat( 'a', 64 ), 'geometry_sha256' => hash( 'sha256', implode( "\n", $paths ) ) ), 'polygons' => $polygons );
}
$annotation = fixture_annotation( $front, array( $polygon ) );
$record = array( 'collection' => 'signature', 'garment_highlight' => $annotation );
check_highlight( null !== skyyrose2_card_garment_highlight( $record, $front, 'sg-009' ), 'Valid source-bound outer and hole accepted' );
check_highlight( null === skyyrose2_card_garment_highlight( array(), $front, 'sg-009' ), 'Absent annotation is ordinary commerce' );
check_highlight( null === skyyrose2_card_garment_highlight( $record, $front, 'lh-004' ), 'Wrong SKU rejected' );
foreach ( array( 'status', 'source_hash', 'source_path', 'source_size', 'review_hash', 'geometry_hash' ) as $case ) {
	$bad = $annotation;
	if ( 'status' === $case ) { $bad['status'] = 'PENDING'; }
	if ( 'source_hash' === $case ) { $bad['source']['sha256'] = str_repeat( '0', 64 ); }
	if ( 'source_path' === $case ) { $bad['source']['path'] = 'assets/../private.webp'; }
	if ( 'source_size' === $case ) { $bad['source']['width']++; }
	if ( 'review_hash' === $case ) { $bad['review']['evidence_sha256'] = ''; }
	if ( 'geometry_hash' === $case ) { $bad['review']['geometry_sha256'] = str_repeat( '0', 64 ); }
	check_highlight( null === skyyrose2_card_garment_highlight( array( 'garment_highlight' => $bad ), $front, 'sg-009' ), 'Reject ' . $case );
}
$blocked = $front;
$blocked['current_fidelity_status'] = 'BLOCKED_PRODUCT_MISMATCH';
check_highlight( null === skyyrose2_card_garment_highlight( $record, $blocked, 'sg-009' ), 'Founder mismatch blocks highlight' );
$malformed = array(
	array( array( 1, 1 ), array( 2, 2 ), array( 3, 3 ) ),
	array( array( 1, 1 ), array( 900, 900 ), array( 1, 900 ), array( 900, 1 ) ),
	array( array( -1, 1 ), array( 10, 1 ), array( 10, 10 ) ),
	array( array( 1.0, 1 ), array( 10, 1 ), array( 10, 10 ) ),
	array( array( '1', 1 ), array( 10, 1 ), array( 10, 10 ) ),
	array( array( INF, 1 ), array( 10, 1 ), array( 10, 10 ) ),
	array( array( 1, 1 ), array( 10, 1 ), array( 10, 10 ), array( 1, 1 ) ),
);
foreach ( $malformed as $ring ) {
	check_highlight( ! skyyrose2_highlight_valid_ring( $ring, 1024, 1536 ), 'Malformed ring rejected' );
}
$outside_hole = $polygon;
$outside_hole['holes'] = array( array( array( 0, 0 ), array( 20, 0 ), array( 20, 20 ) ) );
$touching_hole = $polygon;
$touching_hole['holes'] = array( array( array( 100, 100 ), array( 200, 100 ), array( 200, 200 ) ) );
$overlapping_holes = $polygon;
$overlapping_holes['holes'][] = $polygon['holes'][0];
foreach ( array( $outside_hole, $touching_hole, $overlapping_holes ) as $bad_polygon ) {
	check_highlight( null === skyyrose2_card_garment_highlight( array( 'garment_highlight' => fixture_annotation( $front, array( $bad_polygon ) ) ), $front, 'sg-009' ), 'Invalid holes rejected' );
}
check_highlight( null !== skyyrose2_card_garment_highlight( array( 'garment_highlight' => fixture_annotation( $front, array( $polygon, $polygon ) ) ), $front, 'sg-009' ), 'Overlapping outer regions accepted for union' );

// Runtime cap boundaries match the authoring contract exactly.
$boundary_ring = array();
for ( $i = 0; $i < 64; $i++ ) { $boundary_ring[] = array( 100 + 6 * $i, 100 ); }
for ( $i = 0; $i < 64; $i++ ) { $boundary_ring[] = array( 484, 100 + 6 * $i ); }
for ( $i = 0; $i < 64; $i++ ) { $boundary_ring[] = array( 484 - 6 * $i, 484 ); }
for ( $i = 0; $i < 64; $i++ ) { $boundary_ring[] = array( 100, 484 - 6 * $i ); }
$boundary_polygon = array( 'outer' => $boundary_ring, 'holes' => array() );
check_highlight( skyyrose2_highlight_valid_ring( $boundary_ring, 1024, 1536 ), 'Exact 256-point ring accepted' );
$over_ring = $boundary_ring;
array_splice( $over_ring, 1, 0, array( array( 101, 100 ) ) );
check_highlight( ! skyyrose2_highlight_valid_ring( $over_ring, 1024, 1536 ), '257-point ring rejected' );
$triangle = array( 'outer' => array( array( 100, 100 ), array( 900, 100 ), array( 900, 1000 ) ), 'holes' => array() );
foreach ( array( array( 8, $boundary_polygon, true, '2048 points' ), array( 9, $boundary_polygon, false, '2304 points' ), array( 16, $triangle, true, '16 polygons' ), array( 17, $triangle, false, '17 polygons' ) ) as $case ) {
	$result = skyyrose2_card_garment_highlight( array( 'garment_highlight' => fixture_annotation( $front, array_fill( 0, $case[0], $case[1] ) ) ), $front, 'sg-009' );
	check_highlight( ( null !== $result ) === $case[2], 'Cap boundary ' . $case[3] );
}
$hole_polygon = $polygon;
$hole_polygon['holes'] = array();
for ( $i = 0; $i < 17; $i++ ) {
	$x = 200 + ( $i % 5 ) * 100;
	$y = 200 + intdiv( $i, 5 ) * 100;
	$hole_polygon['holes'][] = array( array( $x, $y ), array( $x + 20, $y ), array( $x + 20, $y + 20 ), array( $x, $y + 20 ) );
}
foreach ( array( array( 16, 1, true, '16 holes' ), array( 17, 1, false, '17 holes' ), array( 15, 4, true, '64 rings' ), array( 16, 4, false, '68 rings' ) ) as $case ) {
	$candidate = $hole_polygon;
	$candidate['holes'] = array_slice( $candidate['holes'], 0, $case[0] );
	$result = skyyrose2_card_garment_highlight( array( 'garment_highlight' => fixture_annotation( $front, array_fill( 0, $case[1], $candidate ) ) ), $front, 'sg-009' );
	check_highlight( ( null !== $result ) === $case[2], 'Cap boundary ' . $case[3] );
}

class WC_Product {
	public function __construct( public $id ) {}
	public function is_visible() { return true; }
	public function get_id() { return $this->id; }
	public function get_permalink() { return 'https://example.test/product/' . $this->id; }
	public function get_name() { return 'The Sherpa <Jacket>'; }
	public function get_sku() { return 'sg-009'; }
	public function get_price_html() { return '$80'; }
	public function get_type() { return 'variable'; }
	public function is_in_stock() { return true; }
	public function is_purchasable() { return true; }
	public function get_short_description() { return ''; }
}
function __( $s ) { return $s; }
function esc_attr( $s ) { return htmlspecialchars( (string) $s, ENT_QUOTES, 'UTF-8' ); }
function esc_html( $s ) { return esc_attr( $s ); }
function esc_url( $s ) { return esc_attr( $s ); }
function esc_html_e( $s ) { echo esc_html( $s ); }
function tag_escape( $s ) { return $s; }
function sanitize_title( $s ) { return $s; }
function wp_kses_post( $s ) { return $s; }
function wp_strip_all_tags( $s ) { return strip_tags( $s ); }
function wp_trim_words( $s ) { return $s; }
function skyyrose2_collections() { return array( 'signature' => array( 'name' => 'Signature' ) ); }
function skyyrose2_product_presentation() { return $GLOBALS['fixture_record']; }
function skyyrose2_approved_card_front() { return $GLOBALS['fixture_front']; }
// Synthetic commerce fixture: highlights do not authorize an order state.
function skyyrose2_is_transaction_preorder_product( $product ) { return false; }
function woocommerce_template_loop_add_to_cart() {
	if ( ! empty( $GLOBALS['throw_native'] ) ) { throw new RuntimeException( 'Native failure' ); }
	echo '<a href="/purchase/' . $GLOBALS['product']->get_id() . '">Select options</a>';
}
function render_highlight_card() {
	$args = array( 'product' => new WC_Product( 41 ), 'frame' => false );
	ob_start();
	try { include SKYYROSE2_DIR . '/template-parts/commerce/product-card.php'; return ob_get_clean(); }
	catch ( Throwable $error ) { ob_end_clean(); throw $error; }
}
$GLOBALS['fixture_record'] = $record;
$GLOBALS['fixture_front'] = $front;
$product = new WC_Product( 7 );
$previous = $product;
$html = render_highlight_card();
check_highlight( $product === $previous && str_contains( $html, '/purchase/41' ), 'Exact native card product and global restoration' );
check_highlight( 1 === substr_count( $html, '<svg ' ) && str_contains( $html, 'clip-rule="evenodd"' ), 'Source-bound union clip and outside mask with per-polygon holes rendered' );
check_highlight( str_contains( $html, 'Highlight item: The Sherpa &lt;Jacket&gt;' ), 'Exact Woo product identity escaped' );
check_highlight( strpos( $html, '</a>' ) < strpos( $html, 'data-garment-toggle' ), 'Toggle outside primary PDP anchor' );
check_highlight( str_contains( $html, 'aria-pressed="false"' ) && str_contains( $html, 'data-garment-toggle' ) && str_contains( $html, 'hidden>Highlight item' ), 'Progressive toggle initially hidden until decoded image geometry' );
$first_html = $html;
$overlap = $polygon;
$overlap['outer'] = array( array( 800, 200 ), array( 1000, 200 ), array( 1000, 900 ), array( 800, 900 ) );
$overlap['holes'] = array();
$GLOBALS['fixture_record']['garment_highlight'] = fixture_annotation( $front, array( $polygon, $overlap ) );
$html = render_highlight_card();
check_highlight( 2 === substr_count( $html, 'clip-rule="evenodd"' ) && str_contains( $html, '<mask ' ) && str_contains( $html, 'mask-type:luminance' ), 'Overlapping polygon children unioned inside source-sized luminance mask' );
preg_match( '/<clipPath id="([^"]+)"/', $first_html, $first_id );
preg_match( '/<clipPath id="([^"]+)"/', $html, $second_id );
check_highlight( $first_id[1] !== $second_id[1], 'Multiple cards receive unique mask IDs' );
if ( '1' === getenv( 'V2_GARMENT_RENDER_FIXTURE' ) ) { echo $html; exit; }
$GLOBALS['fixture_record'] = array( 'collection' => 'signature' );
$html = render_highlight_card();
check_highlight( ! str_contains( $html, '<svg ' ) && ! str_contains( $html, 'data-garment-toggle' ) && str_contains( $html, '/purchase/41' ), 'No mask preserves ordinary direct commerce' );
$GLOBALS['throw_native'] = true;
try { render_highlight_card(); throw new RuntimeException( 'Expected failure' ); }
catch ( RuntimeException $error ) { check_highlight( 'Native failure' === $error->getMessage() && $product === $previous, 'Native exception preserves global product' ); }
echo "PASS reviewed garment source/SKU/hash/dimensions, simple polygons and holes, fail-closed fallback, exact identity and native commerce preservation\n";
