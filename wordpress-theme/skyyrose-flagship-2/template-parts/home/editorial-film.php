<?php
/**
 * On-model film: founder-selected worn looks with approved product fronts as a
 * full-width band under the arrival. The original House of Roses loop controller
 * gates motion; cards keep the class it targets for keyboard pausing.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$products    = is_array( $args['products'] ?? null ) ? $args['products'] : array();
$collections = skyyrose2_collections();
$cards       = array();
foreach ( $products as $sku => $product ) {
	if ( ! is_a( $product, 'WC_Product' ) ) {
		continue;
	}
	$front = skyyrose2_approved_card_front( $product );
	if ( ! $front ) {
		continue;
	}
	$record        = skyyrose2_product_presentation( $product );
	$collection    = isset( $record['collection'] ) ? sanitize_title( $record['collection'] ) : '';
	$cards[ $sku ] = array(
		'product'    => $product,
		'front'      => $front,
		'collection' => $collection,
	);
}
if ( ! $cards ) {
	return;
}
?>
<section class="sr2-editorial-film" aria-labelledby="sr2-editorial-film-title">
	<div class="sr2-editorial-film__head">
		<p class="sr2-eyebrow"><?php esc_html_e( 'On the body', 'skyyrose-flagship-2' ); ?></p>
		<h2 id="sr2-editorial-film-title" class="sr2-title-chapter"><?php esc_html_e( 'The house, worn.', 'skyyrose-flagship-2' ); ?></h2>
	</div>
	<div class="sr2-editorial-film__strip" data-home-model-loop data-motion="static" role="group" aria-label="<?php esc_attr_e( 'Featured on-model looks', 'skyyrose-flagship-2' ); ?>">
		<div class="sr2-editorial-film__track">
			<?php foreach ( array( false, true ) as $is_copy ) : ?>
				<?php foreach ( $cards as $sku => $card ) : ?>
					<?php
					$product = $card['product'];
					$front   = $card['front'];
					?>
					<?php if ( $is_copy ) : ?>
						<div class="sr2-editorial-hero__film-card sr2-editorial-film__card" data-loop-copy aria-hidden="true">
					<?php else : ?>
						<a class="sr2-editorial-hero__film-card sr2-editorial-film__card" href="<?php echo esc_url( $product->get_permalink() ); ?>" data-sku="<?php echo esc_attr( strtoupper( $sku ) ); ?>" data-collection="<?php echo esc_attr( $card['collection'] ); ?>">
					<?php endif; ?>
						<img src="<?php echo esc_url( $front['card_src'] ?? $front['src'] ); ?>" srcset="<?php echo esc_attr( $front['srcset'] ?? '' ); ?>" sizes="(max-width: 47.99em) min(15rem, 68vw), clamp(14rem, 22vw, 20rem)" width="<?php echo esc_attr( (string) $front['width'] ); ?>" height="<?php echo esc_attr( (string) $front['height'] ); ?>" alt="<?php echo $is_copy ? '' : esc_attr( $front['alt'] ); ?>" loading="lazy" decoding="async">
						<span><small><?php echo esc_html( strtoupper( $sku ) ); ?> · <?php echo esc_html( $collections[ $card['collection'] ]['name'] ?? '' ); ?></small><b><?php echo esc_html( $product->get_name() ); ?></b></span>
					<?php
					if ( $is_copy ) :
						?>
						</div>
						<?php
else :
	?>
						</a><?php endif; ?>
				<?php endforeach; ?>
			<?php endforeach; ?>
		</div>
		<button class="sr2-editorial-film__toggle" type="button" data-home-model-toggle aria-pressed="false" hidden><?php esc_html_e( 'Pause product film', 'skyyrose-flagship-2' ); ?></button>
	</div>
</section>
