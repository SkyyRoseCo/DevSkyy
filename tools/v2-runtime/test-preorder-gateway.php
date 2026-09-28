<?php
/** Isolated composition test for the V2 pre-order gateway. */
define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_URI', 'https://example.test/theme' );

class WC_Product {
	public function __construct( public string $sku ) {}
}

function __( $value ) { return $value; }
function esc_html( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $value ) { return esc_html( $value ); }
function esc_url( $value ) { return esc_html( $value ); }
function sanitize_title( $value ) { return strtolower( trim( preg_replace( '/[^a-z0-9-]+/i', '-', (string) $value ), '-' ) ); }
function skyyrose2_sot_asset_uri( $path ) { return '/assets/sot/' . $path; }
function skyyrose2_collection_url( $slug ) { return '/collections/' . $slug . '/'; }
function skyyrose2_collections() {
	return array(
		'black-rose' => array( 'name' => 'Black Rose' ),
		'signature' => array( 'name' => 'Signature' ),
	);
}
function skyyrose2_get_products( $limit, $collection ) {
	if ( 100 !== $limit || 'pre-order' !== $collection ) {
		throw new RuntimeException( 'Gateway must request the full pre-order edit' );
	}
	return $GLOBALS['preorder_products'];
}
function skyyrose2_product_presentation( $product ) { return $GLOBALS['presentations'][ $product->sku ]; }
function get_template_part( $slug, $name = null, $args = array() ) {
	if ( 'template-parts/commerce/product-card' !== $slug ) {
		throw new RuntimeException( 'Gateway must use the native commerce card' );
	}
	$GLOBALS['card_calls'][] = $args;
	echo '<article data-test-sku="' . esc_attr( $args['product']->sku ) . '"></article>';
}
function check_preorder( $condition, $message ) {
	if ( ! $condition ) {
		throw new RuntimeException( $message );
	}
}
function render_preorder() {
	ob_start();
	include __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/template-parts/v2-preorder.php';
	return ob_get_clean();
}

$GLOBALS['preorder_products'] = array( new WC_Product( 'br-003' ), new WC_Product( 'sg-010' ), new WC_Product( 'br-008' ) );
$GLOBALS['presentations'] = array(
	'br-003' => array( 'collection' => 'black-rose', 'presentation' => 'jersey-series' ),
	'sg-010' => array( 'collection' => 'signature', 'presentation' => 'signature' ),
	'br-008' => array( 'collection' => 'black-rose', 'presentation' => 'jersey-series' ),
);
$GLOBALS['card_calls'] = array();
$html = render_preorder();
check_preorder( 3 === count( $GLOBALS['card_calls'] ), 'All pre-order products retain their native commerce cards' );
check_preorder( 1 === substr_count( $html, 'id="reserve-jersey-series"' ) && 1 === substr_count( $html, 'id="reserve-signature"' ), 'Products are grouped by their presentation collection' );
check_preorder( false === strpos( $html, 'id="reserve-black-rose"' ), 'Jersey products do not leak into a generic Black Rose edit' );
check_preorder( false !== strpos( $html, 'data-test-sku="br-003"' ) && false !== strpos( $html, 'data-test-sku="sg-010"' ), 'Both collection edits render' );
check_preorder( 4 === $GLOBALS['card_calls'][0]['heading_level'] && false === $GLOBALS['card_calls'][0]['frame'], 'Commerce card keeps bounded heading and garment-only media' );
check_preorder( false !== strpos( $html, 'Delivery timing is shown on each product page when available.' ), 'Gateway places available delivery timing with the product' );
check_preorder( false === strpos( $html, 'Full payment at checkout' ), 'Gateway does not invent a payment term' );
check_preorder( false !== strpos( $html, 'house-monument-20260928.webp' ) && false === strpos( $html, 'black-rose-salon' ), 'House arrival uses garment-free monument' );

$GLOBALS['preorder_products'] = array();
$GLOBALS['card_calls'] = array();
$html = render_preorder();
check_preorder( 0 === count( $GLOBALS['card_calls'] ) && false !== strpos( $html, 'No pieces are available to pre-order right now.' ), 'Empty live catalog degrades honestly' );
echo "PASS V2 pre-order gateway grouping, native card routing, and empty state\n";
