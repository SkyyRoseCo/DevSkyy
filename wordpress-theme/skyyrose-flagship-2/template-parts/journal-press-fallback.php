<?php
/**
 * Founder-approved press archive shown until the live Journal has posts.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$press_features = function_exists( 'skyyrose2_press_features' ) ? skyyrose2_press_features() : array();
if ( empty( $press_features ) ) {
	return;
}
?>
<section class="sr2-journal-fallback" aria-labelledby="sr2-journal-archive-title">
	<div class="sr2-band__head">
		<div>
			<p class="sr2-eyebrow"><?php esc_html_e( 'Source archive', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr2-journal-archive-title" class="sr2-title-chapter"><?php esc_html_e( 'The work has already been documented.', 'skyyrose-flagship-2' ); ?></h2>
			<p class="sr2-lede"><?php esc_html_e( 'Fresh installs begin with the founder-approved press record below. Published WordPress stories replace this fallback automatically when the Journal is populated.', 'skyyrose-flagship-2' ); ?></p>
		</div>
	</div>
	<ol class="sr2-press-list">
		<?php foreach ( $press_features as $feature ) : ?>
			<li class="sr2-press-list__item">
				<p class="sr2-press-list__meta sr2-eyebrow"><span><?php echo esc_html( $feature['source'] ); ?></span><time><?php echo esc_html( $feature['date'] ); ?></time></p>
				<div class="sr2-press-list__copy">
					<h3 class="sr2-title-editorial"><?php echo esc_html( $feature['title'] ); ?></h3>
					<p><?php echo esc_html( $feature['excerpt'] ); ?></p>
				</div>
				<a class="sr2-editorial-link sr2-press-list__link" href="<?php echo esc_url( $feature['url'] ); ?>" target="_blank" rel="noopener noreferrer"><?php esc_html_e( 'Read the original', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a>
			</li>
		<?php endforeach; ?>
	</ol>
</section>
