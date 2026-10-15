'use client';

import { useEffect, useState } from 'react';
import { Compass } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { fetchAnalyticsSummary, formatAnalyticsMetric, type AnalyticsResult } from '@/lib/analytics-client';

const COLLECTION_NAMES = ['Black Rose', 'Love Hurts', 'Signature', 'Kids Capsule'] as const;

export default function JourneyAnalyticsPage() {
  const [result, setResult] = useState<AnalyticsResult>({ summary: null, error: null });
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;
    async function refresh() {
      const next = await fetchAnalyticsSummary(30, controller.signal);
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
  }, []);
  const { summary, error } = result;
  const evidence = !summary
    ? 'No backend summary verified.'
    : summary.coverage.telemetry === 'observed'
      ? 'Durable backend summary of authenticated, consented WordPress events. Synthetic events are excluded.'
      : summary.coverage.commerce === 'observed'
        ? 'Durable backend summary of signature-verified WooCommerce paid orders. Storefront telemetry is unavailable; no WordPress event observation is established. Synthetic events are excluded.'
        : 'Backend summary verified, but storefront telemetry and commerce measurements are unavailable. Synthetic events are excluded.';

  return (
    <main className='space-y-6'>
      <div className='flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-gray-700 bg-gray-900 p-6'>
        <div>
          <h1 className='flex items-center gap-3 text-3xl font-bold text-white'>
            <Compass className='h-7 w-7 text-[#B76E79]' />
            Journey Analytics
          </h1>
          <p className='mt-2 text-gray-400'>Storefront interaction evidence for the last 30 days.</p>
        </div>
        <Badge variant='outline' className='border-amber-500/50 text-amber-300'>
          {loading ? 'Loading' : summary?.coverage.status === 'partial' ? 'Partial coverage' : 'Unavailable'}
        </Badge>
      </div>
      {error && (
        <p role='status' className='rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-amber-200'>
          {error}
        </p>
      )}
      <Card className='border-gray-800 bg-gray-900'>
        <CardHeader>
          <CardTitle className='text-white'>Reporting scope</CardTitle>
        </CardHeader>
        <CardContent className='space-y-2 text-sm text-gray-300'>
          <p>
            Site: {summary?.site_id ?? 'Unavailable'} · Environment: {summary?.environment ?? 'Unavailable'}
          </p>
          <p>Window: {summary ? `${summary.window.start} to ${summary.window.end}` : 'Unavailable'}</p>
          <p>Evidence: {evidence}</p>
          {summary && <p>Coverage gaps: {summary.coverage.missing.join(', ') || 'None reported'}</p>}
        </CardContent>
      </Card>
      <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
        {[
          ['Observed sessions', summary?.metrics.sessions],
          ['Product views', summary?.metrics.product_views],
          ['Product clicks', summary?.metrics.product_clicks],
          ['Add to cart', summary?.metrics.add_to_cart],
        ].map(([label, value]) => (
          <Card key={String(label)} className='border-gray-800 bg-gray-900'>
            <CardHeader>
              <CardTitle className='text-sm text-gray-400'>{label}</CardTitle>
            </CardHeader>
            <CardContent className='text-2xl font-semibold text-white'>
              {formatAnalyticsMetric(typeof value === 'number' ? value : null)}
            </CardContent>
          </Card>
        ))}
      </div>
      <Card className='border-gray-800 bg-gray-900'>
        <CardHeader>
          <CardTitle className='text-white'>Observed event types</CardTitle>
          <CardDescription className='text-gray-400'>
            Counts describe events in this window; they do not establish linked journeys or conversion uplift.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {summary && Object.keys(summary.event_counts).length > 0 ? (
            <dl className='grid gap-3 sm:grid-cols-2'>
              {Object.entries(summary.event_counts).map(([event, count]) => (
                <div key={event} className='flex justify-between gap-3 rounded-lg bg-gray-800/50 p-3'>
                  <dt className='break-all text-sm text-gray-300'>{event}</dt>
                  <dd className='text-white'>{formatAnalyticsMetric(count)}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <p className='text-sm text-gray-400'>
              {summary?.coverage.telemetry === 'observed'
                ? 'No consented events were recorded in this window. Journey metrics remain unavailable.'
                : 'Event counts unavailable.'}
            </p>
          )}
        </CardContent>
      </Card>
      <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
        {COLLECTION_NAMES.map(name => (
          <Card key={name} className='border-gray-800 bg-gray-900'>
            <CardHeader>
              <CardTitle className='text-white'>{name}</CardTitle>
            </CardHeader>
            <CardContent className='text-sm text-gray-400'>
              Collection journey measurements: unavailable. Collection and room breakdowns are not provided by this
              summary.
            </CardContent>
          </Card>
        ))}
      </div>
      <Card className='border-gray-800 bg-gray-900'>
        <CardHeader>
          <CardTitle className='text-white'>Journey measurement gaps</CardTitle>
        </CardHeader>
        <CardContent className='space-y-2 text-sm text-gray-400'>
          <p>
            Room visits, completion rate, reward redemptions, room heatmaps, and historical journey trends: unavailable.
          </p>
          <p>Active visitors: unavailable. A reporting-window event count cannot establish current presence.</p>
          <p>
            Conversion uplift: unavailable. No measured comparison group or linked purchase attribution is available.
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
