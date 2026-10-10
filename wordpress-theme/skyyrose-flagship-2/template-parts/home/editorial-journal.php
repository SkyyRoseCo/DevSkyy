<?php
/** Homepage journal band: two house films at their native 16:9, routing into the Lookbook and Journal. */
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
	<div class="sr2-editorial-journal__grid">
		<a class="sr2-editorial-journal__media sr2-image-reveal" href="<?php echo esc_url( $lookbook ); ?>"><img src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/skyyrose-tour-around-the-bay-poster.webp' ); ?>" width="1280" height="720" alt="" loading="lazy" decoding="async"><span><span><small><?php esc_html_e( 'Lookbook', 'skyyrose-flagship-2' ); ?></small><b><?php esc_html_e( 'Open the lookbook', 'skyyrose-flagship-2' ); ?></b></span><i aria-hidden="true">↗</i></span></a>
		<a class="sr2-editorial-journal__media sr2-image-reveal" href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'journal' ) ); ?>"><img src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/jersey-series-bart-poster.webp' ); ?>" width="1280" height="720" alt="" loading="lazy" decoding="async"><span><span><small><?php esc_html_e( 'Journal', 'skyyrose-flagship-2' ); ?></small><b><?php esc_html_e( 'Read the journal', 'skyyrose-flagship-2' ); ?></b></span><i aria-hidden="true">→</i></span></a>
	</div>
</section>
