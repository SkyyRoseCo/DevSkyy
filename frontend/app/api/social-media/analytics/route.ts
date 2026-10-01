/** Platform samples never fall back to simulated business results. */
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { withAuth } from '@/lib/api-auth';
import { getPlatformConnection, getPlatformToken, type PlatformId } from '@/lib/social-media/config';
import type { PlatformAnalytics, SocialAnalytics } from '@/lib/api/endpoints/social-media';
import { getAnalyticsProxyConfig } from '@/lib/analytics-client';

// Meta's official Business SDK 26.0.2 targets Graph v26.0.
// https://github.com/facebook/facebook-python-business-sdk/blob/26.0.2/facebook_business/apiconfig.py
const META_GRAPH_VERSION = 'v26.0';
const value = z.number().finite().nonnegative().optional();
const PLATFORMS: PlatformId[] = ['instagram', 'tiktok', 'twitter', 'facebook'];
const sampleWindow = {
  start: null,
  end: null,
  label: 'Latest API sample; post dates are not bounded to a reporting window.',
};

function unavailable(status: Exclude<PlatformAnalytics['status'], 'observed'>, error: string): PlatformAnalytics {
  return {
    posts: null,
    likes: null,
    comments: null,
    shares: null,
    reach: null,
    views: null,
    retweets: null,
    impressions: null,
    status,
    error,
    evidence: 'No platform measurement verified.',
    window: { start: null, end: null, label: 'Unavailable' },
  };
}

function observed(metrics: Omit<PlatformAnalytics, 'status' | 'evidence' | 'error' | 'window'>): PlatformAnalytics {
  return {
    ...metrics,
    status: 'observed',
    error: null,
    evidence: 'Authenticated platform API response; limited latest-post sample.',
    window: sampleWindow,
  };
}

function sum(values: Array<number | undefined>): number | null {
  return values.some(item => item === undefined)
    ? null
    : values.reduce<number>((total, item) => total + (item ?? 0), 0);
}

async function platformFetch(url: string, init?: RequestInit): Promise<unknown> {
  const response = await fetch(url, { ...init, cache: 'no-store', signal: AbortSignal.timeout(10_000) });
  if (!response.ok) throw new Error('Platform API request failed.');
  return response.json();
}

async function instagram(): Promise<PlatformAnalytics> {
  const token = getPlatformToken('instagram');
  const account = process.env.INSTAGRAM_BUSINESS_ACCOUNT_ID;
  if (!token || !account) return unavailable('disconnected', 'Instagram account is not configured.');
  const [mediaPayload, insightPayload] = await Promise.all([
    platformFetch(
      `https://graph.facebook.com/${META_GRAPH_VERSION}/${account}/media?fields=like_count,comments_count&limit=50`,
      { headers: { Authorization: `Bearer ${token}` } }
    ),
    platformFetch(
      `https://graph.facebook.com/${META_GRAPH_VERSION}/${account}/insights?metric=reach&period=day&metric_type=time_series`,
      { headers: { Authorization: `Bearer ${token}` } }
    ).catch(() => null),
  ]);
  const media = z.object({ data: z.array(z.object({ like_count: value, comments_count: value })) }).parse(mediaPayload);
  const insights = z
    .object({
      data: z.array(z.object({ name: z.string(), values: z.array(z.object({ value: z.number().nonnegative() })) })),
    })
    .safeParse(insightPayload);
  const reach = insights.success
    ? (insights.data.data.find(item => item.name === 'reach')?.values[0]?.value ?? null)
    : null;
  return {
    ...observed({
      posts: media.data.length,
      likes: sum(media.data.map(post => post.like_count)),
      comments: sum(media.data.map(post => post.comments_count)),
      // `shares` is not an IGMedia field; this query does not collect share insights.
      shares: null,
      reach,
    }),
    window: {
      start: null,
      end: null,
      label: 'Latest 50 posts; reach is the platform day insight and has a separate window.',
    },
  };
}

