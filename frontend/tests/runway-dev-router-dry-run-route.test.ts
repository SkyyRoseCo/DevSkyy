import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';
import { getServerSession } from 'next-auth';

import { POST } from '../app/api/runway-dev/dry-run/route';

vi.mock('next-auth', () => ({
  getServerSession: vi.fn(),
}));

const CONFIG_ID = 'skyyrose-image-preflight';

function makeRequest(body: unknown) {
  return new NextRequest('http://localhost/api/runway-dev/dry-run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

describe('Runway Dev dry-run route', () => {
  const fetchMock = vi.fn<typeof fetch>();
  const getServerSessionMock = vi.mocked(getServerSession);

  beforeEach(() => {
    getServerSessionMock.mockReset();
    getServerSessionMock.mockResolvedValue({
      user: { email: 'dashboard-user@example.test' },
      expires: '2099-01-01T00:00:00.000Z',
    } as never);
    vi.stubEnv('RUNWAY_DEV_DRY_RUN_ENABLED', 'true');
    vi.stubEnv('RUNWAY_DEV_API_BASE_URL', 'https://api.dev.runwayml.com');
    vi.stubEnv('RUNWAY_ROUTER_CONFIG_ID', CONFIG_ID);
    vi.stubEnv('RUNWAYML_API_SECRET', 'test-only-secret');
    fetchMock.mockReset();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  it('keeps provider calls blocked until the live router snapshot is bound to server runtime', async () => {
    const response = await POST(makeRequest({ aspectRatio: '4:5' }), undefined);

    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({
      ok: false,
      error: 'ROUTER_CONFIGURATION_NOT_RUNTIME_BOUND',
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('rejects unauthenticated callers before provider or Governor handling', async () => {
    getServerSessionMock.mockResolvedValueOnce(null);

    const response = await POST(makeRequest({ aspectRatio: '4:5' }), undefined);

    expect(response.status).toBe(401);
    expect(await response.json()).toMatchObject({ error: 'Unauthorized' });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('fails closed without a provider call when disabled or misconfigured', async () => {
    vi.stubEnv('RUNWAY_DEV_DRY_RUN_ENABLED', 'false');

    const response = await POST(makeRequest({ aspectRatio: '4:5' }), undefined);

    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({
      error: 'RUNWAY_DEV_DRY_RUN_NOT_CONFIGURED',
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('fails closed when the server-side API secret is missing', async () => {
    vi.stubEnv('RUNWAYML_API_SECRET', '');

    const response = await POST(makeRequest({ aspectRatio: '4:5' }), undefined);

    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({
      error: 'RUNWAY_DEV_DRY_RUN_NOT_CONFIGURED',
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('rejects caller prompts and untrusted API hosts before a provider call', async () => {
    const invalidBodyResponse = await POST(
      makeRequest({ aspectRatio: '4:5', promptText: 'caller-supplied prompt' }),
      undefined,
    );
    expect(invalidBodyResponse.status).toBe(400);

    vi.stubEnv('RUNWAY_DEV_API_BASE_URL', 'https://example.test');
    const untrustedHostResponse = await POST(makeRequest({ aspectRatio: '4:5' }), undefined);
    expect(untrustedHostResponse.status).toBe(503);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('rejects an oversized body before shared rate-limit or provider work', async () => {
    const response = await POST(
      makeRequest({ extra: 'x'.repeat(1_100), aspectRatio: '4:5' }),
      undefined,
    );

    expect(response.status).toBe(413);
    expect(await response.json()).toMatchObject({ error: 'REQUEST_TOO_LARGE' });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
