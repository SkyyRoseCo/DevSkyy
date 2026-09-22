<?php
/** Narrow storefront integration repairs. No stored options or product mutations. */
defined( 'ABSPATH' ) || exit;

/** Keep maintained service navigation independent of a legacy collection menu. */
function skyyrose2_register_service_menu() {
	register_nav_menu( 'primary-v2', __( 'V2 House Directory', 'skyyrose-flagship-2' ) );
	register_nav_menu( 'footer-services', __( 'V2 Client Services', 'skyyrose-flagship-2' ) );
}
add_action( 'after_setup_theme', 'skyyrose2_register_service_menu', 20 );

/** Repair only the observed FAQ-as-privacy assignment; preserve custom policies. */
function skyyrose2_storefront_privacy_url( $url, $page_id ) {
	if ( 'faq' !== get_post_field( 'post_name', (int) $page_id ) ) {
		return $url;
	}
	$policy = get_page_by_path( 'privacy-policy', OBJECT, 'page' );
	if ( ! $policy || 'publish' !== $policy->post_status || ! empty( $policy->post_password ) ) {
		return $url;
	}
	return get_permalink( $policy->ID ) ?: $url;
}
add_filter( 'privacy_policy_url', 'skyyrose2_storefront_privacy_url', 20, 2 );

/** Hide the stock sample post from listings, without deleting or editing it. */
function skyyrose2_exclude_default_journal_sample( $query ) {
	if ( is_admin() || ! $query->is_main_query() || ! ( $query->is_home() || $query->is_search() ) ) {
		return;
	}
	$types = $query->get( 'post_type' );
	if ( $types && ! in_array( $types, array( 'post', 'any', array( 'post' ) ), true ) ) {
		return;
	}
	$sample = get_page_by_path( 'hello-world', OBJECT, 'post' );
	if ( ! $sample || 'Hello world!' !== $sample->post_title ) {
		return;
	}
	$excluded = array_map( 'absint', (array) $query->get( 'post__not_in' ) );
	$excluded[] = (int) $sample->ID;
	$query->set( 'post__not_in', array_values( array_unique( $excluded ) ) );
}
add_action( 'pre_get_posts', 'skyyrose2_exclude_default_journal_sample', 20 );

/** One template heading; preserve page content, anchors, and legal wording. */
function skyyrose2_normalize_page_content_headings( $content ) {
	if ( is_admin() || ! is_page( array( 'accessibility', 'landing-black-rose', 'landing-love-hurts', 'privacy-policy', 'refund-policy', 'shipping-returns', 'landing-signature', 'terms-of-service' ) ) || ! in_the_loop() || ! is_main_query() ) {
		return $content;
	}
	return preg_replace( '/<(\/?)h1(?=[\s>])/i', '<$1h2', $content );
}
add_filter( 'the_content', 'skyyrose2_normalize_page_content_headings', 30 );

/** Keep Jetpack sharing controls while preventing their utility label from skipping heading levels. */
function skyyrose2_jetpack_sharing_headline_html( $headline_html, $label, $context ) {
	if ( 'sharing' !== $context ) {
		return $headline_html;
	}
	return '<p class="sd-title">' . esc_html( $label ) . '</p>';
}
add_filter( 'jetpack_sharing_headline_html', 'skyyrose2_jetpack_sharing_headline_html', 10, 3 );

/** Preserve legacy URLs while keeping verified demo prose out of discovery. */
function skyyrose2_exclude_demo_editorials( $query ) {
	if ( is_admin() || ! $query->is_main_query() || ! ( $query->is_home() || $query->is_search() ) ) {
		return;
	}
	$excluded = array_map( 'absint', (array) $query->get( 'post__not_in' ) );
	foreach ( array( '10-designer-buys-that-are-worth-the-investment', 'our-pick-of-the-coolest-denim-jackets-this-season', 'jay-ellis-proves-one-suit-can-work-four-different-ways' ) as $slug ) {
		$post = get_page_by_path( $slug, OBJECT, 'post' );
		if ( $post && false !== strpos( $post->post_content, 'Synth kickstarter coloring book' ) ) {
			$excluded[] = (int) $post->ID;
		}
	}
	$query->set( 'post__not_in', array_values( array_unique( $excluded ) ) );
}
add_action( 'pre_get_posts', 'skyyrose2_exclude_demo_editorials', 21 );

