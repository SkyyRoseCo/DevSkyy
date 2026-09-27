<?php
/** Homepage philosophy feature with an explicit About destination. */
defined( 'ABSPATH' ) || exit;
?>
<section class="sr2-editorial-philosophy" aria-labelledby="sr2-editorial-philosophy-title">
	<figure class="sr2-editorial-philosophy__image"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/about/skyy-rose-founder-hero.webp' ) ); ?>" width="724" height="1086" alt="<?php esc_attr_e( 'Skyy Rose, whose name inspired the SkyyRose house', 'skyyrose-flagship-2' ); ?>" loading="lazy" decoding="async"></figure>
	<div class="sr2-editorial-philosophy__veil" aria-hidden="true"></div>
	<div class="sr2-editorial-philosophy__copy"><p class="sr2-world-index"><?php esc_html_e( 'Our philosophy', 'skyyrose-flagship-2' ); ?></p><h2 id="sr2-editorial-philosophy-title"><?php esc_html_e( 'A legacy in bloom.', 'skyyrose-flagship-2' ); ?></h2><p><?php esc_html_e( 'SkyyRose makes room for a legacy that carries Oakland forward: purposeful, expressive, and made to be lived in.', 'skyyrose-flagship-2' ); ?></p><a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'about' ) ); ?>"><?php esc_html_e( 'Read our story', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a></div>
	<nav class="sr2-editorial-philosophy__rail" aria-label="<?php esc_attr_e( 'SkyyRose values', 'skyyrose-flagship-2' ); ?>"><span><?php esc_html_e( 'Oakland rooted', 'skyyrose-flagship-2' ); ?></span><span><?php esc_html_e( 'Made with care', 'skyyrose-flagship-2' ); ?></span><span><?php esc_html_e( 'Future facing', 'skyyrose-flagship-2' ); ?></span></nav>
</section>
