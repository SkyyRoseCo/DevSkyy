import 'server-only';

import { getServerSession } from 'next-auth';
import { NextResponse, type NextRequest } from 'next/server';
import { authOptions } from '@/lib/auth';

const UUID = '[a-zA-Z0-9_-]{1,80}';
const READ_PATH = new RegExp(`^(?:status|workflows|runs|runs/${UUID}|memory)$`);
const WRITE_PATH = new RegExp(
  `^(?:runs|runs/${UUID}/(?:approve|execute|cancel|review|accept)|memory|memory/${UUID}/promote)$`
);
const MAX_BODY = 16_384;

/** A fixed backend adapter, not a general HTTP or shell proxy. */
export async function proxyGodModeRuntime(request: NextRequest, path: string[]): Promise<Response> {
  const session = await getServerSession(authOptions);
  const token = session && 'accessToken' in session ? session.accessToken : undefined;
  if (typeof token !== 'string' || !token) {
    return NextResponse.json({ error: 'A current backend sign-in is required.' }, { status: 401 });
  }
  const route = path.join('/');
  const method = request.method;
  if (!((method === 'GET' && READ_PATH.test(route)) || (method === 'POST' && WRITE_PATH.test(route)))) {
    return NextResponse.json({ error: 'Unsupported GOD MODE action.' }, { status: 404 });
  }
  if (method === 'POST') {
    const origin = request.headers.get('origin');
    // Next may normalize a loopback URL to localhost internally. The actual Host
    // header retains the browser's destination; do not trust forwarded-host input.
    let sameOrigin = false;
    try {
      const supplied = new URL(origin || '');
      const host = request.headers.get('host') || request.nextUrl.host;
      const configuredOrigin = process.env.NEXTAUTH_URL ? new URL(process.env.NEXTAUTH_URL) : null;
      const protocol = configuredOrigin?.host === host ? configuredOrigin.protocol : request.nextUrl.protocol;
      sameOrigin = supplied.origin === origin && supplied.host === host && supplied.protocol === protocol;
    } catch {
      /* Malformed or opaque origins are rejected. */
    }
    if (!sameOrigin) {
      return NextResponse.json({ error: 'Same-origin action required.' }, { status: 403 });
    }
    if (!request.headers.get('content-type')?.startsWith('application/json')) {
      return NextResponse.json({ error: 'JSON request required.' }, { status: 415 });
    }
  }
  const configured = process.env.GOD_MODE_RUNTIME_URL;
  if (!configured)
    return NextResponse.json(
      { error: 'GOD MODE execution host is not configured.', connected: false },
      { status: 503 }
    );
  let url: URL;
  try {
    const base = new URL(configured);
    if (base.username || base.password || base.search || base.hash || (base.pathname !== '/' && base.pathname !== ''))
      throw new Error('Invalid runtime origin.');
    const loopback = ['localhost', '127.0.0.1', '[::1]'].includes(base.hostname);
    if (base.protocol !== 'https:' && !(base.protocol === 'http:' && loopback && process.env.NODE_ENV !== 'production'))
      throw new Error('HTTPS execution host required.');
    url = new URL(`/api/v1/god-mode/${route}`, base);
    for (const [key, value] of request.nextUrl.searchParams) {
      if (!['query', 'project', 'limit'].includes(key) || value.length > 1000) throw new Error('Unsupported query.');
      url.searchParams.append(key, value);
    }
  } catch {
    return NextResponse.json({ error: 'GOD MODE execution host configuration is invalid.' }, { status: 503 });
  }
  let body: string | undefined;
  if (method === 'POST') {
    // Bound the stream before buffering; Content-Length alone is caller-controlled.
    const reader = request.body?.getReader();
    const decoder = new TextDecoder();
    let bytes = 0;
    body = '';
    if (reader) {
      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;
        bytes += chunk.value.byteLength;
        if (bytes > MAX_BODY) {
          await reader.cancel();
          return NextResponse.json({ error: 'Request is too large.' }, { status: 413 });
        }
        body += decoder.decode(chunk.value, { stream: true });
      }
      body += decoder.decode();
    }
    try {
      JSON.parse(body);
    } catch {
      return NextResponse.json({ error: 'Invalid JSON request.' }, { status: 400 });
    }
  }
  try {
    const response = await fetch(url, {
      method,
      body,
      cache: 'no-store',
      redirect: 'error',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', Accept: 'application/json' },
      signal: AbortSignal.timeout(route.endsWith('/execute') ? 240_000 : 15_000),
    });
    const data: unknown = await response.json();
    return NextResponse.json(data, { status: response.status, headers: { 'Cache-Control': 'private, no-store' } });
  } catch {
    return NextResponse.json(
      {
        error: 'The execution host did not return a result. Reconnect and inspect the existing run before retrying.',
        connected: false,
      },
      { status: 502, headers: { 'Cache-Control': 'private, no-store' } }
    );
  }
}
