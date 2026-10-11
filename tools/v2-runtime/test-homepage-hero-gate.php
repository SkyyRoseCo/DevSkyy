<?php
/**
 * Homepage hero still through the real V2 media gate.
 *
 * `real` runs the shipped gate against the shipped theme directory (catches a
 * wrong canonical pin or an unshipped receipt). Every other mode runs in its own
 * process on a disposable fixture copy and must fail closed. Run with no argument
 * to execute every mode and tally the results.
 */
$theme = dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2';
$hero = 'assets/images/house-monument-20260928.webp';
$hero_sha = '05e9890ba85971569b7a422b892e3db3d51ae53ac6efb6bdd2d55f85c7859811';
$receipt = 'data/v2-media-reviews/homepage-art-restoration-20261006.json';
$mark = 'assets/sot/brand/skyyrose-logo-still-384w.webp';
$font = 'assets/sot/fonts/archivo-latin.woff2';
$mode = $argv[1] ?? 'all';

if ( 'all' === $mode ) {
	$modes = array( 'real', 'fixture-baseline', 'receipt-bytes', 'receipt-missing', 'receipt-symlink', 'binding-sha', 'receipt-content', 'hero-drift', 'canonical-byte', 'wrong-role', 'claims-sku', 'roles-extended' );
	$failed = 0;
	foreach ( $modes as $each ) {
		exec( escapeshellarg( PHP_BINARY ) . ' ' . escapeshellarg( __FILE__ ) . ' ' . escapeshellarg( $each ) . ' 2>&1', $out, $code );
		echo implode( "\n", $out ) . "\n";
		$out = array();
		if ( 0 !== $code ) { ++$failed; }
	}
	echo 0 === $failed ? "HERO GATE: PASS (" . count( $modes ) . " modes)\n" : "HERO GATE: FAIL ($failed of " . count( $modes ) . " modes)\n";
	exit( 0 === $failed ? 0 : 1 );
}

$GLOBALS['sr2_failures'] = 0;
function check_hero( $result, $label ) {
	global $mode;
	if ( $result ) { echo "PASS [$mode]: $label\n"; return; }
	echo "FAIL [$mode]: $label\n";
	++$GLOBALS['sr2_failures'];
}

if ( 'real' === $mode ) {
	$dir = $theme;
} else {
	$dir = sys_get_temp_dir() . '/sr2-hero-gate-' . bin2hex( random_bytes( 8 ) );
	foreach ( array( 'data/v2-media-eligibility.json', 'data/v2-canonical-media.json', $receipt, $hero, $mark, $font ) as $relative ) {
		if ( ! is_dir( dirname( $dir . '/' . $relative ) ) ) { mkdir( dirname( $dir . '/' . $relative ), 0700, true ); }
		if ( is_file( $theme . '/' . $relative ) ) { copy( $theme . '/' . $relative, $dir . '/' . $relative ); }
	}
}
define( 'ABSPATH', $dir . '/' );
define( 'SKYYROSE2_DIR', $dir );
define( 'SKYYROSE2_URI', 'https://example.test/v2' );
function add_action( ...$args ) {}
function add_filter( ...$args ) {}
function is_admin() { return false; }

// Mutations happen before the gate loads its request-cached inventory.
$eligibility_file = $dir . '/data/v2-media-eligibility.json';
$inventory = json_decode( (string) file_get_contents( $eligibility_file ), true );
$record = $inventory['assets'][ $hero ] ?? array();
switch ( $mode ) {
	case 'receipt-bytes':
		file_put_contents( $dir . '/' . $receipt, ' ', FILE_APPEND );
		break;
	case 'receipt-missing':
		@unlink( $dir . '/' . $receipt );
		break;
	case 'receipt-symlink':
		rename( $dir . '/' . $receipt, $dir . '/data/receipt-elsewhere.json' );
		symlink( $dir . '/data/receipt-elsewhere.json', $dir . '/' . $receipt );
		break;
	case 'binding-sha':
		$inventory['assets'][ $hero ]['restoration_receipt']['sha256'] = str_repeat( '0', 64 );
		break;
	case 'receipt-content':
		// A different request text with its binding re-matched to the new bytes.
		$forged = json_decode( (string) @file_get_contents( $theme . '/' . $receipt ), true ) ?: array();
		$forged['user_request'] = 'swap the homepage hero';
		$forged_path = 'data/v2-media-reviews/homepage-art-forged.json';
		file_put_contents( $dir . '/' . $forged_path, json_encode( $forged ) );
		$inventory['assets'][ $hero ]['restoration_receipt'] = array( 'path' => $forged_path, 'sha256' => hash_file( 'sha256', $dir . '/' . $forged_path ) );
		break;
	case 'hero-drift':
		file_put_contents( $dir . '/' . $hero, 'drift', FILE_APPEND );
		break;
	case 'canonical-byte':
		file_put_contents( $dir . '/data/v2-canonical-media.json', "\n", FILE_APPEND );
		break;
	case 'roles-extended':
		$inventory['assets'][ $hero ]['roles'] = array( 'homepage_hero', 'card_front' );
		break;
}
if ( 'real' !== $mode ) { file_put_contents( $eligibility_file, json_encode( $inventory ) ); }

require $theme . '/inc/v2-media-eligibility.php';

$expected = SKYYROSE2_URI . '/' . $hero;
switch ( $mode ) {
	case 'real':
	case 'fixture-baseline':
		check_hero( is_file( $dir . '/' . $receipt ), 'Restoration receipt exists in the theme' );
		check_hero( hash_equals( $hero_sha, (string) @hash_file( 'sha256', $dir . '/' . $hero ) ), 'Hero bytes are the founder-ruled still' );
		check_hero( $expected === skyyrose2_media_uri( $hero ), 'editorial-hero.php call (no role) renders the hero' );
		check_hero( $expected === skyyrose2_media_uri( $hero, 'homepage_hero' ), 'homepage_hero role renders the hero' );
		check_hero( '' !== skyyrose2_media_uri( $mark, 'housemark' ), 'Registered housemark still admitted under the new pin' );
		check_hero( '' !== skyyrose2_media_uri( $font, 'font' ), 'Registered font still admitted under the new pin' );
		break;
	case 'canonical-byte':
		check_hero( '' === skyyrose2_media_uri( $hero ), 'Changed canonical inventory blocks the hero' );
		check_hero( '' === skyyrose2_media_uri( $mark, 'housemark' ), 'Changed canonical inventory blocks every canonical asset' );
		break;
	case 'wrong-role':
		check_hero( '' === skyyrose2_media_uri( $hero, 'card_front' ), 'Hero cannot become a product card' );
		check_hero( '' === skyyrose2_media_uri( $hero, 'collection_hero' ), 'Hero cannot become a collection hero' );
		break;
	case 'claims-sku':
		check_hero( '' === skyyrose2_media_uri( $hero, 'homepage_hero', 'br-001' ), 'Hero cannot claim a SKU' );
		check_hero( '' === skyyrose2_media_uri( $hero, '', 'lh-004' ), 'Hero cannot claim a SKU without a role' );
		break;
	default:
		check_hero( '' === skyyrose2_media_uri( $hero ), 'Tampered hero authority fails closed' );
		check_hero( '' === skyyrose2_media_uri( $hero, 'homepage_hero' ), 'Tampered hero authority fails closed for its role' );
}
if ( 'real' !== $mode ) { exec( 'rm -rf ' . escapeshellarg( $dir ) ); }
exit( $GLOBALS['sr2_failures'] ? 1 : 0 );
