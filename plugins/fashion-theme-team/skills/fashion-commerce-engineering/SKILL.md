---
name: fashion-commerce-engineering
description: Implements catalog truth, WooCommerce templates, product discovery, fit and returns contracts, secure customer journeys, and commerce-state behavior.
---

# Fashion Commerce Engineering

Use for catalog-backed collection, search, PDP, cart, checkout, account, order,
fit, returns, and service surfaces.

For SkyyRose work, read products through `skyyrose.core.product.get_product`
and apply the commerce examples in
[`../fashion-theme-team/references/verified-examples.md`](../fashion-theme-team/references/verified-examples.md#fashion-commerce-engineering).

## Owners and inputs

Route `catalog-sot-integrator`, `woocommerce-theme-engineer`,
`fashion-component-commerce-engineer`, `fashion-merchandising-conversion-architect`,
and `fashion-product-fit-returns-specialist`. Read catalog/dossier/image SOT,
`commerce-state-contract.json`, WooCommerce coverage, page blueprints, and
current official WooCommerce/WordPress documentation.

## Procedure

1. Map SKU, variation, price, availability, imagery, provenance, fit, policy,
   and route IDs to authority before editing templates.
2. Implement product discovery, PDP decisions, variation selection, cart,
   checkout, account, order, fit, returns, and extension-absent states.
3. Preserve server truth: authorization, HPOS-safe reads, nonces, escaping,
   prepared queries, capabilities, privacy, and idempotent actions.
4. Exercise simple, variable, unavailable, sale, sparse, long-content, guest,
   auth, failure, and recovery journeys.
5. Return source changes, state matrix, commerce-truth log, and HTML/JSON proof.

## Verification

Run catalog consistency, provenance/image, PHP/theme lint, template-version, and
browser purchase checks. Never invent products, scarcity, reviews, fit promises,
prices, or policies. Rebuild tracked `.min` assets after CSS/JS changes.

## Boundaries

No external catalog mutation, media upload, payment action, or deployment without
explicit approval. Commercial hypotheses remain experiments.

## End-to-end execution

Run `fashion-e2e-task-execution` with this skill. Bind catalog authority, state
matrix, server-truth checks, and browser purchase proof to the same candidate.
An SKU, variation, price, media, or recovery mismatch becomes a first-seen issue
before retry, release, or promotion.
