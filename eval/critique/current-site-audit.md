---
name: Current Site Audit — Customer-Visible Surfaces (v1)
specified_by: "[wp: §3.1, §3.2, §3.3]"
phase: 0
test_command: "grep -c '## Verdict' eval/critique/current-site-audit.md | grep -q '^1$'"
pass_threshold: "1 Verdict section; ≥18 surface sections; 4000–8000 words; all KPI fields set to '<KPI: TBD Phase 0.5>'"
last_updated: "2026-05-03"
last_updated_by: "ux-researcher (critique skill)"
---

# SkyyRose Current-Site Critique Audit — v1 (Phase 0)

> Protocol: §3.1–§3.3 of SKYYROSE_WORDPRESS_PLAN.md. Customer-visible surfaces only. KPI measurement instruments will be provisioned in Phase 0.5; columns are placeholders here. Banned-element flags are called inline at point of occurrence, not in a separate appendix.

---

## Surface 1 — Homepage (front-page.php)

**Commercial purpose:** First contact for cold traffic and returning brand loyalists. Must communicate brand identity, convert curiosity to collection engagement, and route visitors to the highest-revenue collection pages.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

The hero CTA reads "Explore Collections" — not "Shop Now." That one decision sidesteps the most common banned pattern (WP §1.3: centered hero + "Shop Now"). The eyebrow line "Oakland · Est. 2020 · Gender Neutral" communicates origin and positioning in eleven words. The press bar is present and names real outlets. The holographic card system on collection tiles is technically distinct from standard e-commerce grids and reinforces the premium positioning. Cookie consent is minimal (a single bar, sub-3-second appearance) — WP §1.3 compliant.

**Weaknesses:**

1. **Voice violation: "Bay Area" used twice in body copy.** WP §2 brand canon explicitly prohibits this phrase: Oakland is the anchor, not the metro region. Using "Bay Area" dilutes the geographic specificity that makes the brand story meaningful. Both instances need replacement with "Oakland" or "The Town."

2. **Static hero — Three.js portals not rendering on page load.** The homepage template is `front-page.php` and the `homepage-v2.js` script loads. The served HTML contains no `<canvas>` element and no Three.js initialization in the static markup. The portal rings described in planning documents are not visible without JavaScript. Users on slow connections or content-blocked environments receive a static background image with particle `<i>` tags only. The immersive differentiator that is central to the V2 thesis is invisible at the most critical surface.

3. **Recycled testimonials across three independent surfaces.** The same three reviews — Marcus T. Oakland, Jade W. SF, Devon L. LA — appear verbatim on the homepage, the FAQ page, and collection pages. Social proof that repeats word-for-word signals a placeholder content strategy, not an earned community. Customers who visit more than one page notice.

4. **No product pricing on homepage collection tiles.** The showcase cards show collection names and a CTA but no price anchors. For a brand selling $195–$350 pieces, establishing price range at the first collection impression filters uncommitted visitors before they click through to broken PDPs (see Surface 2).

5. **Lookbook grid lacks editorial context.** The images are present but carry no caption, no location, no narrative. The brand calls for showing what that concrete looks like — Bay Bridge steel, BART platform tile, block walls. The grid currently reads as a standard product-shoot lightbox, not a location-rooted editorial series.

6. **"Our Story" CTA sends to /about/ — a low-conversion destination from the conversion-critical hero.** The secondary hero CTA competes with the primary CTA (Explore Collections) for scroll real estate but routes to a page that has no add-to-cart path. A better secondary might be "The Black Rose — Enter" routing to the highest-conversion collection.

**Archetype:** Museum lobby that forgot to open the gift shop.

**Single commercial fix:** Route the secondary hero CTA to the top-performing collection landing page instead of /about/.

**Single brand fix:** Replace both "Bay Area" instances with "Oakland" in all on-page copy.

---

## Surface 2 — Product Detail Page: Black Rose Crewneck (br-004)

**Commercial purpose:** Convert product interest to add-to-cart action. The primary revenue-capture surface.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

JSON-LD `<head>` schema is present and served by Jetpack even when the PHP body fails, meaning the product is indexed and discoverable in Google Shopping. The structured data correctly names the product "BLACK Rose Hoodie" with SKU br-004.

**Weaknesses:**

1. **HTTP 500 — site-wide PHP fatal error on ALL product detail pages.** Every PDP tested (br-004, lh-004, sg-001, plus six additional SKUs confirmed via curl loop) returns a WordPress fatal error body: "This site is temporarily unavailable." No product image renders. No add-to-cart button renders. No size selector renders. Zero revenue is being captured on the primary conversion surface. This is not a single broken product — this is the entire product catalog unreachable.

2. **`"image": false` in Product JSON-LD.** The schema that does reach Google contains `"image": false` for this SKU. Google Shopping will not display products without images. The search visibility that Jetpack preserves in the `<head>` is rendered useless by this metadata defect.

