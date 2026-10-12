<?php
/**
 * Native Shop URL state and archive composition helpers.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/** Real Woo category terms; never route filtering into a collection story page. */
function skyyrose2_shop_categories( $hide_empty = false ) {
	$terms = get_terms(
		array(
			'taxonomy'   => 'product_cat',
			'hide_empty' => $hide_empty,
			'orderby'    => 'name',
			'order'      => 'ASC',
		)
	);
	return is_wp_error( $terms ) ? array() : $terms;
}

/** Validate only the Shop-owned scalar dimensions, before Woo reads URL prices. */
function skyyrose2_shop_filter_state( $input ) {
	$state = array(
		'product_cat'  => '',
		'stock_status' => '',
		'min_price'    => '',
		'max_price'    => '',
		'orderby'      => '',
	);
	if ( ! is_array( $input ) ) {
		return $state;
	}
	$categories = array_column( skyyrose2_shop_categories(), 'slug' );
	$sort_keys  = array_keys( apply_filters( 'woocommerce_catalog_orderby', array_fill_keys( array( 'menu_order', 'popularity', 'rating', 'date', 'price', 'price-desc', 'relevance' ), '' ) ) );
	foreach ( $state as $key => $unused ) {
		if ( ! isset( $input[ $key ] ) || ! is_string( $input[ $key ] ) ) {
			continue;
		}
		$value         = trim( wp_unslash( $input[ $key ] ) );
		$category_slug = 'product_cat' === $key ? basename( $value ) : '';
		if ( 'product_cat' === $key && in_array( $category_slug, $categories, true ) ) {
			$state[ $key ] = $category_slug;
		} elseif ( 'stock_status' === $key && in_array( $value, array( 'instock', 'outofstock', 'onbackorder' ), true ) ) {
			$state[ $key ] = $value;
		} elseif ( 'orderby' === $key && in_array( $value, $sort_keys, true ) ) {
			$state[ $key ] = $value;
		} elseif ( in_array( $key, array( 'min_price', 'max_price' ), true ) && preg_match( '/^\d{1,9}(?:\.\d{1,6})?$/D', $value ) ) {
			$state[ $key ] = $value;
		}
	}
	return $state;
}

