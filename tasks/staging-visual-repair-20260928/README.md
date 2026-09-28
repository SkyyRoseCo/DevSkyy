# V2 staging visual repair — local candidate evidence

This evidence is from an isolated local WordPress 7.1 / WooCommerce 11.1.0
fixture at `127.0.0.1:18400`, not authenticated staging and not release
acceptance. The fixture activated the repository V2 theme candidate and used no
production writes, product imports, paid generation, or external customer data.

## Captures

- `evidence/desktop-home.png` — 1440×1000 house hero and live desktop Skyy dock.
- `evidence/mobile-home.png` — 390×844 house hero and live mobile Skyy dock.
- `evidence/desktop-mascot.png` / `mobile-mascot.png` — eyes-on idle-arm crops.
- `evidence/desktop-jersey-motion.png` / `mobile-jersey-motion.png` — live
  in-view Tour Around the Bay video frames.
- `evidence/reduced-jersey-reduced.png` — reduced-motion poster fallback.
- `evidence/browser-results.json` — DOM/runtime observations recorded alongside
  the captures.

Eyes-on review found the original desktop title clipped to `SKYYROS`. The
candidate CSS was corrected and recaptured; the final desktop and mobile
captures show the complete `SKYYROSE` wordmark with zero horizontal overflow.
Skyy's idle arms hang naturally in both rig tiers, and the Jersey Series video
is visibly active while reduced motion leaves the video unloaded and displays
the poster.

Live staging remains unverified because the public staging URL currently serves
the older Black Rose homepage candidate; no deployment was authorized.

## Staging preparation — 2026-09-28

Recovered the completed cloud task through `codex cloud diff` after browser sign-in
looped. Applied its theme, regression tests, and fixture evidence to main
`8a1309979`; already-merged setup repairs and unrelated cloud memory edits were
excluded. Source-certification hashes were reconciled only for the changed
`theme.js`, three changed PHP templates, and the resulting PHP baseline file.
No product registry or media asset was changed.

Local checks: 43 mascot tests, generated CSS/JS and critical CSS, product registry
projection, 82 PHP syntax checks, and staging deployment preflight passed.
The full release suite remains incomplete: the collection motion validator rejects
the new `template-parts/home/editorial-journal.php` video emitter. Its whitelist
requires a follow-up reconciliation before a complete release pass. No validator
was disabled. This staging deployment is authorized for live candidate review;
it does not certify production readiness.
