<?php
/**
 * Quiet colophon: the deliberate next world and the complete house index.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;
$index_collections = $args['collections'] ?? array();
$index_current     = $args['slug'] ?? '';
$index_next_slug   = $args['next_slug'] ?? '';
$index_next        = $index_collections[ $index_next_slug ] ?? array();
?>
<section class="sr2-band sr2-world-next" aria-labelledby="sr2-world-next-title"<?php if ( $index_next ) : ?> data-collection="<?php echo esc_attr( $index_next_slug ); ?>"<?php endif; ?>>
	<div class="sr2-world-next__lead">
		<?php if ( $index_next ) : ?>
			<p class="sr2-chapter__index sr2-eyebrow sr2-eyebrow--engraved"><?php esc_html_e( 'Next world', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr2-world-next-title" class="sr2-title-chapter"><a href="<?php echo esc_url( skyyrose2_collection_url( $index_next_slug ) ); ?>"><?php echo esc_html( $index_next['name'] ); ?><span aria-hidden="true"> →</span></a></h2>
			<p class="sr2-lede"><?php echo esc_html( $index_next['headline'] ); ?></p>
		<?php else : ?>
			<h2 id="sr2-world-next-title" class="sr2-title-chapter"><?php esc_html_e( 'The collection worlds', 'skyyrose-flagship-2' ); ?></h2>
		<?php endif; ?>
	</div>
	<nav class="sr2-world-index-nav" aria-label="<?php esc_attr_e( 'Collection worlds', 'skyyrose-flagship-2' ); ?>">
		<?php $index_number = 0; ?>
		<?php foreach ( $index_collections as $index_slug => $index_collection ) : ?>
			<?php ++$index_number; ?>
			<a href="<?php echo esc_url( skyyrose2_collection_url( $index_slug ) ); ?>"<?php if ( $index_slug === $index_current ) : ?> aria-current="page"<?php endif; ?>><span class="sr2-eyebrow--engraved" aria-hidden="true"><?php echo esc_html( sprintf( '%02d', $index_number ) ); ?></span><?php echo esc_html( $index_collection['name'] ); ?></a>
		<?php endforeach; ?>
	</nav>
</section>
