import { expect, test } from '@playwright/test';
import type { AnalyticsSummary } from '../../lib/analytics-client';

function summary(
  telemetry: AnalyticsSummary['coverage']['telemetry'],
  commerce: AnalyticsSummary['coverage']['commerce']
): AnalyticsSummary {
  const hasTelemetry = telemetry === 'observed';
  const hasCommerce = commerce === 'observed';
  return {
    site_id: 'fixture-store',
    environment: 'test',
    window: { start: '2026-08-30T00:00:00Z', end: '2026-09-29T00:00:00Z', days: 30 },
    coverage: {
      status: hasTelemetry || hasCommerce ? 'partial' : 'unavailable',
      telemetry,
      commerce,
      consent: 'accepted_only',
      synthetic_events_excluded: 0,
      missing: ['attribution'],
    },
    metrics: {
      event_count: 0,
      page_views: hasTelemetry ? 0 : null,
      sessions: hasTelemetry ? 0 : null,
      product_views: hasTelemetry ? 0 : null,
      product_clicks: hasTelemetry ? 0 : null,
      add_to_cart: hasTelemetry ? 0 : null,
      checkout_started: hasTelemetry ? 0 : null,
      consented_purchases: null,
      conversion_rate: null,
      verified_purchases: hasCommerce ? 0 : null,
      verified_revenue: hasCommerce ? 0 : null,
      currency: hasCommerce ? 'USD' : null,
      spend: null,
      roas: null,
    },
    event_counts: {},
    revenue_by_currency: hasCommerce ? { USD: 0 } : {},
    provenance: {
      telemetry: 'hmac_authenticated_wordpress_bridge',
      commerce: 'signature_verified_woocommerce_paid_order',
      attribution: 'unavailable',
      revenue_basis: 'paid_order_gross_not_refund_adjusted',
    },
  };
}

const scenarios = [
  {
    name: 'observed telemetry',
    telemetry: 'observed',
    commerce: 'observed',
    evidence: 'Durable backend summary of authenticated, consented WordPress events.',
    eventCopy: 'No consented events were recorded in this window.',
  },
  {
    name: 'commerce only',
    telemetry: 'unavailable',
    commerce: 'observed',
    evidence:
      'Durable backend summary of signature-verified WooCommerce paid orders. Storefront telemetry is unavailable; no WordPress event observation is established.',
    eventCopy: 'Event counts unavailable.',
  },
  {
    name: 'neither source observed',
    telemetry: 'unavailable',
    commerce: 'unavailable',
    evidence: 'Backend summary verified, but storefront telemetry and commerce measurements are unavailable.',
    eventCopy: 'Event counts unavailable.',
  },
] as const;

test.describe('Journey reporting evidence in local fixtures', () => {
  for (const scenario of scenarios) {
    test(scenario.name, async ({ page, baseURL }, testInfo) => {
      if (testInfo.project.name === 'mobile') await page.setViewportSize({ width: 375, height: 900 });
      const errors: string[] = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.route('**/*', async route => {
        const url = new URL(route.request().url());
        const fulfill = (body: unknown) =>
          route.fulfill({ contentType: 'application/json', body: JSON.stringify(body) });
        if (url.pathname === '/api/auth/session')
          return fulfill({
            user: { name: 'Fixture Operator', email: 'fixture@example.test' },
            expires: '2099-01-01T00:00:00Z',
          });
        if (url.pathname === '/api/conversion')
          return fulfill({ success: true, summary: summary(scenario.telemetry, scenario.commerce) });
        if (url.pathname === '/api/console/orders-count') return fulfill({ count: 0 });
        if (url.origin !== new URL(baseURL ?? 'http://localhost:3000').origin)
          return fulfill({
            timestamp: '2026-09-29T00:00:00Z',
            total_agents: 0,
            active_agents: 0,
            agents_by_category: {},
            agents: [],
          });
        return route.continue();
      });
      await page.goto('/admin/journey-analytics');
      await expect(page.getByRole('heading', { name: 'Journey Analytics', level: 1 })).toBeVisible();
      await expect(page.getByText(`Evidence: ${scenario.evidence}`, { exact: false })).toBeVisible({ timeout: 15_000 });
      await expect(page.getByText(scenario.eventCopy, { exact: false })).toBeVisible();
      if (scenario.telemetry === 'unavailable') {
        await expect(page.getByText('authenticated, consented WordPress events.', { exact: false })).toHaveCount(0);
        await expect(page.getByText('No consented events were recorded', { exact: false })).toHaveCount(0);
      }
      for (const collection of ['Black Rose', 'Love Hurts', 'Signature', 'Kids Capsule']) {
        await expect(page.getByText(collection, { exact: true })).toBeVisible();
      }
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
      await page.addStyleTag({ content: 'nextjs-portal { display: none !important; }' });
      await page.evaluate(() => {
        const banner = document.createElement('p');
        banner.textContent = 'LOCAL FIXTURE: mocked session and analytics; no authenticated live execution.';
        banner.style.cssText =
          'position:absolute;top:0;left:0;right:0;z-index:99999;margin:0;padding:6px;background:#fde68a;color:#111;font:12px sans-serif;text-align:center;';
        document.body.append(banner);
      });
      const screenshot = testInfo.outputPath('journey-evidence.png');
      await page.screenshot({ path: screenshot, fullPage: true });
      await testInfo.attach('Local fixture evidence', { path: screenshot, contentType: 'image/png' });
      expect(errors).toEqual([]);
    });
  }
});
