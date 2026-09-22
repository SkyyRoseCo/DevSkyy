<?php
/**
 * The house garment archive, backed by the native WooCommerce main query.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$archive_title = woocommerce_page_title( false );
$filter_state  = skyyrose2_shop_current_state();
$categories    = skyyrose2_shop_categories();
$category_map  = array();
foreach ( $categories as $category ) {
	$category_map[ $category->slug ] = $category;
}
$stock_labels = array(
	'instock'     => __( 'In stock', 'skyyrose-flagship-2' ),
	'outofstock'  => __( 'Out of stock', 'skyyrose-flagship-2' ),
	'onbackorder' => __( 'On backorder', 'skyyrose-flagship-2' ),
);
$active_count = count( array_filter( array_diff_key( $filter_state, array( 'orderby' => true ) ), static function ( $value ) { return '' !== $value; } ) );
$reset_url = wc_get_page_permalink( 'shop' );

get_header();
?>
<main id="primary" class="sr2-shop sr2-shop-archive">
	<div class="sr2-shop-archive__inner">
		<?php do_action( 'woocommerce_before_main_content' ); ?>
		<header class="sr2-shop-archive__head">
			<p class="sr2-shop-archive__index"><?php esc_html_e( 'Oakland, California', 'skyyrose-flagship-2' ); ?><span> / <?php esc_html_e( 'The living archive', 'skyyrose-flagship-2' ); ?></span></p>
			<h1><?php echo esc_html( $archive_title ); ?></h1>
		</header>
		<nav class="sr2-shop-archive__collections" aria-label="<?php esc_attr_e( 'Filter by collection', 'skyyrose-flagship-2' ); ?>">
			<a href="<?php echo esc_url( skyyrose2_shop_category_url( '' ) ); ?>"<?php if ( '' === $filter_state['product_cat'] ) : ?> aria-current="page"<?php endif; ?>><?php esc_html_e( 'All pieces', 'skyyrose-flagship-2' ); ?></a>
			<?php foreach ( skyyrose2_collections() as $slug => $collection ) : ?>
				<?php if ( ! isset( $category_map[ $slug ] ) ) { continue; } ?>
				<a href="<?php echo esc_url( skyyrose2_shop_category_url( $slug ) ); ?>"<?php if ( $slug === $filter_state['product_cat'] ) : ?> aria-current="page"<?php endif; ?>><?php echo esc_html( $category_map[ $slug ]->name ); ?></a>
			<?php endforeach; ?>
		</nav>
		<section class="sr2-shop-archive__results" aria-label="<?php esc_attr_e( 'Products', 'skyyrose-flagship-2' ); ?>">
			<div class="sr2-shop-archive__tools">
				<details class="sr2-shop-filters">
					<summary><?php esc_html_e( 'Filters', 'skyyrose-flagship-2' ); ?><?php if ( $active_count ) : ?><span class="sr2-shop-filters__count"><?php echo esc_html( sprintf( __( '%d active', 'skyyrose-flagship-2' ), $active_count ) ); ?></span><?php endif; ?></summary>
					<form method="get" action="<?php echo esc_url( $reset_url ); ?>" class="sr2-shop-filters__form">
						<fieldset>
							<legend class="screen-reader-text"><?php esc_html_e( 'Filter products', 'skyyrose-flagship-2' ); ?></legend>
							<div class="sr2-field"><label for="sr2-shop-category"><?php esc_html_e( 'Collection or category', 'skyyrose-flagship-2' ); ?></label><select id="sr2-shop-category" name="product_cat"><option value=""><?php esc_html_e( 'All categories', 'skyyrose-flagship-2' ); ?></option><?php foreach ( $categories as $category ) : ?><option value="<?php echo esc_attr( $category->slug ); ?>" <?php selected( $filter_state['product_cat'], $category->slug ); ?>><?php echo esc_html( $category->name ); ?></option><?php endforeach; ?></select></div>
							<div class="sr2-field"><label for="sr2-shop-stock"><?php esc_html_e( 'Availability', 'skyyrose-flagship-2' ); ?></label><select id="sr2-shop-stock" name="stock_status"><option value=""><?php esc_html_e( 'Any availability', 'skyyrose-flagship-2' ); ?></option><?php foreach ( $stock_labels as $value => $label ) : ?><option value="<?php echo esc_attr( $value ); ?>" <?php selected( $filter_state['stock_status'], $value ); ?>><?php echo esc_html( $label ); ?></option><?php endforeach; ?></select></div>
							<div class="sr2-field"><label for="sr2-shop-min"><?php echo esc_html( sprintf( __( 'Minimum price (%s)', 'skyyrose-flagship-2' ), get_woocommerce_currency() ) ); ?></label><input id="sr2-shop-min" type="number" inputmode="decimal" name="min_price" min="0" step="any" value="<?php echo esc_attr( $filter_state['min_price'] ); ?>"></div>
							<div class="sr2-field"><label for="sr2-shop-max"><?php echo esc_html( sprintf( __( 'Maximum price (%s)', 'skyyrose-flagship-2' ), get_woocommerce_currency() ) ); ?></label><input id="sr2-shop-max" type="number" inputmode="decimal" name="max_price" min="0" step="any" value="<?php echo esc_attr( $filter_state['max_price'] ); ?>"></div>
						</fieldset>
						<?php wc_query_string_form_fields( skyyrose2_shop_query_args(), array( 'product_cat', 'stock_status', 'min_price', 'max_price', 'paged', 'product-page', 'page', 'add-to-cart', 'remove_item', 'undo_item', '_wpnonce', 'quantity' ) ); ?>
						<div class="sr2-shop-filters__actions"><button type="submit" class="sr2-control sr2-control--primary"><?php esc_html_e( 'Apply filters', 'skyyrose-flagship-2' ); ?></button><a class="sr2-control sr2-control--quiet" href="<?php echo esc_url( $reset_url ); ?>"><?php esc_html_e( 'Clear filters', 'skyyrose-flagship-2' ); ?></a></div>
					</form>
				</details>
				<?php if ( woocommerce_product_loop() ) : ?>
					<?php do_action( 'woocommerce_before_shop_loop' ); ?>
				<?php else : ?>
					<p class="sr2-shop-archive__no-count"><?php esc_html_e( 'No matching pieces', 'skyyrose-flagship-2' ); ?></p>
				<?php endif; ?>
			</div>
			<?php if ( $active_count ) : ?>
				<p class="sr2-shop-archive__active"><span><?php esc_html_e( 'Viewing:', 'skyyrose-flagship-2' ); ?> <?php
					$active_labels = array();
					if ( $filter_state['product_cat'] ) { $active_labels[] = $category_map[ $filter_state['product_cat'] ]->name; }
					if ( $filter_state['stock_status'] ) { $active_labels[] = $stock_labels[ $filter_state['stock_status'] ]; }
					if ( '' !== $filter_state['min_price'] ) { $active_labels[] = sprintf( __( 'From %s %s', 'skyyrose-flagship-2' ), $filter_state['min_price'], get_woocommerce_currency() ); }
					if ( '' !== $filter_state['max_price'] ) { $active_labels[] = sprintf( __( 'Up to %s %s', 'skyyrose-flagship-2' ), $filter_state['max_price'], get_woocommerce_currency() ); }
					echo esc_html( implode( ' · ', $active_labels ) );
				?></span><a href="<?php echo esc_url( $reset_url ); ?>"><?php esc_html_e( 'Clear', 'skyyrose-flagship-2' ); ?></a></p>
			<?php endif; ?>
			<?php
			if ( woocommerce_product_loop() ) {
				woocommerce_product_loop_start();
				$piece_number = 0;
				$editorial_world = '';
				if ( wc_get_loop_prop( 'total' ) ) {
					while ( have_posts() ) {
						the_post();
						if ( 0 === $piece_number ) {
							$first_piece = wc_get_product( get_the_ID() );
							$first_record = $first_piece ? skyyrose2_product_presentation( $first_piece ) : array();
							$editorial_world = $first_record['collection'] ?? '';
						}
						if ( 8 === $piece_number ) {
							skyyrose2_shop_world_note( $editorial_world );
						}
						++$piece_number;
						do_action( 'woocommerce_shop_loop' );
						wc_get_template_part( 'content', 'product' );
					}
				}
				woocommerce_product_loop_end();
				do_action( 'woocommerce_after_shop_loop' );
			} else {
				do_action( 'woocommerce_no_products_found' );
				?>
				<div class="sr2-shop-archive__empty"><p><?php esc_html_e( 'Try another category or widen your price and availability filters.', 'skyyrose-flagship-2' ); ?></p><a class="sr2-control sr2-control--primary" href="<?php echo esc_url( $reset_url ); ?>"><?php esc_html_e( 'View all pieces', 'skyyrose-flagship-2' ); ?></a></div>
				<?php
			}
			do_action( 'woocommerce_after_main_content' );
			?>
		</section>
	</div>
</main>
<?php get_footer(); ?>
