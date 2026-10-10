---
name: fashion-design-system
description: Builds and governs SkyyRose tokens, typography, primitives, component APIs, states, responsive rules, motion contracts, fixtures, and adoption evidence.
---

# Fashion Design System

Use before broad storefront implementation or when a token, component, state,
or route pattern is missing.

For SkyyRose redesign work, apply the design-system examples in
[`../fashion-theme-team/references/verified-examples.md`](../fashion-theme-team/references/verified-examples.md#fashion-design-system).

## Owners and inputs

Route `fashion-design-system-engineer`, `fashion-token-foundations-engineer`,
`fashion-component-commerce-engineer`, `fashion-motion-responsive-engineer`,
`fashion-accessibility-content-engineer`, and DesignOps. Read the design-system,
V2 motion, component, and official platform contracts. For cascade, layout,
theming, and responsive CSS mechanics, load one file via
`../fashion-theme-team/references/engineering/css/index.md`.

## Procedure

1. Census existing tokens, selectors, primitives, components, variants, and
   generated outputs before creating anything.
2. Build primitive → semantic → component tokens with aliases, modes, contrast,
   forced-color, RTL, deprecation, and transform rules.
3. Define anatomy, slots, variants, invalid combinations, all interaction and
   commerce states, responsive behavior, reduced-motion equivalence, and a11y
   hooks.
4. Generate fixtures for content extremes, viewports, themes, states, and
   collection overrides. Record migration and adoption impact.
5. Return a versioned conformance contract and candidate-bound evidence.

## Verification

Reject raw literals, parallel token systems, ungoverned breakpoints, and
permanent exceptions. Run schema, contrast, fixture, generated-parity, and
adoption checks. The independent red team owns the pixel verdict.

## Boundaries

No self-approval, deployment, or silent rewrite of canonical sources.

## End-to-end execution

Run `fashion-e2e-task-execution` with this skill. Bind token/component contract,
fixture matrix, generated parity, adoption impact, and independent red-team
verdict to one candidate; record a drift or invalid state at first observation.
