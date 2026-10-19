<?php
/** Homepage journal and source-bound Jersey Series reveal. */
defined( 'ABSPATH' ) || exit;

// Link only to pages visitors can open; a missing page leaves the CTA out rather than 404.
$journal_url  = skyyrose2_marketplace_page_live_url( 'journal' );
$lookbook_url = skyyrose2_published_page_permalink( 'lookbook' );
?>
<section class="sr2-editorial-journal sr2-band" aria-labelledby="sr2-editorial-journal-title">
	<div class="sr2-band__head">
		<div>
			<p class="sr2-eyebrow"><?php esc_html_e( 'The journal', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr2-editorial-journal-title" class="sr2-title-chapter"><?php esc_html_e( 'Ideas in motion.', 'skyyrose-flagship-2' ); ?></h2>
			<p class="sr2-lede"><?php esc_html_e( 'Notes from the house, the city, and the people shaping what comes next.', 'skyyrose-flagship-2' ); ?></p>
		</div>
		<?php if ( $journal_url ) : ?>
			<a class="sr2-editorial-link" href="<?php echo esc_url( $journal_url ); ?>"><?php esc_html_e( 'Read the journal', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a>
		<?php endif; ?>
	</div>
	<article class="sr2-jersey-experience" aria-labelledby="sr2-jersey-title">
		<?php get_template_part( 'template-parts/commerce/jersey-gallery' ); ?>
		<div class="sr2-jersey-experience__story">
			<p class="sr2-eyebrow"><?php esc_html_e( 'Jersey Series / Product fronts', 'skyyrose-flagship-2' ); ?></p>
			<h3 id="sr2-jersey-title"><?php esc_html_e( 'Tour Around the Bay.', 'skyyrose-flagship-2' ); ?></h3>
			<p class="sr2-lede"><?php esc_html_e( 'Explore each jersey and its own product page, from Oakland to San Jose.', 'skyyrose-flagship-2' ); ?></p>
			<?php if ( $lookbook_url ) : ?>
				<a class="sr2-editorial-link" href="<?php echo esc_url( $lookbook_url ); ?>"><?php esc_html_e( 'Explore the lookbook', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a>
			<?php endif; ?>
		</div>
	</article>
</section>
