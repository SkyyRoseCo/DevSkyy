'use client';

import { Suspense, useState } from 'react';
import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import {
  ArrowLeft,
  DollarSign,
  Calendar,
  Clock,
  Code2,
  ChevronDown,
  ChevronUp,
  Image,
  FileJson,
  AlertCircle,
} from 'lucide-react';
import { eliteStudioClient } from '@/lib/elite-studio-client';
import { OperationStatusBadge } from '@/components/elite-studio/OperationStatusBadge';
import { IntentBadge } from '@/components/elite-studio/IntentBadge';
import { StageProgress } from '@/components/elite-studio/StageProgress';
import { ErrorState } from '@/components/shared';
import { formatDistanceToNow, format } from 'date-fns';

interface Props {
  params: Promise<{ id: string }>;
}

function ResultPanel({ intent, result }: { intent: string; result: Record<string, unknown> }) {
  // Render result based on intent type
  const imageIntents = new Set(['render', 'product-render', 'mockup', 'virtual-tryon', 'social-pack']);

  if (imageIntents.has(intent)) {
    const imageUrl = (result['image_url'] ?? result['output_url'] ?? result['url']) as string | undefined;
    if (imageUrl) {
      return (
        <div className='space-y-3'>
          <div className='relative overflow-hidden rounded-xl border border-gray-700 bg-gray-800'>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={imageUrl} alt={`Result for ${intent} operation`} className='w-full object-contain max-h-96' />
          </div>
          <a
            href={imageUrl}
            target='_blank'
            rel='noreferrer'
            className='inline-flex items-center gap-1.5 text-sm text-[#B76E79] hover:text-[#D4AF37] transition-colors'
          >
            <Image className='h-4 w-4' aria-hidden='true' />
            Open full image
          </a>
        </div>
      );
    }
  }

  if (intent === 'design-ideation') {
    const concept = result as Record<string, unknown>;
    const conceptName = typeof concept['concept_name'] === 'string' ? concept['concept_name'] : null;
    const description = typeof concept['description'] === 'string' ? concept['description'] : null;
    const techNotes = typeof concept['tech_notes'] === 'string' ? concept['tech_notes'] : null;
    const colorways = Array.isArray(concept['colorways'])
      ? (concept['colorways'] as unknown[]).filter((c): c is string => typeof c === 'string')
      : [];
    return (
      <div className='space-y-4'>
        {conceptName && (
          <div>
            <p className='text-xs text-gray-500 uppercase tracking-wide mb-1'>Concept Name</p>
            <p className='text-lg font-semibold text-white'>{conceptName}</p>
          </div>
        )}
        {description && (
          <div>
            <p className='text-xs text-gray-500 uppercase tracking-wide mb-1'>Description</p>
            <p className='text-gray-300 leading-relaxed'>{description}</p>
          </div>
        )}
        {colorways.length > 0 && (
          <div>
            <p className='text-xs text-gray-500 uppercase tracking-wide mb-2'>Colorways</p>
            <div className='flex flex-wrap gap-2'>
              {colorways.map(c => (
                <Badge key={c} variant='outline' className='border-gray-600 text-gray-300 text-xs'>
                  {c}
                </Badge>
              ))}
            </div>
          </div>
        )}
        {techNotes && (
          <div>
            <p className='text-xs text-gray-500 uppercase tracking-wide mb-1'>Technical Notes</p>
            <p className='text-gray-400 text-sm leading-relaxed'>{techNotes}</p>
          </div>
        )}
      </div>
    );
  }

  // Fallback: JSON display
  return (
    <div className='rounded-lg bg-gray-800 border border-gray-700 p-4 overflow-auto max-h-96'>
      <pre className='text-xs text-gray-300 whitespace-pre-wrap break-words font-mono'>
        {JSON.stringify(result, null, 2)}
      </pre>
    </div>
  );
}

function OperationDetailSkeleton() {
  return (
    <div className='space-y-6'>
      <Skeleton className='h-10 w-48 bg-gray-800' />
      <Skeleton className='h-40 w-full bg-gray-800' />
      <Skeleton className='h-64 w-full bg-gray-800' />
    </div>
  );
}

export default function OperationDetailPage({ params }: Props) {
  return (
    <Suspense fallback={<OperationDetailSkeleton />}>
      <OperationDetailContent params={params} />
    </Suspense>
  );
}

