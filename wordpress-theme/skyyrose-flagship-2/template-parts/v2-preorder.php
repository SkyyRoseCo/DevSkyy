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
		'title'  => 'Find your piece',
		'copy'   => 'Explore the collection below. Each garment opens to its own product page.',
	),
	array(
		'number' => '02',
		'title'  => 'Review the details',
		'copy'   => 'Choose a size where offered and review the current price, availability, and any delivery information on the product page.',
	),
	array(
		'number' => '03',
		'title'  => 'Confirm at checkout',
		'copy'   => 'The bag and checkout show your final order details before payment. Your confirmation records the purchase.',
	),
);
$sr2_reserve_products   = skyyrose2_get_products( 100, 'pre-order' );
$sr2_reserve_worlds     = skyyrose2_collections();
$sr2_reserve_monument   = SKYYROSE2_URI . '/assets/images/house-monument-20260928.webp';
$sr2_reserve_edits      = array();
foreach ( $sr2_reserve_products as $sr2_reserve_product ) {
	$sr2_reserve_record = skyyrose2_product_presentation( $sr2_reserve_product );
	$sr2_reserve_slug   = sanitize_title( $sr2_reserve_record['collection'] ?? '' );
	$sr2_reserve_name   = $sr2_reserve_worlds[ $sr2_reserve_slug ]['name'] ?? __( 'SkyyRose', 'skyyrose-flagship-2' );
	if ( 'jersey-series' === ( $sr2_reserve_record['presentation'] ?? '' ) ) {
		$sr2_reserve_slug = 'jersey-series';
		$sr2_reserve_name = __( 'Jersey Series', 'skyyrose-flagship-2' );
	}
	if ( ! isset( $sr2_reserve_edits[ $sr2_reserve_slug ] ) ) {
		$sr2_reserve_edits[ $sr2_reserve_slug ] = array(
			'name'     => $sr2_reserve_name,
			'products' => array(),
		);
	}
	$sr2_reserve_edits[ $sr2_reserve_slug ]['products'][] = $sr2_reserve_product;
}
?>

<section class="sr2-arrival sr2-reserve-arrival" aria-labelledby="sr2-page-title">
	<div class="sr2-arrival__media">
		<img src="<?php echo esc_url( $sr2_reserve_monument ); ?>" alt="SkyyRose rose monument overlooking the Bay Bridge at dusk" width="1672" height="941" fetchpriority="high" decoding="async">
	</div>
	<div class="sr2-arrival__veil" aria-hidden="true"></div>
	<div class="sr2-arrival__copy">
		<p class="sr2-eyebrow">SkyyRose / Pre-Order</p>
		<h1 id="sr2-page-title" class="sr2-title-display">Made for the moment ahead.</h1>
		<p class="sr2-lede">A first look at what is coming to the house. Discover the pieces, then make your choice with current product details in view.</p>
		<div class="sr2-arrival__actions">
			<a class="sr2-control sr2-control--primary" href="#reserve">Explore the pieces</a>
			<a class="sr2-editorial-link" href="#reserve-process">How pre-order works<span aria-hidden="true">→</span></a>
		</div>
	</div>
	<p class="sr2-reserve-arrival__index" aria-hidden="true">The SkyyRose collection <span>↓</span></p>
</section>

<section id="reserve-process" class="sr2-band sr2-reserve-principles" aria-labelledby="sr2-reserve-principles-title">
	<div class="sr2-band__head">
		<div>
			<p class="sr2-eyebrow">The experience</p>
			<h2 id="sr2-reserve-principles-title" class="sr2-title-chapter">From first look to yours.</h2>
		</div>
		<p class="sr2-reserve-principles__intro">Each piece has its own product details and live purchase options. Delivery timing is shown on each product page when available.</p>
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
			<h2 id="sr2-reserve-products-title" class="sr2-title-chapter">Choose your place in the story.</h2>
			<p class="sr2-lede">Explore the edit, then open a piece to select available options and review its current order details.</p>
		</div>
	</div>
	<?php if ( $sr2_reserve_products ) : ?>
		<nav class="sr2-reserve-nav" aria-label="Browse pre-order collections">
			<?php foreach ( $sr2_reserve_edits as $sr2_reserve_slug => $sr2_reserve_edit ) : ?>
				<a href="#reserve-<?php echo esc_attr( $sr2_reserve_slug ); ?>"><?php echo esc_html( $sr2_reserve_edit['name'] ); ?><span aria-hidden="true"> ↗</span></a>
			<?php endforeach; ?>
		</nav>
		<?php
		$sr2_reserve_index      = 0;
		$sr2_reserve_edit_index = 0; foreach ( $sr2_reserve_edits as $sr2_reserve_slug => $sr2_reserve_edit ) :
			?>
		<section id="reserve-<?php echo esc_attr( $sr2_reserve_slug ); ?>" class="sr2-reserve-edit" aria-labelledby="reserve-<?php echo esc_attr( $sr2_reserve_slug ); ?>-title">
			<div class="sr2-reserve-edit__head">
				<p class="sr2-eyebrow">The collection / <?php echo esc_html( sprintf( '%02d', ++$sr2_reserve_edit_index ) ); ?></p>
				<h3 id="reserve-<?php echo esc_attr( $sr2_reserve_slug ); ?>-title" class="sr2-title-editorial"><?php echo esc_html( $sr2_reserve_edit['name'] ); ?></h3>
			</div>
			<div class="sr2-garment-grid">
					<?php foreach ( $sr2_reserve_edit['products'] as $sr2_reserve_product ) : ?>
						<?php
						get_template_part(
							'template-parts/commerce/product-card',
							null,
							array(
								'product'        => $sr2_reserve_product,
								'index'          => $sr2_reserve_index,
								'heading_level'  => 4,
								'variant'        => 0 === $sr2_reserve_index ? 'feature' : 'standard',
								'media_priority' => 'lazy',
								'frame'          => false,
								'sizes'          => '(max-width: 47.99em) calc(100vw - 2rem), (max-width: 74.99em) calc((100vw - 5rem) / 2), 480px',
							)
						);
						?>
						<?php ++$sr2_reserve_index; ?>
			<?php endforeach; ?>
			</div>
		</section>
				<?php endforeach; ?>
	<?php else : ?>
		<p class="sr2-empty">No pieces are available to pre-order right now. Explore the collections to discover the house.</p>
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
