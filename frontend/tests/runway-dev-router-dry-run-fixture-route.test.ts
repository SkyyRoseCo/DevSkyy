import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';

const fixture = vi.hoisted(() => ({
  getServerSession: vi.fn(),
  authorizeGovernor: vi.fn(),
  getRouterGate: vi.fn(),
  consumeRateLimit: vi.fn(),
  fetch: vi.fn<typeof fetch>(),
}));

vi.mock('next-auth', () => ({ getServerSession: fixture.getServerSession }));
vi.mock('../app/api/runway-dev/dry-run/governor', () => ({
  authorizeRunwayDryRunQuotaOperation: fixture.authorizeGovernor,
}));
vi.mock('../app/api/runway-dev/dry-run/qualification-gate', () => ({
  getRunwayRouterConfigurationGate: fixture.getRouterGate,
}));
vi.mock('../app/api/runway-dev/dry-run/rate-limit', () => ({
  consumeRunwayDryRunRateLimit: fixture.consumeRateLimit,
  RUNWAY_DRY_RUN_RATE_LIMIT_WINDOW_SECONDS: 60,
}));

import { POST } from '../app/api/runway-dev/dry-run/route';
import {
  RUNWAY_IMAGE_MODEL,
  RUNWAY_MAX_IMAGE_CREDITS,
} from '../app/api/runway-dev/dry-run/contract';

const CONFIG_ID = 'fixture-approved-router';
const API_SECRET = 'fixture-only-secret';

function makeRequest(body: unknown) {
  return new NextRequest('http://localhost/api/runway-dev/dry-run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

function makeProviderResponse(overrides: Record<string, unknown> = {}) {
  return {
    dryRun: true,
    routing: {
      model: RUNWAY_IMAGE_MODEL,
      configId: CONFIG_ID,
      resolvedSettings: { optimizeFor: 'quality', priceCeiling: RUNWAY_MAX_IMAGE_CREDITS },
      resolvedInput: { ratio: '4:5', aspectRatio: '4:5', resolution: '2k' },
      estimatedCost: { credits: 16 },
    },
    ...overrides,
  };
}

describe('Runway Dev dry-run route path with local fixtures', () => {
  beforeEach(() => {
    fixture.getServerSession.mockReset();
    fixture.getServerSession.mockResolvedValue({
      user: { email: 'fixture-user@example.test' },
      expires: '2099-01-01T00:00:00.000Z',
    });
    fixture.authorizeGovernor.mockReset();
    fixture.authorizeGovernor.mockReturnValue({ authorized: true });
    fixture.getRouterGate.mockReset();
    fixture.getRouterGate.mockReturnValue({ ready: true });
    fixture.consumeRateLimit.mockReset();
    fixture.consumeRateLimit.mockResolvedValue('allowed');
    fixture.fetch.mockReset();
    vi.stubGlobal('fetch', fixture.fetch);
    vi.stubEnv('RUNWAY_DEV_DRY_RUN_ENABLED', 'true');
    vi.stubEnv('RUNWAY_DEV_API_BASE_URL', 'https://api.dev.runwayml.com');
    vi.stubEnv('RUNWAY_ROUTER_CONFIG_ID', CONFIG_ID);
    vi.stubEnv('RUNWAYML_API_SECRET', API_SECRET);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  it('sends only the fixed synthetic dry-run request and separates estimate from exposure', async () => {
    fixture.fetch.mockResolvedValueOnce(
      new Response(JSON.stringify(makeProviderResponse()), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    const response = await POST(makeRequest({ aspectRatio: '4:5' }), undefined);
    const result = await response.json();
    const [url, init] = fixture.fetch.mock.calls[0];
    const sentBody = JSON.parse(String(init?.body));

    expect(response.status).toBe(200);
    expect(result).toMatchObject({
      ok: true,
      dryRun: true,
      taskCreated: false,
      decision: {
        model: RUNWAY_IMAGE_MODEL,
        configId: CONFIG_ID,
        pricing: {
          estimatedCostCredits: 16,
          routerCeilingCredits: RUNWAY_MAX_IMAGE_CREDITS,
          providerBoundMaximumCredits: null,
          reservationBoundCredits: 0,
        },
      },
    });
    expect(String(url)).toBe('https://api.dev.runwayml.com/v1/generate/image');
    expect(init?.method).toBe('POST');
    expect(init?.cache).toBe('no-store');
    expect(init?.headers).toMatchObject({
      Authorization: `Bearer ${API_SECRET}`,
      'X-Runway-Version': '2024-11-06',
    });
    expect(sentBody).toMatchObject({ configId: CONFIG_ID, dryRun: true });
    expect(sentBody.input).toMatchObject({
      aspectRatio: '4:5',
      resolution: '2k',
      outputCount: 1,
    });
    expect(sentBody.input.referenceImages).toBeUndefined();
    expect(fixture.fetch).toHaveBeenCalledTimes(1);
    expect(fixture.consumeRateLimit).toHaveBeenCalledWith('fixture-user@example.test');
  });

  it('stops before Runway when the shared limiter denies or cannot establish state', async () => {
    fixture.consumeRateLimit.mockResolvedValueOnce('limited');
    const limited = await POST(makeRequest({ aspectRatio: '4:5' }), undefined);
    expect(limited.status).toBe(429);
    expect(limited.headers.get('Retry-After')).toBe('60');
    expect(fixture.authorizeGovernor).not.toHaveBeenCalled();

    fixture.consumeRateLimit.mockResolvedValueOnce('unavailable');
    const unavailable = await POST(makeRequest({ aspectRatio: '4:5' }), undefined);
    expect(unavailable.status).toBe(503);
    expect(await unavailable.json()).toMatchObject({
      error: 'RUNWAY_DRY_RUN_RATE_LIMIT_UNAVAILABLE',
    });
    expect(fixture.fetch).not.toHaveBeenCalled();
  });

  it('rejects oversized requests before rate-limit, Governor, or provider work', async () => {
    const response = await POST(
      makeRequest({ extra: 'x'.repeat(1_100), aspectRatio: '4:5' }),
      undefined,
    );

    expect(response.status).toBe(413);
    expect(fixture.consumeRateLimit).not.toHaveBeenCalled();
    expect(fixture.authorizeGovernor).not.toHaveBeenCalled();
    expect(fixture.fetch).not.toHaveBeenCalled();
  });

  it('does not retry an unavailable provider request or expose provider details', async () => {
    fixture.fetch.mockRejectedValueOnce(new Error('provider details must stay private'));

    const response = await POST(makeRequest({ aspectRatio: '4:5' }), undefined);
    const responseText = await response.text();

    expect(response.status).toBe(502);
    expect(responseText).toContain('RUNWAY_DEV_PREFLIGHT_UNAVAILABLE');
    expect(responseText).not.toContain('provider details must stay private');
    expect(responseText).not.toContain(API_SECRET);
    expect(fixture.fetch).toHaveBeenCalledTimes(1);
  });
});
