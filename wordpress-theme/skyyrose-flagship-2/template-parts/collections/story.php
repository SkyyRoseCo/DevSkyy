<?php
/** Source-backed origin, after the first live product edit. @package SkyyRoseFlagship2 */
defined( 'ABSPATH' ) || exit;
$story = $args['collection'];
?>
<section id="origin" class="sr2-world-origin" aria-labelledby="sr2-world-origin-title" tabindex="-1">
	<div class="sr2-world-origin__heading">
		<p class="sr2-world-index"><?php esc_html_e( 'The origin', 'skyyrose-flagship-2' ); ?></p>
		<h2 id="sr2-world-origin-title"><?php echo esc_html( $story['world_heading'] ); ?></h2>
	</div>
	<div class="sr2-world-origin__copy">
		<p class="sr2-world-origin__statement"><?php echo esc_html( $story['manifesto'] ); ?></p>
		<p><?php echo esc_html( $story['line'] ); ?></p>
	</div>
</section>
