<?php
/**
 * Native archive projection of theme.css. All other styles and routes retain
 * their original delivery and cascade. This module does not inline CSS itself.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;

/** Reject descendant symlinks; the configured theme root may be a release link. */
function skyyrose2_archive_style_file( $name ) {
	if ( ! is_string( $name ) || ! preg_match( '/^[a-z-]+(?:\.min)?\.(css|json)$/D', $name ) ) {
		return '';
	}
	$file = SKYYROSE2_DIR . '/assets/css/' . $name;
	for ( $entry = $file; $entry !== SKYYROSE2_DIR && dirname( $entry ) !== $entry; $entry = dirname( $entry ) ) {
		if ( is_link( $entry ) ) { return ''; }
	}
	return is_file( $file ) && is_readable( $file ) ? $file : '';
}

/** Bind current canonical source/full min and generated projection to receipt. */
function skyyrose2_archive_style_asset() {
	$path = skyyrose2_archive_style_file( 'archive-theme.json' );
	if ( ! $path ) { return array(); }
	$manifest = json_decode( file_get_contents( $path ), true );
	if ( ! is_array( $manifest ) || 'skyyrose.archive-theme-projection.v1' !== ( $manifest['schema'] ?? '' ) || ! is_array( $manifest['classification'] ?? null ) || ! $manifest['classification'] ) { return array(); }
	foreach ( array( 'source' => 'theme.css', 'originalMin' => 'theme.min.css', 'output' => 'archive-theme.min.css' ) as $key => $name ) {
		$record = $manifest[ $key ] ?? null;
		$file = skyyrose2_archive_style_file( $name );
		if ( ! is_array( $record ) || ! $file || $name !== ( $record['file'] ?? '' ) || hash_file( 'sha256', $file ) !== ( $record['sha256'] ?? '' ) || filesize( $file ) !== ( $record['bytes'] ?? -1 ) ) { return array(); }
	}
	return array(
		'src' => SKYYROSE2_URI . '/assets/css/archive-theme.min.css',
		'path' => skyyrose2_archive_style_file( 'archive-theme.min.css' ),
		'ver' => $manifest['output']['sha256'],
	);
}

/** Core's admin-color resolver is inert for these frontend handles. */
function skyyrose2_archive_style_filters_safe() {
	global $wp_filter;
	foreach ( array( 'style_loader_src', 'style_loader_tag', 'print_styles_array', 'pre_wp_filesize', 'wp_filesize' ) as $name ) {
		if ( ! has_filter( $name ) ) { continue; }
		$callbacks = $wp_filter[ $name ]->callbacks ?? array();
		if ( 'style_loader_src' !== $name || array_keys( $callbacks ) !== array( 10 ) || array_keys( $callbacks[10] ) !== array( 'wp_style_loader_src' ) || ( $callbacks[10]['wp_style_loader_src']['function'] ?? null ) !== 'wp_style_loader_src' || ( $callbacks[10]['wp_style_loader_src']['accepted_args'] ?? null ) !== 2 ) { return false; }
	}
	return true;
}

