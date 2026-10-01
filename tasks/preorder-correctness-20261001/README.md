# Preorder correctness — stream 2

Local candidate only. No push, merge, deployment, live migration, real order/payment
mutation, or provider work is authorized. Frozen base:
`7892b797d838e67e62c862a6698a5b42b6dccaee`. Branch:
`codex/preorder-order-promises-20261001`.

The implementation and real local WooCommerce integration checks are delivered.
Overall CODE COMPLETE and E2E acceptance remain **BLOCKED** by the bootstrap,
inventory ownership, commercial decisions, target testing, and release gates.
See [acceptance-ledger.json](acceptance-ledger.json) for per-requirement evidence.

## Delivered transaction contract

`wordpress-theme/skyyrose-flagship-2/inc/woocommerce-compat.php` registers native
cart/checkout/order hooks without invoking WooCommerce during inclusion. Stream 1
owns the required single bootstrap addition:

```php
require_once SKYYROSE2_DIR . '/inc/woocommerce-compat.php';
```

This stream deliberately does not edit `functions.php`, the shared registry,
theme build/package outputs, or CI/deployment files. Stream 1 must cherry-pick
this candidate, load it, and verify its resulting exact head. Module-only checks
do not establish full V2 integration.

Native WooCommerce owns product/variation selection, eligibility, stock, prices,
discounts, taxes, shipping, totals, cart keys, orders and payments. Cart lines
carry `skyyrose_preorder_snapshot`; order lines persist
`_skyyrose_preorder_snapshot`, `_skyyrose_preorder_schema`, and
`_skyyrose_preorder_schema_version` through order-item CRUD.

The schema is `skyyrose.preorder-commercial-promise`, version **2**. Fields:
preorder state; product/variation IDs; selected SKU/attributes; configuration and
allocation source IDs; edition size; optional expected ship date;
`capture_point: add_to_cart`; and descriptive availability at capture. There is
no price, total, personal data, invented date, or unapproved policy reference.
Absent dates and allocation are explicit nulls. Edition specifications stay
strings rather than being silently rounded or converted from ranges.

Woo product metadata is read via product CRUD, with per-field variation
inheritance. The existing registry-derived presentation preorder flag also
activates transaction protection. The single editable product authority remains
`wordpress-theme/skyyrose-flagship/data/logo-registry.json`, root symlink
`logo-registry.json`, with 33 unified product records. Complete product reads use
`from skyyrose.core.product import get_product`. This change authors no product
facts and makes no registry changes. Corey is founder/maker; exact supplied facts,
wording, measurements and ranges retain founder authority. No third-party proof
or invented missing detail is required.

Caller-supplied snapshots are replaced on add. Core-resolved wildcard variation
attributes are finalized after native validation. Current pool totals aggregate
every cart line sharing the allocation source; quantity updates exclude the old
line. Zero updates permit removal; invalid/fractional quantities fail. Explicit
zero availability blocks; absent legacy allocation remains uncapped; malformed
limits/dates fail with a notice rather than turning into positive quantities.

Before checkout, identity/promise changes block purchase with remove/review/re-add
instructions. Prices and changing availability are excluded from descriptive
promise comparison: native prices refresh and allocation is freshly checked.
Legacy restored preorder carts without a recorded snapshot also require review;
the implementation never claims today's metadata was their original offer.
Existing v1 cart snapshots require a fresh add before new purchase; v1 order
snapshots remain readable. Persisted historical items are never backfilled.
Unknown future order schemas are preserved with an `unsupported_schema` status.

Order placement is the permanent promise boundary. Existing order payment checks
that order's native identities and aggregate quantities, independently of its
customer's current bag. Its previously recorded date is preserved after product
edits. Classic payment uses `woocommerce_before_pay_action` notices; Store API
payment uses `woocommerce_checkout_validate_order_before_payment` errors.
Unknown historical promises continue through native stock validation without
fabricated preorder history. Native formatted metadata exposes recorded promises
to order/account/email consumers; historical source fields are never refreshed.

Referral attribution uses coupon/order CRUD. It records schema version, coupon
ID and referrer user ID at native order creation/processing, rejects self
referral, preserves earlier attribution/credited flags, and stores no email in
the new attribution. It introduces no financial credits or reward counters.
V1's $10 reward scheme is dormant in verified V2 and remains outside this change;
reward authorization/concurrency semantics need a separate owner decision if
that scheme is to be enabled.

## Runtime and PR reconciliation

Authenticated **read-only** staging discovery confirmed the intended home URL,
WordPress **7.1.2**, V2 **2.5.1**, WooCommerce **11.1.2**, and HPOS enabled.
Compatibility-sync option was absent, rather than verified in a particular mode.
Neither V1 snapshot/referral functions nor this new module are loaded there.
[staging-readonly.json](evidence/staging-readonly.json) includes the installed
functions.php hash and the Woo cart/Store API order-controller hashes. The two
Woo source hashes match the official downloaded files used locally.

Production comparison, read only: home `https://skyyrose.co`, V1 **2.3.1**, Woo
**11.1.2**, HPOS enabled. Production is not this candidate's acceptance target.

