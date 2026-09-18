<?php
/**
 * Centralized Product Catalog — unified product registry loader
 *
 * Single source of truth for all product data:
 *   data/logo-registry.json
 * The CSV and dossier files are generated compatibility exports.
 *
 * Every consumer (templates, WooCommerce overrides, 404 fallback, immersive
 * templates, JSON-LD, admin screens, sync scripts) MUST read through this file.
 * No other catalog source is authoritative — catalog.yaml, manifest.json,
 * the per-skill products.csv files, and any worktree copies are retired.
 *
 * @package SkyyRose
 * @since   7.0.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Absolute path to the generated compatibility catalog CSV.
 *
 * @since 7.0.0
 * @return string
 */
function skyyrose_catalog_csv_path() {
	return get_theme_file_path( 'data/skyyrose-catalog.csv' );
}

/**
 * Get the full product catalog, keyed by SKU.
 *
 * Reads data/logo-registry.json products on first call, caches in a static for the
 * duration of the request. Returns the stable storefront projection of the
 * registry commerce fields and garment specifications.
 *
 * @since 7.0.0
 * @return array<string, array> Associative array of all products keyed by SKU.
 */
function skyyrose_get_product_catalog() {
	static $catalog = null;

	if ( null !== $catalog ) {
		return $catalog;
	}

	$catalog       = array();
	$registry_path = get_theme_file_path( 'data/logo-registry.json' );
	if ( ! is_readable( $registry_path ) ) {
		return $catalog;
	}
	// Local immutable request snapshot; cache identity follows the registry bytes.
	// phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	$raw = file_get_contents( $registry_path );
	if ( false === $raw ) {
		return $catalog;
	}
	$cache_key = 'skyyrose_product_catalog_' . hash( 'sha256', $raw );
	if ( function_exists( 'wp_cache_get' ) ) {
		$cached = wp_cache_get( $cache_key, 'skyyrose' );
		if ( is_array( $cached ) && ! empty( $cached ) ) {
			$catalog = $cached;
			return $catalog;
		}
	}
	$registry = json_decode( $raw, true );
	if ( ! is_array( $registry ) || empty( $registry['products'] ) ) {
		return $catalog;
	}
	foreach ( $registry['products'] as $record ) {
		$data = $record['catalog'] ?? array();
		foreach ( array( 'fit', 'materials', 'features' ) as $field ) {
			$data[ $field ] = $record['garment'][ $field ]['specification'] ?? '';
		}
		$data['sizing_references'] = wp_json_encode( $record['garment']['sizing_references'] ?? array() );
		if ( isset( $record['garment']['color'] ) ) {
			$data['color'] = $record['garment']['color'];
		}
		if ( isset( $record['garment']['available_sizes'] ) ) {
			$data['sizes'] = implode( '|', $record['garment']['available_sizes'] );
		}
		foreach ( array( 'image', 'front_model_image', 'back_image', 'back_model_image' ) as $slot ) {
			$data[ $slot ] = $record['images'][ $slot ]['path'] ?? '';
		}
		$sku = isset( $data['sku'] ) ? trim( $data['sku'] ) : '';
		if ( '' === $sku ) {
			continue;
		}

		$catalog[ $sku ] = array(
			'sku'               => $sku,
			'name'              => $data['name'] ?? '',
			'price'             => isset( $data['price'] ) ? (float) $data['price'] : 0.0,
			'collection'        => $data['collection'] ?? '',
			'description'       => $data['description'] ?? '',
			'badge'             => $data['badge'] ?? '',
			'image'             => $data['image'] ?? '',
			'front_model_image' => $data['front_model_image'] ?? '',
			'back_image'        => $data['back_image'] ?? '',
			'back_model_image'  => $data['back_model_image'] ?? '',
			'sizes'             => $data['sizes'] ?? '',
			'color'             => $data['color'] ?? '',
			'fit'               => $data['fit'],
			'materials'         => $data['materials'],
			'features'          => $data['features'],
			'sizing_references' => $data['sizing_references'],
			'edition_size'      => isset( $data['edition_size'] ) ? (int) $data['edition_size'] : 0,
			'published'         => (bool) (int) $data['published'],
			'is_preorder'       => (bool) (int) $data['is_preorder'],
			'garment_type_lock' => $data['garment_type_lock'] ?? '',
			'dossier_slug'      => $data['dossier_slug'] ?? '',
		);
	}

	if ( function_exists( 'wp_cache_set' ) && ! empty( $catalog ) ) {
		wp_cache_set( $cache_key, $catalog, 'skyyrose', HOUR_IN_SECONDS );
	}

	return $catalog;
}

/**
 * Pick the best available display image for a product card.
 *
 * Callers that only need "show me the product image" should use this
 * helper instead of reaching into product['image'] / front_model_image
 * directly. Keeps the image-slot precedence in one place.
 *
 * @since 7.1.0
 * @param  array $product Product data array from skyyrose_get_product().
 * @return string Theme-relative path to the best available image.
 */
