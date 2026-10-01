# Local browser evidence — 2026-10-01

The real V2 controller passed six Chromium regression cases in four completed runs (24 executions, zero failures, errors, or skips). The actual isolated WordPress/WooCommerce fixture passed desktop and mobile native shopping journeys after correcting fixture/test assumptions. There was no reproduced theme-controller defect in this scope.

This is local evidence. Authentication is **NOT_APPLICABLE**: anonymous requests to an isolated loopback fixture, with synthetic WooCommerce products and a synthetic triangle. No product-registry write, actual asset acceptance, external HTTP, order submission, payment, provider call, or deployment occurred in this browser work.

## Executed checks

| Boundary | Observed result | Receipt |
| --- | --- | --- |
| Real theme init, desktop and mobile | Incomplete selection downloads no Three; mismatched native option exposes no viewer; matching selected option mounts actual Three r170; keyboard rotation/reset/Escape work; reopening posts a fresh resolver request | `theme-ready-desktop.json`, `theme-ready-mobile.json`, PNG/HTML/trace peers |
| Real WebGL context loss | Canvas disappears; retry resolves native identity again; actual renderer recovers; later unavailable native response prevents further GLB/renderer creation | `theme-context-loss-native-unavailable.json` |
| Asset request fails then recovers | Native link remains usable; no vendor download for failed asset; retry posts fresh identity and renders after recovery | `theme-asset-recovery.json` |
| Selected option changes / root removed | Parsed geometry and material are each disposed once; no remaining canvas; native mismatch hides the stage | `theme-selection-removal-disposal.json` |
| Restored-page lifecycle handler | Synthetic persisted `pagehide` releases renderer; synthetic persisted `pageshow` mounts one controller; duplicate `pageshow` does not duplicate resolver calls/listeners | `theme-pageshow-restoration.json` |
| Actual WP/Woo native desktop and mobile | Keyboard S selection resolves variation 370 with pre-order label; Clear returns incomplete selection; M resolves 371 with “Standard order option.”; native POST add-to-cart succeeds; busy label recovers; real WooCommerce Blocks cart opens with the synthetic line | `wp-native-desktop.json`, `wp-native-mobile.json`, `wp-native.log` |
| Actual WP held/missing assets | Parent SKU `br-002` has missing published media. PDP still has native controls; there is no GLB root, empty viewer stage, canvas, GLB-controller download, or Three download | `wp-native-*-selected-m.png`, HTML and JSON peers |

Primary reusable regression: `tools/3d-commerce/test_theme_mount_browser.py`. Native fixture runner: `verify_native_wp_browser.py`. Chromium version and tested source SHA-256 values are in each JSON receipt. Those hashes bind tested bytes; they do not imply a clean committed checkout or founder acceptance.

Commands actually executed:

```sh
.venv/bin/python -m pytest tools/3d-commerce/test_theme_mount_browser.py -m integration -o addopts='' --timeout=40 --junitxml=tasks/integration-release-20261001/evidence/browser/theme-mount-junit.xml -v
.venv/bin/python tasks/integration-release-20261001/evidence/browser/verify_native_wp_browser.py
.venv/bin/black --check tools/3d-commerce/test_theme_mount_browser.py tasks/integration-release-20261001/evidence/browser/verify_native_wp_browser.py
.venv/bin/ruff check tools/3d-commerce/test_theme_mount_browser.py tasks/integration-release-20261001/evidence/browser/verify_native_wp_browser.py
```

The first run took 7.818 seconds. Three already-started repeated runs took 6.946, 6.726, and 6.762 seconds; `theme-repeat-{1,2,3}.log` and JUnit XML retain complete successful results. No flaky test was quarantined. Browser errors and external requests were zero in the successful WP desktop/mobile runs. Network interception rejects non-loopback requests before transmission.

## Fixture and harness corrections — preserved negative evidence

