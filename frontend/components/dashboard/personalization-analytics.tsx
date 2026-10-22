'use client';

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'motion/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Users,
  Sparkles,
  Eye,
  ShoppingCart,
  TrendingUp,
  Target,
  Layers,
  Zap,
  MousePointerClick,
  Heart,
} from 'lucide-react';
import { getCollection } from '@/lib/collections';

// ─── Brand ───────────────────────────────────────────────────────────────────

const BRAND = {
  roseGold: '#B76E79',
  gold: '#D4AF37',
} as const;

// ─── Types ────────────────────────────────────────────────────────────────────

interface IntentSegment {
  label: string;
  count: number;
  percentage: number;
  color: string;
  description: string;
}

interface PersonalizationMetrics {
  drawerOpens: number;
  recommendationClicks: number;
  clickThroughRate: number;
  bundleSuggestions: number;
  bundleConversions: number;
  moodTransitions: number;
  recentlyViewedClicks: number;
  avgHeatScore: number;
}

interface FunnelStage {
  label: string;
  visitors: number;
  color: string;
}

interface TopProduct {
  sku: string;
  name: string;
  heatScore: number;
  collection: string;
}

// ─── Simulated Real-Time Data ─────────────────────────────────────────────────

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function generateMetrics(): PersonalizationMetrics {
  const drawerOpens = randomInt(85, 140);
  const recommendationClicks = randomInt(22, 48);
  return {
    drawerOpens,
    recommendationClicks,
    clickThroughRate: Math.round((recommendationClicks / drawerOpens) * 100),
    bundleSuggestions: randomInt(35, 65),
    bundleConversions: randomInt(8, 18),
    moodTransitions: randomInt(200, 380),
    recentlyViewedClicks: randomInt(45, 85),
    avgHeatScore: randomInt(12, 28),
  };
}

function generateIntentSegments(): IntentSegment[] {
  const browsing = randomInt(55, 72);
  const interested = randomInt(18, 30);
  const ready = 100 - browsing - interested;
  return [
    {
      label: 'Browsing',
      count: randomInt(180, 320),
      percentage: browsing,
      color: '#6B7280',
      description: 'Exploring collections',
    },
    {
      label: 'Interested',
      count: randomInt(45, 95),
      percentage: interested,
      color: BRAND.gold,
      description: 'Viewing 2+ products',
    },
    {
      label: 'Ready to Buy',
      count: randomInt(12, 35),
      percentage: ready,
      color: '#10B981',
      description: 'High heat score (30+)',
    },
  ];
}

function generateFunnel(): FunnelStage[] {
  return [
    { label: 'Page Views', visitors: randomInt(800, 1200), color: '#6B7280' },
    { label: 'Product Views', visitors: randomInt(350, 550), color: BRAND.roseGold },
    { label: 'Drawer Opens', visitors: randomInt(85, 160), color: BRAND.gold },
    { label: 'Add to Cart', visitors: randomInt(30, 65), color: '#F59E0B' },
    { label: 'Pre-Order', visitors: randomInt(10, 30), color: '#10B981' },
  ];
}

// SKUs tracked by this demo panel. Only the SKU is hardcoded — name and
// collection are resolved live from the catalog below so this never shows a
// stale product name (e.g. a since-renamed product). heatScore itself stays
// simulated: this panel has no real behavioral-tracking backend yet.
const TRACKED_SKUS = ['br-006', 'lh-004', 'br-004', 'sg-001', 'br-001', 'sg-009'];

function generateTopProducts(catalogLookup: Map<string, { name: string; collection: string }>): TopProduct[] {
  return TRACKED_SKUS.map(sku => {
    const entry = catalogLookup.get(sku);
    return {
      sku,
      name: entry?.name ?? sku,
      collection: entry?.collection ?? '',
      heatScore: randomInt(15, 95),
    };
  }).sort((a, b) => b.heatScore - a.heatScore);
}

// ─── Component ────────────────────────────────────────────────────────────────

