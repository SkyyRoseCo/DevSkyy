<?php
/**
 * SEO Structured Data
 *
 * Product, organization, website, and breadcrumb schema output.
 *
 * @package SkyyRose
 * @since   7.2.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Custom-logo URL for og:image / twitter:image — image MIME types only.
 *
 * The live custom_logo attachment has at times been a VideoPress .mp4, which
 * silently produced og:image="…logo_400x100.mp4" and broke link previews
 * everywhere (structural remediation WS4, F13). Social cards require a
 * static image, so any non-image attachment yields '' and callers fall back
 * to the static brand asset.
 *
 * @since 1.8.0
 * @return string Attachment URL, or '' when unset or not an image.
 */
function skyyrose_og_logo_url() {
	$logo_id = get_theme_mod( 'custom_logo' );
	if ( ! $logo_id ) {
		return '';
	}
	// Raster formats only — social crawlers (Facebook, X, LinkedIn) do not
	// render SVG in og:image/twitter:image, so allowing it through recreates
	// the same broken-preview class this function exists to prevent.
	$raster_mimes = array( 'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/avif' );
	$mime         = (string) get_post_mime_type( $logo_id );
	if ( ! in_array( $mime, $raster_mimes, true ) ) {
		return '';
	}
	return (string) wp_get_attachment_url( $logo_id );
}

/**
 * Add Schema.org markup for products.
 *
 * Skips output when Yoast SEO (with WooCommerce SEO add-on) is active
 * to prevent duplicate product structured data.
 *
 * @since 1.0.0
 */
