<?php
/**
 * Isolated label rendering test; simulated media guards, no asset approval claim.
 * Synthetic identities and product states never write the canonical registry.
 *
 * @package SkyyRoseFlagship2
 */

define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_DIR', sys_get_temp_dir() . '/stream1-label-fixture-' . bin2hex( random_bytes( 4 ) ) );
define( 'SKYYROSE2_URI', 'https://example.invalid' );
mkdir( SKYYROSE2_DIR . '/data', 0700, true );
$poster = array( 'role' => 'poster', 'path' => 'synthetic.webp', 'sha256' => 'synthetic-unit-hash' );
file_put_contents( SKYYROSE2_DIR . '/data/approved-scroll-world-scenes.json', json_encode( array( 'scenes' => array( 'UNIT' => array( 'required_runtime_assets' => array( $poster ) ) ) ) ) );
$points = array();
foreach ( array( 'regular', 'variable', 'preorder' ) as $position => $sku ) {
	$points[] = array( 'sku' => $sku, 'x' => 0.2 + $position * 0.2, 'y' => 0.5 );
}
file_put_contents( SKYYROSE2_DIR . '/data/scene-hotspots.json', json_encode( array( 'schema_version' => 1, 'scenes' => array( 'UNIT' => array( 'poster' => $poster['path'], 'poster_sha256' => $poster['sha256'], 'points' => $points ) ) ) ) );
class Skyyrose2LabelProduct {
	public function __construct( public string $name, public bool $preorder, public string $type = 'simple' ) {}
	public function get_name() { return $this->name; }
	public function get_permalink() { return 'https://example.invalid/' . $this->name; }
	public function get_price_html() { return '<span>$80</span>'; }
	public function is_type( $type ) { return $type === $this->type; }
}
function __( $text ) { return $text; }
function esc_html( $text ) { return htmlspecialchars( (string) $text, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $text ) { return esc_html( $text ); }
function esc_url( $text ) { return esc_html( $text ); }
function esc_html_e( $text ) { echo esc_html( $text ); }
function wp_kses_post( $text ) { return $text; }
function absint( $value ) { return abs( (int) $value ); }
function sanitize_html_class( $value ) { return $value; }
function skyyrose2_collections() { return array(); }
function skyyrose2_collection_scene_uri() { return 'https://example.invalid/synthetic.webp'; }
function skyyrose2_approved_scroll_world_scene() { return true; }
function skyyrose2_is_transaction_preorder_product( $product ) { return $product->preorder; }
function skyyrose2_scene_product_action_label( $product ) { return 'View ' . $product->name; }
function skyyrose2_resolve_commerce_scene_products() {
	return array( 'state' => 'ready', 'slots' => array(
		array( 'sku' => 'regular', 'product' => new Skyyrose2LabelProduct( 'Regular', false ) ),
		array( 'sku' => 'variable', 'product' => new Skyyrose2LabelProduct( 'Variable', true, 'variable' ) ),
		array( 'sku' => 'preorder', 'product' => new Skyyrose2LabelProduct( 'Preorder', true ) ),
	) );
}
$args = array( 'collection' => 'unit', 'scene' => array( 'scene_id' => 'UNIT', 'hero_composition' => array(), 'preorder_product_links_required' => true, 'product_bindings' => array( 'regular', 'variable', 'preorder' ), 'width' => 1600, 'height' => 900, 'label' => 'Synthetic scene', 'direction' => 'Synthetic scene', 'copy' => 'Synthetic scene' ) );
ob_start();
include __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/template-parts/commerce/hero-composed-scene.php';
$html = ob_get_clean();
foreach ( array( 'Regular', 'Variable', 'Preorder' ) as $position => $name ) {
	$expected = 'aria-label="' . ( $position + 1 ) . '. View ' . $name . '"';
	if ( ! str_contains( $html, $expected ) || ! str_contains( $html, 'class="sr2-scene-hotspot__label" aria-hidden="true">' . $name . '</span>' ) ) {
		throw new RuntimeException( esc_html( 'Incorrect visible/accessibility label for ' . $name ) );
	}
}
if ( 1 !== substr_count( $html, 'Pre-order / Full payment at checkout' ) || str_contains( $html, 'View pre-order:' ) || str_contains( $html, 'pieces in this scene are pre-order items' ) ) {
	throw new RuntimeException( 'Only the resolved simple preorder may assert preorder status.' );
}
echo "PASS: neutral hotspots for regular, variable and preorder; only simple preorder lower link asserts status\n";
