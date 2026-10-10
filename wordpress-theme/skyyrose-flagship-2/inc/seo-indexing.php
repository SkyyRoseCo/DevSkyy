<?php
/**
 * Search discovery and indexing adapter.
 *
 * The adapter deliberately leaves Product/Offer facts to WooCommerce and
 * yields all metadata/schema output to a supported SEO plugin. Preview,
 * transactional, and non-production robots controls remain fail closed.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/**
 * Detect a plugin that owns the document's SEO graph and social metadata.
 *
 * @return bool
 */
function skyyrose2_seo_has_authority_plugin() {
	return defined( 'WPSEO_VERSION' )
		|| defined( 'RANK_MATH_VERSION' )
		|| defined( 'AIOSEO_VERSION' )
		|| defined( 'SEOPRESS_VERSION' )
		|| defined( 'THE_SEO_FRAMEWORK_VERSION' )
		|| defined( 'SLIM_SEO_VERSION' )
		|| class_exists( 'WPSEO_Options' )
		|| class_exists( 'RankMath' )
		|| class_exists( 'AIOSEO\\Plugin\\AIOSEO' );
}

/**
 * Identify local, development, staging, and preview requests.
 *
 * @return bool
 */
function skyyrose2_seo_is_nonproduction_request() {
	$environment = function_exists( 'wp_get_environment_type' ) ? wp_get_environment_type() : 'production';
	if ( in_array( $environment, array( 'local', 'development', 'staging' ), true ) ) {
		return true;
	}

	$home_host    = (string) wp_parse_url( home_url( '/' ), PHP_URL_HOST );
	$request_host = isset( $_SERVER['HTTP_HOST'] ) ? sanitize_text_field( wp_unslash( $_SERVER['HTTP_HOST'] ) ) : ''; // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotValidated
	$request_host = strtolower( preg_replace( '/:\d+$/', '', $request_host ) );
	$hosts        = array_filter( array( strtolower( $home_host ), $request_host ) );

	foreach ( $hosts as $host ) {
		if (
			'localhost' === $host
			|| '::1' === $host
			|| '127.0.0.1' === $host
			|| str_ends_with( $host, '.localhost' )
			|| str_ends_with( $host, '.local' )
			|| str_ends_with( $host, '.test' )
			|| str_ends_with( $host, '.internal' )
		) {
			return true;
		}
	}

	return function_exists( 'is_preview' ) && is_preview();
}

/**
 * Whether the current request is a private/low-value commerce surface.
 *
 * @return bool
 */
function skyyrose2_seo_is_transactional_request() {
	return ( function_exists( 'is_cart' ) && is_cart() )
		|| ( function_exists( 'is_checkout' ) && is_checkout() )
		|| ( function_exists( 'is_account_page' ) && is_account_page() )
		|| ( function_exists( 'is_page_template' ) && is_page_template( 'page-wishlist.php' ) );
}

/**
 * Apply indexability rules without overriding unrelated plugin directives.
 *
 * @param array<string,bool|string> $robots Robots directives.
 * @return array<string,bool|string>
 */
function skyyrose2_seo_robots( $robots ) {
	if ( skyyrose2_seo_is_nonproduction_request() || skyyrose2_seo_is_transactional_request() ) {
		unset( $robots['index'], $robots['follow'] );
		$robots['noindex']  = true;
		$robots['nofollow'] = true;
		return $robots;
	}

	if ( is_search() ) {
		unset( $robots['index'], $robots['nofollow'] );
		$robots['noindex'] = true;
		$robots['follow']  = true;
		return $robots;
	}

	if ( is_404() ) {
		unset( $robots['index'] );
		$robots['noindex'] = true;
		return $robots;
	}

	if ( ! isset( $robots['noindex'] ) ) {
		$robots['max-image-preview'] = 'large';
	}

	return $robots;
}

/**
 * Add an HTTP noindex safeguard to preview/non-production responses.
 *
 * @param array<string,string> $headers Response headers.
 * @return array<string,string>
 */
