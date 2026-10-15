# WooCommerce Integration — Selling Four Collections, Not a Generic Catalog

Load when: the task touches WooCommerce REST v3, webhooks, product sync, or PDP correctness for the SkyyRose storefront (routed from `overview.md`).

Provenance: embedded from the DevSkyy skill `skyyrose-wp-platform` (`reference/woocommerce-integration.md`); source hash, license, and every adaptation are recorded in [`../index.md`](../index.md).

Every product that reaches skyyrose.co represents a real, founder-approved SKU across
Signature, Black Rose, Love Hurts, or Kids Capsule — this file exists so the WooCommerce
plumbing never becomes the thing that lets a wrong or invented product slip past that. It
replaces what `wp-rest-api`, `woocommerce`, `woocommerce-backend-dev`,
`woocommerce-code-review`, and `woocommerce-webhooks` covered as generic API mechanics.
`wc-pdp-correctness` (in this plugin: `../wc-pdp-correctness.md`) stays a standalone deep-dive
for PDP-specific work; this file is the stack-specific entry point that routes you there.

## The one rule that matters more than any API detail

**The single editable product source of truth is `logo-registry.json` (in DevSkyy a root
symlink to `<theme-root>/data/logo-registry.json`). Its `products[sku]` records own commerce
fields, colors, sizes, fit, materials, design spec, and image bindings. The catalog CSV and
per-SKU dossiers are generated projections, read through sanctioned readers and never
authored. The live WooCommerce store conforms to the registry, never the reverse.** Corey, the
founder and maker, is authoritative on his own product specs: his confirmations are recorded
as `FOUNDER_CONFIRMED`, and no third-party verification is demanded of his facts.
Never create a WooCommerce product that doesn't already exist in the product registry. This is the
same "real products only" discipline that governs imagery on this project (no hallucinated,
never-made renders) applied to the store's product data — a phantom product in WooCommerce is
the same class of failure as a phantom render, just on the commerce side instead of the visual
side. It has been violated before (catalog/store drift incidents) and cost real cleanup time —
don't re-derive this the hard way.

## Auth and connectivity

- Keys live in `.env.wordpress` (never hardcoded, never committed).
  Host repo (DevSkyy): `.env.wordpress` is the DevSkyy env file for WooCommerce credentials.
- WooCommerce REST v3 uses BasicAuth — `index.php?rest_route=/wc/v3/...` per this project's
  REST convention (see `build-and-templates.md`); a bare `/wp-json/wc/v3` path 401s on this
  WordPress.com hosting setup.
- Webhook signature verification is HMAC SHA256 — verify the signature before trusting any
  inbound webhook payload, no exceptions for "it's probably fine, it's our own site."

## Where this touches the Python backend

Host repo (DevSkyy): these are DevSkyy Python modules, not plugin files.

- `integrations/wordpress_com_client.py` — WordPress.com API client
- `integrations/wordpress_product_sync.py` — catalog → WooCommerce sync logic
- `database/seed_catalog.py` — Python-side DB mirror of the catalog
- `api/v1/wordpress_integration.py` — webhook sync-back endpoint

A catalog/schema-mapping task touches the registry record (`logo-registry.json`
`products[sku]`) ↔ its CSV projection ↔ PHP field (`inc/product-catalog.php`, a consumer) ↔
WooCommerce field — several representations of the same product, not one, and only the
registry is authored. Changing a projection or consumer without checking the others against
the registry is how drift happens.

## Product imagery — do not resolve this yourself

Product imagery resolves **only** via the image bindings in `logo-registry.json`
`products[sku]`, read through a sanctioned reader (in DevSkyy: `skyyrose.core.sot_images`,
front-first; `data/sot-images.json` is a generated projection, never authored). Never invent an
image path from a filename pattern or a WooCommerce media ID
alone — this is a locked project rule, not a style preference, because filename/manifest
mismatches have shipped wrong-garment imagery before.

## Domain-specific verification

- **A catalog claim is true** → read the registry record (`logo-registry.json`
  `products[sku]`, via a sanctioned reader such as `skyyrose.core.product_registry` or
  `catalog_loader`) directly, not memory of a prior
  session's catalog state — the registry changes over time and memory rots.
- **A live product's actual state** → a real WooCommerce REST v3 GET against the live store
  (BasicAuth via `.env.wordpress`), not an assumption from the registry alone — the registry is
  what _should_ be true, REST is what _is_ live right now. A sync bug means these can disagree.
  A stage-review reconcile pattern already exists for exactly this cross-check (WC × registry
  projection × render/stage/approve) — use it rather than hand-rolling a new comparison.
  Host repo (DevSkyy): the reconcile pattern is `stage-review --reconcile`.
- **A webhook payload is legitimate** → the HMAC SHA256 signature check passing, not merely
  "the request hit our endpoint."
- **Product imagery is the correct garment for its SKU** → read the actual pixels (vision),
  not the filename or manifest — this is a MANDATORY gate before any product image touches
  skyyrose.co, per this project's standing rule; wrong-garment imagery is the most-repeated
  defect class on this project.

Boundary: Outside plugin scope — the Fashion Theme Team builds and reviews candidates only;
production deploys, live WooCommerce/media writes, and paid calls belong to the host repo's
STOP-AND-SHOW approval process. REST reads for verification are fine; product/media writes are not.
