<?php
/** Offline exercise of actual query helpers against current registry identities. */
$root = dirname( __DIR__, 2 );
$theme = $root . '/wordpress-theme/skyyrose-flagship-2';
function extract_partition_function( $name ) {
    global $theme;
    $tokens = token_get_all( file_get_contents( $theme . '/functions.php' ) );
    $active = false; $depth = 0; $body = false; $source = '';
    foreach ( $tokens as $i => $token ) {
        if ( ! $active && is_array( $token ) && T_FUNCTION === $token[0] ) {
            $next = $i + 1;
            while ( isset( $tokens[$next] ) && is_array( $tokens[$next] ) && T_WHITESPACE === $tokens[$next][0] ) { ++$next; }
            $active = is_array( $tokens[$next] ?? null ) && $name === $tokens[$next][1];
        }
        if ( ! $active ) { continue; }
        $source .= is_array( $token ) ? $token[1] : $token;
        if ( '{' === $token ) { ++$depth; $body = true; }
        if ( '}' === $token && 0 === --$depth && $body ) { break; }
    }
    if ( ! $source || ! $body || $depth ) { throw new RuntimeException( 'Function extraction failed' ); }
    eval( $source );
}
function absint( $v ) { return abs( (int) $v ); }
function sanitize_title( $v ) { return strtolower( $v ); }
function add_action( ...$v ) {}
function wc_get_products( $args ) { $GLOBALS['query_args'] = $args; return $GLOBALS['all_products']; }
function skyyrose2_product_presentation( $p ) { return $p->presentation; }
function skyyrose2_is_transaction_preorder_product( $p ) { return $p->preorder; }
function assert_partition( $v, $label ) { if ( ! $v ) { throw new RuntimeException( $label ); } }
class WC_Product {
    public bool $visible = true; public bool $stock = true;
    public function __construct( public string $sku, public int $id, public bool $preorder, public array $presentation ) {}
    public function is_visible() { return $this->visible; }
    public function is_in_stock() { return $this->stock; }
    public function get_id() { return $this->id; }
}
$catalog = json_decode( file_get_contents( $root . '/logo-registry.json' ), true )['products'];
$GLOBALS['all_products'] = array(); $expected = array();
foreach ( $catalog as $sku => $record ) {
    $collection = $record['catalog']['collection']; $pre = '1' === $record['catalog']['is_preorder'];
    $p = new WC_Product( $sku, count( $GLOBALS['all_products'] )+1, $pre, array( 'collection' => $collection, 'presentation' => $record['merchandising']['series_slug'] ?? $collection ) );
    $GLOBALS['all_products'][] = $p; $expected[ $pre ? 'pre-order' : $collection ][] = $p;
}
extract_partition_function( 'skyyrose2_get_products' );
extract_partition_function( 'skyyrose2_standard_archive_query' );
foreach ( array( 'black-rose', 'love-hurts', 'signature', 'kids-capsule', 'pre-order' ) as $group ) {
    $actual = skyyrose2_get_products( -1, $group );
    assert_partition( $actual === $expected[$group], 'Exact current eligible identities for ' . $group );
}
assert_partition( 18 === count( skyyrose2_get_products( -1 ) ) && 15 === count( skyyrose2_get_products( -1, 'pre-order' ) ), 'Current 18/15 complete partition' );
assert_partition( skyyrose2_get_products( 3, 'signature' ) === array_slice( $expected['signature'], 0, 3 ), 'Display limit after exclusions' );
$standard = $expected['signature'][0]; $standard->visible = false;
assert_partition( ! in_array( $standard, skyyrose2_get_products( -1, 'signature' ), true ), 'Native visibility exclusion' );
$standard->visible = true; $standard->stock = false;
assert_partition( ! in_array( $standard, skyyrose2_get_products( -1, 'signature' ), true ), 'Native available-stock exclusion' );
$standard->stock = true;
class ListingQuery { public $args = array('post__not_in'=>array(999)); public function get($k,$d=array()){return $this->args[$k]??$d;} public function set($k,$v){$this->args[$k]=$v;} }
$query = new ListingQuery(); skyyrose2_standard_archive_query( $query );
$excluded = array_merge( array(999), array_map( static fn($p)=>$p->id, $expected['pre-order'] ) );
assert_partition( $query->args['post__not_in'] === $excluded, 'Native archive excludes all pre-order IDs and preserves prior exclusions' );
echo "PASS current all-33 identity partition, 18 standard /15 pre-order, collection ownership, post-filter limits, stock/visibility and native archive exclusions (offline)\n";
