import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';

const { sessionMock } = vi.hoisted(() => ({ sessionMock: vi.fn() }));
vi.mock('next-auth', () => ({ getServerSession: sessionMock }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
vi.mock('@/lib/api/config', () => ({ API_URL: 'https://backend.example.test' }));

import { GET, POST } from '@/app/api/conversion/route';
import {
  fetchAnalyticsSummary,
  formatAnalyticsMetric,
  formatAnalyticsRevenue,
  parseAnalyticsDays,
  type AnalyticsSummary,
} from '@/lib/analytics-client';
import ConversionIntelligencePage from '@/app/admin/conversion/page';
import JourneyAnalyticsPage from '@/app/admin/journey-analytics/page';
import { ConversionPulse } from '@/components/dashboard/conversion-pulse';

function summary(): AnalyticsSummary {
  return {
    site_id: 'store-test',
    environment: 'test',
    window: { start: '2026-08-30T00:00:00+00:00', end: '2026-09-29T00:00:00+00:00', days: 30 },
    coverage: {
      status: 'partial',
      telemetry: 'observed',
      commerce: 'observed',
      consent: 'accepted_only',
      synthetic_events_excluded: 4,
      missing: ['attribution'],
    },
    metrics: {
      event_count: 3,
      page_views: 3,
      sessions: 1,
      product_views: null,
      product_clicks: null,
      add_to_cart: null,
      checkout_started: null,
      consented_purchases: null,
      conversion_rate: null,
      verified_purchases: 0,
      verified_revenue: 0,
      currency: 'USD',
      spend: null,
      roas: null,
    },
    event_counts: { page_view: 3 },
    revenue_by_currency: { USD: 0 },
    provenance: {
      telemetry: 'hmac_authenticated_wordpress_bridge',
      commerce: 'signature_verified_woocommerce_paid_order',
      attribution: 'unavailable',
      revenue_basis: 'paid_order_gross_not_refund_adjusted',
    },
  };
}

const fetchMock = vi.fn<typeof fetch>();
beforeEach(() => {
  vi.unstubAllEnvs();
  vi.stubEnv('SKYYROSE_ANALYTICS_SITE_ID', 'store-test');
  vi.stubEnv('SKYYROSE_ANALYTICS_ENVIRONMENT', 'test');
  vi.stubGlobal('fetch', fetchMock);
  fetchMock.mockReset();
  sessionMock.mockReset().mockResolvedValue({ user: { email: 'operator@example.test' }, accessToken: 'fixture-jwt' });
});

const request = (query = '') => new NextRequest(`http://localhost/api/conversion${query}`);

describe('conversion summary authentication and scope', () => {
  it('requires an authenticated dashboard session', async () => {
    sessionMock.mockResolvedValue(null);
    const response = await GET(request(), undefined);
    expect(response.status).toBe(401);
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it('requires a backend token even if a session exists', async () => {
    sessionMock.mockResolvedValue({ user: { email: 'operator@example.test' } });
    expect((await GET(request(), undefined)).status).toBe(401);
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it('fails closed on absent site or environment configuration', async () => {
    vi.stubEnv('SKYYROSE_ANALYTICS_SITE_ID', '');
    const response = await GET(request(), undefined);
    expect(response.status).toBe(503);
    expect((await response.json()).summary).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it('proxies only its configured scope with the backend session token', async () => {
    const data = summary();
    fetchMock.mockResolvedValue(Response.json(data));
    const response = await GET(request('?site_id=attacker&environment=production'), undefined);
    expect(response.status).toBe(200);
    const [url, init] = fetchMock.mock.calls[0];
    expect(String(url)).toBe(
      'https://backend.example.test/api/v1/analytics/events/summary?site_id=store-test&environment=test&days=30'
    );
    expect(init?.headers).toEqual({ Authorization: 'Bearer fixture-jwt', Accept: 'application/json' });
    expect(init?.cache).toBe('no-store');
    expect(response.headers.get('cache-control')).toBe('no-store');
    expect(await response.json()).toEqual({ success: true, summary: data });
  });
  it.each(['0', '91', '1.5', '-1', 'NaN'])('rejects unsupported days=%s before querying', async days => {
    expect((await GET(request(`?days=${days}`), undefined)).status).toBe(400);
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it.each(['site', 'environment', 'days', 'metrics', 'provenance'])(
    'rejects an unverified backend response (%s)',
    async mismatch => {
      const data = summary();
      if (mismatch === 'site') data.site_id = 'other-store';
      if (mismatch === 'environment') data.environment = 'production';
      if (mismatch === 'days') data.window.days = 7;
      const payload =
        mismatch === 'metrics'
          ? { site_id: 'store-test' }
          : mismatch === 'provenance'
            ? { ...data, provenance: { ...data.provenance, commerce: 'browser_purchase_claim' } }
            : data;
      fetchMock.mockResolvedValue(Response.json(payload));
      const response = await GET(request(), undefined);
      expect(response.status).toBe(502);
      expect((await response.json()).summary).toBeNull();
    }
  );
  it('keeps backend authorization failure unavailable rather than returning zeroes', async () => {
    fetchMock.mockResolvedValue(Response.json({ error: 'denied' }, { status: 403 }));
    const response = await GET(request(), undefined);
    expect(response.status).toBe(403);
    expect((await response.json()).summary).toBeNull();
  });
  it('rejects authenticated browser purchase batches without any write or query', async () => {
    const response = await POST(
      new NextRequest('http://localhost/api/conversion', {
        method: 'POST',
        body: JSON.stringify({ events: [{ event: 'pre_order_completed', data: { revenue: 50000 } }] }),
      }),
      undefined
    );
    expect(response.status).toBe(405);
    expect(response.headers.get('allow')).toBe('GET');
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe('analytics client unavailable and observed states', () => {
  it('preserves measured zeroes and nullable stages', async () => {
    fetchMock.mockResolvedValue(Response.json({ success: true, summary: summary() }));
    const result = await fetchAnalyticsSummary();
    expect(result.summary?.metrics.verified_purchases).toBe(0);
    expect(result.summary?.metrics.product_views).toBeNull();
    expect(formatAnalyticsMetric(0)).toBe('0');
    expect(formatAnalyticsMetric(null)).toBe('Unavailable');
    expect(formatAnalyticsRevenue(result.summary)).toBe('$0.00');
  });
  it('discards previous measurements after a failed refresh', async () => {
    fetchMock
      .mockResolvedValueOnce(Response.json({ success: true, summary: summary() }))
      .mockRejectedValueOnce(new Error('offline'));
    expect((await fetchAnalyticsSummary()).summary).not.toBeNull();
    expect((await fetchAnalyticsSummary()).summary).toBeNull();
  });
  it('does not accept the legacy in-memory response shape', async () => {
    fetchMock.mockResolvedValue(Response.json({ success: true, metrics: { total_events: 12000 } }));
    expect((await fetchAnalyticsSummary()).summary).toBeNull();
  });
  it('uses explicit default and bounded windows', () => {
    expect(parseAnalyticsDays(null)).toBe(30);
    expect(parseAnalyticsDays('1')).toBe(1);
    expect(parseAnalyticsDays('90')).toBe(90);
    expect(parseAnalyticsDays('')).toBeNull();
  });
});

describe('initial dashboard rendering', () => {
  it.each([ConversionIntelligencePage, JourneyAnalyticsPage, ConversionPulse])(
    'shows unavailable measurements before a verified summary arrives',
    Component => {
      const html = renderToStaticMarkup(createElement(Component));
      expect(html).toContain('Unavailable');
      expect(html).toContain('No backend summary verified.');
      expect(html).not.toContain('Baseline Data');
      expect(html).not.toContain('LIVE');
      expect(html).not.toContain('12,847');
    }
  );
  it('retains all four collection identities without inventing collection counts', () => {
    const html = renderToStaticMarkup(createElement(JourneyAnalyticsPage));
    for (const collection of ['Black Rose', 'Love Hurts', 'Signature', 'Kids Capsule'])
      expect(html).toContain(collection);
    expect(html).toContain('Collection journey measurements: unavailable.');
  });
});
