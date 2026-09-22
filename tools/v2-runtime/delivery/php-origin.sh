#!/bin/sh
# Owned local worker only. Never targets the independent 18303 process.
set -eu
ORIGIN_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ORIGIN_REPO=$(CDPATH= cd -- "$ORIGIN_DIR/../../.." && pwd)
ORIGIN_STATE="$ORIGIN_REPO/.artifacts/v2-delivery-20260906/php-origin"
ORIGIN_PID="$ORIGIN_STATE/pid"
mkdir -p "$ORIGIN_STATE"
owned() {
  test -f "$ORIGIN_PID" && test -f "$ORIGIN_STATE/identity" || return 1
  ORIGIN_PROCESS=$(cat "$ORIGIN_PID")
  case "$ORIGIN_PROCESS" in ''|*[!0-9]*) return 1;; esac
  test "$ORIGIN_PROCESS" -gt 1 || return 1
  test "$(ps -p "$ORIGIN_PROCESS" -o lstart= -o command=)" = "$(cat "$ORIGIN_STATE/identity")"
}
case "${1:-}" in
  start)
    test ! -e "$ORIGIN_PID" || { echo 'Existing ownership record: inspect or stop the owned worker first.' >&2; exit 1; }
    : "${V2_WP_FIXTURE:?Set the existing isolated V2_WP_FIXTURE}"
    ORIGIN_FIXTURE=$(CDPATH= cd -- "$V2_WP_FIXTURE" && pwd -P)
    case "$ORIGIN_FIXTURE" in "$ORIGIN_REPO"/.artifacts/*/wordpress) ;; *) echo 'Fixture must be this repository .artifacts WordPress fixture.' >&2; exit 1;; esac
    test -f "$ORIGIN_FIXTURE/wp-content/mu-plugins/local-isolation.php"
    test -f "$ORIGIN_FIXTURE/wp-content/mu-plugins/v2-delivery-origin.php"
    ORIGIN_ROUTER="$(dirname -- "$ORIGIN_FIXTURE")/router.php"
    test -f "$ORIGIN_ROUTER"
    ORIGIN_PHP=$(command -v php)
    ORIGIN_PHP=$(php -r 'echo realpath($argv[1]);' "$ORIGIN_PHP")
    # A lock prevents two launchers from racing before a PID is published.
    mkdir "$ORIGIN_STATE/launch-lock" || exit 1
    trap 'rmdir "$ORIGIN_STATE/launch-lock"' EXIT
    test ! -e "$ORIGIN_PID"
    # Explicit flags also appear in ps/identity; the env override wins over php.ini.
    ORIGIN_PROCESS=$(node -e '
      const fs = require("node:fs");
      const { spawn } = require("node:child_process");
      const log = fs.openSync(process.argv[1], "a");
      const child = spawn(process.argv[2], process.argv.slice(3), {
        detached: true, env: { ...process.env, XDEBUG_MODE: "off" },
        stdio: ["ignore", log, log]
      });
      child.on("error", error => { console.error(error.message); process.exitCode = 1; });
      child.on("spawn", () => { process.stdout.write(String(child.pid)); child.unref(); fs.closeSync(log); });
    ' "$ORIGIN_STATE/server.log" "$ORIGIN_PHP" \
      -d xdebug.mode=off -d display_errors=0 -d error_reporting=22527 \
      -d opcache.enable=1 -d opcache.enable_cli=1 \
      -d opcache.validate_timestamps=1 -d opcache.revalidate_freq=0 \
      -d opcache.revalidate_path=1 -d opcache.use_cwd=1 \
      -d opcache.save_comments=1 -d opcache.enable_file_override=0 \
      -d opcache.jit=disable -d realpath_cache_size=0 \
      -S 127.0.0.1:18309 -t "$ORIGIN_FIXTURE" "$ORIGIN_ROUTER"
    )
    sleep 1
    kill -0 "$ORIGIN_PROCESS" 2>/dev/null || { cat "$ORIGIN_STATE/server.log" >&2; exit 1; }
    ps -p "$ORIGIN_PROCESS" -o lstart= -o command= > "$ORIGIN_STATE/identity"
    printf '%s\n' "$ORIGIN_PROCESS" > "$ORIGIN_PID"
    printf '%s\n' "$ORIGIN_FIXTURE" > "$ORIGIN_STATE/fixture"
    printf '%s\n' "$ORIGIN_ROUTER" > "$ORIGIN_STATE/router"
    printf '%s\n' "$ORIGIN_PHP" > "$ORIGIN_STATE/binary"
    owned || exit 1
    echo "Owned PHP origin ready: PID $ORIGIN_PROCESS, 127.0.0.1:18309"
    ;;
  stop)
    owned || { echo 'Refusing to signal a missing or mismatched owned process.' >&2; exit 1; }
    kill -TERM "$ORIGIN_PROCESS"
    ORIGIN_TRIES=0
    while kill -0 "$ORIGIN_PROCESS" 2>/dev/null; do
      ORIGIN_TRIES=$((ORIGIN_TRIES + 1))
      test "$ORIGIN_TRIES" -lt 10 || { echo 'Worker did not exit; retained ownership record.' >&2; exit 1; }
      sleep 1
    done
    rm "$ORIGIN_PID" "$ORIGIN_STATE/identity"
    ;;
  status)
    owned || { echo 'Owned worker is absent or identity changed.' >&2; exit 1; }
    cat "$ORIGIN_STATE/identity"
    ;;
  *) echo 'Usage: php-origin.sh start|stop|status' >&2; exit 2;;
esac
