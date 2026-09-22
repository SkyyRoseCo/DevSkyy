<?php
/** Canonical Skyy character and progressively enhanced house concierge. */
defined( 'ABSPATH' ) || exit;
$mascot = get_template_directory_uri() . '/assets/images/skyy-runtime-poster.webp';
?>
<dialog id="skyy-ask-dialog" class="skyy-ask-dialog" aria-labelledby="skyy-ask-dialog-title" aria-describedby="skyy-ask-description">
	<header class="skyy-ask-dialog__head"><div><p class="skyy-ask-dialog__eyebrow">THE HOUSE CONCIERGE</p><h2 id="skyy-ask-dialog-title">Ask Skyy</h2></div><button id="skyy-ask-minimize" type="button" aria-label="<?php echo esc_attr__( 'Minimize Ask Skyy', 'skyyrose-flagship-2' ); ?>">−</button><button id="skyy-ask-cancel" type="button" aria-label="Close Ask Skyy">×</button></header>
	<div class="skyy-ask-dialog__body">
		<div id="skyy-dialog-stage">
		<div id="skyyrose-mascot" class="skyy-concierge-stage" data-state="hidden" data-renderer="static" data-presence="static">
			<div id="skyyrose-mascot-trigger" class="skyyrose-mascot__character" aria-hidden="true"><img class="skyyrose-mascot__image" data-fallback-src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/mascot/skyy-canonical-v2-512w.webp' ) ); ?>" src="<?php echo esc_url( $mascot ); ?>" alt="" width="220" height="340" loading="lazy" decoding="async"><canvas id="skyy-3d-canvas" class="skyy-3d-canvas" width="220" height="340" aria-hidden="true" hidden></canvas></div>
			<p id="skyy-presence-status" class="skyy-presence-status" role="status" aria-live="polite" aria-atomic="true" data-guide-failed="<?php echo esc_attr__( 'Skyy’s guide could not load. Contact the house.', 'skyyrose-flagship-2' ); ?>" data-contact="<?php echo esc_attr__( 'Contact', 'skyyrose-flagship-2' ); ?>" data-static="<?php echo esc_attr__( 'Your house guide.', 'skyyrose-flagship-2' ); ?>" data-loading="<?php echo esc_attr__( 'Skyy is joining you…', 'skyyrose-flagship-2' ); ?>" data-live="<?php echo esc_attr__( 'Your house guide.', 'skyyrose-flagship-2' ); ?>" data-reduced="<?php echo esc_attr__( 'Skyy is here, with motion off.', 'skyyrose-flagship-2' ); ?>" data-saving="<?php echo esc_attr__( 'Skyy is here in data-saving mode.', 'skyyrose-flagship-2' ); ?>" data-failed="<?php echo esc_attr__( 'Motion is unavailable. You can still ask Skyy.', 'skyyrose-flagship-2' ); ?>"><?php esc_html_e( 'Your house guide.', 'skyyrose-flagship-2' ); ?></p>
			<button id="skyy-motion-toggle" type="button" aria-pressed="false" hidden>Pause character</button>
			<div class="skyy-hero-actions"><button id="skyy-hero-chat" type="button" aria-haspopup="dialog" aria-controls="skyy-ask-dialog">Ask Skyy</button><button id="skyy-hero-dismiss" type="button">Dismiss Skyy</button></div>
		</div>
		</div>
		<div class="skyy-ask-dialog__conversation"><p id="skyy-ask-description">Explore the house, find a piece, or ask about sizing. Answers use our site guide and current catalog; this is not a live support chat.</p>
			<div id="skyy-conversation" class="skyy-conversation" role="log" tabindex="0" aria-label="Conversation with Skyy" aria-live="polite" aria-relevant="additions"></div>
			<div id="skyy-chips" class="skyy-chips" role="group" aria-label="Suggested questions"></div>
			<form id="skyy-ask-form" class="skyy-ask-form"><label for="skyy-ask-input">Your question</label><div class="skyy-ask-form__row"><input id="skyy-ask-input" name="question" type="text" autocomplete="off" maxlength="300" required placeholder="A product, collection, or question…"><button type="submit">Ask</button></div></form>
		</div>
	</div>
</dialog>
