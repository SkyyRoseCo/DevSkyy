<?php
/**
 * On-model film: the founder-selected worn looks, one per world, as a full-width
 * band under the arrival. The original House of Roses loop controller gates the
 * motion; cards keep the class it targets for keyboard pausing.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$products    = is_array( $args['products'] ?? null ) ? $args['products'] : array();
$model_media = array(
	'sg-005'   => array(
		'src'        => 'images/home/on-model/signature-sg-005-512w.webp',
		'width'      => 512,
		'height'     => 768,
		'collection' => 'signature',
	),
	'br-004'   => array(
		'src'        => 'images/home/on-model/black-rose-br-004-512w.webp',
		'width'      => 512,
		'height'     => 768,
		'collection' => 'black-rose',
	),
	'lh-004'   => array(
		'src'        => 'images/home/on-model/love-hurts-lh-004-512w.webp',
		'width'      => 512,
		'height'     => 768,
		'collection' => 'love-hurts',
	),
	'kids-001' => array(
		'src'        => 'images/home/on-model/kids-capsule-kids-001-512w.webp',
		'width'      => 512,
		'height'     => 768,
		'collection' => 'kids-capsule',
	),
);
$collections = skyyrose2_collections();
$cards       = array();
foreach ( $model_media as $sku => $media ) {
	if ( isset( $products[ $sku ] ) && is_a( $products[ $sku ], 'WC_Product' ) ) {
		$cards[ $sku ] = $media;
	}
}
if ( ! $cards ) {
	return;
}
?>
<section class="sr2-editorial-film" aria-labelledby="sr2-editorial-film-title">
	<div class="sr2-editorial-film__head">
		<p class="sr2-eyebrow"><?php esc_html_e( 'On the body', 'skyyrose-flagship-2' ); ?></p>
		<h2 id="sr2-editorial-film-title" class="sr2-title-chapter"><?php esc_html_e( 'Four worlds, worn.', 'skyyrose-flagship-2' ); ?></h2>
	</div>
	<div class="sr2-editorial-film__strip" data-home-model-loop data-motion="static" role="group" aria-label="<?php esc_attr_e( 'Featured on-model looks', 'skyyrose-flagship-2' ); ?>">
		<div class="sr2-editorial-film__track">
			<?php foreach ( array( false, true ) as $is_copy ) : ?>
				<?php foreach ( $cards as $sku => $media ) : ?>
					<?php $product = $products[ $sku ]; ?>
					<?php if ( $is_copy ) : ?>
						<div class="sr2-editorial-hero__film-card sr2-editorial-film__card" data-loop-copy aria-hidden="true">
					<?php else : ?>
						<a class="sr2-editorial-hero__film-card sr2-editorial-film__card" href="<?php echo esc_url( $product->get_permalink() ); ?>" data-sku="<?php echo esc_attr( strtoupper( $sku ) ); ?>" data-collection="<?php echo esc_attr( $media['collection'] ); ?>">
					<?php endif; ?>
						<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $media['src'] ) ); ?>" width="<?php echo esc_attr( (string) $media['width'] ); ?>" height="<?php echo esc_attr( (string) $media['height'] ); ?>" sizes="(max-width: 47.99em) 68vw, clamp(14rem, 22vw, 20rem)" alt="<?php echo $is_copy ? '' : esc_attr( $product->get_name() ); ?>" loading="lazy" decoding="async">
						<span><small><?php echo esc_html( strtoupper( $sku ) ); ?> · <?php echo esc_html( $collections[ $media['collection'] ]['name'] ?? '' ); ?></small><b><?php echo esc_html( $product->get_name() ); ?></b></span>
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