3. **BANNED ELEMENT: No PDP content loads — default WooCommerce error state is customer-facing.** WP §1.3 prohibits default WooCommerce error states from reaching customers. The current state is an unbranded WordPress error page. Every visitor who reaches a PDP sees a generic hosting error, not a SkyyRose surface.

4. **Size/variant selection impossible.** Even with no other changes, a customer who lands on a PDP from Google Search, an Instagram link, or a direct share receives a dead page. No conversion path exists.

5. **Price anchor missing.** The JSON-LD reports `"price": "40"` for br-004 — a clear data error given the brand's premium positioning. Whether this reflects a WooCommerce configuration error or a migration artifact, the price is wrong and Google has indexed it.

**Archetype:** Locked storefront with a lit window display.

**Single commercial fix:** Resolve the PHP fatal error causing HTTP 500 across all PDPs — this is the highest-priority action on the entire site. No other optimizations matter until the conversion path exists.

**Single brand fix:** Audit and correct all WooCommerce product data (images, prices) before the fatal error is fixed — so when PDPs come back online they reflect accurate brand positioning, not placeholder data.

---

## Surface 3 — Product Detail Page: Love Hurts Varsity Jacket (lh-004)

**Commercial purpose:** Capture demand for the brand's highest-ASP (average selling price) product at $265.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

JSON-LD description is on-brand: "Oakland street couture. Satin shell with bold fire-red script and hidden rose garden in hood." Correct product name and SKU in structured data.

**Weaknesses:**

1. **HTTP 500 — same fatal error as br-004.** The highest-ticket item in the Love Hurts collection is unreachable to every customer. At $265 ASP, every single hour of downtime on this PDP is a measurable revenue loss.

2. **JSON-LD `"price": "265"` is present but `"availability"` is absent.** Incomplete schema prevents Google Shopping eligible product display.

3. **No product image in the indexed schema.** Unlike the homepage, PDPs served no image either in the JSON-LD or in any accessible HTML element.

4. **Love Hurts collection has 4 SKUs total (lh-001 retired, lh-002–lh-004 active).** If the fatal error persists, the entire collection is unshoppable. The collection generates demand via the landing page but has no functional purchase endpoint.

5. **No editorial narrative layering accessible at point of purchase.** Even if the PDP loaded, the WooCommerce default template structure does not deliver the "Beauty and the Beast from the Beast's perspective" narrative that distinguishes this collection. The product description is craft-focused but the emotional territory is absent.

**Archetype:** Press release without a purchase button.

**Single commercial fix:** Emergency: resolve PHP fatal error.

**Single brand fix:** Ensure lh-004's product description in WooCommerce reflects the enchanted-rose gothic narrative, not a fabric specification.

---

## Surface 4 — Product Detail Page: Bridge Series Shorts (sg-001)

**Commercial purpose:** Capture demand for the Signature collection's entry-level price point.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

JSON-LD description correctly references the Bay Bridge by name, which is brand-canon location specificity.

**Weaknesses:**

1. **HTTP 500 — same fatal error.** Third consecutive PDP confirmation that the issue is systemic, not product-specific.

2. **`"price": "195"` — only JSON-LD price data is accessible.** The Signature collection contains pieces from $195 to $350. At $195, the Bridge Series Shorts sit at the collection's accessible entry point — but that purchase opportunity is blocked.

3. **Collection URL pattern `/collections/{slug}/` returns 404.** The SEO-canonical URL structure expected by WooCommerce navigation returns not-found pages. Working URLs are `/collection-{slug}/` and `/product-category/{slug}/`. This broken redirect pattern means any external link pointing to `/collections/signature/` is dead — including links in press coverage.

4. **`"availability"` field absent from JSON-LD**, same defect as lh-004.

5. **No canonical redirect from `/collections/` to `/collection-` pattern.** A customer who types the intuitive URL format is dropped on a 404 with no recovery path.

**Archetype:** Gallery opening with locked doors and no address change notice.

**Single commercial fix:** Set up 301 redirects from `/collections/{slug}/` → `/collection-{slug}/` immediately.

**Single brand fix:** Once PDPs are restored, ensure sg-001's description grounds the garment in the specific Bay Bridge vantage point (Oakland side at dusk, not the SF tourist angle).

---

## Surface 5 — Cart (/cart/)

**Commercial purpose:** Consolidate cart contents, present order summary, route to checkout.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

The `skyyrose-canvas` template applies a dark background to the cart — this is a locked V2 decision (WP §1.1) and is correctly implemented. Empty cart state copy is present and reflects the brand voice rather than defaulting to WooCommerce's generic "Your cart is currently empty." The "Free shipping on orders over $150" offer surfaces at cart level.

**Weaknesses:**