/** Founder-approved card reuse, separately labeled; never authorizes native media. */
function skyyrose2_render_approved_pdp_styling_view( $product ) {
	if ( ! $product instanceof WC_Product || ! function_exists( 'skyyrose2_approved_card_front' ) ) {
		return false;
	}
	$approved = array(
		'br-001' => array( 'src' => 'assets/approved-card-fronts/br-001-onmodel.webp', 'sha256' => 'fcaddcf8a93e22283137b2a165cfb7ab216d0dab45853e5da7b4a23818071aa8' ),
		'br-003' => array( 'src' => 'assets/card-scenes/br-003-onmodel.webp', 'sha256' => '43e75a7280e7b3bda87bacde28971274bf7633400b06b13b77a873c005647ea9' ),
		'br-004' => array( 'src' => 'assets/approved-card-fronts/br-004-onmodel.webp', 'sha256' => '8c415f0fe1e5ab113e74f7a7040563b5396f2672f400cf9d30f99db839de32c8' ),
		'br-007' => array( 'src' => 'assets/approved-card-fronts/br-007-onmodel.webp', 'sha256' => 'b2e523f08f8bae826e45c0a01584dee54c735c7dda2fc81edcf65c420ac9030d' ),
		'br-011' => array( 'src' => 'assets/card-scenes/br-011-onmodel.webp', 'sha256' => 'aedc47d8fa76fce040dc195330469800de43b346d4d0ccba872abf7016f5f290' ),
	);
	$sku = strtolower( $product->get_sku() );
	if ( ! isset( $approved[ $sku ] ) ) {
		return false;
	}
	$entry = $approved[ $sku ];
	$root = realpath( SKYYROSE2_DIR . '/assets' );
	$file = realpath( SKYYROSE2_DIR . '/' . $entry['src'] );
	if ( ! $root || ! $file || 0 !== strpos( $file, $root . DIRECTORY_SEPARATOR ) || ! is_file( $file ) || ! is_readable( $file ) || ! hash_equals( $entry['sha256'], hash_file( 'sha256', $file ) ) ) {
		return false;
	}
	$front = skyyrose2_approved_card_front( $product );
	if ( ! $front || $front['src'] !== SKYYROSE2_URI . '/' . $entry['src'] ) {
		return false;
	}
	$src = $front['card_src'] ?? $front['src'];
	$width = (int) ( $front['card_width'] ?? $front['width'] );
	$height = (int) ( $front['card_height'] ?? $front['height'] );
	$sizes = function_exists( 'skyyrose2_pdp_gallery_sizes' ) ? skyyrose2_pdp_gallery_sizes( $front['width'], $front['height'] ) : '';
	return skyyrose2_render_approved_pdp_styling_front( $sku, $front, $src, $width, $height, $sizes );
}

/** Render an approved original when no integrity-valid derivative is available. */
function skyyrose2_render_approved_pdp_styling_front( $sku, $front, $src = '', $width = 0, $height = 0, $sizes = '' ) {
	if ( ! is_array( $front ) || 'FOUNDER_APPROVED_V2_CARD' !== ( $front['scene_status'] ?? '' ) || empty( $front['src'] ) || empty( $front['alt'] ) ) {
		return false;
	}
	$src = $src ?: $front['src'];
	$width = (int) ( $width ?: $front['width'] );
	$height = (int) ( $height ?: $front['height'] );
	echo '<figure class="sr2-pdp-styling-view" data-sr2-approved-styling="' . esc_attr( $sku ) . '">';
	echo '<img src="' . esc_url( $src ) . '" width="' . $width . '" height="' . $height . '"';
	if ( ! empty( $front['srcset'] ) && $sizes ) {
		echo ' srcset="' . esc_attr( $front['srcset'] ) . '" sizes="' . esc_attr( $sizes ) . '"';
	}
	echo ' alt="' . esc_attr( $front['alt'] ) . '" decoding="async" fetchpriority="high">';
	echo '<figcaption>' . esc_html__( 'On-model styling view', 'skyyrose-flagship-2' ) . '</figcaption></figure>';
	return true;
}

