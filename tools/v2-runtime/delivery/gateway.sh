#!/bin/sh
set -eu
DELIVERY_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DELIVERY_IMAGE=$(cat "$DELIVERY_DIR/image.txt")
DELIVERY_CONTAINER=skyyrose-v2-delivery-18308
case "${1:-}" in
  start)
    DELIVERY_ASSETS=${V2_DELIVERY_ASSETS:-"$DELIVERY_DIR/../../../wordpress-theme/skyyrose-flagship-2/assets"}
    DELIVERY_ASSETS=$(CDPATH= cd -- "$DELIVERY_ASSETS" && pwd -P)
    test "$(basename -- "$DELIVERY_ASSETS")" = assets
    test -f "$DELIVERY_ASSETS/../style.css"
    "$DELIVERY_DIR/php-origin.sh" status >/dev/null
    DELIVERY_ORIGIN_IP=$(node "$DELIVERY_DIR/origin-ipv4.cjs")
    DELIVERY_NATIVE=$(node "$DELIVERY_DIR/native-assets.cjs")
    docker run --detach --name "$DELIVERY_CONTAINER" --read-only --user 101:101 \
      --cap-drop ALL --security-opt no-new-privileges \
      --tmpfs /tmp:rw,noexec,nosuid,size=32m \
      --publish 127.0.0.1:18308:8080 \
      --add-host "v2-php-origin:$DELIVERY_ORIGIN_IP" \
      --mount "type=bind,src=$DELIVERY_DIR/nginx.conf,dst=/etc/nginx/nginx.conf,readonly" \
      --mount "type=bind,src=$DELIVERY_ASSETS,dst=/srv/v2-assets,readonly" \
      --mount "type=bind,src=$DELIVERY_NATIVE/core-js,dst=/srv/v2-core-js,readonly" \
      --mount "type=bind,src=$DELIVERY_NATIVE/core-css,dst=/srv/v2-core-css,readonly" \
      --mount "type=bind,src=$DELIVERY_NATIVE/core-fonts,dst=/srv/v2-core-fonts,readonly" \
      --mount "type=bind,src=$DELIVERY_NATIVE/woo-assets,dst=/srv/v2-woo-assets,readonly" \
      --entrypoint nginx "$DELIVERY_IMAGE" -g 'daemon off;'
    ;;
  stop) docker stop "$DELIVERY_CONTAINER"; docker rm "$DELIVERY_CONTAINER" ;;
  check) docker exec "$DELIVERY_CONTAINER" nginx -t ;;
  install-fixture)
    : "${V2_WP_FIXTURE:?Set V2_WP_FIXTURE to the existing isolated WordPress fixture}"
    test -f "$V2_WP_FIXTURE/wp-content/mu-plugins/local-isolation.php"
    php -r '
      $root = realpath($argv[1]);
      $source = realpath($argv[2]);
      if (!$root || !str_contains($root, "/.artifacts/") || !$source) { fwrite(STDERR, "Only an existing .artifacts fixture is allowed.\n"); exit(1); }
      $target = $root . "/wp-content/mu-plugins/v2-delivery-origin.php";
      $content = "<?php\n// Local synthetic delivery only; removable without a database change.\ndefine(\x27SKYYROSE_V2_DELIVERY_FIXTURE\x27, true);\nrequire " . var_export($source, true) . ";\n";
      $handle = fopen($target, "x");
      if (!$handle) { fwrite(STDERR, "Refusing to overwrite an existing adapter.\n"); exit(1); }
      fwrite($handle, $content); fclose($handle);
      echo $target, "\n";
    ' "$V2_WP_FIXTURE" "$DELIVERY_DIR/fixture-origin.php"
    ;;
  *) echo 'Usage: gateway.sh start|stop|check|install-fixture' >&2; exit 2 ;;
esac
