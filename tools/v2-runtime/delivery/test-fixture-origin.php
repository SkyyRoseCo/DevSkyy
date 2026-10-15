<?php
// Each mode runs in a fresh PHP process so constants/hooks cannot leak.
$mode = $argv[1] ?? 'guard';
define( 'ABSPATH', '/synthetic/' );
if ( 'disabled' !== $mode ) { define( 'SKYYROSE_V2_DELIVERY_FIXTURE', true ); }
$_SERVER['HTTP_HOST'] = 'guard' === $mode ? '127.0.0.1:18303' : '127.0.0.1:18308';
$hooks = array();
function add_filter( $name, $callback, $priority ) { global $hooks; $hooks[ $name ] = $callback; }
function check_delivery( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
require __DIR__ . '/fixture-origin.php';
if ( 'enabled' !== $mode ) {
	check_delivery( ! $hooks, 'Disabled/wrong-host adapter must register zero filters.' );
} else {
	check_delivery( 'http://127.0.0.1:18308' === $hooks['pre_option_home'](), 'Home origin' );
	check_delivery( 'http://127.0.0.1:18308' === $hooks['pre_option_siteurl'](), 'Site origin' );
	$rewrite = $hooks['content_url'];
	check_delivery( 'http://127.0.0.1:18308/a' === $rewrite( 'http://127.0.0.1:18303/a' ), 'Exact origin must adapt.' );
	foreach ( array( 'https://127.0.0.1:18303/a', 'http://127.0.0.1:183030/a', 'http://example.com/a', 'prefix http://127.0.0.1:18303/a' ) as $url ) {
		check_delivery( $url === $rewrite( $url ), 'Unknown authority/text must remain unchanged.' );
	}
	$uploads = array( 'url' => 'http://127.0.0.1:18303/uploads/a', 'baseurl' => 'http://127.0.0.1:18303/uploads', 'basedir' => '/exact/physical/path', 'path' => '/exact/physical/path/a', 'error' => false );
	$result = $hooks['upload_dir']( $uploads );
	check_delivery( 'http://127.0.0.1:18308/uploads' === $result['baseurl'] && $uploads['basedir'] === $result['basedir'] && $uploads['path'] === $result['path'] && false === $result['error'], 'Only URL fields may change.' );
}
echo 'PASS ', $mode, "\n";
