# SkyyRose V2 Page + Imagery Plan

> **SKYYROSE LLC · FASHION THEME BRAIN**  
> *Luxury Grows from Concrete.*

Status: **planned, not implemented**. This is the visual and commerce brief for V2. It does not assert that a page, integration, product, or image exists.

## Creative thesis

V2 is Oakland-rooted luxury streetwear: the garment is the protagonist, concrete provides the structure, monumental typography creates recognition, and rose gold is the single accent. The reference set is Kith for merchandising discipline, Oaklandish for place, Culture Kings for energetic retail, Fear of God for restraint, and Palm Angels for editorial tension. These are moves to study, not identities to copy.

Every final product image must resolve through the SkyyRose source of truth. Editorial photography must be rights-cleared. New renders require founder approval before generation or publication.

## Page map

| # | Page | Section order | V2 imagery direction |
|---:|---|---|---|
| 01 | Global shell | Announcement → masthead → notices → page slot → service footer → drawers | No hero; approved monogram or concrete-line device only. |
| 02 | Home | Thesis hero → collection gateways → curated products → shoppable editorial → proof → trust → invitation | Oakland establishing frame, verified hero garment, construction macro, movement, process/community. |
| 03 | Shop | Title/count → categories → controls → active filters → grid → editorial insert → pagination | Consistent SOT card crops; one rights-cleared detail insert. |
| 04 | Collection | Thesis hero → chapters → controls → grid → story break → context → verified alternate path | Collection wide, portrait, fabric macro, styling pair, Oakland location detail. Every supporting path requires a catalog relationship ID and availability proof. |
| 05 | Search | Search field → summary → scope → controls → results → recovery | Verified result-card media only; optional approved line mark for empty state. |
| 06 | Product detail | Gallery + decision zone → trust → story → specifications → fit → reviews → styling → style evidence | Ten-frame SKU sequence: front, back, side, three-quarter, detail, fabric, hardware, on-body scale, movement, styling. |
| 07 | Quick view | Compact media → identity/price → variation/size → availability → action → PDP link | First approved PDP frame plus one alternate angle. |
| 08 | Compare | Selected items → matched media → price → attributes → fit → availability → fulfillment → actions | Identical angle, scale, crop, and background across SKUs. |
| 09 | Lookbook | Thesis → scene chapters → annotations → outfits → credits → commerce | Oakland street wide, architecture crop, full look, movement, detail, group composition. |
| 10 | Campaign / drop | Thesis → release facts → rights → assortment → proof → terms → service → fallback | Rights-cleared film still, release macro, full-look frames, product lineup. |
| 11 | About | Thesis → founder → Oakland → values → timeline → craft → community → press → contact | Founder portrait, Oakland context, studio/process, archive, documented community work. |
| 12 | Journal index | Feature → categories → article grid → pagination → search | Story hero, portrait, object study, or place frame in consistent crop families. |
| 13 | Journal article | Header → credited hero → body → captioned media → verified alternate path → adjacent articles → corrections | Story-specific plates with photographer, subject, date, place, and rights recorded. |
| 14 | Size & fit | Category → units → tables → method → ease → models → conversions → help | Measurement diagrams, annotated flat garment, diverse model references with exact worn size. |
| 15 | Wishlist | Summary → products → changes → controls → cart → sharing → recovery | Current verified product-card media only. |
| 16 | Cart | Notices → items → quantity → coupon → shipping/tax → totals → checkout → verified alternate path | Exact variation thumbnails; alternate items appear only with a catalog relationship ID, source SKU, reason, and availability proof. |
| 17 | Checkout | Focused header → errors → contact → addresses → delivery → summary → payment → terms → order | Line-item thumbnails and approved payment marks only. |
| 18 | Confirmation | Status → reference → receipt → delivery → payment → next steps → account → help | Purchased-item thumbnails; optional approved package detail after facts. |
| 19 | Account | Auth → dashboard → orders → downloads → addresses → payment → preferences → privacy | No independent editorial; purchased-item thumbnails in history. |
| 20 | Returns | Policy → item selection → eligibility → reason → resolution → logistics → review → status | Order thumbnails; accurate package or label diagrams only. |
| 21 | Service | Navigation → FAQ → policies → channels → form → order context → escalation | Photography optional; resolution stays primary. |
| 22 | Stores / appointments | Search → list/map → facts → services/accessibility → hours → booking → confirmation | Exterior, interior, service area, accessible entrance, neighborhood context per location. |
| 23 | Gift card | Amount/design → recipient → schedule → message → terms → preview → purchase | Approved type, monogram, and concrete texture system; no invented product art. |
| 24 | Loyalty | Benefits → eligibility → earn/redeem → terms → activity → preferences → leave | Real member or benefit evidence only; otherwise typography-led. |
| 25 | Preorder / waitlist | Status → timing → payment/cancellation → variation → consent → confirmation → management | Current SOT media with explicit status; no speculative colorways. |
| 26 | Coming soon | Identity → launch status → access form → service → privacy | One approved teaser crop; motion requires a poster fallback. |
| 27 | 404 / empty | Status → preserved context → recovery → search/category/service | Approved monogram, rose line drawing, or concrete texture. |
| 28 | Legal / policy | Title/date → contents → document → regional disclosures → contact → history | No photography; typography, rules, and one restrained brand mark. |

## Responsive rules

