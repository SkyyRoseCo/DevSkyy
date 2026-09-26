import { Activity, ListChecks, SquareTerminal, type LucideIcon } from 'lucide-react';

export type SystemAppId = 'sys:terminal' | 'sys:tasks' | 'sys:monitor';

export interface SystemApp {
  id: SystemAppId;
  title: string;
  short: string;
  /** Names the terminal's `open <app>` accepts for this app. */
  aliases: string[];
  Icon: LucideIcon;
}

export const SYSTEM_APPS: SystemApp[] = [
  { id: 'sys:terminal', title: 'Terminal', short: 'Terminal', aliases: ['terminal', 'shell'], Icon: SquareTerminal },
  { id: 'sys:tasks', title: 'Task Manager', short: 'Tasks', aliases: ['tasks', 'taskmgr', 'ps'], Icon: ListChecks },
  {
    id: 'sys:monitor',
    title: 'System Monitor',
    short: 'Monitor',
    aliases: ['monitor', 'top', 'system'],
    Icon: Activity,
  },
];

export const agentWindowId = (name: string): string => `agent:${name}`;