/** Replace only the native theme handle before Core's optional inline offer. */
function skyyrose2_archive_theme_projection() {
	if ( is_admin() || wp_installing() || wp_doing_ajax() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) || ( defined( 'SCRIPT_DEBUG' ) && SCRIPT_DEBUG ) || is_rtl() || ! function_exists( 'is_shop' ) || ! ( is_shop() || is_product_taxonomy() ) || ! is_main_query() || ! apply_filters( 'skyyrose2_archive_theme_projection_enabled', true ) ) { return; }
	if ( ! skyyrose2_archive_style_filters_safe() ) { return; }
	$styles = wp_styles();
	$handle = 'skyyrose2-theme';
	$style = $styles->registered[ $handle ] ?? null;
	if ( ! $style || ! in_array( $handle, $styles->queue, true ) || count( array_keys( $styles->queue, $handle, true ) ) !== 1 || ! empty( $styles->done ) || ! empty( $styles->to_do ) || ! empty( $styles->args[ $handle ] ) ) { return; }
	if ( SKYYROSE2_URI . '/assets/css/theme.min.css' !== $style->src || array( 'skyyrose2-tokens' ) !== $style->deps || 'all' !== $style->args ) { return; }
	foreach ( $style->extra as $key => $value ) {
		if ( 'path' !== $key || SKYYROSE2_DIR . '/assets/css/theme.min.css' !== $value ) { return; }
	}
	$asset = skyyrose2_archive_style_asset();
	if ( ! $asset ) { return; }
	$inline_css = function_exists( '_wp_normalize_relative_css_links' ) ? _wp_normalize_relative_css_links( file_get_contents( $asset['path'] ), $asset['src'] ) : null;
	$original = clone $style;
	$queue = $styles->queue;
	$style->src = $asset['src'];
	$style->ver = $asset['ver'];
	unset( $style->extra['path'] );
	$expected = clone $style;
	// Core may add this exact path and then inline its normalized CSS. Accept
	// only that known transformation; all extension additions trigger fallback.
	add_action( 'wp_print_styles', function () use ( $styles, $handle, $original, $expected, $asset, $queue, $inline_css ) {
		$current = $styles->registered[ $handle ] ?? null;
		if ( ! $current ) { return; }
		$copy = clone $current;
		$owned_inline = false;
		$owned_index = false;
		if ( ( $copy->extra['inlined_src'] ?? null ) === $asset['src'] && is_string( $inline_css ) && is_array( $copy->extra['after'] ?? null ) ) {
			$owned_index = array_search( $inline_css, $copy->extra['after'], true );
		}
		if ( ( $copy->extra['path'] ?? null ) === $asset['path'] ) { unset( $copy->extra['path'] ); }
		if ( false !== $owned_index ) {
			$owned_inline = true;
			if ( false === $copy->src ) { $copy->src = $expected->src; }
			unset( $copy->extra['inlined_src'] );
			unset( $copy->extra['after'][ $owned_index ] );
			$copy->extra['after'] = array_values( $copy->extra['after'] );
			if ( ! $copy->extra['after'] ) { unset( $copy->extra['after'] ); }
		}
		if ( $copy == $expected && $styles->queue === $queue && skyyrose2_archive_style_filters_safe() ) { return; }
		if ( $current->src === $expected->src || ( false === $current->src && $owned_inline ) ) { $current->src = $original->src; }
		if ( $current->ver === $expected->ver ) { $current->ver = $original->ver; }
		if ( ( $current->extra['path'] ?? null ) === $asset['path'] ) { unset( $current->extra['path'] ); }
		if ( $owned_inline ) {
			unset( $current->extra['inlined_src'] );
			unset( $current->extra['after'][ $owned_index ] );
			$current->extra['after'] = array_values( $current->extra['after'] );
			if ( ! $current->extra['after'] ) { unset( $current->extra['after'] ); }
		}
		if ( $current->src === $original->src && ! isset( $current->extra['path'] ) && isset( $original->extra['path'] ) ) { $current->extra['path'] = $original->extra['path']; }
	}, PHP_INT_MAX );
}
add_action( 'wp_enqueue_scripts', 'skyyrose2_archive_theme_projection', 100 );

