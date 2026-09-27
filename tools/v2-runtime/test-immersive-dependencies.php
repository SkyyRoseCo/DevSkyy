<?php
/** Execute the real world template's enqueue phase without a database or network. */
define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_DIR', dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2' );
define( 'SKYYROSE2_URI', 'https://theme.test/wp-content/themes/skyyrose-flagship-2' );
define( 'SKYYROSE2_VERSION', '2.4.4' );
function sanitize_key( $value ) { return $value; }
function wp_generate_uuid4() { return 'offline-test'; }
function skyyrose2_collection_commerce_scenes( $slug ) { return array(); }
function skyyrose2_sot_asset_uri( $path ) { return SKYYROSE2_URI . '/assets/sot/' . $path; }
function skyyrose2_asset_version( $path ) { return hash_file( 'sha256', SKYYROSE2_DIR . $path ); }
function wp_enqueue_style( ...$args ) {}
function wp_enqueue_script( $handle, $src, $deps, $version, $footer ) {
	$GLOBALS['enqueued'][ $handle ] = compact( 'src', 'deps', 'version', 'footer' );
}
class EnqueueComplete extends RuntimeException {}
function get_header() { throw new EnqueueComplete(); }
$args = array(
	'collection_slug' => 'love-hurts',
	'collection_name' => 'Love Hurts',
	'world_name' => 'Story world',
	'poster' => 'images/hero/kids-capsule-heir-throne-v3.webp',
	'chapters' => array( array( 'id' => 'chapter-one' ) ),
);
try {
	require SKYYROSE2_DIR . '/template-parts/immersive/world.php';
} catch ( EnqueueComplete $complete ) {}
$scripts = $GLOBALS['enqueued'] ?? array();
$engine = $scripts['skyyrose2-world-engine'] ?? null;
$world = $scripts['skyyrose2-immersive'] ?? null;
if ( ! $engine || ! $world || ! in_array( 'skyyrose2-world-engine', $world['deps'], true ) ) {
	throw new RuntimeException( 'World must wait for its shared Three loader before requesting Three.js.' );
}
if ( ! in_array( 'skyyrose2-mascot-loader', $engine['deps'], true ) || ! $engine['footer'] ) {
	throw new RuntimeException( 'Engine needs its localized configuration and footer canvas before execution.' );
}
if ( ! str_contains( $engine['src'], '/assets/js/skyy-3d' ) || SKYYROSE2_VERSION === $engine['version'] ) {
	throw new RuntimeException( 'Use the existing self-hosted, content-versioned engine.' );
}
echo "PASS immersive engine dependency ordering, configuration and content version\n";
