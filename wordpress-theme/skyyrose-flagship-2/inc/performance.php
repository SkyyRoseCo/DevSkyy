<?php
/**
 * Route-aware front-end performance policy.
 *
 * This module only changes delivery hints and removes assets that are unused on
 * fully theme-owned routes. It does not change the House of Roses markup,
 * WooCommerce purchase behavior, or the no-JavaScript presentation.
 *
 * Integration contract: require this file once from the theme root.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/** Remove legacy emoji payloads from public pages. */
function skyyrose2_performance_disable_emojis() {
	remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
	remove_action( 'wp_print_styles', 'print_emoji_styles' );
	remove_action( 'wp_enqueue_scripts', 'wp_enqueue_emoji_styles' );
	remove_filter( 'the_content_feed', 'wp_staticize_emoji' );
	remove_filter( 'comment_text_rss', 'wp_staticize_emoji' );
	remove_filter( 'wp_mail', 'wp_staticize_emoji_for_email' );
}
add_action( 'init', 'skyyrose2_performance_disable_emojis', 1 );

/**
 * Identify routes whose complete public markup is owned by this theme.
 *
 * Block styles and wp-embed remain available on ordinary editorial content,
 * WooCommerce archives, products, cart, checkout, and account routes.
 *
 * @return bool
 */
function skyyrose2_performance_is_governed_route() {
	if ( is_front_page() || is_page_template( 'template-collection.php' ) || ( function_exists( 'skyyrose2_collection_page_slug' ) && skyyrose2_collection_page_slug() ) ) {
		return true;
	}

	$immersive_templates = array(
		'template-immersive-signature.php',
		'template-immersive-black-rose.php',
		'template-immersive-love-hurts.php',
		'template-immersive-kids-capsule.php',
	);

	return is_page_template( $immersive_templates );
}

/** Remove public assets that governed routes do not render. */
function skyyrose2_performance_dequeue_unused_assets() {
	if ( ! is_user_logged_in() ) {
		wp_dequeue_style( 'dashicons' );
	}

	// Archive grid geometry is owned by shop-page.css. Retain Woo's general
	// controls, notices and Quick View styling; extensions can restore its layout.
	$is_archive = function_exists( 'is_shop' ) && ( is_shop() || is_product_taxonomy() );
	if ( $is_archive && ! apply_filters( 'skyyrose2_archive_native_woo_layout', false ) ) {
		wp_dequeue_style( 'woocommerce-layout' );
		wp_dequeue_style( 'woocommerce-smallscreen' );
	}

	if ( ! skyyrose2_performance_is_governed_route() ) {
		return;
	}

	$unused_styles = array(
		'wp-block-library',
		'wp-block-library-theme',
		'global-styles',
		'classic-theme-styles',
		'wc-blocks-style',
		'wc-blocks-packages-style',
		'wc-blocks-style-active-filters',
	);

	foreach ( $unused_styles as $handle ) {
		wp_dequeue_style( $handle );
	}

	wp_dequeue_script( 'wp-embed' );

	// These editorial routes render our cards, Quick View and bag dialog. Their
	// controls/notices are owned by theme.css, controls.css and global-shell.css;
	// Woo's product grids, tables and forms are not present. Keep native styles on
	// every transactional, archive, content and legacy immersive route. Extensions
	// adding native Woo markup here can opt back in without changing this policy.
	$collection = function_exists( 'skyyrose2_collection_page_slug' ) ? skyyrose2_collection_page_slug() : '';
	$owned_commerce = is_front_page() || ( $collection && function_exists( 'skyyrose2_collection_world_enabled' ) && skyyrose2_collection_world_enabled( $collection ) );
	if ( $owned_commerce && ! apply_filters( 'skyyrose2_editorial_native_woo_styles', false ) ) {
		foreach ( array( 'woocommerce-general', 'woocommerce-layout', 'woocommerce-smallscreen' ) as $handle ) {
			wp_dequeue_style( $handle );
		}
	}
}
add_action( 'wp_enqueue_scripts', 'skyyrose2_performance_dequeue_unused_assets', 100 );