function skyyrose2_seo_headers( $headers ) {
	if ( skyyrose2_seo_is_nonproduction_request() ) {
		$headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive';
	}
	return $headers;
}

/**
 * Normalize authored text for metadata without manufacturing claims.
 *
 * @param string $text   Source text.
 * @param int    $length Maximum character length.
 * @return string
 */
function skyyrose2_seo_excerpt( $text, $length = 158 ) {
	$text = trim( preg_replace( '/\s+/u', ' ', wp_strip_all_tags( strip_shortcodes( (string) $text ) ) ) );
	if ( function_exists( 'mb_strlen' ) && function_exists( 'mb_substr' ) ) {
		return mb_strlen( $text ) > $length ? rtrim( mb_substr( $text, 0, $length - 1 ) ) . '…' : $text;
	}
	return strlen( $text ) > $length ? rtrim( substr( $text, 0, $length - 3 ) ) . '...' : $text;
}

/**
 * Resolve the canonical URL from WordPress routing, never request query data.
 *
 * @return string
 */
function skyyrose2_seo_canonical_url() {
	if ( is_search() || is_404() || skyyrose2_seo_is_nonproduction_request() || skyyrose2_seo_is_transactional_request() ) {
		return '';
	}
	$paged = max( 1, (int) get_query_var( 'paged' ) );
	if ( $paged > 1 && ! is_singular() ) {
		return (string) get_pagenum_link( $paged );
	}
	if ( is_front_page() ) {
		return home_url( '/' );
	}
	if ( is_singular() ) {
		$canonical = function_exists( 'wp_get_canonical_url' ) ? wp_get_canonical_url( get_queried_object_id() ) : '';
		return $canonical ? (string) $canonical : (string) get_permalink( get_queried_object_id() );
	}
	if ( function_exists( 'is_shop' ) && is_shop() && function_exists( 'wc_get_page_id' ) ) {
		return (string) get_permalink( wc_get_page_id( 'shop' ) );
	}
	if ( is_home() ) {
		$page_id = (int) get_option( 'page_for_posts' );
		return $page_id ? (string) get_permalink( $page_id ) : home_url( '/' );
	}
	if ( is_category() || is_tag() || is_tax() ) {
		$url = get_term_link( get_queried_object() );
		return is_wp_error( $url ) ? '' : (string) $url;
	}
	if ( is_post_type_archive() ) {
		$url = get_post_type_archive_link( get_query_var( 'post_type' ) );
		return $url ? (string) $url : '';
	}
	if ( is_archive() ) {
		return (string) get_pagenum_link( $paged );
	}
	return '';
}

/**
 * Resolve route metadata from actual WordPress, theme SOT, or Woo objects.
 *
 * @return array{title:string,description:string,image:string,type:string,url:string}
 */
