<?php
/**
 * Marketplace page router.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$slug = sanitize_title( get_post_field( 'post_name', get_the_ID() ) );
	?>
	<main id="primary" tabindex="-1" class="sr2-page sr2-page--<?php echo esc_attr( $slug ); ?>">
		<?php if ( 'collections' === $slug ) : ?>
			<section class="sr2-page-hero sr2-page-hero--collections" aria-labelledby="sr2-page-title">
				<div class="sr2-page-hero__media"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'branding/hero/signature-golden-gate-yacht-1280w.webp' ) ); ?>" alt="" width="1280" height="553" fetchpriority="high"></div>
				<div class="sr2-page-hero__copy"><p class="sr2-eyebrow"><?php esc_html_e( 'The House', 'skyyrose-flagship-2' ); ?></p><h1 id="sr2-page-title"><?php esc_html_e( 'Every collection opens another world.', 'skyyrose-flagship-2' ); ?></h1><p><?php esc_html_e( 'Signature begins the story. Black Rose protects it. Love Hurts tells the truth. Kids Capsule carries it forward.', 'skyyrose-flagship-2' ); ?></p></div>
			</section>
			<?php skyyrose2_render_collection_rail(); ?>
			<section class="sr2-section sr2-section--products"><header class="sr2-section-head"><p><?php esc_html_e( 'Across the House', 'skyyrose-flagship-2' ); ?></p><h2><?php esc_html_e( 'Find your chapter.', 'skyyrose-flagship-2' ); ?></h2></header><?php skyyrose2_product_cards( 9 ); ?></section>

		<?php elseif ( 'pre-order' === $slug || 'preorder' === $slug ) : ?>
			<?php get_template_part( 'template-parts/v2-preorder' ); ?>
		<?php elseif ( 'about' === $slug ) : ?>
			<?php get_template_part( 'template-parts/v2-about' ); ?>
			<?php elseif ( 'contact' === $slug ) : ?>
				<?php
				$contact_email = sanitize_email( get_option( 'admin_email' ) );
				$contact_link  = 'mailto:' . $contact_email;
				$contact_result = skyyrose2_contact_result();
			?>
			<section class="sr2-contact-hero" aria-labelledby="sr2-page-title">
				<div class="sr2-contact-hero__media"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/immersive/scene-signature-oakland-atelier-gpt2.webp' ) ); ?>" alt="" width="1920" height="1080" fetchpriority="high"></div>
				<div class="sr2-contact-hero__copy"><p class="sr2-eyebrow"><?php esc_html_e( 'Client Services', 'skyyrose-flagship-2' ); ?></p><h1 id="sr2-page-title"><?php esc_html_e( 'Talk to the house.', 'skyyrose-flagship-2' ); ?></h1><p><?php esc_html_e( 'Orders, sizing, press, collaborations, or anything between.', 'skyyrose-flagship-2' ); ?></p></div>
			</section>
			<section class="sr2-contact-grid">
				<div><p class="sr2-eyebrow"><?php esc_html_e( 'Direct', 'skyyrose-flagship-2' ); ?></p><a class="sr2-contact-grid__email" href="<?php echo esc_url( $contact_link ); ?>"><?php echo esc_html( $contact_email ); ?></a><p><?php esc_html_e( 'Replies typically arrive within two business days.', 'skyyrose-flagship-2' ); ?></p></div>
					<div class="sr2-contact-form-wrap"><?php if ( 'received' === $contact_result ) : ?><p class="sr2-form-notice sr2-form-notice--success" role="status"><?php esc_html_e( 'Message received. The house will reply soon.', 'skyyrose-flagship-2' ); ?></p><?php elseif ( 'rate-limited' === $contact_result ) : ?><p class="sr2-form-notice sr2-form-notice--error" role="alert"><?php esc_html_e( 'Please wait a moment before sending another message.', 'skyyrose-flagship-2' ); ?></p><?php elseif ( $contact_result ) : ?><p class="sr2-form-notice sr2-form-notice--error" role="alert"><?php esc_html_e( 'We could not send that message. Review every field or email the house directly.', 'skyyrose-flagship-2' ); ?></p><?php endif; ?><form class="sr2-contact-form" method="post"><p class="sr2-eyebrow"><?php esc_html_e( 'Send a note', 'skyyrose-flagship-2' ); ?></p><?php wp_nonce_field( 'skyyrose2_contact', 'skyyrose2_contact_nonce' ); ?><input type="hidden" name="skyyrose2_contact_submit" value="1"><label hidden aria-hidden="true"><?php esc_html_e( 'Website', 'skyyrose-flagship-2' ); ?><input name="contact_website" type="text" tabindex="-1" autocomplete="off"></label><label><?php esc_html_e( 'Name', 'skyyrose-flagship-2' ); ?><input name="contact_name" type="text" autocomplete="name" maxlength="120" required></label><label><?php esc_html_e( 'Email', 'skyyrose-flagship-2' ); ?><input name="contact_email" type="email" autocomplete="email" maxlength="254" required></label><label><?php esc_html_e( 'What can we help with?', 'skyyrose-flagship-2' ); ?><select name="contact_subject"><option>Order support</option><option>Styling appointment</option><option>Press or collaboration</option><option>Wholesale</option></select></label><label><?php esc_html_e( 'Message', 'skyyrose-flagship-2' ); ?><textarea name="contact_message" rows="6" maxlength="5000" required></textarea></label><label class="sr2-contact-form__consent"><input name="contact_privacy" type="checkbox" value="1" required><span><?php esc_html_e( 'I agree that SkyyRose may use these details to respond to this request.', 'skyyrose-flagship-2' ); ?> <a href="<?php echo esc_url( home_url( '/privacy-policy/' ) ); ?>"><?php esc_html_e( 'Privacy policy', 'skyyrose-flagship-2' ); ?></a>.</span></label><button class="sr2-button sr2-button--fill" type="submit"><?php esc_html_e( 'Send to the house', 'skyyrose-flagship-2' ); ?></button></form></div>
			</section>
			<nav class="sr2-service-links" aria-label="<?php esc_attr_e( 'Customer service resources', 'skyyrose-flagship-2' ); ?>"><a href="<?php echo esc_url( home_url( '/shipping-returns/' ) ); ?>"><span><?php esc_html_e( 'Shipping + Returns', 'skyyrose-flagship-2' ); ?></span><b>↗</b></a><a href="<?php echo esc_url( home_url( '/returns-exchanges/' ) ); ?>"><span><?php esc_html_e( 'Returns + Exchanges', 'skyyrose-flagship-2' ); ?></span><b>↗</b></a><a href="<?php echo esc_url( home_url( '/size-guide/' ) ); ?>"><span><?php esc_html_e( 'Size Guide', 'skyyrose-flagship-2' ); ?></span><b>↗</b></a><a href="<?php echo esc_url( home_url( '/faq/' ) ); ?>"><span><?php esc_html_e( 'FAQ', 'skyyrose-flagship-2' ); ?></span><b>↗</b></a></nav>

		<?php elseif ( function_exists( 'is_cart' ) && ( is_cart() || is_checkout() ) ) : ?>
			<?php if ( is_cart() && function_exists( 'WC' ) && WC()->cart && WC()->cart->is_empty() ) : ?><header class="sr2-generic-head sr2-empty-bag-head"><h1><?php esc_html_e( 'Your bag', 'skyyrose-flagship-2' ); ?></h1></header><?php endif; ?>
			<?php the_content(); // Native Woo templates own their heading and commerce wrapper. ?>
		<?php else : ?>
			<?php
			$is_account = function_exists( 'is_account_page' ) && is_account_page();
			$is_service = in_array( $slug, array( 'shipping-returns', 'returns-exchanges', 'size-guide', 'faq' ), true );
			$managed_content = '';
			// Imported defaults are stored on the page; merchant edits remain authoritative.

			get_template_part(
				'template-parts/pages/service',
				null,
				array(
					'slug'            => $slug,
					'is_account'      => $is_account,
					'is_service'      => $is_service,
					'managed_content' => $managed_content,
				)
			);
			?>
		<?php endif; ?>
	</main>
	<?php
endwhile;

get_footer();
