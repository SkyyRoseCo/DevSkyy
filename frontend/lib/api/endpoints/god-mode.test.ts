import { afterEach, describe, expect, it, vi } from 'vitest';
import { godMode, type GodModeStartRequest } from './god-mode';

vi.mock('../client', async (importOriginal) => {
    const original = await importOriginal<typeof import('../client')>();
    return { ...original, getAuthHeaders: async () => ({ Authorization: 'Bearer fixture', 'Content-Type': 'application/json' }) };
});
vi.mock('../config', () => ({ API_URL: 'https://api.example.test' }));

const mission = {
    mission_id: 'fixture', objective: 'test', role: 'test', context: 'test',
    scope: 'test', deliverables: 'test', acceptance: 'test', authority: 'test',
    verification: 'test', recovery: 'test', return_contract: 'test',
};
const input: GodModeStartRequest = {
    mission, provider: 'fixture', model: 'fixture', max_calls: 1,
    max_output_tokens: 128, timeout_seconds: 10, max_cost_usd: 1,
    tools: [], authorize_paid: true,
};
const run = {
    id: 'run-one', state: 'queued', provider: 'fixture', model: 'fixture',
    mission_id: 'fixture', created_at: 1, events: [], output: null,
    verification: 'NOT_RUN', release: 'NOT_DEPLOYED',
};

function response(body: unknown, status = 200) {
    return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); });

describe('God Mode API transport', () => {
    it('validates providers without claiming provider authentication', async () => {
        const fetch = vi.fn().mockResolvedValue(response({ providers: [{ id: 'fixture', default_model: 'model', models: ['model'], enabled: true, configured: true, authenticated: false, execution_protocol: 'json-actions-v1' }], tools: [], paid_execution_enabled: true }));
        vi.stubGlobal('fetch', fetch);
        expect((await godMode.providers()).providers[0].authenticated).toBe(false);
        expect(fetch.mock.calls[0][0]).toBe('https://api.example.test/api/v1/orchestration/god-mode/providers');
        expect(fetch.mock.calls[0][1].cache).toBe('no-store');
    });

    it('sends exact authorized request and caller idempotency key with auth', async () => {
        const fetch = vi.fn().mockResolvedValue(response(run, 202));
        vi.stubGlobal('fetch', fetch);
        expect((await godMode.start(input, 'mission-unique-key')).id).toBe('run-one');
        const options = fetch.mock.calls[0][1] as RequestInit;
        expect(options.method).toBe('POST');
        expect(new Headers(options.headers).get('Idempotency-Key')).toBe('mission-unique-key');
        expect(new Headers(options.headers).get('Authorization')).toBe('Bearer fixture');
        expect(JSON.parse(options.body as string)).toEqual(input);
        expect(fetch).toHaveBeenCalledTimes(1);
    });

    it('rejects invalid limits and absent authority before network', () => {
        const fetch = vi.fn();
        vi.stubGlobal('fetch', fetch);
        for (const patch of [{ max_calls: 9 }, { max_output_tokens: 127 }, { timeout_seconds: 301 }, { max_cost_usd: 0 }, { authorize_paid: false }]) {
            expect(() => godMode.start({ ...input, ...patch } as GodModeStartRequest, 'test-key')).toThrow();
        }
        expect(() => godMode.start(input, 'bad\r\nheader')).toThrow();
        expect(fetch).not.toHaveBeenCalled();
    });

    it('propagates server rejection without retrying a paid submission', async () => {
        const fetch = vi.fn().mockResolvedValue(response({ detail: 'disabled' }, 503));
        vi.stubGlobal('fetch', fetch);
        await expect(godMode.start(input, 'test-key')).rejects.toThrow();
        expect(fetch).toHaveBeenCalledTimes(1);
    });

    it('encodes status IDs and posts cancellation', async () => {
        const fetch = vi.fn().mockImplementation(async () => response(run));
        vi.stubGlobal('fetch', fetch);
        await godMode.status('run/a');
        await godMode.cancel('run/a');
        expect(fetch.mock.calls[0][0]).toContain('/runs/run%2Fa');
        expect(fetch.mock.calls[1][0]).toContain('/runs/run%2Fa/cancel');
        expect(fetch.mock.calls[1][1].method).toBe('POST');
    });

    it('rejects a response that falsely claims verified completion', async () => {
        vi.spyOn(console, 'error').mockImplementation(() => {});
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response({ ...run, verification: 'PASS' })));
        await expect(godMode.status('run-one')).rejects.toThrow('Invalid API response format');
    });
});