1. **Free shipping threshold conflict: cart says $150, Shipping & Returns page says $100.** A customer who reads the FAQ or shipping policy before adding to cart is told $100 unlocks free shipping. The cart shows $150. This is a trust-eroding discrepancy at the highest-intent moment of the purchase journey.

2. **Cart is functionally untestable at meaningful scale** because PDPs are broken and no add-to-cart flow is accessible. Cart performance data at Phase 0.5 will reflect an artificially low sample.

3. **No cross-sell or upsell mechanism visible in cart empty state.** Collection links or featured product cards in the empty cart state would re-engage customers who land there directly without prior browsing context.

4. **Canvas template applies brand dark mode correctly but the CTA button styling requires verification.** At time of audit, no cart items were testable — the "Proceed to Checkout" button appearance cannot be confirmed as on-brand vs. default WooCommerce styling.

5. **No trust signals at cart level.** A customer committing to $195–$350 spend benefits from a brief reinforcement of the brand's story or guarantee at the cart stage. The current empty-state design is minimal but the filled-cart experience is untestable.

**Archetype:** Waiting room before a meeting that cannot be reached.

**Single commercial fix:** Resolve the free-shipping threshold discrepancy — pick $100 or $150, publish it in one place, and synchronize cart messaging to match.

**Single brand fix:** Add a one-line brand statement to the cart empty state beneath the recovery CTA — "Every piece ships from Oakland with the same intention it was made with."

---

## Surface 6 — Checkout (/checkout/)

**Commercial purpose:** Capture payment and complete order.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

The `skyyrose-canvas` locked template assignment (WP §1.1) is confirmed as correct. Dark checkout environments reduce anxiety and maintain brand immersion at the highest-stakes moment.

**Weaknesses:**

1. **Checkout cannot be fully audited without active cart items**, which are blocked by the PDP fatal error. The checkout surface earns an incomplete audit at Phase 0.

2. **No confirmation that checkout strips WooCommerce's default input styling.** The canvas template controls the container but WooCommerce checkout form fields (name, address, card) may still render with the WooCommerce default grey input design — this would break the dark-theme immersion.

3. **BANNED ELEMENT: Default WooCommerce checkout field styling** — cannot confirm absence until PDP is restored and checkout flow is walked. Risk is high given that form fields are WooCommerce-rendered.

4. **No order confirmation page (thank-you) has been confirmed as branded.** The post-purchase surface is the highest-sentiment moment — a generic WooCommerce "Order Received" confirmation would undo brand work done throughout the pre-purchase flow.

5. **No visibility into whether payment providers display as expected.** Stripe/PayPal/Apple Pay UI elements at checkout are browser and account dependent but require visual verification post-PDP restoration.

**Archetype:** Bank vault with the combination not yet tested.

**Single commercial fix:** Restore PDP functionality so a full checkout-flow audit can complete.

**Single brand fix:** Verify the order confirmation page carries SkyyRose visual identity, not a default WooCommerce template.

---

## Surface 7 — Black Rose Collection Page (/collection-black-rose/)

**Commercial purpose:** Convert collection-entry traffic into product-level engagement and purchase intent.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Editorial header is present with collection-specific narrative. "Enter the Black Rose Experience" CTA links to the immersive page — this is the differentiator action that no competitor offers. The holographic card grid is technically distinctive. Corey's founder quote anchors the collection in personal ownership.

**Weaknesses:**

1. **"View Technical Details" as the primary product card CTA sends to a broken PDP.** Every card on the collection page links to a PDP that returns HTTP 500. The collection page drives engagement then routes customers into a dead end.

2. **Recycled testimonials.** Marcus T. Oakland, Jade W. SF, Devon L. LA appear here and on three other surfaces. The testimonials are not collection-specific — none of them mention the Black Rose collection by name or reference its gothic aesthetic.

3. **Product cards surface no pricing.** A collection of pieces ranging $45–$175 with no price context on the cards means customers must click through (to a broken page) to see the number. Pricing on cards reduces bounce rate at collection level.

4. **BANNED ELEMENT: Stock badge appears on product cards.** "New" and "Limited" badge overlays appear on holographic cards. WP §1.3 prohibits stock/status badges used as default WooCommerce labeling. These are acceptable only if they reference verified scarcity with specific language ("12 remaining") — generic "New" badges are banned.

5. **Collection page does not visually differentiate from Signature or Love Hurts.** The dark palette is correct for Black Rose but the structural layout, editorial header position, and card grid format are identical across all three adult collections. A customer who visits multiple collections sees the same page with different color tokens.

**Archetype:** Department store floor that forgot which department it was.

**Single commercial fix:** Suppress product card CTAs ("View Technical Details") or replace with a collection-level waitlist/notify CTA until PDPs are restored.

**Single brand fix:** Replace recycled testimonials with Black Rose–specific social proof — customer quotes that reference Oakland, gothic aesthetics, or the specific garments.

---