/** Six unchanged inputs; the projected theme has its own source manifest. */
function skyyrose2_archive_style_inputs() {
	$file = skyyrose2_archive_style_file( 'archive-style-inputs.json' );
	if ( ! $file ) { return array(); }
	$manifest = json_decode( file_get_contents( $file ), true );
	$names = array( 'design-tokens', 'shop-page', 'controls', 'global-shell', 'visual-recovery', 'mascot' );
	if ( ! is_array( $manifest ) || 'skyyrose.archive-style-inputs.v1' !== ( $manifest['schema'] ?? '' ) || ! is_array( $manifest['sources'] ?? null ) || count( $names ) !== count( $manifest['sources'] ) ) { return array(); }
	$files = array();
	foreach ( $names as $index => $name ) {
		$record = $manifest['sources'][ $index ] ?? null;
		$path = skyyrose2_archive_style_file( $name . '.min.css' );
		if ( ! is_array( $record ) || ! $path || ( $record['file'] ?? null ) !== $name . '.min.css' || ( $record['sha256'] ?? null ) !== hash_file( 'sha256', $path ) || ( $record['bytes'] ?? null ) !== filesize( $path ) ) { return array(); }
		$files[ $name ] = $path;
	}
	return $files;
}

/** Never compete with another budget policy, even if it returns the same value. */
function skyyrose2_archive_inline_filter_safe() {
	global $wp_filter;
	$callbacks = $wp_filter['styles_inline_size_limit']->callbacks ?? array();
	return array_keys( $callbacks ) === array( PHP_INT_MAX )
		&& array_keys( $callbacks[ PHP_INT_MAX ] ) === array( 'skyyrose2_archive_inline_budget' )
		&& ( $callbacks[ PHP_INT_MAX ]['skyyrose2_archive_inline_budget']['function'] ?? null ) === 'skyyrose2_archive_inline_budget'
		&& ( $callbacks[ PHP_INT_MAX ]['skyyrose2_archive_inline_budget']['accepted_args'] ?? null ) === 1;
}

/** Native order is checked on a clone, without changing the live queue. */
function skyyrose2_archive_style_order( $styles, $handles ) {
	$start = array_search( $handles[0], $styles->queue, true );
	if ( false === $start || array_slice( $styles->queue, $start, count( $handles ) ) !== $handles ) { return false; }
	foreach ( $handles as $handle ) {
		if ( count( array_keys( $styles->queue, $handle, true ) ) !== 1 ) { return false; }
	}
	$resolved = clone $styles;
	$resolved->to_do = array();
	if ( ! $resolved->all_deps( $resolved->queue ) ) { return false; }
	$start = array_search( $handles[0], $resolved->to_do, true );
	return false !== $start && array_slice( $resolved->to_do, $start, count( $handles ) ) === $handles;
}

/**
 * Core common.css is allowed only when the original 40 KB allocation already
 * inlines it. Its existing native placeholder, media and RTL metadata stay intact.
 */
function skyyrose2_archive_native_common( $styles ) {
	$style = $styles->registered['wp-block-library'] ?? null;
	$relative = '/' . WPINC . '/css/dist/block-library/common.min.css';
	$canonical = rtrim( ABSPATH, '/' ) . $relative;
	$path = $style->extra['path'] ?? null;
	if ( ! $style || $style->src !== $relative || array() !== $style->deps || false !== $style->ver || ! in_array( $style->args, array( null, 'all' ), true ) || ! is_string( $path ) || preg_replace( '~/+~', '/', $path ) !== $canonical || ! is_file( $path ) || ! is_readable( $path ) || ! empty( $styles->args['wp-block-library'] ) ) { return array(); }
	for ( $entry = $canonical; $entry !== rtrim( ABSPATH, '/' ) && dirname( $entry ) !== $entry; $entry = dirname( $entry ) ) {
		if ( is_link( $entry ) ) { return array(); }
	}
	$after = $style->extra['after'] ?? null;
	if ( ! is_array( $after ) || array_keys( $after ) !== array( 0 ) || ! is_string( $after[0] ) || ! preg_match( '~^/\*wp_block_styles_on_demand_placeholder:[a-f0-9]{13}\*/$~D', $after[0] ) || $style->extra !== array( 'path' => $path, 'rtl' => 'replace', 'suffix' => '.min', 'after' => $after ) ) { return array(); }
	$allocation = array();
	foreach ( $styles->queue as $handle ) {
		$item = $styles->registered[ $handle ] ?? null;
		$item_path = $item->extra['path'] ?? null;
		if ( ! $item || ! $item->src || ! $item_path ) { continue; }
		if ( ! is_string( $item_path ) || ! is_file( $item_path ) || ! is_readable( $item_path ) ) { return array(); }
		$allocation[] = array( 'handle' => $handle, 'bytes' => filesize( $item_path ) );
	}
	usort( $allocation, function ( $left, $right ) { return $left['bytes'] <=> $right['bytes']; } );
	$total = 0;
	$already_inline = false;
	foreach ( $allocation as $item ) {
		if ( $total + $item['bytes'] > 40000 ) { break; }
		$total += $item['bytes'];
		if ( 'wp-block-library' === $item['handle'] ) { $already_inline = true; }
	}
	if ( ! $already_inline ) { return array(); }
	return array( 'original' => clone $style, 'bytes' => filesize( $path ), 'chunk' => _wp_normalize_relative_css_links( file_get_contents( $path ), $style->src ) );
}

