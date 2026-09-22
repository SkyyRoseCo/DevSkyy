<?php
/**
 * Home critical rendering.
 *
 * Two narrow, theme-owned delivery paths for the front page:
 *
 * 1. A structural CSS contract (assets/css/critical/home.min.css, built from
 *    the enqueued source sheets by scripts/build-critical-css.mjs) is inlined
 *    in <head> so the header, hero stage, first-viewport typography, primary
 *    controls and rotating-mark container have their geometry before any
 *    external stylesheet arrives. It does not replace the full stylesheets and
 *    it is independent of any optimizer-generated critical CSS.
 *
 * 2. The unchanged hero controller (assets/js/visual-recovery.js) is printed
 *    inline immediately after the hero markup so it executes as soon as the
 *    parser reaches it, ahead of jQuery, WooCommerce and other classic
 *    scripts. The footer copy is dropped on the front page only. Collection
 *    routes keep their enqueued controller.
 *
 * Both paths fail closed: an absent or malformed built file prints nothing and
 * the page still receives its full stylesheets and footer scripts.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/** Absolute path of the built Home critical CSS. */
function skyyrose2_critical_css_path() {
	return SKYYROSE2_DIR . '/assets/css/critical/home.min.css';
}

/** Whether the current request is the front page that receives the contract. */
function skyyrose2_critical_css_applies() {
	if ( is_admin() || is_customize_preview() || ! is_front_page() ) {
		return false;
	}

	return ! apply_filters( 'skyyrose2_critical_css_disabled', false );
}

/**
 * Read the built contract once per request.
 *
 * @return string Empty when the file is absent, empty or contains a closing style tag.
 */
function skyyrose2_critical_css() {
	static $css = null;
	if ( null !== $css ) {
		return $css;
	}

	$css  = '';
	$path = skyyrose2_critical_css_path();
	if ( ! is_readable( $path ) ) {
		return $css;
	}

	$contents = trim( (string) file_get_contents( $path ) ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- Theme-bundled built asset, not a remote URL.
	if ( '' === $contents || false !== stripos( $contents, '</style' ) ) {
		return $css;
	}

	$css = str_replace( '__SKYYROSE2_ASSETS__', SKYYROSE2_URI . '/assets', $contents );

	return $css;
}

/** Print the contract before external stylesheets and before Core's own inline styles. */
function skyyrose2_print_critical_css() {
	if ( ! skyyrose2_critical_css_applies() ) {
		return;
	}

	$css = skyyrose2_critical_css();
	if ( '' === $css ) {
		return;
	}

	echo '<style id="skyyrose2-critical-home">' . $css . '</style>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Built theme asset validated in skyyrose2_critical_css().
}
add_action( 'wp_head', 'skyyrose2_print_critical_css', 1 );

/**
 * The hero controller source that Home prints inline.
 *
 * @return string Empty when the built file is absent, empty or contains a closing script tag.
 */
function skyyrose2_hero_bootstrap_script() {
	static $script = null;
	if ( null !== $script ) {
		return $script;
	}

	$script = '';
	$path   = SKYYROSE2_DIR . '/assets/js/visual-recovery' . skyyrose2_asset_suffix() . '.js';
	if ( ! is_readable( $path ) ) {
		return $script;
	}

	$contents = trim( (string) file_get_contents( $path ) ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- Theme-bundled built asset, not a remote URL.
	if ( '' === $contents || false !== stripos( $contents, '</script' ) ) {
		return $script;
	}

	$script = $contents;

	return $script;
}

/** Whether the front page inlines the hero controller instead of enqueuing it. */
function skyyrose2_hero_bootstrap_inline() {
	if ( is_admin() || ! is_front_page() ) {
		return false;
	}

	if ( apply_filters( 'skyyrose2_hero_bootstrap_disabled', false ) ) {
		return false;
	}

	return '' !== skyyrose2_hero_bootstrap_script();
}

/**
 * Print the controller directly after the hero markup.
 *
 * The data-jetpack-boost="ignore" attribute keeps Jetpack Boost's "Defer
 * Non-Essential JavaScript" module from moving this tag to the end of the
 * document; without it the controller would wait behind every classic script.
 */
function skyyrose2_print_hero_bootstrap() {
	if ( ! skyyrose2_hero_bootstrap_inline() ) {
		return;
	}

	wp_print_inline_script_tag(
		skyyrose2_hero_bootstrap_script(),
		array(
			'id'                 => 'skyyrose2-visual-recovery-early',
			'data-jetpack-boost' => 'ignore',
		)
	);
}

/**
 * First-view font files the front page preloads.
 *
 * The @font-face declarations arrive inline with the contract, but a font
 * download only starts once text that uses the face is laid out. Preloading
 * the two faces the editorial first view sets (Cinzel title, Hanken body and
 * controls) closes that gap so the first paint is set in the brand faces
 * instead of swapping to them a frame later.
 *
 * @return string[] File names beneath assets/sot/fonts.
 */
function skyyrose2_critical_font_files() {
	return array( 'hanken-grotesk-latin.woff2', 'cinzel-latin.woff2' );
}

/**
 * Add the first-view font preloads on the front page, once per href.
 *
 * The preload href must equal the @font-face URL byte for byte or the browser
 * downloads the face twice; both resolve through skyyrose2_sot_asset_uri().
 *
 * @param array<int,mixed> $resources Existing preload records.
 * @return array<int,mixed>
 */
function skyyrose2_critical_font_preloads( $resources ) {
	if ( ! is_array( $resources ) || ! skyyrose2_critical_css_applies() || '' === skyyrose2_critical_css() ) {
		return $resources;
	}

	$existing = array();
	foreach ( $resources as $resource ) {
		if ( is_array( $resource ) && ! empty( $resource['href'] ) ) {
			$existing[ $resource['href'] ] = true;
		}
	}

	foreach ( skyyrose2_critical_font_files() as $file ) {
		if ( ! is_readable( SKYYROSE2_DIR . '/assets/sot/fonts/' . $file ) ) {
			continue;
		}
		$href = skyyrose2_sot_asset_uri( 'fonts/' . $file );
		if ( isset( $existing[ $href ] ) ) {
			continue;
		}
		$resources[]       = array(
			'href'        => $href,
			'as'          => 'font',
			'type'        => 'font/woff2',
			'crossorigin' => 'anonymous',
		);
		$existing[ $href ] = true;
	}

	return $resources;
}
add_filter( 'wp_preload_resources', 'skyyrose2_critical_font_preloads', 20 );
