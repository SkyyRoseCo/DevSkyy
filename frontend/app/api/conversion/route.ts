/** Authenticated read proxy. Event writes belong to the signed WordPress bridge. */
import { getServerSession } from 'next-auth';
import { NextRequest, NextResponse } from 'next/server';

import { withAuth } from '@/lib/api-auth';
import { authOptions } from '@/lib/auth';
import { analyticsSummarySchema, getAnalyticsProxyConfig, parseAnalyticsDays } from '@/lib/analytics-client';

async function getHandler(request: NextRequest) {
  const config = getAnalyticsProxyConfig();
  const days = parseAnalyticsDays(request.nextUrl.searchParams.get('days'));
  const unavailable = (error: string, status: number) =>
    NextResponse.json(
      {
        success: false,
        summary: null,
        error,
        context: { site_id: config?.siteId ?? null, environment: config?.environment ?? null, days },
        coverage: 'unavailable',
        evidence: 'No backend summary was verified for this request.',
      },
      { status, headers: { 'Cache-Control': 'no-store' } }
    );

  if (days === null) return unavailable('days must be an integer from 1 to 90.', 400);
  if (!config) return unavailable('Analytics site and environment are not configured.', 503);
  const session = await getServerSession(authOptions);
  const accessToken = (session as { accessToken?: unknown } | null)?.accessToken;
  if (typeof accessToken !== 'string' || !accessToken)
    return unavailable('Backend access token is unavailable. Sign in again.', 401);

  try {
    const url = new URL('/api/v1/analytics/events/summary', config.apiBase);
    url.search = new URLSearchParams({
      site_id: config.siteId,
      environment: config.environment,
      days: String(days),
    }).toString();
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${accessToken}`, Accept: 'application/json' },
      cache: 'no-store',
      signal: AbortSignal.timeout(10_000),
    });
    if (!response.ok) {
      return unavailable(
        'Backend analytics summary is unavailable.',
        [401, 403, 503].includes(response.status) ? response.status : 502
      );
    }
    const parsed = analyticsSummarySchema.safeParse(await response.json());
    if (
      !parsed.success ||
      parsed.data.site_id !== config.siteId ||
      parsed.data.environment !== config.environment ||
      parsed.data.window.days !== days
    ) {
      return unavailable('Backend analytics response did not match the requested scope.', 502);
    }
    return NextResponse.json({ success: true, summary: parsed.data }, { headers: { 'Cache-Control': 'no-store' } });
  } catch {
    return unavailable('Backend analytics summary could not be verified.', 502);
  }
}

async function postHandler() {
  return NextResponse.json(
    {
      success: false,
      error:
        'Browser event ingestion is disabled. Use the authenticated WordPress bridge; paid orders require verified WooCommerce evidence.',
    },
    { status: 405, headers: { Allow: 'GET' } }
  );
}

export const GET = withAuth(getHandler);
export const POST = withAuth(postHandler);
