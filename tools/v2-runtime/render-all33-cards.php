<?php
/** Offline render of the real V2 card and resolver; never live WooCommerce evidence. */
define( 'ABSPATH', __DIR__ );
$root = dirname( __DIR__, 2 );
define( 'SKYYROSE2_DIR', $root . '/wordpress-theme/skyyrose-flagship-2' );
define( 'SKYYROSE2_URI', '/wordpress-theme/skyyrose-flagship-2' );
function add_action( ...$args ) {} function add_filter( ...$args ) {}
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
function absint( $value ) { return abs( (int) $value ); }
function is_shop() { return false; } function is_product_taxonomy() { return false; }
function skyyrose2_collections() { return $GLOBALS['fixture_collections']; }
function skyyrose2_product_presentation( $product ) { return $GLOBALS['fixture_presentation']['products'][ $product->get_sku() ] ?? array(); }
function skyyrose2_is_transaction_preorder_product( $product ) { return ! empty( skyyrose2_product_presentation( $product )['is_preorder'] ); }
function skyyrose2_product_commerce_media() { return array( 'state' => 'missing', 'ids' => array() ); }
function wc_get_stock_html() { return ''; }
function woocommerce_template_loop_add_to_cart() {
    global $product;
    echo '<a class="button" href="' . esc_url( $product->get_permalink() ) . '">View item</a>';
}
class WC_Product {
    public function __construct( public $sku, private $catalog ) {}
    public function is_visible() { return true; }
    public function get_sku( $context = 'view' ) { return $this->sku; }
    public function get_id() { return 0; }
    public function get_name() { return $this->catalog['name']; }
    public function get_permalink() { return '#item-' . $this->sku; }
    public function get_price_html() { return ''; }
    public function is_in_stock() { return true; }
    public function get_short_description() { return ''; }
    public function get_type() { return 'simple'; }
    public function is_type( $type ) { return 'simple' === $type; }
    public function is_purchasable() { return false; }
    public function is_on_sale() { return false; }
}
$registry = json_decode( file_get_contents( $root . '/logo-registry.json' ), true, 512, JSON_THROW_ON_ERROR );
$GLOBALS['fixture_collections'] = $registry['collections'];
$GLOBALS['fixture_presentation'] = json_decode( file_get_contents( SKYYROSE2_DIR . '/data/product-presentation-registry.json' ), true, 512, JSON_THROW_ON_ERROR );
require SKYYROSE2_DIR . '/inc/v2-media-eligibility.php';
// Rename only the fixture wrapper: the production resolver and gate are intact.
$source = file_get_contents( SKYYROSE2_DIR . '/inc/approved-card-fronts.php' );
$source = str_replace( 'function skyyrose2_approved_card_front(', 'function fixture_current_front(', $source );
eval( '?>' . $source );
require SKYYROSE2_DIR . '/inc/card-garment-highlight.php';
$candidate_mode = 'candidates' === ( $argv[1] ?? '' );
$task = $argv[2] ?? 'tasks/v2-creative-review/v2-imagery-reset-20261002/v2-card-placement-review-20261006/source-adoption-r2';
$GLOBALS['review_candidates'] = array();
if ( $candidate_mode ) {
    foreach ( json_decode( file_get_contents( $root . '/' . $task . '/corrected-candidates.json' ), true ) as $candidate ) {
        if ( 'card_front' === $candidate['role'] ) { $GLOBALS['review_candidates'][ $candidate['sku'] ] = $candidate; }
    }
}
function skyyrose2_approved_card_front( $product ) {
    $candidate = $GLOBALS['review_candidates'][ $product->get_sku() ] ?? null;
    if ( ! $candidate ) { return fixture_current_front( $product ); }
    return array( 'src' => '/' . $candidate['path'], 'path' => $candidate['path'], 'sha256' => $candidate['sha256'], 'width' => $candidate['width'], 'height' => $candidate['height'], 'alt' => $product->get_name(), 'sku' => $product->get_sku(), 'status' => 'CANDIDATE_PENDING_REVIEW' );
}
$title = $candidate_mode ? 'Source correction review' : 'All 33 V2 product cards';
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title><?php echo esc_html( $title ); ?></title>
<?php foreach ( array( 'design-tokens', 'theme', 'premium-commerce' ) as $sheet ) : ?><link rel="stylesheet" href="/wordpress-theme/skyyrose-flagship-2/assets/css/<?php echo esc_attr( $sheet ); ?>.css"><?php endforeach; ?>
<style>body{margin:0;background:#0a0a0a;color:#f4f0ea}main{max-width:1500px;margin:auto;padding:40px 24px}h1{font-size:clamp(2.5rem,6vw,6rem);line-height:1;margin:0 0 20px}h2{font-size:clamp(2rem,4vw,3.5rem)}.review-note{color:#b6aba0;font:14px/1.6 monospace;margin-bottom:40px;max-width:900px}.review-nav{display:flex;gap:20px;flex-wrap:wrap;margin:25px 0}.review-nav a{color:inherit}.review-section{padding:40px 0;border-top:1px solid #37312e}.review-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:48px 30px}.review-grid article{min-width:0}.review-group{padding:20px 0}.review-group h3{font:18px/1.5 monospace;letter-spacing:.15em;text-transform:uppercase}.review-grid a{color:inherit}.review-grid .sr2-c-editorial-card__availability{display:none} .review-grid .sr2-c-editorial-card__media{display:block} @media(max-width:1000px){.review-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:767px){main{padding:30px 16px}.review-grid{grid-template-columns:1fr;gap:40px}}</style></head>
<body><main><p>SKYYROSE · V2</p><h1><?php echo esc_html( $title ); ?></h1><p class="review-note"><?php echo $candidate_mode ? 'Unapproved source corrections shown in the production card template for visual inspection.' : '33 exact SKU cards · 18 standard collection listings · 15 pre-order listings. Current local theme and source bindings.'; ?> This offline preview proves imagery and template wiring. Prices, stock and checkout remain live WooCommerce responsibilities.</p>
<nav class="review-nav"><a href="#black-rose">Black Rose</a><a href="#love-hurts">Love Hurts</a><a href="#signature">Signature</a><a href="#kids-capsule">Kids Capsule</a><a href="#pre-order">Pre-order</a></nav>
<?php
$groups = array( 'black-rose', 'love-hurts', 'signature', 'kids-capsule', 'pre-order' );
$count = 0;
foreach ( $groups as $group ) {
    $is_pre = 'pre-order' === $group;
    $name = $is_pre ? 'Pre-order · each collection in its own world' : ( $GLOBALS['fixture_collections'][ $group ]['name'] ?? $group );
    echo '<section class="review-section" id="' . esc_attr( $group ) . '"><h2>' . esc_html( $name ) . '</h2>';
    foreach ( ( $is_pre ? array( 'black-rose', 'love-hurts', 'signature' ) : array( $group ) ) as $collection ) {
        $selected = array_filter( $GLOBALS['fixture_presentation']['products'], static fn( $r ) => (bool) $r['is_preorder'] === $is_pre && $r['collection'] === $collection );
        if ( $candidate_mode ) { $selected = array_intersect_key( $selected, $GLOBALS['review_candidates'] ); }
        if ( ! $selected ) { continue; }
        echo '<div class="review-group" data-listing="' . ( $is_pre ? 'pre-order' : 'standard' ) . '" data-collection="' . esc_attr( $collection ) . '">';
        if ( $is_pre ) { echo '<h3>' . esc_html( $GLOBALS['fixture_collections'][ $collection ]['name'] ?? $collection ) . '</h3>'; }
        echo '<div class="review-grid">';
        foreach ( $selected as $sku => $projection ) {
            $product = new WC_Product( $sku, $registry['products'][ $sku ]['catalog'] );
            $args = array( 'product' => $product, 'index' => $count++, 'listing' => $is_pre ? 'pre-order' : 'standard' );
            include SKYYROSE2_DIR . '/template-parts/commerce/product-card.php';
        }
        echo '</div></div>';
    }
    echo '</section>';
}
if ( $candidate_mode ) {
    foreach ( json_decode( file_get_contents( $root . '/' . $task . '/corrected-candidates.json' ), true ) as $scene ) {
        if ( 'lh-004' === $scene['sku'] && 'collection_hero_back' === $scene['role'] ) {
            echo '<section class="review-section" id="lh004-hood"><h2>Love Hurts · hood correction candidate</h2><img style="width:100%;height:auto" src="/' . esc_attr( $scene['path'] ) . '" alt="Love Hurts bomber back scene with white rose-lined hood"></section>';
        }
    }
}
?></main></body></html>
