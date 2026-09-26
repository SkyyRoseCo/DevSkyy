# Current Tasks

## ACTIVE — Registry = the only product source: fold side stores, repoint every lookup (2026-09-18)

Founder: "fold in remaining side stores" + "every workflow, pipeline, product
rendering, agent look up points to this 1 source ... everything outside of it
needs to be removed". SOT = `wordpress-theme/skyyrose-flagship/data/logo-registry.json`,
read via `skyyrose.core.product.get_product`. Branch `feat/registry-fold-side-stores`.

### Three buckets (census 2026-09-18, [repo])

| Bucket | Stores | Action |
| --- | --- | --- |
| Authored outside the registry | `render-corrections.json` (20 SKUs/41 lines), `render-keepers.json` (2), 4x `collections/<slug>/identity.json` | FOLD into registry, repoint readers, delete after founder `y` |
| Agent copy, not foldable | `skyyrose/assets/data/product-content.json` (19), `alt-text.json` (19) | Written by `skyyrose/build/gemini-content.js` from its OWN hard-coded 20-SKU table; 11/19 names differ from the registry, 5 describe a different garment; alt keys name images that are not in the repo. Gate in `get_product`, founder decides the copy |
| Generated projections | CSV, `data/dossiers/*.md`, `sot-images.json`, `v7-cards.json`, `lookbook-sot.json`, collection `sot.json`, asset manifest | KEEP — regenerated from the registry, `--check` fails closed on drift. Production PHP can only read deployed projections |
| Consumers | everything that reads the above | REPOINT to `get_product` / registry sections |

