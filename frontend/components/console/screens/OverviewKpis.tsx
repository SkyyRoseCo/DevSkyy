'use client';

import { useMemo, useState } from 'react';
import { ConsoleCard } from '../Card';
import { Sparkline } from '../Sparkline';
import type { WcOrder } from '@/lib/wp/client';
import { computeKpis, dailySeries, filterByTimeframe, type Timeframe } from '@/lib/console/orders';
import { formatCurrency, formatCount } from '@/lib/console/format';

const TIMEFRAME_DAYS: Record<Timeframe, number> = { Today: 1, '7 Days': 7, '30 Days': 30 };

function periodDelta(current: number, prior: number): string | null {
  if (prior <= 0) return null;
  const pct = ((current - prior) / prior) * 100;
  const sign = pct >= 0 ? '+' : '';
  return `${sign}${pct.toFixed(1)}%`;
}

interface OverviewKpisProps {
  orders: WcOrder[];
  referenceDate: string; // ISO — passed from the server so it's stable across client re-renders
}

const TIMEFRAMES: Timeframe[] = ['Today', '7 Days', '30 Days'];

export function OverviewKpis({ orders, referenceDate }: OverviewKpisProps) {
  const [timeframe, setTimeframe] = useState<Timeframe>('Today');
  const ref = useMemo(() => new Date(referenceDate), [referenceDate]);

  const scoped = useMemo(() => filterByTimeframe(orders, timeframe, ref), [orders, timeframe, ref]);
  const kpis = useMemo(() => computeKpis(scoped), [scoped]);
  const revenueSpark = useMemo(() => dailySeries(scoped, 8, ref, 'revenue'), [scoped, ref]);
  const orderSpark = useMemo(() => dailySeries(scoped, 8, ref, 'count'), [scoped, ref]);

  // Prior period = same-length window immediately before the current one.
  const priorKpis = useMemo(() => {
    const days = TIMEFRAME_DAYS[timeframe];
    const priorRef = new Date(ref.getTime() - days * 24 * 60 * 60 * 1000);
    return computeKpis(filterByTimeframe(orders, timeframe, priorRef));
  }, [orders, timeframe, ref]);

  const revenueDelta = periodDelta(kpis.revenue, priorKpis.revenue);
  const ordersDelta = periodDelta(kpis.orderCount, priorKpis.orderCount);
  const avgOrderDelta = periodDelta(kpis.avgOrder, priorKpis.avgOrder);

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        {TIMEFRAMES.map((tf) => (
          <button
            key={tf}
            onClick={() => setTimeframe(tf)}
            className="font-mono text-[9px] uppercase tracking-[0.12em] px-2.5 py-1 rounded"
            style={
              tf === timeframe
                ? { background: 'var(--acc)', color: '#0A0A0A' }
                : { background: 'rgba(255,255,255,.05)', color: '#9A9AA2' }
            }
          >
            {tf}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-4 gap-[18px] mb-[22px]">
        <ConsoleCard className="p-5" style={{ boxShadow: '0 0 24px rgba(183,110,121,.10)' }}>
          <KpiHead label="Revenue" delta={revenueDelta} />
          <div className="font-sans text-[34px] font-semibold text-white leading-none mt-4" style={{ fontFamily: 'var(--font-cinzel)' }}>
            {formatCurrency(kpis.revenue)}
          </div>
          <Sparkline values={revenueSpark} />
        </ConsoleCard>
        <ConsoleCard className="p-5">
          <KpiHead label="Orders" delta={ordersDelta} />
          <div className="font-sans text-[34px] font-semibold text-white leading-none mt-4" style={{ fontFamily: 'var(--font-cinzel)' }}>
            {formatCount(kpis.orderCount)}
          </div>
          <Sparkline values={orderSpark} />
        </ConsoleCard>
        <ConsoleCard className="p-5">
          <KpiHead label="Avg Order" delta={avgOrderDelta} />
          <div className="font-sans text-[34px] font-semibold text-white leading-none mt-4" style={{ fontFamily: 'var(--font-cinzel)' }}>
            {formatCurrency(kpis.avgOrder)}
          </div>
          <Sparkline values={revenueSpark.map((v, i) => (orderSpark[i] > 0 ? v / orderSpark[i] : 0))} />
        </ConsoleCard>
        <ConsoleCard className="p-5">
          <KpiHead label="Conversion" delta={null} />
          <div className="font-sans text-[20px] font-semibold text-[#5A5A62] leading-none mt-4" style={{ fontFamily: 'var(--font-cinzel)' }}>
            Not wired
          </div>
          <div className="font-mono text-[9px] text-[#5A5A62] mt-3.5">needs site-traffic analytics</div>
        </ConsoleCard>
      </div>
    </div>
  );
}

function KpiHead({ label, delta }: { label: string; delta: string | null }) {
  const color = delta?.startsWith('-') ? '#E5A85C' : '#5FBF7F';
  return (
    <div className="flex justify-between items-start">
      <span className="font-mono text-[10px] tracking-[0.18em] text-[#A0A0A0] uppercase">{label}</span>
      {delta && <span className="font-mono text-[10.5px] tracking-[0.02em]" style={{ color }}>{delta}</span>}
    </div>
  );
}