function skyyrose_get_product_display_image( $product ) {
	// IMAGERY PRECEDENCE (canon, 2026-06-16): front-model-first, matching
	// product-card-holo.php and the WC ghost-loop filter. Keep all three in sync.
	foreach ( array( 'front_model_image', 'image', 'back_model_image', 'back_image' ) as $slot ) {
		$value = $product[ $slot ] ?? '';
		if ( is_string( $value ) && '' !== $value ) {
			return $value;
		}
	}
	return '';
}

/**
 * Get a single product by SKU.
 *
 * @since 3.2.1
 * @param  string $sku Product SKU (e.g., 'br-006').
 * @return array|null  Product data array or null if not found.
 */
function skyyrose_get_product( $sku ) {
	$sku     = sanitize_key( $sku );
	$catalog = skyyrose_get_product_catalog();
	return $catalog[ $sku ] ?? null;
}

/**
 * Get all products for a specific collection.
 *
 * @since 3.2.1
 * @param  string $collection Collection slug: 'black-rose', 'love-hurts', 'signature', 'kids-capsule'.
 * @return array  Array of product data arrays for the collection.
 */
function skyyrose_get_collection_products( $collection ) {
	static $cache = array();

	$collection = sanitize_key( $collection );
	if ( isset( $cache[ $collection ] ) ) {
		return $cache[ $collection ];
	}

	$catalog  = skyyrose_get_product_catalog();
	$products = array();

	foreach ( $catalog as $product ) {
		if ( $product['collection'] === $collection ) {
			$products[] = $product;
		}
	}

	$cache[ $collection ] = $products;
	return $products;
}

/**
 * Normalize a SKU to its base product SKU (strip variant suffixes).
 *
 * Handles: sg-001-tee → sg-001, br-003a → br-003.
 *
 * @since 6.3.0
 * @param  string $sku SKU with optional variant suffix.
 * @return string Base SKU.
 */
function skyyrose_normalize_sku( $sku ) {
	$sku = preg_replace( '/-(tee|shorts)$/', '', $sku );
	return preg_replace( '/([a-z]{2,4}-\d{3})[a-z]$/', '$1', $sku );
}

/**
 * Format a product price for display.
 *
 * Returns 'Coming Soon' for unpublished products without pre-order,
 * or the formatted dollar amount.
 *
 * @since 3.2.1
 * @param  array $product Product data array.
 * @return string Formatted price string.
 */
function skyyrose_format_price( $product ) {
	if ( ! $product['published'] && ! $product['is_preorder'] ) {
		return esc_html__( 'Coming Soon', 'skyyrose' );
	}

	$price = (float) $product['price'];

	if ( ! empty( $product['is_preorder'] ) && $price <= 0 ) {
		return esc_html__( 'Pre-Order', 'skyyrose' );
	}

	return '$' . number_format( $price, 0 );
}

/**
 * Get the theme-relative URI for a product image.
 *
 * @since 3.2.1
 * @param  string $image_path Relative image path from catalog (e.g., 'assets/images/products/br-001.webp').
 * @return string Full URI to the image.
 */
function skyyrose_product_image_uri( $image_path ) {
	if ( empty( $image_path ) ) {
		return get_theme_file_uri( 'assets/images/placeholder-product.jpg' );
	}

	/*
	 * Serve a .webp sibling when one exists on disk. Several catalog entries
	 * name 2.4-2.6MB source PNGs that Photon can only recompress LOSSLESSLY
	 * (795-892KB on the wire at w=768 — round-7 mobile LCP contention on
	 * shop/black-rose/signature/landing). The catalog path stays canonical
	 * (SOT untouched); this swaps the encoding of the same pixels at the
	 * presentation layer. No sibling on disk = original path, unchanged.
	 */
	if ( str_ends_with( $image_path, '.png' ) ) {
		$webp_sibling = substr( $image_path, 0, -4 ) . '.webp';
		if ( is_readable( get_theme_file_path( $webp_sibling ) ) ) {
			return get_theme_file_uri( $webp_sibling );
		}
	}
	return get_theme_file_uri( $image_path );
}

/**
 * Get the editorial-PDP eligibility record for a product by SKU.
 *
 * Dossiers (data/dossiers/*.md) are INTERNAL render-pipeline specs —
 * garment locks, branding placement, negative prompts, scene direction.
 * They are Corey-authored internal documents: never parsed at runtime,
 * never rendered as consumer copy, and excluded from the deploy artifact
 * (scripts/deploy-theme.sh). The storefront consumes only a compiled
 * boolean index, data/editorial-index.json, generated by
 * scripts/build-editorial-index.js (`npm run build` from wordpress-theme/).
 *
 * Fails CLOSED: a missing/invalid index yields null for every SKU, which
 * routes the PDP to the standard (non-editorial) layout — never a raw dump.
 *
 * The internal-field keys are retained (always empty) so the return shape
 * matches the pre-1.11.2 contract relied on by ProductCatalogTest.
 *
 * @since 7.2.0
 * @since 1.11.2 Reads compiled editorial-index.json; raw dossiers retired from runtime.
 * @param  string $sku Product SKU.
 * @return array|null  Eligibility record or null when not editorial-eligible.
 */
