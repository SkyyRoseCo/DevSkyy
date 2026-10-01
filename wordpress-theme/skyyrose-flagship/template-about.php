<?php
/**
 * Template Name: About
 *
 * Editorial scroll-cinema, streetwear-luxury register (KITH lookbook x FOG Eternal restraint).
 *
 * Sections: Hero (asymmetric metadata stack) -> Chapter I (Origin)
 *           -> Mission Banner -> Chapter II (Collections grid)
 *           -> Chapter III (Drop Calendar timeline) -> Oakland Manifesto
 *           -> Chapter IV (Press Room newspaper).
 *
 * Content sources:
 *   - knowledge-base/seed/press-features.md -> $press_features + $youtube_embed_id
 *   - knowledge-base/seed/timeline.md       -> $timeline_milestones
 *   - knowledge-base/seed/from-interview.md -> Oakland canon, brand voice
 *   - .claude memory project_founder_voice.md -> founder bio voice register
 *
 * @package SkyyRose
 * @since   1.3.0
 */

defined( 'ABSPATH' ) || exit;
get_header();

// wp_kses inline whitelist shared across partials.
$allowed_inline = array(
	'em'     => array(),
	'strong' => array(),
	'br'     => array(),
);

// Hero portrait (Skyy Rose). User-locked image — do not change file path
// without explicit confirmation.
$hero_img = get_theme_file_uri( 'assets/images/homepage-story-founder.webp' );

// Hero metadata stack (KITH-style lookbook header).
$hero_meta = array(
	array(
		'key' => 'Founded',
		'val' => '2020',
	),
	array(
		'key' => 'City',
		'val' => 'Oakland, CA',
	),
	array(
		'key' => 'Audience',
		'val' => 'Gender Neutral',
	),
	array(
		'key' => 'Chapters',
		'val' => '4 Collections',
	),
);

// Chapter I — origin paragraphs.
// Quote: verbatim from collection-stories.md § Signature — The founding moment.
$origin_quote      = '"I drew the first rose on a night I couldn\'t afford dinner. Broke, a baby on the way, every manufacturer I\'d worked with had scammed me. But I sat there sketching that script logo until 4 AM because something in me knew — if I could get this right, everything changes. Signature is that night made permanent."';
$origin_cite       = 'Corey Foster — Founder & CEO';
$origin_paragraphs = array(
	'SkyyRose was never just a clothing brand. It was a promise &mdash; born in Deep East Oakland, forged by a single father who refused to let his circumstances write his daughter\'s story. <strong>Corey Foster</strong> named the brand after his reason for everything: his daughter, <strong>Skyy Rose</strong>.',
	'The rebrand is the full realization of that promise. Four collections, each with its own world, its own story, its own identity &mdash; unified under one crown. Oakland-born luxury streetwear that doesn\'t apologize for where it came from. It <strong>celebrates</strong> it.',
	'Fashion was always self-expression. Growing up in Oakland\'s toughest neighborhoods, what you wore said everything &mdash; who you were, where you were going, what you refused to accept. SkyyRose carries that energy into every thread, every stitch, every rose.',
);

// Chapter III — canonical timeline (knowledge-base/seed/timeline.md).
$timeline_milestones = array(
	array(
		'year'  => '2020',
		'event' => 'The Beginning',
		'desc'  => 'Single father in Deep East Oakland. Searching for something his daughter could wear. Nothing fit the eye. He made it himself. The brand carries her name.',
	),
	array(
		'year'  => '2021',
		'event' => 'Three Chapters Drop',
		'desc'  => 'Black Rose. Love Hurts. Signature. Three collections, one name &mdash; not a launch, a declaration.',
	),
	array(
		'year'  => '2023',
		'event' => 'National Recognition',
		'desc'  => 'Maxim names Corey Foster one of 14 game-changing entrepreneurs to watch. The work travels past the city limits.',
	),
	array(
		'year'  => '2024',
		'event' => 'The Year of Receipts',
		'desc'  => 'San Francisco Post profile. Best Bay Area Clothing Line Award. CEO Weekly cover story. The Blox interview. Independent press confirms what Oakland already knew.',
	),
	array(
		'year'  => '2026',
		'event' => 'The Kids Capsule',
		'desc'  => 'The fourth chapter. Same craftsmanship, smaller silhouettes. Passing the torch on the same terms that built the brand.',
	),
);

