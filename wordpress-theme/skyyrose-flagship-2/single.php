<?php
/**
 * Single V1/V2 WordPress post presentation.
 *
 * Left-aligned head, the poster at its native ratio (never cropped), then a 72ch
 * reading column that stays anchored to the left edge of the grid.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

get_header();
while ( have_posts() ) : the_post();
	$categories = get_the_category();
	?>
	<main id="primary" tabindex="-1" class="sr2-story" data-sr2-route="journal">
		<article <?php post_class( 'sr2-story__article' ); ?>>
			<header class="sr2-story__head sr2-band__head">
				<div>
					<p class="sr2-eyebrow"><?php echo esc_html( get_the_date() ); ?><?php if ( ! empty( $categories ) ) : ?> · <?php echo esc_html( $categories[0]->name ); ?><?php endif; ?></p>
					<h1 class="sr2-title-display"><?php the_title(); ?></h1>
				</div>
			</header>
			<?php if ( has_post_thumbnail() ) : ?>
				<figure class="sr2-story__hero sr2-image-reveal"><?php the_post_thumbnail( 'full', array( 'loading' => 'eager', 'fetchpriority' => 'high', 'decoding' => 'async' ) ); ?></figure>
			<?php endif; ?>
			<div class="sr2-page-grid sr2-story__grid">
				<div class="sr2-story__body sr2-page-grid__main entry-content"><?php the_content(); wp_link_pages( array( 'before' => '<nav class="sr2-pagination">', 'after' => '</nav>' ) ); ?></div>
			</div>
			<nav class="sr2-story__nav" aria-label="<?php esc_attr_e( 'Post navigation', 'skyyrose-flagship-2' ); ?>"><?php the_post_navigation( array( 'prev_text' => esc_html__( 'Previous story: %title', 'skyyrose-flagship-2' ), 'next_text' => esc_html__( 'Next story: %title', 'skyyrose-flagship-2' ) ) ); ?></nav>
			<?php if ( comments_open() || get_comments_number() ) : comments_template(); endif; ?>
		</article>
	</main>
<?php endwhile; get_footer(); ?>
