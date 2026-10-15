'use client';

import { useCallback, useReducer } from 'react';
import type { AgentInfo } from '@/lib/api/types';
import { INITIAL_WM_STATE, focusedWindowId, wmReducer } from '@/lib/agent-os/window-manager';
import { activeAgentCount } from '@/lib/console/agents';
import { OsWindowFrame } from './OsWindowFrame';
import { DesktopIcons } from './DesktopIcons';
import { Taskbar } from './Taskbar';
import { SYSTEM_APPS, agentWindowId, type SystemAppId } from './system-apps';
import { useAgentRoster } from './queries';
import { AgentApp } from './apps/AgentApp';
import { TaskManagerApp } from './apps/TaskManagerApp';
import { SystemMonitorApp } from './apps/SystemMonitorApp';
import { TerminalApp } from './apps/TerminalApp';

/**
 * Agent OS — the agents roster as an operating system: every agent is an app
 * on the desktop, and the platform's own task queue and health endpoints are
 * the Task Manager, System Monitor and Terminal. Window state is the pure
 * reducer in lib/agent-os/window-manager.ts.
 */
export function AgentOS() {
  const [wm, dispatch] = useReducer(wmReducer, INITIAL_WM_STATE);
  const roster = useAgentRoster();
  const agents = roster.data?.agents;
  const focusedId = focusedWindowId(wm);

  const openSystem = useCallback((id: SystemAppId) => {
    const app = SYSTEM_APPS.find(a => a.id === id);
    if (app) dispatch({ type: 'open', id, title: app.title });
  }, []);

  const openAgent = useCallback((agent: AgentInfo) => {
    dispatch({ type: 'open', id: agentWindowId(agent.name), title: agent.name });
  }, []);

  const openByName = useCallback(
    (target: string): boolean => {
      const t = target.trim().toLowerCase();
      const sys = SYSTEM_APPS.find(a => a.aliases.includes(t));
      if (sys) {
        openSystem(sys.id);
        return true;
      }
      const agent = agents?.find(a => a.name.toLowerCase() === t);
      if (agent) openAgent(agent);
      return Boolean(agent);
    },
    [agents, openAgent, openSystem]
  );

  const renderApp = (id: string) => {
    if (id === 'sys:terminal') return <TerminalApp onOpen={openByName} />;
    if (id === 'sys:tasks') return <TaskManagerApp />;
    if (id === 'sys:monitor') return <SystemMonitorApp />;
    const agent = agents?.find(a => agentWindowId(a.name) === id);
    if (agent) return <AgentApp agent={agent} />;
    return (
      <p className='p-4 text-[13px] text-[#B3B3B3]'>
        {roster.isLoading ? 'Loading…' : 'This agent is no longer reported by /api/v1/agents.'}
      </p>
    );
  };

  return (
    <div className='flex flex-col lg:h-[calc(100vh-68px)] lg:-mb-16'>
      <div
        className='relative flex-1 min-h-0 overflow-hidden'
        style={{
          background:
            'radial-gradient(1200px 600px at 20% 110%, rgba(183,110,121,.20), transparent 60%), radial-gradient(900px 500px at 95% -10%, rgba(212,175,55,.10), transparent 60%), #08080a',
        }}
      >
        <div
          aria-hidden
          className='hidden lg:block absolute bottom-6 left-8 text-[44px] uppercase tracking-[0.3em] text-white/[0.05] select-none pointer-events-none'
          style={{ fontFamily: 'var(--font-cinzel)' }}
        >
          Agent OS
        </div>

        <div className='lg:absolute lg:top-0 lg:right-0 lg:bottom-0 lg:w-[320px] lg:overflow-auto'>
          <DesktopIcons agents={agents} isLoading={roster.isLoading} failed={roster.isError} onOpen={openAgent} />
        </div>

        <div className='space-y-4 px-4 pb-4 lg:space-y-0 lg:p-0 lg:absolute lg:inset-0 lg:pointer-events-none'>
          {wm.windows.map(win => (
            <OsWindowFrame
              key={win.id}
              win={win}
              focused={win.id === focusedId}
              onFocus={() => win.id !== focusedId && dispatch({ type: 'focus', id: win.id })}
              onClose={() => dispatch({ type: 'close', id: win.id })}
              onMinimize={() => dispatch({ type: 'minimize', id: win.id })}
              onMove={(x, y) => dispatch({ type: 'move', id: win.id, x, y })}
            >
              {renderApp(win.id)}
            </OsWindowFrame>
          ))}
        </div>
      </div>

      <Taskbar
        windows={wm.windows}
        focusedId={focusedId}
        onToggle={id => dispatch({ type: 'toggle', id })}
        onLaunch={openSystem}
        activeAgents={agents ? activeAgentCount(agents) : undefined}
        totalAgents={roster.data?.total_agents}
        apiReachable={roster.isLoading ? null : !roster.isError}
      />
    </div>
  );
}
