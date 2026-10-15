# SkyyRose V2 whole-site rework — execution handoff

Recorded September 22, 2026. This document preserves the current task so another session can continue without repeating rejected work. **The whole-site rework has not been implemented.** The approved creative direction, clean working branch, staging baseline, and known operational issues are established. The user requested this handoff because usage was nearly exhausted.

## 1. What Corey wants

Corey rejected the current staging aesthetic and the subsequent narrow homepage repair. His instruction was: **“rework the entire site your edits totally ruined the vibe.”** He then selected this creative direction: **“find a innovative way to follow the Veritas composition but add some of the SkyyRose direction.”**

The task is a coherent, premium fashion-commerce redesign across the entire V2 site, followed by verification and corrected staging deployment. It is not complete after repairing the portrait crop or changing a few homepage rules.

The earlier delivery request still applies: audit marketplace readiness, aesthetics, fashion presentation, API behavior, tests, links, optimization, and other relevant production checks; fix findings; commit; create a PR; send an agent to fix that PR until green; then merge. Production readiness must remain evidence-based.

Corey approved: **“approve corrected staging once fixed.”** This is conditional authorization to deploy the corrected work to staging after it is fixed and verified. Do not ask again merely because the new archive has a different hash. It does not authorize production deployment, database restoration, payment-setting changes, paid asset generation, or sending external messages unrelated to the requested PR workflow.

## 2. Approved direction and proposed implementation

Use **Veritas as the compositional reference**: cinematic photography at full width, a clear editorial sequence, restrained navigation, deliberate scale and negative space, and fewer competing elements in each view. Use **SkyyRose as the identity**: its actual garments and artwork, Oakland settings and culture, founder/family story, four collection worlds, typography, materials, and existing high-end motion.

The proposed organizing idea is a continuous journey through the four collections. Each chapter changes imagery, atmosphere, and its established accent color while navigation and shopping controls stay consistent. This idea was communicated to Corey; implementation has not begun and no completed design has been accepted.

### Site-wide design requirements

- Garments and approved photography lead. Avoid a homepage where the headline, product film, mascot, pause buttons, collection rail, and giant emblem all compete at equal strength.
- Preserve the existing features, animation capabilities, accessibility controls, shopping integrations, and collection worlds. Recompose their presentation; do not remove working features to simplify the screenshots.
- Retain Skyy as part of the experience. Integrate her position and controls into the composition so they do not cover the garment, lead image, copy, navigation, or purchase controls. Preserve pause, dismiss, keyboard, and reduced-motion behavior.
- Keep the four collections visibly discoverable. The current homepage hides the worlds in a details element; reassess that hierarchy rather than copying it by default.
- Keep source artwork intact. Do not crop text embedded in journal posters. Do not enlarge a portrait into a panoramic torso crop. Preserve intentional framing and use suitable landscape assets for cinematic wide sections.
- Desktop and mobile need their own deliberate compositions. Do not rely on shrinking the desktop montage. Make mobile product imagery useful and controls easy to operate.
- Commerce should remain clear: collection → product → variation selection → cart → checkout → account. Editorial presentation must support these paths.

### Surface-by-surface work

| Surface | Intended treatment | Behaviors to preserve and verify |
| --- | --- | --- |
| Global header/footer | Quieter editorial navigation, consistent typography, spacing, collection identity, and clear shopping access | Desktop/mobile menu, search, bag count, account, keyboard focus, footer links |
| Homepage | Full-width cinematic arrival, one dominant focal point, collection chapters, curated products, founder story, journal | Existing film/motion, collection links, Skyy integration, pause/reduced motion, responsive sources |
| Collection landing pages | Distinct collection atmosphere within one consistent layout system | Correct collection/SKU mapping, product links, filters where present, scene links |
| Immersive worlds | Preserve existing high-end worlds and their identity; align entry/exit and shopping connection | Camera/scroll behavior, hotspots, WebGL fallback, reduced motion, real product destinations |
| Shop/archive | Garment-led editorial grid with restrained controls and consistent cards | Native sorting/filtering, pagination, price/availability, product destinations |
| Product pages | Strong product imagery and calm buying hierarchy, consistent collection accents | Gallery, zoom where present, variation availability, size guide, add-to-cart, notices |
| Cart/checkout/account | Clean visual continuation of the brand with excellent readability | Native WooCommerce flows, validation, totals, shipping, authentication; payment proof requires permitted test scope |
| About/journal/lookbook | Cinematic storytelling with intact portrait and poster compositions | Links, readable copy, correct media framing, mobile ordering |
| Contact/FAQ/policies/tracking/wishlist/404 | Finish the shared editorial system on supporting routes | Forms, errors, focus, empty states, navigation and destination accuracy |