async function tiktok(): Promise<PlatformAnalytics> {
  const payload = await platformFetch(
    'https://open.tiktokapis.com/v2/video/list/?fields=like_count,share_count,view_count,comment_count',
    {
      method: 'POST',
      headers: { Authorization: `Bearer ${getPlatformToken('tiktok')}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ max_count: 50 }),
    }
  );
  const data = z
    .object({
      data: z.object({
        videos: z.array(z.object({ like_count: value, share_count: value, view_count: value, comment_count: value })),
      }),
      error: z.object({ code: z.string() }).optional(),
    })
    .parse(payload);
  if (data.error && data.error.code !== 'ok') throw new Error('Platform returned an error.');
  return observed({
    posts: data.data.videos.length,
    likes: sum(data.data.videos.map(video => video.like_count)),
    shares: sum(data.data.videos.map(video => video.share_count)),
    views: sum(data.data.videos.map(video => video.view_count)),
    comments: sum(data.data.videos.map(video => video.comment_count)),
  });
}

async function twitter(): Promise<PlatformAnalytics> {
  const key = process.env.TWITTER_API_KEY;
  const secret = process.env.TWITTER_API_SECRET;
  const user = process.env.TWITTER_USER_ID;
  if (!key || !secret || !user) return unavailable('disconnected', 'X account ID or credentials are not configured.');
  const payload = await platformFetch('https://api.twitter.com/oauth2/token', {
    method: 'POST',
    headers: {
      Authorization: `Basic ${Buffer.from(`${key}:${secret}`).toString('base64')}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'grant_type=client_credentials',
  });
  const token = z.object({ access_token: z.string().min(1) }).parse(payload);
  const tweetsPayload = await platformFetch(
    `https://api.twitter.com/2/users/${user}/tweets?max_results=50&tweet.fields=public_metrics`,
    { headers: { Authorization: `Bearer ${token.access_token}` } }
  );
  const tweets = z
    .object({
      data: z
        .array(
          z.object({
            public_metrics: z
              .object({ like_count: value, retweet_count: value, reply_count: value, impression_count: value })
              .optional(),
          })
        )
        .optional(),
      meta: z.object({ result_count: z.number().int().nonnegative() }).optional(),
    })
    .parse(tweetsPayload);
  if (!tweets.data && tweets.meta?.result_count !== 0) throw new Error('No verified tweet sample.');
  const rows = tweets.data ?? [];
  const shares = sum(rows.map(tweet => tweet.public_metrics?.retweet_count));
  return observed({
    posts: rows.length,
    likes: sum(rows.map(tweet => tweet.public_metrics?.like_count)),
    shares,
    retweets: shares,
    comments: sum(rows.map(tweet => tweet.public_metrics?.reply_count)),
    impressions: sum(rows.map(tweet => tweet.public_metrics?.impression_count)),
  });
}

async function facebook(): Promise<PlatformAnalytics> {
  const token = getPlatformToken('facebook');
  const page = process.env.FACEBOOK_PAGE_ID;
  if (!token || !page) return unavailable('disconnected', 'Facebook page is not configured.');
  const payload = await platformFetch(
    `https://graph.facebook.com/${META_GRAPH_VERSION}/${page}/posts?fields=reactions.type(LIKE).limit(0).summary(true),comments.limit(0).summary(true),shares&limit=50`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  const data = z
    .object({
      data: z.array(
        z.object({
          reactions: z.object({ summary: z.object({ total_count: value }) }).optional(),
          comments: z.object({ summary: z.object({ total_count: value }) }).optional(),
          shares: z.object({ count: value }).optional(),
        })
      ),
    })
    .parse(payload);
  // Absent shares or reach are unknown, even when other engagement fields exist.
  return observed({
    posts: data.data.length,
    likes: sum(data.data.map(post => post.reactions?.summary.total_count)),
    comments: sum(data.data.map(post => post.comments?.summary.total_count)),
    shares: sum(data.data.map(post => post.shares?.count)),
    reach: null,
  });
}

const fetchers: Record<PlatformId, () => Promise<PlatformAnalytics>> = { instagram, tiktok, twitter, facebook };

async function readPlatform(platform: PlatformId, dryRun: boolean): Promise<PlatformAnalytics> {
  if (dryRun) return unavailable('unavailable', 'Dry-run collects no platform measurements.');
  // X analytics uses app-only credentials, unlike the publishing connection.
  if (platform !== 'twitter' && !getPlatformConnection(platform).connected)
    return unavailable('disconnected', 'Platform account is not configured.');
  try {
    return await fetchers[platform]();
  } catch {
    return unavailable('error', 'Platform API measurement failed or returned an invalid response.');
  }
}

async function getHandler(request: NextRequest) {
  const dryRun = request.nextUrl.searchParams.get('dry_run') === 'true';
  const rows = await Promise.all(
    PLATFORMS.map(async platform => [platform, await readPlatform(platform, dryRun)] as const)
  );
  const platforms = Object.fromEntries(rows);
  const observedCount = Object.values(platforms).filter(platform => platform.status === 'observed').length;
  const complete = observedCount === PLATFORMS.length;
  const posts = complete
    ? Object.values(platforms).reduce((total, platform) => total + (platform.posts ?? 0), 0)
    : null;
  const scope = getAnalyticsProxyConfig();
  const analytics: SocialAnalytics = {
    platforms,
    coverage: complete ? 'observed' : observedCount > 0 ? 'partial' : 'unavailable',
    timestamp: new Date().toISOString(),
    total_posts: posts,
    total_published: posts,
    total_queue: null,
    site_id: scope?.siteId ?? null,
    environment: scope?.environment ?? null,
  };
  return NextResponse.json({ success: true, ...analytics }, { headers: { 'Cache-Control': 'no-store' } });
}

export const GET = withAuth(getHandler);
