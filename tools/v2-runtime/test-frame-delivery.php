<?php
/** Each invocation has a fresh request cache and a disposable local fixture. */
$mode = $argv[1] ?? 'valid';
$theme = dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2';
$fixture = sys_get_temp_dir() . '/sr2-frame-' . bin2hex( random_bytes( 8 ) );
mkdir( $fixture, 0700 );
define( 'ABSPATH', $fixture );
define( 'SKYYROSE2_DIR', $fixture );
define( 'SKYYROSE2_URI', 'https://example.test/theme' );
function skyyrose2_sot_asset_uri( $path ) { return SKYYROSE2_URI . '/assets/sot/' . $path; }
function skyyrose2_collections() { return array( 'signature' => array( 'portal_statue' => array( 'small' => 'images/product-card-portals/signature-portal-statue-640w.webp' ) ) ); }
$files = array( 'assets/derived/card-frames/manifest.json', 'assets/derived/card-frames/signature-384w.webp', 'assets/sot/images/product-card-portals/signature-portal-statue-640w.webp', 'assets/derived/card-frames/signature-360w.webp' );
try {
	foreach ( $files as $relative ) {
		$target = $fixture . '/' . $relative;
		if ( ! is_dir( dirname( $target ) ) ) { mkdir( dirname( $target ), 0700, true ); }
		if ( ! copy( $theme . '/' . $relative, $target ) ) { throw new RuntimeException( 'Missing generated fixture ' . $relative ); }
	}
	$manifest = $fixture . '/' . $files[0];
	$derived = $fixture . '/' . $files[1];
	$source = $fixture . '/' . $files[2];
	$narrow = $fixture . '/' . $files[3];
	$data = json_decode( file_get_contents( $manifest ), true );
	switch ( $mode ) {
		case 'valid': break;
		case 'narrow-missing': unlink( $narrow ); break;
		case 'narrow-derived': file_put_contents( $narrow, 'changed' ); break;
		case 'narrow-path': $data['collections']['signature']['narrow_rendition']['src'] = '../escape.webp'; break;
		case 'narrow-dimensions': $data['collections']['signature']['narrow_rendition']['height'] = 1; break;
		case 'narrow-symlink': unlink( $narrow ); symlink( $source, $narrow ); break;
		case 'missing': unlink( $derived ); break;
		case 'source': file_put_contents( $source, 'changed' ); break;
		case 'derived': file_put_contents( $derived, 'changed' ); break;
		case 'schema': $data['schema'] = 'unknown'; break;
		case 'path': $data['collections']['signature']['rendition']['src'] = '../escape.webp'; break;
		case 'dimensions': $data['collections']['signature']['rendition']['height'] = 1; break;
		case 'malformed': $data = 'not an array'; break;
		case 'ancestor':
			rename( $fixture . '/assets/derived', $fixture . '/moved' );
			symlink( $fixture . '/moved', $fixture . '/assets/derived' );
			break;
		case 'symlink': unlink( $derived ); symlink( $source, $derived ); break;
		default: throw new RuntimeException( 'Unknown test mode' );
	}
	file_put_contents( $manifest, json_encode( $data ) );
	require $theme . '/inc/frame-delivery.php';
	$result = skyyrose2_archive_frame_delivery( 'signature' );
	if ( 'valid' === $mode || str_starts_with( $mode, 'narrow-' ) ) {
		if ( str_contains( $result['srcset'] ?? '', 'signature-360w.webp 360w' ) !== ( 'valid' === $mode ) ) { throw new RuntimeException( 'Narrow derivative validity/fallback contract' ); }
		if ( ! str_contains( $result['srcset'] ?? '', 'signature-384w.webp 384w' ) || ! str_contains( $result['srcset'] ?? '', 'signature-portal-statue-640w.webp 640w' ) || '(max-width: 29.99em) calc(100vw - 2rem), 640px' !== ( $result['sizes'] ?? '' ) ) { throw new RuntimeException( 'Responsive source/fallback contract' ); }
	} elseif ( $result ) { throw new RuntimeException( 'Invalid derivative accepted: ' . $mode ); }
	if ( skyyrose2_archive_frame_delivery( '../unknown' ) ) { throw new RuntimeException( 'Unknown frame accepted' ); }
	echo 'PASS frame delivery ' . $mode . "\n";
} finally {
	$iterator = new RecursiveIteratorIterator( new RecursiveDirectoryIterator( $fixture, FilesystemIterator::SKIP_DOTS ), RecursiveIteratorIterator::CHILD_FIRST );
	foreach ( $iterator as $entry ) {
		if ( $entry->isDir() && ! $entry->isLink() ) { rmdir( $entry->getPathname() ); } else { unlink( $entry->getPathname() ); }
	}
	rmdir( $fixture );
}