### Brand rules already identified

Read the current main-checkout `.impeccable.md`, `docs/brand/visual-references.md`, and canonical luxury-design skill before implementation. Latest user direction takes priority over older stylistic assumptions.

- Oakland-rooted, Black-owned American luxury streetwear; the garment is the protagonist.
- Supporting brand references: Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels. Do not imitate another brand's identity or copy.
- Base dark: `#0A0A0A`; Black Rose silver `#C0C0C0`; Love Hurts crimson `#DC143C`; Signature gold `#D4AF37`; Kids rose `#B76E79`.
- Display Archivo, body Hanken, Anton as accent, Cinzel for engraved/limited accents. Do not default to oversized generic serif headlines throughout every surface.
- Current main-checkout brand copy has retired older tagline language. Do not resurrect “Luxury grows from concrete” merely because it appears in an older theme revision.
- Use approved collection lockups where the current canon requires them. Use existing verified imagery; no invented garments or unapproved renders.

## 3. Source authority and reference material

The sole editable product SOT is root `logo-registry.json`, a symlink to `wordpress-theme/skyyrose-flagship/data/logo-registry.json`. Its unified `products` schema contains commerce, design, source bindings, and founder corrections. The active checkout was checked for the unified schema: 33 products and four collections were present. Recheck current founder corrections before changing product-related output.

Default complete read: `from skyyrose.core.product import get_product`, or `python -m skyyrose.core.product <sku>`. Use the registry update API for catalog writes. Do not create alternative product facts in templates, CSVs, dossiers, local maps, or generated manifests. Corey is the maker; his latest specifications are authoritative and recorded as `FOUNDER_CONFIRMED`. Verify implementation against those facts, not the maker against outside evidence. Run `python scripts/sync_product_registry.py --check` before handoff, and the sync command after any authorized direct JSON edits.

Useful local reference mapping:

`/Users/theceo/DevSkyy/tasks/launch-20260921-reference-design-asset-map.md`

This is a recorded mapping, not proof that every suggested image has been visually inspected in this session. The original Veritas reference image itself was not located; do not claim to have reviewed its pixels. The user confirmed the blended direction from the recorded reference description.

Recorded candidate assets to inspect and resolve through current authority before binding:

- Signature Golden Gate cinematic hero: `assets/sot/images/hero/signature-golden-gate-monuments-v2.webp`, recorded 1672 × 941, with mobile responsive source.
- Signature atelier scene: `images/immersive/scene-signature-oakland-atelier-gpt2.webp`, recorded 1920 × 1080.
- Black Rose moon-court/Lake Merritt scenes for darker collection chapters.
- Love Hurts rose-aisle monuments v3 landscape for a wide story composition.
- Black Rose Bay Bridge v4 wide image and existing BART/Tour Around the Bay journal posters; preserve poster text.
- Existing featured product candidates BR-001, BR-004, SG-005, LH-004; use current registry facts/images. Recorded BR-002 and KIDS-002 fidelity concerns are not permission to invent replacements or contradict newer founder confirmations.

Official reference sites opened during the prior design investigation: https://kith.com/ , https://fearofgod.com/ , https://www.oaklandish.com/ . Text/structure was retrieved; no claim of completed visual comparison is justified yet.

## 4. Exact workspace and Git state

**Work here:**

`/Users/theceo/.codex/worktrees/v2-home-layout-repair/DevSkyy`

The directory retains its earlier name, but the active branch is now:

`codex/v2-whole-site-rework-20260922`

Confirmed at handoff:

- HEAD: `6994d978579500e94e1571a223cc4aab70c60609`.
- Branch tracks `origin/main`.
- Working tree was clean immediately before creating this handoff.
- **No new whole-site source changes have been made.**

The original `/Users/theceo/DevSkyy` checkout is on `feat/single-product-entry-point` and contains extensive unrelated dirty work. Read current canon there where needed; do not reset, broadly stage, overwrite, or clean it. Always recheck branch/status before edits.

Read applicable repository/nested `AGENTS.md`, `SOT.md`, and `.wolf/memory.md`. Memory is context, not evidence of current deployment or authorization. Do not write persistent memory unless asked.

