<?php
/**
 * Collection arrival: the approved monument scene as the full-bleed structure,
 * the collection lockup as the title, one primary action and one quiet link.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;
$arrival              = $args['collection'];
$arrival_slug         = $args['slug'];
$arrival_presentation = $args['presentation'];
$arrival_motion       = skyyrose2_collection_hero_motion( $arrival_slug, $arrival['hero'] );
$arrival_lockup       = $arrival_presentation['lockup'] ?? array(
	'width'  => 1600,
	'height' => 540,
);
$arrival_lockup_class = 'sr2-arrival__lockup' . ( 'mark' === ( $arrival_lockup['shape'] ?? '' ) ? ' sr2-arrival__lockup--mark' : '' );
// From 48em the approved monument spells the name, so the lockup is hidden there and lazy
// (never fetched); below 48em the mobile crop carries no lettering and the lockup is the title.
$arrival_title_in_scene = ! empty( $arrival_presentation['title_in_scene'] );
?>
<header class="sr2-arrival sr2-world-arrival" data-recovery-hero data-collection="<?php echo esc_attr( $arrival_slug ); ?>" aria-labelledby="sr2-collection-title" style="--sr2-focal: <?php echo esc_attr( $arrival_presentation['focal'] ); ?>; --sr2-focal-mobile: <?php echo esc_attr( $arrival_presentation['focal_mobile'] ); ?>;">
	<div class="sr2-arrival__media">
		<picture>
			<?php
			if ( ! empty( $arrival['hero_mobile'] ) ) :
				?>
				<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $arrival['hero_mobile'] ) ); ?>"><?php endif; ?>
			<?php
			if ( ! empty( $arrival['hero_tablet'] ) ) :
				?>
				<source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $arrival['hero_tablet'] ) ); ?>"><?php endif; ?>
			<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $arrival['hero'] ) ); ?>" width="1440" height="810" alt="<?php echo esc_attr( $arrival_presentation['arrival_alt'] ); ?>" fetchpriority="high" loading="eager" decoding="async">
		</picture>
		<?php if ( $arrival_motion ) : ?>
			<video data-recovery-hero-video muted loop playsinline preload="none" aria-hidden="true"><source data-src="<?php echo esc_url( $arrival_motion['webm'] ); ?>" type="video/webm"><source data-src="<?php echo esc_url( $arrival_motion['mp4'] ); ?>" type="video/mp4"></video>
		<?php endif; ?>
	</div>
	<div class="sr2-arrival__veil" aria-hidden="true"></div>
	<div class="sr2-arrival__copy">
		<p class="sr2-eyebrow"><span aria-hidden="true"><?php echo esc_html( $arrival_presentation['ordinal'] ); ?> / </span><?php echo esc_html( $arrival['kicker'] ); ?></p>
		<h1 id="sr2-collection-title" class="sr2-world-arrival__title<?php echo $arrival_title_in_scene ? ' sr2-world-arrival__title--in-scene' : ''; ?>"><img class="<?php echo esc_attr( $arrival_lockup_class ); ?>" src="<?php echo esc_url( skyyrose2_sot_asset_uri( $arrival['lockup'] ) ); ?>" width="<?php echo esc_attr( (string) $arrival_lockup['width'] ); ?>" height="<?php echo esc_attr( (string) $arrival_lockup['height'] ); ?>" alt="" <?php echo $arrival_title_in_scene ? 'loading="lazy"' : 'loading="eager"'; ?> decoding="async"><span class="screen-reader-text"><?php echo esc_html( $arrival['name'] ); ?></span></h1>
		<p class="sr2-lede sr2-world-arrival__line"><?php echo esc_html( $arrival['line'] ); ?></p>
		<div class="sr2-arrival__actions">
			<a class="sr2-control sr2-control--primary" href="#shop"><?php echo esc_html( $arrival['hero_cta'] ); ?></a>
			<a class="sr2-editorial-link" href="#world"><?php echo esc_html( $arrival['world_cta'] ); ?><span aria-hidden="true">↓</span></a>
		</div>
	</div>
	<div class="sr2-arrival__utility"><button class="sr2-recovery-motion-toggle" type="button" data-recovery-motion-toggle hidden><?php esc_html_e( 'Pause motion', 'skyyrose-flagship-2' ); ?></button></div>
</header>