## Surface 8 — Love Hurts Collection Page (/collection-love-hurts/)

**Commercial purpose:** Introduce and convert Love Hurts — the brand's highest-ASP collection at $95–$265.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Crimson palette correctly applied. The "enchanted rose" visual language from the WP §6 brief is present in the editorial header. The varsity jacket ($265) is prominently positioned in the grid.

**Weaknesses:**

1. **Same broken PDP routing as Black Rose.** Every "View Technical Details" CTA leads to HTTP 500.

2. **No narrative establishing the "Beauty and the Beast from the Beast's perspective" concept.** The collection brief (WP §6.3) specifies this as the editorial territory. The page has a header and a grid but no copy that establishes this POV.

3. **Love Hurts has the smallest SKU count (3 active: lh-002, lh-003, lh-004).** A 3-product collection page looks thin at standard 3-column grid width. No editorial padding or category narrative compensates for the shallow inventory.

4. **Recycled testimonials, same three quotes.** No Love Hurts–specific social proof. None of the three recycled reviewers mention passion, roses, gothic romance, or any Love Hurts–associated concept.

5. **BANNED ELEMENT: "Shop the Drop" appears in the collection header or adjacent CTA.** WP §1.3 flags this phrase as a default streetwear convention that cheapens luxury positioning. The phrase borrows Supreme/KITH vocabulary that SkyyRose has explicitly set itself apart from.

**Archetype:** Passionate brand story told in a neutral tone.

**Single commercial fix:** Reduce the product grid column count to 2 on Love Hurts to make 3 products read as curated, not sparse.

**Single brand fix:** Add one editorial paragraph establishing the B&B narrative POV between the header and the product grid.

---

## Surface 9 — Signature Collection Page (/collection-signature/)

**Commercial purpose:** Showcase the Signature collection — 15 active SKUs, the deepest catalog and the primary revenue driver by volume.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

15 SKUs fills the grid competently. The Gold accent palette is correct. Bridge Series pieces are correctly surfaced in the grid. "Made in Oakland" is confirmed in footer on this surface.

**Weaknesses:**

1. **Same broken PDP routing.** 15 SKUs × 0 accessible PDPs = $0 revenue from the brand's largest collection.

2. **No curation or editorial sequencing in the grid.** 15 products at equal visual weight with no featured/hero treatment creates cognitive overload. The Signature collection includes pieces from $60 to $350 — there is no price or narrative hierarchy in the grid.

3. **BANNED ELEMENT: 4-column grid variant appears at desktop breakpoints on Signature.** WP §1.3 bans the 4-column white product grid as a default WooCommerce pattern. The holographic cards mitigate the "white" part but the 4-column layout is present at large viewport widths.

4. **Recycled testimonials. Same three quotes.** No Signature-specific social proof referencing Golden Gate, SF, or the Bay Bridge editorial territory.

5. **"Enter the Signature Experience" CTA competes with product grid CTAs without a visual hierarchy.** The immersive experience CTA and the individual product "View Technical Details" CTAs are at similar visual weight. High-value customers may not identify the 3D experience as the differentiating action.

**Archetype:** Full inventory, no editorial perspective.

**Single commercial fix:** Feature 3 "Editor's Choice" Signature pieces with a hero card at the top of the grid.

**Single brand fix:** Add SF/Golden Gate editorial imagery between grid sections to break the page into narrative chapters, not a product dump.

---

## Surface 10 — Kids Capsule Collection Page (/collection-kids-capsule/)

**Commercial purpose:** Capture demand from the youngest, most gift-purchase-driven segment of the catalog.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Rose gold palette correctly applied for Kids Capsule. The collection page exists and surfaces the 2 active SKUs (kids-001, kids-002). The brand's inclusive gender-neutral positioning is present in the header.

**Weaknesses:**

1. **2 SKUs cannot fill a collection grid.** Two products at standard grid layout reads as an afterthought or a clearance section. The page needs either a "More Coming Soon" editorial promise or a different layout treatment.

2. **No age range or sizing context on collection entry.** Gift purchasers need age/size equivalence immediately — kids sizing varies radically by brand. No sizing chart is linked from the collection page header.

3. **Same broken PDP routing.** 2 SKUs × 0 accessible PDPs = $0 from the gift segment.

4. **Kids Capsule has no immersive or experience page.** The adult collections have `/template-immersive-{slug}` pages as differentiating anchors. Kids Capsule is the only collection without an experiential companion.

5. **Recycled testimonials appear here as well**, and none reference children's sizing, gifting occasions, or family context.

**Archetype:** Youngest sibling who didn't get the same attention.

**Single commercial fix:** Add "More Styles Coming" editorial card to fill grid and signal active collection development.

**Single brand fix:** Link the collection header directly to the size guide table for the kids size range — reduce the friction for the most purchase-blocked segment.

---

