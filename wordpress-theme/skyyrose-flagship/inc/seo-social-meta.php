<?php
/**
 * SEO Social Metadata
 *
 * Open Graph, Twitter, canonical, description, and title metadata.
 *
 * @package SkyyRose
 * @since   7.2.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Resolve collection SEO context for landing page templates.
 *
 * The four collection page templates have their own explicit branches. This
 * maps the landing (conversion) templates to
 * their collection so OG / title / description / Twitter / schema output stays
 * consistent instead of falling through to the generic article handling.
 *
 * @since 1.6.4
 *
 * @return array|null array{slug:string,label:string,type:string} or null when
 *                    the current request is not a landing template.
 */
function skyyrose_collection_template_context() {
	$templates = array(
		'template-landing-black-rose.php'   => array( 'black-rose', 'Black Rose', 'landing' ),
		'template-landing-love-hurts.php'   => array( 'love-hurts', 'Love Hurts', 'landing' ),
		'template-landing-signature.php'    => array( 'signature', 'Signature', 'landing' ),
		'template-landing-kids-capsule.php' => array( 'kids-capsule', 'Kids Capsule', 'landing' ),
	);

	foreach ( $templates as $tpl_file => $data ) {
		if ( is_page_template( $tpl_file ) ) {
			return array(
				'slug'  => $data[0],
				'label' => $data[1],
				'type'  => $data[2],
			);
		}
	}

	return null;
}

/**
 * Add Open Graph tags.
 *
 * Skips output when Yoast SEO is active to prevent duplicate meta tags.
 *
 * @since 1.0.0
 */
