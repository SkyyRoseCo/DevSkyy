# Centered hero and letter entrance — independent QA

Current user direction: center SKYYROSE in the hero and give it a fresh fashion treatment with purposeful animation. This direction overrides the earlier left-column composition. No tagline is authorized.

The implementation uses the existing scene and font resources, centers the title against the full viewport, and reveals decorative letter spans using transforms and opacity. Each letter uses a 640ms entrance with 28ms offsets. The native H1 has one accessible brand name. Existing background video, concierge, collection navigation, and commerce controls remain in scope for regression verification.

## Local verification

Source-backed WordPress fixture: `http://127.0.0.1:18883/`. Authentication: NOT_APPLICABLE. This is local behavior evidence, not proof of deployment.

All seven checks passed: widths 320, 390, 768, and 1440; 390 with reduced motion; 390 with JavaScript disabled; and 720 with 200% root text sizing. The last case is a text-resizing check, not a claim to have exercised browser zoom UI.

- H1 center error: 0 to 0.0078125 pixels.
- Horizontal page overflow: none.
- CTA bounds remain inside each viewport.
- Reduced motion and JavaScript-disabled title animations: zero.
- Browser page errors: zero.
- Eyes-on desktop, mobile, and enlarged-text screenshots: centered composition and no observed CTA/concierge overlap.
- Critical CSS: 16,329 bytes of the existing 16,384-byte cap.

A short headless desktop sample after the entrance measured median 33.3ms and p95 34.2ms frame intervals with the existing scene running. A blank-page control measured 16.7ms median. This does not establish 60fps across target hardware or attribute existing scene cost to the new letter entrance. No such performance guarantee is made.

## Skill application evidence

The `animate` skill was supplied by the user; its mandatory Impeccable context preparation was read. Main checkout `.impeccable.md` supplies the audience and brand context. Current user-centered alignment and retired-copy instructions take precedence over older defaults. Visualize routes existing-project implementation to the open project; an additional contained motion preview uses the existing scene and font with local replay controls.

Correct example (REPRODUCED_LOCAL): with reduced motion enabled or JavaScript disabled, the complete title is visible and has no active title animation. Evidence: `tasks/evidence/hero-motion-20260921/local-geometry.json`.

Incorrect example (ILLUSTRATIVE_UNEXECUTED): hide the heading by default and rely on JavaScript to reveal it. This would suppress the brand when JavaScript fails. Correction: static visible defaults, with animation added only under the existing motion-ready state. Authentication for these offline examples: NOT_APPLICABLE. This narrow application does not certify the entire skill library.

## Superseding split-hero correction

Founder correction: SKYYROSE remains centered between the product film and the existing animated scene. The centered-only result above is intermediate evidence and does not certify this new split layout.

The first independent split pass found material regressions and blocked staging: desktop H1 center error was 192px at 768px and 360px at 1440px; blocking deferred external styles expanded the hero to over 5,200px through six normally flowing images; keyboard focus near the end of the loop could remain clipped offscreen. Independent interaction QA also identified visible duplicate frames under Save-Data. These are reproduced observations, not illustrative cases. Terra is repairing the integrated candidate before a fresh pass.

The three original product links were independently followed to WooCommerce PDPs and their displayed SKUs matched SG-005, BR-004, and LH-004. Local authentication: NOT_APPLICABLE. This is route and presentation evidence, not payment verification.

Correction to the CSS-failure interpretation: source and actual HTML confirm `home-page.min.css` is already an ordinary `rel=stylesheet`, `media=all` blocking resource. No asynchronous style swap was present. The blocked-resource experiment represents CSS download failure, not slow-loading first paint. Essential normal layout is supplied before paint by the blocking sheet; no delivery change or complete failed-CSS visual parity is claimed. High-specificity fallback rules added during remediation were removed because they overrode the real mobile layout.

At 23:18 UTC, nine geometry modes pass (320/390/768/1440, desktop/mobile reduced motion and no-JS, 720 text resizing): center error <=0.0078125px, no page overflow/errors, mobile film below copy. The 50s keyboard regression now reveals the focused first card at x7.19..231.19. Fresh Save-Data initialization yields static motion and zero visible copies. Tablet/compact desktop concierge overlap remains under remediation; these passes alone do not approve staging.

## Integrated local result

The final responsive layout uses the triptych at 1024px and above. Below that breakpoint, the centered copy precedes a static swipeable film and separately positioned concierge. Desktop reserves a lower band for the concierge. All nine modes pass again; independent overlap checks at 768, 1024, 1280, and 1440 show no CTA/concierge-region intersection. Eyes-on 390, 768, 1024, and 1440 confirm centered typography and separate product/scene panels. A final 16px concierge lift keeps the rendered controls inside the hero.