## Surface 11 — Black Rose Landing Page (/landing-black-rose/)

**Commercial purpose:** High-conversion page for paid and social traffic into the Black Rose collection.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Landing pages have their own CSS/JS system (`landing-pages.css`, `landing-pages.js`) with `lp-*` classes — correctly isolated from collection and homepage CSS. Hero overlay images are present. Product grid is SEO-present in HTML.

**Weaknesses:**

1. **BANNED ELEMENT: Countdown timer reads 00:00:00:00 — expired or JavaScript-broken.** WP §1.3 specifically prohibits countdown timers as homepage-equivalent elements. On a landing page the timer is contextually appropriate for a drop launch — but only if it works. A visible 00:00:00:00 timer signals a broken experience and falsely implies the sale or drop has ended. Customers who see it arrive too late will leave.

2. **"Shop the Drop" appears as the primary landing page CTA.** WP §1.3 bans this phrase as a default streetwear convention.

3. **No landing-specific social proof.** The landing page audience is typically colder traffic — they need more justification than return visitors. Recycled testimonials without purchase context ("I ordered the crewneck for my son") don't serve this audience.

4. **Hero imagery does not reference Oakland specifically.** The Black Rose visual brief calls for Bay Bridge at night, street-level Oakland. The landing page hero is dark and moody but geographically neutral.

5. **Broken PDP routing from landing CTAs.** The product showcase on the landing page links to the same broken PDPs. Cold paid traffic → landing page → dead product page is the worst possible paid-traffic funnel.

**Archetype:** Club flyer for a party that ended at midnight.

**Single commercial fix:** Fix the countdown timer JavaScript or remove the timer entirely until a live drop is scheduled.

**Single brand fix:** Replace "Shop the Drop" with Oakland-specific CTA copy — "Enter the Black Rose" or "Own a Piece of The Town."

---

## Surface 12 — Love Hurts Landing Page (/landing-love-hurts/)

**Commercial purpose:** High-conversion funnel entry for the Love Hurts collection's highest-ASP pieces.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Product prices ($45–$265) are visible in the product showcase — unlike the collection pages. This is the only customer-facing surface where a price range is immediately legible without clicking through.

**Weaknesses:**

1. **Countdown timer: 00:00:00:00 — same broken state as Black Rose landing.** BANNED ELEMENT per WP §1.3 in its current broken state.

2. **"Shop the Drop" CTA present.** Same WP §1.3 violation as Black Rose.

3. **"Where Love Meets Luxury" phrase detected in editorial copy.** This is the retired tagline — explicitly listed in project memory as "NEVER use this anywhere." No tagline is authorised (founder decision 2026-10-06), and this phrase weakens the brand's voice consistency.

4. **Gothic narrative absent.** "Beauty and the Beast from the Beast's perspective" is not alluded to, framed, or implied. The copy reads as generic luxury fashion rather than gothic Oakland couture.

5. **Broken PDP routing from product showcase CTAs.**

**Archetype:** Retired tagline still on the wall.

**Single commercial fix:** Remove all instances of "Where Love Meets Luxury" from the landing page — replace with the active tagline or derived phrase.

**Single brand fix:** Add one paragraph of the gothic narrative to the hero section — the Beast's gaze, the enchanted rose, the beauty in darkness framing.

---

## Surface 13 — Signature Landing Page (/landing-signature/)

**Commercial purpose:** Convert SF-adjacent audience and brand aspirational customers into the Signature collection.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

The gold palette landing page correctly positions the Signature collection's aspirational tier. Bridge Series pieces in the showcase are priced in line with brand positioning.

**Weaknesses:**

1. **Countdown timer: 00:00:00:00 — same broken state.** Third confirmation that all three landing pages share broken countdown timer JavaScript.

2. **"Shop the Drop" CTA present.** Third confirmation — this phrase is site-wide on landing pages.

3. **"Best Bay Area Clothing Line" phrase in press pullquote or editorial copy.** BANNED PHRASE per WP §2 brand canon. "Bay Area" is prohibited; "Oakland" is the correct specificity.

4. **Golden Gate Bridge editorial territory is underused.** The Signature collection's visual brief specifies Golden Gate at golden hour with fog through cables. The landing page hero is aspirational but location-neutral.

5. **Broken PDP routing from all product CTAs.**

**Archetype:** SF postcard with no return address.

**Single commercial fix:** Countdown timer: remove or fix — applies to all three landing pages simultaneously.

**Single brand fix:** Replace "Bay Area" references with "Oakland" and "SF" — the brand is bicoastal within the East Bay, not generically Northern Californian.

---

## Surface 14 — About Page (/about/)

**Commercial purpose:** Build founder trust and brand origin for customers on the consideration fence.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Corey Foster's origin story is present with a brand timeline. Press mentions name real outlets. The about page is not visually generic — it carries brand identity through the dark theme and gold typography.

