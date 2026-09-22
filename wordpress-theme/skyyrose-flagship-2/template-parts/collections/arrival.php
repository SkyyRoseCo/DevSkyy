<?php
/** Collection identity and its existing full-frame monument. @package SkyyRoseFlagship2 */
defined( 'ABSPATH' ) || exit;
$arrival              = $args['collection'];
$arrival_presentation = $args['presentation'];
$arrival_media        = skyyrose2_collection_arrival_media( $arrival );
$arrival_motion       = skyyrose2_collection_hero_motion( $args['slug'], $arrival['hero'] );
?>
<header data-recovery-hero class="sr2-world-arrival sr2-world-arrival--cinematic">
	<div class="sr2-world-arrival__identity">
		<p class="sr2-world-index"><span aria-hidden="true"><?php echo esc_html( $arrival_presentation['ordinal'] ); ?> / </span><?php echo esc_html( $arrival['kicker'] ); ?></p>
		<h1><?php echo esc_html( $arrival['name'] ); ?></h1>
		<p class="sr2-world-arrival__line"><?php echo esc_html( $arrival['headline'] ); ?></p>
		<div class="sr2-world-arrival__actions">
			<?php if ( 'kids-capsule' === $args['slug'] ) : ?>
				<a class="sr2-control sr2-control--primary" href="<?php echo esc_url( skyyrose2_immersive_url( $args['slug'] ) ); ?>"><?php esc_html_e( 'Explore world', 'skyyrose-flagship-2' ); ?></a>
				<a class="sr2-control sr2-control--primary" href="#shop"><?php esc_html_e( 'Shop collection', 'skyyrose-flagship-2' ); ?></a>
				<a class="sr2-world-text-link" href="#origin"><?php esc_html_e( 'Read the story', 'skyyrose-flagship-2' ); ?> <span aria-hidden="true">↓</span></a>
			<?php else : ?>
			<a class="sr2-control sr2-control--primary" href="#shop"><?php echo esc_html( $arrival['hero_cta'] ); ?></a>
			<a class="sr2-world-text-link" href="#origin"><?php echo esc_html( $arrival['world_cta'] ); ?> <span aria-hidden="true">↓</span></a>
			<?php endif; ?>
		</div>
	</div>
	<figure class="sr2-world-arrival__monument"><div class="sr2-recovery-hero-media">
		<img src="<?php echo esc_url( $arrival_media['src'] ); ?>" srcset="<?php echo esc_attr( $arrival_media['srcset'] ); ?>" sizes="<?php echo esc_attr( $arrival_media['sizes'] ); ?>" width="1440" height="810" alt="<?php echo esc_attr( $arrival_presentation['arrival_alt'] ); ?>" fetchpriority="high" loading="eager" decoding="async">
		<?php
		if ( $arrival_motion ) :
			?>
			<video data-recovery-hero-video muted loop playsinline preload="none" aria-hidden="true"><source data-src="<?php echo esc_url( $arrival_motion['webm'] ); ?>" type="video/webm"><source data-src="<?php echo esc_url( $arrival_motion['mp4'] ); ?>" type="video/mp4"></video><?php endif; ?>
		<button class="sr2-recovery-motion-toggle" type="button" data-recovery-motion-toggle hidden><?php esc_html_e( 'Pause motion', 'skyyrose-flagship-2' ); ?></button></div>
		<figcaption><span><?php echo esc_html( $arrival_presentation['location'] ); ?></span><span><?php echo esc_html( $arrival['name'] ); ?></span></figcaption>
	</figure>
</header>
