<?php
/** Branded recovery route: one full-bleed scene and one way back. @package SkyyRoseFlagship2 */
defined( 'ABSPATH' ) || exit;
get_header();
$not_found_scene = 'images/hero/responsive/black-rose-lake-merritt-monument-v2';
?>
<main id="primary" tabindex="-1" class="sr2-not-found" data-sr2-route="service">
	<section class="sr2-arrival sr2-not-found__arrival" data-collection="black-rose" aria-labelledby="sr2-page-title">
		<div class="sr2-arrival__media" style="--sr2-focal: 50% 55%;">
			<picture>
				<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $not_found_scene . '-640w.webp' ) ); ?>">
				<source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $not_found_scene . '-1024w.webp' ) ); ?>">
				<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $not_found_scene . '-1440w.webp' ) ); ?>" width="1440" height="810" alt="" fetchpriority="high" decoding="async">
			</picture>
		</div>
		<div class="sr2-arrival__veil" aria-hidden="true"></div>
		<div class="sr2-arrival__copy">
			<p class="sr2-eyebrow"><?php esc_html_e( '404', 'skyyrose-flagship-2' ); ?></p>
			<h1 id="sr2-page-title" class="sr2-title-display"><?php esc_html_e( 'This chapter moved.', 'skyyrose-flagship-2' ); ?></h1>
			<p class="sr2-lede"><?php esc_html_e( 'The house is still here. Find a collection, a piece, or a story.', 'skyyrose-flagship-2' ); ?></p>
			<div class="sr2-arrival__actions"><a class="sr2-control sr2-control--primary" href="<?php echo esc_url( home_url( '/collections/' ) ); ?>"><?php esc_html_e( 'Enter the collections', 'skyyrose-flagship-2' ); ?></a></div>
		</div>
	</section>
</main>
<?php get_footer(); ?>