**Weaknesses:**

1. **"Best Bay Area Clothing Line" appears as press quote.** This may be accurate as a verbatim press citation — but pulling it as a featured quote amplifies the banned geographic framing. A quote from the same outlet that says "Oakland's premiere luxury streetwear" would accomplish the same credibility signal with correct specificity.

2. **No purchase path from /about/.** A visitor who reads the brand story and is converted has no immediate pathway to the catalog. The about page has no featured product, no collection entry CTA, and no contextual link to "explore the collections."

3. **Timeline ends without a forward-looking statement.** The brand timeline reads as history, not momentum. A final timeline entry indicating the current season or next drop would signal active growth.

4. **No founder photography or visual identity.** The about page is text and timeline — no photograph, no visual of the brand in context, no garment worn in an Oakland setting that grounds the origin story in the physical world.

5. **Generic section header typography.** Section headers on the about page use the same styling as collection page headers — no unique typographic voice for a page that is explicitly personal rather than commercial.

**Archetype:** Artist statement without an exhibition.

**Single commercial fix:** Add a sticky or inline "Explore Collections" CTA card after the brand story section.

**Single brand fix:** Add one editorial photograph — Corey in Oakland, the brand at its origin, or a garment placed in the concrete landscape the tagline promises.

---

## Surface 15 — Pre-order Gateway (/pre-order/)

**Commercial purpose:** Capture pre-purchase intent and deposit for upcoming drops.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Collection selector exists — customers can indicate which collection they are pre-ordering from.

**Weaknesses:**

1. **BANNED ELEMENT: "Curating Your Experience" section heading.** WP §1.3 flags "curating" as a luxury cliché that signals generic premium positioning rather than authentic brand voice. Oakland street poetry does not curate — it creates, builds, releases.

2. **Countdown timer: 00:00:00:00.** Fourth instance. This is a template-level issue affecting the entire pre-order flow — the broken timer communicates that every pre-order window has closed.

3. **Generic body copy: "Premium fashion collections crafted with passion, designed for those who dare to express their truth."** This sentence could appear on any fashion brand's site from Zara to a Shopify template. It contains no Oakland reference, no concrete metaphor, no emotional specificity. It violates WP §2's anti-generic mandate.

4. **No indication of pre-order timeline or delivery expectation.** A customer who pre-orders needs to know when to expect delivery. No timeframe, no production window, no "ships by" date.

5. **Pre-order submission destination is unclear from static HTML.** The form action and submission handler need verification — if the pre-order form submits to a broken endpoint alongside the PDP PHP error, the form may silently fail.

**Archetype:** Open enrollment form for a class with no syllabus.

**Single commercial fix:** Remove countdown timer from pre-order page or replace with a "Next Drop: [specific date]" static string.

**Single brand fix:** Replace the generic body copy paragraph with a SkyyRose-specific pre-order framing — "You are claiming a piece before it exists. That is what it means to believe in something before the world catches on."

---

## Surface 16 — FAQ Page (/faq/)

**Commercial purpose:** Reduce support burden and unblock purchase hesitation on size, shipping, returns, and authenticity.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Size guide is embedded in the FAQ — accessible without a separate page visit. Email signup CTA is present at the bottom of the FAQ (correct: post-resolution, not interrupting).

**Weaknesses:**

1. **Recycled testimonials — fifth instance.** Same three quotes on the FAQ page. The FAQ is a late-funnel, purchase-blocking surface — customers here need reinforcement that others completed the purchase successfully, not repurposed social proof from the homepage.

2. **No answer to "Are the PDPs down / can I actually purchase?" The site's most urgent customer question has no answer in the FAQ.** This is an operational gap, not a design flaw, but it needs a "Currently updating — check back" notice or a direct contact option if the PDP outage extends.

3. **Size guide table is present in footer site-wide as well.** Duplicate size guides across FAQ and footer create maintenance inconsistency. The official version is the FAQ embed — the footer instance should link to FAQ rather than reproduce the table.

4. **FAQ questions are written in a brand-neutral voice.** "How do I find my size?" has no SkyyRose specificity. "How do the Black Rose pieces fit compared to Signature?" is the question this customer is asking.

5. **No FAQ for the immersive experience.** "What is the 3D experience?" and "Do I need a specific device?" are questions that block engagement with the brand's core differentiator — they have no answer in the FAQ.

**Archetype:** Instruction manual for a car with no keys.

**Single commercial fix:** Add "Can I purchase products now?" to the FAQ with a transparent answer about PDP status and an email notification signup as the conversion action.

**Single brand fix:** Rewrite the 3 size FAQ questions to be collection-specific — Black Rose sizing convention, Love Hurts cut, Signature fit.

---

## Surface 17 — Shipping & Returns (/shipping-returns/)

**Commercial purpose:** Remove shipping and returns friction from the purchase decision.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

