<?php
/** V2 wishlist page shell; the installed wishlist plugin owns list state. @package SkyyRoseFlagship2 */
defined( 'ABSPATH' ) || exit;
get_header();
while ( have_posts() ) : the_post();
?>
<main id="primary" tabindex="-1" class="sr2-generic-page sr2-c-service sr2-wishlist" data-sr2-route="service">
	<header class="sr2-generic-head">
		<p class="sr2-eyebrow"><?php esc_html_e( 'Saved pieces', 'skyyrose-flagship-2' ); ?></p>
		<h1><?php the_title(); ?></h1>
	</header>
	<div class="sr2-generic-page__body sr2-generic-page__body--wide">
		<div class="sr2-page-copy sr2-page-copy--generic sr2-wishlist__list"><?php the_content(); ?></div>
	</div>
</main>
<?php endwhile; get_footer(); ?>
