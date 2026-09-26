# Context Resolver + Creative OS — implementation specification

Status: DESIGN ONLY. Owner decisions supplied on 2026-09-23 are canonical in `constitution.json`; engineering choices below are proposed implementation contracts, not additional owner-ratified Brand DNA. The final K/P/S owner block completes ratification of v1. No runtime is implemented by this document.

## Architecture and ownership

Constitution → Context Resolver → Job Contract → Creative OS → Specialist Production → Verification → Approval / Release.

The Constitution defines protected identity and durable grammar. The Resolver determines applicable truth and constraints. The Job Contract defines the work and its purpose. Creative OS explores possibilities within that contract. Specialist production produces actual artifacts. Verification evaluates those artifacts. Separate authorization permits publication, deployment or spending.

Temporary channel specifications, dimensions, browser requirements, model settings, campaign compositions and platform policies belong in versioned adapters or job contracts, never permanent DNA. Runtime libraries and vendors remain implementation choices to verify at implementation time.

## Resolver interface

Proposed operation: `resolve_context(request) -> resolved_context`. It is read-only. It must not update sources, infer approval, publish, spend or generate media.

Required request fields:

| Field | Contract |
|---|---|
| job_id, brand, objective | Stable job identity, SkyyRose brand identity and concrete intended outcome |
| collection_context, campaign_brief | Named context and versioned brief reference; explicit null with reason when absent |
| lifecycle_stage | M1_RESEARCH, M2_CREATIVE_EXPLORATION, M3_PROTOTYPE, M4_CANDIDATE_ABN, M5_PRODUCTION, M6_RELEASE_CANDIDATE, M7_RELEASE_PUBLICATION, M8_MEASUREMENT_LEARNING, M9_ARCHIVE_PROVENANCE |
| channel, intended_use, audience | Output medium/use; distinguish internal proposals from customer-facing work |
| representation_mode | EXACT_PRODUCT, PRODUCT_CONCEPT or BRAND_ABSTRACT |
| products | SKU plus required views and details; empty only when no real product is represented |
| decisions, constraints | Explicit source references, current brief permissions and unresolved choices |

Resolved output contains `resolution_id`, request digest, Constitution version **and content digest**, selected rule IDs, applicable context, source digests/timestamps, per-field authority, resolved source references, protected constraints, creative freedoms, conflicts, gaps, status and decision/supersession lineage. Status is READY, READY_WITH_NONBLOCKING_GAPS or BLOCKED. Each gap identifies its field, source, affected deliverable/stage and why it is blocking or nonblocking. Missing irrelevant data must not block unrelated work.

An immutable output snapshot may contain resolved values for reproducibility; it is never an editable competing product source. Resolve each real SKU through `from skyyrose.core.product import get_product` / `get_product(sku)`; non-Python callers use the equivalent CLI. Unknown SKU errors fail closed. Check its `gaps` against the requested depiction rather than treating all possible views as universally required.

## Field authority and conflict resolution

| Field/domain | Authority and behavior |
|---|---|
| Constitutional decisions | Explicit owner-ratified Constitution with decision references; newer explicit scoped decisions supersede conflicting older guidance |
| Product identity, specifications, desired commercial data and media bindings | Unified registry via `get_product(sku)`; latest founder corrections are authoritative and must be reconciled in the owning source, not silently patched in a resolver snapshot |
| Live availability, variation/session purchasability, selection and transaction state | Current WooCommerce context; desired registry state is not proof of live checkout state |
| Existing storefront font implementation | `typography.json` until deliberately changed; not eternal Brand DNA |
| Approved asset geometry and usage | Authoritative asset and applicable permission; environmental materials do not rewrite protected logo or garment treatments |
| Campaign/context expression | Approved scoped brief under applicable constitutional and factual limits |
| Historical deployment/research | Evidence and inspiration; frequency and success do not confer constitutional authority |
| Platform and channel requirements | Current versioned adapter with source, retrieval date and applicable use |

Conflicts are field-specific; no blanket “newest file wins.” Newer owner decisions are applied to their stated scope. The resolver records both sides, the governing decision and the result. Unresolved material conflicts block the dependent job stage. Apply K1-001–K5-001, P1-001–P8-001 and S1-001–S12-001 from the final owner block. Environmental, natural-location and accessible UI palette freedom supersedes conflicting older universal color restrictions within those scopes; products and protected marks remain governed separately. Do not invent device-status assignments.

