<?php
/** Isolated missing/tampered asset and receipt regression checks; no WordPress or network. */
if ( '--probe' === ( $argv[1] ?? '' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
	define( 'SKYYROSE2_DIR', $argv[2] );
	define( 'SKYYROSE2_URI', 'https://fixture.invalid/theme' );
	function add_action( ...$args ) {}
	function add_filter( ...$args ) {}
	require SKYYROSE2_DIR . '/inc/v2-media-eligibility.php';
	$relative = 'assets/video/collection-heroes/approved/kids-capsule/runway-r10/hero.mp4';
	$uri = skyyrose2_media_uri( $relative, 'collection_hero_video' );
	echo $uri ? 'ALLOWED' : 'REFUSED';
	exit;
}
$theme = realpath( $argv[1] ?? __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2' );
if ( ! $theme ) { throw new RuntimeException( 'Theme missing' ); }
$fixture = sys_get_temp_dir() . '/kids-r10-integrity-' . bin2hex( random_bytes( 8 ) );
$paths = array(
	'inc/v2-media-eligibility.php',
	'data/v2-media-eligibility.json',
	'data/v2-media-reviews/kids-runway-r10-integration-20261023.json',
	'assets/video/collection-heroes/approved/kids-capsule/runway-r10/hero.mp4',
);
$written = array();
$dirs = array();
$results = array();
try {
	foreach ( $paths as $relative ) {
		$target = $fixture . '/' . $relative;
		$dir = dirname( $target );
		$missing = array();
		while ( ! is_dir( $dir ) ) { $missing[] = $dir; $dir = dirname( $dir ); }
		foreach ( array_reverse( $missing ) as $dir ) { mkdir( $dir ); $dirs[] = $dir; }
		if ( ! copy( $theme . '/' . $relative, $target ) ) { throw new RuntimeException( 'Fixture copy failed' ); }
		$written[] = $target;
	}
	$probe = static function () use ( $fixture ) {
		$process = proc_open( array( PHP_BINARY, __FILE__, '--probe', $fixture ), array( 1 => array( 'pipe', 'w' ), 2 => array( 'pipe', 'w' ) ), $pipes );
		if ( ! is_resource( $process ) ) { throw new RuntimeException( 'Probe unavailable' ); }
		$out = stream_get_contents( $pipes[1] ); $err = stream_get_contents( $pipes[2] );
		fclose( $pipes[1] ); fclose( $pipes[2] );
		if ( 0 !== proc_close( $process ) ) { throw new RuntimeException( $err ); }
		return $out;
	};
	if ( 'ALLOWED' !== $probe() ) { throw new RuntimeException( 'Valid fixture denied' ); }
	$results['valid_fixture'] = 'PASS';
	foreach ( array( 'receipt' => $paths[2], 'media' => $paths[3] ) as $kind => $relative ) {
		$target = $fixture . '/' . $relative;
		$original = file_get_contents( $target );
		foreach ( array( 'missing', 'tampered' ) as $variant ) {
			if ( 'missing' === $variant ) { unlink( $target ); } else { file_put_contents( $target, $original . 'INTENTIONAL_TEST_DRIFT' ); }
			if ( 'REFUSED' !== $probe() ) { throw new RuntimeException( $kind . ' ' . $variant . ' accepted' ); }
			$results[ $kind . '_' . $variant ] = 'PASS';
			file_put_contents( $target, $original );
		}
	}
} finally {
	foreach ( $written as $file ) { if ( is_file( $file ) ) { unlink( $file ); } }
	foreach ( array_reverse( $dirs ) as $dir ) { rmdir( $dir ); }
}
echo json_encode( array( 'scope' => 'ISOLATED_LOCAL_FIXTURE_NO_AUTHENTICATION', 'status' => 'PASS', 'cases' => $results ), JSON_PRETTY_PRINT ) . PHP_EOL;
