# DevSkyy dashboard: Vercel to Fly

Status: local migration candidate, not deployed. Production DNS still points to
Vercel. This migration is based on main commit `9917f0e6b`; unrelated changes in
the shared checkout are not part of this candidate.

## Architecture and cost boundary

Run the existing Next.js application in a standalone Node 22 container on a
separate Fly app, `devskyy-dashboard`, in `sjc`. Preserve the production origin
`https://www.devskyy.app` and serve `devskyy.app` as well. Keep the existing API
at `https://api.devskyy.app`.

Initial configuration: one shared CPU, 1 GB RAM, one warm Machine, one 1 GB
settings volume. Use `--ha=false` on the first deploy to avoid Fly creating a
second Machine. This is a low-cost single-instance deployment, not HA. Do not
add replicas while settings use a local volume. The earlier $6–15/month budget
was an estimate for dashboard compute, not a fixed quote or whole-stack cost;
confirm region rates, transfer, volume snapshots, and builder charges first.

## Local build and verification

Use a working Node 22 installation. From `frontend/`:

```sh
npm ci
npm run type-check
npm run lint
npm test
docker build --platform linux/amd64 --build-arg APP_REVISION="$(git rev-parse HEAD)" \
  -t devskyy-dashboard:migration .
docker run --rm --platform linux/amd64 --name devskyy-dashboard-verification \
  -p 127.0.0.1:3105:3000 \
  -e NEXTAUTH_URL=http://localhost:3105 \
  -e NEXTAUTH_SECRET=local-verification-only \
  devskyy-dashboard:migration
```

The Docker context MUST be `frontend/`, never the monorepo root. No environment
files, saved settings, or private keys enter the build context. Public URLs
are build arguments because Next embeds `NEXT_PUBLIC_*` variables in browser
bundles. Server secrets are supplied only at runtime.

For standalone verification without Docker, build with
`NEXT_OUTPUT_STANDALONE=1 npm run build`, copy `public` into
`.next/standalone/public` and `.next/static` into
`.next/standalone/.next/static`, then run its `server.js`. This is the same
asset layout as the Docker image. It does not verify Linux image execution.

Check `/healthz` and `/login` (200), actual CSS/JS and mascot image (200), and
unauthenticated `/api/catalog`, `/api/mcp`, `/api/settings`, and
`/api/monitoring/health` (401). `/healthz` is process liveness only; it must not
be represented as proof of database, MCP, WordPress, or provider health.
Verify signed-out admin navigation returns to login at desktop and 375px.

## Required runtime configuration

`fly.toml` contains only non-secret origins and service URLs. At minimum,
provide the existing `NEXTAUTH_SECRET` securely; changing it signs out users.
Login also requires the backend authentication endpoint to work.

Feature-dependent server secrets must be reconciled against the current
production configuration, not guessed from old notes:

- MCP: `MCP_SERVICE_TOKEN` matching the backend's authenticated MCP endpoint.
- WordPress client: `WP_BASE_URL`, `WP_APP_USER`, `WP_APP_PASSWORD`,
  `WC_CONSUMER_KEY`, `WC_CONSUMER_SECRET`.
- Existing legacy WordPress paths also consume `WORDPRESS_SITE_URL`,
  `WORDPRESS_URL`, `WORDPRESS_API_TOKEN`, `WOOCOMMERCE_KEY`,
  `WOOCOMMERCE_SECRET`, and `WP_WEBHOOK_SECRET`.
- Queue features: `REDIS_URL`, `WORDPRESS_SYNC_SERVICE_TOKEN`. A queue worker
  is a separate process; this web container does not launch one.
- Provider-specific features retain their existing server-side credentials.
  Migration verification must not invoke paid generation or live payments.

Use `flyctl secrets import` with a reviewed, untracked secret file on stdin,
not literal secrets in commands, logs, Docker build arguments, or Git. Do not
copy every key from the Notes archive. `VERCEL_TOKEN` is not required.

## Vercel dependency inventory

| Surface | Migration disposition |
| --- | --- |
| Next hosting and API routes | Standalone Node/Fly; existing auth wrappers retained |
| Security and CORS headers | Moved from `vercel.json` into `next.config.ts` |
| Analytics and Speed Insights | Layout scripts removed; SDK dependencies removed |
| Blob, KV, Edge Config, Functions, OG, Toolbar SDKs | No direct imports found; unused direct dependencies removed |
| Generic npm deploy commands | Now target Fly; no automatic deploy executed |
| Vercel CLI and explicitly named legacy Vercel scripts/admin integration | Retained for recovery/history; not needed by the Fly runtime; retire after cutover acceptance |
| GitHub CI Vercel deploy steps | Currently opt-in via `ENABLE_VERCEL_DEPLOY`; disable that variable before cutover and verify no other deployment automation remains |
| Cron | No `crons` block in checked-in `frontend/vercel.json`; production-only schedules still require account inspection |
| Env vars and custom domains | Production inventory/export and DNS cutover still required |

## Durable settings

`SETTINGS_FILE=/data/settings.json` separates mutable settings from bundled
read-only catalog projections. Fly mounts `dashboard_state` at `/data`.
Provision the volume in the same region as the one Machine. After the first
Machine exists, use an authenticated root SSH session to set `/data` owner to
UID/GID 1000, then verify the normal Node user can write there. New settings
files use mode 0600. If importing an existing file, explicitly set its owner
and mode 0600 as well. Saved settings may contain credentials; never include
them in screenshots or reports. Verify an authenticated settings save survives
a Machine replacement before accepting persistence. Volume snapshots do not
constitute a tested backup/restore procedure.

