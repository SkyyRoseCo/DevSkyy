<?php
/** Archive of posts, categories, and dates. @package SkyyRoseFlagship2 */
defined( 'ABSPATH' ) || exit;
get_header();
?>
<main id="primary" class="sr2-journal" data-sr2-route="journal">
	<header class="sr2-journal__hero sr2-band__head">
		<div>
			<p class="sr2-eyebrow"><?php esc_html_e( 'SkyyRose Journal', 'skyyrose-flagship-2' ); ?></p>
			<h1><?php the_archive_title(); ?></h1>
			<?php the_archive_description( '<p class="sr2-lede">', '</p>' ); ?>
		</div>
	</header>
	<?php if ( have_posts() ) : ?>
		<div class="sr2-journal__list" role="region" aria-label="<?php esc_attr_e( 'Journal entries', 'skyyrose-flagship-2' ); ?>">
			<?php while ( have_posts() ) : the_post(); ?>
				<?php get_template_part( 'template-parts/pages/journal-entry' ); ?>
			<?php endwhile; ?>
		</div>
		<nav class="sr2-pagination" aria-label="<?php esc_attr_e( 'Archive pages', 'skyyrose-flagship-2' ); ?>"><?php the_posts_pagination(); ?></nav>
	<?php else : ?>
		<p class="sr2-empty"><?php esc_html_e( 'No stories were found.', 'skyyrose-flagship-2' ); ?></p>
	<?php endif; ?>
</main>
<?php get_footer(); ?>