## 5. Rejected work — do not accidentally ship

PR970: https://github.com/SkyyRoseCo/DevSkyy/pull/970

- Branch: `codex/v2-home-layout-repair-20260922`.
- Last recorded head: `274a4899629ada4be4f3c7f7f8de518982ed4b79`.
- Converted to **draft after Corey's rejection**; not merged.
- Narrow fixes changed story portrait to a contained side-by-side layout, contained journal artwork, and adjusted control fonts. They passed technical checks but did not satisfy the design request.
- Its 566-file package SHA-256 was `fb1220db95cceb65dd6a8b441a1268d9dda134ed741e6930f7fe4afc07c6b698`.
- **Do not deploy that archive or treat its screenshots as an approved direction.**

The PR-green agent was told to stop. Last recorded CI had a canceled Security Scan after the 15-minute job limit and Playwright pending; most other checks passed. Recheck remotely if relevant, but do not spend remaining work rescuing a rejected design. Supersede it with the new full-site PR.

Historical PR968 merged as `2bb28983e99c52f851945c6ba9a03e3c78364de6`; PR964 merged as `15d6f012a`. These are prior work, not completion of the new design.

An older pre-PR964 `front-page.php` has the House of Roses hero, filmstrip, product portals, Kids Royal Procession, and Jersey Series tour. It can provide structural/motion reference. Do not restore the old theme wholesale: that could regress later security, accessibility, commerce, source authority, and copy changes.

## 6. Current staging and deployment evidence

Staging: `https://staging-7e48-skyyrose.wpcomstaging.com`, site ID `256563697`.

Last recorded deployed state: **the original 563-file theme was restored and is active**. The previously approved 566-file candidate is preserved separately on the server. No new whole-site changes have been deployed. Production and database/payment settings were not changed.

The prior exact-hash deployment/rehearsal used archive SHA-256:

`37f0d6f7d7b11b55f359c59c2932c761630d64c171169f8d40fd0a00e342a9cb`

Apply, rollback, and reapply manifest checks passed, then the theme was rolled back for safety after inconsistent public CSS delivery. Final recorded rollback: September 22, 2026 at 10:31:45 UTC.

Evidence and helper locations:

- `/tmp/skyyrose-v2-deploy-20260922/deploy.py`
- `/tmp/skyyrose-v2-deploy-20260922/{prepared,applied,reapplied,rolled-back,baseline-manifest}.json`
- `/Users/theceo/.codex/worktrees/v2-readiness-performance/DevSkyy/.artifacts/v2-deploy-20260922/REPORT.md`

The old script hardcodes the old SHA and deployment ID. **Do not reuse it unchanged for the redesign or rerun its prepare phase against existing state.** Inspect actual server directories and preserve both baseline and candidates before preparing a new deployment.

Last recorded remote layout:

- Active: `/srv/htdocs/wp-content/themes/skyyrose-flagship-2` — original restored theme.
- Candidate hold: active path plus `.candidate.approved-37f0d6f7-20260922` — old 566-file candidate.
- Old backup rename path was absent after rollback; original content is active. Verify afresh before rename operations.

### Cache issue still needs resolution

The same optimized CSS URL `/_jb_static/??96139caa5c` delivered different content to different request profiles. A Python request saw 265,710 characters with the film selectors; fresh Chromium saw 254,467 characters without them. The latter produced a roughly 21,215-pixel homepage and a static film layout despite correct deployed file hashes. The precise upstream cause is unresolved.

`wp cache flush` clears object cache and was not proof of edge-cache purge. Fresh no-cache browser requests restored the expected original-theme layout after rollback. Do not equate a cache-busting query or forced no-cache request with healthy ordinary visitor delivery.

Corey is signed into the **WordPress native app** (`com.automattic.wordpress`). The browser hosting dashboard was not established as authenticated. Do not ask for passwords or assume app authentication automatically transfers to another browser.

The local WordPress API token returned 401 once; do not keep retrying stale credentials. A staging guard blocked outbound hosting API delivery with `skyyrose_staging_egress_blocked`; **do not disable that guard or impersonate another user**.

Official WordPress.com hosting purge endpoint was verified from Automattic/wp-calypso source:

`POST https://public-api.wordpress.com/wpcom/v2/sites/256563697/hosting/edge-cache/purge`

It was not successfully executed in the recorded session. Use legitimate authenticated UI/API access and record actual outcome.