function skyyrose2_seo_resolved_context() {
	$site_name = (string) get_bloginfo( 'name' );
	$tagline   = (string) get_bloginfo( 'description' );
	$context   = array(
		'title'       => $site_name,
		'description' => skyyrose2_seo_excerpt( $tagline ),
		'image'       => function_exists( 'skyyrose2_sot_asset_uri' ) ? skyyrose2_sot_asset_uri( 'branding/hero/flagship-house-runway-gpt2.webp' ) : '',
		'type'        => 'website',
		'url'         => skyyrose2_seo_canonical_url(),
	);

	if ( is_front_page() ) {
		$context['title']       = $site_name;
		$context['description'] = skyyrose2_seo_excerpt( __( 'Enter SkyyRose: Oakland-rooted luxury streetwear, living collection worlds, limited pieces, and the stories behind the house.', 'skyyrose-flagship-2' ) );
	} elseif ( is_singular( 'product' ) && function_exists( 'wc_get_product' ) ) {
		$product = wc_get_product( get_queried_object_id() );
		if ( $product ) {
			$product_copy           = $product->get_short_description() ? $product->get_short_description() : $product->get_description();
			$product_description    = skyyrose2_seo_excerpt( $product_copy );
			$context['title']       = $product->get_name() . ' | ' . $site_name;
			$context['description'] = $product_description ? $product_description : $context['description'];
			$media                 = function_exists( 'skyyrose2_product_commerce_media' ) ? skyyrose2_product_commerce_media( $product ) : array();
			$context['image']       = ! empty( $media['ids'] ) ? (string) wp_get_attachment_image_url( $media['ids'][0], 'full' ) : '';
			$context['type']        = 'product';
		}
	} elseif ( is_single() ) {
		$article_copy           = get_the_excerpt() ? get_the_excerpt() : get_post_field( 'post_content', get_queried_object_id() );
		$context['title']       = get_the_title() . ' | ' . $site_name;
		$context['description'] = skyyrose2_seo_excerpt( $article_copy );
		$context['image']       = (string) ( get_the_post_thumbnail_url( get_queried_object_id(), 'full' ) ? get_the_post_thumbnail_url( get_queried_object_id(), 'full' ) : $context['image'] );
		$context['type']        = 'article';
	} elseif ( is_page() ) {
		$slug  = sanitize_title( get_post_field( 'post_name', get_queried_object_id() ) );
		$world = function_exists( 'skyyrose2_collections' ) ? ( skyyrose2_collections()[ $slug ] ?? null ) : null;
		if ( $world ) {
			$context['title']       = $world['name'] . ' | ' . $site_name;
			$context['description'] = skyyrose2_seo_excerpt( $world['line'] . ' ' . $world['manifesto'] );
			$context['image']       = skyyrose2_sot_asset_uri( $world['hero'] );
		} else {
			$page_copy              = get_the_excerpt() ? get_the_excerpt() : get_post_field( 'post_content', get_queried_object_id() );
			$page_description       = skyyrose2_seo_excerpt( $page_copy );
			$context['title']       = get_the_title() . ' | ' . $site_name;
			$context['description'] = $page_description ? $page_description : $context['description'];
			$context['image']       = (string) ( get_the_post_thumbnail_url( get_queried_object_id(), 'full' ) ? get_the_post_thumbnail_url( get_queried_object_id(), 'full' ) : $context['image'] );
		}
	} elseif ( is_archive() ) {
		$archive_description    = skyyrose2_seo_excerpt( get_the_archive_description() );
		$context['title']       = wp_strip_all_tags( get_the_archive_title() ) . ' | ' . $site_name;
		$context['description'] = $archive_description ? $archive_description : $context['description'];
	}

	return apply_filters( 'skyyrose2_seo_context', $context );
}

/**
 * Keep the core document title aligned with social metadata.
 *
 * @param array<string,string> $parts Document title parts.
 * @return array<string,string>
 */
function skyyrose2_seo_document_title( $parts ) {
	if ( skyyrose2_seo_has_authority_plugin() ) {
		return $parts;
	}
	$context        = skyyrose2_seo_resolved_context();
	$parts['title'] = $context['title'];
	unset( $parts['site'], $parts['tagline'] );
	return $parts;
}

/**
 * Emit canonical, description, Open Graph, and Twitter metadata.
 */
