# V2 local HTTP delivery parity

This is a real Nginx compression gateway for the existing isolated WordPress
fixture. It does not change theme CSS/JS, Lighthouse, throttling, scores, native
jQuery ordering, database options, product authority or production hosting.
Decoded asset bytes are unchanged. Public theme assets and filtered public
WordPress/WooCommerce assets use Nginx's native static handler; dynamic requests
reach the PHP fixture. Nginx has no response cache.
This is a host-owned configuration example,
not a claim that a WordPress theme enables compression on WordPress.com.

## Reproduce on Docker Desktop for macOS

Prerequisites: Docker Desktop, Node 22+, PHP CLI, and the existing isolated
WordPress fixture. The independent raw worker on `127.0.0.1:18303` stays untouched;
this launcher owns a separate worker on `127.0.0.1:18309`. Its `local-isolation.php` must
continue disabling outbound HTTP, mail, payment gateways and webhooks. This
workflow does not install WordPress or change its data. Linux host networking
is not certified by this configuration; do not expose the PHP fixture publicly
to make `host.docker.internal` reachable.

From the repository root:

```sh
docker pull "$(cat tools/v2-runtime/delivery/image.txt)"
export V2_WP_FIXTURE="$PWD/.artifacts/v2-phase3-20260905/wordpress"
tools/v2-runtime/delivery/gateway.sh install-fixture
tools/v2-runtime/delivery/php-origin.sh start
tools/v2-runtime/delivery/gateway.sh start
tools/v2-runtime/delivery/gateway.sh check
node --test tools/v2-runtime/delivery/verify.test.cjs tools/v2-runtime/delivery/native-assets.test.cjs
php tools/v2-runtime/delivery/test-fixture-origin.php guard
php tools/v2-runtime/delivery/test-fixture-origin.php disabled
php tools/v2-runtime/delivery/test-fixture-origin.php enabled
node tools/v2-runtime/delivery/verify.cjs \
  .artifacts/v2-delivery-20260906/parity-fresh.json
```

The installer refuses an existing adapter instead of overwriting it. On a
previously configured fixture, inspect its exact source path and skip installation.
A container name collision also fails instead of replacing an unknown container.
The official `nginx:1.28-alpine` image is pinned by the digest in `image.txt`.
The original pull resolved to
`sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236`
on arm64. No mutable tag is used to start the gateway. Nginx runs as UID/GID101,
with a read-only filesystem, dropped capabilities and temporary files in tmpfs.
Docker publishes only `127.0.0.1:18308`; Nginx additionally rejects other Host
values. The one fixed upstream is `host.docker.internal:18309`.

The selected theme's `assets/` directory is mounted read-only at
`/srv/v2-assets`. The default is this checkout's V2 assets. To compare a different
source checkout, set `V2_DELIVERY_ASSETS` to that checkout's absolute `assets`
directory before starting the gateway and when running the verifier. Stop/start
the gateway when changing its source mount. The WordPress fixture theme and
asset mount must reference the same source revision; changing only its PHP
theme symlink is not sufficient. The verifier binds its expected asset root to
the inspected mount and checks wire hashes against that root.

The MU installer creates only `wp-content/mu-plugins/v2-delivery-origin.php` in
the explicitly supplied `.artifacts` fixture. Its source is tracked here. The
adapter requires both an explicit fixture constant and exact `HTTP_HOST`
`127.0.0.1:18308`. It filters `home` and `siteurl` for that request only. Core can
initialize `WP_CONTENT_URL` before MU loading, so the URL APIs `content_url`,
`plugins_url`, `theme_root_uri`, `includes_url`, and upload `url`/`baseurl` also
map only the exact old fixture origin to the gateway. It never rewrites HTML,
attachment files/IDs/physical paths, unrelated URLs, or stored database values.
Raw18303 requests remain unchanged.

## Native public static delivery and the 504 repair

The earlier theme-only static profile still sent native jQuery, WooCommerce
scripts and native CSS through the Docker-to-PHP development-server relay.
Observed upstream connection 504s caused missing `jQuery`/`Cookies` globals.
This profile serves those static bytes directly without changing their loading
strategy, request priority, throttle, proxy timeouts, gzip level or cache policy.

