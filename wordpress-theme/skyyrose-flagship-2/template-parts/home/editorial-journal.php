<?php
/** Homepage journal/media strip; routes into the maintained Journal and Lookbook. */
defined( 'ABSPATH' ) || exit;
?>
<section class="sr2-editorial-journal" aria-labelledby="sr2-editorial-journal-title">
	<figure class="sr2-editorial-journal__still"><img src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/skyyrose-tour-around-the-bay-poster.webp' ); ?>" width="960" height="640" alt="<?php esc_attr_e( 'SkyyRose lookbook detail', 'skyyrose-flagship-2' ); ?>" loading="lazy" decoding="async"></figure>
	<div class="sr2-editorial-journal__copy"><p class="sr2-world-index"><?php esc_html_e( 'The journal', 'skyyrose-flagship-2' ); ?></p><h2 id="sr2-editorial-journal-title"><?php esc_html_e( 'Ideas in motion.', 'skyyrose-flagship-2' ); ?></h2><p><?php esc_html_e( 'Notes from the house, the city, and the people shaping what comes next.', 'skyyrose-flagship-2' ); ?></p><a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'journal' ) ); ?>"><?php esc_html_e( 'Read the journal', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a></div>
	<a class="sr2-editorial-journal__media" href="<?php echo esc_url( get_permalink( get_page_by_path( 'lookbook' ) ) ?: skyyrose2_marketplace_page_url( 'journal' ) ); ?>"><img src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/jersey-series-bart-poster.webp' ); ?>" width="960" height="640" alt="<?php esc_attr_e( 'Open the SkyyRose lookbook', 'skyyrose-flagship-2' ); ?>" loading="lazy" decoding="async"><span><?php esc_html_e( 'Open lookbook', 'skyyrose-flagship-2' ); ?> <b aria-hidden="true">↗</b></span></a>
</section>
