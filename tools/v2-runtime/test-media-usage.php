<?php
/** Exact additional roles require their own source-bound owner grant. */
if ( 'tamper-child' === ( $argv[1] ?? '' ) ) {
	// Child: the gate's root is a const, so on-disk tamper cases run against a temp copy in their own process.
	define( 'ABSPATH', __DIR__ );
	define( 'SKYYROSE2_DIR', $argv[2] );
	define( 'SKYYROSE2_URI', 'https://theme.invalid' );
	function add_filter( ...$args ) {} function add_action( ...$args ) {}
	require $argv[3];
	$assets = skyyrose2_media_inventory()['assets'];
	$roles = array();
	foreach ( skyyrose2_media_inventory()['usage_adoptions'] as $relative => $binding ) { $roles[ $relative ] = skyyrose2_media_usage_roles( $relative, $assets[ $relative ] ); }
	echo json_encode( $roles );
	exit( 0 );
}
ob_start(); require __DIR__ . '/test-pdp-approved-fronts.php'; ob_end_clean();
function esc_attr( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_url( $value ) { return esc_attr( $value ); }
function skyyrose2_presentation_registry() { return $GLOBALS['presentation']; }
$negatives = 0;
function check_negative( $condition, $message ) { check_front( $condition, $message ); ++$GLOBALS['negatives']; }
$counts = array( 'pdp_on_model_front' => 0, 'collection_hero' => 0, 'collection_story' => 0, 'merchandise_scene' => 0 );
foreach ( skyyrose2_media_inventory()['usage_adoptions'] as $relative => $binding ) {
	$record = skyyrose2_media_inventory()['assets'][ $relative ];
	foreach ( skyyrose2_media_usage_roles( $relative, $record ) as $role ) {
		check_front( skyyrose2_media_path_allowed( $relative, $role, $record['skus'][0] ), 'Current original admits its exact additional use' );
		++$counts[ $role ];
	}
	$bad = $record; $bad['skus'] = array( 'unknown-001' );
	check_negative( ! skyyrose2_media_usage_roles( $relative, $bad ), 'Wrong SKU rejected' );
	$bad = $record; $bad['collections'] = array( 'unknown' );
	check_negative( ! skyyrose2_media_usage_roles( $relative, $bad ), 'Wrong collection rejected' );
	$bad = $record; $bad['sha256'] = str_repeat( '0', 64 );
	check_negative( ! skyyrose2_media_record_allowed( $relative, $bad ), 'Changed source rejected' );
	check_negative( ! skyyrose2_media_path_allowed( $relative, 'production_publish' ), 'Unknown use rejected' );
	if ( 'FOUNDER_ACCEPTED' === $record['status'] ) { check_negative( ! skyyrose2_founder_card_allowed( $relative, $record, 'pdp_on_model_front' ), 'Old card receipt alone remains card-only' ); }
}
check_front( $counts === array( 'pdp_on_model_front' => 15, 'collection_hero' => 4, 'collection_story' => 4, 'merchandise_scene' => 3 ), 'Exact 26 new uses' );
foreach ( array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ) as $collection ) {
	foreach ( array( 'collection_hero', 'collection_story', 'merchandise_scene' ) as $role ) {
		$media = skyyrose2_collection_media( $collection, $role );
		if ( 'kids-capsule' === $collection && 'merchandise_scene' === $role ) { check_negative( ! $media, 'No invented Kids preorder slot' ); continue; }
		check_front( $media && $media['collection'] === $collection && $media['role'] === $role, 'Runtime resolves the exact canonical collection placement' );
		$pre = $GLOBALS['presentation']['products'][ $media['sku'] ]['is_preorder'];
		check_front( 'merchandise_scene' === $role ? $pre : ! $pre, 'Only preorder merchandise enters reserve; hero and story use standard merchandise' );
	}
}
// On-disk tamper: grant and authority bytes are copied to a temp theme root, altered, and must stop granting.
$gate = SKYYROSE2_DIR . '/inc/v2-media-eligibility.php';
$root = sys_get_temp_dir() . '/sr2-usage-tamper-' . getmypid() . '-' . bin2hex( random_bytes( 4 ) );
$reviews = $root . '/data/v2-media-reviews';
mkdir( $reviews, 0700, true );
$root = realpath( $root );
register_shutdown_function( function () use ( $root ) { array_map( 'unlink', glob( $root . '/data/v2-media-reviews/*' ) ); @unlink( $root . '/data/v2-media-eligibility.json' ); @rmdir( $root . '/data/v2-media-reviews' ); @rmdir( $root . '/data' ); @rmdir( $root ); } );
copy( SKYYROSE2_DIR . '/data/v2-media-eligibility.json', $root . '/data/v2-media-eligibility.json' );
foreach ( glob( SKYYROSE2_DIR . '/data/v2-media-reviews/*.json' ) as $file ) { copy( $file, $reviews . '/' . basename( $file ) ); }
$tamper_roles = function () use ( $root, $gate ) {
	$out = shell_exec( escapeshellarg( PHP_BINARY ) . ' ' . escapeshellarg( __FILE__ ) . ' tamper-child ' . escapeshellarg( $root ) . ' ' . escapeshellarg( $gate ) );
	$roles = json_decode( (string) $out, true );
	check_front( is_array( $roles ) && 22 === count( $roles ), 'Tamper child evaluated every usage adoption' );
	return $roles;
};
$expected = array();
foreach ( skyyrose2_media_inventory()['usage_adoptions'] as $relative => $binding ) { $expected[ $relative ] = skyyrose2_media_usage_roles( $relative, skyyrose2_media_inventory()['assets'][ $relative ] ); }
check_front( $tamper_roles() === $expected && 26 === array_sum( array_map( 'count', $expected ) ), 'Positive control: the pristine temp copy grants exactly the real roles' );
$tamper = function ( $relative, $edit ) use ( $root, $tamper_roles ) {
	$file = $root . '/' . $relative;
	$original = file_get_contents( $file );
	file_put_contents( $file, $edit( $original ) );
	$roles = $tamper_roles();
	file_put_contents( $file, $original );
	return $roles;
};
$first = array_key_first( $expected );
$grant = skyyrose2_media_inventory()['usage_adoptions'][ $first ]['path'];
$authority = json_decode( file_get_contents( SKYYROSE2_DIR . '/' . $grant ), true )['authorization']['path'];
$production = function ( $bytes ) { return str_replace( 'https://staging-7e48-skyyrose.wpcomstaging.com', 'https://skyyrose.co', $bytes ); };
$widen = function ( $bytes ) { $doc = json_decode( $bytes, true ); $doc['roles'] = array( 'pdp_on_model_front', 'collection_hero', 'collection_story', 'merchandise_scene' ); return json_encode( $doc, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES ) . "\n"; };
$byte = function ( $bytes ) { return $bytes . ' '; };
foreach ( array( 'byte' => $byte, 'roles widened' => $widen, 'target moved to production' => $production ) as $label => $edit ) {
	$roles = $tamper( $grant, $edit );
	check_negative( array() === $roles[ $first ], 'Tampered grant (' . $label . ') rejected' );
	$others = $expected; unset( $others[ $first ] ); $rest = $roles; unset( $rest[ $first ] );
	check_front( $rest === $others, 'Grant tamper is scoped to its own adoption' );
}
foreach ( array( 'byte' => $byte, 'target moved to production' => $production ) as $label => $edit ) {
	$roles = $tamper( $authority, $edit );
	foreach ( $roles as $relative => $value ) { check_negative( array() === $value, 'Tampered authority (' . $label . ') revokes ' . $relative ); }
}
check_front( $tamper_roles() === $expected, 'Restored copy grants the real roles again' );
echo json_encode( array( 'status' => 'PASS', 'additional_roles' => $counts, 'current_pdp_fronts' => $displayed['pdp_on_model_front'], 'negative_cases' => $negatives ), JSON_PRETTY_PRINT ) . "\n";
