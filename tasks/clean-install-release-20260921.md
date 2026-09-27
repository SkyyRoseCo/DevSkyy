> SUPERSEDED CANDIDATE: current packaging is documented in `tasks/current-package-6e988bac.md`. Earlier installation evidence remains historical; old split artifacts preserved outside the worktree under `/tmp/skyyrose-superseded-release-packages-20260921-2252/`.

# Clean WordPress split-package installation and rollback

Task: clean-install-20260921. Executed 2026-09-21 21:24–21:29 UTC.
Manager: /root. Executor: /root/release_install. Independent review: /root pending.
Disposition: NEEDS_REVIEW. Bounded technical acceptance checks passed; this is not founder approval, marketplace certification, or deployment permission.

## Frozen scope and authority

Worktree base 2c7644772be1d19c9218ebfb2b980350033b83f7 with existing uncommitted package changes preserved. Installed immutable split release `dist-marketplace-2.4.4-e1a35cc9`, full source SHA256 `e1a35cc901854714f471e1256e6f2aa60a4610788c07f033a65f7cc65f67ce5d`; release descriptor SHA256 `e15da9ce8e0883b568c67c9ff52d634b1096b0037a484fb1304e2715e95079cc` pinned from prior separate report. No package code, product registry, staging, or production changed. Product authority remains current main unified registry; no product import or invented product facts.

Used canonical `fashion-release-evidence` and `fashion-e2e-task-execution` skills and verified-examples standard. Canonical main `scripts/task_control.py` was absent; scope/evidence record is `tasks/evidence/clean-install-20260921/scope.json`. Release skill's referenced local `scripts/report.sh` and `scripts/verify.sh` directory was absent; no claim those commands ran. Skill example coverage remains partial, independent of reproduced acceptance results.

## Real installed environment

Actual WordPress 7.1.1 downloaded by WP-CLI with archive MD5 verification; WooCommerce 11.1.1 downloaded from official plugin repository and activated. PHP 8.5.6; WP-CLI 2.12.0; Docker 29.8.0; MariaDB 11.4. New isolated container `skyyrose-release-mariadb-20260921`, database port bound only 127.0.0.1:13317. PHP HTTP server bound only 127.0.0.1:18883. Files under `/tmp/skyyrose-clean-install-20260921/site`. Authentication NOT_APPLICABLE to remote services; local synthetic account only, generated password redacted from retained log. No existing containers restarted or altered.

## Executed acceptance

1. `wp core download --version=7.1.1 --skip-content`, `wp config create`, `wp core install --skip-email`; WooCommerce install/activate and Twenty Twenty-Five 1.5 baseline activation succeeded.
2. Extracted core ZIP into wp-content/themes and ran delivered `install-required-media.py` with all three manifest/archive paths and independently pinned descriptor hash. Installer reconstructed full theme and retained rollback core.
3. `wp theme activate skyyrose-flagship-2` succeeded. Every one of 558 installed file hashes and lengths matched full-payload manifest after activation, zero mismatches.
4. Initial shop/cart checks exposed WooCommerce's default coming-soon page, so those were NOT counted as storefront checks. Set `woocommerce_coming_soon=no` only on this isolated install and repeated actual shop/cart smoke.
5. Local Playwright Chromium (Agent Browser absent) loaded home, shop, empty cart, account at 1440×900 and390×900. All eight final checks HTTP200, expected H1, no horizontal overflow, no pageerror, no HTTP>=400 responses observed through load/screenshot. Eight screenshots retained. Eyes-on home390 confirms theme, imagery, centered headline, CTA, guide rendering.
6. Rollback: activated previously installed Twenty Twenty-Five, moved complete candidate aside, renamed installer rollback core to original theme path. All173 restored core file hashes match core manifest; baseline homepage HTTP200 and Twenty Twenty-Five CSS identified. Required-media-free core intentionally NOT reactivated. Rollback restores pre-install core bytes plus usable baseline theme; it does not magically restore a complete SkyyRose storefront.
7. Stopped only newly created database container and local PHP server after evidence capture; files and stopped container retained for review.

## Evidence and limits

Evidence directory: `tasks/evidence/clean-install-20260921/`: redacted setup.log, install.log, payload-check.json, browser-smoke.json, rollback.log, rollback-check.json, scope.json and eight screenshots. SHA256 inventory in evidence-sha256.json.

This closes real clean-environment install/activation/empty-store render and rollback execution evidence for this exact package. It does not validate imported merchant catalog, payment, taxes, international shipping, authenticated customer account actions, emails, full visual certification, every browser, production hosting permissions, licensing, marketplace upload policies, or a shopper-friendly importer. No production/staging permission implied.

CLI emitted PHP8.5 deprecations inside WP-CLI dependencies before subsequent commands used error_reporting=24575 to suppress deprecations only. Theme PHP errors/warnings remain enabled; no fatal error observed. This is a compatibility note, not concealed theme success evidence.

Evidence-backed correct example: reconstruct pinned core+required media, verify558 hashes, activate real WordPress/WooCommerce and inspect rendered routes; REPRODUCED_LOCAL, logs above. Incorrect illustrative case: treating WooCommerce coming-soon HTTP200 or activating core without media as a successful complete shop. Correction: disable coming-soon only in isolated test, inspect expected route content, install and verify required media before activation.
