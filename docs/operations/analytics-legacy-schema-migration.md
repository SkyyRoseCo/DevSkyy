# Storefront analytics migration for the existing DevSkyy schema

The observed DevSkyy Neon database was created outside the main Alembic history.
Its `public.users.id` is a `VARCHAR(36)` primary key, and existing application
tables refer to that key. The main Alembic baseline expects a new UUID `users`
table, so `alembic upgrade head` is not the migration path for this database.

The analytics store has a separate Alembic configuration and version table. Its
single revision creates `public.analytics_events`, keeps UUID event IDs, uses a
nullable `VARCHAR(36)` user foreign key with `ON DELETE SET NULL`, and adds the
eight indexes used by ingestion and reports. All table, index, foreign-key, ORM,
and version-history operations explicitly target `public` regardless of
`search_path`. SQLite execution uses `schema_translate_map={"public": None}`;
independently constructed local engines must specify that mapping too. The
migration does not modify existing tables, install extensions, convert user IDs,
or create synthetic activity.

The revision refuses to proceed unless `public.users.id` is the sole
`VARCHAR(36)` primary key and `analytics_events` is absent in all schemas.
Alembic records this revision in `public.skyyrose_analytics_version`, leaving
the unrelated historical Alembic state untouched. If the schema differs, stop
and prepare a separately reviewed migration for that schema profile.

The application and this migration share the database URL normalizer. A Postgres
URL containing `channel_binding=require` selects SQLAlchemy's async psycopg
dialect and preserves both `sslmode` and `channel_binding`; ordinary Postgres
URLs continue to use asyncpg. The psycopg route translates asyncpg `ssl=require`
to `sslmode=require`, preserves channel binding, and refuses conflicting TLS
values, repeated query options, and options outside the accepted libpq URL
contract instead of silently discarding them. Psycopg is declared as a direct
runtime dependency. See PostgreSQL 17
[connection parameters](https://www.postgresql.org/docs/17/libpq-connect.html#LIBPQ-PARAMKEYWORDS).

## Operator procedure

Set `DATABASE_URL` only in the local secret manager or deployment environment
for the exact intended database. Keep TLS and channel binding requirements
enabled. Never paste the URL into a command argument, checked-in file, or
terminal history.

First inspect the isolated migration plan without connecting:

```bash
alembic -c alembic-analytics.ini heads
alembic -c alembic-analytics.ini upgrade head --sql
```

Before any live migration, capture the target identity and schema inventory,
review the emitted DDL, and preserve a recovery point. A live schema migration
changes a real database and requires separate explicit authorization. Do not run
the main Alembic tree against this existing database or stamp its `001–003`
revisions to make the histories appear aligned.

## Applied production revision — 2026-09-30

Owner-approved revision `sr_analytics_001` has been applied to Neon project
`devskyy` (`fancy-water-68795007`), production branch `br-tiny-brook-ahciwidn`,
database `neondb` (PostgreSQL 17.11). A fresh read-only recheck confirmed the
revision record, 16 event columns, 9 indexes (primary-key index plus eight
secondary indexes), nullable `VARCHAR(36)` user foreign key with
`ON DELETE SET NULL`, and zero events. No customer rows or event payloads were
read. Do not repeat this migration. See
[`live-migration-20260930.md`](../../tasks/e2e-tracking-fixes-20260929/verification/live-migration-20260930.md)
for the dated evidence.

Neon's prepared-migration path rejected the revision's dollar-quoted `DO`
precondition, so the applied plan omitted that procedural guard. Its conditions
were checked against the live catalog before apply, and the tested temporary
branch plus post-apply metadata confirmed the resulting schema. The production
DDL was not executed by Alembic itself; do not describe the two paths as
byte-for-byte equivalent. Ingestion and reporting against production still need
separate end-to-end validation.

Before the live operation, the candidate was qualified against disposable
PostgreSQL 17 with synthetic data. Migration, empty rollback, rollback refusal
with a recorded event, concurrent-writer locking, lock timeout, schema
qualification, ingestion idempotency, and reporting checks passed. The API
Docker image was also built and its isolated migration/runtime path checked
against that disposable database. This evidence does not establish production
ingestion or reporting behavior.

## Empty-table rollback protection

The downgrade sets a transaction-local five-second lock timeout and acquires
`ACCESS EXCLUSIVE` on `public.analytics_events` before checking for recorded
events. Alembic holds this lock through the drops and version update in one
transaction. The isolated migration engine uses `READ COMMITTED` so the check
sees writers that completed while lock acquisition was waiting. A committed
event prevents rollback; a writer already holding a lock must finish before the
check, and a lock timeout aborts the downgrade. The rollback procedure still
requires ingestion to be paused and drained first: writes blocked behind a
successful table drop would fail once the transaction commits. The lock/commit
behavior was exercised on a disposable PostgreSQL 17 instance; live Neon
concurrency has not been exercised.

## Container packaging

The Docker context allowlist includes `alembic-analytics.ini` and the isolated
track's `__init__.py`, `env.py`, `script.py.mako`, and reviewed
`versions/001_create_storefront_analytics.py`. It descends through explicitly
allowed ancestor directories and excludes their siblings. The incompatible main
`alembic.ini`, environment, and revisions remain absent from the context. An
additional analytics revision must be reviewed and explicitly added to the
allowlist when it is introduced. Use the isolated configuration explicitly. This
allowlist change does not add automatic migration execution at build or startup.
The candidate Docker build and isolated runtime path were verified on disposable
PostgreSQL 17 as recorded above. This does not authorize automatic migrations at
build or startup.

The isolated source directory is `alembic/storefront_migrations/`. Its package
marker avoids colliding with the main Alembic `env` module and application/test
`analytics` modules during repository static analysis. The revision ID and
database version table are unchanged.