// Oakland manifesto — neighborhoods/places. Brand canon (from-interview.md).
$manifesto_places = array(
	'Deep East',
	'The Hills',
	'Stone City',
	'The 100s',
	'Brookfield',
	'Sobrante Park',
	'Coliseum',
	'Real Oakland',
	'The Shows',
	'Sequoyah Highlands',
	'Lake Merritt',
	'The 510',
);

$community_frame = 'The Town never asked permission to be itself. Neither did he. Lake Merritt at golden hour, the 510 humming under everything, Mac Dre on the speakers like a saint &mdash; that\'s the studio. The studio is also a laptop on a folding table at the airport lounge between shifts. Both things true. Both things the brand.';

// Chapter IV — press features (knowledge-base/seed/press-features.md).
$press_features = array(
	array(
		'src'      => 'Maxim',
		'year'     => 'Feb 2023',
		'headline' => '14 Game-Changing Entrepreneurs To Watch In 2023',
		'excerpt'  => 'Corey Foster is an innovative entrepreneur and artist who has created a truly unique clothing line. The Skyy Rose Collection blends fashion with streetwear &mdash; high quality, beautiful, unique.',
		'url'      => 'https://www.maxim.com/partner/14-game-changing-entrepreneurs-to-watch-in-2023/',
	),
	array(
		'src'      => 'San Francisco Post',
		'year'     => 'Aug 2024',
		'headline' => 'From Oakland\'s Streets to Fashion Heights',
		'excerpt'  => 'A trailblazing gender-neutral clothing brand redefining fashion in the Bay Area and beyond. Established by Corey Foster, a single father with a dream &mdash; this Oakland-based brand embodies resilience and creativity.',
		'url'      => 'https://sanfranciscopost.com/the-skyy-rose-collection-from-oaklands-streets-to-fashion-heights/',
	),
	array(
		'src'      => 'Best of Best Review',
		'year'     => 'Aug 2024',
		'headline' => 'Best Bay Area Clothing Line Award 2024',
		'excerpt'  => 'The Skyy Rose Collection has been honored with the prestigious Best Bay Area Clothing Line Award 2024 &mdash; recognized for high-end, gender-neutral clothing that transcends age and gender boundaries.',
		'url'      => 'https://bestofbestreview.com/awards/the-skyy-rose-collection-best-bay-area-clothing-line-award-2024',
	),
	array(
		'src'      => 'CEO Weekly',
		'year'     => 'Oct 2024',
		'headline' => 'The Unyielding Journey of a Single Father and Entrepreneur',
		'excerpt'  => 'Despite numerous setbacks &mdash; failed website attempts, deceitful manufacturers &mdash; this indomitable spirit refused to be quenched. SkyyRose represents hope, hard work, and the relentless spirit of never giving up.',
		'url'      => 'https://ceoweekly.com/the-unyielding-journey-of-a-single-father-and-entrepreneur/',
	),
);

// The Blox YouTube embed — verified via YouTube oEmbed 2026-05-13.
$youtube_embed_id = 'Ja11W-g34Zo';

// Arrow SVG for press "READ" affordance.
$arrow_svg = '<svg width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M9 1L13 5L9 9M13 5H1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
?>

