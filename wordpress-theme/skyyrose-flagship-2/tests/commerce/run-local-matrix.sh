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
mutation_lock="$fixture_root/.sr-release-mutation-lock"
mkdir "$mutation_lock" || { echo 'Another fixture mutation suite is active; do not overlap order-authority changes.' >&2; exit 1; }
trap 'rmdir "$mutation_lock"' EXIT
mkdir -p "$evidence_dir"
wp_local eval 'echo wp_json_encode(array("home"=>get_option("home"),"wp"=>get_bloginfo("version"),"woo"=>WC_VERSION,"database"=>defined("DB_ENGINE") ? DB_ENGINE : "mysql"));' > "$evidence_dir/local-environment.json"
wp_local eval 'if (!defined("SKYYROSE_RELEASE_SYNTHETIC_FIXTURE") || !SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== "sr_release_fixture" || !has_filter("pre_http_request") || !has_filter("pre_wp_mail") || !has_filter("woocommerce_webhook_should_deliver")) { throw new RuntimeException("Qualified isolated release fixture required."); }'

for mode in cpt-off hpos-off cpt-on hpos-on; do
  wp_local wc hpos sync > "$evidence_dir/sync-$mode.txt" 2>&1
  wp_local eval '$s=wc_get_container()->get(Automattic\WooCommerce\Internal\DataStores\Orders\DataSynchronizer::class); if ($s->has_orders_pending_sync()) { throw new RuntimeException("Incomplete synchronization blocks changing order authority."); }'
  wp_local option update woocommerce_custom_orders_table_data_sync_enabled no --quiet
  if [[ "$mode" == cpt-* ]]; then
    wp_local option update woocommerce_custom_orders_table_enabled no --quiet
  else
    wp_local option update woocommerce_custom_orders_table_enabled yes --quiet
  fi
  if [[ "$mode" == *-on ]]; then
    wp_local option update woocommerce_custom_orders_table_data_sync_enabled yes --quiet
  fi
  wp_local eval 'echo wp_json_encode(array("hpos_authoritative"=>Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled(),"sync"=>get_option("woocommerce_custom_orders_table_data_sync_enabled"),"native_order_data_store"=>(new WC_Order())->get_data_store()->get_current_class_name()));' > "$evidence_dir/$mode-storage.json"
  SKYYROSE_RELEASE_MIGRATION_TESTS=1 wp_local eval-file "$test_dir/preorder.php" 2>&1 | tee "$evidence_dir/$mode.txt"
done
# Deliberately create an unmirrored synthetic order and verify the same native
# readiness condition blocks an authority transition until synchronization.
wp_local option update woocommerce_custom_orders_table_data_sync_enabled no --quiet
wp_local eval '$o=new WC_Order(); $o->set_status("pending"); $o->save(); $s=wc_get_container()->get(Automattic\WooCommerce\Internal\DataStores\Orders\DataSynchronizer::class); if (!$s->has_orders_pending_sync()) { throw new RuntimeException("Failed to create incomplete synchronization control."); } echo "PASS: incomplete native synchronization detected; authority transition blocked\n";' > "$evidence_dir/incomplete-sync.txt"
wp_local wc hpos sync > "$evidence_dir/incomplete-sync-recovery.txt" 2>&1
wp_local eval '$s=wc_get_container()->get(Automattic\WooCommerce\Internal\DataStores\Orders\DataSynchronizer::class); if ($s->has_orders_pending_sync()) { throw new RuntimeException("Synchronization recovery failed."); } echo "PASS: complete native synchronization permits authority transition\n";' >> "$evidence_dir/incomplete-sync.txt"
