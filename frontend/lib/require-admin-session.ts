/**
 * Server-side session read for /admin/* Server Component pages.
 *
 * The removed proxy.ts matcher gated both /api/* and /admin/* page requests.
 * withAuth() (lib/api-auth.ts) replaced it for API routes only — Server
 * Component pages under /admin that fetch data directly (not through a
 * gated API route) have no equivalent gate.
 *
 * Deliberately does NOT call redirect(): a redirect() thrown from here,
 * after connection() establishes the dynamic boundary, is silently
 * swallowed under this app's Cache Components configuration — confirmed by
 * direct testing (curl + a live browser both stayed on the requested page
 * with the redirect() call verifiably having fired, log-diagnosed via a
 * console.error immediately before the call). ConsoleShell's client-side
 * useSession() check (components/console/ConsoleShell.tsx) owns the actual
 * navigation to /login instead — the same reason app/admin/layout.tsx's
 * own comment gives for handling identity data client-side rather than in
 * an async layout.
 *
 * What this DOES guarantee: callers that gate their data fetch on a null
 * session here never put real backend data (WooCommerce orders, customers,
 * products) into the rendered HTML for an unauthenticated request — that's
 * the actual security property, independent of whether the redirect UX
 * fires immediately or a beat later on the client.
 */
import { getServerSession } from 'next-auth';
import type { Session } from 'next-auth';

import { authOptions } from '@/lib/auth';

export async function getAdminSession(): Promise<Session | null> {
  const session = await getServerSession(authOptions);
  return session?.authError ? null : session;
}