function skyyrose2_seo_render_meta() {
	if ( skyyrose2_seo_has_authority_plugin() || skyyrose2_seo_is_nonproduction_request() ) {
		return;
	}
	$context = skyyrose2_seo_resolved_context();
	?>
	<?php
	if ( $context['url'] ) :
		?>
		<link rel="canonical" href="<?php echo esc_url( $context['url'] ); ?>"><?php endif; ?>
	<?php
	if ( $context['description'] ) :
		?>
		<meta name="description" content="<?php echo esc_attr( $context['description'] ); ?>"><?php endif; ?>
	<meta property="og:locale" content="<?php echo esc_attr( get_locale() ); ?>">
	<meta property="og:site_name" content="<?php echo esc_attr( get_bloginfo( 'name' ) ); ?>">
	<meta property="og:type" content="<?php echo esc_attr( $context['type'] ); ?>">
	<meta property="og:title" content="<?php echo esc_attr( $context['title'] ); ?>">
	<?php
	if ( $context['description'] ) :
		?>
		<meta property="og:description" content="<?php echo esc_attr( $context['description'] ); ?>"><?php endif; ?>
	<?php
	if ( $context['url'] ) :
		?>
		<meta property="og:url" content="<?php echo esc_url( $context['url'] ); ?>"><?php endif; ?>
	<?php
	if ( $context['image'] ) :
		?>
		<meta property="og:image" content="<?php echo esc_url( $context['image'] ); ?>"><?php endif; ?>
	<meta name="twitter:card" content="<?php echo empty( $context['image'] ) ? 'summary' : 'summary_large_image'; ?>">
	<meta name="twitter:title" content="<?php echo esc_attr( $context['title'] ); ?>">
	<?php
	if ( $context['description'] ) :
		?>
		<meta name="twitter:description" content="<?php echo esc_attr( $context['description'] ); ?>"><?php endif; ?>
	<?php
	if ( $context['image'] ) :
		?>
		<meta name="twitter:image" content="<?php echo esc_url( $context['image'] ); ?>"><?php endif; ?>
	<?php
}

/**
 * Get a valid custom logo URL without making assumptions about brand media.
 *
 * @return string
 */
function skyyrose2_seo_logo_url() {
	$logo_id = (int) get_theme_mod( 'custom_logo' );
	return $logo_id ? (string) wp_get_attachment_image_url( $logo_id, 'full' ) : '';
}

/**
 * Construct breadcrumbs for the current public route.
 *
 * @return array<int,array{name:string,url:string}>
 */
function skyyrose2_seo_breadcrumbs() {
	if ( is_front_page() ) {
		return array();
	}
	$items = array(
		array(
			'name' => get_bloginfo( 'name' ),
			'url'  => home_url( '/' ),
		),
	);
	if ( is_singular() ) {
		$post_id = get_queried_object_id();
		foreach ( array_reverse( get_post_ancestors( $post_id ) ) as $ancestor_id ) {
			$items[] = array(
				'name' => get_the_title( $ancestor_id ),
				'url'  => get_permalink( $ancestor_id ),
			);
		}
		$items[] = array(
			'name' => get_the_title( $post_id ),
			'url'  => get_permalink( $post_id ),
		);
	} elseif ( is_category() || is_tag() || is_tax() ) {
		$term = get_queried_object();
		$url  = get_term_link( $term );
		if ( ! is_wp_error( $url ) ) {
			$items[] = array(
				'name' => $term->name,
				'url'  => $url,
			);
		}
	} elseif ( is_archive() ) {
		$items[] = array(
			'name' => wp_strip_all_tags( get_the_archive_title() ),
			'url'  => skyyrose2_seo_canonical_url(),
		);
	}
	return array_values( array_filter( $items, fn( $item ) => $item['name'] && $item['url'] ) );
}

/**
 * Extract the maintained, visible FAQ for honest FAQ schema.
 *
 * @return array<int,array{question:string,answer:string}>
 */
function skyyrose2_seo_faq_entries() {
	if ( ! is_page() || 'faq' !== sanitize_title( get_post_field( 'post_name', get_queried_object_id() ) ) ) {
		return array();
	}
	$content = (string) get_post_field( 'post_content', get_queried_object_id() );

	$entries = array();
	if ( preg_match_all( '#<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>#is', $content, $matches, PREG_SET_ORDER ) ) {
		foreach ( $matches as $match ) {
			$question = skyyrose2_seo_excerpt( $match[1], 240 );
			$answer   = skyyrose2_seo_excerpt( $match[2], 1000 );
			if ( $question && $answer ) {
				$entries[] = array(
					'question' => $question,
					'answer'   => $answer,
				);
			}
		}
	} elseif ( preg_match_all( '#<h2[^>]*>(.*?)</h2>\s*(?:<!--[^>]*-->\s*)*<p[^>]*>(.*?)</p>#is', $content, $matches, PREG_SET_ORDER ) ) {
		foreach ( $matches as $match ) {
			$question = skyyrose2_seo_excerpt( $match[1], 240 );
			$answer   = skyyrose2_seo_excerpt( $match[2], 1000 );
			if ( $question && $answer ) {
				$entries[] = array(
					'question' => $question,
					'answer'   => $answer,
				);
			}
		}
	}
	return apply_filters( 'skyyrose2_seo_faq_entries', $entries, $content );
}

