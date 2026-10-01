<?php
/** Offline enqueue regression: consent assets must invalidate browser caches. */
define( 'ABSPATH', __DIR__ );
define( 'SCRIPT_DEBUG', 'debug' === ( $argv[1] ?? '' ) );
define( 'SKYYROSE_VERSION', 'unchanged-theme-version' );
define( 'SKYYROSE_ASSETS_URI', 'https://fixture.test/assets' );
define( 'SKYYROSE_DIR', sys_get_temp_dir() . '/skyyrose-cache-' . bin2hex( random_bytes( 8 ) ) );
function add_action( ...$args ) {}
function skyyrose_see_is_module_active( $module ) { return true; }
function skyyrose_get_current_template_slug() { return 'collection-standalone'; }
function wp_enqueue_script( $handle, $src, $dependencies, $version, $args ) {
	$GLOBALS['scripts'][ $handle ] = array( 'src' => $src, 'version' => $version );
}
function wp_enqueue_style( ...$args ) {}
require dirname( __DIR__, 2 ) . '/inc/enqueue-phases.php';
$directory = SKYYROSE_DIR . '/assets/js';
mkdir( $directory, 0700, true );
$files = array();
$checks = 0;
function cache_check( $condition, $message ) {
	global $checks;
	++$checks;
	if ( ! $condition ) { throw new RuntimeException( $message ); }
}
try {
	foreach ( array( 'experience-analyzer', 'personalization' ) as $name ) {
		foreach ( array( '.js' => 1700000000, '.min.js' => 1700000100 ) as $suffix => $stamp ) {
			$file = $directory . '/' . $name . $suffix;
			$files[] = $file;
			file_put_contents( $file, '// Synthetic cache fixture' );
			touch( $file, $stamp );
		}
	}
	skyyrose_enqueue_phase3_experience_analyzer();
	skyyrose_enqueue_phase4_assets();
	foreach ( array( 'experience-analyzer', 'personalization' ) as $name ) {
		$script = $GLOBALS['scripts'][ 'skyyrose-' . $name ];
		$suffix = SCRIPT_DEBUG ? '.js' : '.min.js';
		cache_check( str_ends_with( $script['src'], $name . $suffix ), 'Select source/minified asset correctly' );
		cache_check( $script['version'] === (string) ( SCRIPT_DEBUG ? 1700000000 : 1700000100 ), 'Version selected asset, not theme or other variant' );
		touch( $directory . '/' . $name . $suffix, 1700000200 );
	}
	clearstatcache();
	skyyrose_enqueue_phase3_experience_analyzer();
	skyyrose_enqueue_phase4_assets();
	foreach ( array( 'experience-analyzer', 'personalization' ) as $name ) {
		cache_check( '1700000200' === $GLOBALS['scripts'][ 'skyyrose-' . $name ]['version'], 'Asset update changes cache key without theme version bump' );
		unlink( $directory . '/' . $name . '.min.js' );
	}
	clearstatcache();
	skyyrose_enqueue_phase3_experience_analyzer();
	skyyrose_enqueue_phase4_assets();
	foreach ( array( 'experience-analyzer', 'personalization' ) as $name ) {
		$script = $GLOBALS['scripts'][ 'skyyrose-' . $name ];
		cache_check( str_ends_with( $script['src'], $name . '.js' ), 'Missing minified file selects source' );
		cache_check( $script['version'] === (string) filemtime( $directory . '/' . $name . '.js' ), 'Fallback versions the source file' );
	}
	echo "PASS: {$checks} cache checks (" . ( SCRIPT_DEBUG ? 'debug' : 'production' ) . ", offline; authentication N/A).\n";
} finally {
	foreach ( $files as $file ) { if ( file_exists( $file ) ) { unlink( $file ); } }
	rmdir( $directory );
	rmdir( SKYYROSE_DIR . '/assets' );
	rmdir( SKYYROSE_DIR );
}
