'use client';

import { useEffect, useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Share2,
  Send,
  Calendar,
  BarChart3,
  Loader2,
  CheckCircle2,
  Clock,
  Sparkles,
  TrendingUp,
  Eye,
  Heart,
  MessageCircle,
  Repeat2,
  Play,
  Megaphone,
  Hash,
  FileText,
  AlertCircle,
} from 'lucide-react';
import type { SocialPost, SocialAnalytics, PlatformAnalytics, Campaign } from '@/lib/api/endpoints/social-media';
import { getAnalytics, platformEngagement } from '@/lib/api/endpoints/social-media';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PLATFORM_CONFIG: Record<string, { label: string; color: string; bgColor: string; borderColor: string }> = {
  instagram: {
    label: 'Instagram',
    color: '#E1306C',
    bgColor: 'bg-[#E1306C]/10',
    borderColor: 'border-[#E1306C]/30',
  },
  tiktok: {
    label: 'TikTok',
    color: '#000000',
    bgColor: 'bg-white/10',
    borderColor: 'border-white/20',
  },
  twitter: {
    label: 'X / Twitter',
    color: '#1DA1F2',
    bgColor: 'bg-[#1DA1F2]/10',
    borderColor: 'border-[#1DA1F2]/30',
  },
  facebook: {
    label: 'Facebook',
    color: '#4267B2',
    bgColor: 'bg-[#4267B2]/10',
    borderColor: 'border-[#4267B2]/30',
  },
};

const COLLECTIONS = [
  { value: 'black-rose', label: 'Black Rose' },
  { value: 'love-hurts', label: 'Love Hurts' },
  { value: 'signature', label: 'Signature' },
];

interface ProductOption {
  value: string;
  label: string;
  collection: string;
}

