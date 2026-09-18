'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { CONSOLE_NAV_ITEMS } from './nav-config';
import { GrainOverlay } from './GrainOverlay';
import { activeAgentCount } from '@/lib/console/agents';

interface ConsoleShellProps {
  children: React.ReactNode;
}

async function fetchOrderCount(): Promise<number> {
  const res = await fetch('/api/console/orders-count');
  if (!res.ok) return 0;
  const data = (await res.json()) as { count: number };
  return data.count;
}

export function ConsoleShell({ children }: ConsoleShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { data: session, status } = useSession();
  const userName = session?.user?.email ? session.user.email.split('@')[0] : 'Operator';

  // Server Component /admin pages skip their data fetch (never render real
  // WooCommerce data) when unauthenticated, but don't redirect themselves —
  // redirect() thrown from a Server Component under this app's Cache
  // Components config is silently swallowed (see lib/require-admin-session.ts).
  // This is the actual navigation to /login for an unauthenticated visitor.
  useEffect(() => {
    if (status === 'unauthenticated') {
      router.replace('/login');
    }
  }, [status, router]);

  const { data: agentsData } = useQuery({
    queryKey: ['console-agents-count'],
    queryFn: () => api.agents.list(),
    staleTime: 60_000,
    refetchInterval: 60_000,
  });
  const activeAgents = agentsData ? activeAgentCount(agentsData.agents) : undefined;

  const { data: orderCount = 0 } = useQuery({
    queryKey: ['console-orders-count'],
    queryFn: fetchOrderCount,
    staleTime: 60_000,
    refetchInterval: 60_000,
  });

  const badgeFor = (id: string): string | undefined => {
    if (id === 'orders' && orderCount > 0) return String(orderCount);
    if ((id === 'hub' || id === 'agents') && activeAgents !== undefined && activeAgents > 0) {
      return String(activeAgents);
    }
    return undefined;
  };

  return (
    <div className="dsh min-h-screen" style={{ background: 'var(--void)' }}>
      <GrainOverlay />
      <aside className="relative w-full flex flex-col p-[26px_18px] z-50 border-b border-white/[0.06] lg:fixed lg:top-0 lg:left-0 lg:bottom-0 lg:w-[240px] lg:border-b-0 lg:border-r" style={{ background: '#0A0A0A' }}>
        <div className="flex items-center gap-3 px-2 pb-[26px] border-b border-white/[0.06]">
          <div
            aria-hidden
            className="w-[34px] h-[34px] rounded-full flex items-center justify-center flex-none drop-shadow-[0_2px_8px_rgba(0,0,0,.6)]"
            style={{ background: 'linear-gradient(135deg,#B76E79,#D4AF37)' }}
          >
            <span className="text-[12px] font-semibold" style={{ color: '#0A0A0A', fontFamily: 'var(--font-cinzel)' }}>
              SR
            </span>
          </div>
          <div>
            <div className="text-[13px] tracking-[0.22em] text-white uppercase" style={{ fontFamily: 'var(--font-cinzel)' }}>
              Skyy Rose
            </div>
            <div className="font-mono text-[9px] tracking-[0.2em] uppercase mt-0.5" style={{ color: 'var(--acc)' }}>
              Operator Console
            </div>
          </div>
        </div>

        <nav aria-label="Operator console" className="flex flex-wrap gap-[3px] mt-[22px] mb-4 lg:mb-0 lg:flex-col lg:flex-nowrap lg:flex-1">
          {CONSOLE_NAV_ITEMS.map((item) => {
            const active = pathname === item.href;
            const badge = badgeFor(item.id);
            return (
              <Link
                key={item.id}
                href={item.href}
                aria-current={active ? 'page' : undefined}
                className="dsh-nav-item flex items-center gap-[11px] px-3 py-[11px] rounded-md text-[13px] tracking-[0.02em] no-underline transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
                style={active ? { background: 'rgba(183,110,121,.12)', color: '#fff' } : { color: '#9A9AA2' }}
              >
                <span className="w-1.5 h-1.5 rounded-full flex-none" style={{ background: active ? 'var(--acc)' : '#3A3A42' }} />
                <span className="flex-1">{item.label}</span>
                {badge && (
                  <span className="font-mono text-[9px] tracking-[0.1em]" style={{ color: 'var(--acc)' }}>
                    {badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto pt-3.5 px-2.5 border-t border-white/[0.06] flex items-center gap-2.5">
          <div
            className="w-[30px] h-[30px] rounded-full flex items-center justify-center text-[12px] font-semibold"
            style={{ background: 'linear-gradient(135deg,#B76E79,#D4AF37)', color: '#0A0A0A', fontFamily: 'var(--font-cinzel)' }}
          >
            SR
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[12.5px] text-[#E0E0E0] font-semibold truncate">{userName}</div>
            <div className="text-[10px] text-[#A0A0A0]">Operator</div>
          </div>
        </div>
      </aside>

      <main className="min-w-0 min-h-screen pb-16 lg:ml-[240px]">{children}</main>
    </div>
  );
}
