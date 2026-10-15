'use client';

import { useState } from 'react';
import type { AgentInfo } from '@/lib/api/types';
import { TASK_AGENT_TYPES, type TaskAgentType } from '@/lib/agent-os/terminal';
import { agentStatusColor } from '@/lib/console/agents';
import { errorText, useSubmitTask, useTaskList } from '../queries';
import { TaskRows } from './TaskRows';

/** The roster's `category` is free text; only the six task types are runnable. */
function defaultTaskType(agent: AgentInfo): TaskAgentType {
  const c = agent.category.toLowerCase();
  return (TASK_AGENT_TYPES as readonly string[]).includes(c) ? (c as TaskAgentType) : 'operations';
}

function RunTaskForm({ agent }: { agent: AgentInfo }) {
  const [agentType, setAgentType] = useState<TaskAgentType>(defaultTaskType(agent));
  const [prompt, setPrompt] = useState('');
  const [armed, setArmed] = useState(false);
  const submit = useSubmitTask();
  const ready = prompt.trim().length > 0;

  const confirm = () =>
    submit.mutate(
      { agentType, prompt: prompt.trim() },
      {
        onSuccess: () => {
          setPrompt('');
          setArmed(false);
        },
      }
    );

  return (
    <form
      onSubmit={e => {
        e.preventDefault();
        if (ready) setArmed(true);
      }}
      className='space-y-2.5'
    >
      <div className='flex gap-2 items-center'>
        <label
          htmlFor={`os-type-${agent.name}`}
          className='font-mono text-[10px] uppercase tracking-[0.12em] text-[#A0A0A0]'
        >
          Task type
        </label>
        <select
          id={`os-type-${agent.name}`}
          value={agentType}
          onChange={e => setAgentType(e.target.value as TaskAgentType)}
          className='bg-[#141416] border border-white/15 rounded px-2 py-1 text-[12px] text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
        >
          {TASK_AGENT_TYPES.map(t => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>
      <label htmlFor={`os-prompt-${agent.name}`} className='sr-only'>
        Task prompt
      </label>
      <textarea
        id={`os-prompt-${agent.name}`}
        value={prompt}
        onChange={e => {
          setPrompt(e.target.value);
          setArmed(false);
        }}
        rows={3}
        placeholder='Describe the task for this agent…'
        className='w-full resize-none bg-[#141416] border border-white/15 rounded-md px-3 py-2 text-[13px] text-white placeholder:text-[#8A8A92] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#B76E79]'
      />
      {!armed ? (
        <button
          type='submit'
          disabled={!ready}
          className='font-mono text-[10px] uppercase tracking-[0.14em] px-3.5 py-2 rounded border border-[#B76E79]/70 text-white hover:bg-[#B76E79]/15 disabled:opacity-40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
        >
          Run task
        </button>
      ) : (
        <div role='alert' className='flex flex-wrap items-center gap-2 text-[12px] text-[#E0E0E0]'>
          <span>Submit a {agentType} task? This runs a model call and may cost money.</span>
          <button
            type='button'
            onClick={confirm}
            disabled={submit.isPending}
            className='font-mono text-[10px] uppercase tracking-[0.12em] px-3 py-1.5 rounded bg-[#B76E79] text-[#0A0A0A] disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
          >
            {submit.isPending ? 'Submitting…' : 'Confirm'}
          </button>
          <button
            type='button'
            onClick={() => setArmed(false)}
            className='font-mono text-[10px] uppercase tracking-[0.12em] px-3 py-1.5 rounded text-[#B3B3B3] hover:bg-white/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white'
          >
            Cancel
          </button>
        </div>
      )}
      {submit.isError && <p className='text-[12px] text-[#E5A85C]'>{errorText(submit.error, 'Submit failed')}</p>}
      {submit.isSuccess && <p className='text-[12px] text-[#5FBF7F]'>Queued task {submit.data.taskId}.</p>}
    </form>
  );
}

function RecentTasks({ agentType }: { agentType: TaskAgentType }) {
  const { data, isLoading, error } = useTaskList({ agentType });
  if (isLoading) return <p className='font-mono text-[11px] text-[#A0A0A0]'>Loading…</p>;
  if (error)
    return <p className='font-mono text-[11px] text-[#E5A85C]'>{errorText(error, "Couldn't reach the tasks API")}</p>;
  if (!data || data.length === 0) return <p className='text-[13px] text-[#B3B3B3]'>No {agentType} tasks yet.</p>;
  return <TaskRows tasks={data.slice(0, 8)} showAgent={false} />;
}

/** One agent as an application: identity, capabilities, endpoints, run, history. */
export function AgentApp({ agent }: { agent: AgentInfo }) {
  const color = agentStatusColor(agent.status);
  return (
    <div className='p-4 space-y-5'>
      <div className='flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[10px] uppercase tracking-[0.12em] text-[#B3B3B3]'>
        <span style={{ color }}>● {agent.status}</span>
        <span>{agent.category}</span>
        <span>v{agent.version}</span>
        <span>
          {agent.last_execution ? `Last run ${new Date(agent.last_execution).toLocaleString()}` : 'Never run'}
        </span>
      </div>

      {agent.capabilities.length > 0 && (
        <section aria-label='Capabilities'>
          <h3 className='font-mono text-[10px] uppercase tracking-[0.14em] text-[#A0A0A0] mb-2'>Capabilities</h3>
          <ul className='flex flex-wrap gap-1.5'>
            {agent.capabilities.map(c => (
              <li key={c} className='text-[12px] text-[#E0E0E0] px-2.5 py-1 rounded-full border border-white/10'>
                {c}
              </li>
            ))}
          </ul>
        </section>
      )}

      {agent.endpoints.length > 0 && (
        <section aria-label='Endpoints'>
          <h3 className='font-mono text-[10px] uppercase tracking-[0.14em] text-[#A0A0A0] mb-2'>Endpoints</h3>
          <ul className='font-mono text-[11px] text-[#C8C8C8] space-y-1'>
            {agent.endpoints.map(ep => (
              <li key={ep}>{ep}</li>
            ))}
          </ul>
        </section>
      )}

      <section aria-label='Run a task'>
        <h3 className='font-mono text-[10px] uppercase tracking-[0.14em] text-[#A0A0A0] mb-2'>Run</h3>
        <RunTaskForm agent={agent} />
      </section>

      <section aria-label='Recent tasks'>
        <h3 className='font-mono text-[10px] uppercase tracking-[0.14em] text-[#A0A0A0] mb-2'>Recent tasks</h3>
        <RecentTasks agentType={defaultTaskType(agent)} />
      </section>
    </div>
  );
}
