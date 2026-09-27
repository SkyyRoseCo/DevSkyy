<?php
/**
 * Collection Content Data
 *
 * Returns per-collection strings and feature cards for the unified
 * collection page layout. This is the single source of truth for all
 * collection-specific copy.
 *
 * @package SkyyRose
 * @since   6.5.0
 */

defined( 'ABSPATH' ) || exit;

/**
 * Get collection-specific content data.
 *
 * @param  string $slug Collection slug (black-rose, love-hurts, signature, kids-capsule).
 * @return array<string, mixed>|null Content array or null if slug is unknown.
 */
function skyyrose_get_collection_content( $slug ) {
	$collections = array(

		/* ── Black Rose ─────────────────────────────────────────── */
		'black-rose'   => array(
			'hero_badge'          => __( 'The Original Collection', 'skyyrose' ),
			'hero_logo'           => '/branding/black-rose-logo-hero.webp',
			'hero_logo_alt'       => __( 'The Black Rose Collection', 'skyyrose' ),
			'hero_logo_w'         => 560,
			'hero_logo_h'         => 280,
			'hero_bg'             => '/branding/hero/forbidden-midnight-1280w.webp',
			'hero_bg_base'        => '/branding/hero/forbidden-midnight',
			'hero_bg_alt'         => __( 'Black Rose Collection — rose from concrete', 'skyyrose' ),
			'hero_tagline'        => __( 'The beauty of the color black through the rose and high-end fashion design.', 'skyyrose' ),
			'hero_subtitle'       => __( 'Monochrome sophistication. Dark-on-dark texture. Elegance distilled into every fiber. You don\'t wear it to stand out. You wear it because you already stood up.', 'skyyrose' ),
			'hero_scroll_text'    => __( 'Discover', 'skyyrose' ),
			'hero_3d_label'       => __( 'View 3D Experience', 'skyyrose' ),
			'experience_url'      => '#experience',
			'marquee'             => array(
				__( 'Dark Elegance', 'skyyrose' ),
				__( 'Quiet Authority', 'skyyrose' ),
			),
			'marquee_icon'        => '&#x25C6;',
			'story_label'         => __( 'From the Concrete', 'skyyrose' ),
			'story_title'         => __( 'Born from a Single Question', 'skyyrose' ),
			'story_text_1'        => __( 'Someone asked who Black Rose was for. The answer came before the question finished: a black rose is a posture. Not a flower — a conviction. In Oakland, where concrete is the only soil that matters, beauty doesn\'t ask for permission. It forces its way through the cracks.', 'skyyrose' ),
			'story_quote'         => __( '"They said luxury can\'t come from the Town. We said watch. Every piece in Black Rose is the concrete answering back."', 'skyyrose' ),
			'story_text_2'        => __( 'Black Rose is what happens when you stop apologizing for where you\'re from. Monochrome because silence speaks louder. Dark-on-dark because depth is earned, not given. These aren\'t clothes that announce themselves — they command presence the way Oakland taught us. Quiet. Unshakable.', 'skyyrose' ),
			'story_visual_text'   => __( 'BLACK ROSE', 'skyyrose' ),
			'story_visual_label'  => __( 'Dark Elegance', 'skyyrose' ),
			'divider_icon'        => '&#x25C6;',
			'quote_text'          => __( '"Where I\'m from, black isn\'t a color — it\'s armor. Every kid on my block knew that. Black Rose is that truth made into fabric. You don\'t wear it to stand out. You wear it because you already stood up."', 'skyyrose' ),
			'quote_cite'          => __( 'Corey Foster, Oakland', 'skyyrose' ),
			'features_heading'    => __( 'The Philosophy', 'skyyrose' ),
			'features_subheading' => __( 'Every stitch, every detail is designed to empower you to move through the world on your own terms.', 'skyyrose' ),
			'features'            => array(
				array(
					'icon'      => '&#x1F5A4;',
					'title'     => __( 'Monochrome Mastery', 'skyyrose' ),
					'text'      => __( 'The depth of black carries what other colors cannot — layered textures, tonal contrasts, silhouettes that command presence without raising their voice.', 'skyyrose' ),
					'image'     => '/images/lookbook/lb-black-rose-hockey-960w.webp',
					'image_alt' => __( 'Black Rose hockey jersey — layered black-on-black texture', 'skyyrose' ),
					'image_w'   => 960,
					'image_h'   => 1280,
				),
				array(
					'icon'      => '&#x1F339;',
					'title'     => __( 'The Thorn Motif', 'skyyrose' ),
					'text'      => __( 'Resilience encoded in every stitch. The thorn represents protective beauty — guarding what is precious while standing its ground.', 'skyyrose' ),
					'image'     => '/images/immersive/scene-black-rose-courtyard.webp',
					'image_alt' => __( 'Moonlit courtyard rose garden — the Black Rose world', 'skyyrose' ),
					'image_w'   => 1400,
					'image_h'   => 600,
				),
				array(
					'icon'      => '&#x25C6;',
					'title'     => __( 'Dark-on-Dark Texture', 'skyyrose' ),
					'text'      => __( 'This is not loud fashion. This is the quiet authority of someone who knows exactly who they are. Elegance distilled into every fiber.', 'skyyrose' ),
					'image'     => '/images/immersive/scene-black-rose-gazebo.webp',
					'image_alt' => __( 'Night gazebo scene — dark-on-dark depth', 'skyyrose' ),
					'image_w'   => 1344,
					'image_h'   => 896,
				),
			),
			'products_subheading' => __( 'Dark elegance — holographic preview', 'skyyrose' ),
			'cta_title'           => __( 'Wear the Darkness', 'skyyrose' ),
			'cta_text'            => __( 'The thorn protects what the world tries to take. Every piece in Black Rose carries that Oakland lesson: be beautiful, be sharp, never be soft where it counts.', 'skyyrose' ),
			'cta_btn'             => __( 'Shop Black Rose', 'skyyrose' ),
			'newsletter_text'     => __( 'First access to new drops, behind-the-scenes stories, and the darkness behind each piece.', 'skyyrose' ),
			'email_id'            => 'br-email',
			'pin_beats'           => array(
				array(
					'label'  => __( '01 — THE POSTURE', 'skyyrose' ),
					'lead'   => __( 'Not a flower —', 'skyyrose' ),
					'accent' => __( 'a conviction.', 'skyyrose' ),
					'sub'    => __( 'Black Rose / Oakland', 'skyyrose' ),
				),
				array(
					'label'  => __( '02 — THE ANSWER', 'skyyrose' ),
					'lead'   => __( 'Every piece in Black Rose is', 'skyyrose' ),
					'accent' => __( 'the concrete answering back.', 'skyyrose' ),
					'sub'    => __( 'Black Rose / The Town', 'skyyrose' ),
				),
				array(
					'label'  => __( '03 — THE STAND', 'skyyrose' ),
					'lead'   => __( 'You wear it because', 'skyyrose' ),
					'accent' => __( 'you already stood up.', 'skyyrose' ),
					'sub'    => __( 'Black Rose / Collection I', 'skyyrose' ),
				),
			),
		),

		/* ── Love Hurts ─────────────────────────────────────────── */
		'love-hurts'   => array(
			'hero_badge'          => __( 'The Hurts Bloodline', 'skyyrose' ),
			'hero_logo'           => '/branding/love-hurts-logo-hero.webp',
			'hero_logo_alt'       => __( 'Love Hurts', 'skyyrose' ),
			'hero_logo_w'         => 400,
			'hero_logo_h'         => 307, // 1600x1228 SOT lockup (1.30:1) — was 400 (1:1), CLS drift.
			'hero_bg'             => '/branding/hero/beauty-and-beast-1280w.webp',
			'hero_bg_base'        => '/branding/hero/beauty-and-beast',
			'hero_bg_alt'         => __( 'Love Hurts Collection — enchanted rose under glass', 'skyyrose' ),
			'hero_tagline'        => __( 'They called me Beast. They were right.', 'skyyrose' ),
			'hero_subtitle'       => __( 'But even the Beast kept a rose under glass — protecting the most fragile thing he ever loved. This collection carries the weight of three generations of Hurts.', 'skyyrose' ),
			'hero_scroll_text'    => __( 'Explore', 'skyyrose' ),
			'hero_3d_label'       => __( 'Enter the 3D Experience', 'skyyrose' ),
			'experience_url'      => '#experience',
			'marquee'             => array(
				__( 'The Hurts Bloodline', 'skyyrose' ),
				__( 'Love Is Worth the Pain', 'skyyrose' ),
			),
			'marquee_icon'        => '&#x2665;',
			'story_label'         => __( 'The Bloodline', 'skyyrose' ),
			'story_title'         => __( 'The Hurts Bloodline', 'skyyrose' ),
			'story_text_1'        => __( 'My grandmother used to say it plain: "Love hurts, baby. That\'s how you know it\'s real." She wasn\'t being poetic. She was teaching survival. Three generations of Hurts women and men poured everything into the people they loved — and the world poured pain right back. But they never stopped loving. Not once.', 'skyyrose' ),
			'story_quote'         => __( '"The Beast didn\'t hide because he was ugly. He hid because he loved something so beautiful it terrified him. The rose under glass — that\'s every Hurts who ever kept loving when love didn\'t love them back."', 'skyyrose' ),
			'story_text_2'        => __( "This collection carries grandmother's name. Not as a brand, but as a bloodline truth. Every stitch holds the weight of family dinners where we laughed through grief, of front porches where grandmama told stories while pressing creases into Sunday shirts.", 'skyyrose' ),
			'story_visual_text'   => __( 'LOVE HURTS', 'skyyrose' ),
			'story_visual_label'  => __( 'The Hurts Bloodline', 'skyyrose' ),
			'divider_icon'        => '&#x1F339;',
			'quote_text'          => __( '"Every petal that falls is a lesson. Every thorn is a boundary. The enchanted rose doesn\'t die — it transforms. Just like us."', 'skyyrose' ),
			'quote_cite'          => __( 'From Grit to Grace', 'skyyrose' ),
			'features_heading'    => __( 'The Emotional Architecture', 'skyyrose' ),
			'features_subheading' => __( 'Crimson for the blood we share. Deep purple for the bruises that became wisdom. Burgundy for the wine grandmama poured when she said, "Baby, you survived another one."', 'skyyrose' ),
			'features'            => array(
				array(
					'icon'      => '&#x1F5A4;',
					'title'     => __( "Beast's Vulnerability", 'skyyrose' ),
					'text'      => __( "Strength isn't the roar. It's the silence after — when you choose to stay open instead of closing off. These pieces honor the courage it takes to be soft in a world that rewards hardness.", 'skyyrose' ),
					'image'     => '/branding/hero/beauty-and-beast-1280w.webp',
					'image_alt' => __( 'The Beast and the rose — Love Hurts hero artwork', 'skyyrose' ),
					'image_w'   => 1280,
					'image_h'   => 549,
				),
				array(
					'icon'      => '&#x1F339;',
					'title'     => __( 'The Enchanted Rose', 'skyyrose' ),
					'text'      => __( 'Protected under glass, glowing in a dark room, losing petals one by one. The rose is every love worth fighting for — fragile and fierce at the same time.', 'skyyrose' ),
					'image'     => '/images/immersive/scene-love-hurts-cathedral.webp',
					'image_alt' => __( 'Cathedral rose chamber — the enchanted rose under glass', 'skyyrose' ),
					'image_w'   => 1344,
					'image_h'   => 896,
				),
				array(
					'icon'      => '&#x1F4AB;',
					'title'     => __( 'The Transformation', 'skyyrose' ),
					'text'      => __( "From concrete to runway. From grief to grace. The Hurts bloodline doesn't break — it metamorphoses. The Beast becoming the prince he always was.", 'skyyrose' ),
					'image'     => '/images/lookbook/lb-love-hurts-varsity-960w.webp',
					'image_alt' => __( 'Love Hurts varsity jacket — crimson on black', 'skyyrose' ),
					'image_w'   => 960,
					'image_h'   => 1280,
				),
			),
			'products_subheading' => __( 'Pieces forged in the Hurts bloodline', 'skyyrose' ),
			'cta_title'           => __( 'Wear the Bloodline', 'skyyrose' ),
			'cta_text'            => __( "Every piece carries grandmother's truth: love is worth the pain. The Beast kept the rose under glass not out of fear, but out of reverence. This collection is that reverence, made wearable.", 'skyyrose' ),
			'cta_btn'             => __( 'Shop Love Hurts', 'skyyrose' ),
			'newsletter_text'     => __( 'First access to new drops and the stories behind every petal.', 'skyyrose' ),
			'email_id'            => 'lh-email',
			'pin_beats'           => array(
				array(
					'label'  => __( '01 — THE BEAST', 'skyyrose' ),
					'lead'   => __( 'They called me Beast.', 'skyyrose' ),
					'accent' => __( 'They were right.', 'skyyrose' ),
					'sub'    => __( 'Love Hurts / Collection II', 'skyyrose' ),
				),
				array(
					'label'  => __( '02 — THE GLASS', 'skyyrose' ),
					'lead'   => __( 'even the Beast kept a rose under glass —', 'skyyrose' ),
					'accent' => __( 'protecting the most fragile thing he ever loved.', 'skyyrose' ),
					'sub'    => __( 'Love Hurts / The Rose', 'skyyrose' ),
				),
				array(
					'label'  => __( '03 — THE TURN', 'skyyrose' ),
					'lead'   => __( 'From concrete to runway.', 'skyyrose' ),
					'accent' => __( 'From grief to grace.', 'skyyrose' ),
					'sub'    => __( 'Love Hurts / The Bloodline', 'skyyrose' ),
				),
			),
		),

		/* ── Signature ──────────────────────────────────────────── */
		'signature'    => array(
			'hero_badge'          => __( 'Where It All Began', 'skyyrose' ),
			'hero_logo'           => '/branding/signature-logo-hero.webp',
			'hero_logo_alt'       => __( 'The SkyyRose Signature Collection', 'skyyrose' ),
			'hero_logo_w'         => 560,
			'hero_logo_h'         => 189, // 1600x540 SOT lockup (2.96:1) — was 280 (2:1), CLS drift.
			'hero_bg'             => '/branding/hero/signature-golden-gate-yacht-1280w.webp',
			'hero_bg_base'        => '/branding/hero/signature-golden-gate-yacht',
			'hero_bg_alt'         => __( 'Signature Collection — SkyyRose yacht at the pier, Golden Gate Bridge at night', 'skyyrose' ),
			'hero_tagline'        => __( 'The origin. The main event. The birth of it all.', 'skyyrose' ),
			'hero_subtitle'       => __( 'This is what they know us for. The first rose ever pressed. The signature script logo worn around the world. Every collection since has grown from this foundation.', 'skyyrose' ),
			'hero_scroll_text'    => __( 'Discover', 'skyyrose' ),
			'hero_3d_label'       => __( 'View 3D Experience', 'skyyrose' ),
			'experience_url'      => '#experience',
			'marquee'             => array(
				__( 'The Foundation', 'skyyrose' ),
				__( 'Est. Oakland', 'skyyrose' ),
			),
			'marquee_icon'        => '&#x2726;',
			'story_label'         => __( 'Chapter One', 'skyyrose' ),
			'story_title'         => __( 'The First Rose', 'skyyrose' ),
			'story_text_1'        => __( 'I drew the first rose on a night I couldn\'t afford dinner. Broke, a baby on the way, every manufacturer I\'d worked with had scammed me. But I sat there sketching that script logo until 4 AM because something in me knew — if I could get this right, everything changes. Signature is that night made permanent.', 'skyyrose' ),
			'story_quote'         => __( '"They told me luxury doesn\'t come from Oakland. I said  — and I meant that literally. This collection is the concrete. Everything else grew from here."', 'skyyrose' ),
			'story_text_2'        => __( 'Before Black Rose. Before Love Hurts. Before the press wrote us up or anybody knew the name. There was just a father in Oakland with a daughter\'s name and a refusal to quit. Every piece in Signature carries that original DNA — the gold rose, the hand-drawn script, the silhouettes I sketched when I had nothing but the idea.', 'skyyrose' ),
			'story_visual_text'   => __( 'SIGNATURE', 'skyyrose' ),
			'story_visual_label'  => __( 'Est. Oakland, CA', 'skyyrose' ),
			'divider_icon'        => '&#x2726;',
			'quote_text'          => __( '"Four years ago I never would have thought I\'d be here. I had no drive, lost it all, a baby on the way, and was broke. But we knew we had to get it by any means necessary. Signature is the proof that your circumstances don\'t define your destination."', 'skyyrose' ),
			'quote_cite'          => __( 'Corey Foster, Oakland', 'skyyrose' ),
			'features_heading'    => __( 'Built from Nothing', 'skyyrose' ),
			'features_subheading' => __( 'Every Signature piece carries the same stubbornness that built the brand — failed websites, scammer manufacturers, single parenthood with zero support. We refused to cut corners then. We refuse now.', 'skyyrose' ),
			'features'            => array(
				array(
					'icon'      => '&#x2726;',
					'title'     => __( 'Sourced Without Compromise', 'skyyrose' ),
					'text'      => __( 'Italian leathers, Japanese denim, Egyptian cotton — sourced from the finest mills worldwide.', 'skyyrose' ),
					'image'     => '/images/lookbook/lb-rose-hoodie-beanie-960w.webp',
					'image_alt' => __( 'Signature rose hoodie and beanie — gold-accented essentials', 'skyyrose' ),
					'image_w'   => 960,
					'image_h'   => 1280,
				),
				array(
					'icon'      => '&#x2726;',
					'title'     => __( 'Expert Construction', 'skyyrose' ),
					'text'      => __( 'Hand-finished details by master tailors who share our obsession with perfection.', 'skyyrose' ),
					'image'     => '/images/immersive/scene-signature-bay-bridge.webp',
					'image_alt' => __( 'Bay Bridge at dusk — the Signature world', 'skyyrose' ),
					'image_w'   => 1400,
					'image_h'   => 600,
				),
				array(
					'icon'      => '&#x2726;',
					'title'     => __( 'Timeless Design', 'skyyrose' ),
					'text'      => __( 'Classic silhouettes that never date. Investment pieces, not trend pieces.', 'skyyrose' ),
					'image'     => '/images/immersive/scene-signature-golden-gate.webp',
					'image_alt' => __( 'Golden showroom scene — timeless Signature staging', 'skyyrose' ),
					'image_w'   => 1400,
					'image_h'   => 600,
				),
			),
			'products_subheading' => __( 'The original blueprint. Every piece carries the DNA of day one.', 'skyyrose' ),
			'cta_title'           => __( 'Wear the Foundation', 'skyyrose' ),
			'cta_text'            => __( 'This is where it all started. A father in Oakland with a daughter\'s name and a dream that wouldn\'t die. When you wear Signature, you wear the origin story — and you help write the next chapter.', 'skyyrose' ),
			'cta_btn'             => __( 'Shop Signature', 'skyyrose' ),
			'newsletter_text'     => __( 'Early access to new drops, behind-the-scenes stories, and first dibs on each piece.', 'skyyrose' ),
			'email_id'            => 'sig-email',
			'pin_beats'           => array(
				array(
					'label'  => __( '01 — THE ORIGIN', 'skyyrose' ),
					'lead'   => __( 'The origin. The main event.', 'skyyrose' ),
					'accent' => __( 'The birth of it all.', 'skyyrose' ),
					'sub'    => __( 'Signature / Collection I', 'skyyrose' ),
				),
				array(
					'label'  => __( '02 — PERMANENT', 'skyyrose' ),
					'lead'   => __( 'Signature is that night', 'skyyrose' ),
					'accent' => __( 'made permanent.', 'skyyrose' ),
					'sub'    => __( 'Signature / Oakland', 'skyyrose' ),
				),
				array(
					'label'  => __( '03 — THE CONCRETE', 'skyyrose' ),
					'lead'   => __( ' —', 'skyyrose' ),
					'accent' => __( 'and I meant that literally.', 'skyyrose' ),
					'sub'    => __( 'Signature / The Founder', 'skyyrose' ),
				),
			),
		),

		/* ── Kids Capsule ───────────────────────────────────────── */
		'kids-capsule' => array(
			'hero_badge'          => __( 'New Collection', 'skyyrose' ),
			// Interim hero mark: SR monogram (branding tier, 2048×2048 square) until the
			// founder creates a custom Kids Capsule lockup. asset-hierarchy.md canon:
			// assets/branding/ is "USE THIS for theme chrome + page templates"; logos/
			// is "Not for page chrome." AVIF variant exists only in logos/; <picture>
			// format-switching deferred to a future template enhancement.
			'hero_logo'           => '/branding/skyyrose-monogram.webp',
			'hero_logo_alt'       => __( 'SkyyRose Kids Capsule', 'skyyrose' ),
			'hero_logo_w'         => 400,
			'hero_logo_h'         => 400,
			'hero_tagline'        => __( 'Luxury runs in the family.', 'skyyrose' ),
			'hero_subtitle'       => __( 'Premium streetwear for the next generation — powerful, elevated, and born into legacy. Because legacy is not inherited. It is worn.', 'skyyrose' ),
			'hero_scroll_text'    => __( 'Explore', 'skyyrose' ),
			'marquee'             => array(
				__( 'Born Into Luxury', 'skyyrose' ),
				__( 'Next Generation', 'skyyrose' ),
			),
			'marquee_icon'        => '&#x2726;',
			'story_label'         => __( 'Her Name', 'skyyrose' ),
			'story_title'         => __( 'Named After My Daughter', 'skyyrose' ),
			'story_text_1'        => __( 'The whole brand is named after her — Skyy Rose. My daughter. She was on the way when I had nothing. No drive, no money, no support. But that baby coming changed everything. I needed to build something she\'d be proud to carry. Kids Capsule is the promise made real — pieces I designed thinking about my daughter walking into a room and knowing she belongs there.', 'skyyrose' ),
			'story_quote'         => __( '"No pastels. No cartoons. Skyy Rose doesn\'t wear that. She wears what her father built — premium, dark, elegant. Scaled down but never dumbed down."', 'skyyrose' ),
			'story_text_2'        => __( 'Every kid deserves to feel like they belong at the table. Not the kids\' table — THE table. Kids Capsule is that seat.', 'skyyrose' ),
			'story_visual_text'   => __( 'KC', 'skyyrose' ),
			'story_visual_label'  => __( 'Kids Capsule', 'skyyrose' ),
			'divider_icon'        => '&#x2726;',
			'quote_text'          => __( '"I built SkyyRose so my daughter would never have to wonder if she was enough. Every piece in Kids Capsule carries that — a father\'s promise that she can be anything, wear anything, own any room she walks into."', 'skyyrose' ),
			'quote_cite'          => __( 'Corey Foster, Father & Founder', 'skyyrose' ),
			'features_heading'    => __( 'Built Different', 'skyyrose' ),
			'features_subheading' => __( 'The same philosophy that built SkyyRose — uncompromising quality, dark luxury DNA, built different.', 'skyyrose' ),
			'features'            => array(
				array(
					'icon'      => '&#x2726;',
					'title'     => __( 'Uncompromising Fabrics', 'skyyrose' ),
					'text'      => __( 'Same uncompromising fabrics as the adult lines — heavyweight cotton, reinforced stitching, luxury hand-feel.', 'skyyrose' ),
					'image'     => '/images/lookbook/lb-kid-black-rose-960w.webp',
					'image_alt' => __( 'Kids Capsule Black Rose hoodie — premium heavyweight cotton', 'skyyrose' ),
					'image_w'   => 960,
					'image_h'   => 1280,
				),
				array(
					'icon'      => '&#x2726;',
					'title'     => __( 'Built to Last', 'skyyrose' ),
					'text'      => __( 'Engineered for the energy of youth. Double-stitched seams, pre-shrunk fits, colorfast dyes that survive everything.', 'skyyrose' ),
					'image'     => '/images/immersive/scene-kids-capsule-playroom.webp',
					'image_alt' => __( 'Kids Capsule playroom scene', 'skyyrose' ),
					'image_w'   => 1344,
					'image_h'   => 896,
				),
				array(
					'icon'      => '&#x2726;',
					'title'     => __( 'Dark Luxury DNA', 'skyyrose' ),
					'text'      => __( 'No pastels. No cartoons. Real streetwear scaled down, not dumbed down. The same aesthetic the brand was built on.', 'skyyrose' ),
					'image'     => '/images/immersive/scene-kids-capsule-runway.webp',
					'image_alt' => __( 'Kids Capsule runway scene', 'skyyrose' ),
					'image_w'   => 1344,
					'image_h'   => 896,
				),
			),
			'cta_title'           => __( 'Their Turn Now', 'skyyrose' ),
			'cta_text'            => __( 'We built this for Skyy Rose. For every kid who deserves to feel the same luxury their parents wear. Legacy isn\'t inherited — it\'s earned. But we can give them a head start.', 'skyyrose' ),
			'cta_btn'             => __( 'Shop Kids Capsule', 'skyyrose' ),
			'newsletter_text'     => __( 'Be first to know about new Kids Capsule drops and family previews.', 'skyyrose' ),
			'email_id'            => 'kc-email',
			'pin_beats'           => array(
				array(
					'label'  => __( '01 — THE LEGACY', 'skyyrose' ),
					'lead'   => __( 'legacy is not inherited.', 'skyyrose' ),
					'accent' => __( 'It is worn.', 'skyyrose' ),
					'sub'    => __( 'Kids Capsule / Family', 'skyyrose' ),
				),
				array(
					'label'  => __( '02 — NO PASTELS', 'skyyrose' ),
					'lead'   => __( 'No pastels.', 'skyyrose' ),
					'accent' => __( 'No cartoons.', 'skyyrose' ),
					'sub'    => __( 'Kids Capsule / Skyy Rose', 'skyyrose' ),
				),
			),
		),
	);

	if ( ! isset( $collections[ $slug ] ) ) {
		return null;
	}

	$data = $collections[ $slug ];

	/*
	 * SOT override (S-5): resolve hero_bg and hero_logo from sot.json FIRST.
	 *
	 * skyyrose_sot_hero()   → imagery.hero_backdrop.resolved  → overrides hero_bg
	 * skyyrose_sot_lockup() → lockup.display_webp.resolved    → overrides hero_logo
	 *
	 * The SOT reader may not be loaded yet in very early bootstrap (e.g. during
	 * unit tests). Guard with function_exists() so this file remains safe to
	 * include independently.
	 *
	 * Returns '' when the key/file is absent → fall through to the hand-maintained
	 * value already in $data, preserving backward compatibility exactly.
	 */
	if ( function_exists( 'skyyrose_sot_hero' ) ) {
		$sot_hero = skyyrose_sot_hero( $slug );
		if ( '' !== $sot_hero ) {
			$data['hero_bg'] = $sot_hero;
		}
	}

	if ( function_exists( 'skyyrose_sot_lockup' ) ) {
		$sot_lockup = skyyrose_sot_lockup( $slug );
		if ( '' !== $sot_lockup ) {
			$data['hero_logo'] = $sot_lockup;
		}
	}

	return $data;
}