/**
 * Offer small, exact theme styles to Core's bounded inline-style delivery.
 *
 * Core retains handle order, attached CSS and relative URL normalization. Its
 * total byte budget is unchanged; large sheets and every non-selected sheet
 * remain ordinary blocking stylesheet links, including the no-JS path.
 * Third-party replacements, alternate media and RTL variants are not bypassed.
 */
function skyyrose2_performance_inline_small_styles() {
	if ( ( defined( 'SCRIPT_DEBUG' ) && SCRIPT_DEBUG ) || ! apply_filters( 'skyyrose2_inline_small_styles', true ) ) {
		return;
	}

	$styles = wp_styles();
	$assets = array(
		'tokens' => 'design-tokens', 'controls' => 'controls',
		'theme' => 'archive-theme',
		'global-shell' => 'global-shell', 'visual-recovery' => 'visual-recovery',
		'home-page' => 'home-page', 'collection-world' => 'collection-world',
		'product-page' => 'product-page', 'shop-page' => 'shop-page',
		'hero-commerce-scenes' => 'hero-commerce-scenes',
		'collection-scene-motion' => 'collection-scene-motion', 'mascot' => 'mascot',
	);
	foreach ( $assets as $name => $asset ) {
		$handle = 'skyyrose2-' . $name;
		$style = $styles->registered[ $handle ] ?? null;
		if ( ! $style || ! in_array( $handle, $styles->queue, true ) || 'all' !== $style->args || ! empty( $style->extra['rtl'] ) || ! empty( $style->extra['conditional'] ) || ! empty( $style->extra['path'] ) ) {
			continue;
		}
		// The verified archive projection has a separate per-file ceiling;
		// Core still decides whether it fits the unchanged total 40KB budget.
		$limit = 'archive-theme' === $asset ? 32768 : 16384;
		$suffixes = 'archive-theme' === $asset ? array( '.min.css' ) : array( '.min.css', '.css' );
		foreach ( $suffixes as $suffix ) {
			$relative = '/assets/css/' . $asset . $suffix;
			$path = SKYYROSE2_DIR . $relative;
			if ( SKYYROSE2_URI . $relative === $style->src && is_readable( $path ) && filesize( $path ) <= $limit ) {
				wp_style_add_data( $handle, 'path', $path );
				break;
			}
		}
	}
}
add_action( 'wp_enqueue_scripts', 'skyyrose2_performance_inline_small_styles', 101 );

/**
 * Prevent the disabled emoji service from retaining a DNS-prefetch hint.
 * Preserve every hint registered by active plugins and route-owned media.
 *
 * @param array<int,mixed> $urls          Hint entries.
 * @param string           $relation_type Hint relationship.
 * @return array<int,mixed>
 */
function skyyrose2_performance_resource_hints( $urls, $relation_type ) {
	if ( 'dns-prefetch' !== $relation_type ) {
		return $urls;
	}

	return array_values(
		array_filter(
			$urls,
			static function ( $entry ) {
				$url = is_array( $entry ) ? ( $entry['href'] ?? '' ) : $entry;
				return false === strpos( (string) $url, 's.w.org' );
			}
		)
	);
}
add_filter( 'wp_resource_hints', 'skyyrose2_performance_resource_hints', 10, 2 );

/**
 * Keep attachment images responsive and free of conflicting load hints.
 *
 * WordPress remains responsible for native lazy-loading heuristics and srcset
 * generation. This filter fills metadata gaps and ensures an explicitly high
 * priority image is never simultaneously marked lazy.
 *
 * @param array<string,mixed> $attr       Image attributes.
 * @param WP_Post             $attachment Attachment object.
 * @return array<string,mixed>
 */
