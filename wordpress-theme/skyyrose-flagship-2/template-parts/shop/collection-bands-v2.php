<?php
/**
 * Unfiltered Shop as cinema bands: one band per collection, in house order.
 *
 * Each band pins its founder-authorized collection film full-bleed while the
 * collection's pieces travel across it on a horizontal snap rail. A collection
 * without a granted film (Kids Capsule, or any film the media gate withholds)
 * opens on a type-led header with the same structure. Cards are rendered only by
 * the native card pipeline (content-product.php → product-card.php).
 *
 * Arguments:
 * - groups    array<string, array{collection: array, products: WC_Product[]}>, keyed by
 *             skyyrose2_collections() slug. Unknown slugs are ignored; order is the house order.
 * - ungrouped WC_Product[] (optional) visible pieces with no collection; rendered in a final
 *             house band so every published piece stays reachable.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$bands_collections = skyyrose2_collections();
$bands_groups      = isset( $args['groups'] ) && is_array( $args['groups'] ) ? $args['groups'] : array();
// Count only cards the pipeline renders: product-card.php returns early for invisible products
// and for transaction pre-orders in a standard listing, so the header count matches the rail.
$bands_visible     = static function ( $items ) {
	return array_values(
		array_filter(
			is_array( $items ) ? $items : array(),
			static function ( $item ) {
				return is_a( $item, 'WC_Product' ) && $item->is_visible()
					&& ! ( function_exists( 'skyyrose2_is_transaction_preorder_product' ) && skyyrose2_is_transaction_preorder_product( $item ) );
			}
		)
	);
};

$bands = array();
foreach ( $bands_collections as $bands_slug => $bands_house_record ) {
	if ( ! isset( $bands_groups[ $bands_slug ] ) || ! is_array( $bands_groups[ $bands_slug ] ) ) {
		continue;
	}
	$bands_record = isset( $bands_groups[ $bands_slug ]['collection'] ) && is_array( $bands_groups[ $bands_slug ]['collection'] ) ? $bands_groups[ $bands_slug ]['collection'] : $bands_house_record;
	$bands[]      = array(
		'slug'     => $bands_slug,
		'name'     => (string) ( $bands_record['name'] ?? $bands_house_record['name'] ),
		'kicker'   => (string) ( $bands_record['shop_kicker'] ?? '' ),
		'heading'  => (string) ( $bands_record['shop_heading'] ?? $bands_record['name'] ?? '' ),
		'intro'    => (string) ( $bands_record['shop_intro'] ?? '' ),
		'url'      => skyyrose2_shop_category_url( $bands_slug ),
		'products' => $bands_visible( $bands_groups[ $bands_slug ]['products'] ?? array() ),
	);
}
$bands_ungrouped = $bands_visible( $args['ungrouped'] ?? array() );
if ( $bands_ungrouped ) {
	$bands[] = array(
		'slug'     => 'house',
		'name'     => __( 'The House Edit', 'skyyrose-flagship-2' ),
		'kicker'   => __( 'The House Edit', 'skyyrose-flagship-2' ),
		'heading'  => __( 'All pieces', 'skyyrose-flagship-2' ),
		'intro'    => '',
		'url'      => '',
		'products' => $bands_ungrouped,
	);
}
if ( ! $bands ) {
	return;
}

// Every film role is resolved through the media gate; an empty URI is the designed type-led state.
foreach ( $bands as $bands_index => $bands_band ) {
	$bands_film = array();
	if ( 'house' !== $bands_band['slug'] && $bands_band['products'] ) {
		$bands_root   = 'assets/video/collection-heroes/approved/' . $bands_band['slug'] . '/cinema-20261008/';
		$bands_poster = skyyrose2_media_uri( $bands_root . 'poster.webp', 'collection_hero_poster' );
		if ( $bands_poster ) {
			$bands_film = array(
				'poster' => $bands_poster,
				'webm'   => skyyrose2_media_uri( $bands_root . 'hero.webm', 'collection_hero_video' ),
				'mp4'    => skyyrose2_media_uri( $bands_root . 'hero.mp4', 'collection_hero_video' ),
			);
		}
	}
	$bands[ $bands_index ]['film'] = $bands_film;
}

// The lede (intro and "View all") is rendered at two placements and CSS shows exactly one
// per breakpoint (display: none on the other): under the title from 48em, after the rail
// below it. DOM order, focus order and visual order then match at every width.
$bands_lede = static function ( $band, $placement ) {
	if ( '' === $band['intro'] && ! $band['url'] ) {
		return;
	}
	?>
	<div class="sr2-bands-v2__lede sr2-bands-v2__lede--<?php echo esc_attr( $placement ); ?>">
		<?php if ( '' !== $band['intro'] ) : ?>
			<p class="sr2-bands-v2__intro"><?php echo esc_html( $band['intro'] ); ?></p>
		<?php endif; ?>
		<?php if ( $band['url'] ) : ?>
			<a class="sr2-editorial-link sr2-bands-v2__all" href="<?php echo esc_url( $band['url'] ); ?>"><?php /* translators: %s: collection name. */ echo esc_html( sprintf( __( 'View all %s', 'skyyrose-flagship-2' ), $band['name'] ) ); ?><span aria-hidden="true">→</span></a>
		<?php endif; ?>
	</div>
	<?php
};

