<?php
/** Offline authoring adapter: execute the real source media gate, never WordPress. */
if ( PHP_SAPI !== 'cli' || ! in_array( count( $argv ), array( 2, 3 ), true ) || ! is_file( $argv[1] . '/inc/v2-media-eligibility.php' ) || ( isset( $argv[2] ) && 'runtime' !== $argv[2] ) ) { exit( 2 ); }
define( 'ABSPATH', __DIR__ . '/' );
define( 'SKYYROSE2_DIR', realpath( $argv[1] ) );
if ( ! isset( $argv[2] ) ) { define( 'SKYYROSE2_MEDIA_AUTHORING', true ); }
function add_action( ...$args ) {}
function add_filter( ...$args ) {}
require SKYYROSE2_DIR . '/inc/v2-media-eligibility.php';
$inventory = skyyrose2_media_inventory();
$allowed = array();
foreach ( $inventory['assets'] as $path => $record ) {
	if ( skyyrose2_media_record_allowed( $path, $record ) ) {
		$roles = skyyrose2_media_effective_roles( $path, $record );
		if ( $roles ) { $allowed[ $path ] = $roles; }
	}
}
echo json_encode( $allowed, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES );
