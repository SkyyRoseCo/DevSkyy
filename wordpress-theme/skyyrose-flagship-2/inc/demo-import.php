<?php
/**
 * Safe, one-click marketplace demo import.
 *
 * The importer is idempotent, never deletes content, never creates products,
 * and never overwrites merchant-authored pages or navigation.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/** Installer contract version. */
const SKYYROSE2_MARKETPLACE_INSTALL_VERSION = '1.0.0';

/**
 * Create a report value with stable buckets.
 *
 * @return array<string,array<int,string>>
 */
function skyyrose2_demo_report() {
	return array(
		'created'  => array(),
		'reused'   => array(),
		'warnings' => array(),
		'failed'   => array(),
	);
}

/**
 * Validate a requested template without guessing.
 *
 * @param string $template Template filename or default.
 * @return string|WP_Error
 */
function skyyrose2_demo_template( $template ) {
	$template = sanitize_file_name( $template );
	if ( '' === $template || 'default' === $template ) {
		return 'default';
	}
	$path = get_theme_file_path( $template );
	if ( ! is_readable( $path ) ) {
		return new WP_Error( 'missing_template', sprintf( __( 'Required template is missing: %s', 'skyyrose-flagship-2' ), $template ) );
	}
	return $template;
}

/**
 * Create one page or reuse the exact existing path.
 *
 * @param string                              $slug Slug key.
 * @param array<string,mixed>                 $data Page definition.
 * @param int                                 $parent_id Parent page ID.
 * @param array<string,array<int,string>>     $report Import report.
 * @return int
 */
function skyyrose2_demo_upsert_page( $slug, $data, $parent_id, &$report ) {
	$existing = get_page_by_path( $data['path'], OBJECT, 'page' );
	if ( $existing instanceof WP_Post ) {
		$report['reused'][] = sprintf( __( 'Page: %s', 'skyyrose-flagship-2' ), $data['title'] );
		$expected_template = skyyrose2_demo_template( $data['template'] );
		$current_template  = get_page_template_slug( $existing->ID );
		if ( get_post_meta( $existing->ID, '_skyyrose2_demo_owned', true ) && ! is_wp_error( $expected_template ) && 'default' !== $expected_template && $expected_template !== $current_template && in_array( $current_template, array( '', 'default', 'template-collection.php', 'template-immersive-signature.php', 'template-immersive-black-rose.php', 'template-immersive-love-hurts.php', 'template-immersive-kids-capsule.php' ), true ) ) {
			/*
			 * Only repair an owned, known theme assignment; preserve custom templates. Repair
			 * the template so a prior V1/V2 assignment cannot keep an obsolete
			 * layout live after the V2 importer is run.
			 */
			update_post_meta( $existing->ID, '_wp_page_template', $expected_template );
			$report['reused'][] = sprintf(
				/* translators: 1: page title, 2: synchronized template filename. */
				__( 'Template synchronized: %1$s → %2$s', 'skyyrose-flagship-2' ),
				$data['title'],
				$expected_template
			);
		}
		return (int) $existing->ID;
	}
	$template = skyyrose2_demo_template( $data['template'] );
	if ( is_wp_error( $template ) ) {
		$report['failed'][] = $template->get_error_message();
		return 0;
	}
	$page_id = wp_insert_post( skyyrose2_demo_page_args( $slug, $data, $parent_id, $template ), true );
	if ( is_wp_error( $page_id ) ) {
		$report['failed'][] = sprintf( __( 'Page %1$s: %2$s', 'skyyrose-flagship-2' ), $data['title'], $page_id->get_error_message() );
		return 0;
	}
	$report['created'][] = sprintf( __( 'Page: %s', 'skyyrose-flagship-2' ), $data['title'] );
	return (int) $page_id;
}

/**
 * Build sanitized arguments for wp_insert_post().
 *
 * @param string              $slug Slug key.
 * @param array<string,mixed> $data Page definition.
 * @param int                 $parent_id Parent page ID.
 * @param string              $template Validated template.
 * @return array<string,mixed>
 */
function skyyrose2_demo_page_args( $slug, $data, $parent_id, $template ) {
	return array(
		'post_title'   => wp_strip_all_tags( $data['title'] ),
		'post_name'    => sanitize_title( ! empty( $data['slug'] ) ? $data['slug'] : $slug ),
		'post_content' => wp_kses_post( $data['content'] ),
		'post_status'  => 'publish',
		'post_type'    => 'page',
		'post_parent'  => absint( $parent_id ),
		'post_author'  => get_current_user_id(),
		'meta_input'   => array(
			'_wp_page_template'     => $template,
			'_skyyrose2_demo_owned' => SKYYROSE2_MARKETPLACE_INSTALL_VERSION,
		),
	);
}

