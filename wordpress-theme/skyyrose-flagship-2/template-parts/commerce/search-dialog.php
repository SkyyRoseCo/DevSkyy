<?php
/**
 * Global storefront search dialog.
 *
 * Search remains WordPress-owned: this dialog only provides a fast, accessible
 * entry point from the global navigation and submits to the canonical search
 * route. The preview module reads that same route on intent; GET remains usable.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;
?>
<dialog id="sr2-search-dialog" class="sr2-search-dialog" aria-labelledby="sr2-search-dialog-title">
	<div class="sr2-search-dialog__panel">
		<div class="sr2-dialog-head"><p class="sr2-index"><?php esc_html_e( '07 / The Living Archive', 'skyyrose-flagship-2' ); ?></p><form method="dialog"><button type="submit" class="sr2-search-dialog__close" aria-label="<?php esc_attr_e( 'Close search', 'skyyrose-flagship-2' ); ?>">×</button></form></div>
		<h2 id="sr2-search-dialog-title"><?php esc_html_e( 'Search the house.', 'skyyrose-flagship-2' ); ?></h2>
		<p><?php esc_html_e( 'Find a piece, collection, journal story, or service answer.', 'skyyrose-flagship-2' ); ?></p>
		<form class="sr2-search-dialog__form" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>">
			<label for="sr2-global-search"><?php esc_html_e( 'Search SkyyRose', 'skyyrose-flagship-2' ); ?></label>
			<div>
				<input id="sr2-global-search" name="s" type="search" inputmode="search" autocomplete="off" placeholder="<?php esc_attr_e( 'Try “Black Rose”', 'skyyrose-flagship-2' ); ?>" required data-search-input aria-describedby="sr2-search-preview-status">
				<button class="sr2-button sr2-button--fill" type="submit"><?php esc_html_e( 'Search', 'skyyrose-flagship-2' ); ?></button>
			</div>
		</form>
		<div class="sr2-search-preview" data-search-preview hidden
			data-idle="<?php esc_attr_e( 'Type at least 2 characters for a preview.', 'skyyrose-flagship-2' ); ?>"
			data-loading="<?php esc_attr_e( 'Searching the house…', 'skyyrose-flagship-2' ); ?>"
			data-empty="<?php esc_attr_e( 'Nothing surfaced. Try a collection, product, or story title.', 'skyyrose-flagship-2' ); ?>"
			data-error="<?php esc_attr_e( 'Preview unavailable. Use Search to see the full results.', 'skyyrose-flagship-2' ); ?>"
			data-count="<?php esc_attr_e( 'Preview results: %d. Open a result or use Search for all results.', 'skyyrose-flagship-2' ); ?>">
			<p id="sr2-search-preview-status" class="sr2-search-preview__status" role="status" aria-live="polite" aria-atomic="true"></p>
			<ul class="sr2-search-preview__results" data-search-preview-results aria-label="<?php esc_attr_e( 'Search preview results', 'skyyrose-flagship-2' ); ?>"></ul>
		</div>
		<nav class="sr2-search-dialog__links" aria-label="<?php esc_attr_e( 'Search shortcuts', 'skyyrose-flagship-2' ); ?>">
			<a href="<?php echo esc_url( home_url( '/collections/signature/' ) ); ?>"><?php esc_html_e( 'Signature', 'skyyrose-flagship-2' ); ?></a>
			<a href="<?php echo esc_url( home_url( '/collections/black-rose/' ) ); ?>"><?php esc_html_e( 'Black Rose', 'skyyrose-flagship-2' ); ?></a>
			<a href="<?php echo esc_url( home_url( '/collections/love-hurts/' ) ); ?>"><?php esc_html_e( 'Love Hurts', 'skyyrose-flagship-2' ); ?></a>
			<a href="<?php echo esc_url( home_url( '/collections/kids-capsule/' ) ); ?>"><?php esc_html_e( 'Kids Capsule', 'skyyrose-flagship-2' ); ?></a>
		</nav>
	</div>
</dialog>
