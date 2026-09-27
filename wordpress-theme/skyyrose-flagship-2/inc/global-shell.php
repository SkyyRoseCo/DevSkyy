<?php
/** SkyyRose house shell. WordPress owns links; WooCommerce owns bag state. */
defined( 'ABSPATH' ) || exit;

/** Render maintained menu content with a working fresh-install fallback. */
function skyyrose2_shell_links( $location, $links, $class = '' ) {
	if ( has_nav_menu( $location ) ) {
		$menu = wp_nav_menu( array( 'theme_location' => $location, 'container' => false, 'menu_class' => 'sr2-shell-links ' . $class, 'depth' => 2, 'fallback_cb' => false, 'echo' => false ) );
		if ( is_string( $menu ) && '' !== $menu ) {
			foreach ( $links as $label => $url ) {
				if ( function_exists( 'skyyrose2_canonical_collection_menu_links' ) ) {
					$attributes = skyyrose2_canonical_collection_menu_links( array( 'href' => $url ) );
					$url        = $attributes['href'] ?? $url;
				}
				if ( false !== strpos( $menu, 'href="' . esc_url( $url ) . '"' ) ) {
					continue;
				}
				$current_id = get_queried_object_id();
				$is_current = $current_id && ( is_singular() || is_home() ) && (int) url_to_postid( $url ) === (int) $current_id;
				if ( function_exists( 'is_shop' ) && is_shop() && untrailingslashit( $url ) === untrailingslashit( skyyrose2_shop_url() ) ) {
					$is_current = true;
				}
				$item = '<li><a href="' . esc_url( $url ) . '"' . ( $is_current ? ' aria-current="page"' : '' ) . '>' . esc_html( $label ) . '</a></li>';
				$menu = preg_replace( '/<\/ul>\s*$/', $item . '</ul>', $menu, 1 );
			}
			echo $menu;
			return;
		}
	}
	echo '<ul class="sr2-shell-links ' . esc_attr( $class ) . '">';
	foreach ( $links as $label => $url ) {
		$current_id = get_queried_object_id();
		$is_current = $current_id && ( is_singular() || is_home() ) && (int) url_to_postid( $url ) === (int) $current_id;
		if ( function_exists( 'is_shop' ) && is_shop() && untrailingslashit( $url ) === untrailingslashit( skyyrose2_shop_url() ) ) {
			$is_current = true;
		}
		echo '<li><a href="' . esc_url( $url ) . '"' . ( $is_current ? ' aria-current="page"' : '' ) . '>' . esc_html( $label ) . '</a></li>';
	}
	echo '</ul>';
}

/** House routes stay visible and usable even without JavaScript. */
function skyyrose2_house_links() {
	return array(
		__( 'Collections', 'skyyrose-flagship-2' ) => skyyrose2_marketplace_page_url( 'collections' ),
		__( 'Shop', 'skyyrose-flagship-2' ) => skyyrose2_shop_url(),
		__( 'Lookbook', 'skyyrose-flagship-2' ) => home_url( '/lookbook/' ),
		__( 'Pre-Order', 'skyyrose-flagship-2' ) => skyyrose2_marketplace_page_url( 'pre-order' ),
		__( 'Journal', 'skyyrose-flagship-2' ) => skyyrose2_marketplace_page_url( 'journal' ),
		__( 'About', 'skyyrose-flagship-2' ) => skyyrose2_marketplace_page_url( 'about' ),
		__( 'Contact', 'skyyrose-flagship-2' ) => skyyrose2_marketplace_page_url( 'contact' ),
	);
}

/** The four permanent editorial routes shown in the quiet desktop masthead. */
function skyyrose2_masthead_links() {
	return array(
		__( 'Shop', 'skyyrose-flagship-2' )        => skyyrose2_shop_url(),
		__( 'Collections', 'skyyrose-flagship-2' ) => skyyrose2_marketplace_page_url( 'collections' ),
		__( 'Journal', 'skyyrose-flagship-2' )     => skyyrose2_marketplace_page_url( 'journal' ),
		__( 'About', 'skyyrose-flagship-2' )       => skyyrose2_marketplace_page_url( 'about' ),
	);
}