`gateway.sh start` requires `V2_WP_FIXTURE`, verifies the owned PHP process
identity, and requires that environment path to resolve to the same fixture as
the worker ownership record before creating snapshots. The HTTP verifier repeats
that equality check against the fixture established by its actual worker proof.
After that startup check, the launcher runs `native-assets.cjs`. It creates an immutable, content-addressed snapshot under
`.artifacts/v2-delivery-20260906/native-static/` from exactly:

| Fixture source directory | Read-only container destination |
| --- | --- |
| `wp-includes/js` | `/srv/v2-core-js` |
| `wp-includes/css` | `/srv/v2-core-css` |
| `wp-includes/fonts` | `/srv/v2-core-fonts` |
| `wp-content/plugins/woocommerce/assets` | `/srv/v2-woo-assets` |

The original native directories contain PHP files and JSON manifests. They are
**not directly mounted**. Only allowlisted CSS, JavaScript, public images, WASM
and font files are copied; no PHP, JSON, source maps, dotfiles or customer uploads
enter the mounted snapshot. Every copied byte retains its source SHA-256, and
all source symlinks fail closed. No installation file is changed. The receipt,
which sits outside the mounted directories, records the fixture path, installed
WordPress/WooCommerce versions and version-source hashes, all copied paths,
sizes and hashes, and the four snapshot mount identities. Source drift produces
a different snapshot; stale/tampered existing snapshots fail verification.

The Nginx route allowlist independently rejects private extensions, directories,
dot paths, symlinks, traversal encodings and methods other than GET/HEAD. Public
SVG/GIF/WOFF/TTF/EOT types are included for native core/editor/Woo assets; the
existing theme allowlist is unchanged. Actual `Inter-VariableFont_slnt,wght.woff2`
names are supported. Asset responses retain native MIME, HEAD and byte-range
behavior. PHP routes, AJAX, cart, checkout and account remain proxied uncached.

After an authorized restart, use a **new** parity receipt path. The verifier
checks exact identity/gzip bytes for native jQuery, js-cookie and native CSS,
exact font bytes, HEAD/range/416/write denial, all four read-only mount identities,
source inventory hashes and coverage of native resource URLs emitted in the
current frontend HTML. This is not a replacement for browser verification of
JavaScript-created requests. No successful live proof is implied by source tests.

This is a new delivery profile. Preserve earlier theme-only static measurements
as historical and rerun baseline and candidate with these same native snapshots,
Nginx configuration, PHP profile and throttling. Do not compare measurements
across profiles as though the theme alone caused the change. The configuration
remains a reproducible local fixture and host-owned infrastructure example;
production/WordPress.com delivery is unverified.

## What is compressed and preserved

Nginx compresses HTML and declared textual MIME types (CSS, JavaScript, JSON,
XML, SVG and plain text), minimum256bytes, gzip level6. It requests identity
upstream and performs the actual HTTP content encoding at the gateway.
`Vary: Accept-Encoding` is enabled. Already-compressed garment images, fonts,
films and the model are not added to gzip MIME types.

Dynamic upstream status, MIME, redirects and cookies pass through. Error interception,
redirect rewriting, retrying requests, proxy caching and proxy storage are off.
No cache zone, `expires`, cache bypass exception or static-versus-commerce cache
is installed: **cart, checkout, account and all other dynamic pages always reach
the existing upstream**. Existing upstream cache headers remain authoritative.
The fixture adapter and diagnostic header must never be shipped to production.

The exact public route `/wp-content/themes/skyyrose-flagship-2/assets/` serves
only `css`, `js`, `wasm`, `glb`, `png`, `jpg`, `jpeg`, `webp`, `mp4`, `webm` and
`woff2`. File and directory names must fit the explicit safe-character pattern.
Nginx handles HEAD, ranges (206), unsatisfiable ranges (416), MIME, Last-Modified
and ETag directly without involving PHP. WebM/MP4 and binary media remain
uncompressed, so range offsets address the exact original bytes. `wasm` uses
`application/wasm`, and `glb` uses `model/gltf-binary`.

Directory listing, symlinks, dot paths, PHP, JSON manifests, Markdown, text and
unknown extensions are denied. Ambiguous encoded traversal paths are rejected
before proxy routing; query strings are exempt from that path guard. Only GET
and HEAD are allowed in the static location. The mounts exclude the PHP theme
root, the full WordPress installation, private configuration and uploads. Existing JSON files under
assets are build/QA manifests, not runtime fetch dependencies. New asset types
require a reviewed allowlist extension; do not broaden to arbitrary files.

## Proof semantics

