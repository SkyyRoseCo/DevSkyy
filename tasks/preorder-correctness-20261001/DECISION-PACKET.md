# Remaining owner decisions — bounded closing packet

Source review at this branch is evidence of recorded wording and implementation,
not proof of current publication or approval. No live stock/payment mutation,
policy enactment, migration or paid provider work ran. No proposed field below
exists in the delivered snapshot schema yet.

## Reuse the recorded commercial facts

`docs/legal/{refund-return-policy,shipping-policy,terms-of-service}.html` carry
June 5, 2026 update dates. Their preorder sections specify full payment at order,
estimated ship dates displayed at purchase, full-refund cancellation up to 48 hours
before that estimate, and standard returns after delivery. Refund policy refers
to the order confirmation's date; Terms refers to the PDP date at purchase.
Approved cancellation refunds use the original payment method within 5–7 business
days. Shipping policy specifies separate preorder/in-stock shipments and dispatch
tracking email. Existing standard return conditions are preserved; do not request
reconfirmation of facts already supplied or manufacture replacements.

Newer V2 source (`inc/presentation-registry.php:128`,
`template-parts/v2-preorder.php:20`) keeps full payment but directs customers to
Client Services for estimates; the preorder label establishes neither a shipping
date nor stock reservation. Current snapshot permits a null estimate. Thus an
estimate-dependent 48-hour cutoff cannot be calculated for every current offer.
No recorded policy version/acknowledgement contract resolves this source conflict.

Only these commercial choices remain: identify the controlling approved source
and immutable version; choose the policy for a missing date; specify whether the
PDP-at-purchase or order-confirmation date controls cancellation and what happens
when an estimate changes. Preserve recorded original order promises either way.
Do not invent a date, cancellation duration, stock hold, or later payment model.
Corey's latest explicit correction governs any conflicting product fact.

## Exact missing machine fields and consumers

Proposed fields are implementation inputs after the owner decision, not new facts:

| Missing input | Required consuming boundary |
| --- | --- |
| `policy_id`, immutable `policy_version` or content digest, `effective_date`, canonical `source_reference`, approval provenance | Stream 1's customer policy display; stream 2's config/snapshot and immutable order history |
| Approved `acknowledgement_required` plus text/version and scope (order or specified lines) | Stream 1 PDP/cart/classic/Store API checkout UI and server validation |
| Chosen acknowledgement `capture_point`, affirmative value, timestamp, displayed policy binding | Server-recorded checkout/order data; historical order/account/email readers; never infer consent from adding to cart |
| Null-date eligibility and cancellation handling; original date basis/timezone and changed-estimate rules | Stream 1 eligibility/copy; stream 2 snapshot comparison and cancellation consumer once one is assigned |

Existing `skyyrose2_preorder_config`, `_snapshot`, `_promise_matches`, `_persist_item`,
`_read_item`, and display callbacks consume identity/date/edition only. A future
policy extension must deliberately version its schema and preserve v1/v2 history;
it cannot silently append acknowledged policy to old carts/orders. There is no
cancellation execution consumer in this module; owner assignment is still needed.
This packet requests no generic approval and does not implement these fields.

## Inventory lifecycle: decide only the unresolved execution contract

**PROPOSAL:** one native WooCommerce stock authority, at the approved product or
variation level. Keep `_preorder_available` descriptive/validation-only until its
relationship to stock is decided. It is currently not decremented or restored.
The separate last-item diagnostic proves two independent carts can validate it;
it remains in every storage-mode run. Validation is not a reservation.

| Owner choice still needed | Execution detail to record |
| --- | --- |
| Authority | Native stock or a specifically owned atomic allocation store; relation of `_preorder_available` to that authority and edition size |
| Pooling | Parent-shared or variation-specific inventory; explicit mapping for selected IDs |
| Reservation/decrement | Exact native lifecycle point, responsible component and stock-management setting; payment/checkout must not decrement twice |
| Unpaid expiry | Pending-payment hold duration, expiry trigger and release responsibility |
| Failure/cancel/refund | Which events release a reservation or restore reduced quantity, including partial refunds and whether explicit restock is required |
| Duplicate identity/concurrency | Native order/item/event identity, retry guard, atomic locking/reservation mechanism and last-item two-checkout outcome |
| Migration | Existing balances/holds to reconcile, mapping, dry run, rollback and separately authorized execution; or an explicit no-migration decision |

Installed WooCommerce 11.1.2 source registers native reduction for payment complete,
processing/completed/on-hold and checks its stock-reduced guard; native increase is
registered for cancelled/pending/failed. Reservation release has native lifecycle
hooks too. Those source observations describe candidate mechanisms; they do not
prove the target's stock flags, hold settings, gateway behavior, refund restock,
concurrent checkout or owner-approved lifecycle. No second theme counter is added.

After choices exist, qualify stock-managed simple/variation/pool cases, last-item
concurrent checkout, repeated payment/webhooks, unpaid expiry, failures,
cancellation and approved full/partial refund restock on the intended database.
The SQLite monetary fixture is not MariaDB/native reservation qualification.

## Ownership and acceptance

Stream 1 owns policy/presentation, bootstrap and combined storefront acceptance.
Stream 2 owns descriptive order metadata and approved transaction implementation.
Stream 3 owns the existing scoped native paid-order event; use the integration
contract, without a second purchase hook, counter, PII or snapshot payload.
The coordinator assigns inventory lifecycle/migration ownership after the choice.
R21/R25 stay BLOCKED absent actual combined-candidate evidence. Target tax/shipping,
browser/payment qualification and release retain their own gates.
