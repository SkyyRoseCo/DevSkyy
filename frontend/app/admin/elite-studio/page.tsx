'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Image,
  Box,
  Share2,
  Pencil,
  Users,
  ArrowRight,
  Activity,
  TrendingUp,
  Layers,
} from 'lucide-react';
import { eliteStudioClient } from '@/lib/elite-studio-client';
import { OperationCard } from '@/components/elite-studio/OperationCard';
import { UsageMeter } from '@/components/elite-studio/UsageMeter';
import { StatsCard } from '@/components/dashboard';
import { ErrorState } from '@/components/shared';

// ---------------------------------------------------------------------------
// Quick action definitions
// ---------------------------------------------------------------------------

const QUICK_ACTIONS = [
  {
    title: 'Create Render',
    description: 'Generate a product render from a SKU',
    href: '/admin/elite-studio/operations?intent=render',
    icon: Image,
    gradient: 'from-[#B76E79] to-[#D4AF37]',
    border: 'border-[#B76E79]/30',
  },
  {
    title: 'Create 3D Model',
    description: 'Generate a 3D model for any product',
    href: '/admin/elite-studio/operations?intent=3d-model',
    icon: Box,
    gradient: 'from-[#D4AF37] to-amber-600',
    border: 'border-[#D4AF37]/30',
  },
  {
    title: 'Social Pack',
    description: 'Create a full social media asset pack',
    href: '/admin/elite-studio/operations?intent=social-pack',
    icon: Share2,
    gradient: 'from-blue-500 to-indigo-600',
    border: 'border-blue-500/30',
  },
  {
    title: 'Design Ideation',
    description: 'AI-assisted design concept generation',
    href: '/admin/elite-studio/design',
    icon: Pencil,
    gradient: 'from-purple-500 to-violet-600',
    border: 'border-purple-500/30',
  },
  {
    title: 'View Characters',
    description: 'Browse and manage brand characters',
    href: '/admin/elite-studio/characters',
    icon: Users,
    gradient: 'from-[#DC143C] to-rose-700',
    border: 'border-[#DC143C]/30',
  },
] as const;

