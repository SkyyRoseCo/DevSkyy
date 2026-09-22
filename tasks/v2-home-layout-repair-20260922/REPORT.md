# Homepage crop repair — local candidate, not deployed

The founder reported an unacceptable staging homepage on 2026-09-22. The supplied screenshots show a portrait cropped to the torso in a full-width landscape box and clipped journal artwork. The staging theme had been restored after the separate optimized-CSS delivery failure; that rollback restored an older serif homepage and did not establish visual acceptance.

## Scope

- Give the existing 724 × 1086 founder portrait a separate column, preserving its complete contents with `object-fit: contain`; put story copy beside it and stack naturally on mobile.
- Remove fixed-height journal clipping and preserve each poster's declared 960 × 640 aspect ratio.
- Use the body typeface for existing hero pause/concierge controls; preserve target sizes, controls, links, animation and reduced-motion rules.
- Rebuild committed minified CSS and critical CSS. No product facts, source images, JavaScript, templates, payment settings or deployed files changed.

## Evidence

- `philosophy-1440.png`, `philosophy-390.png`, `journal-1440.png`: local presentation captures using saved staging HTML and local candidate stylesheets. These establish crop/layout behavior, not authenticated live commerce or complete live interaction success. The fixed site header appears over the top of the mobile element capture because it remains sticky during capture; the image itself is contained, not cropped.
- `responsive-checks.json`: Chromium and WebKit at widths 320, 390, 768, 1024, 1440, 1920; all 12 states have loaded, positive-size portrait/poster images using contain and no horizontal document overflow. Below-fold images were scrolled into view before checking; an earlier pre-scroll capture was insufficient evidence because lazy images were unloaded.
- Pinned environment: Node 22.23.2, Python 3.12.12, Pillow 12.3.0; native fixture `/tmp/skyyrose-v2-native-fixture`.
- `npm run verify` PASS. `npm run check:assets` PASS after final control-font edit. Critical CSS 16,227 bytes / 16,384 budget. `git diff --check` PASS. `python scripts/sync_product_registry.py --check` PASS.
- Independent read-only code review: no critical/important findings; approved scoped CSS candidate. Reviewer also verified asset parity and zero npm audit vulnerabilities.

## Reproducible guidance

SOURCE_VERIFIED: [MDN object-fit values](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/object-fit#values), checked 2026-09-22, explains that cover clips mismatched aspect ratios while contain preserves the full object. REPRODUCED_LOCAL: linked viewport observations demonstrate contain in this markup. Authentication: NOT_APPLICABLE to local presentation checks. Signed-in staging was observed separately, but no new deployment was performed.

Correct example: inspect the 724 × 1086 source portrait, preserve its aspect ratio in a dedicated area, and verify both narrow and wide renders after lazy loading. Incorrect example (observed in the prior source and founder screenshot): stretch its box across a landscape section and apply cover, cutting off the face. Correction is the separate portrait layout, not a claim that clearing caches changes image composition.

## Remaining boundaries

This patch is a presentation candidate. It does not claim to resolve staging CDN inconsistency, certify the entire homepage aesthetic, or establish post-deployment performance. The previous 566-file package approval does not identify this changed artifact. Prepare/review a new package before deployment. Production remains untouched.