Founder statements do not require manufacturer, photographic or third-party reconfirmation. Evidence sufficiency asks whether the requested depiction is specified, not whether Corey knows his product. Do not invent an unspecified back or detail. If known founder facts conflict with a stale registry record, report the exact source reconciliation required and prevent stale product output.

Cache by request digest, Constitution digest, selected decision/brief digests, relevant registry/reference digests and adapter versions. Registry mtime or CSV mtime alone is insufficient. Live commerce state has an explicitly fresh lookup at the relevant interaction; do not reuse a creative snapshot as live purchase truth. Invalidations are dependency-based, with no stale-success fallback on source error.

## Job contract and exploration

The contract binds a resolved context to purpose, audience assumptions, deliverables, intended emotion/discovery outcome, authored meaning, representation mode, SKU/view bindings, production method, success evidence, applicable channel/technical/accessibility/commerce requirements, approval requirements, novelty dimensions and open issues. Record hashes of the context and brief used. Contract changes create a new version and invalidate affected downstream checks.

For major campaigns, collection experiences and significant creative initiatives, Creative OS should generate materially distinct directions, not merely cosmetic variants of yesterday's successful composition. Routine SKU updates, crops and adaptations do not require a new creative territory; meaningful reuse remains permitted. Each candidate records an authored rationale, relation to collection/product/brand meaning, applicable novelty dimensions, reused devices and why reuse is meaningful, production feasibility, expected interaction costs, and planned verification. Candidate count is a job choice, not a universal brand rule. Stillness, brightness, minimalism, physical or conversational formats are legitimate alongside spatial worlds.

Wonder, atmosphere and spectacle are valid creative purposes. Complex interaction must have a defined experiential role; it need not be directly transactional. Mystery and intentional friction are permitted with recoverable controls, orientation and critical commerce access. Preserve innovative intent as uncertainty resolves through production.

## Local Discovery Protocol

1. Trigger when place, geography, movement, culture, architecture or local storytelling could meaningfully strengthen the brief. Record why it is useful, or why geographic exploration is not relevant.
2. Investigate Bay Area material beyond familiar bridges and skylines: relevant streets, neighborhoods, transit, industrial and waterfront environments, landscapes, infrastructure, cultural locations and natural geography.
3. Record each candidate location, identifiable source, factual confidence, relevance to authored meaning, prior-use evidence if available, access/rights questions and selection rationale. Source uncertain or current claims before customer-facing use; do not equate an image reference with a location permit or endorsement.
4. Compare alternatives for meaning and creative difference. No landmark is mandatory; no fixed search quota is Brand DNA.
5. Preserve truthful origin, product story, historical meaning and partnership status. A metaphor must not imply an unsupported partnership or false historical event.

## Product modes and fidelity-preserving production

EXACT_PRODUCT applies whenever an actual SKU is represented, irrespective of medium or chosen label. PRODUCT_CONCEPT identifies a nonexistent/future product proposal internally and cannot masquerade as current SKU truth. BRAND_ABSTRACT represents no real product. A real-SKU advertisement cannot evade F1 by setting its mode to concept. Detect mode/content mismatches and block.

Before full production approval, document a credible method with required inputs: approved source photography, compositing, validated product photography, validated 3D/scans, controlled rendering or another demonstrably fidelity-preserving method. Generate the world around the product when regeneration cannot preserve it. A planned later repair is not a credible fidelity method.

Required-view evidence missing: **BLOCKED — insufficient authoritative product evidence**, with the exact missing view/detail and affected deliverable. A prototype may substitute an obvious non-product placeholder, explicitly recorded as such; it may not use a near-replica mistaken for the SKU. No missing real-product detail is invented.

## Verification contract

Every check binds the exact deliverable hash, reference/input hashes, applicable rule/requirement IDs, scope, method, reviewer or system identity, timestamp, observations, evidence references and outcome. Gate results are PASS / FAIL / BLOCKED. An inapplicable gate has `applicable: false`, a reason and `result: null`; it is not silently called PASS.

