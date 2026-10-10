<?php
/**
 * Experience Engine — WordPress Admin Dashboard
 *
 * Phase 5 of the SkyyRose Experience Engine.
 *
 * Renders the admin UI for:
 *   - Module toggle controls (enable/disable each of the 6 modules)
 *   - Analytics summary (total events, unique visitors, top collections)
 *   - Active design narrative directives and directive submission form
 *
 * Called by skyyrose_see_render_dashboard() via get_template_part().
 * All write operations use the Experience Engine REST API via inline JS.
 *
 * @package SkyyRose_Flagship
 * @since   6.4.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// Data for this render.
$modules    = function_exists( 'skyyrose_see_get_modules' ) ? skyyrose_see_get_modules() : array();
$summary    = function_exists( 'skyyrose_see_get_summary' ) ? skyyrose_see_get_summary( 30 ) : array();
$directives = function_exists( 'skyyrose_see_get_active_directives' ) ? skyyrose_see_get_active_directives() : array();
$rest_nonce = wp_create_nonce( 'wp_rest' );
$rest_base  = '/?rest_route=/skyyrose/v1';

// Analytics values.
$total_events    = intval( $summary['total_events'] ?? 0 );
$unique_visitors = $summary['unique_visitors'] ?? null;
$top_collections = $summary['top_collections'] ?? array();
$period          = intval( $summary['period'] ?? 30 );
?>

<div class="see-dashboard wrap">

	<div class="see-dashboard__head">
		<div class="see-dashboard__title-row">
			<h1 class="see-dashboard__title">
				<span class="see-dashboard__title-icon" aria-hidden="true">✦</span>
				<?php esc_html_e( 'Experience Engine', 'skyyrose' ); ?>
			</h1>
			<span class="see-dashboard__version">v1.0 · Phase 5</span>
		</div>
		<p class="see-dashboard__desc">
			<?php esc_html_e( 'Real-time UX orchestration for SkyyRose digital properties.', 'skyyrose' ); ?>
		</p>
	</div>

	<!-- ===== Analytics Summary ===== -->
	<div class="see-dashboard__section">
		<h2 class="see-dashboard__section-title">
			<?php esc_html_e( 'Analytics', 'skyyrose' ); ?>
			<span class="see-dashboard__period">
				<?php printf( esc_html__( 'Last %d days', 'skyyrose' ), absint( $period ) ); ?>
			</span>
		</h2>

		<div class="see-dashboard__stats-grid">
			<div class="see-dashboard__stat">
				<span class="see-dashboard__stat-value"><?php echo esc_html( number_format_i18n( $total_events ) ); ?></span>
				<span class="see-dashboard__stat-label"><?php esc_html_e( 'Total Events', 'skyyrose' ); ?></span>
			</div>
			<div class="see-dashboard__stat">
				<span class="see-dashboard__stat-value"><?php echo esc_html( null === $unique_visitors ? __( 'Unavailable', 'skyyrose' ) : number_format_i18n( $unique_visitors ) ); ?></span>
				<span class="see-dashboard__stat-label"><?php esc_html_e( 'Unique Visitors', 'skyyrose' ); ?></span>
			</div>
			<?php if ( ! empty( $top_collections ) ) : ?>
			<div class="see-dashboard__stat">
				<span class="see-dashboard__stat-value">
					<?php echo esc_html( strtoupper( str_replace( '-', ' ', array_key_first( $top_collections ) ?? '' ) ) ); ?>
				</span>
				<span class="see-dashboard__stat-label"><?php esc_html_e( 'Top Collection', 'skyyrose' ); ?></span>
			</div>
			<?php endif; ?>
		</div>

		<?php if ( ! empty( $top_collections ) ) : ?>
		<div class="see-dashboard__collection-bars">
			<?php
			$max = max( array_values( $top_collections ) ) ?: 1;
			foreach ( $top_collections as $slug => $count ) :
				$pct = round( ( $count / $max ) * 100 );
				?>
			<div class="see-dashboard__bar-row">
				<span class="see-dashboard__bar-label">
					<?php echo esc_html( strtoupper( str_replace( '-', ' ', $slug ) ) ); ?>
				</span>
				<div class="see-dashboard__bar-track">
					<div class="see-dashboard__bar-fill" style="width:<?php echo esc_attr( (string) $pct ); ?>%"></div>
				</div>
				<span class="see-dashboard__bar-count"><?php echo esc_html( number_format_i18n( (int) $count ) ); ?></span>
			</div>
			<?php endforeach; ?>
		</div>
		<?php endif; ?>
	</div>

	<!-- ===== Module Controls ===== -->
	<div class="see-dashboard__section">
		<h2 class="see-dashboard__section-title">
			<?php esc_html_e( 'Modules', 'skyyrose' ); ?>
		</h2>
		<p class="see-dashboard__section-desc">
			<?php esc_html_e( 'Toggle modules without a code deploy. Changes take effect immediately.', 'skyyrose' ); ?>
		</p>

		<div class="see-dashboard__modules" id="see-modules">
			<?php
			foreach ( $modules as $slug => $config ) :
				$is_active = function_exists( 'skyyrose_see_is_module_active' )
					? skyyrose_see_is_module_active( $slug )
					: $config['default'];
				?>
			<div class="see-dashboard__module" data-module="<?php echo esc_attr( $slug ); ?>">
				<div class="see-dashboard__module-info">
					<span class="see-dashboard__module-name">
						<?php echo esc_html( $config['label'] ); ?>
					</span>
					<span class="see-dashboard__module-priority">
						<?php printf( esc_html__( 'Priority %s', 'skyyrose' ), esc_html( (string) $config['priority'] ) ); ?>
					</span>
				</div>
				<button
					class="see-dashboard__toggle <?php echo $is_active ? 'see-dashboard__toggle--on' : ''; ?>"
					type="button"
					aria-pressed="<?php echo esc_attr( $is_active ? 'true' : 'false' ); ?>"
					aria-label="
					<?php
					echo esc_attr(
						sprintf(
							$is_active
							? __( 'Disable %s', 'skyyrose' )
							: __( 'Enable %s', 'skyyrose' ),
							$config['label']
						)
					);
					?>
					"
					data-module-slug="<?php echo esc_attr( $slug ); ?>"
					data-active="<?php echo $is_active ? '1' : '0'; ?>">
					<span class="see-dashboard__toggle-knob"></span>
				</button>
			</div>
			<?php endforeach; ?>
		</div>

		<p class="see-dashboard__save-status" id="see-save-status" aria-live="polite"></p>
	</div>

	<!-- ===== Design Narrative Directives ===== -->
	<div class="see-dashboard__section">
		<h2 class="see-dashboard__section-title">
			<?php esc_html_e( 'Design Narratives', 'skyyrose' ); ?>
		</h2>
		<p class="see-dashboard__section-desc">
			<?php esc_html_e( 'Active directives shape the Experience Engine\'s UX decisions.', 'skyyrose' ); ?>
		</p>

		<?php if ( ! empty( $directives ) ) : ?>
		<ul class="see-dashboard__directives">
			<?php foreach ( $directives as $d ) : ?>
			<li class="see-dashboard__directive">
				<span class="see-dashboard__directive-badge see-dashboard__directive-badge--<?php echo esc_attr( $d['target'] ?? 'global' ); ?>">
					<?php echo esc_html( strtoupper( $d['target'] ?? 'global' ) ); ?>
				</span>
				<span class="see-dashboard__directive-desc">
					<?php echo esc_html( $d['description'] ?? '' ); ?>
				</span>
				<span class="see-dashboard__directive-priority" title="<?php esc_attr_e( 'Priority', 'skyyrose' ); ?>">
					<?php echo esc_html( $d['priority'] ?? 5 ); ?>
				</span>
			</li>
			<?php endforeach; ?>
		</ul>
		<?php else : ?>
		<p class="see-dashboard__empty"><?php esc_html_e( 'No active directives.', 'skyyrose' ); ?></p>
		<?php endif; ?>

		<form class="see-dashboard__narrative-form" id="see-narrative-form" novalidate>
			<h3 class="see-dashboard__subsection-title">
				<?php esc_html_e( 'Add Directive', 'skyyrose' ); ?>
			</h3>
			<div class="see-dashboard__form-row">
				<label for="see-narrative-desc" class="see-dashboard__label">
					<?php esc_html_e( 'Description', 'skyyrose' ); ?>
				</label>
				<input
					type="text"
					id="see-narrative-desc"
					name="description"
					class="see-dashboard__input"
					placeholder="<?php esc_attr_e( 'e.g. Emphasise scarcity on Black Rose pre-orders', 'skyyrose' ); ?>"
					required
					maxlength="280">
			</div>
			<div class="see-dashboard__form-row see-dashboard__form-row--inline">
				<div>
					<label for="see-narrative-target" class="see-dashboard__label">
						<?php esc_html_e( 'Target', 'skyyrose' ); ?>
					</label>
					<select id="see-narrative-target" name="target" class="see-dashboard__select">
						<option value="global"><?php esc_html_e( 'Global', 'skyyrose' ); ?></option>
						<option value="black-rose"><?php esc_html_e( 'Black Rose', 'skyyrose' ); ?></option>
						<option value="love-hurts"><?php esc_html_e( 'Love Hurts', 'skyyrose' ); ?></option>
						<option value="signature"><?php esc_html_e( 'Signature', 'skyyrose' ); ?></option>
						<option value="kids-capsule"><?php esc_html_e( 'Kids Capsule', 'skyyrose' ); ?></option>
					</select>
				</div>
				<div>
					<label for="see-narrative-priority" class="see-dashboard__label">
						<?php esc_html_e( 'Priority (1–10)', 'skyyrose' ); ?>
					</label>
					<input
						type="number"
						id="see-narrative-priority"
						name="priority"
						class="see-dashboard__input see-dashboard__input--short"
						value="5" min="1" max="10">
				</div>
			</div>
			<button type="submit" class="see-dashboard__submit" id="see-narrative-submit">
				<?php esc_html_e( 'Add Directive', 'skyyrose' ); ?>
			</button>
			<p class="see-dashboard__save-status" id="see-narrative-status" aria-live="polite"></p>
		</form>
	</div>

</div><!-- .see-dashboard -->

<style>
.see-dashboard { max-width: 900px; padding: 0 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.see-dashboard__head { margin-bottom: 28px; }
.see-dashboard__title-row { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.see-dashboard__title { font-size: 1.5rem; margin: 0; color: #1d2327; }
.see-dashboard__title-icon { color: #B76E79; }
.see-dashboard__version { font-size: 0.72rem; background: #f6f7f7; border: 1px solid #ddd; border-radius: 4px; padding: 2px 8px; color: #646970; }
.see-dashboard__desc { color: #646970; margin: 0; }
.see-dashboard__section { background: #fff; border: 1px solid #e2e4e7; border-radius: 6px; padding: 24px; margin-bottom: 20px; }
.see-dashboard__section-title { font-size: 1rem; font-weight: 600; margin: 0 0 4px; display: flex; align-items: center; gap: 10px; }
.see-dashboard__period { font-size: 0.72rem; font-weight: 400; color: #999; background: #f6f7f7; padding: 2px 8px; border-radius: 4px; }
.see-dashboard__section-desc { color: #646970; font-size: 0.85rem; margin: 0 0 18px; }
.see-dashboard__subsection-title { font-size: 0.88rem; font-weight: 600; margin: 24px 0 14px; color: #1d2327; border-top: 1px solid #f0f0f1; padding-top: 20px; }
/* Stats */
.see-dashboard__stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 16px; margin-bottom: 20px; }
.see-dashboard__stat { background: #f6f7f7; border-radius: 6px; padding: 16px; }
.see-dashboard__stat-value { display: block; font-size: 1.5rem; font-weight: 700; color: #1d2327; line-height: 1; }
.see-dashboard__stat-label { display: block; font-size: 0.72rem; color: #646970; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; }
/* Bars */
.see-dashboard__collection-bars { display: flex; flex-direction: column; gap: 10px; }
.see-dashboard__bar-row { display: grid; grid-template-columns: 120px 1fr 60px; align-items: center; gap: 10px; }
.see-dashboard__bar-label { font-size: 0.72rem; color: #646970; text-transform: uppercase; letter-spacing: 0.06em; }
.see-dashboard__bar-track { height: 6px; background: #f0f0f1; border-radius: 3px; overflow: hidden; }
.see-dashboard__bar-fill { height: 100%; background: #B76E79; border-radius: 3px; transition: width 0.6s ease; }
.see-dashboard__bar-count { font-size: 0.72rem; color: #999; text-align: right; }
/* Modules */
.see-dashboard__modules { display: flex; flex-direction: column; gap: 2px; margin-bottom: 12px; }
.see-dashboard__module { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f1; }
.see-dashboard__module:last-child { border-bottom: none; }
.see-dashboard__module-info { display: flex; flex-direction: column; gap: 2px; }
.see-dashboard__module-name { font-size: 0.9rem; font-weight: 500; color: #1d2327; }
.see-dashboard__module-priority { font-size: 0.72rem; color: #999; }
/* Toggle */
.see-dashboard__toggle { position: relative; width: 40px; height: 22px; border-radius: 11px; border: none; background: #ddd; cursor: pointer; transition: background 0.2s; flex-shrink: 0; }
.see-dashboard__toggle--on { background: #B76E79; }
.see-dashboard__toggle-knob { position: absolute; top: 3px; left: 3px; width: 16px; height: 16px; border-radius: 50%; background: #fff; transition: transform 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
.see-dashboard__toggle--on .see-dashboard__toggle-knob { transform: translateX(18px); }
/* Save status */
.see-dashboard__save-status { font-size: 0.8rem; color: #646970; min-height: 20px; margin: 0; transition: color 0.2s; }
.see-dashboard__save-status--success { color: #00a32a; }
.see-dashboard__save-status--error { color: #d63638; }
/* Directives */
.see-dashboard__directives { margin: 0 0 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 8px; }
.see-dashboard__directive { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 10px; padding: 10px 12px; background: #f6f7f7; border-radius: 4px; font-size: 0.85rem; }
.see-dashboard__directive-badge { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; padding: 2px 7px; border-radius: 3px; background: #e8d5da; color: #7a3040; }
.see-dashboard__directive-badge--global { background: #e2e4e7; color: #1d2327; }
.see-dashboard__directive-desc { color: #1d2327; }
.see-dashboard__directive-priority { font-size: 0.72rem; color: #999; white-space: nowrap; }
.see-dashboard__empty { color: #999; font-style: italic; font-size: 0.85rem; }
/* Form */
.see-dashboard__form-row { margin-bottom: 14px; }
.see-dashboard__form-row--inline { display: flex; gap: 20px; flex-wrap: wrap; }
.see-dashboard__label { display: block; font-size: 0.8rem; font-weight: 500; color: #1d2327; margin-bottom: 5px; }
.see-dashboard__input { width: 100%; max-width: 500px; padding: 8px 10px; border: 1px solid #c3c4c7; border-radius: 4px; font-size: 0.88rem; color: #1d2327; box-sizing: border-box; }
.see-dashboard__input--short { width: 80px; }
.see-dashboard__select { padding: 8px 10px; border: 1px solid #c3c4c7; border-radius: 4px; font-size: 0.88rem; color: #1d2327; }
.see-dashboard__submit { background: #B76E79; color: #fff; border: none; border-radius: 4px; padding: 10px 20px; font-size: 0.88rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; }
.see-dashboard__submit:hover { opacity: 0.85; }
.see-dashboard__submit:disabled { opacity: 0.5; cursor: not-allowed; }
</style>

<script>
( function () {
	'use strict';

	var REST_BASE  = <?php echo wp_json_encode( $rest_base ); ?>;
	var REST_NONCE = <?php echo wp_json_encode( $rest_nonce ); ?>;

	function apiPost( url, data ) {
		return fetch( url, {
			method:      'POST',
			headers:     { 'Content-Type': 'application/json', 'X-WP-Nonce': REST_NONCE },
			credentials: 'same-origin',
			body:        JSON.stringify( data ),
		} ).then( function ( r ) { return r.ok ? r.json() : Promise.reject( r.status ); } );
	}

	function setStatus( el, msg, type ) {
		el.textContent = msg;
		el.className = 'see-dashboard__save-status' + ( type ? ' see-dashboard__save-status--' + type : '' );
		if ( type === 'success' ) setTimeout( function () { el.textContent = ''; el.className = 'see-dashboard__save-status'; }, 3000 );
	}

	// Module toggles
	var saveStatus = document.getElementById( 'see-save-status' );
	document.querySelectorAll( '.see-dashboard__toggle' ).forEach( function ( btn ) {
		btn.addEventListener( 'click', function () {
			var slug   = btn.dataset.moduleSlug;
			var active = btn.dataset.active === '1';
			var next   = ! active;

			btn.disabled = true;
			var payload = {};
			payload[ 'module_' + slug ] = next;
			apiPost( REST_BASE + '/settings', payload )
				.then( function () {
					btn.dataset.active = next ? '1' : '0';
					btn.setAttribute( 'aria-pressed', String( next ) );
					btn.classList.toggle( 'see-dashboard__toggle--on', next );
					setStatus( saveStatus, next ? slug + ' enabled.' : slug + ' disabled.', 'success' );
				} )
				.catch( function () {
					setStatus( saveStatus, 'Save failed — please try again.', 'error' );
				} )
				.finally( function () { btn.disabled = false; } );
		} );
	} );

	// Narrative form
	var narrativeForm   = document.getElementById( 'see-narrative-form' );
	var narrativeStatus = document.getElementById( 'see-narrative-status' );
	if ( narrativeForm ) {
		narrativeForm.addEventListener( 'submit', function ( e ) {
			e.preventDefault();
			var desc     = narrativeForm.querySelector( '[name="description"]' ).value.trim();
			var target   = narrativeForm.querySelector( '[name="target"]' ).value;
			var priority = parseInt( narrativeForm.querySelector( '[name="priority"]' ).value, 10 );
			var btn      = document.getElementById( 'see-narrative-submit' );

			if ( ! desc ) return;
			btn.disabled = true;
			setStatus( narrativeStatus, 'Saving…', '' );

			apiPost( REST_BASE + '/settings/narrative', {
				id:          'directive_' + Date.now(),
				description: desc,
				target:      target,
				priority:    priority,
				config:      {},
			} )
				.then( function () {
					narrativeForm.reset();
					setStatus( narrativeStatus, 'Directive added. Reload to see it in the list.', 'success' );
				} )
				.catch( function () {
					setStatus( narrativeStatus, 'Submit failed — please try again.', 'error' );
				} )
				.finally( function () { btn.disabled = false; } );
		} );
	}
} )();
</script>
