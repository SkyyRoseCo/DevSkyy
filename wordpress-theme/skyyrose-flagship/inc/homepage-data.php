<?php
/**
 * Homepage v3 — data assembly.
 *
 * Every homepage act reads its collection facts from here, and this file
 * reads them from the existing single sources: inc/collections-config.php for
 * names / taglines / canonical URLs, skyyrose_get_collection_products() for
 * piece counts, and skyyrose_get_collections_world_config() for the scene
 * stills the collection rooms use as backgrounds. Nothing is hardcoded that
 * already lives in a source of truth.
 *
 * Template parts under template-parts/home/ call these instead of receiving
 * a page-level array, so front-page.php stays pure orchestration.
 *
 * @package SkyyRose
 * @since   1.13.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Canonical homepage collection order (Black Rose 01 → Kids Capsule 04).
 *
 * @since 1.13.0
 * @return array<int, string> Collection slugs.
 */
function skyyrose_home_collection_order() {
	return array( 'black-rose', 'love-hurts', 'signature', 'kids-capsule' );
}

/**
 * Resolve a collection's canonical page URL.
 *
 * Always via the config helper: /collections/{slug}/ is the LOCKED canonical
 * route (inc/redirects.php rewrites it onto the legacy collection-{slug}
 * pages), so no template may reconstruct either form by hand.
 *
 * @since 1.13.0
 * @param  string $slug Collection slug.
 * @return string Absolute URL.
 */
function skyyrose_home_collection_url( $slug ) {
	$config = function_exists( 'skyyrose_get_collection' ) ? skyyrose_get_collection( $slug ) : null;
	if ( ! empty( $config['page_url'] ) ) {
		return $config['page_url'];
	}
	return home_url( '/collections/' . sanitize_key( $slug ) . '/' );
}

/**
 * Collection name lockup images (brand-script artwork, never type-rendered).
 *
 * Kids Capsule has no lockup asset in the theme — it is the one documented
 * gap, and callers fall back to type in Grand Hotel when the key is absent.
 *
 * @since 1.13.0
 * @return array<string, string> Slug => extensionless asset base URI.
 */
function skyyrose_home_lockups() {
	$base = SKYYROSE_ASSETS_URI . '/images/hero-overlays/';
	return array(
		'black-rose' => $base . 'br-brand-script-logotype',
		'love-hurts' => $base . 'lh-logo-combined',
		'signature'  => $base . 'sig-brand-skyy-rose-gold',
	);
}

/**
 * Static hero navigation row — one cell per collection.
 *
 * @since 1.13.0
 * @return array<int, array<string, string>> Nav entries.
 */
function skyyrose_home_collection_nav() {
	$kickers = array(
		'signature'    => __( 'Core Luxury', 'skyyrose' ),
		'black-rose'   => __( 'Drop Focus', 'skyyrose' ),
		'love-hurts'   => __( 'Now Styling', 'skyyrose' ),
		'kids-capsule' => __( 'Born Into It', 'skyyrose' ),
	);
	$abbr    = array(
		'signature'    => 'sig',
		'black-rose'   => 'br',
		'love-hurts'   => 'lh',
		'kids-capsule' => 'kc',
	);
	$out     = array();
	foreach ( array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ) as $slug ) {
		$config = function_exists( 'skyyrose_get_collection' ) ? skyyrose_get_collection( $slug ) : null;
		$out[]  = array(
			'abbr'   => $abbr[ $slug ],
			'label'  => $config['label'] ?? ucwords( str_replace( '-', ' ', $slug ) ),
			'kicker' => $kickers[ $slug ],
			'href'   => skyyrose_home_collection_url( $slug ),
		);
	}
	return $out;
}

/**
 * Hero marquee marks — the brand artwork that doubles as collection nav.
 *
 * 'src' empty means "no lockup asset exists for this route": the template
 * renders the label in type instead of inventing a file path.
 *
 * @since 1.13.0
 * @return array<int, array<string, mixed>> Mark descriptors.
 */
