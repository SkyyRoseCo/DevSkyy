<?php
/**
 * Template Name: FAQ
 *
 * Frequently Asked Questions — dark luxury accordion.
 * Uses <details>/<summary> for native accessibility + progressive enhancement.
 *
 * @package SkyyRose
 * @since   6.4.0
 */

defined( 'ABSPATH' ) || exit;

$faq_categories = array(
	array(
		'title' => __( 'Orders & Shipping', 'skyyrose' ),
		'icon'  => '&#x2726;',
		'items' => array(
			array(
				'q' => __( 'How long does shipping take?', 'skyyrose' ),
				'a' => __( 'Standard shipping within the US takes 5–7 business days. Express shipping delivers in 2–3 business days. International orders typically arrive within 10–14 business days depending on your location and customs processing.', 'skyyrose' ),
			),
			array(
				'q' => __( 'Do you ship internationally?', 'skyyrose' ),
				'a' => __( 'Yes. We ship to over 40 countries worldwide. International shipping rates are calculated at checkout based on your destination. Duties and taxes are the responsibility of the recipient.', 'skyyrose' ),
			),
			array(
				'q' => __( 'How can I track my order?', 'skyyrose' ),
				'a' => __( 'Once your order ships, you\'ll receive an email with a tracking number and link. You can also check your order status anytime by logging into your account on our website.', 'skyyrose' ),
			),
			array(
				'q' => __( 'Can I change or cancel my order?', 'skyyrose' ),
				'a' => __( 'We process orders quickly. If you need to make changes, contact us within 2 hours of placing your order at support@skyyrose.co. After that window, we cannot guarantee modifications as your order may already be in production.', 'skyyrose' ),
			),
		),
	),
	array(
		'title' => __( 'Returns & Exchanges', 'skyyrose' ),
		'icon'  => '&#x2726;',
		'items' => array(
			array(
				'q' => __( 'What is your return policy?', 'skyyrose' ),
				'a' => __( 'We accept returns within 30 days of delivery for unworn, unwashed items with original tags attached. Items must be in their original packaging. Refunds are processed within 5–7 business days after we receive and inspect the return.', 'skyyrose' ),
			),
			array(
				'q' => __( 'How do I start a return?', 'skyyrose' ),
				'a' => __( 'Email support@skyyrose.co with your order number and reason for return. We\'ll send you a prepaid return label (US orders) or return instructions (international orders) within 24 hours.', 'skyyrose' ),
			),
			array(
				'q' => __( 'Can I exchange for a different size?', 'skyyrose' ),
				'a' => __( 'Yes. Exchanges are free for US orders. Request an exchange through support@skyyrose.co and we\'ll ship your new size as soon as we receive the original item. If the size you need is available, we can ship it immediately and provide a return label for the original.', 'skyyrose' ),
			),
			array(
				'q' => __( 'Are sale items final sale?', 'skyyrose' ),
				'a' => __( 'Items marked "Final Sale" cannot be returned or exchanged. All other sale items follow our standard 30-day return policy.', 'skyyrose' ),
			),
		),
	),
	array(
		'title' => __( 'Products & Sizing', 'skyyrose' ),
		'icon'  => '&#x2726;',
		'items' => array(
			array(
				'q' => __( 'How do your pieces fit?', 'skyyrose' ),
				'a' => __( 'Most pieces run true to size with a relaxed, gender-neutral fit. Each product page includes a detailed size chart with measurements. When in doubt, check our Size Guide or reach out — we\'ll point you right.', 'skyyrose' ),
			),
			array(
				'q' => __( 'Are your products unisex?', 'skyyrose' ),
				'a' => __( 'Every SkyyRose piece is designed gender-neutral. Our sizing accounts for all body types with relaxed silhouettes that drape naturally regardless of how you identify.', 'skyyrose' ),
			),
			array(
				'q' => __( 'How should I care for my SkyyRose pieces?', 'skyyrose' ),
				'a' => __( 'Machine wash cold, inside out, on a gentle cycle. Hang dry or tumble dry low. Do not bleach. Iron on low heat if needed, avoiding printed or embroidered areas. Detailed care instructions are included on every garment label.', 'skyyrose' ),
			),
			array(
				'q' => __( 'What materials do you use?', 'skyyrose' ),
				'a' => __( 'We source heavyweight cotton (280–320 GSM), reinforced stitching, and colorfast dyes. Our materials are chosen for longevity — these are investment pieces, not fast fashion. Specific material details are listed on each product page.', 'skyyrose' ),
			),
		),
	),
	array(
		'title' => __( 'Pre-Orders & Limited Editions', 'skyyrose' ),
		'icon'  => '&#x2726;',
		'items' => array(
			array(
				'q' => __( 'How do pre-orders work?', 'skyyrose' ),
				'a' => __( 'Pre-orders secure your piece before the official drop. Your card is charged at the time of pre-order. Estimated ship dates are listed on each product page. Pre-order items ship separately from in-stock items.', 'skyyrose' ),
			),
			array(
				'q' => __( 'What does "Limited Edition" mean?', 'skyyrose' ),
				'a' => __( 'Limited Edition pieces are produced in a fixed quantity — once they sell out, they\'re gone forever. The edition size is displayed on the product card. We never reprint or restock limited runs.', 'skyyrose' ),
			),
			array(
				'q' => __( 'Can I cancel a pre-order?', 'skyyrose' ),
				'a' => __( 'Pre-orders can be cancelled for a full refund up to 48 hours before the estimated ship date. After that, standard return policy applies once the item is delivered.', 'skyyrose' ),
			),
		),
	),
	array(
		'title' => __( 'About SkyyRose', 'skyyrose' ),
		'icon'  => '&#x2726;',
		'items' => array(
			array(
				'q' => __( 'Who is behind SkyyRose?', 'skyyrose' ),
				'a' => __( 'SkyyRose was founded by Corey Foster in Oakland, California. The brand is named after his daughter, Skyy Rose. What started as a father\'s promise became a luxury streetwear label built on authenticity, uncompromising craft.', 'skyyrose' ),
			),
			array(
				'q' => __( 'Where are your pieces made?', 'skyyrose' ),
				'a' => __( 'Our pieces are designed in Oakland and manufactured by vetted production partners who share our commitment to quality. Every manufacturer is personally approved and regularly audited.', 'skyyrose' ),
			),
			array(
				'q' => __( 'How can I collaborate or partner with SkyyRose?', 'skyyrose' ),
				'a' => __( 'For wholesale inquiries, press features, collaboration proposals, or influencer partnerships, email partnerships@skyyrose.co with your proposal and we\'ll review it within 5 business days.', 'skyyrose' ),
			),
		),
	),
);

