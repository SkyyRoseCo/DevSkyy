# SkyyRose staging commerce REDTEAM — 2026-09-21

## Scope and environment

- Staging: `https://staging-7e48-skyyrose.wpcomstaging.com`
- Active theme: `skyyrose-flagship-2` `2.4.4`
- WordPress: `7.1.1`
- WooCommerce: `11.1.1`
- Source matching the deployed PHP hashes: `/Users/theceo/.codex/worktrees/abe0/DevSkyy/wordpress-theme/skyyrose-flagship-2`
- No order was submitted and no payment was attempted. The founder-authorized U.S. staging shipping methods were changed as recorded below; no gateway, tax, product, or substantive policy setting was changed.

## Evidence ledger

| ID | Severity/state | Finding and reproduction evidence | Required disposition | Retest |
| --- | --- | --- | --- | --- |
| COM-001 | `DEFERRED_TO_PRODUCTION` by founder | WooCommerce Stripe `11.0.0` is active, but every registered payment gateway reports `enabled=no`. Stripe is forced to `testmode=yes` by the staging sandbox. The saved staging option has no test-shaped publishable key, secret key, or webhook secret. Available repository Stripe environment fields are empty. | Preserve the staging sandbox. After production cutover, authenticate at `/wp-admin/admin.php?page=wc-settings&tab=checkout&section=stripe`, connect the intended production Stripe account, verify live mode and webhook status without exposing credentials, and obtain founder approval before the first real charge. | Complete one tightly controlled production acceptance purchase; verify successful payment, order creation, confirmation email, webhook delivery/idempotency, refund path, and fulfillment routing. Record redacted order/payment identifiers and reverse/refund the charge as directed. |
| COM-002 | `US_FIXED_ON_STAGING` / international gap | Founder authorized the published U.S. offer. Staging zone 1 now has Standard `$17`, Express `$22`, and Free standard at a `$200` minimum; paid Express remains available above the threshold. The catch-all zone still has zero methods while the policy advertises international shipping to 40+ countries with checkout-calculated rates. Exact before/after evidence is in `tasks/evidence/`. | Preserve the verified U.S. configuration. Do not invent international rates; connect an approved carrier/rate source or narrow the policy before production promotion. | A synthetic Woo cart using published SKU `br-003` showed Standard/Express at `$100`, then Free standard/Standard/Express at `$200`. Root should repeat the customer-visible checkout test. Test one supported international destination only after an approved carrier configuration exists. |
| COM-003 | `UNVERIFIED_SETUP` | Taxes are enabled, base tax-rate count is zero, and Stripe Tax/WooPayments tax plugins are inactive. This audit does not infer the business's tax obligations. | Record the intended tax-calculation owner and configure it before accepting production orders if required by that decision. | Verify expected-versus-actual checkout tax for California and at least one other intended destination; preserve accountant/legal ownership of the tax decision. |
| COM-004 | `FIXED_IN_SOURCE` | Live database FAQ claimed universal XS–3XL sizing, 4–6 week preorders, worldwide shipping, fair-trade-certified facilities, and 24-hour support. Those claims conflict with product-specific facts and current service/policy wording. | `page.php` now renders the maintained marketplace FAQ on `/faq/` without overwriting the database or legal pages. `inc/seo-indexing.php` now builds FAQ schema from that same maintained content. | After staging deploy, confirm visible FAQ contains exactly three maintained questions; inspect rendered JSON-LD in a production-mode fixture and confirm the same questions/answers with none of the stale claims. |
| COM-005 | `VERIFIED` | Published WooCommerce bindings: shop `9836`, cart `9451`, checkout `9452`, account `9710`. Cart and checkout contain their required classic WooCommerce shortcodes. | Preserve bindings. | Repeat cart, checkout validation, guest/account, and order-recovery journeys after the final theme deploy. |
| COM-006 | `REVIEW_REQUIRED` | `/shipping-returns/`, `/refund-policy/`, and `/returns-exchanges/` all publish related guidance. The formal refund policy promises prepaid US labels/free US exchanges, while the service summary describes replacement availability as case-by-case. | Confirm the operating promise and reconcile overlapping copy before production so Client Services has one enforceable workflow. | Crawl every policy/service link and compare the displayed summary against the final formal policy. |
| COM-007 | `VERIFIED` | `/journal/` returns `200` with the visible `Journal` H1. `/hello-world/` returns one redirect to `/journal/`, then `200`; post ID `1` matches the exact retired-demo fingerprint and resolves through `skyyrose2_retired_content_target()`. | Preserve the reversible compatibility redirect; the sample post does not need destructive deletion. | Recheck redirect and Journal H1 after the final staging deploy. |

