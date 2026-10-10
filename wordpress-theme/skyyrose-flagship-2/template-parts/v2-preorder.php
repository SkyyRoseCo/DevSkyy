<?php
/**
 * V2 pre-order page: one full-bleed Black Rose salon arrival, clear terms, then the
 * garment-led edit. WooCommerce stays the authority for price, size and availability.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$sr2_reserve_principles = array(
	array(
		'number' => '01',
		'title'  => 'Choose with the details open',
		'copy'   => 'Each piece links to its product page for size, price, availability, and order terms.',
	),
	array(
		'number' => '02',
		'title'  => 'Full payment at checkout',
		'copy'   => 'Pre-orders require full payment at checkout. The pre-order label does not reserve stock or establish a shipping date. Contact Client Services for shipping estimates before ordering.',
	),
	array(
		'number' => '03',
		'title'  => 'Keep the receipt',
		'copy'   => 'Order confirmation and account history remain the source for purchase status and any updates the store publishes.',
	),
);
$sr2_reserve_products   = skyyrose2_get_products( 12, 'pre-order' );
$sr2_reserve_worlds     = skyyrose2_collections();
$sr2_reserve_salon      = 'images/preorder/responsive/black-rose-salon';
?>

<section class="sr2-arrival sr2-reserve-arrival" data-collection="black-rose" aria-labelledby="sr2-page-title">
	<div class="sr2-arrival__media" style="--sr2-focal: 50% 60%;">
		<picture>
			<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_reserve_salon . '-640w.webp' ) ); ?>">
			<source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_reserve_salon . '-1024w.webp' ) ); ?>">
			<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_reserve_salon . '-1440w.webp' ) ); ?>" alt="Black Rose pieces displayed in the SkyyRose pre-order salon" width="1440" height="960" fetchpriority="high" decoding="async">
		</picture>
	</div>
	<div class="sr2-arrival__veil" aria-hidden="true"></div>
	<div class="sr2-arrival__copy">
		<p class="sr2-eyebrow">The Pre-Order Collection</p>
		<h1 id="sr2-page-title" class="sr2-title-display">The piece is the invitation.</h1>
		<p class="sr2-lede">Enter through the Black Rose salon, then select the piece with the product facts in front of you. Review size, price, and availability before ordering.</p>
		<div class="sr2-arrival__actions">
			<a class="sr2-control sr2-control--primary" href="#reserve">View pieces</a>
			<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_collection_url( 'black-rose' ) ); ?>">Enter Black Rose<span aria-hidden="true">→</span></a>
		</div>
	</div>
</section>

<section class="sr2-band sr2-reserve-principles" aria-labelledby="sr2-reserve-principles-title">
	<div class="sr2-band__head">
		<div>
			<p class="sr2-eyebrow">Before the order</p>
			<h2 id="sr2-reserve-principles-title" class="sr2-title-chapter">Clear terms belong beside the feeling.</h2>
		</div>
	</div>
	<ol class="sr2-reserve-principles__list">
		<?php foreach ( $sr2_reserve_principles as $sr2_principle ) : ?>
			<li>
				<p class="sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( $sr2_principle['number'] ); ?></p>
				<h3 class="sr2-title-editorial"><?php echo esc_html( $sr2_principle['title'] ); ?></h3>
				<p><?php echo esc_html( $sr2_principle['copy'] ); ?></p>
			</li>
		<?php endforeach; ?>
	</ol>
</section>

<section id="reserve" class="sr2-band sr2-reserve-products" aria-labelledby="sr2-reserve-products-title" tabindex="-1">
	<div class="sr2-band__head">
		<div>
			<p class="sr2-eyebrow">Browse the collection</p>
			<h2 id="sr2-reserve-products-title" class="sr2-title-chapter">Future pieces. Present choice.</h2>
			<p class="sr2-lede">Review each product for current price and availability.</p>
		</div>
	</div>
	<?php if ( $sr2_reserve_products ) : ?>
		<div class="sr2-garment-grid">
			<?php foreach ( $sr2_reserve_products as $sr2_reserve_index => $sr2_reserve_product ) : ?>
				<?php
				get_template_part(
					'template-parts/commerce/product-card',
					null,
					array(
						'product'        => $sr2_reserve_product,
						'index'          => $sr2_reserve_index,
						'heading_level'  => 3,
						'variant'        => 'standard',
						'media_priority' => 'lazy',
						'frame'          => false,
						'sizes'          => '(max-width: 47.99em) calc((100vw - 3rem) / 2), (max-width: 74.99em) calc((100vw - 5rem) / 3), 360px',
					)
				);
				?>
			<?php endforeach; ?>
		</div>
	<?php else : ?>
		<p class="sr2-empty">Next pieces entering the world soon.</p>
	<?php endif; ?>
</section>

<section class="sr2-band sr2-reserve-worlds" aria-labelledby="sr2-reserve-worlds-title">
	<div class="sr2-page-grid">
		<div class="sr2-page-grid__main">
			<p class="sr2-eyebrow">The house remains open</p>
			<h2 id="sr2-reserve-worlds-title" class="sr2-title-chapter">Choose the world before the product.</h2>
		</div>
		<ol class="sr2-index-list sr2-page-grid__aside">
			<?php $sr2_reserve_number = 0; foreach ( $sr2_reserve_worlds as $sr2_reserve_slug => $sr2_reserve_world ) : ?>
				<li><a href="<?php echo esc_url( skyyrose2_collection_url( $sr2_reserve_slug ) ); ?>"><span class="sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( sprintf( '%02d', ++$sr2_reserve_number ) ); ?></span><span><?php echo esc_html( $sr2_reserve_world['name'] ); ?></span><span aria-hidden="true">→</span></a></li>
			<?php endforeach; ?>
		</ol>
	</div>
</section>
