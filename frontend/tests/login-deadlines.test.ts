// @vitest-environment jsdom
import { act, createElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { CredentialsConfig } from 'next-auth/providers/credentials';

const { signIn, push } = vi.hoisted(() => ({ signIn: vi.fn(), push: vi.fn() }));
vi.mock('next/navigation', () => ({ useRouter: () => ({ push }) }));
vi.mock('next-auth/react', () => ({ signIn }));
// Capture the exact source authorize callback passed to the SDK provider.
vi.mock('next-auth/providers/credentials', () => ({ default: (options: unknown) => options }));

import LoginPage from '@/app/login/page';
import { authOptions } from '@/lib/auth';

const credentials = { email: 'offline@example.invalid', password: 'SyntheticPassword123!' };
const tokens = { access_token: 'synthetic-access', refresh_token: 'synthetic-refresh', token_type: 'Bearer' };
const authorize = (authOptions.providers[0] as CredentialsConfig).authorize;
const request = { body: {}, query: {}, headers: {}, method: 'POST' };
let root: Root | undefined;
let container: HTMLDivElement;
const fetchMock = vi.fn<typeof fetch>();
let fixtureTime = new Date('2026-10-01T12:00:00Z').getTime();

beforeEach(() => {
  vi.useFakeTimers();
  fixtureTime += 120000;
  vi.setSystemTime(fixtureTime);
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true);
  vi.stubGlobal('fetch', fetchMock);
  fetchMock.mockReset();
  signIn.mockReset();
  push.mockReset();
  localStorage.clear();
  document.cookie = 'access_token=; path=/; max-age=0';
  container = document.createElement('div');
  document.body.appendChild(container);
});

afterEach(async () => {
  if (root) await act(() => root?.unmount());
  root = undefined;
  container.remove();
  vi.restoreAllMocks();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

async function renderForm() {
  await act(async () => {
    root = createRoot(container);
    root.render(createElement(LoginPage));
  });
  for (const [id, value] of [
    ['email', credentials.email],
    ['password', credentials.password],
  ]) {
    const input = container.querySelector<HTMLInputElement>(`#${id}`)!;
    await act(async () => {
      Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, value);
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });
  }
}

async function submit() {
  await act(async () => {
    container.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
  });
}

function submitButton() {
  return container.querySelector<HTMLButtonElement>('button[type="submit"]')!;
}

describe('bounded login deadlines', () => {
  it('allows retry after successful legacy login and stalled NextAuth; ignores the late first result', async () => {
    const setTimer = vi.spyOn(globalThis, 'setTimeout');
    const clearTimer = vi.spyOn(globalThis, 'clearTimeout');
    let resolveFirst!: (result: { ok: boolean }) => void;
    signIn.mockImplementationOnce(
      () =>
        new Promise(resolve => {
          resolveFirst = resolve;
        })
    );
    fetchMock.mockImplementation(async () => new Response(JSON.stringify(tokens)));
    await renderForm();
    await submit();
    expect(signIn).toHaveBeenCalledTimes(1);
    expect(submitButton().disabled).toBe(true);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(30000);
    });
    expect(submitButton().disabled).toBe(false);
    expect(container.textContent).toContain('Login request timed out. Please try again.');
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(document.cookie).not.toContain('access_token=');
    expect(push).not.toHaveBeenCalled();

    signIn.mockResolvedValueOnce({ ok: true });
    await submit();
    expect(signIn).toHaveBeenCalledTimes(2);
    expect(localStorage.getItem('access_token')).toBe(tokens.access_token);
    expect(push).toHaveBeenCalledExactlyOnceWith('/admin');
    await act(async () => {
      resolveFirst({ ok: true });
    });
    expect(push).toHaveBeenCalledTimes(1);
    expect(submitButton().disabled).toBe(false);
    expect(container.textContent).not.toContain('timed out');
    const deadlines = setTimer.mock.calls.flatMap((args, index) =>
      args[1] === 30000 ? [setTimer.mock.results[index].value] : []
    );
    expect(deadlines).toHaveLength(2);
    for (const timer of deadlines) expect(clearTimer).toHaveBeenCalledWith(timer);
  });

  it.each(['fetch', 'body'])('bounds a stalled legacy %s and aborts its transport', async phase => {
    const signal: AbortSignal[] = [];
    fetchMock.mockImplementation(async (_, init) => {
      signal.push(init!.signal!);
      return phase === 'fetch'
        ? new Promise<Response>(() => {})
        : ({ ok: true, json: () => new Promise(() => {}) } as Response);
    });
    await renderForm();
    await submit();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(30000);
    });
    expect(signal[0].aborted).toBe(true);
    expect(submitButton().disabled).toBe(false);
    expect(signIn).not.toHaveBeenCalled();
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it.each(['fetch', 'body'])('server authorize returns null on stalled %s without leaking credentials', async phase => {
    fetchMock.mockImplementation(() =>
      phase === 'fetch'
        ? new Promise(() => {})
        : Promise.resolve({ ok: true, json: () => new Promise(() => {}) } as Response)
    );
    const result = authorize(credentials, request);
    await vi.advanceTimersByTimeAsync(10000);
    await expect(result).resolves.toBeNull();
    expect(fetchMock.mock.calls[0][1]!.signal!.aborted).toBe(true);
    expect(vi.getTimerCount()).toBe(0);
  });

  it.each(['rejected', 'unauthorized', 'invalid-body'])('server clears the deadline on fast %s failure', async mode => {
    if (mode === 'rejected') fetchMock.mockRejectedValue(new Error('private upstream error'));
    else fetchMock.mockResolvedValue(new Response(JSON.stringify({}), { status: mode === 'unauthorized' ? 401 : 200 }));
    await expect(authorize(credentials, request)).resolves.toBeNull();
    expect(vi.getTimerCount()).toBe(0);
  });

  it('keeps successful server identity and token fields unchanged and clears its timer', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify(tokens)));
    await expect(authorize(credentials, request)).resolves.toEqual({
      id: credentials.email,
      email: credentials.email,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
    });
    expect(vi.getTimerCount()).toBe(0);
  });
});
