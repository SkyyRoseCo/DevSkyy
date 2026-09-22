<?php
/** Homepage collection split: resolved approved scene, centered house edit, direct collection rail. */
defined( 'ABSPATH' ) || exit;

$collections = is_array( $args['collections'] ?? null ) ? $args['collections'] : array();
$scenes      = array_values( array_filter( (array) skyyrose2_collection_commerce_scenes( 'black-rose' ), static function ( $scene ) {
	return is_array( $scene ) && ! empty( $scene['hero_composed'] ) && skyyrose2_approved_scroll_world_scene( $scene, 'black-rose' );
} ) );
$scene       = $scenes[0] ?? array();
?>
<section id="sr2-archive-worlds" class="sr2-editorial-collection" aria-labelledby="sr2-editorial-collection-title" tabindex="-1">
	<figure class="sr2-editorial-collection__image">
		<?php if ( $scene ) : ?><img src="<?php echo esc_url( skyyrose2_collection_scene_uri( $scene ) ); ?>" width="<?php echo esc_attr( (string) absint( $scene['width'] ) ); ?>" height="<?php echo esc_attr( (string) absint( $scene['height'] ) ); ?>" alt="<?php echo esc_attr( $scene['direction'] ); ?>" loading="lazy" decoding="async"><?php else : ?><span class="sr2-editorial-collection__media-fallback"><?php esc_html_e( 'Explore the Black Rose collection.', 'skyyrose-flagship-2' ); ?></span><?php endif; ?>
	</figure>
	<div class="sr2-editorial-collection__copy">
		<p class="sr2-world-index"><?php esc_html_e( 'The collection', 'skyyrose-flagship-2' ); ?></p>
		<h2 id="sr2-editorial-collection-title"><?php esc_html_e( 'Designed for the worlds ahead.', 'skyyrose-flagship-2' ); ?></h2>
		<p><?php esc_html_e( 'Four expressions of the same house: memory, craft, movement, and the next generation in view.', 'skyyrose-flagship-2' ); ?></p>
		<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'collections' ) ); ?>"><?php esc_html_e( 'Explore all collections', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a>
	</div>
	<nav class="sr2-editorial-collection__rail" aria-label="<?php esc_attr_e( 'Shop by collection', 'skyyrose-flagship-2' ); ?>">
		<?php foreach ( array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ) as $slug ) : ?>
			<?php if ( empty( $collections[ $slug ] ) ) { continue; } ?>
			<a href="<?php echo esc_url( skyyrose2_collection_url( $slug ) ); ?>"><?php echo esc_html( $collections[ $slug ]['name'] ); ?></a>
		<?php endforeach; ?>
	</nav>
</section>
