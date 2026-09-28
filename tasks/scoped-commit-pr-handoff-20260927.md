# Scoped commits and PR handoff

Prepared from `/Users/theceo/DevSkyy`, branch `feat/single-product-entry-point`,
starting at `8b6ab3cda`.

## Scope and review

The user's request was to commit, scope a PR agent, and identify unfinished
work. A read-only PR scope agent inspected the pending groups and relevant
existing history. A TypeScript reviewer checked the Runway scaffold and 3D store
extraction. The review was bounded; it was not a complete audit of the
accumulated branch.

Selected implementation groups:

1. Registry-aware asset manifests and remaining registry consumers/writers.
2. Source-bound context resolver, creative job contracts, ratified constitution
   inputs, opt-in enhancer integration, focused tests, and runtime
   documentation.
3. Standalone Worktree Fleet and Wolf Memory MCP servers and isolated tests.
4. Fail-closed Runway dry-run scaffold, offline tests, integration
   documentation, and matching SDK dependency/lockfile.
5. 3D route-module export cleanup; shared job store remains in memory.
6. This handoff and clarification of local-only historical evidence links.

Normal commit hooks run for these groups. The three ratified source files used
by the resolver are narrowly excluded from formatting because exact source-byte
hashes are verified at runtime. Their content and existing hash bindings are
preserved. New commits use the established global Git identity; a stale local
fixture identity was corrected for this turn's commits only, with identical
trees.

## Proposed PR structure

Do not open a misleading narrow PR from the entire accumulated branch. A remote
fetch showed substantial divergence from `origin/main`: 143 main-only commits
and 68 branch-only commits immediately after the first new commit. Counts change
as the local series grows or remote branches advance.

Before publication, reconcile the pre-existing product/registry branch with
current main in an isolated checkout. Inspect patch equivalence and existing PRs
before selecting older dependencies. Do not rebase the shared dirty checkout or
sweep its residual work into a PR.

Suggested review units:

| PR                                   | Scope                                                                                                  | Dependency                                              |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------- |
| Product registry and asset integrity | Existing unified product entry point/registry migration plus remaining asset consumers and hash checks | Reconciled registry baseline                            |
| Creative context and job contracts   | Constitution inputs, resolver, job evidence contracts, enhancer integration, tests/docs                | Product registry PR                                     |
| Standalone local MCP services        | Fleet and Wolf implementations, entrypoints, tests, architecture docs                                  | Review current main's MCP configuration before applying |
| Disabled Runway preflight            | Closed qualification/Governor gates, request/response validation, rate limiter, offline tests, docs    | Current frontend/auth baseline                          |
| 3D route export cleanup              | Move shared state out of the Next.js route module                                                      | Current frontend/3D baseline                            |

No PR publication, push, deployment, paid call, or live-provider verification is
part of this handoff. Recheck current refs and all applicable CI before
publishing.

## Verification and limits

Validation uses a managed clean checkout at
`/Users/theceo/.codex/worktrees/pending-pr-validation/DevSkyy` with the existing
Python environment. Each tested candidate contains only committed source.
JavaScript validation may share installed dependencies, not uncommitted source.

- Clean product/registry/review/asset tests: **95 passed**.
- Clean context/creative contracts: **68 passed**.
- Clean MCP server tests: **107 passed**.
- Registry compatibility projection check: **PASS**.
- Asset manifest regeneration check: **PASS**.
- Clean Runway offline route/contract tests: **26 passed**; also passed in the
  working checkout. The clean run used shared installed JavaScript dependencies.
- Frontend type-check: **PASS**, including the clean implementation checkout.
  Frontend lint: **0 errors, 231 warnings** in the working checkout.
- Normal Python commit hooks reported mypy success across **1,730 source
  files**, unit-test success, and freshness success in the working checkout.
  That global type result is not a substitute for the isolated candidate tests.
- `git diff --check` reports one retained trailing-space warning at line 475 of
  `OWNER-RATIFICATION-20260923.md`. The original owner source is deliberately
  byte-preserved so its existing SHA-256 provenance remains valid.

The final chat reports final commit IDs and residual working-tree counts.
Authentication is not applicable to these offline tests. Fixture responses are
not authenticated provider evidence. Historical account, balance, visual review,
and deployment statements in retained documents were not refreshed here.

## Unfinished implementation

1. **Runway runtime qualification:** `qualification-gate.ts` always returns
   `ready: false`. Router identity, version, and settings digest still need a
   qualified server-runtime binding.
2. **Runway Governor and paid execution:** `governor.ts` always returns
   `authorized: false`. Real quota/audit authorization, paid task execution,
   task-to-operation receipts, and billing reconciliation are not implemented.
3. **Redis integration evidence:** limiter tests use a substitute. They do not
   prove connectivity, expiry, or atomic behavior across deployed instances.
4. **3D persistence:** `jobs/store.ts` remains a module-level array. Durable
   storage, cross-instance consistency, and restart recovery remain absent.
5. **Creative validation integrations:** job contracts validate supplied
   evidence; they do not perform pixel inspection, authenticate reviewers,
   verify rights, or grant release/spend authority. Broad consumer migration is
   not implemented.
6. **PR integration:** the accumulated branch needs baseline reconciliation,
   appropriately scoped PRs, remote CI, and broader review before merge.
7. **MCP reclaim lifecycle bug (review finding):** in
   `mcp_servers/worktree_fleet/store.py`, reclaiming a released checkout with
   the same owner and branch updates only `last_seen_at`. It does not restore
   `active` status or clear `closed_at`, so a clean resumed checkout can remain
   eligible for pruning. Branch commits survive, but the checkout/claim can be
   removed. Reactivate the claim or reject closed claims, then add release →
   reclaim → prune regression coverage before merging the MCP scope. The
   existing 107 passing MCP tests do not cover this identified lifecycle gap.

## Preserved outside these commits

- Broad retired-brand-copy changes, their scanner and CI wiring, theme changes,
  skills/plugin revisions, and agent/configuration documentation.
- Love Hurts and hero-motion prototypes, `ready.glb`, staging screenshots,
  historical investigation/production-readiness evidence, and local planning.
- `.worktrees/`, which contains a nested checkout and must never be staged as
  ordinary application source.
- Other independent test or workflow edits not selected above.

Uncommitted does not mean broken. These groups need their own bounded review and
appropriate checks; their production readiness was not established in this run.

## Product authority for the next agent

The root `logo-registry.json` is a symlink to
`wordpress-theme/skyyrose-flagship/data/logo-registry.json`, the single editable
product authority. Read via `skyyrose.core.product.get_product`; do not
substitute older CSV/dossier snapshots or invent product facts. Corey's latest
explicit maker specifications are `FOUNDER_CONFIRMED`; preserve their exact
wording, dimensions, ranges, materials, artwork, and placements. Verify
execution against his instructions without demanding additional proof of his
product knowledge. Verify the registry schema/current corrections in any new
checkout and run `scripts/sync_product_registry.py --check` before handoff.
Follow governing `AGENTS.md` for writes and preserve all unrelated working-tree
changes.
