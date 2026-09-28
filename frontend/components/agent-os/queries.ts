'use client';

/**
 * Agent OS data layer — every window reads through these hooks, so a task
 * submitted from the terminal refreshes the Task Manager and agent windows
 * (shared `agent-os` query-key prefix). All data is live API data.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '@/lib/api';
import type { TaskAgentType, TaskStatus } from '@/lib/agent-os/terminal';

const TASKS_ROOT = ['agent-os', 'tasks'] as const;

export interface TaskFilter {
  agentType?: TaskAgentType;
  status?: TaskStatus;
}

export function useAgentRoster() {
  return useQuery({
    queryKey: ['agent-os', 'agents'],
    queryFn: () => api.agents.list(),
    staleTime: 30_000,
    refetchInterval: 30_000,
  });
}

export function useTaskList(filter: TaskFilter = {}) {
  return useQuery({
    queryKey: [...TASKS_ROOT, filter.agentType ?? '*', filter.status ?? '*'],
    queryFn: () => api.tasks.fetchTasks({ agent_type: filter.agentType, status: filter.status, limit: 50 }),
    refetchInterval: 10_000,
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ['agent-os', 'health'],
    queryFn: () => api.monitoring.health(),
    refetchInterval: 15_000,
  });
}

export function useSubmitTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { agentType: TaskAgentType; prompt: string }) =>
      api.tasks.submitTask(vars.agentType, vars.prompt),
    onSuccess: () => qc.invalidateQueries({ queryKey: TASKS_ROOT }),
  });
}

export function useCancelTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) => api.tasks.cancelTask(taskId),
    onSettled: () => qc.invalidateQueries({ queryKey: TASKS_ROOT }),
  });
}

/** Human-readable error line; never leaks a stack trace into the UI. */
export function errorText(err: unknown, fallback = 'Request failed'): string {
  // 4xx details are the backend's own user-facing reason ("Cannot cancel
  // task in status: completed"); 5xx bodies stay out of the UI.
  if (err instanceof ApiError && err.status < 500) return `${fallback}: ${err.message} (HTTP ${err.status})`;
  if (err instanceof ApiError) return `${fallback} (HTTP ${err.status})`;
  if (err instanceof Error && err.name === 'AbortError') return `${fallback} (timed out)`;
  return fallback;
}
