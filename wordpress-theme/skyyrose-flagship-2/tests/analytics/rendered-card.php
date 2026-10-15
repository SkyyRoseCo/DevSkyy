<?php
/** Isolated rendering regression for the real canonical product-card partial. */
define( 'ABSPATH', __DIR__ );
class WC_Product {
	public $visible  = true;
	public $in_stock = true;
	public $type     = 'variable';
	public $sale     = false;
	public $preorder = false;
	public function is_on_sale() {
		return $this->sale; }
	public function __construct( public $id = 41 ) {}
	public function is_visible() {
		return $this->visible; }
	public function get_id() {
		return $this->id; }
	public function get_permalink() {
		return 'https://example.test/product/' . $this->id . '/'; }
	public function get_name() {
		return 'Fixture product'; }
	public function get_sku() {
		return 'fixture-001'; }
	public function get_image_id() {
		return 999; }
	public function get_price_html() {
		return '<span class="amount">$25.00</span>'; }
	public function is_in_stock() {
		return $this->in_stock; }
	public function get_short_description() {
		return '<p>Current Woo description.</p>'; }
	public function get_type() {
		return $this->type; }
	public function is_purchasable() {
		return true; }
}
function __( $text ) {
	return $text; }
function esc_html( $value ) {
	return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $value ) {
	return esc_html( $value ); }
function esc_url( $value ) {
	return esc_html( $value ); }
function esc_html_e( $value ) {
	echo esc_html( $value ); }
function tag_escape( $value ) {
	return preg_replace( '/[^a-z0-9]/i', '', $value ); }
function sanitize_title( $value ) {
	return strtolower( $value ); }
function wp_kses_post( $value ) {
	return $value; }
function wp_strip_all_tags( $value ) {
	return strip_tags( $value ); }
function wp_trim_words( $value ) {
	return $value; }
function skyyrose2_collections() {
	return array(
		'fixture' => array(
			'name'          => 'Signature',
			'portal_statue' => $GLOBALS['test_frame'] ?? array(),
		),
	); }
function skyyrose2_sot_asset_uri( $path ) {
	return 'https://example.test/sot/' . $path; }
function absint( $value ) {
	return abs( (int) $value ); }
function skyyrose2_is_transaction_preorder_product( $product ) {
	return $product->preorder; }
function skyyrose2_product_presentation() {
	return array(
		'collection'   => 'fixture',
		'presentation' => 'fixture',
	); }
function skyyrose2_approved_card_front() {
	return $GLOBALS['test_front']; }
function skyyrose2_product_commerce_media() {
	++$GLOBALS['resolver_calls'];
	return $GLOBALS['test_media']; }
function is_shop() {
	return $GLOBALS['test_archive']; }
function is_product_taxonomy() {
	return false; }
function is_main_query() {
	return $GLOBALS['test_main']; }
function wc_get_loop_prop() {
	return $GLOBALS['test_loop_name']; }
function wc_get_stock_html( $product ) {
	return '<p class="stock">' . ( $product->is_in_stock() ? 'Available on backorder' : 'Out of stock' ) . '</p>'; }
function wp_get_attachment_image_url( $id ) {
	return 'https://example.test/attachment-' . $id . '.webp'; }
function wp_get_attachment_image( $id, $size, $icon, $attributes ) {
	$markup = '<img src="' . wp_get_attachment_image_url( $id ) . '" width="300" height="450"';
	foreach ( $attributes as $key => $value ) {
		$markup .= ' ' . $key . '="' . esc_attr( $value ) . '"'; }
	return $markup . '>';
}
function woocommerce_template_loop_add_to_cart() {
	global $product;
	if ( $GLOBALS['test_action_throw'] ) {
		throw new RuntimeException( 'Native extension failed' ); }
	echo '<a class="button" data-native-product="' . $product->get_id() . '" href="' . $product->get_permalink() . '">Select options</a>';
}
function check_card( $condition, $message ) {
	if ( ! $condition ) {
		throw new RuntimeException( $message ); } }
function render_card( $args, $previous ) {
	global $product;
	$product = $previous;
	ob_start();
	try {
		include dirname( __DIR__, 2 ) . '/template-parts/commerce/product-card.php';
		return ob_get_clean();
	} catch ( Throwable $exception ) {
		ob_end_clean();
		throw $exception;
	}
}
$front                        = array(
	'src'         => 'https://example.test/approved-original.webp',
	'width'       => 1024,
	'height'      => 1536,
	'alt'         => 'Approved "front" <view>',
	'card_src'    => 'https://example.test/approved-480.webp',
	'card_width'  => 480,
	'card_height' => 720,
	'srcset'      => 'https://example.test/approved-320.webp 320w, https://example.test/approved-480.webp 480w, https://example.test/approved-original.webp 1024w',
	'sizes'       => '(max-width: 640px) 92vw, 30vw',
);
$GLOBALS['test_front']        = $front;
$GLOBALS['test_media']        = array(
	'state' => 'rejected',
	'ids'   => array(),
);
$GLOBALS['resolver_calls']    = 0;
$GLOBALS['test_frame']        = array(
	'small'  => 'fixture/legacy-portal.webp',
	'width'  => 640,
	'height' => 960,
);
$GLOBALS['test_archive']      = false;
$GLOBALS['test_main']         = true;
$GLOBALS['test_loop_name']    = '';
$GLOBALS['test_action_throw'] = false;
$previous                     = new WC_Product( 7 );
$piece                        = new WC_Product( 9 );
$html                         = render_card(
	array(
		'product' => $piece,
		'index'   => 0,
	),
	$previous
);
check_card(
	false === strpos( $html, 'class="sr2-c-editorial-card__frame"' ),
	'The default V2 card must omit the optional legacy archive frame.'
);
$opted_in_html = render_card(
	array(
		'product' => $piece,
		'index'   => 0,
		'frame'   => true,
	),
	$previous
);
check_card(
	false !== strpos( $opted_in_html, 'class="sr2-c-editorial-card__frame"' ),
	'An explicitly opted-in legacy archive frame must remain renderable.'
);
echo $html;
