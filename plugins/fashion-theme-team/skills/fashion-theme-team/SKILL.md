---
name: fashion-theme-team
description: Orchestrates an end-to-end specialist team for fashion storefront and WooCommerce theme audits, design systems, builds, integrations, quality gates, and release evidence. Use when a request spans multiple theme disciplines or asks to take a fashion-commerce experience from discovery through a production-ready candidate. Do not use for a bounded one-file fix, content-only request, or production deployment without explicit approval.
---

# Fashion Theme Team Motherbase

Build a complete, distinctive fashion-commerce theme through separated
architecture, design-system, implementation, review, and release roles. This
skill is the lightweight router. Load only the reference and charter needed for
the current phase; never inject the whole team into every agent context.

The governed knowledge layer is [brain/README.md](brain/README.md). Route every
fashion, merchandising, page, conversion, fit, engineering, or measurement task
through `brain/taxonomy.json`; load only the selected packs. Brain guidance never
outranks repository canon, current official documentation, or approved SOT facts.
All presentation and sale-candidate artifacts use the SkyyRose system in
`brain/brand/`; the rendered hub is `brain/showcase/index.html`. For new or
substantially redesigned storefronts, load the complete V2 page, section,
responsive, feature, and imagery plan from `brain/v2/v2-page-plan.json` and its
visual companion `brain/showcase/v2-page-atlas.html`.

All callable tools are available to the team but only active subsets are loaded
into a role context by default. Default active tools are `Read`, `Grep`,
`Glob`, and `Bash`; other tools are request-explicit. This keeps context budgets
predictable while preserving capability.

## One team distribution control

`/Users/theceo/plugins/fashion-theme-team` is the canonical editable Fashion
Theme Team source. The DevSkyy vendor package and the Codex installed cache are
distributions, not independent products. A feature, agent, capability, charter,
or verifier change is complete only when the designated distributions have the
same package content as the canonical source, excluding Git metadata and local
runtime caches.

Use `scripts/sync-team-distributions.py` to inspect or synchronize a named
distribution. Run `--check` before and after an `--apply --prune` operation.
Read [references/distribution-contract.md](references/distribution-contract.md)
before a synchronization. Do not author changes directly in the installed cache,
and do not make a vendor-only capability claim. The cache may be refreshed only
from a verified source package; a source change must be propagated deliberately.

## Capability routing

Use the narrowest execution skill for the phase, then return to this motherbase
for scheduling and evidence integration:

| Capability                                                   | Skill                            | Primary owners                                                                   |
| ------------------------------------------------------------ | -------------------------------- | -------------------------------------------------------------------------------- |
| Fashion Commerce Brain, page blueprints, V2 atlas            | `fashion-strategy-brain`         | commerce strategist, brand architect, merchandising architect, knowledge curator |
| SkyyRose visual artifact system and imagery direction        | `fashion-brand-experience`       | brand architect, brand-systems researcher, typography/layout director            |
| Exact-product media, native collection scenes, and fidelity gates | `product-fidelity-image-edits` | brand architect, product-truth owner, independent visual reviewer                 |
| Tokens, components, states, design-system adoption           | `fashion-design-system`          | design-system engineer and inner pod                                             |
| Catalog, WooCommerce, fit, returns, product discovery        | `fashion-commerce-engineering`   | catalog SOT, WooCommerce, merchandising, fit/returns                             |
| PHP/CSS/JS implementation, immersive motion, fallbacks       | `fashion-frontend-motion`        | frontend, WooCommerce, motion/responsive                                         |
| WCAG, content states, reduced motion, performance            | `fashion-a11y-performance`       | accessibility/content engineer and independent reviewer                          |
| Browser, visual, and purchase-journey proof                  | `fashion-visual-commerce-qa`     | visual red team, visual commerce QA, accessibility/performance reviewer          |
| HTML/JSON/evidence parity                                    | `fashion-handoff-contracts`      | every role producing an artifact; lead integrates                                |
| Packaging, marketplace readiness, rollback, release evidence | `fashion-release-evidence`       | release engineer and DesignOps                                                   |
| 44-item premium feature implementation and enterprise gates  | `fashion-premium-feature-system` | frontend, commerce, design-system, accessibility, QA, and release owners         |
| 234 branded capability adapters and source-gap closure       | `fashion-branded-skills`         | knowledge curator, brand systems, DesignOps, and independent reviewer            |
| Optional provider execution and self-healing                 | `elite-builder-runtime`          | explicitly approved runtime owner                                                |
| End-to-end task, issue, evidence, and release control        | `fashion-e2e-task-execution`     | lead plus independent reviewer                                                    |

Do not load all skills by default. A role may temporarily expand its tool profile
only under `references/tool-budget-and-loading.md`, with the expansion recorded
in the phase ledger. The scheduler permits four active roles maximum.

