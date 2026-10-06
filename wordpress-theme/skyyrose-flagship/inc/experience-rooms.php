<?php
/**
 * Experience Room Configurations
 *
 * Single source of truth for every collection's immersive-experience layer:
 * world name, tagline, accent, and the room/hotspot data previously inlined
 * in four standalone immersive templates. Consumed by the canonical
 * immersive templates (now 301-redirected) and the embedded experience layer
 * on each /collections/{slug}/ page (structural remediation WS3).
 *
 * Scene images are SOT-wired: skyyrose_sot_scene() resolves
 * imagery.scene_portrait.resolved from data/collections/{slug}/sot.json,
 * falling back to the hand-maintained filename when the accessor returns ''.
 *
 * @package SkyyRose
 * @since   1.8.0
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Get the experience-layer configuration for a collection.
 *
 * @since 1.8.0
 * @param  string $slug Collection slug (black-rose|love-hurts|signature|kids-capsule).
 * @return array|null {
 *     @type string $collection_name Display name.
 *     @type string $world_name      Experience world title.
 *     @type string $tagline         Experience subtitle.
 *     @type string $accent_color    Hex accent.
 *     @type array  $rooms           Room data for template-parts/immersive/scene.php.
 * } Null when the collection has no experience configured.
 */
function skyyrose_get_experience_config( $slug ) {
	$slug = sanitize_key( $slug );

	$sot_scene   = function_exists( 'skyyrose_sot_scene' ) ? skyyrose_sot_scene( $slug ) : '';
	$sot_room1   = ( '' !== $sot_scene ) ? basename( $sot_scene ) : '';
	$room1_image = static function ( $fallback ) use ( $sot_room1 ) {
		return ( '' !== $sot_room1 ) ? $sot_room1 : $fallback;
	};

	switch ( $slug ) {
		case 'black-rose':
			return array(
				'collection_name' => __( 'Black Rose Collection', 'skyyrose' ),
				'world_name'      => __( 'The Bay Bridge', 'skyyrose' ),
				'tagline'         => '',
				'accent_color'    => SKYYROSE_COLOR_SILVER,
				'rooms'           => skyyrose_experience_filter_rooms(
					array(
						array(
							'name'     => esc_html__( 'Moonlit Courtyard', 'skyyrose' ),
							'image'    => $room1_image( 'scene-black-rose-courtyard.webp' ),
							'products' => array(
								skyyrose_immersive_product(
									'br-006',
									array(
										'left'       => '15',
										'top'        => '42',
										'prop'       => 'marble-statue',
										'prop_label' => __( 'Draped over marble garden statue', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'br-005',
									array(
										'left'       => '38',
										'top'        => '50',
										'prop'       => 'fountain-edge',
										'prop_label' => __( 'Folded on fountain edge', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'br-002',
									array(
										'left'       => '62',
										'top'        => '55',
										'prop'       => 'topiary-base',
										'prop_label' => __( 'Folded at base of rose topiary', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'br-007',
									array(
										'left'       => '82',
										'top'        => '48',
										'prop'       => 'statue-pedestal',
										'prop_label' => __( 'Draped over statue pedestal', 'skyyrose' ),
									)
								),
							),
						),
						array(
							'name'     => esc_html__( 'Iron Gazebo', 'skyyrose' ),
							'image'    => 'scene-black-rose-gazebo.webp',
							'products' => array(
								skyyrose_immersive_product(
									'br-004',
									array(
										'left'       => '30',
										'top'        => '40',
										'prop'       => 'iron-gazebo',
										'prop_label' => __( 'Displayed inside iron gazebo', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'br-001',
									array(
										'left'       => '55',
										'top'        => '35',
										'prop'       => 'hedge-arch',
										'prop_label' => __( 'Hanging from rose hedge archway', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'br-003',
									array(
										'left'       => '72',
										'top'        => '50',
										'prop'       => 'cobblestone-bench',
										'prop_label' => __( 'Draped over cobblestone garden bench', 'skyyrose' ),
									)
								),
							),
						),
					)
				),
			);

		case 'love-hurts':
			return array(
				'collection_name' => __( 'Love Hurts Collection', 'skyyrose' ),
				'world_name'      => __( 'The Cathedral', 'skyyrose' ),
				'tagline'         => __( 'Every petal tells a story.', 'skyyrose' ),
				'accent_color'    => SKYYROSE_COLOR_CRIMSON,
				'rooms'           => skyyrose_experience_filter_rooms(
					array(
						array(
							'name'     => esc_html__( 'The Cathedral', 'skyyrose' ),
							'image'    => $room1_image( 'scene-love-hurts-cathedral.webp' ),
							'products' => array(
								skyyrose_immersive_product(
									'lh-004',
									array(
										'left'       => '32',
										'top'        => '50',
										'prop'       => 'mannequin',
										'prop_label' => __( 'On the mannequin stand', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'lh-003',
									array(
										'left'       => '67',
										'top'        => '35',
										'prop'       => 'float',
										'prop_label' => __( 'Suspended above the pews', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'lh-002',
									array(
										'left'       => '72',
										'top'        => '62',
										'prop'       => 'pew',
										'prop_label' => __( 'Draped across the pew', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'lh-006',
									array(
										'left'       => '83',
										'top'        => '50',
										'prop'       => 'candelabra',
										'prop_label' => __( 'Hanging from the candelabra', 'skyyrose' ),
									)
								),
							),
						),
					)
				),
			);

		case 'signature':
			return array(
				'collection_name' => __( 'Signature Collection', 'skyyrose' ),
				'world_name'      => __( 'The Golden Gate Runway', 'skyyrose' ),
				'tagline'         => __( 'The Origin. The Crown.', 'skyyrose' ),
				'accent_color'    => SKYYROSE_COLOR_GOLD,
				'rooms'           => skyyrose_experience_filter_rooms(
					array(
						array(
							'name'     => esc_html__( 'The Golden Gate', 'skyyrose' ),
							'image'    => $room1_image( 'scene-signature-golden-gate.webp' ),
							'products' => array(
								skyyrose_immersive_product(
									'sg-009',
									array(
										'left'       => '15',
										'top'        => '42',
										'prop'       => 'glass-orb',
										'prop_label' => __( 'Inside glass orb display case', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'sg-002',
									array(
										'left'       => '42',
										'top'        => '35',
										'prop'       => 'gold-display-frame',
										'prop_label' => __( 'Hanging in gold-lit LED display frame', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'sg-003',
									array(
										'left'       => '50',
										'top'        => '38',
										'prop'       => 'gold-display-frame',
										'prop_label' => __( 'Hanging in gold-lit LED display frame', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'sg-006',
									array(
										'left'       => '62',
										'top'        => '36',
										'prop'       => 'gold-display-frame',
										'prop_label' => __( 'Hanging in gold-lit LED display frame', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'sg-001',
									array(
										'left'       => '78',
										'top'        => '50',
										'prop'       => 'marble-pedestal',
										'prop_label' => __( 'Featured on stepped marble pedestal', 'skyyrose' ),
									)
								),
							),
						),
						array(
							'name'     => esc_html__( 'The Bay Bridge', 'skyyrose' ),
							'image'    => 'scene-signature-bay-bridge.webp',
							'products' => array(
								skyyrose_immersive_product(
									'sg-011',
									array(
										'left'       => '18',
										'top'        => '38',
										'prop'       => 'clothing-rack',
										'prop_label' => __( 'Hanging on left wall clothing rack', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'sg-005',
									array(
										'left'       => '50',
										'top'        => '52',
										'prop'       => 'marble-display-table',
										'prop_label' => __( 'Featured on center marble display table', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'sg-007',
									array(
										'left'       => '32',
										'top'        => '48',
										'prop'       => 'marble-pedestal',
										'prop_label' => __( 'On left marble pedestal', 'skyyrose' ),
									)
								),
								skyyrose_immersive_product(
									'sg-015',
									array(
										'left'       => '72',
										'top'        => '38',
										'prop'       => 'clothing-rack',
										'prop_label' => __( 'Hanging on right wall clothing rack', 'skyyrose' ),
									)
								),
							),
						),
					)
				),
			);

		case 'kids-capsule':
			return array(
				'collection_name' => __( 'Kids Capsule Collection', 'skyyrose' ),
				'world_name'      => __( 'The Playroom', 'skyyrose' ),
				'tagline'         => __( 'Luxury runs in the family.', 'skyyrose' ),
				'accent_color'    => SKYYROSE_COLOR_ROSE_GOLD,
				'rooms'           => skyyrose_experience_filter_rooms(
					array(
						array(
							'name'     => esc_html__( 'The Playroom', 'skyyrose' ),
							'image'    => $room1_image( 'scene-kids-capsule-playroom.webp' ),
							'products' => array(
								skyyrose_immersive_product(
									'kids-001',
									array(
										'left'       => '50',
										'top'        => '38',
										'prop'       => 'playroom-display',
										'prop_label' => __( 'Featured on center playroom display', 'skyyrose' ),
									)
								),
							),
						),
						array(
							'name'     => esc_html__( 'The Runway', 'skyyrose' ),
							'image'    => 'scene-kids-capsule-runway.webp',
							'products' => array(
								skyyrose_immersive_product(
									'kids-002',
									array(
										'left'       => '50',
										'top'        => '38',
										'prop'       => 'playroom-display',
										'prop_label' => __( 'Featured on center runway display', 'skyyrose' ),
									)
								),
							),
						),
					)
				),
			);
	}

	return null;
}

/**
 * Drop empty product entries (unpublished SKUs filtered by
 * skyyrose_immersive_product()) and rooms left with no products.
 *
 * @since 1.8.0
 * @param  array $rooms Raw room definitions.
 * @return array Filtered rooms, reindexed.
 */
function skyyrose_experience_filter_rooms( array $rooms ) {
	$filtered = array();
	foreach ( $rooms as $room ) {
		$room['products'] = array_values( array_filter( $room['products'] ) );
		$filtered[]       = $room;
	}
	return $filtered;
}
