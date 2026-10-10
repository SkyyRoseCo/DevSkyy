# Verified Examples for SkyyRose Redesign Routing

Coverage: **PARTIAL**. These examples verify the local routing, product-authority,
design-system, and motion-shell branches used by the current V2 redesign. They
do not prove a storefront render, deployment, payment, external write,
marketplace acceptance, or future environment state.

Shared context for each example: the founder requested reproduction of a
supplied visual reference in DevSkyy, with existing motion and commerce features
preserved. The implementation target is
`wordpress-theme/skyyrose-flagship-2`. Product facts come only from the root
`logo-registry.json` symlink and are read through
`skyyrose.core.product.get_product`. Current-session authorization covers the
scoped local redesign and skill repair; historical records never create new
authorization.

## Fashion Brand Experience

**Correct example — SOURCE_VERIFIED.** Translate the supplied composition into
SkyyRose's current visual language, including an intentionally centered footer
when directed, while preserving the exact brand lockup, founder-confirmed facts,
accessible navigation, and commerce affordances. Current founder direction
outranks an older anti-generic heuristic for this scoped presentation decision.
Expected: a direction contract tied to the supplied reference and current theme;
observed: the routing and precedence rules are present in the canonical skills,
but no storefront render is established by this example. Evidence:
`skills/fashion-theme-team/SKILL.md` (Inputs),
`skills/fashion-brand-experience/SKILL.md`, and the DevSkyy `AGENTS.md`, read
2026-09-21. Authentication: `NOT_APPLICABLE` for local source review.

**Incorrect example — ILLUSTRATIVE_UNEXECUTED.** Reject the supplied centered
composition solely because an older rule says “no generic centered-everything,”
or copy the unrelated reference brand's name and promise. Correction: honor the
founder's current composition direction, then express it with SkyyRose identity
and preserve the locked product and behavior contracts. The older heuristic is
an anti-generic guard, not authority to overrule current direction.

## Fashion Design System

**Correct example — SOURCE_VERIFIED guidance with related REPRODUCED_LOCAL checks.** Census existing tokens and selectors,
reuse the current type and spacing system, and add only the component rules
needed to reproduce the supplied composition at 390, 768, and 1440 widths.
Expected: existing components and motion states remain reachable; observed:
the 2026-09-21 motion-shell receipt records 26 passing local tests, including
focus restoration, menu isolation, reduced motion, Save-Data, poster fallback,
and media error recovery. Those tests do not reproduce the token census or
verify layout at the named widths; those design checks remain unverified here. Evidence:
`/Users/theceo/.agents/skills/skyyrose-3d-web-os/references/motion-shell-tests-20260921.log`,
modified 2026-09-21 15:04 -0700. Authentication: `NOT_APPLICABLE`.

**Incorrect example — ILLUSTRATIVE_UNEXECUTED.** Create a parallel token set or
replace stable header/dialog behavior because the screenshot appears visually
close. Correction: map the direction onto existing semantic tokens and states,
then rerun focused interaction, responsive, and reduced-motion checks. A static
screenshot cannot establish component-state preservation.

## Fashion Frontend and Motion

**Correct example — REPRODUCED_LOCAL.** Bind implementation to
`wordpress-theme/skyyrose-flagship-2`, retain existing animation controllers,
and change source before rebuilding tracked generated assets. Treat the V2 atlas
as a plan and require browser evidence for any rendered claim. Expected: motion,
focus, fallback, and commerce hooks survive the redesign; observed: the same
26/26 local shell tests passed on 2026-09-21, but no storefront visual pass is
claimed here. Evidence: the motion-shell receipt above and
`skills/fashion-frontend-motion/SKILL.md`. Authentication: `NOT_APPLICABLE`.

**Incorrect example — ILLUSTRATIVE_UNEXECUTED.** Edit the original V1 theme or
an installed plugin cache because it contains similar files, or cite the V2
atlas as proof that the storefront renders correctly. Correction: record the
discovered runtime target, edit its owned source, rebuild, and collect fresh
candidate-bound browser evidence. Planning artifacts and cache bytes are not
runtime evidence or canonical authoring sources.

## Fashion Commerce Engineering

**Correct example — REPRODUCED_LOCAL.** Call `get_product("br-003")` once and
use the returned commerce, media, design, authority, and `gaps` fields; keep
WooCommerce as live cart, stock, and order truth. Expected: unknown SKUs fail
closed and missing facts appear in `gaps`; observed on 2026-09-21 in the DevSkyy
repository Python environment: `br-003` resolved and returned `gaps: []`.
Evidence: `/Users/theceo/DevSkyy/skyyrose/core/product.py`, root
`logo-registry.json`, and local execution with
`/Users/theceo/DevSkyy/.venv/bin/python -m skyyrose.core.product br-003` on
2026-09-21; returned registry identity `c27f1a3809208542`. The observed
valid SKU result does not reproduce the unknown-SKU error branch. Authentication: `NOT_APPLICABLE`; this did not read or mutate
a live store.

**Incorrect example — ILLUSTRATIVE_UNEXECUTED.** Assemble a product from a CSV,
standalone dossier, image manifest, or several narrow readers, then fill a
missing field from inference. Correction: use `get_product`, respect `gaps`, and
ask the founder only for a genuinely absent fact. Projections may be checked for
drift but never become competing product authority.

## Authorization and distribution limits

A current user instruction authorizing scoped local edits remains valid within
that scope. A prior deployment log, approval note, successful authenticated run,
or available credential is historical evidence only; it does not authorize a
new deployment, upload, payment, paid provider call, or remote mutation. The
canonical editable plugin is `/Users/theceo/plugins/fashion-theme-team`.
Installed caches and vendored copies are distributions and must be updated only
through the documented verified synchronization workflow.

Refresh these examples when the theme target, product entry point, authorization
model, motion controller, test command, evidence schema, or canonical plugin
location changes. Add authenticated, candidate-bound examples before claiming
coverage of live staging, production, payment, deployment, or marketplace
acceptance.

## Founder-retired slogan

**Correct example — SOURCE_VERIFIED.** The founder retired the previous brand
slogan on 2026-09-21. Remove it from skill prose, schemas, examples, fixtures,
prompts, and rendered planning artifacts. State that no tagline is currently
authorized; use `SkyyRose` only as a brand-name fallback where a structured
nonempty value is required.

**Incorrect example — ILLUSTRATIVE_UNEXECUTED.** Preserve or quote the retired
wording as a warning, paraphrase it, or invent a successor. Correction: remove
the wording entirely and leave the tagline unauthorized until a new direct
founder instruction exists. Authentication: `NOT_APPLICABLE`. This documentation
correction does not establish a storefront render or deployment.
