<?php
/**
 * Template Name: Pre-Order Gateway
 *
 * Flagship conversion-led pre-order page: cinematic video hero → marquee strip →
 * collection gateway (3 art panels) → capsule product grids (PHP-rendered, JS-toggled) →
 * production journey → lookbook band → manifesto strip → FAQ → email capture.
 * Sticky reserve/cart summary bar throughout after hero.
 *
 * Reserve meters are gated by the `skyyrose_preorder_meters_enabled` filter (default false).
 * Do NOT enable until real WC stock data is wired. No stub counts ever ship to production.
 *
 * @package SkyyRose
 * @since   2.0.0
 * @updated 7.0.0 — flagship full-throttle port (video hero, conversion order, po-* system)
 */

defined( 'ABSPATH' ) || exit;

/* ─── Canon: 3 gateway collections (Kids Capsule excluded from pre-order gateway) ── */
$po_collections = array(
	'black-rose' => array(
		'label'       => esc_html__( 'Black Rose', 'skyyrose' ),
		'number'      => esc_html__( '01', 'skyyrose' ),
		'tagline'     => esc_html__( 'Armor for the concrete world.', 'skyyrose' ),
		'accent_word' => esc_html__( 'Black', 'skyyrose' ),
	),
	'love-hurts' => array(
		'label'       => esc_html__( 'Love Hurts', 'skyyrose' ),
		'number'      => esc_html__( '02', 'skyyrose' ),
		'tagline'     => esc_html__( 'Bloodline you carry forward.', 'skyyrose' ),
		'accent_word' => esc_html__( 'Love', 'skyyrose' ),
	),
	'signature'  => array(
		'label'       => esc_html__( 'Signature', 'skyyrose' ),
		'number'      => esc_html__( '03', 'skyyrose' ),
		'tagline'     => esc_html__( 'The origin. The crown.', 'skyyrose' ),
		'accent_word' => esc_html__( 'Origin', 'skyyrose' ),
	),
);

/*
─── Pre-load all 3 collection product arrays ─────────────────────────────────── */

/*
 * Production-image gate (structural remediation WS5): a SKU whose resolved
 * display image is missing on disk never renders here — no placeholder
 * imagery may reach the pre-order page. Data-driven (catalog + filesystem),
 * never a hardcoded SKU list.
 */
$po_products = array();
foreach ( array_keys( $po_collections ) as $po_slug ) {
	$po_products[ $po_slug ] = array_values(
		array_filter(
			skyyrose_get_collection_products( $po_slug ),
			static function ( $po_candidate ) {
				$po_image = skyyrose_get_product_display_image( $po_candidate );
				return '' !== $po_image && file_exists( get_theme_file_path( $po_image ) );
			}
		)
	);
}

/* ─── WC helpers ───────────────────────────────────────────────────────────────── */
$po_checkout_url = function_exists( 'wc_get_checkout_url' ) ? wc_get_checkout_url() : home_url( '/checkout/' );
$po_cart_url     = function_exists( 'wc_get_cart_url' ) ? wc_get_cart_url() : home_url( '/cart/' );
$po_currency     = function_exists( 'get_woocommerce_currency_symbol' )
	? html_entity_decode( get_woocommerce_currency_symbol(), ENT_QUOTES, 'UTF-8' )
	: '$';

/* ─── Reserve meters: gated — never enable with stub counts ────────────────────── */
$po_meters_on = (bool) apply_filters( 'skyyrose_preorder_meters_enabled', false );

/* ─── Asset base ───────────────────────────────────────────────────────────────── */
$po_assets = SKYYROSE_ASSETS_URI;
$po_ver    = SKYYROSE_VERSION;

get_header();
?>