Product Fidelity checks all visually applicable characteristics: silhouette, proportions, construction/cut/geometry, approved colorway, material appearance, artwork, logos, placement, authoritative dimensions, trims, relevant stitching/detail and front/back identity. Each criterion records expected source reference, observed result and review evidence. PASS requires all applicable criteria to pass. FAIL requires remediation and re-review; missing sufficient evidence is BLOCKED. Similarity scores, filenames, a provider success receipt or aesthetic quality alone cannot establish fidelity.

The final composed/cropped/animated deliverable is verified, not merely its source photograph or 3D model. Source, product, composition, color, animation, camera/view or output changes invalidate the relevant checks. Do not crop away a required product detail without revising the contract and checking the resulting depiction.

Release Candidate requires applicable Constitution, Product Fidelity, Factual Claims, Rights/Approvals, Channel Requirements, Creative QA, Technical QA, Accessibility and Commerce Integrity gates. Novelty/saturation observations and applicable experiment evidence must be recorded. Any applicable FAIL or BLOCKED prevents release-ready status; no average score can override it. Automated and manual coverage remain distinct; do not claim comprehensive accessibility from automated checks alone.

## Lifecycle and approvals

| Stage | Required behavior |
|---|---|
| M1 Research | Separate sources, observations, hypotheses and unknowns |
| M2 Creative Exploration | Label proposals; preserve protected truth while exploring broadly |
| M3 Prototype | Test experience/method; obvious non-product placeholders permitted; never deceptive near-replicas |
| M4 Candidate / A-B-n | Bind candidate lineage, hypotheses, differences and evidence; identify credible product method |
| M5 Production | Full production approval requires credible fidelity-preserving inputs/method; no fidelity debt |
| M6 Release Candidate | All applicable gates PASS; novelty/saturation and applicable experiments recorded |
| M7 Release / Publication | Require action-specific authority and exact approved artifact/environment/scope |
| M8 Measurement & Learning | Record experiment context, results, limitations and recommendations; no automatic constitutional changes |
| M9 Archive / Provenance | Retain source/decision/artifact lineage, receipts and supersession history |

Stage transition records reference the exact contract and outputs plus applicable evidence. New material changes return affected checks to pending; an old release approval cannot authorize a changed artifact. A valid approval contains action, actor, scope, artifact/version, environment/account when relevant, budget when spending, timestamp and any expiry/conditions. Verify current scope before acting. Verification readiness and action authorization are separate fields.

## Learning and saturation

The approved S1–S12 policy requires awareness of recent relevant work, meaningful novelty for major initiatives, practical exploration of distinct hypotheses before expensive final production, and contextual learning. Routine crops and adaptations are not independently required to reinvent the campaign. Preserve the `when practical` qualifier; record why multi-direction exploration is impractical when applicable, without inventing a universal candidate quota.

Each direction records: hypothesis, underlying meaning, visual direction, material language, environment/location, narrative approach, product role, interaction/shopping idea, novelty relative to recent work, execution approach, risk and expected learning.

Keep four experiment classes distinct: CREATIVE_DIRECTION (which concept/world expresses meaning), EXPERIENCE (which interaction/discovery/shopping model strengthens experience), EXECUTION (which composition/copy/edit/format/hook/sequence/framing works), MARKET (which released version produces intended outcomes). A market experiment still requires separate authority for publication and spend.

For every major concept, record a difference map against identifiable recent relevant work: each meaningful dimension, NEW/EVOLVED/EXISTING assessment, evidence, what changed and why it matters. These example labels describe differences, not permanent device statuses. Evaluate constitutional compliance and meaningful novelty on separate axes; neither similarity nor novelty proves the other. Review applicable material dimensions across visual direction, material language, palette, environment, location, architecture, composition, camera, story, character, sound, media, motion, technology, interaction, discovery, shopping, physical/digital relationships and channel behavior.

Synthesis is permitted when coherent. Record contributing candidate IDs and elements, rationale and a new candidate/prototype identity. The synthesis must be tested itself; prior candidate successes do not transfer automatically. Do not stack unrelated features to simulate innovation.

Archive significant initiatives with applicable campaign/initiative identity, Constitution and context-bundle versions, collection, SKUs, content intents, directions, hypotheses, selection, synthesized elements, devices, materials, palette, locations, camera language, interaction, shopping mechanic, production methods, channels, market results, creative/experience/channel learning, failures and saturation update. Mark unmeasured results unknown instead of inventing outcomes. Learning remains contextual knowledge. Explicit owner ratification is required to change constitutional rules. The earlier proposed REQUIRED/PREFERRED/AVAILABLE/ROTATE/SCOPED/RETIRED taxonomy is historical and unadopted; S completion does not approve it.

