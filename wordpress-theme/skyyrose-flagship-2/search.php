<?php
/** Exclusive groups over native, bounded and paginated GET search. @package SkyyRoseFlagship2 */
defined( 'ABSPATH' ) || exit;
get_header();
$query  = get_search_query();
$groups = array( 'products' => array(), 'collections' => array(), 'stories' => array(), 'pages' => array() );
$labels = array(
	'products'    => __( 'Products', 'skyyrose-flagship-2' ),
	'collections' => __( 'Collections', 'skyyrose-flagship-2' ),
	'stories'     => __( 'Stories / Journal', 'skyyrose-flagship-2' ),
	'pages'       => __( 'Pages', 'skyyrose-flagship-2' ),
);
while ( have_posts() ) {
	the_post();
	$group = skyyrose2_search_result_group( get_post_type(), get_post_field( 'post_name', get_the_ID() ) );
	if ( 'products' === $group ) {
		$product = function_exists( 'wc_get_product' ) ? wc_get_product( get_the_ID() ) : false;
		if ( $product && $product->is_visible() ) {
			$groups[ $group ][ get_the_ID() ] = $product;
		}
	} elseif ( $group ) {
		$groups[ $group ][ get_the_ID() ] = get_post();
	}
}
// Native text search does not search SKU metadata. One indexed exact lookup
// supplements the first page; it cannot duplicate an existing result by ID.
if ( $query && get_query_var( 'paged', 1 ) <= 1 && function_exists( 'wc_get_product_id_by_sku' ) && in_array( get_query_var( 'post_type' ), array( '', 'product', array( 'product', 'post', 'page' ) ), true ) ) {
	$sku_id      = wc_get_product_id_by_sku( $query );
	$sku_product = $sku_id ? wc_get_product( $sku_id ) : false;
	if ( $sku_product && 'publish' === $sku_product->get_status() && ! $sku_product->is_type( 'variation' ) && $sku_product->is_visible() ) {
		$groups['products'][ $sku_id ] = $sku_product;
	}
}
wp_reset_postdata();
?>
<main id="primary" class="sr2-search" data-sr2-route="shop">
	<header class="sr2-journal__hero">
		<p class="sr2-eyebrow"><?php esc_html_e( 'Search the House', 'skyyrose-flagship-2' ); ?></p>
		<h1><?php printf( esc_html__( 'Results for “%s”', 'skyyrose-flagship-2' ), esc_html( $query ) ); ?></h1>
		<form class="sr2-search__form" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>"><label class="screen-reader-text" for="sr2-search-field"><?php esc_html_e( 'Search', 'skyyrose-flagship-2' ); ?></label><input id="sr2-search-field" type="search" name="s" value="<?php echo esc_attr( $query ); ?>" required><button class="sr2-c-action" type="submit"><?php esc_html_e( 'Search', 'skyyrose-flagship-2' ); ?></button></form>
	</header>
	<?php foreach ( $groups as $group => $results ) : ?>
		<?php if ( ! $results ) { continue; } ?>
		<section class="sr2-search__<?php echo 'products' === $group ? 'products' : 'list'; ?>" data-search-group="<?php echo esc_attr( $group ); ?>" aria-labelledby="sr2-search-<?php echo esc_attr( $group ); ?>-title">
			<header class="sr2-section-head"><h2 id="sr2-search-<?php echo esc_attr( $group ); ?>-title"><?php echo esc_html( $labels[ $group ] ); ?></h2></header>
			<?php if ( 'products' === $group ) : ?>
				<div class="sr2-c-product-grid"><?php $index = 0; foreach ( $results as $product ) { skyyrose2_render_product_loop_card( $product, $index++ ); } ?></div>
			<?php else : ?>
				<?php foreach ( $results as $result ) : ?>
					<article class="sr2-search__result"><h2><a href="<?php echo esc_url( get_permalink( $result ) ); ?>"><?php echo esc_html( get_the_title( $result ) ); ?></a></h2><?php if ( 'stories' === $group ) : ?><p><?php echo esc_html( wp_trim_words( get_the_excerpt( $result ), 32 ) ); ?></p><?php endif; ?></article>
				<?php endforeach; ?>
			<?php endif; ?>
		</section>
	<?php endforeach; ?>
	<?php if ( ! array_filter( $groups ) ) : ?>
		<section class="sr2-search__empty"><h2><?php esc_html_e( 'Nothing surfaced.', 'skyyrose-flagship-2' ); ?></h2><p><?php esc_html_e( 'Try a collection, product, or story title.', 'skyyrose-flagship-2' ); ?></p><a class="sr2-c-action" href="<?php echo esc_url( function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' ) ); ?>"><?php esc_html_e( 'Shop all pieces', 'skyyrose-flagship-2' ); ?></a></section>
	<?php endif; ?>
	<nav class="sr2-pagination"><?php the_posts_pagination(); ?></nav>
</main>
<?php get_footer(); ?>
