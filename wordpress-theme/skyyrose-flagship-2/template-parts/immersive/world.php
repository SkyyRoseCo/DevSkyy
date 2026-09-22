<?php
/**
 * Governed immersive story-world renderer.
 *
 * The world is intentionally DOM-first: verified photography and complete
 * chapter copy render before JavaScript, while Three.js is a progressive
 * atmospheric layer. Commerce remains fail-closed — a hotspot is emitted only
 * when WooCommerce resolves its canonical SKU to a published, visible product.
 *
 * @package SkyyRoseFlagship2
 *
 * @param array $args Immersive world contract supplied by a page template.
 */

defined( 'ABSPATH' ) || exit;

$collection_slug = isset( $args['collection_slug'] ) ? sanitize_key( $args['collection_slug'] ) : '';
$collection_name = isset( $args['collection_name'] ) ? (string) $args['collection_name'] : '';
$world_name      = isset( $args['world_name'] ) ? (string) $args['world_name'] : '';
$world_type      = isset( $args['world_type'] ) ? sanitize_key( $args['world_type'] ) : '';
$kicker          = isset( $args['kicker'] ) ? (string) $args['kicker'] : '';
$manifesto       = isset( $args['manifesto'] ) ? (string) $args['manifesto'] : '';
$direction       = isset( $args['direction'] ) ? (string) $args['direction'] : '';
$poster          = isset( $args['poster'] ) ? ltrim( (string) $args['poster'], '/' ) : '';
$chapters        = isset( $args['chapters'] ) && is_array( $args['chapters'] ) ? $args['chapters'] : array();
$scene_config    = isset( $args['scene'] ) && is_array( $args['scene'] ) ? $args['scene'] : array();
$accent          = isset( $args['accent'] ) ? (string) $args['accent'] : '#b76e79';
$accent_rgb      = isset( $args['accent_rgb'] ) ? (string) $args['accent_rgb'] : '183, 110, 121';
$correlation_id  = wp_generate_uuid4();

/* Approved commerce chapters are distinct from the collection's entry hero. */
$commerce_chapters = skyyrose2_collection_commerce_scenes( $collection_slug );
if ( ! empty( $commerce_chapters ) ) {
	$motion_chapters = array_filter(
		$commerce_chapters,
		static function ( $chapter ) {
			return ! empty( $chapter['scene_motion'] );
		}
	);
	if ( count( $motion_chapters ) === count( $commerce_chapters ) ) {
		$chapters = array_map(
			static function ( $chapter ) {
				$chapter['id']  = strtolower( $chapter['scene_id'] );
				$chapter['alt'] = (string) ( $chapter['direction'] ?? '' );
				return $chapter;
			},
			$commerce_chapters
		);
	}
}


if ( ! $collection_slug || ! $collection_name || ! $world_name || ! $poster || empty( $chapters ) ) {
	return;
}

$source_css = SKYYROSE2_DIR . '/assets/css/immersive.css';
$min_css    = SKYYROSE2_DIR . '/assets/css/immersive.min.css';
$source_js  = SKYYROSE2_DIR . '/assets/js/immersive.js';
$min_js     = SKYYROSE2_DIR . '/assets/js/immersive.min.js';
$css_suffix = ! ( defined( 'SCRIPT_DEBUG' ) && SCRIPT_DEBUG ) && file_exists( $min_css ) && filemtime( $min_css ) >= filemtime( $source_css ) ? '.min' : '';
$js_suffix  = ! ( defined( 'SCRIPT_DEBUG' ) && SCRIPT_DEBUG ) && file_exists( $min_js ) && filemtime( $min_js ) >= filemtime( $source_js ) ? '.min' : '';

wp_enqueue_style( 'skyyrose2-immersive', SKYYROSE2_URI . '/assets/css/immersive' . $css_suffix . '.css', array( 'skyyrose2-tokens', 'skyyrose2-theme' ), SKYYROSE2_VERSION );
wp_enqueue_script( 'skyyrose2-immersive', SKYYROSE2_URI . '/assets/js/immersive' . $js_suffix . '.js', array( 'skyyrose2-theme' ), SKYYROSE2_VERSION, true );