Engineering mechanics for WordPress builds, WooCommerce PDP correctness, CSS,
and three.js/immersive work live in the on-demand library at
[references/engineering/index.md](references/engineering/index.md). Load only
the single file the active phase needs.

## Inputs

- Target repository and theme path.
- Requested outcome, deadline, target marketplace, compatibility matrix, and surfaces in scope.
- Brand, catalog, and imagery sources of truth. For SkyyRose, product facts
  come only from `logo-registry.json`; read
  [references/product-registry-authority.md](references/product-registry-authority.md)
  before any catalog, imagery, or product-spec work.
- Existing design-system artifacts and ownership.
- Allowed external services and approval boundaries.
- Existing build, lint, test, browser, and packaging commands.
- Fashion segment, audience, assortment/launch model, service promise, and measurement baseline.

For a SkyyRose redesign, record the implementation target explicitly. The
current V2 theme path is `wordpress-theme/skyyrose-flagship-2`; the V2 atlas and
page plan are planning inputs, not proof of the runtime implementation. Current
founder direction may intentionally override an older presentation heuristic,
while founder-confirmed product facts, registry authority, accessibility,
commerce behavior, and working features remain binding. Read
[references/verified-examples.md](references/verified-examples.md) before using
the redesign capabilities below.

If an input is absent, discover it read-only. Classify facts as `OBSERVED`,
`APPROVED`, `RECOMMENDED`, or `UNKNOWN`. Do not invent product data, commands,
URLs, credentials, licenses, or approval.

## Team selection

Read [references/autonomy-protocol.md](references/autonomy-protocol.md) and
[references/team-contract.md](references/team-contract.md) before dispatch.
Use the fourteen outer-team roles plus the design-system architect's eight-member
inner pod across waves for a full build. Keep only the lead plus three runnable
specialists active. Read `references/design-system-pod.md` only when the design
system phase is active. Stop and swap completed roles so specialist charters
and optional runtime tools remain lazy-loaded.

## Procedure

1. Run `scripts/preflight.sh <repo-root> [theme-path]`; record capability gaps
   without confusing optional-tool absence with plugin failure.
2. Have the lead initialize the durable phase ledger from
   [references/autonomy-protocol.md](references/autonomy-protocol.md), capture an
   immutable baseline, and confirm that the current-session authorization covers
   the proposed edits. Do not request the same approval again while that scope
   remains valid. Historical notes, receipts, or prior runs never grant current
   permission; obtain additional approval only for a newly consequential action
   or expanded scope.
   For every capability in scope, also load `fashion-e2e-task-execution` and
   issue a named project manager and create its task record before the first
   side effect. The E2E record binds scope, declared evidence, first-seen
   issues, resolutions, and completion; the phase ledger remains the cross-role
   schedule of record.
3. Run discovery and creative direction against
   [references/skyyrose-design-canon.md](references/skyyrose-design-canon.md) and
   [references/high-end-design-standard.md](references/high-end-design-standard.md).
   First route strategy, merchandising, fit/returns, page architecture, and
   measurement through the Fashion Theme Brain. Record loaded pack IDs and source
   freshness in the ledger.
   For a collection world, hero, lookbook, or model-in-scene asset, route the
   approved direction through `product-fidelity-image-edits` before any image-model
   call. Use `native_collection_scene` for final-commerce candidates. Treat
   `protected_scene_composite` as layout proof unless its separate native optical
   integration gate passes.
4. Census the existing system before creating tokens. Produce the governed
   artifacts in [references/design-system-contract.md](references/design-system-contract.md)
   through the inner pod in [references/design-system-pod.md](references/design-system-pod.md).
5. Create isolated worktrees or branches and assign non-overlapping ownership.
6. Execute implementation waves against
   [references/theme-deliverable-contract.md](references/theme-deliverable-contract.md)
   and [references/woocommerce-coverage.md](references/woocommerce-coverage.md).
   Every page in scope must have a complete section/feature/state contract derived
   from `brain/pages/page-blueprints.md` and a documented reason for deviations.
7. Integrate only checkpointed handoffs. Recompute the candidate manifest after
   every mutation and invalidate evidence tied to an older candidate.
8. Swap builders out and dispatch fresh independent reviewers. Apply every
   applicable gate in [references/acceptance-gates.md](references/acceptance-gates.md).
   Use [references/evidence-examples.md](references/evidence-examples.md) for the
   minimum proof format; every material claim must be verified.
9. Release engineering verifies hashes and issues `PASS`, `FAIL`, or `BLOCKED`.
   `PASS` means ready for founder review, never permission to publish or deploy.
10. Close agents, update the repository session log, and preserve the ledger so
    the next session resumes from state rather than rediscovering the project.
