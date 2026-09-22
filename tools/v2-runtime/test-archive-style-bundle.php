<?php
/** Synthetic fixture verifies projection delivery without customer/DB state. */
$root = sys_get_temp_dir() . '/archive-projection-' . bin2hex( random_bytes( 6 ) );
mkdir( $root . '/assets/css', 0700, true );
$alias = $root . '-theme-link';
symlink( realpath( $root ), $alias );
define( 'ABSPATH', $root );
define( 'WPINC', 'wp-includes' );
mkdir( $root . '/wp-includes/css/dist/block-library', 0700, true );
define( 'SKYYROSE2_DIR', $alias );
define( 'SKYYROSE2_URI', 'http://127.0.0.1:18308/theme' );
$GLOBALS['actions'] = array();
$GLOBALS['filters'] = array();
$GLOBALS['enabled'] = true;
$GLOBALS['archive'] = true;
$GLOBALS['head'] = true;
$GLOBALS['footer'] = false;
function doing_action( $name ) { return 'wp_head' === $name ? $GLOBALS['head'] : ( 'wp_footer' === $name && $GLOBALS['footer'] ); }
function did_action( $name ) { return 0; }
function add_filter( $name, $callback, $priority = 10, $args = 1 ) {
	$GLOBALS['wp_filter'][ $name ] = (object) array( 'callbacks' => array( $priority => array( $callback => array( 'function' => $callback, 'accepted_args' => $args ) ) ) );
}
function add_action( $name, $callback, $priority = 10 ) { $GLOBALS['actions'][ $name ][] = $callback; }
function apply_filters( $name, $value ) { return $GLOBALS['enabled']; }
function has_filter( $name ) { return ! empty( $GLOBALS['filters'][ $name ] ); }
function is_admin() { return false; }
function wp_installing() { return false; }
function wp_doing_ajax() { return false; }
function is_rtl() { return false; }
function is_shop() { return $GLOBALS['archive']; }
function is_product_taxonomy() { return false; }
function is_main_query() { return true; }
function wp_styles() { return $GLOBALS['styles']; }
function _wp_normalize_relative_css_links( $css, $src ) { return $css; }
require dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2/inc/archive-style-bundle.php';
function expect( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
class WP_Styles {
	public $registered = array();
	public $queue = array();
	public $done = array();
	public $to_do = array();
	public $args = array();
	public function all_deps( $items ) {
		foreach ( $items as $item ) {
			if ( in_array( $item, $this->to_do, true ) ) { continue; }
			if ( ! isset( $this->registered[ $item ] ) || ! $this->all_deps( $this->registered[ $item ]->deps ) ) { return false; }
			$this->to_do[] = $item;
		}
		return true;
	}
}
function fresh() {
	$GLOBALS['actions']['wp_print_styles'] = array();
	$GLOBALS['styles'] = new WP_Styles();
	foreach ( array( 'plugin-before', 'skyyrose2-tokens', 'skyyrose2-theme', 'skyyrose2-shop-page', 'plugin-after' ) as $handle ) {
		$GLOBALS['styles']->registered[ $handle ] = (object) array( 'src' => SKYYROSE2_URI . '/assets/css/' . ( 'skyyrose2-theme' === $handle ? 'theme.min.css' : $handle . '.css' ), 'deps' => 'skyyrose2-theme' === $handle ? array( 'skyyrose2-tokens' ) : array(), 'args' => 'all', 'ver' => 'original', 'extra' => array() );
		$GLOBALS['styles']->queue[] = $handle;
	}
	return $GLOBALS['styles'];
}
function fixture_projection() {
	$manifest = array( 'schema' => 'skyyrose.archive-theme-projection.v1', 'classification' => array( array( 'selector' => '.shared', 'disposition' => 'PRESERVE' ) ) );
	foreach ( array( 'source' => 'theme.css', 'originalMin' => 'theme.min.css', 'output' => 'archive-theme.min.css' ) as $key => $file ) {
		$bytes = 'output' === $key ? '.shared{color:red}' : '.shared{color:red}.sr2-cart{color:blue}';
		file_put_contents( SKYYROSE2_DIR . '/assets/css/' . $file, $bytes );
		$manifest[ $key ] = array( 'file' => $file, 'sha256' => hash( 'sha256', $bytes ), 'bytes' => strlen( $bytes ) );
	}
	file_put_contents( SKYYROSE2_DIR . '/assets/css/archive-theme.json', json_encode( $manifest ) );
}
function print_guard() { foreach ( $GLOBALS['actions']['wp_print_styles'] as $callback ) { $callback(); } }
function simulate_core( $style ) {
	$style->extra['path'] = $style->extra['path'] ?? SKYYROSE2_DIR . '/assets/css/archive-theme.min.css';
	$style->extra['inlined_src'] = $style->src;
	$style->extra['after'] = array_merge( array( file_get_contents( $style->extra['path'] ) ), $style->extra['after'] ?? array() );
	$style->src = false;
}
function inline_fixture() {
	$s = fresh();
	$names = array( 'design-tokens', 'shop-page', 'controls', 'global-shell', 'visual-recovery', 'mascot' );
	$s->queue = array( 'plugin-before', 'skyyrose2-tokens', 'skyyrose2-theme' );
	$receipt = array( 'schema' => 'skyyrose.archive-style-inputs.v1', 'sources' => array() );
	foreach ( $names as $name ) {
		$handle = 'design-tokens' === $name ? 'skyyrose2-tokens' : 'skyyrose2-' . $name;
		$file = $name . '.min.css'; $bytes = '.' . $name . '{color:red}';
		file_put_contents( SKYYROSE2_DIR . '/assets/css/' . $file, $bytes );
		$receipt['sources'][] = array( 'file' => $file, 'sha256' => hash( 'sha256', $bytes ), 'bytes' => strlen( $bytes ) );
		$deps = 'design-tokens' === $name ? array() : array( 'mascot' === $name ? 'skyyrose2-tokens' : 'skyyrose2-theme' );
		$s->registered[ $handle ] = (object) array( 'src' => SKYYROSE2_URI . '/assets/css/' . $file, 'deps' => $deps, 'args' => 'all', 'ver' => 'original', 'extra' => array( 'path' => SKYYROSE2_DIR . '/assets/css/' . $file ) );
		if ( 'design-tokens' !== $name ) { $s->queue[] = $handle; }
	}
	$s->queue[] = 'plugin-after';
	file_put_contents( SKYYROSE2_DIR . '/assets/css/archive-style-inputs.json', json_encode( $receipt ) );
	skyyrose2_archive_theme_projection();
	$s->registered['skyyrose2-theme']->extra['path'] = SKYYROSE2_DIR . '/assets/css/archive-theme.min.css';
	return $s;
}
function native_common_fixture( $s, $bytes = 4203 ) {
	$path = ABSPATH . '//' . WPINC . '/css/dist/block-library/common.min.css';
	file_put_contents( $path, '/*' . str_repeat( 'c', $bytes - 4 ) . '*/' ); clearstatcache();
	$s->registered['wp-block-library'] = (object) array( 'src' => '/' . WPINC . '/css/dist/block-library/common.min.css', 'deps' => array(), 'ver' => false, 'args' => null, 'extra' => array( 'path' => $path, 'rtl' => 'replace', 'suffix' => '.min', 'after' => array( '/*wp_block_styles_on_demand_placeholder:6a9da145f3e66*/' ) ) );
	array_unshift( $s->queue, 'wp-block-library' );
	// Native Core enqueues its library before the theme projection snapshot.
	$GLOBALS['actions']['wp_print_styles'] = array();
	$theme = $s->registered['skyyrose2-theme'];
	$theme->src = SKYYROSE2_URI . '/assets/css/theme.min.css'; $theme->ver = 'original'; $theme->extra = array();
	skyyrose2_archive_theme_projection();
	$theme->extra['path'] = SKYYROSE2_DIR . '/assets/css/archive-theme.min.css';
	return $s->registered['wp-block-library'];
}
try {
	fixture_projection();
	$s = fresh(); $other = clone $s->registered['plugin-before']; $queue = $s->queue;
	skyyrose2_archive_theme_projection();
	expect( str_ends_with( $s->registered['skyyrose2-theme']->src, 'archive-theme.min.css' ), 'Known archive should use projection' );
	expect( $other == $s->registered['plugin-before'] && $queue === $s->queue, 'Other styles and order unchanged' );
	print_guard();
	expect( str_ends_with( $s->registered['skyyrose2-theme']->src, 'archive-theme.min.css' ), 'Stable external projection survives print' );
	simulate_core( $s->registered['skyyrose2-theme'] ); print_guard();
	expect( false === $s->registered['skyyrose2-theme']->src && 1 === count( $s->registered['skyyrose2-theme']->extra['after'] ), 'Known Core inline transformation survives' );
	$s->registered['skyyrose2-theme']->extra['after'][] = '.late-plugin{}'; print_guard();
	expect( SKYYROSE2_URI . '/assets/css/theme.min.css' === $s->registered['skyyrose2-theme']->src, 'Late change restores full source' );
	expect( array( '.late-plugin{}' ) === $s->registered['skyyrose2-theme']->extra['after'], 'Rollback removes only owned inline CSS' );
	foreach ( array( 'replace-src', 'prepend-css', 'replace-and-prepend' ) as $mode ) {
		$s = fresh();
		$s->registered['skyyrose2-theme']->extra['path'] = SKYYROSE2_DIR . '/assets/css/theme.min.css';
		skyyrose2_archive_theme_projection();
		$style = $s->registered['skyyrose2-theme'];
		simulate_core( $style );
		$replace = 'prepend-css' !== $mode;
		$prepend = 'replace-src' !== $mode;
		if ( $replace ) { $style->src = SKYYROSE2_URI . '/plugin-theme.css'; }
		if ( $prepend ) { array_unshift( $style->extra['after'], '.plugin-first{color:green}' ); }
		print_guard();
		expect( $style->src === SKYYROSE2_URI . ( $replace ? '/plugin-theme.css' : '/assets/css/theme.min.css' ), 'Rollback preserves replacement URL or restores original after prepend' );
		expect( ( $style->extra['after'] ?? array() ) === ( $prepend ? array( '.plugin-first{color:green}' ) : array() ), 'Rollback locates only owned CSS independently of source and position' );
		expect( ! isset( $style->extra['inlined_src'] ), 'Owned inline source marker removed on rollback' );
		expect( $replace ? ! isset( $style->extra['path'] ) : $style->extra['path'] === SKYYROSE2_DIR . '/assets/css/theme.min.css', 'Never apply original path metadata to a plugin replacement' );
	}
	foreach ( array(
		function ( $s ) { $s->registered['skyyrose2-theme']->src .= '?custom'; },
		function ( $s ) { $s->registered['skyyrose2-theme']->extra['after'] = array( '.custom{}' ); },
		function ( $s ) { $s->registered['skyyrose2-theme']->args = 'screen'; },
		function ( $s ) { $s->registered['skyyrose2-theme']->extra['rtl'] = true; },
		function ( $s ) { $s->registered['skyyrose2-theme']->extra['path'] = '/custom.css'; },
		function ( $s ) { $s->registered['skyyrose2-theme']->deps = array(); },
		function ( $s ) { $s->done[] = 'skyyrose2-theme'; },
	) as $mutate ) {
		$s = fresh(); $mutate( $s ); $before = serialize( $s ); skyyrose2_archive_theme_projection(); expect( $before === serialize( $s ), 'Unknown style context untouched' );
	}
	foreach ( array( 'missing', 'source', 'originalMin', 'output', 'manifest' ) as $mode ) {
		fixture_projection(); $s = fresh(); $before = serialize( $s );
		if ( 'missing' === $mode ) { unlink( SKYYROSE2_DIR . '/assets/css/archive-theme.min.css' ); }
		elseif ( 'manifest' === $mode ) { file_put_contents( SKYYROSE2_DIR . '/assets/css/archive-theme.json', '{"schema":"skyyrose.archive-theme-projection.v1","classification":"bad"}' ); }
		else { $files = array( 'source' => 'theme.css', 'originalMin' => 'theme.min.css', 'output' => 'archive-theme.min.css' ); file_put_contents( SKYYROSE2_DIR . '/assets/css/' . $files[ $mode ], 'changed' ); }
		skyyrose2_archive_theme_projection(); expect( $before === serialize( $s ), 'Missing/drifted/malformed delivery falls back' );
	}
	fixture_projection();
	foreach ( array( 'enabled', 'archive' ) as $guard ) { $GLOBALS[ $guard ] = false; $s = fresh(); $before = serialize( $s ); skyyrose2_archive_theme_projection(); expect( $before === serialize( $s ), 'Opt out/nonarchive unchanged' ); $GLOBALS[ $guard ] = true; }
	foreach ( array( 'valid', 'missing', 'drift', 'interleave', 'dependency', 'src', 'media', 'inline', 'path', 'unknown-path', 'unknown-media-path', 'footer', 'not-head', 'loader-filter', 'over-budget', 'custom-budget', 'budget-filter', 'optout', 'late-src', 'late-inline', 'late-path', 'late-dependency', 'projection-rollback' ) as $mode ) {
		$s = inline_fixture(); $shop = $s->registered['skyyrose2-shop-page'];
		$budget_filters = clone $GLOBALS['wp_filter']['styles_inline_size_limit'];
		if ( 'missing' === $mode ) { unlink( SKYYROSE2_DIR . '/assets/css/archive-style-inputs.json' ); }
		if ( 'drift' === $mode ) { file_put_contents( SKYYROSE2_DIR . '/assets/css/controls.min.css', 'drift' ); }
		if ( 'interleave' === $mode ) { array_splice( $s->queue, 4, 0, array( 'plugin-after' ) ); }
		if ( 'dependency' === $mode ) { $s->registered['skyyrose2-controls']->deps[] = 'plugin-after'; }
		if ( 'src' === $mode ) { $shop->src = '/custom.css'; }
		if ( 'media' === $mode ) { $shop->args = 'screen'; }
		if ( 'inline' === $mode ) { $shop->extra['after'] = array( '.plugin{}' ); }
		if ( 'path' === $mode ) { $shop->extra['path'] = '/custom.css'; }
		if ( in_array( $mode, array( 'unknown-path', 'unknown-media-path' ), true ) ) { $s->registered['plugin-after']->extra['path'] = '/plugin.css'; $s->registered['plugin-after']->args = 'unknown-media-path' === $mode ? '(max-width:768px)' : 'all'; }
		if ( 'over-budget' === $mode ) {
			$path = SKYYROSE2_DIR . '/assets/css/controls.min.css';
			$bytes = str_repeat( '.controls{color:red}', 6000 ); file_put_contents( $path, $bytes );
			$manifest_path = SKYYROSE2_DIR . '/assets/css/archive-style-inputs.json';
			$manifest = json_decode( file_get_contents( $manifest_path ), true );
			$manifest['sources'][2]['sha256'] = hash( 'sha256', $bytes ); $manifest['sources'][2]['bytes'] = strlen( $bytes );
			file_put_contents( $manifest_path, json_encode( $manifest ) ); clearstatcache();
		}
		if ( 'not-head' === $mode ) { $GLOBALS['head'] = false; }
		if ( 'loader-filter' === $mode ) { $GLOBALS['filters']['style_loader_tag'] = true; }
		if ( 'footer' === $mode ) { $GLOBALS['footer'] = true; }
		if ( 'budget-filter' === $mode ) { $GLOBALS['wp_filter']['styles_inline_size_limit']->callbacks[10] = array( 'plugin' => array() ); }
		if ( 'optout' === $mode ) { $GLOBALS['enabled'] = false; }
		$before = serialize( $s );
		$incoming = 'custom-budget' === $mode ? 50000 : 40000;
		$result = skyyrose2_archive_inline_budget( $incoming );
		$GLOBALS['footer'] = false; $GLOBALS['head'] = true; $GLOBALS['enabled'] = true; unset( $GLOBALS['filters']['style_loader_tag'] );
		$GLOBALS['wp_filter']['styles_inline_size_limit'] = $budget_filters;
		$accepted = in_array( $mode, array( 'valid', 'late-src', 'late-inline', 'late-path', 'late-dependency', 'projection-rollback' ), true );
		expect( serialize( $s ) === $before, 'Budget filter never remaps sources or metadata: ' . $mode );
		if ( ! $accepted ) { expect( $result === $incoming, 'Unsupported inline context retains incoming budget: ' . $mode ); continue; }
		expect( 100000 === $result, 'Verified chain receives bounded allowance' );
		foreach ( $s->queue as $handle ) { if ( str_starts_with( $handle, 'skyyrose2-' ) ) { simulate_core( $s->registered[ $handle ] ); } }
		if ( 'late-src' === $mode ) { $shop->src = '/plugin-new.css'; }
		if ( 'late-inline' === $mode ) { array_unshift( $s->registered['skyyrose2-controls']->extra['after'], '.plugin-late{}' ); }
		if ( 'late-dependency' === $mode ) { $s->registered['plugin-before']->deps = array( 'skyyrose2-controls' ); }
		if ( 'late-path' === $mode ) { $s->registered['plugin-after']->extra['path'] = '/plugin.css'; }
		if ( 'projection-rollback' === $mode ) { $s->registered['skyyrose2-theme']->extra['after'][] = '.plugin-late{}'; }
		print_guard();
		if ( 'valid' === $mode ) { expect( false === $shop->src && isset( $shop->extra['inlined_src'] ), 'Exact Core inline state survives' ); }
		else {
			expect( $shop->src === ( 'late-src' === $mode ? '/plugin-new.css' : SKYYROSE2_URI . '/assets/css/shop-page.min.css' ), 'Restore original or preserve plugin replacement' );
			expect( ! isset( $shop->extra['inlined_src'] ), 'Owned Core marker removed on rollback' );
			expect( $s->registered['skyyrose2-controls']->src === SKYYROSE2_URI . '/assets/css/controls.min.css', 'Restore other original sources' );
			if ( 'late-src' === $mode ) { expect( ! isset( $shop->extra['path'] ), 'No original path attached to plugin URL' ); }
			if ( 'late-inline' === $mode ) { expect( $s->registered['skyyrose2-controls']->extra['after'] === array( '.plugin-late{}' ), 'Keep prepended plugin CSS' ); }
		}
	}
	foreach ( array( 'valid', 'too-large', 'crowded-budget', 'media', 'extra-css', 'wrong-path', 'late-plugin', 'late-core' ) as $mode ) {
		$s = inline_fixture();
		$core = native_common_fixture( $s, 'too-large' === $mode ? 40001 : ( 'crowded-budget' === $mode ? 35000 : 4203 ) );
		if ( 'crowded-budget' === $mode ) {
			$path = SKYYROSE2_DIR . '/assets/css/design-tokens.min.css'; $bytes = str_repeat( ' ', 10000 ); file_put_contents( $path, $bytes );
			$file = SKYYROSE2_DIR . '/assets/css/archive-style-inputs.json'; $manifest = json_decode( file_get_contents( $file ), true );
			$manifest['sources'][0]['bytes'] = 10000; $manifest['sources'][0]['sha256'] = hash( 'sha256', $bytes ); file_put_contents( $file, json_encode( $manifest ) ); clearstatcache();
		}
		if ( 'media' === $mode ) { $core->args = '(max-width:768px)'; }
		if ( 'extra-css' === $mode ) { $core->extra['after'][] = '.custom{}'; }
		if ( 'wrong-path' === $mode ) { $core->extra['path'] = SKYYROSE2_DIR . '/assets/css/controls.min.css'; }
		$before = serialize( $core );
		$result = skyyrose2_archive_inline_budget( 40000 );
		expect( serialize( $core ) === $before, 'Native registration unchanged by budget exception' );
		if ( ! in_array( $mode, array( 'valid', 'late-plugin', 'late-core' ), true ) ) { expect( 40000 === $result, 'Only common CSS already fitting original allocation is eligible: ' . $mode ); continue; }
		expect( 100000 === $result, 'Native common CSS already in original budget is compatible' );
		simulate_core( $core ); $native_after = serialize( $core );
		foreach ( $s->queue as $handle ) { if ( str_starts_with( $handle, 'skyyrose2-' ) ) { simulate_core( $s->registered[ $handle ] ); } }
		if ( 'late-plugin' === $mode ) { $s->registered['skyyrose2-controls']->extra['after'][] = '.plugin-late{}'; }
		if ( 'late-core' === $mode ) { $core->extra['after'][] = '.core-extension{}'; $native_after = serialize( $core ); }
		print_guard();
		expect( serialize( $core ) === $native_after, 'Native baseline Core chunk and placeholder are never rolled back or edited' );
		expect( 'valid' === $mode ? false === $s->registered['skyyrose2-shop-page']->src : false !== $s->registered['skyyrose2-shop-page']->src, 'Native permission survives exact Core inlining and detects late changes' );
	}
	foreach ( array( 'pre_wp_filesize', 'wp_filesize' ) as $filter ) {
		$s = inline_fixture(); $core = native_common_fixture( $s );
		$GLOBALS['filters'][ $filter ] = true;
		$before = serialize( $s );
		expect( 40000 === skyyrose2_archive_inline_budget( 40000 ) && serialize( $s ) === $before, 'Unknown file-size filter must prevent a widened initial allocation: ' . $filter );
		unset( $GLOBALS['filters'][ $filter ] );
		$s = inline_fixture(); $core = native_common_fixture( $s );
		expect( 100000 === skyyrose2_archive_inline_budget( 40000 ), 'Known unfiltered allocation starts normally' );
		simulate_core( $core ); $native = serialize( $core );
		foreach ( $s->queue as $handle ) { if ( str_starts_with( $handle, 'skyyrose2-' ) ) { simulate_core( $s->registered[ $handle ] ); } }
		$GLOBALS['filters'][ $filter ] = true;
		print_guard();
		expect( false !== $s->registered['skyyrose2-shop-page']->src && ! isset( $s->registered['skyyrose2-shop-page']->extra['inlined_src'] ), 'Late size filter restores owned external delivery: ' . $filter );
		expect( serialize( $core ) === $native, 'Late filter never changes baseline Core inline chunk' );
		unset( $GLOBALS['filters'][ $filter ] );
	}
	$GLOBALS['filters']['style_loader_tag'] = true; $s = fresh(); $before = serialize( $s ); skyyrose2_archive_theme_projection(); expect( $before === serialize( $s ), 'Unknown loader filter unchanged' );
	echo "PASS archive projection, bounded native inline eligibility, input authority and late extension preservation\n";
} finally {
	foreach ( glob( SKYYROSE2_DIR . '/assets/css/*' ) as $file ) { unlink( $file ); }
	$native_file = ABSPATH . '/' . WPINC . '/css/dist/block-library/common.min.css';
	if ( is_file( $native_file ) ) { unlink( $native_file ); }
	foreach ( array( '/css/dist/block-library', '/css/dist', '/css', '' ) as $part ) { rmdir( ABSPATH . '/' . WPINC . $part ); }
	rmdir( SKYYROSE2_DIR . '/assets/css' ); rmdir( SKYYROSE2_DIR . '/assets' ); unlink( $alias ); rmdir( $root );
}