function skyyrose_open_graph_tags() {
	// Defer to Yoast SEO if active.
	if ( defined( 'WPSEO_VERSION' ) ) {
		return;
	}

	$site_name = get_bloginfo( 'name' );

	// Locale — always output.
	echo '<meta property="og:locale" content="' . esc_attr( get_locale() ) . '" />' . "\n";
	echo '<meta property="og:site_name" content="' . esc_attr( $site_name ) . '" />' . "\n";

	// Fallback OG image (brand monogram).
	$fallback_og_image = get_template_directory_uri() . '/assets/branding/sr-primary-hero.webp';

	// Custom collection page templates — must precede the generic is_singular() branch.
	$collection_templates = array(
		'template-collection-black-rose.php'   => array( 'Black Rose Collection', 'black-rose' ),
		'template-collection-love-hurts.php'   => array( 'Love Hurts Collection', 'love-hurts' ),
		'template-collection-signature.php'    => array( 'Signature Collection', 'signature' ),
		'template-collection-kids-capsule.php' => array( 'Kids Capsule Collection', 'kids-capsule' ),
	);

	$active_collection_template = false;
	foreach ( $collection_templates as $tpl_file => $tpl_data ) {
		if ( is_page_template( $tpl_file ) ) {
			$active_collection_template = $tpl_data;
			break;
		}
	}

	$collection_ctx = skyyrose_collection_template_context();

	if ( $active_collection_template ) {
		$col_label = $active_collection_template[0];
		echo '<meta property="og:type" content="website" />' . "\n";
		echo '<meta property="og:title" content="' . esc_attr( 'Shop ' . $col_label . ' | ' . $site_name ) . '" />' . "\n";
		echo '<meta property="og:description" content="' . esc_attr( 'Browse the ' . $col_label . ' from SkyyRose. ' ) . '" />' . "\n";
		echo '<meta property="og:url" content="' . esc_url( get_permalink() ) . '" />' . "\n";
		if ( has_post_thumbnail() ) {
			echo '<meta property="og:image" content="' . esc_url( get_the_post_thumbnail_url( get_the_ID(), 'full' ) ) . '" />' . "\n";
			echo '<meta property="og:image:width" content="1200" />' . "\n";
			echo '<meta property="og:image:height" content="630" />' . "\n";
		} else {
			echo '<meta property="og:image" content="' . esc_url( $fallback_og_image ) . '" />' . "\n";
		}
	} elseif ( null !== $collection_ctx ) {
		if ( 'landing' === $collection_ctx['type'] ) {
			$ctx_title = 'Shop ' . $collection_ctx['label'] . ' | ' . $site_name;
			$ctx_desc  = 'Shop the ' . $collection_ctx['label'] . ' collection from SkyyRose. ';
		} else {
			$ctx_title = $collection_ctx['label'] . ' — Immersive Experience | ' . $site_name;
			$ctx_desc  = 'Step inside the ' . $collection_ctx['label'] . ' world — an immersive SkyyRose experience. ';
		}
		echo '<meta property="og:type" content="website" />' . "\n";
		echo '<meta property="og:title" content="' . esc_attr( $ctx_title ) . '" />' . "\n";
		echo '<meta property="og:description" content="' . esc_attr( $ctx_desc ) . '" />' . "\n";
		echo '<meta property="og:url" content="' . esc_url( get_permalink() ) . '" />' . "\n";
		if ( has_post_thumbnail() ) {
			echo '<meta property="og:image" content="' . esc_url( get_the_post_thumbnail_url( get_the_ID(), 'full' ) ) . '" />' . "\n";
			echo '<meta property="og:image:width" content="1200" />' . "\n";
			echo '<meta property="og:image:height" content="630" />' . "\n";
		} else {
			echo '<meta property="og:image" content="' . esc_url( $fallback_og_image ) . '" />' . "\n";
		}
	} elseif ( is_singular() && ! is_front_page() ) {
		global $post;

		echo '<meta property="og:type" content="' . esc_attr( is_singular( 'product' ) ? 'product' : 'article' ) . '" />' . "\n";
		echo '<meta property="og:title" content="' . esc_attr( get_the_title() . ' | ' . $site_name ) . '" />' . "\n";
		echo '<meta property="og:description" content="' . esc_attr( wp_strip_all_tags( get_the_excerpt() ) ) . '" />' . "\n";
		echo '<meta property="og:url" content="' . esc_url( get_permalink() ) . '" />' . "\n";

		if ( has_post_thumbnail() ) {
			$image_url = get_the_post_thumbnail_url( $post->ID, 'full' );
			echo '<meta property="og:image" content="' . esc_url( $image_url ) . '" />' . "\n";
			echo '<meta property="og:image:width" content="1200" />' . "\n";
			echo '<meta property="og:image:height" content="630" />' . "\n";
		} else {
			echo '<meta property="og:image" content="' . esc_url( $fallback_og_image ) . '" />' . "\n";
		}

		// Product-specific OG tags.
		if ( is_singular( 'product' ) ) {
			$product = skyyrose_current_wc_product( $post->ID );
			if ( $product && function_exists( 'get_woocommerce_currency' ) ) {
				echo '<meta property="product:price:amount" content="' . esc_attr( $product->get_price() ) . '" />' . "\n";
				echo '<meta property="product:price:currency" content="' . esc_attr( get_woocommerce_currency() ) . '" />' . "\n";
				echo '<meta property="product:availability" content="' . esc_attr( $product->is_in_stock() ? 'in stock' : 'out of stock' ) . '" />' . "\n";
			}
		}
	} elseif ( is_front_page() ) {
		echo '<meta property="og:type" content="website" />' . "\n";
		echo '<meta property="og:title" content="' . esc_attr( $site_name . ' — ' ) . '" />' . "\n";
		echo '<meta property="og:description" content="' . esc_attr( get_bloginfo( 'description' ) ) . '" />' . "\n";
		echo '<meta property="og:url" content="' . esc_url( home_url( '/' ) ) . '" />' . "\n";

		$logo_url = skyyrose_og_logo_url();
		echo '<meta property="og:image" content="' . esc_url( $logo_url ? $logo_url : $fallback_og_image ) . '" />' . "\n";
	} elseif ( is_tax( 'product_cat' ) ) {
		$term = get_queried_object();
		echo '<meta property="og:type" content="website" />' . "\n";
		echo '<meta property="og:title" content="' . esc_attr( $term->name . ' Collection | ' . $site_name ) . '" />' . "\n";
		$desc = term_description( $term->term_id );
		echo '<meta property="og:description" content="' . esc_attr( wp_strip_all_tags( $desc ?: 'Shop the ' . $term->name . ' collection from SkyyRose.' ) ) . '" />' . "\n";
		$term_link = get_term_link( $term );
		if ( ! is_wp_error( $term_link ) ) {
			echo '<meta property="og:url" content="' . esc_url( $term_link ) . '" />' . "\n";
		}
		echo '<meta property="og:image" content="' . esc_url( $fallback_og_image ) . '" />' . "\n";
	} elseif ( function_exists( 'is_shop' ) && is_shop() ) {
		echo '<meta property="og:type" content="website" />' . "\n";
		echo '<meta property="og:title" content="' . esc_attr( 'Shop | ' . $site_name ) . '" />' . "\n";
		echo '<meta property="og:description" content="' . esc_attr( 'Premium streetwear and luxury fashion. ' ) . '" />' . "\n";
		echo '<meta property="og:url" content="' . esc_url( get_permalink( wc_get_page_id( 'shop' ) ) ) . '" />' . "\n";
		echo '<meta property="og:image" content="' . esc_url( $fallback_og_image ) . '" />' . "\n";
	} elseif ( is_category() || is_tag() ) {
		$term = get_queried_object();
		echo '<meta property="og:type" content="website" />' . "\n";
		echo '<meta property="og:title" content="' . esc_attr( $term->name . ' | ' . $site_name ) . '" />' . "\n";
		$desc = term_description( $term->term_id );
		echo '<meta property="og:description" content="' . esc_attr( wp_strip_all_tags( $desc ?: $site_name ) ) . '" />' . "\n";
		$term_link = get_term_link( $term );
		if ( ! is_wp_error( $term_link ) ) {
			echo '<meta property="og:url" content="' . esc_url( $term_link ) . '" />' . "\n";
		}
		echo '<meta property="og:image" content="' . esc_url( $fallback_og_image ) . '" />' . "\n";
	}
}
add_action( 'wp_head', 'skyyrose_open_graph_tags', 1 );

