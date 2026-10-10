<?php
/**
 * Homepage arrival. One monument, one wordmark, one action; the early video
 * bootstrap and the recovery motion toggle keep their controller hooks.
 */
defined( 'ABSPATH' ) || exit;

$collections = is_array( $args['collections'] ?? null ) ? $args['collections'] : array();
$motion      = is_array( $args['motion'] ?? null ) ? $args['motion'] : array();
$shop_url    = (string) ( $args['shop_url'] ?? '' );
?>
<section id="sr2-archive-arrival" class="sr2-archive-scene sr2-editorial-hero sr2-arrival" data-recovery-hero aria-labelledby="sr2-archive-title">
	<div class="sr2-archive-scene__image sr2-editorial-hero__media sr2-arrival__media" aria-hidden="true">
		<picture>
			<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-640w.webp' ) ); ?>">
			<source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1024w.webp' ) ); ?>">
			<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1440w.webp' ) ); ?>" width="1440" height="810" alt="" fetchpriority="high" loading="eager" decoding="async">
		</picture>
		<?php if ( $motion ) : ?><video data-recovery-hero-video muted loop playsinline preload="none" aria-hidden="true"><source data-src="<?php echo esc_url( $motion['webm'] ); ?>" type="video/webm"><source data-src="<?php echo esc_url( $motion['mp4'] ); ?>" type="video/mp4"></video><?php endif; ?>
	</div>
	<div class="sr2-archive-scene__veil sr2-editorial-hero__veil sr2-arrival__veil" aria-hidden="true"></div>
	<div class="sr2-archive-scene__copy sr2-editorial-hero__copy sr2-arrival__copy">
		<p class="sr2-world-index"><?php esc_html_e( 'SkyyRose / Oakland, California', 'skyyrose-flagship-2' ); ?></p>
		<h1 id="sr2-archive-title" aria-label="<?php esc_attr_e( 'SkyyRose', 'skyyrose-flagship-2' ); ?>"><?php foreach ( str_split( 'SKYYROSE' ) as $letter_index => $letter ) : ?><span aria-hidden="true" style="--sr2-letter-delay: <?php echo esc_attr( (string) ( $letter_index * 28 ) ); ?>ms;"><?php echo esc_html( $letter ); ?></span><?php endforeach; ?></h1>
		<p class="sr2-archive-scene__intro"><?php esc_html_e( 'A house built by a father, named after a daughter, and rooted in The Town.', 'skyyrose-flagship-2' ); ?></p>
		<div class="sr2-archive-scene__actions sr2-arrival__actions"><a class="sr2-control sr2-control--primary" href="#sr2-archive-worlds"><?php esc_html_e( 'Enter the collection', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a><a class="sr2-control sr2-control--quiet" href="<?php echo esc_url( $shop_url ); ?>"><?php esc_html_e( 'Shop the house', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a></div>
	</div>
	<div class="sr2-arrival__utility"><button class="sr2-recovery-motion-toggle" type="button" data-recovery-motion-toggle hidden><?php esc_html_e( 'Pause motion', 'skyyrose-flagship-2' ); ?></button></div>
	<nav class="sr2-archive-scene__worlds sr2-editorial-hero__world-rail" aria-label="<?php esc_attr_e( 'Collection worlds', 'skyyrose-flagship-2' ); ?>">
		<?php foreach ( array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ) as $index => $slug ) : ?>
			<?php if ( empty( $collections[ $slug ] ) ) { continue; } ?>
			<a href="<?php echo esc_url( skyyrose2_collection_url( $slug ) ); ?>"><span aria-hidden="true"><?php echo esc_html( sprintf( '%02d', $index + 1 ) ); ?></span><b><?php echo esc_html( $collections[ $slug ]['name'] ); ?></b></a>
		<?php endforeach; ?>
	</nav>
</section>
