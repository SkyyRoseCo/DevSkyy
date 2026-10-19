<?php
/**
 * Collection code: the founder's headline and manifesto beside the lookbook
 * garment, closing on the invitation back to the edit.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;
$story       = $args['collection'];
$story_slug  = $args['slug'];
$story_image = skyyrose2_collection_media( $story_slug, 'collection_story' );
?>
<section id="origin" class="sr2-chapter sr2-world-origin" data-collection="<?php echo esc_attr( $story_slug ); ?>" aria-labelledby="sr2-world-origin-title" tabindex="-1">
	<div class="sr2-chapter__band">
		<div class="sr2-chapter__copy">
			<p class="sr2-chapter__index sr2-eyebrow sr2-eyebrow--engraved"><?php esc_html_e( 'Collection Code', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr2-world-origin-title" class="sr2-title-chapter"><?php echo esc_html( $story['headline'] ); ?></h2>
			<p class="sr2-lede sr2-world-origin__statement"><?php echo esc_html( $story['manifesto'] ); ?></p>
			<div class="sr2-world-origin__invitation">
				<h3 class="sr2-world-origin__invitation-title"><?php echo esc_html( $story['invitation_title'] ); ?></h3>
				<p class="sr2-lede"><?php echo esc_html( $story['invitation'] ); ?></p>
				<a class="sr2-editorial-link" href="#shop"><?php echo esc_html( $story['invitation_cta'] ); ?><span aria-hidden="true">→</span></a>
			</div>
		</div>
		<?php if ( $story_image ) : ?>
		<figure class="sr2-chapter__aside sr2-world-origin__look sr2-world-origin__look--approved" data-media-role="collection_story">
			<?php echo skyyrose2_collection_media_markup( $story_image ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- skyyrose2_collection_media_markup() escapes every attribute. ?>
			<figcaption class="sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( $story_image['alt'] ); ?></figcaption>
		</figure>
		<?php endif; ?>
	</div>
</section>