/**
 * Head-only allowance for seven verified archive sheets, inlined by Core.
 * Every unrelated stylesheet and every unsupported context keeps Core's budget.
 */
function skyyrose2_archive_inline_budget( $limit ) {
	if ( 40000 !== $limit || ! doing_action( 'wp_head' ) || doing_action( 'wp_footer' ) || did_action( 'wp_print_styles' ) || is_admin() || wp_installing() || wp_doing_ajax() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) || ( defined( 'SCRIPT_DEBUG' ) && SCRIPT_DEBUG ) || is_rtl() || ! function_exists( 'is_shop' ) || ! ( is_shop() || is_product_taxonomy() ) || ! is_main_query() || ! apply_filters( 'skyyrose2_archive_inline_enabled', true ) ) { return $limit; }
	$styles = wp_styles();
	if ( 'WP_Styles' !== get_class( $styles ) || ! empty( $styles->done ) || ! empty( $styles->to_do ) || ! skyyrose2_archive_style_filters_safe() || ! skyyrose2_archive_inline_filter_safe() ) { return $limit; }
	$files = skyyrose2_archive_style_inputs();
	$projection = skyyrose2_archive_style_asset();
	if ( ! $files || ! $projection ) { return $limit; }
	$assets = array( 'tokens' => 'design-tokens', 'theme' => 'archive-theme', 'shop-page' => 'shop-page', 'controls' => 'controls', 'global-shell' => 'global-shell', 'visual-recovery' => 'visual-recovery', 'mascot' => 'mascot' );
	$files['archive-theme'] = $projection['path'];
	$handles = array_map( function ( $name ) { return 'skyyrose2-' . $name; }, array_keys( $assets ) );
	if ( ! skyyrose2_archive_style_order( $styles, $handles ) ) { return $limit; }
	$native_common = array();
	// The budget is global: any other eligible path could acquire new inline
	// delivery or lose its media condition, so decline the entire allowance.
	foreach ( $styles->queue as $handle ) {
		$style = $styles->registered[ $handle ] ?? null;
		if ( $style && $style->src && ! empty( $style->extra['path'] ) && ! in_array( $handle, $handles, true ) ) {
			if ( 'wp-block-library' !== $handle ) { return $limit; }
			$native_common = skyyrose2_archive_native_common( $styles );
			if ( ! $native_common ) { return $limit; }
		}
	}
	$originals = array();
	$chunks = array();
	$total = $native_common['bytes'] ?? 0;
	foreach ( $assets as $name => $asset ) {
		$handle = 'skyyrose2-' . $name;
		$style = $styles->registered[ $handle ] ?? null;
		$deps = 'tokens' === $name ? array() : array( in_array( $name, array( 'theme', 'mascot' ), true ) ? 'skyyrose2-tokens' : 'skyyrose2-theme' );
		$src = SKYYROSE2_URI . '/assets/css/' . $asset . '.min.css';
		if ( ! $style || $style->src !== $src || $style->deps !== $deps || 'all' !== $style->args || ! empty( $styles->args[ $handle ] ) || $style->extra !== array( 'path' => $files[ $asset ] ) ) { return $limit; }
		if ( 'theme' === $name && $style->ver !== $projection['ver'] ) { return $limit; }
		$total += filesize( $files[ $asset ] );
		$originals[ $handle ] = clone $style;
		$chunks[ $handle ] = _wp_normalize_relative_css_links( file_get_contents( $files[ $asset ] ), $src );
	}
	if ( $total > 100000 ) { return $limit; }
	$queue = $styles->queue;
	// Core owns the mutation. Before print, tolerate only its exact normalized
	// chunk, otherwise undo that chunk without erasing an extension's changes.
	add_action( 'wp_print_styles', function () use ( $styles, $originals, $chunks, $queue, $native_common ) {
		$valid = $styles->queue === $queue && skyyrose2_archive_style_filters_safe() && skyyrose2_archive_inline_filter_safe() && skyyrose2_archive_style_order( $styles, array_keys( $originals ) );
		if ( $native_common ) {
			$current = $styles->registered['wp-block-library'] ?? null;
			$copy = $current ? clone $current : null;
			$original = $native_common['original'];
			if ( $copy && false === $copy->src && ( $copy->extra['inlined_src'] ?? null ) === $original->src && is_array( $copy->extra['after'] ?? null ) && ( $copy->extra['after'][0] ?? null ) === $native_common['chunk'] ) {
				$copy->src = $original->src;
				unset( $copy->extra['inlined_src'] ); array_shift( $copy->extra['after'] );
			}
			$valid = $valid && $copy == $original;
		}
		foreach ( $styles->queue as $handle ) {
			if ( $native_common && 'wp-block-library' === $handle ) { continue; }
			$style = $styles->registered[ $handle ] ?? null;
			if ( $style && $style->src && ! empty( $style->extra['path'] ) && ! isset( $originals[ $handle ] ) ) { $valid = false; }
		}
		$owned = array();
		foreach ( $originals as $handle => $original ) {
			$current = $styles->registered[ $handle ] ?? null;
			if ( ! $current ) { $valid = false; continue; }
			$copy = clone $current;
			$index = false;
			if ( ( $copy->extra['inlined_src'] ?? null ) === $original->src && is_array( $copy->extra['after'] ?? null ) ) { $index = array_search( $chunks[ $handle ], $copy->extra['after'], true ); }
			if ( false !== $index ) {
				$owned[ $handle ] = $index;
				if ( false === $copy->src ) { $copy->src = $original->src; }
				unset( $copy->extra['inlined_src'], $copy->extra['after'][ $index ] );
				$copy->extra['after'] = array_values( $copy->extra['after'] );
				if ( ! $copy->extra['after'] ) { unset( $copy->extra['after'] ); }
			}
			$valid = $valid && $copy == $original;
		}
		if ( $valid ) { return; }
		foreach ( $owned as $handle => $index ) {
			$current = $styles->registered[ $handle ];
			if ( false === $current->src ) { $current->src = $originals[ $handle ]->src; }
			unset( $current->extra['inlined_src'], $current->extra['after'][ $index ] );
			$current->extra['after'] = array_values( $current->extra['after'] );
			if ( ! $current->extra['after'] ) { unset( $current->extra['after'] ); }
			if ( $current->src !== $originals[ $handle ]->src && ( $current->extra['path'] ?? null ) === $originals[ $handle ]->extra['path'] ) { unset( $current->extra['path'] ); }
		}
	}, PHP_INT_MAX );
	return 100000;
}
add_filter( 'styles_inline_size_limit', 'skyyrose2_archive_inline_budget', PHP_INT_MAX );
