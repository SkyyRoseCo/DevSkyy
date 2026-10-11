<?php
/** Offline regression of the actual query helper with more than twelve pre-orders. */
$theme = dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2';
$tokens = token_get_all( file_get_contents( $theme . '/functions.php' ) );
$source = '';
$active = false;
$depth = 0;
$body = false;
foreach ( $tokens as $index => $token ) {
	if ( ! $active && is_array( $token ) && T_FUNCTION === $token[0] ) {
		$next = $index + 1;
		while ( isset( $tokens[ $next ] ) && is_array( $tokens[ $next ] ) && T_WHITESPACE === $tokens[ $next ][0] ) { ++$next; }
		$active = is_array( $tokens[ $next ] ?? null ) && 'skyyrose2_get_products' === $tokens[ $next ][1];
	}
	if ( ! $active ) { continue; }
	$source .= is_array( $token ) ? $token[1] : $token;
	if ( '{' === $token ) { ++$depth; $body = true; }
	if ( '}' === $token && 0 === --$depth && $body ) { break; }
}
if ( ! $source || ! $body || 0 !== $depth ) { throw new RuntimeException( 'Actual query helper extraction failed' ); }
eval( $source ); // Execute trusted repository helper, never user or network input.
function absint( $value ) { return abs( (int) $value ); }
function sanitize_title( $value ) { return strtolower( $value ); }
function wc_get_products( $args ) { $GLOBALS['query_args'] = $args; return $GLOBALS['products']; }
function skyyrose2_product_presentation( $product ) { return $product['presentation']; }
function skyyrose2_is_transaction_preorder_product( $product ) { return $product['preorder']; }
function complete_check( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
$GLOBALS['products'] = array();
foreach ( array( 'signature' => 5, 'black-rose' => 9, 'love-hurts' => 1 ) as $collection => $count ) {
	for ( $index = 0; $index < $count; ++$index ) {
		$GLOBALS['products'][] = array( 'identity' => $collection . '-' . $index, 'preorder' => true, 'presentation' => array( 'collection' => $collection, 'presentation' => 'black-rose' === $collection ? 'jersey-series' : 'editorial' ) );
	}
}
$expected = $GLOBALS['products'];
array_splice( $GLOBALS['products'], 4, 0, array( array( 'identity' => 'standard-order', 'preorder' => false, 'presentation' => array( 'collection' => 'signature' ) ), array( 'identity' => 'unregistered', 'preorder' => true, 'presentation' => array() ) ) );
$actual = skyyrose2_get_products( -1, 'pre-order' );
complete_check( $actual === $expected && 15 === count( $actual ), 'Unlimited pre-order query must retain every eligible identity after exclusions, including items after twelve' );
complete_check( -1 === $GLOBALS['query_args']['limit'] && 'publish' === $GLOBALS['query_args']['status'] && ! isset( $GLOBALS['query_args']['category'] ), 'Woo remains the published pre-order identity query authority' );
complete_check( array_slice( $expected, 0, 3 ) === skyyrose2_get_products( 3, 'pre-order' ), 'Existing positive rail limits remain effective after exclusions' );
$template = file_get_contents( $theme . '/template-parts/v2-preorder.php' );
complete_check( str_contains( $template, "skyyrose2_get_products( -1, 'pre-order' )" ), 'The actual pre-order page must request the complete published assortment' );
echo "PASS offline actual pre-order query: fifteen identities, exclusions, published authority, complete page request and positive rail limits\n";
