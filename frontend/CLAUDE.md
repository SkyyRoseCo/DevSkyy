# Frontend — devskyy-dashboard (Next.js 16 · React 19)

Scoped context for `frontend/`. Loads on top of the root CLAUDE.md. Commands +
"npm not pnpm" are in root. The gotchas below are the ones a fresh session gets
wrong.

## Auth — two systems, do not conflate

- **Admin (`/admin/*`): NextAuth v4.** `lib/auth.ts` + `SessionProvider`
  (`app/admin/layout.tsx`). Server-side: `getServerSession(authOptions)`.
  Client-side: `useSession()`. JWT, 15-min expiry.
- **Storefront/legacy:** `contexts/AuthContext.tsx` → `useAuth()`,
  `localStorage` key `access_token`. NOT used by any admin page.
  `lib/api/client.ts` also reads this key directly for backend calls. Calling
  `useAuth()` in an admin page gets undefined context.
- **API gate = `withAuth()` per route handler** (`lib/api-auth.ts`). Every
  handler under `app/api/` is exported as
  `export const GET = withAuth(getHandler);`. Unauthenticated → **401 JSON,
  never a redirect**: these are all `fetch` calls from `/admin` pages, and a 302
  to `/login` gets followed transparently, handing the caller an HTML login page
  with status 200 — which parses as success. Exemptions live in
  `lib/api-public-routes.ts` (`auth/[...nextauth]`, `checkout`,
  `webhooks/woocommerce`) and are **exact** route matches, so a future
  `checkout-status/` cannot inherit `checkout/`'s pass.
- **Adding an API route? It is gated or the build fails.**
  `tests/api-auth-coverage.test.ts` walks `app/api/**/route.ts` on disk and
  rejects any exported handler that is neither wrapped nor explicitly exempted.
  Per-handler auth is fail-OPEN by nature (a new route is unprotected until
  someone remembers) — that test is what restores the fail-closed property the
  old matcher had for free. Do not add a route to `PUBLIC_API_ROUTES` without
  writing the reason next to it.
- **No edge gate.** `frontend/proxy.ts` was removed 2026-07-28 (`ed8e79c89`,
  founder decision); `withAuth()` above is the only gate for `/api/*`. Don't
  reintroduce a `config.matcher` gate — wrap new routes instead. If edge/proxy
  logic is ever needed again: Next.js 16 deprecated `middleware.ts` in favor of
  `proxy.ts`, and having both files present is a hard error.

## Catalog data is SERVER-ONLY

`lib/catalog.ts` and `lib/catalog-server.ts` use `node:fs` (`catalog.ts:13`).
Importing either from a `'use client'` component **crashes the build**. Client
code must call the REST routes (`/api/catalog`, `/api/catalog/[sku]`). The CSV
resolver walks up 6 dirs from `process.cwd()` (`catalog.ts:48`) — confirm Vercel
`rootDirectory=frontend` keeps
`wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` in scope.

## State management — three layers, pick the right one

- Server/API data → **TanStack Query** (`@tanstack/react-query`, `useQuery`).
- Persistent cart → **Zustand** + `persist` (`lib/stores/cart-store.ts`).
- Admin auth → **NextAuth** `useSession()`.
- `jotai` is in package.json but unused in admin — don't introduce atoms without
  confirming the domain isn't already one of the above.

## API barrel — never bypass it

Always import from `@/lib/api` (re-exports via `lib/api.ts` →
`lib/api/index.ts`). To add an endpoint: (1) file in `lib/api/endpoints/`, (2)
Zod schema in `lib/api/schemas.ts`, (3) register in `lib/api/index.ts`. Direct
imports from `@/lib/api/endpoints/*` bypass the unified `api` object the pages
depend on.

## UI components

shadcn/ui **"new-york"** style, `rsc: true` (`components.json`). Install
primitives with `npx shadcn@latest add <name>` (don't copy default-style
examples). Icons: **`lucide-react` only**. Primitives land in `components/ui/`.

## E2E tests — canonical dir is `tests/e2e/`

`playwright.config.ts:4` sets `testDir: './tests/e2e'`. The legacy
`frontend/e2e/` dir is NOT executed — new specs go to `tests/e2e/`. Launch/smoke
the app with the `run-devskyy-dashboard` skill.

**Unit runner is vitest** — `npm test` → `vitest run`. `vitest.config.ts` uses
an explicit `include` (`lib/wp/**`, `tests/**`), NOT a default glob, because
most of the dashboard cannot be imported under vitest: `lib/wp/client.ts` sits
behind a `server-only` boundary the resolver can't satisfy, and anything
reaching `next-auth`/`next/server` drags the framework in. Keep new suites
framework-free, or they get skipped — and a skipped security test is
indistinguishable from a passing one. `tests/e2e/**` is excluded here; it
belongs to Playwright.

## next.config.ts — leave the Vercel guard alone

`outputFileTracingRoot` and `turbopack.root` are set ONLY when
`!process.env.VERCEL` (`next.config.ts:13`). Setting them unconditionally causes
a doubled-path crash on Vercel builds. Do not touch this conditional.
