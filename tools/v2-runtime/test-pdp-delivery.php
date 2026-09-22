<?php
/** Read-only delivery regression against real accepted files and the actual PDP resolver. */
define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_DIR', realpath( __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2' ) );
define( 'SKYYROSE2_URI', 'https://theme.invalid' );
$GLOBALS['is_product'] = true;
$GLOBALS['file_reads'] = 0;
$GLOBALS['files'] = array();
class WC_Product {
	public function __construct( private string $sku, private int $image = 77 ) {}
	public function get_sku() { return $this->sku; }
	public function get_id() { return 101; }
	public function get_image_id() { return $this->image; }
	public function get_gallery_image_ids() { return array(); }
}
class WC_Product_Variation extends WC_Product { public function get_parent_id() { return 101; } }
function add_filter( $hook, $callback, $priority = 10, $arguments = 1 ) {
	$GLOBALS['registered'][ $hook ] = array( $callback, $priority, $arguments );
}
function is_product() { return $GLOBALS['is_product']; }
function get_attached_file( $id, $unfiltered = false ) {
	verify_delivery( $unfiltered, 'Attachment identity must use the local unfiltered path.' );
	++$GLOBALS['file_reads'];
	return $GLOBALS['files'][ $id ] ?? false;
}
function sanitize_key( $value ) { return preg_replace( '/[^a-z0-9_-]/', '', strtolower( $value ) ); }
function absint( $value ) { return abs( (int) $value ); }
function wp_get_attachment_metadata( $id ) { return array( 'width' => 1024, 'height' => 1536 ); }
function wp_attachment_is_image( $id ) { return $id > 0; }
function wp_get_attachment_url( $id ) { return 'https://uploads.invalid/' . $id . '.webp'; }
function skyyrose2_product_card_media_manifest() {
	return json_decode( file_get_contents( SKYYROSE2_DIR . '/data/opening-product-media.json' ), true );
}
function skyyrose2_product_verified_card_media( $product ) { return array(); }
function verify_delivery( $condition, $message ) {
	if ( ! $condition ) { throw new RuntimeException( $message ); }
}
$source = file_get_contents( SKYYROSE2_DIR . '/functions.php' );
$start = strpos( $source, 'function skyyrose2_product_commerce_media(' );
$end = strpos( $source, '/** Keep Product schema', $start );
verify_delivery( false !== $start && false !== $end, 'Actual PDP resolver extraction failed.' );
eval( substr( $source, $start, $end - $start ) );
require SKYYROSE2_DIR . '/inc/pdp-media-delivery.php';
$accepted = json_decode( file_get_contents( SKYYROSE2_DIR . '/data/approved-card-fronts.json' ), true );
$sg = new WC_Product( 'sg-005' );
$original = SKYYROSE2_DIR . '/' . $accepted['products']['sg-005']['src'];
$GLOBALS['files'][77] = $original;
$delivery = skyyrose2_pdp_media_delivery( $sg, 77 );
verify_delivery( str_ends_with( $delivery['src'] ?? '', '/sg-005-480w.webp' ), 'Matching permitted original must reuse the existing 480w file.' );
verify_delivery( 480 === $delivery['width'] && 720 === $delivery['height'], 'Delivery dimensions must be real uncropped rendition dimensions.' );
verify_delivery( 3 === count( explode( ', ', $delivery['srcset'] ) ), 'Only the three verified derivatives should be candidates.' );
verify_delivery( str_contains( $delivery['sizes'], '47.99rem' ) && str_contains( $delivery['sizes'], 'svh' ), 'Sizes must reflect the actual contained mobile image.' );

// This rejected SKU has a separately accepted card and byte-matched original.
// The real opening/PDP resolver must reject it before any local file inspection.
$GLOBALS['files'][78] = SKYYROSE2_DIR . '/' . $accepted['products']['br-003']['src'];
$reads = $GLOBALS['file_reads'];
verify_delivery( array() === skyyrose2_pdp_media_delivery( new WC_Product( 'br-003', 78 ), 78 ), 'Card acceptance must not override rejected PDP authority.' );
verify_delivery( $reads === $GLOBALS['file_reads'], 'Rejected media must stop before reading the attachment file.' );
verify_delivery( array() === skyyrose2_pdp_media_delivery( $sg, 78 ), 'A matching SKU must not permit an unrelated attachment ID.' );
verify_delivery( array() === skyyrose2_pdp_media_delivery( new WC_Product( 'unknown' ), 77 ), 'Unknown accepted SKU must preserve native delivery.' );
$GLOBALS['files'][77] = SKYYROSE2_DIR . '/' . $accepted['products']['br-006']['src'];
verify_delivery( array() === skyyrose2_pdp_media_delivery( $sg, 77 ), 'A different accepted garment is not an interchangeable delivery source.' );
$GLOBALS['files'][77] = 'https://offload.invalid/sg-005.webp';
verify_delivery( array() === skyyrose2_pdp_media_delivery( $sg, 77 ), 'Remote files cannot establish local byte identity.' );
$GLOBALS['files'][77] = false;
verify_delivery( array() === skyyrose2_pdp_media_delivery( $sg, 77 ), 'Missing local files must preserve native delivery.' );
$GLOBALS['files'][77] = $original;

