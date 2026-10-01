'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { AgentInfo } from '@/lib/api';
import { TopBar } from '@/components/console/TopBar';
import { ConsoleCard, ConsoleRow } from '@/components/console/Card';
import { StatusDot } from '@/components/console/StatusPill';
import { RoundtableDiagram } from '@/components/console/RoundtableDiagram';
import { agentGradient, agentInitials, agentStatusColor } from '@/lib/console/agents';
import { formatAnalyticsMetric } from '@/lib/analytics-client';

function timeAgo(iso: string): string {
  const ms = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(ms / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function taskStatusColor(status: string): string {
  if (status === 'completed') return '#5FBF7F';
  if (status === 'running') return 'var(--acc)';
  if (status === 'failed') return '#E5A85C';
  return '#8A8A92'; // pending
}

export default function HubPage() {
  const [calledAgent, setCalledAgent] = useState<AgentInfo | null>(null);

  const agentsQuery = useQuery({
    queryKey: ['hub-agents'],
    queryFn: () => api.agents.list(),
    staleTime: 30_000,
    refetchInterval: 30_000,
  });
  const tasksQuery = useQuery({
    queryKey: ['hub-tasks'],
    queryFn: () => api.tasks.fetchTasks({ limit: 12 }),
    staleTime: 15_000,
    refetchInterval: 15_000,
  });
  const jobsQuery = useQuery({
    queryKey: ['hub-3d-jobs'],
    queryFn: () => api.pipeline3d.getJobs(8),
    staleTime: 30_000,
    refetchInterval: 30_000,
  });
  const postsQuery = useQuery({
    queryKey: ['hub-post-queue'],
    queryFn: () => api.socialMedia.getPostQueue(),
    staleTime: 30_000,
    refetchInterval: 30_000,
  });
  const analyticsQuery = useQuery({
    queryKey: ['hub-social-analytics'],
    queryFn: () => api.socialMedia.getAnalytics(),
    staleTime: 60_000,
  });

  const agents = agentsQuery.data?.agents ?? [];
  const recentTasks = [...(tasksQuery.data ?? [])].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  const currentAnalytics = analyticsQuery.isError ? undefined : analyticsQuery.data;

  return (
    <>
      <TopBar title='The Hub' />
      <div className='px-9 py-8 max-w-[1320px]'>
        {/* Roundtable hero */}
        <ConsoleCard
          className='relative overflow-hidden mb-5 rounded-[10px]'
          style={{
            borderColor: 'rgba(183,110,121,.28)',
            background: 'linear-gradient(135deg,#100E12 0%,#0A0A0A 60%,#080808 100%)',
          }}
        >
          <div
            className='absolute inset-0 pointer-events-none'
            style={{
              background:
                'radial-gradient(70% 120% at 88% 10%,rgba(183,110,121,.16),transparent 55%), radial-gradient(50% 90% at 8% 90%,rgba(212,175,55,.07),transparent 60%)',
            }}
          />
          <div className='relative grid grid-cols-[1fr_360px] gap-7 items-center p-[30px]'>
            <div>
              <span className='font-mono text-[10px] tracking-[0.22em] uppercase' style={{ color: 'var(--acc)' }}>
                The Hub · Command Center
              </span>
              <h2
                className='text-[30px] tracking-[0.1em] uppercase text-white mt-3 font-semibold'
                style={{ fontFamily: 'var(--font-cinzel)' }}
              >
                The Roundtable
              </h2>
              <p
                className='italic text-[15px] text-white/65 mt-2.5 max-w-[52ch]'
                style={{ fontFamily: 'var(--font-playfair)' }}
              >
                Real agent roster from the DevSkyy platform, seated live. Each intelligence highlights as the diagram
                cycles — this build has no &quot;currently working&quot; event stream yet, so the cycle is a timer, not
                a task feed.
              </p>
              {calledAgent && (
                <div
                  className='flex items-center gap-2.5 mt-5 px-[15px] py-[11px] rounded-lg border w-fit'
                  style={{ borderColor: 'rgba(183,110,121,.3)', background: 'rgba(183,110,121,.06)' }}
                >
                  <StatusDot color='var(--acc)' pulse size={8} />
                  <span className='font-mono text-[10px] tracking-[0.12em] text-[#C8C8C8] uppercase'>
                    Now calling · <span style={{ color: 'var(--acc)' }}>{calledAgent.name}</span>
                  </span>
                </div>
              )}
              <div className='flex gap-[26px] mt-[22px]'>
                <HeroStat value={String(agentsQuery.data?.total_agents ?? agents.length)} label='Agents' />
                <HeroStat value={String(agentsQuery.data?.active_agents ?? 0)} label='Active' color='#5FBF7F' />
                <HeroStat
                  value={String(Object.keys(agentsQuery.data?.agents_by_category ?? {}).length)}
                  label='Categories'
                />
              </div>
            </div>
            <RoundtableDiagram agents={agents} onActiveChange={setCalledAgent} />
          </div>
        </ConsoleCard>

        {/* Pipeline columns */}
        <div className='grid grid-cols-3 gap-[18px] mb-5'>
          <ConsoleCard className='p-[22px]'>
            <PipelineHeader title='Content Studio' meta={`${postsQuery.data?.length ?? 0} in queue`} />
            {(postsQuery.data ?? []).slice(0, 5).map(post => (
              <div key={post.id} className='py-[13px] border-t border-white/[0.05]'>
                <div className='flex justify-between items-baseline gap-2.5 mb-1.5'>
                  <span className='text-[13px] text-[#E0E0E0] truncate'>{post.caption || post.content_type}</span>
                  <span
                    className='font-mono text-[9px] tracking-[0.12em] uppercase flex-none'
                    style={{
                      color: taskStatusColor(
                        post.status === 'published'
                          ? 'completed'
                          : post.status === 'scheduled'
                            ? 'pending'
                            : post.status
                      ),
                    }}
                  >
                    {post.status}
                  </span>
                </div>
                <div className='font-mono text-[9.5px] tracking-[0.1em] text-[#7A7A82] uppercase'>
                  {post.platform} · {post.collection || 'uncategorized'}
                </div>
              </div>
            ))}
            {(postsQuery.data ?? []).length === 0 && <EmptyRow label='No queued content.' />}
          </ConsoleCard>

          <ConsoleCard className='p-[22px]'>
            <PipelineHeader title='Imagery Pipeline' meta={`${jobsQuery.data?.length ?? 0} jobs`} />
            {(jobsQuery.data ?? []).slice(0, 5).map(job => (
              <div key={job.id} className='py-[13px] border-t border-white/[0.05]'>
                <div className='flex justify-between items-baseline gap-2.5 mb-1.5'>
                  <span className='text-[13px] text-[#E0E0E0] truncate'>{job.input.slice(0, 40)}</span>
                  <span
                    className='font-mono text-[9px] tracking-[0.12em] uppercase flex-none'
                    style={{ color: taskStatusColor(job.status) }}
                  >
                    {job.status}
                  </span>
                </div>
                <div className='font-mono text-[9.5px] tracking-[0.1em] text-[#7A7A82] uppercase'>
                  {job.provider} · {job.input_type}
                </div>
              </div>
            ))}
            {(jobsQuery.data ?? []).length === 0 && <EmptyRow label='No 3D/imagery jobs in flight.' />}
          </ConsoleCard>

          <ConsoleCard className='p-[22px]'>
            <PipelineHeader title='Web Automation' meta={`${recentTasks.length} tasks`} />
            {recentTasks.slice(0, 5).map(task => (
              <ConsoleRow key={task.taskId} className='flex items-center gap-3 py-3 px-1 border-t border-white/[0.05]'>
                <StatusDot color={taskStatusColor(task.status)} />
                <div className='flex-1 min-w-0'>
                  <div className='text-[12.5px] text-[#E0E0E0] truncate'>{task.prompt}</div>
                  <div className='font-mono text-[9px] tracking-[0.1em] text-[#7A7A82] uppercase mt-0.5'>
                    {task.agentType} · {timeAgo(task.createdAt)}
                  </div>
                </div>
                <span
                  className='font-mono text-[8.5px] tracking-[0.1em] uppercase flex-none'
                  style={{ color: taskStatusColor(task.status) }}
                >
                  {task.status}
                </span>
              </ConsoleRow>
            ))}
            {recentTasks.length === 0 && <EmptyRow label='No recent agent tasks.' />}
          </ConsoleCard>
        </div>

        {/* Social */}
        <ConsoleCard className='p-6 mb-5'>
          <div className='flex justify-between items-center mb-[18px]'>
            <span className='font-mono text-[10px] tracking-[0.18em] uppercase' style={{ color: 'var(--acc)' }}>
              Social · Post Analytics
            </span>
            {currentAnalytics && (
              <span className='font-mono text-[9.5px] tracking-[0.1em]' style={{ color: '#5FBF7F' }}>
                {formatAnalyticsMetric(currentAnalytics.total_queue)} queued
              </span>
            )}
          </div>
          <div className='grid grid-cols-3 gap-3.5'>
            {currentAnalytics &&
              Object.entries(currentAnalytics.platforms).map(([platform, stats]) => (
                <div
                  key={platform}
                  className='rounded-lg border border-white/[0.08] p-4'
                  style={{ background: 'rgba(17,17,19,.7)' }}
                >
                  <span
                    className='text-[13px] tracking-[0.06em] text-white uppercase'
                    style={{ fontFamily: 'var(--font-cinzel)' }}
                  >
                    {platform}
                  </span>
                  <div className='flex items-baseline gap-2 mt-3.5'>
                    <span
                      className='text-[26px] font-semibold text-white leading-none'
                      style={{ fontFamily: 'var(--font-barlow)' }}
                    >
                      {formatAnalyticsMetric(stats.posts)}
                    </span>
                    <span className='font-mono text-[10px]' style={{ color: '#5FBF7F' }}>
                      {formatAnalyticsMetric(stats.likes)} likes · {stats.status}
                    </span>
                  </div>
                  <div className='font-mono text-[8.5px] tracking-[0.14em] text-[#7A7A82] uppercase mt-1'>
                    Posts published
                  </div>
                </div>
              ))}
            {!currentAnalytics && <EmptyRow label='Social analytics unavailable.' />}
          </div>
        </ConsoleCard>

        {/* Site mirror + activity log */}
        <div className='grid grid-cols-[1.5fr_1fr] gap-[18px] mb-5'>
          <ConsoleCard className='overflow-hidden p-0'>
            <div
              className='flex items-center gap-2.5 px-4 py-3 border-b border-white/[0.08]'
              style={{ background: '#0D0D0F' }}
            >
              <span className='w-[11px] h-[11px] rounded-full bg-[#FF5F57]' />
              <span className='w-[11px] h-[11px] rounded-full bg-[#FEBC2E]' />
              <span className='w-[11px] h-[11px] rounded-full bg-[#28C840]' />
              <div className='flex-1 flex justify-center'>
                <span className='font-mono text-[11px] tracking-[0.08em] text-[#9A9AA2] bg-white/[0.04] border border-white/[0.06] rounded-md px-3 py-1.5'>
                  skyyrose.co
                </span>
              </div>
            </div>
            <iframe
              src='https://skyyrose.co'
              title='skyyrose.co live mirror'
              className='w-full h-[320px] border-0'
              loading='lazy'
            />
          </ConsoleCard>

          <ConsoleCard className='p-[22px]'>
            <PipelineHeader title='Recent Agent Activity' meta='live' />
            {recentTasks.slice(0, 5).map(task => (
              <div key={task.taskId} className='flex gap-3 py-[13px] border-t border-white/[0.05]'>
                <StatusDot color={taskStatusColor(task.status)} />
                <div className='flex-1 min-w-0'>
                  <div className='text-[12.5px] text-[#E0E0E0] leading-[1.4] truncate'>{task.prompt}</div>
                  <div className='flex gap-2 mt-1'>
                    <span
                      className='font-mono text-[8.5px] tracking-[0.1em] uppercase'
                      style={{ color: taskStatusColor(task.status) }}
                    >
                      {task.agentType}
                    </span>
                    <span className='font-mono text-[8.5px] tracking-[0.1em] text-[#7A7A82]'>
                      {timeAgo(task.createdAt)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {recentTasks.length === 0 && <EmptyRow label='No recent activity.' />}
          </ConsoleCard>
        </div>

        {/* Roster */}
        <ConsoleCard className='rounded-[10px] overflow-hidden' style={{ background: '#0C0C0E' }}>
          <div className='flex justify-between items-end gap-5 flex-wrap p-[24px_28px_18px] border-b border-white/[0.06]'>
            <div>
              <span className='font-mono text-[10px] tracking-[0.22em] uppercase' style={{ color: 'var(--acc)' }}>
                The Development Institute
              </span>
              <p
                className='italic text-[14px] text-white/60 mt-2 max-w-[56ch]'
                style={{ fontFamily: 'var(--font-playfair)' }}
              >
                Real agents registered on the DevSkyy platform — count and status only, no fabricated task copy.
              </p>
            </div>
            {agentsQuery.data && (
              <span className='font-mono text-[10px] tracking-[0.1em]' style={{ color: '#5FBF7F' }}>
                {agentsQuery.data.active_agents} active ·{' '}
                {agentsQuery.data.total_agents - agentsQuery.data.active_agents} idle
              </span>
            )}
          </div>
          <div className='grid grid-cols-3 gap-3.5 p-[22px_28px_26px]'>
            {agents.map(agent => {
              const color = agentStatusColor(agent.status);
              return (
                <ConsoleCard
                  key={agent.name}
                  className='p-[18px] flex flex-col gap-3.5'
                  style={{ background: 'rgba(17,17,19,.7)' }}
                >
                  <div className='flex items-center gap-3.5'>
                    <div className='relative flex-none'>
                      <div
                        className='w-[46px] h-[46px] rounded-full flex items-center justify-center text-[15px] font-semibold'
                        style={{
                          background: agentGradient(agent.name),
                          color: '#0A0A0A',
                          fontFamily: 'var(--font-cinzel)',
                        }}
                      >
                        {agentInitials(agent.name)}
                      </div>
                      <span
                        className='absolute -right-px -bottom-px w-3 h-3 rounded-full border-[2.5px]'
                        style={{ background: color, borderColor: '#111113' }}
                      />
                    </div>
                    <div className='flex-1 min-w-0'>
                      <div
                        className='text-[15px] tracking-[0.06em] text-white uppercase'
                        style={{ fontFamily: 'var(--font-cinzel)' }}
                      >
                        {agent.name}
                      </div>
                      <div className='text-[11.5px] text-[#9A9AA2] truncate'>{agent.category}</div>
                    </div>
                  </div>
                  <div className='flex justify-between items-center pt-[11px] border-t border-white/[0.06]'>
                    <span className='font-mono text-[10px] tracking-[0.1em] text-[#8A8A92]'>v{agent.version}</span>
                    <span
                      className='inline-flex items-center gap-1.5 font-mono text-[9px] tracking-[0.14em] uppercase'
                      style={{ color }}
                    >
                      <StatusDot color={color} size={6} />
                      {agent.status}
                    </span>
                  </div>
                </ConsoleCard>
              );
            })}
            {agents.length === 0 && <EmptyRow label='No agents reporting.' />}
          </div>
        </ConsoleCard>
      </div>
    </>
  );
}

function HeroStat({ value, label, color = '#fff' }: { value: string; label: string; color?: string }) {
  return (
    <div>
      <div className='text-[24px] font-semibold leading-none' style={{ fontFamily: 'var(--font-barlow)', color }}>
        {value}
      </div>
      <div className='font-mono text-[9px] tracking-[0.16em] text-[#8A8A92] uppercase mt-1'>{label}</div>
    </div>
  );
}

function PipelineHeader({ title, meta }: { title: string; meta: string }) {
  return (
    <div className='flex justify-between items-center mb-1.5'>
      <span className='font-mono text-[10px] tracking-[0.18em] uppercase' style={{ color: 'var(--acc)' }}>
        {title}
      </span>
      <span className='font-mono text-[9.5px] tracking-[0.1em] text-[#8A8A92]'>{meta}</span>
    </div>
  );
}

function EmptyRow({ label }: { label: string }) {
  return <div className='font-mono text-[10px] text-[#7A7A82] py-3'>{label}</div>;
}
