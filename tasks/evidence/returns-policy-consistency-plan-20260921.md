# Returns-Policy Consistency Repair Plan — 2026-09-21

Scope: service-summary copy only. The formal refund policy is the reference for
this repair; no product, payment, checkout, shipping-zone, or CSS behavior is
changed.

## Observed inconsistency

The published formal policy at `docs/legal/refund-return-policy.html` specifies:

- eligible returns within 30 days of confirmed delivery;
- a prepaid USPS label for US returns within 24 business hours;
- free US exchanges for a different size or color of the same style;
- shipment of the original within 14 days of receiving the exchange label;
- original-condition eligibility and final-sale/customized exceptions.

The live `/returns-exchanges/` page was cache-busted and inspected before this
source edit. Its existing summary instead said availability, fit, and production
windows were reviewed case by case and that a replacement was never promised.
That understates and conflicts with the published free US same-style exchange
term.

## Source repair

`inc/presentation-registry.php` now makes the importer/service summary state
the formal policy’s US return window, eligibility, prepaid-label timing, free
same-style US exchange scope, 14-day label deadline, and exceptions. It still
requires replacement availability confirmation and keeps international return
shipping/customer responsibility distinct. It does not change the formal policy
or invent a broader exchange promise.

## Before/after staging content backup plan

Before any staging content update:

1. Read and save each existing WordPress page record for the exact
   `shipping-returns` and `returns-exchanges` slugs: ID, title, status,
   `post_content`, template, parent, modified timestamp, and demo-owned meta.
   Save redacted JSON receipts under `tasks/evidence/` with a UTC timestamp.
2. Hash each original `post_content` with SHA-256 in the receipt. Do not use a
   page update call until both receipts exist and match the intended site.
3. Apply only the two prepared service-page contents. Do not overwrite a
   merchant-owned page that lacks the theme’s demo-owned marker; report that
   case for merchant approval instead.
4. Read both records back, save separate after receipts with content hashes,
   and cache-bust both public URLs. Verify the four policy sections and five
   service links render exactly once.
5. If the content or page identity is wrong, restore the saved `post_content`
   and original metadata from the before receipt, then re-read and record the
   rollback result.

The source repair did not itself mutate staging. The separately authorized,
guarded staging application and its evidence are recorded below.

## Staging readback and proposed compare-and-swap — 2026-09-21

Read-only staging capture confirmed the expected staging home URL and two
published root pages. The complete before records, including content, are in
`staging-policy-before-20260921.json`; the prepared operations are in
`staging-policy-cas-payload-20260921.json`.

- `shipping-returns`: post `9712`, content SHA-256
  `6d67f8ba309418e658247a1ac5d4192b79bdabe4609a8e8b4d54ce3064a803e0`,
  template `template-shipping-returns.php`, no `_skyyrose2_demo_owned` marker.
  This is the formal merchant shipping policy and must remain unchanged.
- `returns-exchanges`: post `10406`, content SHA-256
  `eb19f34fa4408153ee634d7f768778342ee6b71a53c4f0d715b6ee67afe099cc`,
  template `default`, `_skyyrose2_demo_owned=1.0.0`. The proposed service-summary
  content SHA-256 is
  `d17a5946908975c792792352df8397805886a9d6a3f6912f000b33abe817e6f8`.

Any apply step must first re-read and match the site, page IDs, slugs, published
status, parent, template, demo-owned markers, and both before-content hashes.
Only post `10406` is eligible for a `post_content` update. A mismatch aborts the
whole operation before any write.

After an authorized apply, read both records back. Require the shipping page
hash and metadata to remain byte-for-byte unchanged and the returns page hash to
equal the proposed hash. Cache-bust both public URLs and verify the returns page
shows all four maintained sections exactly once, omits “reviewed case by case”
and “replacement is never promised,” and retains the five service navigation
destinations. Preserve a separate after receipt; if any assertion fails, restore
post `10406` from the complete before record and record a rollback readback.

## Applied staging result — 2026-09-21

The compare-and-swap guards matched the staging home URL, active
`skyyrose-flagship-2` stylesheet, both page identities, status, parent, template,
ownership marker, and before-content hash. Only post `10406` was updated at
`2026-09-21T22:20:47Z`. The after receipt is
`staging-policy-after-20260921.json`; the prepared rollback payload is
`staging-policy-rollback-payload-20260921.json`.

Database readback confirmed that `shipping-returns` remained at its original
content hash and modification timestamp. `returns-exchanges` now has the exact
proposed content hash. Canonical and cache-busted public reads both rendered the
four maintained sections once within the page-copy region, omitted both stale
phrases, and exposed the exact five service links. The scoped public receipt is
`staging-policy-public-readback-20260921.json`.
