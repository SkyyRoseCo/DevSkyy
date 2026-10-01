'use client';

import { useEffect, useState } from 'react';
import { Activity, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  fetchAnalyticsSummary,
  formatAnalyticsMetric,
  formatAnalyticsRevenue,
  type AnalyticsResult,
} from '@/lib/analytics-client';

export default function ConversionIntelligencePage() {
  const [result, setResult] = useState<AnalyticsResult>({ summary: null, error: null });
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;
    async function refresh() {
      const next = await fetchAnalyticsSummary(days, controller.signal);
      if (cancelled) return;
      setResult(next);
      setLoading(false);
    }
    refresh();
    const timer = setInterval(refresh, 30_000);
    return () => {
      cancelled = true;
      controller.abort();
      clearInterval(timer);
    };
  }, [days, revision]);

  const { summary, error } = result;
  const metrics = summary?.metrics;
  const stages = [
    ['Page views', metrics?.page_views],
    ['Product views', metrics?.product_views],
    ['Product clicks', metrics?.product_clicks],
    ['Add to cart', metrics?.add_to_cart],
    ['Checkout started', metrics?.checkout_started],
    ['Verified paid orders', metrics?.verified_purchases],
  ] as const;

  return (
    <main className='space-y-6'>
      <div className='flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-gray-700 bg-gray-900 p-6'>
        <div>
          <h1 className='flex items-center gap-3 text-3xl font-bold text-white'>
            <Activity className='h-7 w-7 text-[#B76E79]' />
            Conversion Intelligence
          </h1>
          <p className='mt-2 text-gray-400'>Consent-based storefront events and verified paid orders.</p>
        </div>
        <Badge variant='outline' className='border-amber-500/50 text-amber-300'>
          {loading ? 'Loading' : summary?.coverage.status === 'partial' ? 'Partial coverage' : 'Unavailable'}
        </Badge>
      </div>

      <div className='flex flex-wrap items-center gap-3'>
        <label htmlFor='analytics-window' className='text-sm text-gray-300'>
          Reporting window
        </label>
        <select
          id='analytics-window'
          value={days}
          onChange={event => {
            setResult({ summary: null, error: null });
            setLoading(true);
            setDays(Number(event.target.value));
          }}
          className='min-h-10 rounded-md border border-gray-700 bg-gray-900 px-3 text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-rose-300'
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
        <Button variant='outline' onClick={() => setRevision(value => value + 1)}>
          <RefreshCw className='mr-2 h-4 w-4' />
          Refresh
        </Button>
      </div>

      {error && (
        <p role='status' className='rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-amber-200'>
          {error} No measurement is available for this request.
        </p>
      )}
      <Card className='border-gray-800 bg-gray-900'>
        <CardHeader>
          <CardTitle className='text-white'>Reporting scope and evidence</CardTitle>
          <CardDescription className='text-gray-400'>
            Counts apply only to the selected site, environment, and window.
          </CardDescription>
        </CardHeader>
        <CardContent className='space-y-3 text-sm text-gray-300'>
          <p>
            Site: {summary?.site_id ?? 'Unavailable'} · Environment: {summary?.environment ?? 'Unavailable'}
          </p>
          <p>Window: {summary ? `${summary.window.start} to ${summary.window.end}` : 'Unavailable'}</p>
          <p>
            Telemetry: {summary?.coverage.telemetry ?? 'unavailable'} · Commerce:{' '}
            {summary?.coverage.commerce ?? 'unavailable'} · Consent: accepted only
          </p>
          <p>
            Evidence:{' '}
            {summary
              ? 'Durable backend summary verified for this scope. Source contracts: authenticated WordPress telemetry and signature-verified WooCommerce paid orders.'
              : 'No backend summary verified.'}
          </p>
          {summary && <p>Excluded synthetic events: {summary.coverage.synthetic_events_excluded.toLocaleString()}</p>}
          {summary && summary.coverage.missing.length > 0 && (
            <p>Coverage gaps: {summary.coverage.missing.join(', ')}</p>
          )}
        </CardContent>
      </Card>

      <Card className='border-gray-800 bg-gray-900'>
        <CardHeader>
          <CardTitle className='text-white'>Observed stage counts</CardTitle>
          <CardDescription className='text-gray-400'>
            Event counts are not a linked session funnel. Purchase attribution and conversion rates are unavailable.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <dl className='grid gap-3 sm:grid-cols-2 lg:grid-cols-3'>
            {stages.map(([label, value]) => (
              <div key={label} className='rounded-lg border border-gray-800 bg-gray-800/40 p-4'>
                <dt className='text-sm text-gray-400'>{label}</dt>
                <dd className='mt-2 text-xl font-semibold text-white'>
                  {loading ? <Skeleton className='h-7 w-20' /> : formatAnalyticsMetric(value)}
                </dd>
              </div>
            ))}
          </dl>
        </CardContent>
      </Card>

      <div className='grid gap-4 md:grid-cols-3'>
        {[
          ['Verified revenue (gross)', formatAnalyticsRevenue(summary)],
          ['Observed sessions', formatAnalyticsMetric(metrics?.sessions)],
          ['Conversion rate', formatAnalyticsMetric(metrics?.conversion_rate, '%')],
        ].map(([label, value]) => (
          <Card key={label} className='border-gray-800 bg-gray-900'>
            <CardHeader>
              <CardTitle className='text-sm text-gray-400'>{label}</CardTitle>
            </CardHeader>
            <CardContent className='text-2xl font-semibold text-white'>{value}</CardContent>
          </Card>
        ))}
      </div>

      <Card className='border-gray-800 bg-gray-900'>
        <CardHeader>
          <CardTitle className='text-white'>Additional measurements</CardTitle>
        </CardHeader>
        <CardContent className='space-y-2 text-sm text-gray-400'>
          <p>
            A/B experiments, product heat, hover duration, conversion uplift, velocity, and momentum: unavailable. These
            require their own measured evidence and attribution contracts.
          </p>
          <p>
            Spend and ROAS: unavailable. No advertising spend or attributed sales source is connected to this summary.
          </p>
          <p>Verified revenue is paid-order gross revenue; refunds are not deducted.</p>
          <p>Storefront controls have no persistence endpoint available here.</p>
        </CardContent>
      </Card>
    </main>
  );
}
