<?php
/** Synthetic contract tests; fixture bytes are never production fashion assets. */
define( 'ABSPATH', '/tmp/' );
$source = dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2/inc/v2-media-eligibility.php';
$fixture = sys_get_temp_dir() . '/skyyrose-v2-media-' . bin2hex( random_bytes( 6 ) );
mkdir( $fixture . '/assets/test', 0700, true ); mkdir( $fixture . '/data/v2-media-reviews', 0700, true );
define( 'SKYYROSE2_DIR', $fixture ); define( 'SKYYROSE2_URI', 'https://example.test/v2' );
function add_action( ...$args ) {} function add_filter( ...$args ) {}
function check_media( $result, $label ) { if ( ! $result ) { throw new RuntimeException( $label ); } echo "PASS: $label\n"; }
file_put_contents( $fixture . '/assets/test/new.png', 'synthetic-new-bytes' );
file_put_contents( $fixture . '/assets/test/old.webp', 'synthetic-retired-bytes' );
file_put_contents( $fixture . '/assets/test/mark.webp', 'synthetic-housemark-bytes' );
$hash = hash_file( 'sha256', $fixture . '/assets/test/new.png' );
$receipt = array( 'asset_sha256' => $hash, 'reviewer' => 'independent-test-reviewer', 'verdict' => 'PASS', 'v2_originality_pass' => true, 'product_fidelity_pass' => true, 'roles' => array( 'card_front' ), 'skus' => array( 'sg-009' ), 'collections' => array( 'signature' ), 'production_id' => 'fixture-only', 'producer' => 'test-producer' );
file_put_contents( $fixture . '/data/v2-media-reviews/new.json', json_encode( $receipt ) );
$record = array( 'sha256' => $hash, 'kind' => 'photograph', 'origin' => 'V2_ORIGINAL_20261002', 'status' => 'INDEPENDENT_VISUAL_PASS', 'production_id' => 'fixture-only', 'producer' => 'test-producer', 'roles' => array( 'card_front' ), 'skus' => array( 'sg-009' ), 'collections' => array( 'signature' ), 'review' => array( 'path' => 'data/v2-media-reviews/new.json', 'sha256' => hash_file( 'sha256', $fixture . '/data/v2-media-reviews/new.json' ), 'reviewer' => 'independent-test-reviewer', 'verdict' => 'PASS' ) );
$forged_mark = array( 'sha256' => hash_file( 'sha256', $fixture . '/assets/test/mark.webp' ), 'kind' => 'housemark', 'status' => 'CANONICAL_EXACT_BYTES', 'authority_reference' => 'synthetic canonical fixture', 'roles' => array( 'housemark' ) );
$canonical_source = dirname( $source ) . '/../data/v2-canonical-media.json';
copy( $canonical_source, $fixture . '/data/v2-canonical-media.json' );
$canonical = json_decode( file_get_contents( $canonical_source ), true );
$mark_path = 'assets/sot/brand/skyyrose-logo-still-384w.webp';
$mark = $canonical['assets'][ $mark_path ];
mkdir( $fixture . '/assets/sot/brand', 0700, true );
copy( dirname( $source ) . '/../' . $mark_path, $fixture . '/' . $mark_path );
$art_path = 'assets/images/house-monument-20260928.webp';
$art = $canonical['assets'][ $art_path ];
$art_receipt = $art['restoration_receipt']['path'];
mkdir( $fixture . '/assets/images', 0700, true );
copy( dirname( $source ) . '/../' . $art_path, $fixture . '/' . $art_path );
copy( dirname( $source ) . '/../' . $art_receipt, $fixture . '/' . $art_receipt );
file_put_contents( $fixture . '/data/v2-media-eligibility.json', json_encode( array( 'schema' => 'skyyrose.v2.media-eligibility.v1', 'assets' => array( 'assets/test/new.png' => $record, $mark_path => $mark, $art_path => $art ), 'disallowed_legacy_sha256' => array( hash_file( 'sha256', $fixture . '/assets/test/old.webp' ) ) ) ) );
require $source;
try {
check_media( skyyrose2_media_path_allowed( 'assets/test/new.png', 'card_front', 'sg-009' ), 'New independently reviewed exact SKU and role allowed' );
check_media( skyyrose2_media_uri( 'assets/test/new.png', 'card_front', 'sg-009' ) === SKYYROSE2_URI . '/assets/test/new.png?v=' . $hash, 'Public image cache key is bound to the verified bytes' );
check_media( skyyrose2_media_url( SKYYROSE2_URI . '/assets/test/new.png?v=stale&other=old' ) === SKYYROSE2_URI . '/assets/test/new.png?v=' . $hash, 'Stale cache versions normalize to current verified bytes' );
check_media( skyyrose2_media_url( skyyrose2_media_uri( 'assets/test/new.png' ) ) === skyyrose2_media_uri( 'assets/test/new.png' ), 'Cache normalization is idempotent' );
$attachment = skyyrose2_media_attachment_src( array( SKYYROSE2_URI . '/assets/test/new.png?v=old', 1, 2, false ) );
check_media( $attachment === array( skyyrose2_media_uri( 'assets/test/new.png' ), 1, 2, false ), 'Native attachment source normalizes cache identity and retains dimensions' );
$background = skyyrose2_media_filter_html( '<div style="background:url(' . SKYYROSE2_URI . '/assets/test/new.png?v=old)"></div>' );
check_media( str_contains( $background, 'new.png?v=' . $hash ) && ! str_contains( $background, '?v=old' ), 'Accepted CSS backgrounds carry the exact byte cache identity' );
check_media( ! skyyrose2_media_path_allowed( 'assets/test/new.png', 'card_front', 'lh-004' ), 'Wrong SKU blocked' );
check_media( ! skyyrose2_media_path_allowed( 'assets/test/new.png', 'pdp_back', 'sg-009' ), 'Wrong view role blocked' );
check_media( ! skyyrose2_media_path_allowed( 'assets/test/old.webp' ), 'Historical approval cannot reopen retired media' );
check_media( ! skyyrose2_media_url( 'https://example.test/wp-content/uploads/old.jpg' ), 'External Woo attachment fallback blocked' );
check_media( skyyrose2_media_path_allowed( $mark_path, 'housemark' ), 'Exact inventoried housemark allowed' );
check_media( skyyrose2_media_path_allowed( $art_path, 'homepage_hero' ), 'Exact unchanged V2 homepage art restored under separate authority' );
check_media( ! skyyrose2_media_path_allowed( $art_path, 'card_front' ), 'Homepage art cannot become a product card' );
check_media( ! skyyrose2_media_path_allowed( $art_path, 'homepage_hero', 'lh-004' ), 'Homepage art cannot claim a SKU' );
$bad_art = $art; $bad_art['restoration_receipt']['sha256'] = str_repeat( '0', 64 );
check_media( ! skyyrose2_media_record_allowed( $art_path, $bad_art, 'homepage_hero' ), 'Changed homepage restoration authority blocked' );
file_put_contents( $fixture . '/' . $art_path, 'drift' );
check_media( ! skyyrose2_media_path_allowed( $art_path, 'homepage_hero' ), 'Changed homepage art pixels blocked' );
copy( dirname( $source ) . '/../' . $art_path, $fixture . '/' . $art_path );
check_media( ! skyyrose2_media_record_allowed( 'assets/test/mark.webp', $forged_mark ), 'Unregistered canonical label cannot exempt imagery' );
$forged_old = $forged_mark; $forged_old['sha256'] = hash_file( 'sha256', $fixture . '/assets/test/old.webp' );
check_media( ! skyyrose2_media_record_allowed( 'assets/test/old.webp', $forged_old ), 'Legacy hash blocked even when relabelled housemark' );
foreach ( array( 'hash', 'review', 'producer', 'origin', 'path' ) as $case ) {
 $bad = $record; $path = 'assets/test/new.png';
 if ( 'hash' === $case ) { $bad['sha256'] = str_repeat( '0', 64 ); }
 if ( 'review' === $case ) { unset( $bad['review'] ); }
 if ( 'producer' === $case ) { $bad['producer'] = $bad['review']['reviewer']; }
 if ( 'origin' === $case ) { $bad['origin'] = 'retained-v1'; }
 if ( 'path' === $case ) { $path = 'assets/../test/new.png'; }
 check_media( ! skyyrose2_media_record_allowed( $path, $bad ), 'Reject ' . $case );
}
foreach ( array( 'roles', 'skus', 'collections', 'production_id', 'producer' ) as $binding ) {
 $changed = $record;
 $changed[ $binding ] = in_array( $binding, array( 'roles', 'skus', 'collections' ), true ) ? array( 'different-binding' ) : 'different-identity';
 check_media( ! skyyrose2_media_record_allowed( 'assets/test/new.png', $changed ), 'Independent receipt rejects altered ' . $binding );
}
$malformed = $record; $malformed['collections'] = 'signature';
check_media( ! skyyrose2_media_record_allowed( 'assets/test/new.png', $malformed ), 'Scalar binding fails closed' );
foreach ( array( 'roles', 'skus', 'collections' ) as $binding ) {
 $object_record = $record; $object_receipt = $receipt;
 $object_record[ $binding ] = array( 'slot' => $record[ $binding ][0] );
 $object_receipt[ $binding ] = $object_record[ $binding ];
 file_put_contents( $fixture . '/data/v2-media-reviews/new.json', json_encode( $object_receipt ) );
 $object_record['review']['sha256'] = hash_file( 'sha256', $fixture . '/data/v2-media-reviews/new.json' );
 check_media( ! skyyrose2_media_record_allowed( 'assets/test/new.png', $object_record ), 'Object binding fails closed for ' . $binding );
}
file_put_contents( $fixture . '/data/v2-media-reviews/new.json', json_encode( $receipt ) );
$html = '<img src="https://example.test/wp-content/uploads/old.jpg" srcset="https://example.test/v2/assets/test/old.webp 400w"><video poster="https://example.test/v2/assets/test/old.webp"><source src="https://example.test/v2/assets/test/old.webp"></video><img src="https://example.test/v2/assets/test/new.png"><div style="background:url(https://example.test/v2/assets/test/old.webp)"></div><script src="https://example.test/app.js"></script>';
$clean = skyyrose2_media_filter_html( $html );
check_media( ! str_contains( $clean, 'old.webp' ) && ! str_contains( $clean, 'uploads/old' ), 'Raw image, srcset, poster, source and CSS background blocked' );
check_media( str_contains( $clean, 'new.png' ) && str_contains( $clean, 'app.js' ), 'Reviewed media and scripts retained' );
$data = skyyrose2_media_variation( array( 'image' => array( 'src' => 'https://example.test/uploads/old.jpg', 'full_src' => 'https://example.test/uploads/old.jpg' ), 'image_id' => 42 ) );
check_media( ! $data['image'] && 0 === $data['image_id'], 'Variation full image cannot reopen attachment' );
file_put_contents( $fixture . '/assets/test/new.png', 'drift' );
check_media( ! skyyrose2_media_path_allowed( 'assets/test/new.png' ), 'Live bytes drift blocks display' );
} finally {
	foreach ( array( '/assets/test/new.png', '/assets/test/old.webp', '/assets/test/mark.webp', '/data/v2-media-reviews/new.json', '/data/v2-media-eligibility.json', '/data/v2-canonical-media.json', '/' . $mark_path, '/' . $art_path, '/' . $art_receipt ) as $path ) { unlink( $fixture . $path ); }
 rmdir( $fixture . '/assets/images' );
 rmdir( $fixture . '/assets/sot/brand' ); rmdir( $fixture . '/assets/sot' ); rmdir( $fixture . '/assets/test' ); rmdir( $fixture . '/assets' ); rmdir( $fixture . '/data/v2-media-reviews' ); rmdir( $fixture . '/data' ); rmdir( $fixture );
}
