# Independent public staging preservation verification

Target canonical URL: https://staging-7e48-skyyrose.wpcomstaging.com/
Date:2026-09-21T22:26:21Z. Reviewer: immersive_preservation. Manager:root.
Authentication: NOT_APPLICABLE, public storefront browser only. Evidence: VERIFIED_LIVE public staging. No account/cart/order/payment writes.

Actual Chromium390x1000 and1440x1000: new .sr2-editorial-hero present. Normal Ask Skyy clicks open dialog; Escape after300ms restores focus to skyy-hero-chat. Motion pause/play label toggles work. Native worlds summary opens with Enter, rail End reaches03/03, closing pauses all3 videos/offscreen. No page errors and document scrollWidth equals viewport at both widths.

Bounds measurements show no tested control/CTA/worldrail intersections or controls extending past hero. The earlier431px desktop pause defect is fixed. Eyes-on final top screenshots confirm discrete46px pause control and separated mobile worldrail labels. Fullpage captures follow instant scroll through lazyimages; fonts.ready awaited.

Public asset byte checks: home-page.min.css, global-shell.min.css, visual-recovery.min.js and collection-scene-motion.min.js each HTTP200 and SHA256 identical to frozen abe0 source. See reference-staging-asset-hashes.json.

One initial run using domcontentloaded+1200ms timed out awaiting worlds summary and did not produce a completion receipt; fresh canonical run above succeeded. This initial incomplete run is not represented as a pass. No forced clicks used. Scope does not include live payment, complete commerce, or production.

Artifacts alongside this file: scripts, rawJSON, bounds, remote/local asset hashes,1440/390 top and full screenshots. Original v3/v4 evidence retained separately under /tmp/skyyrose-launch-redteam-20260921/ and earlier report.

## Final commerce follow-up

Root independently ran `commerce-final.cjs` on the normal public homepage at
390 and 1440 widths. Both passed menu open/close, actual hoodie search results,
empty bag drawer, and SG-005 Quick View with the correct $25 price and product
link. Four featured cards resolve to SG-005, BR-001, BR-004 and LH-004. No cart,
order, payment or account mutation was performed. Raw results: `commerce-final.json`.

An earlier reviewer described a mobile menu-close failure without a saved
complete receipt. Root's separate `menu-repro.json` and final commerce run both
confirmed open=true then closed=false in aria-expanded at 390 and 1440. The
earlier observation remains unconfirmed and caused no speculative code change.
The earlier HTTP image sample containing KIDS-001/KIDS-002 was not a check of
this new featured-card section; do not reuse it as current featured-card proof.

The final current-home link scan checked 35 unique HTTP destinations from the
new editorial DOM. Thirty-four returned 200 to HEAD. My Account returned a
rate-limit response to the automated HEAD scan, then a separate normal browser
navigation returned 200 with the expected My Account heading and login form
(`account-browser.json`); no login was attempted. All five named same-page
fragments exist. The sole bare `#` belongs to the initially hidden Quick View
URL template; the exercised dialog resolves it to the exact SG-005 product URL.
These distinctions are retained in `current-home-links.json` and the browser
receipts rather than turning the HEAD rate limit into a fabricated pass.
