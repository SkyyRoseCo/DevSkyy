# Accessibility remediation and code review — 2026-09-21

Scope: address the confirmed findings from `tasks/a11y-all-pages-20260921.md` in the active V2 theme, review the resulting patch independently, then verify the authorized staging update. Production is excluded.

Baseline: `/tmp/skyyrose-a11y-fixes-20260921/baseline/`, captured before this task's edits. The existing worktree contains earlier launch/hero changes; review must compare against this baseline rather than attributing the entire dirty worktree to accessibility remediation.

Required outcomes:

1. Small Love Hurts text reaches the automated 4.5:1 minimum while decorative brand treatments remain intact.
2. Journal media links have accessible names or are absent when there is no media.
3. Scene product navigation and collection story regions have distinguishable accessible names.
4. Jetpack sharing markup no longer creates skipped heading levels; sharing remains usable.
5. Post comments live inside a landmark.
6. The homepage film has valid group semantics.
7. Footer link targets remain usable when the target-size token is unavailable.

Independent pre-fix footer fault injection: 15 visible footer links measure44px normally but20.46875px when `--sr2-target-size` is set to its guaranteed-invalid initial value. Evidence: `/tmp/skyyrose-a11y-fixes-20260921/footer-before.json`. This reproduces a missing-token weakness; it does not establish the historical cause of the intermittent staging observation.

Product registry projection check PASS in the canonical main checkout. No product facts or image bindings are in scope.

## Implementation and independent review

Implemented all seven outcomes in eight source files, rebuilding CSS and translation outputs. The independent review caught incomplete contrast-selector coverage in the first patch; the final correction covers chapter markers, navigation numbers, and prologue/portal eyebrows. No remaining actionable code findings were identified. See `tasks/a11y-code-review-20260921.md`.

Two full-suite attempts exposed stale generated metadata: PHP runtime hashes, then the translation catalog. These were reconciled without changing product facts or scene assets. The runtime hash reconciliation also includes three earlier launch changes (`front-page.php`, `inc/global-shell.php`, `inc/performance.php`); these are existing work, not new accessibility source edits.

Independent local verification:

- 15 affected/home/footer URLs at desktop 1440px and mobile 390px: 30/30 HTTP 200 scans, zero automated axe violations, zero page overflow, zero navigation errors.
- Nine homepage profiles: 320/390/768/1440px, mobile and desktop reduced motion, mobile and desktop JavaScript disabled, and 200% text zoom. All passed; centered heading error below 0.01px.
- Footer missing-token fault injection: all 15 visible links remain 44px minimum with and without the token (before fix: 44px to 20.46875px).
- PHP lint and focused template contracts pass. Full `npm run verify` completed with exit 0; log: `tasks/evidence/a11y-remediation-20260921/verify-suite-pass.log`.

Full-suite environment: Node from `/Users/theceo/.local/bin`, Python from `/tmp/skyyrose-launch-redteam-20260921/verify-venv/bin`, and `V2_WP_FIXTURE=/tmp/skyyrose-launch-redteam-20260921/wp-fixture`. Earlier runs stopped on missing fixture configuration and missing Brotli in the main virtual environment; the existing verification environment resolved both without source changes.

Evidence copied to `tasks/evidence/a11y-remediation-20260921/`. Initial unpatched staging output under `/tmp/skyyrose-a11y-fixes-20260921/affected.*` is excluded from post-fix claims.

## Staging and package

Guarded patch applied at 2026-09-22 00:04:15 UTC (September 21, 17:04 PDT) to `https://staging-7e48-skyyrose.wpcomstaging.com`. Exact home URL and active stylesheet were checked before writing. All 14 scoped files passed before/after SHA-256 checks; remote rollback archive retained at `/tmp/skyyrose-a11y-stage-20260921/rollback-existing.tar.gz`. Object cache flush succeeded.

The fresh staging homepage passed the same nine regression profiles. Staging footer fault injection tested 17 links, all retaining 44px minimum height with and without the sizing token.

The first canonical collection response after deployment was explicitly marked CDN `STALE` and still contained the old unqualified scene headings. A fresh-query response was marked `MISS` and contained all corrected scene labels. Initial cached findings are retained and require canonical recheck; they are not evidence against the deployed source nor a final pass.

The canonical retest exposed a subsequent Jetpack `Like this` h3 on three pages after the sharing h3 was corrected. The installed `modules/likes.php:485` uses the same supported hook with context `likes`. The final callback recognizes `sharing` and `likes` and returns the format string `<p class="sd-title">%s</p>`; Jetpack escapes the label before interpolation. Seven focused cases passed, including percent literals, escaped markup, and unchanged unknown contexts. Independent follow-up review found no actionable issue. The one-file follow-up and rebuilt POT were deployed with separate guards, backups, and hash checks. All 14 final remote file hashes match current source.

The complete `npm run verify` passed with exit 0 after the Jetpack follow-up. A subsequent functional geometry check found that the new absolutely positioned one-pixel scene labels escaped their rail's containing block and expanded root horizontal scrolling. A one-line `position: relative` on `.sr2-hero-commerce__products h4` anchors those labels to their headings. Independent review approved the correction; all six injected diagnostic states restored viewport width and preserved keyboard rail scrolling. CSS source and minified output were deployed with guarded before/after hashes. The final full-suite pass after this correction is `tasks/evidence/a11y-remediation-20260921/verify-suite-containment.log`.

Marketplace package refreshed after final verification: full ZIP SHA-256 `6f69d598ce40457c9b423bca58a9b4ac777ba8b967291fad1b546973ff28f2ed`, 563 files; 178 core + 385 media in split distribution. Every ZIP member byte-matches current source. Package report: `/Users/theceo/.codex/worktrees/marketplace-split/DevSkyy/tasks/current-package-6f69d598.md`. Earlier `1886b135` and `c2f6539b` packages are superseded. No new clean-install claim is made for this package.

## Final public accessibility results

Coverage: all 80 discovered public URLs at 1440px and 390px, 160 route/viewport states. The full sweep is retained in `staging-final-all.json`; canonical affected-route retests are retained in `staging-final-affected.json`, `likes-canonical-final.json`, and `containment-canonical-confirmed.json`. Later canonical observations supersede earlier cached observations only for the same URL and viewport. The merged `final-summary.json` contains zero automated axe violations, zero navigation errors, and zero horizontal overflow observations. The intentional 404 and redirect states remain in the inventory.

Automation is not a WCAG conformance certificate. Axe incomplete checks remain for image/gradient contrast, dynamic ARIA references, labels on scroll rails and WordPress pagination, and third-party frames. Actual assistive-technology testing and authenticated account states were not added in this pass. Payment execution remains deferred to production per the user's instruction.

Final functional geometry retest on ordinary staging URLs (no CSS injection): all three collections at both 390px and 1440px have document width equal to viewport width and `window.scrollX === 0` after an attempted horizontal page scroll. Every rail retains focus and advances on ArrowRight. Evidence: `staging/overflow-deployed-settled.json`. Earlier cached failures and the injection-only diagnostic results remain preserved separately.

Status: implementation, independent code review, full local verification, guarded staging update, current package refresh, public-route accessibility scans, and collection functional geometry checks complete. Production and real payment execution are excluded.
