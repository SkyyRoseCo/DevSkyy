# Few-Shot and Contrastive Patterns

> **SKYYROSE LLC · FASHION THEME BRAIN**  
> *SkyyRose*

## Collection hero

**Accepted:** The hero identifies the collection thesis, shows a verified garment
at an intentional crop, offers one primary path into the assortment, preserves
product visibility on mobile, and moves secondary editorial context below the
first product discovery opportunity.

**Rejected:** Full-screen stock model, vague luxury adjective, two competing CTAs,
autoplay video without fallback, and no visible product or collection information.

## Product detail page

**Accepted:** Media, product identity, price, variation/size selection, fit help,
availability, fulfillment, returns, and add-to-cart form one coherent decision
zone. Variant selection updates truthful media, price, availability, and URL/state.
Long-form craft and styling content follows the purchase decision zone.

**Rejected:** Editorial animation delays product facts; size guide opens without
measurements; color swatches have no accessible names; reviews are decorative;
sticky add-to-cart can purchase an unselected variation.

## Merchandising recommendation

**Accepted:** “Complete the look” uses catalog-proven compatibility, excludes the
current SKU, explains the styling relationship, handles unavailable items, and is
measured as an experiment with attachment rate and return-rate guardrails.

**Rejected:** “You may also like” displays arbitrary high-margin products and is
described as a proven conversion win without data.

## Checkout

**Accepted:** The theme preserves WooCommerce page content and block behavior,
keeps notices and recovery paths visible, maintains labels and autocomplete, and
styles through supported global/block surfaces.

**Rejected:** The theme replaces checkout internals, hides errors, disables paste,
forces account creation, or relies on fragile descendant selectors.

## Fashion voice

**Accepted:** Specific material, construction, cultural, and styling language is
supported by the SOT and scaled to the shopper's decision stage.

**Rejected:** “Elevate your wardrobe with timeless luxury” is used as generic
filler, unsupported scarcity, or a substitute for actual product information.

## HTML/JSON parity

**Accepted:** `<section data-section-id="pdp-decision-zone">` corresponds to a
`contract.json` section with ID `pdp-decision-zone`, requirements, states,
components, and evidence references.

**Rejected:** The HTML shows a loyalty module that has no JSON requirement, or the
JSON requires a fit guide that is absent from every rendered viewport.
