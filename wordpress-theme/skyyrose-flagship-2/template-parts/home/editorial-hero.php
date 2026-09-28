<?php
/** House arrival: Oakland atmosphere, fashion portraiture, and restrained identity. */
defined( 'ABSPATH' ) || exit;
$collections = is_array( $args['collections'] ?? null ) ? $args['collections'] : array();
$shop_url = (string) ( $args['shop_url'] ?? '' );
?>
<section id="sr2-archive-arrival" class="sr2-house-arrival" data-house-motion aria-labelledby="sr2-archive-title">
	<div class="sr2-house-arrival__art" aria-hidden="true"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/house-oakland-atelier-20260928.webp' ) ); ?>" width="1672" height="941" alt="" fetchpriority="high" decoding="async"></div>
	<div class="sr2-house-arrival__shade" aria-hidden="true"></div>
	<div class="sr2-house-arrival__copy">
		<p class="sr2-house-kicker"><?php esc_html_e( 'Oakland, California / The house of SkyyRose', 'skyyrose-flagship-2' ); ?></p>
		<h1 id="sr2-archive-title"><?php esc_html_e( 'Rooted in the Town.', 'skyyrose-flagship-2' ); ?><em><?php esc_html_e( 'Made to be felt.', 'skyyrose-flagship-2' ); ?></em></h1>
		<p class="sr2-house-arrival__intro"><?php esc_html_e( 'Four worlds. One point of view. Discover the pieces, people, and places that make our house.', 'skyyrose-flagship-2' ); ?></p>
		<div class="sr2-house-arrival__actions"><a class="sr2-control sr2-control--primary" href="<?php echo esc_url( $shop_url ); ?>"><?php esc_html_e( 'Explore the collection', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a><a class="sr2-editorial-link" href="#sr2-archive-worlds"><?php esc_html_e( 'Find your world', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↓</span></a></div>
	</div>
	<aside class="sr2-house-arrival__editorial" aria-label="<?php esc_attr_e( 'From the house editorial', 'skyyrose-flagship-2' ); ?>">
		<div class="sr2-house-arrival__portraits">
			<a href="<?php echo esc_url( skyyrose2_collection_url( 'signature' ) ); ?>"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/home/on-model/signature-sg-005-512w.webp' ) ); ?>" width="512" height="768" alt="<?php esc_attr_e( 'Explore Signature', 'skyyrose-flagship-2' ); ?>" decoding="async"><span>Signature</span></a>
			<a href="<?php echo esc_url( skyyrose2_collection_url( 'black-rose' ) ); ?>"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/home/on-model/black-rose-br-004-512w.webp' ) ); ?>" width="512" height="768" alt="<?php esc_attr_e( 'Explore Black Rose', 'skyyrose-flagship-2' ); ?>" decoding="async"><span>Black Rose</span></a>
		</div>
		<p><?php esc_html_e( 'The city is our backdrop. The story is yours.', 'skyyrose-flagship-2' ); ?></p>
	</aside>
	<div class="sr2-house-arrival__foot"><span>SKYYROSE <i aria-hidden="true">/</i> EST. OAKLAND</span><button type="button" data-house-motion-toggle aria-pressed="false" hidden><?php esc_html_e( 'Pause atmosphere', 'skyyrose-flagship-2' ); ?></button></div>
</section>
