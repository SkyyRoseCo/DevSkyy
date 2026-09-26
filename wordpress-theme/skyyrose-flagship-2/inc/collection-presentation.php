<?php
/**
 * Collection presentation: ordinal, crop focal points and lockup geometry for the
 * existing founder assets. Never product facts, prices, availability or new media.
 * title_in_scene: from 48em the approved monument already spells the collection name,
 * so the arrival hides the lockup there instead of laying it over the same lettering;
 * the mobile crop carries no lettering, so below 48em the lockup stays the visible title.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/**
 * Presentation record for one collection slug, or an empty array.
 *
 * @param string $slug Collection slug.
 * @return array<string,mixed>
 */
function skyyrose2_collection_presentation( $slug ) {
	$presentations = array(
		'signature'    => array(
			'title_in_scene' => true,
			'composition'    => 'origin',
			'ordinal'        => '01',
			'arrival_alt'    => __( 'Bronze SkyyRose signature and SR rose monuments beside the Golden Gate Bridge.', 'skyyrose-flagship-2' ),
			'focal'          => '50% 50%',
			'focal_mobile'   => '72% 50%',
			'lockup'         => array(
				'width'  => 1600,
				'height' => 540,
			),
			'next_slug'      => 'black-rose',
		),
		'black-rose'   => array(
			'title_in_scene' => true,
			'composition'    => 'nocturne',
			'ordinal'        => '02',
			'arrival_alt'    => __( 'Silver Black Rose lettering and a star-and-rose monument face the Bay Bridge beneath a full moon.', 'skyyrose-flagship-2' ),
			'focal'          => '50% 50%',
			'focal_mobile'   => '75% 50%',
			'lockup'         => array(
				'width'  => 1600,
				'height' => 796,
			),
			'next_slug'      => 'love-hurts',
		),
		'love-hurts'   => array(
			'title_in_scene' => true,
			'composition'    => 'devotion',
			'ordinal'        => '03',
			'arrival_alt'    => __( 'Crimson Love Hurts lettering and a rose-and-heart star frame a cathedral aisle, with a cloaked figure facing a rose under glass.', 'skyyrose-flagship-2' ),
			'focal'          => '50% 45%',
			'focal_mobile'   => '50% 50%',
			'lockup'         => array(
				'width'  => 1600,
				'height' => 1228,
			),
			'next_slug'      => 'kids-capsule',
		),
		'kids-capsule' => array(
			'composition'  => 'inheritance',
			'ordinal'      => '04',
			'arrival_alt'  => __( 'The Skyy mascot sits on a gold-trimmed throne beneath The Heir lettering, with Next Up at its base.', 'skyyrose-flagship-2' ),
			'focal'        => '50% 40%',
			'focal_mobile' => '50% 50%',
			'lockup'       => array(
				'width'  => 720,
				'height' => 720,
				'shape'  => 'mark',
			),
			'next_slug'    => 'signature',
		),
	);
	return $presentations[ sanitize_title( (string) $slug ) ] ?? array();
}