function skyyrose_get_product_dossier( $sku ) {
	static $eligible = null;

	$sku     = sanitize_key( $sku );
	$product = skyyrose_get_product( $sku );
	if ( ! $product || empty( $product['dossier_slug'] ) ) {
		return null;
	}

	if ( null === $eligible ) {
		$eligible = array();
		$path     = get_theme_file_path( 'data/editorial-index.json' );
		if ( is_readable( $path ) ) {
			// phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- local theme file read.
			$json = json_decode( (string) file_get_contents( $path ), true );
			if ( is_array( $json ) && isset( $json['eligible'] ) && is_array( $json['eligible'] ) ) {
				$eligible = $json['eligible'];
			}
		}
		if ( array() === $eligible && defined( 'WP_DEBUG' ) && WP_DEBUG ) {
			error_log( 'skyyrose: data/editorial-index.json missing or invalid — editorial PDP disabled (fail-closed). Run npm run build.' ); // phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_error_log
		}
	}

	$slug = sanitize_file_name( $product['dossier_slug'] );
	if ( empty( $eligible[ $slug ] ) ) {
		return null;
	}

	return array(
		'has_editorial_content' => true,
		'garment_type_lock'     => '',
		'branding'              => array(
			'front' => '',
			'back'  => '',
			'other' => '',
		),
	);
}

/**
 * Get similarity-ranked SKUs for a product from data/product-similarities.json.
 *
 * Originally a fallback for the now-retired complete-the-look cross-sell.
 * Retained because the CLIP-embedding similarity data is still useful for
 * future ranking surfaces (search, recommendations, internal QA). Safe to
 * remove if no consumer materializes.
 *
 * @since 1.5.4
 *
 * @param  string $sku   Source SKU.
 * @param  int    $limit Max number of related SKUs to return.
 * @return array<int, string> Related SKUs, highest similarity first.
 */
function skyyrose_get_similarity_skus( $sku, $limit = 2 ) {
	static $data  = null;
	static $cache = array();

	$sku = sanitize_key( $sku );
	if ( '' === $sku ) {
		return array();
	}

	$cache_key = $sku . ':' . absint( $limit );
	if ( isset( $cache[ $cache_key ] ) ) {
		return $cache[ $cache_key ];
	}

	// Load + memoize the JSON once per request.
	if ( null === $data ) {
		$path = get_theme_file_path( 'data/product-similarities.json' );
		if ( ! is_readable( $path ) ) {
			$data = array();
		} else {
			// phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- local theme file read.
			$raw = file_get_contents( $path );
			if ( false === $raw || '' === $raw ) {
				$data = array();
			} else {
				$decoded = json_decode( $raw, true );
				$data    = ( is_array( $decoded ) && isset( $decoded['products'] ) && is_array( $decoded['products'] ) )
					? $decoded['products']
					: array();
			}
		}
	}

	if ( ! isset( $data[ $sku ]['global'] ) || ! is_array( $data[ $sku ]['global'] ) ) {
		$cache[ $cache_key ] = array();
		return array();
	}

	$result = array();
	foreach ( $data[ $sku ]['global'] as $entry ) {
		if ( isset( $entry['sku'] ) && is_string( $entry['sku'] ) ) {
			$result[] = sanitize_key( $entry['sku'] );
			if ( count( $result ) >= absint( $limit ) ) {
				break;
			}
		}
	}

	$cache[ $cache_key ] = $result;
	return $result;
}

/**
 * Get the best available URL for a product.
 *
 * Uses WooCommerce permalink if product exists, falls back to pre-order page.
 *
 * @since 3.2.3
 * @param  string $sku Product SKU.
 * @return string Product URL.
 */
function skyyrose_product_url( $sku ) {
	if ( function_exists( 'wc_get_product_id_by_sku' ) ) {
		$lookup_sku = skyyrose_normalize_sku( $sku );
		$product_id = wc_get_product_id_by_sku( $lookup_sku );
		if ( $product_id ) {
			return get_permalink( $product_id );
		}
	}

	$product = skyyrose_get_product( $sku );
	if ( $product && ! empty( $product['is_preorder'] ) ) {
		return home_url( '/pre-order/#' . sanitize_title( $sku ) );
	}
	if ( $product && ! empty( $product['collection'] ) ) {
		return home_url( '/collections/' . sanitize_title( $product['collection'] ) . '/#' . sanitize_title( $sku ) );
	}

	return home_url( '/pre-order/#' . sanitize_title( $sku ) );
}