function skyyrose_product_schema() {
	if ( ! is_singular( 'product' ) || ! function_exists( 'get_woocommerce_currency' ) ) {
		return;
	}

	// Defer to Yoast WooCommerce SEO if active.
	if ( defined( 'WPSEO_WOO_VERSION' ) ) {
		return;
	}

	$product = skyyrose_current_wc_product();

	if ( ! $product ) {
		return;
	}

	$product_price = $product instanceof WC_Product_Variable ? $product->get_variation_price( 'min' ) : $product->get_price();

	$schema = array(
		'@context'    => 'https://schema.org/',
		'@type'       => 'Product',
		'name'        => $product->get_name(),
		'description' => wp_strip_all_tags( $product->get_short_description() ?: $product->get_description() ),
		'sku'         => $product->get_sku(),
		'image'       => wp_get_attachment_url( absint( $product->get_image_id() ) ),
		'offers'      => array(
			'@type'         => 'Offer',
			'url'           => get_permalink( $product->get_id() ),
			'priceCurrency' => get_woocommerce_currency(),
			'price'         => $product_price,
			'availability'  => $product->is_in_stock() ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
		),
	);

	// Add brand if available (sanitize for safe JSON-LD output).
	$brand = sanitize_text_field( get_post_meta( $product->get_id(), '_product_brand', true ) );
	if ( $brand ) {
		$schema['brand'] = array(
			'@type' => 'Brand',
			'name'  => $brand,
		);
	}

	// Add aggregate rating if available.
	if ( $product->get_average_rating() ) {
		$schema['aggregateRating'] = array(
			'@type'       => 'AggregateRating',
			'ratingValue' => $product->get_average_rating(),
			'reviewCount' => $product->get_review_count(),
		);
	}

	// Add reviews.
	$reviews = get_comments(
		array(
			'post_id' => $product->get_id(),
			'status'  => 'approve',
			'type'    => 'review',
			'number'  => 5,
		)
	);

	if ( ! empty( $reviews ) ) {
		$schema['review'] = array();
		foreach ( $reviews as $review ) {
			$rating = get_comment_meta( absint( $review->comment_ID ), 'rating', true );
			if ( $rating ) {
				$schema['review'][] = array(
					'@type'         => 'Review',
					'author'        => array(
						'@type' => 'Person',
						'name'  => wp_strip_all_tags( $review->comment_author ),
					),
					'reviewRating'  => array(
						'@type'       => 'Rating',
						'ratingValue' => $rating,
					),
					'reviewBody'    => wp_strip_all_tags( $review->comment_content ),
					'datePublished' => mysql2date( 'c', $review->comment_date ),
				);
			}
		}
	}

	echo '<script type="application/ld+json">' . wp_json_encode( $schema, JSON_HEX_TAG | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- JSON-encoded with JSON_HEX_TAG preventing script injection.
}
add_action( 'wp_head', 'skyyrose_product_schema', 1 );

/**
 * Add Organization schema markup for SkyyRose LLC.
 *
 * Outputs JSON-LD Organization structured data on the front page.
 * Skips output when Yoast SEO is active and handles Organization schema.
 *
 * @since 1.0.0
 */
function skyyrose_organization_schema() {
	if ( ! is_front_page() ) {
		return;
	}

	// Defer to Yoast SEO for Organization schema if active.
	if ( defined( 'WPSEO_VERSION' ) ) {
		return;
	}

	$logo_url = skyyrose_og_logo_url();

	$schema = array(
		'@context'    => 'https://schema.org',
		'@type'       => 'Organization',
		'name'        => 'SkyyRose',
		'legalName'   => 'SkyyRose LLC',
		'url'         => home_url( '/' ),
		'founder'     => array(
			'@type' => 'Person',
			'name'  => 'Corey Foster',
		),
		'description' => __( 'Premium streetwear and luxury fashion brand.', 'skyyrose' ),
		'logo'        => $logo_url ? array(
			'@type' => 'ImageObject',
			'url'   => $logo_url,
		) : null,
		'brand'       => array(
			'@type' => 'Brand',
			'name'  => 'SkyyRose',
		),
		'sameAs'      => array(),
	);

	// Canonical brand social profiles — always present in sameAs.
	$default_profiles = array(
		'https://instagram.com/skyyrose.co',
		'https://tiktok.com/@skyyroseco',
	);

	foreach ( $default_profiles as $profile_url ) {
		$schema['sameAs'][] = $profile_url;
	}

	// Add additional social media profiles from Customizer settings (deduplicated).
	$social_profiles = array(
		'facebook'  => get_theme_mod( 'facebook_url' ),
		'twitter'   => get_theme_mod( 'twitter_url' ),
		'instagram' => get_theme_mod( 'instagram_url' ),
		'linkedin'  => get_theme_mod( 'linkedin_url' ),
		'youtube'   => get_theme_mod( 'youtube_url' ),
	);

	foreach ( $social_profiles as $profile ) {
		if ( ! empty( $profile ) && ! in_array( esc_url_raw( $profile ), $schema['sameAs'], true ) ) {
			$schema['sameAs'][] = esc_url( $profile );
		}
	}

	// Add contact information.
	$phone = get_theme_mod( 'contact_phone' );
	$email = get_theme_mod( 'contact_email' );

	if ( $phone || $email ) {
		$schema['contactPoint'] = array(
			'@type'       => 'ContactPoint',
			'contactType' => 'customer service',
		);

		if ( $phone ) {
			$schema['contactPoint']['telephone'] = sanitize_text_field( $phone );
		}
		if ( $email ) {
			$schema['contactPoint']['email'] = sanitize_email( $email );
		}
	}

	// Remove null fields (e.g., logo when no custom logo is set).
	$schema = array_filter(
		$schema,
		function ( $v ) {
			return null !== $v;
		}
	);

	echo '<script type="application/ld+json">' . wp_json_encode( $schema, JSON_HEX_TAG | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- JSON-encoded with JSON_HEX_TAG preventing script injection.
}
add_action( 'wp_head', 'skyyrose_organization_schema', 1 );

/**
 * Add WebSite schema with SearchAction (sitelinks search box).
 *
 * Enables the search box that appears in Google sitelinks for branded queries.
 * Only outputs on the front page. Defers to Yoast SEO when active.
 *
 * @since 6.4.0
 */
function skyyrose_website_schema() {
	if ( ! is_front_page() ) {
		return;
	}

	// Defer to Yoast SEO if active.
	if ( defined( 'WPSEO_VERSION' ) ) {
		return;
	}

	$schema = array(
		'@context'        => 'https://schema.org',
		'@type'           => 'WebSite',
		'name'            => get_bloginfo( 'name' ),
		'url'             => home_url( '/' ),
		'potentialAction' => array(
			'@type'       => 'SearchAction',
			'target'      => array(
				'@type'       => 'EntryPoint',
				'urlTemplate' => home_url( '/?s={search_term_string}' ),
			),
			'query-input' => 'required name=search_term_string',
		),
	);

	echo '<script type="application/ld+json">' . wp_json_encode( $schema, JSON_HEX_TAG | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
}
add_action( 'wp_head', 'skyyrose_website_schema', 1 );

/**
 * Add BreadcrumbList schema markup.
 *
 * Skips output when Yoast SEO is active to prevent duplicate breadcrumb schema.
 *
 * @since 1.0.0
 */
function skyyrose_breadcrumb_schema() {
	if ( is_front_page() ) {
		return;
	}

	// Defer to Yoast SEO for breadcrumb schema if active.
	if ( defined( 'WPSEO_VERSION' ) ) {
		return;
	}

	$breadcrumbs = skyyrose_get_breadcrumb_trail();

	if ( empty( $breadcrumbs ) ) {
		return;
	}

	$schema = array(
		'@context'        => 'https://schema.org',
		'@type'           => 'BreadcrumbList',
		'itemListElement' => array(),
	);

	$position = 1;
	foreach ( $breadcrumbs as $breadcrumb ) {
		$schema['itemListElement'][] = array(
			'@type'    => 'ListItem',
			'position' => $position,
			'name'     => $breadcrumb['title'],
			'item'     => $breadcrumb['url'],
		);
		++$position;
	}

	echo '<script type="application/ld+json">' . wp_json_encode( $schema, JSON_HEX_TAG | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- JSON-encoded with JSON_HEX_TAG preventing script injection.
}
add_action( 'wp_head', 'skyyrose_breadcrumb_schema', 1 );

/**
 * Get breadcrumb trail.
 *
 * @since 1.0.0
 *
 * @return array Breadcrumb items.
 */
function skyyrose_get_breadcrumb_trail() {
	$breadcrumbs = array(
		array(
			'title' => __( 'Home', 'skyyrose' ),
			'url'   => home_url( '/' ),
		),
	);

	// Custom collection page templates: Home → Collections → [Collection Name].
	$breadcrumb_collection_templates = array(
		'template-collection-black-rose.php'   => __( 'Black Rose', 'skyyrose' ),
		'template-collection-love-hurts.php'   => __( 'Love Hurts', 'skyyrose' ),
		'template-collection-signature.php'    => __( 'Signature', 'skyyrose' ),
		'template-collection-kids-capsule.php' => __( 'Kids Capsule', 'skyyrose' ),
	);

	$matched_breadcrumb_collection = false;
	foreach ( $breadcrumb_collection_templates as $tpl_file => $col_name ) {
		if ( is_page_template( $tpl_file ) ) {
			$matched_breadcrumb_collection = $col_name;
			break;
		}
	}

	if ( $matched_breadcrumb_collection ) {
		$collections_page = get_page_by_path( 'collections' );
		if ( $collections_page ) {
			$breadcrumbs[] = array(
				'title' => __( 'Collections', 'skyyrose' ),
				'url'   => get_permalink( $collections_page->ID ),
			);
		} else {
			$breadcrumbs[] = array(
				'title' => __( 'Collections', 'skyyrose' ),
				'url'   => home_url( '/collections/' ),
			);
		}

		$breadcrumbs[] = array(
			'title' => $matched_breadcrumb_collection,
			'url'   => get_permalink(),
		);
	} elseif ( is_singular( 'product' ) && function_exists( 'wc_get_page_id' ) ) {
		$breadcrumbs[] = array(
			'title' => __( 'Shop', 'skyyrose' ),
			'url'   => get_permalink( wc_get_page_id( 'shop' ) ),
		);

		$terms = get_the_terms( get_the_ID(), 'product_cat' );
		if ( $terms && ! is_wp_error( $terms ) ) {
			$term          = array_shift( $terms );
			$breadcrumbs[] = array(
				'title' => wp_strip_all_tags( html_entity_decode( $term->name, ENT_QUOTES, 'UTF-8' ) ),
				'url'   => get_term_link( $term ),
			);
		}

		$breadcrumbs[] = array(
			'title' => wp_strip_all_tags( html_entity_decode( get_the_title(), ENT_QUOTES, 'UTF-8' ) ),
			'url'   => get_permalink(),
		);
	} elseif ( function_exists( 'wc_get_page_id' ) && ( is_post_type_archive( 'product' ) || is_shop() ) ) {
		$breadcrumbs[] = array(
			'title' => __( 'Shop', 'skyyrose' ),
			'url'   => get_permalink( wc_get_page_id( 'shop' ) ),
		);
	} elseif ( function_exists( 'wc_get_page_id' ) && is_tax( 'product_cat' ) ) {
		$breadcrumbs[] = array(
			'title' => __( 'Shop', 'skyyrose' ),
			'url'   => get_permalink( wc_get_page_id( 'shop' ) ),
		);

		$term = get_queried_object();
		if ( $term instanceof WP_Term ) {
			$breadcrumbs[] = array(
				'title' => wp_strip_all_tags( html_entity_decode( $term->name, ENT_QUOTES, 'UTF-8' ) ),
				'url'   => get_term_link( $term ),
			);
		}
	} elseif ( is_singular( 'post' ) ) {
		$categories = get_the_category();
		if ( $categories ) {
			$category      = array_shift( $categories );
			$breadcrumbs[] = array(
				'title' => wp_strip_all_tags( html_entity_decode( $category->name, ENT_QUOTES, 'UTF-8' ) ),
				'url'   => get_category_link( $category->term_id ),
			);
		}

		$breadcrumbs[] = array(
			'title' => get_the_title(),
			'url'   => get_permalink(),
		);
	} elseif ( is_page() ) {
		$breadcrumbs[] = array(
			'title' => get_the_title(),
			'url'   => get_permalink(),
		);
	} elseif ( is_category() ) {
		$breadcrumbs[] = array(
			'title' => single_cat_title( '', false ),
			'url'   => get_category_link( get_queried_object_id() ),
		);
	} elseif ( is_search() ) {
		$breadcrumbs[] = array(
			'title' => sprintf( __( 'Search Results for: %s', 'skyyrose' ), esc_html( get_search_query() ) ),
			'url'   => '',
		);
	}

	return $breadcrumbs;
}

/**
 * Display breadcrumb navigation.
 *
 * @since 1.0.0
 */
function skyyrose_breadcrumb() {
	if ( is_front_page() ) {
		return;
	}

	$breadcrumbs = skyyrose_get_breadcrumb_trail();

	if ( empty( $breadcrumbs ) ) {
		return;
	}

	echo '<nav class="breadcrumb-navigation" aria-label="' . esc_attr__( 'Breadcrumb', 'skyyrose' ) . '">';
	echo '<ol class="breadcrumbs" itemscope itemtype="https://schema.org/BreadcrumbList">';

	$position   = 1;
	$last_index = count( $breadcrumbs ) - 1;

	foreach ( $breadcrumbs as $index => $breadcrumb ) {
		$is_last = ( $index === $last_index );

		echo '<li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">';

		if ( $is_last ) {
			echo '<span itemprop="name" aria-current="page">' . esc_html( $breadcrumb['title'] ) . '</span>';
		} else {
			echo '<a href="' . esc_url( $breadcrumb['url'] ) . '" itemprop="item">';
			echo '<span itemprop="name">' . esc_html( $breadcrumb['title'] ) . '</span>';
			echo '</a>';
		}

		echo '<meta itemprop="position" content="' . esc_attr( (string) $position ) . '" />';
		echo '</li>';

		++$position;
	}

	echo '</ol>';
	echo '</nav>';
}
add_action( 'skyyrose_after_header', 'skyyrose_breadcrumb', 10 );