### Plan
- [x] Fold: `products[sku].corrections` (per-line authority from the file's own `_meta`: 9 lines added 2026-06-12 per Fable vision test = `AGENT_ADDED`, 32 = `FOUNDER_VERBATIM`), `products[sku].render_policy.keepers`, top-level `collections`, folded `_meta` kept verbatim; schema version 1 -> 2; `logo-registry.schema.json` extended
- [x] `get_product`: corrections + render_policy from the registry; content exact-name gate (`content.sku_mismatch`); alt text served only when its key names a registry-bound image
- [x] Repoint `scripts/oai_render` (corrections, keepers), `sot_common.load_identity`, collection generators/verifiers, drift hooks, agent prompts naming `garment-analysis.json` / side stores
- [x] Tests: value-equal round trip for every folded store; gates; readers hit the registry; guard covers JS + folded stores
- [x] `sync_product_registry.py`, asset manifest, `organize --check`, full suite, clean-checkout run, review
- [ ] Phase 4 STOP-AND-SHOW: exact deletion manifest (folded stores + legacy product stores + dead readers/writers) -> founder `y`
- [ ] Founder decision list: the 19 agent-copy records (names side by side)
- [x] Also repointed (census follow-ups): dashboard admin editor writes through the registry (CLI `python -m skyyrose.core.product_registry update`); `frontend/data/skyyrose-catalog.csv` generated as a projection (had drifted: 15 image cells + 6 branding specs); dashboard CSV parser handles multi-line cells (was minting 70 fake products); content agent, SDK commerce agent (invented products under real SKUs), and domain-agent prompts read the registry
- [x] Review REQUEST CHANGES fixed: agent-added corrections rendered under their own prompt header; authorship note corrected; alt-text writer bound to registry images; SDK canon from registry; replica pinned to the canonical registry (bug-231 recurrence #6)

## ACTIVE — Refactor scripts/deploy-theme.sh (2026-08-01)

Scope narrowed after advisor review (production deploy script, bug-107 history
with `if fn` suppressing errexit for the whole dynamic call stack). Splitting
`try_rsync()` or `verify_live()` is explicitly OUT of scope this pass:
- `verify_live()`: a RETURN trap on line 867 (`trap "rm -f '$tmpfile'" RETURN`)
  would fire early if the fetch were extracted into a helper, deleting the
  response body before the size/grep/version checks run — silent false
  "response too small" → bogus auto-rollback on a healthy deploy.
- `try_rsync()`: `tmpzip`/`remote_tar_name`/`zstd_flag`/`swap_id` cross
  section boundaries; bash 3.2 has no namerefs, so a split forces new
  globals for no real readability win.
- Neither is exercised by `--dry-run` (both return at their first line), so
  a split here is unverifiable without a real production deploy.

- [x] Dedup `RSYNC_EXCLUDES` (top-level) vs `tar_excludes` (inside
      `try_rsync()`) — two hand-maintained arrays the code itself flags as
      "keep in sync" but nothing enforces it. Extract a shared base +
      documented per-consumer-only arrays + tiny renderer functions.
      **Found and preserved (not fixed) a real divergence**: RSYNC_EXCLUDES
      excludes `package.json`/`package-lock.json`/`composer.json`/
      `composer.lock`/`webpack.config.js`/`generate_models.js` that
      tar_excludes does NOT; tar_excludes excludes `_archive`/`.serena` that
      RSYNC_EXCLUDES does not. tar/sftp is the live path (rsync protocol
      isn't supported by WP.com), so those RSYNC-only files currently ship
      to production. Reported as a finding, not silently fixed.
- [x] Split `preflight_completeness()` (~78 lines) into
      `check_version_triple()`, `check_tracked_files()`, `check_asset_floor()`
      — three independent checks, no shared state crossing boundaries, and
      `--dry-run` actually exercises this path so it's verifiable.

### Verification — all green 2026-08-02 (STOPSHOW_ACK confirmed by founder, all local/no-network)
- [x] `bash -n scripts/deploy-theme.sh` — SYNTAX OK
- [x] Rendered RSYNC_EXCLUDES/tar_excludes (sourced defs-only, main() stripped)
      vs pristine `git show HEAD` reconstruction, sorted+diffed — **IDENTICAL**
      both arrays (50 rsync / 45 tar entries incl. the live dynamic data/
      fail-closed gate, which read the same real data/ dir both times).
      Proves the dedup did not change what ships.
- [x] shellcheck (git-HEAD vs modified, `-s bash`): 0 issues both sides,
      SC-code set diff empty — no pre-existing debt to attribute, no new debt.
- [x] `bash scripts/deploy-theme.sh --dry-run` — full local pass. Confirmed
      the 3-way `preflight_completeness()` split runs correctly: "Version
      triple in sync: 2.2.3", "Tracked-file completeness: 1828/1828 on
      disk", "Critical-asset floor: 3 emblem webp, 12 woff2, mascot GLB
      present". Zero network/SSH contact (dry-run skips connectivity test).
- [x] `git diff --name-only` → exactly `scripts/deploy-theme.sh` +
      `tasks/todo.md`, nothing else. File 1124→1122 lines (net -2, despite
      adding ~35 lines of new comment/renderer code — the old file had two
      arrays' worth of duplicated `--exclude=` lines that the shared-base
      design collapsed).

### Left alone / flagged, not fixed
- Line 653 `tar $zstd_flag -cf "$tmpzip" ...` is unchecked inside
  `try_rsync()`, which runs with errexit suppressed (called as
  `if try_rsync; then`). A tar failure falls through to `du` on a missing
  file and is only caught downstream by the scp size-mismatch retry loop.
  Real bug-086/bug-107-class gap — worth its own follow-up change, not
  bundled into this refactor.

### Stop-hook catch — 2 real test failures, fixed properly (not weakened)
`tests/scripts/test_deploy_theme.py::TestExcludes::test_excludes_git` and
`::test_excludes_tests` did a static regex grep for `--exclude='.git'` /
`--exclude='tests/'` literally in the script source — broke because those
patterns moved into the `SKYY_EXCLUDE_COMMON_*` arrays. Root cause was the
test coupling to an implementation detail (literal adjacency to
`--exclude=`), not a real regression — confirmed by the same
manually-run byte-identical-array verification above. Fixed by adding
`_rendered_excludes()` (sources the script with `main "$@"` stripped,
reads the actual `RSYNC_EXCLUDES` array + `skyyrose_render_tar_excludes`
output) and rewriting the 2 tests to assert on real rendered output
instead of source text — strictly more rigorous, not a weakened check
(would now catch a typo inside the render functions that the old regex
never could). All 31 tests in the file green; ruff/isort/black clean.

## ACTIVE — Harden repo middleware (2026-08-01)

Scope: `security/security_middleware.py`, `billing/middleware.py`, `security/csp_middleware.py`,
`core/middleware/tenant.py`, `security/input_validation.py` (CSRF secret only).

Live-wiring check `[repo]`: `main_enterprise.py` mounts `billing_middleware` + `tenant_middleware`
directly (lines 452-461) and has its own inline `security_headers_middleware` / `rate_limit_middleware`
(lines 268-296). `SecurityMiddleware` and `CSPMiddleware` are never passed to `app.add_middleware()`
anywhere in the app, `mcp_service.py`, or `api/index.py` — confirmed via grep, no hit outside their own
files. Dead code today, but fully-featured-looking and importable (`create_security_middleware` factory
exists) — the auth bug below is a landmine, not yet a live exploit.

- [x] 1. `security/security_middleware.py` `_check_authentication` — was accepting ANY bearer token
      ≥10 chars as valid. FIXED: now calls `security.jwt_oauth2_auth.jwt_manager.validate_token()`,
      401 on `ExpiredSignatureError`/`InvalidTokenError`, verified `TokenPayload` stored on
      `request.state.user`. Still dead code (never mounted) — repair, not live hardening.
- [x] 2. `billing/middleware.py` entitlement check — was failing OPEN on Redis/infra error. FIXED:
      returns 503 `entitlement_check_unavailable` instead of `call_next(request)`; confirmed no
      health-check route falls under the `elite-studio|portal` creative-path regex. **This was the
      one live fix** — logged as bug recurrence below.
- [x] 3. `security/csp_middleware.py` `dispatch` — was skipping `_add_security_headers()` for all
      non-HTML responses. FIXED: baseline headers now apply to every response; only the CSP directive
      itself is skipped for non-HTML. Dead code (never mounted) — repair, not live hardening.
- [x] 4. `core/middleware/tenant.py` `_extract_jwt_claims` — algorithm allowlist widened to
      `["HS256", "HS512"]` while the issuer (`JWTConfig.algorithm`) only ever signs HS512. FIXED:
      narrowed to `["HS512"]`, and validates issuer/audience with `JWTConfig` alongside signature.
      Regression test confirms tenant context resolves from a normally-issued JWT. Corrected the
      "WITHOUT verification" docstring (signature IS verified).
      Live code (tenant_middleware is mounted) — closes real unnecessary attack surface.
- [x] 5. `security/input_validation.py` `SecurityValidator._csrf_secret` — class-level fallback was
      per-process, so multi-worker deployments without `CSRF_SECRET_KEY` reject cross-worker tokens.
      FIXED: module-level ephemeral fallback stays shared by every validator in one process; startup
      warning requires `CSRF_SECRET_KEY` for multi-worker production. Review P2 addressed: added
      cross-instance token-validation regression test. Only reachable via dead
      `SecurityMiddleware`/`APISecurityMiddleware` today — repair, not live hardening.
- [x] Verify: `rtk proxy pytest tests/test_security.py tests/test_saas_infrastructure.py -v` →
      209 passed, 2 pre-existing intentional skips, 0 failures. `ruff check` + `isort --check-only` +
      `black --check` on all 7 Python files → clean. `git diff --name-only` → scope-clean (5 hardened
      files, 2 regression-test files, plus this todo.md; pre-existing unrelated dirty files from session
      start untouched).

## ACTIVE — Commercial-Grade Theme Build, fashion-theme-architect owns it — 2026-07-27

Supersedes the 2026-07-19 sweep below (same goal, folded in — live has since moved 1.12.0→1.12.8,
so that entry's blocking/status lines are stale; its Sentinel/Lighthouse loop-until-90 mandate
carries forward into Phase 2 here rather than running standalone).

Goal: skyyrose.co storefront pushed to full commercial/production quality — real catalog, real
content (not genericized/resold), zero placeholders, full WCAG/security/performance bar, plus a
deliberate visual upgrade sourced from a screened 176-pattern shortlist. Owner agent:
**fashion-theme-architect** (`.claude/agents/fashion-theme-architect.md`, upgraded 2026-07-27 with
§2b shortlist boot + §5.2 Motion QA gate). Actual worktree: `.claude/worktrees/glimmering-crafting-shannon`
(the planned `theme-commercial-build` worktree was never created — this session executed in-place;
clean, un-diverged from origin/main on the theme path at kickoff).

**2026-07-27 execution session (today, founder deadline):** Phase 0 run — verify:theme baseline
captured, min-sync FAIL fixed (`clean-css` module was missing from `node_modules`; `npm install` +
full `npm run build` resolved it, confirmed benign single-line minifier-version drift, not content
change). wp-security baseline: 1 MEDIUM (bug-289, kids-capsule REST publish-status leak) found+fixed.
wp-code-simplifier baseline captured (dead-refs, duplicate-selector count, size-growth — see
`.wolf/memory.md` 2026-07-27 entries for detail). Phase 1 dispatched to fashion-theme-architect
(background agent `funnel-architect`), scope-cut for today: full Phase 1 funnel-to-commercial-grade
+ ONLY 4 code-extending Phase 1a patterns (luxury-cursor/product-card-holo/toast/footer-cro) + 2 font
retokens. Remaining 12 Phase 1a patterns and ALL of Phase 1b (Immersive Worlds) explicitly deferred
past today — not dropped, just sequenced after the funnel ships.

Visual source: `docs/design/visual-pattern-shortlist.md` — 176/202 patterns screened against real
brand tokens/fonts/references. 24 extend existing code (`luxury-cursor.js`, `product-card-holo.js`,
`toast.js`, `footer-cro.js`, try-on backend, Immersive Worlds) — build those first, cheapest wins.
Known landmine: "Dark Luxury Hero"/"Dark Luxury Newsletter" spec a cut font (Cormorant Garamond) —
retoken before building either.

### 2026-07-29 session — collection template revamp + base-layout prototype (this worktree)
- [x] Base-layout prototype SHIPPED: `docs/brand/design-mockups/prototype-collection-base-layout.html`
      (4 variants A–D, `?variant=`, Signature skin, real catalog/SOT data; verdict placeholder in
      `prototype-collection-base-layout.NOTES.md`). Playwright/Chrome-verified: 4 distinct trees,
      8 cards each, lockup images intact, mobile collapse OK.
- [x] Founder picked VARIANT C (scroll-world spine) 2026-07-29 → folded in + independently verified:
      NEW `template-parts/collection/film-spine.php` (sticky scroll-scrub film, 3 SOT-product hotspots,
      pin_beats captions), grid split in two with marquee-copy band, experience/lookbook/feature-scroll
      after grids, pin-narrative include dropped (kids LANDING template still consumes the part — not
      orphaned). All UNCOMMITTED.
- [ ] Delete prototype pair + OPEN-VARIANT-* launchers after founder confirms fold-in on live (or on request)
- [x] `collection-revamp` agent DONE + independently re-verified 2026-07-29: 15 patterns / 4 collections
      in NEW `assets/css/collection-motion.css` (597) + `assets/js/collection-motion.js` (303) + enqueue
      wiring + `magnetic` class on hero CTA. My re-run: php -l clean, lint:php clean, cut-fonts 0,
      reduced-motion in all 4 new files, verify:theme 2 FAILs both PRE-EXISTING (min-sync terser drift,
      file-size). Section order unchanged; heroes/film/experience intact. UNCOMMITTED.
- [x] DEPLOYED v1.13.0 to skyyrose.co 2026-07-29 (preflight 1805/1805, homepage 13/13 Scrapling PASS)
- [x] Post-deploy QA on BR/LH/SIG [live]: spine+beats+hotspots render correct real product/price/voice
      per collection, video playing, 0 console errors, hotspots real focusable links. Verified via
      Playwright computed-style+text (NOT screenshots — headless CLI --screenshot and Playwright's
      screenshot tool both failed to paint this page's video/JS layer; a tooling gap, not a site defect)
- [x] GAP CLOSED — reduced-motion live-verified via page.emulateMedia() (browser_run_code_unsafe):
      all 3 collections confirm stage collapses to static, track shrinks 2520px->~1300px, beats
      render as static stack, hotspots stay present. Matches spec.
- [x] Kids Capsule 0 spine/motion markers — CONFIRMED via 5-lens adversarial audit (workflow
      wf_2912d330-ecb): skyyrose_kc_is_launch_mode() + kc-launch routing predates cd2899fe7 by
      3.5mo (c4d00b98a, 2026-04-12); zero refs to it in cd2899fe7's diff. Pre-existing, not a
      regression, confirmed by git blame + git show, not just inferred.
- [x] Adversarial audit (5 independent lenses, ultracode workflow) on shipped v1.13.0 source —
      2 CLEAN (reduced-motion completeness: 24 effects all guarded, zero gaps beyond what was
      already checked; toggle-move claim: functionally sound, structurally rewritten not
      byte-identical as claimed, no a11y regression), 2 REAL FINDINGS fixed below, 1 confirmed above.
- [x] FIX — hotspot price text WCAG AA failure: LH accent-text (#FF5C7A) computed 3.49:1, KC
      (#B76E79) 2.73:1 against the rest-state plate composited over a bright video frame (both
      below 4.5:1 AA). Changed `.col-film__hotspot-price` to `#fff` (matches the name span, proven
      10.37:1 worst-case). Accent identity kept on border/dot/focus-outline (non-text, no WCAG
      1.4.3 risk). File: assets/css/collection-film-spine.css.
- [x] FIX — LCP-doctrine violation: initFilmSpine()'s initial update() ran synchronously at
      DOMContentLoaded (forced layout + style writes), inside the FCP->LCP window Wave 7b exists
      to protect; not part of the interaction/8s-gated loader chain. Deferred to `load` event,
      matching the existing Kids-bounce pattern. File: assets/js/collection-motion.js.
- [x] v1.13.1 committed (functions.php/style.css/readme.txt triple bump) — both fixes verified:
      php -l clean, correct min output confirmed by content (not just presence), verify:theme same
      2 pre-existing FAILs only (min-sync terser drift, file-size — neither touches these 2 files).
      UNCOMMITTED->committed, awaiting deploy y.
- [ ] Follow-ups flagged by builder (pre-existing, NOT this session's): `.col-cta` has zero styles
      theme-wide; min-sync terser drift needs lockfile or one-time full-min rebuild commit; KC
      launch-mode ON bypasses collection-standalone assets (kids motion invisible until off); 5 inc/
      files over 800-line gate

### Phase 0 — Audit (read-only, in the new worktree, before any code changes)
- [ ] `devskyy` MCP: `serena_full_project_audit`, `serena_check_code_style`, `serena_validate_security`, `serena_find_issues` — SKIPPED today (time-boxed); wp-security + wp-code-simplifier baselines cover the same ground for this pass
- [x] `wp-security` agent pass (CSP/nonce/escaping/auth/upload/SQL) — 1 MEDIUM found+fixed (bug-289), zero CRITICAL/HIGH
- [ ] Accessibility baseline — deferred to Phase 2 Accessibility Auditor (needs-browser checks anyway, verify:theme only does static `<img alt>` count: 72 without alt, WARN not FAIL)
- [x] `npm run verify:theme` baseline — captured; min-sync FAIL fixed (npm install, npm run build); 1 pre-existing FAIL remains (file-size, 5 PHP files, out of scope today), 2 WARN (escaping, a11y)
- [x] `wp-code-simplifier` — dead-code/file-bloat baseline captured (4 dead-refs, 43 dup selectors, homepage-v2.css 1339→1993 lines)

### Phase 1a — Visual direction (informs Phase 1, doesn't block it — cheap wins can start immediately)
- [ ] Retoken the two font-landmine patterns (Dark Luxury Hero, Dark Luxury Newsletter) to Cinzel/Pinyon Script + real `#D4AF37`
- [ ] Build the 16 priority-tier patterns first (table at top of `visual-pattern-shortlist.md`) — they extend code that already exists
- [ ] Each pattern built passes Motion QA (`fashion-theme-architect.md` §5.2) before being marked done

### Phase 1b — Immersive Worlds enhancement (wp-immersive owns; NOT fashion-theme-architect — top-of-funnel storytelling, not shopping)
4 live templates: `template-immersive-black-rose.php`, `-love-hurts.php`, `-signature.php`, `-kids-capsule.php` — real, actively maintained (`assets/js/immersive.js` last touched 2026-07-23), not stale. Shortlist patterns tagged ★ "matches Immersive Worlds build" apply directly here:
- [ ] Black Rose (gothic cathedral) — Smoke/Fog Drift Background, 3D Scroll Depth Scene, Full Page 3D Scene Hero
- [ ] Love Hurts (romantic castle) — Bioluminescent Wave / Interactive Ink Drop Background, Fluid Simulation Section, Ink Bleed Text Reveal (graffiti-identity match), Retro VHS Scanline (mood-specific)
- [ ] Signature (city tour) — Sunrise/Sunset Sky Gradient Animator, Liquid Metal/Chrome Material Effect (gold token), Constellation Star Field
- [ ] Kids Capsule — Physics-Based Bouncing Logo Elements (playful register fit)
- [ ] Cross-collection: Multi-Layer Parallax Scene, Scroll-Triggered Hero w/ Sequence Frames, Scroll-Driven SVG Map Animation (Bay Area/Oakland founder-story tie-in) — any page it fits
- [ ] Each pattern still passes fashion-theme-architect.md §5.2 Motion QA (reduced-motion, cut-font grep, token grep, mobile WebGL fallback) even though wp-immersive is the builder — the gate isn't agent-specific
- [ ] `immersive-wc-bridge.js` stays untouched by this phase unless a hotspot needs a real product link — that's the one legitimate funnel crossover point, per wp-immersive's own charter

### Phase 1 — Funnel build (fashion-theme-architect owns; wp-theme-dev/wp-woocommerce/wp-catalog-sync as needed)
- [ ] Home → collection → PDP → cart → checkout → account, all templates resolve, zero white-screens
- [ ] WooCommerce wiring: add-to-cart (simple+variable), AJAX cart, mini-cart, cross-sell/upsell, real catalog data
- [ ] Real content everywhere — no lorem, no "coming soon" as final state (Kids Capsule's 0-card launch mode is documented by-design, not a gap)
- [ ] Customizer options wired so non-code reskinning is possible
- [ ] Demo import + `screenshot.png` + complete `style.css` header + README

### Phase 2 — Cross-cutting gates (dispatch in parallel once Phase 1 lands)
- [ ] `wp-security` + `security-reviewer` — two independent OWASP/CSP passes
- [ ] Accessibility Auditor — re-verify WCAG holds post-build
- [ ] `chrome-devtools` MCP `lighthouse_audit` + `performance_start_trace`/`performance_analyze_insight` — carries forward the old sweep's "every page ≥90 all categories, mobile+desktop" mandate
- [ ] `e2e-runner` (Playwright) — add-to-cart, checkout, account critical flows
- [ ] `wp-code-simplifier` — final pass after the full batch of edits

### Phase 3 — Adversarial verify (never trust the builder's own "done")
- [ ] `theme-heal-doctor` + `theme-heal-verifier` pair on anything flagged live-broken
- [ ] Independent re-run: `npm run verify:theme` fresh (not fashion-theme-architect's cached claim), `npm run lint:php`, `git diff --stat` scope check
- [ ] Reality Checker pass — default NEEDS WORK, require overwhelming proof before calling this "commercial-grade"

### Phase 4 — Docs + ship (STOP-AND-SHOW gated, not autonomous)
- [ ] `doc-updater` — codemap refresh
- [ ] `npm run deploy:dry` preview, then `npm run deploy` — exact manifest shown, wait for `y`
- [ ] `devskyy` MCP `wp_verify_live` post-deploy

---

## FOLDED IN ABOVE — WP Commercial Theme Sweep (/loop dynamic) — 2026-07-19

Goal: skyyrose.co every page Lighthouse ≥90 (all 4 categories, mobile+desktop) + commercial-grade
aesthetics (headers aligned, heroes visually sound). Award-grade finish.
Team charter: `tasks/wp-commercial-theme/team.md` (Atlas/Pixel/Bolt/Access/Sentinel).

- [x] Enumerate pages — 30 published + PDPs + 404; 18-URL set covers every distinct template (`pages.txt`)
- [x] Baseline Lighthouse sweep, mobile+desktop → `baseline/summary.csv` (zero pages ≥90 all-cat mobile)
- [x] Atlas: architecture census → `architecture-census.md` (2 live P0s found + fixed)
- [x] Pixel: visual audit → `visual-audit.md` (dossier leak, shop collapse, font bug found)
- [x] Triage + fix waves COMPLETE: Bolt (enqueue/preloads/header 637KB), Atlas (PDP LCP reveal-bug,
      cart-empty shell, 3-layer dossier exposure seal bug-273), Pixel (shop grid, Hanken sitewide,
      overlay clearance), Access (16 a11y/SEO root-cause fixes) — bug-266..274
- [x] Sweep clean: php -l ×19, lint:php, build 34/34 + .min fresh, editorial index 35/35 parity
- [x] Committed v1.12.0 (15e238068 + e812c8402 incl. newly-tracked tsrc lockup riders) + PUSHED origin
- [ ] ⛔ DEPLOY BLOCKED — permission classifier denied `deploy-theme.sh` this session. Founder:
      `STOPSHOW_ACK=1 bash scripts/deploy-theme.sh` (manifest shown in-session; report:
      `tasks/wp-commercial-theme/wave1-report.md`)
- [ ] AUTO-RESUMES on live=1.12.0 (loop probes every ~30 min): Sentinel fresh Lighthouse 18 URLs +
      dossier-404 check + dequeue risk spots; Pixel Playwright per-fix harness
- [ ] Loop until every page ≥90 all categories (cart/checkout SEO exempt by design) + visual pass;
      final 30-page confirmation sweep. Founder decision queue in wave1-report.md §3

## DONE — golden-fixture CI wiring for character_pipeline, spec DoD #2 (2026-07-10)

Plan-mode task (2 Explore agents + 1 Plan agent dispatched first). Built
`scripts/prepare_character_pipeline_fixture.py`, derived a real 2.98MB fixture from the actual
Love Hurts Girl Blender export, wrote `tests/character_pipeline/test_love_hurts_girl_golden.py`
(golden-path + corruption/mutation tests, no pytest marker — CI's `pytest tests/` has no `-m`
override so a marked test would silently never run). Running the pipeline against real geometry
for the first time immediately surfaced bug-226 (Head's oversized radius had no region-mask gate,
causing 6cm chest-vertex displacement under a pure Head rotation) — fixed in `weights.py`, not
worked around. Also resolved a real crotch_y auto-detection unreliability on clothed-mesh noise via
the existing `character.yaml` override mechanism (not a hack — that's what it's for). 26/26 tests
green, ruff+mypy clean, negative test confirmed non-vacuous (disabled injection, confirmed it fails).

- [x] `scripts/prepare_character_pipeline_fixture.py` — rerunnable fixture-prep + real-number observability script
- [x] `tests/character_pipeline/fixtures/love_hurts_girl_static.glb` — committed real mesh fixture (no LFS, matches `tests/fixtures/qc_ground_truth/` precedent)
- [x] `tests/character_pipeline/test_love_hurts_girl_golden.py` — golden-path + corruption tests
- [x] `weights.py` bug-226 fix — Head/HeadTop_End region-gated to `y >= neck_y`
- [x] Verification: full suite green, ruff+mypy clean, negative test proven non-vacuous

## DONE — CHARACTER_PIPELINE_SPEC.md → skyyrose/character_pipeline/ (2026-07-10)

11 modules, 2794 lines, 24 pytest unit tests + 3 one-off e2e smoke scripts (all green), ruff+mypy
clean. Deviations from literal spec text, all deliberate and documented in-file: FBX2glTF has no
darwin-arm64 release upstream (used darwin-x64, runs under Rosetta 2); `devskyy-character` is a new
console script, not folded into the existing `devskyy` (that's `main_enterprise:main`, unrelated).
3 real bugs found+fixed this session, logged as bug-223/224/225. Golden-fixture CI wiring against
the real Love Hurts Girl asset (spec DoD #2) is a flagged follow-up — that binary wasn't available
this session.

Port validated reference implementation (clean_static.py, rig_girl.py, widget_template.html,
inspector_template.html — the scripts that shipped Love Hurts Girl) into the spec's clean
8-workstream package. numpy/scipy/pygltflib/Pillow already in pyproject.toml — zero new deps.

- [x] `_glb_io.py` — shared `read_accessor()` + `GLBWriter` (dedupes the `add()` chunk-accumulator
      boilerplate that's copy-pasted across both reference scripts)
- [x] `config.py` — constants registry (verbatim §3 table) + `character.yaml` loader + `CharacterConfig`
- [x] `convert.py` (WS1) — FBX/GLB ingest, pre-flight rigged/texture scan, vendored `FBX2glTF` invoke
- [x] `clean.py` (WS2) — transform bake generalized to read actual node TRS (delta 1: no hardcoded
      S=100/-90°X), ground+center, PBR fix, dead-emissive drop, texture re-encode, degenerate gate
- [x] `landmarks.py` (WS3a) — delta 1: height-normalized slice-clustering auto-detect (fractional
      bands derived from reference measurements) + `character.yaml` override layer
- [x] `skeleton.py` (WS3b) — 25-joint mixamorig builder off `Landmarks`, column-major IBM
- [x] `segment.py` (WS4) — geodesic Dijkstra seg + arm-tube filter + iterative weld-cut (the
      "204 welded bridge triangles" algorithm), shoulder-relative cut gate instead of the reference's
      absolute `y<1.05` (which only worked because it matched one model's shoulder height)
- [x] `weights.py` (WS5) — radius-normalized capsule LBS weights + region masks, radii scaled by
      `target_height`
- [x] `verify.py` (WS6, hard gate) — delta 3: formalize wave_R/wave_L/bow/look as named `PoseGate`s,
      pure-numpy FK, matplotlib QA renders, round-trip/texture-last/hash asserts, `report.json`,
      nonzero exit on failure
- [x] `package.py` (WS7) — surgical texture-swap (byte-splice, never full rebuild), `@@PLACEHOLDER@@`
      template assembly + `node --check` gate, base64 + `widget-external.html` variants
- [x] `cli.py` (WS8) — `build`/`verify` subcommands; new `devskyy-character` console script (existing
      `devskyy` entry is `main_enterprise:main`, a FastAPI dev-launcher — reusing that name would collide)
- [x] `templates/widget.html`, `templates/inspector.html` — copied verbatim, already match spec's
      WS7.3 contract exactly (confirmed by full read)
- [x] `pyproject.toml` — add `"skyyrose*"` to `packages.find.include` (currently absent — needed for
      the new console script to resolve), register `devskyy-character`
- [x] `tests/character_pipeline/` — unit tests on synthetic fixtures (small dumbbell mesh, 2-bone
      skinned cube) for `_glb_io`, `segment`, `weights`, `verify` FK math. Real golden-fixture CI
      wiring against the actual Love Hurts Girl asset (spec DoD #2) is a separate follow-up — that
      binary isn't available in this session.
- [x] STOP-AND-SHOW before fetching: vendored `FBX2glTF` v0.9.7 binary (linux-x64+darwin-arm64) and
      three.js r128 `three.min.js`/`GLTFLoader.js`/`OrbitControls.js` — no local copy exists in-repo
      (theme loads three.js via CDN ESM, not a vendorable UMD build). Code fails loudly with a
      setup-script pointer until fetched; mirrors existing `vendor/README.md` convention.
## DONE — Robust Stop test-gate hook (2026-07-12)

Stop-hook pytest gate false-blocked twice in one session: a load-timeout flake
(`test_ml_optional` — 60s import guard trips under machine saturation; import itself
succeeds ~7s unloaded) and a concurrent-session mid-edit race (`content_agent` fixture
caught half-edited → `tmp_path` NameError). Both passed clean on re-run.

- [x] Extracted the inline `.claude/settings.json` pytest one-liner → `.claude/hooks/stop-test-gate.sh`
- [x] Retry-on-failure: on a red run, settle 5s then re-run `pytest --last-failed`; block (exit 2)
      ONLY if the failure reproduces. Kills both false-block modes; never masks a real failure.
- [x] Verified: decision logic green→0 / flake→0 / real-fail→2; `bash -n` clean; `--last-failed` valid.
- [ ] **FOLLOW-UP (real backend task, founder-gated):** `import main_enterprise` makes blocking
      connect attempts at import time (DB via `api/gdpr.py`, `skyyrose.elite_studio.queue.consumer`,
      `mcp_tools.http_mount`) → ~7s unloaded vs ~62s under load. Make them lazy / short-timeout so the
      import is fast + non-blocking (the in-memory fallback already exists — it just runs AFTER a slow
      connect timeout). This is the ROOT fix for the `ml_optional` flake; the retry only papers over it.

## ACTIVE — Build the Signature Collection (all assets) — 2026-07-11

Founder: emblem + bespoke font + page pass. Sequence each; gate every money/deploy step. 3 scouts running.

> ⏸ Queued: bespoke BR Script + LH Graffiti fonts committed (`13c61beda`, v1.10.3) with clean-worktree
> deploy manifest shown — awaiting founder `y`. Sits atop the v1.10.2 deploy train (also gated, line below).

- [ ] **Track A — Signature font** (replace Pinyon Script): feasibility pending scout → build if autonomous,
      STOP-AND-SHOW if paid glyph gen. Wire like BR/LH (fonts.css/identity/sot/typography/design-tokens/.impeccable).
- [ ] **Track B — Signature emblem** (gold star-rose): source pending scout → compose from existing gold-rose+star
      (zero-paid) OR STOP-AND-SHOW paid render. Output `assets/images/emblems/signature-emblem.webp`; auto-wires via
      file-gated `.col-hero__emblem`. Eyes-on pixels before it touches the site.
- [ ] **Track C — Signature page pass**: autonomous copy/layout/imagery/experience per .impeccable.md; gate any new
      render (money) or WooCommerce/live-data write; verify all 12 SIG products resolve via SOT.
- [ ] Batch to ONE gated deploy (no drip); bundle with the queued font deploy if founder wants.

## ACTIVE — WS7 launch-night wiring + gap closure (2026-07-11)

Spec: `.planning/SKYYROSE_LAUNCH_NIGHT_SPEC_V2.html` (committed to main 2026-07-11).
This workstream previously had NO todo.md entry — tracked only in project memory. Register created
during the 2026-07-11 gap-closure sweep; full detail in memory `project_structural_remediation_2026_07_05`.

- [x] Sync: main==origin/main; launch spec + typography previews committed; feeds/ + tasks/assets/ gitignored
- [x] bug-222 /cart/ + /checkout/ shell restored (template_include override, commit 940665873, v1.10.2)
- [x] HG-5 skip links — verified ALREADY CLOSED (live audit 99/0, 2026-07-11)
- [x] WS5.4 root fix — session cookie now set at guest wishlist write time, not every pageview (f75c92cb4)
- [x] C5 /analytics/events shared-key gate — __return_true removed from write route (cdb76a951)
- [x] C6 wiring_audit.py FIRST RUN: 8/8 read-only PASS (after .env WP_APP_PASSWORD quoting fix +
      audit scope/pattern fixes). Write round-trips still gated (--write + STOPSHOW_ACK=1).
- [x] WS4.7 orphan categorization DONE 2026-07-11 (founder-approved): lh-005→love-hurts,
      sg-015→signature. Live verified: 33/33 in collections, uncategorized=0.
- [x] C4 webhooks REGISTERED 2026-07-11 (founder-approved): 5 topics active →
      https://www.devskyy.app/api/webhooks/woocommerce (product.create/update/delete, order.create/update).
- [x] Cookie-policy duplicate <h1> removed from page 10143 body (founder-approved) —
      live renders exactly one h1.
- [x] wiring_audit.py --write: **10/10 PASS** 2026-07-11 (after fixing the audit's settings
      round-trip to use whitelisted fastapi_url — endpoint whitelist was correct, probe was wrong).
- [ ] ⛔ GATED (founder y — NOT yet approved): theme deploy train v1.10.2 — 6 committed fixes
      (cart shell, session cookie, analytics key, policy titles, lockup CLS, PDP size-chip)
      inert on live until deployed.
- [ ] FOUNDER DECISION: dashboard font migration (spec C5: Fraunces/Archivo/JetBrains vs current
      Playfair/Cormorant/Space Mono in frontend/lib/fonts.ts) — spec cites nonexistent skyyrose-tokens.css;
      brand canon cut Playfair/Cormorant 2026-07-10. Needs a call, then execution.
- [ ] FOUNDER/OPS: `agents-manager` REST namespace live on production but in NO repo source — identify
      what serves it (plugin? leftover deploy?), bring under version control or retire.
- [ ] FOUNDER: HG-3 real pre-order ship window for /faq/; HG-1 TikTok/X handle confirm.
- [ ] Spec DoD amendment needed: "zero __return_true on write routes" now satisfied; consider
      documenting the shared-key analytics exemption model in the spec.
- [x] Go-live sweep reconcile: 9/11 theme fixes hold; 2 regressions (policy bare <title>,
      scene.php lockup CLS heights) re-fixed 2026-07-11
- [ ] WP-ADMIN (not code): site title "The Skyy Rose Collection"→"SkyyRose"; Jetpack SEO Tools
      duplicate meta-description toggle (now SITEWIDE, worse than register said); /kids-capsule/
      → /collections/kids-capsule/ redirect rule (live 404 today)
- [ ] ⛔ GATED (live content edit): cookie-policy page body carries its own <h1> duplicating the
      template's — remove via wp-admin editor
- [ ] IMAGERY (founder-gated, paid): KC hero brand-script lockup asset (Grand Hotel per canon) —
      scene.php still falls back to sr-monogram
- [ ] PERF BACKLOG: homepage stylesheet count grew 37→40
- [ ] SDK regressions (2026-04-15 consolidation kept the UNFIXED duplicate): 4 fixes being
      re-applied to sdk/python/agent_sdk — worker await-crash is production-critical
      (docker-compose runs agent_sdk.worker)

## DONE — Tier-3 stub-body wires → real agent delegation (2026-06-28)

Replace 4 hardcoded-fixture handler bodies with real agent delegation. TDD, tests green, scope-clean.
Wiring is autonomous-safe; runtime paid/prod gates stay intact (tests MUST mock paid/prod calls).
Register: `tasks/wiring-gaps-register.md` (T3-1..T3-4) — but 3 of its 4 specifics were wrong; wired from verified source.

- [x] **T3-1 code/scan** — DONE. Verified 5/5 via rtk; path-injection guard; `asyncio.to_thread`. — `api/v1/code.py:170-194` mock `ScanIssue` list → `CodeSecurityAnalyzer.analyze_directory()`
      (real source SAST, `security/code_analysis.py`; NOT the register's dependency-CVE scanner). Map
      `SecurityFinding{file_path,line_number,severity,category,recommendation}` → `ScanIssue`. Fix MCP route
      `mcp_tools/tools/infrastructure.py:163` `"scanner/scan"`→`"code/scan"`.
- [x] **T3-2 commerce/bulk** — DONE. Wire 3/3; bug-165 (CommerceAgent WC integration) FIXED full per founder: alias + `WordPressClient.from_env()` + lifecycle reconcile + dashboard.py 3 sites. 231 passed, no regression. — `api/v1/commerce.py:156-182,308-340` mock loops → `CommerceAgent` (init pattern proven
      at `commerce.py:467`). create→`sync_product_to_woocommerce`, update→`update_woocommerce_product(product_id,updates)`,
      delete→honest (no agent method; WC client or unsupported-result). Fix MCP endpoint_map `ecommerce.py:133-137`→`"commerce/products/bulk"`.
- [x] **T3-3 3D text/image-to-3D** — DONE. 4/4 via rtk; async BackgroundTask + status endpoint; +my fixes (SSRF follow_redirects=False, close() comment). — `api/v1/media.py:173-196,255-278` fake URLs → `TripoAssetAgent` (real class name;
      generators `_tool_generate_from_text`/`_tool_generate_from_image` → `GenerationResult`; PAID at runtime → MOCK in tests).
      Fix MCP routes `threed.py:149,203` → `media/3d/generate/text`, `media/3d/generate/image`.
- [x] **T3-4 theme deploy** — DONE. 3/3 via rtk (subprocess MOCKED, never ran real deploy); `create_subprocess_exec`+600s timeout; non-prod→`--dry-run`. — `api/v1/wordpress_theme.py:46-56` `success=False` stub → `subprocess.run(["bash","scripts/deploy-theme.sh",...])`
      (flag-driven: `--dry-run`/`--with-maintenance`, NOT env). non-prod env→`--dry-run`. PROD-touching at runtime → MOCK subprocess in tests, never run live.

### Verify (main thread, after agents — never on a subagent's word)
- [x] Re-run pytest for all 4 modules myself · `git diff --name-only` scope-clean · ruff/black/isort clean on touched files
- [x] Update buglog/anatomy/cerebrum/memory; mark register items done; report

## ACTIVE — Phase 2 `skyyrose/core/embeddings/` package (Track E) — 2026-06-24

Branch `feat/embeddings-phase2` off `origin/main`. Spec: `docs/superpowers/specs/2026-06-22-embeddings-reframe-design.md` §Track E.
Base: Phase 0 (frozen contract + golden gate) IS in main; Phase 1 (Track P) is NOT (open PR #604) — Track E is orthogonal.

**Approach (decided):** Shim migration — `skyyrose/core/clip_embedder.py` + `dino_embedder.py` become thin facades over the new
package → zero consumer churn (6 in-repo sites + `capability.py` importlib string-probe + 2 scripts unchanged). `store.py`
(sqlite LocalVectorStore) DEFERRED — no current consumer (YAGNI); E-store covered by atomic-centroid + space-guard on the
live `.npz` path. All tests model-free (CI red on HF Hub 429 — never download a model in a test).

Foundation: [x] errors.py [x] device.py [x] space.py [x] config.py [x] base.py
Encoders:   [x] clip.py [x] dino.py [x] cache.py
Wire:       [x] embedding_gate (E-encoder-gate) [x] brand_centroid (E-space/E-store) [x] shims
Migrate:    [x] repoint visual_product_recognition [x] delete scripts/image_embeddings (E-delete)
Verify:     [x] new unit suite green (50) [x] Phase-0 golden+contract still green (11) [x] elite_studio CI-mode green (185) + lint clean
            [~] adversarial 5-lens review running (wf_5bc8945c-3d3) → triage + fix → commit
DEFER:      store.py (sqlite LocalVectorStore) — no consumer, YAGNI; E-store covered by atomic centroid + dim guard.

## ACTIVE — MCP over HTTP, connected to dashboard + WordPress (2026-06-15)

Goal: expose the devskyy MCP (tool count computed at runtime — see mcp_service.py
/health) over authenticated HTTP so the Next.js
dashboard (AI console) and skyyrose.co (wp-admin buttons) can both consume it, AND
the tools can read/act on those surfaces' data. Branch `feat/mcp-http-surfaces`.
Architecture: mount the FastMCP `streamable_http_app()` into `main_enterprise` at
`/mcp` (→ `api.devskyy.app/mcp/`); reuse the backend both surfaces already call.

- [x] P0 Research — Context7 confirmed `app.mount("/mcp", mcp.streamable_http_app())` +
      `session_manager.run()` in lifespan + Bearer auth. SDK FastMCP already has the methods.
- [x] P1 HTTP mount — `api/mcp_mount.py` + lifespan wrap + mount in main_enterprise.
      Fixed double-path (`streamable_http_path="/"`). Verified: `/mcp/` → 200 + session.
- [x] P2 Auth — `BearerAuthMiddleware` (MCP_SERVICE_TOKEN). Verified 401 without/wrong token,
      200 with. Enforced when token set; warns if unset in non-dev.
- [x] P3a fly.toml pinned to 1 always-on machine (commit 624631520); MCP_SERVICE_TOKEN generated.
- [x] P3b Backend deploy — LIVE at https://devskyy-api.fly.dev/mcp/ (Fly app `devskyy-api`, 1 machine,
      MCP_SERVICE_TOKEN set). Pivoted from the torch monolith to a SLIM standalone MCP service
      (`mcp_service.py` + `Dockerfile.mcp`, no ML stack) — the full main_enterprise image is a
      ~6-10GB torch monolith with a broken Dockerfile + unsatisfiable [all] dep graph. Verified live:
      initialize→200+Mcp-Session-Id, tools/list→42 tools (stale point-in-time reading;
      live count is now served by /health's tool_count field), 401 w/o Bearer, foreign Host→421.
      Commit f08691b6b. Follow-up: `fly secrets set WC_CONSUMER_KEY/SECRET` to make WC tools callable.
- [x] P4 Dashboard AI console — `app/api/mcp` NextAuth-gated proxy (token server-side) + `app/admin/mcp`
      console UI; @modelcontextprotocol/sdk added (commit 8977cc5c1). type-check+lint+build green.
      Vercel deploy ⚠️ PENDING.
- [x] P5 WP-admin console — `inc/mcp-bridge.php` (PHP streamable-HTTP client: initialize →
      notifications/initialized → tools/call, SSE-frame parse, session DELETE teardown;
      SSRF-guarded via `skyyrose_see_is_safe_url`; Bearer from SKYYROSE_MCP_TOKEN const/env/option).
      Tools → DevSkyy MCP page + `assets/js/admin-mcp-console.js` (createElement only, no innerHTML),
      nonce + `manage_options` gated AJAX relay. Wired in functions.php after fastapi-client.php.
      WC catalog/orders read = ALREADY covered by `mcp_tools/tools/wc_client.py`
      (`wc_get_products`/`wc_get_product`/`wc_get_orders`) — no redundant resources built.
      php -l + PHPCS clean. Deploy skyyrose.co ⚠️ PENDING (gate on backend live first).
- [x] P6 docs — `docs/mcp-http-architecture.md` covers the mount, Bearer auth, both consumer
      surfaces (dashboard proxy + WP bridge), env var matrix, and failure modes (401/421).
      `scripts/verify-mcp-surfaces.sh` is a read-only E2E verifier (initialize -> tools/list,
      401-without-token) — CI-safe (SKIPPED + exit 0 when MCP_URL/MCP_SERVICE_TOKEN unset).
      Live E2E (both surfaces invoking a tool against production /mcp) is prepared — pending
      gated go-live, see `tasks/mcp-golive-manifest.md`.

  Remaining wiring (backend now LIVE at https://devskyy-api.fly.dev/mcp/) — exact gated
  commands + verify steps are in `tasks/mcp-golive-manifest.md`:
  - P4 Vercel env: MCP_URL + MCP_SERVICE_TOKEN (Production), redeploy frontend. ⚠️
  - P5 WP deploy: SKYYROSE_MCP_URL + SKYYROSE_MCP_TOKEN (option/wp-config const), then
    `bash scripts/deploy-theme.sh` if needed. ⚠️
  - DNS (optional, cleaner): point api.devskyy.app → Fly, then the committed default URLs
    work without per-surface overrides.
  - WC tools: `fly secrets set WC_CONSUMER_KEY/WC_CONSUMER_SECRET -a devskyy-api`.
  - Post every step: `bash scripts/verify-mcp-surfaces.sh` (MCP_URL/MCP_SERVICE_TOKEN exported)
    to confirm the surface is still healthy.

## ACTIVE — Consolidation Sweep (2026-06-10 standup plan)

Source: `~/.claude-mem/STANDUP.md` (10-agent standup; all decisions founder-approved 2026-06-10).
Context: org Actions block = ALL PR checks red regardless of code. Gate every merge on
LOCAL verification, not GitHub CI. Execute via `/do`. Sequenced by dependency.

### Phase 1 — Independent quick lands — DONE 2026-06-10
- [x] 1.1 Merge PR #537 — gate 20/20 tests green; merged `9169db1d`
- [x] 1.2 Merge PR #539 — php -l + ast + import gates clean; merged `dfe5254c`
- [x] 1.3 Land fix/ci-bandit-debt (consolidated assets + hook fix; PR #546)
      [this session: fad555a50 landed via PR #543; PR #546 = parallel session's follow-up, still OPEN]
- [x] 1.4 Close PR #501 — CLOSED with superseded comment

### Phase 2 — oai_render pipeline — DONE 2026-06-10 (with recovery)
- [x] 2.1 Pushed 409187921 → feat/oai-render-pipeline. CORRECTION: commit order was inverted —
      2b2ab382a was the TIP (child of 409187921), not parent; it was stranded by the push.
- [x] 2.2 PR #540 merged `948b59b25` (51/51 tests + dry-run smoke: 75 imgs/30 SKUs, 3 excluded).
      Stranded tip recovered via PR #544, merged `0f0ea0c43`, 52/52 tests. Both SHAs verified
      ancestors of origin/main. Lesson logged as buglog bug-124 (push tips, not assumed parents).
- [x] 2.3 render-fixes worktree + feat/legal-policies-shipping-sync branch deleted;
      be3a072c (.claude/-deletion hazard) now unreachable.

### Phase 3 — WP theme — DONE/DEFERRED 2026-06-10
- [x] 3.1 PR #534 CLOSED; partition B re-cut as PR #545, merged `6fb5350d4`.
      php -l clean; buglog merged additively (4 entries renumbered bug-120..123); webps carried.
- [x] 3.2 DEFERRED (founder call 2026-06-10): refactor/wp-template-consolidation is a stale
      reference snapshot (own commit message says "not mergeable code"); 9 main commits rewrote
      the 4 landing templates since branch point — merging would wipe brand/a11y/perf work.
      Branch kept as pattern reference. Redo on current main when templates stabilize.
- [x] 3.3 Not triggered: #545 = docblocks/artifacts only, no CSS/JS source changes this sweep.
      NOTE: #539's PDP size-chip JS (min rebuilt in-branch) is on main but NOT yet deployed
      to skyyrose.co — rides the next deploy train.

### Phase 4 — Holds + hygiene
- [x] 4.1 HOLD wip/codex-homepage-v2 (51ee222a2). Trigger: OAI render batch re-run + validated
      (sections hard-reference deleted render image paths). Then cherry-pick onto theme branch.
- [x] 4.2 HOLD PR #538 (pipeline3d draft). Trigger: founder picks 3D path (tasks/3d-pipeline-handoff.md).
- [x] 4.3 Main-checkout cleanup — DONE 2026-06-12 (landed on main via 525c6799a):
      frontend/.next.stale-20260609/ (252MB) DELETED (commit 76acaa98e);
      claude-mem CLAUDE.md churn ROOT-FIXED — redirected to gitignored CLAUDE.local.md
      (FOLDER_USE_LOCAL_MD=true) + worker restarted; 265 stub CLAUDE.md deleted, 77
      stripped, 0 blocks left tracked (commit 525c6799a); prototypes/ gitignored.
      Doctrine: docs/memory-architecture.html. clip bug-128 + theme v1.6.2 also landed.

**Done when:** main = #537 + #539 + #540(+2 commits) + #534-partition-B + wp-templates + fad555a50;
#501 + #534 closed; render-fixes worktree gone; every merge locally verified.

---

## ACTIVE — 3D products on skyyrose.co PDPs (2026-05-31)

**Decisions (founder):** Balanced KTX2+meshopt · Cloudflare R2 hosting · PDP-only · Google `<model-viewer>`.
**Verified:** 33 GLBs `renders/3d/{sku}.glb`, avg 7.5MB / ~74% textures. No viewer in theme (April mascot stripped). `.glb` not upload-allowed (only AVIF in `inc/performance.php`). PDP = `woocommerce/single-product.php`. No R2 creds / no compression tool yet.

### Phase 1 — Compress (local, no gate)
- [x] Install `gltfpack` (meshoptimizer; bundles Basis/KTX2)
- [x] Validate on br-003 (smallest): `-cc -tc`, confirm ~1–2MB + integrity
- [x] Batch all 33 → `renders/3d/web/{sku}.glb`
- [x] Report per-SKU before/after; flag non-shrinkers / degraded

### Phase 2 — Theme integration (local, deploy-gated by sweep)
- [x] Self-host `model-viewer.min.js` → `assets/js/vendor/`
- [x] `SKYYROSE_3D_CDN_BASE` constant (functions.php), empty = viewer off
- [x] Enqueue model-viewer (`is_product()` only, ES module)
- [x] Inject `<model-viewer>` in `woocommerce/single-product.php`: SKU→`{CDN_BASE}/{sku}.glb`, poster=product image, lazy, reveal=interaction, camera-controls, ar
- [x] Graceful: no GLB for SKU → render nothing
- [x] `assets/css/product-3d.css` + build `.min`
- [x] Sweep: php -l + phpcs + WP health + /wp-simplify + animation verify

### Phase 3 — R2 hosting (BLOCKED on founder; STOP-AND-SHOW on upload)
- [x] **NEEDS FOUNDER:** Cloudflare → R2 bucket `skyyrose-3d` → public (r2.dev or `cdn.skyyrose.co`) → API token
- [x] Creds → `.env.secrets` (R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET, SKYYROSE_3D_CDN_BASE)
- [x] CORS: allow `https://skyyrose.co` GET
- [x] Upload script (boto3/rclone), dry-run first → **STOP-AND-SHOW** → real upload
- [x] Set `SKYYROSE_3D_CDN_BASE` live → viewers activate

### Phase 4 — Verify live
- [x] Cache-busted PDP curl: `<model-viewer>` present + GLB 200 + correct MIME
- [x] WebGL renders desktop + mobile; poster pre-interaction
- [x] Docs + lessons + memory updated

**Order:** Phase 1+2 now (no creds). Phase 3 waits on R2. Code ships complete; 3D activates when `SKYYROSE_3D_CDN_BASE` set.

---

## Session Summary (Apr 6, 2026)

### Completed This Session
- [x] Monorepo cleanup: .gitignore gaps fixed (.agents/, .mcp.json, .aidesigner/)
- [x] 21 Python files formatted (ruff/black/isort) + 7 lint errors fixed (StrEnum, unused vars)
- [x] PR Intelligence Agent built (pr-automator.md + /pr-auto command + pr-agent.yml workflow)
- [x] PR audit dry-run completed: 42 open PRs classified, 28 actionable, 14 need review
- [x] Experience Engine Phase 1: 4 PHP theme modules (experience-engine, experience-analyzer, fastapi-client, rest-api-experience) + functions.php wired
- [x] Experience Dashboard page: frontend/app/admin/experience/page.tsx — all 5 sections built
- [x] Full dashboard audit: 18 pages analyzed, 12 production-ready, 6 need work

---

## Experience Engine — Remaining Phases

### Phase 2: Performance + Atmosphere — COMPLETE (Apr 15, 2026)
- [x] `inc/performance-guardian.php` — CLS prevention CSS, animation budget config
- [x] `assets/js/performance-guardian.js` — Animation budget manager, FPS watchdog
- [x] `assets/js/brand-atmosphere.js` — Canvas particle system per collection
- [x] `assets/css/brand-atmosphere.css` — Canvas overlay, particle container
- [x] Update `inc/enqueue.php` — register Phase 2 assets (priority 30)

### Phase 3: WooCommerce Integration — COMPLETE (Apr 15, 2026)
- [x] `assets/js/experience-analyzer.js` — IntersectionObserver views, dwell timing, click tracking, sendBeacon flush
- [x] `assets/js/smart-showcase.js` — Native <dialog> quick-view, zero-AJAX (reads card DOM), focus trap
- [x] `assets/js/micro-interactions.js` — Cart fly-to arc animation, wishlist heart burst (8 particles)
- [x] `assets/css/smart-showcase.css` — Dialog + quick-view button + cart bounce keyframe + reduced-motion
- [x] Update `inc/woocommerce.php` — skyyrose_wc_inject_product_attrs() on woocommerce_before_shop_loop_item_title
- [x] Update `inc/enqueue.php` — skyyrose_enqueue_phase3_assets() at priority 40; holo card gets data-collection + data-name + quick-view button

### Phase 4: Personalization
- [x] `inc/personalization.php` — Curated For You section, REST recommendations
- [x] `assets/js/personalization.js` — Visitor profiling, affinity scoring
- [x] `assets/css/personalization.css` — Curated For You grid
- [x] Update `inc/enqueue.php` — register Phase 4 assets

### Phase 5: Admin Dashboard (WordPress side)
- [x] `inc/admin-experience-dashboard.php` — Admin page: module status, analytics, narratives

---

## Dashboard (devskyy.app) — Gaps to Fill

### Priority 1: Settings Persistence
SHIPPED — `frontend/app/api/settings/route.ts` exists (GET/PUT, real handler);
`frontend/app/admin/settings/page.tsx` already wired per
`tasks/wiring-gaps-register.md` T2-4. This section is stale, kept for history.

### Priority 2: Tasks Page Expansion
- [x] Expand `frontend/app/admin/tasks/page.tsx` (122L) — add task list, filtering, history, status tracking
- [x] Add task creation form with type selector (content, image, deploy, general)
- [x] Show Round Table competition results inline

### Priority 3: Agents Page — Dynamic Loading
- [x] Remove hardcoded "54 agents" from `frontend/app/admin/agents/page.tsx`
- [x] Load agent list dynamically from API or file system scan
- [x] Add live status indicators (connected to actual agent health)
- [x] Expand specialized agents list (currently "+42 more agents..." placeholder)

### Priority 4: Monitoring — Real API Wiring
Backend SHIPPED — `api/v1/monitoring.py:360` `/monitoring/metrics` route,
mounted `main_enterprise.py:286`. Remaining: frontend `metrics()` client
method + `useMonitoring` wire per `tasks/wiring-gaps-register.md` T3-9
(frontend-only).

### Priority 5: Autonomous — Live Data
- [x] Wire `frontend/app/admin/autonomous/page.tsx` to selfHealingService real endpoints
- [x] Add start/stop controls for autonomous operations
- [x] Add execution history log

### Priority 6: Assets — API-Backed Gallery
- [x] Wire `frontend/app/admin/assets/page.tsx` to HuggingFace datasets API or local asset scan
- [x] Add search/filter functionality with real data
- [x] Show product image count per SKU

---

## PR Management

### Open PRs Requiring Action
- [x] PR #393: Experience Engine plugin — CLOSE with comment (pivoted to theme integration)
- [x] PR #379: skill-prompt-generator — CLOSE (functionality exists as Claude Code skills)
- [x] PR #433: cryptography 46.0.5→46.0.6 — MERGE PRIORITY (security patch)
- [x] 26 Dependabot patch/minor PRs — BATCH into pip + npm combined PRs
- [x] 8 Dependabot MAJOR PRs — review individually (vite 8.0, psutil 7.x, lucide-react 1.0)
- [x] 4 GitHub Actions MAJOR PRs — review together (artifact v7/v8, docker v6/v7)

---

## Files Over 800-Line Limit (monitor, don't split)
> Splitting CSS adds HTTP requests. These work fine in production.
- `about.css` — 1,401 lines
- `homepage-v2.css` — 1,339 lines
- `contact.css` — 1,252 lines
- `immersive.css` — 1,216 lines
- `404.css` — 1,207 lines
- `single-product.css` — 1,133 lines
- `preorder-gateway.js` — 985 lines
- `product-catalog.php` — 918 lines
- `header.css` — 811 lines
- `frontend: conversion/page.tsx` — 1,822 lines (needs component extraction)
- `frontend: huggingface/page.tsx` — 1,218 lines (needs component extraction)

---

## Hero Images Needed (1-shot fix batch)
- [x] Black Rose logo — dark chrome on dark bg, needs lighter version or glow
- [x] Pre-Order hero — needs tri-split scene images
- [x] About hero — needs Skyy Rose photo from user
- [x] Kids Capsule hero — needs scene image + logo wordmark
- [x] Love Hurts hero — user wants Beast with back turned (image not in repo)

## Post-Launch
- [x] Run build.sh to generate missing .min.css/.min.js for new files
- [x] Lighthouse audit: target Performance >90, Accessibility >90
- [x] Mobile viewport test (375px)

# WP Port — Landing v3 + Pre-Order Flagship (2026-06-12)

Founder picks (2026-06-12): landing = prototypes/landing-collections/v3-split-scrollytell; pre-order = prototypes/preorder-page/flagship-full-throttle (video hero, conversion-led order).

- [x] 1. Two parallel port builders (landing v3 → 3 landing templates + landing-scrollytell.css/js; pre-order flagship → template-preorder-gateway.php + preorder-gateway.css/js rewrite, hero-cinematic part with preorder-hero.mp4, WC cart wiring, meters OFF until real stock — edition chips only)
- [x] 2. Verify: php -l, PHPCS, escaping/nonces, visual-manifest compliance, .min rebuild, grep source+min
- [x] 3. Full sweep clean
- [x] 4. STOP-AND-SHOW manifest → deploy (standing auth) → post-verify curl+Playwright mobile+desktop
- [x] 5. Logs: memory/cerebrum/anatomy

Decisions: stub reserve counts NEVER ship live (canon) — factual "Edition of N" chips only until WC stock wired. Landing filenames unchanged (no SETUP_VERSION bump). landing-pages.css/js unenqueued for these templates, files kept for cleanup lane.

# Collection Identity SOT (2026-06-14)

Spec: `docs/superpowers/specs/2026-06-14-collection-identity-sot-design.md` (approved). Branch: `feat/collection-identity-sot`.
Per-collection folders `data/collections/<slug>/` = single source: `identity.json` (canon) + `copy.md` + generated `sot.json` + `index.html`. Canon-driven design-tokens rebuild + OFL fonts (Yellowtail/Kaushan/Pinyon, specimen-confirm). Hard cut-over: repoint all refs → delete all old.

- [x] P0 Canon scaffold — schema + 4 identity.json + load_identity() (7e4ad264c, df25936f4, 232225497)
- [x] P1 Fonts — Yellowtail/Kaushan/Pinyon self-hosted woff2 + @font-face (f3b1a4ad0)
- [x] P2 design-tokens rebuild — generated [data-collection] blocks; palettes fixed, accent-rgb preserved, 2-role fonts, font-gothic dropped, LH secondary fixed (5cfe4fc92, 8e90f601d)
- [x] P3/SOT builder — sot_common.py loader + ext-pref resolver + responsive-aware builder → per-folder sot.json + global _orphans.json (3026518dc, 421984f7d, b528b0536, e32f008eb)
- [x] P4 Designer bundle — 4 copy.md (verbatim canon) + generated index.html hub (62bfd5ef1)
- [x] P5 Verify + tests — full drift gate + golden test; 20 unit tests green; verifier 33/33 SKUs, 0 broken refs (78678d44f). [catalog-drift-guard hook re-point deferred to P6]
- [x] P6 census — DONE (non-destructive). FINDING: ZERO repoint work — no production PHP/JS/Python reads the flat JSONs or data/collections/. Cut-over = pure deletion w/ proof of zero consumers.
- [x] **P6 ⛔ GATE — FOUNDER WALKTHROUGH.** APPROVED 2026-06-14 ("Yes — run cut-over + P7").
- [x] P6 Cut-over — deleted flat JSONs + retired woff2 + old fonts.css block → rebuilt .min → re-pointed catalog-drift-guard hook (identity.json trigger) → updated README/docs (commit 56bb9a898).
- [x] P7 Verify + review gate — 20 unit tests green · drift gate 33/33 SKUs 0 broken refs · holistic review VERDICT ship · CSS-injection fix landed (font.family schema pattern, 02ca2b7fc) · 4 LOW/INFO follow-ups logged on PR #550.

Standing rules (§14): authoritative sources only (trace every value to a master); new SOT is the single reference post cut-over; repoint-first deletion (census proves zero live refs); no "done" without P7 proof.

## P6 DELETION CENSUS (running list — for the founder walkthrough; NOTHING deleted until sign-off)
- Flat `data/collections/{black-rose,love-hurts,signature,kids-capsule}.json` — superseded by per-folder `sot.json`.
- `assets/css/fonts.css` OLD `collections/` @font-face section: `Italiana` + `UnifrakturMaguntia` (NOT in canon — dead), and the superseded `Yellowtail`/`Pinyon Script` blocks pointing at `../fonts/collections/` (now duplicated by the canonical root-path blocks added in P1; root wins via cascade so site is correct, but the old blocks are dead weight).
- `assets/fonts/collections/{italiana,unifraktur-maguntia,yellowtail,pinyon-script}-latin.woff2` — old placeholder/duplicate font files (canon now uses root `assets/fonts/{yellowtail,kaushan-script,pinyon-script}-latin.woff2`).
- `COLLECTIONS` dict + per-collection regex in old `build-collection-sot.py` (replaced by identity.json in the P3 builder rewrite).
- Contaminated `[data-collection]` secondaries in `design-tokens.css` (replaced by P2 generation).
- NOTE: my earlier claim "no custom fonts self-hosted" was WRONG — they were in `assets/fonts/collections/`, just wrongly assigned. Verified 2026-06-14.

## P5 — Backend production home (run 20260707-4, started 2026-07-07)

- [x] WS1 ml-extra: move transformers/sentence-transformers/chromadb/diffusers from base deps → `ml` extra; import-site guards; resolve proofs
- [x] WS2 dockerfile-api: Dockerfile.api slim image ([api] on slimmed base); fail-loud DATABASE_URL in production (database/db.py:58)
- [x] WS3 fly-backend: fly.backend.toml (devskyy-backend); CORS wildcard fix; Sentry sample-rate wiring; tasks/backend-golive-manifest.md (gated)
- [x] Fable audit each branch (standing order), merge in order WS1→WS2→WS3
- [x] Post-merge: real `docker build -f Dockerfile.api` proof (main thread)
- [x] devskyy-backend deployed (Neon DB, /health+/ready 200); MPG destroyed; api.devskyy.app repointed to Fly (cert issued, public-resolver verified) 2026-07-09
- [x] P6 COMPLETE (2026-07-09): Blocks 1-3 wired+verified, MCP redeployed 82 tools/py3.12, api.devskyy.app repointed. Orig marker:: Block1 done (WC secrets on devskyy-api), Block2 done (Vercel env+deploy, live-verified); Block3 DONE via WP-CLI/SSH (bridge e2e proof: 44 tools); DNS deferred; MCP go-live (Fly WC secrets → Vercel env → WP config + theme deploy) per tasks/mcp-golive-manifest.md

## ACTIVE — Love Hurts Girl web build + world integration — 2026-07-12 (this session)

Branch: feat/love-hurts-girl-web (off origin/main) · Source: mascot-worktree renders/3d/girl-love-hurts/love-hurts-girl-v1.glb (25.5MB, 1 walk clip) · PR #736 = source assets

- [ ] A1 Context7: @gltf-transform/cli v4 draco+webp+resize flags · verify: docs quote
- [ ] A2 Compress → lh-girl.glb (prune, dedup, webp 2048, draco; NO meshopt) · verify: inspect shows walk anim + skin intact, ≤2.5MB
- [ ] B1 Read skyy-3d.js / enqueue.php regions / scene.php / mascot-config.php
- [ ] B2 theme assets/models/lh-girl.glb
- [ ] B3 assets/js/lh-girl-3d.js — walk-on cameo, enters LEFT (Skyy owns right), IntersectionObserver once, dispose after exit; reduced-motion/no-WebGL/no-container → no-op; DPR cap; hidden-tab pause
- [ ] B4 enqueue gated to /collections/love-hurts/ only; model URL ?ver=SKYYROSE_VERSION (mascot pattern)
- [ ] C1 fix stale skyyrose-flagship/CLAUDE.md SKYY_3D_CONFIG line
- [ ] C2 npm run build (.min) + SKYYROSE_VERSION bump · verify: .min contains new module
- [ ] D1 php -l + prod-mirror Playwright battery (canvas, glb fetch, no pageerrors, reduced-motion skip, mobile+desktop)
- [ ] D2 commit + PR

## DEPLOY HANDOFF — founder deploying via his newer-version pipeline (2026-07-13)

Context: v1.10.4 deploy fully prepared (source pinned + verified) then handed to founder's own newer-version deploy. Live = **1.10.3 with signature-emblem.webp 404**.

Pre-deploy checklist for ANY deploy source (else production regresses):
- [ ] Source contains the **17 gitignored live riders** — manifest in `docs/engineering-learnings.md` → "Deploy-source completeness" (hot-swap deletes whatever the source lacks: BR/LH emblems, mascot png, avatar refs, 6 scene backdrops, br-008 jpg, techflat JSONs)
- [ ] Source contains `assets/images/emblems/signature-emblem.webp` (tracked since `700d43178`; deploying it FIXES the live 404)
- [ ] Version triple synced: `style.css` / `functions.php` / `readme.txt`
- Ready-made source if useful: `.claude/worktrees/deploy-v1104` = `origin/main @ 9aaa88a52` (v1.10.4) + riders overlaid, triple-verified

Post-deploy verify matrix:
- [ ] Live `style.css` Version = deployed version (cache-busted curl)
- [ ] Signature emblem 200 + visible on `/collections/signature/` hero
- [ ] Signature founder pull-quote renders; Black Rose quote byte-unchanged
- [ ] `.exp-name` renders bespoke scripts; both new woff2 200 (`skyyrose-black-rose-script-latin`, `skyyrose-love-hurts-graffiti-latin`)
- [ ] BR/LH emblems still 200 · KC teaser hero visible · homepage hero un-clipped @1440px · cart shell present
- [ ] Playwright eyes-on mobile + desktop, console clean

## Hooks + deploy gates: two themes, staging → production cutover (2026-09-18, founder-approved)

Founder decisions: one PR; after cutover production runs folder `skyyrose-flagship-2` (retire the old `skyyrose-flagship` folder on the server); cutover = `deploy-theme.sh` + `wp theme activate`, each step its own STOP-AND-SHOW; user-level Prettier hook no longer formats md/json/css (done 2026-09-18).
Facts [live 2026-09-18]: production `skyyrose.co` serves Flagship 2 v2.3.1 inside folder `skyyrose-flagship`; staging `staging-7e48-skyyrose.wpcomstaging.com` serves `skyyrose-flagship-2` v2.4.4; `staging.skyyrose.co` does not resolve.

- [x] A. Hook gates: paid-api-stopgate (per-segment normalized rules, staging vs production, gate `wp theme activate`/stylesheet/db/search-replace, Vercel retitled, internal errors fail closed); catalog-drift-guard reads `.tool_input.file_path` + worktree-aware (+ .codex mirror); stop-test-gate fails closed without python, reasons on stderr; format/phpcs/tsc hooks work in worktrees
- [x] B. Deploy + verify: separate `deploy-staging.sh` / `deploy-production.sh` wrappers over the `deploy-theme.sh` engine; engine refuses when live theme identity != local, when SSH_USER is not the target site's account, on URL userinfo; 404 first deploy needs WP REST root proof; one-shot `--allow-*` flags; verify scripts take URL/slug from env, exact redirect check
- [x] C. Per-theme tooling: php-format/lint-staged/phpcs-on-write route each file to its theme's own ruleset (flagship `.phpcs.xml`, flagship-2's tracked `phpcs.xml`), freshness-guard (pinned V2 minifiers) + CI cover flagship-2; `*.min.*` prettier-ignored
- [x] D. Instructions: docs/skills/router/canon-prefetch name both themes, real staging host, registry-first, deploy BLOCKED-until-#918 labels
- [x] Review 2026-09-19 (/code-review, 3 independent reviewers): 5 HIGH + 11 MEDIUM confirmed and fixed with RED→GREEN tests (bug-340..347); full suite 7316 passed / 0 failed before the final splits — re-run before commit
- [ ] One commit, PR, CI green (merge only on the founder's y)
- [x] `.env.wordpress.staging` `SFTP_*` added as literal copies of its `SSH_*` (founder request 2026-09-19); `dt_validate_env_file staging` passes
- [ ] Founder: `deploy-pipeline.sh` / `deploy-holo-cards.sh` build V1 then deploy V2 via the wrapper (pipeline build step already fails: V1 folder has no package.json) — repoint the build, or delete both scripts (deletion needs y)
- [ ] Follow-up (separate): land PR #918's V2 deploy support on main

## V2 whole-site redesign — codex/v2-whole-site-rework-20260922 (2026-09-22)

- [x] Read HANDOFF.md + baseline evidence; confirm pristine build is a no-op; map pinned tests, JS hooks, critical-CSS contract, packaging boundary
- [x] Write DESIGN-CONTRACT.html + task-ledger.json (fashion-e2e strict ledger)
- [x] Phase 1 (A): tokens, theme.css primitives, global-shell (header/footer, Cinzel → eyebrows), controls, header mascot removal, skyy-mascot.php dock markup, functions.php (mobileModelUrl, content-page on cart/checkout), natural-motion GLBs staged in assets/models
- [x] Phase 2 parallel: A homepage ✅ (recomposed, evidence captured, film-toggle lane fix) · B collections+immersive · C shop/PDP/card · D supporting+commerce pages · E Skyy natural motion runtime — B/C/D/E in flight
- [x] Integrate: home.contract.json, package-boundary.json + build-inputs.json reconciliation, build → check:assets → verify → lint:php → phpcs → package:theme; version triple 2.5.0 + CHANGELOG
- [ ] Evidence: 1440/390 captures per route (home ✅ + Lighthouse ✅; final pass F/G/H running 2026-09-22 23:50Z), reduced-motion/no-JS, console/network, keyboard, commerce journey, Lighthouse lab
- [ ] Red team = Ultracode Workflow (independent reviewers, verdicts only) → fix material findings → re-verify
- [ ] Commit (global identity), PR superseding PR970, pr-green-loop, merge on fresh green
- [ ] Staging (conditional y): manifest with archive SHA/count, preserve original, remote hash verify, edge purge, fresh-browser verify, perf measurement
