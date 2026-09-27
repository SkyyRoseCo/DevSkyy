<?php
/**
 * Generic, account, and client-service page shell.
 *
 * @package SkyyRoseFlagship2
 *
 * @var array $args {
 *     Template inputs prepared by page.php.
 *
 *     @type string $slug            Current page slug.
 *     @type bool   $is_account      Whether the current request is Woo account.
 *     @type bool   $is_service      Whether the page belongs to client services.
 *     @type string $managed_content Canonical FAQ content, when present.
 * }
 */

defined( 'ABSPATH' ) || exit;

$args            = isset( $args ) && is_array( $args ) ? $args : array();
$slug            = isset( $args['slug'] ) ? (string) $args['slug'] : '';
$is_account      = ! empty( $args['is_account'] );
$is_service      = ! empty( $args['is_service'] );
$managed_content = isset( $args['managed_content'] ) ? (string) $args['managed_content'] : '';
$page_class      = $is_account ? ' sr2-c-account' : ( $is_service ? ' sr2-c-service' : '' );
$route           = $is_account ? 'account' : ( $is_service ? 'service' : 'page' );
?>
<section class="sr2-generic-page<?php echo esc_attr( $page_class ); ?>" data-sr2-route="<?php echo esc_attr( $route ); ?>">
	<header class="sr2-generic-head">
		<p class="sr2-eyebrow"><?php echo esc_html( $is_account ? __( 'Client account', 'skyyrose-flagship-2' ) : get_the_title() ); ?></p>
		<h1><?php the_title(); ?></h1>
	</header>
	<div class="sr2-page-copy sr2-page-copy--generic">
		<?php
		if ( $managed_content ) {
			echo wp_kses_post( apply_filters( 'the_content', $managed_content ) );
		} else {
			the_content();
		}
		?>
	</div>
	<?php if ( $is_service ) : ?>
		<nav class="sr2-c-service__links" aria-label="<?php esc_attr_e( 'Client service links', 'skyyrose-flagship-2' ); ?>">
			<a href="<?php echo esc_url( home_url( '/shipping-returns/' ) ); ?>"><?php esc_html_e( 'Shipping + returns', 'skyyrose-flagship-2' ); ?></a>
			<a href="<?php echo esc_url( home_url( '/returns-exchanges/' ) ); ?>"><?php esc_html_e( 'Returns + exchanges', 'skyyrose-flagship-2' ); ?></a>
			<a href="<?php echo esc_url( home_url( '/size-guide/' ) ); ?>"><?php esc_html_e( 'Size guide', 'skyyrose-flagship-2' ); ?></a>
			<a href="<?php echo esc_url( home_url( '/faq/' ) ); ?>"><?php esc_html_e( 'FAQ', 'skyyrose-flagship-2' ); ?></a>
			<a href="<?php echo esc_url( home_url( '/contact/' ) ); ?>"><?php esc_html_e( 'Contact', 'skyyrose-flagship-2' ); ?></a>
		</nav>
	<?php endif; ?>
</section>
