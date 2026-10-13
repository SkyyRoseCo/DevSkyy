<?php
/**
 * Template Name: Cinematic Prologue
 * Template Post Type: page
 *
 * Four vertical chapter panels. Hover/focus/tap widens one and plays its motion
 * verb; the page is complete with CSS and no JavaScript.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/*
 * Loaded here, not from functions.php: the chapter module exists only on this
 * template, so no existing hero, scene or product card can be affected.
 * Hooks register before get_header() fires wp_head / wp_enqueue_scripts.
 */
require_once SKYYROSE2_DIR . '/inc/cinematic-chapters.php';

get_header();
?>
<main id="primary" class="sr2-prologue" data-prologue>
	<h1 class="screen-reader-text"><?php echo esc_html( get_the_title() ); ?></h1>
	<div class="sr2-prologue__panels" role="list">
		<?php foreach ( skyyrose2_chapters() as $chapter ) : ?>
			<a class="sr2-panel" role="listitem" href="<?php echo esc_url( $chapter['url'] ); ?>" data-panel data-chapter="<?php echo esc_attr( $chapter['slug'] ); ?>" data-verb="<?php echo esc_attr( $chapter['verb'] ); ?>" style="--chapter-accent: <?php echo esc_attr( $chapter['accent'] ); ?>; --chapter-rgb: <?php echo esc_attr( $chapter['rgb'] ); ?>;">
				<span class="sr2-panel__light" aria-hidden="true"></span>
				<span class="sr2-panel__numeral" aria-hidden="true"><?php echo esc_html( $chapter['numeral'] ); ?></span>
				<span class="sr2-panel__name"><?php echo esc_html( $chapter['name'] ); ?></span>
				<?php if ( 'play' === $chapter['verb'] ) : ?>
					<span class="sr2-panel__start" data-chapter-iv-start><?php esc_html_e( 'Press Start', 'skyyrose-flagship-2' ); ?></span>
				<?php endif; ?>
			</a>
		<?php endforeach; ?>
	</div>
</main>
<?php
get_footer();
