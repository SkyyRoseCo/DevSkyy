<?php
/**
 * Client services: a quiet arrival, the native contact form, and the direct line.
 *
 * Field names, the nonce, the honeypot and the result tokens are read by
 * skyyrose2_contact_form_submit() / skyyrose2_contact_result() in functions.php.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$contact_email  = sanitize_email( get_option( 'admin_email' ) );
$contact_link   = 'mailto:' . $contact_email;
$contact_result = skyyrose2_contact_result();
$contact_links  = array(
	home_url( '/shipping-returns/' )  => __( 'Shipping + Returns', 'skyyrose-flagship-2' ),
	home_url( '/returns-exchanges/' ) => __( 'Returns + Exchanges', 'skyyrose-flagship-2' ),
	home_url( '/size-guide/' )        => __( 'Size Guide', 'skyyrose-flagship-2' ),
	home_url( '/faq/' )               => __( 'FAQ', 'skyyrose-flagship-2' ),
);
?>
<header class="sr2-band sr2-page-arrival" aria-labelledby="sr2-page-title">
	<div class="sr2-band__head">
		<div>
			<p class="sr2-eyebrow"><?php esc_html_e( 'Client Services', 'skyyrose-flagship-2' ); ?></p>
			<h1 id="sr2-page-title" class="sr2-title-display"><?php esc_html_e( 'Talk to the house.', 'skyyrose-flagship-2' ); ?></h1>
			<p class="sr2-lede"><?php esc_html_e( 'Orders, sizing, press, collaborations, or anything between.', 'skyyrose-flagship-2' ); ?></p>
		</div>
	</div>
</header>
<section class="sr2-band sr2-contact" aria-label="<?php esc_attr_e( 'Contact the house', 'skyyrose-flagship-2' ); ?>">
	<div class="sr2-page-grid">
		<div class="sr2-page-grid__main sr2-contact-form-wrap">
			<?php if ( 'received' === $contact_result ) : ?>
				<p class="sr2-form-notice sr2-form-notice--success" role="status"><?php esc_html_e( 'Message received. The house will reply soon.', 'skyyrose-flagship-2' ); ?></p>
			<?php elseif ( 'rate-limited' === $contact_result ) : ?>
				<p class="sr2-form-notice sr2-form-notice--error" role="alert"><?php esc_html_e( 'Please wait a moment before sending another message.', 'skyyrose-flagship-2' ); ?></p>
			<?php elseif ( $contact_result ) : ?>
				<p class="sr2-form-notice sr2-form-notice--error" role="alert"><?php esc_html_e( 'We could not send that message. Review every field or email the house directly.', 'skyyrose-flagship-2' ); ?></p>
			<?php endif; ?>
			<form class="sr2-contact-form" method="post">
				<p class="sr2-eyebrow"><?php esc_html_e( 'Send a note', 'skyyrose-flagship-2' ); ?></p>
				<?php wp_nonce_field( 'skyyrose2_contact', 'skyyrose2_contact_nonce' ); ?>
				<input type="hidden" name="skyyrose2_contact_submit" value="1">
				<label class="sr2-contact-form__trap" hidden aria-hidden="true"><?php esc_html_e( 'Website', 'skyyrose-flagship-2' ); ?><input name="contact_website" type="text" tabindex="-1" autocomplete="off"></label>
				<div class="sr2-contact-form__row">
					<div class="sr2-field"><label for="sr2-contact-name"><?php esc_html_e( 'Name', 'skyyrose-flagship-2' ); ?></label><input id="sr2-contact-name" name="contact_name" type="text" autocomplete="name" maxlength="120" required></div>
					<div class="sr2-field"><label for="sr2-contact-email"><?php esc_html_e( 'Email', 'skyyrose-flagship-2' ); ?></label><input id="sr2-contact-email" name="contact_email" type="email" autocomplete="email" maxlength="254" required></div>
				</div>
				<div class="sr2-field"><label for="sr2-contact-subject"><?php esc_html_e( 'What can we help with?', 'skyyrose-flagship-2' ); ?></label><select id="sr2-contact-subject" name="contact_subject"><option><?php esc_html_e( 'Order support', 'skyyrose-flagship-2' ); ?></option><option><?php esc_html_e( 'Styling appointment', 'skyyrose-flagship-2' ); ?></option><option><?php esc_html_e( 'Press or collaboration', 'skyyrose-flagship-2' ); ?></option><option><?php esc_html_e( 'Wholesale', 'skyyrose-flagship-2' ); ?></option></select></div>
				<div class="sr2-field"><label for="sr2-contact-message"><?php esc_html_e( 'Message', 'skyyrose-flagship-2' ); ?></label><textarea id="sr2-contact-message" name="contact_message" rows="6" maxlength="5000" required></textarea></div>
				<label class="sr2-contact-form__consent"><input name="contact_privacy" type="checkbox" value="1" required><span><?php esc_html_e( 'I agree that SkyyRose may use these details to respond to this request.', 'skyyrose-flagship-2' ); ?> <a href="<?php echo esc_url( home_url( '/privacy-policy/' ) ); ?>"><?php esc_html_e( 'Privacy policy', 'skyyrose-flagship-2' ); ?></a>.</span></label>
				<button class="sr2-control sr2-control--primary" type="submit"><?php esc_html_e( 'Send to the house', 'skyyrose-flagship-2' ); ?></button>
			</form>
		</div>
		<aside class="sr2-page-grid__aside sr2-contact-direct">
			<p class="sr2-eyebrow"><?php esc_html_e( 'Direct', 'skyyrose-flagship-2' ); ?></p>
			<a class="sr2-contact-direct__email" href="<?php echo esc_url( $contact_link ); ?>"><?php echo esc_html( $contact_email ); ?></a>
			<p class="sr2-contact-direct__note"><?php esc_html_e( 'Replies typically arrive within two business days.', 'skyyrose-flagship-2' ); ?></p>
			<nav class="sr2-contact-direct__links" aria-label="<?php esc_attr_e( 'Customer service resources', 'skyyrose-flagship-2' ); ?>">
				<p class="sr2-eyebrow"><?php esc_html_e( 'Before you write', 'skyyrose-flagship-2' ); ?></p>
				<ul class="sr2-index-list">
					<?php foreach ( $contact_links as $contact_href => $contact_label ) : ?>
						<li><a href="<?php echo esc_url( $contact_href ); ?>"><span><?php echo esc_html( $contact_label ); ?></span><span aria-hidden="true">→</span></a></li>
					<?php endforeach; ?>
				</ul>
			</nav>
		</aside>
	</div>
</section>