/** Render an opaque, responsive house header and indexed navigation. */
function skyyrose2_header() {
	$bag_url = function_exists( 'wc_get_cart_url' ) ? wc_get_cart_url() : home_url( '/cart/' );
	$account = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'myaccount' ) : home_url( '/my-account/' );
	?>
	<header class="sr2-header sr2-house-header" data-site-header>
		<a class="sr2-header__brand" href="<?php echo esc_url( home_url( '/' ) ); ?>" aria-label="<?php esc_attr_e( 'SkyyRose home', 'skyyrose-flagship-2' ); ?>"><span class="sr2-brand-media"><img class="sr2-header__brand-mark" src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'brand/skyyrose-logo-still-384w.webp' ) ); ?>" data-brand-video="<?php echo esc_url( skyyrose2_sot_asset_uri( 'brand/skyyrose-logo-optimized-384w.webm' ) ); ?>" data-brand-animation="<?php echo esc_url( skyyrose2_sot_asset_uri( 'brand/skyyrose-logo-animated-384w.webp' ) ); ?>" fetchpriority="low" width="384" height="216" decoding="async" alt="" aria-hidden="true"></span></a>
		<nav class="sr2-house-header__editorial" aria-label="<?php esc_attr_e( 'Editorial navigation', 'skyyrose-flagship-2' ); ?>">
			<?php skyyrose2_shell_links( 'masthead-v2', skyyrose2_masthead_links(), 'sr2-house-header__editorial-links' ); ?>
		</nav>
		<div class="sr2-house-header__end">
			<a class="sr2-house-header__direct sr2-house-header__search" href="<?php echo esc_url( home_url( '/?s=' ) ); ?>" data-search-open><span class="screen-reader-text"><?php esc_html_e( 'Search', 'skyyrose-flagship-2' ); ?></span><svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" fill="none"><circle cx="10.5" cy="10.5" r="6.5" stroke="currentColor"></circle><path d="m15.5 15.5 5 5" stroke="currentColor"></path></svg></a>
			<a class="sr2-header__bag" href="<?php echo esc_url( $bag_url ); ?>" data-bag-open><?php esc_html_e( 'Bag', 'skyyrose-flagship-2' ); ?> <span class="sr2-header__bag-count" aria-live="polite" aria-atomic="true" aria-label="<?php echo esc_attr( sprintf( __( '%d items in bag', 'skyyrose-flagship-2' ), skyyrose2_cart_count() ) ); ?>"><?php echo esc_html( skyyrose2_cart_count() ); ?></span></a>
			<button class="sr2-header__menu" type="button" aria-label="<?php esc_attr_e( 'Open site menu', 'skyyrose-flagship-2' ); ?>" aria-controls="sr2-menu" aria-expanded="false" data-sr2-menu><span aria-hidden="true"></span><span><?php esc_html_e( 'Menu', 'skyyrose-flagship-2' ); ?></span></button>
		</div>
		<nav id="sr2-menu" class="sr2-header__nav sr2-house-nav" aria-label="<?php esc_attr_e( 'Primary navigation', 'skyyrose-flagship-2' ); ?>" data-sr2-nav>
			<div class="sr2-house-nav__directory">
				<p class="sr2-index"><?php esc_html_e( 'SkyyRose / House directory', 'skyyrose-flagship-2' ); ?></p>
				<?php skyyrose2_shell_links( 'primary-v2', skyyrose2_house_links(), 'sr2-house-nav__links' ); ?>
				<?php if ( has_nav_menu( 'primary' ) ) : ?>
				<div class="sr2-house-nav__experiences"><h2 class="sr2-index"><?php esc_html_e( 'Experiences', 'skyyrose-flagship-2' ); ?></h2><?php skyyrose2_shell_links( 'primary', array(), 'sr2-house-nav__experience-links' ); ?></div>
				<?php endif; ?>
				<div class="sr2-house-nav__utility"><a href="<?php echo esc_url( home_url( '/?s=' ) ); ?>" data-search-open><?php esc_html_e( 'Search', 'skyyrose-flagship-2' ); ?></a><a href="<?php echo esc_url( $account ); ?>"><?php esc_html_e( 'Account', 'skyyrose-flagship-2' ); ?></a><a href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'wishlist' ) ); ?>"><?php esc_html_e( 'Saved pieces', 'skyyrose-flagship-2' ); ?></a><a href="<?php echo esc_url( home_url( '/lookbook/' ) ); ?>"><?php esc_html_e( 'Lookbook', 'skyyrose-flagship-2' ); ?></a><?php if ( ! ( function_exists( 'is_checkout' ) && is_checkout() ) ) : ?><a id="skyyrose-mascot-recall" class="skyyrose-mascot__recall sr2-house-nav__ask" href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'contact' ) ); ?>" aria-controls="skyy-ask-dialog" aria-haspopup="dialog" aria-expanded="false"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/mascot/skyy-canonical-v2-512w.webp' ) ); ?>" alt="" width="40" height="40" loading="lazy" decoding="async"><span><?php esc_html_e( 'Ask Skyy', 'skyyrose-flagship-2' ); ?><small><?php esc_html_e( 'Your house guide', 'skyyrose-flagship-2' ); ?></small></span></a><?php endif; ?></div>
			</div>
			<div class="sr2-house-nav__collections">
				<p class="sr2-index"><?php esc_html_e( 'Four worlds. One house.', 'skyyrose-flagship-2' ); ?></p>
				<h2 data-sr2-type-motion="mask"><?php esc_html_e( 'Choose your chapter.', 'skyyrose-flagship-2' ); ?></h2>
				<div class="sr2-house-nav__previews">
				<?php foreach ( skyyrose2_collections() as $slug => $collection ) : ?>
					<div class="sr2-house-nav__preview-entry">
						<a data-collection="<?php echo esc_attr( $slug ); ?>" href="<?php echo esc_url( skyyrose2_collection_url( $slug ) ); ?>"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $collection['hero_tablet'] ?? $collection['hero'] ) ); ?>" width="1024" height="576" loading="lazy" decoding="async" fetchpriority="low" alt=""><span><?php echo esc_html( $collection['name'] ); ?></span><span aria-hidden="true">↗</span></a>
						<button type="button" data-nav-preview-toggle aria-controls="sr2-nav-preview-stage" aria-pressed="false" aria-label="<?php echo esc_attr( sprintf( __( 'Preview %s', 'skyyrose-flagship-2' ), $collection['name'] ) ); ?>" hidden><?php esc_html_e( 'Preview', 'skyyrose-flagship-2' ); ?></button>
					</div>
				<?php endforeach; ?>
				</div>
				<p class="sr2-house-nav__origin"><?php esc_html_e( 'Oakland, California', 'skyyrose-flagship-2' ); ?><br><?php esc_html_e( 'Independent luxury fashion.', 'skyyrose-flagship-2' ); ?></p>
			</div>
		</nav>
	</header>
	<?php
}