function OperationDetailContent({ params }: Props) {
  const { id } = use(params);
  const [showRaw, setShowRaw] = useState(false);

  const {
    data: operation,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['elite-studio', 'operation', id],
    queryFn: () => eliteStudioClient.getOperation(id),
    refetchInterval: query => {
      const status = query.state.data?.status;
      return status === 'queued' || status === 'running' ? 3000 : false;
    },
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className='space-y-6'>
        <Skeleton className='h-10 w-48 bg-gray-800' />
        <Skeleton className='h-40 w-full bg-gray-800' />
        <Skeleton className='h-64 w-full bg-gray-800' />
      </div>
    );
  }

  if (error || !operation) {
    return (
      <ErrorState title='Operation not found' message={`Could not load operation ${id}.`} onRetry={refetch} fullPage />
    );
  }

  const createdAt = (() => {
    try {
      return format(new Date(operation.created_at), 'PPpp');
    } catch {
      return operation.created_at;
    }
  })();

  const createdAgo = (() => {
    try {
      return formatDistanceToNow(new Date(operation.created_at), { addSuffix: true });
    } catch {
      return '';
    }
  })();

  const totalMs = Object.values(operation.stage_timings).reduce((a, b) => a + b, 0);

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className='space-y-6'>
      {/* Back link */}
      <Link
        href='/admin/elite-studio/operations'
        className='inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors'
      >
        <ArrowLeft className='h-4 w-4' aria-hidden='true' />
        Back to Operations
      </Link>

      {/* Header */}
      <Card className='bg-gray-900 border-gray-800'>
        <CardHeader>
          <div className='flex flex-wrap items-start gap-3 justify-between'>
            <div className='space-y-2'>
              <div className='flex flex-wrap items-center gap-2'>
                <IntentBadge intent={operation.intent} />
                <OperationStatusBadge status={operation.status} />
              </div>
              <h1 className='text-2xl font-bold text-white font-mono'>{operation.sku}</h1>
              <p className='text-xs text-gray-500 font-mono'>{operation.operation_id}</p>
            </div>
            <div className='flex flex-col items-end gap-1 text-sm text-gray-400'>
              <span className='flex items-center gap-1.5'>
                <Calendar className='h-3.5 w-3.5' aria-hidden='true' />
                {createdAt}
              </span>
              <span className='text-gray-600 text-xs'>{createdAgo}</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className='grid grid-cols-2 sm:grid-cols-4 gap-4'>
            <div className='rounded-lg bg-gray-800 p-3'>
              <p className='text-xs text-gray-500 mb-1'>Status</p>
              <OperationStatusBadge status={operation.status} />
            </div>
            <div className='rounded-lg bg-gray-800 p-3'>
              <p className='text-xs text-gray-500 mb-1 flex items-center gap-1'>
                <DollarSign className='h-3 w-3' aria-hidden='true' />
                Cost
              </p>
              <p className='text-sm font-mono text-white'>${operation.cost_usd.toFixed(4)}</p>
            </div>
            <div className='rounded-lg bg-gray-800 p-3'>
              <p className='text-xs text-gray-500 mb-1 flex items-center gap-1'>
                <Clock className='h-3 w-3' aria-hidden='true' />
                Duration
              </p>
              <p className='text-sm font-mono text-white'>
                {totalMs < 1000 ? `${Math.round(totalMs)}ms` : `${(totalMs / 1000).toFixed(1)}s`}
              </p>
            </div>
            <div className='rounded-lg bg-gray-800 p-3'>
              <p className='text-xs text-gray-500 mb-1'>Stages</p>
              <p className='text-sm font-mono text-white'>{Object.keys(operation.stage_timings).length}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stage progress */}
      <Card className='bg-gray-900 border-gray-800'>
        <CardHeader>
          <CardTitle className='text-white text-base'>Pipeline Stages</CardTitle>
          <CardDescription className='text-gray-400'>
            Time spent in each stage of the Elite Studio compositor
          </CardDescription>
        </CardHeader>
        <CardContent>
          <StageProgress stageTimings={operation.stage_timings} status={operation.status} />
        </CardContent>
      </Card>

      {/* Error panel (for failed operations) */}
      {operation.status === 'failed' && operation.error && (
        <Card className='bg-red-950/20 border-red-800/40'>
          <CardHeader>
            <CardTitle className='text-red-400 flex items-center gap-2 text-base'>
              <AlertCircle className='h-4 w-4' aria-hidden='true' />
              Error Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className='text-red-300 text-sm leading-relaxed'>{operation.error}</p>
          </CardContent>
        </Card>
      )}

      {/* Result panel */}
      {operation.result && Object.keys(operation.result).length > 0 && (
        <Card className='bg-gray-900 border-gray-800'>
          <CardHeader>
            <div className='flex items-center justify-between'>
              <div>
                <CardTitle className='text-white text-base flex items-center gap-2'>
                  <FileJson className='h-4 w-4 text-[#B76E79]' aria-hidden='true' />
                  Result
                </CardTitle>
                <CardDescription className='text-gray-400'>
                  Output from the {operation.intent} operation
                </CardDescription>
              </div>
              <Button
                variant='ghost'
                size='sm'
                onClick={() => setShowRaw(v => !v)}
                className='text-gray-400 hover:text-white gap-1.5'
                aria-expanded={showRaw}
                aria-label={showRaw ? 'Hide raw JSON' : 'Show raw JSON'}
              >
                <Code2 className='h-3.5 w-3.5' aria-hidden='true' />
                {showRaw ? 'Hide' : 'Raw JSON'}
                {showRaw ? (
                  <ChevronUp className='h-3.5 w-3.5' aria-hidden='true' />
                ) : (
                  <ChevronDown className='h-3.5 w-3.5' aria-hidden='true' />
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {showRaw ? (
              <div className='rounded-lg bg-gray-800 border border-gray-700 p-4 overflow-auto max-h-96'>
                <pre className='text-xs text-gray-300 whitespace-pre-wrap break-words font-mono'>
                  {JSON.stringify(operation.result, null, 2)}
                </pre>
              </div>
            ) : (
              <ResultPanel intent={operation.intent} result={operation.result} />
            )}
          </CardContent>
        </Card>
      )}

      {/* Cost breakdown */}
      <Card className='bg-gray-900 border-gray-800'>
        <CardHeader>
          <CardTitle className='text-white text-base'>Cost Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className='space-y-2'>
            {Object.entries(operation.stage_timings).map(([stage, ms]) => {
              // Estimate per-stage cost proportional to time
              const stageCost = totalMs > 0 ? (ms / totalMs) * operation.cost_usd : 0;
              return (
                <div key={stage} className='flex items-center justify-between text-sm'>
                  <span className='text-gray-400 capitalize'>{stage.replace(/_/g, ' ')}</span>
                  <span className='font-mono text-gray-300'>${stageCost.toFixed(5)}</span>
                </div>
              );
            })}
            <div className='border-t border-gray-700 pt-2 flex items-center justify-between text-sm font-semibold'>
              <span className='text-white'>Total</span>
              <span className='font-mono text-[#B76E79]'>${operation.cost_usd.toFixed(4)}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
