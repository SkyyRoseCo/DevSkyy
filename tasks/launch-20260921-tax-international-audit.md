# Staging tax and international-shipping configuration audit — 2026-09-21

## Scope and evidence class

This was a read-only commerce configuration investigation. No staging or
production option, plugin, tax rate, shipping method, payment setting, product,
or catalog record was changed. Secrets and provider account data were not read
or emitted.

- `VERIFIED_LIVE`, authenticated staging SSH/WP-CLI target:
  `staging-7e48-skyyrose.wpcomstaging.com`.
- `VERIFIED_LIVE`, authenticated WordPress.com connector production target:
  blog ID `238510894`, public domain `skyyrose.co`; plugin inventory only.
- `SOURCE_VERIFIED`, public production policy:
  `https://skyyrose.co/shipping-returns/`, last-updated statement June 5, 2026.
- Product facts were not edited. The unified root product registry remains the
  only editable product authority and Corey remains the authoritative founder
  and maker.

## Current staging configuration

### Tax

- WooCommerce tax calculation is enabled.
- Prices are entered and displayed excluding tax.
- Tax location is based on the shipping address.
- Shipping inherits the cart item's tax class.
- Store base country/state is `US:CA` and currency is `USD`.
- Standard, reduced-rate, and zero-rate tables all contain **zero rates**.
- Stripe Tax for WooCommerce `2.1.0`, WooCommerce Tax `3.6.16`, and
  WooPayments `11.1.0` are installed but inactive.
- No configured Stripe Tax settings option was found. Migration/status markers
  alone are not evidence of an authenticated or configured provider account.

Result: staging is configured to calculate taxes in principle but has neither a
rate table nor an active automated-tax owner. A taxable checkout can therefore
produce zero tax. This audit does not infer the merchant's legal obligations.

### Shipping

- The United States zone is correctly configured and previously browser-tested:
  Standard `$17`, Express `$22`, and Free standard at a `$200` pre-tax
  merchandise subtotal. Express remains available above the threshold.
- The catch-all `Locations not covered by your other zones` zone has no methods.
- All countries are allowed for selling and no narrower ship-to-country list is
  configured.
- All 33 published physical products require shipping; all 33 have no WooCommerce
  weight and all 33 lack at least one package dimension.
- WooCommerce Shipping `2.3.16` is installed but inactive. Its stated function
  is label purchase/printing; its presence does not establish customer-visible
  international checkout rates.
- WooCommerce Tax is also inactive and does not establish a live carrier-rate
  source.

Result: international customers are permitted at the country-setting layer but
have no matching shipping method. Weight/dimension-based dynamic rates also lack
the product/package inputs advertised by the public policy.

## Production comparison

The authenticated production plugin inventory reports these plugins active:

- Stripe Tax for WooCommerce `2.1.0`
- WooCommerce Tax `3.6.16`
- WooPayments `11.1.0`
- WooCommerce Shipping `2.4.0`
- WooCommerce Stripe Gateway `11.0.0`
- WooCommerce PayPal Payments `4.1.3`

That inventory proves installation and activation only. The connector does not
expose WooCommerce tax registrations, provider connection health, tax engine
selection, shipping zones, carrier accounts, or checkout rate results. It is
therefore unsafe to describe production tax or international rates as configured
or to mirror undisclosed settings into staging.

The current public shipping policy promises shipment to 40+ countries and says
international prices are calculated dynamically from destination plus order
weight and dimensions. No live-rate carrier extension was identified in the
production plugin inventory. WooCommerce Shipping's own installed description
is limited to discounted label printing. The production public claim therefore
remains unverified against checkout capability.

## Concrete before/after plan

No mutation should occur until the owner inputs below are supplied. Activating
multiple tax engines would risk duplicate or conflicting tax calculation;
adding a catch-all price would invent an international rate.

### Tax configuration

**Before:** Woo tax calculation enabled; zero manual rates; no active staging
tax provider.

**Required merchant/accounting inputs:**

1. Select exactly one calculation owner: Stripe Tax, WooCommerce Tax, or a
   maintained manual rate table.
2. Provide the jurisdictions in which SkyyRose is registered or instructed to
   collect, including effective dates. This must come from the merchant's tax
   professional or provider account, not from theme code.
3. Confirm product tax-code mapping, whether shipping is taxable per registered
   jurisdiction, and whether displayed/catalog prices remain tax-exclusive.
4. For Stripe Tax, confirm the intended Stripe account is connected and its tax
   registrations are complete. Payment execution remains deferred to production,
   but calculation ownership still must be explicit.

**After, once supplied:** activate only the chosen staging tax engine; preserve
the current tax-exclusive display unless explicitly changed; import/sync only
the approved registrations/rates; capture a redacted configuration receipt;
verify expected-versus-actual tax at a California address and one other intended
destination using synthetic checkout data and no order submission.

### International shipping

**Before:** all countries allowed, catch-all zone empty, 33/33 published physical
products lack weight and dimensions.

**Required merchant/logistics inputs:**

1. The exact supported-country list replacing the non-operational `40+` claim.
2. The carrier/account and checkout-rate extension to use, with allowed services
   and origin postal code/account authorization.
3. Founder-confirmed packed weight and package dimensions for each SKU, or an
   approved packaging/rate-table strategy. These must be recorded through the
   unified product registry workflow before WooCommerce synchronization; they
   must not be guessed in WooCommerce.
4. Handling, insurance, signature, free-shipping, and excluded-destination rules.
5. Duties model (`DAP`/recipient pays versus `DDP`/merchant prepays) and matching
   customer-facing wording.

**After, once supplied:** update the product registry first and sync its approved
shipping fields; install/connect the selected live-rate extension in staging;
create explicit country zones rather than an unrestricted catch-all; keep the
verified U.S. zone unchanged; verify at least one supported international address,
one unsupported address, missing-rate failure behavior, rate refresh after cart
changes, and mobile checkout visibility without placing an order.

## Block disposition

- U.S. shipping: `PASS`, configured and customer-visible on staging.
- International shipping: `BLOCKED_MERCHANT_INPUT`; there is no safe rate or
  carrier configuration to mirror and required package data is absent.
- Tax calculation: `BLOCKED_MERCHANT_TAX_DECISION`; active production plugins do
  not establish which engine is authoritative or which registrations apply.
- Payment execution: `DEFERRED_TO_PRODUCTION` by the founder and unchanged.

## Correct and incorrect examples

**Correct — `VERIFIED_LIVE`:** retain the founder-approved U.S. rates and report
the empty international zone plus 33/33 missing package attributes. Request the
carrier, supported countries, and founder-confirmed package data before staging
configuration. Evidence: authenticated staging WooCommerce configuration query
and published-product aggregate query on 2026-09-21.

**Incorrect — illustrative, unexecuted:** activate Stripe Tax and WooCommerce
Tax together because both are active in the production plugin list, then add an
arbitrary worldwide flat rate. This mistakes activation for configuration,
risks competing calculators, and invents a shipping price. The correction is to
choose one tax owner from merchant/accounting evidence and configure an approved
carrier or rate table from real package inputs.
