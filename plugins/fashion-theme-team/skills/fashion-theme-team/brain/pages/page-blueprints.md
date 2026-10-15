# Complete Fashion Commerce Page Blueprints

> **SKYYROSE LLC · FASHION THEME BRAIN**

V2 visual layouts and imagery direction: [`../v2/v2-page-and-imagery-plan.md`](../v2/v2-page-and-imagery-plan.md).

These are starting contracts, not fixed wireframes. Section order follows customer
intent, brand strategy, real data and approved commerce configuration. Any omission
or reordering must be explicit in `contract.json`.

Every route covers loading, empty, error, success, unavailable, long-content,
missing-optional-media, keyboard, reduced-motion, mobile, tablet and desktop states.
Every section declares purpose, data source, component IDs, responsive behavior,
analytics, accessibility and evidence.

## Global shell

1. Skip link and service/status notices.
2. Announcement/promotion bar with terms, expiry and dismissal rules.
3. Header: identity, primary navigation, search, locale/currency if supported, account, wishlist if real, cart.
4. Mega menu or drawer with category, collection, editorial and service paths.
5. Global notices and breadcrumb policy.
6. Consent/preferences surfaces where applicable.
7. Footer: service, policies, contact, locale, newsletter with explicit consent, social, legal and accessibility statement.
8. Overlays: search, mini-cart, quick view, size guide and dialogs with focus containment/restoration.

Features: sticky behavior only when useful; no layout shift; responsive navigation;
real-time cart state; offline/network failure recovery; translation/RTL; structured
landmarks; no inaccessible hover-only content.

## 1. Homepage

**Intent:** understand the brand and reach a relevant product or story.

1. Brand/collection thesis hero with verified protagonist and primary CTA.
2. Current collection or drop gateway.
3. Curated product discovery with explicit merchandising logic.
4. Recognition device or brand proof—not a generic icon strip.
5. Shoppable editorial/lookbook module.
6. Category/occasion paths.
7. Material, craft, founder or cultural story proportional to evidence.
8. Service/trust proposition: delivery, returns, support, store/appointment as real.
9. Journal/community/press only with approved content and rights.
10. Newsletter/relationship invitation with value and preference clarity.

Features: campaign scheduling, product/collection availability fallback, mobile art
direction, hero media fallback, deep links, impression/click instrumentation.
Classic: `front-page.php`, `home.php` distinction. Block: `templates/front-page.html`.

## 2. Shop / all products

**Intent:** browse the entire available assortment.

1. Shop title, scope and optional concise context.
2. Category/collection shortcuts.
3. Result count, sort, filter and view controls.
4. Active-filter summary and reset.
5. Product grid with consistent truthful cards.
6. Controlled editorial insertions.
7. Pagination/load-more with state and URL continuity.
8. No-results guidance and recovery.

Features: responsive filter drawer, filter counts, color/size/price/availability,
shareable URLs, back-position restoration, unavailable-product policy.
Classic: `archive-product.php`. Block: `templates/archive-product.html`.

## 3. Collection, category, tag and attribute archive

**Intent:** understand a curated range and find a suitable item within it.

1. Collection identity, thesis, season/drop metadata and verified campaign media.
2. Optional chapter navigation or subcategories.
3. Shop controls and product grid.
4. Shoppable story interruption at an intentional depth.
5. Styling/material/cultural context.
6. Related collection or service path.

Features: scheduled/prelaunch/sold-out/archive states, deep links, taxonomy-specific
fallbacks, canonical URLs, localized collection content.
Classic: `taxonomy-product_cat.php`, `taxonomy-product_tag.php`, taxonomy templates.
Block: `templates/taxonomy-product_cat.html`, `taxonomy-product_tag.html`, `taxonomy-product_attribute.html`.

## 4. Search and filtered results

**Intent:** locate a known or describable product/content item.

1. Search form with preserved query.
2. Results summary and spelling/suggestion treatment only if real.
3. Product/content scope tabs where supported.
4. Filters, sort and product/result cards.
5. No-results recovery: remove filters, category paths, support—never fabricated matches.
6. Recent/popular searches only with approved privacy and data behavior.

Features: keyboard suggestions, escaped queries, loading/cancel/error, analytics
without leaking sensitive terms. Classic: `search.php` plus product search behavior.
Block: `templates/search.html`, `product-search-results.html`.

## 5. Product detail page

**Intent:** decide whether this exact product/variation is suitable and purchase it.

