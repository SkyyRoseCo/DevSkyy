<?php
/**
 * Enqueue — Experience Engine phases 2/3/4 + commercial polish
 *
 * Each phase function is gated by `skyyrose_see_is_module_active()` so the
 * features can be toggled from the WP admin without a code deploy. Extracted
 * from inc/enqueue.php in v1.5.0 to keep that file under the 800-line cap.
 *
 * Hook priority order:
 *   25 — commercial-polish (after template styles at 20, so it has highest
 *        CSS specificity for the typography/card refinement layer)
 *   30 — phase 2 (performance-guardian, brand-atmosphere)
 *   40 — phase 3 (experience-analyzer, smart-showcase, micro-interactions)
 *   42 — phase 4 (personalization) — before personalization.php's
 *        wp_localize_script at priority 45
 *
 * @package SkyyRose
 * @since   1.5.0
 */

defined( 'ABSPATH' ) || exit;

/**
 * Phase 2a — Performance Guardian (loads globally, all pages).
 *
 * @since  1.5.3
 * @return void
 */
function skyyrose_enqueue_phase2_performance_guardian(): void {
	if ( ! skyyrose_see_is_module_active( 'performance_guardian' ) ) {
		return;
	}
	$base_js_dir = SKYYROSE_DIR . '/assets/js';
	$use_min     = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;
	$pg_file     = $use_min && file_exists( $base_js_dir . '/performance-guardian.min.js' )
		? 'performance-guardian.min.js' : 'performance-guardian.js';
	if ( ! file_exists( $base_js_dir . '/' . $pg_file ) ) {
		return;
	}
	wp_enqueue_script(
		'skyyrose-performance-guardian',
		SKYYROSE_ASSETS_URI . '/js/' . $pg_file,
		array(),
		SKYYROSE_VERSION,
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
}

/**
 * Phase 2b — Brand Atmosphere (collection pages only).
 *
 * @since  1.5.3
 * @return void
 */
function skyyrose_enqueue_phase2_brand_atmosphere(): void {
	if ( ! skyyrose_see_is_module_active( 'brand_atmosphere' ) ) {
		return;
	}
	$slug = skyyrose_get_current_template_slug();
	if ( 'collection-standalone' !== $slug ) {
		return;
	}
	$base_js_dir  = SKYYROSE_DIR . '/assets/js';
	$base_css_dir = SKYYROSE_DIR . '/assets/css';
	$use_min      = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;

	$ba_css = $use_min && file_exists( $base_css_dir . '/brand-atmosphere.min.css' )
		? 'brand-atmosphere.min.css' : 'brand-atmosphere.css';
	if ( file_exists( $base_css_dir . '/' . $ba_css ) ) {
		wp_enqueue_style(
			'skyyrose-brand-atmosphere',
			SKYYROSE_ASSETS_URI . '/css/' . $ba_css,
			array( 'skyyrose-design-tokens' ),
			SKYYROSE_VERSION
		);
	}
	$ba_js = $use_min && file_exists( $base_js_dir . '/brand-atmosphere.min.js' )
		? 'brand-atmosphere.min.js' : 'brand-atmosphere.js';
	if ( ! file_exists( $base_js_dir . '/' . $ba_js ) ) {
		return;
	}
	wp_enqueue_script(
		'skyyrose-brand-atmosphere',
		SKYYROSE_ASSETS_URI . '/js/' . $ba_js,
		array( 'skyyrose-performance-guardian' ),
		SKYYROSE_VERSION,
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
}

/**
 * Enqueue Phase 2 Experience Engine assets.
 *
 * - performance-guardian.js loads globally on every page (priority 30).
 * - brand-atmosphere.css + brand-atmosphere.js load on collection pages only.
 *
 * Both checks respect the Experience Engine module activation state.
 */
function skyyrose_enqueue_phase2_assets(): void {
	if ( ! function_exists( 'skyyrose_see_is_module_active' ) ) {
		return;
	}
	skyyrose_enqueue_phase2_performance_guardian();
	skyyrose_enqueue_phase2_brand_atmosphere();
}

/**
 * Phase 3 product-page slugs (where experience-analyzer, smart-showcase,
 * micro-interactions should load). Single source of truth so the sub-helpers
 * and any future Phase 3 modules share one slug list.
 *
 * @since  1.5.3
 * @return array<int, string>
 */
function skyyrose_phase3_product_slugs(): array {
	return array(
		'collection-standalone',
		'shop-archive',
		'search',
		'front-page',
		'landing',
		'preorder-gateway',
	);
}

/**
 * Phase 3a — Experience Analyzer (behavioral tracking + event relay).
 *
 * @since  1.5.3
 * @return void
 */
function skyyrose_enqueue_phase3_experience_analyzer(): void {
	if ( ! skyyrose_see_is_module_active( 'experience_analyzer' ) ) {
		return;
	}
	$base_js_dir = SKYYROSE_DIR . '/assets/js';
	$js_uri      = SKYYROSE_ASSETS_URI . '/js';
	$use_min     = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;
	$file        = $use_min && file_exists( $base_js_dir . '/experience-analyzer.min.js' )
		? 'experience-analyzer.min.js' : 'experience-analyzer.js';
	if ( ! file_exists( $base_js_dir . '/' . $file ) ) {
		return;
	}
	wp_enqueue_script(
		'skyyrose-experience-analyzer',
		$js_uri . '/' . $file,
		array( 'skyyrose-performance-guardian' ),
		(string) filemtime( $base_js_dir . '/' . $file ),
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);

	// Shared ingest key for POST /analytics/events (launch spec C5) — static
	// per site, so cached page HTML stays valid.
	if ( function_exists( 'skyyrose_see_analytics_key' ) ) {
		wp_add_inline_script(
			'skyyrose-experience-analyzer',
			'window.skyyroseSEE = window.skyyroseSEE || {};' .
			'window.skyyroseSEE.key = ' . wp_json_encode( skyyrose_see_analytics_key() ) . ';',
			'before'
		);
	}
}

/**
 * Phase 3b — Smart Showcase (quick-view dialog + CSS).
 *
 * @since  1.5.3
 * @return void
 */
function skyyrose_enqueue_phase3_smart_showcase(): void {
	if ( ! skyyrose_see_is_module_active( 'smart_showcase' ) ) {
		return;
	}
	$base_js_dir  = SKYYROSE_DIR . '/assets/js';
	$base_css_dir = SKYYROSE_DIR . '/assets/css';
	$js_uri       = SKYYROSE_ASSETS_URI . '/js';
	$css_uri      = SKYYROSE_ASSETS_URI . '/css';
	$use_min      = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;

	$ss_css = $use_min && file_exists( $base_css_dir . '/smart-showcase.min.css' )
		? 'smart-showcase.min.css' : 'smart-showcase.css';
	if ( file_exists( $base_css_dir . '/' . $ss_css ) ) {
		wp_enqueue_style(
			'skyyrose-smart-showcase',
			$css_uri . '/' . $ss_css,
			array( 'skyyrose-design-tokens' ),
			SKYYROSE_VERSION
		);
	}

	$file = $use_min && file_exists( $base_js_dir . '/smart-showcase.min.js' )
		? 'smart-showcase.min.js' : 'smart-showcase.js';
	if ( ! file_exists( $base_js_dir . '/' . $file ) ) {
		return;
	}
	wp_enqueue_script(
		'skyyrose-smart-showcase',
		$js_uri . '/' . $file,
		array( 'skyyrose-performance-guardian' ),
		SKYYROSE_VERSION,
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
}

/**
 * Phase 3c — Micro-Interactions (cart fly-to + wishlist burst).
 *
 * @since  1.5.3
 * @return void
 */
function skyyrose_enqueue_phase3_micro_interactions(): void {
	if ( ! skyyrose_see_is_module_active( 'micro_interactions' ) ) {
		return;
	}
	$base_js_dir = SKYYROSE_DIR . '/assets/js';
	$js_uri      = SKYYROSE_ASSETS_URI . '/js';
	$use_min     = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;
	$file        = $use_min && file_exists( $base_js_dir . '/micro-interactions.min.js' )
		? 'micro-interactions.min.js' : 'micro-interactions.js';
	if ( ! file_exists( $base_js_dir . '/' . $file ) ) {
		return;
	}
	wp_enqueue_script(
		'skyyrose-micro-interactions',
		$js_uri . '/' . $file,
		array( 'skyyrose-performance-guardian' ),
		SKYYROSE_VERSION,
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
}

/**
 * Enqueue Phase 3 Experience Engine assets.
 *
 * Loads experience-analyzer, smart-showcase, and micro-interactions on any
 * page that renders product cards. All three depend on skyyrose-performance-guardian
 * (Phase 2). Each sub-helper is independently testable + each stays under
 * the 50-line function cap.
 */
function skyyrose_enqueue_phase3_assets(): void {
	if ( ! function_exists( 'skyyrose_see_is_module_active' ) ) {
		return;
	}
	if ( ! in_array( skyyrose_get_current_template_slug(), skyyrose_phase3_product_slugs(), true ) ) {
		return;
	}
	skyyrose_enqueue_phase3_experience_analyzer();
	skyyrose_enqueue_phase3_smart_showcase();
	skyyrose_enqueue_phase3_micro_interactions();
}

/**
 * Enqueue Phase 4 Experience Engine assets — Personalization.
 *
 * Personalization.js + personalization.css load on pages that render product
 * grids or single products. Runs at priority 42 so personalization.php's
 * localize (priority 45) attaches to the already-registered handle.
 */
function skyyrose_enqueue_phase4_assets(): void {
	if ( ! function_exists( 'skyyrose_see_is_module_active' ) ) {
		return;
	}
	$product_slugs = array_merge(
		skyyrose_phase3_product_slugs(),
		array( 'single-product' )
	);
	if ( ! in_array( skyyrose_get_current_template_slug(), $product_slugs, true ) ) {
		return;
	}
	if ( ! skyyrose_see_is_module_active( 'personalization' ) ) {
		return;
	}
	$base_js_dir  = SKYYROSE_DIR . '/assets/js';
	$base_css_dir = SKYYROSE_DIR . '/assets/css';
	$use_min      = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;
	$pers_css     = $use_min && file_exists( $base_css_dir . '/personalization.min.css' )
		? 'personalization.min.css' : 'personalization.css';
	if ( file_exists( $base_css_dir . '/' . $pers_css ) ) {
		wp_enqueue_style(
			'skyyrose-personalization',
			SKYYROSE_ASSETS_URI . '/css/' . $pers_css,
			array( 'skyyrose-design-tokens' ),
			SKYYROSE_VERSION
		);
	}
	$pers_js = $use_min && file_exists( $base_js_dir . '/personalization.min.js' )
		? 'personalization.min.js' : 'personalization.js';
	if ( ! file_exists( $base_js_dir . '/' . $pers_js ) ) {
		return;
	}
	wp_enqueue_script(
		'skyyrose-personalization',
		SKYYROSE_ASSETS_URI . '/js/' . $pers_js,
		array(),
		(string) filemtime( $base_js_dir . '/' . $pers_js ),
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
}

/**
 * Enqueue commercial polish CSS as the LAST stylesheet.
 *
 * Runs at priority 25 — after template-specific styles (priority 20).
 * Ensures the commercial polish layer can refine typography, cards,
 * collection story-world overrides, and focus states with highest specificity.
 *
 * @since 1.0.0
 * @return void
 */
function skyyrose_enqueue_commercial_polish() {
	$base_uri = SKYYROSE_ASSETS_URI . '/css';
	$base_dir = SKYYROSE_DIR . '/assets/css';
	$use_min  = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;

	$polish_file = $use_min && file_exists( $base_dir . '/commercial-polish.min.css' )
		? 'commercial-polish.min.css' : 'commercial-polish.css';

	if ( file_exists( $base_dir . '/' . $polish_file ) ) {
		wp_enqueue_style(
			'skyyrose-commercial-polish',
			$base_uri . '/' . $polish_file,
			array( 'skyyrose-design-tokens' ),
			SKYYROSE_VERSION
		);
	}
}

add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_commercial_polish', 25 );
add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_phase2_assets', 30 );
add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_phase3_assets', 40 );
add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_phase4_assets', 42 );

/**
 * Enqueue the unified collection-pages stylesheet plus cross-collection
 * View Transitions API choreography. Called from skyyrose_enqueue_template_styles()
 * in inc/enqueue.php when the current template slug is 'collection-standalone'.
 * Lives here (not in enqueue.php) so the parent file stays under 800 lines.
 *
 * @since  1.5.6
 * @param  string $base_css_dir Absolute path to assets/css directory.
 * @param  string $base_css_uri Public URI of assets/css directory.
 * @param  bool   $use_min      Whether to prefer minified files.
 * @param  array  $global_deps  Dependency handle list for the collection stylesheet.
 * @return void
 */
function skyyrose_enqueue_collection_styles( $base_css_dir, $base_css_uri, $use_min, $global_deps ) {
	$col_css = $use_min && file_exists( $base_css_dir . '/collection-pages.min.css' )
		? 'collection-pages.min.css' : 'collection-pages.css';
	if ( file_exists( $base_css_dir . '/' . $col_css ) ) {
		wp_enqueue_style( 'skyyrose-collection-pages', $base_css_uri . '/' . $col_css, $global_deps, SKYYROSE_VERSION );
	}

	// View Transitions API choreography for cross-collection nav. Progressive
	// enhancement — browsers without support fall back to normal page loads;
	// reduced-motion users get the feature short-circuited inside the stylesheet.
	$vt_css = $use_min && file_exists( $base_css_dir . '/view-transitions.min.css' )
		? 'view-transitions.min.css' : 'view-transitions.css';
	if ( file_exists( $base_css_dir . '/' . $vt_css ) ) {
		wp_enqueue_style( 'skyyrose-view-transitions', $base_css_uri . '/' . $vt_css, array( 'skyyrose-collection-pages' ), SKYYROSE_VERSION );
	}

	// Per-collection motion identity (visual-pattern-shortlist packages):
	// Black Rose fog/noise/tilt, Love Hurts ink/VHS, Signature aurora/chrome/
	// stars, Kids Capsule spring/bounce/confetti, cross-collection underline
	// + dividers. Depends on collection-pages so its overrides win cascade order.
	$motion_css = $use_min && file_exists( $base_css_dir . '/collection-motion.min.css' )
		? 'collection-motion.min.css' : 'collection-motion.css';
	if ( file_exists( $base_css_dir . '/' . $motion_css ) ) {
		wp_enqueue_style( 'skyyrose-collection-motion', $base_css_uri . '/' . $motion_css, array( 'skyyrose-collection-pages' ), SKYYROSE_VERSION );
	}

	// Film spine (Variant C, founder pick 2026-07-29): sticky scroll-scrub
	// stage + beats + shoppable hotspots for collection/film-spine.php.
	// Split from collection-motion.css (800-line gate); same dep so its
	// .col-film--spine overrides load after the legacy ambient rules.
	$spine_css = $use_min && file_exists( $base_css_dir . '/collection-film-spine.min.css' )
		? 'collection-film-spine.min.css' : 'collection-film-spine.css';
	if ( file_exists( $base_css_dir . '/' . $spine_css ) ) {
		wp_enqueue_style( 'skyyrose-collection-film-spine', $base_css_uri . '/' . $spine_css, array( 'skyyrose-collection-pages' ), SKYYROSE_VERSION );
	}
}
