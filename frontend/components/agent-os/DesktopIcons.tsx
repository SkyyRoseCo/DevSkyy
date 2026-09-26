'use client';

import type { AgentInfo } from '@/lib/api/types';
import { agentGradient, agentInitials, agentStatusColor } from '@/lib/console/agents';

interface DesktopIconsProps {
  agents: AgentInfo[] | undefined;
  isLoading: boolean;
  failed: boolean;
  onOpen: (agent: AgentInfo) => void;
}

function groupByCategory(agents: AgentInfo[]): Array<[string, AgentInfo[]]> {
  const groups = new Map<string, AgentInfo[]>();
  for (const a of agents) groups.set(a.category, [...(groups.get(a.category) ?? []), a]);
  return [...groups.entries()].sort(([a], [b]) => a.localeCompare(b));
}

function AgentIcon({ agent, onOpen }: { agent: AgentInfo; onOpen: () => void }) {
  const color = agentStatusColor(agent.status);
  return (
    <button
      type='button'
      onClick={onOpen}
      title={`${agent.name} — ${agent.status}`}
      className='group flex flex-col items-center gap-1.5 w-[84px] p-1.5 rounded-lg hover:bg-white/[0.06] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
    >
      <span
        className='relative w-12 h-12 rounded-[14px] flex items-center justify-center shadow-[0_6px_18px_rgba(0,0,0,.5)] transition-transform group-hover:-translate-y-0.5'
        style={{ background: agentGradient(agent.name) }}
      >
        <span className='text-[14px] font-semibold text-[#0A0A0A]' style={{ fontFamily: 'var(--font-cinzel)' }}>
          {agentInitials(agent.name)}
        </span>
        <span
          aria-hidden
          className='absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-[#0A0A0A]'
          style={{ background: color }}
        />
      </span>
      <span className='w-full text-center text-[11px] leading-tight text-[#E0E0E0] break-words line-clamp-2'>
        {agent.name}
      </span>
      <span className='sr-only'>status {agent.status}</span>
    </button>
  );
}

/** The desktop's app icons — one per agent in the live roster, grouped by category. */
export function DesktopIcons({ agents, isLoading, failed, onOpen }: DesktopIconsProps) {
  if (isLoading) return <p className='font-mono text-[11px] text-[#A0A0A0] p-4'>Mounting agent roster…</p>;
  if (failed) {
    return (
      <p className='font-mono text-[11px] text-[#E5A85C] p-4'>
        Couldn&apos;t reach /api/v1/agents. System apps still work once the API is back.
      </p>
    );
  }
  if (!agents || agents.length === 0) {
    return <p className='text-[13px] text-[#B3B3B3] p-4'>The API reports no agents.</p>;
  }
  return (
    <div className='space-y-4 p-4'>
      {groupByCategory(agents).map(([category, group]) => (
        <section key={category} aria-label={`${category} agents`}>
          <h2 className='font-mono text-[9px] uppercase tracking-[0.18em] text-[#A0A0A0] mb-1.5 px-1.5'>{category}</h2>
          <div className='flex flex-wrap gap-1'>
            {group.map(agent => (
              <AgentIcon key={agent.name} agent={agent} onOpen={() => onOpen(agent)} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
