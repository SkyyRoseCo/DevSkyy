# Fashion Theme Brain

> **SKYYROSE LLC · FASHION THEME BRAIN**

This directory is the active, governed knowledge layer for the Fashion Theme
Team. It converts fashion-commerce evidence, platform requirements, page
anatomy, and prompt patterns into small context packs. It is not a dump that is
loaded wholesale.

## Authority and claim classes

Use sources in this order:

1. Repository instructions, approved brand canon, catalog SOT, and founder decisions.
2. Current official WordPress, WooCommerce, W3C, marketplace, and extension documentation.
3. Dated research recorded in `source-registry.json`.
4. Brain guidance labeled `DURABLE`.
5. `INFERENCE` and `EXPERIMENT` recommendations, which never become facts without evidence.

Every commercial or behavioral statement must carry one of these labels:

- `DURABLE`: stable craft or engineering rule.
- `CURRENT`: dated external evidence with a source ID and review date.
- `BRAND_SPECIFIC`: approved repository or founder fact.
- `INFERENCE`: reasoned recommendation that has not been experimentally verified.
- `EXPERIMENT`: measurable hypothesis with a success metric and guardrail.

Unknowns remain `UNKNOWN`; contradictions remain visible. Never convert a trend,
competitor pattern, or model preference into a universal rule.

## Retrieval protocol

1. Classify the request with `taxonomy.json`.
2. Load this file, `prompts/prompt-stack.md`, and only the matching knowledge and page packs.
3. Load the target repository's instructions, session log, SOT, design system, and implementation evidence.
4. Record every loaded pack in `contract.json.context.loaded_packs`.
5. If a `CURRENT` source is past `review_after`, refresh or downgrade the claim to `UNVERIFIED`.
6. Return `preview.html`, `contract.json`, and `evidence.json` using the schemas in `schemas/`.

## Brain map

- `brand/skyyrose-artifact-system.json`: SkyyRose visual token and anti-generic contract.
- `brand/skyyrose-artifact.css`: shared presentation layer with bundled SkyyRose theme fonts.
- `showcase/index.html`: branded visual artifact hub.
- `showcase/v2-page-atlas.html`: filterable V2 layout and imagery atlas for all twenty-eight pages.
- `showcase/interactive-feature-scaffold.html`: market-scraped interactive and immersive feature inventory with filters, CTA mapping, and proof lifecycle.
- `showcase/v2-gap-closure.html`: visual execution runbook for filling remaining catalog, commerce, responsive, accessibility, review, and release gaps.
- `visuals/*.png`: eyes-on-reviewed desktop, mobile, atlas, and handoff presentation captures.
- `references/animated-website-prompt-pack-200.pdf`: saved user-provided 200-prompt motion reference.
- `references/animated-prompt-pack-adaptation.md`: SkyyRose routing, CTA rules, and prohibited direct carries for that reference.
- `v2/v2-page-and-imagery-plan.md`: human-readable V2 page, layout, feature, and shot plan.
- `v2/v2-page-plan.json`: machine-readable V2 planning contract.
- `v2/team-run-summary.md`: consolidated V2 specialist disposition and remediation sequence.
- `v2/team-run-design-system.md`, `v2/team-run-commerce.md`, `v2/team-run-motion.md`: independent design, commerce, and motion/responsive audit reports.
- `v2/v2-page-plan.schema.json`: enforceable V2 route contract for tokens, provenance, responsive behavior, states, CTAs, motion, rhythm, and acceptance.
- `v2/commerce-state-contract.json`: WooCommerce-facing product, variation, availability, cart, checkout, account, service, and extension-state contract.
- `v2/motion-responsive-contract.json`: 390/768/1440 motion, fallback, cancellation, budget, and proof contract.
- `v2/team-run-contract-repair.md`, `v2/team-run-commerce-repair.md`, `v2/team-run-motion-repair.md`, `v2/team-run-release-loop.md`: remediation records and fail-closed release loop.
- `v2/gap-closure-procedure.json`: machine-readable eight-phase gap closure procedure with owners, dependencies, outputs, acceptance, evidence, and stop conditions.
- `knowledge/fashion-commerce-fundamentals.md`: customer value, segments, fashion economics, ethics.
- `knowledge/merchandising-and-conversion.md`: discovery, assortment, PDP, basket, checkout, retention.
- `knowledge/fit-imagery-and-returns.md`: garment truth, sizing, reviews, photography, returns.
- `knowledge/theme-engineering.md`: classic/block structure, WooCommerce contracts, performance, accessibility.
- `knowledge/do-dont.md`: contrastive guardrails and generic-theme failure patterns.
- `pages/page-blueprints.md`: human-readable full page and section system.
- `pages/page-blueprints.json`: machine-routable page inventory and implementation mappings.
- `features/premium-feature-catalog.json`: 44-item premium feature inventory with owner, contract, acceptance, and evidence requirements.
- `prompts/prompt-stack.md`: prompt assembly, reasoning checklist, critic and evaluator loops.
- `prompts/prompt-orchestration.md`: governed prompt engineering, typed chain stages, deterministic cache keys, invalidation, observability, and fallbacks.
- `prompts/few-shot-patterns.md`: good/bad structured examples.
- `prompts/evaluator-rubric.json`: weighted independent-review rubric and hard fails.
- `schemas/*.schema.json`: strict HTML/JSON handoff contracts.
- `examples/preview.html`: visual handoff fixture.
- `research/fashion-commerce-research-2026-08-06.md`: dated evidence synthesis.
- `research/interactive-commerce-research-2026-08-06.md`: cited market scan of interactive, animated, immersive, AI, and commerce patterns.
- `interactive/feature-scaffold.json`: machine-readable 22-feature scaffold with tiers, fallbacks, acceptance checks, and candidate-bound proof contract.
- `source-registry.json`: provenance, authority, freshness, and review schedule.
- `branded-skills/`: authenticated provenance, deterministic routes, strict gap-
  closure contracts, and 234 lazy-loaded SkyyRose enhancement records.

## Non-negotiables

- The garment and its truthful information remain the protagonist.
- Never invent products, prices, inventory, materials, sustainability claims, reviews, urgency, or permissions.
- Never use visual polish to conceal missing commerce states or broken customer journeys.
- HTML is the visual contract; JSON is the machine contract. Both describe the same stable IDs.
- A builder cannot approve its own output. Visual claims require rendered eyes-on review.
- A conversion hypothesis without measurement is an opinion, not a pass condition.
- A premium feature is not covered until its catalog record has implementation, fallback, accessibility, security, performance, and candidate-bound evidence.
- Prompt caching is never authority. Every chain must remain correct on cache miss and invalidate when candidate, SOT, approval, schema, or evidence changes.
