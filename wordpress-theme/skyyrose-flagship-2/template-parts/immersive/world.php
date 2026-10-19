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
$immersive_dependencies = array( 'skyyrose2-theme' );
if ( ! ( function_exists( 'is_checkout' ) && is_checkout() ) ) {
	$immersive_dependencies[] = skyyrose2_three_core_handle();
}
wp_enqueue_script( 'skyyrose2-immersive', SKYYROSE2_URI . '/assets/js/immersive' . $js_suffix . '.js', $immersive_dependencies, SKYYROSE2_VERSION, true );

// Resolve the existing canonical collection/placement binding. A generic media
// URI, a card approval or a filename cannot grant a hero/story placement.
$entry_media = skyyrose2_collection_media( $collection_slug, 'collection_hero' );
$story_media = skyyrose2_collection_media( $collection_slug, 'collection_story' );
$poster_uri = $entry_media['src'] ?? '';
$poster_available = '' !== $poster_uri;

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
	data-scene-state="<?php echo $poster_available ? 'poster-loading' : 'poster-unavailable'; ?>"
	data-poster-state="<?php echo $poster_available ? 'loading' : 'unavailable'; ?>"
	data-correlation-id="<?php echo esc_attr( $correlation_id ); ?>"
	style="--sr2-immersive-accent: <?php echo esc_attr( $accent ); ?>; --sr2-immersive-accent-rgb: <?php echo esc_attr( $accent_rgb ); ?>;">
	<div class="sr2-immersive__progress" aria-hidden="true"><span></span></div>

	<section class="sr2-immersive__entry sr2-arrival" id="world-entry" aria-labelledby="immersive-world-title">
		<div class="sr2-immersive__poster sr2-arrival__media" aria-hidden="true">
			<?php if ( $poster_available ) : ?>
			<?php echo skyyrose2_collection_media_markup( $entry_media, 'eager' ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escaped media renderer. ?>
			<?php endif; ?>
		</div>
		<canvas class="sr2-immersive__canvas" width="1280" height="720" aria-hidden="true"></canvas>
		<div class="sr2-immersive__entry-veil sr2-arrival__veil" aria-hidden="true"></div>
		<div class="sr2-immersive__entry-copy sr2-arrival__copy">
			<p class="sr2-immersive__kicker sr2-eyebrow"><?php echo esc_html( $kicker ); ?></p>
			<h1 id="immersive-world-title" class="sr2-immersive__sr-title"><?php echo esc_html( $collection_name . ': ' . $world_name ); ?></h1>
			<p class="sr2-immersive__direction sr2-lede"><?php echo esc_html( $direction ); ?></p>
			<div class="sr2-immersive__portal-actions sr2-arrival__actions">
				<a class="sr2-immersive__enter sr2-control sr2-control--primary" href="#chapter-<?php echo esc_attr( sanitize_key( $chapters[0]['id'] ?? 'one' ) ); ?>"><?php esc_html_e( 'Enter the story', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↓</span></a>
				<a class="sr2-immersive__enter sr2-editorial-link" href="<?php echo esc_url( skyyrose2_collection_url( $collection_slug ) ); ?>#shop"><?php esc_html_e( 'Shop collection', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a>
			</div>
		</div>
		<p class="sr2-immersive__scene-status <?php echo $poster_available ? 'screen-reader-text' : 'sr2-immersive__noscript'; ?>" aria-live="polite"><?php echo esc_html( $poster_available ? __( 'Loading the story scene.', 'skyyrose-flagship-2' ) : __( 'Scene imagery is unavailable. Continue with the story below.', 'skyyrose-flagship-2' ) ); ?></p>
		<noscript><p class="sr2-immersive__noscript"><?php esc_html_e( 'Read the story and explore the collection below. Motion is optional.', 'skyyrose-flagship-2' ); ?></p></noscript>
	</section>

	<nav class="sr2-immersive__chapter-nav" aria-label="<?php esc_attr_e( 'Story chapters', 'skyyrose-flagship-2' ); ?>">
		<p class="sr2-immersive__chapter-mark sr2-eyebrow sr2-eyebrow--engraved" aria-hidden="true"><?php echo esc_html( sprintf( '%02d', count( $chapters ) ) ); ?></p>
		<ol>
			<?php foreach ( $chapters as $index => $chapter ) : ?>
				<?php $chapter_id = sanitize_key( $chapter['id'] ?? 'chapter-' . ( $index + 1 ) ); ?>
				<li><a href="#chapter-<?php echo esc_attr( $chapter_id ); ?>"<?php echo 0 === $index ? ' aria-current="step"' : ''; ?>><span class="sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( sprintf( '%02d', $index + 1 ) ); ?></span><?php echo esc_html( $chapter['label'] ?? '' ); ?></a></li>
			<?php endforeach; ?>
		</ol>
	</nav>

	<section class="sr2-immersive__prologue sr2-band" aria-labelledby="immersive-prologue-title">
		<div class="sr2-band__head">
			<div>
				<p class="sr2-immersive__eyebrow sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( $collection_name ); ?></p>
				<h2 id="immersive-prologue-title" class="sr2-title-chapter"><?php echo esc_html( $world_name ); ?></h2>
				<p class="sr2-lede"><?php echo esc_html( $manifesto ); ?></p>
			</div>
		</div>
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
			$relative      = ( $is_scroll ? 'assets/scroll-world/' : 'assets/sot/' ) . $chapter_image;
			$record        = skyyrose2_media_inventory()['assets'][ $relative ] ?? array();
			$image_uri     = array( $collection_slug ) === ( $record['collections'] ?? null ) ? skyyrose2_media_uri( $relative, 'collection_story' ) : '';
			$image_exists  = $chapter_image && '' !== $image_uri && file_exists( $image_path );
			$image_size    = $image_exists ? getimagesize( $image_path ) : false;
			$hotspots      = isset( $chapter['hotspots'] ) && is_array( $chapter['hotspots'] ) ? $chapter['hotspots'] : array();
			$scene_product_skus = $image_exists ? ( $record['skus'] ?? array() ) : array();
			$scene_product_links = '';
			$related_product_links = '';
			$chapter_title = 'immersive-chapter-' . $chapter_id . '-title';
			?>
			<article class="sr2-immersive__chapter sr2-chapter<?php echo 1 === $index % 2 ? ' sr2-chapter--flip' : ''; ?>" id="chapter-<?php echo esc_attr( $chapter_id ); ?>" data-chapter="<?php echo esc_attr( $chapter_id ); ?>" data-index="<?php echo esc_attr( (string) $index ); ?>" data-original-scene-available="<?php echo $image_exists ? 'true' : 'false'; ?>" aria-labelledby="<?php echo esc_attr( $chapter_title ); ?>">
				<div class="sr2-immersive__chapter-media sr2-chapter__scene">
					<?php if ( $image_exists ) : ?>
						<img src="<?php echo esc_url( $image_uri ); ?>"
							alt="<?php echo esc_attr( $chapter['alt'] ?? $chapter['label'] ?? '' ); ?>"
							data-media-role="collection_story" data-media-skus="<?php echo esc_attr( wp_json_encode( $scene_product_skus ) ); ?>"
							width="<?php echo esc_attr( (string) ( $image_size ? $image_size[0] : 1344 ) ); ?>"
							height="<?php echo esc_attr( (string) ( $image_size ? $image_size[1] : 896 ) ); ?>"
							loading="lazy"
							decoding="async">
					<?php elseif ( ! empty( $story_media ) ) : ?>
						<?php echo skyyrose2_collection_media_markup( $story_media ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escaped media renderer. ?>
					<?php else : ?>
						<p class="sr2-immersive__image-unavailable"><?php esc_html_e( 'Scene imagery is unavailable. Continue with the story below.', 'skyyrose-flagship-2' ); ?></p>
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
						if ( ! $product || 'publish' !== $product->get_status() || ! $product->is_visible() || ! $approved_front ) {
							continue;
						}
						$hotspot_presentation = function_exists( 'skyyrose2_product_presentation' ) ? skyyrose2_product_presentation( $product ) : array();
						if ( empty( $hotspot_presentation ) || sanitize_title( $hotspot_presentation['collection'] ?? '' ) !== $collection_slug ) {
							continue;
						}
						$left = isset( $hotspot['left'] ) ? max( 8, min( 92, (float) $hotspot['left'] ) ) : 50;
						$top  = isset( $hotspot['top'] ) ? max( 12, min( 88, (float) $hotspot['top'] ) ) : 50;
						$is_depicted = in_array( $sku, $scene_product_skus, true );
						ob_start();
						?>
						<a class="<?php echo $is_depicted ? 'sr2-immersive__hotspot' : 'sr2-immersive__related-product'; ?>" href="<?php echo esc_url( get_permalink( $product->get_id() ) ); ?>"
							<?php if ( $is_depicted ) : ?>
							style="--hotspot-x: <?php echo esc_attr( (string) $left ); ?>%; --hotspot-y: <?php echo esc_attr( (string) $top ); ?>%;"
							data-scene-product="true"
							<?php endif; ?>
							data-sku="<?php echo esc_attr( $sku ); ?>"
							data-correlation-id="<?php echo esc_attr( $correlation_id ); ?>"
							aria-label="<?php echo esc_attr( sprintf( __( 'Explore %s', 'skyyrose-flagship-2' ), $product->get_name() ) ); ?>">
							<span class="sr2-immersive__hotspot-media">
								<?php if ( $approved_front ) : ?>
									<img class="sr2-immersive__hotspot-image" src="<?php echo esc_url( $approved_front['card_src'] ?? $approved_front['src'] ); ?>" srcset="<?php echo esc_attr( $approved_front['srcset'] ?? '' ); ?>" sizes="(max-width: 47.99em) 5.5rem, clamp(11rem, 16vw, 16rem)" alt="<?php echo esc_attr( $approved_front['alt'] ); ?>" width="<?php echo esc_attr( (string) $approved_front['width'] ); ?>" height="<?php echo esc_attr( (string) $approved_front['height'] ); ?>" loading="lazy" decoding="async">
								<?php endif; ?>
							</span>
							<span class="sr2-immersive__hotspot-copy"><small><?php echo esc_html( $is_depicted ? __( 'Piece in this scene', 'skyyrose-flagship-2' ) : __( 'Explore collection piece', 'skyyrose-flagship-2' ) ); ?></small><strong><?php echo esc_html( $product->get_name() ); ?></strong><em><?php esc_html_e( 'View the product', 'skyyrose-flagship-2' ); ?> →</em></span>
						</a>
						<?php
						if ( $is_depicted ) { $scene_product_links .= ob_get_clean(); } else { $related_product_links .= ob_get_clean(); }
						?>
					<?php endforeach; ?>
					<?php echo $scene_product_links; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escaped markup above. ?>
				</div>
				<div class="sr2-immersive__chapter-copy sr2-chapter__band">
					<div class="sr2-chapter__copy">
						<p class="sr2-immersive__chapter-number sr2-chapter__index sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( sprintf( '%02d / %02d', $index + 1, count( $chapters ) ) ); ?></p>
						<h2 id="<?php echo esc_attr( $chapter_title ); ?>" class="sr2-title-chapter"><?php echo esc_html( $chapter['label'] ?? '' ); ?></h2>
						<p class="sr2-lede"><?php echo esc_html( $chapter['copy'] ?? '' ); ?></p>
						<?php if ( ! empty( $chapter['aside'] ) ) : ?>
							<p class="sr2-immersive__aside"><?php echo esc_html( $chapter['aside'] ); ?></p>
						<?php endif; ?>
						<?php if ( $related_product_links ) : ?>
						<nav class="sr2-immersive__related-products" aria-label="<?php esc_attr_e( 'Related collection pieces', 'skyyrose-flagship-2' ); ?>"><?php echo $related_product_links; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escaped markup above. ?></nav>
						<?php endif; ?>
					</div>
				</div>
			</article>
		<?php endforeach; ?>
	</div>

	<section class="sr2-immersive__portal sr2-band" aria-labelledby="immersive-portal-title">
		<div class="sr2-band__head">
			<div>
				<p class="sr2-immersive__eyebrow sr2-eyebrow sr2-eyebrow--engraved"><?php esc_html_e( 'The story continues in the collection', 'skyyrose-flagship-2' ); ?></p>
				<h2 id="immersive-portal-title" class="sr2-title-chapter"><?php echo esc_html( $args['exit_title'] ?? __( 'Carry the world with you.', 'skyyrose-flagship-2' ) ); ?></h2>
				<p class="sr2-lede"><?php echo esc_html( $args['exit_copy'] ?? '' ); ?></p>
				<div class="sr2-immersive__portal-actions">
					<a class="sr2-immersive__portal-link sr2-control sr2-control--primary" href="<?php echo esc_url( skyyrose2_collection_url( $collection_slug ) ); ?>"><?php echo esc_html( sprintf( __( 'Enter the %s collection', 'skyyrose-flagship-2' ), $collection_name ) ); ?><span aria-hidden="true">→</span></a>
					<a class="sr2-immersive__portal-link sr2-editorial-link" href="<?php echo esc_url( skyyrose2_shop_url() ); ?>"><?php esc_html_e( 'Shop all pieces', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a>
				</div>
			</div>
		</div>
	</section>

	<script type="application/json" class="sr2-immersive__config"><?php echo wp_json_encode( $scene_payload, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT ); ?></script>
</main>
<?php
get_footer();
