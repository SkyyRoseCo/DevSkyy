<?php
/** House arrival: Oakland skyline and the SkyyRose monument. */
defined( 'ABSPATH' ) || exit;
$collections = is_array( $args['collections'] ?? null ) ? $args['collections'] : array();
$shop_url    = (string) ( $args['shop_url'] ?? '' );
?>
<section id="sr2-archive-arrival" class="sr2-house-arrival" data-house-motion aria-labelledby="sr2-archive-title">
	<div class="sr2-house-arrival__art"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/house-monument-20260928.webp' ) ); ?>" width="1672" height="941" alt="<?php esc_attr_e( 'A translucent SkyyRose monogram and rose sculpture overlooking Oakland at dusk.', 'skyyrose-flagship-2' ); ?>" fetchpriority="high" decoding="async"></div>
	<div class="sr2-house-arrival__shade" aria-hidden="true"></div>
	<div class="sr2-house-arrival__copy">
		<p class="sr2-house-kicker"><?php esc_html_e( 'Oakland, California / The house of SkyyRose', 'skyyrose-flagship-2' ); ?></p>
		<h1 id="sr2-archive-title"><?php esc_html_e( 'Rooted in the Town.', 'skyyrose-flagship-2' ); ?><em><?php esc_html_e( 'Made to be felt.', 'skyyrose-flagship-2' ); ?></em></h1>
		<p class="sr2-house-arrival__intro"><?php esc_html_e( 'Four worlds. One point of view. Discover the pieces, people, and places that make our house.', 'skyyrose-flagship-2' ); ?></p>
		<div class="sr2-house-arrival__actions"><a class="sr2-control sr2-control--primary" href="<?php echo esc_url( $shop_url ); ?>"><?php esc_html_e( 'Explore the collection', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a><a class="sr2-editorial-link" href="#sr2-archive-worlds"><?php esc_html_e( 'Find your world', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↓</span></a></div>
	</div>
	<div class="sr2-house-arrival__foot"><span>SKYYROSE <i aria-hidden="true">/</i> EST. OAKLAND</span><button type="button" data-house-motion-toggle aria-pressed="false" hidden><?php esc_html_e( 'Pause atmosphere', 'skyyrose-flagship-2' ); ?></button></div>
</section>