`verify.cjs` performs bounded HTTP GETs without a browser, dependency downloads,
redirect following, cart writes or external requests. It writes a RUNNING then
PASS/FAIL receipt, with runID and timestamps. Use a fresh output name to preserve
previous failed evidence. It verifies gzip and identity CSS/JS against SHA256 of
the actual theme files on disk, compression negotiation, MIME and status.

For HTML, each proof request opts into `X-V2-Delivery-Proof: 1`. The guarded
fixture adapter buffers that response and emits its pre-encoding SHA256 in
`X-V2-Fixture-Body-SHA256`. The verifier hashes the Nginx-decoded body and compares
**that same response**. It does not compare two separately rendered nonce-bearing
HTML requests. PDP HTML varied between requests during the first successful run;
each independently matched its own pre-encoding hash. Ordinary requests and
Lighthouse omit this header, so they do not enable the diagnostic output buffer.
The runner also checks that ordinary responses omit the diagnostic digest.
It requires an ordinary 200 HTML response with actual gzip and Vary, not merely
the absence of a diagnostic header. Checkout must return 200 or a valid redirect
with a nonempty same-origin Location; 404/500 cannot satisfy that gate.

The receipt also inspects the running Docker image ID, pinned image reference,
read-only setting and exact loopback port publication, and saves `nginx -T`
beside the JSON receipt with its SHA256. It rejects config changes newer than
container startup: restart the gateway before measuring a new configuration.
This binds the intended config to the inspected running container, not just a
source file that may never have been loaded.
The static proof additionally inspects the exact read-only mount, audits its
tree for symlinks, compares a complete approved VP9 response to source SHA256,
verifies prefix and suffix ranges against exact source slices, and checks native
416, HEAD/MIME/size for WebM/WOFF2/WASM/GLB. It tests traversal/private-file,
directory and write-method denial. The inventory digest binds paths and sizes;
it is not a replacement for the separately recorded content hashes.

The resource census examines scripts/images/video/posters/source sets and
stylesheet/preload/icon links in Home/Shop/PDP/cart/account/404 HTML, rejects
non-gateway origins and raw18303 strings, and preserves checkout's native empty
cart redirect without following it. This is source URL evidence, not a claim of
complete JavaScript-driven network coverage. The existing browser/Lighthouse
exact-origin guard remains mandatory for runtime network proof.

## Fair baseline and candidate measurements

Request an exclusive browser window before running Lighthouse. Stop HTTP
verifiers, builds and other browsers during the run. First measure unchanged
baseline `aabd2bffdc1e322862acd05a5640c14cf00f3acf` through this gateway, then
measure any theme delivery changes under the identical gateway image/config,
origin adapter, upstream fixture, dataset, native dependencies and QA versions.
Do not compare a raw18303 baseline directly with a compressed18308 candidate and
attribute the entire difference to theme changes. Preserve prior raw reports.
Likewise preserve the earlier proxy-only compressed reports as historical;
direct-static delivery is a new configuration. Compare both relevant theme
revisions under this same static configuration and matching asset mounts before
attributing gains to theme changes.

```sh
export V2_BASE_URL=http://127.0.0.1:18308
export V2_QA_PACKAGE="$PWD/.artifacts/v2-phase3-20260905/qa/package.json"
export V2_ARTIFACT_DIR="$PWD/.artifacts/v2-delivery-20260906/lighthouse"
node tools/v2-runtime/phase3b-browser/run-lighthouse.cjs compressed-baseline
# After root's source/build gate, use the exact same settings and a new label:
node tools/v2-runtime/phase3b-browser/run-lighthouse.cjs compressed-candidate
```

The existing runner executes its five cases serially and preserves its
exact-origin forward proxy. This task does not alter that proxy. Its upstream
`Connection: close` behavior applies to both comparison runs. Record config
SHA256, source/build SHA receipts and artifact labels with each result.
A passing local mobile LCP budget is still synthetic evidence, not field CWV or
proof of WordPress.com/CDN configuration. The separate hardware Skyy cost proof
remains necessary: the Lighthouse runner uses `--disable-gpu`.

## Stop and remove only the fixture adapter

```sh
tools/v2-runtime/delivery/gateway.sh stop
```

Inspect `v2-delivery-origin.php` and confirm that it is the generated file pointing
to this directory before deleting just that file from the fixture MU directory.
Do not remove `local-isolation.php`, reset the database or replace the WordPress
installation. The ordinary18303 fixture is unchanged when this adapter's Host
guard is inactive.