$bands_total           = count( $bands );
$bands_previous_post   = $GLOBALS['post'] ?? null;
$bands_previous_global = $GLOBALS['product'] ?? null;
// One continuous native loop: only the first card of the first band is an eager candidate.
wc_set_loop_prop( 'loop', 0 );
?>
<div class="sr2-bands-v2" data-sr2bv2>
	<?php
	foreach ( $bands as $bands_index => $bands_band ) :
		$bands_slug     = $bands_band['slug'];
		$bands_id       = 'sr2-bands-v2-' . $bands_slug;
		$bands_film     = $bands_band['film'];
		$bands_has_film = (bool) $bands_film;
		$bands_motion   = $bands_has_film && ( $bands_film['webm'] || $bands_film['mp4'] );
		$bands_count    = count( $bands_band['products'] );
		$bands_next     = $bands[ $bands_index + 1 ] ?? null;
		$bands_numeral  = sprintf( '%02d', $bands_index + 1 );
		?>
	<section id="<?php echo esc_attr( $bands_id ); ?>" class="sr2-bands-v2__band" data-sr2bv2-band data-collection="<?php echo esc_attr( $bands_slug ); ?>" data-film="<?php echo $bands_has_film ? 'cinema' : 'type'; ?>" aria-labelledby="<?php echo esc_attr( $bands_id . '-name' ); ?>">
		<div class="sr2-bands-v2__film" aria-hidden="true">
			<?php if ( $bands_has_film ) : ?>
				<img class="sr2-bands-v2__poster" data-sr2bv2-poster src="<?php echo esc_url( $bands_film['poster'] ); ?>" width="1440" height="810" alt="" loading="<?php echo 0 === $bands_index ? 'eager' : 'lazy'; ?>" decoding="async">
				<?php if ( $bands_motion ) : ?>
					<video class="sr2-bands-v2__video" data-sr2bv2-video muted playsinline loop preload="none" tabindex="-1" disablepictureinpicture>
						<?php if ( $bands_film['webm'] ) : ?>
							<source data-src="<?php echo esc_url( $bands_film['webm'] ); ?>" type="video/webm">
						<?php endif; ?>
						<?php if ( $bands_film['mp4'] ) : ?>
							<source data-src="<?php echo esc_url( $bands_film['mp4'] ); ?>" type="video/mp4">
						<?php endif; ?>
					</video>
				<?php endif; ?>
			<?php else : ?>
				<span class="sr2-bands-v2__type-mark"><?php echo esc_html( $bands_band['name'] ); ?></span>
			<?php endif; ?>
			<span class="sr2-bands-v2__scrim"></span>
			<span class="sr2-bands-v2__dim"></span>
		</div>
		<div class="sr2-bands-v2__content">
			<header class="sr2-bands-v2__head">
				<div class="sr2-bands-v2__copy">
					<p class="sr2-bands-v2__index"><span class="sr2-bands-v2__numeral" aria-hidden="true"><?php echo esc_html( $bands_numeral ); ?></span><span class="sr2-bands-v2__of" aria-hidden="true"><?php echo esc_html( sprintf( '/ %02d', $bands_total ) ); ?></span><span id="<?php echo esc_attr( $bands_id . '-name' ); ?>" class="sr2-bands-v2__name"><?php echo esc_html( $bands_band['name'] ); ?></span></p>
					<?php if ( '' !== $bands_band['kicker'] && $bands_band['kicker'] !== $bands_band['name'] ) : ?>
						<p class="sr2-bands-v2__kicker"><?php echo esc_html( $bands_band['kicker'] ); ?></p>
					<?php endif; ?>
					<h2 class="sr2-bands-v2__title"><?php echo esc_html( $bands_band['heading'] ); ?></h2>
				</div>
			</header>
			<?php $bands_lede( $bands_band, 'head' ); ?>
			<?php if ( $bands_count ) : ?>
				<div class="sr2-bands-v2__stage">
					<div class="sr2-bands-v2__bar">
						<p class="sr2-bands-v2__count"><?php /* translators: %d: number of pieces in the collection. */ echo esc_html( sprintf( _n( '%d piece', '%d pieces', $bands_count, 'skyyrose-flagship-2' ), $bands_count ) ); ?></p>
						<div class="sr2-bands-v2__controls" data-sr2bv2-controls hidden>
							<?php if ( $bands_motion ) : ?>
								<button type="button" class="sr2-bands-v2__motion" data-sr2bv2-motion aria-pressed="false" data-label-pause="<?php esc_attr_e( 'Pause motion', 'skyyrose-flagship-2' ); ?>" data-label-play="<?php esc_attr_e( 'Play motion', 'skyyrose-flagship-2' ); ?>" data-label-failed="<?php esc_attr_e( 'Film unavailable', 'skyyrose-flagship-2' ); ?>" hidden><?php esc_html_e( 'Play motion', 'skyyrose-flagship-2' ); ?></button>
							<?php endif; ?>
							<button type="button" class="sr2-bands-v2__step" data-sr2bv2-prev aria-controls="<?php echo esc_attr( $bands_id . '-rail' ); ?>" aria-label="<?php /* translators: %s: collection name. */ echo esc_attr( sprintf( __( 'Previous %s piece', 'skyyrose-flagship-2' ), $bands_band['name'] ) ); ?>"><span aria-hidden="true">←</span></button>
							<output class="sr2-bands-v2__position" data-sr2bv2-position aria-live="polite"><?php echo esc_html( sprintf( '01 / %02d', $bands_count ) ); ?></output>
							<button type="button" class="sr2-bands-v2__step" data-sr2bv2-next aria-controls="<?php echo esc_attr( $bands_id . '-rail' ); ?>" aria-label="<?php /* translators: %s: collection name. */ echo esc_attr( sprintf( __( 'Next %s piece', 'skyyrose-flagship-2' ), $bands_band['name'] ) ); ?>"><span aria-hidden="true">→</span></button>
						</div>
					</div>
					<p id="<?php echo esc_attr( $bands_id . '-hint' ); ?>" class="screen-reader-text"><?php esc_html_e( 'Use the left and right arrow keys to move between pieces.', 'skyyrose-flagship-2' ); ?></p>
					<ul id="<?php echo esc_attr( $bands_id . '-rail' ); ?>" class="products sr2-bands-v2__rail" data-sr2bv2-rail aria-label="<?php /* translators: %s: collection name. */ echo esc_attr( sprintf( __( '%s pieces', 'skyyrose-flagship-2' ), $bands_band['name'] ) ); ?>" aria-describedby="<?php echo esc_attr( $bands_id . '-hint' ); ?>">
						<?php
						foreach ( $bands_band['products'] as $bands_product ) :
							$bands_post = get_post( $bands_product->get_id() );
							if ( ! $bands_post ) {
								continue;
							}
							$GLOBALS['post']    = $bands_post; // phpcs:ignore WordPress.WP.GlobalVariablesOverride.Prohibited
							$GLOBALS['product'] = $bands_product; // phpcs:ignore WordPress.WP.GlobalVariablesOverride.Prohibited
							setup_postdata( $bands_post );
							do_action( 'woocommerce_shop_loop' );
							wc_get_template_part( 'content', 'product' );
						endforeach;
						?>
					</ul>
				</div>
				<?php $bands_lede( $bands_band, 'after' ); ?>
				<?php if ( $bands_next ) : ?>
					<a class="sr2-bands-v2__handoff" data-sr2bv2-handoff href="<?php echo esc_url( '#sr2-bands-v2-' . $bands_next['slug'] ); ?>"><span class="sr2-bands-v2__handoff-label"><?php esc_html_e( 'Next', 'skyyrose-flagship-2' ); ?></span><span class="sr2-bands-v2__handoff-rule" aria-hidden="true"></span><span class="sr2-bands-v2__handoff-name"><span aria-hidden="true"><?php echo esc_html( sprintf( '%02d / ', $bands_index + 2 ) ); ?></span><?php echo esc_html( $bands_next['name'] ); ?></span></a>
				<?php endif; ?>
			<?php else : ?>
				<p class="sr2-bands-v2__quiet"><?php /* translators: %s: collection name. */ echo esc_html( sprintf( __( 'No %s pieces are published right now.', 'skyyrose-flagship-2' ), $bands_band['name'] ) ); ?></p>
				<?php $bands_lede( $bands_band, 'after' ); ?>
			<?php endif; ?>
		</div>
	</section>
	<?php endforeach; ?>
</div>
<?php
wp_reset_postdata();
$GLOBALS['post']    = $bands_previous_post; // phpcs:ignore WordPress.WP.GlobalVariablesOverride.Prohibited
$GLOBALS['product'] = $bands_previous_global; // phpcs:ignore WordPress.WP.GlobalVariablesOverride.Prohibited
