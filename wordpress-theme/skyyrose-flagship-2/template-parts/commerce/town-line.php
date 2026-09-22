<?php
/**
 * Static Town Line directory. Registry order and real public product links;
 * no film, poster, campaign image, or inferred product-media authorization.
 * Reusable by collection and Home compositions.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;

$town_registry = skyyrose2_presentation_registry();
$town_records  = isset( $town_registry['products'] ) && is_array( $town_registry['products'] ) ? $town_registry['products'] : array();
$town_series   = array();
foreach ( $town_records as $town_sku => $town_record ) {
	if ( 'black-rose' === ( $town_record['collection'] ?? '' ) && 'jersey-series' === ( $town_record['presentation'] ?? '' ) ) {
		$town_series[ $town_sku ] = absint( $town_record['series_order'] ?? 0 );
	}
}
asort( $town_series, SORT_NUMERIC );
// This resolver checks the exact SKU, published status, visibility, registry
// collection, and actual Woo category membership. Missing pieces stay absent.
$town_products = skyyrose2_get_products_by_skus( array_keys( $town_series ), 'black-rose' );
if ( ! $town_products ) {
	return;
}
?>
<section class="sr2-town-line" aria-labelledby="sr2-town-line-title" data-collection="black-rose" data-presentation="jersey-series">
	<header class="sr2-town-line__head">
		<p class="sr2-world-index"><?php esc_html_e( 'Jersey Series / The Town Line', 'skyyrose-flagship-2' ); ?></p>
		<h2 id="sr2-town-line-title"><?php esc_html_e( 'Every number carries the tour.', 'skyyrose-flagship-2' ); ?></h2>
		<p><?php esc_html_e( 'Oakland is the origin. San Francisco, The Bay, and San Jose become chapters on The Town Line: SkyyRose’s fictional house journey.', 'skyyrose-flagship-2' ); ?></p>
	</header>
	<ol class="sr2-town-line__directory">
		<?php foreach ( $town_products as $town_sku => $town_product ) : ?>
			<li>
				<a href="<?php echo esc_url( $town_product->get_permalink() ); ?>">
					<span class="sr2-town-line__sku"><?php echo esc_html( strtoupper( $town_sku ) ); ?></span>
					<span class="sr2-town-line__name"><?php echo esc_html( $town_product->get_name() ); ?></span>
					<span class="sr2-town-line__arrow" aria-hidden="true">↗</span>
				</a>
			</li>
		<?php endforeach; ?>
	</ol>
</section>