## FAQ repair files

- `wordpress-theme/skyyrose-flagship-2/page.php`
- `wordpress-theme/skyyrose-flagship-2/inc/seo-indexing.php`
- `wordpress-theme/skyyrose-flagship-2/scripts/test-seo-indexing.php`

## Verification performed

- `php -l page.php` — passed.
- `php -l inc/seo-indexing.php` — passed.
- `php -l scripts/test-seo-indexing.php` — passed.
- `php scripts/test-seo-indexing.php` — passed, including canonical visible/schema FAQ parity.
- `php scripts/test-marketplace-registry.php` — passed.
- `npm run lint:php` — passed for every theme PHP file.
- `git diff --check` on the FAQ repair — passed.
- `npm run verify` was attempted with the default environment and stopped at `check:source-integrity` because its Python interpreter lacked Pillow. A second attempt used `/Users/theceo/DevSkyy/.venv/bin/python`, which has Pillow, and stopped at the same integrity gate because the current Node is `26.8.1` while the declared release version is `22.23.2`. The root release operator will run the complete build/verification with both declared runtimes after all coordinated changes are integrated.

### Post-patch customer journey — isolated Chrome session

The final staging build was exercised in a fresh session named `Commerce REDTEAM` with cache-busted URLs. This test created no order and attempted no payment.

- BR-002 opened with the approved on-model front as `src` and `data-large_image`: `assets/approved-card-fronts/br-002-onmodel.webp`. Its alt text was `BLACK Rose Joggers — front on model`, and its responsive `sizes` value was `(max-width: 47.99rem) clamp(139px, 20.0000svh, 182px), clamp(299px, 33.3333vw, 512px)`.
- Selecting size `M` preserved the exact approved front source, large source, alt text, and responsive sizing. The customer status changed to `Selection confirmed. Current price and availability are shown above.` Clearing the selection restored the initial prompt while retaining the approved front.
- The secondary back-model image remained in the gallery. The lightbox opened and advanced from `1 / 2` to `2 / 2`.
- Adding the selected piece succeeded. The bag showed `BLACK Rose Joggers - M` at `$50.00`.
- At quantity `3`, subtotal `$150.00`, the customer saw Standard shipping `$17.00` and Express shipping `$22.00`; Free standard was absent. An invalid coupon was rejected as nonexistent and left the subtotal unchanged.
- At quantity `4`, subtotal `$200.00`, the customer saw Free standard shipping, Standard shipping `$17.00`, and Express shipping `$22.00`. Free standard was selected and the order total was `$200.00`.
- At a `390 x 844` viewport, checkout had `scrollWidth=390` and no horizontal overflow. Billing fields, the three shipping choices, privacy/terms links, and the order summary were visible. The page displayed the staging payment-disabled notice and no gateway option; Place order was not activated.
- The FAQ displayed all three maintained questions: `How do I choose a size?`, `When will a pre-order ship?`, and `How do I get order help?`. The stale `4-6 weeks`, `XS through 3XL`, `fair-trade certified`, `within 24 hours`, and `ship worldwide` claims were absent. There was no horizontal overflow at 390px.
- FAQ service links opened the correct semantic destinations: Shipping & Returns, Returns + Exchanges, Size Guide, and Contact, each with matching titles or H1 content.
- Theme-owned JSON-LD is intentionally suppressed on requests identified as staging by `skyyrose2_seo_schema_graph()`. Visible/schema parity is therefore covered by the production-mode regression fixture rather than claimed from staging HTML.

After the final service-template deployment, cache-busted browser token `launch_final_20260921b` confirmed `/faq/` still renders `data-sr2-route="service"` with the service class, all three canonical questions, and the five maintained service destinations in order. All five stale-claim probes remained absent and the header showed `Bag 0`. The account and final BR-002 image spot checks were handed to the separate visual-QA browser owner to avoid concurrent browser-extension control; this audit does not duplicate or claim those checks.

After explicit action-time approval, the isolated browser session removed only BR-002 size M at quantity 4. The cart then showed `Bag 0`, no cart lines, and `Your cart is currently empty.` No order was created and no payment was attempted.

## Release boundary

Payment execution is not a staging gate under the founder's explicit 2026-09-21 direction that the gateway cannot be tested until production. It remains a mandatory, separately evidenced post-cutover acceptance test. U.S. shipping is customer-visible and verified at the authorized rates and threshold; international shipping configuration and tax-calculation ownership remain unresolved and must not be represented as verified.
