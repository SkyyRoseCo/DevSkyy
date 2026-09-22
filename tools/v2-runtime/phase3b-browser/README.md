# SkyyRose V2 Phase 3B browser verification

## Cinematic integration candidate

For the September 5 cinematic candidate, use `test-cinematic-integration.cjs`
after the current theme build. The historical `test-collection-browser.cjs`
expects Phase 3B's static composition and is not the cinematic scene gate.
The cinematic helper verifies 25 core collection cards, eight preserved Town
Line directory links, all 33 Shop cards through native pagination, keyboard
Quick View, nine approved scenes at three widths, motion fallbacks, and the
global shell. It requires the same isolated fixture and never submits orders.

```bash
V2_QA_PACKAGE="$PWD/.artifacts/v2-phase3-20260905/qa/package.json" \
V2_ARTIFACT_DIR="$PWD/.artifacts/v2-visual-recovery-20260905" \
node tools/v2-runtime/phase3b-browser/test-cinematic-integration.cjs
node tools/v2-runtime/phase3b-browser/build-cinematic-review.cjs
```

The review builder exposes only exact image/video evidence beneath its dedicated
`review/` directory. Serve that directory, never its WordPress-containing parent.
Home physical-gait recordings and real hardware measurements are separately
bound by `tasks/v2-visual-recovery-20260905/home-walkon-evidence.json`; an action
name alone is not evidence of movement. Source clips contain held poses and the
candidate derives new joint motion without changing the approved GLB.

These are the maintained copies of the eight helpers originally run from
`.artifacts/v2-phase3b-20260905/`. They remain explicit browser tasks, below
their own directory so the theme's
`node --test ../../tools/v2-runtime/test-*.cjs` unit wildcard does not launch
browsers or modify a cart. Promotion preserves the existing assertions, fixture
assumptions, screenshot dimensions, resource restrictions, and artifact names.
Shared configuration replaces hardcoded dependency/output paths. Invalid capture
labels, nonlocal targets, and unknown Lighthouse case names now fail early.

## Dependencies and setup

Use Node **22.19 or later** (promotion syntax checks used 22.23.2). Exact QA
versions are pinned in `package.json` and `package-lock.json`:

| Package              | Version |
| -------------------- | ------- |
| Playwright           | 1.58.2  |
| @axe-core/playwright | 4.11.1  |
| Lighthouse           | 13.4.1  |

The lockfile derives from the already installed Phase 3A QA environment and was
resolved with `--package-lock-only --offline --ignore-scripts`. No dependencies
or browser binaries were downloaded during promotion. Native
WordPress/WooCommerce code is not vendored here.

Run setup from the repository root when dependencies are needed:

```bash
npm ci --prefix tools/v2-runtime/phase3b-browser --ignore-scripts
node tools/v2-runtime/phase3b-browser/node_modules/playwright/cli.js install chromium
```

The Chromium installation command can download a browser; skip it when the
Playwright 1.58.2 browser is already installed. For the existing local QA
installation, use this instead of installing another copy:

```bash
export V2_QA_PACKAGE="$PWD/.artifacts/v2-phase3-20260905/qa/package.json"
```

When supplying an external QA package, confirm it contains the three pinned
versions above; the external package's own installation is outside this
lockfile. The helpers use that package to resolve both Playwright and the
Lighthouse CLI.

## Local fixture contract

Run only against the existing isolated **WordPress 7.1 / WooCommerce 11.1.0** V2
verification fixture with the current built theme. These tools do not create
WordPress, seed data, activate plugins, install a theme, reset sessions, or
start the server. Complete the normal theme build and source/package checks
before running them. Keep production and staging outside this workflow.

