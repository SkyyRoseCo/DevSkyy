<?php
/**
 * Product-level fit and size guide dialog.
 *
 * Product measurements remain owned by the WooCommerce product record. This
 * dialog gives shoppers a fast, accessible decision aid without inventing
 * measurements or replacing the product page's authoritative fit notes.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;
?>
<dialog id="sr2-size-guide-dialog" class="sr2-size-guide-dialog" aria-labelledby="sr2-size-guide-title">
	<div class="sr2-size-guide-dialog__panel">
		<div class="sr2-dialog-head sr2-size-guide-dialog__head">
			<p class="sr2-index"><?php esc_html_e( 'SkyyRose / Fit + size guide', 'skyyrose-flagship-2' ); ?></p>
			<form method="dialog" class="sr2-size-guide-dialog__close-form">
				<button type="submit" class="sr2-icon-button sr2-size-guide-dialog__close" aria-label="<?php esc_attr_e( 'Close fit and size guide', 'skyyrose-flagship-2' ); ?>">×</button>
			</form>
		</div>
		<h2 id="sr2-size-guide-title"><?php esc_html_e( 'Choose the silhouette you want to live in.', 'skyyrose-flagship-2' ); ?></h2>
		<ol class="sr2-size-guide-dialog__steps">
			<li><span class="sr2-eyebrow sr2-eyebrow--engraved" aria-hidden="true">01</span><h3><?php esc_html_e( 'Start with the piece', 'skyyrose-flagship-2' ); ?></h3><p><?php esc_html_e( 'Read its fit note and published measurements first. They are the product-specific source of truth.', 'skyyrose-flagship-2' ); ?></p></li>
			<li><span class="sr2-eyebrow sr2-eyebrow--engraved" aria-hidden="true">02</span><h3><?php esc_html_e( 'Measure what you own', 'skyyrose-flagship-2' ); ?></h3><p><?php esc_html_e( 'Lay a comparable garment flat. Compare chest, length, waist, rise, and inseam without stretching it.', 'skyyrose-flagship-2' ); ?></p></li>
			<li><span class="sr2-eyebrow sr2-eyebrow--engraved" aria-hidden="true">03</span><h3><?php esc_html_e( 'Ask before the order', 'skyyrose-flagship-2' ); ?></h3><p><?php esc_html_e( 'If you are between sizes or buying a made-to-order piece, Client Services can help before checkout.', 'skyyrose-flagship-2' ); ?></p></li>
		</ol>
		<div class="sr2-size-guide-dialog__actions">
			<a class="sr2-control sr2-control--primary" href="<?php echo esc_url( home_url( '/size-guide/' ) ); ?>"><?php esc_html_e( 'Open full size guide', 'skyyrose-flagship-2' ); ?></a>
			<a class="sr2-control sr2-control--quiet" href="<?php echo esc_url( home_url( '/contact/' ) ); ?>"><?php esc_html_e( 'Ask Client Services', 'skyyrose-flagship-2' ); ?></a>
		</div>
	</div>
</dialog>
