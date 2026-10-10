<?php
/** Exercise the actual shared route predicate and template selection. */
define( 'SKYYROSE2_DIR', __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2' );
function is_page() { return $GLOBALS['route']['page']; }
function get_queried_object_id() { return 17; }
function get_post_field() { return $GLOBALS['route']['slug']; }
function get_page_uri() { return $GLOBALS['route']['uri']; }
function is_page_template( $template ) { return $GLOBALS['route']['template'] === $template; }
function sanitize_title( $value ) { return strtolower( trim( $value ) ); }
function skyyrose2_collections() { return array_fill_keys( array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ), array() ); }
function add_filter() {}
$source = file_get_contents( SKYYROSE2_DIR . '/functions.php' );
$start = strpos( $source, '/** One exact collection-route predicate' );
$end = strpos( $source, '/** Keep custom Woo wrappers', $start );
if ( false === $start || false === $end ) { throw new Exception( 'Missing route implementation' ); }
eval( substr( $source, $start, $end - $start ) );
foreach ( array_keys( skyyrose2_collections() ) as $slug ) {
	foreach ( array( 'default', 'template-collection.php' ) as $template ) {
		$GLOBALS['route'] = array( 'page' => true, 'slug' => $slug, 'uri' => 'collections/' . $slug, 'template' => $template );
		if ( $slug !== skyyrose2_collection_page_slug() || SKYYROSE2_DIR . '/template-collection.php' !== skyyrose2_collection_template( 'page.php' ) ) { throw new Exception( 'Canonical route failed: ' . $slug ); }
	}
	$GLOBALS['route']['uri'] = 'unrelated/' . $slug;
	if ( $slug !== skyyrose2_collection_page_slug() ) { throw new Exception( 'Explicit supported template failed' ); }
	$GLOBALS['route']['template'] = 'default';
	if ( '' !== skyyrose2_collection_page_slug() || 'page.php' !== skyyrose2_collection_template( 'page.php' ) ) { throw new Exception( 'Unrelated same-slug page leaked' ); }
	$GLOBALS['route']['page'] = false;
	$GLOBALS['route']['uri'] = 'collections/' . $slug;
	if ( '' !== skyyrose2_collection_page_slug() ) { throw new Exception( 'Non-page route leaked' ); }
}
$GLOBALS['route'] = array( 'page' => true, 'slug' => 'unknown', 'uri' => 'collections/unknown', 'template' => 'template-collection.php' );
if ( '' !== skyyrose2_collection_page_slug() ) { throw new Exception( 'Unknown collection promoted' ); }
echo "PASS shared collection routes, explicit assignments, automatic child routes and unrelated route isolation\n";