<main id="primary" class="site-main po-page" role="main" tabindex="-1">

	<?php
	get_template_part(
		'template-parts/preorder/opening',
		null,
		array(
			'assets'  => $po_assets,
			'version' => $po_ver,
		)
	);
	?>

	<!-- ══════════════════════════════════════════════════════════════════
		03 · COLLECTION GATEWAY (3 art panels)
		══════════════════════════════════════════════════════════════════ -->
	<section class="po-gateway" id="po-gateway"
		aria-label="<?php esc_attr_e( 'Choose a collection', 'skyyrose' ); ?>">

		<header class="po-gateway__header">
			<h1 class="po-gateway__title po-rv">
				<?php esc_html_e( 'Choose Your Collection', 'skyyrose' ); ?>
			</h1>
			<p class="po-gateway__sub po-rv">
				<?php esc_html_e( 'Three collections. One story.', 'skyyrose' ); ?>
			</p>
		</header>

		<div class="po-gateway__panels">
			<?php
			/* Portrait image map — from visual-manifest.json */
			$po_portrait_map = array(
				'black-rose' => array(
					'avif' => $po_assets . '/images/homepage-col-black-rose.avif?v=' . $po_ver,
					'webp' => $po_assets . '/images/homepage-col-black-rose.webp?v=' . $po_ver,
					'jpg'  => $po_assets . '/images/homepage-col-black-rose.webp?v=' . $po_ver,
					'w'    => 800,
					'h'    => 1000,
				),
				'love-hurts' => array(
					'avif' => $po_assets . '/images/homepage-col-love-hurts.avif?v=' . $po_ver,
					'webp' => $po_assets . '/images/homepage-col-love-hurts.webp?v=' . $po_ver,
					'jpg'  => $po_assets . '/images/homepage-col-love-hurts.webp?v=' . $po_ver,
					'w'    => 800,
					'h'    => 1000,
				),
				'signature'  => array(
					'avif' => $po_assets . '/images/homepage-col-signature.avif?v=' . $po_ver,
					'webp' => $po_assets . '/images/homepage-col-signature.webp?v=' . $po_ver,
					'jpg'  => $po_assets . '/images/homepage-col-signature.webp?v=' . $po_ver,
					'w'    => 800,
					'h'    => 1000,
				),
			);

			/* Lockup image map — from visual-manifest.json */
			$po_lockup_map = array(
				'black-rose' => array(
					'avif'  => $po_assets . '/images/hero-overlays/br-brand-script-logotype.avif?v=' . $po_ver,
					'webp'  => $po_assets . '/images/hero-overlays/br-brand-script-logotype.webp?v=' . $po_ver,
					'png'   => $po_assets . '/images/hero-overlays/br-brand-script-logotype.png?v=' . $po_ver,

					/*
					 * BR lockup is BLACK lettering — invert on dark ground.
					 * Manifest rule: "filter: invert(1) grayscale(1) brightness(1.05)"
					 */
					'style' => 'filter:invert(1) grayscale(1) brightness(1.05);',
					'alt'   => esc_attr__( 'Black Rose', 'skyyrose' ),
				),
				'love-hurts' => array(
					'avif'  => $po_assets . '/images/hero-overlays/lh-logo-combined.avif?v=' . $po_ver,
					'webp'  => $po_assets . '/images/hero-overlays/lh-logo-combined.webp?v=' . $po_ver,
					'png'   => $po_assets . '/images/hero-overlays/lh-logo-combined.png?v=' . $po_ver,
					'style' => '',
					'alt'   => esc_attr__( 'Love Hurts', 'skyyrose' ),
				),
				'signature'  => array(
					'avif'  => $po_assets . '/images/hero-overlays/sig-brand-skyy-rose-gold.avif?v=' . $po_ver,
					'webp'  => $po_assets . '/images/hero-overlays/sig-brand-skyy-rose-gold.webp?v=' . $po_ver,
					'png'   => $po_assets . '/images/hero-overlays/sig-brand-skyy-rose-gold.png?v=' . $po_ver,
					'style' => '',
					'alt'   => esc_attr__( 'Signature', 'skyyrose' ),
				),
			);

			$po_panel_index = 0;
			foreach ( $po_collections as $po_slug => $po_col ) :
				$po_portrait = $po_portrait_map[ $po_slug ];
				$po_lockup   = $po_lockup_map[ $po_slug ];
				?>
				<?php // No list/listitem roles: aria-pressed is invalid on role="listitem", and the toggle semantics matter more than list semantics here. ?>
				<button type="button"
					class="po-panel po-panel--<?php echo esc_attr( $po_slug ); ?>"
					data-collection="<?php echo esc_attr( $po_slug ); ?>"
					aria-label="<?php echo esc_attr( sprintf( /* translators: %s: collection label */ __( 'View %s collection', 'skyyrose' ), $po_col['label'] ) ); ?>">

					<div class="po-panel__bg" aria-hidden="true">
							<?php
							// Panels render ≤290px wide (minmax(220px,1fr) in a 900px grid)
							// but shipped full-size AVIF (round-3 uses-responsive-images).
							// Photon width variants via the webp; avif <source> suppressed
							// while Photon answers (it serves webp — keeps type= honest).
							$po_p_srcset = function_exists( 'skyyrose_photon_srcset' )
								? skyyrose_photon_srcset( $po_portrait['webp'], array( 320, 480, 640 ) )
								: '';
							$po_p_sizes  = '(max-width: 480px) 92vw, (max-width: 900px) 46vw, 290px';
							?>
							<picture>
								<?php if ( '' !== $po_p_srcset ) : ?>
									<source srcset="<?php echo esc_attr( $po_p_srcset ); ?>" sizes="<?php echo esc_attr( $po_p_sizes ); ?>" type="image/webp">
								<?php else : ?>
									<source srcset="<?php echo esc_url( $po_portrait['avif'] ); ?>" type="image/avif">
									<source srcset="<?php echo esc_url( $po_portrait['webp'] ); ?>" type="image/webp">
								<?php endif; ?>
								<img src="<?php echo esc_url( $po_portrait['jpg'] ); ?>"
									<?php if ( '' !== $po_p_srcset ) : ?>
										srcset="<?php echo esc_attr( $po_p_srcset ); ?>"
										sizes="<?php echo esc_attr( $po_p_sizes ); ?>"
									<?php endif; ?>
									alt=""
									width="<?php echo absint( $po_portrait['w'] ); ?>"
									height="<?php echo absint( $po_portrait['h'] ); ?>"
									loading="<?php echo 0 === $po_panel_index ? 'eager' : 'lazy'; ?>">
							</picture>
						<div class="po-panel__overlay" aria-hidden="true"></div>
					</div>

					<div class="po-panel__content">
						<span class="po-panel__number">
							<?php echo esc_html( $po_col['number'] ); ?>
						</span>

							<?php
							// Lockup renders ≤120px (.po-panel__lockup) — full-size AVIF
							// (50-93KB) was pure waste. Same Photon/avif-suppression trade.
							$po_l_srcset = function_exists( 'skyyrose_photon_srcset' )
								? skyyrose_photon_srcset( $po_lockup['webp'], array( 120, 240, 360 ) )
								: '';
							?>
							<picture class="po-panel__lockup">
								<?php if ( '' !== $po_l_srcset ) : ?>
									<source srcset="<?php echo esc_attr( $po_l_srcset ); ?>" sizes="120px" type="image/webp">
								<?php else : ?>
									<source srcset="<?php echo esc_url( $po_lockup['avif'] ); ?>" type="image/avif">
									<source srcset="<?php echo esc_url( $po_lockup['webp'] ); ?>" type="image/webp">
								<?php endif; ?>
								<img src="<?php echo esc_url( $po_lockup['png'] ); ?>"
									<?php if ( '' !== $po_l_srcset ) : ?>
										srcset="<?php echo esc_attr( $po_l_srcset ); ?>"
										sizes="120px"
									<?php endif; ?>
									alt="<?php echo esc_attr( $po_lockup['alt'] ); ?>"
									width="260" height="80" loading="lazy"
									<?php if ( ! empty( $po_lockup['style'] ) ) : ?>
										style="<?php echo esc_attr( $po_lockup['style'] ); ?>"
									<?php endif; ?>>
							</picture>
						<p class="po-panel__tagline">
							<?php echo esc_html( $po_col['tagline'] ); ?>
						</p>

						<span class="po-panel__cta" aria-hidden="true">
							<?php esc_html_e( 'Reserve Now', 'skyyrose' ); ?>
							<span class="po-panel__arrow">&#8594;</span>
						</span>
					</div>
				</button>
				<?php
				++$po_panel_index;
			endforeach;
			?>
		</div>
	</section>

	<!-- ══════════════════════════════════════════════════════════════════
		04 · CAPSULE PRODUCT GRIDS  (PHP-rendered, JS-toggled)
		══════════════════════════════════════════════════════════════════ -->
	<section class="po-products" id="po-products"
		aria-label="<?php esc_attr_e( 'Pre-order products', 'skyyrose' ); ?>">

		<div class="po-products__tabs" role="tablist"
			aria-label="<?php esc_attr_e( 'Filter by collection', 'skyyrose' ); ?>">
			<?php
			$po_tab_first = true;
			foreach ( $po_collections as $po_slug => $po_col ) :
				?>
				<button type="button"
					class="po-tab"
					role="tab"
					id="po-tab-<?php echo esc_attr( $po_slug ); ?>"
					aria-controls="po-grid-<?php echo esc_attr( $po_slug ); ?>"
					aria-selected="<?php echo $po_tab_first ? 'true' : 'false'; ?>"
					tabindex="<?php echo $po_tab_first ? '0' : '-1'; ?>"
					data-collection="<?php echo esc_attr( $po_slug ); ?>">
					<?php echo esc_html( $po_col['label'] ); ?>
				</button>
				<?php
				$po_tab_first = false;
			endforeach;
			?>
		</div>

		<?php
		$po_grid_first = true;
		foreach ( $po_collections as $po_slug => $po_col ) :
			$po_items = $po_products[ $po_slug ];
			?>
			<div class="po-grid"
				id="po-grid-<?php echo esc_attr( $po_slug ); ?>"
				role="tabpanel"
				aria-labelledby="po-tab-<?php echo esc_attr( $po_slug ); ?>"
				<?php
				if ( ! $po_grid_first ) :
					?>
					hidden<?php endif; ?>>

				<header class="po-grid__header">
					<div class="po-grid__meta">
						<span class="po-grid__col-num"><?php echo esc_html( $po_col['number'] ); ?></span>
						<?php
						$po_g_lockup = $po_lockup_map[ $po_slug ];
							// Renders ≤140px (.po-grid__lockup) — same Photon/avif-suppression
							// trade as the panel lockup above.
							$po_gl_srcset = function_exists( 'skyyrose_photon_srcset' )
								? skyyrose_photon_srcset( $po_g_lockup['webp'], array( 140, 280, 420 ) )
								: '';
						?>
							<picture class="po-grid__lockup">
								<?php if ( '' !== $po_gl_srcset ) : ?>
									<source srcset="<?php echo esc_attr( $po_gl_srcset ); ?>" sizes="140px" type="image/webp">
								<?php else : ?>
								<source srcset="<?php echo esc_url( $po_g_lockup['avif'] ); ?>" type="image/avif">
									<source srcset="<?php echo esc_url( $po_g_lockup['webp'] ); ?>" type="image/webp">
								<?php endif; ?>
								<img src="<?php echo esc_url( $po_g_lockup['png'] ); ?>"
									<?php if ( '' !== $po_gl_srcset ) : ?>
										srcset="<?php echo esc_attr( $po_gl_srcset ); ?>"
										sizes="140px"
									<?php endif; ?>
									alt="<?php echo esc_attr( $po_g_lockup['alt'] ); ?>"
									width="200" height="60" loading="lazy"
									<?php if ( ! empty( $po_g_lockup['style'] ) ) : ?>
										style="<?php echo esc_attr( $po_g_lockup['style'] ); ?>"
									<?php endif; ?>>
							</picture>
					</div>
					<p class="po-grid__tagline"><?php echo esc_html( $po_col['tagline'] ); ?></p>
				</header>

				<?php if ( ! empty( $po_items ) ) : ?>
					<div class="po-grid__items">
						<?php
						foreach ( $po_items as $po_item ) :
							$po_sku         = isset( $po_item['sku'] ) ? $po_item['sku'] : '';
							$po_name        = isset( $po_item['name'] ) ? $po_item['name'] : '';
							$po_edition     = isset( $po_item['edition_size'] ) ? (int) $po_item['edition_size'] : 0;
							$po_wc_id       = isset( $po_item['wc_product_id'] ) ? (int) $po_item['wc_product_id'] : 0;
							$po_price_str   = skyyrose_format_price( $po_item );
							$po_img_front   = skyyrose_product_image_uri(
								skyyrose_get_product_display_image( $po_item )
							);
							$po_img_back    = skyyrose_product_image_uri(
								isset( $po_item['back_model_image'] ) ? $po_item['back_model_image']
									: ( isset( $po_item['back_image'] ) ? $po_item['back_image'] : '' )
							);
							$po_product_url = skyyrose_product_url( $po_sku );
							?>
							<article class="po-card holo" aria-label="<?php echo esc_attr( $po_name ); ?>">
								<a class="po-card__img-wrap" href="<?php echo esc_url( $po_product_url ); ?>"
									tabindex="-1" aria-hidden="true">
									<img class="po-card__img po-card__img--front"
										src="<?php echo esc_url( $po_img_front ); ?>"
										alt="<?php echo esc_attr( $po_name ); ?>"
										width="400" height="500" loading="lazy">
									<?php if ( $po_img_back ) : ?>
										<img class="po-card__img po-card__img--back"
											src="<?php echo esc_url( $po_img_back ); ?>"
											alt="<?php echo esc_attr( sprintf( /* translators: %s: product name */ __( '%s — back view', 'skyyrose' ), $po_name ) ); ?>"
											width="400" height="500" loading="lazy" aria-hidden="true">
									<?php endif; ?>
								</a>

								<div class="po-card__body">
									<div class="po-card__meta">
										<h3 class="po-card__name">
											<a href="<?php echo esc_url( $po_product_url ); ?>">
												<?php echo esc_html( $po_name ); ?>
											</a>
										</h3>
										<?php if ( $po_edition > 0 ) : ?>
											<span class="po-card__edition">
												<?php
												echo esc_html(
													sprintf(
														/* translators: %d: edition size number */
														__( 'Edition of %d', 'skyyrose' ),
														$po_edition
													)
												);
												?>
											</span>
										<?php endif; ?>
									</div>

									<?php
									/*
									 * Reserve meters: gated by filter (default false).
									 * NEVER enable until real WC stock data is wired.
									 * Do NOT use stub "31 of 80" counts in production.
									 */
									if ( $po_meters_on && $po_edition > 0 ) :
										?>
										<div class="po-card__meter"
											aria-label="<?php esc_attr_e( 'Reservation availability', 'skyyrose' ); ?>">
											<div class="po-card__meter-bar" aria-hidden="true">
												<div class="po-card__meter-fill" style="width:0%"></div>
											</div>
										</div>
									<?php endif; ?>

									<div class="po-card__footer">
										<span class="po-card__price"><?php echo esc_html( $po_price_str ); ?></span>
										<?php if ( $po_wc_id ) : ?>
											<?php
											// AJAX add-to-cart (WS5): WooCommerce's global add-to-cart.js
											// intercepts .ajax_add_to_cart clicks and POSTs wc-ajax=add_to_cart
											// with data-product_id. The href is the no-JS fallback and points
											// at the PDP — never a GET ?add-to-cart= URL (crawler cart-adds,
											// cache poisoning).
											?>
											<a class="po-btn po-btn--reserve add_to_cart_button ajax_add_to_cart"
												href="<?php echo esc_url( $po_product_url ); ?>"
											data-product_id="<?php echo esc_attr( (string) $po_wc_id ); ?>"
												data-quantity="1"
												rel="nofollow"
												aria-label="<?php echo esc_attr( sprintf( /* translators: %s: product name */ __( 'Reserve %s', 'skyyrose' ), $po_name ) ); ?>">
												<?php esc_html_e( 'Reserve', 'skyyrose' ); ?>
											</a>
										<?php else : ?>
											<a class="po-btn po-btn--reserve po-btn--reserve-link"
												href="<?php echo esc_url( $po_product_url ); ?>"
												aria-label="<?php echo esc_attr( sprintf( /* translators: %s: product name */ __( 'View %s', 'skyyrose' ), $po_name ) ); ?>">
												<?php esc_html_e( 'View', 'skyyrose' ); ?>
											</a>
										<?php endif; ?>
									</div>
								</div>
							</article>
						<?php endforeach; ?>
					</div>
				<?php else : ?>
					<p class="po-grid__empty"><?php esc_html_e( 'Pieces coming soon.', 'skyyrose' ); ?></p>
				<?php endif; ?>
			</div>
			<?php
			$po_grid_first = false;
		endforeach;
		?>
	</section>

	<!-- ══════════════════════════════════════════════════════════════════
		05 · STICKY CART SUMMARY BAR
		══════════════════════════════════════════════════════════════════ -->
	<div class="po-cart-bar" id="po-cart-bar" role="complementary"
		aria-label="<?php esc_attr_e( 'Cart summary', 'skyyrose' ); ?>"
		aria-live="polite" aria-atomic="true">
		<div class="po-cart-bar__inner">
			<div class="po-cart-bar__summary">
				<span class="po-cart-bar__count" id="po-cart-count" aria-label="<?php esc_attr_e( 'Items in cart', 'skyyrose' ); ?>">
					<?php esc_html_e( '0 items', 'skyyrose' ); ?>
				</span>
				<span class="po-cart-bar__sep" aria-hidden="true">&mdash;</span>
				<span class="po-cart-bar__total" id="po-cart-total">
					<?php echo esc_html( $po_currency . '0.00' ); ?>
				</span>
			</div>
			<div class="po-cart-bar__actions">
				<a class="po-btn po-btn--ghost-sm" href="<?php echo esc_url( $po_cart_url ); ?>">
					<?php esc_html_e( 'View Cart', 'skyyrose' ); ?>
				</a>
				<a class="po-btn po-btn--primary-sm" href="<?php echo esc_url( $po_checkout_url ); ?>">
					<?php esc_html_e( 'Checkout', 'skyyrose' ); ?>
				</a>
			</div>
		</div>
	</div>

	<!-- ══════════════════════════════════════════════════════════════════
		06 · PRODUCTION JOURNEY  (5 beats)
		══════════════════════════════════════════════════════════════════ -->
	<section class="po-journey" id="po-journey"
		aria-label="<?php esc_attr_e( 'How your piece is made', 'skyyrose' ); ?>">

		<header class="po-journey__header">
			<p class="po-journey__eyebrow po-rv"><?php esc_html_e( 'The Process', 'skyyrose' ); ?></p>
			<h2 class="po-journey__title po-rv"><?php esc_html_e( 'Built from the concrete up.', 'skyyrose' ); ?></h2>
		</header>

		<?php
		$po_journey_steps = array(
			array(
				'num'   => '01',
				'title' => __( 'Reserve', 'skyyrose' ),
				'copy'  => __( 'You claim your piece. Limited quantities, no restocks.', 'skyyrose' ),
			),
			array(
				'num'   => '02',
				'title' => __( 'Production', 'skyyrose' ),
				'copy'  => __( 'Every garment cut and sewn in the precise run size. No overstock, no waste.', 'skyyrose' ),
			),
			array(
				'num'   => '03',
				'title' => __( 'Quality Gate', 'skyyrose' ),
				'copy'  => __( 'Each piece passes a hands-on review before it leaves the floor.', 'skyyrose' ),
			),
			array(
				'num'   => '04',
				'title' => __( 'Ship', 'skyyrose' ),
				'copy'  => __( 'Delivered to your door. Tracked. Protected.', 'skyyrose' ),
			),
			array(
				'num'   => '05',
				'title' => __( 'Yours', 'skyyrose' ),
				'copy'  => __( 'One of a defined number. Carry it knowing exactly what it is.', 'skyyrose' ),
			),
		);
		?>
		<ol class="po-journey__steps">
			<?php foreach ( $po_journey_steps as $po_step ) : ?>
				<li class="po-journey__step po-rv">
					<span class="po-journey__step-num" aria-hidden="true"><?php echo esc_html( $po_step['num'] ); ?></span>
					<div class="po-journey__step-body">
						<h3 class="po-journey__step-title"><?php echo esc_html( $po_step['title'] ); ?></h3>
						<p class="po-journey__step-copy"><?php echo esc_html( $po_step['copy'] ); ?></p>
					</div>
				</li>
			<?php endforeach; ?>
		</ol>
	</section>

	<!-- ══════════════════════════════════════════════════════════════════
		07 · LOOKBOOK BAND
		══════════════════════════════════════════════════════════════════ -->
	<section class="po-lookbook" id="po-lookbook"
		aria-label="<?php esc_attr_e( 'Lookbook', 'skyyrose' ); ?>">

		<header class="po-lookbook__header po-rv">
			<p class="po-lookbook__eyebrow"><?php esc_html_e( 'Lookbook', 'skyyrose' ); ?></p>
			<h2 class="po-lookbook__title"><?php esc_html_e( 'Worn.', 'skyyrose' ); ?></h2>
		</header>

		<div class="po-lookbook__strip">
			<?php
			/* Lookbook entries from visual-manifest.json */
			$po_lookbook_items = array(
				array(
					'key'  => 'lb-black-rose-football',
					'avif' => $po_assets . '/images/lookbook/lb-black-rose-football-960w.avif?v=' . $po_ver,
					'webp' => $po_assets . '/images/lookbook/lb-black-rose-football-960w.webp?v=' . $po_ver,
					'alt'  => esc_attr__( 'Black Rose football jersey', 'skyyrose' ),
					'w'    => 960,
					'h'    => 1200,
				),
				array(
					'key'  => 'lb-black-rose-hockey',
					'avif' => $po_assets . '/images/lookbook/lb-black-rose-hockey-960w.avif?v=' . $po_ver,
					'webp' => $po_assets . '/images/lookbook/lb-black-rose-hockey-960w.webp?v=' . $po_ver,
					'alt'  => esc_attr__( 'Black Rose hockey jersey', 'skyyrose' ),
					'w'    => 960,
					'h'    => 1200,
				),
				array(
					'key'  => 'lb-love-hurts-varsity',
					'avif' => $po_assets . '/images/lookbook/lb-love-hurts-varsity-960w.avif?v=' . $po_ver,
					'webp' => $po_assets . '/images/lookbook/lb-love-hurts-varsity-960w.webp?v=' . $po_ver,
					'alt'  => esc_attr__( 'Love Hurts varsity jacket', 'skyyrose' ),
					'w'    => 960,
					'h'    => 1200,
				),
				array(
					'key'  => 'lb-rose-hoodie-beanie',
					'avif' => $po_assets . '/images/lookbook/lb-rose-hoodie-beanie-960w.avif?v=' . $po_ver,
					'webp' => $po_assets . '/images/lookbook/lb-rose-hoodie-beanie-960w.webp?v=' . $po_ver,
					'alt'  => esc_attr__( 'Rose hoodie and beanie', 'skyyrose' ),
					'w'    => 960,
					'h'    => 1200,
				),
			);
			foreach ( $po_lookbook_items as $po_lb ) :
				?>
				<figure class="po-lookbook__figure po-rv">
					<picture>
						<source srcset="<?php echo esc_url( $po_lb['avif'] ); ?>" type="image/avif">
						<source srcset="<?php echo esc_url( $po_lb['webp'] ); ?>" type="image/webp">
						<img src="<?php echo esc_url( $po_lb['webp'] ); ?>"
							alt="<?php echo esc_attr( $po_lb['alt'] ); ?>"
							width="<?php echo absint( $po_lb['w'] ); ?>"
							height="<?php echo absint( $po_lb['h'] ); ?>"
							loading="lazy">
					</picture>
				</figure>
			<?php endforeach; ?>
		</div>
	</section>

	<!-- ══════════════════════════════════════════════════════════════════
		08 · MANIFESTO STRIP
		══════════════════════════════════════════════════════════════════ -->
	<section class="po-manifesto" id="po-manifesto"
		aria-label="<?php esc_attr_e( 'Brand manifesto', 'skyyrose' ); ?>">

		<div class="po-manifesto__bg" aria-hidden="true">
			<!--
			 * Using luxury-nighttime (brand_global) — NOT forbidden-midnight.
			 * forbidden-midnight is Black Rose collection only.
			 * luxury-nighttime is the correct multi-collection backdrop.
			-->
			<picture>
				<source
					srcset="<?php echo esc_url( $po_assets . '/branding/hero/luxury-nighttime-480w.webp?v=' . $po_ver ); ?> 480w,
							<?php echo esc_url( $po_assets . '/branding/hero/luxury-nighttime-1280w.webp?v=' . $po_ver ); ?> 1280w,
							<?php echo esc_url( $po_assets . '/branding/hero/luxury-nighttime-1680w.webp?v=' . $po_ver ); ?> 1680w"
					sizes="100vw"
					type="image/webp">
				<img src="<?php echo esc_url( $po_assets . '/branding/hero/luxury-nighttime-1680w.jpg?v=' . $po_ver ); ?>"
					alt="" width="1680" height="945" loading="lazy">
			</picture>
			<div class="po-manifesto__overlay" aria-hidden="true"></div>
		</div>

		<div class="po-manifesto__content">
			<picture class="po-manifesto__seal po-rv" aria-hidden="true">
				<!--
				 * Circular seal: WHITE SQUARE background.
				 * CSS handles: border-radius:50% + object-fit:cover per manifest rule.
				-->
				<source srcset="<?php echo esc_url( $po_assets . '/images/logos/skyy-rose-collection-circular-patch.avif?v=' . $po_ver ); ?>" type="image/avif">
				<source srcset="<?php echo esc_url( $po_assets . '/images/logos/skyy-rose-collection-circular-patch.webp?v=' . $po_ver ); ?>" type="image/webp">
				<img src="<?php echo esc_url( $po_assets . '/images/logos/skyy-rose-collection-circular-patch.jpeg?v=' . $po_ver ); ?>"
					alt="" width="120" height="120" loading="lazy">
			</picture>

			<p class="po-manifesto__body po-rv">
				<?php esc_html_e( 'Every piece in every collection is a limited number. Defined. Finite. When the run closes it stays closed. This is not a drop. This is a record.', 'skyyrose' ); ?>
			</p>

			<a class="po-btn po-btn--primary po-rv" href="#po-gateway">
				<?php esc_html_e( 'Reserve Your Piece', 'skyyrose' ); ?>
			</a>
		</div>
	</section>

	<!-- ══════════════════════════════════════════════════════════════════
		09 · FAQ
		══════════════════════════════════════════════════════════════════ -->
	<section class="po-faq" id="po-faq"
		aria-label="<?php esc_attr_e( 'Frequently asked questions', 'skyyrose' ); ?>">

		<header class="po-faq__header">
			<h2 class="po-faq__title po-rv"><?php esc_html_e( 'Questions', 'skyyrose' ); ?></h2>
		</header>

		<?php
		$po_faqs = array(
			array(
				'q' => __( 'What is a pre-order?', 'skyyrose' ),
				'a' => __( 'You reserve your piece before production closes. Your order locks your place in the run. Once the edition sells out, it does not reopen.', 'skyyrose' ),
			),
			array(
				'q' => __( 'When will my order ship?', 'skyyrose' ),
				'a' => __( 'Pre-orders ship after production completes for your collection run. You will receive a tracking number the moment your piece leaves the floor.', 'skyyrose' ),
			),
			array(
				'q' => __( 'Can I cancel or exchange my pre-order?', 'skyyrose' ),
				'a' => __( 'Pre-orders are final once placed. If there is a defect or fulfillment error, reach out to us directly — we will make it right.', 'skyyrose' ),
			),
			array(
				'q' => __( 'What sizes are available?', 'skyyrose' ),
				'a' => __( 'Size availability varies by piece. Check the product page for current options. If your size is gone, the run is closed.', 'skyyrose' ),
			),
			array(
				'q' => __( 'How are edition sizes determined?', 'skyyrose' ),
				'a' => __( 'Each piece has a defined number set before production opens. That number does not change — no reprints, no restocks.', 'skyyrose' ),
			),
		);

		$po_faq_index = 0;
		foreach ( $po_faqs as $po_faq ) :
			$po_faq_id   = 'po-faq-' . $po_faq_index;
			$po_panel_id = 'po-faq-panel-' . $po_faq_index;
			?>
			<div class="po-accordion po-rv">
				<h3 class="po-accordion__heading">
					<button type="button"
						class="po-accordion-btn"
						id="<?php echo esc_attr( $po_faq_id ); ?>"
						aria-expanded="false"
						aria-controls="<?php echo esc_attr( $po_panel_id ); ?>">
						<?php echo esc_html( $po_faq['q'] ); ?>
						<span class="po-accordion-icon" aria-hidden="true"></span>
					</button>
				</h3>
				<div class="po-accordion-panel"
					id="<?php echo esc_attr( $po_panel_id ); ?>"
					role="region"
					aria-labelledby="<?php echo esc_attr( $po_faq_id ); ?>">
					<div class="po-accordion-panel__inner">
						<p><?php echo esc_html( $po_faq['a'] ); ?></p>
					</div>
				</div>
			</div>
			<?php
			++$po_faq_index;
		endforeach;
		?>
	</section>

	<!-- ══════════════════════════════════════════════════════════════════
		10 · EMAIL CAPTURE
		══════════════════════════════════════════════════════════════════ -->
	<section class="po-email-capture" id="po-email-capture"
		aria-label="<?php esc_attr_e( 'Stay informed about new drops', 'skyyrose' ); ?>">

		<div class="po-email-capture__inner">
			<picture class="po-email-capture__art po-rv" aria-hidden="true">
				<source srcset="<?php echo esc_url( $po_assets . '/images/logos/sr-monogram-gold.avif?v=' . $po_ver ); ?>" type="image/avif">
				<source srcset="<?php echo esc_url( $po_assets . '/images/logos/sr-monogram-gold.webp?v=' . $po_ver ); ?>" type="image/webp">
				<img src="<?php echo esc_url( $po_assets . '/images/logos/sr-monogram-gold.jpeg?v=' . $po_ver ); ?>"
					alt="" width="200" height="200" loading="lazy">
			</picture>

			<div class="po-email-capture__copy">
				<h2 class="po-email-capture__title po-rv">
					<?php esc_html_e( 'First access. Always.', 'skyyrose' ); ?>
				</h2>
				<p class="po-email-capture__sub po-rv">
					<?php esc_html_e( 'Drop alerts before they open. No noise.', 'skyyrose' ); ?>
				</p>
			</div>

			<form class="po-email-form po-rv" id="po-email-form"
				aria-label="<?php esc_attr_e( 'Subscribe for drop alerts', 'skyyrose' ); ?>">

				<?php wp_nonce_field( 'skyyrose-nonce', 'nonce' ); ?>

				<div class="po-email-form__row">
					<label for="po-email-input" class="screen-reader-text">
						<?php esc_html_e( 'Email address', 'skyyrose' ); ?>
					</label>
					<input type="email"
						id="po-email-input"
						name="email"
						class="po-email-form__input"
						placeholder="<?php esc_attr_e( 'your@email.com', 'skyyrose' ); ?>"
						autocomplete="email"
						required
						aria-required="true">
					<button type="submit" class="po-btn po-btn--primary">
						<?php esc_html_e( 'Notify Me', 'skyyrose' ); ?>
					</button>
				</div>

				<p class="po-email-form__status" id="po-email-status" role="status" aria-live="polite" aria-atomic="true"></p>
			</form>
		</div>
	</section>

</main><!-- #primary.po-page -->

<?php get_footer(); ?>
