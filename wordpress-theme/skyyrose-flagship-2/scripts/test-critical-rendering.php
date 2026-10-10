<?php
/** Standalone contract tests for inc/critical-rendering.php. */

define( 'ABSPATH', __DIR__ . '/' );
define( 'SKYYROSE2_DIR', dirname( __DIR__ ) );
define( 'SKYYROSE2_URI', 'https://example.test/wp-content/themes/skyyrose-flagship-2' );

$GLOBALS['sr2_hooks']         = array();
$GLOBALS['sr2_front']         = false;
$GLOBALS['sr2_admin']         = false;
$GLOBALS['sr2_customizer']    = false;
$GLOBALS['sr2_filter_values'] = array();
$GLOBALS['sr2_inline_tags']   = array();

function add_action( $hook, $callback, $priority = 10, $accepted_args = 1 ) {
	$GLOBALS['sr2_hooks'][] = array( $hook, $callback, $priority );
}
function add_filter( $hook, $callback, $priority = 10, $accepted_args = 1 ) {
	$GLOBALS['sr2_hooks'][] = array( $hook, $callback, $priority );
}
function skyyrose2_sot_asset_uri( $path ) {
	return SKYYROSE2_URI . '/assets/sot/' . ltrim( $path, '/' );
}
function apply_filters( $hook, $value ) {
	return $GLOBALS['sr2_filter_values'][ $hook ] ?? $value; }
function is_front_page() {
	return $GLOBALS['sr2_front']; }
function is_admin() {
	return $GLOBALS['sr2_admin']; }
function is_customize_preview() {
	return $GLOBALS['sr2_customizer']; }
function skyyrose2_asset_suffix() {
	return '.min'; }
function wp_print_inline_script_tag( $javascript, $attributes = array() ) {
	$GLOBALS['sr2_inline_tags'][] = array(
		'js'         => $javascript,
		'attributes' => $attributes,
	);
	echo '<script>' . $javascript . '</script>';
}

require dirname( __DIR__ ) . '/inc/critical-rendering.php';

function sr2_assert( $condition, $message ) {
	if ( ! $condition ) {
		fwrite( STDERR, "FAIL: {$message}\n" );
		exit( 1 );
	}
}

$hooks = array_map(
	static function ( $hook ) {
		return $hook[0] . ':' . $hook[1] . ':' . $hook[2];
	},
	$GLOBALS['sr2_hooks']
);
sr2_assert( in_array( 'wp_head:skyyrose2_print_critical_css:1', $hooks, true ), 'critical CSS prints at wp_head priority 1, after optimizer-generated blocks at 0' );

// The built contract is a real, bounded, source-derived asset.
$contract = json_decode( file_get_contents( SKYYROSE2_DIR . '/assets/css/critical/home.contract.json' ), true );
$built    = file_get_contents( skyyrose2_critical_css_path() );
sr2_assert( is_array( $contract ) && ! empty( $contract['budgetBytes'] ), 'contract declares a byte budget' );
sr2_assert( is_string( $built ) && '' !== trim( $built ), 'built critical CSS exists' );
sr2_assert( strlen( $built ) <= (int) $contract['budgetBytes'], 'built critical CSS is within budget' );
foreach ( array( '@font-face', ':root', '.sr2-house-header', '.sr2-header__brand-mark', '.sr2-brand-media', '.sr2-archive-scene', '.sr2-editorial-hero__copy', '#sr2-archive-title', '.sr2-control--primary', '[data-recovery-hero-video]', '.sr2-arrival', '.sr2-house-nav' ) as $needle ) {
	sr2_assert( false !== strpos( $built, $needle ), "critical CSS carries first-view structure: {$needle}" );
}
sr2_assert( false === strpos( $built, '__SKYYROSE2_ASSETS__/css/' ), 'no relative asset path survives that would resolve against the document' );
sr2_assert( false === stripos( $built, 'is-open' ) && false === stripos( $built, ':hover' ), 'state-only rules stay in the full stylesheets' );
sr2_assert( 1 === preg_match( '/@media\s*\(scripting:\s*none\).*?\.sr2-house-nav\{([^}]+)\}/s', $built, $no_script_rules ), 'critical CSS includes the no-script navigation fallback' );
foreach ( array( 'visibility:visible', 'opacity:1', 'position:static' ) as $declaration ) {
	sr2_assert( false !== strpos( $no_script_rules[1], $declaration ), 'no-script fallback keeps ' . $declaration );
}

// Off the front page nothing prints; on the front page the resolved contract prints once.
ob_start();
skyyrose2_print_critical_css();
sr2_assert( '' === ob_get_clean(), 'content routes print no critical CSS' );
$GLOBALS['sr2_front'] = true;
ob_start();
skyyrose2_print_critical_css();
$head = ob_get_clean();
sr2_assert( 0 === strpos( $head, '<style id="skyyrose2-critical-home">' ), 'front page prints the contract with a stable id' );
sr2_assert( false !== strpos( $head, SKYYROSE2_URI . '/assets/sot/fonts/' ), 'font URLs are absolute theme URLs' );
sr2_assert( false === strpos( $head, '__SKYYROSE2_ASSETS__' ), 'the asset placeholder is resolved' );
sr2_assert( 1 === substr_count( $head, '</style>' ), 'exactly one style element' );
$GLOBALS['sr2_customizer'] = true;
ob_start();
skyyrose2_print_critical_css();
sr2_assert( '' === ob_get_clean(), 'customizer previews are untouched' );
$GLOBALS['sr2_customizer']                                       = false;
$GLOBALS['sr2_filter_values']['skyyrose2_critical_css_disabled'] = true;
ob_start();
skyyrose2_print_critical_css();
sr2_assert( '' === ob_get_clean(), 'the opt-out filter disables the contract' );
$GLOBALS['sr2_filter_values'] = array();