/**
 * Add Twitter Card tags.
 *
 * Skips output when Yoast SEO is active to prevent duplicate meta tags.
 *
 * @since 1.0.0
 */
function skyyrose_twitter_card_tags() {
	// Defer to Yoast SEO if active.
	if ( defined( 'WPSEO_VERSION' ) ) {
		return;
	}

	echo '<meta name="twitter:card" content="summary_large_image" />' . "\n";

	// Use theme_mod handle when configured; fall back to the canonical brand account.
	$twitter_handle = get_theme_mod( 'twitter_handle', 'skyyroseco' );
	echo '<meta name="twitter:site" content="@' . esc_attr( ltrim( $twitter_handle, '@' ) ) . '" />' . "\n";

	$fallback_image = get_template_directory_uri() . '/assets/branding/sr-primary-hero.webp';

	// Custom collection page templates — must precede the generic is_singular() branch.
	$twitter_collection_templates = array(
		'template-collection-black-rose.php'   => array( 'Black Rose Collection', 'black-rose' ),
		'template-collection-love-hurts.php'   => array( 'Love Hurts Collection', 'love-hurts' ),
		'template-collection-signature.php'    => array( 'Signature Collection', 'signature' ),
		'template-collection-kids-capsule.php' => array( 'Kids Capsule Collection', 'kids-capsule' ),
	);

	$active_twitter_collection = false;
	foreach ( $twitter_collection_templates as $tpl_file => $tpl_data ) {
		if ( is_page_template( $tpl_file ) ) {
			$active_twitter_collection = $tpl_data;
			break;
		}
	}

	$twitter_ctx = skyyrose_collection_template_context();

	if ( $active_twitter_collection ) {
		$tc_label = $active_twitter_collection[0];
		echo '<meta name="twitter:title" content="' . esc_attr( 'Shop ' . $tc_label . ' | SkyyRose' ) . '" />' . "\n";
		echo '<meta name="twitter:description" content="' . esc_attr( 'Browse the ' . $tc_label . ' from SkyyRose. ' ) . '" />' . "\n";
		if ( has_post_thumbnail() ) {
			echo '<meta name="twitter:image" content="' . esc_url( get_the_post_thumbnail_url( get_the_ID(), 'full' ) ) . '" />' . "\n";
		} else {
			echo '<meta name="twitter:image" content="' . esc_url( $fallback_image ) . '" />' . "\n";
		}
	} elseif ( null !== $twitter_ctx ) {
		if ( 'landing' === $twitter_ctx['type'] ) {
			$tw_title = 'Shop ' . $twitter_ctx['label'] . ' | SkyyRose';
			$tw_desc  = 'Shop the ' . $twitter_ctx['label'] . ' collection from SkyyRose. ';
		} else {
			$tw_title = $twitter_ctx['label'] . ' — Immersive Experience | SkyyRose';
			$tw_desc  = 'Step inside the ' . $twitter_ctx['label'] . ' world — an immersive SkyyRose experience.';
		}
		echo '<meta name="twitter:title" content="' . esc_attr( $tw_title ) . '" />' . "\n";
		echo '<meta name="twitter:description" content="' . esc_attr( $tw_desc ) . '" />' . "\n";
		if ( has_post_thumbnail() ) {
			echo '<meta name="twitter:image" content="' . esc_url( get_the_post_thumbnail_url( get_the_ID(), 'full' ) ) . '" />' . "\n";
		} else {
			echo '<meta name="twitter:image" content="' . esc_url( $fallback_image ) . '" />' . "\n";
		}
	} elseif ( is_singular() && ! is_front_page() ) {
		echo '<meta name="twitter:title" content="' . esc_attr( get_the_title() ) . '" />' . "\n";
		echo '<meta name="twitter:description" content="' . esc_attr( wp_strip_all_tags( get_the_excerpt() ) ) . '" />' . "\n";

		if ( has_post_thumbnail() ) {
			echo '<meta name="twitter:image" content="' . esc_url( get_the_post_thumbnail_url( get_the_ID(), 'full' ) ) . '" />' . "\n";
		} else {
			echo '<meta name="twitter:image" content="' . esc_url( $fallback_image ) . '" />' . "\n";
		}
	} elseif ( is_front_page() ) {
		echo '<meta name="twitter:title" content="' . esc_attr( get_bloginfo( 'name' ) . ' — ' ) . '" />' . "\n";
		echo '<meta name="twitter:description" content="' . esc_attr( get_bloginfo( 'description' ) ) . '" />' . "\n";

		$logo_url = skyyrose_og_logo_url();
		echo '<meta name="twitter:image" content="' . esc_url( $logo_url ? $logo_url : $fallback_image ) . '" />' . "\n";
	} elseif ( is_tax( 'product_cat' ) ) {
		$term = get_queried_object();
		echo '<meta name="twitter:title" content="' . esc_attr( $term->name . ' Collection | SkyyRose' ) . '" />' . "\n";
		echo '<meta name="twitter:description" content="' . esc_attr( wp_strip_all_tags( term_description( $term->term_id ) ?: 'Shop the ' . $term->name . ' collection.' ) ) . '" />' . "\n";
		echo '<meta name="twitter:image" content="' . esc_url( $fallback_image ) . '" />' . "\n";
	} elseif ( function_exists( 'is_shop' ) && is_shop() ) {
		echo '<meta name="twitter:title" content="Shop | SkyyRose" />' . "\n";
		echo '<meta name="twitter:description" content="Premium streetwear and luxury fashion. " />' . "\n";
		echo '<meta name="twitter:image" content="' . esc_url( $fallback_image ) . '" />' . "\n";
	}
}
add_action( 'wp_head', 'skyyrose_twitter_card_tags', 1 );