function skyyrose2_performance_image_attributes( $attr, $attachment ) {
	if ( 'high' === ( $attr['fetchpriority'] ?? '' ) ) {
		unset( $attr['loading'] );
	}

	if ( empty( $attr['decoding'] ) ) {
		$attr['decoding'] = 'async';
	}

	if ( ( empty( $attr['width'] ) || empty( $attr['height'] ) ) && ! empty( $attachment->ID ) ) {
		$metadata = wp_get_attachment_metadata( $attachment->ID );
		if ( is_array( $metadata ) ) {
			if ( empty( $attr['width'] ) && ! empty( $metadata['width'] ) ) {
				$attr['width'] = (int) $metadata['width'];
			}
			if ( empty( $attr['height'] ) && ! empty( $metadata['height'] ) ) {
				$attr['height'] = (int) $metadata['height'];
			}
		}
	}

	if ( ! empty( $attr['srcset'] ) && empty( $attr['sizes'] ) && ! empty( $attr['width'] ) ) {
		$attr['sizes'] = sprintf( '(max-width: %1$dpx) 100vw, %1$dpx', (int) $attr['width'] );
	}

	return $attr;
}
add_filter( 'wp_get_attachment_image_attributes', 'skyyrose2_performance_image_attributes', 20, 2 );

/**
 * Limit Core's automatic eager-loading allowance to the first content image.
 * Explicit template attributes continue to take precedence.
 *
 * @return int
 */
function skyyrose2_performance_loading_threshold() {
	return 1;
}
add_filter( 'wp_omit_loading_attr_threshold', 'skyyrose2_performance_loading_threshold' );

/**
 * MIME type for a preloadable image URL.
 *
 * @param string $url Image URL.
 * @return string
 */
function skyyrose2_performance_image_mime( $url ) {
	$extension = strtolower( pathinfo( wp_parse_url( $url, PHP_URL_PATH ) ?: '', PATHINFO_EXTENSION ) );
	$types     = array(
		'avif' => 'image/avif',
		'gif'  => 'image/gif',
		'jpg'  => 'image/jpeg',
		'jpeg' => 'image/jpeg',
		'png'  => 'image/png',
		'webp' => 'image/webp',
	);

	return $types[ $extension ] ?? '';
}

/**
 * Build a preload record only for a bundled SOT asset that exists.
 *
 * @param string $path  Path beneath assets/sot.
 * @param string $media Optional media query.
 * @return array<string,string>
 */
function skyyrose2_performance_sot_preload( $path, $media = '' ) {
	$path       = ltrim( (string) $path, '/' );
	$local_path = SKYYROSE2_DIR . '/assets/sot/' . $path;
	if ( ! is_readable( $local_path ) ) {
		return array();
	}

	$url      = skyyrose2_sot_asset_uri( $path );
	$resource = array(
		'href'          => $url,
		'as'            => 'image',
		'fetchpriority' => 'high',
	);
	$type     = skyyrose2_performance_image_mime( $url );
	if ( $type ) {
		$resource['type'] = $type;
	}
	if ( $media ) {
		$resource['media'] = $media;
	}

	return $resource;
}

/**
 * Build mutually exclusive preloads for an art-directed hero picture.
 *
 * Exactly one record matches a viewport, mirroring the template breakpoints.
 *
 * @param string $desktop Desktop SOT path.
 * @param string $tablet  Tablet SOT path.
 * @param string $mobile  Mobile SOT path.
 * @return array<int,array<string,string>>
 */
function skyyrose2_performance_art_directed_preloads( $desktop, $tablet, $mobile ) {
	$specification = array(
		array( $mobile, '(max-width: 47.99em)' ),
		array( $tablet, '(min-width: 48em) and (max-width: 74.99em)' ),
		array( $desktop, '(min-width: 75em)' ),
	);
	$resources     = array();

	foreach ( $specification as $item ) {
		$resource = skyyrose2_performance_sot_preload( $item[0], $item[1] );
		if ( $resource ) {
			$resources[] = $resource;
		}
	}

	return $resources;
}

/**
 * Resolve the one route-owned LCP asset (or one art-directed set).
 *
 * @return array<int,array<string,string>>
 */