The integration lead prepared the existing isolated WP fixture at `http://127.0.0.1:19365`, active V2 symlink to worktree 4035, synthetic SQLite catalog, and offline external-HTTP/mail hooks. Parent 369 initially used canonical pre-order SKU `br-003`, which made both S and M pre-order options. The integration lead corrected only the fixture parent to canonical regular SKU `br-002`; S retains explicit synthetic pre-order metadata and M regular metadata. The synthetic slug still contains `br-003`. This is not a registry change or a production defect. The successful receipts record the actual synthetic product name and IDs.

Two assertion assumptions were corrected: native WooCommerce resets `variation_id` to an empty string, and this fixture uses the real WooCommerce Blocks cart rather than the classic `.woocommerce-cart-form`. The incorrect assumptions and failures remain in `wp-native-initial-assertion-gap.log` and `wp-native-classic-selector-gap.log`. They are not counted as passing executions.

A capture refresh using a string `wait_for_function` failed under the actual theme CSP (`unsafe-eval` is absent). `wp-native-csp-wait-gap.log` retains the error. The final runner preserves CSP and waits for locator stability with `click(trial=True)` before availability screenshots. `wp-native-pre-visual-settle.log` records an earlier successful run whose screenshots were subsequently refreshed after the Woo slide animation settled. `wp-before-desktop.png`, `wp-selected-s.png`, `wp-cart-anonymous.html`, and `wp-native-desktop-failure.*` are diagnostic/superseded snapshots, not the final successful fixture evidence.

## Task-specific skill example provenance

Applied `/Users/theceo/.agents/skills/e2e-testing/SKILL.md` for condition-based assertions, semantic controls, separate contexts, and browser artifacts. Read `/Users/theceo/.codex/skill-standards/verified-examples.md`. This report is a task evidence handoff, not a modification or compliance certification of the skill distribution.

**Correct example — REPRODUCED_LOCAL:** wait for actual native `data-state="valid"`, verify selected variation identity and preorder/regular availability, then exercise keyboard POST add-to-cart and assert a real successful cart line. Evidence: `verify_native_wp_browser.py`, successful `wp-native.log`, `wp-native-desktop.json` / `wp-native-mobile.json`, screenshots, DOM and trace. Expected and observed behavior agree. Authentication NOT_APPLICABLE.

**Incorrect example — OBSERVED_LOCAL_HARNESS_FAILURE:** expect a reset variation ID of exactly `0`, or expect a classic cart form on a Blocks cart. These assertions fail even when WooCommerce correctly recovers and adds the selected item. Correction: allow the native empty/zero incomplete ID, detect actual classic/Blocks cart surface, and assert the current fixture product name and real cart line. Evidence: preserved negative logs above and the corrected successful runner. Reason: assertions must verify user behavior, not an invented implementation detail. Authentication NOT_APPLICABLE.

**Incorrect claim — ILLUSTRATIVE_UNEXECUTED:** describe the synthetic triangle's `SYNTHETIC-TEST-ONLY` manifest as founder-approved product imagery, or describe dispatched lifecycle events as real browser-managed bfcache navigation. Correct wording separates synthetic acceptance/controller lifecycle evidence from real product/asset approval and actual bfcache. Sources: this test fixture and JSON receipts explicitly identify both limits. No such approval or broader claim is established.

## Remaining scope limits / refresh triggers

- Page-transition events were dispatched in the browser to exercise the real handlers. Actual browser-managed bfcache eviction/restoration was not verified.
- Accepted rendering uses a synthetic native resolver and triangle; actual WP accepted-asset rendering is untested because current manifest publication/asset gates are held.
- Full registry-hash positive responses for the new WP route remain pending projection regeneration and certification-owner review. The existing held manifest only supports dormant-path evidence.
- No checkout submission, gateway, payment, durable inventory reservation, authenticated staging/production, or deployment acceptance is established.
- Re-run affected checks after changing the tested source hashes, rebuilding browser JS, regenerating the presentation projection, changing fixture native identity, or enabling an accepted real asset.

The parent owns `.wolf` session/anatomy/bug logging and final independent review. Browser work changed only the allocated test and evidence paths; no commit was made here.
