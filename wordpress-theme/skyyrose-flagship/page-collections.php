<?php
/**
 * Collections Index — /collections/ (flagship shell).
 *
 * Template-hierarchy page for the 'collections' page slug (structural
 * remediation WS1/WS2). Replaces the shell-less skyyrose-canvas.php canvas
 * (a stale live-only file, absent from the repo) that rendered an empty
 * page with no header, footer, or Kids Capsule.
 *
 * Editorial index of all four collections — no product grids. Cards are
 * config-driven (inc/collections-config.php) and piece counts derive from
 * the canonical catalog CSV via skyyrose_get_collection_products(), exposed
 * through the same data-collection/data-piece-count contract the homepage
 * uses so scripts/structural_audit.py can assert the surfaces agree.
 *
 * @package SkyyRose
 * @since   1.8.0
 */

defined( 'ABSPATH' ) || exit;

$ci_config = skyyrose_get_collections_config();

/* Lockup images — collection names render as brand-script lockups, never type. */
$ci_lockups = array(
	'black-rose'   => array(
		'base' => 'hero-overlays/br-brand-script-logotype',
		'ext'  => 'png',
	),
	'love-hurts'   => array(
		'base' => 'hero-overlays/lh-logo-combined',
		'ext'  => 'png',
	),
	'signature'    => array(
		'base' => 'hero-overlays/sig-brand-skyy-rose-gold',
		'ext'  => 'png',
	),
	'kids-capsule' => array(
		'base' => 'logos/sr-monogram-rose-gold',
		'ext'  => 'webp',
	),
);

get_header();
?>

<main id="primary" class="site-main collections-index" role="main" tabindex="-1">

	<?php
	// Above the fold — no reveal class on the hero: the hidden resting state
	// stalls LCP behind the deferred JS queue (the PDP 24.9s bug class). The
	// first ci-card is exempted from the stagger in collections-index.css. Wave 5.
	?>
	<section class="ci-hero">
		<p class="ci-hero__eyebrow"><?php esc_html_e( 'The Collections', 'skyyrose' ); ?></p>
		<h1 class="ci-hero__title"><?php esc_html_e( 'Four Collections. One Vision.', 'skyyrose' ); ?></h1>
		<p class="ci-hero__subtitle"><?php esc_html_e( 'Every piece limited, numbered, and never restocked.', 'skyyrose' ); ?></p>
	</section>

	<section class="ci-grid stagger-grid" aria-label="<?php esc_attr_e( 'All collections', 'skyyrose' ); ?>">
		<?php
		$ci_index = 0;
		foreach ( $ci_config as $ci_slug => $ci_col ) :
			$ci_count  = count( skyyrose_get_collection_products( $ci_slug ) );
			$ci_lockup = $ci_lockups[ $ci_slug ] ?? null;
			?>
			<a href="<?php echo esc_url( $ci_col['page_url'] ); ?>" class="ci-card ci-card--<?php echo esc_attr( $ci_col['class_abbr'] ?? $ci_slug ); ?> magnetic" data-collection="<?php echo esc_attr( $ci_slug ); ?>" data-piece-count="<?php echo esc_attr( (string) $ci_count ); ?>">
				<div class="ci-card__body">
					<p class="ci-card__num"><?php echo esc_html( sprintf( '%02d', $ci_index + 1 ) ); ?></p>
					<?php if ( $ci_lockup ) : ?>
						<?php
						$ci_lk_uri = SKYYROSE_ASSETS_URI . '/images/' . $ci_lockup['base'];
						// Lockups render at ≤300px (min(300px, 70%) in collections-index.css)
						// but shipped as full-size AVIF sources (48-88KB each — round-3
						// uses-responsive-images, 690ms). Photon width variants via the
						// .webp sibling; the avif <source> is suppressed while Photon
						// answers (Photon serves webp — keeps type= honest, same trade
						// as skyyrose_render_picture()). '' return = previous markup.
						$ci_srcset = function_exists( 'skyyrose_photon_srcset' )
							? skyyrose_photon_srcset( $ci_lk_uri . '.webp', array( 320, 640, 960 ) )
							: '';
						$ci_sizes  = '(max-width: 430px) 70vw, 300px';
						?>
						<picture class="ci-card__name">
							<?php if ( '' !== $ci_srcset ) : ?>
								<source srcset="<?php echo esc_attr( $ci_srcset ); ?>" sizes="<?php echo esc_attr( $ci_sizes ); ?>" type="image/webp">
							<?php else : ?>
								<source srcset="<?php echo esc_url( $ci_lk_uri . '.avif' ); ?>" type="image/avif">
								<source srcset="<?php echo esc_url( $ci_lk_uri . '.webp' ); ?>" type="image/webp">
							<?php endif; ?>
							<img src="<?php echo esc_url( $ci_lk_uri . '.' . $ci_lockup['ext'] ); ?>"
								<?php if ( '' !== $ci_srcset ) : ?>
									srcset="<?php echo esc_attr( $ci_srcset ); ?>"
									sizes="<?php echo esc_attr( $ci_sizes ); ?>"
								<?php endif; ?>
								alt=""
								loading="<?php echo 0 === $ci_index ? 'eager' : 'lazy'; ?>"
								decoding="async"
								class="ci-card__lockup">
						</picture>
						<span class="screen-reader-text"><?php echo esc_html( $ci_col['label'] ); ?></span>
					<?php else : ?>
						<h2 class="ci-card__name-text"><?php echo esc_html( $ci_col['label'] ); ?></h2>
					<?php endif; ?>
					<p class="ci-card__tagline"><?php echo esc_html( $ci_col['tagline'] ); ?></p>
					<p class="ci-card__desc"><?php echo esc_html( $ci_col['description'] ); ?></p>
					<div class="ci-card__meta">
						<span><?php echo esc_html( ( $ci_count ? $ci_count : '—' ) . ' ' . __( 'Pieces', 'skyyrose' ) ); ?></span>
						<span><?php echo esc_html( $ci_col['short_desc'] ); ?></span>
					</div>
					<span class="ci-card__cta"><?php esc_html_e( 'Explore Collection', 'skyyrose' ); ?> &rarr;</span>
				</div>
			</a>
			<?php
			++$ci_index;
		endforeach;
		?>
	</section>

	<section class="ci-preorder rv-blur">
		<h2 class="ci-preorder__title"><?php esc_html_e( 'Reserve Before the Drop', 'skyyrose' ); ?></h2>
		<p class="ci-preorder__text"><?php esc_html_e( 'Pre-order pieces are numbered in the order they are claimed.', 'skyyrose' ); ?></p>
		<a href="<?php echo esc_url( home_url( '/pre-order/' ) ); ?>" class="ci-preorder__btn btn btn-ghost btn-sweep btn-press"><?php esc_html_e( 'Enter Pre-Order', 'skyyrose' ); ?></a>
	</section>

</main>

<?php
get_footer();