/** Only the public main product archive request, including pretty taxonomy URLs. */
function skyyrose2_shop_request_vars( $vars ) {
	if ( ! function_exists( 'wc_get_page_id' ) || is_admin() || wp_doing_ajax() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) || ! is_array( $vars ) ) {
		return $vars;
	}
	$is_archive = 'product' === ( $vars['post_type'] ?? '' )
		|| isset( $vars['product_cat'] ) || isset( $vars['product_tag'] )
		|| ( isset( $vars['taxonomy'] ) && is_string( $vars['taxonomy'] ) && in_array( $vars['taxonomy'], get_object_taxonomies( 'product' ), true ) )
		|| ( isset( $vars['page_id'] ) && is_scalar( $vars['page_id'] ) && (int) $vars['page_id'] === wc_get_page_id( 'shop' ) )
		|| ( isset( $vars['pagename'] ) && is_string( $vars['pagename'] ) && $vars['pagename'] === get_page_uri( wc_get_page_id( 'shop' ) ) );
	if ( ! $is_archive || isset( $vars['product'] ) || isset( $vars['name'] ) || isset( $vars['p'] ) ) {
		return $vars;
	}
	// No mutation/nonce: these are read-only, public catalog filters. Clear
	// malformed arrays before native WP taxonomy and Woo price parsing run.
	$input = array_merge( $_GET, array_intersect_key( $vars, array( 'product_cat' => true ) ) ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended
	$state = skyyrose2_shop_filter_state( $input );
	foreach ( $state as $key => $value ) {
		// WP resolves hierarchical category paths and unknown terms itself. Keep
		// scalar native routing intact so parent/child works and unknown URLs
		// remain 404s; only malformed category containers need removal here.
		if ( 'product_cat' === $key && isset( $input[ $key ] ) && is_string( $input[ $key ] ) ) {
			continue;
		}
		if ( isset( $_GET[ $key ] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Recommended
			if ( '' === $value ) {
				unset( $_GET[ $key ] );
			} else {
				$_GET[ $key ] = $value;
			}
		}
		if ( array_key_exists( $key, $vars ) ) {
			if ( '' === $value ) {
				unset( $vars[ $key ] );
			} else {
				$vars[ $key ] = $value;
			}
		}
	}
	return $vars;
}
add_filter( 'request', 'skyyrose2_shop_request_vars', 20 );

/**
 * Restrict stock filtering to the real main frontend Woo archive query.
 *
 * Woo's meta-query filter receives WC_Query, not the affected WP_Query, and
 * does not forward its main-query flag. This action supplies the actual query
 * after Woo built its native conditions; wrap them, never overwrite their OR.
 */
function skyyrose2_shop_stock_query( $query ) {
	if ( is_admin() || wp_doing_ajax() || ( defined( 'REST_REQUEST' ) && REST_REQUEST )
		|| ! $query->is_main_query()
		|| ! ( $query->is_post_type_archive( 'product' ) || $query->is_tax( get_object_taxonomies( 'product' ) ) ) ) {
		return;
	}
	$state = skyyrose2_shop_filter_state( $_GET ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended
	if ( '' === $state['stock_status'] ) {
		return;
	}
	$stock_clause = array(
		'key'     => '_stock_status',
		'value'   => $state['stock_status'],
		'compare' => '=',
	);
	$existing     = $query->get( 'meta_query' );
	$meta         = array( 'relation' => 'AND' );
	if ( is_array( $existing ) && $existing ) {
		$meta[] = $existing;
	}
	$meta[] = $stock_clause;
	$query->set( 'meta_query', $meta );
}
add_action( 'woocommerce_product_query', 'skyyrose2_shop_stock_query', 20 );

/** Current controls include the category from a pretty native taxonomy route. */
function skyyrose2_shop_current_state() {
	$input = $_GET; // phpcs:ignore WordPress.Security.NonceVerification.Recommended
	if ( is_product_category() ) {
		$term = get_queried_object();
		if ( $term instanceof WP_Term ) {
			$input['product_cat'] = $term->slug;
		}
	}
	return skyyrose2_shop_filter_state( $input );
}

/** Change a collection/category, preserving other public native filter state. */
function skyyrose2_shop_query_args() {
	$args = $_GET; // phpcs:ignore WordPress.Security.NonceVerification.Recommended
	if ( is_product_taxonomy() && ! is_product_category() ) {
		$term = get_queried_object();
		if ( $term instanceof WP_Term ) {
			$taxonomy = get_taxonomy( $term->taxonomy );
			if ( $taxonomy && is_string( $taxonomy->query_var ) && '' !== $taxonomy->query_var ) {
				$args[ $taxonomy->query_var ] = $term->slug;
			}
		}
	}
	return $args;
}

/** Change a category without losing search, attribute, or pretty taxonomy state. */
function skyyrose2_shop_category_url( $slug ) {
	$args = map_deep( wp_unslash( skyyrose2_shop_query_args() ), 'sanitize_text_field' );
	foreach ( array( 'product_cat', 'paged', 'product-page', 'page', 'add-to-cart', 'remove_item', 'undo_item', '_wpnonce', 'quantity' ) as $key ) {
		unset( $args[ $key ] );
	}
	if ( '' !== $slug ) {
		$args['product_cat'] = $slug;
	}
	return add_query_arg( $args, wc_get_page_permalink( 'shop' ) );
}

/**
 * Image slots for the garment grid: one full-width tile below 48em, then 2/3/4
 * tracks at 48/64/90em with the page pad and --sr2-grid-gap subtracted; the
 * grid stops growing at four 363px tracks (shop-page.css caps the shell).
 */
function skyyrose2_shop_card_sizes() {
	return '(max-width: 22.49em) calc(100vw - 2rem), (max-width: 47.99em) calc(100vw - 2 * clamp(1rem, 4vw, 4rem)), (max-width: 63.99em) calc((100vw - 2 * clamp(1rem, 4vw, 4rem) - clamp(1rem, 2vw, 2rem)) / 2), (max-width: 89.99em) calc((100vw - 2 * clamp(1rem, 4vw, 4rem) - 2 * clamp(1rem, 2vw, 2rem)) / 3), (max-width: 104.74em) calc((100vw - 2 * clamp(1rem, 4vw, 4rem) - 3 * clamp(1rem, 2vw, 2rem)) / 4), 363px';
}

/**
 * Arrival copy for the archive head. A collection category speaks in its own
 * shop voice from skyyrose2_collections(); everything else is the house edit.
 *
 * @param array $filter_state Output of skyyrose2_shop_current_state().
 * @return array{collection:string,eyebrow:string,lede:string}
 */
function skyyrose2_shop_archive_context( $filter_state ) {
	$slug        = is_array( $filter_state ) ? (string) ( $filter_state['product_cat'] ?? '' ) : '';
	$collections = skyyrose2_collections();
	if ( '' !== $slug && isset( $collections[ $slug ] ) ) {
		$collection = $collections[ $slug ];
		return array(
			'collection' => $slug,
			'eyebrow'    => (string) ( $collection['shop_kicker'] ?? $collection['name'] ),
			'lede'       => (string) ( $collection['shop_intro'] ?? '' ),
		);
	}
	return array(
		'collection' => '',
		'eyebrow'    => __( 'The House Edit', 'skyyrose-flagship-2' ),
		'lede'       => '',
	);
}

/** Keep Woo's options, selection, extension filters and URL fields; add no-JS submit. */
function skyyrose2_shop_ordering() {
	ob_start();
	woocommerce_catalog_ordering( array( 'useLabel' => true ) );
	$form   = ob_get_clean();
	$submit = '<button type="submit" class="sr2-control sr2-shop-sort-submit">' . esc_html__( 'Sort', 'skyyrose-flagship-2' ) . '</button>';
	// The native template owns this form. Only append its missing submit action.
	echo str_replace( '</form>', $submit . '</form>', $form ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
}

/** Apply the Shop-specific ordering presentation only on native archives. */
function skyyrose2_shop_hooks() {
	if ( function_exists( 'is_shop' ) && ( is_shop() || is_product_taxonomy() ) ) {
		remove_action( 'woocommerce_before_shop_loop', 'woocommerce_catalog_ordering', 30 );
		add_action( 'woocommerce_before_shop_loop', 'skyyrose2_shop_ordering', 30 );
	}
}
add_action( 'wp', 'skyyrose2_shop_hooks', 20 );

/** An editorial aside, never a grouping or reordering of native query results. */
function skyyrose2_shop_world_note( $slug ) {
	$worlds = skyyrose2_collections();
	if ( ! is_string( $slug ) || ! isset( $worlds[ $slug ] ) ) {
		return;
	}
	$world  = $worlds[ $slug ];
	$number = array_search( $slug, array_keys( $worlds ), true ) + 1;
	?>
	<li class="sr2-shop-world-note" data-collection="<?php echo esc_attr( $slug ); ?>">
		<aside class="sr2-shop-world-note__inner" aria-labelledby="sr2-shop-world-title">
			<p class="sr2-eyebrow sr2-eyebrow--engraved sr2-shop-world-note__index"><?php echo esc_html( sprintf( '%02d / %s', $number, $world['name'] ) ); ?></p>
			<h2 id="sr2-shop-world-title" class="sr2-shop-world-note__title"><?php echo esc_html( $world['shop_heading'] ?? $world['headline'] ); ?></h2>
			<p class="sr2-lede sr2-shop-world-note__story"><?php echo esc_html( $world['manifesto'] ); ?></p>
			<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_collection_url( $slug ) ); ?>"><?php echo esc_html( sprintf( __( 'Enter %s', 'skyyrose-flagship-2' ), $world['name'] ) ); ?><span aria-hidden="true">→</span></a>
		</aside>
	</li>
	<?php
}

/**
 * Founder ruling 2026-10-11: the unfiltered Shop keeps the separate collection
 * structure (the v2 Cinema Bands). Only the public main product archive with no
 * collection, stock, price, layered-nav or rating filter qualifies; search and
 * taxonomy routes keep the grid. Ordering alone orders pieces within each band.
 *
 * @param WP_Query|null $query Query to classify; the global main query by default.
 * @return bool
 */
function skyyrose2_shop_bands_v2_active( $query = null ) {
	$query = null === $query ? ( $GLOBALS['wp_query'] ?? null ) : $query;
	if ( is_admin() || wp_doing_ajax() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) || ! is_object( $query ) || ! method_exists( $query, 'is_main_query' )
		|| ! $query->is_main_query() || ! $query->is_post_type_archive( 'product' ) || $query->is_search() || $query->is_tax() || $query->is_feed() ) {
		return false;
	}
	$state = skyyrose2_shop_filter_state( $_GET ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended
	if ( '' !== $state['product_cat'] . $state['stock_status'] . $state['min_price'] . $state['max_price'] ) {
		return false;
	}
	// Woo's layered-nav (filter_*) and rating filters are filtered views too (WC is_filtered()).
	foreach ( $_GET as $key => $value ) { // phpcs:ignore WordPress.Security.NonceVerification.Recommended
		if ( is_string( $key ) && ( 0 === strpos( $key, 'filter_' ) || 'rating_filter' === $key ) && '' !== $value ) {
			return false;
		}
	}
	return true;
}

/**
 * The grouped view renders every published piece on one page. WooCommerce's own
 * pre_get_posts (priority 10) applies loop_shop_per_page; this runs after it.
 *
 * @param WP_Query $query Main query being prepared.
 */
function skyyrose2_shop_bands_v2_query( $query ) {
	if ( skyyrose2_shop_bands_v2_active( $query ) ) {
		$query->set( 'posts_per_page', -1 );
	}
}
add_action( 'pre_get_posts', 'skyyrose2_shop_bands_v2_query', 30 );

/**
 * House collection slug a piece is grouped under, or '' when it has none.
 *
 * @param WC_Product $product Native product.
 * @return string
 */
function skyyrose2_shop_bands_v2_collection( $product ) {
	$record = skyyrose2_product_presentation( $product );
	$slug   = sanitize_title( (string) ( $record['collection'] ?? '' ) );
	return '' !== $slug && array_key_exists( $slug, skyyrose2_collections() ) ? $slug : '';
}

/**
 * Stable house-order sort of the grouped view's results, so the main query's
 * first piece is the first card of the first band (the archive preload reads
 * this order). Within a collection the native order, including Sort, is kept.
 *
 * @param WP_Post[] $posts Query results.
 * @param WP_Query  $query Query that produced them.
 * @return WP_Post[]
 */
function skyyrose2_shop_bands_v2_house_order( $posts, $query ) {
	if ( ! is_array( $posts ) || count( $posts ) < 2 || ! function_exists( 'wc_get_product' ) || ! skyyrose2_shop_bands_v2_active( $query ) ) {
		return $posts;
	}
	$rank  = array_flip( array_keys( skyyrose2_collections() ) );
	$order = array();
	foreach ( array_values( $posts ) as $position => $post ) {
		$product = is_object( $post ) && isset( $post->ID ) ? wc_get_product( $post->ID ) : null;
		$slug    = $product ? skyyrose2_shop_bands_v2_collection( $product ) : '';
		$order[] = array( $rank[ $slug ] ?? count( $rank ), $position, $post );
	}
	usort(
		$order,
		static function ( $left, $right ) {
			return array( $left[0], $left[1] ) <=> array( $right[0], $right[1] );
		}
	);
	return array_column( $order, 2 );
}
add_filter( 'the_posts', 'skyyrose2_shop_bands_v2_house_order', 20, 2 );

/**
 * Group pieces for the bands template: every house collection in house order,
 * plus the pieces with no collection so nothing published is unreachable.
 *
 * @param WC_Product[] $products Pieces in main-query order.
 * @return array{groups:array<string,array{collection:array,products:WC_Product[]}>,ungrouped:WC_Product[]}
 */
function skyyrose2_shop_bands_v2_groups( $products ) {
	$groups = array();
	foreach ( skyyrose2_collections() as $slug => $collection ) {
		$groups[ $slug ] = array(
			'collection' => $collection,
			'products'   => array(),
		);
	}
	$ungrouped = array();
	foreach ( $products as $product ) {
		$slug = skyyrose2_shop_bands_v2_collection( $product );
		if ( '' !== $slug ) {
			$groups[ $slug ]['products'][] = $product;
		} else {
			$ungrouped[] = $product;
		}
	}
	return array(
		'groups'    => $groups,
		'ungrouped' => $ungrouped,
	);
}

/** Stale /shop/page/N/ links on the one-page grouped view resolve to /shop/, keeping ordering and tracking args. */
function skyyrose2_shop_bands_v2_redirect() {
	if ( (int) get_query_var( 'paged' ) < 2 || ! skyyrose2_shop_bands_v2_active() ) {
		return;
	}
	wp_safe_redirect( skyyrose2_shop_category_url( '' ), 301 );
	exit;
}
add_action( 'template_redirect', 'skyyrose2_shop_bands_v2_redirect', 5 );
