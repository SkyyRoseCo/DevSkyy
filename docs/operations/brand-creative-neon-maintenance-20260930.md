# Brand, Creative OS, and Neon maintenance — 2026-09-30

## Brand source of truth

The editable SkyyRose product source of truth is
[`wordpress-theme/skyyrose-flagship/data/logo-registry.json`](../../wordpress-theme/skyyrose-flagship/data/logo-registry.json).
Application reads should use `from skyyrose.core.product import get_product` and
`get_product(sku)`. Preserve Corey's founder-confirmed product facts and make
corrections in the canonical registry workflow; CSVs, dossiers, and manifests
are projections or consumers.

The owner-ratified brand constitution at
[`docs/brand/constitution-v1/`](../brand/constitution-v1/README.md) is a
separate authority. Current verification found all 14 stored artifact hashes
matching, all 72 records `OWNER_RATIFIED`, and zero unresolved constitutional
decisions. A prior report generalized drift from a stale primary checkout; that
claim is superseded by this current check. No canonical brand or product file
was changed for this maintenance work.

## Creative OS tracking implementation

The candidate adds six modules under `skyyrose/elite_studio/creative/`:
`editorial.py`, `local_composite.py`, `spend_ledger.py`,
`governor_reporting.py`, `receipt_reader.py`, and `reporting_app.py`, exported
through the package `__init__.py`. They provide local editorial/composite
workflows, spend and receipt records, and reporting surfaces. The implementation
and its fixtures are local, synthetic, and read-only with respect to paid
providers. It is not a complete live provider gateway, does not demonstrate paid
execution, and does not establish release approval.

The earlier integration tree had **339 Python tests pass**, including the
concurrent report-write regression and coverage for the context resolver,
Creative Job, reporting, local composite, spend ledger, database fail-loud
behavior, and `tests/api/analytics`. These results do not establish final CI on
the later PR head; focused follow-up results are listed below.

## Neon analytics migration

Owner-approved revision `sr_analytics_001` is already applied to Neon project
`devskyy` (`fancy-water-68795007`), branch `br-tiny-brook-ahciwidn`, database
`neondb`. The current metadata recheck found the revision, 9 indexes, primary
key `id`, nullable foreign key `user_id -> users(id)` with `ON DELETE SET NULL`,
and zero events. No event payloads or customer rows were read. **Do not rerun
the migration.** The detailed operator and qualification record is
[`analytics-legacy-schema-migration.md`](analytics-legacy-schema-migration.md);
the live apply caveat and recheck are recorded in
[`live-migration-20260930.md`](../../tasks/e2e-tracking-fixes-20260929/verification/live-migration-20260930.md).

Disposable PostgreSQL 17 and Docker checks passed before the live apply. The
Neon connector's prepared DDL omitted a dollar-quoted `DO` guard after rejecting
that block; its preconditions were checked on the live schema before applying,
and the resulting objects were rechecked afterward. This is not an Alembic
execution, and production ingestion/reporting remain unvalidated. The previous
clean-room report is historical evidence for the earlier pre-migration state,
not the current Neon state.

## Maintenance boundaries

Keep follow-up work scoped to the owning surfaces. Product corrections belong in
the canonical registry process; ratified constitution text is immutable without
an owner decision. Recheck current branch/schema state before any future
migration request, and distinguish local tests, disposable database checks,
authenticated production metadata, and production application flows. This record
documents maintenance evidence; it does not authorize deployment, publication,
or additional provider execution.

## Prior integration tree verification

The integration checkout is based on `origin/main` at
`3e720a4903a7e4f09813d71741d0a3b1f2be5556`. It includes the isolated analytics
migration and its dependency lockfile, Creative OS receipt/reporting modules,
consented storefront ingestion, measured dashboard consumers, and the portable
tracking board. Unrelated dirty worktrees and generated historical observation
logs are excluded.

- Python integration suites: 339 passed against the exact integration Git tree,
  including the concurrent report-write regression.
- Before dependency remediation, frontend suite: 270 passed across 24 files;
  production build and TypeScript passed.
- Before dependency remediation, frontend lint: zero errors, 228 existing
  warnings.
