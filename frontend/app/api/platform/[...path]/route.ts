/** Dashboard HTTP boundary: browser cookies stay here; backend credentials stay server-side. */
import { NextResponse, type NextRequest } from 'next/server';

import { withAuth } from '@/lib/api-auth';
import { getBackendAccessToken } from '@/lib/backend-session';
import { buildBackendUrl } from '@/lib/backend-proxy';

type PlatformRouteContext = { params: Promise<{ path: string[] }> };
type StreamingRequestInit = RequestInit & { duplex?: 'half' };

export const maxDuration = 180;

const unavailable = (error: string, status: number) =>
  NextResponse.json({ success: false, error }, { status, headers: { 'Cache-Control': 'no-store' } });

async function relay(request: NextRequest, context: PlatformRouteContext): Promise<Response> {
  const { path } = await context.params;
  const upstreamUrl = buildBackendUrl(`/${path.join('/')}`, request.nextUrl.search, request.method);
  if (!upstreamUrl) return unavailable('Unsupported platform API path or method', 404);

  if (!['GET', 'HEAD'].includes(request.method) && request.headers.get('origin') !== request.nextUrl.origin) {
    return unavailable('A same-origin request is required', 403);
  }

  const accessToken = await getBackendAccessToken(request);
  if (!accessToken) return unavailable('Backend session unavailable. Sign in again.', 401);

  const headers = new Headers({ authorization: `Bearer ${accessToken}` });
  for (const name of ['accept', 'content-type', 'x-request-id', 'idempotency-key']) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  try {
    const options: StreamingRequestInit = {
      method: request.method,
      headers,
      cache: 'no-store',
      redirect: 'error',
      signal: AbortSignal.any([
        request.signal,
        AbortSignal.timeout(upstreamUrl.pathname === '/api/v1/context-dev/extractions' ? 180_000 : 120_000),
      ]),
    };
    // Stream uploads instead of buffering an unbounded body into function memory.
    if (request.body && !['GET', 'HEAD'].includes(request.method)) {
      options.body = request.body;
      options.duplex = 'half';
    }
    const upstream = await fetch(upstreamUrl, options);
    if (upstream.status >= 300 && upstream.status < 400) return unavailable('Backend redirect refused', 502);

    const responseHeaders = new Headers({ 'Cache-Control': 'no-store' });
    for (const name of ['content-type', 'content-disposition', 'retry-after']) {
      const value = upstream.headers.get(name);
      if (value) responseHeaders.set(name, value);
    }
    return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
  } catch {
    return unavailable('DevSkyy platform API is unavailable', 502);
  }
}

export const GET = withAuth(relay);
export const POST = withAuth(relay);
export const PUT = withAuth(relay);
export const PATCH = withAuth(relay);
export const DELETE = withAuth(relay);