/**
 * Provision theme pages in dependency order.
 *
 * @param array<string,array<int,string>> $report Import report.
 * @return array<string,int>
 */
function skyyrose2_demo_create_theme_pages( &$report ) {
	$definitions = skyyrose2_marketplace_pages();
	$page_ids    = array();
	foreach ( $definitions as $slug => $data ) {
		if ( ! empty( $data['parent'] ) ) {
			continue;
		}
		$page_ids[ $slug ] = skyyrose2_demo_upsert_page( $slug, $data, 0, $report );
	}
	foreach ( $definitions as $slug => $data ) {
		if ( empty( $data['parent'] ) ) {
			continue;
		}
		$parent_id         = $page_ids[ $data['parent'] ] ?? 0;
		$page_ids[ $slug ] = $parent_id ? skyyrose2_demo_upsert_page( $slug, $data, $parent_id, $report ) : 0;
		if ( ! $parent_id ) {
			$report['failed'][] = sprintf( __( 'Parent page missing for %s.', 'skyyrose-flagship-2' ), $data['title'] );
		}
	}
	return array_filter( array_map( 'absint', $page_ids ) );
}

/**
 * Create or resolve a WooCommerce page.
 *
 * @param string                          $slug Page slug.
 * @param array<string,string>            $data Page definition.
 * @param array<string,array<int,string>> $report Import report.
 * @return int
 */
function skyyrose2_demo_upsert_wc_page( $slug, $data, &$report ) {
	$option_id = $data['option'] ? absint( get_option( $data['option'] ) ) : 0;
	if ( $option_id && get_post( $option_id ) ) {
		$report['reused'][] = sprintf( __( 'WooCommerce page: %s', 'skyyrose-flagship-2' ), $data['title'] );
		return $option_id;
	}
	$page_id = skyyrose2_demo_upsert_page(
		$slug,
		array( 'path' => $slug, 'title' => $data['title'], 'template' => 'default', 'content' => $data['content'] ),
		0,
		$report
	);
	if ( $page_id && $data['option'] ) {
		update_option( $data['option'], $page_id );
	}
	return $page_id;
}

/**
 * Provision WooCommerce classic shortcode pages when WooCommerce is active.
 *
 * @param array<string,array<int,string>> $report Import report.
 * @return array<string,int>
 */
function skyyrose2_demo_create_woocommerce_pages( &$report ) {
	if ( ! class_exists( 'WooCommerce' ) ) {
		$report['warnings'][] = __( 'WooCommerce is inactive. Activate it, then run the importer again to create and assign commerce pages.', 'skyyrose-flagship-2' );
		return array();
	}
	$page_ids = array();
	foreach ( skyyrose2_marketplace_woocommerce_pages() as $slug => $data ) {
		$page_ids[ $slug ] = skyyrose2_demo_upsert_wc_page( $slug, $data, $report );
	}
	return array_filter( array_map( 'absint', $page_ids ) );
}

/**
 * Configure front-page, posts-page, and privacy-page options when unassigned.
 *
 * @param array<string,int> $page_ids Theme page IDs.
 * @return void
 */
function skyyrose2_demo_configure_reading( $page_ids ) {
	if ( empty( get_option( 'page_on_front' ) ) && ! empty( $page_ids['home'] ) ) {
		update_option( 'show_on_front', 'page' );
		update_option( 'page_on_front', absint( $page_ids['home'] ) );
	}
	if ( empty( get_option( 'page_for_posts' ) ) && ! empty( $page_ids['journal'] ) ) {
		update_option( 'page_for_posts', absint( $page_ids['journal'] ) );
	}
	if ( empty( get_option( 'wp_page_for_privacy_policy' ) ) && ! empty( $page_ids['privacy-policy'] ) ) {
		update_option( 'wp_page_for_privacy_policy', absint( $page_ids['privacy-policy'] ) );
	}
}

/**
 * Insert a page-backed menu item.
 *
 * @param int                                 $menu_id Menu term ID.
 * @param string                              $title Menu label.
 * @param int                                 $page_id Page ID.
 * @param int                                 $parent_item_id Parent menu item.
 * @param array<string,array<int,string>>     $report Import report.
 * @return int
 */
