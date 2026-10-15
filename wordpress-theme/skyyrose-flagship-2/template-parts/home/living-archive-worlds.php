<?php
/**
 * Three current V2 collection entries. Retired motion sources cannot empty the rail.
 * The Heir retains a direct native destination.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;

$archive_worlds   = $args['collections'] ?? array();
$archive_defaults = skyyrose2_collections();
?>
<div class="sr2-recovery-collection-worlds" data-recovery-rail>
	<div class="sr2-recovery-controls" hidden><button type="button" data-recovery-prev aria-label="<?php esc_attr_e( 'Previous collection', 'skyyrose-flagship-2' ); ?>">←</button><span data-recovery-count aria-live="polite"></span><button type="button" data-recovery-next aria-label="<?php esc_attr_e( 'Next collection', 'skyyrose-flagship-2' ); ?>">→</button></div>
	<div class="sr2-recovered-worlds__rail" data-recovery-track tabindex="0" aria-label="<?php esc_attr_e( 'Approved collection worlds', 'skyyrose-flagship-2' ); ?>">
	<?php foreach ( array( 'signature', 'black-rose', 'love-hurts' ) as $world_index => $world_slug ) : ?>
		<?php
		$world_image = skyyrose2_collection_media( $world_slug, 'love-hurts' === $world_slug ? 'collection_story' : 'collection_hero' );
		if ( empty( $world_image['src'] ) ) {
			continue;
		}
		?>
		<div class="sr2-recovery-home-world" style="--scene-ratio: <?php echo esc_attr( (string) ( absint( $world_image['width'] ) / max( 1, absint( $world_image['height'] ) ) ) ); ?>;" data-collection="<?php echo esc_attr( $world_slug ); ?>" data-home-scene="<?php echo esc_attr( $world_slug ); ?>" data-scene-state="approved-v2-still">
			<figure class="sr2-hero-commerce__frame" style="--scene-aspect: <?php echo absint( $world_image['width'] ); ?> / <?php echo absint( $world_image['height'] ); ?>;">
				<?php echo skyyrose2_collection_media_markup( $world_image, 'lazy', '(max-width: 47.99em) calc(100vw - 2rem), 768px' ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- skyyrose2_collection_media_markup() escapes every attribute. ?>
			</figure>
			<a class="sr2-control sr2-control--secondary" href="<?php echo esc_url( skyyrose2_collection_url( $world_slug ) ); ?>"><?php
				echo esc_html(
					sprintf(
						__( 'Enter %s', 'skyyrose-flagship-2' ),
						$archive_worlds[ $world_slug ]['name'] ?? $archive_defaults[ $world_slug ]['name']
					)
				);
				?> ↗</a>
		</div>
	<?php endforeach; ?>
	</div>
	<p><a class="sr2-world-text-link" href="<?php echo esc_url( skyyrose2_collection_url( 'kids-capsule' ) ); ?>"><?php esc_html_e( 'The Heir / Discover Kids Capsule', 'skyyrose-flagship-2' ); ?> ↗</a></p>
</div>