export function PersonalizationAnalytics() {
  const { data: productsData } = useQuery({
    queryKey: ['products', 'personalization-tracked'],
    queryFn: async () => {
      const res = await fetch('/api/products');
      if (!res.ok) throw new Error('Failed to load products');
      const json = await res.json();
      return json.data.products as Array<{ sku: string; name: string; collection: string }>;
    },
    staleTime: 5 * 60 * 1000,
  });

  const catalogLookup = useMemo(() => {
    const map = new Map<string, { name: string; collection: string }>();
    for (const p of productsData ?? []) {
      const collectionName = getCollection(p.collection)?.name ?? p.collection;
      map.set(p.sku, { name: p.name, collection: collectionName });
    }
    return map;
  }, [productsData]);

  const [metrics, setMetrics] = useState<PersonalizationMetrics>(generateMetrics);
  const [segments, setSegments] = useState<IntentSegment[]>(generateIntentSegments);
  const [funnel, setFunnel] = useState<FunnelStage[]>(generateFunnel);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refreshData = useCallback(() => {
    setMetrics(generateMetrics());
    setSegments(generateIntentSegments());
    setFunnel(generateFunnel());
    setTopProducts(generateTopProducts(catalogLookup));
  }, [catalogLookup]);

  useEffect(() => {
    refreshData();
    intervalRef.current = setInterval(refreshData, 15000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [refreshData]);

  const maxFunnel = funnel[0]?.visitors ?? 1;

  return (
    <Card className='bg-gray-900 border-gray-800 overflow-hidden'>
      <div className='h-1 bg-gradient-to-r from-[#B76E79] via-[#D4AF37] to-[#B76E79]' />
      <CardHeader>
        <div className='flex items-center justify-between'>
          <div>
            <CardTitle className='text-white font-display text-2xl flex items-center gap-3'>
              <div className='h-10 w-10 rounded-xl bg-gradient-to-br from-[#B76E79] to-[#D4AF37] flex items-center justify-center'>
                <Sparkles className='h-5 w-5 text-white' />
              </div>
              Adaptive Personalization Engine
            </CardTitle>
            <CardDescription className='text-gray-400 mt-2'>
              Behavioral scoring, recommendations, and mood-driven conversions
            </CardDescription>
          </div>
          <Badge variant='outline' className='border-[#B76E79] text-[#B76E79]'>
            <div className='h-2 w-2 rounded-full bg-[#B76E79] animate-pulse mr-2' />
            Live
          </Badge>
        </div>
      </CardHeader>

      <CardContent className='space-y-8'>
        {/* Metrics Grid */}
        <div className='grid gap-4 md:grid-cols-4'>
          <MetricCard label='Drawer Opens' value={metrics.drawerOpens} icon={Layers} color={BRAND.roseGold} />
          <MetricCard
            label='Rec. CTR'
            value={`${metrics.clickThroughRate}%`}
            icon={MousePointerClick}
            color={BRAND.gold}
          />
          <MetricCard label='Bundle Converts' value={metrics.bundleConversions} icon={ShoppingCart} color='#10B981' />
          <MetricCard label='Avg Heat Score' value={metrics.avgHeatScore} icon={Zap} color='#F59E0B' />
        </div>

        {/* Two-Column Layout */}
        <div className='grid gap-8 lg:grid-cols-2'>
          {/* Intent Segmentation */}
          <div>
            <h3 className='text-sm font-semibold text-white mb-4 flex items-center gap-2'>
              <Target className='h-4 w-4 text-[#B76E79]' />
              Visitor Intent Segments
            </h3>
            <div className='space-y-4'>
              {segments.map(seg => (
                <div key={seg.label}>
                  <div className='flex items-center justify-between mb-1.5'>
                    <div className='flex items-center gap-2'>
                      <div className='h-2.5 w-2.5 rounded-full' style={{ backgroundColor: seg.color }} />
                      <span className='text-sm font-medium text-white'>{seg.label}</span>
                      <span className='text-xs text-gray-500'>{seg.description}</span>
                    </div>
                    <div className='flex items-center gap-3'>
                      <span className='text-sm text-gray-400'>{seg.count} visitors</span>
                      <span className='text-sm font-medium text-white tabular-nums'>{seg.percentage}%</span>
                    </div>
                  </div>
                  <div className='h-2 rounded-full bg-gray-800 overflow-hidden'>
                    <motion.div
                      className='h-full rounded-full'
                      style={{ backgroundColor: seg.color }}
                      initial={{ width: 0 }}
                      animate={{ width: `${seg.percentage}%` }}
                      transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Conversion Funnel */}
          <div>
            <h3 className='text-sm font-semibold text-white mb-4 flex items-center gap-2'>
              <TrendingUp className='h-4 w-4 text-[#D4AF37]' />
              Personalization Funnel
            </h3>
            <div className='space-y-3'>
              {funnel.map((stage, i) => {
                const width = Math.max(8, (stage.visitors / maxFunnel) * 100);
                const dropoff =
                  i > 0 ? Math.round(((funnel[i - 1].visitors - stage.visitors) / funnel[i - 1].visitors) * 100) : 0;

                return (
                  <div key={stage.label}>
                    <div className='flex items-center justify-between mb-1'>
                      <span className='text-xs font-medium text-gray-400'>{stage.label}</span>
                      <div className='flex items-center gap-2'>
                        <span className='text-sm font-bold text-white tabular-nums'>
                          {stage.visitors.toLocaleString()}
                        </span>
                        {i > 0 && <span className='text-xs text-red-400/70'>-{dropoff}%</span>}
                      </div>
                    </div>
                    <div className='h-6 rounded bg-gray-800/50 overflow-hidden'>
                      <motion.div
                        className='h-full rounded flex items-center justify-end pr-2'
                        style={{ backgroundColor: `${stage.color}40` }}
                        initial={{ width: 0 }}
                        animate={{ width: `${width}%` }}
                        transition={{
                          duration: 0.6,
                          delay: i * 0.1,
                          ease: [0.22, 1, 0.36, 1],
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Top Products by Heat Score */}
        <div>
          <h3 className='text-sm font-semibold text-white mb-4 flex items-center gap-2'>
            <Heart className='h-4 w-4 text-[#B76E79]' />
            Top Products by Behavioral Heat Score
          </h3>
          <div className='grid gap-3 md:grid-cols-2 lg:grid-cols-3'>
            {topProducts.map((product, i) => (
              <div
                key={product.sku}
                className='flex items-center gap-3 rounded-lg bg-gray-800/50 p-3 border border-gray-700/50'
              >
                <div className='flex h-8 w-8 items-center justify-center rounded-full bg-gray-800 text-sm font-bold text-gray-400 flex-shrink-0'>
                  {i + 1}
                </div>
                <div className='flex-1 min-w-0'>
                  <p className='text-sm font-medium text-white truncate'>{product.name}</p>
                  <p className='text-xs text-gray-500'>{product.collection}</p>
                </div>
                <div className='flex items-center gap-1 flex-shrink-0'>
                  <Zap className='h-3 w-3 text-[#D4AF37]' />
                  <span className='text-sm font-bold text-[#D4AF37] tabular-nums'>{product.heatScore}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Stats Row */}
        <div className='grid gap-3 md:grid-cols-4 pt-4 border-t border-gray-800'>
          <MiniStat label='Mood Transitions' value={metrics.moodTransitions} />
          <MiniStat label='Recently Viewed Clicks' value={metrics.recentlyViewedClicks} />
          <MiniStat label='Bundle Suggestions' value={metrics.bundleSuggestions} />
          <MiniStat label='Rec. Clicks' value={metrics.recommendationClicks} />
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function MetricCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}) {
  return (
    <div className='rounded-xl bg-gray-800/50 border border-gray-700/50 p-4'>
      <div className='flex items-center justify-between mb-2'>
        <span className='text-xs font-medium text-gray-400 uppercase tracking-wider'>{label}</span>
        <div className='h-8 w-8 rounded-lg flex items-center justify-center' style={{ backgroundColor: `${color}15` }}>
          <span style={{ color }}>
            <Icon className='h-4 w-4' />
          </span>
        </div>
      </div>
      <p className='text-2xl font-bold text-white tabular-nums'>{value}</p>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: number }) {
  return (
    <div className='text-center'>
      <p className='text-lg font-bold text-white tabular-nums'>{value}</p>
      <p className='text-xs text-gray-500'>{label}</p>
    </div>
  );
}
