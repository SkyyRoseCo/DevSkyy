<?php
/**
 * Garment-led collection story using unchanged current registry front pixels.
 * Merchandising choices here are presentation only; product facts remain live.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;
$editorial_slug       = $args['slug'] ?? '';
$editorial_collection = $args['collection'] ?? array();
$editorial_registry   = skyyrose2_presentation_registry();
$editorial_seed       = $editorial_registry['collections'][ $editorial_slug ]['story']['seed'] ?? '';
$editorial_seed       = is_string( $editorial_seed ) ? $editorial_seed : '';
// The generated consumer carries the reviewed lead selection and current role.
$editorial_lead = $editorial_registry['collections'][ $editorial_slug ]['editorial']['lead_sku'] ?? '';
if ( ! is_string( $editorial_lead ) || '' === $editorial_lead || empty( $editorial_collection['name'] ) ) {
	return;
}
$editorial_pieces = array();
foreach ( array( $editorial_lead ) as $editorial_sku ) {
	foreach ( $args['products'] ?? array() as $editorial_product ) {
		if ( ! is_a( $editorial_product, 'WC_Product' ) || ! $editorial_product->is_visible() || sanitize_key( $editorial_product->get_sku() ) !== $editorial_sku ) {
			continue;
		}
		$editorial_record = skyyrose2_product_presentation( $editorial_product );
		if ( $editorial_slug !== ( $editorial_record['collection'] ?? '' ) ) {
			continue;
		}
		// The generated SOT consumer binds the exact current source. Historical
		// card approvals cannot substitute for a missing or changed front here.
		$editorial_front = $editorial_record['editorial_front'] ?? array();
		if ( ! is_array( $editorial_front ) ) {
			continue;
		}
		$editorial_path  = $editorial_front['src'] ?? '';
		$editorial_hash  = $editorial_front['sha256'] ?? '';
		if (
			! is_string( $editorial_path ) ||
			! preg_match( '#^assets/[a-zA-Z0-9_./-]+\.(?:webp|png|jpe?g)$#D', $editorial_path ) ||
			false !== strpos( $editorial_path, '..' ) ||
			! is_string( $editorial_hash ) ||
			! preg_match( '/^[a-f0-9]{64}$/D', $editorial_hash ) ||
			$editorial_hash !== ( $editorial_front['source_sha256'] ?? '' ) ||
			'card_front' !== ( $editorial_front['role'] ?? '' ) ||
			(int) ( $editorial_front['width'] ?? 0 ) < 1 ||
			(int) ( $editorial_front['height'] ?? 0 ) < 1 ||
			! is_string( $editorial_front['alt'] ?? null )
		) {
			continue;
		}
		$editorial_asset = realpath( SKYYROSE2_DIR . '/' . $editorial_path );
		$editorial_root  = realpath( SKYYROSE2_DIR . '/assets' );
		if ( ! $editorial_asset || ! $editorial_root || ! str_starts_with( $editorial_asset, $editorial_root . DIRECTORY_SEPARATOR ) || ! is_file( $editorial_asset ) || ! is_readable( $editorial_asset ) ) {
			continue;
		}
		$editorial_actual_hash = hash_file( 'sha256', $editorial_asset );
		if ( ! skyyrose2_media_path_allowed( $editorial_path, 'card_front', $editorial_sku ) ) { continue; }
		$editorial_dimensions  = getimagesize( $editorial_asset );
		if ( ! is_string( $editorial_actual_hash ) || ! hash_equals( $editorial_hash, $editorial_actual_hash ) || ! $editorial_dimensions || (int) $editorial_front['width'] !== $editorial_dimensions[0] || (int) $editorial_front['height'] !== $editorial_dimensions[1] ) {
			continue;
		}
		$editorial_front['src']    = SKYYROSE2_URI . '/' . $editorial_path;
		$editorial_front['width']  = $editorial_dimensions[0];
		$editorial_front['height'] = $editorial_dimensions[1];
		$editorial_delivery = skyyrose2_approved_card_front( $editorial_product );
		if ( ( $editorial_delivery['path'] ?? '' ) === $editorial_path && ( $editorial_delivery['sha256'] ?? '' ) === $editorial_hash ) {
			$editorial_front['delivery'] = $editorial_delivery;
		}
		$editorial_pieces[] = array( 'product' => $editorial_product, 'front' => $editorial_front );
		break;
	}
}
$editorial_shop_url = $args['shop_url'] ?? add_query_arg( 'product_cat', $editorial_slug, skyyrose2_shop_url() );
$editorial_count    = count( $editorial_pieces );
?>
<section id="world" class="sr2-band sr2-fashion-editorial" data-collection="<?php echo esc_attr( $editorial_slug ); ?>" data-editorial-count="<?php echo esc_attr( (string) $editorial_count ); ?>" data-editorial-state="<?php echo $editorial_count ? 'ready' : 'missing-current-portrait'; ?>" aria-labelledby="sr2-fashion-editorial-title" tabindex="-1">
	<header class="sr2-fashion-editorial__story">
		<p class="sr2-fashion-editorial__index sr2-eyebrow"><?php echo esc_html( $editorial_collection['shop_kicker'] ); ?></p>
		<h2 id="sr2-fashion-editorial-title" class="sr2-title-chapter"><?php
		/* translators: %s: collection name. */
		echo esc_html( sprintf( __( '%s — the pieces', 'skyyrose-flagship-2' ), $editorial_collection['name'] ) );
		?></h2>
		<?php if ( $editorial_seed ) : ?><p class="sr2-lede"><?php echo esc_html( $editorial_seed ); ?></p><?php endif; ?>
	</header>
	<?php foreach ( $editorial_pieces as $editorial_index => $editorial_piece ) : ?>
		<?php
		$editorial_product = $editorial_piece['product'];
		$editorial_front   = $editorial_piece['front'];
		$editorial_caption = 'sr2-fashion-caption-' . sanitize_html_class( $editorial_product->get_sku() );
		?>
		<a class="sr2-fashion-editorial__piece sr2-fashion-editorial__product<?php echo 0 === $editorial_index ? ' sr2-fashion-editorial__piece--lead' : ' sr2-fashion-editorial__piece--support'; ?>" data-editorial-sku="<?php echo esc_attr( $editorial_product->get_sku() ); ?>" href="<?php echo esc_url( $editorial_product->get_permalink() ); ?>" aria-labelledby="<?php echo esc_attr( $editorial_caption ); ?>">
			<figure>
					<img src="<?php echo esc_url( $editorial_front['delivery']['display_src'] ?? $editorial_front['src'] ); ?>" srcset="<?php echo esc_attr( $editorial_front['delivery']['srcset'] ?? '' ); ?>" sizes="(max-width: 47.99em) calc(100vw - 2rem), (max-width: 74.99em) 55vw, 660px" width="<?php echo esc_attr( (string) $editorial_front['width'] ); ?>" height="<?php echo esc_attr( (string) $editorial_front['height'] ); ?>" alt="<?php echo esc_attr( $editorial_front['alt'] ); ?>" loading="lazy" decoding="async">
				<figcaption id="<?php echo esc_attr( $editorial_caption ); ?>"><span><?php echo esc_html( $editorial_product->get_name() ); ?></span><span aria-hidden="true">↗</span></figcaption>
			</figure>
		</a>
	<?php endforeach; ?>
	<?php
	$editorial_scene = $editorial_registry['collections'][ $editorial_slug ]['editorial']['scene'] ?? array();
	if ( $editorial_count && is_array( $editorial_scene ) && ( $editorial_scene['sku'] ?? '' ) === $editorial_lead && 'collection_scene_back' === ( $editorial_scene['role'] ?? '' ) ) :
		$editorial_scene_path = $editorial_scene['src'] ?? '';
		$editorial_scene_uri = is_string( $editorial_scene_path ) ? skyyrose2_media_uri( $editorial_scene_path, 'collection_scene_back', $editorial_lead ) : '';
		$editorial_scene_record = skyyrose2_media_inventory()['assets'][ $editorial_scene_path ] ?? array();
		$editorial_scene_size = $editorial_scene_uri ? getimagesize( SKYYROSE2_DIR . '/' . $editorial_scene_path ) : false;
		if ( $editorial_scene_uri && $editorial_scene_size && ( $editorial_scene_record['sha256'] ?? '' ) === ( $editorial_scene['sha256'] ?? '' ) && array( $editorial_slug ) === ( $editorial_scene_record['collections'] ?? null ) ) :
			$editorial_scene_product = $editorial_pieces[0]['product'];
			$editorial_scene_caption = 'sr2-fashion-caption-' . sanitize_html_class( $editorial_lead ) . '-back';
	?>
		<a class="sr2-fashion-editorial__piece sr2-fashion-editorial__product sr2-fashion-editorial__piece--support" data-editorial-sku="<?php echo esc_attr( $editorial_lead ); ?>" data-editorial-view="back" href="<?php echo esc_url( $editorial_scene_product->get_permalink() ); ?>" aria-labelledby="<?php echo esc_attr( $editorial_scene_caption ); ?>">
			<figure>
				<img src="<?php echo esc_url( $editorial_scene_uri ); ?>" width="<?php echo esc_attr( (string) $editorial_scene_size[0] ); ?>" height="<?php echo esc_attr( (string) $editorial_scene_size[1] ); ?>" alt="<?php echo esc_attr( $editorial_scene_product->get_name() . ' — back view' ); ?>" loading="lazy" decoding="async" style="object-fit:contain">
				<figcaption id="<?php echo esc_attr( $editorial_scene_caption ); ?>"><span><?php echo esc_html( $editorial_scene_product->get_name() ); ?></span><span aria-hidden="true">↗</span></figcaption>
			</figure>
		</a>
	<?php endif; endif; ?>
	<div class="sr2-fashion-editorial__shop"><a class="sr2-editorial-link" href="<?php echo esc_url( $editorial_shop_url ); ?>"><?php echo esc_html( $editorial_collection['hero_cta'] ); ?><span aria-hidden="true">↗</span></a><a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_immersive_url( $editorial_slug ) ); ?>"><?php esc_html_e( 'Enter the full scene', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a></div>
</section>