Evidence: `tasks/evidence/hero-motion-20260921/split-local-geometry.json` and `split-local-reel.json`. The reel's synthetic visibility/page-transition checks are not an actual browser BFCache certification. Payment execution remains outside this hero task.

Main registry projection check: `/Users/theceo/DevSkyy/.venv/bin/python scripts/sync_product_registry.py --check` PASS; CSV and product dossiers match the registry. No product facts or source assets were edited for this restoration.

## Refreshed distribution

Release packaging agent verified full ZIP SHA256 `17022575dca1dfe8d3053b883f2a66d8a84903c983630d5143d72ab8e3998e41`: all 563 runtime members byte-match the frozen source; zero mismatches. Critical CSS is 16,042/16,384 bytes. Marketplace split contains 178 core and 385 required-media files; descriptor SHA256 `3859a7df3a39f60b28bd1cc0c7ab3e271b67c220a7632dbd8186093e19436ab3`. Source certification and deterministic packaging pass. This candidate has no fresh clean-install claim and is not a production deployment.

## Hosted verification and delivery correction

Staging identity: `https://staging-7e48-skyyrose.wpcomstaging.com`; active stylesheet `skyyrose-flagship-2`. Authenticated SSH operations were limited to guarded staging theme files, before/after hash checks, rollback capture, and cache flush. Credentials were not recorded. Production was not modified.

The hosted environment differs from the local fixture: installed Jetpack Boost rewrites stylesheet links using `media=not all` and an onload swap. This invalidates the local blocking-only assumption for staging. Installed source evidence: `jetpack-boost/app/modules/optimizations/critical-css/class-critical-css.php:147` and `jetpack-boost/app/lib/critical-css/class-display-critical-css.php:34-84`. The documented `jetpack_boost_async_style` filter accepts false to retain blocking delivery. The final `inc/performance.php` filter applies only on the homepage for all-media styles. Other routes retain existing behavior.

Fresh live response `/?hero_centered_review=20260921b` confirms the new hero and a native combined stylesheet `media=all`, with no asynchronous swap. All nine live geometry modes passed on the preceding fresh candidate query using the identical CSS. Live smoke on the final review URL at 23:28 UTC passed:

- SG-005, BR-004, LH-004 links each HTTP200; displayed WooCommerce SKU matches.
- Film pause and resume work; actual animation state returns running after focus/pointer leave.
- Existing scene video readyState4, playing, currentTime6.72s.
- Ask Skyy and Dismiss Skyy are inside hero bounds and do not overlap either shop action.

Final remote performance.php hash matches local: `5b5dbe28de366f59e6c36ca55220676844b26e18893eec3d6986713617636d9b`.

At the final plain-URL observation before this entry, the CDN still served old markup (`last-modified: 23:22:31 GMT`, max-age300, HIT). Fresh query delivery is verified; plain URL propagation is not yet claimed. No safe installed CLI edge-purge operation was identified; object-cache flush is not represented as CDN purge. The earlier full package `17022575...` is superseded by the final package including the hosted-delivery filter.

Final package including Jetpack delivery fix: SHA256 `a833143145b68a6cbe3d1e462f7c7daa1931d45b02b811c44032a11e6889e0a1`, 563 files, all byte-identical to frozen source. Split descriptor `7dd983beb94d153a3262f2df1f7d46ea44949d44746123b4134e6c156c945dce`; 178 core plus 385 required-media files. Certification and package checks pass. Packaging report: `/Users/theceo/.codex/worktrees/marketplace-split/DevSkyy/tasks/current-package-a8331431.md`.

## Final canonical outcome — supersedes pending-cache notes

At 23:29 UTC the plain canonical staging URL returned the new film markup and native blocking stylesheet (no async swap). Root reran all nine geometry modes on the plain URL: every mode PASS, center error <=0.0078125px, no horizontal overflow or browser page errors. Canonical live smoke at 23:29:52 UTC also PASS: exact three PDP SKUs/HTTP200; film pause/resume; Ask/Dismiss controls within hero and clear of CTAs; existing video playing at readyState4. The edge-cache propagation limitation recorded above is resolved for these observations.

Final evidence JSON and desktop/mobile captures in `tasks/evidence/hero-motion-20260921/` now reflect the canonical staging URL. Scope complete for this homepage hero change. Production launch and payment verification are not claimed.
