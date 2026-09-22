<?php
/** Render the cart override against native extension hooks and quantity states. No WP writes. */
define( 'ABSPATH', __DIR__ );
function __( $s, $domain = '' ) { return $s; }
function esc_html__( $s, $domain = '' ) { return htmlspecialchars( $s ); }
function esc_html_e( $s, $domain = '' ) { echo esc_html__( $s ); }
function esc_attr_e( $s, $domain = '' ) { echo esc_attr( $s ); }
function esc_attr( $s ) { return htmlspecialchars( (string) $s, ENT_QUOTES ); }
function esc_url( $s ) { return esc_attr( $s ); }
function wp_kses_post( $s ) { return $s; }
function wp_strip_all_tags( $s ) { return strip_tags( $s ); }
function do_action( $name, ...$args ) { $GLOBALS['hooks'][] = $name; }
function apply_filters( $name, $value, ...$args ) {
    $GLOBALS['filters'][] = array( $name, $args );
    // Simulate installed extensions modifying the two commercial prices and native control.
    if ( 'woocommerce_cart_item_price' === $name ) { return '$24.00 member price'; }
    if ( 'woocommerce_cart_item_subtotal' === $name ) { return '$48.00 member subtotal'; }
    if ( 'woocommerce_cart_item_quantity' === $name ) { return '<div data-extension-quantity>' . $value . '</div>'; }
    return $value;
}
function wc_get_cart_url() { return '/cart/'; }
function wc_get_cart_remove_url( $key ) { return '/cart/?remove_item=' . $key . '&_wpnonce=test'; }
function wc_get_page_permalink( $slug ) { return '/' . $slug . '/'; }
function wc_get_formatted_cart_item_data( $item ) { return '<dl><dt>Size</dt><dd>M</dd></dl>'; }
function wc_coupons_enabled() { return true; }
function wp_nonce_field() { echo '<input type="hidden" name="woocommerce-cart-nonce" value="test">'; }
function woocommerce_quantity_input( $args, $product, $echo = true ) {
    $GLOBALS['quantity_args'] = $args;
    $html = '<input type="number" name="' . esc_attr( $args['input_name'] ) . '" value="' . $args['input_value'] . '">';
    if ( $echo ) { echo $html; } else { return $html; }
}
class CartContractProduct {
    public bool $single = false;
    public bool $backorder = false;
    public function exists() { return true; }
    public function is_visible() { return true; }
    public function get_permalink( $item ) { return '/product/sg-005/'; }
    public function get_name() { return 'Signature Tee'; }
    public function get_image() { return '<img alt="Signature Tee" src="/approved.webp">'; }
    public function get_sku() { return 'SG-005'; }
    public function get_max_purchase_quantity() { return 8; }
    public function is_sold_individually() { return $this->single; }
    public function backorders_require_notification() { return $this->backorder; }
    public function is_on_backorder( $qty ) { return $this->backorder && $qty > 0; }
}
class CartContractCart {
    public function __construct( public CartContractProduct $product ) {}
    public function is_empty() { return false; }
    public function get_cart() { return array( 'test-key' => array( 'data' => $this->product, 'product_id' => 182, 'quantity' => 2 ) ); }
    public function get_product_price( $product ) { return '$25.00'; }
    public function get_product_subtotal( $product, $quantity ) { if ( 2 !== $quantity ) { throw new Exception( 'Quantity lost' ); } return '$50.00'; }
}
function WC() { return $GLOBALS['woo']; }
$product = new CartContractProduct();
$GLOBALS['woo'] = (object) array( 'cart' => new CartContractCart( $product ) );
function check( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
foreach ( array( false, true ) as $single ) {
    $product->single = $single; $product->backorder = $single;
    $GLOBALS['hooks'] = array(); $GLOBALS['filters'] = array();
    ob_start(); include __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/woocommerce/cart/cart.php'; $html = ob_get_clean();
    check( str_contains( $html, 'Line subtotal' ) && str_contains( $html, '$48.00 member subtotal' ) && str_contains( $html, '$24.00 member price' ), 'Native filtered prices must reach the visible line' );
    check( str_contains( $html, 'data-extension-quantity' ) && str_contains( $html, 'cart[test-key][qty]' ), 'Native extension quantity control must survive output' );
    check( $GLOBALS['quantity_args']['min_value'] === ( $single ? 1 : 0 ) && $GLOBALS['quantity_args']['max_value'] === ( $single ? 1 : 8 ), 'Sold individually bounds must match native Woo' );
    check( str_contains( $html, 'Available on backorder' ) === $single, 'Backorder notification must follow product state' );
    check( str_contains( $html, 'woocommerce-cart-nonce' ) && str_contains( $html, 'remove_item=test-key' ), 'Native mutation nonce/URL must remain' );
    foreach ( array( 'woocommerce_after_cart_item_name', 'woocommerce_cart_coupon', 'woocommerce_before_cart', 'woocommerce_after_cart', 'woocommerce_cart_collaterals' ) as $hook ) {
        check( 1 === count( array_keys( $GLOBALS['hooks'], $hook, true ) ), 'Hook must run once: ' . $hook );
    }
    foreach ( array( 'woocommerce_cart_item_subtotal', 'woocommerce_cart_item_price', 'woocommerce_cart_item_quantity', 'woocommerce_cart_item_remove_link' ) as $filter ) {
        check( 1 === count( array_filter( $GLOBALS['filters'], fn( $call ) => $filter === $call[0] ) ), 'Filter must run once: ' . $filter );
    }
}
echo "PASS cart totals, price/quantity/remove extensions, sold-individually bounds, backorder states, native lifecycle and nonce\n";

// Keep native notice text/data authority with a live region that retains list semantics.
function wc_get_notice_data_attr( $notice ) { return ' data-native="retained"'; }
function wc_kses_notice( $notice ) { return htmlspecialchars( $notice ); }
$notices = array( array( 'notice' => '<script>untrusted</script> Invalid code' ) );
ob_start(); include __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/woocommerce/notices/error.php'; $notice_html = ob_get_clean();
check( str_contains( $notice_html, '<div class="woocommerce-error" role="alert">' ) && str_contains( $notice_html, '<ul class="sr2-notice-list" role="list">' ), 'Native inserted errors must retain an alert containing a semantic list' );
check( str_contains( $notice_html, 'data-native="retained"' ) && ! str_contains( $notice_html, '<script>' ), 'Native Woo notice data and escaping must survive' );
$notices = array(); ob_start(); include __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/woocommerce/notices/error.php'; check( '' === ob_get_clean(), 'No phantom empty error region' );
echo "PASS native notice escaping, data, list semantics and live announcements\n";
