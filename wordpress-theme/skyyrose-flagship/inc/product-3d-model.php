<?php
/**
 * Product 3D model — URL policy + viewer enqueue.
 *
 * Pure helpers (no hooks) shared by the WooCommerce meta box / button in
 * inc/woocommerce.php and the template enqueue in inc/enqueue-templates.php.
 * Kept hook-free so tests/unit can load it under the WP stubs.
 *
 * The viewer runs under the theme CSP (connect-src 'self'), and three r170 is
 * self-hosted under assets/js/lib/<SKYYROSE_THREE_LIB_DIR>/ — the version is in
 * the path so an upgrade is a new URL (the module imports are intentionally
 * un-versioned: a ?ver on our import would load a second copy of three).
 *
 * @package SkyyRose
 * @since 2.3.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

if ( ! defined( 'SKYYROSE_THREE_LIB_DIR' ) ) {
	define( 'SKYYROSE_THREE_LIB_DIR', 'three-0.170.0' );
}

/**
 * Sanitize a product 3D model URL.
 *
 * Accepts a same-site relative path (/wp-content/…/model.glb) or an absolute
 * https URL on this site's host, ending in .glb or .gltf. Everything else —
 * http, protocol-relative, off-site hosts (which the CSP would block at
 * runtime with no admin feedback), other extensions — sanitizes to ''.
 *
 * @since 2.3.0
 *
 * @param string $url Raw URL from the meta box or post meta.
 * @return string Clean URL, or '' when rejected.
 */
function skyyrose_sanitize_3d_model_url( $url ) {
	$url = trim( (string) $url );
	if ( '' === $url ) {
		return '';
	}

	$clean = esc_url_raw( $url, array( 'https' ) );
	if ( '' === $clean ) {
		return '';
	}

	/*
	 * Validate the CANONICAL form, and reject anything canonicalization changed.
	 * esc_url_raw strips characters (\ " < >), so testing the raw string first was
	 * unsound: "/\/evil.com/x.glb" passed a leading-"//" check and then BECAME
	 * "//evil.com/x.glb" — protocol-relative, off-site. Fail closed on any rewrite.
	 */
	if ( $clean !== $url ) {
		return '';
	}

	// "//host/file.glb" is protocol-relative, not same-site — esc_url_raw passes it through.
	if ( 0 === strpos( $clean, '//' ) ) {
		return '';
	}

	// Credentials and an explicit port both make fetch() fail or leave the origin — no
	// silent runtime error; reject at save time so the admin sees it.
	if ( null !== wp_parse_url( $clean, PHP_URL_USER ) || null !== wp_parse_url( $clean, PHP_URL_PORT ) ) {
		return '';
	}

	if ( 0 !== strpos( $clean, '/' ) ) {
		if ( 'https' !== wp_parse_url( $clean, PHP_URL_SCHEME ) ) {
			return '';
		}
		$host      = strtolower( (string) wp_parse_url( $clean, PHP_URL_HOST ) );
		$site_host = strtolower( (string) wp_parse_url( home_url(), PHP_URL_HOST ) );
		if ( '' === $host || $host !== $site_host ) {
			return '';
		}
	}

	$path = (string) wp_parse_url( $clean, PHP_URL_PATH );
	$ext  = strtolower( pathinfo( $path, PATHINFO_EXTENSION ) );
	if ( ! in_array( $ext, array( 'glb', 'gltf' ), true ) ) {
		return '';
	}

	return $clean;
}

/**
 * Sanitized 3D model URL bound to a product, or '' when none/invalid.
 *
 * Re-sanitizes on read so meta stored before the hardening is held to the
 * same rule as new saves.
 *
 * @since 2.3.0
 *
 * @param int $product_id Product post ID.
 * @return string
 */
function skyyrose_get_product_3d_model_url( $product_id ) {
	return skyyrose_sanitize_3d_model_url( get_post_meta( $product_id, '_product_3d_model', true ) );
}

/**
 * Enqueue the PDP 3D viewer click gate (idempotent).
 *
 * Called by skyyrose_woocommerce_3d_model_button() right before it prints, so
 * the script follows the button wherever it renders (theme PDP template, the
 * woocommerce_single_product_summary hook on a [product_page] shortcode…),
 * and by the template enqueue for the earlier-in-head path. The enqueued file
 * is a small click gate; three + decoders are dynamic-import()ed on first
 * click. Footer strategy so an enqueue during the_content still prints.
 *
 * @since 2.3.0
 * @return bool True when the viewer is (already) enqueued, false when its files are missing.
 */
function skyyrose_enqueue_product_3d_viewer() {
	if ( wp_script_is( 'skyyrose-product-3d-viewer', 'enqueued' ) ) {
		return true;
	}

	$js_dir  = SKYYROSE_DIR . '/assets/js';
	$js_uri  = SKYYROSE_ASSETS_URI . '/js';
	$use_min = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;
	$lib_dir = 'lib/' . SKYYROSE_THREE_LIB_DIR;

	$viewer_js = $use_min && file_exists( $js_dir . '/product-3d-viewer.min.js' )
		? 'product-3d-viewer.min.js' : 'product-3d-viewer.js';
	if ( ! file_exists( $js_dir . '/' . $viewer_js ) || ! file_exists( $js_dir . '/' . $lib_dir . '/three.module.min.js' ) ) {
		return false;
	}

	wp_enqueue_script(
		'skyyrose-product-3d-viewer',
		$js_uri . '/' . $viewer_js,
		array(),
		SKYYROSE_VERSION,
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
	wp_localize_script(
		'skyyrose-product-3d-viewer',
		'skyyRoseProduct3d',
		array(
			'libBase' => trailingslashit( $js_uri . '/' . $lib_dir ),
			'i18n'    => array(
				'title'   => __( 'View in 3D', 'skyyrose' ),
				'close'   => __( 'Close 3D viewer', 'skyyrose' ),
				'loading' => __( 'Loading 3D model…', 'skyyrose' ),
				'ready'   => __( '3D model loaded', 'skyyrose' ),
				'hint'    => __( 'Drag to rotate · Scroll or pinch to zoom', 'skyyrose' ),
				'error'   => __( 'The 3D model could not be loaded. Please try again later.', 'skyyrose' ),
				'noWebgl' => __( 'Your browser cannot display 3D models. The photos show every detail.', 'skyyrose' ),
			),
		)
	);

	return true;
}
