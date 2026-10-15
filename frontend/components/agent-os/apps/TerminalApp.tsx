'use client';

import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { formatAgents, formatSystem, formatTasks } from '@/lib/agent-os/format';
import {
  HELP_LINES,
  confirmationPrompt,
  parseCommand,
  resolveConfirmation,
  type GatedCommand,
  type TerminalCommand,
} from '@/lib/agent-os/terminal';
import { errorText } from '../queries';

type LineKind = 'in' | 'out' | 'err' | 'ok';
interface Line {
  id: number;
  kind: LineKind;
  text: string;
}

const LINE_COLOR: Record<LineKind, string> = { in: '#FFFFFF', out: '#C8C8C8', err: '#E5A85C', ok: '#5FBF7F' };

interface TerminalAppProps {
  /** Opens a desktop window by name; returns false when nothing matches. */
  onOpen: (target: string) => boolean;
}

async function runReadOnly(cmd: TerminalCommand, onOpen: TerminalAppProps['onOpen']): Promise<string[]> {
  switch (cmd.kind) {
    case 'help':
      return HELP_LINES;
    case 'ls':
      return formatAgents((await api.agents.list()).agents);
    case 'ps':
      return formatTasks(await api.tasks.fetchTasks({ status: cmd.status, limit: 50 }));
    case 'top':
      return formatSystem(await api.monitoring.health());
    case 'open':
      return onOpen(cmd.target) ? [`opened ${cmd.target}`] : [`open: no app named "${cmd.target}"`];
    default:
      return [];
  }
}

async function runGated(cmd: GatedCommand): Promise<string> {
  if (cmd.kind === 'run') {
    const task = await api.tasks.submitTask(cmd.agentType, cmd.prompt);
    return `queued ${task.taskId} (${task.agentType}) — status ${task.status}`;
  }
  const res = await api.tasks.cancelTask(cmd.taskId);
  return res.message;
}

/** A shell over the agents/tasks/monitoring APIs. `run` and `kill` never fire without a typed `y`. */
export function TerminalApp({ onOpen }: TerminalAppProps) {
  const qc = useQueryClient();
  const [lines, setLines] = useState<Line[]>([{ id: 0, kind: 'out', text: 'SkyyRose Agent OS — type "help".' }]);
  const [input, setInput] = useState('');
  const [pending, setPending] = useState<GatedCommand | null>(null);
  const [busy, setBusy] = useState(false);
  const nextId = useRef(1);
  const scroller = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight });
  }, [lines]);

  const print = (kind: LineKind, texts: string[]) =>
    setLines(prev => [...prev, ...texts.map(text => ({ id: nextId.current++, kind, text }))]);

  const execute = async (raw: string) => {
    if (pending) {
      const gated = pending;
      setPending(null);
      if (resolveConfirmation(raw) === 'abort') return print('out', ['aborted.']);
      try {
        print('ok', [await runGated(gated)]);
        await qc.invalidateQueries({ queryKey: ['agent-os', 'tasks'] });
      } catch (err) {
        print('err', [errorText(err, gated.kind === 'run' ? 'run failed' : 'kill failed')]);
      }
      return;
    }
    const cmd = parseCommand(raw);
    if (!cmd) return;
    if (cmd.kind === 'clear') return setLines([]);
    if (cmd.kind === 'error') return print('err', [cmd.message]);
    if (cmd.kind === 'run' || cmd.kind === 'kill') {
      setPending(cmd);
      return print('out', [confirmationPrompt(cmd)]);
    }
    try {
      print('out', await runReadOnly(cmd, onOpen));
    } catch (err) {
      print('err', [errorText(err, `${cmd.kind} failed`)]);
    }
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (busy) return;
    const raw = input;
    setInput('');
    print('in', [`${pending ? '?' : '❯'} ${raw}`]);
    setBusy(true);
    await execute(raw);
    setBusy(false);
  };

  return (
    <div className='h-full flex flex-col font-mono text-[12px] bg-[#070708]'>
      <div
        ref={scroller}
        role='log'
        aria-live='polite'
        aria-label='Terminal output'
        className='flex-1 min-h-0 overflow-auto p-3.5'
      >
        {lines.map(l => (
          <pre
            key={l.id}
            className='m-0 whitespace-pre-wrap break-words leading-[1.55]'
            style={{ color: LINE_COLOR[l.kind] }}
          >
            {l.text}
          </pre>
        ))}
      </div>
      <form onSubmit={onSubmit} className='flex items-center gap-2 px-3.5 py-2.5 border-t border-white/[0.06]'>
        <span aria-hidden style={{ color: pending ? '#E5A85C' : '#B76E79' }}>
          {pending ? '?' : '❯'}
        </span>
        <label htmlFor='agent-os-terminal-input' className='sr-only'>
          {pending ? 'Confirm with y' : 'Command'}
        </label>
        <input
          id='agent-os-terminal-input'
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            // Esc backs out of a pending y/N prompt instead of closing the window.
            if (e.key === 'Escape' && pending) {
              e.stopPropagation();
              setPending(null);
              print('out', ['aborted.']);
            }
          }}
          readOnly={busy}
          aria-busy={busy}
          autoComplete='off'
          spellCheck={false}
          className='flex-1 bg-transparent text-white outline-none placeholder:text-[#8A8A92]'
          placeholder={pending ? 'y / N' : 'help'}
        />
      </form>
    </div>
  );
}