The default origin is `http://127.0.0.1:18303`. A different local port may be
selected with `V2_BASE_URL`; runtime validation rejects HTTPS, non-127.0.0.1
hosts, credentials, paths, queries, and fragments. Playwright browser contexts
abort requests outside the exact configured origin. The gallery test's direct
variation API request disables redirects and checks the response origin before
reading its body. Lighthouse now starts an HTTP forward proxy that permits only
the exact fixture origin, rejects other ports/literal IPs, and denies CONNECT
and protocol upgrades. Chromium receives an explicit proxy and disables its
implicit loopback bypass; the existing HTTPS and DNS restrictions remain. The
proxy passed six focused local HTTP tests and subsequently completed all five
Chrome/Lighthouse cases for the source-attested baseline and two final candidate
runs. Exact run IDs, positive per-case proxy traffic and report hashes are in
`tasks/v2-phase3b-20260905/performance-comparison.json`. These client
controls do not sandbox the WordPress server: the isolated fixture must retain
its independent `WP_HTTP_BLOCK_EXTERNAL` setting and disabled outbound provider
integrations. Third-party behavior, staging caches and optimizers remain outside
this evidence.

The journey fixtures are intentional and fail when their truth differs:

- Shop has enough products for a second page, the Signature category, a nonempty
  `max_price=30` result, native sorting, GET filters and the documented taxonomy
  route.
- `/product/sg-005/` has an initially unselected Size control; **M resolves to
  variation 182 at $25**, is purchasable, and supports the native gallery and
  fit guide. `pdp-behavior.cjs` explicitly asserts those values. Update fixture
  expectations only after reviewing the fixture; never alter live catalog data
  to satisfy this test.
- `/product/br-006/` and `/product/br-002/` expose permitted PDP media;
  `/product/br-003/` stays rejected. The gallery test reads the parent product
  ID from the rendered form and calls the native local `get_variation` AJAX
  endpoint.
- Collection tests apply to the completed Phase 3B collection renderer: one main
  heading, lazy cards, a `#shop` link, category navigation, and no legacy
  video/pinned horizontal-world structure. Run only worlds whose implementation
  checkpoint has completed.

`pdp-behavior.cjs` adds **one local cart item**, opens the bag, visits Cart and
Checkout, and verifies the subtotal. It does not submit payment, click Place
Order, or create an order. All contexts are fresh and unauthenticated; no
production session/cookies are imported. `test-gallery-delivery.cjs`
selects/reset sizes and posts only the read-oriented native variation lookup. No
tool changes inventory, product media approval or account permissions.

### Source switches in the local PHP fixture

Do not change the theme symlink beneath an already running PHP server and assume
both PHP and static assets switched together. A Phase 3B investigation reproduced
candidate PHP markup with baseline stylesheets. That mixed-source benchmark is
invalid. Restart the local PHP server on every source switch, disable the realpath
cache with `-d realpath_cache_size=0`, and verify an expected page markup marker plus
SHA-256 of served CSS/JS against the selected checkout before measuring. Restore and
verify the candidate in a `finally` path. The source-attested baseline/final receipts
and excluded attempts are recorded in the Phase 3B report. This is a local fixture
procedure, not a deployment method.

## Configuration and artifact handling

| Input                          | Default / meaning                                                                                |
| ------------------------------ | ------------------------------------------------------------------------------------------------ |
| `V2_BASE_URL`                  | `http://127.0.0.1:18303`; local origin only.                                                     |
| `V2_QA_PACKAGE`                | This directory's `package.json`; otherwise the absolute path to an already installed QA package. |
| `V2_ARTIFACT_DIR`              | Repository `.artifacts/v2-phase3b-20260905`; created if missing.                                 |
| `V2_LH_CASE`                   | Unset runs all five serial Lighthouse cases. A set value must match the exact case list below.   |
| Capture positional arguments   | `<label> </local/route/>`; label is used in output filenames.                                    |
| Lighthouse positional argument | Optional run label inserted before the case name in report filenames.                            |

Output names are preserved for existing report consumers. Repeating a run in the
same directory overwrites those files. Prefer a fresh evidence directory for a
new run and keep baseline files immutable:

Capture, static, inventory, collection and commerce runners begin by replacing
the old JSON receipt with `RUNNING`, a fresh UUID `runId`, and `startedAt`,
before loading browser dependencies. A companion `<receipt-name>.run.json`
records the same lifecycle. Successful completion after browser cleanup writes
`PASS` with `finishedAt`; caught errors overwrite the old receipt with `FAIL`
and the error. Array-shaped capture outputs remain arrays on success; their
sidecar carries the run metadata. An interrupted process can leave `RUNNING`,
which is incomplete evidence, never a pass. Old screenshots may remain on disk
after a failed run; they cannot certify that run. Check the matching run sidecar
and use fresh output directories instead of treating file presence as success.