- Desktop composition may be cinematic; mobile must remain decisive. Product, price, fit, availability, terms, and primary action move ahead of atmosphere.
- Tablet is a first-class 768px art direction, not a compressed desktop: measured two-column regions only when content fits, and linear forms remain linear.
- A desktop hotspot becomes a labeled product list on mobile. A film becomes a poster image under reduced motion or constrained bandwidth.
- Editorial crops require a separate portrait art direction when the focal garment cannot survive center cropping.
- Commerce forms stay linear, error-linked, keyboard operable, and free of decorative imagery that competes with completion.

## Visual production checklist

1. Resolve every SKU and image to the canonical catalog and image manifest.
2. Record rights, creator, subject, location, capture date, and allowed usage for editorial media.
3. Approve crop families before shooting: landscape thesis, portrait commerce, square card, macro detail, and motion poster.
4. Capture fit truth: model measurements, worn size, garment measurements, silhouette, and ease.
5. Produce desktop and mobile review images for every core page plus loading, empty, error, unavailable, long-content, keyboard, and reduced-motion states.
6. Treat this plan as an input to design—not release evidence. Publication still requires founder approval and the full Fashion Theme Team gates.

## Contract additions (machine-bound)

The companion JSON is validated by v2-page-plan.schema.json. It is a planned, not implemented, contract; every route remains planned-not-implemented until candidate-bound browser evidence exists.

### Recognition and token contract

Logo-independent recognition uses five devices: concrete/asphalt hairlines, Archivo + Anton scale contrast, Oakland civic/place proof, the thesis-wide → commerce-portrait → SKU-truth shot sequence, and asymmetric 60/40 rhythm with one resolved collection accent. Global chrome resolves to canonical --color-* semantics from assets/css/design-tokens.css; collection routes resolve exactly one accent and dark accent from the identity records:

| Collection | Accent | Dark accent | Lockup source | Media status |
|---|---|---|---|---|
| Black Rose | #C0C0C0 | #999999 | data/logo-registry.json → collections.black-rose | interim-pending-mj, non-shippable |
| Love Hurts | #DC143C | #9B0F2E | data/logo-registry.json → collections.love-hurts | interim-pending-mj, non-shippable |
| Signature | #D4AF37 | #B8960C | data/logo-registry.json → collections.signature | interim-pending-mj, non-shippable |
| Kids Capsule | #B76E79 | #B8960C | data/logo-registry.json → collections.kids-capsule | interim-pending-mj, non-shippable |

Canonical type roles are Archivo display, Hanken Grotesk body, and Anton utility. Cinzel is limited to approved caps contexts; European-maison serif direction, cut display fonts, and type-rendered collection scripts are prohibited. Components consume semantic token aliases and never introduce page-local raw values.

### Imagery provenance contract

Every shot resolves by page_id/shot_id through repo://data/sot-images.json for product media or the approved rights ledger for editorial media. Each manifest row must carry asset_id, exact sku_refs, rights_record, creator, location, capture_date, status, crop_family, mobile_fallback, and review_after. interim-pending or expired rows fail closed; descriptive shot ideas are not publication permission. New renders stay review-only pending founder approval and independent visual QA.

### Responsive, state, CTA, and motion matrices

Every page entry carries all three viewports:

| Viewport | Required transformation |
|---|---|
| 390px | Portrait-first single column; product, price, fit, availability, terms, and primary action lead; labeled rails; static media fallback. |
| 768px | Measured two-column regions only when content fits; touch/keyboard parity; tablet crop preserves the garment focal point. |
| 1440px | 60/40 or ledger composition; one restrained showpiece; DOM-first commerce facts and static fallback remain visible. |

Required states are loading, empty, error, unavailable, success, keyboard, and reduced motion. CTA state rows cover default, hover, focus-visible, active, loading, success, disabled, unavailable, error, and reduced motion. Async controls acknowledge loading within 100ms, retain an accessible name, announce results in a live region, and never gate purchase or service on movement.

Motion is limited to one showpiece per route, one active section, 160/360/600ms canonical durations, opacity/transform properties, and at most three staggered items. Cancel on route change, unmount, visibility change, resize, Escape, pointer cancel, or preference change. Reduced motion uses the same DOM, captions, facts, focus path, and CTA states as the static route.

### Rhythm and verification matrix

Each route records desktop/tablet/mobile rhythm, a maximum of two repeated identical rows, one authored editorial interruption, featured scale, and filter priority. The route/viewport/state matrix is:

| Coverage | 390 | 768 | 1440 |
|---|---|---|---|
| Core routes (all 28) | fresh capture + loading/empty/error/unavailable | fresh capture + loading/empty/error/unavailable | fresh capture + loading/empty/error/unavailable |
| CTA and forms | keyboard/focus/announcement trace | keyboard/focus/announcement trace | keyboard/focus/announcement trace |
| Motion | reduced-motion static equivalence | reduced-motion static equivalence | reduced-motion static equivalence |
| Media | crop/fallback/overflow check | crop/fallback/overflow check | crop/fallback/overflow check |

Evidence is UNVERIFIED until the same candidate snapshot has jq/schema output, fresh captures, keyboard/focus/overflow/contrast checks, reduced-motion evidence, and an independent design-qc verdict. This document cannot approve its own pixels.

Machine-readable companion: [`v2-page-plan.json`](v2-page-plan.json). Visual companion: [`../showcase/v2-page-atlas.html`](../showcase/v2-page-atlas.html).
