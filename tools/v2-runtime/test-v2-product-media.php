<?php
/** Offline exact-SKU delivery contract. Synthetic pixels/receipts are never fashion approvals. */
define( 'ABSPATH', '/tmp/' );
$root = dirname( __DIR__, 2 );
$theme = $root . '/wordpress-theme/skyyrose-flagship-2';
$fixture = sys_get_temp_dir() . '/v2-sku-media-' . bin2hex( random_bytes( 5 ) );
mkdir( $fixture . '/assets/v2-original/products', 0700, true );
mkdir( $fixture . '/data/v2-media-reviews', 0700, true );
define( 'SKYYROSE2_DIR', $fixture );
define( 'SKYYROSE2_URI', 'https://example.test/v2' );
function add_filter( ...$args ) {} function add_action( ...$args ) {}
function is_admin() { return false; } function is_product() { return true; }
function absint( $value ) { return abs( (int) $value ); }
function esc_attr( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_url( $value ) { return esc_attr( $value ); }
function esc_html__( $value, $domain ) { return esc_attr( $value ); }
function wp_get_attachment_url( $id ) { return $GLOBALS['attachments'][ $id ] ?? ''; }
function get_attached_file( $id, $unfiltered ) { check( true === $unfiltered, 'Local attachment identity uses raw path' ); return $GLOBALS['files'][ $id ] ?? false; }
function wc_get_product( $id ) { return $GLOBALS['products'][ $id ] ?? null; }
function skyyrose2_media_inventory() { return $GLOBALS['inventory']; }
function skyyrose2_product_presentation( $product ) { return $GLOBALS['presentation']['products'][ strtolower( $product->get_sku( 'edit' ) ) ] ?? array(); }
class WC_Product {
    public function __construct( public $id, public $sku, public $ids = array( 901, 902 ) ) {}
    public function get_sku( $context = 'view' ) { return $this->sku; }
    public function get_id() { return $this->id; }
    public function get_name() { return $this->sku . ' <contract>'; }
    public function get_image_id() { return $this->ids[0] ?? 0; }
    public function get_gallery_image_ids() { return array_slice( $this->ids, 1 ); }
}
class WC_Product_Variation extends WC_Product {
    public function __construct( $id, $sku, public $parent, public $attributes ) { parent::__construct( $id, $sku ); }
    public function get_parent_id() { return $this->parent; }
    public function get_variation_attributes() { return $this->attributes; }
    public function get_sku( $context = 'view' ) { return 'view' === $context && '' === $this->sku ? wc_get_product( $this->parent )->get_sku() : $this->sku; }
}
class WP_REST_Response {
    public function __construct( private $data ) {}
    public function get_data() { return $this->data; }
    public function set_data( $data ) { $this->data = $data; }
}
class ContractRequest { public function __construct( private $route ) {} public function get_route() { return $this->route; } }
function check( $result, $label ) { if ( ! $result ) { throw new RuntimeException( $label ); } }
$GLOBALS['presentation'] = json_decode( file_get_contents( $theme . '/data/product-presentation-registry.json' ), true );
$slots = json_decode( file_get_contents( $theme . '/data/v2-required-media-roles.json' ), true )['slots'];
$skus = array_column( array_filter( $slots, static fn( $slot ) => 'card_front' === $slot['role'] ), 'sku' );
check( 33 === count( $skus ) && 33 === count( array_unique( $skus ) ) && count( $slots ) >= count( $skus ), 'Current all-SKU card-role census' );
$GLOBALS['inventory'] = array( 'assets' => array(), 'disallowed_legacy_sha256' => array() );
$bytes = base64_decode( 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l2UAAAAASUVORK5CYII=' );
function contract_asset( $path, $sku, $collection, $roles ) {
    global $fixture, $bytes;
    if ( ! is_dir( dirname( $fixture . '/' . $path ) ) ) { mkdir( dirname( $fixture . '/' . $path ), 0700, true ); }
    file_put_contents( $fixture . '/' . $path, $bytes );
    $hash = hash_file( 'sha256', $fixture . '/' . $path );
    $receipt_path = 'data/v2-media-reviews/' . str_replace( '/', '-', $path ) . '.json';
    $receipt = array( 'asset_sha256' => $hash, 'reviewer' => 'independent-contract-fixture', 'producer' => 'contract-fixture-producer', 'production_id' => 'synthetic-offline-contract-only', 'verdict' => 'PASS', 'product_fidelity_pass' => true, 'v2_originality_pass' => true, 'roles' => $roles, 'skus' => array( $sku ), 'collections' => array( $collection ) );
    file_put_contents( $fixture . '/' . $receipt_path, json_encode( $receipt ) );
    return array( 'sha256' => $hash, 'kind' => 'photograph', 'status' => 'INDEPENDENT_VISUAL_PASS', 'origin' => 'V2_ORIGINAL_20261002', 'producer' => $receipt['producer'], 'production_id' => $receipt['production_id'], 'roles' => $roles, 'skus' => array( $sku ), 'collections' => array( $collection ), 'review' => array( 'path' => $receipt_path, 'sha256' => hash_file( 'sha256', $fixture . '/' . $receipt_path ), 'reviewer' => $receipt['reviewer'], 'verdict' => 'PASS' ) );
}
foreach ( $skus as $index => $sku ) {
    $GLOBALS['products'][ $index + 1 ] = new WC_Product( $index + 1, $sku );
    $path = 'assets/v2-original/products/' . $sku . '.png';
    $GLOBALS['inventory']['assets'][ $path ] = contract_asset( $path, $sku, $GLOBALS['presentation']['products'][ $sku ]['collection'], array( 'card_front', 'pdp_on_model_front' ) );
}
$current_fronts = array( 'schema_version' => 1, 'products' => array() );
foreach ( $skus as $sku ) {
    $path = 'assets/v2-original/products/' . $sku . '.png';
    $entry = $GLOBALS['inventory']['assets'][ $path ];
    $current_fronts['products'][ $sku ] = array( 'src' => $path, 'width' => 1, 'height' => 1, 'sha256' => $entry['sha256'], 'source_sha256' => $entry['sha256'], 'current_fidelity_status' => $entry['status'], 'review' => $entry['review'] );
}
file_put_contents( $fixture . '/data/approved-card-fronts.json', json_encode( $current_fronts ) );
$source = file_get_contents( $theme . '/inc/v2-media-eligibility.php' );
$start = strpos( $source, '/** Validate immutable bytes' );
$end = strpos( $source, 'function skyyrose2_media_start_buffer()', $start );
eval( substr( $source, $start, $end - $start ) );
require $theme . '/inc/approved-card-fronts.php';
require $theme . '/inc/pdp-media-delivery.php';
$source = file_get_contents( $theme . '/functions.php' );
$start = strpos( $source, '/** Resolve attachment IDs only' );
$end = strpos( $source, "/**\n * Render the shared", $start );
check( false !== $start && false !== $end, 'Actual resolver extraction' );
eval( substr( $source, $start, $end - $start ) );
try {
    foreach ( $GLOBALS['products'] as $product ) {
        $front = skyyrose2_approved_card_front( $product );
        check( $front && $product->sku === $front['sku'], 'All 33 exact card fronts' );
        check( $front['src'] === skyyrose2_approved_pdp_front( $product )['src'], 'Explicit same-master PDP role' );
        check( str_contains( skyyrose2_product_v2_thumbnail( '<img src="old.jpg">', $product ), $front['src'] ), 'Same-SKU native thumbnail' );
        check( ! str_contains( skyyrose2_product_v2_thumbnail( '', $product ), '<contract>' ), 'Thumbnail alt escaped' );
    }
    $parent = array_values( array_filter( $GLOBALS['products'], static fn( $p ) => 'sg-009' === $p->sku ) )[0];
    $path = 'assets/v2-original/products/sg-009.png';
    $saved = $GLOBALS['inventory']['assets'][ $path ];
    foreach ( array( 'missing-review', 'wrong-hash', 'wrong-collection', 'mixed-cast', 'card-only' ) as $case ) {
        $bad = $saved;
        if ( 'missing-review' === $case ) { unset( $bad['review'] ); }
        if ( 'wrong-hash' === $case ) { $bad['sha256'] = str_repeat( '0', 64 ); }
        if ( 'wrong-collection' === $case ) { $bad['collections'] = array( 'black-rose' ); }
        if ( 'mixed-cast' === $case ) { $bad['skus'][] = 'sg-002'; }
        if ( 'card-only' === $case ) { $bad = contract_asset( $path, 'sg-009', 'signature', array( 'card_front' ) ); }
        $GLOBALS['inventory']['assets'][ $path ] = $bad;
        check( ! skyyrose2_approved_pdp_front( $parent ), 'Reject ' . $case );
    }
    $GLOBALS['inventory']['assets'][ $path ] = contract_asset( $path, 'sg-009', 'signature', array( 'card_front', 'pdp_on_model_front' ) );
    $saved = $GLOBALS['inventory']['assets'][ $path ];
    $duplicate_path = 'assets/v2-original/products/sg-009-duplicate.png';
    $GLOBALS['inventory']['assets'][ $duplicate_path ] = contract_asset( $duplicate_path, 'sg-009', 'signature', $saved['roles'] );
    check( ! skyyrose2_approved_card_front( $parent ), 'Competing masters fail closed' );
    unset( $GLOBALS['inventory']['assets'][ $duplicate_path ] );
    $derived_path = 'assets/derived/card-fronts/sg-009-480w.webp';
    $GLOBALS['inventory']['assets'][ $derived_path ] = contract_asset( $derived_path, 'sg-009', 'signature', $saved['roles'] );
    check( skyyrose2_approved_card_front( $parent )['path'] === $path, 'Rendition is not competing master' );
    unset( $GLOBALS['inventory']['assets'][ $path ] );
    check( ! skyyrose2_approved_card_front( $parent ), 'Derived-only master fails closed' );
    unset( $GLOBALS['inventory']['assets'][ $derived_path ] );
    $GLOBALS['inventory']['assets'][ $path ] = $saved;
    $GLOBALS['attachments'] = array( 901 => 'https://example.test/wp-content/uploads/v1.jpg', 902 => SKYYROSE2_URI . '/assets/v2-original/products/sg-002.png' );
    check( ! skyyrose2_product_commerce_media( $parent )['ids'], 'Wrong-SKU and V1 assigned attachments blocked' );
    $GLOBALS['attachments'][903] = SKYYROSE2_URI . '/' . $path;
    $parent->ids[] = 903;
    check( array( 903 ) === skyyrose2_product_commerce_media( $parent )['ids'], 'Only same-SKU eligible attachment retained' );
    $GLOBALS['files'][903] = $fixture . '/' . $path;
    $delivery = skyyrose2_pdp_media_delivery( $parent, 903 );
    check( $delivery['src'] === skyyrose2_media_uri( $path, 'pdp_on_model_front', 'sg-009' ) && 1 === $delivery['width'], 'Current exact-role bytes deliver valid uncropped dimensions with their cache identity' );
    $GLOBALS['skyyrose2_pdp_media_context'] = skyyrose2_pdp_capture_media_context( $parent );
    $native_attributes = array( 'alt' => 'Native accessibility text', 'data-large_image' => SKYYROSE2_URI . '/' . $path );
    $attributes = skyyrose2_pdp_gallery_attributes( $native_attributes, 903, true, $parent );
    check( $attributes['src'] === $delivery['src'] && $attributes['alt'] === $native_attributes['alt'] && $attributes['data-large_image'] === $native_attributes['data-large_image'], 'Native full-view and accessibility attributes retained' );
    $GLOBALS['files'][903] = 'https://unbound.test/source.png';
    check( ! skyyrose2_pdp_media_delivery( $parent, 903 ), 'Remote local-source proof denied' );
    unset( $GLOBALS['skyyrose2_pdp_media_context'] );
    $schema = skyyrose2_product_commerce_schema_image( array( 'image' => 'v1.jpg', 'price' => 91 ), $parent );
    check( skyyrose2_media_uri( $path, 'pdp_on_model_front', 'sg-009' ) === $schema['image'] && 91 === $schema['price'], 'Schema exact front and cache identity, native facts retained' );
    $size = new WC_Product_Variation( 101, '', $parent->id, array( 'attribute_pa_size' => 'M' ) );
    $distinct = new WC_Product_Variation( 102, 'sg-002', $parent->id, array( 'attribute_pa_size' => 'M' ) );
    $denied = new WC_Product_Variation( 103, '', $parent->id, array( 'attribute_pa_color' => 'blue' ) );
    $unknown = new WC_Product_Variation( 104, 'unknown-color', $parent->id, array( 'attribute_pa_size' => 'M' ) );
    $empty = new WC_Product_Variation( 105, '', $parent->id, array() );
    foreach ( array( $size, $distinct, $denied, $unknown, $empty ) as $variation ) { $GLOBALS['products'][ $variation->id ] = $variation; }
    check( 'sg-009' === skyyrose2_approved_pdp_front( $size )['sku'], 'Explicit size-only variant may use parent SKU' );
    check( 'sg-002' === skyyrose2_approved_pdp_front( $distinct )['sku'], 'Distinct SKU uses its own approved master' );
    foreach ( array( $denied, $unknown, $empty ) as $variation ) { check( ! skyyrose2_approved_pdp_front( $variation ), 'Unproven variation equivalence denied' ); }
    $purchase = array( 'display_price' => 137, 'is_in_stock' => true, 'attributes' => array( 'attribute_pa_size' => 'M' ), 'image' => array( 'src' => 'v1.jpg' ), 'image_id' => 901 );
    $payloads = array();
    foreach ( array( 'size' => $size, 'distinct' => $distinct, 'denied' => $denied, 'unknown' => $unknown ) as $name => $variation ) {
        $payloads[ $name ] = skyyrose2_pdp_variation_delivery( $purchase, $parent, $variation );
        check( $payloads[ $name ]['display_price'] === 137 && $payloads[ $name ]['attributes'] === $purchase['attributes'], 'Native variation purchase fields retained' );
        check( str_contains( $payloads[ $name ]['gallery_images_html'], 'woocommerce-product-gallery ' ) && str_contains( $payloads[ $name ]['gallery_images_html'], ' images"' ), 'Complete native variation gallery root' );
    }
    check( ! $payloads['denied']['image'] && ! str_contains( $payloads['denied']['gallery_images_html'], '<img' ), 'Denied variation carries explicit unavailable gallery' );
    $parent_front = skyyrose2_approved_pdp_front( $parent );
    $native = array( 'default' => skyyrose2_pdp_v2_gallery_markup( $parent_front ), 'empty_default' => skyyrose2_pdp_v2_gallery_markup( array() ), 'payloads' => $payloads );
    foreach ( array( '/wc/store/v1/products', '/wc/store/v1/cart' ) as $route ) {
        $items = array( array( 'id' => $parent->id, 'images' => array( array( 'src' => 'v1.jpg' ) ), 'prices' => array( 'price' => '13700' ) ), array( 'id' => $denied->id, 'images' => array( array( 'src' => 'wrong-parent.jpg' ) ) ) );
        $response = new WP_REST_Response( str_contains( $route, '/cart' ) ? array( 'items' => $items, 'totals' => array( 'total_price' => '13700' ) ) : $items );
        skyyrose2_store_api_v2_images( $response, null, new ContractRequest( $route ) );
        $data = $response->get_data(); $updated = $data['items'] ?? $data;
        check( $updated[0]['images'][0]['src'] === $parent_front['src'] && $updated[0]['prices'] === $items[0]['prices'], 'Store API exact thumb preserves pricing' );
        check( array() === $updated[1]['images'], 'Store API rejects inherited color thumbnail' );
    }
    $response = new WP_REST_Response( array( 'id' => $parent->id, 'images' => array( 'unrelated' ) ) );
    skyyrose2_store_api_v2_images( $response, null, new ContractRequest( '/wc/v3/products' ) );
    check( array( 'unrelated' ) === $response->get_data()['images'], 'Unrelated REST response untouched' );
    if ( in_array( '--native-json', $argv, true ) ) { echo json_encode( $native ); }
    else { echo "PASS all 33 card/PDP/thumbnail SKU bindings, exact-role review, duplicates, variations, schema and Store API isolation (offline contract only)\n"; }
} finally {
    $iterator = new RecursiveIteratorIterator( new RecursiveDirectoryIterator( $fixture, FilesystemIterator::SKIP_DOTS ), RecursiveIteratorIterator::CHILD_FIRST );
    foreach ( $iterator as $entry ) { $entry->isDir() ? rmdir( $entry->getPathname() ) : unlink( $entry->getPathname() ); }
    rmdir( $fixture );
}