function skyyrose2_demo_insert_menu_item( $menu_id, $title, $page_id, $parent_item_id, &$report ) {
	if ( ! $page_id || ! get_post( $page_id ) ) {
		$report['warnings'][] = sprintf( __( 'Menu item skipped because its page is unavailable: %s', 'skyyrose-flagship-2' ), $title );
		return 0;
	}
	$item_id = wp_update_nav_menu_item(
		$menu_id,
		0,
		array(
			'menu-item-title'     => $title,
			'menu-item-object-id' => absint( $page_id ),
			'menu-item-object'    => 'page',
			'menu-item-type'      => 'post_type',
			'menu-item-parent-id' => absint( $parent_item_id ),
			'menu-item-status'    => 'publish',
		)
	);
	if ( is_wp_error( $item_id ) ) {
		$report['failed'][] = sprintf( __( 'Menu item %1$s: %2$s', 'skyyrose-flagship-2' ), $title, $item_id->get_error_message() );
		return 0;
	}
	return (int) $item_id;
}

/**
 * Populate an empty menu from registry definitions.
 *
 * @param int                                 $menu_id Menu term ID.
 * @param array<int,array<string,mixed>>      $items Menu definitions.
 * @param array<string,int>                   $page_ids Page IDs.
 * @param array<string,array<int,string>>     $report Import report.
 * @return void
 */
function skyyrose2_demo_populate_menu( $menu_id, $items, $page_ids, &$report ) {
	$pages = skyyrose2_marketplace_pages();
	foreach ( $items as $item ) {
		$parent_id = skyyrose2_demo_insert_menu_item( $menu_id, $item['title'], $page_ids[ $item['page'] ] ?? 0, 0, $report );
		foreach ( $item['children'] ?? array() as $child_key ) {
			$title = isset( $pages[ $child_key ] ) ? $pages[ $child_key ]['title'] : $child_key;
			skyyrose2_demo_insert_menu_item( $menu_id, $title, $page_ids[ $child_key ] ?? 0, $parent_id, $report );
		}
	}
}

/**
 * Create and assign navigation without replacing merchant-managed items.
 *
 * @param array<string,int>                   $page_ids Combined page IDs.
 * @param array<string,array<int,string>>     $report Import report.
 * @return void
 */
function skyyrose2_demo_create_menus( $page_ids, &$report ) {
	$locations = get_theme_mod( 'nav_menu_locations', array() );
	foreach ( skyyrose2_marketplace_menus() as $location => $definition ) {
		$menu = wp_get_nav_menu_object( $definition['name'] );
		$menu_id = $menu ? (int) $menu->term_id : wp_create_nav_menu( $definition['name'] );
		if ( is_wp_error( $menu_id ) ) {
			$report['failed'][] = sprintf( __( 'Menu %1$s: %2$s', 'skyyrose-flagship-2' ), $definition['name'], $menu_id->get_error_message() );
			continue;
		}
		$items = wp_get_nav_menu_items( $menu_id );
		if ( empty( $items ) ) {
			skyyrose2_demo_populate_menu( $menu_id, $definition['items'], $page_ids, $report );
			$report['created'][] = sprintf( __( 'Menu: %s', 'skyyrose-flagship-2' ), $definition['name'] );
		} else {
			$report['reused'][] = sprintf( __( 'Menu: %s', 'skyyrose-flagship-2' ), $definition['name'] );
		}
		if ( empty( $locations[ $location ] ) ) {
			$locations[ $location ] = (int) $menu_id;
		}
	}
	set_theme_mod( 'nav_menu_locations', $locations );
}

/**
 * Run the explicit demo import.
 *
 * @return array<string,array<int,string>>
 */
function skyyrose2_run_demo_import() {
	$report    = skyyrose2_demo_report();
	$page_ids  = skyyrose2_demo_create_theme_pages( $report );
	$wc_ids    = skyyrose2_demo_create_woocommerce_pages( $report );
	$all_pages = array_merge( $page_ids, $wc_ids );
	skyyrose2_demo_configure_reading( $page_ids );
	skyyrose2_demo_create_menus( $all_pages, $report );
	update_option( 'skyyrose2_demo_import_version', SKYYROSE2_MARKETPLACE_INSTALL_VERSION );
	flush_rewrite_rules( false );
	return $report;
}

/**
 * Handle the nonce- and capability-protected import request.
 *
 * @return void
 */
function skyyrose2_handle_demo_import() {
	if ( ! current_user_can( 'manage_options' ) ) {
		wp_die( esc_html__( 'You are not allowed to import theme content.', 'skyyrose-flagship-2' ), '', array( 'response' => 403 ) );
	}
	check_admin_referer( 'skyyrose2_demo_import', 'skyyrose2_demo_nonce' );
	$report = skyyrose2_run_demo_import();
	set_transient( 'skyyrose2_demo_report_' . get_current_user_id(), $report, 5 * MINUTE_IN_SECONDS );
	wp_safe_redirect( admin_url( 'themes.php?page=skyyrose2-welcome&imported=1' ) );
	exit;
}
add_action( 'admin_post_skyyrose2_demo_import', 'skyyrose2_handle_demo_import' );

