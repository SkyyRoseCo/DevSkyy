<?php
/**
 * Collections index: a quiet head, then four full-bleed chapters — one per
 * collection — each opening on its approved monument scene with the lockup, the
 * founder's line, and one enter link. No grid of cards.
 *
 * Rendered by page.php for the "collections" page.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;
$index_collections = skyyrose2_collections();
$index_lockups     = array(
	'signature'    => array(
		'width'  => 1600,
		'height' => 540,
	),
	'black-rose'   => array(
		'width'  => 1600,
		'height' => 796,
	),
	'love-hurts'   => array(
		'width'  => 1600,
		'height' => 1228,
	),
	'kids-capsule' => array(
		'width'  => 720,
		'height' => 720,
		'shape'  => 'mark',
	),
);
$index_focals      = array(
	'signature'    => '50% 50%',
	'black-rose'   => '50% 50%',
	'love-hurts'   => '50% 45%',
	'kids-capsule' => '50% 40%',
);
$index_number      = 0;
?>
<section class="sr2-band sr2-collections-index__head" aria-labelledby="sr2-page-title">
	<div class="sr2-band__head">
		<div>
			<p class="sr2-eyebrow"><?php esc_html_e( 'The House', 'skyyrose-flagship-2' ); ?></p>
			<h1 id="sr2-page-title" class="sr2-title-display"><?php esc_html_e( 'Every collection opens another world.', 'skyyrose-flagship-2' ); ?></h1>
			<p class="sr2-lede"><?php esc_html_e( 'Signature begins the story. Black Rose protects it. Love Hurts tells the truth. Kids Capsule carries it forward.', 'skyyrose-flagship-2' ); ?></p>
		</div>
	</div>
</section>
<?php foreach ( $index_collections as $index_slug => $index_collection ) : ?>
	<?php
	++$index_number;
	$index_title_id = 'sr2-collections-index-' . $index_slug . '-title';
	$index_lockup   = $index_lockups[ $index_slug ] ?? array(
		'width'  => 1600,
		'height' => 540,
	);
	?>
	<section class="sr2-chapter sr2-collections-index__chapter<?php echo 0 === $index_number % 2 ? ' sr2-chapter--flip' : ''; ?>" data-collection="<?php echo esc_attr( $index_slug ); ?>" aria-labelledby="<?php echo esc_attr( $index_title_id ); ?>">
		<figure class="sr2-chapter__scene sr2-image-reveal" style="--sr2-focal: <?php echo esc_attr( $index_focals[ $index_slug ] ?? '50% 50%' ); ?>;">
			<picture>
				<?php
				if ( ! empty( $index_collection['hero_mobile'] ) ) :
					?>
					<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $index_collection['hero_mobile'] ) ); ?>"><?php endif; ?>
				<?php
				if ( ! empty( $index_collection['hero_tablet'] ) ) :
					?>
					<source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $index_collection['hero_tablet'] ) ); ?>"><?php endif; ?>
				<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $index_collection['hero'] ) ); ?>" width="1440" height="810" alt="" loading="<?php echo 1 === $index_number ? 'eager' : 'lazy'; ?>"<?php echo 1 === $index_number ? ' fetchpriority="high"' : ''; ?> decoding="async">
			</picture>
		</figure>
		<div class="sr2-chapter__band">
			<div class="sr2-chapter__copy">
				<p class="sr2-chapter__index sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( sprintf( '%02d', $index_number ) ); ?> / <?php echo esc_html( $index_collection['kicker'] ); ?></p>
				<h2 id="<?php echo esc_attr( $index_title_id ); ?>" class="sr2-title-chapter sr2-collections-index__title"><img class="sr2-collections-index__lockup<?php echo 'mark' === ( $index_lockup['shape'] ?? '' ) ? ' sr2-collections-index__lockup--mark' : ''; ?>" src="<?php echo esc_url( skyyrose2_sot_asset_uri( $index_collection['lockup'] ) ); ?>" width="<?php echo esc_attr( (string) $index_lockup['width'] ); ?>" height="<?php echo esc_attr( (string) $index_lockup['height'] ); ?>" alt="" loading="lazy" decoding="async"><span class="screen-reader-text"><?php echo esc_html( $index_collection['name'] ); ?></span></h2>
				<p class="sr2-lede"><?php echo esc_html( $index_collection['line'] ); ?></p>
				<p class="sr2-collections-index__action"><a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_collection_url( $index_slug ) ); ?>">
				<?php
					/* translators: %s: collection name, e.g. Black Rose. */
					echo esc_html( sprintf( __( 'Enter the %s collection', 'skyyrose-flagship-2' ), $index_collection['name'] ) );
				?>
				<span aria-hidden="true">→</span></a></p>
			</div>
		</div>
	</section>
<?php endforeach; ?>
