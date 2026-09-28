<?php
/**
 * Homepage journal band: two house films at their native 16:9.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$lookbook = get_page_by_path( 'lookbook' );
$lookbook = $lookbook ? get_permalink( $lookbook ) : skyyrose2_marketplace_page_url( 'journal' );
?>
<section class="sr2-editorial-journal sr2-band" aria-labelledby="sr2-editorial-journal-title">
	<div class="sr2-band__head">
		<div>
			<p class="sr2-eyebrow"><?php esc_html_e( 'The journal', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr2-editorial-journal-title" class="sr2-title-chapter"><?php esc_html_e( 'Ideas in motion.', 'skyyrose-flagship-2' ); ?></h2>
			<p class="sr2-lede"><?php esc_html_e( 'Notes from the house, the city, and the people shaping what comes next.', 'skyyrose-flagship-2' ); ?></p>
		</div>
		<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'journal' ) ); ?>"><?php esc_html_e( 'Read the journal', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a>
	</div>
	<article class="sr2-jersey-experience" aria-labelledby="sr2-jersey-title">
		<div class="sr2-jersey-experience__screen sr2-home-motion" data-home-motion>
			<img src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/skyyrose-tour-around-the-bay-poster.webp' ); ?>" width="1280" height="720" alt="<?php esc_attr_e( 'Tour Around the Bay — the SkyyRose Jersey Series film', 'skyyrose-flagship-2' ); ?>" loading="lazy" decoding="async">
			<video id="sr2-jersey-film" muted loop playsinline preload="none" aria-hidden="true"><source data-src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/skyyrose-tour-around-the-bay.webm' ); ?>" type="video/webm"><source data-src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/skyyrose-tour-around-the-bay.mp4' ); ?>" type="video/mp4"></video>
			<span class="sr2-jersey-experience__stamp" aria-hidden="true">SKYYROSE / BAY AREA</span>
			<button class="sr2-home-motion__toggle" type="button" aria-controls="sr2-jersey-film" data-home-motion-toggle hidden><?php esc_html_e( 'Play motion', 'skyyrose-flagship-2' ); ?></button>
		</div>
		<div class="sr2-jersey-experience__story">
			<p class="sr2-eyebrow"><?php esc_html_e( 'Jersey Series / A house film', 'skyyrose-flagship-2' ); ?></p>
			<h3 id="sr2-jersey-title"><?php esc_html_e( 'Tour Around the Bay.', 'skyyrose-flagship-2' ); ?></h3>
			<p class="sr2-lede"><?php esc_html_e( 'The city sets the scene. Step into the Jersey Series, then explore the house lookbook.', 'skyyrose-flagship-2' ); ?></p>
			<a class="sr2-editorial-link" href="<?php echo esc_url( $lookbook ); ?>"><?php esc_html_e( 'Explore the lookbook', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a>
		</div>
	</article>
</section>
