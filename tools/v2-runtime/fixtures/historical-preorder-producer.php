<?php
function skyyrose_create_preorder_snapshot( $config ) {
	return array(
		'schema'                   => 'skyyrose.preorder-commercial-promise',
		'schema_version'           => 1,
		'is_preorder'              => true,
		'product_id'               => absint( $config['product_id'] ?? 0 ),
		'variation_id'             => absint( $config['variation_id'] ?? 0 ),
		'configuration_source_id'  => absint( $config['configuration_source_id'] ?? 0 ),
		'allocation_source_id'     => absint( $config['allocation_source_id'] ?? 0 ),
		'edition_size'             => isset( $config['edition_size'] ) ? absint( $config['edition_size'] ) : null,
		'available_at_add_to_cart' => isset( $config['available'] ) ? absint( $config['available'] ) : null,
		'expected_ship_date'       => (string) ( $config['expected_ship_date'] ?? '' ),
	);
}
