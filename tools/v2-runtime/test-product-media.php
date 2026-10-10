<?php
/** Isolated tests of the actual PDP media resolver and schema/variation filters. */
$source = file_get_contents( __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/functions.php' );
$start = strpos( $source, '/** Resolve PDP commerce attachments' );
$end = strpos( $source, "/**\n * Render the shared", $start );
function add_filter() {}
function sanitize_key( $key ) { return strtolower( $key ); }
function absint( $value ) { return abs( (int) $value ); }
function skyyrose2_product_card_media_manifest() { return $GLOBALS['manifest']; }
function skyyrose2_product_verified_card_media() { return $GLOBALS['editorial']; }
function wp_get_attachment_metadata( $id ) { return in_array( $id, array( 1, 2, 3 ), true ) ? array( 'width' => 600, 'height' => 900 ) : array(); }
function wp_attachment_is_image( $id ) { return in_array( $id, array( 1, 2, 3 ), true ); }
function wp_get_attachment_url( $id ) { return 'https://example.test/' . $id . '.webp'; }
class WC_Product {
	public function get_sku() { return 'test'; }
	public function get_image_id() { return 1; }
	public function get_gallery_image_ids() { return array( 2, 1, 999 ); }
}
if ( false === $start || false === $end ) { throw new Exception( 'Resolver extraction failed' ); }
eval( substr( $source, $start, $end - $start ) );
function check( $condition, $message ) { if ( ! $condition ) { throw new Exception( $message ); } }
$product = new WC_Product();
$GLOBALS['manifest'] = array( 'products' => array( 'test' => array( 'status' => 'STALE_PRODUCT_HASH' ) ) );
$GLOBALS['editorial'] = array();
check( skyyrose2_product_commerce_media( $product ) === array( 'state' => 'commerce', 'ids' => array( 1, 2 ) ), 'Stale editorial must allow valid assigned commerce attachments' );
$GLOBALS['manifest']['products']['test']['status'] = 'MISSING_APPROVED_ON_MODEL_FRONT';
check( skyyrose2_product_commerce_media( $product )['state'] === 'commerce', 'Missing editorial must not suppress commerce media' );
$GLOBALS['editorial'] = array( array( 'id' => 3 ) );
check( skyyrose2_product_commerce_media( $product ) === array( 'state' => 'editorial', 'ids' => array( 3 ) ), 'Valid editorial wins' );
$GLOBALS['editorial'] = array( array( 'id' => 999 ) );
check( skyyrose2_product_commerce_media( $product )['state'] === 'commerce', 'Invalid editorial attachment falls back to commerce' );
$GLOBALS['manifest']['products']['test']['status'] = 'REJECTED_AUTHENTICITY';
check( skyyrose2_product_commerce_media( $product )['ids'] === array(), 'Rejected media cannot be filled from Woo' );
check( ! isset( skyyrose2_product_commerce_schema_image( array( 'image' => 'rejected' ), $product )['image'] ), 'Rejected schema image removed' );
$data = skyyrose2_product_commerce_variation_image( array( 'image' => array( 'src' => 'rejected' ), 'price' => 25 ), $product, null );
check( empty( $data['image'] ) && 25 === $data['price'], 'Variation cannot restore rejected image or change price' );
$GLOBALS['manifest'] = array();
check( skyyrose2_product_commerce_media( $product )['state'] === 'missing', 'Missing approval manifest fails closed' );
echo "PASS PDP editorial/commerce/rejection hierarchy, schema and variation isolation\n";
