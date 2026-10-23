import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';

const mocks = vi.hoisted(() => ({ session: vi.fn(), token: vi.fn(), fetch: vi.fn() }));
vi.mock('next-auth', () => ({ getServerSession: mocks.session }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
vi.mock('@/lib/backend-session', () => ({ getBackendAccessToken: mocks.token }));

import { GET, POST, DELETE } from '@/app/api/platform/[...path]/route';

const origin = 'https://dashboard.example.test';
const context = (path: string) => ({ params: Promise.resolve({ path: path.split('/') }) });
const request = (path: string, init?: ConstructorParameters<typeof NextRequest>[1]) =>
  new NextRequest(`${origin}/api/platform/${path}`, init);

beforeEach(() => {
  vi.stubEnv('BACKEND_API_URL', 'https://backend.example.test');
  mocks.session.mockReset().mockResolvedValue({ user: { email: 'operator@example.test' } });
  mocks.token.mockReset().mockResolvedValue('synthetic-server-bearer');
  mocks.fetch.mockReset().mockResolvedValue(Response.json({ success: true }));
  vi.stubGlobal('fetch', mocks.fetch);
});
afterEach(() => {
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

describe('authenticated platform relay', () => {
  it('requires a dashboard session before resolving backend credentials', async () => {
    mocks.session.mockResolvedValue(null);
    expect((await GET(request('health'), context('health'))).status).toBe(401);
    expect(mocks.token).not.toHaveBeenCalled();
    expect(mocks.fetch).not.toHaveBeenCalled();
  });

  it('fails closed when the server credential has expired or is absent', async () => {
    mocks.token.mockResolvedValue(null);
    const response = await GET(request('health'), context('health'));
    expect(response.status).toBe(401);
    expect(response.headers.get('cache-control')).toBe('no-store');
    expect(mocks.fetch).not.toHaveBeenCalled();
  });

  it.each([
    'api/v1/auth/token',
    'api/v1/webhooks/stripe',
    'api/v1/unknown',
    'api/v1/assets/../auth',
    'api/v1/assets/%2e%2e',
    'api/v1/assets/%252e%252e',
    'api/v1/assets/%2fsecret',
  ])('rejects unsupported path %s', async path => {
    expect((await GET(request('health'), context(path))).status).toBe(404);
    expect(mocks.fetch).not.toHaveBeenCalled();
  });

  it('relays only the server bearer and selected headers, retaining the query and upstream status', async () => {
    mocks.fetch.mockResolvedValue(
      Response.json(
        { operations: [] },
        {
          status: 202,
          headers: {
            'Set-Cookie': 'upstream-secret=value',
            'Cache-Control': 'public, max-age=3600',
            'X-Internal': 'private',
          },
        }
      )
    );
    const response = await GET(
      request('api/v1/tasks?limit=7', {
        headers: {
          Authorization: 'Bearer caller-value',
          Cookie: 'private-browser-cookie=value',
          'X-Request-ID': 'synthetic-id',
          'X-Forwarded-Host': 'attacker.example.test',
        },
      }),
      context('api/v1/tasks')
    );
    const [url, options] = mocks.fetch.mock.calls[0];
    expect(String(url)).toBe('https://backend.example.test/api/v1/tasks?limit=7');
    expect(options.headers.get('authorization')).toBe('Bearer synthetic-server-bearer');
    expect(options.headers.get('x-request-id')).toBe('synthetic-id');
    expect(options.headers.has('cookie')).toBe(false);
    expect(options.headers.has('x-forwarded-host')).toBe(false);
    expect(options).toMatchObject({ cache: 'no-store', redirect: 'error' });
    expect(options.signal).toBeInstanceOf(AbortSignal);
    expect(response.status).toBe(202);
    expect(response.headers.get('cache-control')).toBe('no-store');
    expect(response.headers.has('set-cookie')).toBe(false);
    expect(response.headers.has('x-internal')).toBe(false);
    expect(await response.json()).toEqual({ operations: [] });
  });

  it.each([undefined, 'https://attacker.example.test', 'null'])(
    'rejects cookie-authenticated mutation from origin %s',
    async originHeader => {
      const headers: Record<string, string> = {};
      if (originHeader) headers.Origin = originHeader;
      expect(
        (
          await DELETE(
            request('api/v1/assets/asset-1', { method: 'DELETE', headers }),
            context('api/v1/assets/asset-1')
          )
        ).status
      ).toBe(403);
      expect(mocks.fetch).not.toHaveBeenCalled();
    }
  );

  it('streams multipart uploads and preserves idempotency without synthesizing a JSON content type', async () => {
    const body = new FormData();
    body.append('file', new Blob(['synthetic-upload']), 'sample.txt');
    const req = request('api/v1/assets/upload', {
      method: 'POST',
      body,
      headers: { Origin: origin, 'Idempotency-Key': 'synthetic-operation' },
    });
    expect((await POST(req, context('api/v1/assets/upload'))).status).toBe(200);
    const [, options] = mocks.fetch.mock.calls[0];
    expect(options.headers.get('content-type')).toContain('multipart/form-data; boundary=');
    expect(options.headers.get('idempotency-key')).toBe('synthetic-operation');
    expect(options.duplex).toBe('half');
    expect(await new Response(options.body).text()).toContain('synthetic-upload');
  });

  it('does not permit POST on a read-only route', async () => {
    expect(
      (await POST(request('health', { method: 'POST', headers: { Origin: origin } }), context('health'))).status
    ).toBe(404);
    expect(mocks.fetch).not.toHaveBeenCalled();
  });

  it('preserves the existing three-minute extraction deadline', async () => {
    const timeout = vi.spyOn(AbortSignal, 'timeout');
    try {
      expect(
        (
          await POST(
            request('api/v1/context-dev/extractions', {
              method: 'POST',
              headers: { Origin: origin },
              body: '{}',
            }),
            context('api/v1/context-dev/extractions')
          )
        ).status
      ).toBe(200);
      expect(timeout).toHaveBeenCalledWith(180_000);
    } finally {
      timeout.mockRestore();
    }
  });

  it('refuses upstream redirects and does not expose the redirect target', async () => {
    mocks.fetch.mockResolvedValue(
      new Response(null, { status: 302, headers: { Location: 'https://attacker.example.test' } })
    );
    const response = await GET(request('health'), context('health'));
    expect(response.status).toBe(502);
    expect(response.headers.has('location')).toBe(false);
    expect(await response.text()).not.toContain('attacker');
  });

  it('returns a generic no-store error for an upstream failure', async () => {
    mocks.fetch.mockRejectedValue(new Error('synthetic-server-bearer'));
    const response = await GET(request('health'), context('health'));
    expect(response.status).toBe(502);
    expect(response.headers.get('cache-control')).toBe('no-store');
    expect(await response.text()).not.toContain('synthetic-server-bearer');
  });
  it.each([
    ['providers', 'GET'],
    ['runs/550e8400-e29b-41d4-a716-446655440000', 'GET'],
    ['runs/550e8400-e29b-41d4-a716-446655440000/cancel', 'POST'],
  ])('relays God Mode %s using only the server credential', async (suffix, method) => {
    const path = `api/v1/orchestration/god-mode/${suffix}`;
    const handler = method === 'GET' ? GET : POST;
    const response = await handler(request(path, {method, headers: {Origin: origin}}), context(path));
    expect(response.status).toBe(200);
    expect(String(mocks.fetch.mock.calls[0][0])).toBe(`https://backend.example.test/${path}`);
    expect(mocks.fetch.mock.calls[0][1].headers.get('authorization')).toBe('Bearer synthetic-server-bearer');
    expect(await response.text()).not.toContain('synthetic-server-bearer');
  });

  it('retains God Mode request bytes and idempotency across upstream uncertainty and replay', async () => {
    const path = 'api/v1/orchestration/god-mode/runs';
    const body = JSON.stringify({mission: {objective: 'A concrete fixture mission'}, authorize_paid: true});
    for (const status of [503, 202]) {
      mocks.fetch.mockResolvedValue(Response.json({id: 'run-one'}, {status}));
      const response = await POST(request(path, {
        method: 'POST', body,
        headers: {Origin: origin, 'Content-Type': 'application/json', 'Idempotency-Key': 'same-mission-key'},
      }), context(path));
      expect(response.status).toBe(status);
      const options = mocks.fetch.mock.calls.at(-1)![1];
      expect(options.headers.get('idempotency-key')).toBe('same-mission-key');
      expect(await new Response(options.body).text()).toBe(body);
    }
    expect(mocks.fetch).toHaveBeenCalledTimes(2);
  });

});
