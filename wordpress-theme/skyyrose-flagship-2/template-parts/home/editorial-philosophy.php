<?php
/** Homepage founder feature: the portrait stays a portrait, beside the words, with a direct About destination. */
defined( 'ABSPATH' ) || exit;
?>
<section class="sr2-editorial-philosophy sr2-band" aria-labelledby="sr2-editorial-philosophy-title">
	<div class="sr2-editorial-philosophy__grid">
		<figure class="sr2-editorial-philosophy__portrait sr2-image-reveal"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/about/skyy-rose-founder-hero.webp' ) ); ?>" width="724" height="1086" alt="<?php esc_attr_e( 'Skyy Rose, whose name inspired the SkyyRose house', 'skyyrose-flagship-2' ); ?>" loading="lazy" decoding="async"></figure>
		<div class="sr2-editorial-philosophy__copy">
			<p class="sr2-eyebrow"><?php esc_html_e( 'The house', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr2-editorial-philosophy-title" class="sr2-title-chapter"><?php esc_html_e( 'A legacy in bloom.', 'skyyrose-flagship-2' ); ?></h2>
			<p class="sr2-lede"><?php esc_html_e( 'SkyyRose makes room for a legacy that carries Oakland forward: purposeful, expressive, and made to be lived in.', 'skyyrose-flagship-2' ); ?></p>
			<ul class="sr2-editorial-philosophy__values" aria-label="<?php esc_attr_e( 'SkyyRose values', 'skyyrose-flagship-2' ); ?>"><li><?php esc_html_e( 'Oakland rooted', 'skyyrose-flagship-2' ); ?></li><li><?php esc_html_e( 'Made with care', 'skyyrose-flagship-2' ); ?></li><li><?php esc_html_e( 'Future facing', 'skyyrose-flagship-2' ); ?></li></ul>
			<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'about' ) ); ?>"><?php esc_html_e( 'Read our story', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a>
		</div>
	</div>
</section>
