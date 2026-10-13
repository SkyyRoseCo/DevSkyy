<?php
/**
 * Cinematic chapters: four collections as four chapters of one story.
 *
 * Phase 1a — chapter registry, Story Thread, Prologue hero, art-directed hover
 * cards and the progressive media slot. Brand type, palette, logo and copy are
 * untouched: chapters re-use the locked collection accents and the existing
 * display/body/ui faces. Nothing here is a tagline; verbs are motion cues only.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/**
 * Chapter registry. Order is the story order; Chapter IV is always "play".
 *
 * @return array<int,array<string,string>>
 */
function skyyrose2_chapters() {
	$chapters = array(
		array(
			'slug'    => 'signature',
			'numeral' => 'I',
			'index'   => '1',
			'name'    => __( 'Signature', 'skyyrose-flagship-2' ),
			'verb'    => 'develop',
			'accent'  => '#d4af37',
			'rgb'     => '212 175 55',
			'light'   => 'golden-hour',
		),
		array(
			'slug'    => 'black-rose',
			'numeral' => 'II',
			'index'   => '2',
			'name'    => __( 'Black Rose', 'skyyrose-flagship-2' ),
			'verb'    => 'weave',
			'accent'  => '#c0c0c0',
			'rgb'     => '192 192 192',
			'light'   => 'midnight',
		),
		array(
			'slug'    => 'love-hurts',
			'numeral' => 'III',
			'index'   => '3',
			'name'    => __( 'Love Hurts', 'skyyrose-flagship-2' ),
			'verb'    => 'breathe',
			'accent'  => '#eb4666',
			'rgb'     => '235 70 102',
			'light'   => 'ember',
		),
		array(
			'slug'    => 'kids-capsule',
			'numeral' => 'IV',
			'index'   => '4',
			'name'    => __( 'Kids Capsule', 'skyyrose-flagship-2' ),
			'verb'    => 'play',
			'accent'  => '#b76e79',
			'rgb'     => '183 110 121',
			'light'   => 'playroom',
		),
	);

	foreach ( $chapters as $i => $chapter ) {
		$chapters[ $i ]['url'] = skyyrose2_immersive_url( $chapter['slug'] );
	}

	return $chapters;
}

/**
 * Whether this request carries the chapter shell (Story Thread + motion CSS/JS).
 * This file is loaded only by template-prologue.php, so the shell never reaches
 * existing heroes or product cards.
 *
 * @return bool
 */
function skyyrose2_chapters_enabled() {
	$enabled = is_page_template( 'template-prologue.php' );

	return (bool) apply_filters( 'skyyrose2_chapters_enabled', $enabled );
}

/** Enqueue chapter CSS/JS. Source edits require `npm run build:assets`. */
function skyyrose2_chapters_assets() {
	if ( ! skyyrose2_chapters_enabled() ) {
		return;
	}

	$suffix = skyyrose2_asset_suffix();
	$style  = '/assets/css/chapters' . $suffix . '.css';
	$script = '/assets/js/chapters' . $suffix . '.js';

	wp_enqueue_style( 'skyyrose2-chapters', SKYYROSE2_URI . $style, array( 'skyyrose2-theme' ), skyyrose2_asset_version( $style ) );
	wp_enqueue_script( 'skyyrose2-chapters', SKYYROSE2_URI . $script, array(), skyyrose2_asset_version( $script ), true );
	wp_script_add_data( 'skyyrose2-chapters', 'strategy', 'defer' );
}
add_action( 'wp_enqueue_scripts', 'skyyrose2_chapters_assets', 30 );

/**
 * Story Thread: persistent I · II · III · IV chapter indicator.
 *
 * @param string $current Current chapter slug, or '' when none.
 */