```bash
export V2_ARTIFACT_DIR="$PWD/.artifacts/v2-phase3b-20260905/review-run-01"
```

## Exact commands and evidence scope

Run commands from the repository root. The JavaScript tools themselves resolve
their default repository paths from their own location.

| Command                                                                                                          | Outputs and what it establishes                                                                                                                                                                                                                                                                                                                                                                                |
| ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `node tools/v2-runtime/phase3b-browser/capture-surface.cjs shop-final /shop/`                                    | `<label>-<width>.png` at 320, 360, 375, 390, 414, 768, 1024, 1280, 1440, 1728; full-page captures at 390/1440; `<label>-responsive.json`. Records overflow, page errors, images/cards and main-scoped axe violations at 390/768/1440. It asserts HTTP 200 and waits for visible media/native gallery state; recorded axe/errors/overflow still require review and are not automatically a zero-violation gate. |
| `node tools/v2-runtime/phase3b-browser/static-surface.cjs pdp-final /product/sg-005/`                            | `<label>-delayed-390.png`, corresponding 1440/nojs captures, and `<label>-static.json`. Captures theme-enhancement delay and disabled page JavaScript separately; records before/after height and gallery visibility. This is evidence capture, not an assertion that every native commerce interaction works without JavaScript.                                                                              |
| `node tools/v2-runtime/phase3b-browser/test-shop-browser.cjs`                                                    | `shop-behavior.json`, `shop-filter-390.png`. Asserts JS/no-JS filtering, reload, sorting, history, empty-state recovery, pagination, malformed query handling, taxonomy selection, keyboard disclosure, no page errors and zero main-scoped axe violations for the tested filter state.                                                                                                                        |
| `node tools/v2-runtime/phase3b-browser/pdp-behavior.cjs`                                                         | `pdp-behavior.json`, `pdp-selected-390.png`, `pdp-state-<sku>-390.png`. Shop→PDP→valid M variation→local cart/bag→Cart→Checkout subtotal, native lightbox, fit-guide focus restoration, and the four media-state fixtures. Stops before any order submission.                                                                                                                                                  |
| `node tools/v2-runtime/phase3b-browser/test-gallery-delivery.cjs`                                                | `gallery-delivery.json`, `pdp-delivery-selected-390.png`. Permitted/rejected visible gallery, embedded reset template, global default cache, M→reset→M, explicit lightbox and direct AJAX variation delivery. Asserts no rejected BR-003 attachment request and no embedded rejected image.                                                                                                                    |
| `node tools/v2-runtime/phase3b-browser/test-collection-browser.cjs signature black-rose love-hurts kids-capsule` | `collections-behavior.json`. At 390px, JS/no-JS card loading, shop anchor, real PDP links, back/reload and native category query. With no arguments, tests Signature only. This does not replace the ten-width visual capture pass.                                                                                                                                                                            |
| `node tools/v2-runtime/phase3b-browser/home-behavior.cjs`                                                        | Home's eight acts; SG-005 and two canonical Kids cards, all lazy; five continue GET destinations returning 200; no-JS native Quick View fallback to PDP. Checks exact Quick View name/collection/price/status/image/PDP URL, Enter/Tab/Escape and focus return, plus axe at 390/1440 across seven surfaces. No cart writes. Run after the Home implementation checkpoint.                                      |
| `node tools/v2-runtime/phase3b-browser/inventory-final.cjs`                                                      | `final-page-inventory.json`; Home, Shop, PDP and four collection routes at 390/1440. Fresh browser context **per page**, initial load plus 1200ms, no scroll, reduced motion. Records request/decoded bytes, images, font/CSS/JS totals, errors and failures. HTTP status is asserted; recorded metrics still require review.                                                                                  |

