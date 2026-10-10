import { afterEach, describe, expect, it, vi } from 'vitest';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { SocialAnalytics } from '@/lib/api/endpoints/social-media';

const { getAnalytics } = vi.hoisted(() => ({ getAnalytics: vi.fn() }));
vi.mock('@/lib/api', () => ({
  api: {
    agents: { list: vi.fn() },
    tasks: { fetchTasks: vi.fn() },
    pipeline3d: { getJobs: vi.fn() },
    socialMedia: { getPostQueue: vi.fn(), getAnalytics },
  },
}));
vi.mock('next-auth/react', () => ({ signOut: vi.fn() }));

import HubPage from '@/app/admin/hub/page';

const clients: QueryClient[] = [];
const queryKey = ['hub-social-analytics'];

function createClient() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity } } });
  clients.push(client);
  client.setQueryData(['hub-agents'], { agents: [], total_agents: 0, active_agents: 0, agents_by_category: {} });
  for (const key of ['hub-tasks', 'hub-3d-jobs', 'hub-post-queue']) client.setQueryData([key], []);
  return client;
}

function observedAnalytics(posts = 7, likes = 123, queued = 9): SocialAnalytics {
  return {
    platforms: {
      instagram: {
        posts,
        likes,
        shares: 0,
        status: 'observed',
        evidence: 'Offline synthetic fixture.',
        error: null,
        window: { start: '2026-09-01T00:00:00Z', end: '2026-09-29T00:00:00Z', label: 'Fixture window' },
      },
    },
    total_posts: posts,
    total_queue: queued,
    total_published: posts,
    coverage: 'observed',
    timestamp: '2026-09-29T00:00:00Z',
    site_id: 'fixture-store',
    environment: 'test',
  };
}

function renderSocial(client: QueryClient) {
  const html = renderToStaticMarkup(createElement(QueryClientProvider, { client }, createElement(HubPage)));
  return html.slice(html.indexOf('Social · Post Analytics'), html.indexOf('<iframe'));
}

afterEach(() => {
  clients.splice(0).forEach(client => client.clear());
  getAnalytics.mockReset();
});

describe('Hub current social analytics', () => {
  it('hides actual retained query data after a successful query followed by a failed refetch', async () => {
    const client = createClient();
    const observed = observedAnalytics();
    getAnalytics.mockResolvedValueOnce(observed).mockRejectedValueOnce(new Error('HTTP 401'));
    await client.fetchQuery({ queryKey, queryFn: getAnalytics });
    expect(renderSocial(client)).toContain('9 queued');
    expect(renderSocial(client)).toContain('123 likes · observed');
    expect(renderSocial(client)).toContain('Posts published');

    await expect(client.fetchQuery({ queryKey, queryFn: getAnalytics })).rejects.toThrow('HTTP 401');
    expect(client.getQueryState(queryKey)?.status).toBe('error');
    expect(client.getQueryData(queryKey)).toEqual(observed);

    const html = renderSocial(client);
    expect(html).toContain('Social analytics unavailable.');
    expect(html).not.toContain('9 queued');
    expect(html).not.toContain('123 likes');
    expect(html).not.toContain('Posts published');
    expect(html).not.toContain('observed');

    getAnalytics.mockResolvedValueOnce(observedAnalytics(0, 0, 0));
    await client.fetchQuery({ queryKey, queryFn: getAnalytics });
    const recovered = renderSocial(client);
    expect(recovered).toContain('0 queued');
    expect(recovered).toContain('0 likes · observed');
    expect(recovered).not.toContain('Social analytics unavailable.');
  });

  it('shows an unavailable state before any analytics query succeeds', () => {
    expect(renderSocial(createClient())).toContain('Social analytics unavailable.');
  });
});
