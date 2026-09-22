<?php
/**
 * Full-frame, responsive composition with independently shoppable products.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;
$scene = $args['scene'];
$record = $scene['hero_composition'];
$collection = $args['collection'];
$index = absint( $args['index'] ?? 0 );
$scene_id = sanitize_html_class( strtolower( $scene['scene_id'] ) );
$products = skyyrose2_resolve_commerce_scene_products( $scene, $collection );
$is_preorder_scene = ! empty( $scene['preorder_product_links_required'] );
$srcset = array();
$final_manifest_path = SKYYROSE2_DIR . '/data/approved-scroll-world-scenes.json';
$final_manifest = is_readable( $final_manifest_path ) ? json_decode( file_get_contents( $final_manifest_path ), true ) : array(); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
$final_scene = $final_manifest['scenes'][ $scene['scene_id'] ] ?? array();
$hotspot_path = SKYYROSE2_DIR . '/data/scene-hotspots.json';
$hotspot_manifest = is_readable( $hotspot_path ) ? json_decode( file_get_contents( $hotspot_path ), true ) : array(); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
$hotspot_record = 1 === ( $hotspot_manifest['schema_version'] ?? 0 ) ? ( $hotspot_manifest['scenes'][ $scene['scene_id'] ] ?? array() ) : array();
$approved_poster = array();
foreach ( $final_scene['required_runtime_assets'] ?? array() as $asset ) {
	if ( 'poster' === ( $asset['role'] ?? '' ) ) { $approved_poster = $asset; }
}
$hotspots = $hotspot_record['points'] ?? array();
$hotspots_valid = is_array( $hotspots ) && ! empty( $hotspots )
	&& skyyrose2_approved_scroll_world_scene( $scene, $collection )
	&& ( $hotspot_record['poster'] ?? '' ) === ( $approved_poster['path'] ?? '' )
	&& ! empty( $approved_poster['sha256'] )
	&& ( $hotspot_record['poster_sha256'] ?? '' ) === $approved_poster['sha256']
	&& array_column( $hotspots, 'sku' ) === array_values( $scene['product_bindings'] ?? array() );
foreach ( (array) $hotspots as $point ) {
	foreach ( array( 'x', 'y' ) as $axis ) {
		if ( ! isset( $point[ $axis ] ) || ! is_numeric( $point[ $axis ] ) || $point[ $axis ] < 0.02 || $point[ $axis ] > 0.98 ) { $hotspots_valid = false; }
	}
}
foreach ( $final_scene['responsive_posters'] ?? array() as $derivative ) {
	$path = (string) ( $derivative['path'] ?? '' );
	if ( 0 === strpos( $path, 'assets/scroll-world/derived/approved-scenes/' ) && false === strpos( $path, '..' ) && ! empty( $derivative['width'] ) ) {
		$srcset[] = SKYYROSE2_URI . '/' . $path . ' ' . absint( $derivative['width'] ) . 'w';
	}
}
foreach ( (array) ( $record['variants'] ?? array() ) as $variant ) {
	$asset = (string) ( $variant['asset'] ?? '' );
	if ( 0 === strpos( $asset, 'generated-candidates/hero-commerce-c1/' ) && false === strpos( $asset, '..' ) && ! empty( $variant['width'] ) ) {
		$srcset[] = skyyrose2_scroll_world_asset_uri( $asset ) . ' ' . absint( $variant['width'] ) . 'w';
	}
}
?>
<article class="sr2-world sr2-world--commerce sr2-world--hero-composed" style="--scene-ratio: <?php echo esc_attr( (string) ( absint( $scene['width'] ) / max( 1, absint( $scene['height'] ) ) ) ); ?>;" data-scene-id="<?php echo esc_attr( $scene_id ); ?>" data-product-state="<?php echo esc_attr( $products['state'] ); ?>" data-composite-state="<?php echo empty( $scene['scene_motion'] ) ? 'candidate' : 'founder-approved-local-motion'; ?>" data-product-count="<?php echo esc_attr( count( $scene['product_bindings'] ) ); ?>">
	<figure class="sr2-hero-commerce__frame" style="--scene-aspect: <?php echo absint( $scene['width'] ); ?> / <?php echo absint( $scene['height'] ); ?>;">
		<img data-scene-poster src="<?php echo esc_url( skyyrose2_collection_scene_uri( $scene ) ); ?>" data-src="<?php echo esc_url( skyyrose2_collection_scene_uri( $scene ) ); ?>"<?php if ( $srcset ) : ?> srcset="<?php echo esc_attr( implode( ', ', $srcset ) ); ?>" data-srcset="<?php echo esc_attr( implode( ', ', $srcset ) ); ?>" sizes="(max-width: 767px) 100vw, 92vw"<?php endif; ?> alt="<?php echo esc_attr( $scene['direction'] ); ?>" width="<?php echo esc_attr( $scene['width'] ); ?>" height="<?php echo esc_attr( $scene['height'] ); ?>" loading="lazy" decoding="async">
		<?php if ( $hotspots_valid ) : ?>
			<nav id="scene-hotspots-<?php echo esc_attr( $scene_id ); ?>" class="sr2-scene-hotspots" data-scene-hotspots aria-label="<?php echo esc_attr( sprintf( __( 'Shop garments in %s', 'skyyrose-flagship-2' ), $scene['label'] ) ); ?>" hidden>
				<?php foreach ( $hotspots as $point_index => $point ) : ?>
					<?php $point_product = $products['slots'][ $point_index ]['product'] ?? false; if ( ! $point_product ) { continue; } ?>
					<a class="sr2-scene-hotspot" data-hotspot-sku="<?php echo esc_attr( $point['sku'] ); ?>" href="<?php echo esc_url( $point_product->get_permalink() ); ?>" style="--hotspot-x: <?php echo esc_attr( (string) ( 100 * (float) $point['x'] ) ); ?>%; --hotspot-y: <?php echo esc_attr( (string) ( 100 * (float) $point['y'] ) ); ?>%;" aria-label="<?php echo esc_attr( sprintf( $is_preorder_scene ? __( '%1$d. View pre-order: %2$s', 'skyyrose-flagship-2' ) : __( '%1$d. View %2$s', 'skyyrose-flagship-2' ), $point_index + 1, $point_product->get_name() ) ); ?>">
						<span class="sr2-scene-hotspot__number" aria-hidden="true"><?php echo esc_html( $point_index + 1 ); ?></span><span class="sr2-scene-hotspot__label" aria-hidden="true"><?php echo esc_html( $is_preorder_scene ? sprintf( __( 'Pre-order: %s', 'skyyrose-flagship-2' ), $point_product->get_name() ) : $point_product->get_name() ); ?></span>
					</a>
				<?php endforeach; ?>
			</nav>
		<?php endif; ?>

		<?php if ( ! empty( $scene['scene_motion'] ) ) : ?>
			<video
				id="scene-motion-<?php echo esc_attr( $scene_id ); ?>"
				data-collection-scene-motion
				data-scene-label="<?php echo esc_attr( $scene['label'] ); ?>"
				data-desktop-src="<?php echo esc_url( skyyrose2_scroll_world_asset_uri( $scene['scene_motion']['desktop'] ) ); ?>"
				data-mobile-src="<?php echo esc_url( skyyrose2_scroll_world_asset_uri( $scene['scene_motion']['mobile'] ) ); ?>"
				muted loop playsinline preload="none"
				width="<?php echo esc_attr( $scene['width'] ); ?>"
				height="<?php echo esc_attr( $scene['height'] ); ?>"
				aria-hidden="true" tabindex="-1"
			></video>
		<?php endif; ?>
	</figure>
	<?php if ( ! empty( $scene['scene_motion'] ) ) : ?>
		<div class="sr2-scene-motion-controls">
			<a class="sr2-scene-shop-link" href="#scene-products-title-<?php echo esc_attr( $scene_id ); ?>"><?php echo esc_html( $is_preorder_scene ? __( 'Pre-order this look', 'skyyrose-flagship-2' ) : __( 'Shop this look', 'skyyrose-flagship-2' ) ); ?><span aria-hidden="true">&rarr;</span></a>
			<?php if ( $hotspots_valid ) : ?><button type="button" class="sr2-scene-motion__toggle" data-scene-shop-toggle aria-pressed="false" aria-controls="scene-hotspots-<?php echo esc_attr( $scene_id ); ?>" hidden><?php esc_html_e( 'Product hotspots', 'skyyrose-flagship-2' ); ?></button><?php endif; ?>
			<button type="button" class="sr2-scene-motion__toggle" data-scene-motion-toggle
				aria-controls="scene-motion-<?php echo esc_attr( $scene_id ); ?>"
				aria-label="<?php echo esc_attr( 'Play motion: ' . $scene['label'] ); ?>" hidden>Play motion</button>
		</div>
	<?php endif; ?>
	<div class="sr2-hero-commerce__details">
		<header class="sr2-hero-commerce__story">
			<p class="sr2-eyebrow"><?php echo esc_html( sprintf( __( 'Chapter %02d', 'skyyrose-flagship-2' ), $index + 1 ) ); ?></p>
			<?php if ( $is_preorder_scene ) : ?><p class="sr2-eyebrow"><?php esc_html_e( 'Pre-order edition', 'skyyrose-flagship-2' ); ?></p><?php endif; ?>
			<h3<?php if ( 2 === $index ) : ?> data-sr2-type-motion="statement"<?php endif; ?>><?php echo esc_html( $scene['label'] ); ?></h3>
			<p><?php echo esc_html( $scene['copy'] ); ?></p>
			<?php if ( ! empty( $record['review_message'] ) ) : ?><p class="sr2-hero-commerce__review"><?php echo esc_html( $record['review_message'] ); ?></p><?php endif; ?>
		</header>
		<nav class="sr2-hero-commerce__products" aria-labelledby="<?php echo esc_attr( 'scene-products-title-' . $scene_id ); ?>">
			<h4 id="<?php echo esc_attr( 'scene-products-title-' . $scene_id ); ?>" tabindex="-1"><?php echo esc_html( $is_preorder_scene ? __( 'Pre-order this look', 'skyyrose-flagship-2' ) : __( 'Shop this look', 'skyyrose-flagship-2' ) ); ?><span class="screen-reader-text">: <?php echo esc_html( $scene['label'] ); ?></span></h4>
			<?php if ( $is_preorder_scene ) : ?><p><?php esc_html_e( 'The pieces in this scene are pre-order items. Full payment is due at checkout. Review each product for shipping details, or contact Client Services for an estimate before ordering.', 'skyyrose-flagship-2' ); ?></p><?php endif; ?>
			<ul>
				<?php foreach ( $products['slots'] as $slot ) : ?>
					<li data-scene-product-sku="<?php echo esc_attr( $slot['sku'] ); ?>">
						<?php if ( $slot['product'] ) : ?>
							<a href="<?php echo esc_url( $slot['product']->get_permalink() ); ?>">
								<span><?php echo esc_html( $slot['product']->get_name() ); ?></span>
								<small><?php echo wp_kses_post( $slot['product']->get_price_html() ); ?></small>
								<em><?php if ( $is_preorder_scene ) : ?><?php esc_html_e( 'Pre-order / Full payment at checkout', 'skyyrose-flagship-2' ); ?><br><?php endif; ?><?php echo esc_html( skyyrose2_scene_product_action_label( $slot['product'], $is_preorder_scene ) ); ?> &rarr;</em>
							</a>
						<?php else : ?>
							<span><?php echo esc_html( sprintf( __( '%s is not currently available.', 'skyyrose-flagship-2' ), strtoupper( $slot['sku'] ) ) ); ?></span>
						<?php endif; ?>
					</li>
				<?php endforeach; ?>
			</ul>
		</nav>
	</div>
</article>