/**
 * Build theme-owned editorial schema. Product/Offer is never emitted here.
 *
 * @return array<int,array<string,mixed>>
 */
function skyyrose2_seo_schema_graph() {
	if (
		skyyrose2_seo_has_authority_plugin()
		|| skyyrose2_seo_is_nonproduction_request()
		|| skyyrose2_seo_is_transactional_request()
		|| is_search()
		|| is_404()
	) {
		return array();
	}
	$site_name       = (string) get_bloginfo( 'name' );
	$home_url        = home_url( '/' );
	$organization_id = trailingslashit( $home_url ) . '#organization';
	$website_id      = trailingslashit( $home_url ) . '#website';
	$graph           = array();

	$organization = array(
		'@type' => 'Organization',
		'@id'   => $organization_id,
		'name'  => $site_name,
		'url'   => $home_url,
	);
	$logo         = skyyrose2_seo_logo_url();
	if ( $logo ) {
		$organization['logo'] = array(
			'@type' => 'ImageObject',
			'url'   => $logo,
		);
	}
	$graph[] = $organization;
	$graph[] = array(
		'@type'     => 'WebSite',
		'@id'       => $website_id,
		'name'      => $site_name,
		'url'       => $home_url,
		'publisher' => array( '@id' => $organization_id ),
	);

	$breadcrumbs = skyyrose2_seo_breadcrumbs();
	if ( count( $breadcrumbs ) > 1 ) {
		$elements = array();
		foreach ( $breadcrumbs as $index => $item ) {
			$elements[] = array(
				'@type'    => 'ListItem',
				'position' => $index + 1,
				'name'     => $item['name'],
				'item'     => $item['url'],
			);
		}
		$graph[] = array(
			'@type'           => 'BreadcrumbList',
			'@id'             => skyyrose2_seo_canonical_url() . '#breadcrumb',
			'itemListElement' => $elements,
		);
	}

	if ( is_single() && ! is_singular( 'product' ) ) {
		$article = array(
			'@type'            => 'Article',
			'@id'              => get_permalink() . '#article',
			'headline'         => get_the_title(),
			'datePublished'    => get_the_date( DATE_W3C ),
			'dateModified'     => get_the_modified_date( DATE_W3C ),
			'mainEntityOfPage' => get_permalink(),
			'author'           => array(
				'@type' => 'Person',
				'name'  => get_the_author(),
			),
			'publisher'        => array( '@id' => $organization_id ),
		);
		$image   = get_the_post_thumbnail_url( get_queried_object_id(), 'full' );
		if ( $image ) {
			$article['image'] = $image;
		}
		$graph[] = $article;
	}

	if ( is_page() && function_exists( 'skyyrose2_collections' ) ) {
		$slug  = sanitize_title( get_post_field( 'post_name', get_queried_object_id() ) );
		$world = skyyrose2_collections()[ $slug ] ?? null;
		if ( $world ) {
			$graph[] = array(
				'@type'              => 'CollectionPage',
				'@id'                => get_permalink() . '#collection',
				'name'               => $world['name'],
				'description'        => skyyrose2_seo_excerpt( $world['line'] . ' ' . $world['manifesto'] ),
				'url'                => get_permalink(),
				'isPartOf'           => array( '@id' => $website_id ),
				'primaryImageOfPage' => array(
					'@type' => 'ImageObject',
					'url'   => skyyrose2_sot_asset_uri( $world['hero'] ),
				),
			);
		}
	}

	$faq_entries = skyyrose2_seo_faq_entries();
	if ( $faq_entries ) {
		$graph[] = array(
			'@type'      => 'FAQPage',
			'@id'        => get_permalink() . '#faq',
			'mainEntity' => array_map(
				fn( $entry ) => array(
					'@type'          => 'Question',
					'name'           => $entry['question'],
					'acceptedAnswer' => array(
						'@type' => 'Answer',
						'text'  => $entry['answer'],
					),
				),
				$faq_entries
			),
		);
	}

	return apply_filters( 'skyyrose2_seo_schema_graph', $graph );
}

