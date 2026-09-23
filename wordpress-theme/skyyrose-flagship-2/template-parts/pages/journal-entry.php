<?php
/**
 * One Journal entry in the editorial list: date, poster at its native ratio, title, excerpt.
 *
 * Posters keep their full frame (width/height from WordPress, height auto) so any
 * text set inside the artwork is never cropped.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$entry_categories = get_the_category();
$entry_meta       = get_the_date();
if ( ! empty( $entry_categories ) ) {
	$entry_meta .= ' · ' . $entry_categories[0]->name;
}
?>
<article <?php post_class( 'sr2-journal-entry' ); ?>>
	<p class="sr2-journal-entry__meta sr2-eyebrow"><?php echo esc_html( $entry_meta ); ?></p>
	<?php if ( has_post_thumbnail() ) : ?>
		<a class="sr2-journal-entry__media sr2-image-reveal" href="<?php the_permalink(); ?>" tabindex="-1" aria-hidden="true">
			<?php
			the_post_thumbnail(
				'large',
				array(
					'loading'  => 'lazy',
					'decoding' => 'async',
				)
			);
			?>
		</a>
	<?php endif; ?>
	<div class="sr2-journal-entry__copy">
		<h2 class="sr2-title-editorial"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
		<p><?php echo esc_html( wp_trim_words( get_the_excerpt(), 32 ) ); ?></p>
		<a class="sr2-editorial-link" href="<?php the_permalink(); ?>"><?php esc_html_e( 'Read the story', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a>
	</div>
</article>
