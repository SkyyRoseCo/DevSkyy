<?php
/**
 * Founder page: V1 source photography and press record in the V2 system.
 *
 * The founder portrait (724×1086) is shown as a portrait column beside the story,
 * never cropped panoramic and never veiled. The Blox premiere still keeps its
 * native frame. The press record is a left-aligned editorial list. Founder copy
 * is restyled, never rewritten.
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
	'founder' => 'images/about/skyy-rose-founder-hero.webp',
	'blox'    => 'images/about/the-blox-premiere.webp',
);

$sr2_press_features = skyyrose2_press_features();

$sr2_chapters = array(
	array( 'number' => '01', 'name' => 'Signature', 'line' => 'The first mark. Oakland carried forward.', 'url' => skyyrose2_collection_url( 'signature' ) ),
	array( 'number' => '02', 'name' => 'Black Rose', 'line' => 'Protection, polish, and refusal.', 'url' => skyyrose2_collection_url( 'black-rose' ) ),
	array( 'number' => '03', 'name' => 'Love Hurts', 'line' => 'Softness and armor in the same piece.', 'url' => skyyrose2_collection_url( 'love-hurts' ) ),
	array( 'number' => '04', 'name' => 'Kids Capsule', 'line' => 'The next chapter belongs to the heir.', 'url' => skyyrose2_collection_url( 'kids-capsule' ) ),
);
?>

<section class="sr2-band sr2-about-arrival" aria-labelledby="sr2-page-title">
	<div class="sr2-about-arrival__grid">
		<figure class="sr2-about-arrival__portrait sr2-image-reveal">
			<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_about_assets['founder'] ) ); ?>" alt="Skyy Rose, the daughter whose name inspired the SkyyRose house" width="724" height="1086" fetchpriority="high" decoding="async">
		</figure>
		<div class="sr2-about-arrival__copy">
			<p class="sr2-eyebrow">About / SR–001 / Oakland, California</p>
			<h1 id="sr2-page-title" class="sr2-title-display">Built by a father. Named for his daughter.</h1>
			<p class="sr2-lede">SkyyRose began as Corey Foster's promise to build a future Skyy Rose could recognize herself inside. The house keeps Oakland in the frame: concrete, care, memory, and the refusal to shrink.</p>
			<dl class="sr2-about-arrival__facts">
				<div><dt>Founded</dt><dd>2020</dd></div>
				<div><dt>Origin</dt><dd>Oakland, CA</dd></div>
				<div><dt>Design</dt><dd>Gender-neutral</dd></div>
			</dl>
		</div>
	</div>
</section>

<section class="sr2-chapter sr2-about-blox" aria-labelledby="sr2-blox-title">
	<figure class="sr2-chapter__scene sr2-about-blox__scene sr2-image-reveal" style="--sr2-scene-ratio: 1344 / 768; --sr2-scene-ratio-mobile: 1344 / 768;">
		<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_about_assets['blox'] ) ); ?>" alt="Corey Foster featured on The Blox" width="1344" height="768" loading="lazy" decoding="async">
		<iframe class="sr2-about-blox__player" src="https://www.youtube-nocookie.com/embed/Ja11W-g34Zo?rel=0&amp;modestbranding=1" title="SkyyRose Collection — The Blox premiere" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
	</figure>
	<div class="sr2-chapter__band">
		<div class="sr2-chapter__copy">
			<p class="sr2-chapter__index sr2-eyebrow sr2-eyebrow--engraved">The Blox / Premiere</p>
			<h2 id="sr2-blox-title" class="sr2-title-chapter">The founder, in his own words.</h2>
			<p class="sr2-lede">The Blox premiere is not a mood board or a summary. It is the record of the work, the reason for the name, and the city that made the point of view possible.</p>
			<a class="sr2-editorial-link" href="https://www.youtube.com/watch?v=Ja11W-g34Zo" target="_blank" rel="noopener noreferrer">Watch on YouTube<span aria-hidden="true">↗</span></a>
		</div>
	</div>
</section>

<section class="sr2-band sr2-about-press" aria-labelledby="sr2-press-title">
	<div class="sr2-band__head">
		<div>
			<p class="sr2-eyebrow">The Record</p>
			<h2 id="sr2-press-title" class="sr2-title-chapter">The press did not make the story. It documented it.</h2>
			<p class="sr2-lede">Each source below is the original published feature—not a recreated quote card.</p>
		</div>
	</div>
	<ol class="sr2-press-list">
		<?php foreach ( $sr2_press_features as $sr2_press_feature ) : ?>
			<li class="sr2-press-list__item">
				<p class="sr2-press-list__meta sr2-eyebrow"><span><?php echo esc_html( $sr2_press_feature['source'] ); ?></span><time><?php echo esc_html( $sr2_press_feature['date'] ); ?></time></p>
				<div class="sr2-press-list__copy">
					<h3 class="sr2-title-editorial"><?php echo esc_html( $sr2_press_feature['title'] ); ?></h3>
					<p><?php echo esc_html( $sr2_press_feature['excerpt'] ); ?></p>
				</div>
				<a class="sr2-editorial-link sr2-press-list__link" href="<?php echo esc_url( $sr2_press_feature['url'] ); ?>" target="_blank" rel="noopener noreferrer">Read the original<span aria-hidden="true">↗</span></a>
			</li>
		<?php endforeach; ?>
	</ol>
</section>

<section class="sr2-band sr2-about-chapters" aria-labelledby="sr2-chapters-title">
	<div class="sr2-page-grid">
		<div class="sr2-page-grid__main">
			<p class="sr2-eyebrow">Four Worlds / One Bloodline</p>
			<h2 id="sr2-chapters-title" class="sr2-title-chapter">The V1 lookbook, carried forward.</h2>
		</div>
		<ol class="sr2-index-list sr2-about-chapters__list sr2-page-grid__aside">
			<?php foreach ( $sr2_chapters as $sr2_chapter ) : ?>
				<li><a href="<?php echo esc_url( $sr2_chapter['url'] ); ?>"><span class="sr2-about-chapters__index sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( $sr2_chapter['number'] ); ?></span><span class="sr2-about-chapters__name"><?php echo esc_html( $sr2_chapter['name'] ); ?><small><?php echo esc_html( $sr2_chapter['line'] ); ?></small></span><span aria-hidden="true">→</span></a></li>
			<?php endforeach; ?>
		</ol>
		<?php
		// The four V1 lookbook frames the heading names (same founder assets page-lookbook.php serves).
		$sr2_about_lookbook = array(
			array( 'name' => 'Signature', 'image' => 'images/lookbook/lb-rose-hoodie-beanie' ),
			array( 'name' => 'Black Rose', 'image' => 'images/lookbook/lb-black-rose-football' ),
			array( 'name' => 'Love Hurts', 'image' => 'images/lookbook/lb-love-hurts-varsity' ),
			array( 'name' => 'Kids Capsule', 'image' => 'images/lookbook/lb-kid-black-rose' ),
		);
		?>
		<div class="sr2-about-chapters__frames">
			<?php foreach ( $sr2_about_lookbook as $sr2_frame ) : ?>
				<figure class="sr2-about-chapters__frame sr2-image-reveal">
					<picture>
						<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_frame['image'] . '-480w.webp' ) ); ?>">
						<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $sr2_frame['image'] . '-960w.webp' ) ); ?>" alt="<?php echo esc_attr( $sr2_frame['name'] ); ?> lookbook image" width="960" height="1200" loading="lazy" decoding="async">
					</picture>
				</figure>
			<?php endforeach; ?>
		</div>
	</div>
</section>

<section class="sr2-band sr2-about-oakland" aria-labelledby="sr2-oakland-title">
	<div class="sr2-band__head">
		<div>
			<p class="sr2-eyebrow">The Town</p>
			<h2 id="sr2-oakland-title" class="sr2-title-chapter">Deep East · The Hills · Stone City · Lake Merritt · The 510</h2>
			<p class="sr2-lede">SkyyRose is gender-neutral by design and Oakland in its posture. The house was built for the person wearing the piece—not for a category somebody else assigned.</p>
		</div>
		<a class="sr2-control sr2-control--primary" href="<?php echo esc_url( home_url( '/collections/' ) ); ?>">Enter the collections</a>
	</div>
</section>
