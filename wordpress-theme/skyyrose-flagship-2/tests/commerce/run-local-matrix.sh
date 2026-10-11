#!/usr/bin/env bash
# Only mutate an explicitly selected synthetic loopback fixture.
set -euo pipefail
fixture_root="${1:?Pass the isolated WordPress fixture directory}"
evidence_dir="${2:?Pass the local evidence output directory}"
test_dir="$(cd "$(dirname "$0")" && pwd)"
wp_cli="$(command -v wp)"

wp_local() {
  # Existing WP-CLI/react deprecations on PHP 8.5 are toolchain noise.
  # Preserve warnings/errors and all commands' exit statuses.
  php -d error_reporting=24575 "$wp_cli" --path="$fixture_root" "$@"
}

fixture_home="$(wp_local option get home)"
if [[ "$fixture_home" != 'http://127.0.0.1:18362' ]]; then
  echo 'Refusing a non-fixture site.' >&2
  exit 1
fi
mkdir -p "$evidence_dir"
wp_local eval 'echo wp_json_encode(array("home"=>get_option("home"),"wp"=>get_bloginfo("version"),"woo"=>WC_VERSION,"database"=>defined("DB_ENGINE") ? DB_ENGINE : "mysql"));' > "$evidence_dir/local-environment.json"

for mode in cpt hpos compatibility; do
  wp_local wc hpos sync > "$evidence_dir/sync-$mode.txt" 2>&1
  wp_local option update woocommerce_custom_orders_table_data_sync_enabled no --quiet
  if [[ "$mode" == 'cpt' ]]; then
    wp_local option update woocommerce_custom_orders_table_enabled no --quiet
  else
    wp_local option update woocommerce_custom_orders_table_enabled yes --quiet
  fi
  if [[ "$mode" == 'compatibility' ]]; then
    wp_local option update woocommerce_custom_orders_table_data_sync_enabled yes --quiet
  fi
  wp_local eval-file "$test_dir/preorder.php" 2>&1 | tee "$evidence_dir/$mode.txt"
done
