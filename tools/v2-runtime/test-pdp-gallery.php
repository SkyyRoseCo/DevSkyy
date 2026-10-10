<?php
/**
 * Native template-boundary regression with real WP hooks and Woo templates/helpers.
 * Attachment/data-store adapters are in-memory; no WordPress database is loaded.
 */
namespace Automattic\WooCommerce\Internal\ProductGallery {
	class ProductMediaGallery {
		public static function get_product_media_gallery_items_for_display( $product ) {
			// Model Woo 11.1's independent positioned-video metadata channel.
			if ( \get_post_meta($product->get_id(), '_wc_video_gallery', true) ) {
				throw new \RuntimeException('Unpermitted native video entered the image-only gallery.');
			}
			return array_map( static fn($id) => array('id' => $id, 'media_type' => 'image', 'source_type' => 'attachment'), array_values(array_filter(array_merge(array($product->get_image_id()), $product->get_gallery_image_ids()))));
		}
	}
}
namespace {
define('ABSPATH', __DIR__);
define('SKYYROSE2_DIR', realpath(__DIR__ . '/../../wordpress-theme/skyyrose-flagship-2'));
define('SKYYROSE2_URI', 'https://theme.invalid');
$fixture_path = getenv('V2_WP_FIXTURE');
$wp = realpath(false !== $fixture_path && '' !== $fixture_path ? $fixture_path : __DIR__ . '/../../.artifacts/v2-phase3-20260905/wordpress');
if (!$wp) { throw new \RuntimeException('UNVERIFIED: set V2_WP_FIXTURE to the pinned WordPress 7.1 / WooCommerce 11.1.0 fixture root.'); }
// Validate every native dependency before requiring or evaluating any fixture code.
$pins = json_decode(file_get_contents(__DIR__ . '/fixtures/pdp-native-template-hashes.json'), true, 512, JSON_THROW_ON_ERROR);
$required_native_files = array(
	'wp-includes/plugin.php',
	'wp-includes/class-wp-hook.php',
	'wp-includes/class-wp-filter-sentinel.php',
	'wp-content/plugins/woocommerce/includes/wc-template-functions.php',
	'wp-content/plugins/woocommerce/templates/single-product/product-image.php',
	'wp-content/plugins/woocommerce/templates/single-product/product-thumbnails.php',
	'wp-content/plugins/woocommerce/templates/single-product/add-to-cart/variable.php',
);
$pinned_native_files = array_keys($pins['files'] ?? array());
sort($required_native_files);
sort($pinned_native_files);
if ('skyyrose.pdp-native-template-hashes.v1' !== ($pins['schema'] ?? '') || $required_native_files !== $pinned_native_files) {
	throw new \RuntimeException('UNVERIFIED: incomplete or incompatible native gallery fixture manifest.');
}
foreach ($required_native_files as $relative) {
	$native_file = realpath($wp . '/' . $relative);
	$expected = $pins['files'][$relative];
	if (!$native_file || !str_starts_with($native_file, $wp . DIRECTORY_SEPARATOR) || !is_file($native_file) || !is_readable($native_file) || !is_string($expected) || !preg_match('/^[a-f0-9]{64}$/D', $expected) || hash_file('sha256', $native_file) !== $expected) {
		throw new \RuntimeException('UNVERIFIED: native gallery fixture SHA-256 mismatch or missing file: ' . $relative);
	}
}
$GLOBALS['woo_path'] = $wp . '/wp-content/plugins/woocommerce';
require $wp . '/wp-includes/plugin.php';
$GLOBALS['is_product'] = true;
$GLOBALS['ajax'] = false;
$GLOBALS['files'] = array();
$GLOBALS['attachment_urls'] = array();
$GLOBALS['permission_calls'] = 0;
class WC_Product {
	public function __construct(public int $id, public string $sku, public int $image, public array $gallery = array(), public string $state = 'commerce') {}
	public function get_id() { return $this->id; }
	public function get_sku() { return $this->sku; }
	public function get_image_id() { return apply_filters('woocommerce_product_get_image_id', $this->image, $this); }
	public function get_gallery_image_ids() { return apply_filters('woocommerce_product_get_gallery_image_ids', $this->gallery, $this); }
	public function get_title() { return $this->sku; }
}
class WC_Product_Variation extends WC_Product {
	public function get_parent_id() { return 101; }
}
function WC() { return new class { public function plugin_path() { return $GLOBALS['woo_path']; } }; }
function is_product() { return $GLOBALS['is_product']; }
function wp_doing_ajax() { return $GLOBALS['ajax']; }
function skyyrose2_product_commerce_media($product) {
	++$GLOBALS['permission_calls'];
	return array('state' => $product->state, 'ids' => $product->state === 'rejected' ? array() : array_values(array_filter(array_merge(array($product->get_image_id()), $product->get_gallery_image_ids()))));
}
function get_attached_file($id, $unfiltered) { return $GLOBALS['files'][$id] ?? false; }
function absint($value) { return abs((int)$value); }
function get_theme_support($feature) { return true; }
function wc_get_image_size($size) { return array('width' => 100, 'height' => 100); }
function wp_get_attachment_image_src($id, $size) { return array('https://uploads.invalid/' . $id . (is_array($size) ? '-thumb' : '-full') . '.webp', 1024, 1536); }
function wp_get_attachment_image_srcset($id, $size) { return ''; }
function wp_get_attachment_image_sizes($id, $size) { return '100px'; }
function get_post_meta($id, $key, $single) {
	$value = apply_filters('get_post_metadata', null, $id, $key, $single);
	if (null !== $value) { return $single && is_array($value) ? $value[0] : $value; }
	return '_wc_video_gallery' === $key ? array(array('id' => 999, 'media_type' => 'video')) : 'Native alt';
}
function get_post_field($key, $id) { return ''; }
function wp_strip_all_tags($text) { return strip_tags($text); }
function _wp_specialchars($text, ...$args) { return htmlspecialchars($text, ENT_QUOTES); }
function esc_url($text) { return htmlspecialchars($text, ENT_QUOTES); }
function esc_attr($text) { return htmlspecialchars((string)$text, ENT_QUOTES); }
function sanitize_key($text) { return strtolower(preg_replace('/[^a-z0-9_\\-]/', '', (string)$text)); }
function wp_get_attachment_url($id) { return $GLOBALS['attachment_urls'][$id] ?? false; }
function sanitize_html_class($text) { return preg_replace('/[^a-zA-Z0-9_-]/', '', $text); }
function wp_get_attachment_image($id, $size, $icon, $attrs) {
	$attrs = array_merge(array('src' => 'https://uploads.invalid/' . $id . '-full.webp', 'data-test-attachment' => $id), $attrs);
	return '<img ' . implode(' ', array_map(static fn($key) => $key . '="' . esc_attr($attrs[$key]) . '"', array_keys($attrs))) . '>';
}
function wc_get_template_html($name) {
	ob_start();
	try { require SKYYROSE2_DIR . '/woocommerce/' . $name; return ob_get_contents(); }
	finally { ob_end_clean(); }
}
function check_gallery($condition, $message) { if (!$condition) { throw new \RuntimeException($message); } }
$source = file_get_contents($GLOBALS['woo_path'] . '/includes/wc-template-functions.php');
$start = strpos($source, 'function wc_get_gallery_image_html(');
$end = strpos($source, "if ( ! function_exists( 'woocommerce_get_alt_from_product_title_and_position'", $start);
check_gallery(false !== $start && false !== $end, 'Native gallery helper boundary was not found.');
eval(substr($source, $start, $end - $start));
require SKYYROSE2_DIR . '/inc/approved-card-fronts.php';
require SKYYROSE2_DIR . '/inc/pdp-media-delivery.php';
add_action('woocommerce_product_thumbnails', static function () { require $GLOBALS['woo_path'] . '/templates/single-product/product-thumbnails.php'; });
$manifest = json_decode(file_get_contents(SKYYROSE2_DIR . '/data/approved-card-fronts.json'), true);
check_gallery( 33 === count( $manifest['products'] ?? array() ), 'The approved-front manifest must retain all 33 product bindings.' );
foreach ( $manifest['products'] as $approved_sku => $approved_record ) {
	$approved_product = new WC_Product( 800 + count( $GLOBALS['files'] ), $approved_sku, 800 + count( $GLOBALS['files'] ) );
	$approved_front = skyyrose2_approved_card_front( $approved_product );
	check_gallery( 'FOUNDER_APPROVED_V2_CARD' === ( $approved_front['scene_status'] ?? '' ) && str_ends_with( strtolower( $approved_front['alt'] ?? '' ), 'front on model' ), 'Every published SKU must resolve its founder-approved on-model front: ' . $approved_sku . '.' );
	check_gallery( ( $approved_record['sha256'] ?? '' ) === ( $approved_front['sha256'] ?? '' ), 'Approved-front source hash must stay bound for ' . $approved_sku . '.' );
}
$GLOBALS['files'][77] = SKYYROSE2_DIR . '/' . $manifest['products']['sg-005']['src'];
$parent = new WC_Product(101, 'sg-005', 77, array(78));
$variation = new WC_Product_Variation(201, 'sg-005-m', 77, array(78));
$GLOBALS['product'] = 'previous-global';
$GLOBALS['skyyrose2_pdp_media_context'] = skyyrose2_pdp_capture_media_context($parent);
$permission_calls = $GLOBALS['permission_calls'];
$default = wc_get_product_gallery_html($parent);
check_gallery(str_contains($default, 'sg-005-480w.webp'), 'Native default HTML must use same-source delivery.');
check_gallery(str_contains($default, 'href="https://uploads.invalid/77-full.webp"') && str_contains($default, 'data-thumb="https://uploads.invalid/77-thumb.webp"'), 'Original lightbox and thumbnail references must remain native.');
check_gallery($GLOBALS['product'] === 'previous-global', 'Native product global was not restored.');
$ordered = wc_get_product_gallery_html($parent, array(78, 999, 77));
check_gallery(!str_contains($ordered, '999-') && strpos($ordered, 'data-test-attachment="78"') < strpos($ordered, 'data-test-attachment="77"'), 'Variation candidate intersection must preserve permitted order and exclude injected ID.');
check_gallery($GLOBALS['permission_calls'] === $permission_calls, 'Permission was recomputed while native getter overrides were active.');
check_gallery($parent->get_image_id() === 77 && $parent->get_gallery_image_ids() === array(78), 'Native and wrapper getter overrides leaked.');
check_gallery($default === wc_get_product_gallery_html($parent), 'Repeated reset/default snapshot differs after variation rendering.');
check_gallery('' === wc_get_product_gallery_html($parent, array(999)), 'No permitted candidates must render no gallery.');

// Ghost primary images may be replaced only by the exact SKU's integrity-checked,
// founder-approved model front. The native gallery keeps its remaining views.
$ghost_cases = array( 'br-002', 'br-005', 'kids-002', 'lh-003', 'sg-014' );
$ghost_id = 300;
foreach ( $ghost_cases as $ghost_sku ) {
	$ghost_product = new WC_Product( $ghost_id, $ghost_sku, $ghost_id, array( 78 ) );
	$GLOBALS['attachment_urls'][ $ghost_id ] = 'https://uploads.invalid/' . $ghost_sku . '-ghost-front.webp';
	$approved_html = skyyrose2_pdp_approved_ghost_front_html( '<div>ghost</div>', $ghost_id, $ghost_product );
	$approved_front = skyyrose2_approved_card_front( $ghost_product );
	check_gallery( $approved_front && str_contains( $approved_html, $approved_front['src'] ) && str_contains( $approved_html, esc_attr( $approved_front['alt'] ) ), 'Ghost primary must render the exact approved model front for ' . $ghost_sku . '.' );
	$approved_pdp_sizes = skyyrose2_pdp_gallery_sizes( $approved_front['width'], $approved_front['height'] );
	check_gallery( str_contains( $approved_html, 'data-large_image="' . $approved_front['src'] . '"' ) && str_contains( $approved_html, 'sizes="' . $approved_pdp_sizes . '"' ), 'Approved PDP front must keep zoom and responsive sources for ' . $ghost_sku . '.' );
	$previous_context = $GLOBALS['skyyrose2_pdp_media_context'] ?? null;
	$GLOBALS['skyyrose2_pdp_media_context'] = skyyrose2_pdp_capture_media_context( $ghost_product );
	$primary_done = false;
	$primary_filter = static function ( $html, $id ) use ( &$primary_done, $ghost_product ) {
		if ( $primary_done ) { return $html; }
		$replacement = skyyrose2_pdp_approved_ghost_front_html( $html, $id, $ghost_product );
		if ( $replacement !== $html ) { $primary_done = true; }
		return $replacement;
	};
	add_filter( 'woocommerce_single_product_image_thumbnail_html', $primary_filter, 30, 2 );
	$gallery_html = wc_get_product_gallery_html( $ghost_product );
	remove_filter( 'woocommerce_single_product_image_thumbnail_html', $primary_filter, 30 );
	check_gallery( $primary_done && str_contains( $gallery_html, $approved_front['src'] ) && ! str_contains( $gallery_html, 'ghost-front.webp' ), 'Native PDP gallery must lead with the approved front and omit the ghost for ' . $ghost_sku . '.' );
	check_gallery( str_contains( $gallery_html, 'data-test-attachment="78"' ), 'Native gallery must retain non-primary views for ' . $ghost_sku . '.' );
	if ( null === $previous_context ) { unset( $GLOBALS['skyyrose2_pdp_media_context'] ); } else { $GLOBALS['skyyrose2_pdp_media_context'] = $previous_context; }
	check_gallery( '<div>ghost</div>' === skyyrose2_pdp_approved_ghost_front_html( '<div>ghost</div>', 999, $ghost_product ), 'A non-primary attachment must not be replaced for ' . $ghost_sku . '.' );
	$GLOBALS['attachment_urls'][ $ghost_id ] = 'https://uploads.invalid/' . $ghost_sku . '-onmodel.webp';
	check_gallery( '<div>ghost</div>' === skyyrose2_pdp_approved_ghost_front_html( '<div>ghost</div>', $ghost_id, $ghost_product ), 'A non-ghost primary must remain untouched for ' . $ghost_sku . '.' );
	++$ghost_id;
}
$wrong_sku = new WC_Product( 400, 'br-005', 400 );
$GLOBALS['attachment_urls'][400] = 'https://uploads.invalid/br-002-ghost-front.webp';
check_gallery( '<div>ghost</div>' === skyyrose2_pdp_approved_ghost_front_html( '<div>ghost</div>', 400, $wrong_sku ), 'A ghost image from another SKU must remain untouched.' );

// The resolver can select an editorial order different from raw assignments.
// Default/reset must honor that canonical order without rewriting a variation.
$original_context = $GLOBALS['skyyrose2_pdp_media_context'];
$GLOBALS['skyyrose2_pdp_media_context']['media'] = array('state' => 'editorial', 'ids' => array(78, 77));
$editorial_default = wc_get_product_gallery_html($parent);
check_gallery(strpos($editorial_default, 'data-test-attachment="78"') < strpos($editorial_default, 'data-test-attachment="77"'), 'Default raw [77,78] must render canonical editorial [78,77].');
$editorial_variation = wc_get_product_gallery_html($parent, array(77));
check_gallery(str_contains($editorial_variation, 'data-test-attachment="77"') && !str_contains($editorial_variation, 'data-test-attachment="78"'), 'An explicit permitted variation [77] must not be replaced by the editorial default.');
check_gallery($GLOBALS['permission_calls'] === $permission_calls, 'Editorial mapping must not resolve authority under overrides.');
$GLOBALS['skyyrose2_pdp_media_context'] = $original_context;

// Test the actual default-cache expression and the embedded-template gallery
// expression, without evaluating native purchase controls or changing commerce.
check_gallery(str_contains($source, 'wp_json_encode( wc_get_product_gallery_html( $product ) )'), 'Installed inline-default call path changed.');
$variable_template = file_get_contents($GLOBALS['woo_path'] . '/templates/single-product/add-to-cart/variable.php');
check_gallery(str_contains($variable_template, 'wc_get_product_gallery_html( $product )'), 'Installed embedded-default call path changed.');
$inline_default = json_decode(json_encode(wc_get_product_gallery_html($parent)), true);
$embedded_default = wc_get_product_gallery_html($parent);
check_gallery($inline_default === $default && $embedded_default === $default, 'Reset representations must use the same native template boundary.');

$thrower = static function () { throw new \RuntimeException('native gallery hook failure'); };
add_action('woocommerce_product_thumbnails', $thrower, 5);
try { wc_get_product_gallery_html($parent, array(78)); throw new \RuntimeException('Expected native exception.'); }
catch (\RuntimeException $error) { check_gallery($error->getMessage() === 'native gallery hook failure', 'Native error must propagate.'); }
remove_action('woocommerce_product_thumbnails', $thrower, 5);
check_gallery($parent->get_image_id() === 77 && $parent->get_gallery_image_ids() === array(78), 'Exception leaked temporary getters.');
check_gallery(!has_filter('woocommerce_gallery_image_html_attachment_image_params'), 'Exception leaked delivery attributes.');
check_gallery(!has_filter('get_post_metadata') && !has_filter('woocommerce_product_get__wc_video_gallery'), 'Exception leaked video metadata filters.');
check_gallery(get_post_meta(101, '_wc_video_gallery', true)[0]['id'] === 999, 'Native video data was mutated outside its render boundary.');
check_gallery($GLOBALS['product'] === 'previous-global', 'Exception leaked native product global.');

$rejected = new WC_Product(102, 'br-003', 79, array(), 'rejected');
$GLOBALS['skyyrose2_pdp_media_context'] = skyyrose2_pdp_capture_media_context($rejected);
check_gallery('' === wc_get_product_gallery_html($rejected) && '' === wc_get_product_gallery_html($rejected, array(77)), 'Rejected default and variation galleries must stay empty.');
unset($GLOBALS['skyyrose2_pdp_media_context']);
$GLOBALS['is_product'] = false;
$GLOBALS['ajax'] = true;
$_REQUEST['wc-ajax'] = 'get_variation';
check_gallery('' === wc_get_product_gallery_html($parent, array(999, 77)), 'AJAX intermediate render must not infer permission from overridden IDs.');
$data = array('image_id' => 77, 'image' => array('src' => 'original', 'full_src' => 'full', 'gallery_thumbnail_src' => 'thumb'), 'gallery_image_ids' => array(78,999), 'gallery_images_html' => 'untrusted intermediate');
$result = skyyrose2_pdp_variation_delivery($data, $parent, $variation);
check_gallery(str_contains($result['gallery_images_html'], 'sg-005-480w.webp') && !str_contains($result['gallery_images_html'], '999-'), 'AJAX gallery must be regenerated through the guarded native template.');
check_gallery($result['gallery_image_ids'] === array(78) && $result['image_id'] === 77 && $result['image']['full_src'] === 'full', 'AJAX identity/order/full metadata changed incorrectly.');
check_gallery(!isset($GLOBALS['skyyrose2_pdp_media_context']), 'AJAX context leaked.');
add_action('woocommerce_product_thumbnails', $thrower, 5);
try { skyyrose2_pdp_variation_delivery($data, $parent, $variation); throw new \RuntimeException('Expected AJAX exception.'); }
catch (\RuntimeException $error) { check_gallery($error->getMessage() === 'native gallery hook failure', 'AJAX native error must propagate.'); }
remove_action('woocommerce_product_thumbnails', $thrower, 5);
check_gallery(!isset($GLOBALS['skyyrose2_pdp_media_context']) && $parent->get_image_id() === 77 && $GLOBALS['product'] === 'previous-global', 'AJAX exception must restore context, getters and global product.');

// Native variation JSON and reset must retain the same approved primary.
$_REQUEST['wc-ajax'] = 'get_variation';
$ghost_variation_parent = new WC_Product(101, 'br-002', 501, array(78));
$ghost_variation = new WC_Product_Variation(201, 'br-002-m', 501, array(78));
$GLOBALS['attachment_urls'][501] = 'https://uploads.invalid/br-002-ghost-front.webp';
$GLOBALS['skyyrose2_pdp_media_context'] = skyyrose2_pdp_capture_media_context($ghost_variation_parent);
$GLOBALS['is_product'] = true;
$ghost_front = skyyrose2_approved_card_front($ghost_variation_parent);
$variation_payload = array(
	'image_id' => 501,
	'image' => array( 'src' => 'ghost-small', 'src_w' => 600, 'src_h' => 600, 'full_src' => 'ghost-full', 'full_src_w' => 1024, 'full_src_h' => 1024, 'gallery_thumbnail_src' => 'ghost-thumb', 'gallery_thumbnail_src_w' => 100, 'gallery_thumbnail_src_h' => 100, 'thumb_src' => 'ghost-thumb', 'thumb_src_w' => 100, 'thumb_src_h' => 100, 'alt' => 'ghost' ),
	'gallery_image_ids' => array(78),
	'gallery_images_html' => 'untrusted ghost variation markup',
	'price' => '$40.00',
);
$approved_variation_payload = skyyrose2_pdp_variation_delivery($variation_payload, $ghost_variation_parent, $ghost_variation);
check_gallery($approved_variation_payload['image_id'] === 501 && $approved_variation_payload['image']['src'] === $ghost_front['card_src'] && $approved_variation_payload['image']['full_src'] === $ghost_front['src'] && $approved_variation_payload['image']['sizes'] === skyyrose2_pdp_gallery_sizes($ghost_front['width'], $ghost_front['height']), 'Selected variation must expose approved responsive front and full-view image data.');
check_gallery(!str_contains($approved_variation_payload['image']['src'], 'ghost') && !str_contains($approved_variation_payload['gallery_images_html'], 'ghost-front.webp') && str_contains($approved_variation_payload['gallery_images_html'], $ghost_front['src']) && str_contains($approved_variation_payload['gallery_images_html'], 'data-test-attachment="78"'), 'Variation gallery must replace only the ghost primary and retain secondary views.');
check_gallery($approved_variation_payload['price'] === '$40.00', 'Image substitution must preserve variation commerce data.');
$reset_gallery = wc_get_product_gallery_html($ghost_variation_parent);
check_gallery(str_contains($reset_gallery, $ghost_front['src']) && !str_contains($reset_gallery, 'ghost-front.webp'), 'Variation reset/default must return to the approved model front.');
$invalid_variation_payload = $variation_payload;
$invalid_variation_payload['image_id'] = 999;
$invalid_variation = skyyrose2_pdp_variation_delivery($invalid_variation_payload, $ghost_variation_parent, $ghost_variation);
check_gallery(0 === $invalid_variation['image_id'] && array() === $invalid_variation['image'] && !str_contains($invalid_variation['gallery_images_html'], '999-'), 'An unpermitted variation image must fail closed without restoring an image.');
unset($GLOBALS['skyyrose2_pdp_media_context']);
$GLOBALS['is_product'] = false;
$_REQUEST['wc-ajax'] = 'unrelated';
check_gallery($data === skyyrose2_pdp_variation_delivery($data, $parent, $variation), 'Unrelated AJAX presentation must remain untouched.');
echo "PASS native PDP gallery boundary: default/embedded/reset, variation order and exclusion, stable permission, rejected/empty, AJAX regeneration, native metadata and exception cleanup.\n";
}