/**
 * Register the Appearance onboarding page.
 *
 * @return void
 */
function skyyrose2_register_welcome_page() {
	add_theme_page(
		__( 'SkyyRose V2 Setup', 'skyyrose-flagship-2' ),
		__( 'SkyyRose V2 Setup', 'skyyrose-flagship-2' ),
		'manage_options',
		'skyyrose2-welcome',
		'skyyrose2_render_welcome_page'
	);
}
add_action( 'admin_menu', 'skyyrose2_register_welcome_page' );

/**
 * Render one report list.
 *
 * @param string            $heading List heading.
 * @param array<int,string> $items Report items.
 * @return void
 */
function skyyrose2_render_report_list( $heading, $items ) {
	if ( empty( $items ) ) {
		return;
	}
	echo '<h3>' . esc_html( $heading ) . '</h3><ul>';
	foreach ( $items as $item ) {
		echo '<li>' . esc_html( $item ) . '</li>';
	}
	echo '</ul>';
}

/**
 * Render the setup screen.
 *
 * @return void
 */
function skyyrose2_render_welcome_page() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$report = get_transient( 'skyyrose2_demo_report_' . get_current_user_id() );
	delete_transient( 'skyyrose2_demo_report_' . get_current_user_id() );
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'SkyyRose Flagship 2 — Marketplace Setup', 'skyyrose-flagship-2' ); ?></h1>
		<p><?php esc_html_e( 'Create the complete page hierarchy, collection routes, service pages, navigation, and WooCommerce classic page shells. Existing content and merchant-managed menus are never overwritten.', 'skyyrose-flagship-2' ); ?></p>
		<?php if ( is_array( $report ) ) : ?>
			<div class="notice notice-<?php echo esc_attr( empty( $report['failed'] ) ? 'success' : 'warning' ); ?> inline"><p><?php esc_html_e( 'Import finished. Review the result below, then verify every storefront route before publishing.', 'skyyrose-flagship-2' ); ?></p></div>
			<?php skyyrose2_render_report_list( __( 'Created', 'skyyrose-flagship-2' ), $report['created'] ); ?>
			<?php skyyrose2_render_report_list( __( 'Reused', 'skyyrose-flagship-2' ), $report['reused'] ); ?>
			<?php skyyrose2_render_report_list( __( 'Warnings', 'skyyrose-flagship-2' ), $report['warnings'] ); ?>
			<?php skyyrose2_render_report_list( __( 'Failed', 'skyyrose-flagship-2' ), $report['failed'] ); ?>
		<?php endif; ?>
		<form action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" method="post">
			<input type="hidden" name="action" value="skyyrose2_demo_import">
			<?php wp_nonce_field( 'skyyrose2_demo_import', 'skyyrose2_demo_nonce' ); ?>
			<?php submit_button( __( 'Import SkyyRose V2 demo structure', 'skyyrose-flagship-2' ), 'primary', 'submit', true ); ?>
		</form>
		<p><strong><?php esc_html_e( 'Important:', 'skyyrose-flagship-2' ); ?></strong> <?php esc_html_e( 'Products are never fabricated by this importer. Import or synchronize the real WooCommerce catalog through its separate authorized workflow.', 'skyyrose-flagship-2' ); ?></p>
	</div>
	<?php
}

/**
 * Offer onboarding once after theme activation without importing anything.
 *
 * @return void
 */
function skyyrose2_schedule_welcome() {
	set_transient( 'skyyrose2_activation_redirect', 1, MINUTE_IN_SECONDS );
}
add_action( 'after_switch_theme', 'skyyrose2_schedule_welcome' );

/**
 * Redirect an authorized administrator to the opt-in setup screen.
 *
 * @return void
 */
function skyyrose2_maybe_redirect_to_welcome() {
	if ( ! get_transient( 'skyyrose2_activation_redirect' ) || ! current_user_can( 'manage_options' ) ) {
		return;
	}
	delete_transient( 'skyyrose2_activation_redirect' );
	if ( wp_doing_ajax() || is_network_admin() || isset( $_GET['activate-multi'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Recommended -- read-only core activation flag.
		return;
	}
	wp_safe_redirect( admin_url( 'themes.php?page=skyyrose2-welcome' ) );
	exit;
}
add_action( 'admin_init', 'skyyrose2_maybe_redirect_to_welcome' );
