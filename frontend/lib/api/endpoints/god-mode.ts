import { z } from 'zod';
import { fetchWithTimeout, getAuthHeaders, handleResponse } from '../client';
import { API_URL } from '../config';

const BASE = '/api/v1/orchestration/god-mode';
const requiredText = z.string().trim().min(1);
const missionText = requiredText.max(12000).refine(
    (text) => !['todo', 'tbd', 'n/a', 'placeholder'].includes(text.toLowerCase()),
    'Mission fields require concrete content',
);

export const GodModeMissionSchema = z.object({
    mission_id: missionText,
    objective: missionText,
    role: missionText,
    context: missionText,
    scope: missionText,
    deliverables: missionText,
    acceptance: missionText,
    authority: missionText,
    verification: missionText,
    recovery: missionText,
    return_contract: missionText,
}).strict().refine((mission) => new TextEncoder().encode(JSON.stringify(mission)).length <= 100000, 'Mission exceeds 100KB');

export const GodModeProviderSchema = z.object({
    id: requiredText,
    default_model: z.string(),
    models: z.array(z.string()).default([]),
    enabled: z.boolean(),
    configured: z.boolean(),
    authenticated: z.literal(false),
    execution_protocol: z.string(),
});

export const GodModeProvidersSchema = z.object({
    providers: z.array(GodModeProviderSchema),
    paid_execution_enabled: z.boolean(),
    tools: z.array(z.string()).default([]),
});

export const GodModeStartSchema = z.object({
    mission: GodModeMissionSchema,
    provider: requiredText.max(200),
    model: requiredText.max(200),
    max_calls: z.number().int().min(1).max(8),
    max_output_tokens: z.number().int().min(128).max(8192),
    timeout_seconds: z.number().int().min(10).max(300),
    max_cost_usd: z.number().positive().max(100),
    tools: z.array(requiredText.max(100)).max(16).refine((tools) => new Set(tools).size === tools.length, 'Tool names must be unique'),
    authorize_paid: z.literal(true),
}).strict();

export const GodModeRunSchema = z.object({
    id: requiredText,
    state: z.enum(['queued', 'running', 'cancel_requested', 'cancelled', 'completed', 'failed', 'unknown']),
    provider: requiredText,
    model: requiredText,
    mission_id: requiredText,
    created_at: z.number(),
    events: z.array(z.record(z.string(), z.unknown())),
    output: z.string().nullable(),
    verification: z.literal('NOT_RUN'),
    release: z.literal('NOT_DEPLOYED'),
    error: z.string().optional(),
    output_sha256: z.string().optional(),
    reserved_cost_usd: z.number().nonnegative().optional(),
});

export type GodModeMission = z.infer<typeof GodModeMissionSchema>;
export type GodModeProvider = z.infer<typeof GodModeProviderSchema>;
export type GodModeProviders = z.infer<typeof GodModeProvidersSchema>;
export type GodModeStartRequest = z.infer<typeof GodModeStartSchema>;
export type GodModeRun = z.infer<typeof GodModeRunSchema>;

async function request<T>(path: string, schema: z.ZodType<T>, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(await getAuthHeaders());
    new Headers(options.headers).forEach((value, key) => headers.set(key, value));
    const response = await fetchWithTimeout(`${API_URL}${BASE}${path}`, {
        ...options,
        headers,
        cache: 'no-store',
    });
    return handleResponse(response, schema);
}

function runPath(id: string): string {
    return `/runs/${encodeURIComponent(requiredText.parse(id))}`;
}

export const godMode = {
    providers(): Promise<GodModeProviders> {
        return request('/providers', GodModeProvidersSchema);
    },
    start(input: GodModeStartRequest, idempotencyKey: string): Promise<GodModeRun> {
        const payload = GodModeStartSchema.parse(input);
        const key = z.string().trim().min(8).max(128).regex(/^[A-Za-z0-9._:-]+$/).parse(idempotencyKey);
        return request('/runs', GodModeRunSchema, {
            method: 'POST',
            headers: { 'Idempotency-Key': key },
            body: JSON.stringify(payload),
        });
    },
    status(id: string): Promise<GodModeRun> {
        return request(runPath(id), GodModeRunSchema);
    },
    cancel(id: string): Promise<GodModeRun> {
        return request(`${runPath(id)}/cancel`, GodModeRunSchema, { method: 'POST' });
    },
};
