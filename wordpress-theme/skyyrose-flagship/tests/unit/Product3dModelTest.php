<?php
/**
 * Tests for inc/product-3d-model.php — the 3D model URL policy.
 *
 * @package SkyyRose
 */

use PHPUnit\Framework\TestCase;

class Product3dModelTest extends TestCase {

	// home_url() stub = https://skyyrose.co (tests/stubs/wp-stubs.php).

	public function test_same_host_https_glb_accepted(): void {
		$url = 'https://skyyrose.co/wp-content/uploads/3d/br-006.glb';
		$this->assertSame( $url, skyyrose_sanitize_3d_model_url( $url ) );
	}

	public function test_same_host_gltf_accepted_and_host_case_insensitive(): void {
		$url = 'https://SkyyRose.co/models/sg-006.gltf';
		$this->assertSame( $url, skyyrose_sanitize_3d_model_url( $url ) );
	}

	public function test_relative_path_accepted(): void {
		$this->assertSame( '/wp-content/uploads/3d/br-006.glb', skyyrose_sanitize_3d_model_url( '/wp-content/uploads/3d/br-006.glb' ) );
	}

	public function test_query_string_does_not_hide_extension(): void {
		$url = 'https://skyyrose.co/3d/br-006.glb?ver=2';
		$this->assertSame( $url, skyyrose_sanitize_3d_model_url( $url ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( 'https://skyyrose.co/3d/br-006.png?x=.glb' ) );
	}

	public function test_off_site_https_rejected(): void {
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( 'https://cdn.example.com/br-006.glb' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( 'https://skyyrose.co.evil.com/br-006.glb' ) );
	}

	public function test_http_rejected(): void {
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( 'http://skyyrose.co/br-006.glb' ) );
	}

	public function test_protocol_relative_rejected(): void {
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( '//skyyrose.co/br-006.glb' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( '//evil.com/br-006.glb' ) );
	}

	/**
	 * esc_url_raw strips \ " < >, so a raw-string check for a leading "//" was
	 * unsound: these inputs BECAME protocol-relative off-site URLs after
	 * canonicalization and reached the page as data-model="//evil.com/x.glb".
	 */
	public function test_characters_stripped_into_a_protocol_relative_url_rejected(): void {
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( '/\/evil.com/br-006.glb' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( '/"/evil.com/br-006.glb' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( '/<>/evil.com/br-006.glb' ) );
	}

	public function test_credentials_and_explicit_port_rejected(): void {
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( 'https://user:pass@skyyrose.co/br-006.glb' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( 'https://evil.com\@skyyrose.co/br-006.glb' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( 'https://skyyrose.co:8443/br-006.glb' ) );
	}

	public function test_wrong_extension_rejected(): void {
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( 'https://skyyrose.co/br-006.png' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( '/wp-content/uploads/br-006.png' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( '/wp-content/uploads/br-006' ) );
	}

	public function test_javascript_and_data_schemes_rejected(): void {
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( 'javascript:alert(1)//.glb' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( 'data:model/gltf-binary;base64,AAAA.glb' ) );
	}

	public function test_empty_and_whitespace_sanitize_to_empty(): void {
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( '' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( '   ' ) );
		$this->assertSame( '', skyyrose_sanitize_3d_model_url( null ) );
	}

	public function test_lib_dir_constant_matches_vendored_directory(): void {
		$this->assertDirectoryExists( SKYYROSE_DIR . '/assets/js/lib/' . SKYYROSE_THREE_LIB_DIR );
		$this->assertFileExists( SKYYROSE_DIR . '/assets/js/lib/' . SKYYROSE_THREE_LIB_DIR . '/three.module.min.js' );
		$this->assertFileExists( SKYYROSE_DIR . '/assets/js/lib/' . SKYYROSE_THREE_LIB_DIR . '/basis/basis_transcoder.wasm' );
	}
}
