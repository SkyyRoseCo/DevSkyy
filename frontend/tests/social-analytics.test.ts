import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';

const { sessionMock, connectionMock, tokenMock } = vi.hoisted(() => ({
  sessionMock: vi.fn(),
  connectionMock: vi.fn(),
  tokenMock: vi.fn(),
}));
vi.mock('next-auth', () => ({ getServerSession: sessionMock }));
vi.mock('@/lib/auth', () => ({ authOptions: {} }));
vi.mock('@/lib/social-media/config', () => ({ getPlatformConnection: connectionMock, getPlatformToken: tokenMock }));

import { GET } from '@/app/api/social-media/analytics/route';
import {
  getAnalytics,
  platformEngagement,
  socialAnalyticsSchema,
  type PlatformAnalytics,
} from '@/lib/api/endpoints/social-media';

const fetchMock = vi.fn<typeof fetch>();
beforeEach(() => {
  vi.unstubAllEnvs();
  for (const key of ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_USER_ID']) vi.stubEnv(key, '');
  vi.stubGlobal('fetch', fetchMock);
  fetchMock.mockReset();
  sessionMock.mockReset().mockResolvedValue({ user: { email: 'operator@example.test' } });
  connectionMock.mockReset().mockReturnValue({ connected: false });
  tokenMock.mockReset().mockReturnValue('fixture-token');
});

const request = (query = '') => new NextRequest(`http://localhost/api/social-media/analytics${query}`);

describe('social analytics evidence contract', () => {
  it('requires authentication', async () => {
    sessionMock.mockResolvedValue(null);
    expect((await GET(request(), undefined)).status).toBe(401);
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it('marks disconnected accounts and totals unavailable without platform calls', async () => {
    const response = await GET(request(), undefined);
    const data = socialAnalyticsSchema.parse(await response.json());
    expect(data.coverage).toBe('unavailable');
    expect(data.total_posts).toBeNull();
    expect(data.total_published).toBeNull();
    expect(data.total_queue).toBeNull();
    for (const platform of Object.values(data.platforms)) {
      expect(platform.status).toBe('disconnected');
      expect(platform.posts).toBeNull();
      expect(platform.likes).toBeNull();
    }
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it('keeps dry-run unavailable instead of generating simulated reports', async () => {
    connectionMock.mockReturnValue({ connected: true });
    const response = await GET(request('?dry_run=true'), undefined);
    const body = await response.json();
    expect(body.total_posts).toBeNull();
    expect(body.simulated).toBeUndefined();
    expect(body.platforms.instagram.status).toBe('unavailable');
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it('preserves a measured zero sample while keeping disconnected accounts unknown', async () => {
    connectionMock.mockImplementation(platform => ({ connected: platform === 'instagram' }));
    vi.stubEnv('INSTAGRAM_BUSINESS_ACCOUNT_ID', 'fixture-account');
    fetchMock.mockResolvedValue(Response.json({ data: [] }));
    const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
    expect(data.platforms.instagram.status).toBe('observed');
    expect(data.platforms.instagram.posts).toBe(0);
    expect(data.platforms.instagram.likes).toBe(0);
    expect(data.platforms.instagram.reach).toBeNull();
    expect(data.platforms.tiktok.posts).toBeNull();
    expect(data.coverage).toBe('partial');
    expect(data.total_posts).toBeNull();
  });
  it('requests supported Instagram fields and day reach without inventing shares', async () => {
    connectionMock.mockImplementation(platform => ({ connected: platform === 'instagram' }));
    vi.stubEnv('INSTAGRAM_BUSINESS_ACCOUNT_ID', 'fixture-account');
    fetchMock.mockImplementation(async input => {
      const url = new URL(String(input));
      expect(url.origin).toBe('https://graph.facebook.com');
      if (url.pathname === '/v26.0/fixture-account/media') {
        expect(url.searchParams.get('fields')).toBe('like_count,comments_count');
        expect(url.searchParams.get('limit')).toBe('50');
        return Response.json({
          data: [
            { like_count: 3, comments_count: 0 },
            { like_count: 2, comments_count: 1 },
          ],
        });
      }
      expect(url.pathname).toBe('/v26.0/fixture-account/insights');
      expect(url.searchParams.get('metric')).toBe('reach');
      expect(url.searchParams.get('period')).toBe('day');
      expect(url.searchParams.get('metric_type')).toBe('time_series');
      return Response.json({ data: [{ name: 'reach', period: 'day', values: [{ value: 12 }] }] });
    });
    const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(data.platforms.instagram).toMatchObject({
      status: 'observed',
      posts: 2,
      likes: 5,
      comments: 1,
      reach: 12,
      shares: null,
    });
  });
  it.each([
    Response.json({ error: { message: 'Missing insights permission' } }, { status: 403 }),
    Response.json({ data: [{ name: 'reach', total_value: { value: 999 } }] }),
  ])('keeps valid Instagram media when reach is denied or has a different metric shape', async insightResponse => {
    connectionMock.mockImplementation(platform => ({ connected: platform === 'instagram' }));
    vi.stubEnv('INSTAGRAM_BUSINESS_ACCOUNT_ID', 'fixture-account');
    fetchMock.mockImplementation(async input =>
      String(input).includes('/insights?')
        ? insightResponse
        : Response.json({ data: [{ like_count: 0, comments_count: 1 }] })
    );
    const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
    expect(data.platforms.instagram).toMatchObject({
      status: 'observed',
      posts: 1,
      likes: 0,
      reach: null,
      shares: null,
    });
  });
  it('reads Facebook LIKE reactions and preserves an absent share count as unknown', async () => {
    connectionMock.mockImplementation(platform => ({ connected: platform === 'facebook' }));
    vi.stubEnv('FACEBOOK_PAGE_ID', 'fixture-page');
    fetchMock.mockImplementation(async input => {
      const url = new URL(String(input));
      expect(url.origin).toBe('https://graph.facebook.com');
      expect(url.pathname).toBe('/v26.0/fixture-page/posts');
      expect(url.searchParams.get('fields')).toBe(
        'reactions.type(LIKE).limit(0).summary(true),comments.limit(0).summary(true),shares'
      );
      return Response.json({
        data: [
          {
            reactions: { summary: { total_count: 2 } },
            comments: { summary: { total_count: 0 } },
            shares: { count: 1 },
          },
          { reactions: { summary: { total_count: 3 } }, comments: { summary: { total_count: 1 } } },
        ],
      });
    });
    const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(data.platforms.facebook).toMatchObject({
      status: 'observed',
      posts: 2,
      likes: 5,
      comments: 1,
      shares: null,
    });
  });
  it('does not treat a Meta error envelope as an observed empty sample', async () => {
    connectionMock.mockImplementation(platform => ({ connected: platform === 'facebook' }));
    vi.stubEnv('FACEBOOK_PAGE_ID', 'fixture-page');
    fetchMock.mockResolvedValue(Response.json({ error: { message: 'Unsupported field', code: 100 } }));
    const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
    expect(data.platforms.facebook).toMatchObject({ status: 'error', posts: null, likes: null });
    expect(data.total_posts).toBeNull();
  });
  it('sends Meta tokens only in Authorization headers, never request URLs or report bodies', async () => {
    connectionMock.mockImplementation(platform => ({ connected: platform === 'instagram' || platform === 'facebook' }));
    vi.stubEnv('INSTAGRAM_BUSINESS_ACCOUNT_ID', 'fixture-account');
    vi.stubEnv('FACEBOOK_PAGE_ID', 'fixture-page');
    tokenMock.mockReturnValue('fixture-secret-token-with-special&characters');
    fetchMock.mockResolvedValue(Response.json({ data: [] }));
    const body = await (await GET(request(), undefined)).json();
    expect(fetchMock).toHaveBeenCalledTimes(3);
    for (const [input, init] of fetchMock.mock.calls) {
      const url = new URL(String(input));
      expect(url.origin).toBe('https://graph.facebook.com');
      expect(url.searchParams.has('access_token')).toBe(false);
      expect(String(input)).not.toContain('fixture-secret');
      expect(new Headers(init?.headers).get('Authorization')).toBe(
        'Bearer fixture-secret-token-with-special&characters'
      );
    }
    expect(JSON.stringify(body)).not.toContain('fixture-secret');
  });
  it('marks connected API errors unknown and excludes them from totals', async () => {
    connectionMock.mockImplementation(platform => ({ connected: platform === 'tiktok' }));
    fetchMock.mockResolvedValue(Response.json({ error: 'access denied' }, { status: 403 }));
    const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
    expect(data.platforms.tiktok.status).toBe('error');
    expect(data.platforms.tiktok.views).toBeNull();
    expect(data.total_posts).toBeNull();
  });
  it('does not interpret an invalid platform response as an observed empty sample', async () => {
    connectionMock.mockImplementation(platform => ({ connected: platform === 'tiktok' }));
    fetchMock.mockResolvedValue(Response.json({ data: {} }));
    const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
    expect(data.platforms.tiktok.status).toBe('error');
    expect(data.platforms.tiktok.posts).toBeNull();
  });
  it('keeps missing engagement counters unavailable even when posts exist', async () => {
    connectionMock.mockImplementation(platform => ({ connected: platform === 'tiktok' }));
    fetchMock.mockResolvedValue(Response.json({ data: { videos: [{ like_count: 0, view_count: 100 }] } }));
    const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
    expect(data.platforms.tiktok.posts).toBe(1);
    expect(data.platforms.tiktok.likes).toBe(0);
    expect(data.platforms.tiktok.shares).toBeNull();
    expect(platformEngagement(data.platforms.tiktok)).toBeNull();
  });
  it('reads X with app-only credentials even when the publishing connection is disconnected', async () => {
    vi.stubEnv('TWITTER_API_KEY', 'fixture-key');
    vi.stubEnv('TWITTER_API_SECRET', 'fixture-secret');
    vi.stubEnv('TWITTER_USER_ID', 'fixture-user');
    vi.stubEnv('TWITTER_ACCESS_TOKEN', '');
    vi.stubEnv('TWITTER_ACCESS_SECRET', '');
    fetchMock.mockResolvedValueOnce(Response.json({ access_token: 'fixture-app-token' }));
    fetchMock.mockResolvedValueOnce(Response.json({ meta: { result_count: 0 } }));
    const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
    expect(data.platforms.twitter.status).toBe('observed');
    expect(data.platforms.twitter.posts).toBe(0);
    expect(data.platforms.instagram.status).toBe('disconnected');
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls[1][1]?.headers).toEqual({ Authorization: 'Bearer fixture-app-token' });
  });
  it.each(['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_USER_ID'])(
    'does not call X when app-only credential %s is absent',
    async missing => {
      vi.stubEnv('TWITTER_API_KEY', 'fixture-key');
      vi.stubEnv('TWITTER_API_SECRET', 'fixture-secret');
      vi.stubEnv('TWITTER_USER_ID', 'fixture-user');
      vi.stubEnv(missing, '');
      const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
      expect(data.platforms.twitter.status).toBe('disconnected');
      expect(fetchMock).not.toHaveBeenCalled();
    }
  );
  it('shows totals as measured zero only when every platform returned an observed empty sample', async () => {
    connectionMock.mockReturnValue({ connected: true });
    vi.stubEnv('INSTAGRAM_BUSINESS_ACCOUNT_ID', 'fixture-account');
    vi.stubEnv('FACEBOOK_PAGE_ID', 'fixture-page');
    vi.stubEnv('TWITTER_API_KEY', 'fixture-key');
    vi.stubEnv('TWITTER_API_SECRET', 'fixture-secret');
    vi.stubEnv('TWITTER_USER_ID', 'fixture-user');
    fetchMock.mockImplementation(async url => {
      if (String(url).includes('/oauth2/token')) return Response.json({ access_token: 'fixture-twitter-token' });
      if (String(url).includes('tiktokapis')) return Response.json({ data: { videos: [] }, error: { code: 'ok' } });
      return Response.json({ data: [] });
    });
    const data = socialAnalyticsSchema.parse(await (await GET(request(), undefined)).json());
    expect(data.coverage).toBe('observed');
    expect(data.total_posts).toBe(0);
    expect(data.total_published).toBe(0);
    expect(data.total_queue).toBeNull();
  });
  it('does not count retweets twice in engagement', () => {
    const platform: PlatformAnalytics = {
      posts: 1,
      likes: 0,
      comments: 0,
      shares: 2,
      retweets: 2,
      status: 'observed',
      evidence: 'fixture',
      error: null,
      window: { start: null, end: null, label: 'fixture' },
    };
    expect(platformEngagement(platform)).toBe(2);
  });
  it('routes every analytics consumer through the authenticated honest report', async () => {
    const response = await GET(request(), undefined);
    fetchMock.mockResolvedValue(response);
    const data = await getAnalytics();
    expect(data.total_posts).toBeNull();
    expect(fetchMock.mock.calls[0][0]).toBe('/api/social-media/analytics');
  });
});