function skyyrose_home_marquee_marks() {
	$branding = SKYYROSE_ASSETS_URI . '/branding/';
	return array(
		array(
			'src'    => $branding . 'signature-logo.webp',
			'label'  => __( 'Signature', 'skyyrose' ),
			'href'   => skyyrose_home_collection_url( 'signature' ),
			'height' => 40,
			'invert' => false,
			'wide'   => false,
		),
		array(
			'src'    => $branding . 'black-rose-collection-text.webp',
			'label'  => __( 'Black Rose', 'skyyrose' ),
			'href'   => skyyrose_home_collection_url( 'black-rose' ),
			'height' => 64,
			'invert' => true,
			'wide'   => true,
		),
		array(
			'src'    => $branding . 'love-hurts-logo.webp',
			'label'  => __( 'Love Hurts', 'skyyrose' ),
			'href'   => skyyrose_home_collection_url( 'love-hurts' ),
			'height' => 64,
			'invert' => true,
			'wide'   => false,
		),
		array(
			// No Kids Capsule lockup asset exists — set in Grand Hotel type.
			'src'    => '',
			'label'  => __( 'Kids Capsule', 'skyyrose' ),
			'href'   => skyyrose_home_collection_url( 'kids-capsule' ),
			'height' => 40,
			'invert' => false,
			'wide'   => false,
		),
		array(
			'src'    => $branding . 'skyyrose-monogram.webp',
			'label'  => __( 'All collections', 'skyyrose' ),
			'href'   => home_url( '/collections/' ),
			'height' => 60,
			'invert' => true,
			'wide'   => false,
		),
		array(
			'src'    => $branding . 'skyyrose-rose-icon.webp',
			'label'  => __( 'Our story', 'skyyrose' ),
			'href'   => home_url( '/about/' ),
			'height' => 56,
			'invert' => true,
			'wide'   => false,
		),
	);
}

/**
 * Ticker copy — collection names above the rule, attributes below.
 *
 * @since 1.13.0
 * @return array{names: array<int, string>, lower: array<int, array<string, string>>}
 */
function skyyrose_home_ticker() {
	$names = array();
	foreach ( skyyrose_home_collection_order() as $slug ) {
		$config  = function_exists( 'skyyrose_get_collection' ) ? skyyrose_get_collection( $slug ) : null;
		$names[] = $config['label'] ?? ucwords( str_replace( '-', ' ', $slug ) );
	}

	$lower = array(
		array(
			'kind' => 'sub',
			'text' => __( 'Oakland Made', 'skyyrose' ),
		),
		array(
			'kind' => 'sub',
			'text' => __( 'Gender Neutral', 'skyyrose' ),
		),
		array(
			'kind' => 'sub',
			'text' => __( 'Limited Edition', 'skyyrose' ),
		),
		array(
			'kind' => 'sub',
			'text' => __( 'Luxury Streetwear', 'skyyrose' ),
		),
		array(
			'kind' => 'sub',
			'text' => __( 'Built Different', 'skyyrose' ),
		),
	);

	return array(
		'names' => $names,
		'lower' => $lower,
	);
}

/**
 * The on-model garment that fronts each collection room.
 *
 * SKUs are drawn from the theme's already eyes-on-verified hero pool and were
 * re-verified pixel-against-catalog for this build (2026-07-29): br-006 black
 * satin bomber with chest rose, lh-004 white/black varsity bomber with the
 * red Love Hurts script, sg-009 black jacket with white sherpa lining and
 * chest rose, kids-001 red/black/white colorblock hoodie set.
 *
 * Paths always resolve through skyyrose_sot_product_image_uri() at render
 * time — the SKU is the only thing recorded here.
 *
 * @since 1.13.0
 * @return array<string, array<string, string>> Slug => { sku, alt }.
 */
function skyyrose_home_room_figures() {
	return array(
		'black-rose'   => array(
			'sku' => 'br-006',
			'alt' => __( 'Black Rose satin bomber with chest rose embroidery, worn on model', 'skyyrose' ),
		),
		'love-hurts'   => array(
			'sku' => 'lh-004',
			'alt' => __( 'Love Hurts varsity bomber in white and black with red script, worn on model', 'skyyrose' ),
		),
		'signature'    => array(
			'sku' => 'sg-009',
			'alt' => __( 'Signature sherpa-lined jacket with chest rose embroidery, worn on model', 'skyyrose' ),
		),
		'kids-capsule' => array(
			'sku' => 'kids-001',
			'alt' => __( 'Kids Capsule colorblock hoodie set in red, black and white, worn on model', 'skyyrose' ),
		),
	);
}