/** A native Woo mini-cart; quantities and totals are rendered by Woo only. */
function skyyrose2_bag_shell() {
	if ( ! function_exists( 'woocommerce_mini_cart' ) || ( function_exists( 'is_checkout' ) && is_checkout() ) ) {
		return;
	}
	?>
	<dialog id="sr2-bag-dialog" class="sr2-bag-dialog" aria-labelledby="sr2-bag-title">
		<div class="sr2-dialog-head"><p class="sr2-index"><?php esc_html_e( 'SkyyRose / Your selection', 'skyyrose-flagship-2' ); ?></p><form method="dialog"><button class="sr2-icon-button" aria-label="<?php esc_attr_e( 'Close bag', 'skyyrose-flagship-2' ); ?>">×</button></form></div>
		<h2 id="sr2-bag-title"><?php esc_html_e( 'Your bag.', 'skyyrose-flagship-2' ); ?></h2>
		<p class="screen-reader-text" role="status" aria-live="polite" aria-atomic="true" data-bag-status></p>
		<div class="widget_shopping_cart_content"><?php woocommerce_mini_cart(); ?></div>
		<a class="sr2-control sr2-control--secondary sr2-bag-empty-link" href="<?php echo esc_url( skyyrose2_shop_url() ); ?>"><?php esc_html_e( 'Explore the shop', 'skyyrose-flagship-2' ); ?></a>

	</dialog>
	<?php
}

