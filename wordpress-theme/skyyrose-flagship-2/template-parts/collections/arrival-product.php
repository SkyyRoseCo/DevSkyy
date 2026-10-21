<?php
/** Role-admitted product still with a usable collection title and shopping links. */
defined( 'ABSPATH' ) || exit;
$collection = $args['collection'];
$slug       = $args['slug'];
$image      = skyyrose2_collection_media( $slug, 'collection_hero' );
$markup     = skyyrose2_collection_media_markup( $image, 'eager', '(max-width: 47.99em) calc(100vw - 2rem), 60vw' );
?>
<header class="sr2-product-arrival" data-product-arrival data-collection="<?php echo esc_attr( $slug ); ?>" data-media-state="<?php echo $markup ? 'admitted' : 'unavailable'; ?>" aria-labelledby="sr2-collection-title">
	<div class="sr2-product-arrival__copy">
		<p class="sr2-eyebrow"><?php echo esc_html( $collection['kicker'] ); ?></p>
		<h1 id="sr2-collection-title" class="sr2-title-display"><?php echo esc_html( $collection['name'] ); ?></h1>
		<p class="sr2-lede"><?php echo esc_html( $collection['card_story'] ); ?></p>
		<div class="sr2-arrival__actions">
			<a class="sr2-control sr2-control--primary" href="#shop"><?php echo esc_html( $collection['hero_cta'] ); ?></a>
			<a class="sr2-editorial-link" href="<?php echo esc_url( $args['pieces_anchor'] ?? '#shop' ); ?>"><?php esc_html_e( 'Explore the pieces', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↓</span></a>
		</div>
	</div>
	<?php if ( $markup ) : ?>
		<figure class="sr2-product-arrival__media" data-product-arrival-media><?php echo $markup; // Governed, escaped collection-media helper output. ?></figure>
	<?php endif; ?>
</header>