1. Breadcrumb/back context.
2. Verified media gallery with position, detail, scale and fallback policy.
3. Decision zone: name, price, rating summary if real, color/material, variations, size/fit, stock, quantity, add to cart, notices.
4. Delivery, duties, returns/exchanges and payment summary.
5. Product story and verified description.
6. Construction, materials, care, origin and measurements.
7. Size guide/fit finder and fit-oriented reviews.
8. Styling and complete-the-look relationships.
9. Reviews/Q&A with empty and moderation states.
10. Related/alternate products with provenance.
11. Recently viewed only under approved privacy behavior.

Features: simple/variable/grouped/external/virtual/downloadable behavior as applicable;
variation URL/state; media/price/stock updates; zoom/video; sticky purchase summary;
backorder/preorder/sold-out/waitlist; share; structured product data.
Classic: `single-product.php` and `woocommerce/single-product/*` only where justified.
Block: `templates/single-product.html` and supported product blocks.

## 6. Quick view

**Intent:** evaluate essential product facts without losing collection context.

Sections: compact verified media; identity/price; variation and size; availability;
add-to-cart; PDP link; notices. It must use real product forms, accessible dialog
behavior and focus restoration. Remove quick view if it cannot preserve variation,
stock and accessibility correctness.

## 7. Product comparison

**Intent:** compare factual differences among suitable items.

Sections: selected items, consistent media, price, verified attributes, fit,
availability, fulfillment and actions. Features: add/remove, missing-data honesty,
mobile comparison transformation, no invented normalization.

## 8. Lookbook / shoppable editorial

**Intent:** explore styling or narrative and reach the exact featured products.

1. Editorial thesis and context.
2. Chapters/scenes with verified media.
3. Accessible product annotations or adjacent product list.
4. Outfit composition and availability-aware alternatives.
5. Credits, provenance and rights where required.
6. Route into collection/PDP.

Features: no hover-only hotspots, mobile substitutions, reduced-motion story path,
deep links, product-identity verification, graceful handling of unavailable products.

## 9. Campaign, launch, drop and collaboration

**Intent:** understand a time-bound proposition and participate fairly.

Sections: thesis, verified participants/rights, release facts, featured assortment,
editorial proof, eligibility/terms, service expectations and fallback. Features:
timezone-safe schedule, approved countdown only from real timestamp, queue/limit
rules, preorder/waitlist, sold-out/archive state, no fabricated scarcity.

## 10. Brand story / About

**Intent:** understand who made the brand, why it exists and why its claims are credible.

Sections: clear thesis; founder/origin; values expressed through evidence; timeline
or milestones; craft/process; community/cultural accountability; press/partners with
rights; service/contact path. No invented heritage, vague mission filler or unsupported impact claims.

## 11. Journal index and article

**Intent:** discover and consume useful brand/editorial content.

Index sections: featured story, categories, article grid, pagination, search if real.
Article sections: title/dek/byline/date, hero/credits, semantic body, media captions,
related products with disclosure, related articles, sharing and corrections. Include
article structured data, readable measure, heading integrity and reduced-motion embeds.

## 12. Size guide, fit finder and measurement education

**Intent:** choose a suitable size with understandable limitations.

Sections: category/garment selection; unit/system selector; body versus garment
measurements; tables; illustrated measurement method; silhouette/ease/stretch;
model references; conversion notes; fit help/contact; recommendation disclosure.
Features: accessible tables, no horizontal trap, localized units, version/source,
product-specific overrides and print/save support where useful.

## 13. Wishlist / saved items

**Intent:** preserve products for later consideration.

Sections: identity, saved products, availability/price change, controls, move to
cart, sharing only with consent, empty recovery. Define guest persistence, account
merge, privacy, expiry and unavailable-product behavior. Do not render if no real service exists.

## 14. Cart and mini-cart

**Intent:** verify intended purchase and proceed or recover.

1. Cart notices and errors.
2. Line items with product/variation truth and edit path.
3. Quantity/remove/undo.
4. Coupon/promotion with terms and error states.
5. Shipping/tax estimate when configured.
6. Subtotal, discounts, fees and total clarity.
7. Checkout action and continued-shopping path.
8. Cross-sells only when stable and useful.
9. Empty-cart recovery.

Features: fragments/block updates, focus/status announcements, stock changes,
minimums/limits, session expiry and network recovery. Block templates keep assigned
page content through `core/post-content`.

## 15. Checkout