/** House directory, client-service ledger, then legal colophon. */
function skyyrose2_footer() {
	$services = array(
		__( 'FAQ', 'skyyrose-flagship-2' ) => skyyrose2_marketplace_page_url( 'faq' ),
		__( 'Shipping + Returns', 'skyyrose-flagship-2' ) => skyyrose2_marketplace_page_url( 'shipping-returns' ),
		__( 'Size Guide', 'skyyrose-flagship-2' ) => skyyrose2_marketplace_page_url( 'size-guide' ),
		__( 'Contact', 'skyyrose-flagship-2' ) => skyyrose2_marketplace_page_url( 'contact' ),
		__( 'Account', 'skyyrose-flagship-2' ) => function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'myaccount' ) : home_url( '/my-account/' ),
	);
	?>
	<footer class="sr2-footer sr2-house-footer">
		<div class="sr2-house-footer__identity"><span aria-hidden="true"></span><a class="sr2-house-footer__wordmark" href="<?php echo esc_url( home_url( '/' ) ); ?>"><span class="sr2-brand-media sr2-house-footer__animated-mark" aria-hidden="true"><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'brand/skyyrose-logo-still-384w.webp' ) ); ?>" data-brand-video="<?php echo esc_url( skyyrose2_sot_asset_uri( 'brand/skyyrose-logo-optimized-384w.webm' ) ); ?>" data-brand-animation="<?php echo esc_url( skyyrose2_sot_asset_uri( 'brand/skyyrose-logo-animated-384w.webp' ) ); ?>" data-brand-animation-mode="viewport" width="384" height="216" loading="lazy" decoding="async" alt=""></span><span><?php esc_html_e( 'SkyyRose', 'skyyrose-flagship-2' ); ?></span></a></div>
		<div class="sr2-house-footer__disclosures">
			<details><summary><?php esc_html_e( 'Explore', 'skyyrose-flagship-2' ); ?></summary><nav aria-label="<?php esc_attr_e( 'Explore SkyyRose', 'skyyrose-flagship-2' ); ?>"><?php skyyrose2_shell_links( 'footer-house', skyyrose2_house_links(), 'sr2-house-footer__routes' ); ?></nav></details>
			<details><summary><?php esc_html_e( 'Client Services', 'skyyrose-flagship-2' ); ?></summary><nav aria-label="<?php esc_attr_e( 'Client Services', 'skyyrose-flagship-2' ); ?>"><?php skyyrose2_shell_links( 'footer-services', $services ); ?></nav><?php if ( has_nav_menu( 'footer' ) ) : ?><nav class="sr2-house-footer__legacy" aria-label="<?php esc_attr_e( 'More from the house', 'skyyrose-flagship-2' ); ?>"><?php skyyrose2_shell_links( 'footer', array( __( 'Kids Capsule', 'skyyrose-flagship-2' ) => home_url( '/collections/kids-capsule/' ), __( 'Pre-Order', 'skyyrose-flagship-2' ) => home_url( '/pre-order/' ) ) ); ?></nav><?php endif; ?></details>
			<details><summary><?php esc_html_e( 'Legal', 'skyyrose-flagship-2' ); ?></summary><nav aria-label="<?php esc_attr_e( 'Legal', 'skyyrose-flagship-2' ); ?>"><?php foreach ( array( 'privacy-policy' => __( 'Privacy', 'skyyrose-flagship-2' ), 'terms-of-service' => __( 'Terms', 'skyyrose-flagship-2' ), 'accessibility' => __( 'Accessibility', 'skyyrose-flagship-2' ) ) as $slug => $label ) : ?><a href="<?php echo esc_url( skyyrose2_marketplace_page_url( $slug ) ); ?>"><?php echo esc_html( $label ); ?></a><?php endforeach; ?></nav></details>
		</div>
		<p class="sr2-house-footer__copyright">© <?php echo esc_html( gmdate( 'Y' ) ); ?> <?php esc_html_e( 'The Skyy Rose Collection LLC', 'skyyrose-flagship-2' ); ?></p>
	</footer>
	<?php
}

/** Label-only native widget button integration; URLs and checkout stay Woo-owned. */
function skyyrose2_bag_view_button() {
	echo '<a href="' . esc_url( wc_get_cart_url() ) . '" class="button wc-forward">' . esc_html__( 'View Bag', 'skyyrose-flagship-2' ) . '</a>';
}
function skyyrose2_bag_buttons_setup() {
	if ( function_exists( 'woocommerce_widget_shopping_cart_button_view_cart' ) ) {
		remove_action( 'woocommerce_widget_shopping_cart_buttons', 'woocommerce_widget_shopping_cart_button_view_cart', 10 );
		add_action( 'woocommerce_widget_shopping_cart_buttons', 'skyyrose2_bag_view_button', 10 );
	}
}
add_action( 'init', 'skyyrose2_bag_buttons_setup', 20 );

require_once __DIR__ . '/launch-readiness.php';