// The early bootstrap is the unchanged controller, byte for byte, ignored by Boost's deferral.
$controller = file_get_contents( SKYYROSE2_DIR . '/assets/js/visual-recovery.min.js' );
sr2_assert( trim( $controller ) === skyyrose2_hero_bootstrap_script(), 'inline bootstrap is the built controller' );
sr2_assert( false !== strpos( $controller, 'recoveryInitialized' ), 'controller guards against a second initialisation' );
sr2_assert( skyyrose2_hero_bootstrap_inline(), 'front page inlines the controller' );
ob_start();
skyyrose2_print_hero_bootstrap();
$printed = ob_get_clean();
sr2_assert( '' !== $printed && 1 === count( $GLOBALS['sr2_inline_tags'] ), 'front page prints one inline controller' );
sr2_assert( 'ignore' === $GLOBALS['sr2_inline_tags'][0]['attributes']['data-jetpack-boost'], 'inline controller opts out of Jetpack Boost script deferral' );
sr2_assert( 'skyyrose2-visual-recovery-early' === $GLOBALS['sr2_inline_tags'][0]['attributes']['id'], 'inline controller has a stable id' );
$GLOBALS['sr2_inline_tags'] = array();
$GLOBALS['sr2_front']       = false;
sr2_assert( ! skyyrose2_hero_bootstrap_inline(), 'collection routes keep the enqueued controller' );
ob_start();
skyyrose2_print_hero_bootstrap();
sr2_assert( '' === ob_get_clean() && empty( $GLOBALS['sr2_inline_tags'] ), 'nothing prints off the front page' );
$GLOBALS['sr2_front'] = true;
$GLOBALS['sr2_filter_values']['skyyrose2_hero_bootstrap_disabled'] = true;
sr2_assert( ! skyyrose2_hero_bootstrap_inline(), 'the opt-out filter restores the enqueued controller' );
$GLOBALS['sr2_filter_values'] = array();

// The template prints the bootstrap directly after the hero section.
$front_page = file_get_contents( SKYYROSE2_DIR . '/front-page.php' );
$hero_start = strpos( $front_page, "get_template_part( 'template-parts/home/editorial-hero'" );
$hero_end   = false !== $hero_start ? strpos( $front_page, '); ?>', $hero_start ) : false;
$bootstrap  = strpos( $front_page, 'skyyrose2_print_hero_bootstrap()' );
sr2_assert( false !== $hero_end && false !== $bootstrap && $bootstrap > $hero_end && $bootstrap - $hero_end < 40, 'bootstrap follows the rendered hero part immediately' );
sr2_assert( strpos( $front_page, "get_template_part( 'template-parts/home/editorial-collection'" ) > $bootstrap, 'bootstrap precedes the next visual section' );
$hero_part = file_get_contents( SKYYROSE2_DIR . '/template-parts/home/editorial-hero.php' );
sr2_assert( false !== strpos( $hero_part, 'data-recovery-hero-video' ) && false !== strpos( $hero_part, 'data-recovery-motion-toggle' ) && false !== strpos( $hero_part, 'id="sr2-archive-title"' ) && false !== strpos( $hero_part, 'aria-label="<?php esc_attr_e( \'SkyyRose\'' ), 'rendered hero retains controller hooks and exposes one accessible wordmark' );

// First-view font preloads: front page only, one record per face, hrefs equal to the inline @font-face URLs.
sr2_assert( in_array( 'wp_preload_resources:skyyrose2_critical_font_preloads:20', $hooks, true ), 'font preloads register on wp_preload_resources after the route hero preloads' );
$GLOBALS['sr2_front'] = false;
sr2_assert( array( array( 'href' => 'x' ) ) === skyyrose2_critical_font_preloads( array( array( 'href' => 'x' ) ) ), 'content routes get no font preloads' );
$GLOBALS['sr2_front'] = true;
$preloads = skyyrose2_critical_font_preloads( array() );
sr2_assert( 2 === count( $preloads ), 'front page preloads only its two first-view faces' );
sr2_assert( in_array( SKYYROSE2_URI . '/assets/derived/fonts/archivo-normal-width.woff2', array_column( $preloads, 'href' ), true ), 'the current Archivo headline face is preloaded' );
sr2_assert( ! in_array( SKYYROSE2_URI . '/assets/sot/fonts/cinzel-latin.woff2', array_column( $preloads, 'href' ), true ), 'the former Cinzel headline face does not compete for first-view bandwidth' );
foreach ( $preloads as $record ) {
	sr2_assert( 'font' === $record['as'] && 'font/woff2' === $record['type'] && 'anonymous' === $record['crossorigin'], 'font preload records are CORS font preloads' );
	sr2_assert( 1 === preg_match( '#url\\(["\']?' . preg_quote( $record['href'], '#' ) . '["\']?\\)#', $head ), 'preload href matches the inline @font-face URL byte for byte: ' . $record['href'] );
}
sr2_assert( 2 === count( skyyrose2_critical_font_preloads( array( $preloads[0] ) ) ), 'an existing href is not preloaded twice' );

echo "critical-rendering: OK\n";