Official sources consulted 2026-09-06:
[Nginx gzip module](https://nginx.org/en/docs/http/ngx_http_gzip_module.html),
[Nginx proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html),
and [official Nginx container](https://hub.docker.com/_/nginx).

## Owned PHP profile and source switches

The original raw worker was confirmed by a same-worker diagnostic to already
have OPcache active, but Xdebug ran in coverage mode. `php-origin.sh` starts a
separate detached PHP worker with `XDEBUG_MODE=off` and explicit `xdebug.mode=off`.
It uses the existing PHP binary, fixture and router. No installation, database
write, page cache, object cache, customer cache or theme change is introduced.
The built-in PHP server remains a local development server, not a production
server recommendation. Only its instrumentation and bytecode policy model the
intended delivery comparison.

OPcache remains enabled; timestamp validation and path revalidation are on,
`revalidate_freq=0`, `realpath_cache_size=0`, and JIT is disabled. These settings
check source changes each request. They do not replace process restart on a
theme symlink switch. Start refuses an existing PID record; stop validates both
PID and exact process start time/command before sending TERM. A mismatch fails
closed without signaling an unrelated process. Port 18303 is never targeted.
Node built-ins detach the process into its own session so tool-shell teardown
cannot inadvertently terminate it. No Node package installation is required.

Before **each** baseline/candidate measurement, with all browser jobs stopped:

```sh
tools/v2-runtime/delivery/gateway.sh stop
tools/v2-runtime/delivery/php-origin.sh stop
# Atomically switch only the fixture theme symlink to the selected source.
# Set V2_DELIVERY_ASSETS to that SAME source's absolute assets directory.
export V2_WP_FIXTURE="$PWD/.artifacts/v2-phase3-20260905/wordpress"
tools/v2-runtime/delivery/php-origin.sh start
tools/v2-runtime/delivery/gateway.sh start
node tools/v2-runtime/delivery/verify.cjs /absolute/path/to/unique-parity.json
```

Then attest route markup and served asset hashes against the selected revision,
close all proof requests, and run the same serial Lighthouse cases with unchanged
Nginx/PHP settings. Repeat the full restart/proof for the other source. Preserve
old raw/proxy/static receipts as historical measurements; do not relabel them as
having this new worker profile.

The verifier creates a random-name, random-token MU diagnostic in the existing
guarded fixture and removes it in `finally`. It requires exact fixture ABSPATH,
Host `127.0.0.1:18308`, port 18309 and the per-run secret header. Only the explicitly
owned worker is queried. Its actual SAPI, PID, effective Xdebug modes, OPcache
settings and binary/INI/router/launcher hashes are included in a separate receipt.
No diagnostic token is retained in the receipt. No permanent public diagnostic
endpoint is installed. A terminated proof process may require manual removal of
its uniquely named `v2-worker-proof-*.php` file before the next benchmark; verify
none remain. The token and exact host/port guards remain effective even then.

The local gateway binds its PHP upstream to the task-owned `v2-php-origin` alias.
At each startup, `origin-ipv4.cjs` runs exactly one disposable, unprivileged,
read-only container from the same digest-pinned Nginx image, without mounts or
published ports, to resolve `host.docker.internal` using `getent ahostsv4`.
Only one unique canonical RFC1918 IPv4 address is accepted; unavailable,
ambiguous, public, or IPv6 results fail startup before native snapshot creation.
The address is supplied through the gateway's sole `--add-host` override. No
Docker address or DNS server is hardcoded, and no global networking is changed.
This avoids Docker's intermittently unreachable IPv6 host address while retaining
port 18309, existing connection settings, gzip, and uncached dynamic requests.

Parity verification binds Docker `HostConfig.ExtraHosts` to both live
`getent ahostsv4 v2-php-origin` and `getent ahosts v2-php-origin` results and
records those outputs plus the resolver source hash. Any additional override,
address mismatch, or IPv6 alias fails verification. A Docker host address change
requires an explicit gateway restart and fresh proof; there is no retry or
runtime DNS override. Repeat baseline and candidate under this same configuration;
earlier receipts using `host.docker.internal` directly remain historical.
Focused source checks: `node --test tools/v2-runtime/delivery/origin-ipv4.test.cjs`
and `sh -n tools/v2-runtime/delivery/gateway.sh`. These tests use mocked process
output and do not start a container or make a network request.
