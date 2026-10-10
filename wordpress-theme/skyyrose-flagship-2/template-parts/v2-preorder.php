<?php
/**
 * V2 pre-order: distinct collection edits and independently eligible merchandise
 * scenes. WooCommerce owns the selected pieces, prices, sizes and availability.
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
$sr2_reserve_products   = skyyrose2_get_products( -1, 'pre-order' );
$sr2_reserve_worlds     = skyyrose2_collections();
$sr2_reserve_registry   = skyyrose2_presentation_registry();
$sr2_reserve_groups     = array_fill_keys( array( 'signature', 'black-rose', 'love-hurts' ), array() );
$sr2_reserve_by_sku     = array();
foreach ( $sr2_reserve_products as $sr2_reserve_product ) {
	$sr2_reserve_record = skyyrose2_product_presentation( $sr2_reserve_product );
	$sr2_reserve_slug   = sanitize_title( $sr2_reserve_record['collection'] ?? '' ) ?: 'house';
	$sr2_reserve_groups[ $sr2_reserve_slug ][] = $sr2_reserve_product;
	$sr2_reserve_by_sku[ sanitize_key( $sr2_reserve_product->get_sku() ) ] = $sr2_reserve_product;
}
$sr2_reserve_groups = array_filter( $sr2_reserve_groups );

// The eligibility inventory owns delivery. Never infer a replacement from a
// filename or fall back to a historical salon, hero, scene or Woo attachment.
$sr2_reserve_media = static function ( $role, $collection, $pieces ) {
	$piece_skus = array_map( static fn( $piece ) => sanitize_key( $piece->get_sku() ), $pieces );
	foreach ( (array) ( skyyrose2_media_inventory()['assets'] ?? array() ) as $path => $record ) {
		if ( ! is_array( $record ) || 'photograph' !== ( $record['kind'] ?? '' ) || ! is_array( $record['roles'] ?? null ) || ! in_array( $role, $record['roles'], true ) ) {
			continue;
		}
		$cast = $record['skus'] ?? array();
		if ( ! is_array( $cast ) || ! array_is_list( $cast ) || ! $cast || count( array_filter( $cast, 'is_string' ) ) !== count( $cast ) || array_diff( $cast, $piece_skus ) || ( $collection && array( $collection ) !== ( $record['collections'] ?? array() ) ) ) {
			continue;
		}
		$uri = skyyrose2_media_uri( $path, $role );
		if ( ! $uri ) {
			continue;
		}
		$size = getimagesize( SKYYROSE2_DIR . '/' . $path );
		if ( $size && $size[0] > 0 && $size[1] > 0 ) {
			return array( 'src' => $uri, 'width' => $size[0], 'height' => $size[1], 'skus' => $cast );
		}
	}
	return array();
};
?>

<section class="sr2-arrival sr2-reserve-arrival sr2-reserve-arrival--text" aria-labelledby="sr2-page-title">
	<div class="sr2-arrival__copy">
		<p class="sr2-eyebrow"><?php esc_html_e( 'The Pre-Order Edit', 'skyyrose-flagship-2' ); ?></p>
		<h1 id="sr2-page-title" class="sr2-title-display">The piece is the invitation.</h1>
		<p class="sr2-lede"><?php esc_html_e( 'Each collection, its own story. Every piece, a personal choice. Explore the pieces, then review your size, price, availability, and order terms.', 'skyyrose-flagship-2' ); ?></p>
		<div class="sr2-arrival__actions">
			<a class="sr2-control sr2-control--primary" href="#reserve"><?php esc_html_e( 'Choose your collection', 'skyyrose-flagship-2' ); ?></a>
			<a class="sr2-editorial-link" href="#sr2-reserve-principles-title"><?php esc_html_e( 'Read the order terms', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↓</span></a>
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
	<?php if ( $sr2_reserve_groups ) : ?>
		<nav class="sr2-reserve-nav" aria-label="<?php esc_attr_e( 'Pre-order collections', 'skyyrose-flagship-2' ); ?>">
			<?php foreach ( $sr2_reserve_groups as $sr2_reserve_slug => $sr2_reserve_pieces ) : ?>
				<a href="#reserve-<?php echo esc_attr( $sr2_reserve_slug ); ?>"><?php echo esc_html( $sr2_reserve_worlds[ $sr2_reserve_slug ]['name'] ?? __( 'SkyyRose', 'skyyrose-flagship-2' ) ); ?><span aria-hidden="true">↓</span></a>
			<?php endforeach; ?>
		</nav>
		<?php foreach ( $sr2_reserve_groups as $sr2_reserve_slug => $sr2_reserve_pieces ) : ?>
			<?php
			$sr2_reserve_name  = $sr2_reserve_worlds[ $sr2_reserve_slug ]['name'] ?? __( 'SkyyRose', 'skyyrose-flagship-2' );
			$sr2_reserve_story = $sr2_reserve_registry['collections'][ $sr2_reserve_slug ]['story']['seed'] ?? '';
			$sr2_reserve_scene = $sr2_reserve_media( 'merchandise_scene', $sr2_reserve_slug, $sr2_reserve_pieces );
			?>
			<section id="reserve-<?php echo esc_attr( $sr2_reserve_slug ); ?>" class="sr2-reserve-edit<?php echo 1 === count( $sr2_reserve_pieces ) ? ' sr2-reserve-edit--single' : ''; ?>" data-preorder-collection="<?php echo esc_attr( $sr2_reserve_slug ); ?>" data-collection="<?php echo esc_attr( $sr2_reserve_slug ); ?>" aria-labelledby="reserve-<?php echo esc_attr( $sr2_reserve_slug ); ?>-title" tabindex="-1">
				<header class="sr2-reserve-edit__head">
					<div>
						<p class="sr2-eyebrow"><?php esc_html_e( 'The pre-order edit', 'skyyrose-flagship-2' ); ?></p>
						<h3 id="reserve-<?php echo esc_attr( $sr2_reserve_slug ); ?>-title" class="sr2-title-chapter"><?php echo esc_html( $sr2_reserve_name ); ?></h3>
						<?php if ( $sr2_reserve_story ) : ?><p class="sr2-lede"><?php echo esc_html( $sr2_reserve_story ); ?></p><?php endif; ?>
					</div>
					<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_collection_url( $sr2_reserve_slug ) ); ?>"><?php echo esc_html( sprintf( __( 'Explore %s', 'skyyrose-flagship-2' ), $sr2_reserve_name ) ); ?><span aria-hidden="true">→</span></a>
				</header>
				<?php if ( $sr2_reserve_scene ) : ?>
					<figure class="sr2-reserve-scene" data-media-role="merchandise_scene">
						<img src="<?php echo esc_url( $sr2_reserve_scene['src'] ); ?>" alt="<?php echo esc_attr( sprintf( __( '%s pre-order pieces', 'skyyrose-flagship-2' ), $sr2_reserve_name ) ); ?>" width="<?php echo esc_attr( $sr2_reserve_scene['width'] ); ?>" height="<?php echo esc_attr( $sr2_reserve_scene['height'] ); ?>" loading="lazy" decoding="async">
						<figcaption class="sr2-reserve-scene__pieces">
							<?php foreach ( $sr2_reserve_scene['skus'] as $sr2_reserve_scene_sku ) : ?>
								<?php $sr2_reserve_scene_product = $sr2_reserve_by_sku[ $sr2_reserve_scene_sku ]; ?>
								<a class="sr2-editorial-link" href="<?php echo esc_url( $sr2_reserve_scene_product->get_permalink() ); ?>"><?php echo esc_html( $sr2_reserve_scene_product->get_name() ); ?><span aria-hidden="true">→</span></a>
							<?php endforeach; ?>
						</figcaption>
					</figure>
				<?php endif; ?>
				<div class="sr2-garment-grid">
			<?php foreach ( $sr2_reserve_pieces as $sr2_reserve_index => $sr2_reserve_product ) : ?>
				<?php
				get_template_part(
					'template-parts/commerce/product-card',
					null,
					array(
						'product'        => $sr2_reserve_product,
						'index'          => $sr2_reserve_index,
						'heading_level'  => 4,
						'variant'        => 'standard',
						'media_priority' => 'lazy',
						'frame'          => false,
						'listing'        => 'pre-order',
						'sizes'          => '(max-width: 47.99em) calc(100vw - 3rem), (max-width: 63.99em) calc((100vw - 5rem) / 2), 360px',
					)
				);
				?>
			<?php endforeach; ?>
				</div>
			</section>
		<?php endforeach; ?>
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
