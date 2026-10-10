#!/usr/bin/env bash
set -euo pipefail

theme_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

php -l "${theme_dir}/inc/performance.php"
php -l "${theme_dir}/scripts/test-performance.php"
php "${theme_dir}/scripts/test-performance.php"

if rg -n "(wc-add-to-cart|wc-cart-fragments|woocommerce-general).*dequeue" "${theme_dir}/inc/performance.php"; then
	echo "FAIL performance policy must not dequeue WooCommerce purchase assets" >&2
	exit 1
fi

echo "PASS performance verification"
