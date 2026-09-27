> SUPERSEDED CANDIDATE: current packaging is documented in `tasks/current-package-6e988bac.md`. Earlier installation evidence remains historical; old split artifacts preserved outside the worktree under `/tmp/skyyrose-superseded-release-packages-20260921-2252/`.

# Final candidate split package and real clean installation

Task clean-install-b013b115. 2026-09-21 22:25–22:29 UTC. Manager/reviewer /root, executor /root/release_install. NEEDS_REVIEW; technical checks passed, independent/founder review not implied.

Candidate source ZIP SHA256 `b013b1155970287d20e0b19ada41c6d6c8a3d6a4c464e2510e3da895263fb39a`, exactly563 files. Built with existing reviewed split tooling into new `wordpress-theme/skyyrose-flagship-2/dist-marketplace-2.4.4-b013b115/`, preserving prior candidate and all unrelated changes.

- Core ZIP SHA256 `5d57577dcef70cd50f2d515da640d9b47160aeddf96ce21b8f19c1904852c7c3`,178 files.
- Required media ZIP SHA256 `f821432712b1319fe25ca6ccba66a1f24f79ad9552277711d45116a9098bb911`,385 files unchanged.
- Release descriptor SHA256 `2d8f2c27a70a7e835e3877ea6dfb342f440324a73bf1bb5c94b831e0fe69cc8c`.

Fresh real WordPress7.1.1, WooCommerce11.1.1, PHP8.5.6, MariaDB11.4 installation under `/tmp/skyyrose-clean-b013b115/site`, separate new `skyyrose_b013b115` schema in existing test container, separate localhost18884 server. Did not modify parent18883 site or symlink, parent schema, staging, production, catalog, or assets. Authentication external NOT_APPLICABLE; synthetic local admin only, generated password redacted. Existing test container kept running for parent.

Executed core install, Woo activation, baseline TwentyTwentyFive install, unzip delivered core, delivered media installer with pinned descriptor, SkyyRose activation, disable default Woo coming-soon on isolated site only. Verified all563 installed hashes/lengths, zero mismatches.

Final Playwright Chromium checks home, shop, cart, account each at1440×900 and390×900: eight HTTP200/expectedH1/nooverflow/noJSerror/noHTTP>=400 checks passed. Eight screenshots retained. Initial reused old `Skyy Rose` H1 assertion failed because this candidate's `template-parts/home/editorial-hero.php:21` explicitly renders `Luxury Grows from Concrete.` Initial failed expectation retained in `browser-smoke-initial-stale-heading.json`, current source-backed assertion rerun passed. No candidate edit to satisfy test.

Rollback activated TwentyTwentyFive baseline, moved full candidate aside, restored installer core backup to original path; all178 restored core hashes match, baseline homepage HTTP200. Core-only rollback is NOT complete SkyyRose; do not reactivate without required media. Local18884 PHP server stopped after acceptance; shared MariaDB container untouched.

Evidence `tasks/evidence/clean-install-b013b115/`: setup/install logs, exact payload check, initial/final browser JSON, rollback checks, eight screenshots, SHA inventory. Correct reproduced example: verify563 bytes and actual WordPress activation/render; illustrative incorrect example: reuse558-file prior candidate proof or accept homepage stale expectedH1 without reconciling current source. Correction performed: new clean install/new source-specific evidence and preserved failed expectation.

Limits: empty catalog, no orders/payment/tax/import/export/email testing. Not marketplace licensing certification or deployment authorization. Canonical fashion-release-evidence/fashion-e2e-task-execution skill context remains as recorded in earlier clean-install report; no new skill adoption or package tool edits. No claim full independent visual certification from this smoke. PHP deprecation reporting suppressed for known WP-CLI8.5 notices; other error classes enabled.
