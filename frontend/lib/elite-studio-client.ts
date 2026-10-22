import { z } from 'zod';
import { ApiError } from './api';

import { API_URL } from './api/config';
import { fetchWithTimeout, getAuthHeaders } from './api/client';

// =============================================================================
// ZOD SCHEMAS
// =============================================================================

const CreativeOperationSchema = z.object({
  operation_id: z.string(),
  intent: z.string(),
  sku: z.string(),
  status: z.enum(['queued', 'running', 'completed', 'failed']),
  created_at: z.string(),
  result: z.record(z.string(), z.unknown()).optional(),
  error: z.string().optional(),
  cost_usd: z.number(),
  stage_timings: z.record(z.string(), z.number()),
});

const CharacterSchema = z.object({
  character_id: z.string(),
  name: z.string(),
  style: z.string(),
  front_view_prompt: z.string(),
  sprite_description: z.string(),
  created_at: z.string(),
});

const OperationListResponseSchema = z.object({
  operations: z.array(CreativeOperationSchema),
  total: z.number(),
});

const UsageSchema = z.object({
  renders_used: z.number(),
  renders_quota: z.number(),
  models_3d_used: z.number(),
  social_packs_used: z.number(),
  period_start: z.string(),
  period_end: z.string(),
});

const HealthSchema = z.object({
  status: z.string(),
  services: z.record(z.string(), z.unknown()),
});

// =============================================================================
// TYPE EXPORTS
// =============================================================================

export type CreativeOperation = z.infer<typeof CreativeOperationSchema>;
export type Character = z.infer<typeof CharacterSchema>;
export type OperationListResponse = z.infer<typeof OperationListResponseSchema>;
export type EliteStudioUsage = z.infer<typeof UsageSchema>;
export type EliteStudioHealth = z.infer<typeof HealthSchema>;

export interface CreateOperationRequest {
  intent: string;
  sku: string;
  params?: Record<string, unknown>;
}

export interface ListOperationsFilters {
  status?: 'queued' | 'running' | 'completed' | 'failed';
  intent?: string;
  page?: number;
  limit?: number;
}

// =============================================================================
// REQUEST UTILITIES (mirrors api.ts patterns)
// =============================================================================

async function handleResponse<T>(response: Response, schema: z.ZodType<T>): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw ApiError.fromResponse(response.status, body);
  }
  const data = await response.json();
  const result = schema.safeParse(data);
  if (!result.success) {
    console.error('Elite Studio API response validation failed:', result.error.issues);
    throw new ApiError('Invalid Elite Studio API response format', 500, 'VALIDATION_ERROR', result.error.issues);
  }
  return result.data;
}

async function handleVoid(response: Response): Promise<void> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw ApiError.fromResponse(response.status, body);
  }
}

// =============================================================================
// ELITE STUDIO CLIENT
// =============================================================================

export const eliteStudioClient = {
  // ──────────────────────────────────────────────────────────────────────────
  // Operations
  // ──────────────────────────────────────────────────────────────────────────

  createOperation: async (
    intent: string,
    sku: string,
    params?: Record<string, unknown>
  ): Promise<CreativeOperation> => {
    if (!intent.trim()) throw new ApiError('intent is required', 400, 'INVALID_INPUT');
    if (!sku.trim()) throw new ApiError('sku is required', 400, 'INVALID_INPUT');

    const res = await fetchWithTimeout(`${API_URL}/api/v1/elite-studio/operations`, {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify({ intent: intent.trim(), sku: sku.trim(), params }),
    });
    return handleResponse(res, CreativeOperationSchema);
  },

  getOperation: async (id: string): Promise<CreativeOperation> => {
    const res = await fetchWithTimeout(`${API_URL}/api/v1/elite-studio/operations/${encodeURIComponent(id)}`, {
      headers: await getAuthHeaders(),
    });
    return handleResponse(res, CreativeOperationSchema);
  },

  listOperations: async (filters: ListOperationsFilters = {}): Promise<OperationListResponse> => {
    const params = new URLSearchParams();
    if (filters.status) params.set('status', filters.status);
    if (filters.intent) params.set('intent', filters.intent);
    if (filters.page !== undefined) params.set('page', String(Math.max(1, filters.page)));
    if (filters.limit !== undefined) params.set('limit', String(Math.min(100, Math.max(1, filters.limit))));

    const res = await fetchWithTimeout(`${API_URL}/api/v1/elite-studio/operations?${params.toString()}`, {
      headers: await getAuthHeaders(),
    });
    return handleResponse(res, OperationListResponseSchema);
  },

  cancelOperation: async (id: string): Promise<void> => {
    const res = await fetchWithTimeout(`${API_URL}/api/v1/elite-studio/operations/${encodeURIComponent(id)}/cancel`, {
      method: 'POST',
      headers: await getAuthHeaders(),
    });
    return handleVoid(res);
  },

  // ──────────────────────────────────────────────────────────────────────────
  // Characters
  // ──────────────────────────────────────────────────────────────────────────

  getCharacter: async (id: string): Promise<Character> => {
    const res = await fetchWithTimeout(`${API_URL}/api/v1/elite-studio/characters/${encodeURIComponent(id)}`, {
      headers: await getAuthHeaders(),
    });
    return handleResponse(res, CharacterSchema);
  },

  listCharacters: async (): Promise<Character[]> => {
    const res = await fetchWithTimeout(`${API_URL}/api/v1/elite-studio/characters`, {
      headers: await getAuthHeaders(),
    });
    const data = await (res.ok
      ? res.json()
      : res.json().then((b: unknown) => {
          throw ApiError.fromResponse(res.status, b);
        }));
    const parsed = z.array(CharacterSchema).safeParse(data);
    if (!parsed.success) {
      console.error('Character list validation failed:', parsed.error.issues);
      return [];
    }
    return parsed.data;
  },

  getRosie: async (): Promise<Character> => {
    const res = await fetchWithTimeout(`${API_URL}/api/v1/elite-studio/characters/rosie`, {
      headers: await getAuthHeaders(),
    });
    return handleResponse(res, CharacterSchema);
  },

  // ──────────────────────────────────────────────────────────────────────────
  // Usage
  // ──────────────────────────────────────────────────────────────────────────

  getUsage: async (): Promise<EliteStudioUsage> => {
    const res = await fetchWithTimeout(`${API_URL}/api/v2/usage`, {
      headers: await getAuthHeaders(),
    });
    return handleResponse(res, UsageSchema);
  },

  // ──────────────────────────────────────────────────────────────────────────
  // Health
  // ──────────────────────────────────────────────────────────────────────────

  getHealth: async (): Promise<EliteStudioHealth> => {
    const res = await fetchWithTimeout(`${API_URL}/api/v1/elite-studio/health`, {
      headers: await getAuthHeaders(),
    });
    return handleResponse(res, HealthSchema);
  },
};