function skyyrose2_performance_route_preloads() {
	if ( is_front_page() ) {
		return skyyrose2_performance_art_directed_preloads(
			'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1440w.webp',
			'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1024w.webp',
			'images/hero/responsive/black-rose-bay-bridge-monuments-v4-640w.webp'
		);
	}
	if ( function_exists( 'is_shop' ) && ( is_shop() || is_product_taxonomy() ) ) {
		$front = skyyrose2_performance_archive_front_preload();
		return $front ? array( $front ) : array();
	}

	if ( ( ( function_exists( 'skyyrose2_collection_page_slug' ) && skyyrose2_collection_page_slug() ) || is_page_template( 'template-collection.php' ) ) && function_exists( 'skyyrose2_collections' ) ) {
		$slug        = sanitize_title( get_post_field( 'post_name', get_queried_object_id() ) );
		$collections = skyyrose2_collections();
		$collection  = $collections[ $slug ] ?? array();
		if ( ! empty( $collection['hero'] ) ) {
			// The arrival <picture> selects its candidate by viewport, so the hint is art-directed the same way.
			return skyyrose2_performance_art_directed_preloads(
				$collection['hero'],
				$collection['hero_tablet'] ?? $collection['hero'],
				$collection['hero_mobile'] ?? $collection['hero']
			);
		}
	}

	$immersive_posters = array(
		'template-immersive-signature.php'    => 'images/hero/signature-golden-gate-monuments-v2.webp',
		'template-immersive-black-rose.php'   => 'images/hero/black-rose-bay-bridge-monuments-v4.webp',
		'template-immersive-love-hurts.php'   => 'images/hero/love-hurts-rose-aisle-monuments-v3.webp',
		'template-immersive-kids-capsule.php' => 'images/hero/kids-capsule-heir-throne-v3.webp',
	);
	foreach ( $immersive_posters as $template => $poster ) {
		if ( is_page_template( $template ) ) {
			$resource = skyyrose2_performance_sot_preload( $poster );
			return $resource ? array( $resource ) : array();
		}
	}

	if ( is_page() ) {
		$slug = sanitize_title( get_post_field( 'post_name', get_queried_object_id() ) );
		if ( 'collections' === $slug && function_exists( 'skyyrose2_collections' ) ) {
			// The collections index opens on the first world's monument (template-parts/collections/index.php).
			$first = current( skyyrose2_collections() );
			if ( empty( $first['hero'] ) ) {
				return array();
			}
			return skyyrose2_performance_art_directed_preloads(
				$first['hero'],
				$first['hero_tablet'] ?? $first['hero'],
				$first['hero_mobile'] ?? $first['hero']
			);
		}
		if ( in_array( $slug, array( 'pre-order', 'preorder' ), true ) ) {
			return skyyrose2_performance_art_directed_preloads(
				'images/preorder/responsive/black-rose-salon-1440w.webp',
				'images/preorder/responsive/black-rose-salon-1024w.webp',
				'images/preorder/responsive/black-rose-salon-640w.webp'
			);
		}
		// Contact renders no hero image since 2.5.0; only About keeps a page hero.
		$page_heroes = array(
			'about' => 'images/about/skyy-rose-founder-hero.webp',
		);
		if ( isset( $page_heroes[ $slug ] ) ) {
			$resource = skyyrose2_performance_sot_preload( $page_heroes[ $slug ] );
			return $resource ? array( $resource ) : array();
		}
	}

	$image_id   = 0;
	$image_size = 'full';
	if ( is_singular( 'product' ) && function_exists( 'wc_get_product' ) ) {
		$product    = wc_get_product( get_queried_object_id() );
		// Delivery hints obey the same authority as the visible PDP gallery.
		$media      = $product && function_exists( 'skyyrose2_product_commerce_media' ) ? skyyrose2_product_commerce_media( $product ) : array();
		$image_id   = (int) ( $media['ids'][0] ?? 0 );
		$image_size = 'woocommerce_single';
		$delivery = $image_id && function_exists( 'skyyrose2_pdp_media_delivery' ) ? skyyrose2_pdp_media_delivery( $product, $image_id ) : array();
		if ( $delivery ) {
			return array( array( 'href' => $delivery['src'], 'as' => 'image', 'type' => 'image/webp', 'fetchpriority' => 'high', 'imagesrcset' => $delivery['srcset'], 'imagesizes' => $delivery['sizes'] ) );
		}
	} elseif ( is_single() ) {
		$image_id = (int) get_post_thumbnail_id( get_queried_object_id() );
	}

	if ( $image_id ) {
		$source = wp_get_attachment_image_src( $image_id, $image_size );
		if ( $source && ! empty( $source[0] ) ) {
			$resource = array(
				'href'          => $source[0],
				'as'            => 'image',
				'fetchpriority' => 'high',
			);
			$type = skyyrose2_performance_image_mime( $source[0] );
			if ( $type ) {
				$resource['type'] = $type;
			}
			$srcset = wp_get_attachment_image_srcset( $image_id, $image_size );
			if ( $srcset ) {
				$resource['imagesrcset'] = $srcset;
				$resource['imagesizes']  = sprintf( '(max-width: %dpx) 100vw, %dpx', (int) $source[1], (int) $source[1] );
			}
			return array( $resource );
		}
	}

	return array();
}

