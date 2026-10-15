<?php
/** Behavioral regressions for contact throttling and non-destructive import. */
define( 'ABSPATH', __DIR__ );
define( 'OBJECT', 'OBJECT' );
function add_action() {}
function __( $value, $domain = '' ) { return $value; }
function sanitize_file_name( $value ) { return $value; }
function get_theme_file_path( $value ) { return dirname( __DIR__ ) . '/' . $value; }
function is_wp_error( $value ) { return $value instanceof WP_Error; }
function wp_salt( $scheme ) { return 'synthetic-test-only'; }
class WP_Post { public $ID = 17; }
class WP_Error {}
function get_page_by_path() { return new WP_Post(); }
function get_page_template_slug() { return $GLOBALS['template']; }
function get_post_meta() { return $GLOBALS['owned']; }
function update_post_meta( $id, $key, $value ) { $GLOBALS['writes'][] = array( $id, $key, $value ); }
require dirname( __DIR__ ) . '/inc/demo-import.php';
$definition = array( 'path' => 'collections/black-rose', 'title' => 'Black Rose', 'template' => 'template-collection.php' );
foreach ( array(
	array( '', 'merchant-custom.php', 0 ),
	array( '', 'default', 0 ),
	array( '1.0.0', 'merchant-custom.php', 0 ),
	array( '1.0.0', 'default', 1 ),
	array( '1.0.0', 'template-collection.php', 0 ),
) as $case ) {
	list( $owned, $template, $expected_writes ) = $case;
	$writes = array();
	$report = skyyrose2_demo_report();
	if ( 17 !== skyyrose2_demo_upsert_page( 'black-rose', $definition, 0, $report ) || count( $writes ) !== $expected_writes ) {
		throw new RuntimeException( 'Importer changed merchant ownership or repeat-import behavior.' );
	}
}
$source = file_get_contents( dirname( __DIR__ ) . '/functions.php' );
$start = strpos( $source, 'function skyyrose2_contact_rate_key()' );
$end = strpos( $source, '/** Handle client-service messages', $start );
eval( substr( $source, $start, $end - $start ) );
$_SERVER['REMOTE_ADDR'] = '192.0.2.12';
$_SERVER['HTTP_USER_AGENT'] = 'Browser A';
$first = skyyrose2_contact_rate_key();
$_SERVER['HTTP_USER_AGENT'] = 'Browser B';
$_SERVER['HTTP_X_FORWARDED_FOR'] = '192.0.2.99';
if ( $first !== skyyrose2_contact_rate_key() || str_contains( $first, '192.0.2.12' ) ) {
	throw new RuntimeException( 'Client headers bypass the throttle or raw address leaks into its key.' );
}
$_SERVER['REMOTE_ADDR'] = '192.0.2.13';
if ( $first === skyyrose2_contact_rate_key() ) {
	throw new RuntimeException( 'Independent client address shares the throttle bucket.' );
}
echo "PASS merchant-template preservation, idempotency, and header-independent contact throttle\n";