`static-surface.cjs` delays only scripts beneath
`/themes/skyyrose-flagship-2/assets/js/`. Native jQuery/Woo scripts are not held
in that mode. Its separate `nojs` mode disables page JavaScript; Playwright's
inspection APIs can still read the DOM. Do not describe theme-delay evidence as
“all JavaScript delayed.” The capture helpers wait for fonts and visible images
and may scroll/decode images before full-page screenshots; they are **not**
performance measurements.

## Lighthouse: serial, isolated runs only

**Do not run Lighthouse while another browser capture, test, theme build,
dependency installation, or local profiling process is active.** The runner uses
awaited child processes, so its own cases run serially while the proxy remains
responsive, but it does not coordinate separate processes or acquire a
machine-wide lock. Reserve the local fixture before starting. Do not run
multiple invocations in parallel.

```bash
node tools/v2-runtime/phase3b-browser/run-lighthouse.cjs final-01
V2_LH_CASE=pdp-mobile node tools/v2-runtime/phase3b-browser/run-lighthouse.cjs repeat-02
```

Exact cases: `home-mobile`, `home-desktop`, `pdp-mobile`, `pdp-desktop`,
`shop-mobile`. Reports are `lighthouse-<label>-<case>.json` and `.html` (label
omitted when absent). Mobile uses 390×844, device scale factor 1 and
Lighthouse's default mobile configuration; desktop uses `--preset=desktop`,
1440×1000 and device scale factor 1. All four categories are requested. Each
child has a 180-second timeout; nonzero exit fails the runner. An unknown
`V2_LH_CASE` fails instead of producing an empty run.

`lighthouse-<label>-run.json` and its `.run.json` sidecar identify the current
RUNNING/PASS/FAIL lifecycle; the successful receipt lists completed cases,
per-case and total allowed HTTP proxy request counts, and blocked requests.
Each case must produce at least one allowed proxy request before it can pass;
a successful Lighthouse exit without proxy traffic fails the run as unverified.
Proxy shutdown destroys both incoming sockets and active outgoing requests,
including fixture responses that stall after the request body has completed.
A disconnected downstream client also destroys its outgoing request. Never use
reports left by an earlier run when this
receipt is failed or incomplete. The proxy changes the measurement path relative
to the original ignored runner. Establish matching repeated baselines under the
same proxy before attributing small timing differences to theme changes.

These are synthetic local Lighthouse measurements, not field Core Web Vitals,
live traffic or staging optimizer certification. Preserve full reports, exact
build/fixture/environment and every repeated measurement. The runner checks
process completion; it does not impose score/LCP/CLS budgets or grant visual
approval. Compare equivalent cases serially and disclose errors or missing
coverage.

`inventory-final.cjs` uses fresh page contexts. Earlier baseline resource
inventories may have reused warm contexts or captured different windows. Never
subtract a fresh-context final inventory from a cached baseline and call it a
measured byte saving; compare equivalent fresh inventories, or label the
baselines' cache/procedure difference. Source/minified file sizes, decoded
response bytes, transfer bytes, and Lighthouse metrics are different
measurements.

## Maintenance and verification

The promotion was formatted with an already installed Prettier 3.9.6. That
formatter is not a runtime dependency. Keep edits inside this directory,
preserve the native product/state assertions, and request independent source
review before using changed helpers as release evidence.

Syntax checks do not launch browsers:

```bash
for helper in tools/v2-runtime/phase3b-browser/*.cjs; do
  node --check "$helper" || exit 1
done
```

The initial promotion passed syntax and runner AST-preservation checks. The
subsequent review repair adds lifecycle bookkeeping, direct API redirect checks,
and a Lighthouse origin proxy while preserving the original primary assertions.
Run focused support tests without starting WordPress, Chromium or Lighthouse:

```bash
node --test tools/v2-runtime/phase3b-browser/support.test.cjs
```

These tests use temporary files and isolated loopback HTTP servers. The promoted
browser helpers subsequently completed the final responsive/static, native
commerce, gallery, collections, Home, Quick View and resource-inventory runs.
The isolated five-case Lighthouse baseline and two final runs also completed;
see the phase browser/performance certification records for scope and exclusions.
Existing dependency lock entries remain unchanged. Passing assertions or
producing screenshots does not establish founder approval, live deployment
readiness or full-site accessibility compliance.
