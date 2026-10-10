<?php
/**
 * Native Woo errors with valid list semantics and assertive announcements.
 *
 * Based on WooCommerce notices/error.php 8.6.0. Keep native notice escaping,
 * data attributes and class selectors. The alert contains a real list, so native
 * AJAX insertion retains urgent announcements without erasing list semantics.
 *
 * @package SkyyRoseFlagship2
 * @version 8.6.0
 */
defined( 'ABSPATH' ) || exit;
if ( ! $notices ) {
	return;
}
?>
<div class="woocommerce-error" role="alert">
	<ul class="sr2-notice-list" role="list">
	<?php foreach ( $notices as $notice ) : ?>
		<li<?php echo wc_get_notice_data_attr( $notice ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Native Woo data attributes. ?>>
			<?php echo wc_kses_notice( $notice['notice'] ); ?>
		</li>
	<?php endforeach; ?>
	</ul>
</div>
