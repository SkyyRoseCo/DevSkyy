# Reference homepage immersive preservation review

Reviewer: immersive_preservation. Manager: root. Candidate: in-progress abe0 V2 theme; local fixture http://127.0.0.1:18883/. Authentication: NOT_APPLICABLE. Evidence classification: REPRODUCED_LOCAL plus SOURCE_VERIFIED. No deployment or production claim.

## Initial local review

390px reduced-motion: closed collection films paused with no src assigned; native summary Enter opens; rail width358, scrollWidth1064; End key scrollLeft706 and counter03/03. No page errors.1440px default motion: closed films unloaded; eligible film activates after opening; close pauses all and sets offscreen. No page errors.

No-WebGL simulation (canvas getContext returns null for webgl): after character intent, mascot presence=failed, approved portrait loaded/visible, canvas hidden, guide API present.

Observed defect editorial-home-mobile-ask-skyy-overlap: at390x844 #skyy-hero-chat x20,y494.65625,width128,height44. elementsFromPoint at center returned .sr2-recovery-motion-toggle first. Normal click timed out because Pause motion intercepted pointer events. Reported immediately to Terra/root. This is initial candidate evidence and must be superseded by fresh normal-click verification after CSS rebuild.

Withdrawn hypothesis: an initial partial reading suggested tooltip width was initialized while details was closed. Full assets/js/collection-scene-motion.js read shows setShopping(true) computes width at activation, so no demonstrated zero-width tooltip bug. Root/Terra received the correction. visual-recovery.js computes live rail dimensions on movement; no permanent zero-width cache was reproduced.

## Source provenance

- assets/js/visual-recovery.js: initRails, live geometry in move/update, native key handlers, reduced-motion instant scrolling, hero IO and pause lifecycle.
- assets/js/collection-scene-motion.js: ratio>=0.15 visibility gate, setShopping width measurement, reduced-motion static defaults, IO and pagehide lifecycle.
- assets/js/mascot-loader.js: character-intent load, reduced-motion/saveData guard, local script failure fallback.
- assets/js/skyy-3d.js: WebGL/context-loss fallback.
- front-page.php: native details wraps living-archive-worlds after journal.

Skills read: /Users/theceo/.agents/skills/skyyrose-3d-web-os/SKILL.md; canonical Fashion Theme Team fashion-frontend-motion and fashion-e2e-task-execution. OS V1/Vercel/older aesthetic references are stale for this task; current V2 and explicit user reference govern. This scoped review does not certify entire skill example library.

## Latest build retest

Raw browser script and results: /tmp/skyyrose-launch-redteam-20260921/reference-v3-preservation.cjs and reference-v3-preservation.json. Screenshots reference-v3-{390,1440}-{full,top}.png in same directory. See JSON for actual latest outcomes; any absent outcome is unverified, not passed.

V3 fresh local run at2026-09-21T22:12:32Z:390 Ask normal click opens dialog. Initial immediate post-Escape focus read raced the asynchronous close handler; separate300ms followup returned dialog.open=false and focus=skyy-hero-chat. Pause/play labels flip correctly at390/1440. Both widths keyboard End counter03/03; reclose pauses all films/offscreen. No page errors or horizontal overflow.

Eyes-on v3 top captures:390 mascot and actions visually overlap main editorial CTA/collection navigation region;1440 Pause motion overlaps the mascot Ask control and Dismiss protrudes below hero boundary. These composition defects were sent Terra/root for remediation. Do not interpret functional390 Ask fix as complete visual approval. Desktop Ask normal-click retest remains required.

V4 local retest2026-09-21T22:15:55Z: Ask Skyy normal click succeeds at390 AND1440; Escape after300ms restores hero-chat. Both pause/play, worlds keyboard, close-pause lifecycle pass; no page errors/overflow. Raw /tmp/skyyrose-launch-redteam-20260921/reference-v4-preservation.json, reference-v4-bounds.json; full/top screenshots sameprefix. V3 preserved unchanged.

V4 newly observed desktop defect: Pause motion x1264.234375,y92,width103.765625,height431.1875,bottom523.1875 intersects all4 worldrail links. Likely simultaneous top and inherited bottom anchoring; sent Terra/root to reset bottom:auto.390 tested controls have no intersection with CTA/worldrail/eachother and remain within hero.1440 mascot controls now within hero, but oversized pause control remains blocking desktop visual/interaction approval.
