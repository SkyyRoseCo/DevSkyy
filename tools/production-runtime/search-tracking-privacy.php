<?php
/**
 * Disable optional public Search tracking on the reviewed SkyyRose targets.
 *
 * Search remains registered and available. This separate runtime extension is
 * not part of the immutable V2 theme package. No cookie-dependent HTML is used.
 *
 * @package SkyyRoseRuntime
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** Determine whether this public request belongs to the reviewed scope. */
function skyyrose_runtime_search_privacy_applies(): bool {
	if ( is_admin() || wp_doing_ajax() || wp_doing_cron()
		|| ( defined( 'REST_REQUEST' ) && REST_REQUEST )
		|| ( defined( 'WP_CLI' ) && WP_CLI ) ) {
		return false;
	}
	$targets = array(
		'https://skyyrose.co' => array( 'skyyrose-flagship', 'skyyrose-flagship-2' ),
		'https://staging-7e48-skyyrose.wpcomstaging.com' => array( 'skyyrose-flagship-2' ),
	);
	$home = get_option( 'home' );
	if ( ! isset( $targets[ $home ] )
		|| ! in_array( get_stylesheet(), $targets[ $home ], true ) ) {
		return false;
	}
	return class_exists( 'Jetpack' ) && Jetpack::is_module_active( 'search' );
}

/** Disable Search's analytics pushes without changing its interface. */
function skyyrose_runtime_search_disable_tracking( bool $disabled ): bool {
	return skyyrose_runtime_search_privacy_applies() ? true : $disabled;
}

/** Remove only the optional tracking queue entry, preserving registration. */
function skyyrose_runtime_search_dequeue_tracking(): void {
	if ( skyyrose_runtime_search_privacy_applies() ) {
		wp_dequeue_script( 'jp-tracks' );
	}
}

/** Prevent late block enqueues or dependency resolution from printing Tracks. */
function skyyrose_runtime_search_tracking_tag( string $tag, string $handle ): string {
	if ( 'jp-tracks' === $handle && skyyrose_runtime_search_privacy_applies() ) {
		return '';
	}
	return $tag;
}

add_filter( 'jetpack_instant_search_disable_tracking', 'skyyrose_runtime_search_disable_tracking', PHP_INT_MAX );
add_action( 'wp_enqueue_scripts', 'skyyrose_runtime_search_dequeue_tracking', PHP_INT_MAX );
add_action( 'wp_print_footer_scripts', 'skyyrose_runtime_search_dequeue_tracking', PHP_INT_MAX );
add_filter( 'script_loader_tag', 'skyyrose_runtime_search_tracking_tag', PHP_INT_MAX, 2 );
