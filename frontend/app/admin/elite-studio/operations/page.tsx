'use client';

import { Suspense, useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Activity, ChevronLeft, ChevronRight, Search, DollarSign } from 'lucide-react';
import Link from 'next/link';
import { eliteStudioClient, type CreativeOperation, type ListOperationsFilters } from '@/lib/elite-studio-client';
import { OperationStatusBadge } from '@/components/elite-studio/OperationStatusBadge';
import { IntentBadge } from '@/components/elite-studio/IntentBadge';
import { ErrorState } from '@/components/shared';
import { formatDistanceToNow } from 'date-fns';

const INTENTS = [
  'render',
  'product-render',
  '3d-model',
  'social-pack',
  'design-ideation',
  'mockup',
  'virtual-tryon',
] as const;

const STATUSES = ['queued', 'running', 'completed', 'failed'] as const;

const PAGE_SIZE = 20;

function formatAgo(dateStr: string): string {
  try {
    return formatDistanceToNow(new Date(dateStr), { addSuffix: true });
  } catch {
    return dateStr;
  }
}

function OperationsListSkeleton() {
  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-3xl font-bold text-white'>Operations</h1>
        <p className='text-gray-400 mt-1'>All Elite Studio creative operations</p>
      </div>
      <Card className='bg-gray-900 border-gray-800'>
        <CardContent className='p-6 space-y-3'>
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className='h-12 w-full bg-gray-800' />
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

export default function OperationsListPage() {
  return (
    <Suspense fallback={<OperationsListSkeleton />}>
      <OperationsListContent />
    </Suspense>
  );
}

function OperationsListContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>(searchParams.get('status') ?? 'all');
  const [intentFilter, setIntentFilter] = useState<string>(searchParams.get('intent') ?? 'all');
  const [skuSearch, setSkuSearch] = useState('');

  const filters: ListOperationsFilters = {
    page,
    limit: PAGE_SIZE,
    ...(statusFilter !== 'all' && { status: statusFilter as CreativeOperation['status'] }),
    ...(intentFilter !== 'all' && { intent: intentFilter }),
  };

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['elite-studio', 'operations', filters],
    queryFn: () => eliteStudioClient.listOperations(filters),
    refetchInterval: 10_000,
    retry: 1,
  });

  const handleStatusChange = useCallback((val: string) => {
    setStatusFilter(val);
    setPage(1);
  }, []);

  const handleIntentChange = useCallback((val: string) => {
    setIntentFilter(val);
    setPage(1);
  }, []);

  const operations = (data?.operations ?? []).filter(op =>
    skuSearch.trim() === '' ? true : op.sku.toLowerCase().includes(skuSearch.toLowerCase())
  );

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className='space-y-6'>
      {/* Header */}
      <div>
        <h1 className='text-3xl font-bold text-white'>Operations</h1>
        <p className='text-gray-400 mt-1'>All Elite Studio creative operations</p>
      </div>

      {/* Filters */}
      <Card className='bg-gray-900 border-gray-800'>
        <CardContent className='p-4'>
          <div className='flex flex-wrap gap-3 items-center'>
            {/* SKU search */}
            <div className='relative flex-1 min-w-48'>
              <Search className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500' aria-hidden='true' />
              <Input
                placeholder='Search by SKU...'
                value={skuSearch}
                onChange={e => setSkuSearch(e.target.value)}
                className='pl-9 bg-gray-800 border-gray-700 text-white placeholder:text-gray-500 focus-visible:ring-[#B76E79]'
                aria-label='Filter by SKU'
              />
            </div>

            {/* Status filter */}
            <Select value={statusFilter} onValueChange={handleStatusChange}>
              <SelectTrigger
                className='w-36 bg-gray-800 border-gray-700 text-gray-300 focus:ring-[#B76E79]'
                aria-label='Filter by status'
              >
                <SelectValue placeholder='Status' />
              </SelectTrigger>
              <SelectContent className='bg-gray-800 border-gray-700'>
                <SelectItem value='all' className='text-gray-300 focus:bg-gray-700'>
                  All Statuses
                </SelectItem>
                {STATUSES.map(s => (
                  <SelectItem key={s} value={s} className='text-gray-300 focus:bg-gray-700 capitalize'>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Intent filter */}
            <Select value={intentFilter} onValueChange={handleIntentChange}>
              <SelectTrigger
                className='w-44 bg-gray-800 border-gray-700 text-gray-300 focus:ring-[#B76E79]'
                aria-label='Filter by intent'
              >
                <SelectValue placeholder='Intent' />
              </SelectTrigger>
              <SelectContent className='bg-gray-800 border-gray-700'>
                <SelectItem value='all' className='text-gray-300 focus:bg-gray-700'>
                  All Intents
                </SelectItem>
                {INTENTS.map(i => (
                  <SelectItem key={i} value={i} className='text-gray-300 focus:bg-gray-700 capitalize'>
                    {i}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card className='bg-gray-900 border-gray-800'>
        <CardHeader>
          <div className='flex items-center justify-between'>
            <div>
              <CardTitle className='text-white'>
                {isLoading ? 'Loading…' : `${total.toLocaleString()} operations`}
              </CardTitle>
              <CardDescription className='text-gray-400'>
                Click any row to view the full operation detail
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className='p-0'>
          {isLoading ? (
            <div className='p-6 space-y-3'>
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className='h-12 w-full bg-gray-800' />
              ))}
            </div>
          ) : error ? (
            <div className='p-6'>
              <ErrorState
                title='Failed to load operations'
                message='Could not reach the Elite Studio API.'
                onRetry={refetch}
              />
            </div>
          ) : operations.length === 0 ? (
            <div className='flex flex-col items-center justify-center py-16 text-center px-6'>
              <Activity className='h-12 w-12 text-gray-700 mb-4' aria-hidden='true' />
              <p className='text-gray-400 font-medium'>No operations found</p>
              <p className='text-gray-600 text-sm mt-1'>Try adjusting your filters or create a new operation.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className='border-gray-800 hover:bg-transparent'>
                  <TableHead className='text-gray-400 font-medium'>Intent</TableHead>
                  <TableHead className='text-gray-400 font-medium'>SKU</TableHead>
                  <TableHead className='text-gray-400 font-medium'>Status</TableHead>
                  <TableHead className='text-gray-400 font-medium'>Created</TableHead>
                  <TableHead className='text-gray-400 font-medium text-right'>
                    <span className='inline-flex items-center gap-1'>
                      <DollarSign className='h-3.5 w-3.5' aria-hidden='true' />
                      Cost
                    </span>
                  </TableHead>
                  <TableHead className='text-gray-400 font-medium sr-only'>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {operations.map(op => (
                  <TableRow
                    key={op.operation_id}
                    className='border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors'
                    onClick={() => router.push(`/admin/elite-studio/operations/${op.operation_id}`)}
                  >
                    <TableCell>
                      <IntentBadge intent={op.intent} />
                    </TableCell>
                    <TableCell>
                      <span className='font-mono text-sm text-gray-300'>{op.sku}</span>
                    </TableCell>
                    <TableCell>
                      <OperationStatusBadge status={op.status} />
                    </TableCell>
                    <TableCell className='text-gray-400 text-sm'>{formatAgo(op.created_at)}</TableCell>
                    <TableCell className='text-right text-sm font-mono text-gray-400'>
                      ${op.cost_usd.toFixed(4)}
                    </TableCell>
                    <TableCell>
                      <Link
                        href={`/admin/elite-studio/operations/${op.operation_id}`}
                        onClick={e => e.stopPropagation()}
                        className='text-xs text-[#B76E79] hover:text-[#D4AF37] transition-colors'
                        aria-label={`View operation details for ${op.sku}`}
                      >
                        View
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {!isLoading && !error && totalPages > 1 && (
        <div className='flex items-center justify-between'>
          <p className='text-sm text-gray-500'>
            Page {page} of {totalPages} ({total.toLocaleString()} total)
          </p>
          <div className='flex items-center gap-2'>
            <Button
              variant='outline'
              size='sm'
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page <= 1}
              className='border-gray-700 text-gray-400 hover:text-white disabled:opacity-40'
              aria-label='Previous page'
            >
              <ChevronLeft className='h-4 w-4' aria-hidden='true' />
              Prev
            </Button>
            <Button
              variant='outline'
              size='sm'
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className='border-gray-700 text-gray-400 hover:text-white disabled:opacity-40'
              aria-label='Next page'
            >
              Next
              <ChevronRight className='h-4 w-4' aria-hidden='true' />
            </Button>
          </div>
        </div>
      )}
    </motion.div>
  );
}
