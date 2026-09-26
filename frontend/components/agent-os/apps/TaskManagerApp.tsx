'use client';

import { useState } from 'react';
import { TASK_STATUSES, type TaskStatus } from '@/lib/agent-os/terminal';
import { errorText, useTaskList } from '../queries';
import { TaskRows } from './TaskRows';

/** Process table over GET /api/v1/tasks — "End task" is POST …/cancel. */
export function TaskManagerApp() {
  const [status, setStatus] = useState<TaskStatus | undefined>(undefined);
  const { data, isLoading, error, dataUpdatedAt } = useTaskList({ status });
  const filters: Array<TaskStatus | undefined> = [undefined, ...TASK_STATUSES];

  return (
    <div className='p-4'>
      <div role='group' aria-label='Filter tasks by status' className='flex flex-wrap gap-1.5 mb-3'>
        {filters.map(f => (
          <button
            key={f ?? 'all'}
            type='button'
            aria-pressed={status === f}
            onClick={() => setStatus(f)}
            className='font-mono text-[10px] uppercase tracking-[0.12em] px-2.5 py-1 rounded border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
            style={
              status === f
                ? { borderColor: '#B76E79', color: '#FFFFFF', background: 'rgba(183,110,121,.14)' }
                : { borderColor: 'rgba(255,255,255,.12)', color: '#B3B3B3' }
            }
          >
            {f ?? 'all'}
          </button>
        ))}
      </div>

      {isLoading && <p className='font-mono text-[11px] text-[#A0A0A0]'>Reading process table…</p>}
      {error && (
        <p className='font-mono text-[11px] text-[#E5A85C]'>{errorText(error, "Couldn't reach the tasks API")}</p>
      )}
      {data && data.length === 0 && (
        <p className='text-[13px] text-[#B3B3B3]'>
          No {status ?? ''} tasks. Submit one from an agent window or the terminal.
        </p>
      )}
      {data && data.length > 0 && <TaskRows tasks={data} />}
      {dataUpdatedAt > 0 && (
        <p className='font-mono text-[9px] tracking-[0.1em] uppercase text-[#8A8A92] mt-3'>
          Refreshes every 10s · last {new Date(dataUpdatedAt).toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}
