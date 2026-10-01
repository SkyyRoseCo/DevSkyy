/**
 * Route-handler authentication gate for the DevSkyy dashboard API.
 *
 * Replaces the removed `proxy.ts` matcher-based gate. That gate was fail-closed
 * by construction — a new route under /api was gated the moment it existed,
 * because the matcher was an exclusion list. Per-handler auth inverts that: a
 * new route is OPEN until someone remembers to wrap it.
 *
 * Two things restore the fail-closed property:
 *   1. `withAuth()` — wrapping is structural, not a convention. An unwrapped
 *      export is visible in the source as a bare function.
 *   2. `tests/api-auth-coverage.test.ts` — enumerates every app/api route file
 *      and fails when a handler is neither wrapped nor on PUBLIC_API_ROUTES.
 *      Adding an ungated route breaks the build rather than shipping a hole.
 *
 * NextAuth v4 (4.24.x): the session is read with `getServerSession(authOptions)`.
 * The v5 `auth()` wrapper does not exist in this major — do not port it here
 * without also migrating lib/auth.ts.
 */

import { getServerSession, type Session } from 'next-auth';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

import { authOptions } from '@/lib/auth';

export { PUBLIC_API_ROUTES } from '@/lib/api-public-routes';

/** A Next.js App Router route handler, with its optional route-context arg. */
type RouteHandler<C> = (request: NextRequest, context: C) => Promise<Response> | Response;

/**
 * Wrap a route handler so unauthenticated callers get 401 JSON.
 *
 * JSON, never a redirect: every caller here is a `fetch` from an authenticated
 * /admin page, and a 302 to /login would be followed transparently, handing the
 * caller an HTML login page with a 200 status. That parses as success and
 * corrupts the client far more quietly than an error does.
 *
 * The generic `C` passes the route context through untouched so dynamic
 * segments (`catalog/[sku]`) keep their `params` typing at the call site.
 */
export function withAuth<C>(handler: RouteHandler<C>): RouteHandler<C> {
  return async (request: NextRequest, context: C) => {
    let session: Session | null;
    try {
      session = await getServerSession(authOptions);
    } catch {
      return NextResponse.json(
        { success: false, error: 'Authentication unavailable' },
        { status: 503, headers: { 'Cache-Control': 'private, no-store', Pragma: 'no-cache', Vary: 'Cookie' } }
      );
    }

    if (!session) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401, headers: { 'Cache-Control': 'private, no-store', Pragma: 'no-cache', Vary: 'Cookie' } }
      );
    }

    return handler(request, context);
  };
}
