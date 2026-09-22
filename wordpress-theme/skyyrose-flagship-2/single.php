<?php
/**
 * Single V1/V2 WordPress post presentation.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

get_header();
while ( have_posts() ) : the_post();
	$categories = get_the_category();
	?>
	<main id="primary" class="sr2-story" data-sr2-route="journal">
		<article <?php post_class( 'sr2-story__article' ); ?>>
			<?php if ( has_post_thumbnail() ) : ?><div class="sr2-story__hero"><?php the_post_thumbnail( 'full', array( 'loading' => 'eager', 'fetchpriority' => 'high', 'decoding' => 'async' ) ); ?></div><?php endif; ?>
			<header class="sr2-story__head"><p class="sr2-eyebrow"><?php echo esc_html( get_the_date() ); ?><?php if ( ! empty( $categories ) ) : ?> · <?php echo esc_html( $categories[0]->name ); ?><?php endif; ?></p><h1><?php the_title(); ?></h1></header>
			<div class="sr2-story__body entry-content"><?php the_content(); wp_link_pages( array( 'before' => '<nav class="sr2-pagination">', 'after' => '</nav>' ) ); ?></div>
			<nav class="sr2-story__nav" aria-label="<?php esc_attr_e( 'Post navigation', 'skyyrose-flagship-2' ); ?>"><?php the_post_navigation( array( 'prev_text' => esc_html__( 'Previous story: %title', 'skyyrose-flagship-2' ), 'next_text' => esc_html__( 'Next story: %title', 'skyyrose-flagship-2' ) ) ); ?></nav>
			<?php if ( comments_open() || get_comments_number() ) : comments_template(); endif; ?>
		</article>
	</main>
<?php endwhile; get_footer(); ?>
