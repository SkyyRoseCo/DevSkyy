<?php
/**
 * Entry through three approved final scene references.
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
		$world_scenes = skyyrose2_collection_commerce_scenes( $world_slug );
		$world_scene  = $world_scenes[0] ?? array();
		if ( empty( $world_scene['hero_composed'] ) ) {
			continue;
		}
		?>
		<div class="sr2-recovery-home-world" style="--scene-ratio: <?php echo esc_attr( (string) ( absint( $world_scene['width'] ) / max( 1, absint( $world_scene['height'] ) ) ) ); ?>;" data-collection="<?php echo esc_attr( $world_slug ); ?>">
			<?php
			get_template_part(
				'template-parts/commerce/hero-composed-scene',
				null,
				array(
					'scene'      => $world_scene,
					'collection' => $world_slug,
					'index'      => $world_index,
				)
			);
			?>
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
