<?php
/**
 * The three declared world scenes as full-bleed chapters: scene, then a band
 * with the founder's label and copy. Scene authority stays in skyyrose2_collections().
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;
$chapter_slug       = $args['slug'];
$chapter_collection = $args['collection'];
$chapter_scenes     = isset( $chapter_collection['world'] ) && is_array( $chapter_collection['world'] ) ? array_values( $chapter_collection['world'] ) : array();
$chapter_statement  = ! empty( $args['world_statement'] );
$chapter_total      = count( $chapter_scenes );
if ( ! $chapter_scenes ) {
	return;
}
?>
<div id="world" class="sr2-world-chapters" tabindex="-1">
	<?php foreach ( $chapter_scenes as $chapter_index => $chapter_scene ) : ?>
		<?php
		$chapter_number = $chapter_index + 1;
		$chapter_id     = 'sr2-world-chapter-' . $chapter_number . '-title';
		$chapter_path   = isset( $chapter_scene['source'] ) && 'scroll-world' === $chapter_scene['source']
			? SKYYROSE2_DIR . '/assets/scroll-world/' . ltrim( (string) $chapter_scene['image'], '/' )
			: SKYYROSE2_DIR . '/assets/sot/' . ltrim( (string) $chapter_scene['image'], '/' );
		$chapter_size   = is_file( $chapter_path ) ? getimagesize( $chapter_path ) : false;
		?>
		<section class="sr2-chapter sr2-world-chapter<?php echo 0 === $chapter_number % 2 ? ' sr2-chapter--flip' : ''; ?>" data-collection="<?php echo esc_attr( $chapter_slug ); ?>" aria-labelledby="<?php echo esc_attr( $chapter_id ); ?>">
			<figure class="sr2-chapter__scene sr2-image-reveal">
				<img src="<?php echo esc_url( skyyrose2_collection_scene_uri( $chapter_scene ) ); ?>" alt="" width="<?php echo esc_attr( (string) ( $chapter_size ? $chapter_size[0] : 1920 ) ); ?>" height="<?php echo esc_attr( (string) ( $chapter_size ? $chapter_size[1] : 1080 ) ); ?>" loading="lazy" decoding="async">
			</figure>
			<div class="sr2-chapter__band">
				<div class="sr2-chapter__copy">
					<p class="sr2-chapter__index sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( sprintf( '%02d', $chapter_number ) ); ?> / <?php echo esc_html( $chapter_collection['name'] ); ?></p>
					<h2 id="<?php echo esc_attr( $chapter_id ); ?>" class="sr2-title-chapter"><?php echo esc_html( $chapter_scene['label'] ); ?></h2>
					<p class="sr2-lede"><?php echo esc_html( $chapter_scene['copy'] ); ?></p>
					<?php if ( $chapter_number === $chapter_total ) : ?>
						<div class="sr2-world-chapter__actions">
							<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_immersive_url( $chapter_slug ) ); ?>"><?php esc_html_e( 'Enter the full scene', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a>
						</div>
					<?php endif; ?>
				</div>
				<?php if ( 1 === $chapter_number && $chapter_statement ) : ?>
					<div class="sr2-chapter__aside sr2-world-chapter__aside">
						<p class="sr2-world-chapter__statement"><?php echo esc_html( $chapter_collection['world_heading'] ); ?></p>
						<p class="sr2-lede"><?php echo esc_html( $chapter_collection['world_intro'] ); ?></p>
					</div>
				<?php endif; ?>
			</div>
		</section>
	<?php endforeach; ?>
</div>