/**
 * Add canonical URL.
 *
 * Skips output when Yoast SEO is active to prevent duplicate canonical tags.
 *
 * @since 1.0.0
 */
function skyyrose_canonical_url() {
	// Defer to Yoast SEO if active.
	if ( defined( 'WPSEO_VERSION' ) ) {
		return;
	}

	if ( is_singular() ) {
		echo '<link rel="canonical" href="' . esc_url( get_permalink() ) . '" />' . "\n";
	} elseif ( is_front_page() ) {
		echo '<link rel="canonical" href="' . esc_url( home_url( '/' ) ) . '" />' . "\n";
	} elseif ( function_exists( 'is_shop' ) && ( is_post_type_archive( 'product' ) || is_shop() ) ) {
		if ( function_exists( 'wc_get_page_id' ) ) {
			echo '<link rel="canonical" href="' . esc_url( get_permalink( wc_get_page_id( 'shop' ) ) ) . '" />' . "\n";
		}
	} elseif ( is_tax() || is_category() || is_tag() ) {
		$queried = get_queried_object();
		if ( $queried instanceof WP_Term ) {
			$term_link = get_term_link( $queried );
			if ( ! is_wp_error( $term_link ) ) {
				echo '<link rel="canonical" href="' . esc_url( $term_link ) . '" />' . "\n";
			}
		}
	}
}
add_action( 'wp_head', 'skyyrose_canonical_url', 1 );

