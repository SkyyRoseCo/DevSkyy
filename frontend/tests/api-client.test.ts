import { afterEach, expect, it, vi } from 'vitest';
import { fetchWithTimeout, getAuthHeaders, getAuthToken } from '../lib/api/client';
import { API_URL } from '../lib/api/config';
import { brandAssets } from '../lib/api/endpoints/brand-assets';
import { buildBackendUrl } from '../lib/backend-proxy';
afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});
it('never reads browser credentials or emits a Bearer header', async () => {
  const getItem = vi.fn(() => {
    throw new Error('browser credentials accessed');
  });
  vi.stubGlobal('window', {});
  vi.stubGlobal('localStorage', { getItem });
  expect(getAuthToken()).toBeNull();
  expect(new Headers(await getAuthHeaders()).has('authorization')).toBe(false);
  expect(getItem).not.toHaveBeenCalled();
});
it('routes configured backend requests through the dashboard, preserving query and multipart', async () => {
  vi.stubGlobal('window', {});
  const fetcher = vi.fn().mockResolvedValue(new Response());
  vi.stubGlobal('fetch', fetcher);
  const body = new FormData();
  body.set('file', 'example');
  await fetchWithTimeout(`${API_URL}/api/v1/assets/upload?source=test`, { method: 'POST', body });
  expect(fetcher.mock.calls[0][0]).toBe('/api/platform/api/v1/assets/upload?source=test');
  expect(fetcher.mock.calls[0][1].body).toBe(body);
  expect(fetcher.mock.calls[0][1].headers).toBeUndefined();
});
it('preserves non-backend and server request URLs', async () => {
  const fetcher = vi.fn().mockResolvedValue(new Response());
  vi.stubGlobal('fetch', fetcher);
  await fetchWithTimeout('https://external.example.test/file', {});
  expect(fetcher.mock.calls[0][0]).toBe('https://external.example.test/file');
});
it('preserves an already-aborted caller signal', async () => {
  const caller = new AbortController();
  caller.abort();
  const fetcher = vi.fn(async (_url, init) => {
    expect(init.signal.aborted).toBe(true);
    return new Response();
  });
  vi.stubGlobal('fetch', fetcher);
  await fetchWithTimeout('/api/settings', { signal: caller.signal });
});
it('aborts when a caller cancels after the request starts', async () => {
  const caller = new AbortController();
  let received: AbortSignal | undefined;
  vi.stubGlobal(
    'fetch',
    vi.fn(async (_url, init) => {
      received = init.signal;
      caller.abort();
      return new Response();
    })
  );
  await fetchWithTimeout('/api/settings', { signal: caller.signal });
  expect(received?.aborted).toBe(true);
});

it('keeps existing Next.js pipeline and settings routes on the dashboard', async () => {
  vi.stubGlobal('window', {});
  const fetcher = vi.fn().mockResolvedValue(new Response());
  vi.stubGlobal('fetch', fetcher);
  for (const path of ['/api/v1/3d/status', '/api/v1/3d/generate/image', '/api/settings']) {
    await fetchWithTimeout(path, {});
    expect(fetcher.mock.calls.at(-1)?.[0]).toBe(path);
  }
});
it('enforces the timeout while retaining caller cancellation', async () => {
  vi.useFakeTimers();
  let signal: AbortSignal | undefined;
  vi.stubGlobal(
    'fetch',
    vi.fn((_url, init) => {
      signal = init.signal;
      return new Promise<Response>(resolve => setTimeout(() => resolve(new Response()), 20));
    })
  );
  const result = fetchWithTimeout('/api/settings', {}, 10);
  await vi.advanceTimersByTimeAsync(10);
  expect(signal?.aborted).toBe(true);
  await vi.advanceTimersByTimeAsync(10);
  await result;
});

it.each(['approve', 'reject'] as const)(
  'sends the actual brandAssets.%s client through a PATCH-authorized relay path',
  async action => {
    vi.stubGlobal('window', {});
    const fetcher = vi
      .fn()
      .mockResolvedValue(Response.json({ error: 'synthetic upstream unavailable' }, { status: 503 }));
    vi.stubGlobal('fetch', fetcher);
    await expect(brandAssets[action]('example-id')).rejects.toThrow();
    const [url, options] = fetcher.mock.calls[0];
    expect(url).toBe(`/api/platform/api/v1/brand-assets/assets/example-id/${action}`);
    expect(options.method).toBe('PATCH');
    expect(buildBackendUrl(url.slice('/api/platform'.length), '', options.method)).not.toBeNull();
  }
);