get_header();
?>

<main id="primary" class="info-page info-page--faq" role="main">
	<div class="info-page__container">

		<?php
		// Hero + first category are above the fold — no reveal classes: the hidden
		// resting state stalls LCP behind the deferred JS queue (the PDP 24.9s bug
		// class). Below-fold categories keep reveals. Wave 5.
		?>
		<!-- Hero -->
		<header class="info-page__hero">
			<span class="info-page__badge"><?php esc_html_e( 'Support', 'skyyrose' ); ?></span>
			<h1 class="info-page__title"><?php esc_html_e( 'Frequently Asked Questions', 'skyyrose' ); ?></h1>
			<p class="info-page__subtitle"><?php esc_html_e( 'Everything you need to know about shopping with SkyyRose.', 'skyyrose' ); ?></p>
		</header>

		<!-- FAQ Categories -->
		<div class="faq-categories">
			<?php foreach ( $faq_categories as $cat_idx => $category ) : ?>
				<section class="faq-category<?php echo 0 === $cat_idx ? '' : ' rv-clip-up'; ?>" aria-labelledby="faq-cat-<?php echo esc_attr( (string) $cat_idx ); ?>">
					<h2 class="faq-category__title" id="faq-cat-<?php echo esc_attr( (string) $cat_idx ); ?>">
						<span class="faq-category__icon" aria-hidden="true"><?php echo wp_kses( $category['icon'], array() ); ?></span>
						<?php echo esc_html( $category['title'] ); ?>
					</h2>

					<div class="faq-category__items">
						<?php foreach ( $category['items'] as $item_idx => $item ) : ?>
							<details class="faq-item" <?php echo ( 0 === $cat_idx && 0 === $item_idx ) ? 'open' : ''; ?>>
								<summary class="faq-item__question">
									<span class="faq-item__q-text"><?php echo esc_html( $item['q'] ); ?></span>
									<span class="faq-item__toggle" aria-hidden="true">
										<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
									</span>
								</summary>
								<div class="faq-item__answer">
									<p><?php echo esc_html( $item['a'] ); ?></p>
								</div>
							</details>
						<?php endforeach; ?>
					</div>
				</section>
			<?php endforeach; ?>
		</div>

		<!-- Contact CTA -->
		<section class="info-page__cta rv-blur">
			<h2><?php esc_html_e( 'Still have questions?', 'skyyrose' ); ?></h2>
			<p><?php esc_html_e( 'Questions live here. For everything else — reach out.', 'skyyrose' ); ?></p>
			<a href="<?php echo esc_url( home_url( '/contact/' ) ); ?>" class="info-page__cta-btn btn-sweep btn-press"><?php esc_html_e( 'Reach Out', 'skyyrose' ); ?></a>
		</section>

	</div>
</main>

<?php
// FAQPage Schema (JSON-LD) — enables rich snippets in Google search results.
if ( ! defined( 'WPSEO_VERSION' ) ) {
	$faq_schema = array(
		'@context'   => 'https://schema.org',
		'@type'      => 'FAQPage',
		'mainEntity' => array(),
	);

	foreach ( $faq_categories as $category ) {
		foreach ( $category['items'] as $item ) {
			$faq_schema['mainEntity'][] = array(
				'@type'          => 'Question',
				'name'           => $item['q'],
				'acceptedAnswer' => array(
					'@type' => 'Answer',
					'text'  => $item['a'],
				),
			);
		}
	}

	echo '<script type="application/ld+json">' . wp_json_encode( $faq_schema, JSON_HEX_TAG | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
}
?>

<?php get_footer(); ?>