/**
 * Add meta descriptions.
 *
 * Skips output when Yoast SEO is active to prevent duplicate meta descriptions.
 *
 * @since 1.0.0
 */
function skyyrose_meta_description() {
	// Defer to Yoast SEO if active.
	if ( defined( 'WPSEO_VERSION' ) ) {
		return;
	}

	$description = '';

	if ( is_singular() && ! is_front_page() ) {
		// Custom template meta descriptions (155 chars max, CTA-driven).
		if ( is_page() ) {
			$template     = get_page_template_slug();
			$descriptions = array(
				'template-collection-black-rose.php' => 'Browse the full Black Rose Collection. Limited edition gothic streetwear — hockey jerseys, basketball jerseys, and more.',
				'template-collection-love-hurts.php' => 'Browse the full Love Hurts Collection. Crimson luxury fashion — fanny packs, apparel, and accessories from SkyyRose.',
				'template-collection-signature.php'  => 'Browse the full Signature Collection. Everyday luxury — windbreakers, shorts, beanies, and essentials from SkyyRose.',
				'template-about.php'                 => 'The SkyyRose story —  Founded in Oakland, building premium streetwear for the culture.',
				'template-preorder-gateway.php'      => 'Secure your SkyyRose pieces before they drop. Pre-order limited edition streetwear and luxury fashion.',
				'template-contact.php'               => 'Reach SkyyRose directly. Oakland-made, founder-led. Questions about orders, sizing, collaborations, or press — we read every message.',
				'template-faq.php'                   => 'Frequently asked questions about SkyyRose orders, shipping, returns, sizing, and pre-orders. Everything you need to know.',
				'template-shipping-returns.php'      => 'SkyyRose shipping rates, delivery times, 30-day return policy, free exchanges, and pre-order cancellation details.',
			);
			if ( $template && isset( $descriptions[ $template ] ) ) {
				$description = $descriptions[ $template ];
			}

			if ( empty( $description ) ) {
				$collection_ctx = skyyrose_collection_template_context();
				if ( null !== $collection_ctx ) {
					$description = ( 'landing' === $collection_ctx['type'] )
						? 'Shop the ' . $collection_ctx['label'] . ' collection from SkyyRose. Premium streetwear and luxury fashion — '
						: 'Step inside the ' . $collection_ctx['label'] . ' world. An immersive SkyyRose experience — ';
				}
			}
		}

		if ( empty( $description ) ) {
			$description = get_the_excerpt();
		}
		if ( empty( $description ) ) {
			$description = wp_trim_words( get_the_content(), 30, '...' );
		}
	} elseif ( is_front_page() ) {
		$description = get_bloginfo( 'description' );
	} elseif ( is_category() ) {
		$description = category_description();
	} elseif ( is_tag() ) {
		$description = tag_description();
	} elseif ( is_tax( 'product_cat' ) ) {
		$description = term_description();
	} elseif ( function_exists( 'is_shop' ) && is_shop() ) {
		$description = 'Shop premium streetwear and luxury fashion from SkyyRose.  Oakland, CA.';
	}

	if ( ! empty( $description ) ) {
		$description = wp_strip_all_tags( $description );
		$description = str_replace( array( "\r", "\n", "\t" ), ' ', $description );
		$description = trim( preg_replace( '/\s+/', ' ', $description ) );

		echo '<meta name="description" content="' . esc_attr( wp_trim_words( $description, 30 ) ) . '" />' . "\n";
	}
}
add_action( 'wp_head', 'skyyrose_meta_description', 1 );

