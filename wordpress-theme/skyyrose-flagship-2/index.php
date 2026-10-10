<?php
/**
 * Primary fallback template: the Journal list when no more specific template applies.
 *
 * @package SkyyRose_Flagship_2
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<main id="primary" tabindex="-1" class="sr2-journal" data-sr2-route="journal">
	<header class="sr2-journal__hero sr2-band__head">
		<div>
			<p class="sr2-eyebrow"><?php esc_html_e( 'SkyyRose Journal', 'skyyrose-flagship-2' ); ?></p>
			<h1><?php echo esc_html( is_home() ? __( 'Journal', 'skyyrose-flagship-2' ) : wp_get_document_title() ); ?></h1>
		</div>
	</header>
	<?php if ( have_posts() ) : ?>
		<div class="sr2-journal__list" role="region" aria-label="<?php esc_attr_e( 'Journal entries', 'skyyrose-flagship-2' ); ?>">
			<?php while ( have_posts() ) : ?>
				<?php the_post(); ?>
				<?php get_template_part( 'template-parts/pages/journal-entry' ); ?>
			<?php endwhile; ?>
		</div>
		<nav class="sr2-pagination" aria-label="<?php esc_attr_e( 'Journal pages', 'skyyrose-flagship-2' ); ?>"><?php the_posts_pagination( array( 'mid_size' => 1 ) ); ?></nav>
	<?php else : ?>
		<?php get_template_part( 'template-parts/journal-press-fallback' ); ?>
	<?php endif; ?>
</main>
<?php
get_footer();
