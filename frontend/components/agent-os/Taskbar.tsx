'use client';

import { useEffect, useState } from 'react';
import type { OsWindow } from '@/lib/agent-os/window-manager';
import { STATUS_AMBER, STATUS_GREEN, STATUS_GREY } from '@/lib/console/brand';
import { SYSTEM_APPS, type SystemAppId } from './system-apps';

/** Time renders only after mount: a clock read during render would break
 *  Next 16 Cache Components prerendering (see app/admin/layout.tsx). */
function Clock() {
  const [now, setNow] = useState<Date | null>(null);
  useEffect(() => {
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), 30_000);
    return () => clearInterval(id);
  }, []);
  return (
    <time className='font-mono text-[11px] text-[#E0E0E0] tabular-nums min-w-[44px] text-right'>
      {now ? now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
    </time>
  );
}

interface TaskbarProps {
  windows: OsWindow[];
  focusedId: string | null;
  onToggle: (id: string) => void;
  onLaunch: (id: SystemAppId) => void;
  activeAgents?: number;
  totalAgents?: number;
  apiReachable: boolean | null;
}

export function Taskbar({
  windows,
  focusedId,
  onToggle,
  onLaunch,
  activeAgents,
  totalAgents,
  apiReachable,
}: TaskbarProps) {
  const apiColor = apiReachable === null ? STATUS_GREY : apiReachable ? STATUS_GREEN : STATUS_AMBER;
  return (
    <nav
      aria-label='Agent OS taskbar'
      className='flex flex-wrap items-center gap-2 px-3 py-2 border-t border-white/[0.08] backdrop-blur-xl lg:flex-nowrap lg:h-12 lg:py-0'
      style={{ background: 'rgba(10,10,12,.88)' }}
    >
      <div className='flex gap-1.5'>
        {SYSTEM_APPS.map(app => (
          <button
            key={app.id}
            type='button'
            onClick={() => onLaunch(app.id)}
            className='flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.12em] px-2.5 py-1.5 rounded-md border border-white/10 text-[#E0E0E0] hover:bg-white/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
          >
            <app.Icon aria-hidden className='w-3.5 h-3.5' style={{ color: '#B76E79' }} />
            {app.short}
          </button>
        ))}
      </div>

      <span aria-hidden className='hidden lg:block w-px h-6 bg-white/10 mx-1' />

      <ul className='flex flex-1 min-w-0 gap-1.5 overflow-x-auto'>
        {windows.map(w => {
          const active = w.id === focusedId;
          return (
            <li key={w.id} className='flex-none'>
              <button
                type='button'
                onClick={() => onToggle(w.id)}
                aria-pressed={active}
                title={w.minimized ? `Restore ${w.title}` : active ? `Minimize ${w.title}` : `Focus ${w.title}`}
                className='max-w-[180px] truncate text-[12px] px-3 py-1.5 rounded-md border-b-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
                style={{
                  background: active ? 'rgba(183,110,121,.16)' : 'rgba(255,255,255,.03)',
                  borderBottomColor: active ? '#B76E79' : w.minimized ? 'transparent' : '#6A6A72',
                  color: w.minimized ? '#A0A0A0' : '#FFFFFF',
                }}
              >
                {w.title}
              </button>
            </li>
          );
        })}
      </ul>

      <div className='flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.12em] text-[#B3B3B3]'>
        <span className='flex items-center gap-1.5'>
          <span className='w-2 h-2 rounded-full' style={{ background: apiColor }} aria-hidden />
          {apiReachable === false ? 'API offline' : 'API'}
        </span>
        {totalAgents !== undefined && (
          <span>
            {activeAgents}/{totalAgents} agents
          </span>
        )}
        <Clock />
      </div>
    </nav>
  );
}
