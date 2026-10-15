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
