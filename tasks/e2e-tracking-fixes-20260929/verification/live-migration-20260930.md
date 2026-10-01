# Live analytics migration — 2026-09-30

## Change applied

- Target: Neon project `devskyy` (`fancy-water-68795007`), primary/default
  production branch `br-tiny-brook-ahciwidn`, database `neondb`, PostgreSQL
  `17.11`.
- Revision: `sr_analytics_001` only.
- Applied at 2026-10-01 02:07 UTC (2026-09-30 7:07 PM America/Los_Angeles).
- The Neon migration workflow created a temporary branch, tested the DDL,
  applied it to the parent branch, and deleted the temporary branch.
- Owner authorized the production apply after reviewing the tested plan.

## Preflight and test evidence

Before applying, fresh catalog checks confirmed `public.users.id` was
`VARCHAR(36)` and the sole primary key, `public.analytics_events` was absent in
every schema, and `public.skyyrose_analytics_version` was absent. No user rows
were read.

The first Neon prepare request rejected the migration's dollar-quoted `DO`
precondition block (`unterminated dollar-quoted string`). The successful
prepared plan therefore contained the version table, analytics table, FK, eight
secondary indexes, and revision record, but omitted that procedural guard. The
omitted guard's conditions had been verified in the fresh production preflight;
the temporary branch was then tested before apply. This limitation is recorded
explicitly: the live DDL was applied through Neon’s prepared-migration path
rather than by running Alembic itself, so equivalence to the candidate
revision's procedural guard is based on the preflight and tested FK/schema
result.

Temporary-branch verification returned:

- revision `sr_analytics_001`
- 16 analytics columns
- 9 total indexes (primary-key index plus eight secondary indexes)
- 1 foreign key
- 0 events

## Production verification

Read-only metadata query after application confirmed:

- `public.skyyrose_analytics_version` records `sr_analytics_001`
- `public.analytics_events` has 16 columns and 9 indexes
- one foreign key exists; PostgreSQL delete-action code `n` confirms
  `ON DELETE SET NULL`
- event count is 0
- database `neondb`, server `17.11 (8a81ecb)`

No customer rows or event payloads were read. No application deployment, commit,
push, or other schema migration was performed. The production migration is
complete; real analytics ingestion and reporting still require separate
end-to-end validation.
