import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';

// Behavioural companion to api-auth-coverage, which only reads the source
// text: this imports the real route and proves each exported method is gated
// before the proxy (and its backend bearer token) is ever reached.
const mocks = vi.hoisted(() => ({ session: vi.fn(), proxy: vi.fn() }));
vi.mock('next-auth', () => ({ getServerSession: mocks.session }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
vi.mock('@/lib/god-mode-runtime-proxy', () => ({ proxyGodModeRuntime: mocks.proxy }));

import { GET, POST } from '@/app/api/admin/god-mode/runtime/[[...path]]/route';

const HANDLERS = { GET, POST } as const;

function call(method: keyof typeof HANDLERS, path?: string[]) {
  const request = new NextRequest('http://localhost/api/admin/god-mode/runtime/runs', { method });
  return { request, response: HANDLERS[method](request, { params: Promise.resolve({ path }) }) };
}

beforeEach(() => {
  vi.resetAllMocks();
  mocks.proxy.mockResolvedValue(Response.json({ proxied: true }));
});

describe('/api/admin/god-mode/runtime/[[...path]]', () => {
  it.each(['GET', 'POST'] as const)('%s rejects a caller with no session and never reaches the proxy', async method => {
    mocks.session.mockResolvedValue(null);

    const response = await call(method, ['runs']).response;

    expect(response.status).toBe(401);
    expect(await response.json()).toEqual({ success: false, error: 'Unauthorized' });
    expect(mocks.proxy).not.toHaveBeenCalled();
  });

  it.each(['GET', 'POST'] as const)('%s hands a signed-in request to the proxy with its path', async method => {
    mocks.session.mockResolvedValue({ user: { email: 'synthetic-operator@example.test' } });

    const { request, response } = call(method, ['runs', 'synthetic-run', 'approve']);

    expect(await (await response).json()).toEqual({ proxied: true });
    expect(mocks.proxy).toHaveBeenCalledExactlyOnceWith(request, ['runs', 'synthetic-run', 'approve']);
  });

  it('defaults an absent catch-all segment to an empty path', async () => {
    mocks.session.mockResolvedValue({ user: { email: 'synthetic-operator@example.test' } });

    await call('GET').response;

    expect(mocks.proxy).toHaveBeenCalledExactlyOnceWith(expect.any(NextRequest), []);
  });
});
