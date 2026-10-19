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
	public function get_name() { return $this->sku; }
}
class WC_Product_Variation extends WC_Product {
	public function get_parent_id() { return 101; }
	public function get_variation_attributes() { return $GLOBALS['variation_attributes'] ?? array('attribute_pa_size' => 'M'); }
}
function WC() { return new class { public function plugin_path() { return $GLOBALS['woo_path']; } }; }
function is_admin() { return false; }
function wc_get_product($id) { return $GLOBALS['parents'][$id] ?? null; }
function esc_html__($text, ...$args) { return htmlspecialchars($text, ENT_QUOTES); }
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
function skyyrose2_product_presentation($product) {
	static $presentation = null;
	if (null === $presentation) { $presentation = json_decode(file_get_contents(SKYYROSE2_DIR . '/data/product-presentation-registry.json'), true); }
	return $presentation['products'][strtolower($product->get_sku())] ?? array();
}
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
require SKYYROSE2_DIR . '/inc/v2-media-eligibility.php';
require SKYYROSE2_DIR . '/inc/approved-card-fronts.php';
require SKYYROSE2_DIR . '/inc/pdp-media-delivery.php';
add_action('woocommerce_product_thumbnails', static function () { require $GLOBALS['woo_path'] . '/templates/single-product/product-thumbnails.php'; });
// Current source/review bindings replace the superseded founder-label fixture.
$manifest = json_decode(file_get_contents(SKYYROSE2_DIR . '/data/approved-card-fronts.json'), true);
check_gallery(33 === count($manifest['products'] ?? array()), 'Every current SKU has its exact card binding.');
$pdp_count = 0;
foreach ($manifest['products'] as $sku => $record) {
    $item = new WC_Product(800, $sku, 800);
    $front = skyyrose2_approved_card_front($item);
    check_gallery($front && $front['sha256'] === $record['sha256'] && $front['path'] === $record['src'] && $front['status'] === $record['current_fidelity_status'], 'Exact current card bytes/review for ' . $sku);
    if (skyyrose2_approved_pdp_front($item)) { ++$pdp_count; }
}
// 18 independently reviewed PDP-role records plus the 15 founder usage grants
// (data/v2-media-reviews/usage-*.json) that add pdp_on_model_front to an unchanged card original.
$usage_pdp = 0;
foreach (skyyrose2_media_inventory()['usage_adoptions'] as $relative => $binding) {
    if (in_array('pdp_on_model_front', skyyrose2_media_usage_roles($relative, skyyrose2_media_inventory()['assets'][$relative]), true)) { ++$usage_pdp; }
}
check_gallery(15 === $usage_pdp && 18 + $usage_pdp === $pdp_count, 'PDP fronts = 18 reviewed PDP-role grants + 15 founder usage grants; card approval alone grants none.');
$parent = new WC_Product(101, 'sg-005', 77, array(78));
$GLOBALS['parents'][101] = $parent;
$front = skyyrose2_approved_pdp_front($parent);
check_gallery($front && str_ends_with((string) parse_url($front['display_src'], PHP_URL_PATH), 'sg-005-768w.webp') && preg_match('/\?v=[a-f0-9]{64}$/D', $front['display_src']),'Fixture requires an actual current PDP-role lead.');
$GLOBALS['files'][77] = SKYYROSE2_DIR . '/' . $front['path'];
$GLOBALS['attachment_urls'][77] = $front['src'];
$GLOBALS['product'] = 'previous-global';
$GLOBALS['skyyrose2_pdp_media_context'] = skyyrose2_pdp_capture_media_context($parent);
$permission_calls = $GLOBALS['permission_calls'];
$default = wc_get_product_gallery_html($parent);
check_gallery(str_contains($default, 'src="' . $front['display_src'] . '"') && str_contains($default, 'srcset="') && str_contains($default, 'href="' . $front['src'] . '"'), 'Native default uses bounded responsive display and exact original zoom.');
check_gallery(str_contains($default, 'data-test-attachment="78"'), 'Native secondary hooks remain available before the final media boundary.');
$filtered = skyyrose2_media_filter_html($default);
check_gallery(substr_count($filtered, '<img ') === 1 && !str_contains($filtered, 'src="https://uploads.invalid'), 'Final media gate retains only the reviewed responsive family.');
check_gallery($GLOBALS['product'] === 'previous-global', 'Native product global is restored.');
$ordered = wc_get_product_gallery_html($parent, array(78, 999, 77));
check_gallery(!str_contains($ordered, '999-') && str_contains($ordered, $front['display_src']), 'Native variation candidates exclude unpermitted IDs and retain exact current primary.');
check_gallery($GLOBALS['permission_calls'] === $permission_calls, 'No permission lookup occurs under temporary native getters.');
check_gallery($parent->get_image_id() === 77 && $parent->get_gallery_image_ids() === array(78), 'Temporary getters do not leak.');
check_gallery($default === wc_get_product_gallery_html($parent), 'Repeated default/reset snapshots remain stable.');
check_gallery('' === wc_get_product_gallery_html($parent, array(999)), 'An empty candidate intersection cannot restore unpermitted media.');

