# Stream 1 / stream 3 executable integration contract

This closing dependency retains the module from `f16f179cf2b73fa817691f72b15906309c628153`
unchanged. The successor commit adds fixture qualification and this handoff;
its full SHA is supplied in the final delivery. It supersedes the earlier
test/evidence handoff, not V1 PR #886. If stream 1 already integrated `f16f179`,
cherry-pick only the successor delta. Otherwise apply `f16f179` then the successor.
Cherry-picking the delta alone does not supply the module introduced by its parent.

## Exact bootstrap and artifact boundary

Stream 1 owns `functions.php` and must include once, after `SKYYROSE2_DIR` exists:

```php
require_once SKYYROSE2_DIR . '/inc/woocommerce-compat.php';
```

The module calls no WC runtime while being included; hooks defer their WC reads.
No minified output is involved in this PHP-only dependency. Keep all paths in place.
Module SHA256:
`98fb6726e5704a5ac741d9b20b2bc38bb1578633998cacbe2ecac79d7ed778a1`.
The exact fixture, runner and registration-check hashes are in the ledger's
`closing_artifacts`; use them with the actual combined Git HEAD and theme build
hashes. No module changes means no new commerce implementation supersession.

Read-only registration command, **after** bootstrap integration:

```bash
wp --path=<selected-candidate-WordPress> eval-file \
  <combined-checkout>/wordpress-theme/skyyrose-flagship-2/tests/commerce/verify-bootstrap.php
```

It requires active `skyyrose-flagship-2`, WooCommerce 11.1.2, the exact module hash
and all 14 registrations once at priority 10. It never includes the module itself
or mutates orders. This check is NOT RUN on a combined candidate here. It cannot
prove accepted arguments, visible checkout, payment, tax configuration or analytics.

For behavioral reproduction, use the guarded local matrix command in README.
It explicitly includes the module, so its success does not establish bootstrap.
After integration, exercise the same cases through the full theme's actual
classic and Store API paths, record exact HEAD/artifacts/environment, and check
presentation/transaction preorder classification for the same native IDs.
Do not run the destructive fixture suite against an external store.

## Metadata and callbacks

Cart key: `skyyrose_preorder_snapshot`. Order-item CRUD keys:
`_skyyrose_preorder_snapshot`, `_skyyrose_preorder_schema`,
`_skyyrose_preorder_schema_version`. Schema `skyyrose.preorder-commercial-promise`,
integer version `2`. Fields: `is_preorder`, `product_id`, `variation_id`, `sku`,
`attributes`, `configuration_source_id`, `allocation_source_id`, `edition_size`,
`expected_ship_date`, `capture_point` (`add_to_cart`), `available_at_add_to_cart`.
Absent date/allocation are null. No monetary or customer fields are added.

`skyyrose2_preorder_config()` reads native product CRUD with per-field parent
inheritance, plus the presentation preorder flag when available. Parent pool sums
all selected sibling lines. Explicit variation zero overrides parent availability;
missing legacy availability is uncapped. `_preorder_available` stays validation-only.

`skyyrose2_preorder_add_cart_data()` replaces caller snapshots; the native
`woocommerce_add_cart_item` callback `skyyrose2_preorder_finalize_cart_item()`
captures resolved wildcard attributes. Validation runs on add and quantity update.
`skyyrose2_preorder_promise_matches()` compares identity, classification, sources,
edition and ship date, excluding prices and current availability. Stale/legacy/v1
cart promises require remove/review/re-add. Do not silently replace their offer.
Cart notices/Store API errors and `skyyrose2_preorder_validate_new_order()` protect
new checkout. Fresh native prices still calculate normally.

`skyyrose2_preorder_persist_item()` attaches snapshots to new order lines only;
11.1.2's Store API OrderController uses the shared WC_Checkout line builder.
Persisted/history/meta-bearing items remain unchanged. `skyyrose2_preorder_read_item()`
returns `recorded` for v1/v2, `legacy_unknown` for absent history and
`unsupported_schema` for future history. Display callbacks consume recorded history.
Existing-order payment uses `skyyrose2_preorder_validate_order_payment()` on
`woocommerce_checkout_validate_order_before_payment` and
`skyyrose2_preorder_before_pay()` on `woocommerce_before_pay_action`; it checks the
order's own native IDs/pool quantities, independent of a customer's current bag.

Referral callback `skyyrose2_preorder_capture_referral()` runs on
`woocommerce_checkout_order_created` and
`woocommerce_store_api_checkout_order_processed`. Order CRUD key
`_skyyrose_referral_attribution` holds version 1, `coupon_id`, `referrer_id` only.
It ignores self-referral and existing attribution/`_skyyrose_referral_credited`.
No payout, $10 reward, reward counter or purchase event is introduced. Concurrent
financial reward delivery is outside this metadata callback's qualification.

## Stream 3: existing native paid-order identity

Reuse `api/v1/analytics/ingest.py::capture_paid_order()` through the existing
HMAC-verified `/order` webhook handler in `api/v1/woocommerce_webhooks.py`.
Source-qualified acceptance requires native `processing`/`completed` status AND
`date_paid_gmt`, matching configured site/webhook source, validated order ID,
amount, currency and paid time. An order-created callback alone is not a purchase.
Identity remains:

```python
scoped_event_id(site_id, environment, f"paid_order:{wc_order_id}")
# uuid5(NAMESPACE_URL, f"skyyrose:{site_id}:{environment}:{event_id}")
```

`event_store.py` owns persistence/deduplication. Unchanged retry or transition from
processing to completed with unchanged paid facts must produce one event. Changed
facts for the same scoped identity must follow its conflict response, never a
second identity. Other sites/environments have distinct scopes. Keep native order
ID, amount, currency and paid time in the established minimal contract. Send no
customer fields or preorder snapshot; add no second purchase hook or counter.
These are source-derived contracts, not a new authenticated analytics execution.

R21 (bootstrap) and R25 (purchase integration) remain BLOCKED until the actual
combined candidate supplies evidence. R20-local qualifies fixture totals only;
R20-target stays NOT RUN. Never infer target qualification from the $159.50 fixture.

Product authority remains root `logo-registry.json` pointing to the unified V1
registry; complete reads use `get_product`. Corey's supplied specifications retain
FOUNDER_CONFIRMED authority. This contract creates no product facts or policy.