**Intent:** complete payment with minimal ambiguity and recover from failures.

1. Checkout header and progress only if accurate.
2. Global notices/error summary.
3. Contact and guest/account choice per configuration.
4. Billing/shipping address with autocomplete semantics.
5. Delivery method and timing.
6. Order summary with edit path.
7. Coupons/gift cards only if supported.
8. Payment methods and provider states.
9. Terms, privacy and explicit consent.
10. Place-order action, processing state and duplicate-submission prevention.
11. Payment/address/stock/session failure recovery.

Never suppress WooCommerce internals, disable paste, force account creation or
create unsupported payment UI. Block: `templates/page-checkout.html` must render
assigned page content.

## 16. Order confirmation, tracking and guest lookup

**Intent:** confirm outcome and understand next steps.

Sections: success/failure status; order reference; items/totals; delivery or pickup;
billing/payment summary with privacy; next-step timeline; account creation invitation
without coercion; help, cancellation/returns eligibility; related care/content only
after essentials. Include refresh/idempotency, pending payment and guest authorization states.

## 17. Account and authentication

**Intent:** securely manage identity, orders and preferences.

Routes: login, registration, reset, dashboard, orders, order detail, downloads,
addresses, payment methods, profile, preferences, privacy/export/deletion and logout.
Features: accessible authentication, password-manager/paste support, authorization
failures, empty histories, destructive confirmation and clear marketing-consent separation.

## 18. Returns and exchanges

**Intent:** understand eligibility and complete a fair post-purchase resolution.

Sections: policy summary; order/item selection; eligibility and deadline; reason;
exchange/credit/refund options as configured; fees/labels/drop-off; review; confirmation;
status/help. Features: guest/auth, partial orders, final-sale clarity, unavailable
exchange variation, regional policy, accessible upload if needed, privacy-safe reason analytics.

## 19. Customer service, FAQ and contact

**Intent:** resolve a question through the appropriate channel.

Sections: service navigation; searchable FAQ; delivery/returns/size/care topics;
contact channels and hours; form with expectations; order context with privacy;
store/appointment escalation. Include validation, attachment rules, response-time truth,
spam protection and success/error recovery.

## 20. Store locator and appointment

**Intent:** locate physical service or schedule a visit.

Sections: search/location permission choice; list and optional map; store facts;
services/accessibility; hours; directions; appointment availability; confirmation.
Provide a complete non-map list, denied-location fallback, timezone handling and cancellation path.

## 21. Gift cards and gifting

**Intent:** purchase or redeem a gift with clear restrictions.

Sections: amount/design, recipient/sender, delivery schedule/timezone, message,
terms/expiry, preview, purchase and confirmation. Cover invalid recipient, delivery
failure, balance, refund and regional constraints. Never imply unsupported physical/digital behavior.

## 22. Loyalty, membership and referrals

**Intent:** understand value and choose whether to join.

Sections: concrete benefits, eligibility, earning/redemption, exclusions/expiry,
current balance/activity, preferences and leave/close path. Separate enrollment,
marketing consent and paid subscription. Test immediate value as an experiment;
do not assume points create loyalty.

## 23. Preorder, waitlist and back-in-stock

**Intent:** act on unavailable or future inventory with accurate expectations.

Sections: exact status, expected timing, payment/cancellation terms, size/variation,
notification channel and consent, confirmation, status management. Features: timezone,
duplicate handling, inventory race, delay communication and unsubscribe. Notification
interest is not marketing consent.

## 24. Coming soon, password and maintenance

**Intent:** understand access state and next legitimate action.

Sections: identity, approved launch/status information, access form if real, service
contact, legal/privacy. Preserve admin/customer access, correct status/cache behavior,
accessible form errors and no fake countdown.

## 25. Empty, unavailable, error and 404

**Intent:** understand what failed and recover without blame.

Sections: plain-language status, preserved context/query where safe, primary recovery,
search/category/service paths, incident reference only when useful. Distinguish no
results, no inventory, removed product, permission, network, validation and server
errors. Never return a visually successful page with an incorrect HTTP status.

## 26. Legal, policy, privacy and accessibility

**Intent:** understand rights, responsibilities and support.

Routes: terms, privacy, cookies/preferences, shipping, returns, warranty/care,
accessibility statement, promotions and regional disclosures. Include owner-approved
content, effective/update date, jurisdiction/localization, contact/escalation and
version history where required. Design never substitutes for legal review.