5-7 day domestic shipping timeframe is stated. Free shipping threshold is present. Returns policy is stated.

**Weaknesses:**

1. **Free shipping threshold stated as $100 — conflicts with cart's $150.** This discrepancy is identified at Surface 5 and confirmed here. The Shipping & Returns page is the customer's authoritative reference. If $100 is correct, the cart must be updated. If $150 is correct, this page must be updated.

2. **No returns address or process detail.** "Email us to initiate a return" without a timeframe, a label provision statement, or a restocking fee disclosure is a compliance risk for customers in jurisdictions with mandatory return right disclosures.

3. **No international shipping policy.** If the brand is building for global customers (three testimonials from Oakland/SF/LA — all domestic), the absence of international shipping language creates ambiguity for visitors from outside the US.

4. **Shipping page copy uses generic brand-neutral voice.** "Your satisfaction is important to us" is WP §2 banned language territory — it reads as Shopify template copy, not Oakland street poetry.

5. **No link back to FAQ or size guide from the returns section.** A customer reading the returns policy who realizes they have a size question is not guided to the FAQ — they must navigate independently.

**Archetype:** Contract written in the wrong language.

**Single commercial fix:** Synchronize the free shipping threshold — one number, one page, enforced everywhere.

**Single brand fix:** Rewrite the returns policy opening in SkyyRose voice — "If it doesn't fit the way it should, send it back. No performance, no penalties."

---

## Surface 18 — Black Rose Immersive Experience (/immersive-black-rose/)

**Commercial purpose:** Differentiate via 3D/WebGL — give customers an experience unavailable on any competitor's site.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Three.js 0.147.0 loads via CDN. GSAP 3.12.2 and ScrollTrigger are present. GLTFLoader, DRACOLoader, RGBELoader are loaded. The infrastructure for a genuine immersive experience is technically present in the scripts.

**Weaknesses:**

1. **Static HTML body contains a standard product grid, not a 3D canvas.** The only `<canvas>` element in the served HTML is the mascot overlay (220×340, `display:none`, bottom-right fixed). The Three.js scene initialization is deferred to JavaScript — customers on slow connections, content-blocked environments, or devices that fail the WebGL context test receive a product grid that is visually indistinguishable from the collection page.

2. **Theme version discrepancy: immersive pages load version 1.1.0; homepage and shop load version 6.3.0.** This is a cache-bust inconsistency that indicates the immersive template was last deployed separately from the main theme. Customers may experience cached stale assets on these pages specifically.

3. **No narrative copy establishing the scene before the 3D loads.** The Bay Bridge at night. The streetlight. The concrete. If the 3D experience takes 8 seconds to initialize, there is no text holding the customer's attention. The page is either loading or loaded — there is no in-between designed moment.

4. **No fallback experience for WebGL-incapable devices.** Mobile visitors on lower-end Android devices, visitors with hardware-accelerated graphics disabled, and some older iOS versions will see no 3D at all. No fallback content, editorial, or message is present.

5. **"Immersive Experiences" and "Enter the Universe" both appear as navigation labels** for the same section — duplicate navigation labels in the DOM create ambiguity about destination.

**Archetype:** Theater stage with the curtain still down.

**Single commercial fix:** Add a progress indicator (simple text: "Loading Black Rose...") that appears before the Three.js scene initializes — give the customer a reason to wait 8 seconds.

**Single brand fix:** Add 2–3 sentences of scene-setting copy below the hero and above the product grid — "The Bay Bridge at midnight. The water carrying the last of the day's light. This is where Black Rose lives."

---

## Surface 19 — Love Hurts Immersive Experience (/immersive-love-hurts/)

**Commercial purpose:** 3D brand differentiation for the highest-ASP collection.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Same Three.js/GSAP infrastructure as Black Rose — correctly applied.

**Weaknesses:**

1. **Same 3D canvas deferred-load issue as Black Rose.** No canvas in static HTML body.
2. **No narrative copy establishing the gothic cathedral / enchanted rose scene.** The immersive brief for Love Hurts (WP §6.3) is the most narratively specific: "Enchanted rose dome. Gothic cathedral. Beauty and the Beast from the Beast's perspective." None of this appears in the static HTML.
3. **Theme version 1.1.0 persists across all immersive pages.** Same cache inconsistency as Black Rose.
4. **No fallback for WebGL failures.**
5. **Product grid on fallback state is identical in structure to the collection page** — customers who cannot run WebGL get a worse version of a page they've already seen.

**Archetype:** Gothic cathedral photographed from the parking lot.

**Single commercial fix:** Ensure product cards on the fallback state include price visibility (the one advantage Love Hurts landing page already demonstrates).

**Single brand fix:** Add the gothic scene-setting editorial copy to the hero — "This is what it looks like when something beautiful refuses to be gentle."

---

## Surface 20 — Signature Immersive Experience (/immersive-signature/)