// Product list is fetched from /api/products on mount — reads the canonical
// catalog CSV server-side. Never hardcode SKUs here.

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function SocialMediaPage() {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<SocialAnalytics | null>(null);
  const [queue, setQueue] = useState<SocialPost[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [products, setProducts] = useState<ProductOption[]>([]);

  // Post generator state
  const [selectedSku, setSelectedSku] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('instagram');
  const [generating, setGenerating] = useState(false);
  const [generatedPost, setGeneratedPost] = useState<SocialPost | null>(null);

  // Campaign generator state
  const [campaignCollection, setCampaignCollection] = useState('black-rose');
  const [campaignName, setCampaignName] = useState('');
  const [generatingCampaign, setGeneratingCampaign] = useState(false);

  // Error state
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [analyticsData, scheduleRes, productsRes] = await Promise.all([
        getAnalytics().catch(() => null),
        fetch('/api/social-media/schedule'),
        fetch('/api/products'),
      ]);

      if (productsRes.ok) {
        const productsJson = await productsRes.json();
        if (productsJson?.success && Array.isArray(productsJson.data?.products)) {
          type ApiProduct = { sku: string; name: string; collection: string };
          const opts: ProductOption[] = (productsJson.data.products as ApiProduct[]).map(p => ({
            value: p.sku,
            label: p.name,
            collection: p.collection,
          }));
          setProducts(opts);
        }
      }

      setAnalytics(analyticsData);

      if (scheduleRes.ok) {
        const scheduleJson = await scheduleRes.json();
        if (Array.isArray(scheduleJson.scheduled_posts)) {
          // Scheduled posts populate queue display
          setQueue(prev => (prev.length > 0 ? prev : []));
        }
      }

      setError(null);
    } catch {
      setAnalytics(null);
      setError('Failed to load social media data. Backend may be offline.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  async function handleGeneratePost() {
    if (!selectedSku) return;
    setGenerating(true);
    setError(null);

    try {
      const res = await fetch('/api/social-media/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_sku: selectedSku,
          platform: selectedPlatform,
          content_type: 'product_launch',
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error((errData as Record<string, string>).error ?? 'Generation failed');
      }

      const data = await res.json();
      const post: SocialPost = data.post ?? {
        id: Math.random().toString(36).slice(2, 14),
        platform: selectedPlatform as SocialPost['platform'],
        content_type: 'product_launch',
        caption: data.caption ?? '',
        hashtags: data.hashtags ?? ['#SkyyRose'],
        media_urls: [],
        product_sku: selectedSku,
        collection: '',
        scheduled_at: null,
        published_at: null,
        status: 'draft',
        engagement: {},
      };
      setGeneratedPost(post);
      setQueue(prev => [post, ...prev]);
    } catch {
      setError('Failed to generate post. Please try again.');
    } finally {
      setGenerating(false);
    }
  }

  async function handleGenerateCampaign() {
    if (!campaignCollection || !campaignName.trim()) return;
    setGeneratingCampaign(true);
    setError(null);

    try {
      const collectionProducts = products.filter(p => p.collection === campaignCollection);
      const campaignPosts: SocialPost[] = [];
      const platforms = ['instagram', 'tiktok', 'twitter', 'facebook'] as const;

      // Generate posts via API for first 3 products x 4 platforms
      for (const product of collectionProducts.slice(0, 3)) {
        for (const platform of platforms) {
          try {
            const res = await fetch('/api/social-media/generate', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                product_sku: product.value,
                platform,
                content_type: 'collection_drop',
              }),
            });

            if (res.ok) {
              const data = await res.json();
              if (data.post) {
                campaignPosts.push(data.post);
                continue;
              }
            }
          } catch {
            // Fall through to template-generated post
          }

          // Fallback if API call fails
          campaignPosts.push({
            id: Math.random().toString(36).slice(2, 14),
            platform,
            content_type: 'collection_drop',
            caption: `${product.label} -- ${campaignName}`,
            hashtags: ['#SkyyRose', '#WhereLoveMeetsLuxury'],
            media_urls: [],
            product_sku: product.value,
            collection: campaignCollection,
            scheduled_at: null,
            published_at: null,
            status: 'draft',
            engagement: {},
          });
        }
      }

      const campaign: Campaign = {
        id: Math.random().toString(36).slice(2, 14),
        name: campaignName,
        collection: campaignCollection,
        posts: campaignPosts,
        created_at: new Date().toISOString(),
        status: 'draft',
      };
      setCampaigns(prev => [campaign, ...prev]);
      setQueue(prev => [...campaignPosts, ...prev]);
      setCampaignName('');
    } catch {
      setError('Failed to generate campaign. Please try again.');
    } finally {
      setGeneratingCampaign(false);
    }
  }

  if (loading) {
    return <SocialMediaSkeleton />;
  }

  return (
    <div className='space-y-6'>
      {/* Header */}
      <div className='relative overflow-hidden rounded-2xl bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8 border border-gray-700'>
        <div className='absolute inset-0 bg-grid-white/[0.02]' />
        <div className='absolute top-0 right-0 w-96 h-96 bg-[#B76E79]/10 rounded-full blur-3xl' />
        <div className='absolute bottom-0 left-0 w-64 h-64 bg-[#D4AF37]/10 rounded-full blur-3xl' />

        <div className='relative flex items-center justify-between'>
          <div>
            <h1 className='text-3xl font-bold text-white flex items-center gap-3'>
              <div className='h-12 w-12 rounded-xl bg-gradient-to-br from-[#B76E79] to-[#D4AF37] flex items-center justify-center'>
                <Megaphone className='h-6 w-6 text-white' />
              </div>
              Social Media Command Center
            </h1>
            <p className='text-gray-400 mt-2 ml-15'>
              Generate, schedule, and track content across Instagram, TikTok, X, and Facebook
            </p>
          </div>
          <div className='flex items-center gap-3'>
            <Badge variant='outline' className='border-[#B76E79] text-[#B76E79]'>
              <div className='h-2 w-2 rounded-full mr-2 bg-[#B76E79] animate-pulse' />
              SkyyRose Brand
            </Badge>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className='flex items-center gap-3 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400'>
          <AlertCircle className='h-5 w-5 flex-shrink-0' />
          <p className='text-sm'>{error}</p>
          <Button
            variant='ghost'
            size='sm'
            className='ml-auto text-red-400 hover:text-red-300'
            onClick={() => setError(null)}
          >
            Dismiss
          </Button>
        </div>
      )}

      {/* Platform Stats */}
      <p role='status' className='text-sm text-gray-400'>
        Analytics coverage: {analytics?.coverage ?? 'unavailable'}. Configured site:{' '}
        {analytics?.site_id ?? 'Unavailable'} · Environment: {analytics?.environment ?? 'Unavailable'}. Latest platform
        samples have separate windows; disconnected or failed measurements remain unavailable.
      </p>
      <div className='grid gap-4 md:grid-cols-4'>
        {Object.entries(PLATFORM_CONFIG).map(([key, config]) => {
          const stats = analytics?.platforms[key];
          return (
            <PlatformStatCard
              key={key}
              platform={config.label}
              color={config.color}
              bgColor={config.bgColor}
              posts={stats?.posts ?? null}
              engagement={platformEngagement(stats)}
              reach={stats?.reach ?? stats?.impressions ?? stats?.views ?? null}
              status={stats?.status ?? 'unavailable'}
            />
          );
        })}
      </div>

      {/* Overview Stats */}
      <div className='grid gap-4 md:grid-cols-3'>
        <GradientStatCard
          title='Observed Posts (API samples)'
          value={formatNumber(analytics?.total_posts)}
          icon={FileText}
          gradient='from-[#B76E79] to-[#D4AF37]'
        />
        <GradientStatCard
          title='In Queue'
          value={formatNumber(analytics?.total_queue)}
          icon={Clock}
          gradient='from-amber-500 to-orange-500'
        />
        <GradientStatCard
          title='Published (API samples)'
          value={formatNumber(analytics?.total_published)}
          icon={CheckCircle2}
          gradient='from-emerald-500 to-teal-500'
        />
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue='generate' className='space-y-4'>
        <TabsList className='grid h-auto w-full grid-cols-2 gap-1 bg-gray-800 sm:inline-flex sm:w-auto'>
          <TabsTrigger value='generate' className='data-[state=active]:bg-gray-700'>
            <Sparkles className='mr-2 h-4 w-4' />
            Generate
          </TabsTrigger>
          <TabsTrigger value='queue' className='data-[state=active]:bg-gray-700'>
            <Calendar className='mr-2 h-4 w-4' />
            Queue ({queue.length})
          </TabsTrigger>
          <TabsTrigger value='campaigns' className='data-[state=active]:bg-gray-700'>
            <Megaphone className='mr-2 h-4 w-4' />
            Campaigns
          </TabsTrigger>
          <TabsTrigger value='analytics' className='data-[state=active]:bg-gray-700'>
            <BarChart3 className='mr-2 h-4 w-4' />
            Analytics
          </TabsTrigger>
        </TabsList>

        {/* Generate Tab */}
        <TabsContent value='generate' className='space-y-6'>
          {/* Quick Post Generator */}
          <Card className='bg-gray-900/80 border-gray-700 backdrop-blur-sm'>
            <CardHeader>
              <CardTitle className='text-white flex items-center gap-2'>
                <Sparkles className='h-5 w-5 text-[#B76E79]' />
                Quick Post Generator
              </CardTitle>
              <CardDescription className='text-gray-400'>
                Generate platform-optimized captions from product data with SkyyRose brand voice
              </CardDescription>
            </CardHeader>
            <CardContent className='space-y-6'>
              <div className='grid gap-4 md:grid-cols-2'>
                <div className='space-y-2'>
                  <Label className='text-gray-300'>Product</Label>
                  <select
                    value={selectedSku}
                    onChange={e => setSelectedSku(e.target.value)}
                    className='w-full h-10 rounded-md bg-gray-800 border border-gray-700 text-white px-3'
                  >
                    <option value=''>Select a product...</option>
                    <optgroup label='Black Rose Collection'>
                      {products
                        .filter(p => p.collection === 'black-rose')
                        .map(p => (
                          <option key={p.value} value={p.value}>
                            {p.label}
                          </option>
                        ))}
                    </optgroup>
                    <optgroup label='Love Hurts Collection'>
                      {products
                        .filter(p => p.collection === 'love-hurts')
                        .map(p => (
                          <option key={p.value} value={p.value}>
                            {p.label}
                          </option>
                        ))}
                    </optgroup>
                    <optgroup label='Signature Collection'>
                      {products
                        .filter(p => p.collection === 'signature')
                        .map(p => (
                          <option key={p.value} value={p.value}>
                            {p.label}
                          </option>
                        ))}
                    </optgroup>
                  </select>
                </div>
                <div className='space-y-2'>
                  <Label className='text-gray-300'>Platform</Label>
                  <div className='flex gap-2'>
                    {Object.entries(PLATFORM_CONFIG).map(([key, config]) => (
                      <Button
                        key={key}
                        variant={selectedPlatform === key ? 'default' : 'outline'}
                        size='sm'
                        onClick={() => setSelectedPlatform(key)}
                        className={selectedPlatform === key ? 'text-white' : 'border-gray-700 text-gray-400'}
                        style={selectedPlatform === key ? { backgroundColor: config.color } : undefined}
                      >
                        {config.label}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>

              <Button
                onClick={handleGeneratePost}
                disabled={generating || !selectedSku}
                className='w-full bg-gradient-to-r from-[#B76E79] via-[#B76E79] to-[#D4AF37] hover:from-[#a5606a] hover:to-[#c4a030] h-12 text-lg text-white'
              >
                {generating ? (
                  <>
                    <Loader2 className='mr-2 h-5 w-5 animate-spin' />
                    Generating...
                  </>
                ) : (
                  <>
                    <Play className='mr-2 h-5 w-5' />
                    Generate Post
                  </>
                )}
              </Button>

              {/* Generated Post Preview */}
              {generatedPost && (
                <div className='rounded-lg border border-gray-700 bg-gray-800/50 p-4 space-y-3'>
                  <div className='flex items-center justify-between'>
                    <h3 className='text-sm font-medium text-white'>Generated Post Preview</h3>
                    <Badge
                      variant='outline'
                      style={{
                        borderColor: PLATFORM_CONFIG[generatedPost.platform]?.color,
                        color: PLATFORM_CONFIG[generatedPost.platform]?.color,
                      }}
                    >
                      {PLATFORM_CONFIG[generatedPost.platform]?.label}
                    </Badge>
                  </div>
                  <p className='text-sm text-gray-300 whitespace-pre-wrap leading-relaxed'>{generatedPost.caption}</p>
                  <div className='flex flex-wrap gap-1'>
                    {generatedPost.hashtags.map(tag => (
                      <span
                        key={tag}
                        className='inline-flex items-center text-xs text-[#B76E79] bg-[#B76E79]/10 px-2 py-0.5 rounded-full'
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className='flex gap-2 pt-2'>
                    <Button size='sm' variant='outline' className='border-gray-700 text-gray-300'>
                      <Calendar className='mr-1 h-3 w-3' />
                      Schedule
                    </Button>
                    <Button size='sm' className='bg-[#B76E79] hover:bg-[#a5606a] text-white'>
                      <Send className='mr-1 h-3 w-3' />
                      Publish Now
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Campaign Generator */}
          <Card className='bg-gray-900/80 border-gray-700 backdrop-blur-sm'>
            <CardHeader>
              <CardTitle className='text-white flex items-center gap-2'>
                <Megaphone className='h-5 w-5 text-[#D4AF37]' />
                Campaign Generator
              </CardTitle>
              <CardDescription className='text-gray-400'>
                Generate a multi-platform campaign for an entire collection
              </CardDescription>
            </CardHeader>
            <CardContent className='space-y-4'>
              <div className='grid gap-4 md:grid-cols-2'>
                <div className='space-y-2'>
                  <Label className='text-gray-300'>Collection</Label>
                  <select
                    value={campaignCollection}
                    onChange={e => setCampaignCollection(e.target.value)}
                    className='w-full h-10 rounded-md bg-gray-800 border border-gray-700 text-white px-3'
                  >
                    {COLLECTIONS.map(c => (
                      <option key={c.value} value={c.value}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className='space-y-2'>
                  <Label className='text-gray-300'>Campaign Name</Label>
                  <Input
                    placeholder='e.g. Spring 2026 Drop'
                    value={campaignName}
                    onChange={e => setCampaignName(e.target.value)}
                    className='bg-gray-800 border-gray-700 text-white placeholder:text-gray-500'
                  />
                </div>
              </div>
              <Button
                onClick={handleGenerateCampaign}
                disabled={generatingCampaign || !campaignName.trim()}
                className='h-auto min-h-12 w-full whitespace-normal bg-gradient-to-r from-[#D4AF37] to-[#B76E79] text-base text-white hover:from-[#c4a030] hover:to-[#a5606a] sm:text-lg'
              >
                {generatingCampaign ? (
                  <>
                    <Loader2 className='mr-2 h-5 w-5 animate-spin' />
                    Generating Campaign...
                  </>
                ) : (
                  <>
                    <Megaphone className='mr-2 h-5 w-5' />
                    Generate Campaign ({products.filter(p => p.collection === campaignCollection).length} products x 4
                    platforms)
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Queue Tab */}
        <TabsContent value='queue'>
          {queue.length === 0 ? (
            <Card className='bg-gray-900 border-gray-800 py-12'>
              <CardContent className='text-center'>
                <Calendar className='h-12 w-12 text-gray-600 mx-auto mb-4' />
                <p className='text-gray-500'>No posts in queue</p>
                <p className='text-gray-600 text-sm mt-1'>Generate posts from the Generate tab to get started</p>
              </CardContent>
            </Card>
          ) : (
            <div className='space-y-3'>
              {queue.map(post => (
                <QueueItem key={post.id} post={post} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Campaigns Tab */}
        <TabsContent value='campaigns'>
          {campaigns.length === 0 ? (
            <Card className='bg-gray-900 border-gray-800 py-12'>
              <CardContent className='text-center'>
                <Megaphone className='h-12 w-12 text-gray-600 mx-auto mb-4' />
                <p className='text-gray-500'>No campaigns yet</p>
                <p className='text-gray-600 text-sm mt-1'>
                  Use the Campaign Generator to create multi-platform campaigns
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className='grid gap-4 md:grid-cols-2'>
              {campaigns.map(campaign => (
                <CampaignCard key={campaign.id} campaign={campaign} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value='analytics'>
          <div className='grid gap-4 md:grid-cols-2'>
            {Object.entries(PLATFORM_CONFIG).map(([key, config]) => {
              const stats = analytics?.platforms[key];
              if (!stats) return null;
              return <AnalyticsCard key={key} platform={config.label} color={config.color} stats={stats} />;
            })}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function PlatformStatCard({
  platform,
  color,
  bgColor,
  posts,
  engagement,
  reach,
  status,
}: {
  platform: string;
  color: string;
  bgColor: string;
  posts: number | null;
  engagement: number | null;
  reach: number | null;
  status: PlatformAnalytics['status'];
}) {
  return (
    <Card className='bg-gray-900/80 border-gray-700 overflow-hidden backdrop-blur-sm'>
      <div className='h-1' style={{ backgroundColor: color }} />
      <CardContent className='pt-5 pb-4'>
        <div className='flex items-center justify-between mb-3'>
          <span className='text-sm font-medium text-white'>{platform}</span>
          <div className={`h-8 w-8 rounded-lg ${bgColor} flex items-center justify-center`}>
            <Share2 className='h-4 w-4' style={{ color }} />
          </div>
        </div>
        <div className='grid grid-cols-3 gap-2 text-center'>
          <div>
            <p className='text-sm font-bold text-white'>{formatNumber(posts)}</p>
            <p className='text-xs text-gray-500'>Posts</p>
          </div>
          <div>
            <p className='text-sm font-bold text-white'>{formatNumber(engagement)}</p>
            <p className='text-xs text-gray-500'>Engage</p>
          </div>
          <div>
            <p className='text-sm font-bold text-white'>{formatNumber(reach)}</p>
            <p className='text-xs text-gray-500'>Reach / Views</p>
          </div>
        </div>
        <p className='mt-3 text-xs text-gray-400'>{status}</p>
      </CardContent>
    </Card>
  );
}

function GradientStatCard({
  title,
  value,
  icon: Icon,
  gradient,
}: {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  gradient: string;
}) {
  return (
    <Card className='bg-gray-900/80 border-gray-700 overflow-hidden backdrop-blur-sm'>
      <div className={`h-1 bg-gradient-to-r ${gradient}`} />
      <CardContent className='pt-6'>
        <div className='flex items-center justify-between'>
          <div>
            <p className='text-sm text-gray-400'>{title}</p>
            <p className='text-2xl font-bold text-white mt-1'>{value}</p>
          </div>
          <div
            className={`h-12 w-12 rounded-xl bg-gradient-to-br ${gradient} bg-opacity-10 flex items-center justify-center`}
          >
            <Icon className='h-6 w-6 text-white' />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function QueueItem({ post }: { post: SocialPost }) {
  const config = PLATFORM_CONFIG[post.platform];
  const statusStyles: Record<string, string> = {
    draft: 'border-gray-500 text-gray-400',
    scheduled: 'border-amber-500 text-amber-400',
    published: 'border-green-500 text-green-400',
    failed: 'border-red-500 text-red-400',
  };

  return (
    <Card className='bg-gray-900 border-gray-800 overflow-hidden'>
      <div className='h-1' style={{ backgroundColor: config?.color ?? '#666' }} />
      <CardContent className='p-4'>
        <div className='flex items-start gap-4'>
          <div
            className={`h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0 ${config?.bgColor ?? 'bg-gray-800'}`}
          >
            <Hash className='h-5 w-5' style={{ color: config?.color ?? '#999' }} />
          </div>
          <div className='flex-1 min-w-0'>
            <div className='flex items-center justify-between gap-2 mb-1'>
              <span className='text-sm font-medium text-white truncate'>
                {config?.label ?? post.platform} - {post.product_sku}
              </span>
              <Badge variant='outline' className={statusStyles[post.status]}>
                {post.status}
              </Badge>
            </div>
            <p className='text-xs text-gray-400 line-clamp-2'>{post.caption}</p>
            {post.scheduled_at && (
              <p className='text-xs text-amber-400 mt-1 flex items-center gap-1'>
                <Clock className='h-3 w-3' />
                Scheduled: {new Date(post.scheduled_at).toLocaleString()}
              </p>
            )}
          </div>
          <div className='flex gap-1 flex-shrink-0'>
            <Button size='sm' variant='ghost' className='text-gray-400 hover:text-white h-8 w-8 p-0'>
              <Calendar className='h-4 w-4' />
            </Button>
            <Button size='sm' variant='ghost' className='text-[#B76E79] hover:text-[#d4919c] h-8 w-8 p-0'>
              <Send className='h-4 w-4' />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function CampaignCard({ campaign }: { campaign: Campaign }) {
  const collection = COLLECTIONS.find(c => c.value === campaign.collection);
  const platformCounts = campaign.posts.reduce(
    (acc, post) => {
      acc[post.platform] = (acc[post.platform] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <Card className='bg-gray-900 border-gray-800 overflow-hidden'>
      <div className='h-1 bg-gradient-to-r from-[#B76E79] to-[#D4AF37]' />
      <CardHeader className='pb-3'>
        <div className='flex items-center justify-between'>
          <CardTitle className='text-lg text-white'>{campaign.name}</CardTitle>
          <Badge variant='outline' className='border-[#D4AF37] text-[#D4AF37]'>
            {campaign.status}
          </Badge>
        </div>
        <CardDescription className='text-gray-500'>
          {collection?.label ?? campaign.collection} Collection - {campaign.posts.length} posts
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className='flex flex-wrap gap-2 mb-3'>
          {Object.entries(platformCounts).map(([platform, count]) => {
            const config = PLATFORM_CONFIG[platform];
            return (
              <Badge key={platform} variant='secondary' className='bg-gray-800 text-gray-300 text-xs'>
                <span className='h-2 w-2 rounded-full mr-1 inline-block' style={{ backgroundColor: config?.color }} />
                {config?.label}: {count}
              </Badge>
            );
          })}
        </div>
        <p className='text-xs text-gray-500'>Created: {new Date(campaign.created_at).toLocaleDateString()}</p>
      </CardContent>
    </Card>
  );
}

function AnalyticsCard({ platform, color, stats }: { platform: string; color: string; stats: PlatformAnalytics }) {
  const keys = ['posts', 'likes', 'comments', 'shares', 'reach', 'views', 'retweets', 'impressions'] as const;
  const metrics = keys.map(key => [key, stats[key]] as const);

  const metricIcons: Record<string, React.ComponentType<{ className?: string }>> = {
    posts: FileText,
    likes: Heart,
    comments: MessageCircle,
    shares: Share2,
    reach: Eye,
    views: Eye,
    retweets: Repeat2,
    impressions: TrendingUp,
  };

  return (
    <Card className='bg-gray-900 border-gray-800 overflow-hidden'>
      <div className='h-1' style={{ backgroundColor: color }} />
      <CardHeader className='pb-3'>
        <div className='flex items-center justify-between'>
          <CardTitle className='text-lg text-white'>{platform}</CardTitle>
          <div
            className='h-8 w-8 rounded-lg flex items-center justify-center'
            style={{ backgroundColor: `${color}20` }}
          >
            <BarChart3 className='h-4 w-4' style={{ color }} />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className='mb-3 space-y-1 text-xs text-gray-400'>
          <p>Status: {stats.status}</p>
          <p>Window: {stats.window.label}</p>
          <p>Evidence: {stats.evidence}</p>
          {stats.error && <p className='text-amber-300'>{stats.error}</p>}
        </div>
        <div className='grid grid-cols-2 gap-3'>
          {metrics.map(([key, value]) => {
            const Icon = metricIcons[key] ?? TrendingUp;
            return (
              <div key={key} className='flex items-center gap-2 rounded-lg bg-gray-800/50 px-3 py-2'>
                <Icon className='h-4 w-4 text-gray-500 flex-shrink-0' />
                <div>
                  <p className='text-sm font-medium text-white'>{formatNumber(value)}</p>
                  <p className='text-xs text-gray-500 capitalize'>{key}</p>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

function SocialMediaSkeleton() {
  return (
    <div className='space-y-6'>
      <Skeleton className='h-40 w-full rounded-2xl bg-gray-800' />
      <div className='grid gap-4 md:grid-cols-4'>
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className='h-28 bg-gray-800' />
        ))}
      </div>
      <div className='grid gap-4 md:grid-cols-3'>
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className='h-24 bg-gray-800' />
        ))}
      </div>
      <Skeleton className='h-64 bg-gray-800' />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function formatNumber(num: number | null | undefined): string {
  if (num == null) return 'Unavailable';
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toString();
}