/** Only the three audited broken collection aliases are retired. */
function skyyrose2_legacy_collection_routes() {
	return array(
		'collection-black-rose' => 'collections/black-rose',
		'collection-love-hurts' => 'collections/love-hurts',
		'collection-signature' => 'collections/signature',
	);
}

/** Demo retirement follows verified content fingerprints, not titles alone. */
function skyyrose2_is_retired_demo_post( $post ) {
	if ( ! is_object( $post ) || 'post' !== $post->post_type ) {
		return false;
	}
	if ( 'hello-world' === $post->post_name ) {
		return 'Hello world!' === $post->post_title && false !== strpos( $post->post_content, 'luxury-design-system.css' );
	}
	return in_array( $post->post_name, array( '10-designer-buys-that-are-worth-the-investment', 'our-pick-of-the-coolest-denim-jackets-this-season', 'jay-ellis-proves-one-suit-can-work-four-different-ways' ), true ) && false !== strpos( $post->post_content, 'Synth kickstarter coloring book' );
}

/** Resolve a replacement only when its published, unprotected page exists. */
function skyyrose2_retired_content_target( $post ) {
	if ( ! is_object( $post ) ) {
		return '';
	}
	$routes = skyyrose2_legacy_collection_routes();
	$path = 'page' === $post->post_type ? ( $routes[ $post->post_name ] ?? '' ) : ( skyyrose2_is_retired_demo_post( $post ) ? 'journal' : '' );
	if ( ! $path ) {
		return '';
	}
	$target = get_page_by_path( $path, OBJECT, 'page' );
	return $target && 'publish' === $target->post_status && empty( $target->post_password ) ? ( get_permalink( $target->ID ) ?: '' ) : '';
}

/** Preserve archived records; use reversible redirects during staging review. */
function skyyrose2_redirect_retired_public_content() {
	if ( is_admin() || wp_doing_ajax() || is_preview() || is_feed() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) || ! is_singular( array( 'page', 'post' ) ) || ! in_array( $_SERVER['REQUEST_METHOD'] ?? 'GET', array( 'GET', 'HEAD' ), true ) ) {
		return;
	}
	$target = skyyrose2_retired_content_target( get_queried_object() );
	if ( ! $target ) {
		return;
	}
	$attribution = array();
	foreach ( array( 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_id', 'gclid', 'fbclid', 'msclkid' ) as $key ) {
		if ( isset( $_GET[ $key ] ) && is_string( $_GET[ $key ] ) ) {
			$attribution[ $key ] = sanitize_text_field( wp_unslash( $_GET[ $key ] ) );
		}
	}
	$target = $attribution ? add_query_arg( $attribution, $target ) : $target;
	if ( wp_safe_redirect( $target, 'production' === wp_get_environment_type() ? 301 : 302, 'SkyyRose V2' ) ) {
		exit;
	}
}
add_action( 'template_redirect', 'skyyrose2_redirect_retired_public_content', 1 );

/**
 * Preserve V2's canonical collection and world URLs after legacy page records are retired.
 *
 * These are request-path aliases rather than WordPress page aliases so old campaign links,
 * saved bookmarks, and classic-menu references remain valid after the source pages move to Trash.
 */
function skyyrose2_retired_v2_page_routes() {
	return array(
		'experiences'                 => 'worlds',
		'experience-signature'        => 'worlds/signature',
		'experience-black-rose'       => 'worlds/black-rose',
		'experience-love-hurts'       => 'worlds/love-hurts',
		'experience-kids-capsule'     => 'worlds/kids-capsule',
		'collections-world'           => 'collections',
		'landing-signature'           => 'collections/signature',
		'landing-black-rose'          => 'collections/black-rose',
		'landing-love-hurts'          => 'collections/love-hurts',
		'landing-kids-capsule'        => 'collections/kids-capsule',
		'collection-kids-capsule'     => 'collections/kids-capsule',
	);
}

/** Return every retired public route that should resolve to a V2 canonical page. */
function skyyrose2_retired_v2_routes() {
	return array_merge( skyyrose2_legacy_collection_routes(), skyyrose2_retired_v2_page_routes() );
}