// Compatibility helpers cannot substitute a historical or other-SKU attachment.
check_gallery(str_contains(skyyrose2_pdp_approved_ghost_front_html('<div>original</div>', 77, $parent), $front['src']), 'An exact current attachment binding may use the current same-source delivery.');
$GLOBALS['attachment_urls'][77] = 'https://uploads.invalid/sg-005-ghost-front.webp';
check_gallery('<div>original</div>' === skyyrose2_pdp_approved_ghost_front_html('<div>original</div>', 77, $parent), 'An unbound historical ghost is not silently adopted.');
$GLOBALS['attachment_urls'][77] = $front['src'];
check_gallery('<div>original</div>' === skyyrose2_pdp_approved_ghost_front_html('<div>original</div>', 999, $parent), 'Non-primary attachments cannot inherit the primary binding.');
$original_context = $GLOBALS['skyyrose2_pdp_media_context'];
$GLOBALS['skyyrose2_pdp_media_context']['media'] = array('state' => 'editorial', 'ids' => array(78, 77));
$editorial_default = wc_get_product_gallery_html($parent);
check_gallery(str_contains($editorial_default, $front['display_src']) && !str_contains($editorial_default, 'data-test-attachment="78"'), 'Canonical editorial order is respected while the first frame retains the reviewed primary.');
check_gallery($GLOBALS['permission_calls'] === $permission_calls, 'Editorial order does not broaden permission.');
$GLOBALS['skyyrose2_pdp_media_context'] = $original_context;
check_gallery(str_contains($source, 'wp_json_encode( wc_get_product_gallery_html( $product ) )'), 'Native inline-default expression remains pinned.');
check_gallery(str_contains(file_get_contents($GLOBALS['woo_path'] . '/templates/single-product/add-to-cart/variable.php'), 'wc_get_product_gallery_html( $product )'), 'Native embedded-default expression remains pinned.');

$thrower = static function () { throw new \RuntimeException('native gallery hook failure'); };
add_action('woocommerce_product_thumbnails', $thrower, 5);
try { wc_get_product_gallery_html($parent, array(78)); throw new \RuntimeException('Expected native exception.'); }
catch (\RuntimeException $error) { check_gallery($error->getMessage() === 'native gallery hook failure', 'Native errors propagate.'); }
remove_action('woocommerce_product_thumbnails', $thrower, 5);
check_gallery($parent->get_image_id() === 77 && $parent->get_gallery_image_ids() === array(78), 'Exceptions restore native getters.');
check_gallery(!has_filter('woocommerce_gallery_image_html_attachment_image_params') && !has_filter('woocommerce_single_product_image_thumbnail_html'), 'Exceptions restore delivery and primary filters.');
check_gallery(!has_filter('get_post_metadata') && !has_filter('woocommerce_product_get__wc_video_gallery'), 'Exceptions restore video metadata filters.');
check_gallery(get_post_meta(101, '_wc_video_gallery', true)[0]['id'] === 999 && $GLOBALS['product'] === 'previous-global', 'Exceptions preserve native video data and global product.');

