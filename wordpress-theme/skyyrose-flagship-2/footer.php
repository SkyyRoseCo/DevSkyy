<?php defined( 'ABSPATH' ) || exit;
get_template_part( 'template-parts/commerce/quick-view' );
get_template_part( 'template-parts/commerce/size-guide-dialog' );
get_template_part( 'template-parts/commerce/search-dialog' );
// Keep the homepage character offline until its full motion rig is accepted.
if ( ! is_front_page() ) {
	get_template_part( 'template-parts/skyy-mascot' );
}
skyyrose2_bag_shell();
skyyrose2_footer();
wp_footer(); ?></body></html>
