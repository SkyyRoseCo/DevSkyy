<?php
/**
 * Accessible product quick-view dialog.
 *
 * This is progressive enhancement over the card's direct product link. The
 * payload comes from the live WooCommerce product card; the dialog never
 * invents price, stock, media, or collection facts.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;
?>
<dialog id="sr2-quick-view-dialog" class="sr2-quick-view" aria-labelledby="sr2-quick-view-title">
	<form method="dialog" class="sr2-quick-view__close-form">
		<button type="submit" class="sr2-quick-view__close" aria-label="<?php esc_attr_e( 'Close quick view', 'skyyrose-flagship-2' ); ?>">×</button>
	</form>
	<div class="sr2-quick-view__panel product">
		<div class="sr2-quick-view__media" data-quick-view-media hidden>
			<img alt="" width="900" height="1125" data-quick-view-image>
		</div>
		<div class="sr2-quick-view__copy">
			<p class="sr2-eyebrow" data-quick-view-collection><?php esc_html_e( 'Piece from the house', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr2-quick-view-title" data-sr2-type-motion="commerce" data-quick-view-name><?php esc_html_e( 'Choose a piece', 'skyyrose-flagship-2' ); ?></h2>
			<p class="sr2-quick-view__price" data-quick-view-price></p>
			<p class="sr2-quick-view__availability" data-quick-view-availability></p>
			<p class="sr2-quick-view__excerpt" data-quick-view-excerpt></p>
			<p class="sr2-quick-view__status" data-quick-view-status role="status" aria-live="polite"
				data-loading="<?php esc_attr_e( 'Loading available options…', 'skyyrose-flagship-2' ); ?>"
				data-submitting="<?php esc_attr_e( 'Adding your selection…', 'skyyrose-flagship-2' ); ?>"
				data-ready="<?php esc_attr_e( 'Choose your options and add to bag. Your selection will be confirmed on the product page.', 'skyyrose-flagship-2' ); ?>"
				data-error="<?php esc_attr_e( 'Open the piece to check options and availability.', 'skyyrose-flagship-2' ); ?>"></p>
			<div class="sr2-quick-view__purchase" data-quick-view-purchase></div>
			<div class="sr2-quick-view__actions">
				<a class="sr2-button sr2-button--fill" href="#" data-quick-view-url><?php esc_html_e( 'Enter the piece', 'skyyrose-flagship-2' ); ?> <span aria-hidden="true">↗</span></a>
				<button type="button" class="sr2-button" data-quick-view-dismiss><?php esc_html_e( 'Keep exploring', 'skyyrose-flagship-2' ); ?></button>
			</div>
		</div>
	</div>
</dialog>
