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

Fresh integration evidence reports **338 Python tests passed**, covering the
context resolver, Creative Job, reporting, local composite, spend ledger,
database fail-loud behavior, and `tests/api/analytics`. Treat this as candidate
test evidence; it does not imply deployment or production acceptance.

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

## Final local verification

The integration checkout is based on `origin/main` at
`3e720a4903a7e4f09813d71741d0a3b1f2be5556`. It includes the isolated analytics
migration and its dependency lockfile, Creative OS receipt/reporting modules,
consented storefront ingestion, measured dashboard consumers, and the portable
tracking board. Unrelated dirty worktrees and generated historical observation
logs are excluded.

- Python integration suites: 338 passed.
- Frontend suite: 270 passed across 24 files; production build and TypeScript
  passed.
- Frontend lint: zero errors, 228 existing warnings.
- Desktop/mobile reporting fixtures: six Playwright checks passed.
- Theme consent tests: 30 passed; PHP relay fixtures: 33 checks passed.
- Tracker unit tests: 34 passed.
- Combined synthetic replay: all four checks passed, including separate-process
  persistence, tamper/auth rejection, exact synthetic pixel/receipt binding, and
  read-only signed Governor reporting.
- Product-registry projection check, dependency lock check, and scoped Ruff
  passed.

The tracker resolves repository-relative source bindings and represents missing
evidence as unavailable. It no longer relies on older absolute worktree paths.
The old archive builder is excluded because its broad `*.lock` filter dropped
`uv.lock`; release verification must use the committed Git tree.

Dependency audit reported 17 existing frontend production advisories (one
critical, four high, six moderate, six low). The critical/high package versions
are unchanged from this base. This PR does not claim to remediate the dependency
baseline or qualify production deployment. The frontend build also retains its
existing Turbopack file-tracing warning.