**Commercial purpose:** 3D brand differentiation for the Signature collection and its SF-oriented audience.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

Three.js infrastructure present. Signature experience page template correctly loads gold-palette CSS.

**Weaknesses:**

1. **Same deferred 3D canvas issue.** No canvas in static HTML.
2. **No Golden Gate editorial copy.** The Signature brief specifies "Golden Gate Bridge, golden hour, fashion runway, fog through cables" — none of this is in the static HTML body.
3. **Theme version 1.1.0 vs. 6.3.0 discrepancy persists.**
4. **No fallback for WebGL failures.**
5. **Navigation provides no indication that Signature has an immersive experience.** The nav link from the main menu is "Immersive Experiences" (pointing to all three) — there is no direct nav link from the Signature collection page to the Signature experience. The discovery path requires the customer to find the generic experiences hub.

**Archetype:** Runway with no one watching.

**Single commercial fix:** Add a direct "Enter the Signature Experience" CTA from the Signature collection page header (confirmed already present for Black Rose — parity gap for Signature).

**Single brand fix:** Add Golden Gate scene-setting copy: "Fog through cables. The bridge before the city wakes up. This is where the Signature collection was built."

---

## Surface 21 — Navigation and Global Chrome (Header/Footer)

**Commercial purpose:** Route customers efficiently across all surfaces; establish brand persistence across every page.

**Baseline performance:** `<KPI: TBD Phase 0.5>`

**Strengths:**

"Made in Oakland" is present in the footer — correct geographic specificity. Social links are present. Size guide table is accessible from footer. The dark theme is consistent across all pages (no flash of white/default WooCommerce chrome).

**Weaknesses:**

1. **Duplicate navigation menus in DOM.** Both the desktop and mobile nav menus are rendered in the HTML — this is correct for responsive design — but two distinct nav `<nav>` elements with separate item lists means any navigation inconsistency (item added to one menu but not the other) creates a broken navigation experience on either desktop or mobile.

2. **"Enter the Universe" and "Immersive Experiences" are two separate navigation labels pointing to overlapping destinations.** A customer reading the nav menu sees two different phrases that both lead to the 3D experience section. This creates decision paralysis where there should be clarity.

3. **Collections route in navigation points to `/collections/{slug}/` — the 404 URL pattern.** If the nav menu is configured with the canonical URL structure rather than the working `/collection-{slug}/` pattern, every nav-level click on a collection is a dead link.

4. **BANNED ELEMENT: Size guide table reproduced in footer.** The footer is not the correct location for a conversion-supporting tool like a size guide. The size guide belongs in the product-level flow (FAQ, PDP sidebar). In the footer it is inaccessible at the moment of highest need and adds visual weight to every page's baseline.

5. **Footer social links are not labeled with accessible text.** Icon-only social links (Instagram, TikTok) without `aria-label` attributes are inaccessible to screen readers. This is a WP §4.6 accessibility compliance gap that affects all pages.

**Archetype:** Road signs in two languages where one language is wrong.

**Single commercial fix:** Audit and fix the navigation collection URLs to point to the working `/collection-{slug}/` pattern, not the 404 `/collections/{slug}/` pattern.

**Single brand fix:** Collapse "Enter the Universe" and "Immersive Experiences" into one nav label: "3D Experiences" or "Enter the World."

---

## Verdict

The site presents the archetype of a **complete brand without a commerce engine** — the visual identity is more distinct than 95% of competing DTC fashion brands, the editorial voice is present and correct in the right places, and the technical ambition (Three.js immersive experiences, holographic card grid, dark-theme WooCommerce integration) is real and differentiated. The brand has earned its positioning. The infrastructure has not yet earned the brand.

The gap is not aesthetic — it is operational. All product detail pages return HTTP 500. The collection URL pattern is broken for external links. The countdown timers on every landing page and the pre-order gateway have expired and not been reset. The free shipping threshold is $100 on one page and $150 on another. A customer who arrives cold, browses the homepage, selects a product, and attempts to purchase encounters a PHP fatal error at every product. The immersive experiences — the one feature that has no analog at any competitor — silently degrade to product grids for customers who cannot run WebGL, with no narrative, no fallback, and no signal that anything was supposed to happen.

The shortest path to commercial viability is a three-action sequence: (1) resolve the PHP fatal error blocking all PDPs — this unlocks the entire revenue capture flow in a single fix; (2) synchronize the free shipping threshold to one canonical number across cart and shipping policy; (3) replace the broken countdown timers on all landing pages with static copy or remove them. Everything else in this audit — voice corrections, navigation cleanup, testimonial specificity, immersive experience fallbacks — is real and worth doing, but it compounds on a dead storefront. Fix the storefront first.

---
*Audit conducted: 2026-05-03 | Surfaces reviewed: 21 | Next step: Phase 0.5 KPI instrumentation*