/**
 * Override document title for specific pages.
 *
 * Uses `pre_get_document_title` at high priority to override before
 * Jetpack/WordPress.com SEO modules can interfere. Returning a
 * non-empty string from this filter makes WordPress use it as-is.
 *
 * @since 1.0.0
 * @since 3.2.3 Switched from wp_title to pre_get_document_title.
 *
 * @param string $title Pre-filtered document title (empty by default).
 * @return string Full document title or empty to use default.
 */
function skyyrose_pre_document_title( $title ) {
	$brand = get_bloginfo( 'name' );

	// Collections "Shop All" page.
	if ( is_page( array( 'collections', 9327 ) ) ) {
		return 'Collections — Shop All | ' . $brand;
	}

	// Custom template page titles (optimized for SEO).
	if ( is_page() ) {
		$template = get_page_template_slug();
		$titles   = array(
			'template-collection-black-rose.php' => 'Shop Black Rose — Limited Edition Streetwear | ' . $brand,
			'template-collection-love-hurts.php' => 'Shop Love Hurts — Crimson Luxury Fashion | ' . $brand,
			'template-collection-signature.php'  => 'Shop Signature — Everyday Luxury Essentials | ' . $brand,
			'template-about.php'                 => 'Our Story —  | ' . $brand,
			'template-preorder-gateway.php'      => 'Pre-Order — Secure Your Pieces | ' . $brand,
			'template-contact.php'               => 'Reach Out | ' . $brand,
			'page-wishlist.php'                  => 'Your Wishlist | ' . $brand,
			'template-faq.php'                   => 'FAQ — Orders, Shipping, Returns & Sizing | ' . $brand,
			'template-shipping-returns.php'      => 'Shipping & Returns Policy | ' . $brand,
		);

		if ( $template && isset( $titles[ $template ] ) ) {
			return $titles[ $template ];
		}

		$collection_ctx = skyyrose_collection_template_context();
		if ( null !== $collection_ctx ) {
			if ( 'landing' === $collection_ctx['type'] ) {
				return 'Shop ' . $collection_ctx['label'] . ' — Luxury Streetwear | ' . $brand;
			}
			return $collection_ctx['label'] . ' — Immersive Experience | ' . $brand;
		}

		// Policy pages use the default page template — no template slug to key
		// on above, and the WP.com SEO layer strips the brand suffix, leaving a
		// bare <title> (go-live sweep P1, regressed in the seo.php rewrite).
		if ( is_page( array( 'privacy-policy', 'terms-of-service', 'cookie-policy', 'refund-policy' ) ) ) {
			return get_the_title() . ' | ' . $brand;
		}
	}

	return $title;
}
add_filter( 'pre_get_document_title', 'skyyrose_pre_document_title', 99 );