// Invoke the actual template callback: optimize display, retain native alt/full
// metadata and the ID used by Woo's unchanged thumbnail/lightbox wrapper.
$GLOBALS['skyyrose2_pdp_media_context'] = skyyrose2_pdp_capture_media_context( $sg );
$image_attributes = static function ($attributes, $id, $size, $main) use ($sg) {
	return skyyrose2_pdp_gallery_attributes($attributes, $id, $main, $sg);
};
$native = array( 'alt' => 'Native accessible description', 'data-src' => 'native-full.webp', 'data-large_image' => 'native-full.webp', 'data-large_image_width' => 1024, 'data-large_image_height' => 1536 );
$attrs = $image_attributes( $native, 77, 'woocommerce_single', true );
verify_delivery( $delivery['src'] === $attrs['src'] && 'eager' === $attrs['loading'], 'Native primary must use responsive display and eager loading.' );
foreach ( $native as $key => $value ) {
	verify_delivery( $attrs[$key] === $value, 'Native gallery metadata changed: ' . $key );
}
$GLOBALS['files'][77] = false;
$fallback = $image_attributes( $native, 77, 'woocommerce_single', true );
verify_delivery( ! isset( $fallback['src'] ) && ! isset( $fallback['srcset'] ), 'Missing proof must leave native source selection to WordPress.' );
$GLOBALS['files'][77] = $original;

unset($GLOBALS['skyyrose2_pdp_media_context']);
$variation = new WC_Product_Variation('sg-005-m');
$native_variation = array( 'image_id' => 77, 'price' => 125, 'is_purchasable' => true, 'image' => array( 'src' => 'native-full.webp', 'full_src' => 'native-full.webp', 'full_src_w' => 1024, 'full_src_h' => 1536, 'gallery_thumbnail_src' => 'native-thumb.webp', 'thumb_src' => 'native-small.webp', 'alt' => 'Native variation alt' ) );
$optimized = skyyrose2_pdp_variation_delivery( $native_variation, $sg, $variation );
verify_delivery( $optimized['image']['src'] === $delivery['src'], 'Variation updates should not restore the full display download.' );
foreach ( array( 'full_src', 'full_src_w', 'full_src_h', 'gallery_thumbnail_src', 'thumb_src', 'alt' ) as $key ) {
	verify_delivery( $optimized['image'][$key] === $native_variation['image'][$key], 'Variation full/thumbnail metadata changed: ' . $key );
}
verify_delivery( $optimized['image_id'] === 77 && $optimized['price'] === 125 && $optimized['is_purchasable'], 'Commerce/attachment identity must stay native.' );
$rejected = array( 'image_id' => 0, 'image' => array() );
$rejected_result = skyyrose2_pdp_variation_delivery( $rejected, new WC_Product('br-003'), $variation );
verify_delivery( 0 === $rejected_result['image_id'] && array() === $rejected_result['image'] && '' === $rejected_result['gallery_images_html'], 'Priority-30 rejection must remain empty.' );
$GLOBALS['is_product'] = false;
verify_delivery( $native_variation === skyyrose2_pdp_variation_delivery( $native_variation, $sg, $variation ), 'Non-PDP variation contexts must stay native.' );
verify_delivery( array( 'skyyrose2_pdp_variation_delivery', 40, 3 ) === $GLOBALS['registered']['woocommerce_available_variation'], 'Delivery must run after the existing priority-30 rejection guard.' );
echo "PASS PDP delivery: permission, exact bytes, rejected/unknown/mismatch/remote/missing fallback, native gallery metadata, variation IDs/full/thumb preservation and route scope.\n";