/**
 * Emit one parseable JSON-LD graph for theme-owned entities.
 */
function skyyrose2_seo_render_schema() {
	$graph = skyyrose2_seo_schema_graph();
	if ( ! $graph ) {
		return;
	}
	$data = array(
		'@context' => 'https://schema.org',
		'@graph'   => $graph,
	);
	echo '<script type="application/ld+json">' . wp_json_encode( $data, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ) . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- wp_json_encode plus JSON_HEX flags make the script payload inert.
}

/**
 * Advertise the native WordPress sitemap in public robots.txt.
 *
 * @param string $output Robots text.
 * @param bool   $is_public Whether search engines are allowed.
 * @return string
 */
function skyyrose2_seo_robots_txt( $output, $is_public ) {
	if ( ! $is_public || skyyrose2_seo_has_authority_plugin() || skyyrose2_seo_is_nonproduction_request() || false !== stripos( $output, 'Sitemap:' ) ) {
		return $output;
	}
	return rtrim( $output ) . "\n\nSitemap: " . esc_url_raw( home_url( '/wp-sitemap.xml' ) ) . "\n";
}

/**
 * Keep noindex commerce utilities out of the native WordPress page sitemap.
 *
 * @param array<string,mixed> $args      Sitemap query arguments.
 * @param string              $post_type Sitemap post type.
 * @return array<string,mixed>
 */
function skyyrose2_seo_sitemap_query_args( $args, $post_type ) {
	if ( 'page' !== $post_type || skyyrose2_seo_has_authority_plugin() ) {
		return $args;
	}

	$excluded = array();
	if ( function_exists( 'wc_get_page_id' ) ) {
		foreach ( array( 'cart', 'checkout', 'myaccount' ) as $page_key ) {
			$page_id = (int) wc_get_page_id( $page_key );
			if ( $page_id > 0 ) {
				$excluded[] = $page_id;
			}
		}
	}
	$wishlist = get_page_by_path( 'wishlist' );
	if ( $wishlist instanceof WP_Post ) {
		$excluded[] = (int) $wishlist->ID;
	}
	if ( $excluded ) {
		$args['post__not_in'] = array_values( array_unique( array_merge( $args['post__not_in'] ?? array(), $excluded ) ) );
	}
	return $args;
}

/**
 * Replace the legacy V2 hooks and register this adapter.
 */
function skyyrose2_seo_indexing_bootstrap() {
	remove_action( 'wp_head', 'skyyrose2_seo_head', 4 );
	remove_action( 'wp_head', 'skyyrose2_schema_head', 5 );
	if ( ! skyyrose2_seo_has_authority_plugin() ) {
		remove_action( 'wp_head', 'rel_canonical' );
	}
	add_filter( 'document_title_parts', 'skyyrose2_seo_document_title', 20 );
	add_filter( 'wp_robots', 'skyyrose2_seo_robots', 20 );
	add_filter( 'wp_headers', 'skyyrose2_seo_headers', 20 );
	add_filter( 'robots_txt', 'skyyrose2_seo_robots_txt', 20, 2 );
	add_filter( 'wp_sitemaps_posts_query_args', 'skyyrose2_seo_sitemap_query_args', 20, 2 );
	add_action( 'wp_head', 'skyyrose2_seo_render_meta', 4 );
	add_action( 'wp_head', 'skyyrose2_seo_render_schema', 5 );
}
add_action( 'after_setup_theme', 'skyyrose2_seo_indexing_bootstrap', 99 );
