<?php
/** Offline delivery test over actual reviewed masters/copies; creates no visual approval. */
define( 'ABSPATH', __DIR__ );
$theme = dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2';
$fixture = sys_get_temp_dir() . '/v2-delivery-contract-' . bin2hex( random_bytes( 5 ) );
mkdir( $fixture, 0700 );
define( 'SKYYROSE2_DIR', $fixture );
define( 'SKYYROSE2_URI', 'https://example.test/v2' );
function add_filter( ...$args ) {} function add_action( ...$args ) {}
function is_admin() { return false; } function is_product() { return true; } function is_shop() { return false; }
function __( $value, ...$args ) { return $value; }
function esc_attr( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_html( $value ) { return esc_attr( $value ); }
function esc_url( $value ) { return esc_attr( $value ); }
function esc_html__( $value, ...$args ) { return esc_attr( $value ); }
function esc_html_e( $value, ...$args ) { echo esc_attr( $value ); }
function sanitize_title( $value ) { return strtolower( $value ); }
function tag_escape( $value ) { return preg_replace( '/[^a-z0-9]/i', '', $value ); }
function wp_kses_post( $value ) { return $value; }
function wp_strip_all_tags( $value ) { return strip_tags( $value ); }
function wp_trim_words( $value, ...$args ) { return $value; }
function skyyrose2_is_transaction_preorder_product( $product ) { return false; }
function skyyrose2_collections() { return array(); }
function skyyrose2_media_inventory() { return $GLOBALS['inventory']; }
function skyyrose2_product_presentation( $product ) { return $GLOBALS['presentation']['products'][ $product->get_sku( 'edit' ) ] ?? array(); }
function wc_get_product( $id ) { return $GLOBALS['products'][ $id ] ?? null; }
class WC_Product {
	public function __construct( public $sku, public $id ) {}
	public function get_sku( $context = 'view' ) { return $this->sku; }
	public function get_id() { return $this->id; }
	public function get_name() { return $this->sku . ' delivery contract'; }
	public function is_visible() { return true; }
	public function get_permalink() { return 'https://example.test/product/' . $this->id . '/'; }
	public function get_price_html() { return '<span class="amount">$137.00</span>'; }
	public function is_in_stock() { return true; }
	public function get_type() { return 'simple'; }
	public function is_type( $type ) { return 'simple' === $type; }
	public function is_purchasable() { return true; }
	public function get_short_description() { return 'Native commerce fixture copy.'; }
	public function get_image_id() { return 0; }
	public function get_gallery_image_ids() { return array(); }
}
class WC_Product_Variation extends WC_Product {
	public function __construct( public $parent_id ) { parent::__construct( '', 9001 ); }
	public function get_parent_id() { return $this->parent_id; }
	public function get_variation_attributes() { return array( 'attribute_pa_size' => 'M' ); }
}
function verify_copy( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
function fixture_copy( $relative ) {
	global $theme, $fixture;
	$destination = $fixture . '/' . $relative;
	if ( ! is_dir( dirname( $destination ) ) ) { mkdir( dirname( $destination ), 0700, true ); }
	copy( $theme . '/' . $relative, $destination );
}
function fixture_render_card( $args ) {
	global $theme;
	$level = ob_get_level();
	ob_start();
	ob_start( 'skyyrose2_media_filter_html' );
	try { include $theme . '/template-parts/commerce/product-card.php'; ob_end_flush(); return ob_get_clean(); }
	finally { while ( ob_get_level() > $level ) { ob_end_clean(); } }
}
$actual_inventory = json_decode( file_get_contents( $theme . '/data/v2-media-eligibility.json' ), true );
$GLOBALS['inventory'] = array( 'assets' => array(), 'disallowed_legacy_sha256' => $actual_inventory['disallowed_legacy_sha256'] );
$GLOBALS['presentation'] = json_decode( file_get_contents( $theme . '/data/product-presentation-registry.json' ), true );
$manifest_path = 'assets/derived/card-fronts/manifest.json';
fixture_copy( $manifest_path );
fixture_copy( 'data/approved-card-fronts.json' );
$manifest_bytes = file_get_contents( $fixture . '/' . $manifest_path );
$manifest = json_decode( $manifest_bytes, true );
$manifest_hash = hash( 'sha256', $manifest_bytes );
$derivatives = array();
foreach ( $manifest['products'] as $sku => $entry ) {
	$master = $actual_inventory['assets'][ $entry['source'] ] ?? null;
	verify_copy( is_array( $master ) && in_array( $master['status'], array( 'INDEPENDENT_VISUAL_PASS', 'FOUNDER_ACCEPTED' ), true ), 'Test requires an actual independently reviewed master' );
	fixture_copy( $entry['source'] ); fixture_copy( $master['review']['path'] );
    if ( 'FOUNDER_ACCEPTED' === $master['status'] ) {
        $owner = json_decode( file_get_contents( $theme . '/' . $master['review']['path'] ), true );
        fixture_copy( $owner['decision_source']['path'] );
    }
	$GLOBALS['inventory']['assets'][ $entry['source'] ] = $master;
	$id = count( $GLOBALS['products'] ?? array() ) + 1;
	$GLOBALS['products'][ $id ] = new WC_Product( $sku, $id );
	foreach ( $entry['renditions'] as $rendition ) {
		fixture_copy( $rendition['src'] );
		$record = array( 'kind' => 'photograph', 'status' => 'DELIVERY_DERIVATIVE', 'origin' => $master['origin'], 'sha256' => $rendition['sha256'], 'source_path' => $entry['source'], 'source_sha256' => $entry['source_sha256'], 'roles' => $master['roles'], 'skus' => $master['skus'], 'collections' => $master['collections'], 'width' => $rendition['width'], 'height' => $rendition['height'], 'delivery_manifest' => array( 'path' => $manifest_path, 'sha256' => $manifest_hash ) );
		$GLOBALS['inventory']['assets'][ $rendition['src'] ] = $record;
		$derivatives[ $rendition['src'] ] = $record;
	}
}
$source = file_get_contents( $theme . '/inc/v2-media-eligibility.php' );
$start = strpos( $source, '/** Validate immutable bytes' );
$end = strpos( $source, 'function skyyrose2_media_start_buffer()', $start );
eval( substr( $source, $start, $end - $start ) );
require $theme . '/inc/approved-card-fronts.php';
require $theme . '/inc/pdp-media-delivery.php';
try {
	verify_copy( count( $derivatives ) >= 6, 'Actual reviewed masters provide delivery copies and distinct SKU families' );
	foreach ( $derivatives as $path => $record ) {
		foreach ( $record['roles'] as $role ) { verify_copy( skyyrose2_media_path_allowed( $path, $role, $record['skus'][0] ), 'Actual reviewed-master derivative must deliver for each inherited role' ); }
	}
	foreach ( $GLOBALS['products'] as $product ) {
		$front = skyyrose2_approved_card_front( $product );
		verify_copy( str_ends_with( parse_url( $front['card_src'] ?? '', PHP_URL_PATH ) ?? '', '-' . 480 . 'w.webp' ) && 480 === $front['card_width'], 'Approved master resolves its bounded WebP card copy' );
		parse_str( parse_url( $front['card_src'], PHP_URL_QUERY ) ?? '', $cache_version );
		$card_path = 'assets/derived/card-fronts/' . $product->sku . '-480w.webp';
		verify_copy( ( $cache_version['v'] ?? '' ) === $GLOBALS['inventory']['assets'][ $card_path ]['sha256'], 'Responsive card cache version matches its own derivative bytes' );
		$card_html = fixture_render_card( array( 'product' => $product, 'frame' => false ) );
		verify_copy( str_contains( $card_html, 'src="' . $front['card_src'] . '"' ) && str_contains( $card_html, 'srcset="' ) && preg_match( '/-320w\.webp\?v=[a-f0-9]{64} 320w/', $card_html ) && preg_match( '/-768w\.webp\?v=[a-f0-9]{64} 768w/', $card_html ), 'Actual output-buffer final flush preserves real card WebP responsive delivery' );
		verify_copy( str_contains( $card_html, '$137.00' ) && str_contains( $card_html, 'Native commerce fixture copy.' ), 'Delivery preserves native price and product copy' );
		$pdp_front = skyyrose2_approved_pdp_front( $product );
		if ( ! $pdp_front ) {
            verify_copy( ! in_array( 'pdp_on_model_front', $front['roles'], true ), 'Card acceptance cannot broaden to PDP or variation gallery' );
            continue;
        }
        $pdp_html = skyyrose2_media_filter_html( skyyrose2_pdp_v2_gallery_markup( $pdp_front ) );
		verify_copy( str_contains( $pdp_html, 'srcset="' ) && preg_match( '/-480w\.webp\?v=[a-f0-9]{64} 480w/', $pdp_html ) && str_contains( $pdp_html, 'data-large_image="' . $pdp_front['src'] . '"' ), 'Final filtered real PDP keeps responsive copies and original full view' );
		$variation = new WC_Product_Variation( $product->id );
		$data = skyyrose2_pdp_variation_delivery( array( 'display_price' => 137, 'is_in_stock' => true ), $product, $variation );
		$data = skyyrose2_media_variation( $data, $product, $variation );
		verify_copy( preg_match( '/-320w\.webp\?v=[a-f0-9]{64} 320w/', $data['image']['srcset'] ) && str_contains( $data['gallery_images_html'], 'srcset="' ) && $pdp_front['src'] === $data['image']['full_src'] && 137 === $data['display_price'], 'Final variation JSON and gallery retain responsive family, original and purchase truth' );
		$link = skyyrose2_media_filter_html( '<link rel="preload" as="image" href="' . $front['src'] . '" imagesrcset="' . esc_attr( $front['srcset'] ) . '">' );
		verify_copy( str_contains( $link, 'imagesrcset="' ), 'Final image preload preserves eligible responsive family' );
	}
	$path = array_key_first( $derivatives ); $good = $derivatives[ $path ];
	foreach ( array( 'source-hash', 'self', 'chain', 'missing-source', 'roles', 'sku', 'collection', 'dimensions', 'scalar-width', 'manifest-hash', 'own-review', 'fake-visual-pass' ) as $case ) {
		$bad = $good;
		if ( 'source-hash' === $case ) { $bad['source_sha256'] = str_repeat( '0', 64 ); }
		if ( 'self' === $case ) { $bad['source_path'] = $path; }
		if ( 'chain' === $case ) { $bad['source_path'] = array_keys( $derivatives )[1]; }
		if ( 'missing-source' === $case ) { $bad['source_path'] = 'assets/test/missing.png'; }
		if ( 'roles' === $case ) { $bad['roles'][] = 'invented_context'; }
		if ( 'sku' === $case ) { $bad['skus'] = array( 'sg-009' ); }
		if ( 'collection' === $case ) { $bad['collections'] = array( 'love-hurts' ); }
		if ( 'dimensions' === $case ) { ++$bad['height']; }
		if ( 'scalar-width' === $case ) { $bad['width'] = (string) $bad['width']; }
		if ( 'manifest-hash' === $case ) { $bad['delivery_manifest']['sha256'] = str_repeat( '0', 64 ); }
		if ( 'own-review' === $case ) { $bad['review'] = array( 'verdict' => 'PASS' ); }
		if ( 'fake-visual-pass' === $case ) { $bad['status'] = 'INDEPENDENT_VISUAL_PASS'; }
		verify_copy( ! skyyrose2_media_record_allowed( $path, $bad ), 'Reject derivative ' . $case );
	}
	foreach ( array( 'source', 'source-review', 'encoding-builder', 'encoding-version', 'crop', 'upscale', 'manifest-collection', 'duplicate-rendition' ) as $case ) {
		$changed = $manifest; $owner = $good['skus'][0];
		if ( 'source' === $case ) { $changed['products'][ $owner ]['source_sha256'] = str_repeat( '0', 64 ); }
		if ( 'source-review' === $case ) { $changed['products'][ $owner ]['source_review']['sha256'] = str_repeat( '0', 64 ); }
		if ( 'encoding-builder' === $case ) { $changed['products'][ $owner ]['encoding']['builder_sha256'] = str_repeat( '0', 64 ); }
		if ( 'encoding-version' === $case ) { $changed['products'][ $owner ]['encoding']['pillow_version'] = 'unqualified'; }
		if ( 'crop' === $case ) { $changed['products'][ $owner ]['encoding']['crop'] = true; }
		if ( 'upscale' === $case ) { $changed['products'][ $owner ]['encoding']['upscale'] = true; }
		if ( 'manifest-collection' === $case ) { $changed['products'][ $owner ]['collections'] = array( 'love-hurts' ); }
		if ( 'duplicate-rendition' === $case ) { $changed['products'][ $owner ]['renditions'][] = $changed['products'][ $owner ]['renditions'][0]; }
		file_put_contents( $fixture . '/' . $manifest_path, json_encode( $changed ) );
		$bad = $good; $bad['delivery_manifest']['sha256'] = hash_file( 'sha256', $fixture . '/' . $manifest_path );
		verify_copy( ! skyyrose2_media_record_allowed( $path, $bad ), 'Reject rehashed manifest ' . $case );
	}
	file_put_contents( $fixture . '/' . $manifest_path, $manifest_bytes );
	$master_path = $good['source_path']; $master = $GLOBALS['inventory']['assets'][ $master_path ];
	$moved = 'assets/test/moved-copy.webp';
	mkdir( $fixture . '/assets/test', 0700, true ); copy( $fixture . '/' . $path, $fixture . '/' . $moved );
	$GLOBALS['inventory']['assets'][ $moved ] = $good;
	$bad = $good; $bad['source_path'] = $moved; $bad['source_sha256'] = $good['sha256'];
	verify_copy( ! skyyrose2_media_record_allowed( $path, $bad ), 'Moving a derivative cannot establish an original master or chain' );
	unset( $GLOBALS['inventory']['assets'][ $moved ] );
	$GLOBALS['inventory']['assets'][ $master_path ]['status'] = 'REVISE';
	verify_copy( ! skyyrose2_media_record_allowed( $path, $good ), 'Master review downgrade immediately removes derivative delivery' );
	$GLOBALS['inventory']['assets'][ $master_path ] = $master;
	$bytes = file_get_contents( $fixture . '/' . $path );
	copy( $fixture . '/' . $master_path, $fixture . '/' . $path );
	$bad = $good; $bad['sha256'] = hash_file( 'sha256', $fixture . '/' . $path );
	$changed = $manifest; $changed['products'][ $good['skus'][0] ]['renditions'][0]['sha256'] = $bad['sha256'];
	file_put_contents( $fixture . '/' . $manifest_path, json_encode( $changed ) );
	$bad['delivery_manifest']['sha256'] = hash_file( 'sha256', $fixture . '/' . $manifest_path );
	verify_copy( ! skyyrose2_media_record_allowed( $path, $bad ), 'A rehashed PNG cannot masquerade as a WebP delivery copy' );
	file_put_contents( $fixture . '/' . $manifest_path, $manifest_bytes ); file_put_contents( $fixture . '/' . $path, $bytes );
	file_put_contents( $fixture . '/' . $path, $bytes . 'drift' );
	verify_copy( ! skyyrose2_media_path_allowed( $path ), 'Actual derivative-byte drift blocks delivery' );
	file_put_contents( $fixture . '/' . $path, $bytes );
	unlink( $fixture . '/' . $path ); symlink( $fixture . '/' . $master_path, $fixture . '/' . $path );
	verify_copy( ! skyyrose2_media_path_allowed( $path ), 'Symlink derivative blocks delivery' );
	unlink( $fixture . '/' . $path ); file_put_contents( $fixture . '/' . $path, $bytes );
	$other = array_values( array_filter( array_keys( $derivatives ), static fn( $candidate ) => $derivatives[ $candidate ]['skus'] !== $good['skus'] ) )[0];
	$primary = SKYYROSE2_URI . '/' . $path;
	$mixed = $primary . ' ' . $good['width'] . 'w, ' . SKYYROSE2_URI . '/' . $other . ' 320w, https://old.test/v1.webp 320w, ' . $primary . ' 0w, ' . $primary . ' 480x';
	$filtered = skyyrose2_media_filter_html( '<img src="' . $primary . '" srcset="' . $mixed . '" data-srcset="' . $mixed . '">' );
	verify_copy( str_contains( $filtered, 'srcset="' . skyyrose2_media_uri( $path ) . ' ' . $good['width'] . 'w"' ) && ! str_contains( $filtered, $other ) && ! str_contains( $filtered, 'old.test' ) && ! str_contains( $filtered, '480x' ), 'Final HTML rejects cross-SKU, legacy and malformed responsive candidates' );
	$withheld = skyyrose2_media_filter_html( '<div><img src="https://old.test/v1.webp" alt="Legacy scene" srcset="' . $primary . ' ' . $good['width'] . 'w"><span>Collection story</span></div>' );
	verify_copy( '<div><span>Collection story</span></div>' === $withheld, 'Withheld imagery leaves no broken image or misleading alt label while preserving surrounding content' );
	verify_copy( '' === skyyrose2_media_filter_html( '<img alt="Unbound image">' ), 'A source-less image cannot enter final storefront HTML' );
	$sources = array( $good['width'] => array( 'url' => $primary, 'descriptor' => 'w', 'value' => $good['width'] ), 481 => array( 'url' => $primary, 'descriptor' => 'w', 'value' => 481 ), 999 => array( 'url' => SKYYROSE2_URI . '/' . $other, 'descriptor' => 'w', 'value' => 320 ) );
	verify_copy( array_keys( skyyrose2_media_srcset( $sources, array( 320, 480 ), $primary ) ) === array( $good['width'] ), 'Native WP srcset descriptors and family are independently checked' );
	$normalized_sources = skyyrose2_media_srcset( $sources, array( 320, 480 ), $primary );
	verify_copy( $normalized_sources[ $good['width'] ]['url'] === skyyrose2_media_uri( $path ), 'Native WP srcset URLs normalize to exact byte cache identity' );
	$owner_product = array_values( array_filter( $GLOBALS['products'], static fn( $product ) => $product->sku === $good['skus'][0] ) )[0];
	$variation = new WC_Product_Variation( $owner_product->id );
	$data = skyyrose2_pdp_variation_delivery( array( 'display_price' => 137 ), $owner_product, $variation );
	$data['gallery_images_html'] .= '<img src="' . SKYYROSE2_URI . '/' . $other . '" srcset="' . SKYYROSE2_URI . '/' . $other . ' 320w">';
	$clean = skyyrose2_media_variation( $data, $owner_product, $variation );
	verify_copy( ! str_contains( $clean['gallery_images_html'], $other ) && ! empty( $clean['image']['srcset'] ), 'Variation gallery cannot inject a different approved SKU family' );
	$data['image']['src'] = SKYYROSE2_URI . '/' . $other;
	$clean = skyyrose2_media_variation( $data, $owner_product, $variation );
	verify_copy( ! $clean['image'] && ! str_contains( $clean['gallery_images_html'], '<img' ) && 137 === $clean['display_price'], 'Wrong approved SKU primary fails to an explicit unavailable gallery without changing price' );
	echo 'PASS ' . count( $derivatives ) . " actual delivery copies: original review inheritance, source/encoding/manifest/byte/dimension bounds; final real card/PDP/variation/preload responsive families; malformed/cross-SKU negatives (offline only)\n";
} finally {
	$iterator = new RecursiveIteratorIterator( new RecursiveDirectoryIterator( $fixture, FilesystemIterator::SKIP_DOTS ), RecursiveIteratorIterator::CHILD_FIRST );
	foreach ( $iterator as $entry ) { $entry->isDir() && ! $entry->isLink() ? rmdir( $entry->getPathname() ) : unlink( $entry->getPathname() ); }
	rmdir( $fixture );
}
