# Commerce final specification and precise external gates

Runtime dependency: `f16f179cf2b73fa817691f72b15906309c628153`.
Fixture/contract closure: `48dca7136bb034727708281c4f1246dd66e4ed5d`.
No runtime correction is required by the verified closing checkpoint. This packet
adds no product fact, policy, stock mutation, purchase producer or release authority.

## Delivered invariants

- Native product/variation identity, selected attributes, prices, coupons,
  tax/shipping and totals remain WooCommerce-owned.
- Server-supplied version2 preorder snapshots replace caller-supplied data. Changed
  identity/date/edition/source before checkout requires remove/review/re-add.
  Current availability is freshly validated; native prices refresh separately.
- New order lines persist the offered promise via CRUD. Existing order metadata
  never refreshes from product edits. Version1 history remains readable; absent
  history stays unknown and future schemas remain preserved/unsupported.
- Existing-order payment validation uses that order's quantities and native IDs,
  independent of the current bag. It does not establish an atomic custom hold.
- Referral metadata retains coupon/referrer identity, rejects self-referral and
  preserves attribution/credited flags. It creates no financial reward or purchase.
- Analytics retains the existing verified native paid-order route and scoped
  `paid_order:<WC order ID>` identity, without a second producer, PII or snapshot.
- `_preorder_available` validates a cart/order aggregate only. The independent
  last-unit two-cart diagnostic remains evidence that validation is not reservation.

Exact schema, callbacks, keys, commands and dependency application are maintained
in [INTEGRATION-CONTRACT.md](INTEGRATION-CONTRACT.md); they are not restated as a
new implementation. Product authority is the unified root `logo-registry.json`
symlink; complete reads use `get_product`, with Corey's latest supplied facts
retaining FOUNDER_CONFIRMED authority.

## Combined source checkpoint

At `c4d971022aee75b6ea58b13b44cdc9d91aeb81e9` plus integration-owner dirty
implementation, the native fixture runs V2 from 4035 through its actual theme
symlink. The commerce lead independently verified the read-only bootstrap checker:
all 14 hooks and canonical module hash PASS. Source hashes were stable during that
check. The owner-executed CPT/HPOS/compatibility logs contain 86 assertions each,
258 total; their bytes/hashes were independently verified, without replaying the
mutating matrix. Enabled/control cart and reloaded order both total 159.50.

[checkpoint.json](evidence/combined-restart-20261001/checkpoint.json) binds fixture
identity, candidate HEAD, dirty functions.php hash, registry hash, source hashes
and originating evidence paths. This is an intermediate source checkpoint, not a
frozen final source/package or target runtime certification. The integration owner
requested no concurrent operation of its fixture; no further operations will run.
Future independent final checks require the owner's frozen SHA and an isolated
fixture, unless existing equivalent evidence already proves the exact artifact.

The aggregate owner log contains an unsupported SQLite ActionScheduler cancellation
log INSERT during storage-mode switching. Per-mode commerce assertions pass. Do
not infer scheduled expiry/job correctness or InnoDB locking from this fixture.

## Only unresolved owner decisions

The integration owner confirmed no new approved inventory/policy semantics during
this restart. Existing full-payment-at-order and 48-hour cancellation wording remain
preserved. Missing choices are exactly those in [DECISION-PACKET.md](DECISION-PACKET.md):

1. Operational stock authority, approved quantities and relationship of the custom
   availability/edition fields to native inventory.
2. Parent versus variation pooling and whether backorders are permitted.
3. Unpaid hold duration, expiry responsibility and late-payment handling.
4. Failure/cancellation/full or partial refund restoration/restock conditions.
5. Duplicate/concurrent lifecycle handling and existing-balance reconciliation or
   an explicit no-migration decision.
6. Controlling immutable policy/version, missing or changed estimate handling,
   cancellation date basis and acknowledgement semantics/consumer ownership.

PROPOSAL ONLY: prefer one native WooCommerce stock authority and reservation path
over a second theme counter. Installed 11.1.2 source groups quantities by native
stock owner and conditionally reserves stock minus active holds under locks;
the implementation requires InnoDB, managed stock and an applicable reservation
duration, and skips backorder-enabled products. These are source-derived mechanisms,
not target configuration qualification or authorization to assign quantities.

## Tests after decisions and frozen source

Qualify the agreed native inventory configuration on the intended database:
concurrent last-unit checkout; parent/variation pools; duplicate payment/status
delivery; unpaid expiry and late payment; approved failure/cancel/refund restock;
and historical promise preservation. Check visible customer policy/acknowledgement
through actual classic/Store API paths and the existing paid-order analytics route.
The integration owner owns viewer unknown-SKU/variation/unavailable-selection route
checks; commerce invariants must hold for the selected native identity.

R21 has intermediate combined-registration evidence but remains held for the frozen
final candidate. R25 combined analytics, target tax/shipping/payment, inventory
qualification and release remain unearned. No extra permission request or invented
business rule is needed to complete this evidence/specification packet.
