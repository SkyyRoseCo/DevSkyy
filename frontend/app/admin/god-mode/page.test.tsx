// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, createElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { ApiError } from '@/lib/api/errors';
import GodModePage from './page';

const api = vi.hoisted(() => ({providers:vi.fn(), start:vi.fn(), status:vi.fn(), cancel:vi.fn(), recoveryKey:vi.fn()}));
vi.mock('@/lib/api/endpoints/god-mode', () => ({godMode:api, getGodModeRecoveryKey:api.recoveryKey}));
let root: Root;
let host: HTMLDivElement;
const pending = {key:'stable-request-key',body:{mission:{objective:'Concrete mission'},authorize_paid:true}};

beforeEach(() => {
    Object.assign(globalThis, {IS_REACT_ACT_ENVIRONMENT:true});
    vi.clearAllMocks(); localStorage.clear(); sessionStorage.clear();
    api.recoveryKey.mockResolvedValue('godmode-run-v1:test-owner');
    api.providers.mockResolvedValue({providers:[], tools:[], paid_execution_enabled:true});
    host = document.createElement('div'); document.body.append(host); root = createRoot(host);
});
afterEach(async () => { await act(async () => root.unmount()); host.remove(); });
async function mount() { await act(async () => root.render(createElement(GodModePage))); }
function retry() { return Array.from(host.querySelectorAll('button')).find(b => b.textContent === 'Retry same submission'); }

describe('God Mode paid submission recovery', () => {
    it('keeps the same body/key on ambiguous 503 and across remount', async () => {
        sessionStorage.setItem('godmode-run-v1:test-owner',JSON.stringify({pending}));
        api.start.mockRejectedValue(new ApiError('gateway unavailable',503));
        await mount();
        // Pending recovery loads uncertain state and shows retry button immediately
        expect(retry()).toBeDefined();
        expect(api.start).not.toHaveBeenCalled();
        await act(async () => retry()?.click());
        expect(api.start).toHaveBeenCalledWith(pending.body,pending.key);
        expect(sessionStorage.getItem('godmode-run-v1:test-owner')).toContain(pending.key);
        await act(async () => root.unmount()); root = createRoot(host); await mount();
        await act(async () => retry()?.click());
        expect(api.start).toHaveBeenCalledTimes(2);
        expect(api.start.mock.calls[1]).toEqual(api.start.mock.calls[0]);
    });
    it.each([401, 403, 409, 422])('preserves recovered submissions after HTTP %s (uncertain protects idempotency)', async status => {
        sessionStorage.setItem('godmode-run-v1:test-owner',JSON.stringify({pending}));
        api.start.mockRejectedValue(new ApiError('policy or session changed',status));
        await mount();
        // Initial recovery loads uncertain state and shows retry
        expect(retry()).toBeDefined();
        await act(async () => retry()?.click());
        // Recovered pending with definitive errors still preserves recovery (uncertain=true blocks the clear path)
        expect(sessionStorage.getItem('godmode-run-v1:test-owner')).toContain(pending.key);
        expect(retry()).toBeDefined();
        await act(async () => retry()?.click());
        expect(api.start.mock.calls[1]).toEqual(api.start.mock.calls[0]);
    });
    it('isolates recovery from a different account', async () => {
        sessionStorage.setItem('godmode-run-v1:other-owner',JSON.stringify({pending}));
        await mount();
        expect(retry()).toBeUndefined(); expect(api.start).not.toHaveBeenCalled();
    });
    it('restores run status without resubmitting paid work', async () => {
        sessionStorage.setItem('godmode-run-v1:test-owner',JSON.stringify({runId:'existing-run'}));
        api.status.mockResolvedValue({id:'existing-run',state:'unknown',verification:'NOT_RUN',release:'NOT_DEPLOYED',output:null});
        await mount();
        // Wait for async status call to complete
        await vi.waitFor(() => expect(host.textContent).toContain('Mission: unknown'));
        expect(host.textContent).toContain('Verification: NOT_RUN');
        expect(api.start).not.toHaveBeenCalled();
    });
    it('waits for authenticated identity before restoring persisted work', async () => {
        let resolve!: (key: string) => void;
        api.recoveryKey.mockReturnValue(new Promise<string>(r => { resolve = r; }));
        sessionStorage.setItem('godmode-run-v1:test-owner',JSON.stringify({pending}));
        await mount();
        expect(host.querySelector('fieldset')?.disabled).toBe(true);
        expect(retry()).toBeUndefined();
        await act(async () => resolve('godmode-run-v1:test-owner'));
        expect(retry()).toBeDefined();
        expect(api.start).not.toHaveBeenCalled();
    });
    it('blocks a retry when the authenticated account changes', async () => {
        sessionStorage.setItem('godmode-run-v1:test-owner',JSON.stringify({pending}));
        await mount();
        api.recoveryKey.mockResolvedValue('godmode-run-v1:other-owner');
        await act(async () => retry()?.click());
        expect(api.start).not.toHaveBeenCalled();
        expect(host.textContent).toContain('Session changed');
        expect(sessionStorage.getItem('godmode-run-v1:test-owner')).toContain(pending.key);
    });
    it('keeps execution locked when identity is unavailable', async () => {
        api.recoveryKey.mockRejectedValue(new Error('expired session'));
        await mount();
        expect(host.querySelector('fieldset')?.disabled).toBe(true);
        expect(api.start).not.toHaveBeenCalled();
    });

});
