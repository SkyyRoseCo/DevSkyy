<?php
/**
 * SkyyRose Journal archive. Uses the existing WordPress posts and media.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<main id="primary" class="sr2-journal" data-sr2-route="journal">
	<header class="sr2-journal__hero">
		<p class="sr2-eyebrow"><?php esc_html_e( 'From the House', 'skyyrose-flagship-2' ); ?></p>
		<h1><?php echo esc_html( single_post_title( '', false ) ?: __( 'Journal', 'skyyrose-flagship-2' ) ); ?></h1>
		<p><?php esc_html_e( 'Dispatches, campaigns, and the faces behind SkyyRose.', 'skyyrose-flagship-2' ); ?></p>
	</header>
	<?php if ( have_posts() ) : ?>
		<section class="sr2-journal__grid" aria-label="<?php esc_attr_e( 'Journal entries', 'skyyrose-flagship-2' ); ?>">
			<?php while ( have_posts() ) : the_post(); ?>
				<article <?php post_class( 'sr2-journal-card' ); ?>>
					<?php if ( has_post_thumbnail() ) : ?>
						<a class="sr2-journal-card__media" href="<?php the_permalink(); ?>" aria-label="<?php echo esc_attr( get_the_title() ); ?>">
							<?php the_post_thumbnail( 'large', array( 'loading' => 'lazy', 'decoding' => 'async' ) ); ?>
						</a>
					<?php endif; ?>
					<div class="sr2-journal-card__copy"><p class="sr2-eyebrow"><?php echo esc_html( get_the_date() ); ?></p><h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2><p><?php echo esc_html( wp_trim_words( get_the_excerpt(), 26 ) ); ?></p><a class="sr2-text-link" href="<?php the_permalink(); ?>"><?php esc_html_e( 'Read the story', 'skyyrose-flagship-2' ); ?> <span aria-hidden="true">↗</span></a></div>
				</article>
			<?php endwhile; ?>
		</section>
		<nav class="sr2-pagination" aria-label="<?php esc_attr_e( 'Journal pages', 'skyyrose-flagship-2' ); ?>"><?php the_posts_pagination( array( 'mid_size' => 1 ) ); ?></nav>
	<?php else : ?>
		<?php get_template_part( 'template-parts/journal-press-fallback' ); ?>
	<?php endif; ?>
</main>
<?php get_footer(); ?>
