<?php
/** Source-bound Jersey Series image gallery. Reusable in Home and house-film surfaces. */
defined( 'ABSPATH' ) || exit;

$registry = skyyrose2_presentation_registry();
$records  = is_array( $registry['products'] ?? null ) ? $registry['products'] : array();
$series   = array();
foreach ( $records as $sku => $record ) {
	if ( 'black-rose' === ( $record['collection'] ?? '' ) && 'jersey-series' === ( $record['presentation'] ?? '' ) ) {
		$series[ $sku ] = absint( $record['series_order'] ?? 0 );
	}
}
asort( $series, SORT_NUMERIC );
$products = skyyrose2_get_products_by_skus( array_keys( $series ), 'black-rose' );
$reveals  = array();
foreach ( $products as $sku => $jersey ) {
	$front = skyyrose2_approved_card_front( $jersey );
	if ( $front ) {
		$reveals[] = array(
			'sku'     => $sku,
			'product' => $jersey,
			'front'   => $front,
		);
	}
}
if ( ! $reveals ) {
	return;
}
?>
		<div class="sr2-jersey-experience__screen" data-jersey-gallery>
			<ol class="sr2-jersey-experience__rail" data-jersey-rail aria-label="<?php esc_attr_e( 'Jersey Series product fronts', 'skyyrose-flagship-2' ); ?>">
				<?php
				foreach ( $reveals as $index => $reveal ) :
					$jersey = $reveal['product'];
					$front  = $reveal['front'];
					?>
				<li class="sr2-jersey-experience__slide">
					<a href="<?php echo esc_url( $jersey->get_permalink() ); ?>" aria-label="<?php echo esc_attr( sprintf( __( 'View %s', 'skyyrose-flagship-2' ), $jersey->get_name() ) ); ?>">
						<img src="<?php echo esc_url( $front['card_src'] ?? $front['src'] ); ?>"
						<?php
						if ( ! empty( $front['srcset'] ) ) :
							?>
							srcset="<?php echo esc_attr( $front['srcset'] ); ?>" sizes="(max-width: 47.99em) 100vw, 60vw"<?php endif; ?> width="<?php echo absint( $front['card_width'] ?? $front['width'] ); ?>" height="<?php echo absint( $front['card_height'] ?? $front['height'] ); ?>" alt="<?php echo esc_attr( $front['alt'] ); ?>" loading="lazy" decoding="async">
						<span class="sr2-jersey-experience__label"><?php echo esc_html( sprintf( '%02d / %s', $index + 1, $jersey->get_name() ) ); ?></span>
					</a>
				</li>
				<?php endforeach; ?>
			</ol>
			<span class="sr2-jersey-experience__stamp" aria-hidden="true">SKYYROSE / BAY AREA</span>
			<div class="sr2-jersey-experience__controls" data-jersey-controls hidden>
				<button type="button" data-jersey-prev aria-label="<?php esc_attr_e( 'Previous jersey', 'skyyrose-flagship-2' ); ?>">←</button>
				<output data-jersey-position aria-live="polite"></output>
				<button type="button" data-jersey-next aria-label="<?php esc_attr_e( 'Next jersey', 'skyyrose-flagship-2' ); ?>">→</button>
			</div>
		</div>