## Palette authority and Kids context

Resolve eight separate palette domains: PRODUCT, PROTECTED_ASSET, INTERFACE, ENVIRONMENT, PHOTOGRAPHIC, CAMPAIGN, LIGHTING, NATURAL_LOCATION. Every materially consequential palette records domain, authority source/reference, applicable permissions, purpose and protected-color checks. Freedom never transfers automatically across domains. Truthful blue sky is permitted without making blue a master-brand color. Appropriate blue UI state does not authorize blue garment graphics. Blue environmental light requires context-sensitive review and cannot silently render an actual black garment as blue. Protected marks retain governed color/material treatments. Broad campaign and environmental experimentation is permitted under P4/P7; retain factual location and product identity.

Kids is a distinct contextual world with heir, continuation, inheritance, imagination, possibility and next-generation meaning. Its creative language need not shrink adult collections. Treat it as a priority for appropriate experiential innovation, character agency, adaptive journeys and play. Characters, rooms, mascots and narrative objects have no authority to redesign real products, marks or origin history. Actual Kids products remain subject to exact fidelity.

## Acceptance scenarios for implementation

These are design tests to implement later, not claims of executed runtime verification.

| Scenario | Expected result |
|---|---|
| Real SKU ad proposes altered logo size or colorway | F1 FAIL; change the output, not the product source to fit it |
| Required back view lacks authoritative information | BLOCKED with named missing view; never generate an imagined back |
| Corey supplies an exact product fact | Accept founder authority; reconcile owning source and test execution fidelity without third-party proof |
| Approved composited product in a bright, new environment | Allowed when applicable context/asset rules and fidelity pass; darkness is not mandatory |
| Kids playful discovery without a throne | Allowed by K1-001–K3-001 within master constraints and exact Kids-product fidelity |
| Surprising interaction with clear escape and accessible fallback | Assess purpose and recoverability; do not reject solely for departing from conventional ecommerce |
| Prior successful chrome/monument composition repeated without rationale | Creative QA flags G8/N issue; historical performance alone is insufficient justification |
| Real SKU mislabeled PRODUCT_CONCEPT | BLOCKED mode/content mismatch; strict product gate applies |
| Artwork source, rule or final artifact changes after PASS | Relevant prior PASS invalidated; re-resolve/re-verify |
| Registry desired availability differs from live cart | Preserve source distinction; live transaction state governs purchase action |
| Abstract brand work with no SKU | Product gate inapplicable with reason; other applicable gates still required |
| All quality gates pass, but no publishing/spend authority | Release-ready may be true; action remains unauthorized |
| New owner G8 conflicts with old hierarchy proposal | Owner final Creative Evolution wording wins; retain old proposal only in provenance |
| Truthful blue sky, accessible UI colors or a new campaign palette | Apply separate P domains; permit scoped freedom without recoloring real products or protected marks |
| A new direction synthesizes elements from three candidates | Create new candidate lineage and test the synthesis itself |
| Generic execution wins a market test | Archive contextual results; do not alter constitutional identity |

## Bounded next implementation phase — proposal only

1. Use the fully ratified v1 and adopted context-manifest digests as the reviewed implementation baseline; verify freshness before implementation.
2. Implement the read-only resolver and typed contracts using existing product readers; add focused tests for authority, scope, missing views, mode mismatch, supersession, source hashing and invalidation.
3. Shadow one explicitly selected consumer, likely the existing brand-context consumer after fresh inspection. Compare current and proposed outputs across representative jobs. Keep a rollback switch and preserve working behavior; do not migrate all consumers at once.
4. Integrate job contracts and artifact-bound gate records without provider execution, publication or spend. Demonstrate FAIL/BLOCKED cannot become release-ready and verify concept/abstract applicability.
5. Review evidence before authorizing broader migration or production runtime. Creative-provider trials, live commerce verification, publishing, deployment and spend each retain their applicable authorization boundaries.

No timeline, existing runtime pass or production readiness is claimed by this specification.
