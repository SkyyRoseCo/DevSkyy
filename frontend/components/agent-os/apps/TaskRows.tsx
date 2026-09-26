'use client';

import { useState } from 'react';
import type { Task } from '@/lib/api/types';
import { STATUS_AMBER, STATUS_GREEN, STATUS_GREY } from '@/lib/console/brand';
import { errorText, useCancelTask } from '../queries';

const STATUS_COLOR: Record<Task['status'], string> = {
  pending: STATUS_AMBER,
  running: STATUS_GREEN,
  completed: STATUS_GREY,
  failed: '#DC143C',
};

function EndTaskButton({ taskId }: { taskId: string }) {
  const [armed, setArmed] = useState(false);
  const cancel = useCancelTask();

  const failure = cancel.isError ? (
    <span className='text-[11px] text-[#E5A85C]'>{errorText(cancel.error, 'End failed')}</span>
  ) : null;
  if (!armed) {
    return (
      <button
        type='button'
        onClick={() => {
          cancel.reset();
          setArmed(true);
        }}
        className='font-mono text-[10px] uppercase tracking-[0.12em] px-2.5 py-1 rounded border border-white/15 text-[#E0E0E0] hover:bg-white/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
      >
        End task
      </button>
    );
  }
  return (
    <span className='flex flex-wrap items-center justify-end gap-1.5'>
      {failure}
      <button
        type='button'
        disabled={cancel.isPending}
        onClick={() => cancel.mutate(taskId)}
        className='font-mono text-[10px] uppercase tracking-[0.12em] px-2.5 py-1 rounded bg-[#DC143C] text-white disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
      >
        {cancel.isPending ? 'Ending…' : cancel.isError ? 'Retry' : 'Confirm'}
      </button>
      <button
        type='button'
        onClick={() => setArmed(false)}
        className='font-mono text-[10px] uppercase tracking-[0.12em] px-2.5 py-1 rounded text-[#B3B3B3] hover:bg-white/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
      >
        Keep
      </button>
    </span>
  );
}

/** Process-table rows shared by the Task Manager and each agent window. */
export function TaskRows({ tasks, showAgent = true }: { tasks: Task[]; showAgent?: boolean }) {
  return (
    <ul className='divide-y divide-white/[0.06]'>
      {tasks.map(t => (
        <li key={t.taskId} className='flex items-start gap-3 py-2.5'>
          <span
            className='mt-1.5 w-2 h-2 rounded-full flex-none'
            style={{ background: STATUS_COLOR[t.status] }}
            aria-hidden
          />
          <div className='flex-1 min-w-0'>
            <div className='text-[13px] text-[#E0E0E0] truncate' title={t.prompt}>
              {t.prompt}
            </div>
            <div className='font-mono text-[10px] tracking-[0.08em] text-[#A0A0A0] mt-1'>
              {t.taskId}
              {showAgent && ` · ${t.agentType}`} · <span style={{ color: STATUS_COLOR[t.status] }}>{t.status}</span> ·{' '}
              {new Date(t.createdAt).toLocaleString()}
              {t.metrics.costUsd != null && ` · $${t.metrics.costUsd.toFixed(4)}`}
            </div>
            {t.error && <div className='text-[11px] text-[#E5A85C] mt-1'>{t.error}</div>}
          </div>
          {(t.status === 'pending' || t.status === 'running') && <EndTaskButton taskId={t.taskId} />}
        </li>
      ))}
    </ul>
  );
}