/**
 * Discover the first native archive card's approved garment front without advancing
 * or replacing its query. The archive renders garment-first (no portal frame), so the
 * hint carries the same approved front, srcset and sizes the first card will request.
 *
 * Category displays and extension-owned loop/visibility behavior are deliberately
 * excluded. Product hydration may read metadata; no product-selection query or
 * Woo loop setup is performed. The first visible product owns the hint or none.
 *
 * @return array<string,string>
 */
function skyyrose2_performance_archive_front_preload() {
	global $wp_query, $wp_the_query;
	if (
		! function_exists( 'is_shop' ) || ! ( is_shop() || is_product_taxonomy() ) ||
		is_admin() || wp_doing_ajax() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) || is_feed() || is_embed() ||
		! ( $wp_query instanceof WP_Query ) || $wp_query !== $wp_the_query || ! $wp_query->is_main_query() ||
		'product_query' !== $wp_query->get( 'wc_query' ) || -1 !== $wp_query->current_post ||
		$wp_query->post_count < 1 || ! is_array( $wp_query->posts ) ||
		has_filter( 'woocommerce_product_is_visible' ) || has_action( 'woocommerce_shop_loop' )
	) {
		return array();
	}
	$loop = $GLOBALS['woocommerce_loop'] ?? array();
	if ( ! is_array( $loop ) || ! empty( $loop['name'] ) || ! empty( $loop['is_shortcode'] ) || ! empty( $loop['loop'] ) || ( isset( $loop['total'] ) && (int) $loop['total'] < 1 ) ) {
		return array();
	}
	$display = '';
	if ( is_shop() ) {
		$display = get_option( 'woocommerce_shop_page_display', '' );
	} elseif ( is_product_category() ) {
		$display = get_term_meta( get_queried_object_id(), 'display_type', true );
		$display = $display ? $display : get_option( 'woocommerce_category_archive_display', '' );
	}
	if ( in_array( $display, array( 'both', 'subcategories' ), true ) ) {
		return array();
	}
	foreach ( $wp_query->posts as $candidate_post ) {
		if ( ! ( $candidate_post instanceof WP_Post ) || 'product' !== $candidate_post->post_type ) {
			return array();
		}
		$candidate = wc_get_product( $candidate_post->ID );
		if ( ! ( $candidate instanceof WC_Product ) || ! $candidate->is_visible() ) {
			continue;
		}
		$front = function_exists( 'skyyrose2_approved_card_front' ) ? skyyrose2_approved_card_front( $candidate ) : array();
		$href  = (string) ( $front['card_src'] ?? $front['src'] ?? '' );
		if ( '' === $href ) {
			return array();
		}
		$resource = array(
			'href'          => $href,
			'as'            => 'image',
			'fetchpriority' => 'high',
		);
		$type = skyyrose2_performance_image_mime( $href );
		if ( $type ) {
			$resource['type'] = $type;
		}
		// The card only emits sizes alongside a srcset; the hint mirrors that exactly so
		// the preloaded candidate is the one the img element selects.
		if ( ! empty( $front['srcset'] ) && function_exists( 'skyyrose2_shop_card_sizes' ) ) {
			$resource['imagesrcset'] = $front['srcset'];
			$resource['imagesizes']  = skyyrose2_shop_card_sizes();
		}
		return $resource;
	}
	return array();
}

/**
 * Add route hero preloads without duplicating an existing href.
 *
 * @param array<int,mixed> $resources Existing preload records.
 * @return array<int,mixed>
 */