/** Repair internal menu URLs without editing the stored menus or other worlds. */
function skyyrose2_canonical_collection_menu_links( $atts ) {
	$href = $atts['href'] ?? '';
	$host = wp_parse_url( $href, PHP_URL_HOST );
	if ( $host && strtolower( $host ) !== strtolower( (string) wp_parse_url( home_url(), PHP_URL_HOST ) ) ) {
		return $atts;
	}
	$slug = trim( (string) wp_parse_url( $href, PHP_URL_PATH ), '/' );
	$routes = skyyrose2_retired_v2_routes();
	if ( isset( $routes[ $slug ] ) ) {
		$target = get_page_by_path( $routes[ $slug ], OBJECT, 'page' );
		if ( $target && 'publish' === $target->post_status && empty( $target->post_password ) ) {
			$atts['href'] = get_permalink( $target->ID ) ?: $href;
		}
	}
	return $atts;
}
add_filter( 'nav_menu_link_attributes', 'skyyrose2_canonical_collection_menu_links', 20 );

/** Keep the footer's direct Kids Capsule path visible when its retired menu item is hidden. */
function skyyrose2_restore_footer_kids_capsule_link( $items, $args ) {
	if ( empty( $args->menu_class ) || false === strpos( (string) $args->menu_class, 'menu-footer-shop' ) || false !== strpos( $items, '/collections/kids-capsule/' ) ) {
		return $items;
	}

	$kids_capsule = get_page_by_path( 'collections/kids-capsule', OBJECT, 'page' );
	if ( ! $kids_capsule || 'publish' !== $kids_capsule->post_status || ! empty( $kids_capsule->post_password ) ) {
		return $items;
	}

	$url = get_permalink( $kids_capsule->ID );
	if ( ! $url ) {
		return $items;
	}

	return '<li class="menu-item menu-item-skyyrose2-kids-capsule"><a href="' . esc_url( $url ) . '">' . esc_html__( 'Kids Capsule', 'skyyrose-flagship-2' ) . '</a></li>' . $items;
}
add_filter( 'wp_nav_menu_items', 'skyyrose2_restore_footer_kids_capsule_link', 20, 2 );

/** Archives and feeds must not re-surface the retired demo material. */
function skyyrose2_exclude_retired_demo_archives( $query ) {
	if ( is_admin() || ! $query->is_main_query() || ! ( $query->is_archive() || $query->is_feed() ) ) {
		return;
	}
	$types = $query->get( 'post_type' );
	if ( $types && ! in_array( $types, array( 'post', 'any', array( 'post' ) ), true ) ) {
		return;
	}
	$excluded = array_map( 'absint', (array) $query->get( 'post__not_in' ) );
	foreach ( array( 'hello-world', '10-designer-buys-that-are-worth-the-investment', 'our-pick-of-the-coolest-denim-jackets-this-season', 'jay-ellis-proves-one-suit-can-work-four-different-ways' ) as $slug ) {
		$post = get_page_by_path( $slug, OBJECT, 'post' );
		if ( skyyrose2_is_retired_demo_post( $post ) ) {
			$excluded[] = (int) $post->ID;
		}
	}
	$query->set( 'post__not_in', array_values( array_unique( $excluded ) ) );
}
add_action( 'pre_get_posts', 'skyyrose2_exclude_retired_demo_archives', 22 );

/** Remove just the first redundant title, retaining any existing fragment anchor. */
function skyyrose2_strip_redundant_content_title( $content, $title ) {
	if ( ! preg_match( '/<h([12])\b([^>]*)>(.*?)<\/h\1\s*>/is', $content, $match, PREG_OFFSET_CAPTURE ) ) {
		return $content;
	}
	$before = substr( $content, 0, $match[0][1] );
	$normalize = static function ( $value ) {
		$value = html_entity_decode( wp_strip_all_tags( $value ), ENT_QUOTES | ENT_HTML5, 'UTF-8' );
		return strtolower( trim( preg_replace( '/\s+/u', ' ', $value ) ) );
	};
	if ( '' !== $normalize( preg_replace( '/<!--.*?-->/s', '', $before ) ) || $normalize( $match[3][0] ) !== $normalize( $title ) ) {
		return $content;
	}
	$anchor = '';
	if ( preg_match( '/\bid\s*=\s*(["\'])(.*?)\1/is', $match[2][0], $id ) ) {
		$anchor = '<span id="' . esc_attr( html_entity_decode( $id[2], ENT_QUOTES | ENT_HTML5, 'UTF-8' ) ) . '" class="sr2-content-title-anchor" aria-hidden="true"></span>';
	}
	return substr_replace( $content, $anchor, $match[0][1], strlen( $match[0][0] ) );
}

