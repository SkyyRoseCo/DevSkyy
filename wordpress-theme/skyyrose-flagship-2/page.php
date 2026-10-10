<?php
/**
 * Marketplace page router.
 *
 * Every page route composes the shared editorial primitives: a quiet arrival
 * band or one full-bleed arrival, then a reading column or a 12-column form.
 * WooCommerce pages keep the native templates' headings and commerce wrappers.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$slug = sanitize_title( get_post_field( 'post_name', get_the_ID() ) );
	?>
	<main id="primary" tabindex="-1" class="sr2-page sr2-page--<?php echo esc_attr( $slug ); ?>">
		<?php if ( 'collections' === $slug ) : ?>
			<?php get_template_part( 'template-parts/collections/index' ); ?>
		<?php elseif ( 'pre-order' === $slug || 'preorder' === $slug ) : ?>
			<?php get_template_part( 'template-parts/v2-preorder' ); ?>
		<?php elseif ( 'about' === $slug ) : ?>
			<?php get_template_part( 'template-parts/v2-about' ); ?>
		<?php elseif ( 'contact' === $slug ) : ?>
			<?php get_template_part( 'template-parts/pages/contact' ); ?>
		<?php elseif ( function_exists( 'is_cart' ) && ( is_cart() || is_checkout() ) ) : ?>
			<?php the_content(); // Native Woo templates own their heading and commerce wrapper. ?>
		<?php else : ?>
			<?php
			$is_account = function_exists( 'is_account_page' ) && is_account_page();
			$is_service = in_array( $slug, array( 'shipping-returns', 'returns-exchanges', 'size-guide', 'faq' ), true );
			$managed_content = '';
			// Imported defaults are stored on the page; merchant edits remain authoritative.

			get_template_part(
				'template-parts/pages/service',
				null,
				array(
					'slug'            => $slug,
					'is_account'      => $is_account,
					'is_service'      => $is_service,
					'managed_content' => $managed_content,
				)
			);
			?>
		<?php endif; ?>
	</main>
	<?php
endwhile;

get_footer();
