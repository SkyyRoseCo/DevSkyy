#!/usr/bin/env bash
# Fail-closed local-review gate for the V2 template renderer.
#
# This intentionally verifies the preview contract only. It does not stand in
# for WordPress, WooCommerce, staging, payment, media-rights, or release QA.
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
preview_file="$repo_dir/tools/v2-theme-preview.php"
port="${SR2_PREVIEW_VERIFY_PORT:-18099}"
base_url="http://127.0.0.1:${port}/tools/v2-theme-preview.php"
server_log="$(mktemp -t sr2-preview-verify.XXXXXX)"
server_pid=""

cleanup() {
	if [[ -n "$server_pid" ]]; then
		kill "$server_pid" 2>/dev/null || true
		wait "$server_pid" 2>/dev/null || true
	fi
	rm -f "$server_log"
}
trap cleanup EXIT

require_text() {
	local needle="$1"
	local file="$2"
	if ! rg -Fq -- "$needle" "$file"; then
		echo "Preview contract missing required text: $needle" >&2
		exit 1
	fi
}

forbid_text() {
	local needle="$1"
	local file="$2"
	if rg -Fq -- "$needle" "$file"; then
		echo "Preview contract contains forbidden legacy fallback: $needle" >&2
		exit 1
	fi
}

php -l "$preview_file" >/dev/null
require_text "SkyyRose Flagship 2" "$preview_file"
require_text "sr2_preview_fail_closed" "$preview_file"
require_text "Unknown V2 preview route" "$preview_file"
require_text "Unknown V2 product fixture" "$preview_file"
require_text "V2 product fixture media unavailable" "$preview_file"
require_text "X-SkyyRose-Preview-Commit" "$preview_file"
require_text "data-card-direction=\"living-archive\"" "$repo_dir/wordpress-theme/skyyrose-flagship-2/template-parts/commerce/product-card.php"
forbid_text "../wordpress-theme/skyyrose-flagship/" "$preview_file"
forbid_text "?: preview_product_for_sku( 'sg-005' )" "$preview_file"

php -S "127.0.0.1:${port}" -t "$repo_dir" >"$server_log" 2>&1 &
server_pid="$!"

for attempt in {1..30}; do
	if curl --silent --fail --max-time 1 "$base_url?route=home" >/dev/null 2>&1; then
		break
	fi
	if [[ "$attempt" -eq 30 ]]; then
		cat "$server_log" >&2
		exit 1
	fi
	sleep 0.1
done

assert_response() {
	local query="$1"
	local expected_status="$2"
	local expected_template="$3"
	local response
	response="$(mktemp -t sr2-preview-response.XXXXXX)"
	local headers
	headers="$(mktemp -t sr2-preview-headers.XXXXXX)"
	local status
	status="$(curl --silent --show-error -o "$response" -D "$headers" -w '%{http_code}' "$base_url?$query")"
	if [[ "$status" != "$expected_status" ]]; then
		echo "Expected $query to return $expected_status, got $status" >&2
		cat "$response" >&2
		rm -f "$response" "$headers"
		exit 1
	fi
	if [[ -n "$expected_template" ]]; then
		rg -Fq "X-SkyyRose-Preview-Template: $expected_template" "$headers"
		rg -Fq 'name="skyyrose-preview-candidate"' "$response"
		rg -Fq "data-preview-route=\"${query#route=}" "$response" || true
	fi
	rm -f "$response" "$headers"
}

assert_response 'route=home' '200' 'front-page.php'
assert_response 'route=collections' '200' 'page.php'
assert_response 'route=shop' '200' 'woocommerce/archive-product.php'
assert_response 'route=product&sku=br-004' '200' 'woocommerce/single-product.php'
for collection_route in signature black-rose love-hurts kids-capsule; do
	assert_response "route=${collection_route}" '200' 'template-collection.php'
done
for immersive_route in immersive-signature immersive-black-rose immersive-love-hurts immersive-kids-capsule; do
	assert_response "route=${immersive_route}" '200' "template-${immersive_route}.php"
done
for page_route in pre-order about contact wishlist faq shipping-returns returns-exchanges size-guide privacy-policy terms-of-service accessibility; do
	assert_response "route=${page_route}" '200' 'page.php'
done
assert_response 'route=journal' '200' 'index.php'
for commerce_route in cart checkout account order-tracking; do
	assert_response "route=${commerce_route}" '200' 'template-parts/v2-commerce-preview.php'
done
assert_response 'route=404' '200' '404.php'
assert_response 'route=does-not-exist' '404' ''
assert_response 'route=product&sku=does-not-exist' '404' ''
assert_response 'route=product&sku=br-003' '422' ''

echo "PASS V2 local preview canonical route gate"
