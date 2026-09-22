<?php
/** Isolated rendering regression for the real canonical product-card partial. */
define( 'ABSPATH', __DIR__ );
class WC_Product {
	public $visible = true;
	public $in_stock = true;
	public $type = 'variable';
	public $sale = false;
	public $preorder = false;
	public function is_on_sale() { return $this->sale; }
	public function __construct( public $id = 41 ) {}
	public function is_visible() { return $this->visible; }
	public function get_id() { return $this->id; }
	public function get_permalink() { return 'https://example.test/product/' . $this->id . '/'; }
	public function get_name() { return 'The Bridge <Edition>'; }
	public function get_sku() { return 'sg-005'; }
	public function get_image_id() { return 999; }
	public function get_price_html() { return '<span class="amount">$25.00</span>'; }
	public function is_in_stock() { return $this->in_stock; }
	public function get_short_description() { return '<p>Current Woo description.</p>'; }
	public function get_type() { return $this->type; }
	public function is_purchasable() { return true; }
}
function __( $text ) { return $text; }
function esc_html( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $value ) { return esc_html( $value ); }
function esc_url( $value ) { return esc_html( $value ); }
function esc_html_e( $value ) { echo esc_html( $value ); }
function tag_escape( $value ) { return preg_replace( '/[^a-z0-9]/i', '', $value ); }
function sanitize_title( $value ) { return strtolower( $value ); }
function wp_kses_post( $value ) { return $value; }
function wp_strip_all_tags( $value ) { return strip_tags( $value ); }
function wp_trim_words( $value ) { return $value; }
function skyyrose2_collections() { return array( 'signature' => array( 'name' => 'Signature', 'portal_statue' => $GLOBALS['test_frame'] ?? array() ) ); }
function skyyrose2_sot_asset_uri( $path ) { return 'https://example.test/sot/' . $path; }
function absint( $value ) { return abs( (int) $value ); }
function skyyrose2_is_preorder_product( $product ) { return $product->preorder; }
function skyyrose2_product_presentation() { return array( 'collection' => 'signature', 'presentation' => 'signature' ); }
function skyyrose2_approved_card_front() { return $GLOBALS['test_front']; }
function skyyrose2_product_commerce_media() { $GLOBALS['resolver_calls']++; return $GLOBALS['test_media']; }
function is_shop() { return $GLOBALS['test_archive']; }
function is_product_taxonomy() { return false; }
function is_main_query() { return $GLOBALS['test_main']; }
function wc_get_loop_prop() { return $GLOBALS['test_loop_name']; }
function wc_get_stock_html( $product ) { return '<p class="stock">' . ( $product->is_in_stock() ? 'Available on backorder' : 'Out of stock' ) . '</p>'; }
function wp_get_attachment_image_url( $id ) { return 'https://example.test/attachment-' . $id . '.webp'; }
function wp_get_attachment_image( $id, $size, $icon, $attributes ) {
	$markup = '<img src="' . wp_get_attachment_image_url( $id ) . '" width="300" height="450"';
	foreach ( $attributes as $key => $value ) { $markup .= ' ' . $key . '="' . esc_attr( $value ) . '"'; }
	return $markup . '>';
}
function woocommerce_template_loop_add_to_cart() {
	global $product;
	if ( $GLOBALS['test_action_throw'] ) { throw new RuntimeException( 'Native extension failed' ); }
	echo '<a class="button" data-native-product="' . $product->get_id() . '" href="' . $product->get_permalink() . '">Select options</a>';
}
function check_card( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
function render_card( $args, $previous ) {
	global $product;
	$product = $previous;
	ob_start();
	try {
		include __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/template-parts/commerce/product-card.php';
		return ob_get_clean();
	} catch ( Throwable $exception ) {
		ob_end_clean();
		throw $exception;
	}
}
$front = array(
	'src' => 'https://example.test/approved-original.webp', 'width' => 1024, 'height' => 1536, 'alt' => 'Approved "front" <view>',
	'card_src' => 'https://example.test/approved-480.webp', 'card_width' => 480, 'card_height' => 720,
	'srcset' => 'https://example.test/approved-320.webp 320w, https://example.test/approved-480.webp 480w, https://example.test/approved-original.webp 1024w',
	'sizes' => '(max-width: 640px) 92vw, 30vw',
);
$GLOBALS['test_front'] = $front;
$GLOBALS['test_media'] = array( 'state' => 'rejected', 'ids' => array() );
$GLOBALS['resolver_calls'] = 0;
$GLOBALS['test_archive'] = false;
$GLOBALS['test_main'] = true;
$GLOBALS['test_loop_name'] = '';
$GLOBALS['test_action_throw'] = false;
$previous = new WC_Product( 7 );
$piece = new WC_Product( 41 );
$html = render_card( array( 'product' => $piece, 'index' => 0 ), $previous );
check_card( $product === $previous, 'Global Woo product must be restored after rendering' );
check_card( str_contains( $html, 'data-native-product="41"' ), 'Native action must render the exact card product' );
check_card( 1 === substr_count( $html, '<img ' ), 'One card front only: no decorative frame or eager secondary image' );
check_card( str_contains( $html, 'src="https://example.test/approved-480.webp"' ) && str_contains( $html, 'width="480" height="720"' ), 'Card uses bounded responsive derivative dimensions' );
check_card( str_contains( $html, 'srcset="' ) && str_contains( $html, 'sizes="(max-width: 47.99em) calc(100vw - 2rem),' ), 'Editorial card source selection uses a full-width mobile slot rather than the asset helper estimate' );
check_card( str_contains( $html, 'loading="lazy" fetchpriority="auto"' ), 'Index zero in an editorial module is lazy by default' );
check_card( str_contains( $html, 'data-quick-view-image="https://example.test/approved-original.webp"' ), 'Deferred quick view uses the same independently approved front' );
check_card( 0 === $GLOBALS['resolver_calls'], 'Approved card-front authority is not blocked by unrelated opening-editorial rejection' );
check_card( str_contains( $html, '&lt;Edition&gt;' ) && str_contains( $html, '&quot;front&quot; &lt;view&gt;' ), 'Product text and image attributes must be escaped' );
check_card( str_contains( $html, '<h3 ' ) && str_contains( $html, 'Available on backorder' ) && str_contains( $html, '$25.00' ), 'Editorial heading and native stock/price truth survive' );
check_card( str_contains( $html, 'data-quick-view-availability="Available on backorder"' ), 'Quick view preserves the exact native backorder label' );
check_card( ! str_contains( $html, 'View piece' ), 'No third duplicate card action' );

$GLOBALS['test_archive'] = true;
$html = render_card( array( 'product' => $piece, 'index' => 0 ), $previous );
check_card( str_contains( $html, 'loading="lazy"' ) && str_contains( $html, '<h2 ' ), 'Archive requires explicit image priority and uses h2' );
check_card( str_contains( $html, 'sizes="(max-width: 29.99em) calc(100vw - 4rem), (max-width: 47.99em) calc((100vw - clamp(2rem, 8vw, 9rem) - 3rem) / 2),' ), 'Main archive models the actual one-column then two-column mobile card slots' );
$html = render_card( array( 'product' => $piece, 'variant' => 'feature' ), $previous );
check_card( str_contains( $html, 'sizes="(max-width: 29.99em) calc(100vw - 4rem),' ), 'Archive feature variants use the same actual grid slot sizing' );
$html = render_card( array( 'product' => $piece, 'sizes' => '(max-width: 900px) 90vw, 600px' ), $previous );
check_card( str_contains( $html, 'sizes="(max-width: 900px) 90vw, 600px"' ), 'Explicit composition sizes override automatic defaults' );
foreach ( array( 0 => array( 'eager', 'high' ), 1 => array( 'eager', 'auto' ), 2 => array( 'lazy', 'auto' ) ) as $index => $expected ) {
	$html = render_card( array( 'product' => $piece, 'index' => $index, 'media_priority' => 'high' ), $previous );
	check_card( str_contains( $html, 'loading="' . $expected[0] . '" fetchpriority="' . $expected[1] . '"' ), 'Only the first two native archive cards may be eager; only the first may be high' );
}
$GLOBALS['test_frame'] = array( 'small' => 'approved-frame.webp', 'width' => 640, 'height' => 1067 );
foreach ( array( 0 => 'high', 1 => 'auto', 2 => 'auto' ) as $index => $expected ) {
	$html = render_card( array( 'product' => $piece, 'index' => $index, 'media_priority' => 'high' ), $previous );
	preg_match( '/<img class="sr2-c-editorial-card__frame"[^>]+>/', $html, $frame_tag );
	check_card( str_contains( $frame_tag[0] ?? '', 'fetchpriority="' . $expected . '"' ), 'The measured LCP frame shares only its first native card priority' );
}
$GLOBALS['test_frame'] = array();
$GLOBALS['test_loop_name'] = 'related';
$html = render_card( array( 'product' => $piece, 'index' => 0, 'media_priority' => 'high' ), $previous );
check_card( str_contains( $html, 'loading="lazy"' ), 'Secondary named Woo loops must not receive main-loop priority' );
$GLOBALS['test_loop_name'] = '';
$GLOBALS['test_main'] = false;
$html = render_card( array( 'product' => $piece, 'index' => 0, 'media_priority' => 'high' ), $previous );
check_card( str_contains( $html, 'loading="lazy"' ), 'A secondary query cannot claim native archive priority' );
$GLOBALS['test_main'] = true;
$GLOBALS['test_archive'] = false;
$html = render_card( array( 'product' => $piece, 'media_priority' => 'high', 'variant' => 'invalid" injected', 'heading_level' => 99 ), $previous );
check_card( str_contains( $html, 'loading="lazy"' ) && str_contains( $html, 'data-card-variant="standard"' ) && str_contains( $html, '<h3 ' ), 'Invalid arguments and nonarchive high priority fail to safe defaults' );

$GLOBALS['test_front'] = array();
foreach ( array( 'rejected', 'missing' ) as $state ) {
	$GLOBALS['test_media'] = array( 'state' => $state, 'ids' => array() );
	$html = render_card( array( 'product' => $piece ), $previous );
	check_card( ! str_contains( $html, '<img ' ) && ! str_contains( $html, 'attachment-999' ), 'Absent or rejected resolver result cannot bypass into raw Woo assignment' );
	check_card( str_contains( $html, 'data-media-state="' . $state . '"' ) && str_contains( $html, 'data-quick-view-image=""' ), 'Card and quick view share missing/rejected policy' );
}
$GLOBALS['test_media'] = array( 'state' => 'commerce', 'ids' => array( 17, 18 ) );
$html = render_card( array( 'product' => $piece, 'heading_level' => 4, 'variant' => 'compact' ), $previous );
check_card( str_contains( $html, 'attachment-17.webp' ) && ! str_contains( $html, 'attachment-18.webp' ) && ! str_contains( $html, 'attachment-999.webp' ), 'Only authorized primary attachment renders, with no secondary fetch' );
check_card( str_contains( $html, '<h4 ' ) && str_contains( $html, 'data-card-variant="compact"' ), 'Bounded heading and variant arguments work' );

$GLOBALS['test_front'] = array_intersect_key( $front, array_flip( array( 'src', 'width', 'height', 'alt' ) ) );
$html = render_card( array( 'product' => $piece ), $previous );
check_card( str_contains( $html, 'src="https://example.test/approved-original.webp"' ) && ! str_contains( $html, 'srcset="' ), 'Legacy approved front degrades gracefully before derivative availability' );
$piece->in_stock = false;
$html = render_card( array( 'product' => $piece ), $previous );
check_card( str_contains( $html, 'data-availability="unavailable"' ) && str_contains( $html, 'Out of stock' ), 'Unavailability remains native Woo truth' );
$GLOBALS['test_action_throw'] = true;
try { render_card( array( 'product' => $piece ), $previous ); throw new RuntimeException( 'Expected native renderer exception' ); } catch ( RuntimeException $exception ) { check_card( 'Native extension failed' === $exception->getMessage(), 'Native renderer exception propagated' ); }
check_card( $product === $previous, 'Global Woo product is restored even when an extension throws' );
$GLOBALS['test_action_throw'] = false;
$piece->visible = false;
check_card( '' === render_card( array( 'product' => $piece ), $previous ), 'Invisible products do not render a card' );
echo "PASS canonical card responsive authority, native commerce, lazy defaults, priority boundaries, escaping and exception restoration\n";

$piece->visible = true;
$piece->type = 'simple';
$piece->preorder = true;
$piece->sale = true;
$GLOBALS['test_action_throw'] = false;
$html = render_card( array( 'product' => $piece ), $previous );
check_card( str_contains( $html, 'data-product-type="simple"' ) && str_contains( $html, 'data-preorder="true"' ) && str_contains( $html, 'data-sale="true"' ), 'Simple/sale/preorder states derive from Woo product' );
check_card( str_contains( $html, 'Pre-order edition' ), 'Authoritative preorder label is visible' );
check_card( str_contains( $html, 'aria-haspopup="dialog"' ) && str_contains( $html, 'aria-expanded="false"' ), 'Quick View progressive dialog semantics exist' );
echo "PASS premium card simple/sale/preorder state derivation and dialog semantics\n";
