<?php
/**
 * V2 pre-order page: a standard purchase path wrapped in the Black Rose salon.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$sr2_reserve_principles = array(
	array( 'number' => '01', 'title' => 'Choose with the details open', 'copy' => 'Each piece links to its product page for size, price, availability, and order terms.' ),
	array( 'number' => '02', 'title' => 'Full payment at checkout', 'copy' => 'Pre-orders require full payment at checkout. The pre-order label does not reserve stock or establish a shipping date. Contact Client Services for shipping estimates before ordering.' ),
	array( 'number' => '03', 'title' => 'Keep the receipt', 'copy' => 'Order confirmation and account history remain the source for purchase status and any updates the store publishes.' ),
);
?>

<section class="sr2-reserve-hero" aria-labelledby="sr2-page-title">
	<div class="sr2-reserve-hero__media"><picture><source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/preorder/responsive/black-rose-salon-640w.webp' ) ); ?>"><source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/preorder/responsive/black-rose-salon-1024w.webp' ) ); ?>"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/preorder/responsive/black-rose-salon-1440w.webp' ) ); ?>" alt="Black Rose pieces displayed in the SkyyRose pre-order salon" width="1440" height="960" fetchpriority="high" decoding="sync"></picture></div>
	<div class="sr2-reserve-hero__copy">
		<p class="sr2-eyebrow">The Pre-Order Collection</p>
		<h1 id="sr2-page-title">The piece is the invitation.</h1>
		<p>Enter through the Black Rose salon, then select the piece with the product facts in front of you. Review size, price, and availability before ordering.</p>
		<a class="sr2-button sr2-button--fill" href="#reserve">View pieces</a>
	</div>
	<p class="sr2-reserve-hero__caption">SkyyRose / Black Rose Salon / Oakland</p>
</section>

<section class="sr2-reserve-principles" aria-labelledby="sr2-reserve-principles-title">
	<header class="sr2-section-head"><p>Before the order</p><h2 id="sr2-reserve-principles-title">Clear terms belong beside the feeling.</h2></header>
	<div>
		<?php foreach ( $sr2_reserve_principles as $sr2_principle ) : ?>
			<article><span><?php echo esc_html( $sr2_principle['number'] ); ?></span><h3><?php echo esc_html( $sr2_principle['title'] ); ?></h3><p><?php echo esc_html( $sr2_principle['copy'] ); ?></p></article>
		<?php endforeach; ?>
	</div>
</section>

<section class="sr2-reserve-salon" aria-labelledby="sr2-reserve-salon-title">
	<header class="sr2-section-head sr2-section-head--split"><div><p>Black Rose / The first room</p><h2 id="sr2-reserve-salon-title">Walk the salon before you shop it.</h2></div><p>The scene is a portal into the Black Rose world. Garment proof, price, size, and availability stay with the actual product.</p></header>
	<div class="sr2-reserve-salon__frame"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/preorder/responsive/black-rose-salon-1440w.webp' ) ); ?>" alt="A dark Black Rose salon with garments arranged as an immersive shopping scene" width="1440" height="960" loading="lazy" decoding="async"><a class="sr2-button" href="<?php echo esc_url( skyyrose2_collection_url( 'black-rose' ) ); ?>">Enter Black Rose</a></div>
</section>

<section id="reserve" class="sr2-section sr2-section--products sr2-reserve-products" aria-labelledby="sr2-reserve-products-title">
	<header class="sr2-section-head"><p>Browse the collection</p><h2 id="sr2-reserve-products-title">Future pieces. Present choice.</h2><p class="sr2-section-head__note">Review each product for current price and availability.</p></header>
	<?php skyyrose2_product_cards( 12, 'pre-order' ); ?>
</section>

<section class="sr2-reserve-worlds" aria-labelledby="sr2-reserve-worlds-title">
	<header class="sr2-section-head"><p>The house remains open</p><h2 id="sr2-reserve-worlds-title">Choose the world before the product.</h2></header>
	<?php skyyrose2_render_collection_rail(); ?>
</section>
