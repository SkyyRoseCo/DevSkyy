# Skyy walk-on dock — Agent E browser evidence (2026-09-22)

Fixture: `php -S 127.0.0.1:8794 -t <repo>` (plain document root, no router) →
`http://127.0.0.1:8794/tools/v2-theme-preview.php?route=<route>&skyy=1`.
Browser: Playwright 1.62.1 chromium-1234, args `--use-gl=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist`.
Script: `verify-skyy.cjs` (copied beside these notes; source lives in the agent-e scratch folder). Machine-readable results: `verify-results.json`.
Reference for identity reads: `/Users/theceo/DevSkyy/assets/branding/mascot/skyy-canonical-reference.jpeg`.

## Scenarios and results (final run 20:36–20:37Z, all `[repro]`)

| Scenario | Page errors / console errors / failed requests | Result |
|---|---|---|
| about @1440×900 | 0 / 0 / 0 | Portrait mounted in the dock 18 ms after load (`data-presence="static"`, recall `hidden`). Rig live (`data-presence="live"`, `data-renderer="3d"`) 4614 ms after load. Events: loading/prepare @4531 → 3d-ready + walking-in @4684 → 3d-visible @4689 → action-complete + idle @10123. Model request: `skyy-natural-desktop.glb` only. |
| home @390×844 (DPR 2, touch) | 0 / 0 / 0 | Live at 4902 ms; walk → wave → idle (action-complete @9903). Model request: `skyy-natural-mobile.glb` only. Character 96×148, three 44 px-high controls (136×44) beside her, dock 240×160 at right 12 / bottom 12. Ask Skyy (tap) opens the dialog with focus on the input; Escape closes and returns focus to `#skyy-hero-chat`. |
| signature @1440, `reducedMotion: 'reduce'` | 0 / 0 / 0 | After 9 s: `data-renderer="static"`, `data-presence="reduced"`, canvas `hidden` (display none), portrait opacity 1, status "Skyy is here, with motion off.", Pause toggle hidden, Ask/Dismiss 144×44. No GLB, no `skyy-3d.js`, no three/draco request. |
| signature @1440 | 0 / 0 / 0 | Live at 4800 ms; action-complete @10235; desktop GLB. |

### about @1440 interaction chain
- Walk-in frames (`frames/about-1440-frame-00..13.png`, ~0.45 s apart): `Skyy_Walk` with `--skyy-entry-shift` 358 px → 297.7 → 178.4 → 79.3 → 21.1 (turning) → 0.5 → `Skyy_Wave` (six frames, front-facing open palm) → `Skyy_Idle`. Entry distance 358 px = viewport edge to her dock mark; she travels in a three-quarter view and turns to the visitor at 60 % of the walk.
- Ask Skyy (click) → `dialog.open`, stage reparented to `#skyy-dialog-stage`, focus on `#skyy-ask-input` (`about-1440-dialog.png`). Escape → dialog closed, stage back in `#skyy-hero-stage`, focus on `#skyy-hero-chat`.
- Dismiss → stage `hidden`, `data-visibility="dismissed"`, renderer stopped (`running:false`), recall pill visible 126×44 at right 24 / bottom 24, `sessionStorage['skyy:dismissed']==='1'`, focus on `#skyyrose-mascot-recall` (`about-1440-dismissed.png`).
- Reload → still dismissed (stage hidden, recall visible), no new GLB request, `skyy:entries` stays `'1'`.
- Recall click → dialog opens, `skyy:dismissed` cleared, pill hidden. Escape → she is back in the dock (stage visible, pill hidden), focus on `#skyy-hero-chat` (`about-1440-recalled.png`, captured mid walk-in).
- Hidden-tab measurement: `document.hidden` emulated true + `visibilitychange` → 0 render calls in 2 s (frames 35 → 35, `running:false`); restored → loop resumes (frames 69, `running:true`).
- Pause toggle visible once 3D is ready (`Pause character`, `aria-pressed="false"`).
- Dock: `position: fixed`, `z-index: 80` (header 100, bottom 64 px; no overlap), right/bottom 24 px at 1440, 12 px at 390. Controls: Hanken Grotesk 500, 12 px (11 px at 390), uppercase, 44 px tall; Ask Skyy border `rgb(183,110,121)` (rose accent), others hairline.

## Identity read (eyes-on, against the canonical reference)
Recognisably Skyy in every frame: dark curly hair, warm brown skin, white varsity jacket with black raglan sleeves and red "Love Hurts" chest script, white joggers with black side stripe and the red rose/heart patch, black/white/red sneakers; the greeting wave is the same open-palm gesture as the reference. The mesh face is simpler and the hair volume smaller than the 2D canonical — the delivery REPORT declares this limit of the delivered rig; it is not a runtime issue.

## Fixed during verification
1. Recall → Escape parked focus on `<body>` / the header menu button. Root cause: `open()` reparented the stage into the still-closed dialog before `showModal()`, so the focused opener stopped rendering, Chromium's focus fixup moved focus to `<body>`, and theme.js's shared overlay lifecycle recorded `<body>` as the opener (its fallback is the header menu). Fix in `mascot.js`: `recall()` restores the dock and focuses `#skyy-hero-chat` before opening; `open()` calls `showModal()` before reparenting; a `beforetoggle(closed)` handler moves the stage home before theme.js returns focus; `restoreHome()` no longer re-appends a stage that is already home (re-inserting blurs the focused descendant). The harness now emulates focus fixup (`hidden` setter) so the unit suite covers this class of bug.
2. 390: the live `role="status"` line floated over page copy; it is now visually hidden (still announced) in the compact dock.

## Open / not verified here
- Composition: at 1440 the dock footprint is 334×248 px (bottom-right); on `route=about` it overlaps the right edge of the founder headline column. Page compositions should keep critical copy clear of the bottom-right ~360×270 px zone, or the founder may prefer the dock to collapse to the pill after the greeting settles (not in the contract; needs a decision).
- During the ~1.5 s walk-in she passes in front of her own controls (Pause/Ask/Dismiss) on the way to her mark (`frames/*-frame-01..02`). Deliberate (foreground character); flip the canvas below the controls if a reviewer prefers her to pass behind.
- Fixture-only: the pink "LOCAL V2 REVIEW" banner is moved bottom-left under `skyy=1` so it does not cover the dock; it is not part of the theme.
- Not measured in this fixture: real-device frame budget (swiftshader is software GL), 20 s load-timeout path (only unit-tested), `deviceMemory <= 4` tier selection in a browser (unit-tested), Save-Data (unit-tested; browser context has no Save-Data switch).
- Built `.min` assets were not regenerated (no `npm run build` per the brief); Agent A reconciles.