function skyyrose2_performance_preload_resources( $resources ) {
	$existing = array();
	foreach ( $resources as $resource ) {
		if ( is_array( $resource ) && ! empty( $resource['href'] ) ) {
			$existing[ $resource['href'] ] = true;
		}
	}

	foreach ( skyyrose2_performance_route_preloads() as $resource ) {
		if ( empty( $resource['href'] ) || isset( $existing[ $resource['href'] ] ) ) {
			continue;
		}
		$resources[]                    = $resource;
		$existing[ $resource['href'] ] = true;
	}

	return $resources;
}
add_filter( 'wp_preload_resources', 'skyyrose2_performance_preload_resources' );

/**
 * Defer only theme-owned progressive-enhancement scripts.
 *
 * Footer placement, dependency order, reduced-motion handling, Save-Data
 * behavior, and DOM-first/no-JavaScript fallbacks remain unchanged.
 */
function skyyrose2_performance_defer_scripts() {
	$handles = array(
		'skyyrose2-theme',
		'skyyrose2-house-of-roses',
		'skyyrose2-kids-capsule-reveal',
		'skyyrose2-mascot-loader',
		'skyyrose2-immersive',
	);

	foreach ( $handles as $handle ) {
		wp_script_add_data( $handle, 'strategy', 'defer' );
	}
}
add_action( 'wp_enqueue_scripts', 'skyyrose2_performance_defer_scripts', 110 );
add_action( 'wp_footer', 'skyyrose2_performance_defer_scripts', 1 );

/**
 * Precompile the two native variation templates without relaxing storefront CSP.
 *
 * Woo's complex-template detection can delegate even a simple field token to
 * wp.template/Underscore, which otherwise compiles with new Function. Populate
 * WordPress's existing memoization cache after wp-util and before its consumer.
 * Only the existing Woo HTML fields are interpolated; commerce resolution stays
 * entirely in WooCommerce. Unknown executable template syntax fails closed.
 */
function skyyrose2_performance_csp_variation_templates() {
	if ( ! function_exists( 'is_product' ) || ( ! is_product() && ! wp_script_is( 'wc-add-to-cart-variation', 'enqueued' ) ) ) {
		return;
	}
	$script = <<<'SKYYROSE_VARIATION_TEMPLATES'
(() => {
  const cache = window.wp?.template?.cache;
  if (!cache) return;
  const allowed = new Set(['variation_description', 'price_html', 'availability_html']);
  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
  for (const id of ['variation-template', 'unavailable-variation-template']) {
    cache[id] = (data) => {
      const element = document.getElementById(`tmpl-${id}`);
      if (!element) throw new Error(`Missing native Woo template: ${id}`);
      const source = element.textContent;
      const token = /({{{?)\s*data\.variation\.([a-z_]+)\s*(}}}?)/g;
      const remaining = source.replace(token, (match, open, key, close) => open.length === close.length && allowed.has(key) ? '' : match);
      if (/<#|{{|}}/.test(remaining)) throw new Error('Unsupported Woo variation template expression under CSP');
      return source.replace(token, (_match, open, key) => {
        const value = data?.variation?.[key] ?? '';
        return open.length === 2 ? escapeHtml(value) : String(value);
      });
    };
  }
})();
SKYYROSE_VARIATION_TEMPLATES;
	wp_add_inline_script( 'wp-util', $script, 'after' );
}
add_action( 'wp_enqueue_scripts', 'skyyrose2_performance_csp_variation_templates', 120 );

/**
 * Keep the editorial home stylesheet render-blocking when Jetpack Boost has
 * critical CSS enabled. The split on-model hero relies on its complete layout
 * before first paint; Other routes retain their existing Boost stylesheet behavior.
 *
 * @param string|false $method Requested Boost loading method.
 * @param string       $handle  Registered style handle.
 * @param string       $media   Stylesheet media attribute.
 * @return string|false
 */
function skyyrose2_homepage_blocking_boost_styles( $method, $handle, $media ) {
	if ( ! is_front_page() || 'all' !== $media ) {
		return $method;
	}

	return false;
}
add_filter( 'jetpack_boost_async_style', 'skyyrose2_homepage_blocking_boost_styles', PHP_INT_MAX, 3 );
