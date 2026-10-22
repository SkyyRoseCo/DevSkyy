'use client';

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight, DollarSign, Clock } from 'lucide-react';
import { motion } from 'motion/react';
import { OperationStatusBadge } from './OperationStatusBadge';
import { IntentBadge } from './IntentBadge';
import type { CreativeOperation } from '@/lib/elite-studio-client';
import { formatDistanceToNow } from 'date-fns';

interface OperationCardProps {
  operation: CreativeOperation;
  className?: string;
}

export function OperationCard({ operation, className = '' }: OperationCardProps) {
  const createdAgo = (() => {
    try {
      return formatDistanceToNow(new Date(operation.created_at), { addSuffix: true });
    } catch {
      return operation.created_at;
    }
  })();

  const totalStageMs = Object.values(operation.stage_timings).reduce((a, b) => a + b, 0);
  const durationLabel =
    totalStageMs > 0
      ? totalStageMs < 1000
        ? `${Math.round(totalStageMs)}ms`
        : `${(totalStageMs / 1000).toFixed(1)}s`
      : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2, transition: { duration: 0.15 } }}
      className={className}
    >
      <Card className='bg-gray-900 border-gray-800 hover:border-[#B76E79]/40 transition-colors'>
        <CardContent className='p-4'>
          <div className='flex items-start justify-between gap-3'>
            <div className='flex-1 min-w-0 space-y-2'>
              <div className='flex flex-wrap items-center gap-2'>
                <IntentBadge intent={operation.intent} />
                <OperationStatusBadge status={operation.status} />
              </div>

              <div className='flex items-center gap-2'>
                <span className='text-sm font-mono text-gray-300 truncate'>{operation.sku}</span>
                <span className='text-gray-600 text-xs'>·</span>
                <span className='text-xs text-gray-500 truncate' title={operation.operation_id}>
                  {operation.operation_id.slice(0, 8)}…
                </span>
              </div>

              {operation.status === 'failed' && operation.error && (
                <p className='text-xs text-red-400 line-clamp-2'>{operation.error}</p>
              )}

              <div className='flex items-center gap-4 text-xs text-gray-500'>
                <span className='flex items-center gap-1'>
                  <Clock className='h-3 w-3' aria-hidden='true' />
                  {createdAgo}
                </span>
                {durationLabel && (
                  <span className='flex items-center gap-1'>
                    <span>Duration: {durationLabel}</span>
                  </span>
                )}
                <span className='flex items-center gap-1'>
                  <DollarSign className='h-3 w-3' aria-hidden='true' />
                  {operation.cost_usd.toFixed(4)}
                </span>
              </div>
            </div>

            <Link
              href={`/admin/elite-studio/operations/${operation.operation_id}`}
              aria-label={`View operation ${operation.operation_id}`}
            >
              <Button variant='ghost' size='sm' className='text-gray-400 hover:text-[#B76E79] shrink-0'>
                <ArrowRight className='h-4 w-4' aria-hidden='true' />
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