PR [#886](https://github.com/SkyyRoseCo/DevSkyy/pull/886) was OPEN and MERGEABLE
at refresh, head `e3d28fd7d38d9a53aabb8ad47f4bc57bdf1acca8`, base
`f97383524206825e9f0bd24042e7990be43aee27`. Its seven files concern V1,
including mutable-price removal, variation-aware snapshots, synthetic PHPUnit
stubs, checkout display and HPOS referral metadata. V2 does not load that module.
This candidate reuses its schema/key vocabulary and behavior where applicable,
adds version 2 identity/drift/payment handling for V2, and preserves historical
version 1 orders. It does not close, merge, or imply supersession of the V1 PR.
Current remote main matched the frozen base after fetch. Main protection API
reported null required-status-check/review fields; this is read-only discovery,
not permission to push or merge.

The version-pinned WC_Cart catches exceptions from the cart-data filter and
returns false plus a notice. Woo **11.1.2** Store API OrderController delegates
line-item creation to WC_Checkout, so it invokes the shared item hook. Do not
assume an upstream trunk or future release retains these boundaries. Official
contracts: [HPOS recipe book](https://developer.woocommerce.com/docs/features/orders/high-performance-order-storage/recipe-book/),
[CRUD objects](https://developer.woocommerce.com/docs/best-practices/data-management/crud-objects/).

The handoff did not identify a standalone current Production OS contract path.
The available `skyyrose/core/execution_policy.py` and `creative_job.py` were read;
their content-context and commerce-integrity constraints were treated as
source context rather than an expansion of current authority. No creative prompt, generation, spending or
publishing is part of this work.

## Inventory decision required

**Recommendation, awaiting owner decision:** use one native WooCommerce stock
authority, configured at product or variation ownership. Keep the theme's
`_preorder_available` as validation-only until its relationship to native stock
is explicitly decided. Current staging HPOS does not establish stock ownership,
reservation configuration, gateway behavior or restoration policy.

The decision must identify the authoritative store, reservation/decrement point,
pending-payment hold/expiry, cancellation/failure/refund restoration, variation
versus parent pooling, duplicate-event idempotency, concurrency mechanism, and
any existing-data migration. Native reservation is preferable to a second theme
counter when configured appropriately. If a custom allocation is chosen instead,
it requires one atomic reservation store with unique order/event identity and
explicit expiry/release semantics; validation alone cannot provide this.

The local suite intentionally proves that independent carts both validate the
last custom allocation. It also proves this module makes no decrement/restore
writes. Those facts do not prove oversell protection or native reservation
correctness. Cross-cart checkout concurrency and all approved allocation
lifecycle cases remain BLOCKED. No live migration or allocation mutation ran.

## Reproduction

Tests require an isolated synthetic local WordPress **7.1.2**, WooCommerce
**11.1.2** installation at `http://127.0.0.1:18362`. This run used official
WordPress/Woo downloads and WordPress Performance Team SQLite integration
**2.2.23**, PHP **8.5**, with synthetic products/users/coupons/orders only.
Authentication is not applicable to this offline fixture. The test guard
refuses other home URLs; it deliberately leaves fixture records for inspection.
Do not run it against staging/production or an existing store database.

```bash
bash wordpress-theme/skyyrose-flagship-2/tests/commerce/run-local-matrix.sh \
  /tmp/skyyrose-preorder-wc-20261001 \
  /Users/theceo/.codex/worktrees/56b5/DevSkyy/tasks/preorder-correctness-20261001/evidence

/Users/theceo/DevSkyy/wordpress-theme/skyyrose-flagship/vendor/bin/phpcs \
  --standard=wordpress-theme/skyyrose-flagship-2/phpcs.xml \
  wordpress-theme/skyyrose-flagship-2/inc/woocommerce-compat.php \
  wordpress-theme/skyyrose-flagship-2/tests/commerce/preorder.php

php tools/v2-runtime/test-checkout-truth.php
python3 scripts/sync_product_registry.py --check
git diff --check
```

The matrix runs CPT, HPOS, and HPOS with compatibility synchronization. It uses
native **local** HPOS synchronization before changing the fixture's mode and
asserts the actual data-store class. Source/store integration is real; gateway,
browser checkout and production database qualification are separate unrun gates.
SQLite initially rejected a session-table ALTER during explicit table setup;
the completed cart/session/order tests run under its translation layer, not
MariaDB. WP-CLI also emits a PHP 8.5/react deprecation; the runner suppresses
E_DEPRECATED toolchain noise while preserving errors/warnings and exit statuses.

The pre-existing checkout-copy test is a synthetic rendering regression only.
No full shared V2 build/package run is claimed: those artifacts and bootstrap
belong to stream 1. No UI mobile/accessibility/performance acceptance or payment
gateway exercise has been performed on the candidate.

## Remaining actions and recovery

Stream 1: integrate the exact dependency commit, align presentation/transaction
classification and customer language, provide approved policy/version and promise
fields where absent, and test the resulting V2 storefront on its exact head.
Stream 3: consume native order identity/lifecycle; do not duplicate purchase
hooks or send snapshot contents to analytics. Stream 5: preserve the module,
test and fixture paths; no path relocation is part of this change.

After owner decisions, complete approved allocation logic and qualification on
the correct database/configuration. Authenticated sandbox order/payment tests,
deployment and release require their separate scopes. Push and merge remain
unauthorized under the current assignment. MERGED, RUNTIME ACCEPTED and RELEASED
are therefore not earned by these local results.

Local rollback is a scoped revert of this candidate's commit; the coordinator
must also remove its one bootstrap include if integrated. No data migration is
required or performed. Existing snapshot/order metadata must remain intact even
if code is rolled back; v1/v2 readers can consume the retained metadata later.
Do not delete historical order metadata or claim an operational deployment
rollback has been tested. The local synthetic fixture stays under `/tmp` for
inspection; this work does not delete it or transfer/archive any worktree.
