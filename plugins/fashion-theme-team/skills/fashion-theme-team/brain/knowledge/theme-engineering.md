# Fashion Theme Engineering

> **SKYYROSE LLC · FASHION THEME BRAIN**  
> *SkyyRose*

## Architecture declaration

Before implementation, declare classic, block or hybrid model; supported WordPress,
WooCommerce and PHP versions; target marketplace; HPOS and block coverage; browser
matrix; extensions; build artifacts; and customization boundary. Verify all current
version claims against official documentation and the local environment.

## WordPress structure

`DURABLE` Follow the template hierarchy and reuse template parts. A classic theme
uses PHP templates, functions, hooks and filters. A block theme uses block-markup
HTML in `/templates`, reusable `/parts`, patterns and `theme.json`. The hierarchy
concept remains, but file formats and supported customization surfaces differ.

Foundation coverage includes metadata, setup, menus/navigation, editor styles,
image sizes, enqueue/versioning, content width/layout, sidebars where applicable,
comments if supported, search, archives, posts, pages, 404, privacy, localization,
RTL, structured data, accessibility and safe defaults.

## WooCommerce structure

- Prefer supported hooks and blocks before copying templates.
- Inventory every override with source version, current upstream version and reason.
- Declare WooCommerce support and test the theme without optional extensions.
- Block themes map WooCommerce templates in `/templates`; keep Cart and Checkout page content through `core/post-content` as official guidance requires.
- Use global styles and supported block surfaces before fragile selectors that depend on private markup or nesting.
- Preserve fragments, notices, Store API/block behavior, sessions, totals, permissions and extension boundaries.

## Commerce state coverage

Cover simple, variable, grouped, external, virtual and downloadable products where
applicable; stock/backorder/sold-individually; regular/sale/unavailable price; sparse
and dense catalogs; filters/pagination/no results; cart and checkout validation;
guest/auth flows; payment failure; order confirmation; account endpoints; returns,
refunds and authorization failures.

## Accessibility

Target the approved standard and record it explicitly. Include landmarks, heading
order, accessible names, labels/instructions, error association and summary, keyboard
operation, focus visibility/order, contrast, reduced motion, alternatives, target
size, authentication support and status announcements. Automated checks assist but
never replace keyboard, screen-reader-informed and eyes-on review.

## Performance

Set route and asset budgets. Use responsive images, intrinsic dimensions, suitable
formats, lazy loading away from critical content, conditional scripts/styles, font
subsetting and fallbacks, cache-safe versioning, limited third parties, and no
animation that competes with input or critical rendering. Measure in representative
browser journeys; do not infer performance from bundle size alone.

## Security, privacy and commerce integrity

Escape by context, sanitize and validate input, use nonces and capability/ownership
checks, safe CRUD/prepared access, REST/AJAX permissions, safe redirects/uploads and
direct-access guards. Minimize personal data, document consent, respect customer/order
privacy and never place credentials or production customer data in fixtures.

## Distribution

Package only intended files. Include licenses, attribution, translations, RTL,
demo import, documentation, customization guide, compatibility, changelog, upgrade
and rollback notes. Bind source, built and package hashes to one candidate. Marketplace
readiness requires the current marketplace rules, not assumptions from an older theme.
