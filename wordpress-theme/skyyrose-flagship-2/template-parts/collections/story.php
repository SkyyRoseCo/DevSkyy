<?php
/**
 * Collection code: the founder's headline and manifesto beside the lookbook
 * garment, closing on the invitation back to the edit.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;
$story      = $args['collection'];
$story_slug = $args['slug'];
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
		<figure class="sr2-chapter__aside sr2-world-origin__look sr2-image-reveal">
			<picture>
				<?php if ( ! empty( $story['lookbook_mobile'] ) ) : ?><source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $story['lookbook_mobile'] ) ); ?>"><?php endif; ?>
				<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $story['lookbook'] ) ); ?>" alt="<?php echo esc_attr( $story['name'] . ' lookbook' ); ?>" width="960" height="1280" loading="lazy" decoding="async">
			</picture>
			<figcaption class="sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( $story['name'] ); ?> / <?php esc_html_e( 'Look 01', 'skyyrose-flagship-2' ); ?></figcaption>
		</figure>
	</div>
</section>
