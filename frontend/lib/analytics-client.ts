import { z } from 'zod';
import { API_URL } from '@/lib/api/config';

const count = z.number().int().nonnegative();
const metric = count.nullable();
export const analyticsSummarySchema = z.object({
  site_id: z.string().min(1),
  environment: z.enum(['staging', 'production', 'test']),
  window: z.object({
    start: z.iso.datetime({ offset: true }),
    end: z.iso.datetime({ offset: true }),
    days: count.min(1).max(90),
  }),
  coverage: z.object({
    status: z.enum(['partial', 'unavailable']),
    telemetry: z.enum(['observed', 'unavailable']),
    commerce: z.enum(['observed', 'unavailable']),
    consent: z.literal('accepted_only'),
    synthetic_events_excluded: count,
    missing: z.array(z.string()),
  }),
  metrics: z.object({
    event_count: count,
    page_views: metric,
    sessions: metric,
    product_views: metric,
    product_clicks: metric,
    add_to_cart: metric,
    checkout_started: metric,
    consented_purchases: z.null(),
    conversion_rate: z.null(),
    verified_purchases: metric,
    verified_revenue: z.number().finite().nonnegative().nullable(),
    currency: z.string().nullable(),
    spend: z.null(),
    roas: z.null(),
  }),
  event_counts: z.record(z.string(), count),
  revenue_by_currency: z.record(z.string(), z.number().finite().nonnegative()),
  provenance: z.object({
    telemetry: z.literal('hmac_authenticated_wordpress_bridge'),
    commerce: z.literal('signature_verified_woocommerce_paid_order'),
    attribution: z.literal('unavailable'),
    revenue_basis: z.literal('paid_order_gross_not_refund_adjusted'),
  }),
});

export type AnalyticsSummary = z.infer<typeof analyticsSummarySchema>;
export type AnalyticsResult = { summary: AnalyticsSummary | null; error: string | null };

/** Server-only values are read only when the route calls this function. */
export function getAnalyticsProxyConfig() {
  const siteId = process.env.SKYYROSE_ANALYTICS_SITE_ID?.trim();
  const environment = process.env.SKYYROSE_ANALYTICS_ENVIRONMENT;
  if (!siteId || !['staging', 'production', 'test'].includes(environment ?? '')) return null;
  return { apiBase: API_URL, siteId, environment: environment as AnalyticsSummary['environment'] };
}

export function parseAnalyticsDays(value: string | null): number | null {
  if (value === null) return 30;
  if (!/^\d+$/.test(value)) return null;
  const days = Number(value);
  return days >= 1 && days <= 90 ? days : null;
}

/** Never retain a previous measurement after a failed refresh. */
export async function fetchAnalyticsSummary(days = 30, signal?: AbortSignal): Promise<AnalyticsResult> {
  try {
    const response = await fetch(`/api/conversion?days=${days}`, { cache: 'no-store', signal });
    if (!response.ok) return { summary: null, error: `Analytics unavailable (HTTP ${response.status}).` };
    const payload: unknown = await response.json();
    const parsed = z.object({ success: z.literal(true), summary: analyticsSummarySchema }).safeParse(payload);
    if (!parsed.success) return { summary: null, error: 'Analytics response could not be verified.' };
    return { summary: parsed.data.summary, error: null };
  } catch {
    return { summary: null, error: 'Analytics service is unavailable.' };
  }
}

export function formatAnalyticsMetric(value: number | null | undefined, suffix = ''): string {
  return value == null ? 'Unavailable' : `${value.toLocaleString()}${suffix}`;
}

export function formatAnalyticsRevenue(summary: AnalyticsSummary | null): string {
  const revenue = summary?.metrics.verified_revenue;
  const currency = summary?.metrics.currency;
  if (revenue == null || !currency) return 'Unavailable';
  try {
    return new Intl.NumberFormat(undefined, { style: 'currency', currency }).format(revenue);
  } catch {
    return `${revenue.toLocaleString()} ${currency}`;
  }
}