function skyyrose2_remove_redundant_content_title( $content ) {
	if ( is_admin() || ! in_the_loop() || ! is_main_query() || ! ( is_singular( 'post' ) || is_page( array( 'accessibility', 'landing-black-rose', 'landing-love-hurts', 'privacy-policy', 'refund-policy', 'shipping-returns', 'landing-signature', 'terms-of-service' ) ) ) ) {
		return $content;
	}
	$content = skyyrose2_strip_redundant_content_title( $content, get_the_title() );
	return is_singular( 'post' ) ? preg_replace( '/<(\/?)h1(?=[\s>])/i', '<$1h2', $content ) : $content;
}
add_filter( 'the_content', 'skyyrose2_remove_redundant_content_title', 25 );

/**
 * Redirect retired collection aliases even after their old page records are removed.
 *
 * These routes are intentionally resolved from the request path rather than a queried
 * page object. That leaves the canonical collection URL available after the legacy
 * page is moved to trash and its old template is no longer publicly renderable.
 */
function skyyrose2_redirect_retired_collection_alias_request() {
	if ( is_admin() || wp_doing_ajax() || is_preview() || is_feed() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) ) {
		return;
	}

	$method = isset( $_SERVER['REQUEST_METHOD'] ) ? strtoupper( sanitize_text_field( wp_unslash( $_SERVER['REQUEST_METHOD'] ) ) ) : 'GET';
	if ( ! in_array( $method, array( 'GET', 'HEAD' ), true ) ) {
		return;
	}

	$request_uri  = isset( $_SERVER['REQUEST_URI'] ) ? wp_unslash( $_SERVER['REQUEST_URI'] ) : '';
	$request_path = wp_parse_url( $request_uri, PHP_URL_PATH );
	$request_slug = trim( is_string( $request_path ) ? $request_path : '', '/' );
	$routes       = skyyrose2_retired_v2_routes();
	if ( ! isset( $routes[ $request_slug ] ) ) {
		return;
	}

	$destination = get_page_by_path( $routes[ $request_slug ], OBJECT, 'page' );
	if ( ! $destination || 'publish' !== $destination->post_status || ! empty( $destination->post_password ) ) {
		return;
	}

	$target = get_permalink( $destination->ID );
	if ( ! $target ) {
		return;
	}

	$attribution = array();
	foreach ( array( 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_id', 'gclid', 'fbclid', 'msclkid' ) as $key ) {
		if ( isset( $_GET[ $key ] ) && is_scalar( $_GET[ $key ] ) ) {
			$attribution[ $key ] = sanitize_text_field( wp_unslash( $_GET[ $key ] ) );
		}
	}
	$target = $attribution ? add_query_arg( $attribution, $target ) : $target;

	if ( wp_safe_redirect( $target, 'production' === wp_get_environment_type() ? 301 : 302, 'SkyyRose V2' ) ) {
		exit;
	}
}
add_action( 'template_redirect', 'skyyrose2_redirect_retired_collection_alias_request', 0 );

/** Retired cross-sell surfaces must not compete with the selected garment. */
function skyyrose2_retire_cross_sells() {
	remove_action( 'woocommerce_after_single_product_summary', 'woocommerce_upsell_display', 15 );
	remove_action( 'woocommerce_after_single_product_summary', 'woocommerce_output_related_products', 20 );
	remove_action( 'woocommerce_cart_collaterals', 'woocommerce_cross_sell_display' );
}
add_action( 'wp', 'skyyrose2_retire_cross_sells' );
