# Agent B evidence — collection landings, collections index part, immersive worlds (2026-09-22)

Branch `codex/v2-whole-site-rework-20260922`, theme `wordpress-theme/skyyrose-flagship-2`. No build run, nothing committed.

## What was exercised

- Preview: `php -S 127.0.0.1:8791 -t <repo>` (plain document root, no router), routes
  `http://127.0.0.1:8791/tools/v2-theme-preview.php?route=signature|black-rose|love-hurts|kids-capsule|collections|immersive-signature|immersive-black-rose|immersive-love-hurts|immersive-kids-capsule`.
- Capture protocol (Agent A's): Chromium (swiftshader), contexts 1440×900 and 390×844 plus a 1440 `reducedMotion:'reduce'`
  pass; `networkidle`, scroll walk in 0.85vh steps with 650 ms dwell, images settle (bounded 4 s), every `.sr2-image-reveal`
  verified `is-seen` before the full-page shot; `pageerror`, console errors, `requestfailed`, responses ≥400 collected.
  Script: scratchpad `capture.cjs`; raw metrics in `browser-results.json` (29 entries).
- The shared fixture links every route sheet `functions.php` enqueues for the collection routes (collection-world,
  hero-commerce-scenes, collection-scene-motion, scene-handoff). It does not load the controllers, so
  `visual-recovery.js`, `collection-scene-motion.js` and `scene-handoff.js` were injected with `addScriptTag` on the
  collection routes, and `hero-commerce-scenes.css` + `collection-scene-motion.css` + `collection-scene-motion.js` on the
  immersive routes (functions.php enqueues those for the three immersive templates). Nothing else was injected.
- `collections-b-*.png` renders the new `template-parts/collections/index.php` part through a scratch copy of the fixture
  (scratchpad `docroot/sr2-b-preview.php`, port 8795) because `page.php` (Agent D) has not yet been switched to include it.
  `collections-*.png` is Agent D's current `page.php` output for reference.

## Results

- 29/29 captures: 0 page errors, 0 console errors, 0 failed requests, 0 responses ≥400, no horizontal overflow.
- Hero motion (visual-recovery hooks): on all four collection arrivals the approved video reaches `readyState 4`, `paused:false`,
  poster published, motion toggle visible. Reduced-motion pass: video stays unloaded (`readyState 0`), toggle hidden, static poster.
- Scroll World rail (SIG/BR/LH): `data-recovery-count` = `01 / 03`, controls visible, 3 slides, 3 hotspot layers rendered;
  `[data-scene-handoff]` state `idle` at the top of the page.
- Immersive: `data-scene-state` = `waiting-for-three` in the fixture (no platform Three loader), `reduced-motion` under reduced
  motion; poster fallback is full-bleed; SIG/BR/LH chapters are the three approved shop-the-look scenes, KIDS four static chapters.
- No h1/h2 renders in Cinzel; Cinzel appears only in `.sr2-eyebrow--engraved` index labels. No frame `<img>` is visible in any edit grid.

## Files (PNG)

`<route>-1440.png`, `<route>-390.png` full page; `<route>-1440-reduced.png` viewport-only, reduced motion; `collections-b-*` as above.

## Left open

- Arrivals put the collection lockup image over a hero that already carries the same lettering as a monument (SIG/BR/LH); legible on
  the veil but two renderings of one mark share the frame. Options for Corey/Agent A: accept, stronger left scrim, or a type title on
  these three arrivals. Not changed here — the contract names the lockup image as the title.
- `global-shell.css:296-298` (Agent A) still carries a `body .sr2-world.sr2-world--hero-composed .sr2-hero-commerce__details`
  auto-fit override; `hero-commerce-scenes.css` matches its specificity so the 12-column band wins. Those three lines should be retired.
- Two `<img>` elements with an empty `currentSrc` report `naturalWidth 0` on every route including Agent D's collections page; they
  are shell-level, not in Agent B templates.
