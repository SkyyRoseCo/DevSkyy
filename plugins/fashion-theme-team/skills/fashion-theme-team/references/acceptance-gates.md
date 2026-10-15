# Acceptance Gates

Apply only gates relevant to the approved scope, but never waive an applicable
gate silently. Every result includes a gate ID, candidate ID, command or journey,
exit/result, environment, timestamp, artifact path/hash, owner, and independent
reviewer. `NOT_APPLICABLE` requires rationale and authority.

No material claim may be accepted without the proof class it requires:

- Visual/design/content/image claims: deterministic artifact plus eyes-on review.
- API/version/security/marketplace claims: current authoritative primary source,
  retrieval date/version, and applicable executable evidence.
- Runtime/commerce claims: reproducible browser or integration journey.
- Build/package claims: exact command, exit status, artifact, and digest.

Official documentation informs expected behavior; it does not prove the local
candidate implements that behavior.

## Design system

- Canonical token sources cover color, typography, spacing, sizing, radii, elevation, motion, and breakpoints.
- Components define variants, interaction states, responsive behavior, accessibility semantics, and content constraints.
- Feature code consumes canonical tokens and primitives without undocumented duplicates.
- Documentation or machine-readable examples show intended component composition.
- Visual fixtures cover representative components and critical states.
- No unresolved parallel token system exists on release surfaces; exceptions expire.
- Fixture coverage includes every critical variant, breakpoint, collection mode, and content extreme.

## Source and build

- Repository-provided PHP, JavaScript, CSS, and package validation commands pass.
- Generated `.min.css` and `.min.js` match current sources when tracked.
- No new placeholder copy, TODO markers, missing referenced assets, or invented commands.
- Candidate hash and changed-file inventory are recorded after integration.

## Commerce

- Homepage, collection, PDP, cart, checkout, and account routes resolve when in scope.
- Simple and variable product flows use real WooCommerce behavior.
- Cart fragments, notices, totals, shipping, taxes, coupons, and account states are exercised when applicable.
- Product facts, prices, SKUs, inventory, and imagery trace to an approved source of truth (SkyyRose: `logo-registry.json`; CSV, dossiers, and image manifests are projections).
- Applicable classic and block flows, product types, payment failures, orders, and account authorization are exercised.
- Template override versions, hook contracts, HPOS behavior, and extension absence are checked.
- Every route has a documented customer job, business objective, complete section
  order, required features, content/data source, state matrix, responsive behavior,
  accessibility requirements, analytics events, and recovery paths.
- Merchandising relationships trace to catalog provenance; arbitrary or unavailable
  recommendations do not pass as complete-the-look logic.
- Fit, size, imagery, review, delivery and return facts are visible at the decision
  stage when applicable and trace to approved sources.
- Conversion recommendations are labeled `DURABLE`, `CURRENT`, `BRAND_SPECIFIC`,
  `INFERENCE`, or `EXPERIMENT`; unmeasured uplift claims are failures.

## Experience

- Desktop and mobile visual evidence exists for each changed primary route.
- Loading, empty, error, focus, hover, disabled, and success states are intentional.
- Brand fonts, colors, imagery, and voice match the approved contract.
- Motion honors reduced motion and has a non-motion fallback.
- The distinctiveness score passes the approved threshold; generic luxury patterns are a failure.
- Crop, focal point, narrative order, CTA visibility, and interaction substitutions are verified per viewport.
- `preview.html` renders desktop, tablet/mobile, critical states and annotations;
  it is reviewed eyes-on independently of the builder.
- `contract.json` and `evidence.json` validate, and their route, section,
  component and evidence IDs match the rendered HTML.

## Accessibility and performance

- Keyboard navigation, focus visibility, labels, landmarks, alternatives, and contrast are checked.
- Automated accessibility findings are triaged; serious violations remain failures.
- Responsive images, script loading, WebGL/media fallbacks, and asset budgets are checked.
- Browser console and network errors introduced by the candidate remain failures.

## Security and release

- WordPress escaping, sanitization, nonces, capabilities, and REST visibility are checked where touched.
- Package contents, version metadata, changelog, rollback steps, and deployment target are documented.
- Evidence is bound to the same candidate; mixed hashes invalidate the report.
- Commit, merge, upload, paid API use, and deployment require explicit human approval.
- Translation catalog, RTL assets, licenses, dependency provenance, installability, and package exclusions pass.
- Source, built, and packaged candidate hashes form one documented provenance chain.
