'use client';

import { STATUS_AMBER, STATUS_GREEN } from '@/lib/console/brand';
import type { ServiceHealthStatus } from '@/lib/api/types';
import { errorText, useSystemHealth } from '../queries';

function Meter({ label, pct }: { label: string; pct: number }) {
  const clamped = Math.min(100, Math.max(0, pct));
  const color = clamped >= 90 ? '#DC143C' : clamped >= 75 ? STATUS_AMBER : STATUS_GREEN;
  return (
    <div>
      <div className='flex justify-between font-mono text-[10px] uppercase tracking-[0.12em] text-[#B3B3B3]'>
        <span>{label}</span>
        <span>{pct.toFixed(1)}%</span>
      </div>
      <div
        role='meter'
        aria-label={label}
        aria-valuenow={clamped}
        aria-valuemin={0}
        aria-valuemax={100}
        className='h-1.5 rounded-full bg-white/[0.06] mt-1.5 overflow-hidden'
      >
        <div
          className='h-full rounded-full transition-[width] duration-500'
          style={{ width: `${clamped}%`, background: color }}
        />
      </div>
    </div>
  );
}

const SERVICE_COLOR: Record<ServiceHealthStatus['status'], string> = {
  healthy: STATUS_GREEN,
  degraded: STATUS_AMBER,
  down: '#DC143C',
};

/** Live GET /api/v1/monitoring/health — nothing here is estimated client-side. */
export function SystemMonitorApp() {
  const { data, isLoading, error } = useSystemHealth();

  if (isLoading) return <p className='p-4 font-mono text-[11px] text-[#A0A0A0]'>Sampling system…</p>;
  if (error || !data) {
    return (
      <p className='p-4 font-mono text-[11px] text-[#E5A85C]'>
        {errorText(error, "Couldn't reach the monitoring API")}
      </p>
    );
  }

  const s = data.system;
  return (
    <div className='p-4 space-y-5'>
      <div className='grid grid-cols-1 sm:grid-cols-3 gap-4'>
        <Meter label='CPU' pct={s.cpu_pct} />
        <Meter label='Memory' pct={s.memory_pct} />
        <Meter label='Disk' pct={s.disk_pct} />
      </div>
      <dl className='grid grid-cols-3 gap-3 font-mono text-[10px] uppercase tracking-[0.1em]'>
        {[
          ['Req / min', String(s.req_per_min)],
          ['Success', `${s.success_rate}%`],
          ['Latency', `${s.avg_latency_ms}ms`],
        ].map(([k, v]) => (
          <div key={k} className='rounded-md border border-white/[0.08] p-2.5'>
            <dt className='text-[#A0A0A0]'>{k}</dt>
            <dd className='text-white text-[14px] mt-1'>{v}</dd>
          </div>
        ))}
      </dl>
      <section aria-label='Services'>
        <h3 className='font-mono text-[10px] uppercase tracking-[0.14em] text-[#A0A0A0] mb-2'>Services</h3>
        {data.services.length === 0 && <p className='text-[13px] text-[#B3B3B3]'>No services reported.</p>}
        <ul className='divide-y divide-white/[0.06]'>
          {data.services.map(svc => (
            <li key={svc.name} className='flex items-center gap-3 py-2 text-[13px]'>
              <span
                className='w-2 h-2 rounded-full flex-none'
                style={{ background: SERVICE_COLOR[svc.status] }}
                aria-hidden
              />
              <span className='flex-1 text-[#E0E0E0] truncate'>{svc.name}</span>
              <span className='font-mono text-[10px] text-[#B3B3B3]'>
                {svc.status} · {svc.uptime_pct}% · breaker {svc.circuit_breaker}
              </span>
            </li>
          ))}
        </ul>
      </section>
      {data.events.length > 0 && (
        <section aria-label='Recent events'>
          <h3 className='font-mono text-[10px] uppercase tracking-[0.14em] text-[#A0A0A0] mb-2'>Recent events</h3>
          <ul className='space-y-1.5'>
            {data.events.slice(0, 6).map(ev => (
              <li key={ev.id} className='text-[12px] text-[#C8C8C8]'>
                <span className='font-mono text-[10px] text-[#A0A0A0]'>
                  {new Date(ev.timestamp).toLocaleTimeString()}
                </span>{' '}
                <span className='text-[#E0E0E0]'>{ev.service}</span> — {ev.message}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