function skyyrose2_render_story_thread( $current = '' ) {
	$current = sanitize_key( $current );
	?>
	<nav class="sr2-thread" aria-label="<?php esc_attr_e( 'Story chapters', 'skyyrose-flagship-2' ); ?>" data-story-thread>
		<ol class="sr2-thread__list">
			<?php foreach ( skyyrose2_chapters() as $chapter ) : ?>
				<li class="sr2-thread__item" data-chapter="<?php echo esc_attr( $chapter['slug'] ); ?>" style="--chapter-accent: <?php echo esc_attr( $chapter['accent'] ); ?>;">
					<a class="sr2-thread__link" href="<?php echo esc_url( $chapter['url'] ); ?>"<?php echo $chapter['slug'] === $current ? ' aria-current="page"' : ''; ?> data-chapter-link>
						<span class="sr2-thread__numeral"><?php echo esc_html( $chapter['numeral'] ); ?></span>
						<span class="screen-reader-text"><?php echo esc_html( sprintf( /* translators: 1: chapter numeral, 2: collection name. */ __( 'Chapter %1$s: %2$s', 'skyyrose-flagship-2' ), $chapter['numeral'], $chapter['name'] ) ); ?></span>
					</a>
				</li>
			<?php endforeach; ?>
		</ol>
	</nav>
	<?php
}

/** Render the thread sitewide-on-opt-in, once, at the end of the body. */
function skyyrose2_story_thread_footer() {
	if ( ! skyyrose2_chapters_enabled() ) {
		return;
	}
	skyyrose2_render_story_thread();
}
add_action( 'wp_footer', 'skyyrose2_story_thread_footer', 20 );

/**
 * Progressive media slot. One component for every product surface: it renders
 * the best tier supplied and upgrades itself when richer sources exist.
 *
 * Tiers, low to high: image → sequence → depth → model. Only `image` is
 * required; each richer tier is data-attribute metadata the runtime upgrades
 * to. An unauthorised image URL (empty string) renders no <img>, never a guess.
 *
 * @param array<string,mixed> $args image, alt, width, height, sequence[], depth, model{glb,usdz,impostor}, sku.
 * @return string Escaped HTML.
 */
function skyyrose2_media_slot( $args ) {
	$args = wp_parse_args(
		$args,
		array(
			'image'    => '',
			'alt'      => '',
			'width'    => 0,
			'height'   => 0,
			'sequence' => array(),
			'depth'    => '',
			'model'    => array(),
			'sku'      => '',
		)
	);

	$tier  = 'image';
	$attrs = array();
	$seq   = array_values( array_filter( array_map( 'esc_url_raw', (array) $args['sequence'] ) ) );
	$model = (array) $args['model'];
	$glb   = isset( $model['glb'] ) ? esc_url_raw( $model['glb'] ) : '';

	if ( count( $seq ) > 1 ) {
		$tier                   = 'sequence';
		$attrs['data-sequence'] = wp_json_encode( $seq );
	}
	if ( $args['depth'] ) {
		$tier               = 'depth';
		$attrs['data-depth'] = esc_url_raw( $args['depth'] );
	}
	if ( $glb ) {
		$tier                = 'model';
		$attrs['data-glb']   = $glb;
		$attrs['data-usdz']  = isset( $model['usdz'] ) ? esc_url_raw( $model['usdz'] ) : '';
		$attrs['data-impostor'] = isset( $model['impostor'] ) ? esc_url_raw( $model['impostor'] ) : '';
	}
	if ( $args['sku'] ) {
		$attrs['data-sku'] = sanitize_key( $args['sku'] );
	}

	$html = '<div class="sr2-slot" data-media-slot data-tier="' . esc_attr( $tier ) . '"';
	foreach ( $attrs as $name => $value ) {
		if ( '' !== $value ) {
			$html .= ' ' . $name . '="' . esc_attr( $value ) . '"';
		}
	}
	$html .= '>';
	if ( $args['image'] ) {
		$html .= '<img class="sr2-slot__still" src="' . esc_url( $args['image'] ) . '" alt="' . esc_attr( $args['alt'] ) . '"'
			. ( $args['width'] ? ' width="' . absint( $args['width'] ) . '"' : '' )
			. ( $args['height'] ? ' height="' . absint( $args['height'] ) . '"' : '' )
			. ' loading="lazy" decoding="async">';
	}
	$html .= '</div>';

	return $html;
}
