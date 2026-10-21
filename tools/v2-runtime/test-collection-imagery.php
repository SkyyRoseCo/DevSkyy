<?php
/**
 * Rendered-page contract for founder-approved collection imagery and media cache keys.
 *
 * Renders /collections/black-rose/, /collections/ and the homepage through the real
 * templates and the real media gate (render-collection-imagery.php), then checks:
 *  - each collections.*.imagery slot renders its exact registry binding (role, SKU);
 *  - every theme media URL (src, srcset candidate, preload href/imagesrcset, video
 *    data-src) carries ?v=<sha256 of the served bytes>;
 *  - each srcset family is one SKU's rendition set, every width matches real pixels;
 *  - the route preload is byte-identical to the eager image it announces
 *    (href = src, imagesrcset = srcset, imagesizes = sizes).
 *
 * Usage: php test-collection-imagery.php [theme-dir]
 */
$theme    = realpath( $argv[1] ?? dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2' );
$renderer = __DIR__ . '/render-collection-imagery.php';
$prefix   = 'https://skyyrose.co/wp-content/themes/skyyrose-flagship-2/';
$failures = 0;
function check_imagery( $result, $label ) {
	global $failures;
	if ( $result ) { echo "PASS: $label\n"; return; }
	echo "FAIL: $label\n";
	++$failures;
}
function render_imagery_page( $page ) {
	global $renderer, $theme;
	$output = array();
	exec( escapeshellarg( PHP_BINARY ) . ' ' . escapeshellarg( $renderer ) . ' ' . escapeshellarg( $page ) . ' ' . escapeshellarg( $theme ) . ' 2>&1', $output, $code );
	$html = implode( "\n", $output );
	if ( 0 !== $code || preg_match( '/(?:Fatal|Warning|Deprecated|Notice):/', $html ) ) { throw new RuntimeException( "render $page failed:\n$html" ); }
	return $html;
}
function imagery_attr( $tag, $name ) {
	return preg_match( '/\s' . preg_quote( $name, '/' ) . '="([^"]*)"/', $tag, $m ) ? html_entity_decode( $m[1], ENT_QUOTES, 'UTF-8' ) : null;
}
/** Every theme media URL must be keyed by the sha256 of the bytes at its path. */
function imagery_keyed( $url ) {
	global $prefix, $theme;
	if ( 0 !== strpos( $url, $prefix ) ) { return false; }
	if ( ! preg_match( '~^([^?#]+)\?v=([a-f0-9]{64})$~D', substr( $url, strlen( $prefix ) ), $m ) ) { return false; }
	$file = $theme . '/' . rawurldecode( $m[1] );
	return is_file( $file ) && hash_equals( $m[2], hash_file( 'sha256', $file ) );
}
function imagery_srcset_ok( $srcset, $sku ) {
	global $prefix, $theme;
	$candidates = array_map( 'trim', explode( ',', (string) $srcset ) );
	if ( ! $srcset || ! $candidates ) { return false; }
	foreach ( $candidates as $candidate ) {
		if ( ! preg_match( '/^(\S+) ([1-9][0-9]*)w$/D', $candidate, $m ) || ! imagery_keyed( $m[1] ) ) { return false; }
		$relative = explode( '?', substr( $m[1], strlen( $prefix ) ) )[0];
		if ( 0 !== strpos( basename( $relative ), $sku . '-' ) ) { return false; }
		$size = getimagesize( $theme . '/' . $relative );
		if ( ! $size || (int) $m[2] !== $size[0] ) { return false; }
	}
	return true;
}
$registry = json_decode( file_get_contents( $theme . '/data/product-presentation-registry.json' ), true );
$expected = array();
foreach ( $registry['collections'] as $slug => $collection ) {
	foreach ( $collection['imagery'] ?? array() as $role => $binding ) { $expected[ $slug ][ $role ] = $binding['sku']; }
}
check_imagery( 11 === array_sum( array_map( 'count', $expected ) ) && empty( $expected['kids-capsule']['merchandise_scene'] ), 'Registry carries the 11 collection slots and no Kids merchandise slot' );

$pages = array();
foreach ( array( 'black-rose', 'collections', 'home' ) as $page ) { $pages[ $page ] = render_imagery_page( $page ); }

// Global: every theme media URL that survived the gate is cache-keyed to its bytes.
foreach ( $pages as $page => $html ) {
	$unkeyed = array();
	preg_match_all( '#<(?:img|source|video|link)\b[^>]*>#i', $html, $tags );
	foreach ( $tags[0] as $tag ) {
		foreach ( array( 'src', 'data-src', 'poster', 'href' ) as $name ) {
			$value = imagery_attr( $tag, $name );
			if ( $value && 0 === strpos( $value, $prefix ) && ! imagery_keyed( $value ) ) { $unkeyed[] = $value; }
		}
		foreach ( array( 'srcset', 'imagesrcset' ) as $name ) {
			$value = imagery_attr( $tag, $name );
			foreach ( $value ? array_map( 'trim', explode( ',', $value ) ) : array() as $candidate ) {
				$url = explode( ' ', $candidate )[0];
				if ( ! imagery_keyed( $url ) ) { $unkeyed[] = $url; }
			}
		}
	}
	check_imagery( ! $unkeyed, "Every $page media URL is keyed ?v=<sha256 of served bytes>" . ( $unkeyed ? ': ' . implode( ' ', array_slice( $unkeyed, 0, 3 ) ) : '' ) );
}

// Role-bound images: exact binding, uncropped markup, keyed srcset family.
function imagery_roles( $html ) {
	if ( preg_match( '#<main\b[^>]*>(.*?)</main>#s', $html, $main ) ) { $html = $main[1]; }
	preg_match_all( '#<img\b[^>]*data-media-role="[^"]+"[^>]*>#', $html, $m );
	return $m[0];
}
$story = imagery_roles( $pages['black-rose'] );
check_imagery( 1 === count( $story ) && 'collection_story' === imagery_attr( $story[0], 'data-media-role' ) && $expected['black-rose']['collection_story'] === imagery_attr( $story[0], 'data-media-sku' ), '/collections/black-rose/ origin story renders the br-004 collection_story binding' );
check_imagery( $story && imagery_srcset_ok( imagery_attr( $story[0], 'srcset' ), 'br-004' ) && imagery_attr( $story[0], 'sizes' ), 'Black Rose story srcset is the keyed br-004 rendition family' );
check_imagery( false === strpos( $pages['black-rose'], 'Look 01' ), 'Retired lookbook caption is gone' );

$index = imagery_roles( $pages['collections'] );
$index_slugs = array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' );
$motion_manifest = json_decode( file_get_contents( $theme . '/data/collection-hero-motion.json' ), true );
check_imagery( 4 === count( $index ), 'Index has one admitted image for each collection' );
foreach ( $index as $number => $tag ) {
	$slug = $index_slugs[ $number ];
	if ( 'kids-capsule' === $slug ) {
		check_imagery( $expected[ $slug ]['collection_hero'] === imagery_attr( $tag, 'data-media-sku' ), 'Kids index keeps its exact product-bound hero' );
	} else {
		$poster = $motion_manifest['collections'][ $slug ]['source']['file'];
		check_imagery( $prefix . $poster . '?v=' . hash_file( 'sha256', $theme . '/' . $poster ) === imagery_attr( $tag, 'src' ), 'Index uses the exact current cinema poster for ' . $slug );
	}
}
check_imagery( $index && 'eager' === imagery_attr( $index[0], 'loading' ) && 'high' === imagery_attr( $index[0], 'fetchpriority' ) && 3 === count( array_filter( array_slice( $index, 1 ), static fn( $tag ) => 'lazy' === imagery_attr( $tag, 'loading' ) ) ), 'Only the first index chapter is eager/high priority' );
foreach ( $index as $tag ) {
	if ( ! imagery_attr( $tag, 'data-media-sku' ) ) { continue; }
	check_imagery( imagery_srcset_ok( imagery_attr( $tag, 'srcset' ), imagery_attr( $tag, 'data-media-sku' ) ), 'Index srcset family is keyed and single-SKU for ' . imagery_attr( $tag, 'data-media-sku' ) );
}
check_imagery( str_contains( file_get_contents( $theme . '/template-parts/collections/index.php' ), 'sr2-collections-index__lockup' ), 'Index chapter titles keep the collection lockup image (template source; the gate decides delivery)' );
preg_match_all( '#<link rel="preload"[^>]*>#', $pages['collections'], $preloads );
$preload = $preloads[0][0] ?? '';
check_imagery( 1 === count( $preloads[0] ) && $index && imagery_attr( $preload, 'href' ) === imagery_attr( $index[0], 'src' ), 'Index preload href is byte-identical to the eager image src' );
check_imagery( $index && imagery_attr( $preload, 'imagesrcset' ) === imagery_attr( $index[0], 'srcset' ) && imagery_attr( $preload, 'imagesizes' ) === imagery_attr( $index[0], 'sizes' ), 'Index preload imagesrcset/imagesizes equal the eager image srcset/sizes' );

$home = imagery_roles( $pages['home'] );
$home_pairs = array_map( static fn( $tag ) => imagery_attr( $tag, 'data-media-role' ) . ':' . imagery_attr( $tag, 'data-media-sku' ), $home );
// Homepage chapters keep their destination-hero motion contract
// (scripts/validate-collection-hero-motion.py); only the worlds rail takes registry imagery.
check_imagery( array( 'collection_hero:' . $expected['kids-capsule']['collection_hero'], 'collection_hero:sg-009', 'collection_hero:br-001', 'collection_story:lh-004' ) === $home_pairs, 'Homepage Kids fallback and worlds rail render their admitted collection bindings' );
check_imagery( 3 === substr_count( $pages['home'], 'data-scene-state="approved-v2-still"' ), 'Worlds rail renders one approved still per world' );
check_imagery( str_contains( file_get_contents( $theme . '/template-parts/home/editorial-collection.php' ), "skyyrose2_collection_cinema( \$slug )" ), 'Homepage chapters use the destination cinema resolver' );
preg_match_all( '#<link rel="preload"[^>]*>#', $pages['home'], $home_preloads );
preg_match( '#<img\b[^>]*fetchpriority="high"[^>]*>#', $pages['home'], $home_lcp );
check_imagery( 1 === count( $home_preloads[0] ) && $home_lcp && imagery_attr( $home_preloads[0][0], 'href' ) === imagery_attr( $home_lcp[0], 'src' ), 'Homepage preload href equals the keyed house-art src' );

echo $failures ? "FAILED: $failures\n" : "PASS all collection-imagery render contracts\n";
exit( $failures ? 1 : 0 );
