<?php
/**
 * Offline rendering regression for the actual V2 pre-order template.
 * Synthetic Woo objects and simulated eligibility are fixtures, never media approval.
 */
define( 'ABSPATH', __DIR__ );
$fixture_root = sys_get_temp_dir() . '/sr2-preorder-' . bin2hex( random_bytes( 6 ) );
mkdir( $fixture_root . '/assets/test', 0777, true );
define( 'SKYYROSE2_DIR', $fixture_root );
$theme = dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2';
$fixture_source = $theme . '/assets/sot/brand/skyyrose-logo-still-384w.webp';
foreach ( array( 'signature', 'black-rose', 'love-hurts', 'arrival' ) as $slug ) {
	copy( $fixture_source, $fixture_root . '/assets/test/' . $slug . '.webp' );
}
class Preorder_Fixture_Product {
	public function __construct( public string $sku, public string $collection, public int $id ) {}
	public function get_sku() { return $this->sku; }
	public function get_name() { return 'Synthetic ' . $this->sku . ' <piece>'; }
	public function get_permalink() { return 'https://example.test/product/' . $this->id . '/'; }
	public function get_price_html() { return '<span class="amount">$' . $this->id . '.01</span>'; }
}
function __( $value, ...$args ) { return $value; }
function esc_html( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $value ) { return esc_html( $value ); }
function esc_url( $value ) { return esc_html( $value ); }
function esc_html_e( $value, ...$args ) { echo esc_html( $value ); }
function esc_attr_e( $value, ...$args ) { echo esc_attr( $value ); }
function sanitize_title( $value ) { return strtolower( (string) $value ); }
function sanitize_key( $value ) { return strtolower( (string) $value ); }
function skyyrose2_collections() {
	return array( 'signature' => array( 'name' => 'Signature' ), 'black-rose' => array( 'name' => 'Black Rose' ), 'love-hurts' => array( 'name' => 'Love Hurts' ), 'kids-capsule' => array( 'name' => 'Kids Capsule' ) );
}
function skyyrose2_presentation_registry() {
	return array( 'collections' => array_fill_keys( array_keys( skyyrose2_collections() ), array( 'story' => array( 'seed' => 'Synthetic story <seed> & identity' ) ) ) );
}
function skyyrose2_product_presentation( $product ) { return array( 'collection' => $product->collection ); }
function skyyrose2_get_products( $limit, $collection ) {
	preorder_check( -1 === $limit && 'pre-order' === $collection, 'Native query requests every published eligible pre-order' );
	return $GLOBALS['fixture_products'];
}
function skyyrose2_collection_url( $slug ) { return 'https://example.test/collections/' . $slug . '/'; }
function skyyrose2_media_inventory() { return array( 'assets' => $GLOBALS['fixture_media'] ); }
function skyyrose2_media_uri( $path, $role ) {
	$GLOBALS['media_requests'][] = array( $path, $role );
	$record = $GLOBALS['fixture_media'][ $path ];
	return ! empty( $record['fixture_allowed'] ) && in_array( $role, $record['roles'], true ) ? 'https://example.test/v2/' . $path : '';
}
function skyyrose2_collection_media( $collection, $role ) {
	$path = 'assets/test/' . $collection . '.webp';
	$record = $GLOBALS['fixture_media'][ $path ] ?? array();
	if ( ! is_array( $record['roles'] ?? null ) || ! is_array( $record['skus'] ?? null ) || ( $record['collections'] ?? array() ) !== array( $collection ) || ! in_array( $role, $record['roles'], true ) || ! skyyrose2_media_uri( $path, $role ) ) { return array(); }
	return array( 'path' => $path, 'skus' => $record['skus'], 'src' => 'https://example.test/v2/' . $path, 'role' => $role );
}
function skyyrose2_collection_media_markup( $scene, ...$args ) {
	return '<img src="' . esc_url( $scene['src'] ) . '" data-media-role="' . esc_attr( $scene['role'] ) . '" alt="Synthetic merchandise">';
}
function get_template_part( $path, $name, $args ) {
	preorder_check( 'template-parts/commerce/product-card' === $path, 'Native shared commerce partial is retained' );
	preorder_check( false === $args['frame'] && 4 === $args['heading_level'], 'Cards use garment-only framing and proper nested headings' );
	$GLOBALS['rendered_products'][] = $args['product'];
	$product = $args['product'];
	echo '<article data-sku="' . esc_attr( $product->get_sku() ) . '"><h4>' . esc_html( $product->get_name() ) . '</h4>' . $product->get_price_html() . '<a href="' . esc_url( $product->get_permalink() ) . '">Select options</a></article>';
}
function preorder_check( $condition, $message ) {
	if ( ! $condition ) { throw new RuntimeException( $message ); }
}
function render_preorder( $template ) {
	$GLOBALS['rendered_products'] = array();
	$GLOBALS['media_requests'] = array();
	ob_start();
	include $template;
	return ob_get_clean();
}
function fixture_products( $groups ) {
	$result = array();
	foreach ( $groups as $collection => $skus ) {
		foreach ( $skus as $sku ) { $result[] = new Preorder_Fixture_Product( $sku, $collection, 100 + count( $result ) ); }
	}
	return array_reverse( $result ); // Mixed native ordering must not determine collection order.
}
$template = $theme . '/template-parts/v2-preorder.php';
$GLOBALS['fixture_products'] = fixture_products(
	array(
		'signature' => array( 'sg-001', 'sg-002' ),
		'black-rose' => array( 'br-003', 'br-006', 'br-008', 'br-009', 'br-010', 'br-011', 'br-012', 'br-014', 'br-015' ),
		'love-hurts' => array( 'lh-005' ),
	)
);
$GLOBALS['fixture_media'] = array();
set_error_handler( static function ( $number, $message ) { throw new RuntimeException( $message ); } );
try {
	$html = render_preorder( $template );
	preorder_check( 12 === count( $GLOBALS['rendered_products'] ), 'All 12 selected products survive grouping exactly once' );
	$expected = $GLOBALS['fixture_products'];
	$actual = $GLOBALS['rendered_products'];
	usort( $expected, static fn( $a, $b ) => $a->id <=> $b->id );
	usort( $actual, static fn( $a, $b ) => $a->id <=> $b->id );
	preorder_check( $actual === $expected, 'Exact Woo object identities are preserved' );
	foreach ( array( 'signature' => 2, 'black-rose' => 9, 'love-hurts' => 1 ) as $slug => $count ) {
		preg_match( '#<section id="reserve-' . $slug . '".*?</section>#s', $html, $match );
		preorder_check( $count === substr_count( $match[0] ?? '', '<article ' ), 'Separate exact membership: ' . $slug );
	}
	preorder_check( strpos( $html, 'id="reserve-signature"' ) < strpos( $html, 'id="reserve-black-rose"' ) && strpos( $html, 'id="reserve-black-rose"' ) < strpos( $html, 'id="reserve-love-hurts"' ), 'Signature, Black Rose and Love Hurts remain distinct in intended order' );
	preorder_check( ! str_contains( $html, '<img ' ) && ! str_contains( $html, 'src=""' ), 'Missing eligibility emits no blank or legacy image' );
	preorder_check( str_contains( $html, '&lt;seed&gt; &amp; identity' ) && str_contains( $html, '&lt;piece&gt;' ), 'Canonical narrative and native product text remain escaped' );
	preorder_check( str_contains( $html, '$100.01' ) && str_contains( $html, 'Full payment at checkout' ) && str_contains( $html, 'does not reserve stock or establish a shipping date' ), 'Native factual commerce and existing full-payment terms remain visible' );
	foreach ( array( 'black-rose-salon', 'monuments', 'assets/scroll-world', 'skyyrose-flagship/' ) as $legacy ) {
		preorder_check( ! str_contains( $html, $legacy ), 'No inherited pre-order path: ' . $legacy );
	}

	foreach ( array( 'signature', 'black-rose', 'love-hurts' ) as $slug ) {
		$cast = array_values( array_map( static fn( $product ) => $product->sku, array_filter( $GLOBALS['fixture_products'], static fn( $product ) => $product->collection === $slug ) ) );
		$GLOBALS['fixture_media'][ 'assets/test/' . $slug . '.webp' ] = array( 'kind' => 'photograph', 'roles' => array( 'merchandise_scene' ), 'collections' => array( $slug ), 'skus' => $cast, 'fixture_allowed' => true );
	}
	$html = render_preorder( $template );
	preorder_check( 3 === substr_count( $html, '<figure class="sr2-reserve-scene" data-media-role="merchandise_scene"' ) && 3 === substr_count( $html, '<img ' ), 'One permitted role-bound merchandise scene appears per collection' );
	preorder_check( 3 === substr_count( $html, 'sr2-reserve-edit__intro sr2-reserve-edit__intro--scene' ), 'Only groups with a rendered scene take the two-column intro' );
	preorder_check( str_contains( $html, 'Synthetic lh-005 &lt;piece&gt;' ), 'Scene cast links use native product names and URLs' );
	foreach ( $GLOBALS['media_requests'] as $request ) { preorder_check( 'merchandise_scene' === $request[1], 'Scene lookup always supplies the required eligibility role' ); }
	$GLOBALS['fixture_media']['assets/test/signature.webp']['fixture_allowed'] = false;
	$GLOBALS['fixture_media']['assets/test/black-rose.webp']['skus'][] = 'sg-001';
	$GLOBALS['fixture_media']['assets/test/love-hurts.webp']['collections'] = array( 'black-rose' );
	$html = render_preorder( $template );
	preorder_check( ! str_contains( $html, '<img ' ), 'Denied, cross-cast and wrong-collection records have no fallback' );
	preorder_check( 3 === substr_count( $html, 'class="sr2-reserve-edit__intro"' ) && ! str_contains( $html, 'sr2-reserve-edit__intro--scene' ), 'Scene-less groups keep the single-column intro (no empty scene column)' );
	$GLOBALS['fixture_media'] = array(
		'assets/test/arrival.webp' => array( 'kind' => 'photograph', 'roles' => array( 'preorder_arrival' ), 'collections' => array( 'signature', 'black-rose', 'love-hurts' ), 'skus' => array( 'sg-001', 'br-006', 'lh-005' ), 'fixture_allowed' => true ),
		'bad-roles' => array( 'kind' => 'photograph', 'roles' => 'merchandise_scene' ),
		'bad-cast' => array( 'kind' => 'photograph', 'roles' => array( 'merchandise_scene' ), 'skus' => array( array( 'bad' ) ) ),
	);
	$html = render_preorder( $template );
	preorder_check( ! str_contains( $html, '<img ' ) && ! in_array( 'preorder_arrival', array_column( $GLOBALS['media_requests'], 1 ), true ), 'A generic preorder_arrival asset is not requested or shown; collection scenes remain the only scene slots' );
	$GLOBALS['fixture_products'] = fixture_products( array( 'signature' => array( 'sg-001', 'sg-002', 'sg-003', 'sg-005', 'sg-015' ), 'black-rose' => array( 'br-003', 'br-006', 'br-008', 'br-009', 'br-010', 'br-011' ), 'love-hurts' => array( 'lh-005' ) ) );
	$GLOBALS['fixture_media'] = array();
	$html = render_preorder( $template );
	preorder_check( 12 === count( $GLOBALS['rendered_products'] ) && str_contains( $html, 'data-sku="sg-003"' ) && str_contains( $html, 'data-sku="sg-005"' ) && str_contains( $html, 'data-sku="sg-015"' ), 'Alternate current Woo assortment is preserved without a creative-list override' );
	$GLOBALS['fixture_products'] = fixture_products( array( 'signature' => array( 'sg-001', 'sg-002', 'sg-003', 'sg-005', 'sg-015' ), 'black-rose' => array( 'br-003', 'br-006', 'br-008', 'br-009', 'br-010', 'br-011', 'br-012', 'br-014', 'br-015' ), 'love-hurts' => array( 'lh-005' ) ) );
	$html = render_preorder( $template );
	preorder_check( 15 === count( $GLOBALS['rendered_products'] ) && str_contains( $html, 'data-sku="br-015"' ), 'All fifteen eligible pieces survive grouping without a twelve-product cap' );
	$GLOBALS['fixture_products'] = fixture_products( array( 'kids-capsule' => array( 'kids-001' ) ) );
	$html = render_preorder( $template );
	preorder_check( 1 === count( $GLOBALS['rendered_products'] ) && str_contains( $html, 'reserve-kids-capsule' ), 'A future valid collection is preserved rather than silently dropped' );
	echo "PASS offline pre-order render: complete fifteen-item assortment, membership variation, distinct groups, native identities/terms, role/cast/collection eligibility, malformed media and zero legacy fallback\n";
} finally {
	restore_error_handler();
	foreach ( glob( $fixture_root . '/assets/test/*' ) as $file ) { unlink( $file ); }
	rmdir( $fixture_root . '/assets/test' );
	rmdir( $fixture_root . '/assets' );
	rmdir( $fixture_root );
}