// ---------------------------------------------------------------------------
// Variants
// ---------------------------------------------------------------------------

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
};
const itemVariants = {
  hidden: { y: 16, opacity: 0 },
  visible: { y: 0, opacity: 1 },
};

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function EliteStudioPage() {
  const {
    data: operationData,
    isLoading: opsLoading,
    error: opsError,
    refetch: refetchOps,
  } = useQuery({
    queryKey: ['elite-studio', 'operations', 'recent'],
    queryFn: () => eliteStudioClient.listOperations({ limit: 10 }),
    refetchInterval: 15_000,
    retry: 1,
  });

  const {
    data: runningData,
    isLoading: runningLoading,
  } = useQuery({
    queryKey: ['elite-studio', 'operations', 'running'],
    queryFn: () => eliteStudioClient.listOperations({ status: 'running', limit: 5 }),
    refetchInterval: 5_000,
    retry: 1,
  });

  const allOps = operationData?.operations ?? [];
  const runningOps = runningData?.operations ?? [];
  const completedOps = allOps.filter((o) => o.status === 'completed').slice(0, 5);

  // Derived stats for this month (from returned data)
  const rendersThisMonth = allOps.filter((o) => o.intent === 'render' || o.intent === 'product-render').length;
  const models3dThisMonth = allOps.filter((o) => o.intent === '3d-model').length;
  const socialPacksThisMonth = allOps.filter((o) => o.intent === 'social-pack').length;
  const totalCost = allOps.reduce((sum, o) => sum + o.cost_usd, 0);

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-8"
    >
      {/* Header */}
      <motion.header variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
            Elite <span className="bg-gradient-to-r from-[#B76E79] to-[#D4AF37] bg-clip-text text-transparent">Studio</span>
          </h1>
        </div>
        <Badge variant="outline" className="border-[#B76E79]/50 bg-[#B76E79]/5 text-[#B76E79] backdrop-blur-sm px-4 py-1">
          <Activity className="h-3 w-3 mr-2 animate-pulse" aria-hidden="true" />
          AI Creative Engine
        </Badge>
      </motion.header>

      {/* Stats */}
      <motion.section variants={itemVariants} aria-label="Elite Studio Statistics">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Renders"
            value={rendersThisMonth}
            description="Product renders this month"
            icon={Image}
            trend="AI-generated"
            trendDirection="up"
          />
          <StatsCard
            title="3D Models"
            value={models3dThisMonth}
            description="3D models generated"
            icon={Box}
            trend="Luxury quality"
            trendDirection="up"
          />
          <StatsCard
            title="Social Packs"
            value={socialPacksThisMonth}
            description="Multi-platform asset packs"
            icon={Share2}
            trend="Ready to post"
            trendDirection="up"
          />
          <StatsCard
            title="Total Cost"
            value={`$${totalCost.toFixed(2)}`}
            description="API spend this period"
            icon={TrendingUp}
            trend="Across all operations"
            trendDirection="neutral"
          />
        </div>
      </motion.section>

      {/* Quick Actions + Usage */}
      <motion.section variants={itemVariants} aria-label="Quick Actions">
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Quick action cards (2/3 width) */}
          <div className="lg:col-span-2">
            <Card className="bg-gray-900 border-gray-800 h-full">
              <CardHeader>
                <CardTitle className="text-white">Quick Actions</CardTitle>
                <CardDescription className="text-gray-400">
                  Launch a new creative operation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {QUICK_ACTIONS.map((action) => {
                    const Icon = action.icon;
                    return (
                      <Link key={action.href} href={action.href}>
                        <motion.div
                          whileHover={{ y: -3, transition: { duration: 0.15 } }}
                          className={`group rounded-xl border ${action.border} bg-gray-800/50 p-4 cursor-pointer transition-colors hover:bg-gray-800`}
                        >
                          <div
                            className={`mb-3 inline-flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br ${action.gradient}`}
                          >
                            <Icon className="h-4 w-4 text-white" aria-hidden="true" />
                          </div>
                          <h3 className="text-sm font-semibold text-white group-hover:text-[#B76E79] transition-colors">
                            {action.title}
                          </h3>
                          <p className="mt-1 text-xs text-gray-500">{action.description}</p>
                        </motion.div>
                      </Link>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Usage meter (1/3 width) */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="text-white">Monthly Usage</CardTitle>
              <CardDescription className="text-gray-400">Quota utilization</CardDescription>
            </CardHeader>
            <CardContent>
              <UsageMeter />
            </CardContent>
          </Card>
        </div>
      </motion.section>

      {/* Active Jobs */}
      <motion.section variants={itemVariants} aria-label="Active Jobs">
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-white flex items-center gap-2">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-blue-500" />
                </span>
                Active Jobs
              </CardTitle>
              <CardDescription className="text-gray-400">
                Operations currently in progress
              </CardDescription>
            </div>
            <Link href="/admin/elite-studio/operations?status=running">
              <Button variant="ghost" size="sm" className="text-[#B76E79] hover:text-[#D4AF37]">
                View All <ArrowRight className="ml-1 h-4 w-4" aria-hidden="true" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {runningLoading ? (
              <div className="space-y-3">
                {[0, 1, 2].map((i) => (
                  <Skeleton key={i} className="h-20 w-full bg-gray-800" />
                ))}
              </div>
            ) : runningOps.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <Layers className="h-10 w-10 text-gray-700 mb-3" aria-hidden="true" />
                <p className="text-gray-400 font-medium">No active jobs</p>
                <p className="text-gray-600 text-sm mt-1">
                  Launch a quick action above to get started
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {runningOps.map((op) => (
                  <OperationCard key={op.operation_id} operation={op} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.section>

      {/* Recent Results */}
      <motion.section variants={itemVariants} aria-label="Recent Results">
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-white">Recent Results</CardTitle>
              <CardDescription className="text-gray-400">
                Last 5 completed operations
              </CardDescription>
            </div>
            <Link href="/admin/elite-studio/operations?status=completed">
              <Button variant="ghost" size="sm" className="text-[#B76E79] hover:text-[#D4AF37]">
                View All <ArrowRight className="ml-1 h-4 w-4" aria-hidden="true" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {opsLoading ? (
              <div className="space-y-3">
                {[0, 1, 2].map((i) => (
                  <Skeleton key={i} className="h-20 w-full bg-gray-800" />
                ))}
              </div>
            ) : opsError ? (
              <ErrorState
                title="Failed to load operations"
                message="Could not reach the Elite Studio API."
                onRetry={refetchOps}
              />
            ) : completedOps.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <Activity className="h-10 w-10 text-gray-700 mb-3" aria-hidden="true" />
                <p className="text-gray-400 font-medium">No completed operations yet</p>
                <p className="text-gray-600 text-sm mt-1">
                  Results will appear here once operations finish
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {completedOps.map((op) => (
                  <OperationCard key={op.operation_id} operation={op} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.section>
    </motion.div>
  );
}
