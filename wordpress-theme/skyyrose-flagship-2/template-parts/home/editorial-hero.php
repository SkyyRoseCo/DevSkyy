<?php
/** Homepage editorial hero; preserves the early video bootstrap and concierge mount. */
defined( 'ABSPATH' ) || exit;

$collections = is_array( $args['collections'] ?? null ) ? $args['collections'] : array();
$motion      = is_array( $args['motion'] ?? null ) ? $args['motion'] : array();
$shop_url    = (string) ( $args['shop_url'] ?? '' );
$products    = is_array( $args['products'] ?? null ) ? $args['products'] : array();
$model_media = array(
	'sg-005' => 'images/home/on-model/signature-sg-005-512w.webp',
	'br-004' => 'images/home/on-model/black-rose-br-004-512w.webp',
	'lh-004' => 'images/home/on-model/love-hurts-lh-004-512w.webp',
);
?>
<section id="sr2-archive-arrival" class="sr2-archive-scene sr2-editorial-hero" data-recovery-hero aria-labelledby="sr2-archive-title">
	<div class="sr2-archive-scene__image sr2-editorial-hero__media" aria-hidden="true">
		<picture>
			<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-640w.webp' ) ); ?>">
			<source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1024w.webp' ) ); ?>">
			<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1440w.webp' ) ); ?>" width="1440" height="810" alt="" fetchpriority="high" loading="eager" decoding="async">
		</picture>
		<?php if ( $motion ) : ?><video data-recovery-hero-video muted loop playsinline preload="none" aria-hidden="true"><source data-src="<?php echo esc_url( $motion['webm'] ); ?>" type="video/webm"><source data-src="<?php echo esc_url( $motion['mp4'] ); ?>" type="video/mp4"></video><?php endif; ?>
	</div>
	<div class="sr2-archive-scene__veil sr2-editorial-hero__veil" aria-hidden="true"></div>
	<?php if ( count( $products ) === count( $model_media ) ) : ?>
		<div class="sr2-editorial-hero__film" data-home-model-loop data-motion="static" role="group" aria-label="<?php esc_attr_e( 'Featured on-model looks', 'skyyrose-flagship-2' ); ?>">
			<div class="sr2-editorial-hero__film-track">
				<?php foreach ( array( false, true ) as $is_copy ) : ?>
					<?php foreach ( $model_media as $sku => $media_path ) : ?>
						<?php $product = $products[ $sku ] ?? null; ?>
						<?php if ( ! is_a( $product, 'WC_Product' ) ) { continue; } ?>
						<?php if ( $is_copy ) : ?>
							<div class="sr2-editorial-hero__film-card" data-loop-copy aria-hidden="true">
						<?php else : ?>
							<a class="sr2-editorial-hero__film-card" href="<?php echo esc_url( $product->get_permalink() ); ?>" data-sku="<?php echo esc_attr( strtoupper( $sku ) ); ?>">
						<?php endif; ?>
							<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $media_path ) ); ?>" width="512" height="768" alt="<?php echo $is_copy ? '' : esc_attr( $product->get_name() ); ?>" loading="<?php echo $is_copy ? 'lazy' : 'eager'; ?>"<?php echo ! $is_copy && 'sg-005' === $sku ? ' fetchpriority="high"' : ''; ?> decoding="async">
							<span><small><?php echo esc_html( strtoupper( $sku ) ); ?></small><b><?php echo esc_html( $product->get_name() ); ?></b></span>
						<?php if ( $is_copy ) : ?></div><?php else : ?></a><?php endif; ?>
					<?php endforeach; ?>
				<?php endforeach; ?>
			</div>
			<button class="sr2-editorial-hero__film-toggle" type="button" data-home-model-toggle aria-pressed="false" hidden><?php esc_html_e( 'Pause product film', 'skyyrose-flagship-2' ); ?></button>
		</div>
	<?php endif; ?>
	<div class="sr2-archive-scene__copy sr2-editorial-hero__copy">
		<p class="sr2-world-index"><?php esc_html_e( 'SkyyRose / Oakland, California', 'skyyrose-flagship-2' ); ?></p>
		<h1 id="sr2-archive-title" aria-label="<?php esc_attr_e( 'SkyyRose', 'skyyrose-flagship-2' ); ?>">
			<span aria-hidden="true" style="--sr2-letter-delay: 0ms;">S</span><span aria-hidden="true" style="--sr2-letter-delay: 28ms;">K</span><span aria-hidden="true" style="--sr2-letter-delay: 56ms;">Y</span><span aria-hidden="true" style="--sr2-letter-delay: 84ms;">Y</span><span aria-hidden="true" style="--sr2-letter-delay: 112ms;">R</span><span aria-hidden="true" style="--sr2-letter-delay: 140ms;">O</span><span aria-hidden="true" style="--sr2-letter-delay: 168ms;">S</span><span aria-hidden="true" style="--sr2-letter-delay: 196ms;">E</span>
		</h1>
		<p class="sr2-archive-scene__intro"><?php esc_html_e( 'A house built by a father, named after a daughter, and rooted in The Town.', 'skyyrose-flagship-2' ); ?></p>
		<div class="sr2-archive-scene__actions"><a class="sr2-control sr2-control--primary" href="#sr2-archive-worlds"><?php esc_html_e( 'Enter the collection', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a><a class="sr2-control sr2-control--secondary" href="<?php echo esc_url( $shop_url ); ?>"><?php esc_html_e( 'Shop the house', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a></div>
	</div>
	<div id="skyy-hero-stage" class="sr2-archive-scene__concierge" role="region" aria-label="<?php esc_attr_e( 'Skyy, your house concierge', 'skyyrose-flagship-2' ); ?>">
		<noscript><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/mascot/skyy-canonical-v2-512w.webp' ) ); ?>" width="160" height="240" alt="<?php esc_attr_e( 'Skyy, the house concierge', 'skyyrose-flagship-2' ); ?>" loading="lazy"><a href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'contact' ) ); ?>"><?php esc_html_e( 'Ask Skyy / Client Services', 'skyyrose-flagship-2' ); ?></a></noscript>
	</div>
	<button class="sr2-recovery-motion-toggle" type="button" data-recovery-motion-toggle hidden><?php esc_html_e( 'Pause motion', 'skyyrose-flagship-2' ); ?></button>
	<nav class="sr2-archive-scene__worlds sr2-editorial-hero__world-rail" aria-label="<?php esc_attr_e( 'Collection worlds', 'skyyrose-flagship-2' ); ?>">
		<?php foreach ( array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ) as $index => $slug ) : ?>
			<?php if ( empty( $collections[ $slug ] ) ) { continue; } ?>
			<a href="<?php echo esc_url( skyyrose2_collection_url( $slug ) ); ?>"><span aria-hidden="true"><?php echo esc_html( sprintf( '%02d', $index + 1 ) ); ?></span><b><?php echo esc_html( $collections[ $slug ]['name'] ); ?></b></a>
		<?php endforeach; ?>
	</nav>
</section>
