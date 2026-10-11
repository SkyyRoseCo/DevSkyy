<?php
/** Exact additional roles require their own source-bound owner grant. */
ob_start(); require __DIR__ . '/test-pdp-approved-fronts.php'; ob_end_clean();
function esc_attr( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_url( $value ) { return esc_attr( $value ); }
function skyyrose2_presentation_registry() { return $GLOBALS['presentation']; }
$counts = array( 'pdp_on_model_front' => 0, 'collection_hero' => 0, 'collection_story' => 0, 'merchandise_scene' => 0 );
foreach ( skyyrose2_media_inventory()['usage_adoptions'] as $relative => $binding ) {
	$record = skyyrose2_media_inventory()['assets'][ $relative ];
	foreach ( skyyrose2_media_usage_roles( $relative, $record ) as $role ) {
		check_front( skyyrose2_media_path_allowed( $relative, $role, $record['skus'][0] ), 'Current original admits its exact additional use' );
		++$counts[ $role ];
	}
	$bad = $record; $bad['skus'] = array( 'unknown-001' );
	check_front( ! skyyrose2_media_usage_roles( $relative, $bad ), 'Wrong SKU rejected' );
	$bad = $record; $bad['collections'] = array( 'unknown' );
	check_front( ! skyyrose2_media_usage_roles( $relative, $bad ), 'Wrong collection rejected' );
	$bad = $record; $bad['sha256'] = str_repeat( '0', 64 );
	check_front( ! skyyrose2_media_record_allowed( $relative, $bad ), 'Changed source rejected' );
	check_front( ! skyyrose2_media_path_allowed( $relative, 'production_publish' ), 'Unknown use rejected' );
	if ( 'FOUNDER_ACCEPTED' === $record['status'] ) { check_front( ! skyyrose2_founder_card_allowed( $relative, $record, 'pdp_on_model_front' ), 'Old card receipt alone remains card-only' ); }
}
check_front( $counts === array( 'pdp_on_model_front' => 15, 'collection_hero' => 4, 'collection_story' => 4, 'merchandise_scene' => 3 ), 'Exact 26 new uses' );
foreach ( array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ) as $collection ) {
	foreach ( array( 'collection_hero', 'collection_story', 'merchandise_scene' ) as $role ) {
		$media = skyyrose2_collection_media( $collection, $role );
		if ( 'kids-capsule' === $collection && 'merchandise_scene' === $role ) { check_front( ! $media, 'No invented Kids preorder slot' ); continue; }
		check_front( $media && $media['collection'] === $collection && $media['role'] === $role, 'Runtime resolves the exact canonical collection placement' );
		$pre = $GLOBALS['presentation']['products'][ $media['sku'] ]['is_preorder'];
		check_front( 'merchandise_scene' === $role ? $pre : ! $pre, 'Only preorder merchandise enters reserve; hero and story use standard merchandise' );
	}
}
echo json_encode( array( 'status' => 'PASS', 'additional_roles' => $counts, 'current_pdp_fronts' => $displayed['pdp_on_model_front'], 'negative_cases' => 22 * 4 + 12 ), JSON_PRETTY_PRINT ) . "\n";