11. Before any role dispatch, confirm `references/tool-budget-and-loading.md` is
    the active profile for that role context and record any temporary expansion.
12. Load `elite-builder-runtime` only when explicitly requested. Its provider
    execution is a separate paid-action approval and its legacy knowledge never
    outranks repository canon.
13. Require structured visual handoffs: `preview.html`, `contract.json`, and
    `evidence.json`. HTML and JSON share stable route, section, component, and
    evidence IDs and validate against `brain/schemas/`. A prose-only visual
    handoff or an HTML/JSON mismatch is `FAIL`.
14. Brand every human-facing Fashion Theme Brain artifact as SkyyRose. Preserve
    the garment-first Oakland visual thesis, use one rose-gold accent, and do not
    substitute fabricated product imagery for SOT-verified or founder-approved media.
15. For every feature request, load `brain/features/premium-feature-catalog.json`
    and route the selected IDs through `fashion-premium-feature-system`. A
    screenshot match is not coverage: implementation, fallback, a11y, security,
    performance, commerce, and candidate-bound evidence are required.
16. Treat prompt engineering, typed prompt chains, and prompt caching as governed
    build infrastructure. Load `brain/prompts/prompt-orchestration.md`, record
    chain stage and cache disposition, and invalidate cached outputs whenever the
    candidate, SOT, founder decision, Brain pack, schema, rubric, rights state, or
    owned source changes. Cache misses must never block a correct uncached run.
17. Route bundled branding, copy, lifecycle, product, funnel, search, and social
    requests through `fashion-branded-skills`. Load one source only after exact
    hash verification, apply every recorded gap closure, and retrieve current
    authenticated primary authority at claim time.
18. For any Fashion Theme Team change, verify distribution parity with
    `scripts/sync-team-distributions.py --target <distribution> --check`. Only
    synchronize a known local distribution after the source verifier passes; run
    `--apply --prune`, rerun `--check`, then verify the destination package.

## Coordination rules

- Lead owns routing and mechanical integration; semantic conflicts return to the owning builder.
- Brand architect defines direction; design-system engineer owns reusable system implementation.
- Builders may edit only assigned paths and may not deploy or certify release.
- Reviewers are read-only and must cite candidate-bound evidence.
- Thread 1 is the lead. Threads 2-4 are the ready queue. Never exceed four active roles.
- Swap sequence: checkpoint, validate handoff, stop role, release slot, dispatch successor.
- Visual claims require eyes-on browser/image evidence. Technical, API, version,
  security, and marketplace claims require current authoritative primary
  documentation plus executable repository evidence when implementation is involved.
- Collection-scene media requires separate product-fidelity, native optical
  integration, collection-story, and founder-promotion states. Pixel equality,
  a beautiful plate, or a prompt receipt cannot substitute for another state.
- A rejected scene is quarantined evidence and may not be reused as a generation
  reference, scene authority, product authority, or wireable asset.
- Never pass secrets, customer data, hidden reasoning, or unrelated repository context to an agent.
- Preserve existing user changes and stop on unexpected overlapping edits.
- Local worktrees, checkpoint commits, builds, tests, browser runs, screenshots,
  and artifact generation are allowed after scope approval and must be logged.
- Every claim returned by a role must be backed by candidate-bound evidence:
  either deterministic artifact + eyes-on review, or current authoritative
  documentation + executable repository evidence.
- Require approval for new dependencies, credentials, paid APIs, remote writes,
  uploads, protected-branch merges, destructive actions, and deployment.
- Never claim that a merchandising or visual pattern will increase conversion.
  Classify it as `EXPERIMENT` with a metric, guardrails, instrumentation, and
  rollback rule unless candidate-bound results already prove it.

## Verification

From the plugin root:

```bash
bash scripts/verify.sh
```

Pass condition: exit `0`, all contracts and twenty-two charters are present, schemas
parse, and bundled scripts pass syntax checks. This proves plugin integrity
only. Operational readiness and theme release evidence are separate verdicts.

## Failure modes

- Missing source of truth: block only dependent catalog work; continue unaffected phases.
- Missing design-system contract: block broad component implementation.
- Overlapping ownership: stop affected agents and re-scope worktrees.
- Baseline already red: preserve the baseline and distinguish new failures.
- Reviewer changes code: invalidate independence and rerun review with a fresh role.
- Evidence from different candidate hashes: quarantine it and rerun against the current candidate.
- Transient failure: retry twice with preserved evidence and bounded backoff.
- Implementation failure: checkpoint, return to owner, increment attempt, then use a fresh reviewer.
- Baseline/environment/authority failure: record it without rewriting history or claiming success.
- Unsupported browser or unavailable staging: mark the corresponding gate `BLOCKED`.
- Deployment request: obtain explicit approval after presenting candidate identity, evidence, rollback plan, and target.
