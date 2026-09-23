<?php
/**
 * Template Name: SkyyRose Collection 2
 *
 * Shared story-commerce template for every collection world. The composition
 * lives in template-parts/collections/world.php; narrative and scene authority
 * stay in skyyrose2_collections().
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$slug        = sanitize_title( get_post_field( 'post_name', get_queried_object_id() ) );
$collections = skyyrose2_collections();
if ( ! isset( $collections[ $slug ] ) ) {
	$slug = 'signature';
}
$collection = $collections[ $slug ];

get_header();
get_template_part( 'template-parts/collections/world', null, array(
	'slug'        => $slug,
	'collection'  => $collection,
	'collections' => $collections,
) );
get_footer();
