<?php
/**
 * Four collection chapters. Each opens on its approved monument scene, then sets
 * the founder's words beside the garments. Product truth stays with WooCommerce.
 */
defined( 'ABSPATH' ) || exit;

$collections = is_array( $args['collections'] ?? null ) ? $args['collections'] : array();
$products    = is_array( $args['products'] ?? null ) ? $args['products'] : array();
// The arrival already shows the Bay Bridge salon; Black Rose opens here on its approved Lake Merritt alternate.
$chapter_scenes = array(
	'signature'    => array( 'base' => 'images/hero/responsive/signature-golden-gate-monuments-v2', 'focal' => '50% 45%' ),
	'black-rose'   => array( 'base' => 'images/hero/responsive/black-rose-lake-merritt-monument-v2', 'focal' => '50% 50%' ),
	'love-hurts'   => array( 'base' => 'images/hero/responsive/love-hurts-rose-aisle-monuments-v3', 'focal' => '50% 45%' ),
	'kids-capsule' => array( 'base' => 'images/hero/responsive/kids-capsule-heir-throne-v3', 'focal' => '50% 40%' ),
);
$lockups = array(
	'signature'  => array( 'width' => 1600, 'height' => 540 ),
	'black-rose' => array( 'width' => 1600, 'height' => 796 ),
	'love-hurts' => array( 'width' => 1600, 'height' => 1228 ),
);
$chapter = 0;
foreach ( $chapter_scenes as $slug => $scene ) :
	if ( empty( $collections[ $slug ] ) ) {
		continue;
	}
	$collection       = $collections[ $slug ];
	$chapter_products = array_values( $products[ $slug ] ?? array() );
	$title_id         = 'sr2-chapter-' . $slug . '-title';
	$chapter++;
	?>
<section<?php echo 1 === $chapter ? ' id="sr2-archive-worlds" tabindex="-1"' : ''; ?> class="sr2-editorial-collection sr2-chapter<?php echo 0 === $chapter % 2 ? ' sr2-chapter--flip' : ''; ?>" data-collection="<?php echo esc_attr( $slug ); ?>" aria-labelledby="<?php echo esc_attr( $title_id ); ?>">
	<figure class="sr2-editorial-collection__image sr2-chapter__scene sr2-image-reveal" style="--sr2-focal: <?php echo esc_attr( $scene['focal'] ); ?>;">
		<picture>
			<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $scene['base'] . '-640w.webp' ) ); ?>">
			<source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $scene['base'] . '-1024w.webp' ) ); ?>">
			<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $scene['base'] . '-1440w.webp' ) ); ?>" width="1440" height="810" alt="" loading="lazy" decoding="async">
		</picture>
	</figure>
	<div class="sr2-editorial-collection__band sr2-chapter__band">
		<div class="sr2-editorial-collection__copy sr2-chapter__copy">
			<p class="sr2-chapter__index sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( sprintf( '%02d', $chapter ) ); ?> / <?php echo esc_html( $collection['name'] ); ?></p>
			<?php if ( isset( $lockups[ $slug ], $collection['lockup'] ) ) : ?>
				<img class="sr2-editorial-collection__lockup" src="<?php echo esc_url( skyyrose2_sot_asset_uri( $collection['lockup'] ) ); ?>" width="<?php echo esc_attr( (string) $lockups[ $slug ]['width'] ); ?>" height="<?php echo esc_attr( (string) $lockups[ $slug ]['height'] ); ?>" alt="" loading="lazy" decoding="async">
			<?php endif; ?>
			<h2 id="<?php echo esc_attr( $title_id ); ?>" class="sr2-title-chapter"><?php echo esc_html( $collection['headline'] ); ?></h2>
			<p class="sr2-lede"><?php echo esc_html( $collection['line'] ); ?></p>
			<div class="sr2-editorial-collection__actions">
				<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_collection_url( $slug ) ); ?>"><?php echo esc_html( $collection['world_cta'] ); ?><span aria-hidden="true">→</span></a>
			</div>
		</div>
		<div class="sr2-editorial-collection__edit sr2-chapter__aside">
			<?php if ( $chapter_products ) : ?>
				<div class="sr2-editorial-collection__cards" data-count="<?php echo esc_attr( (string) count( $chapter_products ) ); ?>">
					<?php foreach ( $chapter_products as $index => $product ) : ?>
						<?php get_template_part( 'template-parts/commerce/product-card', null, array( 'product' => $product, 'index' => $index, 'heading_level' => 3, 'variant' => 'compact', 'media_priority' => 'lazy', 'frame' => false, 'sizes' => '(max-width: 29.99em) calc(100vw - 2rem), (max-width: 63.99em) calc((100vw - 3rem) / 2), 22vw' ) ); ?>
					<?php endforeach; ?>
				</div>
			<?php else : ?>
				<p class="sr2-archive-empty"><a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_collection_url( $slug ) ); ?>"><?php echo esc_html( $collection['hero_cta'] ); ?><span aria-hidden="true">↗</span></a></p>
			<?php endif; ?>
		</div>
	</div>
</section>
<?php endforeach; ?>
