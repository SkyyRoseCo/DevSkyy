<?php
/**
 * Founder page: V1 source photography and press record in the V2 system.
 *
 * Every image asset actually rendered by V1's About template is carried here:
 * Skyy Rose portrait, The Blox poster, and the four collection lookbook frames.
 * The old optional about-story divider was not included because its source file
 * does not exist in V1.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

// Recovered editorial content is opt-in and remains owned by the page editor.
// Keep the historical presentation below until an archive payload is installed.
$sr2_about_content = get_post_field( 'post_content', get_the_ID() );
if ( has_block( 'core/group', $sr2_about_content ) && preg_match( '/"className"\s*:\s*"[^"\r\n]*\bsr2-about-archive\b/', $sr2_about_content ) ) {
	// Delivery metadata belongs to presentation; the native image block stays editable.
	$sr2_about_image_delivery = static function ( $html ) {
		$tag = new WP_HTML_Tag_Processor( $html );
		if ( ! $tag->next_tag( 'IMG' ) ) {
			return $html;
		}
		$path = wp_parse_url( (string) $tag->get_attribute( 'src' ), PHP_URL_PATH );
		$known = array(
			'/assets/sot/images/about/skyy-rose-founder-hero.webp' => array( 724, 1086, true ),
			'/assets/sot/images/lockups/founder-supplied/signature-sr-rose-graphic-founder-supplied-v1.png' => array( 512, 512, false ),
			'/assets/sot/images/lockups/black-rose-star-graphic.webp' => array( 1254, 1254, false ),
			'/assets/sot/images/lockups/love-hurts-star-heart-graphic.webp' => array( 1254, 1254, false ),
			'/assets/sot/images/logos/sr-monogram-rose-gold.webp' => array( 720, 720, false ),
			'/assets/images/about/kids-heir-founder-supplied.png' => array( 1320, 1336, false ),
			'/assets/images/about/oakland-reference-mural.webp' => array( 480, 220, false ),
			'/assets/images/about/oakland-reference-sign.webp' => array( 170, 105, false ),
		);
		$prefix = wp_parse_url( get_template_directory_uri(), PHP_URL_PATH );
		foreach ( $known as $asset => $meta ) {
			if ( $path === $prefix . $asset ) {
				$tag->set_attribute( 'width', $meta[0] );
				$tag->set_attribute( 'height', $meta[1] );
				$tag->set_attribute( 'loading', $meta[2] ? 'eager' : 'lazy' );
				$tag->set_attribute( 'fetchpriority', $meta[2] ? 'high' : 'low' );
				$tag->set_attribute( 'decoding', 'async' );
				break;
			}
		}
		if ( 'https://i.ytimg.com/vi/Ja11W-g34Zo/hqdefault.jpg' === $tag->get_attribute( 'src' ) ) {
			$tag->set_attribute( 'width', 480 );
			$tag->set_attribute( 'height', 360 );
			$tag->set_attribute( 'loading', 'lazy' );
			$tag->set_attribute( 'decoding', 'async' );
		}
		return $tag->get_updated_html();
	};
	add_filter( 'render_block_core/image', $sr2_about_image_delivery );
	the_content();
	remove_filter( 'render_block_core/image', $sr2_about_image_delivery );
	return;
}

$sr2_about_assets = array(
	'founder'    => 'images/about/skyy-rose-founder-hero.webp',
	'blox'       => 'images/about/the-blox-premiere.webp',
	'signature'  => 'images/lookbook/lb-rose-hoodie-beanie',
	'black_rose' => 'images/lookbook/lb-black-rose-football',
	'love_hurts' => 'images/lookbook/lb-love-hurts-varsity',
	'kids'       => 'images/lookbook/lb-kid-black-rose',
);

$sr2_press_features = skyyrose2_press_features();

$sr2_chapters = array(
	array( 'number' => '01', 'name' => 'Signature', 'line' => 'The first mark. Oakland carried forward.', 'image' => $sr2_about_assets['signature'], 'url' => skyyrose2_collection_url( 'signature' ) ),
	array( 'number' => '02', 'name' => 'Black Rose', 'line' => 'Protection, polish, and refusal.', 'image' => $sr2_about_assets['black_rose'], 'url' => skyyrose2_collection_url( 'black-rose' ) ),
	array( 'number' => '03', 'name' => 'Love Hurts', 'line' => 'Softness and armor in the same piece.', 'image' => $sr2_about_assets['love_hurts'], 'url' => skyyrose2_collection_url( 'love-hurts' ) ),
	array( 'number' => '04', 'name' => 'Kids Capsule', 'line' => 'The next chapter belongs to the heir.', 'image' => $sr2_about_assets['kids'], 'url' => skyyrose2_collection_url( 'kids-capsule' ) ),
);
?>

<section class="sr2-about-hero" aria-labelledby="sr2-page-title">
	<figure class="sr2-about-hero__portrait">
		<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_about_assets['founder'] ) ); ?>" alt="Skyy Rose, the daughter whose name inspired the SkyyRose house" width="900" height="1350" fetchpriority="high">
	</figure>
	<div class="sr2-about-hero__copy">
		<p class="sr2-eyebrow">About / SR–001 / Oakland, California</p>
		<h1 id="sr2-page-title">Built by a father. Named for his daughter.</h1>
		<p>SkyyRose began as Corey Foster's promise to build a future Skyy Rose could recognize herself inside. The house keeps Oakland in the frame: concrete, care, memory, and the refusal to shrink.</p>
		<dl class="sr2-about-hero__facts">
			<div><dt>Founded</dt><dd>2020</dd></div>
			<div><dt>Origin</dt><dd>Oakland, CA</dd></div>
			<div><dt>Design</dt><dd>Gender-neutral</dd></div>
		</dl>
	</div>
</section>

<section class="sr2-about-blox" aria-labelledby="sr2-blox-title">
	<div class="sr2-about-blox__copy">
		<p class="sr2-eyebrow">The Blox / Premiere</p>
		<h2 id="sr2-blox-title">The founder, in his own words.</h2>
		<p>The Blox premiere is not a mood board or a summary. It is the record of the work, the reason for the name, and the city that made the point of view possible.</p>
		<a class="sr2-button" href="https://www.youtube.com/watch?v=Ja11W-g34Zo" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a>
	</div>
	<div class="sr2-about-blox__media">
		<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_about_assets['blox'] ) ); ?>" alt="Corey Foster featured on The Blox" width="1200" height="675" loading="lazy" decoding="async">
		<iframe src="https://www.youtube-nocookie.com/embed/Ja11W-g34Zo?rel=0&amp;modestbranding=1" title="SkyyRose Collection — The Blox premiere" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
	</div>
</section>

<section class="sr2-about-press" aria-labelledby="sr2-press-title">
	<header class="sr2-section-head sr2-section-head--split">
		<div><p>The Record</p><h2 id="sr2-press-title">The press did not make the story. It documented it.</h2></div>
		<p>Each source below is the original published feature—not a recreated quote card.</p>
	</header>
	<div class="sr2-about-press__grid">
		<?php foreach ( $sr2_press_features as $sr2_press_feature ) : ?>
			<article>
				<p><span><?php echo esc_html( $sr2_press_feature['source'] ); ?></span><time><?php echo esc_html( $sr2_press_feature['date'] ); ?></time></p>
				<h3><?php echo esc_html( $sr2_press_feature['title'] ); ?></h3>
				<p><?php echo esc_html( $sr2_press_feature['excerpt'] ); ?></p>
				<a href="<?php echo esc_url( $sr2_press_feature['url'] ); ?>" target="_blank" rel="noopener noreferrer">Read the original ↗</a>
			</article>
		<?php endforeach; ?>
	</div>
</section>

<section class="sr2-about-chapters" aria-labelledby="sr2-chapters-title">
	<header class="sr2-section-head"><p>Four Worlds / One Bloodline</p><h2 id="sr2-chapters-title">The V1 lookbook, carried forward.</h2></header>
	<div class="sr2-about-chapters__grid">
		<?php foreach ( $sr2_chapters as $sr2_chapter ) : ?>
			<a class="sr2-about-chapter" href="<?php echo esc_url( $sr2_chapter['url'] ); ?>">
				<picture>
					<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_chapter['image'] . '-480w.webp' ) ); ?>">
					<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_chapter['image'] . '-960w.webp' ) ); ?>" alt="<?php echo esc_attr( $sr2_chapter['name'] ); ?> lookbook image" width="960" height="1200" loading="lazy" decoding="async">
				</picture>
				<span><?php echo esc_html( $sr2_chapter['number'] ); ?></span><strong><?php echo esc_html( $sr2_chapter['name'] ); ?></strong><em><?php echo esc_html( $sr2_chapter['line'] ); ?></em>
			</a>
		<?php endforeach; ?>
	</div>
</section>

<section class="sr2-about-oakland" aria-labelledby="sr2-oakland-title">
	<p class="sr2-eyebrow">The Town</p>
	<h2 id="sr2-oakland-title">Deep East · The Hills · Stone City · Lake Merritt · The 510</h2>
	<p>SkyyRose is gender-neutral by design and Oakland in its posture. The house was built for the person wearing the piece—not for a category somebody else assigned.</p>
	<a class="sr2-button sr2-button--fill" href="<?php echo esc_url( home_url( '/collections/' ) ); ?>">Enter the collections</a>
</section>