/**
 * Collection rooms for Act III.
 *
 * Piece counts come from skyyrose_get_collection_products() — never a literal.
 * Room backgrounds reuse the collections-world engine's per-collection scene
 * stills, resolved through skyyrose_get_collections_world_config() so the
 * Photon srcset and the asset path stay single-sourced with that surface.
 * The garment in front of that ground resolves through the SOT image helper.
 *
 * @since 1.13.0
 * @return array<int, array<string, mixed>> Room descriptors.
 */
function skyyrose_home_rooms() {
	$scenes = array();
	if ( function_exists( 'skyyrose_get_collections_world_config' ) ) {
		$world = skyyrose_get_collections_world_config();
		foreach ( $world['sections'] as $section ) {
			$scenes[ $section['id'] ] = $section;
		}
	}

	$lockups = skyyrose_home_lockups();
	$figures = skyyrose_home_room_figures();
	$rooms   = array();

	foreach ( skyyrose_home_collection_order() as $slug ) {
		$config = function_exists( 'skyyrose_get_collection' ) ? skyyrose_get_collection( $slug ) : null;
		if ( ! $config ) {
			continue;
		}
		$count = function_exists( 'skyyrose_get_collection_products' )
			? count( skyyrose_get_collection_products( $slug ) )
			: 0;
		$scene = $scenes[ $slug ] ?? array();

		$figure     = '';
		$figure_set = '';
		$figure_alt = '';
		if ( isset( $figures[ $slug ] ) && function_exists( 'skyyrose_sot_product_image_uri' ) ) {
			$figure     = skyyrose_sot_product_image_uri( $figures[ $slug ]['sku'], 'front' );
			$figure_alt = $figures[ $slug ]['alt'];
			if ( '' !== $figure && function_exists( 'skyyrose_photon_srcset' ) ) {
				$figure_set = skyyrose_photon_srcset( $figure, array( 480, 768, 1024 ) );
			}
		}

		$rooms[] = array(
			'slug'        => $slug,
			'label'       => $config['label'],
			'num'         => $config['front_page']['num'] ?? '',
			'poetic'      => $config['front_page']['poetic_tagline'] ?? '',
			'description' => $config['description'] ?? '',
			'run'         => $config['front_page']['label'] ?? '',
			'count'       => $count,
			'href'        => skyyrose_home_collection_url( $slug ),
			'lockup'      => $lockups[ $slug ] ?? '',
			'still'       => $scene['still'] ?? '',
			'still_set'   => $scene['stillSet'] ?? '',
			'still_sizes' => $scene['stillSizes'] ?? '',
			'figure'      => $figure,
			'figure_set'  => $figure_set,
			'figure_alt'  => $figure_alt,
		);
	}

	return $rooms;
}

/**
 * Total catalog piece count across the four collections.
 *
 * @since 1.13.0
 * @return int Piece count.
 */
function skyyrose_home_total_pieces() {
	$total = 0;
	foreach ( skyyrose_home_collection_order() as $slug ) {
		if ( function_exists( 'skyyrose_get_collection_products' ) ) {
			$total += count( skyyrose_get_collection_products( $slug ) );
		}
	}
	return $total;
}

/**
 * Press features. Empty 'url' renders flat (no link) rather than inventing one.
 *
 * @since 1.13.0
 * @return array<int, array<string, string>> Press entries.
 */
function skyyrose_home_press() {
	return array(
		array(
			'name' => __( 'Maxim', 'skyyrose' ),
			'url'  => 'https://www.maxim.com/partner/14-game-changing-entrepreneurs-to-watch-in-2023/',
		),
		array(
			'name' => __( 'CEO Weekly', 'skyyrose' ),
			'url'  => 'https://ceoweekly.com/the-unyielding-journey-of-a-single-father-and-entrepreneur/',
		),
		array(
			'name' => __( 'San Francisco Post', 'skyyrose' ),
			'url'  => 'https://sanfranciscopost.com/the-skyy-rose-collection-from-oaklands-streets-to-fashion-heights/',
		),
		array(
			'name' => __( 'Best of Best Review', 'skyyrose' ),
			'url'  => 'https://bestofbestreview.com/awards/the-skyy-rose-collection-best-bay-area-clothing-line-award-2024',
		),
		array(
			'name' => __( 'The Blox', 'skyyrose' ),
			'url'  => '',
		),
	);
}
