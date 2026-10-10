'use client';

import { useEffect, useState } from 'react';
import { BarChart2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  fetchAnalyticsSummary,
  formatAnalyticsMetric,
  formatAnalyticsRevenue,
  type AnalyticsResult,
} from '@/lib/analytics-client';

/** Scoped persisted measurements. No synthetic feed or browser purchase events. */
export function ConversionPulse() {
  const [result, setResult] = useState<AnalyticsResult>({ summary: null, error: null });
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;
    async function refresh() {
      const next = await fetchAnalyticsSummary(1, controller.signal);
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
  const metrics = [
    ['Verified paid orders', formatAnalyticsMetric(summary?.metrics.verified_purchases)],
    ['Verified revenue (gross)', formatAnalyticsRevenue(summary)],
    ['Observed sessions', formatAnalyticsMetric(summary?.metrics.sessions)],
    ['Conversion rate', formatAnalyticsMetric(summary?.metrics.conversion_rate, '%')],
  ];
  return (
    <Card className='border-rose-500/20 bg-gray-900'>
      <CardHeader>
        <div className='flex flex-wrap items-center justify-between gap-3'>
          <CardTitle className='flex items-center gap-2 text-white'>
            <BarChart2 className='h-5 w-5 text-rose-300' />
            Conversion Pulse
          </CardTitle>
          <Badge variant='outline' className='border-amber-500/50 text-amber-300'>
            {loading ? 'Loading' : summary?.coverage.status === 'partial' ? 'Partial coverage' : 'Unavailable'}
          </Badge>
        </div>
        <CardDescription className='text-gray-400'>
          Persisted measurements for the last 24 hours; refreshed every 30 seconds.
        </CardDescription>
      </CardHeader>
      <CardContent className='space-y-4'>
        {error && (
          <p role='status' className='text-sm text-amber-200'>
            {error}
          </p>
        )}
        <dl className='grid grid-cols-2 gap-3'>
          {metrics.map(([label, value]) => (
            <div key={label} className='rounded-lg border border-gray-800 p-3'>
              <dt className='text-xs text-gray-400'>{label}</dt>
              <dd className='mt-1 text-lg font-semibold text-white'>{value}</dd>
            </div>
          ))}
        </dl>
        <div className='space-y-1 text-xs text-gray-400'>
          <p>
            Site: {summary?.site_id ?? 'Unavailable'} · Environment: {summary?.environment ?? 'Unavailable'}
          </p>
          <p>Window: {summary ? `${summary.window.start} to ${summary.window.end}` : 'Unavailable'}</p>
          <p>
            Evidence:{' '}
            {summary
              ? 'Durable backend summary verified for this scope. Source contracts: authenticated WordPress telemetry and signature-verified WooCommerce paid orders.'
              : 'No backend summary verified.'}
          </p>
          <p>
            Telemetry: {summary?.coverage.telemetry ?? 'unavailable'} · Commerce:{' '}
            {summary?.coverage.commerce ?? 'unavailable'}
          </p>
          <p>Live visitors, minute trend, and recent event feed: unavailable.</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default ConversionPulse;