- Desktop/mobile reporting fixtures: six Playwright checks passed.
- Theme consent tests: 30 passed; PHP relay fixtures: 33 checks passed.
- Tracker unit tests: 34 passed against the exact integration Git tree.
- Combined synthetic replay: all four checks passed against the exact
  integration Git tree, including separate-process persistence, tamper/auth
  rejection, exact synthetic pixel/receipt binding, and read-only signed
  Governor reporting.
- Product-registry projection check, dependency lock check, and scoped Ruff
  passed.

The tracker resolves repository-relative source bindings and represents missing
evidence as unavailable. It no longer relies on older absolute worktree paths.
The old archive builder is excluded because its broad `*.lock` filter dropped
`uv.lock`; release verification must use the committed Git tree.

## CI and dependency-audit follow-up

The root TypeScript CI job first failed before running tests at the production
dependency audit, which reported inherited advisories from the base. Focused,
compatible dependency patches in the root and frontend manifests and lockfiles
now report **zero high or critical advisories**. Current audit totals are root:
1 low and 8 moderate; frontend: 6 low and 6 moderate. After remediation, clean
`npm ci` installs succeeded in both packages. The root JavaScript suite passed
all 690 tests and coverage thresholds; the frontend suite passed all 270 tests.
Both packages passed type checking and builds. Resolve the final GitHub CI state
before treating the PR as green. The frontend build also retains its existing
Turbopack file-tracing warning.

## Current PR head follow-up

The current committed head is `846c69e0af4d9143332e49582d07d8265d52dc50`.
Subsequent focused fixes add these verified candidate checks:

- `5487ccad0`: backend webhook 503 handling, ledger schema, and SQLite
  initialization; **126 tests passed**.
- `5fec7ceb6`: Meta request headers and immutable receipts; **51 tests passed**,
  including execution against the actual Lua-backed `fakeredis` path.
- `9a6c0835e`: bound relay coverage; **39 checks passed**. Two legacy-visitor
  metric checks correctly report unavailable and must not be presented as
  measured traffic.
- `ff60ac324`: tailored Copilot review instructions and MCP context. GitHub
  repository settings confirmed the save; built-in GitHub and Playwright MCP
  remain enabled, and Context7 exposes only `resolve-library-id` and
  `query-docs`, both marked read-only.
- `846c69e0a`: bounds and reaps independent database workers. The earlier
  analytics CI failure exposed four webhook fixture failures and an outer
  subprocess timeout (10 seconds) shorter than the inner worker timeout (30
  seconds). The fixture issue is fixed; the worker timeout is now bounded at 60
  seconds with cleanup, while assertions remain intact. The normal focused
  analytics run passed **46 tests**.

These focused results do not replace the final CI and review gate for the
current head; that gate remains pending. Do not claim merge or live analytics
acceptance from these checks.

## Public theme version observation

A read-only inspection of the public site's `skyyrose-flagship/style.css`
reports SkyyRose Flagship2 version `2.3.1`, while the repository's
`wordpress-theme/skyyrose-flagship-2/` package metadata reports `2.5.0`. This is
a public metadata observation, not evidence of the deployed source tree or a
completed release. No staging or production files were changed.

The focused analytics source port for `wordpress-theme/skyyrose-flagship-2/` has
passed bounded source qualification: 29 source/minified collector checks, 36
relay checks, 13 bootstrap checks, five generator-guard checks, and two Chromium
V2 checks. Native asset and POT checks, the canonical 33-product registry check,
existing shell/card/prelaunch runtime checks, and source integrity also passed
with pinned Node 22.23.2/npm 10.9.8. Standalone V2 bootstrap, relay, and card
checks confirmed no sibling V1 dependency. No source certification or digest
changed. Independent PHP and JavaScript reviews approved; the final Python
`TOKEN_PARSE` rerun passed all five guard tests and projection parity.

The combined V1 and V2 unit/relay/bootstrap/parity and browser commands passed
against the final source tree. The aggregate GitHub CI/review gate remains
pending. Focused V2 checks do not establish deployment or live analytics
acceptance. No staging or production files were changed. The already-completed
Neon migration remains in place; do not rerun it.