$poster_path = SKYYROSE2_DIR . '/assets/sot/' . $poster;
if ( ! file_exists( $poster_path ) ) {
	$poster = 'images/hero/kids-capsule-heir-throne-v3.webp';
}
$poster_uri = skyyrose2_sot_asset_uri( $poster );

$scene_payload = array(
	'collection'    => $collection_slug,
	'worldType'     => $world_type,
	'accent'        => $accent,
	'accentRgb'     => $accent_rgb,
	'correlationId' => $correlation_id,
	'scene'         => $scene_config,
);

get_header();
?>
<main id="primary" tabindex="-1" class="sr2-immersive sr2-immersive--<?php echo esc_attr( $world_type ); ?>"
	data-collection="<?php echo esc_attr( $collection_slug ); ?>"
	data-world="<?php echo esc_attr( $world_type ); ?>"
	data-scene-state="poster"
	data-correlation-id="<?php echo esc_attr( $correlation_id ); ?>"
	style="--sr2-immersive-accent: <?php echo esc_attr( $accent ); ?>; --sr2-immersive-accent-rgb: <?php echo esc_attr( $accent_rgb ); ?>;">
	<div class="sr2-immersive__progress" aria-hidden="true"><span></span></div>

	<section class="sr2-immersive__entry" id="world-entry" aria-labelledby="immersive-world-title">
		<div class="sr2-immersive__poster" aria-hidden="true">
			<img src="<?php echo esc_url( $poster_uri ); ?>"
				alt=""
				width="1672"
				height="941"
				fetchpriority="high"
				decoding="async">
		</div>
		<canvas class="sr2-immersive__canvas" width="1280" height="720" aria-hidden="true"></canvas>
		<div class="sr2-immersive__entry-veil" aria-hidden="true"></div>
		<div class="sr2-immersive__entry-copy">
			<p class="sr2-immersive__kicker"><?php echo esc_html( $kicker ); ?></p>
			<h1 id="immersive-world-title" class="sr2-immersive__sr-title"><?php echo esc_html( $collection_name . ': ' . $world_name ); ?></h1>
			<p class="sr2-immersive__direction"><?php echo esc_html( $direction ); ?></p>
			<div class="sr2-immersive__portal-actions">
			<a class="sr2-immersive__enter" href="#chapter-<?php echo esc_attr( sanitize_key( $chapters[0]['id'] ?? 'one' ) ); ?>">
				<span><?php esc_html_e( 'Enter the story', 'skyyrose-flagship-2' ); ?></span>
				<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path d="M12 3v17m-7-7 7 7 7-7" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
			</a>
			<a class="sr2-immersive__enter" href="<?php echo esc_url( skyyrose2_collection_url( $collection_slug ) ); ?>#shop"><?php esc_html_e( 'Shop collection', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a>
			</div>
		</div>
		<p class="sr2-immersive__scene-status screen-reader-text" aria-live="polite"><?php esc_html_e( 'The static story scene is ready.', 'skyyrose-flagship-2' ); ?></p>
		<noscript><p class="sr2-immersive__noscript"><?php esc_html_e( 'The complete visual story is available below. Motion is optional.', 'skyyrose-flagship-2' ); ?></p></noscript>
	</section>

	<nav class="sr2-immersive__chapter-nav" aria-label="<?php esc_attr_e( 'Story chapters', 'skyyrose-flagship-2' ); ?>">
		<p class="sr2-immersive__chapter-mark" aria-hidden="true"><?php echo esc_html( sprintf( '%02d', count( $chapters ) ) ); ?></p>
		<ol>
			<?php foreach ( $chapters as $index => $chapter ) : ?>
				<?php $chapter_id = sanitize_key( $chapter['id'] ?? 'chapter-' . ( $index + 1 ) ); ?>
				<li><a href="#chapter-<?php echo esc_attr( $chapter_id ); ?>"<?php echo 0 === $index ? ' aria-current="step"' : ''; ?>><span><?php echo esc_html( sprintf( '%02d', $index + 1 ) ); ?></span><?php echo esc_html( $chapter['label'] ?? '' ); ?></a></li>
			<?php endforeach; ?>
		</ol>
	</nav>

	<section class="sr2-immersive__prologue" aria-labelledby="immersive-prologue-title">
		<p class="sr2-immersive__eyebrow"><?php echo esc_html( $collection_name ); ?></p>
		<h2 id="immersive-prologue-title"><?php echo esc_html( $world_name ); ?></h2>
		<p><?php echo esc_html( $manifesto ); ?></p>
	</section>

	<div class="sr2-immersive__chapters">
		<?php foreach ( $chapters as $index => $chapter ) : ?>
			<?php if ( ! empty( $chapter['scene_motion'] ) ) : ?>
				<section class="sr2-immersive__chapter sr2-immersive__chapter--commerce"
					id="chapter-<?php echo esc_attr( sanitize_key( $chapter['id'] ) ); ?>"
					data-chapter="<?php echo esc_attr( sanitize_key( $chapter['id'] ) ); ?>"
					data-index="<?php echo absint( $index ); ?>">
					<?php
					get_template_part(
						'template-parts/commerce/hero-composed-scene',
						null,
						array(
							'scene'      => $chapter,
							'collection' => $collection_slug,
							'index'      => $index,
						)
					);
					?>
				</section>
				<?php continue; ?>
			<?php endif; ?>
			<?php
			$chapter_id    = sanitize_key( $chapter['id'] ?? 'chapter-' . ( $index + 1 ) );
			$chapter_image = isset( $chapter['image'] ) ? ltrim( (string) $chapter['image'], '/' ) : '';
			$is_scroll     = isset( $chapter['source'] ) && 'scroll-world' === $chapter['source'];
			$image_path    = $is_scroll ? SKYYROSE2_DIR . '/assets/scroll-world/' . $chapter_image : SKYYROSE2_DIR . '/assets/sot/' . $chapter_image;
			$image_uri     = $is_scroll ? skyyrose2_scroll_world_asset_uri( $chapter_image ) : skyyrose2_sot_asset_uri( $chapter_image );
			$image_exists  = $chapter_image && file_exists( $image_path );
			$hotspots      = isset( $chapter['hotspots'] ) && is_array( $chapter['hotspots'] ) ? $chapter['hotspots'] : array();
			?>
			<article class="sr2-immersive__chapter" id="chapter-<?php echo esc_attr( $chapter_id ); ?>" data-chapter="<?php echo esc_attr( $chapter_id ); ?>" data-index="<?php echo esc_attr( (string) $index ); ?>">
				<div class="sr2-immersive__chapter-media">
					<?php if ( $image_exists ) : ?>
						<img src="<?php echo esc_url( $image_uri ); ?>"
							alt="<?php echo esc_attr( $chapter['alt'] ?? $chapter['label'] ?? '' ); ?>"
							width="1344"
							height="896"
							loading="lazy"
							decoding="async">
					<?php else : ?>
						<img src="<?php echo esc_url( $poster_uri ); ?>" alt="" width="1672" height="941" loading="lazy" decoding="async">
					<?php endif; ?>
					<div class="sr2-immersive__chapter-shade" aria-hidden="true"></div>
					<?php foreach ( $hotspots as $hotspot ) : ?>
						<?php
						$sku     = isset( $hotspot['sku'] ) ? sanitize_text_field( $hotspot['sku'] ) : '';
						$product = false;
						if ( $sku && function_exists( 'wc_get_product_id_by_sku' ) && function_exists( 'wc_get_product' ) ) {
							$product_id = wc_get_product_id_by_sku( $sku );
							$product    = $product_id ? wc_get_product( $product_id ) : false;
						}
						$approved_front = skyyrose2_approved_card_front( $product );
						if ( ! $product || 'publish' !== $product->get_status() || ! $product->is_visible() || ( ! $approved_front && ! $product->get_image_id() ) ) {
							continue;
						}
						$hotspot_presentation = function_exists( 'skyyrose2_product_presentation' ) ? skyyrose2_product_presentation( $product ) : array();
						if ( empty( $hotspot_presentation ) || sanitize_title( $hotspot_presentation['collection'] ?? '' ) !== $collection_slug ) {
							continue;
						}
						$left = isset( $hotspot['left'] ) ? max( 8, min( 92, (float) $hotspot['left'] ) ) : 50;
						$top  = isset( $hotspot['top'] ) ? max( 12, min( 88, (float) $hotspot['top'] ) ) : 50;
						?>
						<a class="sr2-immersive__hotspot" href="<?php echo esc_url( get_permalink( $product->get_id() ) ); ?>"
							style="--hotspot-x: <?php echo esc_attr( (string) $left ); ?>%; --hotspot-y: <?php echo esc_attr( (string) $top ); ?>%;"
							data-sku="<?php echo esc_attr( $sku ); ?>"
							data-correlation-id="<?php echo esc_attr( $correlation_id ); ?>"
							aria-label="<?php echo esc_attr( sprintf( __( 'Explore %s', 'skyyrose-flagship-2' ), $product->get_name() ) ); ?>">
							<span class="sr2-immersive__hotspot-media">
								<?php if ( $approved_front ) : ?>
									<img class="sr2-immersive__hotspot-image" src="<?php echo esc_url( $approved_front['src'] ); ?>" alt="<?php echo esc_attr( $approved_front['alt'] ); ?>" width="<?php echo esc_attr( (string) $approved_front['width'] ); ?>" height="<?php echo esc_attr( (string) $approved_front['height'] ); ?>" loading="lazy" decoding="async">
								<?php else : ?>
									<?php
									echo wp_kses_post(
										wp_get_attachment_image(
											$product->get_image_id(),
											'woocommerce_thumbnail',
											false,
											array(
												'class'    => 'sr2-immersive__hotspot-image',
												'loading'  => 'lazy',
												'decoding' => 'async',
												'alt'      => $product->get_name(),
											)
										)
									);
									?>
								<?php endif; ?>
							</span>
							<span class="sr2-immersive__hotspot-copy"><small><?php esc_html_e( 'Piece in this scene', 'skyyrose-flagship-2' ); ?></small><strong><?php echo esc_html( $product->get_name() ); ?></strong><em><?php esc_html_e( 'View the product', 'skyyrose-flagship-2' ); ?> →</em></span>
						</a>
					<?php endforeach; ?>
				</div>
				<div class="sr2-immersive__chapter-copy">
					<p class="sr2-immersive__chapter-number"><?php echo esc_html( sprintf( '%02d / %02d', $index + 1, count( $chapters ) ) ); ?></p>
					<h2><?php echo esc_html( $chapter['label'] ?? '' ); ?></h2>
					<p><?php echo esc_html( $chapter['copy'] ?? '' ); ?></p>
					<?php
					if ( ! empty( $chapter['aside'] ) ) :
						?>
						<p class="sr2-immersive__aside"><?php echo esc_html( $chapter['aside'] ); ?></p><?php endif; ?>
				</div>
			</article>
		<?php endforeach; ?>
	</div>

	<section class="sr2-immersive__portal" aria-labelledby="immersive-portal-title">
		<p class="sr2-immersive__eyebrow"><?php esc_html_e( 'The story continues in the collection', 'skyyrose-flagship-2' ); ?></p>
		<h2 id="immersive-portal-title"><?php echo esc_html( $args['exit_title'] ?? __( 'Carry the world with you.', 'skyyrose-flagship-2' ) ); ?></h2>
		<p><?php echo esc_html( $args['exit_copy'] ?? '' ); ?></p>
		<div class="sr2-immersive__portal-actions">
			<a class="sr2-immersive__portal-link" href="<?php echo esc_url( skyyrose2_collection_url( $collection_slug ) ); ?>"><?php echo esc_html( sprintf( __( 'Enter the %s collection', 'skyyrose-flagship-2' ), $collection_name ) ); ?><span aria-hidden="true">→</span></a>
			<a class="sr2-immersive__portal-link" href="<?php echo esc_url( skyyrose2_shop_url() ); ?>"><?php esc_html_e( 'Shop all pieces', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a>
		</div>
	</section>

	<script type="application/json" class="sr2-immersive__config"><?php echo wp_json_encode( $scene_payload, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT ); ?></script>
</main>
<?php
get_footer();