Read-only staging helper:

`/tmp/skyyrose-v2-readiness-20260921/remote-read.py`

It uses `/Users/theceo/DevSkyy/.env.wordpress.staging` via dotenv and secret-safe SSH environment passing. Run with `/Users/theceo/DevSkyy/.venv/bin/python`. Never print credentials or include them in artifacts.

## 7. Baseline browser evidence

Latest completed baseline artifacts:

`/tmp/skyyrose-whole-site-20260922/`

Contains `baseline.cjs`, `baseline.log`, `browser-results.json`, and desktop/mobile screenshots for homepage, selected collections, Kids world, shop, cart, and checkout. The log's final seven mobile routes all completed with HTTP 200 and zero recorded JS errors/bad requests. The full run targeted 24 desktop states at 1440px and seven mobile states at 390px.

A durable copy of those files is saved beside this handoff in `baseline-evidence/`; prefer that copy if `/tmp` has been cleaned. These are baseline screenshots of the existing site, not redesigned previews. Handoff and evidence are saved locally and are uncommitted.

Some desktop supporting pages recorded JSON parse errors involving `[object Object]`, `ready`, and `cookie-auth-missing`. The cause was not isolated; obtain stack traces and reproduce before attributing these to theme code. The deliberate missing-route probe returned the expected 404.

The capture waits were short and full-page screenshots did not guarantee all lazy media had loaded. Scroll and wait for images/videos/fonts before judging blank media or capturing final evidence. Public page loads do not establish checkout/payment success.

## 8. Implementation entry points

Theme: `wordpress-theme/skyyrose-flagship-2/`.

Current homepage `front-page.php` composes:

- `template-parts/home/editorial-hero.php`
- `editorial-collection.php`
- `editorial-product-edit.php`
- `editorial-philosophy.php`
- `editorial-journal.php`
- living archive worlds inside a details element.

The current hero has a background scene/video, animated title, three-product duplicated filmstrip, collection rail, CTA group, motion control, and `#skyy-hero-stage`. Preserve functional data attributes, the mascot mount, bootstrap, real destinations, and accessibility while recomposing.

Primary styles to inspect: `assets/css/home-page.css`, `global-shell.css`, `design-tokens.css`, `shop-page.css`, `product-page.css`, `collection-world.css`, `hero-commerce-scenes.css`, `collection-scene-motion.css`, `immersive.css`, `lookbook.css`, `about-archive.css`, `content-page.css`, `premium-commerce.css`, `controls.css`, `mascot.css`, and `theme.css`. Inspect enqueue order in `functions.php` and build projections before adding overrides. Fix structure/cascade coherently rather than layering another disconnected CSS patch.

Potential local actual-template renderer: `tools/v2-theme-preview.php`. It requires `.fashion-theme/codex-desktop-handoff.json` with candidate ID and branch, and binds the current commit. It fails closed if identity is missing. Inspect its stubs and compatibility first; it is a preview fixture, not WordPress commerce proof.

It exposes `?route=` for home, collections, each collection, immersive worlds, shop, product, pre-order, about, journal, contact, wishlist, FAQ, policy pages, cart, checkout, account, tracking, and 404. Product state can use `?sku=` and `?state=`. `tools/verify-v2-theme-preview.sh` is an existing preview check. The earlier preview server on port 18722 was stopped; no new preview server was started.

## 9. Build and verification environment

Use the V2 package manifest as command authority. Existing dependencies are installed there. Known working toolchain:

- Node 22.23.2 via `/Users/theceo/.local/bin`; default Node 26 failed the source gate.
- Python/tooling via `/tmp/skyyrose-v2-audit-venv/bin`.
- Native WordPress fixture: `/tmp/skyyrose-v2-native-fixture`.
- Playwright available from `/Users/theceo/DevSkyy/node_modules/playwright`, with Chromium and WebKit available.
- Lighthouse 13.5 at `/tmp/skyyrose-v2-audit-tools/node_modules/.bin/lighthouse`.

From the V2 directory:

```sh
PATH=/tmp/skyyrose-v2-audit-venv/bin:/Users/theceo/.local/bin:$PATH V2_WP_FIXTURE=/tmp/skyyrose-v2-native-fixture npm run build
PATH=/tmp/skyyrose-v2-audit-venv/bin:/Users/theceo/.local/bin:$PATH V2_WP_FIXTURE=/tmp/skyyrose-v2-native-fixture npm run verify
PATH=/tmp/skyyrose-v2-audit-venv/bin:/Users/theceo/.local/bin:$PATH V2_WP_FIXTURE=/tmp/skyyrose-v2-native-fixture npm run package:theme
```

