import { fetchWithTimeout, getAuthHeaders, handleResponse } from '../client';
import { TaskSchema } from '../schemas';
import type { Task } from '../types';
import { z } from 'zod';
import { API_URL } from '../config';

/**
 * Tasks API client for the dashboard.
 * Connects to the FastAPI /tasks endpoints.
 */
export async function fetchTasks(
  params: { agent_type?: string; status?: string; limit?: number } = {}
): Promise<Task[]> {
  const headers = await getAuthHeaders();
  const query = new URLSearchParams();
  if (params.agent_type) query.append('agent_type', params.agent_type);
  if (params.status) query.append('status', params.status);
  if (params.limit) query.append('limit', params.limit.toString());

  const response = await fetchWithTimeout(`${API_URL}/api/v1/tasks?${query.toString()}`, {
    headers,
  });
  return handleResponse(response, z.array(TaskSchema));
}

export async function fetchTask(taskId: string): Promise<Task> {
  const headers = await getAuthHeaders();
  const response = await fetchWithTimeout(`${API_URL}/api/v1/tasks/${taskId}`, {
    headers,
  });
  return handleResponse(response, TaskSchema);
}

export async function submitTask(agentType: string, prompt: string, useRoundTable: boolean = false): Promise<Task> {
  const headers = await getAuthHeaders();
  const response = await fetchWithTimeout(`${API_URL}/api/v1/tasks`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      agentType,
      prompt,
      useRoundTable,
    }),
  });
  return handleResponse(response, TaskSchema);
}

export async function cancelTask(taskId: string): Promise<{ success: boolean; message: string }> {
  const headers = await getAuthHeaders();
  const response = await fetchWithTimeout(`${API_URL}/api/v1/tasks/${taskId}/cancel`, {
    method: 'POST',
    headers,
  });
  // The backend answers 404 (unknown task) / 400 (already finished) — route
  // through handleResponse so those throw instead of reading as a result.
  return handleResponse(response, z.object({ success: z.boolean(), message: z.string() }));
}
