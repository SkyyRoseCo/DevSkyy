/**
 * Social Media Pipeline API Endpoints
 *
 * Manages social media content generation, scheduling,
 * and analytics for the SkyyRose platform.
 */

import { ApiError } from '../errors';
import { API_URL } from '../config';
import { getAuthHeaders, fetchWithTimeout } from '../client';
import { z } from 'zod';

export interface SocialPost {
  id: string;
  platform: 'instagram' | 'tiktok' | 'twitter' | 'facebook';
  content_type: string;
  caption: string;
  hashtags: string[];
  media_urls: string[];
  product_sku: string;
  collection: string;
  scheduled_at: string | null;
  published_at: string | null;
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  engagement: Record<string, number>;
}

export interface PlatformAnalytics {
  posts: number | null;
  likes: number | null;
  comments?: number | null;
  shares: number | null;
  reach?: number | null;
  views?: number | null;
  retweets?: number | null;
  impressions?: number | null;
  status: 'observed' | 'disconnected' | 'error' | 'unavailable';
  evidence: string;
  error: string | null;
  window: { start: string | null; end: string | null; label: string };
}

export interface SocialAnalytics {
  platforms: Record<string, PlatformAnalytics>;
  total_posts: number | null;
  total_queue: number | null;
  total_published: number | null;
  coverage: 'observed' | 'partial' | 'unavailable';
  timestamp: string;
  site_id: string | null;
  environment: 'staging' | 'production' | 'test' | null;
}

const socialMetric = z.number().finite().nonnegative().nullable();
export const socialAnalyticsSchema: z.ZodType<SocialAnalytics> = z.object({
  platforms: z.record(
    z.string(),
    z.object({
      posts: socialMetric,
      likes: socialMetric,
      shares: socialMetric,
      comments: socialMetric.optional(),
      reach: socialMetric.optional(),
      views: socialMetric.optional(),
      retweets: socialMetric.optional(),
      impressions: socialMetric.optional(),
      status: z.enum(['observed', 'disconnected', 'error', 'unavailable']),
      evidence: z.string(),
      error: z.string().nullable(),
      window: z.object({ start: z.string().nullable(), end: z.string().nullable(), label: z.string() }),
    })
  ),
  total_posts: socialMetric,
  total_queue: socialMetric,
  total_published: socialMetric,
  coverage: z.enum(['observed', 'partial', 'unavailable']),
  timestamp: z.string(),
  site_id: z.string().nullable(),
  environment: z.enum(['staging', 'production', 'test']).nullable(),
});

export function platformEngagement(stats: PlatformAnalytics | undefined): number | null {
  if (!stats) return null;
  const counts = [stats.likes, stats.comments, stats.shares];
  return counts.every((count): count is number => count != null)
    ? counts.reduce((total, count) => total + count, 0)
    : null;
}

export interface Campaign {
  id: string;
  name: string;
  collection: string;
  posts: SocialPost[];
  created_at: string;
  status: 'draft' | 'active' | 'completed';
}

/**
 * Generate a social media post for a product
 */
export async function generatePost(
  productSku: string,
  platform: string,
  contentType: string = 'product_launch'
): Promise<SocialPost> {
  if (!productSku?.trim()) {
    throw new ApiError('Product SKU is required', 400, 'INVALID_INPUT');
  }
  if (!platform?.trim()) {
    throw new ApiError('Platform is required', 400, 'INVALID_INPUT');
  }

  const res = await fetchWithTimeout(`${API_URL}/api/v1/social-media/generate`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      product_sku: productSku.trim(),
      platform: platform.trim(),
      content_type: contentType,
    }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw ApiError.fromResponse(res.status, body);
  }
  return res.json();
}

/**
 * Schedule a post for publishing
 */
export async function schedulePost(postId: string, scheduledAt: string): Promise<{ success: boolean }> {
  if (!postId?.trim()) {
    throw new ApiError('Post ID is required', 400, 'INVALID_INPUT');
  }

  const res = await fetchWithTimeout(`${API_URL}/api/v1/social-media/schedule`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      post_id: postId.trim(),
      scheduled_at: scheduledAt,
    }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw ApiError.fromResponse(res.status, body);
  }
  return res.json();
}

/**
 * Get the post queue
 */
export async function getPostQueue(): Promise<SocialPost[]> {
  const res = await fetchWithTimeout(`${API_URL}/api/v1/social-media/queue`, {
    headers: await getAuthHeaders(),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw ApiError.fromResponse(res.status, body);
  }
  return res.json();
}

/**
 * Get analytics across all platforms
 */
export async function getAnalytics(): Promise<SocialAnalytics> {
  const res = await fetchWithTimeout('/api/social-media/analytics', { cache: 'no-store' });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw ApiError.fromResponse(res.status, body);
  }
  return socialAnalyticsSchema.parse(await res.json());
}

/**
 * Generate a multi-platform campaign for a collection
 */
export async function generateCampaign(collection: string, campaignName: string): Promise<Campaign> {
  if (!collection?.trim()) {
    throw new ApiError('Collection is required', 400, 'INVALID_INPUT');
  }
  if (!campaignName?.trim()) {
    throw new ApiError('Campaign name is required', 400, 'INVALID_INPUT');
  }

  const res = await fetchWithTimeout(`${API_URL}/api/v1/social-media/campaign`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      collection: collection.trim(),
      campaign_name: campaignName.trim(),
    }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw ApiError.fromResponse(res.status, body);
  }
  return res.json();
}

/**
 * Publish a post
 */
export async function publishPost(postId: string): Promise<{ success: boolean }> {
  if (!postId?.trim()) {
    throw new ApiError('Post ID is required', 400, 'INVALID_INPUT');
  }

  const res = await fetchWithTimeout(`${API_URL}/api/v1/social-media/publish`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ post_id: postId.trim() }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw ApiError.fromResponse(res.status, body);
  }
  return res.json();
}

/**
 * Bundled social media API namespace
 */
export const socialMedia = {
  generatePost,
  schedulePost,
  getPostQueue,
  getAnalytics,
  generateCampaign,
  publishPost,
};