// Since 2.5.3 every card original also carries a founder usage grant, so no real
// card-only SKU remains. br-003's PDP role must come only from its exact grant,
// never from its card receipt or from a rejected Woo attachment.
$grant_only = new WC_Product(102, 'br-003', 79, array(), 'rejected');
$grant_path = 'assets/v2-original/products/br-003.png';
$grant_record = skyyrose2_media_inventory()['assets'][$grant_path];
$GLOBALS['skyyrose2_pdp_media_context'] = skyyrose2_pdp_capture_media_context($grant_only);
check_gallery(skyyrose2_approved_card_front($grant_only) && !in_array('pdp_on_model_front', $grant_record['roles'], true) && in_array('pdp_on_model_front', skyyrose2_media_usage_roles($grant_path, $grant_record), true), 'Fixture PDP role exists only through the exact founder usage grant.');
$broken_grant = $grant_record; $broken_grant['skus'] = array('br-002');
check_gallery(!skyyrose2_media_usage_roles($grant_path, $broken_grant) && !skyyrose2_media_record_allowed($grant_path, $grant_record, 'pdp_on_model_front', 'br-002'), 'A grant cannot be borrowed by another SKU.');
$grant_front = skyyrose2_approved_pdp_front($grant_only);
$grant_html = wc_get_product_gallery_html($grant_only);
check_gallery($grant_front && $grant_path === $grant_front['path'] && !str_contains($grant_html, 'uploads.invalid/79'), 'Rejected attachments never enter the gallery; the lead is the granted original.');
unset($GLOBALS['skyyrose2_pdp_media_context']);
$GLOBALS['is_product'] = false;
$GLOBALS['ajax'] = true;
$_REQUEST['wc-ajax'] = 'get_variation';
check_gallery('' === wc_get_product_gallery_html($parent, array(999, 77)), 'Intermediate native AJAX cannot infer permission from overridden IDs.');

// A selected size inherits only its parent SKU, while unknown/color variants fail closed.
$variation = new WC_Product_Variation(201, '', 77, array(78));
$data = array('image_id' => 999, 'image' => array('src' => 'stale', 'srcset' => 'stale 600w'), 'gallery_image_ids' => array(78, 999), 'display_price' => 137, 'is_in_stock' => true, 'is_purchasable' => true, 'variation_id' => 201);
$result = skyyrose2_media_variation(skyyrose2_pdp_variation_delivery($data, $parent, $variation), $parent, $variation);
check_gallery(0 === $result['image_id'] && array() === $result['gallery_image_ids'] && $result['image']['src'] === $front['display_src'] && $result['image']['full_src'] === $front['src'] && $result['image']['sizes'] === skyyrose2_pdp_gallery_sizes($front['width'], $front['height']), 'Selected size has one current responsive family and original zoom, without stale attachment IDs.');
check_gallery(str_contains($result['gallery_images_html'], $front['display_src']) && !str_contains($result['gallery_images_html'], '999-'), 'AJAX produces a complete current gallery for native replacement/reset.');
foreach (array('display_price', 'is_in_stock', 'is_purchasable', 'variation_id') as $field) { check_gallery($data[$field] === $result[$field], 'Image delivery preserves purchase field ' . $field); }
$unknown = new WC_Product_Variation(202, 'unknown-color', 77);
$missing = skyyrose2_pdp_variation_delivery($data, $parent, $unknown);
check_gallery(array() === $missing['image'] && !str_contains($missing['gallery_images_html'], '<img') && str_contains($missing['gallery_images_html'], 'currently unavailable'), 'Unknown variation cannot restore the parent image.');
$GLOBALS['variation_attributes'] = array('attribute_pa_color' => 'red');
$missing = skyyrose2_pdp_variation_delivery($data, $parent, $variation);
check_gallery(array() === $missing['image'] && !str_contains($missing['gallery_images_html'], '<img'), 'Color changes cannot silently inherit parent imagery.');
unset($GLOBALS['variation_attributes']);
check_gallery(!isset($GLOBALS['skyyrose2_pdp_media_context']) && $parent->get_image_id() === 77 && $GLOBALS['product'] === 'previous-global', 'Variation delivery does not leak context or native state.');
$_REQUEST['wc-ajax'] = 'unrelated';
check_gallery($data === skyyrose2_pdp_variation_delivery($data, $parent, $variation), 'Unrelated AJAX remains unchanged.');
echo "PASS pinned native WP7.1/Woo11.1 gallery: 33 exact cards / 33 PDP fronts (18 reviewed + 15 founder grants), responsive originals/reset, candidate exclusion, scoped hooks, no video promotion, exception cleanup, complete variation families and native purchase truth (offline).\n";
}