## Feature and backend release blockers

- `api.devskyy.app/health` reports the database unhealthy. The current backend
  health code performs a query against the users table, so this may be a
  connection, schema, permission, or query failure. Without authenticated Fly
  logs the cause is unknown. Do not reset the database or rotate secrets on
  speculation. Healthy login is a release gate.
- Catalog reads use the existing bundled CSV projection. The root registry
  symlink points to `wordpress-theme/skyyrose-flagship/data/logo-registry.json`,
  the sole editable product authority. Founder corrections are authoritative
  and recorded as `FOUNDER_CONFIRMED`; never re-author product facts here.
- Catalog PUT already fails closed with 503 when the Python registry writer
  and canonical filesystem are absent. This Node-only container intentionally
  does not invent a writable registry copy. A governed backend writer is
  needed before claiming hosted catalog editing works.
- Render review requires repository `renders/oai`; SOT imagery resolution
  requires root `data/sot-images.json`. These are not in this frontend-only
  image. They need a governed storage/backend connection before those
  dashboard features can be accepted. Do not upload arbitrary source assets
  or claim this migration has completed the whole product-management stack.
- Authenticated owner flows, streaming completion, settings persistence on
  Fly, provider wiring, and production-only Vercel resources are unverified.

## Release sequence (requires explicit production approval)

1. Resolve the backend database/login failure. Sign into Fly in the intended
   account and confirm app/organization ownership. No Fly CLI session was
   available during preparation.
2. Finish image verification and secret inventory. Commit/review the exact
   candidate. Confirm the remaining feature scope with the founder.
3. Create the new app/volume in the intended organization. Deploy from
   `frontend/` with `flyctl deploy --config fly.toml --ha=false
   --build-arg APP_REVISION=<reviewed-commit>`. Provision volume permissions.
4. Test the Fly hostname before DNS changes. For a signed-in rehearsal, use
   matching temporary auth/site origins and backend CORS configuration, then
   rebuild with canonical public origins for cutover. Do not weaken auth or
   use owner bypasses to obtain a green test.
5. Provision certificates for `www.devskyy.app` and `devskyy.app`; follow Fly's
   returned DNS records. Verify TLS and both hostnames. Preserve other DNS
   records, especially `api.devskyy.app` and mail.
6. Verify owner login, protected APIs, data loading, MCP handshake, completed
   streaming, desktop/mobile, and settings persistence. Recheck Vercel-free
   network behavior. Record the deployed image/revision and monthly sizing.
7. Only after acceptance, retire Vercel aliases, automation and optional
   integration/CLI; confirm no other project needs the account before
   cancelling anything. Never cancel first: keep a rollback route and record
   the previous DNS values and deployment ID.

No production deployment, DNS change, credential transfer, subscription change,
or provider charge was performed while preparing this candidate.

## Verification record — 2026-09-21

- Node 22.23.2 standalone production build: passed, Next.js 16.2.9.
- TypeScript: passed. ESLint: zero errors, 231 existing warnings.
- Frontend unit tests: 98 passed across 15 files, including auth coverage,
  hosting headers, and synthetic settings save/reload + mode checks.
- HTTP against the built standalone server on loopback port 3105: login,
  healthz, mascot image, and all 16 discovered login assets returned 200;
  unauthenticated catalog, settings, monitoring health and MCP returned 401.
- Browser: signed-out `/admin/hub` returned to `/login`; login rendered at
  desktop and 375x812, with document width equal to viewport width (375).
- Lockfile: removed 68 unused dependency entries; no retained package version
  changed. Product data projections were not modified.
- Fly configuration: parsed as TOML; authenticated `flyctl config validate`
  could not run because this shell has no Fly access token.
- Docker Desktop: restarted with explicit user approval after disk recovery;
  the previously read-only build store accepted a complete build.
- Linux image: `docker build --platform linux/amd64` passed. Local tag:
  `devskyy-dashboard:migration-20260921`; image ID:
  `sha256:23fe7ba84b40ef0882cb4a81d3e60049beb00aea51fc6f2c8a404957e4ee2168`.
  It runs as `node` (UID 1000). Revision label is
  `9917f0e6b-local-migration`, explicitly identifying an uncommitted candidate.
  Build log: `/tmp/devskyy-fly-docker-amd64-build.log`.
- Actual Linux container on loopback port 3106: login, healthz, auth session,
  mascot image, and all 16 discovered login CSS/JS assets returned 200.
  Unsigned catalog, settings, monitoring health, and POST MCP returned 401.
  Health response included no-store and the expected security headers.
  `.env`, `.env.local`, and saved `data/settings.json` were absent from `/app`.
- Local Docker volume: provisioned ownership to UID/GID 1000; the normal
  Node user wrote a synthetic test file with mode 0600. A replacement
  container read the same file successfully. This tests filesystem persistence,
  not authenticated settings writes or Fly volume provisioning. Temporary
  verification containers and volume were removed after testing.
- Production authentication, database repair, mounted-volume save/replacement,
  MCP calls, streaming, and the repository-backed feature gaps above remain
  unverified. Unit tests with synthetic sessions are not an authenticated
  production acceptance test.