<main id="primary" class="site-main abt-page" role="main">

	<!-- Hero — Editorial Lookbook Header (asymmetric, no full-bleed bg) -->
	<section class="abt-hero" aria-label="<?php esc_attr_e( 'About SkyyRose', 'skyyrose' ); ?>">
		<div class="abt-hero__grid">
			<div class="abt-hero__left">
				<?php
				// The hero is the first mobile viewport and the title is the LCP
				// element — no reveal classes here: the hidden resting state stalls
				// LCP behind the deferred JS queue (the PDP 24.9s bug class).
				// Below-fold chapters keep reveals. Wave 5.
				?>
				<p class="abt-hero__doc">
					<span><?php esc_html_e( 'About', 'skyyrose' ); ?></span>
					<span class="abt-hero__doc-sep" aria-hidden="true">/</span>
					<span><?php esc_html_e( 'SR-001', 'skyyrose' ); ?></span>
				</p>
				<h1 class="abt-hero__title">
					<?php echo wp_kses( __( 'The<br>Story', 'skyyrose' ), $allowed_inline ); ?>
				</h1>
				<dl class="abt-hero__meta">
					<?php foreach ( $hero_meta as $row ) : ?>
						<div class="abt-hero__meta-row">
							<dt><?php echo esc_html( $row['key'] ); ?></dt>
							<dd><?php echo esc_html( $row['val'] ); ?></dd>
						</div>
					<?php endforeach; ?>
				</dl>
			</div>
			<div class="abt-hero__right">
				<figure class="abt-hero__portrait">
					<img src="<?php echo esc_url( $hero_img ); ?>"
						alt="<?php esc_attr_e( 'SkyyRose origin portrait', 'skyyrose' ); ?>"
						fetchpriority="high"
						width="900" height="1350">
					<figcaption class="abt-hero__portrait-cap" aria-hidden="true">
						<?php esc_html_e( 'Skyy Rose &mdash; The Heir', 'skyyrose' ); ?>
					</figcaption>
				</figure>
			</div>
		</div>
		<div class="abt-hero__scroll" aria-hidden="true">
			<span><?php esc_html_e( 'Scroll', 'skyyrose' ); ?></span>
			<span class="abt-hero__scroll-line"></span>
		</div>
	</section>

	<!-- Featured Video — The Blox interview (relocated above Chapter I) -->
	<?php
	get_template_part(
		'template-parts/about/featured-video',
		null,
		array(
			'youtube_embed_id' => $youtube_embed_id,
		)
	);
	?>

	<!-- Chapter I — The Rebrand -->
	<?php
	get_template_part(
		'template-parts/about/chapter-origin',
		null,
		array(
			'allowed_inline'    => $allowed_inline,
			'origin_quote'      => $origin_quote,
			'origin_cite'       => $origin_cite,
			'origin_paragraphs' => $origin_paragraphs,
		)
	);
	?>

	<!-- Mission Banner -->
	<?php
	get_template_part(
		'template-parts/about/mission',
		null,
		array(
			'allowed_inline' => $allowed_inline,
		)
	);
	?>

	<!-- Chapter II — Collections Grid -->
	<?php get_template_part( 'template-parts/about/collections-grid' ); ?>

	<!-- Chapter III — Drop Calendar Timeline -->
	<?php
	get_template_part(
		'template-parts/about/timeline',
		null,
		array(
			'allowed_inline'      => $allowed_inline,
			'timeline_milestones' => $timeline_milestones,
		)
	);
	?>

	<!-- Oakland Manifesto -->
	<?php
	get_template_part(
		'template-parts/about/community',
		null,
		array(
			'allowed_inline'   => $allowed_inline,
			'manifesto_places' => $manifesto_places,
			'frame_text'       => $community_frame,
			'customer_photos'  => array(),
		)
	);
	?>

	<!-- Chapter IV — Press Room -->
	<?php
	get_template_part(
		'template-parts/about/press-section',
		null,
		array(
			'allowed_inline'   => $allowed_inline,
			'youtube_embed_id' => '', // Relocated to featured-video partial below the hero; press grid keeps the Blox poster.
			'press_features'   => $press_features,
			'arrow_svg'        => $arrow_svg,
		)
	);
	?>

</main>

<?php get_footer(); ?>
