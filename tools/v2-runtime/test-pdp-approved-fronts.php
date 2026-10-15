<?php
/** Actual current inventory; every current card must resolve its exact eligible master. */
define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_DIR', dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2' );
define( 'SKYYROSE2_URI', 'https://theme.invalid' );
class WC_Product {
    public function __construct( public $sku ) {}
    public function get_sku( $context = 'view' ) { return $this->sku; }
    public function get_name() { return $this->sku; }
}
function add_filter( ...$args ) {} function add_action( ...$args ) {}
function skyyrose2_product_presentation( $product ) { return $GLOBALS['presentation']['products'][ $product->sku ] ?? array(); }
function check_front( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
$GLOBALS['presentation'] = json_decode( file_get_contents( SKYYROSE2_DIR . '/data/product-presentation-registry.json' ), true );
require SKYYROSE2_DIR . '/inc/v2-media-eligibility.php';
require SKYYROSE2_DIR . '/inc/approved-card-fronts.php';
check_front( 33 === count( $GLOBALS['presentation']['products'] ), 'All 33 current SKUs covered' );
$displayed = array( 'card_front' => 0, 'pdp_on_model_front' => 0 );
$cards = array();
$pdp_fronts = array();
foreach ( $GLOBALS['presentation']['products'] as $sku => $projection ) {
	foreach ( array( 'card_front', 'pdp_on_model_front' ) as $role ) {
		$front = skyyrose2_product_media_front( new WC_Product( $sku ), $role );
		if ( ! $front ) {
			check_front( 'card_front' !== $role, 'Missing current V2 card for ' . $sku );
			continue;
		}
		check_front( $front['sku'] === $sku && $front['collections'] === array( $projection['collection'] ), 'Actual exact SKU and collection binding' );
		check_front( skyyrose2_media_path_allowed( $front['path'], $role, $sku ), 'Actual eligible receipt passes for explicit requested role' );
		if ( 'card_front' === $role ) {
			check_front( 'assets/v2-original/products/' . $sku . '.png' === $front['path'], 'One exact-SKU current master location' );
			$cards[ $sku ] = $front;
		} else {
			$pdp_fronts[ $sku ] = $front;
		}
		++$displayed[ $role ];
	}
}
$historical = json_decode( file_get_contents( SKYYROSE2_DIR . '/data/approved-card-fronts.json' ), true );
foreach ( $historical['products'] ?? array() as $sku => $record ) {
	$current = skyyrose2_approved_pdp_front( new WC_Product( $sku ) );
	if ( ! skyyrose2_media_path_allowed( $record['src'] ?? '', 'pdp_on_model_front', $sku ) ) {
		check_front( ! $current || $current['path'] !== $record['src'], 'Historical approval cannot promote old PDP front' );
	}
}
check_front( 33 === $displayed['card_front'], 'Exactly 33 deliverable current card fronts' );
if ( in_array( '--json', $argv, true ) ) {
	$current_media = array();
	$delivery_media = array();
	foreach ( skyyrose2_media_inventory()['assets'] ?? array() as $path => $record ) {
		if ( 'photograph' === ( $record['kind'] ?? '' ) && in_array( $record['status'] ?? '', array( 'INDEPENDENT_VISUAL_PASS', 'FOUNDER_ACCEPTED' ), true ) && skyyrose2_media_record_allowed( $path, $record ) ) { $current_media[ $path ] = $record; }
		if ( 'DELIVERY_DERIVATIVE' === ( $record['status'] ?? '' ) && skyyrose2_media_record_allowed( $path, $record ) ) { $delivery_media[ $path ] = $record; }
	}
	echo json_encode( array( 'status' => 'PASS', 'cards' => $cards, 'pdp_on_model_front' => $pdp_fronts, 'counts' => $displayed, 'current_reviewed_media' => $current_media, 'eligible_card_renditions' => $delivery_media, 'scope' => 'LOCAL_CURRENT_RUNTIME_INVENTORY' ), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES ) . "\n";
} else {
	echo 'PASS all 33 exact-SKU card fronts and historical approval isolation; separate PDP fronts: ' . $displayed['pdp_on_model_front'] . " (local inventory only)\n";
}
