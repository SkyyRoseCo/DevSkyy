import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';

vi.mock('server-only', () => ({}));
vi.mock('next-auth', () => ({ getServerSession: vi.fn() }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
import { getServerSession } from 'next-auth';
import { proxyGodModeRuntime } from './god-mode-runtime-proxy';

const session = vi.mocked(getServerSession);
const upstream = vi.fn();
function request(path = 'status', body?: string, origin = 'http://localhost:3000') {
  return new NextRequest(`http://localhost:3000/api/admin/god-mode/runtime/${path}`, {
    method: body === undefined ? 'GET' : 'POST',
    headers: { 'Content-Type': 'application/json', Origin: origin }, body,
  });
}
beforeEach(() => {
  vi.restoreAllMocks();
  vi.stubGlobal('fetch', upstream);
  upstream.mockReset();
  session.mockResolvedValue({ accessToken: 'local-fixture-token', expires: '' });
  vi.stubEnv('GOD_MODE_RUNTIME_URL', 'https://runtime.example.invalid');
});

describe('GOD MODE authenticated bounded proxy', () => {
  it('rejects missing backend authentication before any network request', async () => {
    session.mockResolvedValue(null);
    expect((await proxyGodModeRuntime(request(), ['status'])).status).toBe(401);
    expect(upstream).not.toHaveBeenCalled();
  });
  it('rejects cross-origin mutation and arbitrary routes', async () => {
    expect((await proxyGodModeRuntime(request('runs', '{}', 'https://attacker.invalid'), ['runs'])).status).toBe(403);
    expect((await proxyGodModeRuntime(request(), ['..', 'secrets'])).status).toBe(404);
    expect(upstream).not.toHaveBeenCalled();
  });
  it('requires an explicitly configured trusted backend', async () => {
    vi.stubEnv('GOD_MODE_RUNTIME_URL', 'http://public.example.invalid');
    expect((await proxyGodModeRuntime(request(), ['status'])).status).toBe(503);
    expect(upstream).not.toHaveBeenCalled();
  });
  it('limits streamed body size without trusting Content-Length', async () => {
    expect((await proxyGodModeRuntime(request('memory', JSON.stringify({ content: 'x'.repeat(17000) })), ['memory'])).status).toBe(413);
    expect(upstream).not.toHaveBeenCalled();
  });
  it('forwards only the session credential and fixed operation, with private response caching', async () => {
    upstream.mockResolvedValue(Response.json({ status: 'PENDING_APPROVAL' }, { status: 201 }));
    const response = await proxyGodModeRuntime(request('runs', '{"workflow":"source-audit"}'), ['runs']);
    expect(response.status).toBe(201);
    expect(response.headers.get('cache-control')).toBe('private, no-store');
    const [url, options] = upstream.mock.calls[0];
    expect(String(url)).toBe('https://runtime.example.invalid/api/v1/god-mode/runs');
    expect(options.headers.Authorization).toBe('Bearer local-fixture-token');
    expect(options.body).toBe('{"workflow":"source-audit"}');
    expect(options.redirect).toBe('error');
  });
  it('reports interrupted connection without silently retrying a mutation', async () => {
    upstream.mockRejectedValue(new Error('private host detail'));
    const response = await proxyGodModeRuntime(request('runs/r1/execute', '{"plan_hash":"test"}'), ['runs', 'r1', 'execute']);
    expect(response.status).toBe(502);
    const output = await response.text();
    expect(output).not.toContain('private host detail');
    expect(upstream).toHaveBeenCalledTimes(1);
  });
  it('uses the actual request Host when Next normalizes the internal URL', async () => {
    upstream.mockResolvedValue(Response.json({ status: 'PENDING_APPROVAL' }));
    const incoming = new NextRequest('http://localhost:3107/api/admin/god-mode/runtime/runs', {
      method: 'POST', headers: { Origin: 'http://127.0.0.1:3107', Host: '127.0.0.1:3107', 'Content-Type': 'application/json' }, body: '{}',
    });
    expect((await proxyGodModeRuntime(incoming, ['runs'])).status).toBe(200);
  });
});
