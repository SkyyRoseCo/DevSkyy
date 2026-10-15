<?php
/**
 * Four collection chapters. Each opens on its approved monument scene, then sets
 * the founder's words beside the garments. Product truth stays with WooCommerce.
 */
defined( 'ABSPATH' ) || exit;

$collections = is_array( $args['collections'] ?? null ) ? $args['collections'] : array();
$products    = is_array( $args['products'] ?? null ) ? $args['products'] : array();
// Use the destination collection's own hero and approved motion binding.
$chapter_slugs = array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' );
$lockups = array(
	'signature'  => array( 'width' => 1600, 'height' => 540 ),
	'black-rose' => array( 'width' => 1600, 'height' => 796 ),
	'love-hurts' => array( 'width' => 1600, 'height' => 1228 ),
);
$chapter = 0;
foreach ( $chapter_slugs as $slug ) :
	if ( empty( $collections[ $slug ] ) ) {
		continue;
	}
	$collection       = $collections[ $slug ];
	$chapter_motion   = skyyrose2_collection_hero_motion( $slug, $collection['hero'] );
	$chapter_products = array_values( $products[ $slug ] ?? array() );
	$title_id         = 'sr2-chapter-' . $slug . '-title';
	$chapter++;
	?>
<section<?php echo 1 === $chapter ? ' id="sr2-archive-worlds" tabindex="-1"' : ''; ?> class="sr2-editorial-collection sr2-chapter<?php echo 0 === $chapter % 2 ? ' sr2-chapter--flip' : ''; ?>" data-collection="<?php echo esc_attr( $slug ); ?>" aria-labelledby="<?php echo esc_attr( $title_id ); ?>">
	<figure class="sr2-editorial-collection__image sr2-chapter__scene sr2-home-motion" data-home-motion>
		<picture>
			<?php if ( ! empty( $collection['hero_mobile'] ) ) : ?>
				<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $collection['hero_mobile'] ) ); ?>">
			<?php endif; ?>
			<?php if ( ! empty( $collection['hero_tablet'] ) ) : ?>
				<source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $collection['hero_tablet'] ) ); ?>">
			<?php endif; ?>
			<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $collection['hero'] ) ); ?>" width="1440" height="810" alt="" loading="lazy" decoding="async">
		</picture>
		<?php if ( $chapter_motion ) : ?>
			<video id="<?php echo esc_attr( 'sr2-home-film-' . $slug ); ?>" muted loop playsinline preload="none" aria-hidden="true"><source data-src="<?php echo esc_url( $chapter_motion['webm'] ); ?>" type="video/webm"><source data-src="<?php echo esc_url( $chapter_motion['mp4'] ); ?>" type="video/mp4"></video>
			<button class="sr2-home-motion__toggle" type="button" aria-controls="<?php echo esc_attr( 'sr2-home-film-' . $slug ); ?>" data-home-motion-toggle hidden><?php esc_html_e( 'Play motion', 'skyyrose-flagship-2' ); ?></button>
		<?php endif; ?>
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
