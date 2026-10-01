# Bounded login deadline correction

Frozen source: `3c93bf0814a9cf1c6295fe3a2c6004cdf4399a39`.
Local parent: `56cba33a6480680d2c8b37bbe81103899c3ac2d0`.
Export base: `c4d971022aee75b6ea58b13b44cdc9d91aeb81e9`.
Patch: `login-deadline.patch`, SHA256 `85dae7374a299461a20a0f605c6274bd3a939f141ba7c42634eb441aadb61e83`.
`git apply --check` passes in an isolated fixture of exact export-base blobs.
Source-map.json binds all three before/after file hashes. This patch is limited
to login/page.tsx, lib/auth.ts and the regression tests; identity/session
callbacks, shared manifests, Governor behavior and historical evidence remain
unchanged. Integration owns assembly and release.

A successful legacy login previously cleared its30-second timer before awaiting
NextAuth. If that call stalled, the form remained disabled. One client deadline
now covers fetch, body parsing and signIn, aborts legacy transport on expiry,
uses a fixed redacted timeout message and clears the timer in finally. The form
can retry. Application token writes and navigation occur only after the raced
session operation succeeds. Late losing results do not resume that continuation.

Server CredentialsProvider authorize now applies one10-second deadline to the
upstream token fetch and body parsing, supplies an AbortSignal, returns null on
timeout/failure and clears its timer on every exit. Successful identity/token
fields and session callbacks remain unchanged. No upstream error or credential
text is exposed by the timeout response.

**Scope limit:** Promise.race does not cancel NextAuth's internal signIn HTTP
request, Set-Cookie processing or session broadcast. This correction qualifies
bounded application waiting and app-side legacy-token/navigation behavior.
It does not establish cookie ordering between different-account retries,
session revocation or deployed owner identity.

## Observed verification

Using integration's installed Next16.3.8, Vitest5.0.2 and jsdom30.0.1 through a
read-only temporary local node_modules symlink:

- Full frontend suite:346 tests pass, including9 new deadline regressions.
- Type check passes; lint passes with0 errors and228 existing warnings.
- Webpack production build passes.
- Security and TypeScript reviewers independently approve the bounded source.
- Astra independently verified frozen source and patch/base hashes and reviewed
  the346-test/type/lint/build logs. Source/unit evidence closure is PASS. Its
  browser late-completion evidence finding was corrected by narrowing the claim.
- Actual NextAuth SDK browser check passes against loopback synthetic identity:
  legacy token succeeds, first SDK callback stalls, timeout message appears,
  retry becomes enabled, no legacy token is stored and navigation stays/login.
  A second real SDK callback and server authorize succeed, navigate/admin and
  store the expected synthetic token. The first callback is then released;
  the browser helper does not deterministically qualify its late SDK completion
  or postcompletion navigation. Deterministic unit tests cover application-side
  late-result continuation isolation. Cookie ordering is NOT_QUALIFIED. The375px
  timeout screenshot was visually inspected.

The initial browser fixture failed its observation gate before the callback
handler updated its counter. That negative result is preserved separately.
The corrected fixture waits for a latch resolved inside the actual route
interceptor; source was unchanged. Unit tests also exposed a DOMException/Error
realm mismatch in the initial timeout construction; source now creates Error
with name AbortError. Test-only clock/reset and timer assertions were corrected
to preserve module rate-limiter state and distinguish Radix timers from the
application's deadline. No passing result was inferred from the failed attempts.

Dependency package hashes and integration lock identity are in dependencies.json.
This is local macOS synthetic evidence, not locked Linux, production, private
bridge or real-account qualification. Browser fixture credentials and backend
are synthetic; there is no authenticated external account or permitted production
mutation. No provider request, deployment, migration replay or publication occurred.

## Reproduction

From frontend with the intended installed dependency tree:

```sh
npm test -- --run tests/login-deadlines.test.ts
npm test
npm run type-check
npm run lint
NEXT_PUBLIC_API_URL=http://127.0.0.1:18080 NODE_OPTIONS=--no-experimental-strip-types npm run build -- --webpack
```

For the optional browser-check.cjs, use the synthetic-only local backend and Next
startup recipe in tasks/governor-analytics-20261001/README.md. The helper blocks
external browser requests and deliberately stalls only its first local NextAuth
callback. It does not create or provision a real account.
