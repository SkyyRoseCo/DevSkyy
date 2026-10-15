<?php
/**
 * Template Name: Immersive — Kids Capsule Heir’s Room
 * Template Post Type: page
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

get_template_part(
	'template-parts/immersive/world',
	null,
	array(
		'collection_slug' => 'kids-capsule',
		'collection_name' => __( 'Kids Capsule', 'skyyrose-flagship-2' ),
		'world_name'      => __( 'The Heir’s Room', 'skyyrose-flagship-2' ),
		'world_type'      => 'heirs-room',
		'kicker'          => __( 'The next chapter sits front and center', 'skyyrose-flagship-2' ),
		'direction'       => __( 'Meet Skyy on her throne in full color, then follow imagination from the playroom to the first runway.', 'skyyrose-flagship-2' ),
		'manifesto'       => __( 'Kids Capsule is not a smaller version of the house. It is the first room built around the next generation: confidence, imagination, and enough space to picture themselves at the center.', 'skyyrose-flagship-2' ),
		'poster'          => 'images/hero/kids-capsule-heir-throne-v3.webp',
		'accent'          => '#b76e79',
		'accent_rgb'      => '183, 110, 121',
		'scene'           => array( 'cameraPath' => 'throne-orbit', 'atmosphere' => 'rose-gold-play', 'instances' => 48 ),
		'chapters'        => array(
			array(
				'id'       => 'throne',
				'label'    => __( 'The Throne Is Already Hers', 'skyyrose-flagship-2' ),
				'image'    => 'images/hero/kids-capsule-heir-throne-v3.webp',
				'alt'      => __( 'Skyy in full color seated front and center on her gold and black throne', 'skyyrose-flagship-2' ),
				'copy'     => __( 'No side outfits. No stand-ins. Skyy is the monument: full color, front and center, already imagining the house she will build next.', 'skyyrose-flagship-2' ),
				'hotspots' => array( array( 'sku' => 'kids-001', 'left' => 68, 'top' => 61 ) ),
			),
			array(
				'id'    => 'playroom',
				'label' => __( 'After-Dark Playroom', 'skyyrose-flagship-2' ),
				'image' => 'images/immersive/scene-kids-capsule-playroom.webp',
				'alt'   => __( 'A playful Kids Capsule room built for imagination after dark', 'skyyrose-flagship-2' ),
				'copy'  => __( 'Imagination is treated like an heirloom here, not an interruption. Every object can become a prop, a portal, or the first piece of a new world.', 'skyyrose-flagship-2' ),
			),
			array(
				'id'       => 'runway',
				'label'    => __( 'First Runway', 'skyyrose-flagship-2' ),
				'image'    => 'images/immersive/scene-kids-capsule-runway.webp',
				'alt'      => __( 'A first Kids Capsule runway framed in royal color', 'skyyrose-flagship-2' ),
				'copy'     => __( 'Confidence does not arrive borrowed. The first walk belongs to the child wearing it — their pace, their color, their way of taking the room.', 'skyyrose-flagship-2' ),
			),
			array(
				'id'    => 'next-up',
				'label' => __( 'Next Up', 'skyyrose-flagship-2' ),
				'image' => 'images/immersive/scene-kids-capsule-heir-runway-gpt2.webp',
				'alt'   => __( 'Skyy entering the next Kids Capsule chapter', 'skyyrose-flagship-2' ),
				'copy'  => __( 'The house does not hand down a script. It hands down the room, the tools, and the belief that the next generation can write something none of us have seen yet.', 'skyyrose-flagship-2' ),
			),
		),
		'exit_title'      => __( 'Dress the next chapter.', 'skyyrose-flagship-2' ),
		'exit_copy'       => __( 'Step into the published Kids Capsule collection where every piece is connected to current fit, size, care, and availability.', 'skyyrose-flagship-2' ),
	)
);