Inspect generated diffs. Critical CSS has a 16,384-byte budget; the earlier base was close to that limit. Do not silently remove critical behavior to fit the budget. Source changes require regenerated committed minified outputs and any intended critical projections.

## 10. Review, release gates, and remaining readiness gaps

1. Establish an explicit design contract from the accepted blended direction, with desktop/mobile page families and preservation inventory.
2. Implement the whole-site system using actual source templates and approved media. Inspect every affected family visually, including scrolled/lazy-loaded states.
3. Exercise navigation, search, collection links, product variation selection, cart, checkout validation, account, forms, error states, keyboard access, focus, reduced motion, and responsive behavior. Record what was actually exercised.
4. Run relevant source/build/registry/package checks. Record the new archive count and SHA from actual output; do not assume 566 files remains the correct count.
5. Obtain independent code review. The explicitly invoked requesting-code-review skill requires a reviewer; pass a bounded brief and founder/SOT rules. Use specialist review for edited languages where required. Fix material findings.
6. Create a new PR with actual screenshots, source changes, tests, and deployment implications. Supersede rejected draft PR970. The user explicitly requested a PR-green agent; use it to fix the new PR until required checks and actionable reviews are resolved. Merge only after fresh checks on the current head, no unresolved conflicts or blockers.
7. Deploy corrected work to staging under existing conditional authorization. Preserve the original, verify archive and remote hashes, handle caching legitimately, and verify ordinary fresh desktop/mobile browsers before claiming deployment healthy.
8. Measure deployed performance in controlled repeated runs. Keep fixture, lab, and field evidence separate. TBT is a lab diagnostic, not the field INP metric. Earlier reported LCP 5.2 seconds / TBT 540 ms / CLS 0 is historical; no new pass has been established. Do not claim Core Web Vitals compliance from one Lighthouse run.
9. Keep target-environment readiness distinct: actual backup restoration, rollback, monitoring/alert delivery, production indexing, and final commerce acceptance remain separate gates. Theme rollback was rehearsed; that does not prove full database/site restoration. Production and payment-setting changes remain outside approval.

Verified documentation/reference sources to use alongside actual test evidence:

- Core Web Vitals thresholds: https://web.dev/articles/defining-core-web-vitals-thresholds
- WordPress.com cache clearing: https://wordpress.com/support/clear-your-sites-cache/
- WP-CLI object cache flushing: https://developer.wordpress.org/cli/commands/cache/flush/
- Image fitting behavior: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/object-fit#values

Sources explain guidance; they are not proof that our implementation or authenticated operation succeeded.

## 11. Skills and evidence standard

The canonical luxury-design skill was read and its use announced:

`/Users/theceo/DevSkyy/.agents/skills/luxury-design-taste/SKILL.md`

The user invoked requesting-code-review; its read location was:

`/Users/theceo/.codex/plugins/cache/claude-plugins-official/superpowers/6.3.0/skills/requesting-code-review/SKILL.md`

For skill creation, revision, audit, or adoption, read:

`/Users/theceo/.codex/skill-standards/verified-examples.md`

Every claimed skill must have identifiable, task-specific evidence for a correct example and an incorrect example with correction/reason. Label illustrative negatives. Distinguish source-verified guidance, historical observation, reproduced test, and authenticated live execution. Record redacted intended account/environment/scope for authenticated workflows; offline work is authentication not applicable. Maintain canonical sources or overlays, never silently edit disposable plugin caches. Do not claim the whole skill library is compliant without checking it.

The earlier reusable production-coding-skill request is part of the broader conversation, but its completion is not established by this handoff. Do not silently claim it delivered or let it displace the immediate site rework.

## Resume instruction

Continue on `codex/v2-whole-site-rework-20260922` in the isolated worktree. Read this handoff and current governing files, verify fresh Git/deployment state, then implement the approved Veritas-composition/SkyyRose-identity redesign across the site. Do not restart the rejected portrait-only repair. Do not deploy either historical 566-file archive. Finish the new design and verification, run the requested PR lifecycle, and use the existing conditional staging authorization once corrected work is actually ready. Keep production-readiness claims limited to evidence.
